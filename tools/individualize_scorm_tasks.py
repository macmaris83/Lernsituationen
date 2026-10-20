#!/usr/bin/env python3
"""Separate independent existing work orders and number each learning path continuously.

No instruction is rewritten. Supporting criteria, source references and optional
AI guidance stay attached to their task. A completed legacy bundle completes its
new parts through explicit signature-checked migration, not through learner data.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import shutil

from transfer_scorm_design import archive, content_of, manifest, payload, read_archive, sha

PHASES = ['informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren']

# Reviewed boundaries between independently assessable products/analyses. Criteria,
# reasoning for the same decision, checkpoints and corrections are not split blindly.
BOUNDARIES = {
    'LS01:0:4:1': ['Entscheiden Sie, welche Materialien'],
    'LS01:0:4:3': ['Untersuchen Sie bei vier', 'Begründen Sie mithilfe', 'Leiten Sie eine BioCasa-Prozesskette'],
    'LS01:1:4:2': ['Erarbeiten Sie je zwei', 'Stellen Sie deren Harmonien', 'Legen Sie fest, wie Ihr Team'],
    'LS01:5:4:1': ['Vergleichen Sie anschließend im Team'],
    'LS02:0:4:1': ['Entwickeln Sie eine eigene Auswertungsstrategie'],
    'LS02:0:4:3': ['Beurteilen Sie außerdem', 'Erklären Sie mithilfe von M5'],
    'LS02:1:4:3': ['Entwickeln Sie drei Auswahlkriterien'],
    'LS02:5:4:1': ['Bewerten Sie anschließend Ihre Arbeitsorganisation'],
    'LS03:0:4:1': ['Entscheiden Sie selbst über Zugriffsreihenfolge'],
    'LS03:0:4:2': ['Werten Sie die Zielgruppen-', 'Vergleichen Sie die Wettbewerbsangebote', 'Prüfen Sie die Marketingoptionen'],
    'LS03:0:4:3': ['Berechnen Sie Jahresabsatz', 'Bearbeiten Sie auch die sechs'],
    'LS03:1:4:2': ['Entwickeln Sie gemeinsame Kriterien', 'Legen Sie Kennzeichnungen'],
    'LS03:2:4:1': ['Entwickeln Sie einen abgestimmten Marketingmix', 'Beurteilen Sie die vorgesehene', 'Legen Sie mindestens drei'],
    'LS03:3:4:1': ['Schreiben Sie die Zusammenfassung'],
    'LS03:5:4:1': ['Zeigen Sie, welche Arbeitsweise'],
    'LS04:0:4:1': ['Stellen Sie Kapitalbedarf', 'Wählen Sie Bearbeitungsreihenfolge'],
    'LS04:0:4:2': ['Berechnen Sie beim Ratendarlehen', 'Bestimmen Sie die Jahreszinsen', 'Ermitteln Sie den nominalen'],
    'LS04:0:4:3': ['Vergleichen Sie die drei Kombinationen', 'Organisieren Sie zu jedem Fachbereich'],
    'LS04:1:4:2': ['Planen Sie die Dramaturgie', 'Wählen Sie drei zentrale Zahlen', 'Bereiten Sie mindestens sechs Rückfragen'],
    'LS04:2:4:1': ['Entscheiden Sie über Kontokorrentbedarf', 'Nehmen Sie zur Stressfestigkeit Stellung'],
    'LS04:5:4:1': ['Wie reagierten Sie auf Unsicherheit'],
    'LS05:0:4:1': ['Entwickeln Sie aus M1', 'Bestimmen Sie, welche Fragen'],
    'LS05:0:4:2': ['Ordnen Sie dabei Firma', 'Prüfen Sie anhand von M3/M4', 'Korrigieren Sie den ungeprüften'],
    'LS05:1:4:2': ['Planen Sie die Sensitivitätsprüfung', 'Entwickeln Sie mindestens zwei Alternativen'],
    'LS05:2:4:1': ['Entscheiden Sie sich', 'Gestalten Sie Beteiligung', 'Legen Sie den nächsten'],
    'LS05:5:4:1': ['Werten Sie außerdem aus'],
    'LS06:0:4:1': ['Klären Sie, welche Dokumente', 'Wählen Sie selbst, ob Sie'],
    'LS06:0:4:2': ['Zustandekommen, endgültige Inhalte', 'Vergleich aller vier Zahlungsoptionen',
                   'Art, Umfang und Netto-Warenwert', 'Prüfung von Untersuchung/Rüge',
                   'Ursachen und verfügbare Lösungsmöglichkeiten', 'Vergleich aller drei Beschäftigungsoptionen',
                   'Prüfung des Vertragsentwurfs'],
    'LS06:1:4:2': ['Entwickeln Sie eine eigene Aktenstruktur'],
    'LS06:2:4:1': ['Wählen Sie eine Zahlungsmöglichkeit', 'Entwickeln Sie eine konkrete Nacherfüllung',
                   'Entscheiden Sie über Beschäftigungsform', 'Legen Sie mindestens drei'],
    'LS06:3:4:1': ['Verfassen Sie eine versandfertige Kundenmail'],
    'LS06:5:4:1': ['Werten Sie aus, an welcher Stelle'],
}
NOTES = re.compile(r'^(?:Ihr fachlicher Pflichtkern|Der fachliche Pflichtkern|Ihr Pflichtkern|Pflichtkern:|'
                   r'Pflichtvergleich:|Checkpoint [AB]:|Ab hier |Ab dieser Phase |Mindest|Das Produkt muss|'
                   r'Sie muss |Das Team entscheidet|Sie entscheiden über|Alle entscheidungsrelevanten|'
                   r'Kundenkommunikation, interne)')


def normalized(value):
    return re.sub(r'\s+', ' ', value).strip()


def signature(value):
    result = 2166136261
    encoded = normalized(value).encode('utf-16-le')
    for index in range(0, len(encoded), 2):
        result = ((result ^ int.from_bytes(encoded[index:index + 2], 'little')) * 16777619) & 0xffffffff
    return f'{result:08x}'


def slice_element(node, start, end):
    """Copy a DOM text range while preserving strong/link markup and exact wording."""
    from lxml import html
    position = 0

    def take(text):
        nonlocal position
        text = text or ''
        left, right = max(0, start - position), min(len(text), end - position)
        position += len(text)
        return text[left:right] if right > left else ''

    def append_text(parent, text):
        if len(parent):
            parent[-1].tail = (parent[-1].tail or '') + text
        else:
            parent.text = (parent.text or '') + text

    def visit(source):
        target = html.Element(source.tag, dict(source.attrib))
        append_text(target, take(source.text))
        for child in source:
            copied = visit(child)
            if copied.text_content() or len(copied) or child.tag in {'img', 'br'} and start <= position < end:
                target.append(copied)
            append_text(target, take(child.tail))
        return target

    return visit(node)


def split_body(body, key, phase, mode):
    """Return partitioned instruction nodes; all source text occurs once and in order."""
    from lxml import html
    children = [copy.deepcopy(c) for c in body if 'book-line' not in c.get('class', '').split()]
    groups = []
    boundaries = BOUNDARIES.get(key)
    if boundaries:
        # Locate the paragraph containing the reviewed boundaries. Generic lead-ins
        # remain attached to the first part and never become empty done-cards.
        positions = []
        for index, child in enumerate(children):
            text = child.text_content()
            if all(boundary in text for boundary in boundaries):
                offsets = [text.index(boundary) for boundary in boundaries]
                assert offsets == sorted(offsets) and len(set(offsets)) == len(offsets), key
                positions = [0, *offsets, len(text)]
                for left, right in zip(positions, positions[1:]):
                    groups.append([slice_element(child, left, right)])
                groups[0] = children[:index] + groups[0]
                groups[-1].extend(children[index + 1:])
                break
        if not positions:
            raise ValueError(f'Geprüfte Aufgabengrenze fehlt: {key}')
    elif mode == 5 and phase in {'informieren', 'planen', 'entscheiden', 'reflektieren'} or key == 'LS03:0:2:1':
        lists = [(i, c) for i, c in enumerate(children) if c.tag in {'ul', 'ol'}]
        if len(lists) == 1:
            index, listing = lists[0]
            for item in listing:
                note = bool(NOTES.match(normalized(item.text_content())))
                paragraph = html.Element('p')
                paragraph.text = item.text
                for descendant in item:
                    paragraph.append(copy.deepcopy(descendant))
                if note and groups:
                    groups[-1].append(paragraph)
                else:
                    groups.append([paragraph])
            if groups:
                groups[0] = children[:index] + groups[0]
                groups[-1].extend(children[index + 1:])
    if not groups:
        return [children]
    before = normalized(' '.join(c.text_content() for c in children))
    after = normalized(' '.join(c.text_content() for group in groups for c in group))
    # Block boundaries can supply visual whitespace even when the source HTML
    # has no newline between list items. All non-whitespace characters stay exact.
    assert re.sub(r'\s+', '', before) == re.sub(r'\s+', '', after), key
    return groups


def update_data(data, meta, lesson):
    from lxml import html
    counts = {mode: 0 for mode in range(1, 6)}
    tasks, mapping, split = {}, {}, []
    for phase in PHASES:
        page = phase + '.html'
        doc = html.fragment_fromstring(data['pages'][page], create_parent='div')
        for panel in doc.xpath('.//*[@data-mode-panel]'):
            mode = int(panel.get('data-mode-panel'))
            for card in list(panel.xpath('.//article[contains(concat(" ",normalize-space(@class)," ")," assignment-frame ")]')):
                old_id = card.get('data-task-id')
                old = meta['tasks'][old_id]
                body = card.xpath('./div[contains(concat(" ",normalize-space(@class)," ")," assignment-body ")]')[0]
                groups = split_body(body, lesson + ':' + old_id, phase, mode)
                shared = []
                if len(groups) > 1 and phase == 'reflektieren' and mode == 5 and body[0].tag == 'p':
                    shared = [body[0]]
                if lesson == 'LS06' and old_id == '0:4:2':
                    shared = [body[0], slice_element(body[1], 0, body[1].text_content().index(':') + 1)]
                refs = body.xpath('./*[contains(concat(" ",normalize-space(@class)," ")," book-line ")]')
                if len(groups) > 1:
                    split.append({'sourceTask': old_id, 'parts': len(groups)})
                for part, nodes in enumerate(groups, 1):
                    child = copy.deepcopy(card)
                    target = child.xpath('./div[contains(@class,"assignment-body")]')[0]
                    if len(groups) > 1:
                        target.clear()
                        target.set('class', 'assignment-body')
                        if part > 1:
                            for context in shared:
                                node = copy.deepcopy(context)
                                node.set('data-split-context', '')
                                target.append(node)
                        for node in nodes:
                            target.append(copy.deepcopy(node))
                        for ref in refs:
                            target.append(copy.deepcopy(ref))
                    task = old_id if part == 1 else old_id + '.' + str(part)
                    child.set('data-task-id', task)
                    child.set('data-task-stable-id', task)
                    child.set('data-source-task', old_id)
                    counts[mode] += 1
                    number = counts[mode]
                    child.set('data-task-number', str(number))
                    for label in child.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," assignment-number ")]'):
                        label.text = str(number)
                        label.set('aria-label', f'Aufgabe {number}')
                    for checkbox in child.xpath('.//input[@data-task-complete]'):
                        checkbox.set('data-task-id', task)
                        checkbox.set('aria-label', f'Aufgabe {number} als erledigt markieren')
                        checkbox.attrib.pop('checked', None)
                    sig = signature(target.text_content()) if len(groups) > 1 else old['signature']
                    child.set('data-task-signature', sig)
                    tasks[task] = {'phase': phase, 'mode': mode, 'signature': sig}
                    if len(groups) > 1:
                        mapping[task] = {'signature': sig, 'from': [{'id': old_id, 'signature': old['signature']}]}
                    card.addprevious(child)
                card.getparent().remove(card)
        data['pages'][page] = ''.join(html.tostring(c, encoding='unicode') for c in doc)
    migration = copy.deepcopy(data.get('progressMigration') or meta.get('migration') or {})
    migration['tasks'] = {**migration.get('tasks', {}), **mapping}
    data['progressMigration'] = migration
    meta['tasks'] = tasks
    meta['migration'] = migration
    return counts, split


CORE_NUMBERING = r'''
/* Display numbering is independent of persistent task identities. */
function taskNumbers(data,parser,overrides={}){const result={},totals={};for(const phase of phases){const source=overrides[phase+'.html']||data.pages[phase+'.html'];const doc=parser.parseFromString(source,'text/html');for(const panel of doc.querySelectorAll('[data-mode-panel]')){const mode=Number(panel.dataset.modePanel);for(const card of panel.querySelectorAll('.assignment-frame')){totals[mode]=(totals[mode]||0)+1;result[card.dataset.taskId]=totals[mode];}}}return result;}
function numberData(data,parser){const numbers=taskNumbers(data,parser);for(const phase of phases){const doc=parser.parseFromString('<div>'+data.pages[phase+'.html']+'</div>','text/html');for(const card of doc.querySelectorAll('.assignment-frame')){const n=numbers[card.dataset.taskId];card.dataset.taskNumber=n;const number=card.querySelector('.assignment-number');if(number){number.textContent=n;number.setAttribute('aria-label','Aufgabe '+n);}card.querySelector('[data-task-complete]')?.setAttribute('aria-label','Aufgabe '+n+' als erledigt markieren');}data.pages[phase+'.html']=doc.body.firstElementChild.innerHTML;}}
'''

RUNTIME_NUMBERING = r'''
function numberVisibleTasks(){const K=window.SOZ_PROGRESS_CORE;if(!K?.taskNumbers)return;const numbers=K.taskNumbers(D,new DOMParser(),settings.overrides);for(const card of document.querySelectorAll('.assignment-frame')){const n=numbers[card.dataset.taskId];if(!n)continue;card.dataset.taskNumber=n;const number=card.querySelector('.assignment-number');if(number){number.textContent=n;number.setAttribute('aria-label','Aufgabe '+n);}card.querySelector('[data-task-complete]')?.setAttribute('aria-label','Aufgabe '+n+' als erledigt markieren');}}
'''

COMPACT_MATERIALS = r'''
/* Only compact material access follows the page; long menus start collapsed. */
(()=>{const menus=[...document.querySelectorAll('.lesson-content>details.material-access,.lesson-content>details.phase-materials')];if(!menus.length)return;const counts=new WeakMap();function measure(){for(const menu of menus){const was=menu.open;menu.open=true;const rows=new Set([...menu.querySelectorAll('a.material-link')].map(a=>Math.round(a.getBoundingClientRect().top)));const long=rows.size>2,previous=counts.get(menu);menu.classList.toggle('material-access-long',long);menu.open=long&&(previous===undefined||previous===false)?false:was;counts.set(menu,long);}}measure();let timer;window.addEventListener('resize',()=>{clearTimeout(timer);timer=setTimeout(measure,100);});document.querySelectorAll('.task-original-preview,.task-summary').forEach(el=>el.addEventListener('click',()=>{for(const menu of menus)if(menu.classList.contains('material-access-long'))menu.open=false;},true));})();
'''


def patch_assets(root):
    core_path = root / 'assets/progress-core.js'
    core = core_path.read_text()
    old = "const id=phases.indexOf(phase)+':'+mode+':'+number;"
    new = "const scope=phases.indexOf(phase)+':'+mode+':',stable=a.dataset.taskStableId;const id=stable&&stable.startsWith(scope)?stable:scope+number;"
    assert core.count(old) == 1
    core = core.replace(old, new)
    core = core.replace('function metadataFrom(data,parser){', CORE_NUMBERING + '\nfunction metadataFrom(data,parser){')
    core = core.replace(" const doc=parser.parseFromString('<div>'+data.pages['handlungssituation.html']", " numberData(data,parser);const doc=parser.parseFromString('<div>'+data.pages['handlungssituation.html']")
    core = core.replace('setTask,decorate,metadataFrom};', 'setTask,decorate,metadataFrom,taskNumbers,numberData};')
    core = core.replace("function blockedBy(p,meta,page,mode=p.m){", "function blockedBy(p,meta,page,mode=p.m){\n if(window.SOZ_TEACHER_VIEW?.active)return null;")
    core_path.write_text(core)
    runtime_path = root / 'assets/runtime.js'
    runtime = runtime_path.read_text().replace('function start(){', RUNTIME_NUMBERING + '\nfunction start(){')
    runtime = runtime.replace('decorateDocumentPDF();configureWorkbookImport();', 'decorateDocumentPDF();configureWorkbookImport();numberVisibleTasks();')
    runtime = runtime.replace('key=`sozpaed:', 'baseKey=`sozpaed:')
    runtime = runtime.replace(",settingKey=key+':settings:'", ",key=(window.SOZ_TEACHER_VIEW?.active?'teacher:':'')+baseKey,settingKey=baseKey+':settings:'")
    runtime = runtime.replace("let active=null;\nfunction valid(task)", "const displayNumbers=window.SOZ_PROGRESS_CORE.taskNumbers(D,new DOMParser(),window.SOZ_API?.getSettings().overrides||{});let active=null;\nfunction valid(task)")
    runtime = runtime.replace("number:String(task).split(':').pop()", "number:String(displayNumbers[task]||String(task).split(':').pop())")
    runtime = runtime.replace("'task-focus-return:'+D.id", "(window.SOZ_TEACHER_VIEW?.active?'teacher:':'')+'task-focus-return:'+D.id")
    runtime = runtime.replace("const key='task-focus-clock:'", "const key=(window.SOZ_TEACHER_VIEW?.active?'teacher:':'')+'task-focus-clock:'")
    runtime += COMPACT_MATERIALS
    runtime_path.write_text(runtime)
    progress_path = root / 'assets/progress.js'
    progress = progress_path.read_text().replace("let bridge=null;", "const teacherView=window.SOZ_TEACHER_VIEW;let bridge=null;")
    progress = progress.replace('if(window.parent!==window&&window.parent.SOZ_SCORM)', 'if(!teacherView?.active&&window.parent!==window&&window.parent.SOZ_SCORM)')
    progress = progress.replace("const localKey='soz-tasks:'", "const storage=teacherView?.active?sessionStorage:localStorage;const localKey=(teacherView?.active?'teacher:':'')+'soz-tasks:'")
    progress = progress.replace('localStorage.getItem(localKey)', 'storage.getItem(localKey)').replace('localStorage.setItem(localKey', 'storage.setItem(localKey')
    progress = progress.replace("function stateMessage(){", "function stateMessage(){if(teacherView?.active)return 'Lehrkräfteansicht: eigener Teststand. Der Lernstand der Lernenden wird nicht verändert.';")
    progress = progress.replace("get learner(){return bridge?.learner||'';}", "get learner(){return teacherView?.learner||bridge?.learner||'';}")
    progress = progress.replace('get initialMode(){return C.allowStudentMode?', 'get initialMode(){if(teacherView?.active)return teacherView.mode;return C.allowStudentMode?')
    progress_path.write_text(progress)
    lg_path = root / 'assets/lg01.js'
    lg_path.write_text(lg_path.read_text().replace("base='biocasa:'", "base=(window.SOZ_TEACHER_VIEW?.active?'teacher:':'')+'biocasa:'"))
    scorm_path = root / 'assets/scorm.js'
    scorm = scorm_path.read_text()
    old = "readOnly=['browse','review'].includes(get('cmi.core.lesson_mode'));"
    new = "const lessonMode=get('cmi.core.lesson_mode');readOnly=lessonMode==='review';if(lessonMode==='browse')kind='preview';"
    assert scorm.count(old) == 1
    scorm = scorm.replace(old, new)
    scorm = scorm.replace("if(readOnly)say('Ansichtsmodus:", "if(lessonMode==='browse'){try{const saved=localStorage.getItem(previewKey+':browse');if(saved)progress=K.sanitize(JSON.parse(saved),meta,C.mode);}catch{}say('Lernvorschau: Du kannst Aufgaben abhaken und den Lernweg ausprobieren. Der Fortschritt dieser Vorschau wird nur auf diesem Gerät gespeichert.');}if(readOnly)say('Ansichtsmodus:")
    scorm = scorm.replace("localStorage.setItem(previewKey,JSON.stringify(progress));", "localStorage.setItem(previewKey+(api?':browse':''),JSON.stringify(progress));")
    scorm = scorm.replace("if(kind==='moodle'){if(!readOnly)commit();try{api.LMSFinish('');}catch{}}finished=true;", "if(kind==='moodle'&&!readOnly)commit();if(api&&kind!=='error'){try{api.LMSFinish('');}catch{}}finished=true;")
    scorm_path.write_text(scorm)
    for name in ['teacher-view.js', 'teacher-view.css']:
        shutil.copyfile(Path(__file__).parent / 'scorm_ui' / name, root / 'assets' / name)
    for path in root.glob('*.html'):
        source = path.read_text()
        if path.name != 'scorm.html' and 'src="lesson-data.js"' in source:
            source = source.replace('<script src="lesson-data.js"></script>', '<script src="lesson-data.js"></script><script src="assets/teacher-view.js"></script>')
            source = source.replace('</head>', '<link rel="stylesheet" href="assets/teacher-view.css"></head>')
            source = re.sub(r'(<a\b[^>]*href="lehrkraft.html"[^>]*>).*?(</a>)', r'\1Editor\2', source, flags=re.S)
        path.write_text(source)
    manifest(root, (root / 'imsmanifest.xml').read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--version', default='1.2')
    args = parser.parse_args()
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)', args.version):
        parser.error('Version muss zwei Zahlen enthalten')
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        parser.error('Ausgabe außerhalb des Repositorys wählen')
    if args.output.exists():
        parser.error('Ausgabe muss neu sein')
    entries = read_archive(args.source.read_bytes())
    args.output.mkdir(parents=True)
    reports, combined = [], {}
    for name, raw in entries.items():
        if not name.endswith('.zip'):
            continue
        ls = re.search(r'LS\d{2}', name)[0]
        files = read_archive(raw)
        root = args.output / 'preview' / ls
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        data, meta = payload(files['lesson-data.js']), payload(files['progress-meta.js'])
        counts, split = update_data(data, meta, ls)
        (root / 'lesson-data.js').write_text('window.SOZPAED=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
        (root / 'progress-meta.js').write_text('window.SOZ_PROGRESS_META=' + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ';\n')
        for page in PHASES:
            target = root / (page + '.html')
            source = target.read_text()
            start = source.index('<div class="lesson-content">') + len('<div class="lesson-content">')
            end = source.index('</div></main>', start)
            target.write_text(source[:start] + data['pages'][page + '.html'] + source[end:])
        patch_assets(root)
        # Print the current numbered data, while preserving the archival original PDFs.
        for page in root.glob('*.html'):
            source = page.read_text()
            page.write_text(re.sub(r'href="pdf/[^\"]*Gesamtdruck[^\"]*\.pdf"', 'href="druckansicht.html"', source))
        from numbered_phase_workbooks import prepare
        prepare(root)
        filename = re.sub(r'_v\d+\.\d+_', '_v' + args.version + '_', name)
        output = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}
        archive(args.output / filename, output)
        combined[filename] = (args.output / filename).read_bytes()
        reports.append({'lesson': ls, 'sourceSha256': sha(raw), 'numbersByMode': counts, 'splitBundles': split,
                        'oldTasks': len(payload(files['progress-meta.js'])['tasks']), 'tasks': len(meta['tasks'])})
        print(ls, counts, 'getrennte Bündel', len(split), flush=True)
    archive(args.output / ('BioCasa_LG01_Moodle_Lernpakete_v' + args.version + '.zip'), combined)
    (args.output / 'Aufgaben_Pruefung.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
