"""Render BFS material content using its repository's material surface templates."""
from functools import lru_cache
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
from lxml import html

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parents[2] / 'Materialvorlagen'
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
HEADINGS = set('h1 h2 h3 h4 h5 h6'.split())
RESOURCES = ('bfs-document-views.css','bfs-document-reader.css')
# Formal records and reading materials use PDF; methods and learner work stay in OneNote.
KINDS = {
 '1.1':{'m1':'acrobat'},'1.3':{'m3':'acrobat'},
 '2.1':{'m1':'outlook'},
 '2.2':{'m5':'sap'},
 '2.3':{'m02':'acrobat','m03':'acrobat'},
 '2.4':{'m1':'outlook','m2':'sap','m3':'acrobat','m8':'acrobat'},
 '2.5':{'m03':'sap'},
 '2.6a':{'m13':'acrobat','m14':'acrobat'},
 '2.6b':{'m1':'outlook','m2':'sap','m3':'sap','m4':'sap','m5':'acrobat','handbuch':'acrobat'},
 '3.1':{},'3.2':{},
 '3.3':{'m1':'sap','m2':'sap','m3':'acrobat','m4':'acrobat','m5':'acrobat','m6':'acrobat','m7':'acrobat'}
}
class MainChildren(HTMLParser):
    """Track raw main child spans. Existing HTML, links, editor IDs and SVG are retained byte-for-byte."""
    def __init__(self,s):
        super().__init__(convert_charrefs=False)
        self.raw=s;self.lines=[0]+[m.end() for m in re.finditer('\n',s)]
        self.open=[];self.children=[];self.start=None;self.end=None;self.at=None
        self.feed(s)
    def pos(self):
        line,col=self.getpos();return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        pos=self.pos()
        if self.start is None and tag=='main':
            self.start=pos+len(self.get_starttag_text());self.open=['main'];return
        if not self.open:return
        if len(self.open)==1:self.at=pos
        if tag not in VOID:self.open.append(tag)
        elif len(self.open)==1:self.children.append((self.at,pos+len(self.get_starttag_text())))
    def handle_startendtag(self,tag,attrs):
        if len(self.open)==1:
            p=self.pos();self.children.append((p,p+len(self.get_starttag_text())))
    def handle_endtag(self,tag):
        if tag not in self.open:return
        pos=self.pos()
        while self.open[-1]!=tag:self.open.pop()
        self.open.pop()
        if not self.open:self.end=pos
        elif len(self.open)==1:self.children.append((self.at,self.raw.index('>',pos)+1))


def clean(s):return ' '.join(s.split())

class Part:
    def __init__(self,raw):
        self.raw=raw;self.el=html.fromstring(raw)
        self.tag=self.el.tag;self.text=clean(self.el.text_content());self.cls=self.el.get('class') or ''
        self.outside=False;self.kind='';self.title='';self.meta='';self.group='';self.omit=False


def mail_fields(sender, recipient, subject):
    return '<dl class="bfs-mail-head">'+''.join('<div><dt>'+k+'</dt><dd>'+escape(val)+'</dd></div>' for k,val in [('Von',sender),('An',recipient),('Betreff',subject)])+'</dl>'


@lru_cache(maxsize=32)
def model(reference,kind):
    s=(Path(reference)/(kind+'.html')).read_text()
    begin=s.index('<div class="source-document">')
    end=s.index('</body>',begin)
    out=s[begin:end].strip().replace('class="source-document"','class="source-document" data-bfs-document=""',1)
    # Program chrome is decorative; let assistive readers go straight to the contents.
    out=out.replace('class="viewerbar"','class="viewerbar" aria-hidden="true"').replace('class="subbar"','class="subbar" aria-hidden="true"')
    start=out.index('<article class="paper">')+len('<article class="paper">')
    stop=out.index('</article>',start)
    return (out[:start],out[stop:])


def render(reference, kind, title, content):
    before,after=model(str(reference),kind)
    return before.replace('[Dokumenttitel]',escape(title))+content+after


