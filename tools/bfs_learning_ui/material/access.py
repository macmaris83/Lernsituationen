"""Install the BFS material switcher into a prepared learner package."""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit,unquote
import json
import re
import shutil
from lxml import html

HERE=Path(__file__).resolve().parent
PHASES=('handlungssituation','informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren')

def entries(folder):
    directory=html.parse(str(folder/'materialien.html'))
    result=[];seen=set()
    for a in directory.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," gb-material-list ")]//a[@href]'):
        href=a.get('href');url=urlsplit(href)
        if url.scheme or url.netloc or not url.path.startswith('material/') or href in seen:continue
        target=(folder/unquote(url.path)).resolve()
        if not target.is_relative_to(folder.resolve()) or not target.is_file():continue
        title=' '.join(a.text_content().split())
        if not title:continue
        seen.add(href)
        result.append({'href':href,'title':title,'textKey':a.get('data-edit-text',''),'linkKey':a.get('data-edit-link','')})
    if not result:raise ValueError('Materialübersicht enthält keine nutzbaren Verweise: '+str(folder))
    return result

def label(title):
    match=re.match(r'^((?:M|Ü)\d+[a-z]?)\s*[·:–-]\s*(.+)$',title)
    if not match:return '<span>'+escape(title)+'</span>'
    return '<b>'+escape(match[1])+'</b><span> · '+escape(match[2])+'</span>'

def menu(records,prefix='',current=None):
    items=[]
    for i,rec in enumerate(records):
        here=' aria-current="page"' if rec['href']==current else ''
        items.append(f'<a class="material-link" data-bfs-mref="{i}" href="{escape(prefix+rec["href"],quote=True)}"{here}>{label(rec["title"])}</a>')
    items.append(f'<a class="material-link bfs-directory" href="{prefix}materialien.html">Materialübersicht</a>')
    return '<details class="card phase-materials material-access bfs-material-access" data-bfs-material-menu><summary>Materialzugriff</summary><nav class="material-grid" aria-label="Materialien und Übungen">'+''.join(items)+'</nav></details>'

def include(file,base,role,static=''):
    source=file.read_text(encoding='utf-8')
    source=re.sub(r'<!-- BFS-MATERIAL-ACCESS:BEGIN -->.*?<!-- BFS-MATERIAL-ACCESS:END -->','',source,flags=re.S)
    source=re.sub(r'<!-- BFS-MATERIAL-PANEL:BEGIN -->.*?<!-- BFS-MATERIAL-PANEL:END -->','',source,flags=re.S)
    tag=(f'<!-- BFS-MATERIAL-ACCESS:BEGIN --><link rel="stylesheet" href="{base}assets/bfs-material-access.css">'
         f'<script defer src="{base}assets/bfs-materials-data.js"></script>'
         f'<script defer src="{base}assets/bfs-material-access.js" data-material-page="{role}"></script><!-- BFS-MATERIAL-ACCESS:END -->')
    # Some supplied board HTML has implicit head/body closing tags. Insert into
    # the head start, before document markup can make a browser close it.
    head=re.search(r'<head(?:\s[^>]*)?>',source,re.I)
    if head:
        # Keep charset detection ahead of the new external references.
        meta=re.match(r'\s*<meta\b[^>]*charset[^>]*>',source[head.end():],re.I)
        end=head.end()+(meta.end() if meta else 0)
        source=source[:end]+tag+source[end:]
    else:source=tag+source
    if static:
        hero=re.search(r'<header\b[^>]*class=["\'][^"\']*\bgb-intro\b[^"\']*["\'][^>]*>[\s\S]*?</header>',source,re.I)
        if not hero:hero=re.search(r'<section\b[^>]*class=["\'][^"\']*\blesson-content\b[^"\']*["\'][^>]*>',source,re.I)
        if not hero:raise ValueError('Phaseninhalt fehlt: '+str(file))
        source=source[:hero.end()]+'<!-- BFS-MATERIAL-PANEL:BEGIN -->'+static+'<!-- BFS-MATERIAL-PANEL:END -->'+source[hero.end():]
    file.write_text(source,encoding='utf-8')

def apply(folder):
    folder=Path(folder);assets=folder/'assets'
    spa=not (folder/'materialien.html').is_file()
    if spa and not all((folder/f).is_file() for f in ('data.js','app.js','index.html')):
        raise ValueError('Unbekannter Pakettyp: '+str(folder))
    data=[] if spa else entries(folder)
    assets.mkdir(exist_ok=True)
    for name in ['bfs-material-access.js','bfs-material-access.css']:shutil.copyfile(HERE/name,assets/name)
    (assets/'bfs-materials-data.js').write_text('window.BFS_MATERIAL_LIST='+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+';\n',encoding='utf-8')
    if spa:
        include(folder/'index.html','','office')
        return
    for phase in PHASES:
        include(folder/(phase+'.html'),'','phase',menu(data))
    include(folder/'materialien.html','','directory')
    for page in (folder/'material').rglob('*.html'):
        prefix='../'*(len(page.relative_to(folder).parts)-1)
        include(page,prefix,'material')
    # Check, orientation, footer, editorial source and manifest are owned by
    # their respective builders. Manifest regeneration follows all migrations.
if __name__=='__main__':
    import sys
    for p in sys.argv[1:]:apply(p)
