#!/usr/bin/env python3
"""Independently audit LG03 source fidelity, student/teacher separation and files.

This verifier deliberately does not import the LG03 builder or its parser. It
compares visible HTML text against the supplied Markdown, allowing the requested
book-label simplification, separately checked index-backed keyword additions,
and the template's Ich competency wording.
Browser behavior, native Moodle, AIS and GoodNotes need separate verification.

Examples:
  python tools/verify_lg03_content.py --source-only
  python tools/verify_lg03_content.py --content-only --lesson LS01
  python tools/verify_lg03_content.py
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import functools
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

from lxml import html

REPO = Path(__file__).resolve().parents[1]
PHASES = ('informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren')
PHASE_LABELS = ('Informieren', 'Planen', 'Entscheiden', 'Durchführen', 'Kontrollieren', 'Reflektieren')
ATTACHMENT = Path('/workspace/attachments/ef2836a5-8ddb-447d-8815-b390a3706381/BioCasa_LG03_Gesamtreihe_5_Lernwege_Seitenverweise.md')
# Independently recognise page-only hints and their operational continuations;
# this does not use the builder's citation parser or its standalone heuristics.
BARE_BOOK_REFERENCE = re.compile(
    r'\*\*Buch:\*\*\s*((?:S\.\s*\d+\s*(?:(?:,|;|/|\bund\b|\bsowie\b|\bbzw\.)\s*)?)+)'
    r'(?=(?:[.)]|\n|$|(?:und|sowie)\s+(?:dokumentieren|kennzeichnen|wählen|schreiben|verknüpfen)\s+Sie'
    r'|;\s*(?:freiwilliges|prüfen|nutzen|gleichen|übertragen|beziehen|halten)))'
)


def require(condition, *context):
    if not condition:
        raise AssertionError(' · '.join(str(item) for item in context))


def sections(value, level):
    matches = list(re.finditer(r'^' + '#' * level + r' (.+)$', value, re.M))
    return [(match[1], value[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(value)].strip())
            for index, match in enumerate(matches)]


def fragment(value):
    return html.fragment_fromstring(value or '<div></div>', create_parent='div')


@functools.lru_cache(maxsize=None)
def markdown_text(value):
    rendered = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'html5', '--wrap=none'],
                              input=value, text=True, capture_output=True, check=True).stdout
    return fragment(rendered).text_content()


def pupil_book_source(value):
    """The user excludes the original editorial paragraph about index photos."""
    paragraphs = re.split(r'\n\s*\n', value)
    return '\n\n'.join('**Lehrbuch**' if paragraph.startswith('**Lehrbuch laut bereitgestelltem Stichwortverzeichnis')
                        else paragraph for paragraph in paragraphs)


def canonical(value):
    value = unicodedata.normalize('NFC', value).replace('\u00ad', '')
    # The user explicitly wants the generic label Lehrbuch, without metadata.
    value = value.replace('Lehrbuch laut bereitgestelltem Stichwortverzeichnis', 'Lehrbuch')
    value = re.sub(r'(?<!\w)(?:Lehrbuch|Buch)\s*:', '', value)
    return re.sub(r'\s+', '', value)


def same_text(actual, expected, context):
    left, right = canonical(actual), canonical(expected)
    if left == right:
        return
    position = next((i for i, pair in enumerate(zip(left, right)) if pair[0] != pair[1]), min(len(left), len(right)))
    raise AssertionError(f'{context}: text differs at {position}; expected {right[max(0, position-45):position+150]!r}; '
                         f'actual {left[max(0, position-45):position+150]!r}')


def css_class(root, name):
    return root.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," ' + name + ' ")]')


def payload(path):
    return json.loads(path.read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';'))


def read_source(path):
    raw = path.read_text(encoding='utf-8')
    chapters = sections(raw, 1)
    lessons = {}
    teachers = {}
    optional = ''
    teacher_all = ''
    for heading, body in chapters:
        match = re.match(r'LS(\d{2}) [–-] (.+)', heading)
        if match:
            number = int(match[1])
            parts = {}
            for label, text in sections(body, 2):
                section_number = re.match(r'(\d+)\.', label)
                require(section_number, f'LS{number:02}', 'unexpected section', label)
                parts[int(section_number[1])] = text
            require(set(parts) == set(range(1, 9)), f'LS{number:02}', 'eight source sections')
            scope = re.search(r'(\d+)\s*UE\s*[,/·]\s*(\d+)\s*Minuten', parts[1])
            require(scope, f'LS{number:02}', 'source duration')
            hours, minutes = map(int, scope.groups())
            modes = {}
            for label, text in sections(parts[5], 3):
                mode_match = re.match(r'Lernweg ([A-E]) ', label)
                require(mode_match, f'LS{number:02}', 'mode heading', label)
                mode = ord(mode_match[1]) - ord('A') + 1
                phase_sections = sections(text, 4)
                require(len(phase_sections) == 6, f'LS{number:02}', mode, 'six phases')
                phases = {}
                for (phase, expected_label), (label, original) in zip(zip(PHASES, PHASE_LABELS), phase_sections):
                    require(label.startswith(expected_label), f'LS{number:02}', mode, 'phase sequence', label)
                    time = re.search(r'·\s*(\d+)\s*Min(?:\.|uten)', label)
                    require(time, f'LS{number:02}', mode, phase, 'minutes in original heading')
                    refs = re.findall(r'\*\*Buch:\*\*([^\n]*)', original)
                    require(all(re.search(r'\bS\.\s*\d+', ref) for ref in refs), f'LS{number:02}', mode, phase, 'book pages')
                    phases[phase] = {'text': original, 'minutes': int(time[1]), 'books': refs}
                require(sum(item['minutes'] for item in phases.values()) == minutes == hours * 45,
                        f'LS{number:02}', mode, 'phase budget equals stated duration')
                modes[mode] = phases
            require(set(modes) == set(range(1, 6)), f'LS{number:02}', 'five modes')
            budgets = [modes[1][phase]['minutes'] for phase in PHASES]
            require(all([values[phase]['minutes'] for phase in PHASES] == budgets for values in modes.values()),
                    f'LS{number:02}', 'equal total and phase budgets for every mode')
            materials = {}
            books = []
            extras = []
            for label, text in sections(parts[6], 3):
                material = re.match(r'M(\d+) [–-] (.+)', label)
                if material:
                    materials[int(material[1])] = (material[2], text)
                    if 'Buchzugriff' in material[2]:
                        books.append((label, text))
                elif label.startswith('Buchzugriff'):
                    books.append((label, text))
                else:
                    extras.append((label, text))
            require(set(materials) == set(range(1, len(materials) + 1)), f'LS{number:02}', 'continuous local material numbers')
            require(len(books) == 1, f'LS{number:02}', 'one local book reference table')
            referenced = {int(n) for n in re.findall(r'\bM(\d+)\b', body)}
            require(referenced <= set(materials), f'LS{number:02}', 'undefined material reference', referenced - set(materials))
            lessons[number] = dict(number=number, title=match[2], parts=parts, hours=hours, minutes=minutes,
                                   modes=modes, budgets=budgets, materials=materials, books=books[0][1], extras=extras, raw=body)
        elif heading.startswith('Optionale Wiederholung'):
            optional = body
        elif heading.startswith('Lehrkräfte-'):
            teacher_all += '\n' + body
            for label, text in sections(body, 2):
                match = re.search(r'\bLS(\d{2})\b', label)
                if match:
                    teachers[int(match[1])] = text
    require(set(lessons) == set(range(1, 13)), 'source', 'all twelve lessons')
    require(set(teachers) == set(range(1, 13)), 'source', 'all twelve teacher appendices')
    require(optional and 'Karten zum Ausschneiden' in optional, 'source', 'optional student vocabulary game')
    require(sum(lesson['hours'] for lesson in lessons.values()) == 80, 'source', '80 UE')
    actions = sum(len(phases) for lesson in lessons.values() for phases in lesson['modes'].values())
    references = sum(len(value['books']) for lesson in lessons.values() for phases in lesson['modes'].values() for value in phases.values())
    require(actions == 360 and references == 180, 'source', '360 complete phase actions and 180 book references', actions, references)
    print('PASS: independent source audit — 12 lessons, 60 paths, 360 phase actions, 180 book references, 80 UE.', flush=True)
    return raw, lessons, teachers, optional, teacher_all


def clean_task_body(node):
    node = copy.deepcopy(node)
    # Added index-backed keywords satisfy the user's keyword + page request.
    # drop_tree preserves each tail, including the original S. / page number.
    for element in css_class(node, 'book-keyword'):
        element.drop_tree()
    for element in node.xpath('.//*[@data-time-ui] | .//button | .//script'):
        element.drop_tree()
    return node.text_content()


def bare_book_pages(raw):
    return [page for reference in BARE_BOOK_REFERENCE.finditer(raw)
            for page in re.findall(r'S\.\s*(\d+)', reference[1])]


def teacher_fingerprints(teacher, all_student_source):
    student = canonical(markdown_text(all_student_source))
    result = set()
    for block in re.split(r'\n\s*\n', teacher):
        if block.lstrip().startswith(('#', '|', '---')):
            continue
        text = canonical(markdown_text(block))
        if len(text) >= 110:
            # Long excerpts exclusive to the appendix reliably reveal answer leaks.
            for start in range(0, len(text) - 109, 110):
                chunk = text[start:start+110]
                if chunk not in student:
                    result.add(chunk)
    return result


def verify_content(root, lesson, teacher, fingerprints):
    name = root.name
    keyword_file = REPO / 'Quellen/BRC_LG03/Lehrbuchstichwoerter.json'
    keyword_map = json.loads(keyword_file.read_text()).get(name, {}) if keyword_file.exists() else {}
    keyword_count = 0
    data = payload(root / 'lesson-data.js')
    meta = payload(root / 'progress-meta.js')
    expected_id = f'BRC-LG03-{name}'
    require(data['id'] == meta['id'] == expected_id, name, 'isolated lesson/progress identity')
    require(data['title'] == lesson['title'], name, 'source title')
    require([data['phaseBudgets'][phase] for phase in PHASES] == lesson['budgets'], name, 'original phase times')
    competencies = data['competencies']
    require(len(competencies) == len(meta['competencies']) == 5, name, 'five competencies')
    require(data['priorityStatement'].startswith('Ich '), name, 'Ich priority competency')
    require(all(item['statement'].startswith('Ich ') and item['id'].startswith(expected_id + '-') for item in competencies),
            name, 'Ich wording and isolated competency identities')
    pages = {filename: fragment(value) for filename, value in data['pages'].items()}
    student_pages = {filename: page for filename, page in pages.items() if filename != 'erwartungshorizont.html'}
    require('erwartungshorizont.html' not in data['printOrder'], name, 'teacher solutions excluded from student print order')
    student_text = canonical('\n'.join(page.text_content() for page in student_pages.values()))
    orientation = pages['index.html'].text_content()
    require(not re.search(r'Lehrkräft|Lehrkraft|Erwartungshorizont|Redaktionsstand|Lese- und Verwendungshinweis|Stichwortverzeichnis', orientation),
            name, 'orientation contains teacher/editorial guidance')
    require(not css_class(pages['index.html'], 'material-access'), name, 'orientation contains material access')
    require(canonical(markdown_text(lesson['parts'][2])) in canonical(orientation), name, 'complete relevance text')
    require(canonical(markdown_text(lesson['parts'][4])) in canonical(pages['handlungssituation.html'].text_content()),
            name, 'complete original situation')
    require(len(meta['tasks']) == 30, name, 'exactly 30 complete phase actions')
    task_ids = set()
    for phase in PHASES:
        require(len(pages[phase + '.html'].xpath('.//*[@data-mode-panel]')) == 5, name, phase, 'five panels')
        for mode in range(1, 6):
            context = f'{name} W{mode} {phase}'
            panel = pages[phase + '.html'].xpath(f'.//*[@data-mode-panel="{mode}"]')[0]
            bodies = css_class(panel, 'assignment-body')
            cards = css_class(panel, 'assignment-frame')
            require(len(bodies) == len(cards) == data['sourceTaskCounts'][phase][str(mode)] == 1,
                    context, 'one complete original action, with criteria in the same card')
            original = lesson['modes'][mode][phase]
            same_text(clean_task_body(bodies[0]), markdown_text(original['text']), context)
            actual_keyword_pages = []
            for keyword in css_class(bodies[0], 'book-keyword'):
                following_page = re.match(r'\s*S\.\s*(\d+)\b', keyword.tail or '')
                require(following_page, context, 'added keyword immediately precedes an original S. page reference')
                page_number = following_page[1]
                require(page_number in keyword_map, context, 'added keyword page exists in separate source map', page_number)
                require(keyword.text_content().strip() == keyword_map[page_number], context, 'added keyword matches source map', page_number)
                require(re.search(r'\bS\.\s*' + re.escape(page_number) + r'\b', original['text']),
                        context, 'added keyword page belongs to this original action', page_number)
                actual_keyword_pages.append(page_number)
                keyword_count += 1
            require(actual_keyword_pages == bare_book_pages(original['text']), context,
                    'every originally bare page reference receives exactly one mapped keyword, in source order',
                    actual_keyword_pages, bare_book_pages(original['text']))
            timers = cards[0].xpath('.//*[@data-time-ui and @data-minutes]')
            require(len(timers) == 1 and float(timers[0].get('data-minutes')) == original['minutes'], context, 'exact source timer')
            identity = cards[0].get('data-task-id')
            require(identity and identity not in task_ids, context, 'unique task identity')
            task_ids.add(identity)
            require(identity in meta['tasks'], context, 'task in progress metadata')
            require(meta['tasks'][identity]['mode'] == mode and meta['tasks'][identity]['phase'] == phase,
                    context, 'progress task mode/phase match')
            require(meta['tasks'][identity]['signature'] == cards[0].get('data-task-signature'), context, 'progress content signature')
            for reference in original['books']:
                require(canonical(markdown_text(reference)) in canonical(clean_task_body(panel)), context, 'full original book reference')
                require(panel.xpath('.//img[contains(@src,"lehrbuch")]'), context, 'template book icon')
                if re.search(r'^\*\*Buch:\*\*', original['text'], re.M):
                    require(css_class(panel, 'book-line') and css_class(panel, 'book-reference'), context, 'template standalone book-reference markup')
            if original['books']:
                require(panel.xpath('.//img[contains(@src,"lehrbuch") and @alt="Lehrbuch"]'), context, 'generic Lehrbuch label')
    require(task_ids == set(meta['tasks']), name, 'no missing or phantom progress tasks')
    for material, (_, original) in lesson['materials'].items():
        document = css_class(pages[f'm{material}.html'], 'paper') + css_class(pages[f'm{material}.html'], 'material-document')
        require(len(document) == 1, name, f'M{material}', 'one source document')
        same_text(document[0].text_content(), markdown_text(pupil_book_source(original)), f'{name} M{material}')
    # Preserve complete local book tables and the pupil-facing synthesis/KI notes.
    for section, original in [('book table', lesson['books']), ('section 7', lesson['parts'][7]), ('section 8', lesson['parts'][8])]:
        require(canonical(markdown_text(pupil_book_source(original))) in student_text, name, 'missing complete', section)
    for title, original in lesson['extras']:
        require(canonical(markdown_text(original)) in student_text, name, 'missing extra pupil source material', title)
    # The Einordnung context may move away from orientation and its labels may change.
    # Check prose independently of labels; timings are checked exactly above.
    for block in re.split(r'\n\s*\n', lesson['parts'][1]):
        if not block.strip() or block.lstrip().startswith(('|', '---')):
            continue
        body = re.sub(r'^\*\*[^*]+:\*\*\s*', '', block)
        require(canonical(markdown_text(body)) in student_text, name, 'missing Einordnung context', body[:70])
    for block in re.split(r'\n\s*\n', lesson['parts'][3]):
        if re.match(r'\*\*(?:Identisch|Gleiche)', block):
            body = re.sub(r'^\*\*[^*]+:\*\*\s*', '', block)
            require(canonical(markdown_text(body)) in student_text, name, 'complete shared required outcomes')
    teacher_text = canonical(pages['erwartungshorizont.html'].text_content())
    require(canonical(markdown_text(teacher)) in teacher_text, name, 'complete lesson-specific teacher appendix')
    leaks = [value for value in fingerprints if value in student_text]
    require(not leaks, name, 'teacher-only solution excerpt leaked to pupil pages', leaks[:1])
    print(f'PASS: {name} — 30 original actions, {len(lesson["materials"])} original materials, {keyword_count} mapped keyword additions, local book table, pupil context and separated solutions.', flush=True)
    return data, fingerprints


def verify_pdfs(root, lesson, data, fingerprints, skip_images=False):
    import fitz
    texts = {}
    required = [f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf' for phase in PHASES for mode in range(1, 6)]
    required += list(data['workbooks'].values())
    required += [f'pdf/LG03_{root.name}_Gesamtdruck_A4.pdf']
    require(len(set(required)) == 36, root.name, '30 phase PDFs and six complete documents')
    for filename in required:
        path = root / filename
        require(path.is_file(), root.name, 'missing PDF', filename)
        with fitz.open(path) as document:
            require(document.page_count > 0 and not document.needs_pass, root.name, 'invalid PDF', filename)
            if filename.endswith('_Gesamtdruck_A4.pdf'):
                require(all(abs(page.rect.width - 595.276) < 1 and abs(page.rect.height - 841.89) < 1 for page in document),
                        root.name, 'entire Gesamtdruck uses portrait A4')
                if not skip_images:
                    mapping = json.loads((REPO / 'Quellen/BRC_LG03/Bildzuordnung.json').read_text())[str(lesson['number'])]
                    expected_sizes = [tuple(mapping[role]['dimensions']) for role in ('orientation', 'situation')]
                    objects = {}
                    for page_number, page in enumerate(document):
                        for item in page.get_images(full=True):
                            xref, width, height = item[0], item[2], item[3]
                            if (width, height) in expected_sizes:
                                objects.setdefault(xref, (page_number, width, height))
                    require(len(objects) == 2, root.name, 'both original-resolution story images embedded in Gesamtdruck', objects)
                    ordered_objects = sorted(objects.values())
                    require(Counter((width, height) for _, width, height in ordered_objects) == Counter(expected_sizes),
                            root.name, 'embedded PDF image dimensions match both uploaded originals')
                    require(ordered_objects[0][0] < ordered_objects[1][0], root.name,
                            'orientation and action story images occur on successive distinct document pages')
            text = '\n'.join(page.get_text() for page in document)
        require(len(text.strip()) > 100, root.name, 'blank PDF', filename)
        # Preserve genuine compound hyphens at line breaks ("Kontroll-\nund").
        # canonical already removes discretionary soft hyphens and whitespace.
        text = canonical(text)
        require(not any(value in text for value in fingerprints), root.name, 'teacher solution in pupil PDF', filename)
        texts[filename] = text
    # Verify substantive excerpts in both the targeted share PDF and whole workbook.
    for mode in range(1, 6):
        whole = texts[data['workbooks'][str(mode)]]
        for phase in PHASES:
            original = lesson['modes'][mode][phase]['text']
            prose = re.split(r'\*\*Buch:\*\*', original, maxsplit=1)[0].strip()
            expected = canonical(markdown_text(prose))
            phase_text = texts[f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf']
            for excerpt in (expected[:90], expected[-90:]):
                require(excerpt in phase_text, root.name, phase, mode, 'source action missing from phase PDF', excerpt)
                require(excerpt in whole, root.name, phase, mode, 'source action missing from whole workbook', excerpt)
            phase_dom = fragment(data['pages'][phase + '.html'])
            panel = phase_dom.xpath(f'.//*[@data-mode-panel="{mode}"]')[0]
            phase_without_keywords, whole_without_keywords = phase_text, whole
            for keyword in css_class(panel, 'book-keyword'):
                page_reference = re.match(r'\s*S\.\s*\d+\b', keyword.tail or '')
                require(page_reference, root.name, phase, mode, 'added keyword has a page reference')
                expected_pair = canonical(keyword.text_content() + page_reference[0])
                require(expected_pair in phase_text and expected_pair in whole,
                        root.name, phase, mode, 'keyword/page pair missing from phase or whole PDF', expected_pair)
                phase_without_keywords = phase_without_keywords.replace(expected_pair, canonical(page_reference[0]))
                whole_without_keywords = whole_without_keywords.replace(expected_pair, canonical(page_reference[0]))
            complete_source = canonical(markdown_text(original))
            require(complete_source in phase_without_keywords, root.name, phase, mode, 'complete original action missing from phase PDF')
            require(complete_source in whole_without_keywords, root.name, phase, mode, 'complete original action missing from whole PDF')
    # Tables carry the input data for the accounting/marketing cases.  Verify
    # every original cell's complete extracted text in the printable document,
    # rather than accepting that a PDF merely opens and has some text.
    total_text = texts[f'pdf/LG03_{root.name}_Gesamtdruck_A4.pdf']
    cells = 0
    for number, (_, original) in lesson['materials'].items():
        rendered = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'html5', '--wrap=none'],
                                  input=pupil_book_source(original), text=True, capture_output=True, check=True).stdout
        for cell in fragment(rendered).xpath('.//td | .//th'):
            expected = canonical(cell.text_content())
            require(not expected or expected in total_text, root.name, f'M{number}', 'table cell missing from Gesamtdruck', cell.text_content())
            cells += 1
    print(f'PASS: {root.name} — 36 readable pupil PDFs, correct path/phase content and {cells} original table cells in the A4 Gesamtdruck.', flush=True)


def verify_package(root, entry, series_dir, skip_images=False):
    manifest_path = root / 'imsmanifest.xml'
    manifest = ET.fromstring(manifest_path.read_bytes())
    paths = set()
    for element in manifest.iter():
        kind = element.tag.rsplit('}', 1)[-1]
        if kind not in ('resource', 'file') or 'href' not in element.attrib:
            continue
        name = element.attrib['href']
        require(not name.startswith(('/', 'http:', 'https:')) and '..' not in PurePosixPath(name).parts,
                root.name, 'non-local manifest file', name)
        require((root / name).is_file(), root.name, 'missing manifest file', name)
        paths.add(name)
    require({'index.html', 'lesson-data.js', 'progress-meta.js'} <= paths, root.name, 'manifest application files')
    if skip_images:
        print(f'SKIP: {root.name} — uploaded image presence and original hashes explicitly not verified.', flush=True)
    else:
        require('images' in entry and all(role in entry['images'] for role in ('orientation', 'situation')),
                root.name, 'two uploaded original images are required; use --skip-image-check only to record an explicit incomplete-image audit')
        for role in ('orientation', 'situation'):
            image = entry['images'][role]
            path = root / image['file']
            from PIL import Image
            definition = json.loads((REPO / 'Quellen/BRC_LG03/Bildzuordnung.json').read_text())[str(int(root.name[2:]))][role]
            original = REPO / 'Quellen/BRC_LG03/Bilder' / definition['filename']
            source_role = 'Orientierung' if role == 'orientation' else 'Handlungssituation'
            require(PurePosixPath(definition['archive_path']).name == f'{root.name}_{source_role}.png',
                    root.name, role, 'correct original uploaded filename and role')
            require(image['file'] in paths, root.name, role, 'image in manifest')
            require(path.name == definition['filename'] and path.read_bytes() == original.read_bytes(), root.name, role, 'unaltered original image bytes')
            require(hashlib.sha256(path.read_bytes()).hexdigest() == image['sha256'] == definition['sha256'], root.name, role, 'source image hash')
            with Image.open(original) as decoded:
                require(list(decoded.size) == definition['dimensions'], root.name, role, 'original image dimensions')
            media = json.loads((root / 'media-map.json').read_text())
            require(media['slots'][role]['src'] == image['file'], root.name, role, 'image media map')
    archive_path = Path(entry['zip'])
    if not archive_path.is_absolute():
        archive_path = REPO / archive_path
    with zipfile.ZipFile(archive_path) as archive:
        require(archive.testzip() is None, root.name, 'ZIP CRC')
        names = [name for name in archive.namelist() if not name.endswith('/')]
        require(len(names) == len(set(names)), root.name, 'duplicate archive filenames')
        require('imsmanifest.xml' in names, root.name, 'root manifest in SCORM ZIP')
        actual = {path.relative_to(root).as_posix() for path in root.rglob('*') if path.is_file()}
        require(set(names) == actual, root.name, 'archive equals current package files')
        for name in names:
            require(archive.read(name) == (root / name).read_bytes(), root.name, 'stale packaged file', name)
    print(f'PASS: {root.name} — local manifest and byte-current SCORM ZIP' + ('; image audit skipped.' if skip_images else '; original image identities verified.'), flush=True)
    return archive_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=REPO / 'Quellen/BRC_LG03/Reihenplan.md')
    parser.add_argument('--series', type=Path, default=REPO / 'Reihen/BRC_LG03/series.json')
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--content-only', action='store_true', help='Skip PDFs and final archive checks while building.')
    parser.add_argument('--skip-image-check', action='store_true', help='Explicitly leave original-image presence/hash checks incomplete; all other artifact checks still run.')
    parser.add_argument('--lesson', help='Comma-separated lesson folders, e.g. LS01,LS12.')
    args = parser.parse_args()
    if not args.source.exists() and args.source == REPO / 'Quellen/BRC_LG03/Reihenplan.md':
        args.source = ATTACHMENT
    raw, lessons, teachers, optional, teacher_all = read_source(args.source)
    if args.source_only:
        return
    series = json.loads(args.series.read_text()) if args.series.exists() else None
    if series:
        entries = series['lessons'] if isinstance(series, dict) else series
        folders = {entry['folder'] for entry in entries}
        require(len(folders) == len(entries), 'series', 'unique lesson entries')
        if not (args.content_only and args.lesson):
            require(folders == {f'LS{i:02}' for i in lessons}, 'series', 'twelve unique lesson entries')
        if isinstance(series, dict):
            require(series['hours'] == 80, 'series', '80 UE')
            require(series['sourceSha256'] == hashlib.sha256(args.source.read_bytes()).hexdigest(), 'series', 'original source SHA-256')
        entries = {int(entry['folder'][2:]): entry for entry in entries}
    else:
        require(args.content_only, 'Missing series.json; use --content-only during construction')
        entries = {}
    selected = {int(value.strip().removeprefix('LS')) for value in args.lesson.split(',')} if args.lesson else set(lessons)
    require(selected <= set(lessons), 'unknown selected lesson')
    all_student_source = '\n\n'.join(f'# LS{number:02}\n\n{lesson["raw"]}' for number, lesson in lessons.items())
    all_student_source += '\n\n# Optionale Wiederholung\n\n' + optional
    fingerprints = teacher_fingerprints(teacher_all, all_student_source)
    source_chapters = dict(sections(raw, 1))
    common_teacher = canonical(markdown_text(source_chapters['Lehrkräfte-Anhang']))
    identities = set()
    competency_ids = set()
    archives = []
    for number in sorted(selected):
        root = args.series.parent / f'LS{number:02}'
        lesson = lessons[number]
        data, _ = verify_content(root, lesson, teachers[number], fingerprints)
        teacher_text = canonical(fragment(data['pages']['erwartungshorizont.html']).text_content())
        require(common_teacher in teacher_text, root.name, 'complete common teacher assessment and guidance')
        if number == 12:
            student_text = canonical('\n'.join(fragment(value).text_content() for filename, value in data['pages'].items()
                                              if filename != 'erwartungshorizont.html'))
            require(canonical(markdown_text(optional)) in student_text, root.name, 'complete optional pupil vocabulary game')
            teacher_game = source_chapters['Lehrkräfte-Ergänzung zum optionalen Begriffsspiel']
            require(canonical(markdown_text(teacher_game)) in teacher_text, root.name, 'complete separate teacher game guidance')
        require(data['id'] not in identities, root.name, 'duplicate lesson ID')
        identities.add(data['id'])
        for competency in data['competencies']:
            require(competency['id'] not in competency_ids, root.name, 'duplicate competency ID')
            competency_ids.add(competency['id'])
        if number in entries:
            require(entries[number]['budgets'] == lesson['budgets'] and entries[number]['hours'] == lesson['hours'], root.name, 'series budgets/hours')
        if not args.content_only:
            verify_pdfs(root, lesson, data, fingerprints, args.skip_image_check)
            archives.append(verify_package(root, entries[number], args.series.parent, args.skip_image_check))
    if not args.lesson:
        require(len(identities) == 12 and len(competency_ids) == 60, 'series', '12 isolated lessons and 60 competency IDs')
    if not args.content_only and not args.lesson:
        included = set()
        for first, last in ((1, 4), (5, 8), (9, 12)):
            collection = REPO / f'Downloads/BRC_LG03_LS{first:02}-LS{last:02}_SCORM.zip'
            expected = {path.name: path for path in archives if first <= int(re.search(r'_LS(\d{2})_', path.name)[1]) <= last}
            require(len(expected) == 4, collection.name, 'four expected checked individual packages')
            require(collection.stat().st_size < 100 * 1024 * 1024, collection.name, 'independent collection remains below 100 MiB')
            with zipfile.ZipFile(collection) as archive:
                require(archive.testzip() is None, collection.name, 'ZIP CRC')
                names = [name for name in archive.namelist() if not name.endswith('/')]
                zip_names = [name for name in names if name.lower().endswith('.zip')]
                actual = [PurePosixPath(name).name for name in zip_names]
                require(len(names) == len(set(names)), collection.name, 'no duplicate member names')
                require(len(actual) == 4 and set(actual) == set(expected), collection.name, 'exactly the intended four complete packages')
                for name in zip_names:
                    basename = PurePosixPath(name).name
                    require(basename not in included, collection.name, 'no duplicate lesson across collections', basename)
                    require(archive.read(name) == expected[basename].read_bytes(), collection.name, 'exact checked individual archive', basename)
                    included.add(basename)
        require(included == {path.name for path in archives}, 'collections', 'all twelve checked packages included once')
        print('PASS: three independent four-lesson collections include exactly the twelve checked SCORM packages without omissions or duplicates; each is below 100 MiB.', flush=True)
    print(f'PASS: LG03 source fidelity and separation checks complete for {len(selected)} lesson(s).', flush=True)


if __name__ == '__main__':
    main()