def categorize(parts,n,stem):
    h=next((p.text for p in parts if p.tag=='h1'),stem)
    base=KINDS.get(n,{}).get(stem,'onenote')
    for p in parts:
        p.kind=base;p.title=h;p.group='base'
        if p.tag in ('nav','footer','header','script','style') or 'bfs-material-slot' in p.raw or p.tag=='a' and 'Materialübersicht' in p.text:
            p.outside=True
        if p.cls in ('dateilink','material-caption') or p.tag=='p' and (p.text.startswith(('BFS dual · Lernfeld','Text als Markdown herunterladen','Material als bearbeitbare Markdown-Datei')) or p.el.xpath('.//a[@download]') and not re.search(r'\w',p.el.text or '')):
            p.outside=True
    def assign(start,end,kind,title,meta=''):
        for p in parts[start:end]:
            p.kind=kind;p.title=title;p.group=str(start)
        parts[start].meta=meta
    def headblock(match,kind,title=None,fields=None,skip=()):
        for i,p in enumerate(parts):
            if p.tag not in HEADINGS or not re.search(match,p.text,re.I):continue
            end=next((j for j in range(i+1,len(parts)) if parts[j].tag in HEADINGS or parts[j].outside),len(parts))
            assign(i,end,kind,title or p.text,mail_fields(*fields) if fields else '')
            for q in parts[i+1:end]:
                if q.text in skip:q.omit=True

    if (n,stem)==('2.2','m5'):
        for p in parts:
            if p.tag in HEADINGS and p.text=='Ergänzende ausführliche Arbeitsfassung (rekonstruiert)':p.omit=True
        i=next(i for i,p in enumerate(parts) if p.tag=='h3' and p.text.startswith('M5.1'))
        for p in parts[i:]:p.kind='onenote'
        headblock(r'^M5\.1\b','outlook','Produktauswahl für regionale Geschäftskunden',
                  ('Sebastian Wolf · Außendienst','Verkaufsteam','Produktauswahl für regionale Geschäftskunden'))
    if (n,stem)==('2.2','m6'):
        headblock(r'^M6\.1\b','outlook','Argumente für das Verkaufsgespräch',
                  ('Jan Richter · Leitung Verkauf und Marketing','Verkaufsteam','Argumente für das Verkaufsgespräch'))
    if (n,stem)==('2.2','m2'):
        headblock(r'^M2\.1\b','outlook','Erste Kundenanfragen aus der Region Nordwest',
                  ('Sebastian Wolf · Außendienst','Verkaufsteam','Erste Kundenanfragen aus der Region Nordwest'),
                  skip=('Darstellung als E-Mail:','Empfänger:in'))
    if (n,stem)==('2.2','m1'):
        i=next(i for i,p in enumerate(parts) if p.text.startswith('Interne Mitteilung'))
        assign(i,i+2,'outlook','Betrieblicher Arbeitsauftrag',mail_fields('Jan Richter · Vertriebsleitung','Verkaufsteam','Beratungsgespräche mit regionalen Fahrradhändlern'))
    if (n,stem)==('2.1','m1'):
        for i,p in enumerate(parts):
            if p.tag=='section' and p.el.xpath('.//h2'):assign(i,i+1,'outlook',clean(p.el.xpath('.//h2')[0].text_content()))
            else:p.outside=True
    if (n,stem)==('2.1','m2'):
        for i,p in enumerate(parts):
            if p.el.xpath('.//table') or p.tag=='table':
                if 'Debitor' in p.text:assign(i,i+2,'sap','Kundenstammdaten · Alster Cycling e.K.')
    if (n,stem)==('2.4','m1'):
        for p in parts:
            if p.tag=='h1' or p.tag=='p' and p.text.startswith('Materialart:'):p.outside=True
        headblock(r'^M1\.1\b','outlook','Angebotsanfrage – Deluxe Touringbike Silber')
        headblock(r'^M1\.2\b','outlook','Weitere Bearbeitung der Anfrage von Alster Cycling')
    if (n,stem)==('2.4','ue4'):headblock(r'^Kundenanfrage$','outlook','Kundenanfrage')
    if (n,stem)==('2.2','m7'):headblock(r'^Beratungsprotokoll$','teams','Besprechungsnotizen · Beratungsprotokoll')
    if (n,stem)==('3.3','m8'):headblock(r'^E-Mail-Vorlage','outlook','E-Mail-Entwurf · Formulierungshilfe')
    if (n,stem)==('2.2','m8'):headblock(r'Simulationspreisliste','sap','Simulierte Verkaufspreise')
    return parts


