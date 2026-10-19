#!/usr/bin/env python3
"""Revise the current LS04 content without replacing its shell, IDs or settings.

Both existing identities (BRC-LG01-LS04 and LG01-LS04) are supported separately.
Only changed content receives new signatures through the approved progress core.
"""
from __future__ import annotations
import argparse
import base64
import copy
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

import fitz
from lxml import html as H
from playwright.sync_api import sync_playwright

from build_brc_series import PHASES, NAMES, quiz_html, workbook_html
from refresh_lg01_upload import compact_orientation, manifest

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO/'Fachbereiche/BRC/LG01/quellen/LS04_Rollenspiel_Materialien.json'
REVISION = 'Business-Angel-Rollenspiel-20261019'
OLD_TITLE = 'Bei Kapitalgebern pitchen'

REPLACEMENTS = [
    ('Rollen des Finanzierungsgremiums', 'Rollenkarten · BioCasa und Business Angels'),
    ('Pitchbriefing und Feedbackbogen', 'Pitchablauf und gemeinsamer Bewertungsbogen'),
    ('Finanzierungsgremiums', 'Business-Angel-Teams'),
    ('Finanzierungsgremium', 'Business-Angel-Team'),
    ('Gremiumsfeedback', 'Feedback des Business-Angel-Teams'),
    ('Gremiumsfrage', 'Frage des Business-Angel-Teams'),
    ('Gremiums', 'Business-Angel-Teams'),
    ('Gremium', 'Business-Angel-Team'),
    ('alle vier Teammitglieder', 'alle Mitglieder Ihres bestehenden Drei- bis Viererteams'),
    ('Alle vier Teammitglieder', 'Alle Mitglieder Ihres bestehenden Drei- bis Viererteams'),
    ('alle vier Gründerinnen und Gründer', 'alle drei bis vier Teammitglieder'),
    ('den vier Gründerrollen', 'den drei bis vier Sprechrollen Ihres Teams'),
    ('vier erkennbaren Gründerrollen', 'drei bis vier erkennbaren Sprechrollen'),
    ('vier erkennbaren Sprechrollen', 'drei bis vier erkennbaren Sprechrollen'),
    ('die vier Sprechrollen', 'die drei bis vier Sprechrollen'),
    ('Darlehen, Kontokorrent, Leasing und Tragfähigkeit', 'Darlehen, Leasing, Factoring und Beteiligungskapital'),
    ('aller drei Formen', 'der Finanzierungsbausteine'),
    ('drei Finanzierungsformen', 'Finanzierungsbausteine'),
    ('M1 bis M6', 'M1 bis M7'),
    ('aus M2 und M3', 'aus M2, M3 und M7'),
    ('Angaben aus M2 und M3', 'Angaben aus M2, M3 und M7'),
    ('„finanzierungsfähig“, „finanzierungsfähig unter Bedingungen“ oder „noch nicht finanzierungsfähig“',
     '„Beteiligung vorstellbar“, „Beteiligung nur unter Bedingungen“ oder „noch keine Beteiligung“'),
]

