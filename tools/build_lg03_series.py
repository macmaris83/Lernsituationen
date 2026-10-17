#!/usr/bin/env python3
"""Build all twelve LG03 lessons with the approved LG01/LS06 application.

The source remains immutable. Student prose, tasks, data and tables are rendered
in full; teacher appendices are kept out of the student print order. The only
application adaptation restores the existing teacher-controlled path selector.
"""
from __future__ import annotations

import argparse
import base64
import copy
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import shutil
import subprocess
import threading
import xml.etree.ElementTree as ET
import zipfile

import fitz
from lxml import html as H
from playwright.sync_api import sync_playwright

from build_brc_series import markdown, radar, quiz_html, workform_icon, workbook_html, ESC
from lg03_runtime import patch_runtime_assets, patch_shell
from lg03_source import load_source, book_references, student_book_text

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / 'Quellen/BRC_LG03'
TEMPLATE = REPO / 'Reihen/BRC_LG01/LS06'
OUT = REPO / 'Reihen/BRC_LG03'
PHASES = ['informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren']
NAMES = ['Informieren', 'Planen', 'Entscheiden', 'Durchführen', 'Überprüfen', 'Reflektieren']
MODES = ['Stark geführt / tradiert', 'Geführt mit Wahlstellen', 'Mittelweg / teiloffen', 'Weitgehend selbstgesteuert', 'Löppt – selbstgesteuert und selbstorganisiert']
VERSION = '2026-10-15.lg03.2'
CLOCK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg>'
TABLE_CSS = '''
/* Wide source tables retain readable amounts inside the existing scroll frame. */
.table-scroll.wide-data-table{overflow-x:auto}
.table-scroll.wide-data-table table{min-width:740px!important;table-layout:auto!important}
.table-scroll.wide-data-table th{overflow-wrap:normal;word-break:normal}
.table-scroll td.numeric-cell{white-space:nowrap;overflow-wrap:normal;word-break:normal}
@media print{.table-scroll.wide-data-table{overflow:visible!important}.table-scroll.wide-data-table table{min-width:0!important;width:100%!important}}
'''


def js_payload(path):
    return json.loads(path.read_text().split('=', 1)[1].strip().rstrip(';'))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def clean_book_source(value):
    """Remove obsolete editorial caveats, as explicitly requested by the user."""
    value = student_book_text(value)
    value = re.sub(r'Buchname und Ausgabe sind auf den vorliegenden Indexbildern nicht erkennbar\.\s*', '', value)
    value = re.sub(r'Die Seiten sind belegte Stichwortseiten, keine behaupteten Kapitelbereiche\.\s*', '', value)
    value = re.sub(r'\*\*Buch:\*\*', '**Lehrbuch:**', value)
    return value


def render(value):
    root = fragments(markdown(clean_book_source(value)))
    for table in root.xpath('.//table'):
        for cell in table.xpath('.//td'):
            if re.fullmatch(r'[+\-−–]?\s*\d[\d\s.,]*\s*(?:€|%|EUR)?', cell.text_content().strip()):
                cell.set('class', 'numeric-cell')
        if max((len(row) for row in table.xpath('.//tr')), default=0) < 6:
            continue
        # Pandoc's pipe-table widths reflect separator syntax rather than the
        # amount of actual text. Let the approved table skin size these columns.
        for group in table.xpath('./colgroup'): table.remove(group)
        wrapper = table.getparent()
        wrapper.set('class', wrapper.get('class', '') + ' wide-data-table')
        wrapper.set('tabindex', '0')
        wrapper.set('aria-label', 'Breite Tabelle – horizontal verschiebbar')
    return serialized(root)


def fragments(value):
    return H.fragment_fromstring(value, create_parent='div')


def serialized(root):
    return ''.join(H.tostring(c, encoding='unicode') for c in root)


