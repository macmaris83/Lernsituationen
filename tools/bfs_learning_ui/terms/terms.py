"""Apply just the learner-facing placement of the Fachbegriffscheck, in place."""
from pathlib import Path
import json
import re
from urllib.parse import urlsplit
from lxml import html

HERE = Path(__file__).parent
ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="6.5" width="15" height="12" rx="2"/><path d="m6 11 1.7 1.8L10.6 9M6 16h7M7 3.5h11a3 3 0 0 1 3 3v9"/></svg>'
ENTRY = f'<div class="bfs-term-entry"><a href="begriffstraining.html" class="bfs-term-launch" aria-label="Fachbegriffscheck öffnen">{ICON}<span>Fachbegriffscheck</span></a></div>'
ANCHOR = re.compile(r'<a\b(?P<attrs>[^>]*?\bhref\s*=\s*(?P<qt>["\'])(?P<href>[^"\']+)(?P=qt)[^>]*)>(?P<body>.*?)</a>',re.I|re.S)
SECTION = re.compile(r'<section\b[^>]*>\s*<h2\b[^>]*>Fachbegriffs[-–]?Check</h2>\s*<p\b[^>]*>.*?</p>\s*<div\s+id="quiz0"></div>\s*</section>',re.I|re.S)
PREFIX = 'window.LESSON='

def control(text):
    return re.sub('<[^>]*>','',text).strip()

def regular(folder):
    for p in sorted(folder.rglob('*.html')):
        raw=p.read_text()
        if 'begriffstraining.html' not in raw and p.name!='informieren.html':continue
        def change(m):
            u=urlsplit(m['href'])
            if u.netloc or u.scheme or Path(u.path).name!='begriffstraining.html' or u.fragment or u.query:return m[0]
            if 'bfs-term-launch' in m['attrs']:return m[0]
            if p.name=='informieren.html' and 'button' in m['attrs']:
                # The transition to the quiz now lives with the last Informieren task. The regular footer goes to the next phase.
                return '<a class="button primary" href="planen.html">Weiter zu Planen →</a>'
            if 'material/' in p.relative_to(folder).as_posix() and control(m['body']) not in ('Fachbegriffscheck','Begriffe prüfen','Zum Fachbegriffscheck'):return m[0]
            return ''
        new=ANCHOR.sub(change,raw)
        if p.name in ('informieren.html','druckansicht.html'):
            # This region formerly combined a standalone glossary link and the quiz on a single line.
            # Retain any meaningful glossary content; strip just the obsolete connector.
            new=re.sub(r'(<p(?:\s[^>]*)?>)\s*(?:<span\b[^>]*>\s*(?:·|&middot;)\s*</span>|·|&middot;)\s*</p>','',new)
            new=re.sub(r'(</a>)\s*(?:<span\b[^>]*>\s*(?:·|&middot;)\s*</span>|·|&middot;)\s*</p>',r'\1</p>',new)
        if p==folder/'informieren.html':
            if 'class="bfs-term-entry"' not in new:
                # This is the end of the lesson section, after every task and any optional exercise.
                new,count=re.subn(r'(</section>\s*<footer\b[^>]*class="page-footer[^"]*")',lambda m:ENTRY+'\n'+m[1],new,count=1)
                if not count:
                    raise ValueError(f'Schluss der Aufgabenphase nicht gefunden: {p}')
            new=add_style(new)
        if new!=raw:p.write_text(new)

def add_style(text):
    marker='/* bfs-check-placement */'
    if marker in text:return text
    return text.replace('</head>','<style>'+marker+'\n'+(HERE/'check.css').read_text()+'</style></head>',1)

def office(folder):
    data_path=folder/'data.js'
    text=data_path.read_text().strip()
    if not text.startswith(PREFIX):raise ValueError(f'Unbekanntes Büro-Datenformat: {data_path}')
    data=json.loads(text[len(PREFIX):].rstrip(';'))
    case=data['pages']['handlungssituation']
    if 'id="quiz0"' in case:
        match=SECTION.search(case)
        if not match:raise ValueError('Büro-Fachbegriffscheck im Fall fehlt')
        data['pages']['handlungssituation']=case[:match.start()]+case[match.end():]
        data['pages']['informieren']+=f'<details class="bfs-term-entry"><summary class="bfs-term-launch" aria-label="Fachbegriffscheck öffnen">{ICON}<span>Fachbegriffscheck</span></summary>{match[0]}</details>'
        data_path.write_text(PREFIX+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';\n')
    assert data['pages']['informieren'].count('id="quiz0"')==1
    index=folder/'index.html';current=index.read_text();new=add_style(current)
    if current!=new:index.write_text(new)
    editor=folder/'assets'/'editor.js'
    if editor.is_file():
        raw=editor.read_text()
        new=raw.replace("if (route==='handlungssituation') {\n          const doc=new DOMParser().parseFromString(source,'text/html');\n          data.quiz0.forEach","if (route==='informieren') {\n          const doc=new DOMParser().parseFromString(source,'text/html');\n          data.quiz0.forEach")
        # Keep the historical keys that installations may have customized. Page reset must follow the editor page the fields are shown on.
        needle="for (const key of Object.keys(state[group])) if (key.startsWith(prefix)) {"
        replacement="""for (const key of Object.keys(state[group])) {
        const movedOfficeField=office && /^index\\.html#handlungssituation::(?:office-check-|text-[34]$)/.test(key);
        if (!(movedOfficeField ? current==='index.html#informieren' : key.startsWith(prefix))) continue;"""
        new=new.replace(needle,replacement)
        if new!=raw:editor.write_text(new)
    # Both the completion gate and quiz use q0.a. Use that same persisted representation for the office XP badges.
    app=folder/'app.js';raw=app.read_text()
    new=raw.replace("state.q0[i] && q.k.every(k=>state.q0[i].includes(k)) && q.k.length===state.q0[i].length","state.q0.a?.[i] && q.k.every(k=>state.q0.a[i].includes(k)) && q.k.length===state.q0.a[i].length")
    if new!=raw:app.write_text(new)

def apply(folder):
    folder=Path(folder)
    if (folder/'begriffstraining.html').is_file():regular(folder)
    elif (folder/'app.js').is_file() and (folder/'data.js').is_file() and '"quiz0"' in (folder/'data.js').read_text():office(folder)
    else:raise ValueError(f'Kein unterstütztes BFS-Lernpaket: {folder}')

if __name__=='__main__':
    import sys
    for arg in sys.argv[1:]:apply(Path(arg))