ADDITIONS = {
    'informieren': '<p><strong class="operator">Vergleichen</strong> Sie zunächst Darlehen, Leasing und Factoring mithilfe von M2, M3, M4 und M7. <strong class="operator">Berechnen</strong> Sie im Factoring-Beispiel Vorschuss, Gebühr, erste Auszahlung und späteren Rest. <strong class="operator">Begründen</strong> Sie, weshalb Factoring ohne bereits bestehende geeignete Forderungen kein Startkapital liefert. <strong class="operator">Leiten</strong> Sie anschließend aus dem verbleibenden Bedarf ab, weshalb BioCasa Business Angels anspricht und neben Geld auch Erfahrung und Kontakte sucht. Unterscheiden Sie Beteiligungskapital von Kredit und bloßer Netzwerkvermittlung.</p>',
    'planen': '<p><strong class="operator">Planen</strong> Sie das Rollenspiel mit Ihrem bereits bestehenden Team aus drei bis vier Personen und einem anderen Schülerteam derselben Größe. Zuerst präsentiert ein Team als BioCasa, das andere spielt die Business Angels; anschließend wechseln beide Teams die Rollen. <strong class="operator">Verteilen</strong> Sie für beide Rollen die Aufgaben aus M5 so, dass jedes Mitglied einen sichtbaren Beitrag leistet. Bei drei Personen verbinden Sie die vierte Zuständigkeit mit den übrigen Rollen. Bereiten Sie den achtminütigen Pitch, fünf Minuten Rückfragen und den gemeinsamen Bewertungsbogen M6 vor. Zwei Lehrkräfte sind anwesend und beurteilen die Pitches; sie beziehen die begründete Peerbeurteilung der Gegengruppe ein.</p>',
    'entscheiden': '<p><strong class="operator">Entscheiden</strong> Sie, welchen Betrag BioCasa nach Berücksichtigung von Eigenmitteln, Darlehen und Leasing als Beteiligungskapital bei den Business Angels anfragen soll. Kombination 3 in M4 zeigt einen möglichen Restbedarf von 90.000 Euro; eine andere begründete Lösung ist möglich. <strong class="operator">Formulieren</strong> Sie einen konkreten Beteiligungsantrag mit Betrag, Mittelverwendung, Meilensteinen sowie gewünschter Erfahrung und Netzwerkunterstützung. Kennzeichnen Sie Beteiligungsquote und Mitspracherechte als zu verhandelnde Bedingungen. Zählen Sie Kreditrahmen, Leasingersparnis, künftige Umsätze oder eine unverbindliche Zusage nicht als zusätzlichen sicheren Geldzufluss.</p>',
    'durchfuehren': '<p><strong class="operator">Spielen</strong> Sie die vereinbarte Pitchrunde: Ihr bestehendes Drei- bis Viererteam präsentiert BioCasa vor einem anderen Schülerteam aus drei bis vier Personen, das die Business Angels spielt. Alle Teammitglieder sprechen; die Business Angels stellen fachliche Rückfragen und dokumentieren Beobachtungen in M6. Zwei Lehrkräfte beobachten und beurteilen. <strong class="operator">Wechseln</strong> Sie nach dokumentiertem Feedback die Rollen, sodass beide Teams sowohl BioCasa präsentieren als auch Business Angels spielen. Bleiben Sie in der Rolle; es werden keine echten Beteiligungen oder Verträge abgeschlossen.</p>',
    'reflektieren': '<p><strong class="operator">Vergleichen</strong> Sie Ihre Erfahrungen als BioCasa-Pitchteam und als Business Angel. Welche Frage oder Beobachtung war fachlich hilfreich? Wodurch unterscheiden sich Kapital, Beratung und Kontakte? Welche begründete Rückmeldung der Gegengruppe und welche Rückmeldung der beiden Lehrkräfte führte zu einer konkreten Verbesserung? <strong class="operator">Belegen</strong> Sie Ihren persönlichen Beitrag in beiden Rollen und einen nächsten Lernschritt. Eine gespielte Investitionszusage allein belegt noch keine hohe Pitchqualität.</p>',
}

EVALUATION = '<p><strong class="operator">Beurteilen</strong> Sie als Schülerteam in den Business-Angel-Rollen den Pitch der Gegengruppe mit M6. Nutzen Sie je Kriterium die Skala 0–3 und nennen Sie konkrete Beobachtungen, eine Folie, eine Zahl oder eine Antwort als Beleg. Prüfen Sie Geschäftsidee und Markt, Finanzierungsplausibilität, Beteiligungsantrag und Netzwerkbedarf, Risiken, Darstellung und Teambeiträge sowie Antworten auf Rückfragen. <strong class="operator">Begründen</strong> Sie Ihr gespieltes Beteiligungsurteil und geben Sie zwei konkrete Verbesserungsvorschläge.</p><p>Die beiden anwesenden Lehrkräfte beurteilen den Pitch mit demselben Raster und beziehen die begründete Bewertung der Gegengruppe ein. Peerurteil, Lehrkräftebeurteilung und Selbstbild werden getrennt dokumentiert; es gibt keine automatische Mittelung. Eine gespielte Zusage oder Absage ist keine Note.</p><p><strong class="operator">Werten</strong> Sie als Pitchteam die Rückmeldungen aus und <strong class="operator">überarbeiten</strong> Sie höchstens drei zentrale Folien oder Aussagen. Dokumentieren Sie Rückmeldung, Änderung und fachliche Begründung. Geben Sie Pitchdeck, Finanzierungsanlage, Rollen-/Beitragsübersicht und den ausgefüllten Peerbogen ab. Beim Rollenwechsel erstellt jedes Schülerteam einen eigenen Peerbogen für die andere Präsentation.</p>'


