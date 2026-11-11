"""Remove alternative path content without reserializing retained task HTML.

The caller selects active Lernsituationen and the traditional template.  This
module deliberately does not choose repository scope or regenerate metadata.
"""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import PurePosixPath


VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())


@dataclass
class Element:
    tag: str
    attrs: dict
    start: int
    open_end: int
    end: int | None
    parent: 'Element | None'

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent


class SpanParser(HTMLParser):
    """Only records spans; does not normalize case, entities, SVG or whitespace."""
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0]
        self.lines.extend(m.end() for m in re.finditer('\n', text))
        self.stack = []
        self.nodes = []
        self.feed(text)
        self.close()
        for node in self.stack:
            node.end = len(text)

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        pos = self.source_offset()
        end = pos + len(self.get_starttag_text())
        node = Element(tag, dict(attrs), pos, end, end if tag in VOID else None,
                       self.stack[-1] if self.stack else None)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop().end = self.source_offset() + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        matches = [i for i, node in enumerate(self.stack) if node.tag == tag]
        if not matches:
            return
        pos = self.source_offset()
        end = self.text.find('>', pos) + 1
        if end <= pos:
            raise ValueError('Unterminated HTML end tag')
        index = matches[-1]
        for node in self.stack[index:]:
            node.end = end
        del self.stack[index:]


def _remove_spans(text, spans):
    merged = []
    for start, end in sorted(set(spans)):
        if end is None:
            raise ValueError('Alternative learning-path element is not closed')
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    for start, end in reversed(merged):
        text = text[:start] + text[end:]
    return text


def w1_panels(text):
    """Exact source of retained phase panels, used as a preservation invariant."""
    return [text[n.start:n.end] for n in SpanParser(text).nodes
            if n.attrs.get('data-mode-panel') == '1']


