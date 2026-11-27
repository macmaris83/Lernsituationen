"""BFS dual task focus, pathway selection, and BRC-backed Löppt-Pilot."""
import json
import re
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

from lxml import html, etree
from html import escape

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BRC=ROOT/'Fachbereiche/BRC/LG01/LS04/assets/runtime.js'
NS='http://www.imsproject.org/xsd/imscp_rootv1p1p2'
CHOICE_POINTS=1.92

def exactly(text,before,after):
    if text.count(before)!=1: raise ValueError(f'Expected one occurrence of {before}')
    return text.replace(before,after,1)

def pilot_config():
    ref=BRC.read_text()
    match=re.search(r'/\* LS_TASK_FOCUS_OPTIONS \*/(\{[^\n]+\})(?=\);)',ref)
    if not match:raise ValueError('Löppt-Pilot-Konfiguration fehlt in BRC')
    options=json.loads(match.group(1))
    url=urlsplit(options['aiHelpUrl'])
    if url.scheme!='https' or url.hostname!='app.ais-chat.schule' or not url.path.startswith('/ua/characters/'):
        raise ValueError('Löppt-Pilot-Ziel prüfen')
    return options

def save_html(path,node):path.write_text(html.tostring(node,encoding='unicode',doctype='<!doctype html>'))

def header_asset(doc,rel,files):
    head=doc.find('head')
    for name in files:
        url=rel+'assets/'+name
        if head.xpath('./*[@src=$url or @href=$url]',url=url):continue
        if name.endswith('.css'): tag=etree.Element('link',rel='stylesheet',href=url)
        else:tag=etree.Element('script',defer='',src=url)
        head.append(tag)

def patch_choice(folder):
    page=folder/'entscheiden.html'
    doc=html.parse(page).getroot()
    task=doc.xpath('//article[@data-task-id and contains(@class,"assignment-frame")]')[0]
    if task.get('data-bfs-choice') is None:
        task.set('data-bfs-choice','')
        host=task.xpath('./div[contains(@class,"assignment-body")]')[0]
        fieldset=doc.xpath('//fieldset[contains(@class,"gb-choice")]')[0]
        fieldset.set('data-bfs-choice-ui','')
        hint=etree.Element('p',{'class':'bfs-choice-status','data-bfs-choice-status':'','role':'status'})
        hint.text='Wähle A, B oder C, um „Durchführen“ freizuschalten.'
        host.insert(1,fieldset)
        host.insert(2,hint)
        save_html(page,doc)
    cfg=folder/'assets/requirements.js'
    body=cfg.read_text()
    if 'window.GB_REQUIREMENTS.choice=' not in body:
        cfg.write_text(body.rstrip()+'\nwindow.GB_REQUIREMENTS.choice='+json.dumps(task.get('data-task-id'))+';\n')

def patch_runtime(folder,options):
    path=folder/'assets/runtime.js'
    value=path.read_text()
    opts=re.compile(r'(/\* LS_TASK_FOCUS_OPTIONS \*/)(\{[^\n]+\})(?=\);)')
    value,count=opts.subn(lambda m:m[1]+json.dumps(options,ensure_ascii=False,separators=(',',':')),value)
    if count!=1:raise ValueError(path)
    before="el.disabled = session.locked || (field && !field.value.trim());"
    if before in value:
        value=exactly(value,before,
            "el.disabled = session.locked || (el.dataset.done === requirements.choice && !validPath(state.path)) || Boolean(field && !field.value.trim());")
    if 'refreshUI: render' not in value:
        value=exactly(value,'  window.GB = {','  window.GB = {\n    refreshUI: render,')
    path.write_text(value)
    css=folder/'assets/global-bike.css'
    s=css.read_text();css.write_text(s.replace('.gb-learning .focus-ai-help{display:none}\n',''))
    adapter=folder/'assets/focus-adapter.js'
    a=adapter.read_text()
    a=a.replace("    card.querySelector('.focus-ai-help')?.remove();\n",'')
    if 'bfs-pilot-dialog-escape' not in a:
        a=a.replace("  if (!cards.length) return;","""  if (!cards.length) return;
  // bfs-pilot-dialog-escape
  document.addEventListener('keydown',event=>{
    const dialog=document.querySelector('.ais-help-dialog[open]');
    if (event.key!=='Escape' || !dialog) return;
    event.preventDefault();event.stopImmediatePropagation();dialog.close();
  },true);""",1)
    if 'GB?.refreshUI()' not in a:
        # A cloned checked radio can take over its name group before the clone
        # inputs are removed. Reapply the persisted selection afterwards.
        a=exactly(a,'})();','  window.GB?.refreshUI();\n  window.SOZ_TASK_FOCUS?.refresh();\n})();')
    adapter.write_text(a)