def transform(path,folder,n,reference):
    s=path.read_text()
    if 'data-bfs-document=""' in s:return False
    doc=MainChildren(s)
    if not doc.children or doc.end is None:raise ValueError(f'Kein Dokumenthaupttext in {path}')
    parts=categorize([Part(s[a:b]) for a,b in doc.children],n,path.stem)
    output=[];pending=[];group=None
    def flush():
        if pending:
            first=pending[0]
            content='\n'.join((p.raw+p.meta if p.tag in HEADINGS else p.meta+p.raw) for p in pending)
            output.append(render(reference,first.kind,first.title,content))
            pending.clear()
    for part in parts:
        if part.omit:continue
        if part.outside:
            flush();output.append(part.raw)
            if part.tag=='header' and 'bfs-material-brand' in part.cls and 'data-bfs-material-slot' not in s:
                output.append('<div data-bfs-material-slot></div>')
        else:
            key=(part.kind,part.group)
            if key!=group:flush()
            pending.append(part);group=key
    flush()
    result=s[:doc.start]+'\n'+'\n'.join(output)+'\n'+s[doc.end:]
    prefix='../'*(len(path.relative_to(folder).parts)-1)
    css=''.join(f'<link rel="stylesheet" href="{prefix}assets/{f}">' for f in RESOURCES)
    path.write_text(result.replace('</head>',css+'</head>',1))
    return True


def office_materials(folder,reference):
    import json
    file=folder/'data.js'
    course=json.loads(file.read_text().strip()[len('window.LESSON='):-1])
    source=html.fragment_fromstring(course['pages']['informieren'],create_parent='div')
    count=0
    for item in source.xpath('.//details[@class="card"][summary]'):
        title=item.findtext('summary')
        if not title or not re.match(r'^M0[1-5]\b',title) or item.xpath('./*[@data-bfs-document]'):continue
        content=[]
        for child in list(item):
            if child.tag=='summary':continue
            content.append(html.tostring(child,encoding='unicode'))
            item.remove(child)
        doc=render(reference,'acrobat',title,''.join(content))
        item.append(html.fragment_fromstring(doc))
        count+=1
    if count:
        course['pages']['informieren']=''.join(html.tostring(n,encoding='unicode') for n in source)
        file.write_text('window.LESSON='+json.dumps(course,ensure_ascii=False).replace('<','\\u003c')+';\n')
    page=folder/'index.html'
    old=page.read_text()
    if RESOURCES[0] not in old:
        styles=''.join(f'<link rel="stylesheet" href="assets/{name}">' for name in RESOURCES)
        page.write_text(old.replace('</head>',styles+'</head>',1))
    return count


def apply(folder,reference=None):
    folder=Path(folder).resolve()
    ref=Path(reference) if reference else next((p.parent/'Materialvorlagen' for p in folder.parents if p.name=='Fachbereiche'),REFERENCE)
    if not (ref/'outlook.html').is_file():ref=REFERENCE
    if (folder/'data.js').is_file() and not (folder/'material').exists():
        count=office_materials(folder,ref)
    else:
        return multipage_materials(folder,ref)
    install_assets(folder,ref)
    return count


def multipage_materials(folder,ref):
    learn_id=re.search(r'BFSDUAL-LF(\d+)-LS(\d+)([A-Z]?)',(folder/'assets'/'requirements.js').read_text())
    if not learn_id:raise ValueError(f'Paketkennung fehlt bei {folder}')
    lf,ls,suffix=learn_id.groups()
    n=f'{int(lf)}.{int(ls)}{suffix.lower()}'
    count=sum(transform(f,folder,n,ref) for f in sorted((folder/'material').rglob('*.html')))
    install_assets(folder,ref)
    return count


def install_assets(folder,ref):
    shutil.copyfile(ref/'assets/material-views.css',folder/'assets'/RESOURCES[0])
    shutil.copyfile(HERE/'reader.css',folder/'assets'/RESOURCES[1])
    manifest=folder/'imsmanifest.xml'
    if manifest.is_file():
        s=manifest.read_text()
        paths={f.get('href') for f in ET.fromstring(s).iter() if f.tag.split('}')[-1]=='file'}
        adds=''.join(f'      <file href="assets/{f}" />\n' for f in RESOURCES if 'assets/'+f not in paths)
        if adds:manifest.write_text(s.replace('</resource>',adds+'</resource>',1))