def render_assignment(raw, keywords=None):
    # A phase is a complete original instruction, with its exact phase budget.
    # Separate book paragraphs use the original book-icon component. Embedded
    # references remain in their sentence so no instruction can disappear.
    keywords = keywords or {}
    for reference in reversed(book_references(raw)):
        citation = reference['text']
        content_start = reference['start'] + len('**Buch:**')
        while content_start < len(raw) and raw[content_start].isspace():
            content_start += 1
        # Inline reference metadata can deliberately stop before an operative
        # continuation ("und dokumentieren Sie …"). Its sentence end offset is
        # broader; replace only the actual citation, never that continuation.
        replacement_end = content_start + len(citation)
        assert raw[content_start:replacement_end] == citation
        residue = re.sub(r'\b(?:S|und|sowie|bzw)\b|[\d\s.,/;–—()\-]', '', citation)
        if not residue:
            def keyword(match):
                page = match[1]
                if page not in keywords:
                    raise ValueError('Missing sourced textbook keyword for page ' + page)
                return '<span class="book-keyword">' + ESC(keywords[page]) + ' </span>' + match[0]
            citation = re.sub(r'S\.\s*(\d+)', keyword, citation)
        # Source offset bounds preserve embedded citations in their sentence.
        # A complete final book sentence becomes the template's separate line.
        if reference['standalone']:
            replacement = '\n\n**Buch:** ' + citation + '\n\n'
        else:
            replacement = '**Buch:** ' + citation
        raw = raw[:reference['start']] + replacement + raw[replacement_end:]
    document = fragments(render(raw))
    operators = ('Lesen|Markieren|Berechnen|Unterscheiden|Halten|Übernehmen|Teilen|Tragen|'
                 'Wählen|Begründen|Entscheiden|Füllen|Formulieren|Nutzen|Tauschen|Prüfen|'
                 'Rechnen|Erklären|Bearbeiten|Notieren|Erschließen|Planen|Erstellen|Entwickeln|'
                 'Analysieren|Ermitteln|Ordnen|Erläutern|Vergleichen|Skizzieren|Stellen|'
                 'Diskutieren|Beurteilen|Überprüfen|Beschreiben|Bewerten|Reflektieren|'
                 'Untersuchen|Benennen|Dokumentieren|Zeigen|Leiten|Verfassen|Sichern|'
                 'Sammeln|Bilden|Legen|Arbeiten|Führen|Kontrollieren|Bewahren|Definieren|'
                 'Visualisieren|Entwerfen|Gestalten|Entscheiden|Argumentieren|Organisieren')
    for p in document.xpath('.//p'):
        if p.text_content().strip().startswith('Lehrbuch:'):
            # Keep the keyword spans as a verifiable, sourced addition.
            marker = p.find('strong')
            if marker is None: raise ValueError('Missing book marker')
            span = H.Element('span', {'class': 'book-reference'})
            span.text = (marker.tail or '').lstrip()
            p.remove(marker)
            for child in list(p): span.append(child)
            p.text = None
            p.set('class', 'book-line')
            icon = H.Element('img', {'class': 'book-ref-icon', 'src': 'assets/lehrbuch-icon.png', 'alt': 'Lehrbuch'})
            p.extend([icon, span])
        else:
            for marker in p.xpath('.//strong'):
                if marker.text_content().strip() == 'Lehrbuch:':
                    icon = H.Element('img', {'class': 'book-ref-icon', 'src': 'assets/lehrbuch-icon.png', 'alt': 'Lehrbuch', 'title': 'Lehrbuch'})
                    icon.tail = marker.tail
                    marker.getparent().replace(marker, icon)
    result = serialized(document)
    # Inline emphasis does not change text. Keep existing emphasis and avoid
    # matching tag attributes or splitting separable operators.
    chunks = re.split(r'(<[^>]*>)', result)
    depth = 0
    for i, chunk in enumerate(chunks):
        if chunk.startswith('<'):
            if re.match(r'<strong(?:\s|>)', chunk): depth += 1
            elif chunk.startswith('</strong'): depth = max(0, depth - 1)
        elif not depth:
            chunks[i] = re.sub(r'\b(' + operators + r')(?= Sie\b)', r'<strong class="operator">\1</strong>', chunk)
    return ''.join(chunks)


def competency_remainder(raw):
    """The competency statements themselves already appear in orientation."""
    rendered = fragments(render(raw))
    for table in rendered.xpath('.//table'):
        parent = table.getparent()
        if parent.get('class') == 'table-scroll':
            parent.getparent().remove(parent)
        else:
            parent.remove(table)
    for p in list(rendered.xpath('./p')):
        if p.text_content().startswith('Vorrangige Fachkompetenz:'):
            rendered.remove(p)
    return serialized(rendered)