def payload(path):
    return json.loads(path.read_text().split('=', 1)[1].strip().rstrip(';'))


def fragment(source):
    return H.fragment_fromstring(source, create_parent='div')


def serialize(root):
    return ''.join(H.tostring(e, encoding='unicode') for e in root)


def fill(element, source):
    for child in list(element): element.remove(child)
    element.text = None
    f = fragment(source)
    element.text = f.text
    for child in list(f): element.append(child)


def text_replace(value, title):
    value = value.replace(OLD_TITLE, title)
    for before, after in REPLACEMENTS: value = value.replace(before, after)
    return value.replace('drei bis drei bis vier', 'drei bis vier')


def substance(body):
    body = copy.deepcopy(body)
    for element in body.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," book-line ") or @data-time-ui]'):
        element.getparent().remove(element)
    return ' '.join(body.text_content().split())


def add_before_reference(body, source):
    before = next((c for c in body if 'book-line' in c.get('class', '').split() or c.get('data-time-ui')), None)
    for element in list(fragment(source)):
        if before is not None: body.insert(body.index(before), element)
        else: body.append(element)


def material_page(existing, title, item):
    root = fragment(existing)
    root.xpath('./section[contains(@class,"hero")]/h1')[0].text = title
    shell = root.xpath('.//div[contains(concat(" ",normalize-space(@class)," ")," source-document ")]')[0]
    template = H.parse(str(REPO/'Materialvorlagen/onenote.html'))
    replacement = template.xpath('//div[@class="source-document"]')[0]
    replacement.xpath('.//span[@class="file"]')[0].text = item['title']
    content = '<h1>'+__import__('html').escape(item['title'])+'</h1><p><b>Materialart:</b> '+__import__('html').escape(item['kind'])+'<br><b>Quelle:</b> '+__import__('html').escape(item['source'])+'<br><b>Kontext:</b> '+__import__('html').escape(item['context'])+'</p>'+item['content']
    fill(replacement.xpath('.//article[@class="paper"]')[0], content)
    shell.getparent().replace(shell, replacement)
    for check in root.xpath('.//details[contains(@class,"micro-question")]'):
        key = check.get('data-micro-id','')
        if key == 'mat-4-1':
            check.set('data-explanation','Die Business Angels werden von der Schülergegengruppe gespielt. Jede Person stellt eine eigene fachliche Frage zu Markt, Finanzierung, Risiken oder Beteiligung und begründet ihre Beobachtung.')
            check.xpath('./summary')[0].text = '2. Rollen der Business Angels'
            check.xpath('./div[@class="micro-body"]/p')[0].text = 'Die beiden Lehrkräfte spielen die Business Angels; die Schülergegengruppe hört nur zu.'
        if key == 'mat-5-1':
            check.set('data-explanation','Jede der drei bis vier Personen übernimmt einen eigenen Pitchanteil und eine fachliche Antwort sowie in der anderen Runde eine eigene Business-Angel-Frage und einen Beobachtungsbeleg. Die Gruppen bleiben bestehen.')
            check.xpath('./div[@class="micro-body"]/p')[0].text = 'Es genügt, wenn eine Person pitcht und später allein als Business Angel fragt; die übrigen Gruppenmitglieder müssen beide Rollen nicht übernehmen.'
        if key == 'mat-6-a':
            model = check.xpath('.//details/p')
            if model: model[0].text = 'Darlehen, Leasing und Factoring haben unterschiedliche Zwecke und Liquiditätsfolgen. Factoring setzt geeignete bestehende Forderungen voraus. Business Angels können Beteiligungskapital, Erfahrung und Kontakte einbringen; Betrag, Verwendung, Meilensteine und Rechte müssen begründet und verhandelt werden.'
    return serialize(root)


