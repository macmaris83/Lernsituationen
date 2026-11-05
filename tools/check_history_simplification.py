#!/usr/bin/env python3
"""Validate the single traditional learning path and compact task phases in Geschichte."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PHASES = ('informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren')

def data(path, variable):
    source = path.read_text(encoding='utf-8')
    match = re.search(r'window\.' + variable + r'\s*=\s*', source)
    if not match:
        raise ValueError(str(path) + ': Daten fehlen')
    return json.JSONDecoder().raw_decode(source[match.end():])[0]

class Tasks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.modes = []
        self.count = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-mode-panel' in attrs:
            self.modes.append(attrs['data-mode-panel'])
        if 'assignment-frame' in attrs.get('class', '').split():
            self.count += 1

def check():
    catalog = json.loads((ROOT / 'master-katalog.json').read_text(encoding='utf-8'))
    selected = [p for p in catalog['packages'] if p['typ'] == 'Lernsituation' and p['id'].startswith('GESCHICHTE-')]
    if not selected:
        raise ValueError('Keine Geschichte-Lernsituationen im Katalog')
    for package in selected:
        folder = ROOT / package['master']
        config = data(folder / 'mode-config.js', 'SOZ_CONFIG')
        lesson = data(folder / 'lesson-data.js', 'SOZPAED')
        if config.get('mode') != 1 or config.get('allowStudentMode') is not False or set(config.get('learningPaths', {})) != {'1'} or not config.get('singleLearningPath'):
            raise ValueError(package['id'] + ': ausschließlich Tradiert konfigurieren')
        counts = []
        for phase in PHASES:
            page = phase + '.html'
            if set(lesson['phases'][phase]['modes']) != {'1'}:
                raise ValueError(package['id'] + '/' + phase + ': weitere Lernwege in den Daten')
            values = []
            for source in (lesson['pages'][page], (folder / page).read_text(encoding='utf-8')):
                parsed = Tasks()
                parsed.feed(source)
                if set(parsed.modes) != {'1'} or not 1 <= parsed.count <= 4:
                    raise ValueError(package['id'] + '/' + phase + ': ein Lernweg und höchstens vier Aufgaben erforderlich')
                values.append(parsed.count)
            if values[0] != values[1]:
                raise ValueError(package['id'] + '/' + phase + ': Daten und HTML weichen ab')
            counts.append(values[0])
        print(package['id'] + ': Tradiert; Aufgaben je Phase ' + '/'.join(map(str, counts)))
    return len(selected)

if __name__ == '__main__':
    try:
        print(str(check()) + ' Geschichte-Lernsituationen geprüft.')
    except (ValueError, KeyError, OSError) as error:
        raise SystemExit(str(error))
