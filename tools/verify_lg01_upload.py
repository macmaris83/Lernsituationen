#!/usr/bin/env python3
"""Independent content, archive and actual browser audit of an LG01 delivery."""
from __future__ import annotations
import argparse
import base64
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import threading
import xml.etree.ElementTree as ET
import zipfile
import fitz
from lxml import html
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
PHASES = ['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren']


def payload(path): return json.loads(path.read_text().split('=',1)[1].strip().rstrip(';'))
def digest(data): return hashlib.sha256(data).hexdigest()
def normalized(text): return re.sub(r'\s+','',text.replace('\u00ad',''))
def need(condition, *context):
    if not condition: raise AssertionError(' · '.join(map(str,context)))


def static(source, target, archive):
    before=payload(source/'lesson-data.js'); after=payload(target/'lesson-data.js')
    for key,value in before.items():
        if key not in ('pages','competencies'): need(after[key]==value,target.name,key)
    for name,body in before['pages'].items():
        if name!='index.html': need(after['pages'][name]==body,target.name,name,'complete original content')
    for name in ['progress-meta.js','Konfiguration.json','mode-config.js']:
        need((target/name).read_bytes()==(source/name).read_bytes(),target.name,name,'unchanged bytes')
    protected=0
    for file in source.rglob('*'):
        if file.is_file() and (file.suffix.lower() in ('.pdf','.png','.jpg','.jpeg','.svg','.webp') or file.name.startswith('goodnotes-')):
            need(file.read_bytes()==(target/file.relative_to(source)).read_bytes(),target.name,file.name,'original media/PDF/phase payload')
            protected+=1
    old_meta=payload(source/'progress-meta.js')
    books=sum(body.count('class="book-reference"') for name,body in before['pages'].items() if name.replace('.html','') in PHASES)
    for phase in PHASES:
        for mode in range(1,6):
            script=(target/f'goodnotes-phase-{phase}-W{mode}.js').read_text()
            raw=json.loads(re.search(r'"'+phase+':'+str(mode)+r'"\s*:\s*("[A-Za-z0-9+/=]+")',script)[1])
            need(base64.b64decode(raw)==(target/f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf').read_bytes(),target.name,phase,mode,'correct PDF payload')
    doc=fitz.open(target/'pdf/Gesamtdokument_A4.pdf')
    text=normalized(''.join(page.get_text() for page in doc))
    need(all(c['statement'].startswith('Ich ') for c in after['competencies']),target.name,'Ich competencies')
    for c in after['competencies']: need(normalized(c['statement']) in text,target.name,'competency in current PDF',c['label'])
    cells=0
    for name,body in before['pages'].items():
        if not re.fullmatch(r'm\d+\.html',name): continue
        root=html.fragment_fromstring(body,create_parent='div')
        for cell in root.xpath('.//td|.//th'):
            expected=normalized(cell.text_content())
            need(not expected or expected in text,target.name,name,'original table cell in PDF',cell.text_content())
            cells+=1
    image_sizes={(image[2],image[3]) for page in doc for image in page.get_images(full=True)}
    need(any(width==1672 for width,height in image_sizes),target.name,'full-resolution original images in PDF')
    doc.close()
    original=ET.parse(source/'imsmanifest.xml').getroot(); updated=ET.parse(target/'imsmanifest.xml').getroot()
    need(original.attrib==updated.attrib,target.name,'unchanged manifest identity')
    resources=lambda r:[(e.get('identifier'),e.get('href')) for e in r.iter() if e.tag.split('}')[-1]=='resource']
    need(resources(original)==resources(updated),target.name,'unchanged launch identifiers')
    with zipfile.ZipFile(archive) as z:
        need(z.testzip() is None,target.name,'CRC')
        actual={p.relative_to(target).as_posix():p for p in target.rglob('*') if p.is_file()}
        need(set(z.namelist())==set(actual),target.name,'archive equals current files')
        for name,file in actual.items(): need(z.read(name)==file.read_bytes(),target.name,name,'current packaged bytes')
        for e in updated.iter():
            if e.tag.split('}')[-1]=='file': need(e.get('href') in actual,target.name,'manifest member',e.get('href'))
    return {'lesson':target.name,'tasks':len(old_meta['tasks']),'bookReferences':books,'protectedFiles':protected,'pdfTableCells':cells,'contentAndArchives':'PASS'}


def browser_audit(browser, base, root, reports):
    context=browser.new_context(viewport={'width':1024,'height':768},reduced_motion='reduce',accept_downloads=True)
    context.add_init_script("navigator.canShare=()=>true;navigator.share=async({files})=>{window.sharedPdf={name:files[0].name,hash:[...new Uint8Array(await crypto.subtle.digest('SHA-256',await files[0].arrayBuffer()))].map(x=>x.toString(16).padStart(2,'0')).join('')};}")
    page=context.new_page(); page.set_default_timeout(15000); errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    picture_views=0; materials=0
    slots=json.loads((root/'media-map.json').read_text())['slots']
    for width in (390,768,1024):
        page.set_viewport_size({'width':width,'height':844})
        for filename,role in [('index.html','orientation'),('handlungssituation.html','situation')]:
            page.goto(base+filename);page.wait_for_function('window.SOZ_READY===true')
            if filename=='index.html':
                need(page.locator('.material-access').count()==0,root.name,'no orientation material access')
                need(page.locator('.orientation-competence-list>article').count()==4,root.name,'four complete competency cards')
                need(page.locator('.orientation-priority').count()==1,root.name,'one priority competency')
                need('Ich ' in page.locator('.orientation-priority').inner_text(),root.name,'pupil perspective')
                page.locator('[data-orientation-complete]').check()
            need(page.locator('[data-share-workbook]').count()==0,root.name,'no introductory GoodNotes import')
            picture=page.locator(f'[data-media-key="{role}"] img')
            need(picture.count()==1 and picture.is_visible(),root.name,role,'visible original image')
            page.wait_for_function('e=>e.complete&&e.naturalWidth>0',arg=picture.element_handle())
            geom=picture.evaluate('e=>({w:e.width,h:e.height,nw:e.naturalWidth,nh:e.naturalHeight,fit:getComputedStyle(e).objectFit})')
            need(abs(geom['h']-geom['w']*geom['nh']/geom['nw'])<1.5 and geom['fit']!='cover',root.name,role,'uncropped proportional picture')
            need(picture.get_attribute('src')==slots[role]['src'],root.name,role,'assigned image')
            need(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),root.name,width,filename,'page width')
            need(page.locator('.footer-utils [data-document-pdf]').count()==1,root.name,'single PDF footer')
            if root.name=='LS01' and width in (390,1024): page.screenshot(path=str(reports/f'{root.name}_{role}_{width}.png'),full_page=True)
            picture_views+=1
    page.set_viewport_size({'width':1024,'height':768})
    page.goto(base+'lehrkraft.html');page.wait_for_function('window.SOZ_READY===true')
    page.locator('#teacher-pin').fill('1234');page.locator('#teacher-unlock').click()
    page.locator('[data-start-teacher-view]').click();page.wait_for_url('**/index.html')
    page.goto(base+'informieren.html');page.wait_for_function('document.body.dataset.taskFocusReady==="true"')
    for mode in (1,5):
        selector=page.locator('.teacher-view-bar select')
        if selector.input_value()!=str(mode):
            with page.expect_navigation(wait_until='domcontentloaded'): selector.select_option(str(mode))
            page.wait_for_function('document.body.dataset.taskFocusReady==="true"&&Number(document.body.dataset.mode)==='+str(mode))
            need('aufgabe=' not in page.url,root.name,'deliberate path change clears stale return context')
        page.locator('[data-share-workbook]:visible').first.click();page.wait_for_function('!!window.sharedPdf')
        shared=page.evaluate('sharedPdf');expected=f'GoodNotes_Phase_informieren_W{mode}.pdf'
        need(shared['name']==expected and shared['hash']==digest((root/'pdf'/expected).read_bytes()),root.name,mode,'actual phase GoodNotes share')
        page.evaluate('delete window.sharedPdf')
        page.locator('.task-original-preview:visible').first.click()
        task=page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')
        access=page.locator('details.material-access').first
        if access.get_attribute('open') is None: access.locator('summary').first.click()
        page.locator('.material-access a').first.click();page.locator('.return-task').wait_for(state='visible')
        need(page.evaluate('SOZ_MATERIAL_RETURN.read().task')==task,root.name,mode,'correct return task')
        choices=page.locator('.material-switch a').count()
        for index in range(choices):
            if index:
                page.locator('.material-switch summary').click();page.locator('.material-switch a').nth(index).click();page.locator('.return-task').wait_for(state='visible')
            need(page.evaluate('SOZ_MATERIAL_RETURN.read().task')==task,root.name,mode,'task retained across material switch')
            need(page.locator('.material-phase-navigation [data-learning-page]').count()==8,root.name,'material phase overview')
            page.set_viewport_size({'width':390,'height':844})
            need(page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),root.name,page.url,'mobile material width')
            materials+=1
        page.set_viewport_size({'width':1024,'height':768});page.locator('.return-task').click()
        page.wait_for_function('!!document.querySelector(".task-accordion[open]")')
        need(page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')==task,root.name,'exact task return')
        page.locator('.task-accordion[open] .focus-back-actions button').click()
    # Exercise a real configured export after changing a task, then inspect bytes.
    page.goto(base+'lehrkraft.html');page.wait_for_function('window.SOZ_READY===true')
    page.locator('#teacher-pin').fill('1234');page.locator('#teacher-unlock').click()
    page.locator('[data-edit-page]').select_option('informieren.html')
    marker=' Exportprüfung 1.5.'
    page.locator('[data-page-editor]').evaluate('(e,m)=>e.querySelector(".assignment-body p").append(document.createTextNode(m))',marker)
    page.locator('[data-save-page]').click()
    with page.expect_download(timeout=60000) as info: page.locator('[data-export-ims]').click()
    download=info.value; export=reports/(root.name+'-editor-export.zip');download.save_as(export)
    with zipfile.ZipFile(export) as z:
        data=json.loads(z.read('lesson-data.js').decode().split('=',1)[1].strip().rstrip(';'))
        metadata=json.loads(z.read('progress-meta.js').decode().split('=',1)[1].strip().rstrip(';'))
        original_meta=payload(root/'progress-meta.js')
        need(metadata['orientationSignature']==original_meta['orientationSignature'],root.name,'task edit preserves read orientation')
        changed={key for key,value in metadata['tasks'].items() if value!=original_meta['tasks'][key]}
        need(len(changed)==1,root.name,'only edited task signature changes',changed)
        need(marker.strip() in data['pages']['informieren.html'],root.name,'saved edit in export data')
        need(marker.strip() in z.read('informieren.html').decode(),root.name,'saved edit in export HTML')
        for slot in slots.values(): need(z.read(slot['src'])==(root/slot['src']).read_bytes(),root.name,'original image in editor export')
        need(z.read('assets/progress-core.js')==(root/'assets/progress-core.js').read_bytes(),root.name,'current progress code in export')
        need(z.read('Paketversion.json')==(root/'Paketversion.json').read_bytes(),root.name,'delivery version in export')
        for name in ('calculator-engine.js','calculator.js','calculator.css'):
            need(z.read('assets/'+name)==(root/'assets'/name).read_bytes(),root.name,'calculator packaged in editor export',name)
    export.unlink()
    need(not errors,root.name,'JavaScript errors',errors)
    context.close()
    return {'lesson':root.name,'imageViews':picture_views,'materialVisits':materials,'phaseSharePayloads':2,'editorExport':'PASS','browser':'PASS'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('delivery',type=Path);args=ap.parse_args()
    report={'version':'1.5','static':[],'browser':[],'limitations':['Local Chromium and SCORM simulation; native Moodle/AIS/GoodNotes require the classroom system.']}
    folder=args.delivery/'preview'; reports=args.delivery/'Pruefberichte';reports.mkdir(exist_ok=True)
    for n in range(1,7):
        lesson=f'LS{n:02d}'
        report['static'].append(static(args.source/lesson,folder/lesson,args.delivery/f'BRC_LG01_{lesson}_v1.5_SCORM12.zip'))
        print('PASS content',lesson,flush=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_): pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for n in range(1,7):
                lesson=f'LS{n:02d}'
                report['browser'].append(browser_audit(browser,f'http://127.0.0.1:{server.server_port}/{lesson}/',folder/lesson,reports))
                (reports/'Lieferpruefung.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
                print('PASS browser',lesson,flush=True)
            browser.close()
    finally: server.shutdown();server.server_close()
    report['status']='PASS';(reports/'Lieferpruefung.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__': main()