def questions():
    return [
        {'title':'Die Rollen im Pitch','question':'Wer spielt in dieser Lernsituation die Business Angels?', 'options':['Die beiden Lehrkräfte übernehmen alle Investorenrollen.','Eine echte Bank entscheidet über einen Kredit.','Das BioCasa-Team beurteilt ausschließlich sich selbst.','Eine Leasinggesellschaft nimmt die Präsentation ab.','Ein anderes Schülerteam aus drei bis vier Personen; danach wechseln die Schülerteams die Rollen.','Ein KI-System ersetzt das Gegenüber.'],'correct':4,'feedback':'Die Schülerinnen und Schüler spielen beide Seiten: BioCasa und Business Angels. Die zwei Lehrkräfte beobachten und beurteilen die Pitches und beziehen das begründete Peerurteil ein.'},
        {'title':'Factoring in der Startphase','question':'Warum kann BioCasa Factoring nicht einfach als Geldquelle vor dem ersten Verkauf einplanen?','options':['Factoring ersetzt automatisch jede Beteiligung.','Eine Umsatzprognose gilt bereits als verkaufbare Forderung.','Es werden geeignete bereits bestehende Forderungen verkauft; ohne diese Forderungen entsteht daraus kein Startkapital.','Factoring ist immer kostenlos.','Leasingraten werden durch Factoring automatisch erlassen.','Es handelt sich stets um einen langfristigen Bankkredit.'],'correct':2,'feedback':'Factoring setzt geeignete bestehende Forderungen voraus. Im Beispiel 50.000 Euro × 80 Prozent − 1.000 Euro Gebühr = 39.000 Euro erste Auszahlung; die mögliche spätere Zahlung setzt den bestehenden Forderungsfall voraus.'},
        {'title':'Beteiligungsbedarf','question':'Welchen Beteiligungsbedarf zeigt Kombination 3 nach Berücksichtigung der Leasingwirkung und des Darlehens?','options':['1.410.500 Euro, weil Eigenmittel nie berücksichtigt werden.','1.048.000 Euro zusätzlich zu Leasing und Darlehen.','558.000 Euro als sicherer Geldzufluss des Leasinggebers.','180.000 Euro, weil eine Kreditlinie schon Bargeld ist.','0 Euro, weil künftiger Umsatz eine sichere Finanzierung ersetzt.','90.000 Euro: 490.000 Euro verbleibender Finanzierungsbedarf minus 400.000 Euro Darlehen.'],'correct':5,'feedback':'1.410.500 − 558.000 − 362.500 = 490.000 Euro. Nach 400.000 Euro Darlehen verbleiben 90.000 Euro als mögliche Beteiligungsanfrage. Dies ist ein Vorschlag, keine Zusage der gespielten Business Angels.'},
        {'title':'Mehr als Geld','question':'Was kann die Zusammenarbeit mit Business Angels zusätzlich zu Beteiligungskapital beitragen?','options':['Erfahrung und Kontakte, etwa zu Vertriebspartnern oder weiteren Investoren; konkrete Leistungen und Rechte werden verhandelt.','Eine garantierte Bestellung aller Händler.','Eine automatische Kreditzusage jeder Bank.','Keine Mitspracherechte unter irgendeinem Vertrag.','Einen sicheren Gewinn ohne Risiko.','Einen Anspruch auf jede gewünschte Förderung.'],'correct':0,'feedback':'Business Angels können Kapital, Erfahrung, Beratung und Kontakte einbringen. Kontakte sind noch keine Aufträge oder Finanzierungszusagen. Beteiligung und vereinbarte Mitspracherechte müssen geklärt werden.'},
        {'title':'Beurteilung des Rollenspiels','question':'Wie werden die Pitches beurteilt?','options':['Die gespielte Investitionszusage ergibt automatisch die beste Note.','Die Gegengruppe bewertet mit Belegen; beide Lehrkräfte beurteilen den Pitch mit demselben Raster und beziehen diese Peerbeurteilung ein.','Nur das Pitchteam bewertet sich selbst.','Die Business-Angel-Rollen werden nicht von Schülern gespielt.','Die Bewertung ist allein eine Abstimmung über schöne Folien.','Peerwerte ersetzen ohne Prüfung jede Lehrkräftebeurteilung.'],'correct':1,'feedback':'Entscheidend sind beobachtbare Leistungen und begründete Rückmeldungen. Schülerteam und zwei Lehrkräfte nutzen das gemeinsame Raster. Es gibt keine automatische Mittelung und keine Gleichsetzung von Investitionsentscheidung und Note.'},
    ]


