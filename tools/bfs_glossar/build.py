"""Install the contextual, link-only glossary in the BFS dual SCORM masters."""
import json
import re
from copy import deepcopy
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlencode, urlsplit
import shutil
import xml.etree.ElementTree as ET
from lxml import html, etree

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BFS=ROOT/'Fachbereiche/BFSdual'
OFFICE=BFS/'LF06/Buero/LS09'
BOOK_ONLY={'ls-glossar.html','glossar.pdf','fachwoerter.html'}
NS='http://www.imsproject.org/xsd/imscp_rootv1p1p2'
ET.register_namespace('',NS)
ET.register_namespace('adlcp','http://www.adlnet.org/xsd/adlcp_rootv1p2')
ICON='<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5" stroke-linecap="round"/></svg>'

def serialize(page):
    return html.tostring(page,encoding='unicode',method='html',doctype='<!doctype html>')

def contextual_link(href, page, anchor):
    url=urlsplit(href)
    return url.path+'?'+urlencode({'from':page+('#'+anchor if anchor else '')})+'#'+url.fragment

def strip_generic(doc, anchor):
    parent=anchor.getparent()
    card=next((node for node in anchor.iterancestors('article') if 'gb-material-list' in (node.getparent().get('class') or '').split()),None)
    if card is not None:
        card.drop_tree()
        return
    if parent.tag=='p':
        before=''.join(parent.itertext()).strip()
        label=anchor.text_content().strip()
        if before==label:
            parent.drop_tree()
            return
        if not parent.xpath('.//a[not(contains(@href,"ls-glossar.html"))]'):
            rest=before.replace(label,'').strip(' ·|—.\n\t')
            if not rest:
                parent.drop_tree()
                return
    anchor.drop_tree()
    if parent.tag=='p' and not re.search(r'[\wÄÖÜäöüß]',parent.text_content()):
        parent.drop_tree()

def glossary(folder, glossary_entries, ls):
    blocks=[]
    for key,node in glossary_entries:
        node=deepcopy(node)
        node.set('id',key)
        node.set('class','glossary-entry')
        heading=node.xpath('./h2')[0]
        heading.set('id','glossary-heading-'+key)
        heading.set('tabindex','-1')
        if 'aria-labelledby' in node.attrib:node.set('aria-labelledby','glossary-heading-'+key)
        for a in node.xpath('.//a[contains(@class,"return-to-source")]'):
            if a.getparent().tag=='p' and len(a.getparent())==1:a.getparent().drop_tree()
            else:a.drop_tree()
        blocks.append(html.tostring(node,encoding='unicode',with_tail=False))
    template=f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Begriff nachschlagen · Global Bike · LS {ls}</title>