def material_list(ls, types):
    result = []
    for heading, raw in ls['materials']:
        match = re.match(r'M(\d+)\s*[–-]\s*(.*)', heading)
        assert match, heading
        n = int(match[1])
        assert n == len(result) + 1, (ls['number'], heading)
        result.append({'number': n, 'title': match[2], 'raw': raw,
                       'kind': types[str(ls['number'])][f'M{n}'], 'sourceKey': f'M{n}'})
    def extra(title, raw, key, kind='onenote', rendered=None):
        result.append({'number': len(result) + 1, 'title': title, 'raw': raw,
                       'kind': kind, 'sourceKey': key, 'rendered': rendered})
    for heading, raw in ls.get('book_access', []):
        extra('Lehrbuch · Stichwörter und Seiten', raw, 'book_access', 'acrobat')
    for heading, raw in ls.get('extra_materials', []):
        extra(heading, raw, 'extra:' + heading)
    context = render(ls['parts'][1]) + competency_remainder(ls['parts'][3])
    context = context.replace('Standalone-Einstieg:', 'Ausgangslage:')
    extra('Ihr Auftrag im Überblick', ls['parts'][1], 'assignment_overview', rendered=context)
    extra('Das nehmen Sie fachlich mit', ls['parts'][7], 'section7')
    extra('Operatoren, Lernbegleitung und KI', ls['parts'][8], 'section8')
    if ls['number'] == 12 and ls.get('optional_activity'):
        extra('Optionale Wiederholung · Sag es anders: BioCasa', ls['optional_activity'], 'optional_activity')
    return result


def document_html(material):
    template = H.parse(str(REPO / 'Materialvorlagen' / (material['kind'] + '.html')))
    wrapper = template.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," source-document ")]')[0]
    paper = wrapper.xpath('.//article[contains(concat(" ",normalize-space(@class)," ")," paper ")]')[0]
    for child in list(paper): paper.remove(child)
    paper.text = None
    body = fragments(material.get('rendered') or render(material['raw']))
    if body.text: paper.text = body.text
    for child in list(body): paper.append(child)
    for span in wrapper.xpath('.//span[contains(concat(" ",normalize-space(@class)," ")," file ")]'):
        span.text = material['title']
    return H.tostring(wrapper, encoding='unicode')


