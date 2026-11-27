"""Apply the common BFS dual editor, checks and BRC XP presentation."""
import json
import re
import shutil
import sys
from pathlib import Path
from html import escape
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

from lxml import html, etree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BFS = ROOT/'Fachbereiche/BFSdual'
BRC = ROOT/'Fachbereiche/BRC/LG01/LS04'
OFFICE = BFS/'LF06/Buero/LS09'
ANSWERS = json.loads((HERE/'answers.json').read_text())
NS = 'http://www.imsproject.org/xsd/imscp_rootv1p1p2'
ET.register_namespace('', NS)
ET.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')
ICONS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 3-1 3-3 1-2 3 2 2-1 3 2 3 3-1 3 3 3-3 3 1 2-3-1-3 2-2-2-3-3-1-1-3z"/><circle cx="12" cy="11" r="3"/></svg>'
STATIONS = ('index','handlungssituation','informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren')

def tag(tagname,text=None, **attrs):
    obj=etree.Element(tagname,attrs)
    obj.text=text
    return obj

def serialize(doc):
    return html.tostring(doc,encoding='unicode',method='html',doctype='<!doctype html>')

def file_js(path,key,content):
    path.write_text(key+'='+json.dumps(content,ensure_ascii=False).replace('<','\\u003c')+';\n')

def manifest(folder):
    filename=folder/'imsmanifest.xml'
    t=ET.parse(filename)
    return filename,t,t.find('.//{*}resource')

def resource_add(folder,paths):
    filename,t,res=manifest(folder)
    existing={node.get('href') for node in res}
    for path in sorted(set(paths)-existing):
        ET.SubElement(res,'{'+NS+'}file',href=path)
    ET.indent(t)
    t.write(filename,encoding='utf-8',xml_declaration=True)

def id_for(folder):
    return manifest(folder)[1].getroot().get('identifier')

def title_and_n(folder):
    if folder==OFFICE:return 'Büro mit Zukunft','6.9'
    t=html.parse(folder/'index.html')
    return t.xpath('//h1')[0].text_content(),f'{int(folder.parent.name[2:])}.{int(folder.name[2:4])}{folder.name[4:].lower()}'

def slot(kind):
    title={'peer':'Peer-Check in Moodle','feedback':'Feedback in Moodle','knowledge':'Optionaler Wissens-Check in Moodle'}[kind]
    root=tag('aside',**{'class':'bfs-moodle-slot','data-edit-moodle':kind})
    root.append(tag('span',title+' · Link folgt.',**{'class':'bfs-link-placeholder'}))
    root.append(tag('a',title,hidden='',target='_blank',rel='noopener noreferrer'))
    return root

def mark(node,path):
    n=0
    qs=node.xpath('.//fieldset[@data-right or @data-answer]')
    for i,check in enumerate(qs,1):
        check.set('data-edit-check',f'{path}::check-{i}')
        for j,entry in enumerate(check.xpath('./legend|./label/span'),1):
            entry.set('data-edit-text',f'{path}::check-{i}-text-{j}')
    editable_root=node.xpath('.//*[@id="inhalt"]') or node.xpath('.//main')
    host=editable_root[0] if editable_root else node
    for child in host.xpath('.//p|.//h1|.//h2|.//h3|.//li|.//figcaption'):
        if child.xpath('./*') or not (child.text or '').strip():continue
        if child.xpath('ancestor::fieldset|ancestor::nav|ancestor::footer|ancestor::*[@data-edit-moodle]'):continue
        if child.get('id') in ('wahlhinweis','chosen','finish-msg','quiz-result','status'):continue
        if set(child.attrib) & {'data-runtime-status','data-finish-hint','data-assessment-widget'}:continue
        n+=1;child.set('data-edit-text',f'{path}::text-{n}')
    for i,img in enumerate(host.xpath('.//img[not(ancestor::nav) and not(ancestor::footer)]'),1):
        img.set('data-edit-image',f'{path}::image-{i}')
    return [
        {'key':check.get('data-edit-check'),'answer':int(check.get('data-answer',check.get('data-right')))}
        for check in qs
    ]

