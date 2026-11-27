"""Build phase workbooks and print views for BFS dual Global Bike SCORM masters."""
from pathlib import Path
from html import escape
import json
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit, quote, unquote
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

from lxml import html
from playwright.sync_api import sync_playwright
import fitz

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('BFS_REPO', HERE.parents[1])).resolve()
BFS = ROOT/'Fachbereiche/BFSdual'
BRC = ROOT/'Fachbereiche/BRC/LG01/LS04'
OFFICE = BFS/'LF06/Buero/LS09'
PHASES = dict(informieren='Informieren', planen='Planen', entscheiden='Entscheiden',
              durchfuehren='Durchführen', bewerten='Bewerten', reflektieren='Reflektieren')
ORDER = ('index', 'handlungssituation', 'informieren', 'begriffstraining', 'planen',
         'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren', 'materialien')
PRINTER = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V3h12v6M6 17H4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2M6 14h12v7H6zM17 12h1"/></svg>'
MATH_TASKS = {
    '2.4': {'07','09','12','13A','13B','13C'},
    '2.5': {'08','10','12','13A','13B','13C'},
    '2.6a': {'14','15A','15B','15C'},
    '2.6b': {'12','13','14A','14B','14C','15'},
    '2.7': {'13','14','15'},
    '3.1': {'06','09','11','12','13A','13B','13C','14'},
    '3.2': {'07','09','12'},
    '3.3': {'12'},
}
NS = 'http://www.imsproject.org/xsd/imscp_rootv1p1p2'
ET.register_namespace('', NS)
ET.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')

def fragment(text):
    return html.fragment_fromstring(text, create_parent='div')

def serial(node):
    return html.tostring(node, encoding='unicode', with_tail=False)

def body(node):
    return escape(node.text or '') + ''.join(html.tostring(child, encoding='unicode') for child in node)

def clean(node, prefix=''):
    for addon in node.xpath('.//*[@data-phase-exports or @data-document-pdf or @class="bfs-material-footer" or @data-bfs-material-menu or @data-bfs-choice-status or contains(concat(" ", normalize-space(@class), " "), " viewerbar ") or contains(concat(" ", normalize-space(@class), " "), " subbar ") or contains(concat(" ", normalize-space(@class), " "), " material-rail ")]'):
        if addon.getparent() is not None:addon.drop_tree()
    for element in node.xpath('.//script|.//style|.//noscript|.//button|.//select|.//progress|.//*[@data-completion-label or @data-finish-hint or @data-runtime-status or @data-export-pick]'):
        element.drop_tree()
    for x in node.xpath('.//details'):
        x.set('open','')
    for x in node.xpath('.//img'):
        x.attrib.pop('loading',None)
    for x in node.xpath('.//textarea'):
        x.tag='div'
        x.attrib.clear()
        x.set('class','pdf-response')
    for x in node.xpath('.//input'):
        kind=x.get('type','text')
        x.tag='span'
        x.attrib.clear()
        x.text='○ ' if kind=='radio' else '□ ' if kind=='checkbox' else '________________'
    for x in node.xpath('.//*[@id]'):
        x.attrib.pop('id')
    for x in node.xpath('.//*[@src or @href]'):
        for a in ('src','href'):
            value=x.get(a)
            if value and prefix and not value.startswith('#') and not urlsplit(value).scheme:
                x.set(a, prefix+value)
    return node

def numbered_task(node):
    n=node.get('data-task-number')
    minutes=node.get('data-task-minutes')
    path=node.get('data-path')
    block=node.xpath('./*[@class="assignment-body"]')[0]
    timed=block.xpath('.//*[contains(concat(" ",@class," ")," assignment-time ")]')
    for x in timed:x.drop_tree()
    label=f'Aufgabe {n} · {minutes} Min.'
    if path:label+=f' · Lernweg {path}'
    return (path, label, body(clean(block)))