def content(ls, competencies, checks, forms, types, book_keywords):
    n = ls['number']; pages = {}; titles = {'index.html': 'Orientierung', 'handlungssituation.html': 'Handlungssituation'}
    titles.update({phase + '.html': title for phase, title in zip(PHASES, NAMES)})
    mats = material_list(ls, types)
    titles.update({f'm{m["number"]}.html': f'M{m["number"]} · {m["title"]}' for m in mats})
    titles['erwartungshorizont.html'] = 'Erwartungshorizont und Lehrkräftehinweise'
    def hero(label):
        return f'<section class="card hero"><div class="eyebrow">BRC · LG03 · LS{n:02d} · {ESC(ls["title"])}</div><h1>{ESC(label)}</h1></section>'
    access = '<section class="card phase-materials material-access" aria-label="Materialzugriff"><h2>Materialzugriff</h2><nav class="material-grid" aria-label="Materialien">' + ''.join(
        f'<a class="material-link" href="m{m["number"]}.html"><b>M{m["number"]}</b><span> · {ESC(m["title"])}</span></a>' for m in mats) + '</nav></section>'
    details = ''.join('<article class="card"><h3><strong>' + ESC(c['label']) + '</strong></h3><p>' + ESC(competencies['priorityStatement'] if c['label'] == 'Fachkompetenz' else c['statement']) + '</p></article>' for c in competencies['competencies'])
    pages['index.html'] = hero(ls['title']) + '<section class="card relevance"><h2>Darum ist das Thema relevant</h2><figure class="story-photo" data-media-key="orientation"></figure>' + render(ls['parts'][2]) + '</section><section class="card priority-section"><h2>Kompetenzprofil</h2><section class="weight-radar">' + radar(competencies['competencies']) + '</section><div class="competence-cards orientation-competencies">' + details + '</div></section>'
    pages['handlungssituation.html'] = hero('Handlungssituation') + access + '<section class="card situation-prose"><figure class="story-photo" data-media-key="situation"></figure>' + render(ls['parts'][4]) + '</section>' + quiz_html(checks)
    instructions = {}; counts = {}
    for pi, phase in enumerate(PHASES):
        result = hero(NAMES[pi]) + access
        instructions[phase] = {}; counts[phase] = {}
        for mode in range(1, 6):
            raw = ls['modes'][mode]['phases'][pi]
            task = render_assignment(raw, book_keywords.get(f'LS{n:02d}', {}))
            form = forms[f'LS{n:02d}:{phase}:{mode}:1']
            minutes = ls['budgets'][pi]
            instructions[phase][mode] = {'tasks': [task], 'times': [minutes], 'workforms': [form], 'meta': {}}
            counts[phase][mode] = 1
            result += f'<section class="task-card phase-mode" data-mode-panel="{mode}" data-phase="{phase}"><h2 class="phase-mode-title">{chr(64+mode)} · {ESC(MODES[mode-1])}</h2><div class="phase-meta"><p>{CLOCK}<span><strong>Arbeitszeit:</strong> {minutes} Minuten</span></p><p>{workform_icon(form["kind"])}<span><strong>Arbeitsform:</strong> {ESC(form["label"])}</span></p></div>'
            if ls['modes'][mode].get('intro'):
                result += '<details class="series-way-brief"><summary>Auftrag und Zielkern</summary>' + render(ls['modes'][mode]['intro']) + '</details>'
            result += '<div class="task-text"><article class="assignment-frame" data-task-number="1" data-goodnotes-task="true"><span class="assignment-number" aria-label="Auftrag 1">1</span><button type="button" class="assignment-goodnotes-button" data-share-workbook aria-label="Arbeitsheft dieser Phase in GoodNotes importieren"><img class="assignment-goodnotes" src="assets/goodnotes.png" alt="GoodNotes"></button>'
            result += f'<span class="assignment-social" data-workform="{ESC(form["kind"])}" title="{ESC(form["label"])}">{workform_icon(form["kind"])}<small>{ESC(form["label"])}</small></span><div class="assignment-body">{task}<span class="assignment-time" data-time-ui="true" data-minutes="{minutes}">{CLOCK} ca. {minutes} Min.</span></div></article></div></section>'
        if phase == 'reflektieren': result += '<div data-assessment-widget></div>'
        pages[phase + '.html'] = result
    for m in mats:
        pages[f'm{m["number"]}.html'] = hero(f'M{m["number"]} · {m["title"]}') + access + document_html(m)
    teacher = ''
    for key in ['teacher_common', 'teacher_group_intro', 'teacher_appendix']:
        if ls.get(key): teacher += '<section class="card">' + render(ls[key]) + '</section>'
    if n == 12 and ls.get('teacher_optional'):
        teacher += '<section class="card">' + render(ls['teacher_optional']) + '</section>'
    pages['erwartungshorizont.html'] = hero('Erwartungshorizont und Lehrkräftehinweise') + teacher
    return pages, titles, instructions, counts, mats


def shell(page, body, ls):
    path = TEMPLATE / page
    if not path.exists(): path = TEMPLATE / 'm1.html'
    original = patch_shell(path.read_text(), ls['number'], ls['title'], cache_version='lg03-20261015-2')
    original = re.sub(r'data-page="[^"]*"', f'data-page="{page}"', original)
    if page not in ['lehrkraft.html', 'scorm.html', 'druckansicht.html']:
        start = original.index('<div class="lesson-content">') + len('<div class="lesson-content">')
        end = original.index('</div></main>', start)
        original = original[:start] + body + original[end:]
    for mode, title in enumerate(MODES, 1):
        original = re.sub(r'(<option value="' + str(mode) + r'">)[^<]+', lambda m: m[1] + chr(64+mode) + ' · ' + ESC(title), original)
    original = original.replace('Unterstützungsstufe', 'Lernweg').replace('>Stufe <', '>Lernweg <')
    return original