def decorate(doc,path):
    stem=Path(path).stem
    prefix='../'*(len(Path(path).parts)-1)
    head=doc.find('head')
    head.append(tag('link',rel='stylesheet',href=prefix+'assets/editor.css'))
    config=tag('script',src=prefix+'assets/editor-config.js',defer='')
    logic=tag('script',src=prefix+'assets/editor-settings.js',defer='')
    scripts=head.xpath('./script')
    idx=head.index(scripts[0]) if scripts else len(head)
    head.insert(idx,config);head.insert(idx+1,logic)
    doc_body=doc.find('body')
    for target in doc.xpath('//*[@data-document-pdf]'):
        link=html.fragment_fromstring(f'<a class="bfs-editor-link" href="{prefix}lehrkraft.html">{ICONS}<span>Editor</span></a>')
        target.addprevious(link)
    if stem in (*STATIONS,'begriffstraining','materialien'):
        for script in ('points-ui','bfs-xp-config','bfs-checks-xp'):
            head.append(tag('script',src=prefix+f'assets/{script}.js',defer=''))
    if stem in (*STATIONS[1:],):
        for e in doc.xpath('//header[contains(@class,"gb-intro")]/p[not(contains(@class,"eyebrow"))]'):
            e.drop_tree()
    host=doc.xpath('//*[@id="inhalt"]') or doc.xpath('//main')
    if host:
        choices={'bewerten':'peer','peer-check':'peer','reflektieren':'feedback','feedback':'feedback',
                 'materialien':'knowledge'}
        if stem in choices:
            kind=choices[stem]
            additions=host[0].xpath('.//*[@data-finish]') if stem=='reflektieren' else []
            if additions:additions[0].addprevious(slot(kind))
            else:host[0].append(slot(kind))
    return mark(doc,path)

def situation(doc,n):
    sections=doc.xpath('//section[contains(concat(" ",@class," ")," extra-task ")]')
    assert len(sections)==len(ANSWERS[n])+1,(n,len(sections))
    read=sections[0]
    text=read.xpath('./h3|./span[@data-task-id]|./label[@class="gb-done"]')
    removed=read.xpath('./span[@data-task-id]')[0].get('data-task-id')
    for node in text:node.drop_tree()
    for i,(section,options) in enumerate(zip(sections[1:],ANSWERS[n])):
        heading=section.xpath('./h3')[0]
        response=section.xpath('.//textarea[@data-response]')[0]
        task_id=response.get('data-response')
        timing=section.xpath('./span[@data-task-minutes]')
        right=i%3
        alternatives=list(options[1:]);alternatives.insert(right,options[0])
        card=tag('fieldset',**{'class':'bfs-mc','data-situation-question':task_id,'data-right':str(right),
                              'data-explain':'Die Antwort ergibt sich aus der Handlungssituation.'})
        card.append(tag('legend',heading.text_content().strip()))
        for j,option in enumerate(alternatives):
            l=tag('label',**{'class':'bfs-mc-option'})
            l.append(tag('input',type='radio',name=task_id,value=str(j)))
            l.append(tag('span',' '+option))
            card.append(l)
        card.append(tag('p','',**{'data-situation-feedback':'','aria-live':'polite'}))
        for item in timing:card.append(item)
        section.getparent().replace(section,card)
    return removed