def add_page(title, body_html, cls='pdf-document', controls='', css='assets/pdf-document.css'):
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><link rel="stylesheet" href="{css}"></head>
<body class="{cls}"><main>{controls}{body_html}</main></body></html>'''

def heading(title, ls, phase='', logo='assets/bbs1-aurich.svg'):
    loeppt=logo.rsplit("/",1)[0]+"/loept.png"
    return f'<header class="pdf-heading"><div class="pdf-logos"><img src="{logo}" alt="BBS 1 Aurich"><img src="{loeppt}" alt="Löppt"></div><div class="pdf-brand">BBS 1 Aurich · BFS dual · Global Bike · LS {ls}</div><h1>{escape(title)}</h1>' + (f'<h2>{escape(phase)}</h2>' if phase else '') + '</header>'

def answer_space(ls, task, large):
    match=re.match(r'Aufgabe ([A-Z0-9]+)',task[1])
    math=match and match[1] in MATH_TASKS.get(ls,set())
    if math:
        rows=18 if large else 10
        return '<div class="pdf-notes pdf-grid"><p>Rechenweg · 5-mm-Karo</p><div class="pdf-squares" style="height:'+str(rows*5)+'mm"></div></div>'
    rows=12 if large else 6
    return '<div class="pdf-notes"><p>Notizen</p>'+'<div class="pdf-line"></div>'*rows+'</div>'

def task_html(task,ls,large=False):
    code, meta, content=task
    variant=f' data-pdf-path="{code}"' if code else ''
    return f'<article class="pdf-task"{variant}><div class="pdf-task-meta">{escape(meta)}</div>{content}{answer_space(ls,task,large)}</article>'

def download(phase, ls, variant=''):
    suffix='-'+variant if variant else ''
    return f'pdf/GoodNotes-LS-{ls}-{phase}{suffix}.pdf'

def phase_box(phase,ls):
    def link(code=''):
        data=f' data-path="{code}" hidden' if code else ''
        return f'<a class="button" href="{download(phase,ls,code)}" download{data}><img src="assets/goodnotes.png" alt="">GoodNotes-Export</a>'
    controls=''.join(link(path) for path in 'ABC')+'<a href="entscheiden.html" data-export-pick>Wähle für den GoodNotes-Export zuerst deinen Lernweg.</a>' if phase=='durchfuehren' else link()
    return f'<nav class="bfs-phase-export no-print" data-phase-exports aria-label="Arbeitsblatt für {PHASES[phase]}">{controls}</nav>'

def footer(prefix=''):
    return f'<div class="bfs-document-footer no-print"><a class="bfs-document-pdf" data-document-pdf href="{prefix}druckansicht.html">{PRINTER}Gesamtdokument als PDF</a></div>'

def interactive_view(d,title,ls,chunks,back):
    controls=f'''<nav class="pdf-controls" aria-label="Druckoptionen">