def patch_office(folder,options):
    data=folder/'data.js'
    course=json.loads(data.read_text().strip()[len('window.LESSON='):-1])
    page=course['pages']['entscheiden']
    if 'data-bfs-choice-status' not in page:
        doc=html.fragment_fromstring(page,create_parent='div')
        picker=doc.xpath('.//select[@data-save="paket"]')[0]
        hint=etree.Element('p',{'class':'bfs-choice-status','data-bfs-choice-status':'','role':'status'})
        picker.addnext(hint)
        course['pages']['entscheiden']= ''.join(html.tostring(n,encoding='unicode') for n in doc)
        data.write_text('window.LESSON='+json.dumps(course,ensure_ascii=False).replace('<','\\u003c')+';\n')
    p=folder/'assets/bfs-checks-xp.js'
    app=folder/'app.js'
    s=app.read_text()
    s=s.replace("40*done/10","(38.08*(done-Number(Boolean(state.v.paket)))/9 + (state.v.paket?1.92:0))")
    app.write_text(s)
    doc=html.parse(folder/'index.html').getroot()
    if not doc.xpath('//*[@data-office-pilot]'):
        brc=BRC.read_text()
        logo=re.search(r"aiLogo\.innerHTML='([^']+)'",brc)
        if not logo:raise ValueError('AIS-Signet fehlt')
        area=html.fragment_fromstring('<aside hidden data-office-pilot data-pilot-url="'+escape(options['aiHelpUrl'])+'"><button type="button">'+logo[1]+'KI-Hilfe öffnen</button></aside>')
        doc.xpath('//*[@id="page"]')[0].addnext(area)
        save_html(folder/'index.html',doc)
    for name in ('office-pilot.js','office-pilot.css'):shutil.copyfile(HERE/name,folder/'assets'/name)

def extend_manifest(folder,names):
    path=folder/'imsmanifest.xml';tree=ET.parse(path)
    res=tree.find('.//{*}resource')
    ET.register_namespace('',res.tag.split('}')[0][1:] if res.tag.startswith('{') else NS)
    ET.register_namespace('adlcp','http://www.adlnet.org/xsd/adlcp_rootv1p2')
    known={i.get('href') for i in res}
    for name in sorted(set(names)-known):ET.SubElement(res,'{'+NS+'}file',href=name)
    ET.indent(tree);tree.write(path,encoding='utf-8',xml_declaration=True)

def apply(folder):
    folder=Path(folder)
    is_office=not (folder/'entscheiden.html').exists()
    options=pilot_config()
    if is_office:patch_office(folder,options)
    else:
        patch_choice(folder)
        patch_runtime(folder,options)
    assets=['fokus.css','lernweg.js']
    for name in assets:shutil.copyfile(HERE/name,folder/'assets'/name)
    xp=ROOT/'tools/bfs_editor/checks-xp.js'
    shutil.copyfile(xp,folder/'assets/bfs-checks-xp.js')
    if is_office:assets+=['office-pilot.js','office-pilot.css']
    for page in folder.rglob('*.html'):
        if page.name in ('druckansicht.html','ls-glossar.html','lehrkraft.html','scorm.html') or 'pdf' in page.relative_to(folder).parts:continue
        if is_office and page.name!='index.html':continue
        if page.name in ('peer-check.html','feedback.html'):continue
        doc=html.parse(page).getroot()
        rel='../'*(len(page.relative_to(folder).parts)-1)
        header_asset(doc,rel,assets)
        if is_office:
            for name in ('lernweg.js','office-pilot.js'):
                selected=doc.xpath('//script[@src=$url]',url='assets/'+name)[0]
                doc.find('body').append(selected)
        save_html(page,doc)
    extend_manifest(folder,['assets/'+name for name in assets])
