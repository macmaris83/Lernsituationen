#!/usr/bin/env python3
"""Verify the current whole-document A4 print view and its touch entry points.

Prints actual browser PDFs; checks full task paragraphs, material table cells,
closed editor details, pictures, vector drawings, page bounds, and stable IDs.
Use --all --delivery work/delivery-v1.7/preview for all 14 package contexts.
Browser touch and SCORM simulations do not constitute a native iPad test.
"""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import threading
import time
import unicodedata

import fitz
from playwright.sync_api import sync_playwright
from check_scorm_resume import API_INIT, fixture, encode

REPO = Path(__file__).resolve().parents[1]
PHASES = ('informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren')


def payload(path):
    return json.loads(path.read_text().split('=', 1)[1].strip().rstrip(';'))


def norm(text):
    # Keep meaningful letters/numbers while tolerating PDF line wrap/hyphenation.
    return re.sub(r'[^\w]', '', unicodedata.normalize('NFKC', text).lower()).replace('_', '')


def stable_files(root, baseline):
    names = ('mode-config.js', 'progress-meta.js')
    checks = []
    if root.name.startswith('LS') and 'preview' in root.parts and (baseline/root.name).is_dir():
        old = baseline/root.name
        for name in names:
            assert (old/name).read_bytes() == (root/name).read_bytes(), f'{name}: changed stable data'
            checks.append({'file': name, 'sha256': hashlib.sha256((root/name).read_bytes()).hexdigest()})
        a, b = payload(old/'lesson-data.js'), payload(root/'lesson-data.js')
        assert a['id'] == b['id'] and a['version'] == b['version'], 'Internal learning-state identity changed'
        for name in ('index.html', *[p+'.html' for p in PHASES]):
            pattern = r'data-task-(?:id|stable-id|signature)="[^"]+"'
            assert re.findall(pattern, a['pages'][name]) == re.findall(pattern, b['pages'][name]), f'{name}: task identity changed'
        import xml.etree.ElementTree as ET
        a, b = ET.parse(old/'imsmanifest.xml').getroot(), ET.parse(root/'imsmanifest.xml').getroot()
        identity = lambda t: [(e.tag.split('}')[-1], e.get('identifier'), e.get('identifierref'), e.get('href'))
                              for e in t.iter() if e.tag.split('}')[-1] in ('manifest','organization','item','resource')]
        assert identity(a) == identity(b), 'SCORM manifest identities changed'
        checks.append({'internalLessonAndVersion': True, 'taskIdentitiesAndSignatures': True, 'SCORMIdentities': True})
    return checks