<a href="{back}">Zur Lernsituation</a>
<label for="pdf-lernweg">Lernweg</label><select id="pdf-lernweg"><option value="">Alle Lernwege</option><option>A</option><option>B</option><option>C</option></select>
<button type="button" data-print-document>Drucken / als PDF sichern</button>
<a href="pdf/Gesamtdokument-LS-{ls}.pdf" download>PDF mit allen Lernwegen herunterladen</a></nav>
<script defer src="assets/editor-config.js"></script><script defer src="assets/editor-settings.js"></script><script defer src="assets/pdf-ui.js"></script>'''
    (d/'druckansicht.html').write_text(add_page(f'{title} · Gesamtdokument',heading(title,ls)+''.join(chunks),controls=controls))

def source_plan(d):
    ls=f'{int(d.parent.name[2:])}.{int(d.name[2:4])}{d.name[4:].lower()}'
    title=html.parse(d/'index.html').xpath('//h1')[0].text_content()
    chunks=[]
    phases={}
    for page in ORDER:
        f=d/(page+'.html')
        root=html.parse(f)
        for node in root.xpath('//input[@name="lernweg"]/parent::*'):
            node.set('class','pdf-choice')
        content=root.xpath('//*[@id="inhalt"]')[0]
        headers=content.xpath('./header[h1]')
        section_heading=content.xpath('.//h1[1]')
        display=section_heading[0].text_content() if section_heading else PHASES.get(page,page)
        if page=='index':display='Orientierung'
        if headers:headers[0].drop_tree()
        elif section_heading:section_heading[0].drop_tree()
        if page in PHASES:
            tasks=content.xpath('.//*[@data-task-number]')
            structured=[numbered_task(node) for node in tasks]
            phases[page]=structured
            for node, task in zip(tasks,structured):
                node.getparent().replace(node,fragment(task_html(task,ls))[0])
        for node in content.xpath('.//*[@id="wahlhinweis"]'):
            node.drop_tree()
        for node in content.xpath('.//*[@data-require-path]'):
            node.attrib.pop('hidden',None)
        for node in content.xpath('.//*[@data-current-path]/parent::*'):
            node.drop_tree()
        for node in content.xpath('.//*[@data-result or @ID="quiz-result"]'):
            if node.get('id')=='quiz-result':node.drop_tree()
        chunks.append(f'<section class="pdf-chapter"><h2>{escape(display)}</h2>{body(clean(content))}</section>')
    # The material index links to the same public material pages available in the course.
    seen=set()
    index=html.parse(d/'materialien.html')
    for a in index.xpath('//a[starts-with(@href,"material/")]'):
        local=urlsplit(a.get('href')).path
        if not local.endswith('.html') or local in seen or Path(local).name in ('ls-glossar.html','fachwoerter.html'):continue
        seen.add(local)
        actual=d/unquote(local)
        if not actual.is_file():continue
        tree=html.parse(actual); nodes=tree.xpath('//main')
        node=nodes[0] if nodes else tree.getroot().find('body')
        if node is None:continue
        for shortcut in node.xpath('.//nav|.//a[contains(@class,"skip")]'):
            shortcut.drop_tree()
        cleaned=body(clean(node,str(Path(local).parent)+'/'))
        chunks.append(f'<section class="pdf-chapter" id="pdf-material-{actual.stem}">{cleaned}</section>')
    for extra in ('peer-check',):
        main=html.parse(d/(extra+'.html')).xpath('//main')[0]
        for x in main.xpath('.//*[contains(@class,"nur-bildschirm") or contains(@class,"rueckweg") or contains(@class,"wahl")]'):
            x.drop_tree()
        for x in main.xpath('.//*[@data-role]'):
            x.attrib.pop('hidden',None)
        chunks.append(f'<section class="pdf-chapter">{body(clean(main))}</section>')
    return ls,title,phases,chunks

def office_plan(d):
    source=(d/'data.js').read_text().strip()
    content=json.loads(source[len('window.LESSON='):-1])
    title='Büro mit Zukunft'
    ls='6.9'
    chunks=[]
    phases={}
    for phase, source in content['pages'].items():
        node=fragment(source)
        if phase=='durchfuehren':
            chosen=node.xpath('.//*[@id="chosen-material"]')[0]
            for code,value in content['materials'].items():
                chosen.append(fragment(f'<section class="pdf-task" data-pdf-path="{code}">{value}</section>')[0])
            phases[phase]=[(code,f'Lernweg {code} · 60 Min.',body(clean(fragment(value)))) for code,value in content['materials'].items()]
        elif phase=='informieren':
            phases[phase]=[(None,'Auftrag zu '+el.findtext('summary'),'<p>Arbeite mit diesem Material und halte deine Beobachtungen für den Arbeitsplatzcheck fest.</p>') for el in node.xpath('.//details[@class="card"]')]
        elif phase in PHASES:
            phase_node=fragment(source)
            for x in phase_node.xpath('.//h1|.//h2|.//article'):
                x.drop_tree()
            phases[phase]=[(None,PHASES[phase],body(clean(phase_node)))]
        if phase=='informieren':
            check=node.xpath('.//*[@id="quiz0"]')
            if check:
                for i,q in enumerate(content['quiz0'],1):
                    key=f'index.html#handlungssituation::office-check-{i}'
                    options=''.join(f'<li>○ <span data-edit-text="{key}-a{j}">{escape(answer)}</span></li>' for j,answer in enumerate(q['o']))
                    check[0].append(fragment(f'<p data-edit-text="{key}-q">{escape(q["q"])}</p><ul>{options}</ul>')[0])
                    check[0].append(fragment(f'<ul>{options}</ul>')[0])
        chunks.append(f'<section class="pdf-chapter">{body(clean(node))}</section>')
    return ls,title,phases,chunks

def wire_main(d,ls):
    runtime=d/'assets/runtime.js'
    value=runtime.read_text()
    marker='  window.GB = {'
    if 'getPath: () => session.read().path' not in value:
        runtime.write_text(value.replace(marker,marker+'\n    getPath: () => session.read().path,',1))
    for f in d.rglob('*.html'):
        if f.name in ('scorm.html','druckansicht.html') or 'pdf' in f.relative_to(d).parts:continue
        src=f.read_text()
        if 'data-document-pdf' in src:continue
        sub='../'*(len(f.relative_to(d).parts)-1)
        src=src.replace('</head>',f'<link rel="stylesheet" href="{sub}assets/pdf-ui.css"><script defer src="{sub}assets/pdf-ui.js"></script></head>',1)
        phase=f.stem
        if not sub and phase in PHASES:
            src=re.sub(r'(<header class="gb-intro"[^>]*>.*?</header>)',lambda m:m[0]+phase_box(phase,ls),src,count=1,flags=re.S)
        if 'class="gb-footerline"' in src:
            src=src.replace('</footer>',footer()+'</footer>',1)
        elif '</main>' in src.lower():
            src=re.sub(r'</main>',lambda m:'<footer class="bfs-material-footer">'+footer(sub)+'</footer>'+m[0],src,count=1,flags=re.I)
        else:
            src=re.sub(r'</body>',lambda m:footer(sub)+m[0],src,count=1,flags=re.I)
        f.write_text(src)

def wire_office(d):
    f=d/'index.html';s=f.read_text()
    app=d/'app.js'
    current=app.read_text()
    corrected=current.replace("document.querySelectorAll('nav a')", '''document.querySelectorAll('nav.navigation a[href^="#"]')''')
    if corrected!=current:app.write_text(corrected)
    if 'data-document-pdf' in s:return
    s=s.replace('</head>','<link rel="stylesheet" href="assets/pdf-ui.css"></head>')
    s=s.replace('<div id="page"', '<nav class="bfs-phase-export" data-office-exports hidden aria-label="Arbeitsblatt für diese Phase"><a class="button" download><img src="assets/goodnotes.png" alt="">GoodNotes-Export</a><a href="#entscheiden" data-export-pick hidden>Wähle zuerst deinen Lernweg.</a></nav><div id="page"',1)
    s=s.replace('</footer>',footer()+'</footer>',1).replace('</body>','<script src="assets/pdf-ui.js"></script></body>',1)
    f.write_text(s)
    f=d/'app.js';s=f.read_text()
    marker='if(active&&!location.hash)'
    assert marker in s
    f.write_text(s.replace(marker,'window.BFS_OFFICE_PATH=()=>state.v.paket;\n'+marker,1))

def manifest(d,added):
    f=d/'imsmanifest.xml';t=ET.parse(f);r=t.find('.//{*}resource')
    existing={x.get('href') for x in r}
    for name in sorted(set(added)-existing):
        ET.SubElement(r,f'{{{NS}}}file',href=name)
    ET.indent(t)
    t.write(f,encoding='utf-8',xml_declaration=True)

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()

def render(work):
    d, ls,title,phases,base = work
    pdf=d/'pdf'
    with sync_playwright() as p:
        engine=os.environ.get('BFS_CHROMIUM') or shutil.which('chromium')
        browser=p.chromium.launch(executable_path=engine,args=['--no-sandbox'])
        page=browser.new_page()
        def make(url,dest):
            page.goto(url,wait_until='load')
            page.evaluate('Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))')
            page.evaluate("""document.querySelectorAll('a[href]').forEach(a=>{if(new URL(a.href).origin===location.origin)a.removeAttribute('href')})""")
            data=page.pdf(prefer_css_page_size=True,print_background=True)
            f=fitz.open(stream=data,filetype='pdf')
            assert f.page_count and all(p.get_text().strip() or p.get_images() for p in f),dest
            assert all(abs(p.rect.width-595.28)<3 and abs(p.rect.height-841.89)<3 for p in f),dest
            dest.write_bytes(data)
            return ' '.join(' '.join(sheet.get_text() for sheet in f).split())
        written=[]
        for phase,items in phases.items():
            for code in ('A','B','C') if phase=='durchfuehren' else ('',):
                nodes=[]
                for item in items:
                    if item[0] and code and item[0]!=code:continue
                    section=heading(title,ls,PHASES[phase],'../assets/bbs1-aurich.svg')
                    section+=task_html((None,item[1],item[2]),ls,large=True)
                    nodes.append(f'<section class="workbook-sheet">{section}</section>')
                assert nodes,(ls,phase,code)
                dest=d/download(phase,ls,code)
                scratch=pdf/f'_render-{phase}-{code}.html'
                scratch.write_text(add_page(title,''.join(nodes),'pdf-workbook',css='../assets/pdf-document.css'))
                printed=make(base+'/pdf/'+scratch.name,dest)
                assert PHASES[phase] in printed and ('Notizen' in printed or '5-mm-Karo' in printed),(ls,phase,code)
                if code:
                    assert f'Lernweg {code}' in printed,(ls,phase,code,printed[:300])
                    assert all(f'Lernweg {other}' not in printed for other in 'ABC' if other!=code),(ls,phase,code)
                scratch.unlink()
                written.append(download(phase,ls,code))
        make(base+'/druckansicht.html',pdf/f'Gesamtdokument-LS-{ls}.pdf')
        browser.close()
    manifest(d,[*written,f'pdf/Gesamtdokument-LS-{ls}.pdf','druckansicht.html','assets/pdf-ui.js','assets/pdf-ui.css','assets/pdf-document.css','assets/goodnotes.png'])
    print(f'LS {ls}: {len(written)} Phasen-PDFs und Gesamtdokument',flush=True)

def main():
    all_dirs=[*sorted(BFS.glob('LF0[123]/LS*')),OFFICE]
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=ROOT))
    Thread(target=server.serve_forever,daemon=True).start()
    builds=[]
    selected=set(os.environ.get('BFS_PDF_CASES','').split())
    for d in all_dirs:
        case='6.9' if d==OFFICE else f'{int(d.parent.name[2:])}.{int(d.name[2:4])}{d.name[4:].lower()}'
        if selected and case not in selected:continue
        ls,title,phases,chunks=(office_plan if d==OFFICE else source_plan)(d)
        for name in ('pdf-ui.js','pdf-ui.css','pdf-document.css'):
            shutil.copyfile(HERE/name,d/'assets'/name)
        shutil.copyfile(BRC/'assets/goodnotes.png',d/'assets/goodnotes.png')
        (d/'pdf').mkdir(exist_ok=True)
        interactive_view(d,title,ls,chunks,'index.html')
        (wire_office if d==OFFICE else lambda d: wire_main(d,ls))(d)
        base=f'http://127.0.0.1:{server.server_port}/'+quote(d.relative_to(ROOT).as_posix())
        builds.append((d,ls,title,phases,base))
    with ThreadPoolExecutor(3) as pool:
        list(pool.map(render,builds))
    if selected and '6.9' not in selected:return
    zpath=OFFICE.parent/'LS_6_9_Buero_mit_Zukunft_Erklaerbilder_SCORM12.zip'
    with ZipFile(zpath,'w',ZIP_DEFLATED) as z:
        for f in sorted(OFFICE.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(OFFICE))
        assert z.testzip() is None

if __name__=='__main__':
    main()