def editor_page(title, n, office):
    attr=' data-office=""' if office else ''
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Editor · {title}</title><link rel="stylesheet" href="assets/{'styles.css' if office else 'global-bike.css'}"><link rel="stylesheet" href="assets/editor.css">
<script defer src="assets/editor-config.js"></script><script defer src="assets/editor-settings.js"></script><script defer src="assets/jszip.min.js"></script><script defer src="assets/editor.js"></script></head>
<body class="bfs-editor-page" data-teacher="true"{attr}><div class="shell"><header class="brand-header"><strong>BFS dual · Global Bike · LS {n}</strong><img src="assets/bbs1-aurich.svg" alt="BBS 1 Aurich"></header><main class="main">
<div class="editor-intro"><nav aria-label="Editor"><a href="index.html">Zur Lernsituation</a></nav><h1>Editor</h1><p>{title}</p></div>
<section class="teacher-card" id="teacher-login"><label>PIN<input id="teacher-pin" type="password" inputmode="numeric" maxlength="4" autocomplete="off"></label><button id="teacher-unlock" type="button">Öffnen</button><p id="teacher-login-message" role="status"></p></section>
{(HERE/'editor-panel.html').read_text()}
</main></div></body></html>'''

def add_progress(runtime, removed):
    src=runtime.read_text()
    src=src.replace("const api = findAPI(window) || findAPI(window.opener);",
        "const api = window.BFS_EDITOR?.preview ? null : (findAPI(window) || findAPI(window.opener));")
    src=src.replace("const localKey = packageId + ':' + root.pathname;",
        "const localKey = packageId + ':' + root.pathname + (window.BFS_EDITOR?.preview ? ':editor-preview' : '');")
    src=src.replace("    getPath: () => session.read().path,", """    getPath: () => session.read().path,
    snapshot: () => session.read(),
    answerSituation(id, choice, right) {
      if (!(requirements.responses || []).includes(id) || ![0,1,2].includes(choice)) return false;
      return session.change(state => {
        if (state.done.includes(id)) return;
        const old = state.responses[id];
        const first = typeof old === 'string' && old.startsWith('mc:') ? old.split(':')[1] : Number(choice===right);
        state.responses[id] = 'mc:' + first + ':' + choice;
        if (choice===right) state.done.push(id);
      });
    },""")
    src=src.replace("return session.change(s => { s.check = value.slice(); });", """return session.change(s => {
        s.checkFirst ||= Array(checkCount).fill(null);
        value.forEach((choice, i) => { if (s.checkFirst[i] == null) s.checkFirst[i]=choice; });
        s.check = value.slice();
      });""")
    needle="  }\n  const initial = session.read();"
    assert needle in src
    src=src.replace(needle,"    window.dispatchEvent(new Event('bfs-progress'));\n"+needle,1)
    runtime.write_text(src)
    req=runtime.with_name('requirements.js')
    s=req.read_text()
    expr=re.compile(r'(window\.GB_REQUIREMENTS=)(\{[^;]+\})')
    m=expr.search(s)
    data=json.loads(m[2])
    data['common']=[i for i in data['common'] if i!=removed]
    req.write_text(s[:m.start(2)]+json.dumps(data,ensure_ascii=False)+s[m.end(2):])

def apply_office(folder):
    f=folder/'data.js'
    data=json.loads(f.read_text().strip()[len('window.LESSON='):-1])
    for key, source in data['pages'].items():
        root=html.fragment_fromstring(source,create_parent='div')
        if key in ('bewerten','reflektieren'):
            root.append(slot('peer' if key=='bewerten' else 'feedback'))
            if key=='bewerten':root.append(slot('knowledge'))
        mark(root,'index.html#'+key)
        data['pages'][key]=''.join(html.tostring(c,encoding='unicode') for c in root)
    file_js(f,'window.LESSON',data)
    f=folder/'app.js';s=f.read_text()
    s=s.replace("const storage='global-bike-buero-v1';","const storage='global-bike-buero-v1'+(window.BFS_EDITOR?.preview?':editor-preview':'');")
    s=s.replace("api=find(window)||find(window.opener);","api=window.BFS_EDITOR?.preview ? null : (find(window)||find(window.opener));")
    s=s.replace("$('#page').innerHTML=D.pages[page];","$('#page').innerHTML=D.pages[page];window.BFS_EDITOR?.apply($('#page'));")
    s=s.replace("function save(){if(readonly)return;", "function save(){window.dispatchEvent(new Event('bfs-office-progress'));if(readonly)return;")
    s=s.replace('window.BFS_OFFICE_PATH=()=>state.v.paket;',"""window.BFS_OFFICE_PATH=()=>state.v.paket;
window.BFS_OFFICE_XP=()=>{
 const qOK=D.quiz0.filter((q,i)=>state.q0[i] && q.k.every(k=>state.q0[i].includes(k)) && q.k.length===state.q0[i].length).length;
 const done=['paket','grund','check0','check1','check2','check3','check4','check5','abgabe','feedback'].filter(k=>state.v[k]).length;
 return {points:Math.round((60*qOK/Math.max(1,D.quiz0.length)+40*done/10)*100)/100,maxPoints:100};
};""")
    f.write_text(s)
    page=folder/'index.html'
    doc=html.parse(page).getroot()
    decorate(doc,'index.html')
    head=doc.find('head')
    for n in head.xpath('./script[@src="assets/bfs-checks-xp.js" or @src="assets/points-ui.js"]'):n.drop_tree()
    for file in ('points-ui.js','bfs-checks-xp.js'):
        doc.find('body').append(tag('script',src='assets/'+file,defer=''))
    head.append(tag('link',rel='stylesheet',href='assets/progress.css'))
    for script in doc.xpath('//script[@src="data.js" or @src="app.js" or @src="assets/pdf-ui.js"]'):
        script.set('defer','')
    page.write_text(serialize(doc))
    shutil.copyfile(ROOT/'Formmaster/assets/progress.css',folder/'assets/progress.css')

def main():
    for folder in ([Path(v).resolve() for v in sys.argv[1:]] or [*sorted(BFS.glob('LF0[123]/LS*')),OFFICE]):
        if (folder/'lehrkraft.html').exists():raise ValueError(f'Editor already exists: {folder}')
        title,n=title_and_n(folder);ident=id_for(folder)
        for original,name in [('settings.js','editor-settings.js'),('editor.js','editor.js'),('editor.css','editor.css'),
                              ('checks-xp.js','bfs-checks-xp.js')]:
            shutil.copyfile(HERE/original,folder/'assets'/name)
        shutil.copyfile(BRC/'assets/jszip.min.js',folder/'assets/jszip.min.js')
        shutil.copyfile(ROOT/'Formmaster/assets/points-ui.js',folder/'assets/points-ui.js')
        file_js(folder/'assets/editor-config.js','window.BFS_EDITOR_CONFIG',{'id':ident})
        (folder/'lehrkraft.html').write_text(editor_page(escape(title),n,folder==OFFICE))
        added=['lehrkraft.html','assets/editor-settings.js','assets/editor.js','assets/editor.css','assets/jszip.min.js',
               'assets/bfs-checks-xp.js','assets/editor-config.js','assets/bfs-xp-config.js','assets/points-ui.js']
        terms=[]
        if folder==OFFICE:
            apply_office(folder)
            shutil.copyfile(ROOT/'Formmaster/assets/points-ui.js',folder/'assets/points-ui.js')
            added+=['assets/points-ui.js','assets/progress.css']
        else:
            removed=None
            for page in sorted(folder.rglob('*.html')):
                relative=page.relative_to(folder).as_posix()
                if relative in ('druckansicht.html','scorm.html','lehrkraft.html') or relative.startswith('pdf/'):continue
                doc=html.parse(page).getroot()
                if relative=='handlungssituation.html':removed=situation(doc,n)
                cards=decorate(doc,relative)
                if relative=='begriffstraining.html':terms=cards
                page.write_text(serialize(doc))
            assert removed and 10<=len(terms)<=20,(n,terms)
            add_progress(folder/'assets/runtime.js',removed)
        file_js(folder/'assets/bfs-xp-config.js','window.BFS_XP',{'terms':terms})
        resource_add(folder,added)
        print(n,ident,len(terms),flush=True)

if __name__=='__main__':main()
