#!/usr/bin/env python3
"""Bring the explicitly supplied LG01 1.4 delivery to the catalogue UI standard.

This operates on a delivery, not on the catalogue's distinct BRC master IDs.
Original tasks, configuration, progress metadata and PDFs remain byte-identical.
"""
from __future__ import annotations
import argparse
import copy
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import shutil
import threading
import xml.etree.ElementTree as ET
import zipfile
from lxml import html as H
from lxml.etree import SubElement
from playwright.sync_api import sync_playwright
from install_calculator import install as install_calculator
from install_ipad_layout import install as install_ipad_layout
from install_print_layout import install as install_print_layout

REPO = Path(__file__).resolve().parents[1]
ICH = [
[
"Ich unterscheide wirtschaftliche, soziale und ökologische Ziele, analysiere Zielbeziehungen und Stakeholderinteressen, bestimme die Betriebsart und übertrage grundlegende Leistungsprozesse auf BioCasa.",
"Ich gleiche eigene Vorstellungen mit überprüfbaren Informationen ab und erkenne, welche Stärken und Interessen ich in eine Gruppenentscheidung einbringe.",
"Ich vertrete unterschiedliche Gründerperspektiven sachlich, bearbeite Zielkonflikte und treffe eine kompromissfähige gemeinsame Entscheidung.",
"Ich entnehme Informationen aus betrieblichen Dokumenten, ordne Ziele und Interessen nach vorgegebenen Kriterien und verdichte meine Ergebnisse.",
"Ich nutze eine vorgegebene digitale Vorlage zur gemeinsamen Dokumentation und kennzeichne die Herkunft übernommener Informationen."
], [
"Ich unterscheide Gründungsvoraussetzungen, ordne offene Fragen zuständigen Stellen zu und bringe notwendige Schritte in eine sachlogische Reihenfolge.",
"Ich gleiche Anforderungen mit den vorhandenen Kompetenzen des Gründerteams ab, erkenne Lücken und übernehme begründet Verantwortung für Maßnahmen.",
"Ich verteile Aufgaben fair nach Kompetenzen und Ressourcen und stimme parallele Arbeitsschritte mit anderen ab.",
"Ich prüfe Quellen nach Absender, Aktualität, Zuständigkeit und Verbindlichkeit und verdichte Informationen in einem umsetzbaren Maßnahmenplan.",
"Ich nutze offizielle digitale Informationsangebote, dokumentiere Links und Abrufdatum und unterscheide Primärquellen von allgemeinen Ratgeberseiten."
], [
"Ich analysiere Markt- und Unternehmensdaten, treffe zusammenhängende Entscheidungen zu Produkt, Preis, Distribution und Kommunikation und ermittle daraus den Kapitalbedarf.",
"Ich bearbeite einen umfangreichen Auftrag nach vorgegebenen Etappen, prüfe eigene Annahmen und übernehme Verantwortung für die Qualität eines Teilbereichs.",
"Ich führe Teilanalysen zusammen, löse Widersprüche zwischen Funktionsbereichen und vertrete Entscheidungen gegenüber anderen Arbeitsgruppen.",
"Ich strukturiere heterogene Informationen, rechne Szenariodaten aus, dokumentiere Annahmen und erstelle ein konsistentes Gesamtdokument.",
"Ich nutze Tabellenkalkulation und Textverarbeitung nach Vorgabe, setze Formeln nachvollziehbar ein und führe einen digitalen Konsistenzcheck durch."
], [
"Ich analysiere Konditionen, Kosten, Liquiditätswirkungen, Risiken und Zweckbindung der drei Finanzierungsformen und entwickle daraus ein tragfähiges Konzept.",
"Ich vertrete eine belastbare Position unter Nachfragen, erkenne Unsicherheiten an und reagiere sachlich auf Kritik.",
"Ich einige mich trotz unterschiedlicher Risikovorstellungen mit anderen auf eine gemeinsame Botschaft, übernehme meinen Anteil an der Verteilung der Sprechrollen und gebe kriteriengeleitet Feedback.",
"Ich berechne Finanzierungswirkungen, führe einen Stressvergleich durch und verdichte komplexe Informationen für eine Entscheidung.",
"Ich erstelle ein übersichtliches Pitchdeck, visualisiere Planwerte korrekt und präsentiere mit digitalen Medien adressatengerecht."
], [
"Ich unterscheide Firma, Kaufmannseigenschaft, Handelsregister, Geschäftsführung, Vertretung und Haftung und wende die Rechtsformmerkmale auf den BioCasa-Fall an.",
"Ich erkenne eigene Risikopräferenzen, trenne persönliche Wünsche von rechtlichen Folgen und vertrete ein begründetes Urteil.",
"Ich bearbeite den Konflikt zwischen Kapital, Expertise, Haftung und Einfluss und entwickle mit anderen eine gemeinsam tragfähige Governance-Lösung.",
"Ich erschließe angeleitet Gesetzesauszüge, wende eine gewichtete Entscheidungsmatrix an und verfasse eine nachvollziehbare Beschlussvorlage.",
"Ich nutze aktuelle amtliche Rechtsquellen, dokumentiere Rechtsstand und Fundstelle und unterscheide Gesetz, IHK-Orientierung und individuelle Beratung."
], [
"Ich rekonstruiere einen Vertrag aus einer Dokumentenkette, wende Kauf- und Mängelrecht an, beurteile Zahlungsalternativen und treffe eine begründete Personalentscheidung.",
"Ich handle unter Zeitdruck sorgfältig, übernehme Fehlerverantwortung und wäge Kundenbeziehung, Liquidität und Personalbindung ab.",
"Ich koordiniere Vertrieb, Qualität, Finanzen und Personal und formuliere mit anderen eine gemeinsame professionelle Kundenposition.",
"Ich erstelle eine Vertragschronologie, berechne Zahlungs- und Personalwirkungen, prüfe Rechtsfolgen und führe Teilentscheidungen in einer Auftragsakte zusammen.",
"Ich arbeite mit einer digitalen Dokumentenkette, nutze Tabellenkalkulation für Vergleiche und verfasse eine adressatengerechte geschäftliche E-Mail."
]]