<link rel="stylesheet" href="assets/glossar.css">
<script defer src="assets/editor-config.js"></script><script defer src="assets/editor-settings.js"></script><script defer src="assets/glossar.js"></script>
</head><body class="bfs-glossary">
<main class="glossary-page"><header class="glossary-brand"><img src="assets/bbs1-aurich.svg" alt="BBS 1 Aurich"><img src="assets/loept.png" alt="Löppt"></header>
<p data-glossary-empty>Öffne einen verlinkten Begriff im Lernmaterial oder im Fachbegriffscheck.</p>
<div class="glossary-deck" data-glossary-deck hidden>{''.join(blocks)}</div></main>
<dialog class="glossary-panel" data-glossary-panel aria-label="Fachbegriff und Erklärung"><header class="glossary-panel-header">
<span>{ICON}Begriff nachschlagen</span><a class="glossary-back" href="index.html" data-glossary-back hidden>Zurück zur Textstelle</a><button type="button" class="glossary-close" data-glossary-close>Schließen</button>
</header><div data-glossary-entry></div></dialog></body></html>'''
    (folder/'ls-glossar.html').write_text(template)
    for asset in ('glossar.css','glossar.js'):
        shutil.copyfile(HERE/asset,folder/'assets'/asset)
    man=folder/'imsmanifest.xml'
    t=ET.parse(man); resource=t.find('.//{*}resource')
    existing={n.get('href') for n in resource}
    for name in ['assets/glossar.css','assets/glossar.js','ls-glossar.html']:
        if name not in existing:ET.SubElement(resource,'{'+NS+'}file',href=name)
    ET.indent(t);t.write(man,encoding='utf-8',xml_declaration=True)

def rewrite_page(folder,f,terms):
    rel=f.relative_to(folder).as_posix()
    d=html.parse(f).getroot()
    edited=False
    for a in d.xpath('//a[@href]'):
        path=urlsplit(a.get('href'))
        if path.scheme or path.netloc or not path.path:continue
        name=Path(path.path).name
        if name not in BOOK_ONLY:continue
        edited=True
        if name!='ls-glossar.html' or not path.fragment:
            # The learner reaches the glossary only from an actual term.
            before=a.getprevious()
            if before is not None and before.tag=='span' and before.text and before.text.rstrip().endswith('Für Fachwörter nutze das'):
                before.text=before.text.rstrip().removesuffix('Für Fachwörter nutze das').rstrip()
                if a.getnext() is not None and a.getnext().text in ('.',' .'):a.getnext().drop_tree()
            strip_generic(d,a)
            continue
        assert unquote(path.fragment) in terms,(folder,rel,a.get('href'))
        anchor=a.get('id')
        if not anchor:
            container=next((x for x in a.iterancestors() if x.get('id') and x.tag in ('fieldset','section','article') and x.get('id') not in ('inhalt','main')),None)
            if container is not None:anchor=container.get('id')
        if not anchor:
            i=1
            while d.xpath('//*[@id=$id]',id=f'glossar-stelle-{i}'):i+=1
            anchor=f'glossar-stelle-{i}';a.set('id',anchor)
        a.set('href',contextual_link(a.get('href'),rel,anchor))
    if edited:f.write_text(serialize(d))

def install(folder):
    doc=html.parse(folder/'ls-glossar.html')
    entries=[]
    for card in doc.xpath('//section[h2][@id or h2/@id]'):
        entries.append((card.get('id') or card.xpath('h2/@id')[0],card))
    assert entries
    terms={key for key,_ in entries}
    gallery=f'{int(folder.parent.name[2:])}.{int(folder.name[2:4])}{folder.name[4:].lower()}'
    glossary(folder,entries,gallery)
    for f in sorted(folder.rglob('*.html')):
        if f.name in ('ls-glossar.html','druckansicht.html'):continue
        rewrite_page(folder,f,terms)
    print(gallery,len(terms),'Glossarbegriffe',flush=True)

def office():
    details=json.loads((HERE/'office.json').read_text())
    entries=[]
    for id,title,definition,example in details:
        node=html.fragment_fromstring(f'<section><h2 data-edit-text="ls-glossar.html::{id}-1">{escape(title)}</h2><p data-edit-text="ls-glossar.html::{id}-2">{escape(definition)}</p><p data-edit-text="ls-glossar.html::{id}-3">{escape(example)}</p></section>')
        entries.append((id,node))
    glossary(OFFICE,entries,'6.9')
    d=OFFICE/'data.js'
    data=json.loads(d.read_text().strip()[len('window.LESSON='):-1])
    page=html.fragment_fromstring(data['pages']['informieren'],create_parent='div')
    for card in page.xpath('.//details[@class="card"]'):
        touched=set()
        for id,title,_,_ in details:
            aliases={'bueroform':r'Büroformen?','fluchtweg':r'Fluchtwege?','blickabstand':r'(?:Blick|Bildschirm)abstand'}
            token=re.compile(r'(?<![\w])'+aliases.get(id,re.escape(title))+r'(?![\w])',re.I)
            for block in card.xpath('./p|./p/span|./ul/li|./ul/li/span'):
                if block in touched or not block.text:continue
                text=block.text
                found=token.search(text)
                if not found:continue
                touched.add(block)
                marker='glossar-'+id
                tag=etree.Element('a',{'id':marker,'href':'ls-glossar.html?'+urlencode({'from':'index.html?glossarStelle='+marker+'#informieren'})+'#'+id})
                tag.text=found[0];tag.tail=text[found.end():]
                block.text=text[:found.start()]
                block.insert(0,tag)
                break
    data['pages']['informieren']=''.join(html.tostring(c,encoding='unicode') for c in page)
    d.write_text('window.LESSON='+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';\n')
    print('6.9',len(entries),'Glossarbegriffe',flush=True)

if __name__=='__main__':
    import sys
    if len(sys.argv)>1:
        for source in sys.argv[1:]:install(Path(source).resolve())
    else:
        for folder in sorted(BFS.glob('LF0[123]/LS*')):install(folder)
        office()
