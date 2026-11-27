"""Apply the BRC reference's school links to existing BFS dual package chrome."""
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
BACKUP_REFERENCE = Path('/workspace/work/publish/Fachbereiche/BRC/LG01/LS04')
HEADER = re.compile(r'<header\b(?=[^>]*class="(?:brand-header|bfs-material-brand|glossary-brand)")[^>]*>.*?</header>', re.S|re.I)
LAPTOP = re.compile(r'<img\b(?=[^>]*src="[^"]*/(?:loept\.png|footer-2\.svg)")[^>]*>', re.I)
FOOTER = re.compile(r'<footer\b[^>]*>.*?</footer>', re.S|re.I)
LINKS = (
    (0,'https://virtuelles-klassenbuch.de/','Virtuelles Klassenbuch'),
    (1,'https://bbs1-aurich.eu/','IServ BBS 1 Aurich'),
    (2,'index.html','Löppt – zur Orientierung'),
    (3,'https://www.instagram.com/bbs1aurich/','Instagram der BBS 1 Aurich'),
    (4,'https://www.facebook.com/bbs1aurich/','Facebook der BBS 1 Aurich'),
    (5,'https://www.youtube.com/channel/UC0UuEZnhTVPjXVNSm3oAxOg','YouTube der BBS 1 Aurich'),
    (6,'https://www.bbs1-aurich.de/','Website der BBS 1 Aurich'),
)
FILES = ['bfs-chrome.css',*(f'footer-{i}.svg' for i in range(7))]


def links(prefix):
    groups = []
    for group, entries in [('tools', LINKS[:2]), ('loeppt', LINKS[2:3]), ('social', LINKS[3:])]:
        items = []
        for idx, url, label in entries:
            external = url.startswith('https://')
            attrs = ' target="_blank" rel="noopener noreferrer"' if external else ''
            href = url if external else prefix + url
            items.append(f'<a href="{href}" aria-label="{label}"{attrs}><img src="{prefix}assets/footer-{idx}.svg" alt="{label}"></a>')
        groups.append(f'<div class="bfs-school-group bfs-school-{group}">{"".join(items)}</div>')
    return '<nav class="bfs-school-links" aria-label="Schulangebote und Social Media">'+''.join(groups)+'</nav>'


def header(match):
    s=match.group(0)
    s=re.sub(r'<div class="(?:gb-brand|brand-title)">.*?</div>', '', s, flags=re.S)
    s=re.sub(r'(<header\b[^>]*>)\s*<strong>(?:BFS dual|Global Bike)[^<]*</strong>', r'\1', s)
    s=LAPTOP.sub('',s)
    if 'data-bfs-school' not in s:s=s.replace('<header ', '<header data-bfs-school="" ', 1)
    return s


def page(path, folder):
    if path.name in {'druckansicht.html','scorm.html'} or 'pdf' in path.relative_to(folder).parts:return False
    s=path.read_text()
    if 'class="bfs-school-links"' in s:return False
    if not (HEADER.search(s) or FOOTER.search(s)):return False
    p='../'*(len(path.relative_to(folder).parts)-1)
    new=HEADER.sub(header,s)
    nav=links(p)
    found=list(FOOTER.finditer(new))
    if found:
        last=found[-1]
        footer=last.group()
        footer=LAPTOP.sub('',footer)
        footer=re.sub(r'<span>Global Bike · Büroorganisation</span>', '',footer)
        footer=footer.replace('<footer','<footer data-bfs-chrome=""',1)
        if '<div class="bfs-document-footer' in footer:
            footer=footer.replace('<div class="bfs-document-footer',nav+'<div class="bfs-document-footer',1)
        else:
            footer=footer.replace('</footer>',nav+'</footer>',1)
        new=new[:last.start()]+footer+new[last.end():]
    else:
        extra=f'<footer data-bfs-chrome="" class="bfs-standalone-footer">{nav}</footer>'
        if path.name=='lehrkraft.html' and '</main></div>' in new:
            new=new.replace('</main></div>','</main>'+extra+'</div>',1)
        else:
            new=new.replace('</body>',extra+'</body>',1)
    if 'assets/bfs-chrome.css' not in new:
        new=new.replace('</head>',f'<link rel="stylesheet" href="{p}assets/bfs-chrome.css"></head>',1)
    if new!=s:path.write_text(new)
    return new!=s


def add_resources(folder):
    manifest=folder/'imsmanifest.xml'
    if not manifest.is_file():return
    s=manifest.read_text()
    root=ET.fromstring(s)
    rs=[r for r in root.iter() if r.tag.split('}')[-1]=='resource' and r.get('href')]
    if len(rs)!=1:raise ValueError(f'Expected one SCO resource for {manifest}')
    present={f.get('href') for f in rs[0] if f.tag.split('}')[-1]=='file'}
    additions=''.join(f'      <file href="assets/{f}" />\n' for f in FILES if 'assets/'+f not in present)
    if additions:
        s,count=re.subn(r'(?m)([ \t]*</resource>)',lambda m:additions+m[1],s,count=1)
        if count!=1:raise ValueError(f'Manifest has no resource close: {manifest}')
        manifest.write_text(s)


def apply(folder, reference=None):
    folder=Path(folder).resolve()
    if reference is None:
        reference=next((parent/'BRC/LG01/LS04' for parent in folder.parents if parent.name=='Fachbereiche'),BACKUP_REFERENCE)
    reference=Path(reference)
    if not (reference/'assets/footer-0.svg').is_file(): reference=BACKUP_REFERENCE
    assets=folder/'assets';assets.mkdir(exist_ok=True)
    for i in range(7):
        n=f'footer-{i}.svg'
        shutil.copyfile(reference/'assets'/n,assets/n)
    shutil.copyfile(HERE/'chrome.css',assets/'bfs-chrome.css')
    count=sum(page(f,folder) for f in sorted(folder.rglob('*.html')))
    add_resources(folder)
    return count