def revise(root, page, source):
    data = payload(root/'lesson-data.js')
    if data.get('roleplayRevision') == REVISION:
        print('Already current:', root, flush=True)
        return data, payload(root/'progress-meta.js')
    assert data['id'] in ('BRC-LG01-LS04', 'LG01-LS04')
    core_path = root/'assets/progress-core.js'
    core = core_path.read_text()
    condition = 'rule.from.length&&rule.from.every(t=>raw.t?.[t.id]===t.signature)'
    extended = '((rule.from?.length&&rule.from.every(t=>raw.t?.[t.id]===t.signature))||(rule.alternatives||[]).some(chain=>chain.length&&chain.every(t=>raw.t?.[t.id]===t.signature)))'
    if condition in core:
        assert core.count(condition)==1
        core_path.write_text(core.replace(condition,extended))
    old = copy.deepcopy(data); old_meta = payload(root/'progress-meta.js')
    title = source['title']; data['title'] = title
    data['pages'] = {name: text_replace(body, title) for name, body in data['pages'].items()}
    compact_orientation(data, source['competencies'])
    index = fragment(data['pages']['index.html'])
    relevance = index.xpath('.//section[contains(concat(" ",normalize-space(@class)," ")," relevance ")]')[0]
    for child in list(relevance):
        if child.tag not in ('h2', 'figure'): relevance.remove(child)
    for child in list(fragment(source['relevance'])): relevance.append(child)
    for model in index.xpath('.//details[contains(@class,"micro-question")]//details/p'):
        model.text = 'Darlehen, Leasing und Factoring wirken unterschiedlich auf Liquidität und Risiko. Business Angels können zusätzlich Beteiligungskapital, Erfahrung und Kontakte einbringen. Im Rollenspiel übernehmen Schülerteams beide Seiten.'
    data['pages']['index.html'] = serialize(index)
    situation = fragment(data['pages']['handlungssituation.html'])
    prose = situation.xpath('.//section[contains(@class,"situation-prose") or contains(@class,"situation-text")]')[0]
    picture = prose.xpath('.//figure[@data-media-key="situation"]')[0]
    fill(prose, source['situation']); prose.insert(0, picture)
    old_quiz = situation.xpath('.//*[@data-situation-quiz]')[0]
    old_quiz.getparent().replace(old_quiz, fragment(quiz_html(questions()))[0])
    data['pages']['handlungssituation.html'] = serialize(situation)
    unchanged = []
    for phase in PHASES:
        root_page = fragment(data['pages'][phase+'.html'])
        old_page = fragment(old['pages'][phase+'.html'])
        old_bodies = {a.get('data-task-id'):a.xpath('./div[@class="assignment-body"]')[0] for a in old_page.xpath('.//article[@data-task-id]')}
        for panel in root_page.xpath('.//*[@data-mode-panel]'):
            mode = panel.get('data-mode-panel')
            for note in panel.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," phase-meta ")]/p'):
                if note.text_content().strip().startswith('Arbeitsform:'):
                    label = ('Einzelarbeit und arbeitsteilige Analyse im bestehenden Drei- bis Viererteam' if phase == 'informieren' else
                             'Rollenspiel · zwei bestehende Schülerteams mit je drei bis vier Personen' if phase in ('durchfuehren','bewerten') else
                             'Einzelreflexion nach beiden Rollenspielrunden' if phase == 'reflektieren' else
                             'Planung im bestehenden Drei- bis Viererteam')
                    fill(note, '<b>Arbeitsform:</b> '+label)
            tasks = panel.xpath('.//article[@data-task-id]')
            first = tasks[0].xpath('./div[@class="assignment-body"]')[0]
            if phase == 'bewerten':
                timer = copy.deepcopy(first.xpath('./span[@data-time-ui]')[0])
                fill(first, EVALUATION); first.append(timer)
            else: add_before_reference(first, ADDITIONS[phase])
            if phase in ('planen','durchfuehren','bewerten'):
                add_before_reference(first, '<p><strong class="operator">Sichern</strong> Sie die Beteiligung jeder einzelnen Person: eigener Sprechanteil im Gruppenpitch und eine beantwortete fachliche Rückfrage; in der anderen Runde mindestens eine eigene Frage als Business Angel und ein konkreter Beobachtungsbeleg für die Peerbeurteilung. <strong class="operator">Dokumentieren</strong> Sie dies für jedes Mitglied in M6. Die Gruppen bleiben bestehen; jede Person übernimmt beide Rollen aktiv.</p>')
            # All existing task slots and original timing remain in place.
            for task in tasks:
                body = task.xpath('./div[@class="assignment-body"]')[0]
                key = task.get('data-task-id')
                if substance(body) == substance(old_bodies[key]): unchanged.append(key)
                books = body.xpath('.//span[contains(@class,"book-reference")]')
                if not books:
                    line = fragment('<p class="book-line"><img class="book-ref-icon" src="assets/lehrbuch-icon.png" alt="Lehrbuch"><span class="book-reference"></span></p>')[0]
                    before = body.xpath('./span[@data-time-ui]')[0]
                    body.insert(body.index(before), line); books = line.xpath('./span')
                wording = body.text_content().lower()
                references = ['Finanzierung, S. 350']
                if 'darlehen' in wording or 'tilgung' in wording: references.append('Darlehen, S. 391')
                if 'leasing' in wording: references.append('Leasing, S. 398–399')
                for book in books: book.text = ' · '.join(references)
                if phase in ('durchfuehren', 'bewerten'):
                    social = task.xpath('./span[contains(@class,"assignment-social")]')
                    if social:
                        social[0].set('title', 'Rollenspiel · zwei Schülerteams mit je 3–4 Personen')
                        label = social[0].xpath('./small')
                        if label: label[0].text = 'Rollenspiel · Schülerteams'
            data['pages'][phase+'.html'] = serialize(root_page)
    for name, item in source['materials'].items():
        data['pageTitles'][name] = re.match(r'm(\d+)', name)[1].join(['M', ' · '])+item['title']
        data['pages'][name] = material_page(data['pages'][name], data['pageTitles'][name], item)
    # Synchronise material link labels throughout all chapters.
    for name, content in list(data['pages'].items()):
        tree = fragment(content)
        for link in tree.xpath('.//a[@href]'):
            target = link.get('href').split('?')[0]
            if target in source['materials']:
                labels = link.xpath('./span')
                if labels: labels[0].text = ' · '+source['materials'][target]['title']
                else: link.text = data['pageTitles'][target]
        data['pages'][name] = serialize(tree)
    teacher = fragment(data['pages']['erwartungshorizont.html'])
    sections = teacher.xpath('./section')
    for child in sections[1:]: teacher.remove(child)
    guidance = H.Element('section', {'class':'card'}); fill(guidance, source['teacherGuidance']); teacher.append(guidance)
    data['pages']['erwartungshorizont.html'] = serialize(teacher)
    data['roleplayRevision'] = REVISION
    # New substantive instructions must be read again; the storage/SCO identity
    # and existing competency evidence remain the same. Book-reference-only
    # changes migrate exactly matching previous task completions.
    data.pop('orientationPresentation', None)
    page.goto('about:blank'); page.add_script_tag(path=str(root/'assets/progress-core.js'))
    result = page.evaluate('d=>{const meta=SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser());return {data:d,meta};}', data)
    data, meta = result['data'], result['meta']
    assert set(meta['tasks']) == set(old_meta['tasks']), 'Existing task IDs must stay intact'
    migration = data.get('progressMigration') or {}
    rules = migration.setdefault('tasks', {})
    for key in unchanged:
        if meta['tasks'][key]['signature'] != old_meta['tasks'][key]['signature']:
            prior = copy.deepcopy(rules.get(key, {}))
            rules[key] = {'signature':meta['tasks'][key]['signature'], 'from':[{'id':key,'signature':old_meta['tasks'][key]['signature']}]}
            if prior.get('signature') == old_meta['tasks'][key]['signature']:
                alternatives = [prior['from']] if prior.get('from') else []
                alternatives.extend(prior.get('alternatives', []))
                if alternatives: rules[key]['alternatives'] = alternatives
    data['progressMigration'] = migration; meta['migration'] = migration
    for filename, value, variable in [('lesson-data.js',data,'SOZPAED'),('progress-meta.js',meta,'SOZ_PROGRESS_META')]:
        (root/filename).write_text('window.'+variable+'='+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';\n')
    for name, content in data['pages'].items():
        file = root/name; raw = file.read_text()
        start = raw.index('<div class="lesson-content">')+len('<div class="lesson-content">')
        end = raw.index('</div></main>', start)
        file.write_text(raw[:start]+content+raw[end:])
    for file in root.glob('*.html'):
        file.write_text(file.read_text().replace(OLD_TITLE, title))
    path = root/'imsmanifest.xml'; tree = ET.parse(path)
    for element in tree.getroot().iter():
        if element.tag.split('}')[-1]=='title' and element.text: element.text=element.text.replace(OLD_TITLE,title)
    tree.write(path,encoding='utf-8',xml_declaration=True)
    return data, meta