def manifest(root, ls):
    ns = 'http://www.imsproject.org/xsd/imscp_rootv1p1p2'; adl = 'http://www.adlnet.org/xsd/adlcp_rootv1p2'
    ET.register_namespace('', ns); ET.register_namespace('adlcp', adl)
    e = lambda tag: '{' + ns + '}' + tag
    tree = ET.Element(e('manifest'), {'identifier': f'BRC_LG03_LS{ls["number"]:02d}_SCORM', 'version': '1.0'})
    meta = ET.SubElement(tree, e('metadata')); ET.SubElement(meta, e('schema')).text = 'ADL SCORM'; ET.SubElement(meta, e('schemaversion')).text = '1.2'
    orgs = ET.SubElement(tree, e('organizations'), {'default': 'ORG_MAIN'})
    org = ET.SubElement(orgs, e('organization'), {'identifier': 'ORG_MAIN', 'structure': 'hierarchical'})
    ET.SubElement(org, e('title')).text = ls['title']
    item = ET.SubElement(org, e('item'), {'identifier': 'ITEM_MAIN', 'identifierref': 'RES_MAIN', 'isvisible': 'true'})
    ET.SubElement(item, e('title')).text = ls['title']
    resources = ET.SubElement(tree, e('resources'))
    resource = ET.SubElement(resources, e('resource'), {'identifier': 'RES_MAIN', 'type': 'webcontent', 'href': 'scorm.html', '{'+adl+'}scormtype': 'sco'})
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.name != 'imsmanifest.xml': ET.SubElement(resource, e('file'), {'href': path.relative_to(root).as_posix()})
    ET.ElementTree(tree).write(root / 'imsmanifest.xml', encoding='utf-8', xml_declaration=True)