def filter_html(text):
    before = w1_panels(text)
    parsed = SpanParser(text)
    remove = []
    for node in parsed.nodes:
        attrs = node.attrs
        if attrs.get('data-mode-panel') in {'2', '3', '4', '5'}:
            remove.append((node.start, node.end))
        if node.tag == 'option' and attrs.get('value') in {'2', '3', '4', '5'}:
            if any(a.tag == 'select' and
                   ('data-teacher-mode' in a.attrs or 'data-student-mode' in a.attrs)
                   for a in node.ancestors()):
                remove.append((node.start, node.end))
        if 'data-allow-mode' in attrs:
            label = next((a for a in node.ancestors() if a.tag == 'label'), node)
            remove.append((label.start, label.end))
        if 'data-path-module' in attrs:
            section = next((a for a in node.ancestors()
                            if a.tag == 'section' and 'teacher-card' in a.attrs.get('class', '').split()), None)
            if section is None:
                raise ValueError('Learning-path module input lacks its expected teacher card')
            remove.append((section.start, section.end))
    text = _remove_spans(text, remove)
    # These strings describe the removed interface, not any assignment.
    replacements = {
        'Lernweg einstellen, Moodle-Abgaben verknüpfen und die Paketfassung exportieren':
            'Moodle-Abgaben verknüpfen und die Paketfassung exportieren',
        'Die fünf Stufen sind alternative Lernwege zum selben Ergebnis.':
            'Dieses Paket enthält ausschließlich den tradierten Lernweg 1.',
        'Weitere Lernwege können als vollständiges Modul ergänzt werden. Bilder und Materialien werden gemeinsam genutzt.':
            'Dieses Paket enthält ausschließlich den tradierten Lernweg 1.',
        'Aufgabentexte aller Lernwege bleiben im Editor enthalten; die Vorschau zeigt den ausgewählten Lernweg. PDFs gibt es für alle fünf Lernwege.':
            'Die Vorschau und die PDFs enthalten ausschließlich den tradierten Lernweg 1.',
        'Fachlicher Auftrag für alle fünf Lernwege:': 'Fachlicher Auftrag:',
        'Die folgenden fünf Varianten sind alternative Wege zur Bearbeitung dieses Auftrags. Wählt eine Variante; gemeinsame Teilaufträge und Variantenbeschreibung bilden zusammen einen Auftrag.': '',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    if w1_panels(text) != before:
        raise AssertionError('Traditional task panel changed during subtractive migration')
    return text


def is_w1_task(task_id):
    return bool(re.fullmatch(r'\d+:1:\d+', task_id))


def filter_migration(migration):
    if not isinstance(migration, dict):
        return migration
    result = copy.deepcopy(migration)
    if isinstance(result.get('tasks'), dict):
        result['tasks'] = {key: value for key, value in result['tasks'].items()
                           if is_w1_task(key)}
        # Existing grouped W1 tasks remain all-or-nothing.  Never turn an old
        # alternative-path tick into completion of a traditional assignment.
        for key, value in result['tasks'].items():
            if any(not is_w1_task(item.get('id', '')) for item in value.get('from', [])):
                raise AssertionError(f'Cross-path progress migration for {key}')
    return result


def filter_lesson(data):
    result = copy.deepcopy(data)
    result['pages'] = {name: filter_html(html) for name, html in result['pages'].items()}
    for key in ('workbooks', 'printPdfs'):
        if isinstance(result.get(key), dict):
            if '1' not in result[key]:
                raise ValueError(f'{key} has no traditional path')
            result[key] = {'1': result[key]['1']}
    for phase, values in result.get('sourceTaskCounts', {}).items():
        if not isinstance(values, dict) or '1' not in values:
            raise ValueError(f'Unknown sourceTaskCounts structure in {phase}')
        result['sourceTaskCounts'][phase] = {'1': values['1']}
    for phase, values in result.get('phases', {}).items():
        if isinstance(values.get('modes'), dict):
            if '1' not in values['modes']:
                raise ValueError(f'Phase {phase} lacks traditional mode')
            values['modes'] = {'1': values['modes']['1']}
        if isinstance(values.get('metadata'), dict):
            values['metadata'] = {key.replace(' für alle fünf Varianten', '')
                                    .replace(' · für alle fünf Lernwege', ''): value
                                  for key, value in values['metadata'].items()}
    if 'progressMigration' in result:
        result['progressMigration'] = filter_migration(result['progressMigration'])
    # legacyTaskDictionaries are decoding tables, not tasks.  Their order must
    # survive so an old compact suspend_data bitset can still be decoded.
    return result


def filter_meta(data):
    result = copy.deepcopy(data)
    result['tasks'] = {key: value for key, value in result['tasks'].items()
                       if value.get('mode') == 1}
    if not result['tasks']:
        raise ValueError('No traditional tasks in progress metadata')
    if any(not is_w1_task(key) for key in result['tasks']):
        raise AssertionError('Unexpected W1 task ID format')
    if 'migration' in result:
        result['migration'] = filter_migration(result['migration'])
    return result


def filter_config(data):
    result = copy.deepcopy(data)
    result['mode'] = 1
    result['allowStudentMode'] = False
    if isinstance(result.get('learningPaths'), dict):
        result['learningPaths'] = {'1': result['learningPaths'].get('1', {'label': 'Tradiert'})}
    if isinstance(result.get('overrides'), dict):
        result['overrides'] = {name: filter_html(html) if isinstance(html, str) else html
                               for name, html in result['overrides'].items()}
    return result


def _js_transform(text, symbol, fn):
    match = re.fullmatch(r'(\s*window\.' + re.escape(symbol) + r'\s*=\s*)([\s\S]+?)(;?\s*)', text)
    if not match:
        raise ValueError(f'Unknown {symbol} assignment syntax')
    original = json.loads(match.group(2))
    changed = fn(original)
    if changed == original:
        return text
    return match.group(1) + json.dumps(changed, ensure_ascii=False, separators=(',', ':')) + ';\n'


def transform(path, text):
    path = str(path).replace('\\', '/')
    basename = PurePosixPath(path).name
    if basename == 'lesson-data.js':
        return _js_transform(text, 'SOZPAED', filter_lesson)
    if basename == 'progress-meta.js':
        return _js_transform(text, 'SOZ_PROGRESS_META', filter_meta)
    if basename == 'mode-config.js':
        return _js_transform(text, 'SOZ_CONFIG', filter_config)
    if basename == 'Konfiguration.json':
        data = json.loads(text)
        changed = filter_config(data)
        return text if changed == data else json.dumps(changed, ensure_ascii=False, indent=2) + '\n'
    if basename.endswith('.html'):
        return filter_html(text)
    return text