def payload(path):
    return json.loads(path.read_text().split('=', 1)[1].strip().rstrip(';'))


def dump(path, value, prefix=None):
    text = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    path.write_text((prefix + '=' + text + ';\n') if prefix else json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def fragment(value): return H.fragment_fromstring(value, create_parent='div')


def serialize(root): return ''.join(H.tostring(c, encoding='unicode') for c in root)


def compact_orientation(data, statements):
    root = fragment(data['pages']['index.html'])
    for block in root.xpath('./section[contains(@class,"material-access")]'):
        root.remove(block)
    old = root.xpath('./section[contains(@class,"competence-overview") or contains(@class,"priority-section")]')[0]
    chart = old.xpath('.//*[local-name()="svg"]')[0]
    chart.set('style', 'display:block;width:100%;max-width:420px;margin:0 auto;overflow:visible')
    new = H.Element('section', {'class': 'card priority-section'})
    SubElement(new, 'h2').text = 'Kompetenzprofil'
    radar = SubElement(new, 'section', {'class': 'weight-radar'}); radar.append(chart)
    cards = SubElement(new, 'div', {'class': 'competence-cards orientation-competencies'})
    for competency, statement in zip(data['competencies'], statements):
        competency['statement'] = statement
        article = SubElement(cards, 'article', {'class': 'card'})
        heading = SubElement(article, 'h3'); SubElement(heading, 'strong').text = competency['label']
        SubElement(article, 'p').text = statement
    data['priorityStatement'] = statements[0]
    root.replace(old, new)
    data['pages']['index.html'] = serialize(root)


def protect_orientation_signature(root, data, original_meta, page):
    core_path = root / 'assets/progress-core.js'
    core = core_path.read_text()
    old = 'orientationSignature:hash(orientationText(index.body))'
    replacement = "orientationSignature:(data.orientationPresentation?.renderedSignature===hash(orientationText(index.body))?data.orientationPresentation.sourceSignature:hash(orientationText(index.body)))"
    assert core.count(old) == 1, 'Expected the approved signature computation'
    core_path.write_text(core.replace(old, replacement))
    page.goto('about:blank'); page.add_script_tag(path=str(core_path))
    rendered = page.evaluate('d=>SOZ_PROGRESS_CORE.metadataFrom(structuredClone(d),new DOMParser()).orientationSignature', data)
    data['orientationPresentation'] = {'renderedSignature': rendered, 'sourceSignature': original_meta['orientationSignature']}
    actual = page.evaluate('d=>SOZ_PROGRESS_CORE.metadataFrom(structuredClone(d),new DOMParser())', data)
    for key in ('tasks', 'quiz', 'quizSignature', 'orientationSignature', 'competencies'):
        assert actual[key] == original_meta[key], (root.name, key, 'must retain learning progress')
    edited = copy.deepcopy(data)
    edited['pages']['index.html'] = edited['pages']['index.html'].replace('Darum ist das Thema relevant', 'Inhaltlich geänderte Orientierung', 1)
    assert page.evaluate('d=>SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser()).orientationSignature', edited) != original_meta['orientationSignature']


def manifest(root):
    path = root / 'imsmanifest.xml'; tree = ET.parse(path)
    for resource in tree.getroot().iter():
        if resource.tag.split('}')[-1] != 'resource': continue
        ns = resource.tag.rsplit('}', 1)[0] + '}' if '}' in resource.tag else ''
        for node in list(resource):
            if node.tag.split('}')[-1] == 'file': resource.remove(node)
        for file in sorted(root.rglob('*')):
            if file.is_file() and file != path: ET.SubElement(resource, ns + 'file', {'href': file.relative_to(root).as_posix()})
    tree.write(path, encoding='utf-8', xml_declaration=True)


def archive(root, target):
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in sorted(root.rglob('*')):
            if file.is_file(): z.write(file, file.relative_to(root).as_posix())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path, help='Folder with the six extracted LS01..LS06 originals')
    ap.add_argument('output', type=Path)
    ap.add_argument('--version', default='1.7', help='Two-part delivery version')
    args = ap.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    preview = args.output / 'preview'; preview.mkdir(exist_ok=True)
    catalog = json.loads((REPO / 'master-katalog.json').read_text())['packages']
    if not re.fullmatch(r'\d+\.\d+', args.version): ap.error('Version must contain two numbers, for example 1.6')
    report = {'version': args.version, 'referenceCommit': '8dd3853c69e1d33499037956c5fe3096fd2016f7', 'lessons': []}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        page = browser.new_page()
        for n in range(1, 7):
            name = f'LS{n:02d}'; source = args.input / name; target = preview / name
            shutil.copytree(source, target, dirs_exist_ok=True)
            entry = next(x for x in catalog if x['id'] == f'BRC-LG01-{name}')
            reference = REPO / entry['master']
            data = payload(source / 'lesson-data.js'); meta = payload(source / 'progress-meta.js')
            compact_orientation(data, ICH[n-1])
            protect_orientation_signature(target, data, meta, page)
            teacher_view = target / 'assets/teacher-view.js'
            script = teacher_view.read_text()
            old = "select.addEventListener('change',()=>{remember(select.value);location.reload();});"
            new = "select.addEventListener('change',()=>{remember(select.value);try{sessionStorage.removeItem('teacher:task-focus-return:'+D.id);}catch{}const next=new URL(location.href);next.searchParams.delete('aufgabe');next.searchParams.delete('rueckaufgabe');location.replace(next.href);});"
            assert script.count(old) == 1
            teacher_view.write_text(script.replace(old, new))
            dump(target / 'lesson-data.js', data, 'window.SOZPAED')
            # The shell and current individual-task runtime are already the
            # catalogue's UI plus the supplied 1.4 clock/editor improvements.
            for style in ('styles.css', 'phases.css', 'lg01.css', 'print.css', 'material-views.css'):
                assert (source / 'assets' / style).read_bytes() == (reference / 'assets' / style).read_bytes(), style
            media = json.loads((reference / 'media-map.json').read_text())
            for slot in media['slots'].values():
                file = target / slot['src']; file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(reference / slot['src'], file)
                assert 'crop' not in slot
            dump(target / 'media-map.json', media); dump(target / 'media-map.js', media, 'window.SOZ_MEDIA')
            for file in target.glob('*.html'):
                raw = file.read_text()
                if file.name == 'index.html':
                    start = raw.index('<div class="lesson-content">') + len('<div class="lesson-content">')
                    end = raw.index('</div></main>', start)
                    raw = raw[:start] + data['pages']['index.html'] + raw[end:]
                raw = raw.replace('lg01-bilder-aufgaben-20261014', 'lg01-upload-' + args.version.replace('.', '-') + '-20261016')
                file.write_text(raw)
            dump(target / 'Paketversion.json', {'version': args.version, 'id': data['id'], 'referenceMaster': entry['master'], 'sourceVersion': '1.4'})
            install_calculator(target)
            install_ipad_layout(target)
            shutil.copyfile(REPO / 'Vorlagen/Lernsituation_fuenf_Lernwege/assets/scorm.js', target / 'assets/scorm.js')
            install_print_layout(target)
            report['lessons'].append({'folder': name, 'id': data['id'], 'tasks': len(meta['tasks']), 'sourceProgressSha256': sha(source / 'progress-meta.js'), 'progressSha256': sha(target / 'progress-meta.js'), 'sourceCompetencies': payload(source / 'lesson-data.js')['competencies'], 'competencies': data['competencies'], 'images': {role: {'file':slot['src'], 'sha256':sha(target/slot['src'])} for role,slot in media['slots'].items()}})
            print('Prepared', name, len(meta['tasks']), 'unchanged tasks', flush=True)
        browser.close()
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(preview)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
            page = browser.new_page()
            for n in range(1,7):
                root = preview/f'LS{n:02d}'
                page.goto(f'http://127.0.0.1:{server.server_port}/{root.name}/druckansicht.html')
                page.wait_for_function('window.SOZ_READY===true')
                page.evaluate('async()=>{await window.SOZ_PRINT.ready();}')
                page.pdf(path=str(root/'pdf/Gesamtdokument_A4.pdf'), print_background=True, prefer_css_page_size=True, display_header_footer=False)
                manifest(root)
                archive(root, args.output/f'BRC_LG01_LS{n:02d}_v{args.version}_SCORM12.zip')
                print('Packed', root.name, flush=True)
            browser.close()
    finally: server.shutdown(); server.server_close()
    dump(args.output/'Inhaltspruefung.json', report)


if __name__ == '__main__': main()