def zip_package(root, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(root.rglob('*')):
            if path.is_file(): z.write(path, path.relative_to(root).as_posix())


def prepare_images(ls, root, pictures, allow_missing):
    info = {}; slots = {}
    for role in ['orientation', 'situation']:
        picture = pictures.get(str(ls['number']), {}).get(role)
        if not picture:
            if allow_missing: continue
            raise ValueError(f'Missing original image: LS{ls["number"]:02d} {role}')
        name = picture['filename']; assert Path(name).name == name
        source = SOURCE / 'Bilder' / name
        target = root / 'assets/images' / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, target)
        relative = target.relative_to(root).as_posix()
        info[role] = {'file': relative, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
        slots[role] = {'src': relative, 'alt': picture['alt'], 'label': ('Orientierung' if role == 'orientation' else 'Handlungssituation') + ' · ' + ls['title']}
    write_json(root / 'media-map.json', {'slots': slots})
    (root / 'media-map.js').write_text('window.SOZ_MEDIA=' + json.dumps({'slots': slots}, ensure_ascii=False) + ';\n')
    return info


def collection_archives(summaries):
    """Bundle four full packages per ZIP without recompressing original images."""
    for group in [summaries[:4], summaries[4:8], summaries[8:]]:
        first, last = group[0]['folder'], group[-1]['folder']
        target = REPO / f'Downloads/BRC_LG03_{first}-{last}_SCORM.zip'
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_STORED) as z:
            for x in group: z.write(REPO / x['zip'], Path(x['zip']).name)
            z.writestr('LIESMICH.txt', f'BioCasa · BRC LG03 · {first}–{last}\nVier vollständige Einzelpakete, jeweils fünf alternative Lernwege.\nDieses Sammelarchiv zuerst entpacken. In Moodle jede enthaltene SCORM-ZIP als eigene SCORM-Aktivität hochladen.\nDie drei Sammelarchive sind unabhängig entpackbar; sie müssen nicht zusammengesetzt werden.\nDie Lehrkraft stellt den Lernweg ein und kann den Wechsel durch Lernende freigeben.\nPDF-Gesamtdokument und phasenbezogener GoodNotes-Import entsprechen der vorhandenen Vorlage.\n')
        if target.stat().st_size >= 100 * 1024**2:
            raise ValueError('Collection exceeds GitHub file limit: ' + str(target))
        print('Collection:', target, flush=True)
    # Remove only earlier generated collections replaced by these three.
    for old in ['BRC_LG03_PlugAndPlay_Gesamtreihe_SCORM.zip',
                'BRC_LG03_LS01-LS06_SCORM.zip', 'BRC_LG03_LS07-LS12_SCORM.zip']:
        (REPO / 'Downloads' / old).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=SOURCE / 'Reihenplan.md')
    parser.add_argument('--allow-missing-images', action='store_true', help='Internal draft only; final build requires all 24 originals.')
    parser.add_argument('--no-pdf', action='store_true', help='Build HTML and metadata for preliminary browser checks.')
    parser.add_argument('--only', type=int, nargs='+')
    args = parser.parse_args()
    lessons = load_source(args.source)
    checks = json.loads((SOURCE / 'Einstiegskontrollen.json').read_text())
    comps = json.loads((SOURCE / 'Kompetenzen_Ich.json').read_text())
    forms = json.loads((SOURCE / 'Arbeitsformen.json').read_text())
    types = json.loads((SOURCE / 'Materialtypen.json').read_text())
    book_keywords = json.loads((SOURCE / 'Lehrbuchstichwoerter.json').read_text())
    pictures = json.loads((SOURCE / 'Bildzuordnung.json').read_text()) if (SOURCE / 'Bildzuordnung.json').exists() else {}
    if args.only: lessons = [ls for ls in lessons if ls['number'] in args.only]
    OUT.mkdir(parents=True, exist_ok=True)
    built = []; summaries = []
    for ls in lessons:
        n = ls['number']; root = OUT / f'LS{n:02d}'
        root.mkdir(exist_ok=True); (root / 'pdf').mkdir(exist_ok=True)
        shutil.copytree(TEMPLATE / 'assets', root / 'assets', dirs_exist_ok=True)
        shutil.rmtree(root / 'assets/images', ignore_errors=True)
        (root / 'assets/images').mkdir()
        for name in ['biocasa-szenen.jpg', 'handlungssituation.jpg']:
            (root / 'assets' / name).unlink(missing_ok=True)
        app_report = patch_runtime_assets(root)
        css = root / 'assets/styles.css'
        css.write_text(css.read_text() + TABLE_CSS)
        image_info = prepare_images(ls, root, pictures, args.allow_missing_images)
        cc = copy.deepcopy(comps[str(n)])
        for c in cc['competencies']:
            c['id'] = f'BRC-LG03-LS{n:02d}-' + {'Fachkompetenz':'F','Personalkompetenz':'P','Sozialkompetenz':'S','Methodenkompetenz':'M','Medienkompetenz':'D'}[c['label']]
        pages, titles, instructions, counts, mats = content(ls, cc, checks[str(n)], forms, types, book_keywords)
        data = {'id': f'BRC-LG03-LS{n:02d}', 'title': ls['title'], 'version': VERSION,
                'priorityStatement': cc['priorityStatement'], 'competencies': cc['competencies'],
                'pages': pages, 'pageTitles': titles, 'printOrder': [p for p in pages if p != 'erwartungshorizont.html'],
                'workbook': f'pdf/GoodNotes_LG03_LS{n:02d}_W1.pdf',
                'workbooks': {str(m): f'pdf/GoodNotes_LG03_LS{n:02d}_W{m}.pdf' for m in range(1,6)},
                'phaseBudgets': dict(zip(PHASES, ls['budgets'])), 'sourceTaskCounts': counts,
                'materialSources': {f'm{m["number"]}.html': {k:m[k] for k in ['title','kind','sourceKey']} for m in mats}}
        cfg = json.loads((TEMPLATE / 'Konfiguration.json').read_text())
        cfg.update({'mode': 1, 'allowStudentMode': False, 'packageRevision': f'BRC-LG03-LS{n:02d}-20261015-2', 'overrides': {}, 'media': {}, 'moodle': {}})
        write_json(root / 'Konfiguration.json', cfg)
        (root / 'mode-config.js').write_text('window.SOZ_CONFIG=' + json.dumps(cfg, ensure_ascii=False) + ';\n')
        built.append((ls, root, data, instructions))
        summaries.append({'folder': root.name, 'id': data['id'], 'title': ls['title'], 'hours': ls['hours'], 'budgets': ls['budgets'],
                          'materials': len(ls['materials']), 'allMaterials': len(mats), 'tasks': counts, 'images': image_info,
                          'zip': f'Downloads/BRC_LG03_LS{n:02d}_SCORM.zip', 'sharedJavascriptSha256': app_report['sharedJavascriptSha256']})
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page()
        for ls, root, data, instructions in built:
            page.goto('about:blank'); page.add_script_tag(path=str(root / 'assets/progress-core.js'))
            result = page.evaluate('d=>{const meta=SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser());return {data:d,meta};}', json.loads(json.dumps(data)))
            data = result['data']
            (root / 'lesson-data.js').write_text('window.SOZPAED=' + json.dumps(data, ensure_ascii=False, separators=(',',':')) + ';\n')
            (root / 'progress-meta.js').write_text('window.SOZ_PROGRESS_META=' + json.dumps(result['meta'], ensure_ascii=False, separators=(',',':')) + ';\n')
            for name, body in data['pages'].items(): (root / name).write_text(shell(name, body, ls))
            for name in ['lehrkraft.html','druckansicht.html','scorm.html']: (root / name).write_text(shell(name, '', ls))
            if not args.no_pdf:
                for phase in PHASES:
                    for mode in range(1,6):
                        book = workbook_html(ls, phase, mode, instructions[phase][mode]).replace('LG01', 'LG03')
                        # Preserve the original icon even when Chromium's
                        # about:blank document cannot read file: resources.
                        icon = base64.b64encode((root / 'assets/lehrbuch-icon.png').read_bytes()).decode()
                        book = book.replace('src="assets/lehrbuch-icon.png"', 'src="data:image/png;base64,' + icon + '"')
                        book = book.replace('</style>', '.book-ref-icon{width:38px;height:auto;vertical-align:middle}.book-line{display:flex;align-items:center;gap:8px}.book-reference{font-size:10pt}</style>')
                        page.set_content(book); file = root / f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf'
                        page.pdf(path=str(file), print_background=True, prefer_css_page_size=True)
                        encoded = base64.b64encode(file.read_bytes()).decode()
                        (root / f'goodnotes-phase-{phase}-W{mode}.js').write_text('window.GOODNOTES_PHASES=window.GOODNOTES_PHASES||{};window.GOODNOTES_PHASES[' + json.dumps(phase+':'+str(mode)) + ']=' + json.dumps(encoded) + ';\n')
                for mode in range(1,6):
                    book = fitz.open()
                    for phase in PHASES:
                        with fitz.open(root / f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf') as fragment: book.insert_pdf(fragment)
                    book.save(root / f'pdf/GoodNotes_LG03_LS{ls["number"]:02d}_W{mode}.pdf'); book.close()
            print('Built:', root.name, ls['title'], len(result['meta']['tasks']), 'original phase assignments', flush=True)
        browser.close()
    if not args.no_pdf:
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args): pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(REPO)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
                page = browser.new_page()
                for ls, root, data, instructions in built:
                    page.goto(f'http://127.0.0.1:{server.server_port}/' + root.relative_to(REPO).as_posix() + '/druckansicht.html')
                    page.wait_for_function('window.SOZ_READY===true')
                    page.evaluate('async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r})));}')
                    page.pdf(path=str(root / f'pdf/LG03_LS{ls["number"]:02d}_Gesamtdruck_A4.pdf'), print_background=True, prefer_css_page_size=True)
                    manifest(root, ls)
                    zip_package(root, REPO / f'Downloads/BRC_LG03_LS{ls["number"]:02d}_SCORM.zip')
                    print('Packed:', root.name, flush=True)
                browser.close()
        finally: server.shutdown()
    else:
        for ls, root, data, instructions in built: manifest(root, ls)
    series = {'title': 'BRC LG03 · Wettbewerbsfähigkeit unter marketingpolitischen und kostenrechnerischen Aspekten sichern', 'hours': 80,
              'template': 'Reihen/BRC_LG01/LS06', 'templateCommit': 'bcd1140e0a86287709a9709a20ac2ad618b23f6b',
              'sourceSha256': hashlib.sha256(args.source.read_bytes()).hexdigest(), 'completeImages': all(len(x['images']) == 2 for x in summaries),
              'lessons': summaries}
    write_json(OUT / 'series.json', series)
    links = ''.join(f'<article><small>LS{x["folder"][2:]} · {x["hours"]} Unterrichtsstunden</small><h2>{ESC(x["title"])}</h2><p><a href="{x["folder"]}/index.html">Lernsituation öffnen</a> · <a href="../../{x["zip"]}" download>SCORM-ZIP herunterladen</a></p></article>' for x in summaries)
    (OUT / 'index.html').write_text('<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BioCasa · BRC LG03</title><link rel="stylesheet" href="LS01/assets/styles.css"><style>article{padding:18px;border:1px solid #b8e0f2;border-radius:14px;background:#ffffffbb;margin:14px 0}</style><body><main class="shell main"><h1>BioCasa · Wettbewerbsfähigkeit sichern</h1><p>Zwölf Lernsituationen · 80 Unterrichtsstunden</p>' + links + '</main></body></html>')
    if not args.no_pdf and not args.only:
        collection_archives(summaries)


if __name__ == '__main__':
    main()