def workbooks(root, page, data):
    budgets = []
    for phase in PHASES:
        tree = fragment(data['pages'][phase+'.html'])
        panel = tree.xpath('.//*[@data-mode-panel="1"]')[0]
        budgets.append(sum(float(t.get('data-minutes')) for t in panel.xpath('.//span[@data-time-ui]')))
    lesson = {'number':4,'title':data['title'],'budgets':budgets}
    for phase in PHASES:
        tree = fragment(data['pages'][phase+'.html'])
        for mode in range(1,6):
            panel = tree.xpath(f'.//*[@data-mode-panel="{mode}"]')[0]
            instruction = {'tasks':[],'times':[],'workforms':[]}
            for task in panel.xpath('.//article[@data-task-id]'):
                body = copy.deepcopy(task.xpath('./div[@class="assignment-body"]')[0])
                timer = body.xpath('./span[@data-time-ui]')[0]
                instruction['times'].append(float(timer.get('data-minutes'))); body.remove(timer)
                for image in body.xpath('.//img[@src]'):
                    local = root/image.get('src')
                    if local.is_file():
                        mime = 'image/svg+xml' if local.suffix=='.svg' else 'image/png'
                        image.set('src','data:'+mime+';base64,'+base64.b64encode(local.read_bytes()).decode())
                instruction['tasks'].append(serialize(body))
                social = task.xpath('./span[contains(@class,"assignment-social")]/small')
                instruction['workforms'].append({'label':social[0].text_content() if social else 'Teamarbeit'})
            markup = workbook_html(lesson,phase,mode,instruction)
            # Long authored tasks can span sheets; no worksheet may be clipped.
            markup = markup.replace('.worksheet-task{', '.worksheet-task{overflow-wrap:anywhere;').replace('break-inside:avoid}', 'break-inside:auto}')
            markup = markup.replace('</style>', '.book-line{font-size:9pt;background:#f5f8ef;padding:5px}.book-ref-icon{width:24px;height:auto;vertical-align:middle;margin-right:6px}</style>')
            page.set_content(markup)
            page.evaluate('async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));}')
            page.pdf(path=str(root/f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf'),print_background=True,prefer_css_page_size=True)
            raw = (root/f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf').read_bytes()
            (root/f'goodnotes-phase-{phase}-W{mode}.js').write_text('window.GOODNOTES_PHASES=Object.assign(window.GOODNOTES_PHASES||{},'+json.dumps({phase+':'+str(mode):base64.b64encode(raw).decode()})+');\n')
    for mode in range(1,6):
        target = root/data['workbooks'][str(mode)]
        combined = fitz.open()
        for phase in PHASES:
            with fitz.open(root/f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf') as part: combined.insert_pdf(part)
        combined.save(target,garbage=4,deflate=True); combined.close()
        script = root/f'goodnotes-share-W{mode}.js'
        if script.exists(): script.write_text('window.GOODNOTES_WORKBOOKS=Object.assign(window.GOODNOTES_WORKBOOKS||{},'+json.dumps({str(mode):base64.b64encode(target.read_bytes()).decode()})+');\n')
    if (root/'pdf/GoodNotes_LG01_LS04.pdf').exists(): shutil.copyfile(root/data['workbooks']['1'],root/'pdf/GoodNotes_LG01_LS04.pdf')
    manifest(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packages',type=Path,nargs='+')
    parser.add_argument('--workbooks',action='store_true',help='Regenerate affected phase PDFs and matching GoodNotes payloads')
    args = parser.parse_args(); source = json.loads(SOURCE.read_text())
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=browser.new_page()
        for root in args.packages:
            data, meta = revise(root,page,source)
            if args.workbooks: workbooks(root,page,data)
            print('Revised:',root,data['id'],len(meta['tasks']),'stable task IDs',flush=True)
        browser.close()


if __name__=='__main__':main()
