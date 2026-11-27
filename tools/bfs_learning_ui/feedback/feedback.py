"""Keep learner course feedback in the Moodle activity linked by the editor."""
from pathlib import Path
import re
from html import escape
from lxml import html

BOOKMARK = """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=reflektieren.html"><title>Feedback in Moodle</title></head>
<body><main><h1>Feedback in Moodle</h1><p>Öffne in der Phase „Reflektieren“ die separate Moodle-Aktivität „Feedback“ und gib deine Rückmeldung dort ab.</p>
<p><a href="reflektieren.html">Zur Phase Reflektieren</a></p></main></body></html>
"""
INSTRUCTION = ' die separate Aktivität „Feedback“ in deinem Moodle-Kurs aus und sende deine Rückmeldung dort ab. Falls hier kein Direktlink angezeigt wird, öffne „Feedback“ in der Kursübersicht.'
def write_if_changed(f,s):
    if f.read_text()!=s:
        f.write_text(s)
def apply(folder):
    """Update one BFS-dual learner package. Keeps editor integration and Moodle URLs."""
    d=Path(folder)
    f=d/'reflektieren.html'
    if not f.exists():
        # 6.9 already embeds the course Feedback link and only a completion checkbox in its single-page application.
        data=d/'data.js'
        if data.exists() and 'separate Moodle-Aktivität Feedback' in data.read_text() and (d/'app.js').exists():
            return
        raise ValueError(f'Keine passende Reflexionsseite in {d}')
    s=f.read_text()
    if 'href="feedback.html"' in s:
        # Keep the existing semantic instruction and the two editor keys for its verb and body.
        rule=r'(<p><strong\b[^>]*>Fülle</strong>)(<span\b[^>]*>)\s*die Aktivität „Feedback“.*?</p>'
        s,k=re.subn(rule,lambda m:m[1]+m[2]+escape(INSTRUCTION)+'</span></p>',s,count=1,flags=re.S)
        if k!=1: raise ValueError(f'Unbekannter Auftragsaufbau in {f}')
        s=re.sub(r'<p>\s*<a\b[^>]*href="feedback\.html"[^>]*>[^<]*</a>\s*</p>','',s)
        if 'href="feedback.html"' in s: raise ValueError(f'Weitere lokale Feedbackverknüpfung in {f}')
        write_if_changed(f,s)
    # Existing bookmark and manifest resource remain valid without exposing any fields, printable form or local export.
    if (d/'feedback.html').exists():
        write_if_changed(d/'feedback.html',BOOKMARK)
    editorial=d/'Lernsituation.md'
    if editorial.exists():
        s=editorial.read_text()
        s=re.sub(r'^\*\*Fülle\*\* die Aktivität „Feedback“ im Moodle-Kurs aus\..*$', '**Fülle**'+INSTRUCTION,s,flags=re.M)
        s=re.sub(r'^\[Feedbackbogen öffnen\]\(#feedback\)\s*\n','',s,flags=re.M)
        s=re.sub(r'^\| FEEDBACK \| \[Feedback zur Lernsituation\]\(#feedback\) \|\n','',s,flags=re.M)
        s=re.sub(r'^<a id="feedback"></a>\n.*?(?=^<a id="|\Z)','',s,flags=re.M|re.S)
        write_if_changed(editorial,s)
    doc=html.fromstring(f.read_text())
    if not doc.xpath('//*[@data-edit-moodle="feedback"]') or doc.xpath('//textarea|//form|//a[@href="feedback.html"]'):
        raise ValueError(f'Moodle-Verankerung oder Aufgabeninhalt in {f} prüfen')