def case(browser, server, root, mode, reports, baseline):
    key = root.relative_to(REPO).as_posix()
    label = key.replace('/', '__') + f'__W{mode}'
    result = {'package': key, 'mode': mode, 'checks': {}, 'failures': []}
    def check(name, value, details=None):
        result['checks'][name] = bool(value)
        if not value:
            result['failures'].append({'check': name, 'details': details})
    result['stableState'] = stable_files(root, baseline)
    config = payload(root/'mode-config.js'); config['mode'] = mode
    ctx = browser.new_context(viewport={'width':1024, 'height':768}, has_touch=True, reduced_motion='reduce')
    saved = fixture(payload(root/'progress-meta.js')); saved['m'] = mode
    saved['a']['feedback'] = f'Gedrucktes Fremdfeedback für Lernweg {mode}'
    saved['a']['nextGoal'] = f'Gedruckter nächster Lernschritt für Lernweg {mode}'
    values = {'cmi.core.student_id':'print-test-learner','cmi.core.lesson_mode':'normal',
              'cmi.suspend_data':encode(saved),'cmi.core.lesson_location':'index.html',
              'cmi.core.lesson_status':'incomplete','cmi.interactions._count':'0'}
    ctx.add_init_script('('+API_INIT+')('+json.dumps({'values':values})+')')
    page = ctx.new_page(); page.set_default_timeout(15000)
    errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.route('**/mode-config.js', lambda route: route.fulfill(status=200, content_type='application/javascript', body='window.SOZ_CONFIG='+json.dumps(config)+';'))
    base = f'http://127.0.0.1:{server.server_port}/'+key+'/'
    page.goto(base+'scorm.html')
    page.wait_for_function('document.querySelector("iframe")?.contentWindow?.SOZ_READY===true')
    frame = next(f for f in page.frames if f != page.main_frame)
    check('iPadLandscapeNoOverflow', frame.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
    footer = frame.evaluate('''()=>{const p=document.querySelector('.footer-utils [data-document-pdf]'),e=document.querySelector('.footer-utils a[href="lehrkraft.html"]');return {print: p?{href:p.getAttribute('href'),target:p.target,printer:!!p.querySelector('.document-print-icon,.printer-icon,[data-icon="printer"]'),adobe:!!p.querySelector('.acrobat-pdf-icon'),box:p.getBoundingClientRect().toJSON()}:null,editor:e?{gear:!!e.querySelector('.editor-settings-icon,.editor-gear-icon,.gear-icon,[data-icon="settings"],[data-icon="gear"]'),href:e.getAttribute('href'),box:e.getBoundingClientRect().toJSON()}:null};}''')
    check('FooterPrinter', footer['print'] and footer['print']['printer'] and not footer['print']['adobe'], footer)
    check('EditorGear', footer['editor'] and footer['editor']['gear'], footer)
    check('FooterDestinationsPreserved', footer['print'] and footer['print']['href']=='druckansicht.html' and footer['editor'] and footer['editor']['href']=='lehrkraft.html', footer)
    check('Footer44pxTouch', all(footer.get(k) and footer[k]['box']['width'] >= 43.9 and footer[k]['box']['height'] >= 43.9 for k in ('print','editor')), footer)

    # A real saved page override contains closed nested details and a long value.
    # Its content must survive printing without changing the saved original.
    marker = f'Druckprüfung geschlossene Detailinformation {root.name} Lernweg {mode}'
    saved_value = 'Vollständige gespeicherte Eingabe '+('mit mehreren lesbaren Zeilen und eigenem Arbeitsbeleg. '*12)
    frame.evaluate('''marker=>{const s=SOZ_API.getSettings();s.overrides={...s.overrides};let name='informieren.html';s.overrides[name]=(s.overrides[name]||SOZPAED.pages[name])+`<details data-print-qa-closed><summary>Gespeicherter Zusatz</summary><details><summary>Weitere Einzelheiten</summary><p>${marker}</p></details></details>`;s.overrides['index.html']=(s.overrides['index.html']||SOZPAED.pages['index.html'])+`<label data-print-qa-value>Eigener Arbeitsbeleg<textarea data-work-surface data-work-id="print-qa"></textarea></label>`;SOZ_API.saveSettings();}''', marker)
    frame.goto(base+'index.html');frame.wait_for_function('window.SOZ_READY===true')
    frame.locator('[data-print-qa-value] textarea').fill(saved_value)
    micro_value = f'Meine tatsächlich eingegebene Relevanzantwort für {root.name} und Lernweg {mode}.'
    micro = frame.locator('.micro-question:has(textarea[data-micro-text])').first
    has_micro = micro.count()>0
    if has_micro:
        micro.evaluate('e=>e.open=true');micro.locator('textarea[data-micro-text]').first.fill(micro_value)
        micro.evaluate('e=>e.open=false')
        frame.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    micro_before=frame.evaluate('Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.startsWith("biocasa:")))')
    before_calls = len(page.evaluate('testCalls'))
    if footer['print'] and footer['print']['target'] != '_blank':
        frame.locator('.footer-utils [data-document-pdf]').click()
        frame.wait_for_url('**/druckansicht.html')
        check('ActualSCORMPrintClickKeepsFrame', True)
    else:
        check('ActualSCORMPrintClickKeepsFrame', False, footer)
        frame.goto(base+'druckansicht.html')
    frame.wait_for_function('window.SOZ_READY===true')
    check('LearnerAndSCORMBridgePreserved', frame.evaluate('SOZ_PROGRESS.learner')=='print-test-learner' and frame.evaluate('SOZ_PROGRESS.kind')=='moodle')
    check('SelectedMode', frame.locator('body').get_attribute('data-mode') == str(mode))
    # Derive expected text independently from the current source/overrides.
    expected = frame.evaluate('''()=>{const s=SOZ_API.getSettings(),d=SOZPAED;let tasks=[],cells=[],materialParagraphs=[],detailParagraphs=[];for(const name of d.printOrder){const doc=new DOMParser().parseFromString(s.overrides?.[name]||d.pages[name]||'','text/html');doc.querySelectorAll('[data-mode-panel]').forEach(e=>{if(Number(e.dataset.modePanel)!==Number(s.mode))e.remove();});for(const p of doc.querySelectorAll('.assignment-body>p'))if(p.textContent.trim())tasks.push(p.textContent.trim());for(const p of doc.querySelectorAll('details p'))if(!p.closest('.material-access,.phase-materials,.no-print')&&p.textContent.trim())detailParagraphs.push(p.textContent.trim());if(/^m\\d+\\.html$/.test(name)){for(const cell of doc.querySelectorAll('td,th'))if(cell.textContent.trim())cells.push(cell.textContent.trim());for(const p of doc.querySelectorAll('.source-document .paper p,.material-document p,.material-content p'))if(p.textContent.trim().length>20)materialParagraphs.push(p.textContent.trim());}}return {tasks,cells,materialParagraphs,detailParagraphs,order:d.printOrder};}''')
    # Observe the actual user click; window.print is stubbed only to record readiness.
    frame.evaluate('''()=>{window.__printCalls=[];window.print=()=>{window.__printCalls.push({fonts:document.fonts.status,images:[...document.querySelectorAll('[data-print-content] img')].every(i=>i.complete&&i.naturalWidth>0),ready:document.body.dataset.printReady,closed:[...document.querySelectorAll('[data-print-content] details')].filter(d=>!d.open).length});window.dispatchEvent(new Event('beforeprint'));};}''')
    # Introduce real pending image/font requests immediately before activation.
    # A synchronous window.print() handler would record images=False/fonts=loading.
    requests=[]
    def delayed_image(route):
        requests.append('image');time.sleep(.15)
        route.fulfill(content_type='image/svg+xml',body='<svg xmlns="http://www.w3.org/2000/svg" width="32" height="24"><rect width="32" height="24" fill="#009bd9"/></svg>')
    font = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    def delayed_font(route):
        requests.append('font');time.sleep(.15)
        route.fulfill(content_type='font/ttf',body=font.read_bytes())
    page.route('**/print-qa-loading.svg', delayed_image)
    page.route('**/print-qa-font.ttf', delayed_font)
    frame.evaluate('''()=>{const root=document.querySelector('[data-print-content]');window.__printQAFont=root.style.fontFamily;const image=new Image(32,24);image.dataset.printQaLoading='';image.src='print-qa-loading.svg';image.alt='Druckprüfung Bildladen';root.append(image);const f=new FontFace('Print QA','url(print-qa-font.ttf)');document.fonts.add(f);f.load();root.style.fontFamily='"Print QA",sans-serif';document.querySelector('[data-print]').click();}''')
    frame.wait_for_function('window.__printCalls.length>0')
    calls = frame.evaluate('window.__printCalls')
    check('PrintClickWaitsForFontsAndImages', calls[-1]['fonts']=='loaded' and calls[-1]['images'] and set(requests)=={'font','image'}, calls)
    check('AllDetailsExpanded', calls[-1]['closed']==0, calls)
    frame.evaluate('''()=>{document.querySelector('[data-print-content]').style.fontFamily=window.__printQAFont;document.querySelector('[data-print-qa-loading]')?.remove();}''')
    page.emulate_media(media='print')
    frame.evaluate('window.dispatchEvent(new Event("beforeprint"))')
    metrics = frame.evaluate('''()=>{const root=document.querySelector('[data-print-content]'),visible=e=>e.checkVisibility({checkVisibilityCSS:true});const all=[...root.querySelectorAll('*')].filter(visible);const clip=all.filter(e=>{const c=getComputedStyle(e);return /(auto|scroll|hidden|clip)/.test(c.overflowY)&&e.scrollHeight>e.clientHeight+3&&e.clientHeight>0;}).map(e=>({tag:e.tagName,cls:e.className,h:e.clientHeight,scroll:e.scrollHeight}));const b=getComputedStyle(document.body),pseudo=getComputedStyle(document.body,'::before');return {background:b.backgroundImage,color:b.backgroundColor,pseudo:{content:pseudo.content,display:pseudo.display,opacity:pseudo.opacity},clip,closed:[...root.querySelectorAll('details')].filter(d=>!d.open).length,visibleModes:[...root.querySelectorAll('[data-mode-panel]')].filter(visible).map(e=>Number(e.dataset.modePanel)),chapters:[...root.querySelectorAll(':scope>.print-chapter')].map(c=>c.dataset.printSource),photos:[...root.querySelectorAll('.story-photo img,[data-media-key] img')].filter(visible).map(i=>({w:i.naturalWidth,h:i.naturalHeight,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})),svg:all.filter(e=>e.tagName.toLowerCase()==='svg').length,hiddenTasks:[...root.querySelectorAll('.assignment-body')].filter(e=>!e.closest('[data-mode-panel][hidden]')&&!visible(e)).length};}''')
    check('PageBackgroundRemoved', metrics['background']=='none' and metrics['color'] in ('rgb(255, 255, 255)','rgba(0, 0, 0, 0)') and (metrics['pseudo']['content'] in ('none','normal') or metrics['pseudo']['display']=='none' or metrics['pseudo']['opacity']=='0'), metrics)
    check('NoClippedScrollingContent', not metrics['clip'], metrics['clip'][:12])
    check('NoHiddenCurrentTasks', metrics['hiddenTasks']==0, metrics['hiddenTasks'])
    check('NoAlternateLearningWaysPrinted', all(n==mode for n in metrics['visibleModes']), metrics['visibleModes'])
    cards=frame.evaluate('''()=>[...document.querySelectorAll('.print-chapter[data-print-source="index.html"] .orientation-competence-list>article,.print-chapter[data-print-source="index.html"] .orientation-competence-list>.competence-row')].map(e=>({text:e.textContent.trim().slice(0,40),x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))''')
    check('CompetenceProfileCompact2x2',len(cards)==4 and abs(cards[0]['y']-cards[1]['y'])<2 and abs(cards[2]['y']-cards[3]['y'])<2 and abs(cards[0]['x']-cards[2]['x'])<2 and abs(cards[1]['x']-cards[3]['x'])<2 and cards[2]['y']>cards[0]['y'],cards)
    check('CompleteChapterOrder', metrics['chapters']==expected['order'], metrics['chapters'])
    check('PicturesUncropped', all(abs(p['width']/p['height']-p['w']/p['h'])<.025 for p in metrics['photos'] if p['height'] and p['h']), metrics['photos'])
    # Print an exact prepared iframe-DOM snapshot as a top-level document, so
    # Chromium's print API includes the entire document rather than iframe height.
    choices = frame.evaluate('''()=>{const saved=SOZ_PROGRESS.read().q;return [...document.querySelectorAll('[data-print-content] [data-quiz-question]')].filter(p=>saved[p.dataset.quizQuestion]).map(p=>({expected:String(saved[p.dataset.quizQuestion][0]),selected:p.querySelector('input:checked')?.value}));}''')
    check('SavedMCChoicesRendered',all(c['expected']==c['selected'] for c in choices),choices)
    snapshot = frame.evaluate('''()=>{const d=document.documentElement.cloneNode(true);const live=[...document.querySelectorAll('input,textarea,select')],copy=[...d.querySelectorAll('input,textarea,select')];live.forEach((e,i)=>{const c=copy[i];if(e.matches('input[type=radio],input[type=checkbox]'))c.toggleAttribute('checked',e.checked);else if(e.tagName==='TEXTAREA')c.textContent=e.value;else if(e.tagName==='SELECT')[...c.options].forEach((o,n)=>o.toggleAttribute('selected',e.options[n].selected));else c.setAttribute('value',e.value);});d.querySelectorAll('script').forEach(e=>e.remove());const base=document.createElement('base');base.href=location.href;d.querySelector('head').prepend(base);return '<!doctype html>'+d.outerHTML;}''')
    pdfpage = ctx.new_page();pdfpage.set_content(snapshot,wait_until='networkidle')
    serialized_choices=pdfpage.evaluate('''()=>[...document.querySelectorAll('[data-print-content] [data-quiz-question]')].filter(p=>p.querySelector('input:checked')).map(p=>p.querySelector('input:checked').value)''')
    check('SavedMCChoicesSerialized',serialized_choices==[c['expected'] for c in choices],serialized_choices)
    pdfpage.evaluate('''async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r;})));}''')
    pdf = reports/(label+'.pdf')
    pdfpage.pdf(path=str(pdf), print_background=True, prefer_css_page_size=True, display_header_footer=False)
    doc = fitz.open(pdf)
    texts = [p.get_text('text') for p in doc]; full = norm('\n'.join(texts))
    sorted_full = norm('\n'.join(p.get_text('text',sort=True) for p in doc))
    missing = lambda items: [s for s in items if norm(s) not in full and norm(s) not in sorted_full]
    for name,items in [('AllCurrentTaskParagraphs',expected['tasks']), ('AllMaterialTableCells',expected['cells']), ('AllMaterialParagraphs',expected['materialParagraphs']), ('AllExpandedDetailParagraphs',expected['detailParagraphs'])]:
        absent=missing(items);check(name,not absent,{'expected':len(items),'missing':absent[:6]})
    check('SavedClosedDetailPrinted', norm(marker) in full)
    check('LongSavedValuePrinted', norm(saved_value) in full, {'expectedCharacters':len(saved_value)})
    check('SCORMAssessmentTextPrinted', not missing([saved['a']['feedback'],saved['a']['nextGoal'],*[a['evidence'] for a in saved['a']['assessments'].values()]]))
    if has_micro:
        check('TypedMicroResponsePrinted',norm(micro_value) in full)
        check('PrintDoesNotChangeSavedAccordionState',frame.evaluate('Object.fromEntries(Object.entries(localStorage).filter(([k])=>k.startsWith("biocasa:")))')==micro_before)
    print_calls = page.evaluate('testCalls')[before_calls:]
    check('PrintHasNoLMSGradingWrites',not any(c.get('type')=='set' and (c.get('key','').startswith(('cmi.interactions.','cmi.core.score.')) or c.get('key')=='cmi.core.lesson_status') for c in print_calls),print_calls)
    check('AllPagesA4', all(abs(p.rect.width-595.276)<1 and abs(p.rect.height-841.89)<1 for p in doc), [list(p.rect) for p in doc[:2]])
    edge=[];blank=[];images=[];drawings=0
    for i,p in enumerate(doc):
        spans=[s for b in p.get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for s in line['spans'] if s['text'].strip()]
        for span in spans:
            r=fitz.Rect(span['bbox'])
            if r.x0<17 or r.x1>p.rect.width-17 or r.y0<11 or r.y1>p.rect.height-11:edge.append({'page':i+1,'text':span['text'][:70],'box':list(r)})
        if not spans and not p.get_images():blank.append(i+1)
        images.extend((im[2],im[3]) for im in p.get_images());drawings+=len(p.get_drawings())
    check('ContentInsidePrintMargins',not edge,edge[:12]);check('NoEmptyPages',not blank,blank)
    check('VectorGraphicsRetained',drawings>=max(1,metrics['svg']),{'svgElements':metrics['svg'],'PDFDrawings':drawings})
    check('OriginalPhotosEmbedded',all((p['w'],p['h']) in images for p in metrics['photos']),{'expected':[(p['w'],p['h']) for p in metrics['photos']],'imageDimensions':list(set(images))})
    doc[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(reports/(label+'_page1.png'))
    result.update({'pages':len(doc),'PDF':str(pdf.relative_to(REPO)),'tasks':len(expected['tasks']),'tableCells':len(expected['cells']),'materialParagraphs':len(expected['materialParagraphs']),'visibleSVGs':metrics['svg'],'photoCount':len(metrics['photos']),'MCChoices':len(choices)})
    check('NoJavaScriptErrors',not errors,errors)
    doc.close();ctx.close();result['status']='FAIL' if result['failures'] else 'PASS'
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--all',action='store_true');ap.add_argument('--root','--roots',type=Path,action='append')
    ap.add_argument('--delivery',type=Path,default=REPO/'work/delivery-v1.7/preview')
    ap.add_argument('--baseline',type=Path,default=REPO/'work/delivery-v1.6/preview')
    ap.add_argument('--modes',type=int,nargs='+',default=[1,5]);ap.add_argument('--report',type=Path,default=REPO/'work/print-quality/Druck_Pruefung.json')
    args=ap.parse_args();args.report=args.report.resolve();args.report.parent.mkdir(parents=True,exist_ok=True)
    if args.root:roots=[p.resolve() for p in args.root]
    elif args.all:
        catalogue=json.loads((REPO/'master-katalog.json').read_text())['packages']
        roots=[REPO/item['master'] for item in catalogue if item['id'].startswith('BRC-LG01-') or item['id'] in ('VORLAGE-TRADIERT','VORLAGE-FUENF-LERNWEGE')]+sorted(args.delivery.resolve().glob('LS??'))
    else:roots=[args.delivery.resolve()/'LS01']
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(REPO)))
    threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for root in roots:
                modes=args.modes if payload(root/'lesson-data.js').get('workbooks') else [1]
                for mode in modes:
                    r=case(browser,server,root,mode,args.report.parent,args.baseline.resolve());results.append(r)
                    print(r['status'],root.relative_to(REPO),f'W{mode}',f'{r["pages"]} A4 pages',[(e['check']) for e in r['failures']],flush=True)
                    args.report.write_text(json.dumps({'status':'RUNNING','results':results},ensure_ascii=False,indent=2)+'\n')
            browser.close()
    finally:server.shutdown();server.server_close()
    status='FAIL' if any(r['failures'] for r in results) else 'PASS'
    args.report.write_text(json.dumps({'status':status,'packages':len(roots),'cases':len(results),'results':results,'limits':'Actual Chromium A4 browser PDFs and touch SCORM iframe simulations. Physical iPad, native Safari, Moodle App and printer hardware have not been tested.'},ensure_ascii=False,indent=2)+'\n')
    raise SystemExit(0 if status=='PASS' else 1)


if __name__=='__main__':main()
