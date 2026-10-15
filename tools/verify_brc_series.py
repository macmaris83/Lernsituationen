#!/usr/bin/env python3
"""Exercise every new BRC lesson and check the deliverable SCORM archives.

The Markdown phase budgets are read independently of the generator.  These are
Chromium/API simulations; native Moodle, AIS and GoodNotes are not simulated as
if their embedding/share behavior had been verified on a real iPad.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
import math
from pathlib import Path
import re
import subprocess
import threading
import xml.etree.ElementTree as ET
import zipfile

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
PHASES = ['informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren']
WIDTHS = [(1024, 768), (768, 1024), (600, 900), (390, 844)]


def payload(path_or_bytes):
    raw = path_or_bytes.read_bytes() if isinstance(path_or_bytes, Path) else path_or_bytes
    return json.loads(raw.decode('utf-8').split('=', 1)[1].strip().rstrip(';'))


def clean(text):
    return re.sub(r'\s+', '', text)


def read_plan_budgets(source):
    text = source.read_text(encoding='utf-8')
    blocks = re.split(r'^# LS (\d+)\s*[–-].*$', text, flags=re.M)
    result = {}
    for index in range(1, len(blocks), 2):
        number, block = int(blocks[index]), blocks[index + 1]
        w1 = block.split('### Lernweg W1', 1)[1].split('### Lernweg W', 1)[0]
        hours = re.findall(r'\*\*Arbeitszeit:\*\*\s*([\d,\.]+)\s+Unterrichtsstunde', w1)
        assert len(hours) == 6, (number, hours)
        result[f'LS{number:02}'] = [float(value.replace(',', '.')) * 45 for value in hours]
        total = int(re.search(r'\*\*Zeitrichtwert:\*\*\s*(\d+)', block)[1]) * 45
        assert sum(result[f'LS{number:02}']) == total, number
    assert len(result) == 6
    assert sum(sum(budgets) for budgets in result.values()) == 3600
    return result


def lesson_root(series, lesson):
    return series.parent / lesson['folder']


def zip_path(series, lesson):
    catalog = json.loads((REPO / 'master-katalog.json').read_text())
    master = lesson_root(series, lesson).resolve().relative_to(REPO).as_posix()
    matches = [entry for entry in catalog['packages'] if entry['master'] == master]
    assert len(matches) == 1, ('Master nicht eindeutig im Katalog', master)
    entry = matches[0]
    return REPO / 'Downloads' / entry['id'] / f"{entry['archiveStem']}_v{entry['version']}_SCORM12.zip"


@functools.lru_cache(maxsize=1)
def task_forms():
    return json.loads((REPO / 'Fachbereiche/BRC/LG01/quellen/Arbeitsformen.json').read_text())


def task_form(lesson, phase, mode, number):
    forms = task_forms()
    return forms[f'{lesson["folder"]}:{phase}:{mode}:{number}']


def assert_pupil_modes_hidden(page):
    assert page.locator('[data-mode-label]:visible,.mode-badge:visible,[data-student-mode]:visible,.phase-mode-title:visible').count() == 0


def verify_story_image(page, base, lesson, role):
    expected = lesson['images'][role]
    figure = page.locator(f'figure.story-photo[data-media-key="{role}"]')
    assert figure.count() == 1 and figure.is_visible(), (lesson['id'], role)
    picture = figure.locator('img')
    assert picture.count() == 1
    picture.wait_for(state='visible')
    page.wait_for_function('e=>e.complete&&e.naturalWidth>0&&e.naturalHeight>0', arg=picture.element_handle())
    assert picture.get_attribute('src') == expected['file']
    assert picture.get_attribute('alt'), (lesson['id'], role, 'Missing image description')
    original = REPO / 'Fachbereiche/BRC/LG01/quellen/Bilder' / Path(expected['file']).name
    response = page.request.get(base + expected['file'])
    assert response.ok and response.body() == original.read_bytes()
    assert hashlib.sha256(response.body()).hexdigest() == expected['sha256']


def verify_manifest(root, archive=None):
    raw = archive.read('imsmanifest.xml') if archive else (root / 'imsmanifest.xml').read_bytes()
    manifest = ET.fromstring(raw)
    paths = []
    for element in manifest.iter():
        kind = element.tag.split('}')[-1]
        if kind in ['file', 'resource'] and 'href' in element.attrib:
            name = element.attrib['href']
            assert not name.startswith(('/', 'http:', 'https:')) and '..' not in Path(name).parts, name
            assert (root / name).is_file(), (root.name, name)
            if archive:
                assert name in archive.namelist(), (root.name, name)
                assert archive.read(name) == (root / name).read_bytes(), (root.name, name)
            if kind == 'file':
                paths.append(name)
    assert 'lesson-data.js' in paths and 'progress-meta.js' in paths
    assert 'assets/bbs1-campus-background.png' in paths
    return paths


def verify_artifacts(series, lessons, source):
    independent = read_plan_budgets(source)
    identities, competency_ids = set(), set()
    task_total = 0
    image_map = json.loads((REPO / 'Fachbereiche/BRC/LG01/quellen/Bildzuordnung.json').read_text())
    forms = task_forms()
    for lesson in lessons:
        root = lesson_root(series, lesson)
        data, meta = payload(root / 'lesson-data.js'), payload(root / 'progress-meta.js')
        assert data['id'] == meta['id'] == lesson['id']
        assert data['id'] not in identities
        identities.add(data['id'])
        assert data['title'] == lesson['title']
        assert len(data['competencies']) == len(meta['competencies']) == 5
        assert data['priorityStatement'].startswith('Ich ')
        for competency in data['competencies']:
            assert competency['statement'].startswith('Ich ')
            assert competency['id'] not in competency_ids
            competency_ids.add(competency['id'])
        assert lesson['budgets'] == independent[root.name], (root.name, lesson['budgets'], independent[root.name])
        assert [data['phaseBudgets'][phase] for phase in PHASES] == independent[root.name]
        assert set(task['mode'] for task in meta['tasks'].values()) == set(range(1, 6))
        assert set(task['phase'] for task in meta['tasks'].values()) == set(PHASES)
        task_total += len(meta['tasks'])
        for phase in ['bewerten', 'reflektieren']:
            for mode in range(1, 6):
                assert sum(task['phase'] == phase and task['mode'] == mode for task in meta['tasks'].values()) == 1, (root.name, phase, mode)
        for identity, task in meta['tasks'].items():
            number = identity.split(':')[-1]
            form = forms[f'{root.name}:{task["phase"]}:{task["mode"]}:{number}']
            assert form['kind'] in ['individual', 'pair', 'group', 'partner-groups', 'expert-group'] and form['label'] and form['reason']
        media = json.loads((root / 'media-map.json').read_text())
        for role in ['orientation', 'situation']:
            image = lesson['images'][role]
            definition = image_map[str(int(root.name[2:]))][role]
            assert Path(image['file']).name == definition['filename']
            original = REPO / 'Fachbereiche/BRC/LG01/quellen/Bilder' / definition['filename']
            assert (root / image['file']).read_bytes() == original.read_bytes()
            assert hashlib.sha256(original.read_bytes()).hexdigest() == image['sha256']
            assert media['slots'][role]['src'] == image['file']
        for script in root.glob('assets/*.js'):
            subprocess.run(['node', '--check', str(script)], check=True, capture_output=True)
        manifest_paths = verify_manifest(root)
        assert all(image['file'] in manifest_paths for image in lesson['images'].values())
        archive_path = zip_path(series, lesson)
        with zipfile.ZipFile(archive_path) as archive:
            assert archive.testzip() is None
            assert 'imsmanifest.xml' in archive.namelist()
            verify_manifest(root, archive)
            files = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
            names = {name for name in archive.namelist() if not name.endswith('/')}
            assert files == names, (root.name, files - names, names - files)
            for name in names:
                assert archive.read(name) == (root / name).read_bytes(), (root.name, name)
        print('PASS:', root.name, 'unique IDs, independent plan budgets, JavaScript, manifest and exact root-level SCORM ZIP', flush=True)
    print('PASS: six different lesson IDs and thirty different competency/report IDs; total 80 UStd.', flush=True)
    assert task_total == 440, task_total
    assert len(forms) == task_total
    assert {'individual', 'pair', 'group'} <= {form['kind'] for form in forms.values()}
    print('PASS: 440 complete task groups, one whole checking/reflection task per path, diverse individual/pair/group forms, twelve original images with source SHA-256 and media-map references', flush=True)
    print('PASS: current ZIPs resolved from the master catalog; no legacy collection archive required', flush=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def ready(page):
    page.wait_for_function("document.body.dataset.taskFocusReady === 'true'")


def unlock(page, mode=1, omit=None):
    page.evaluate('''args => {
      const [mode, omit] = args, m = SOZ_PROGRESS_META, p = SOZ_PROGRESS.read();
      p.o = true; p.m = mode;
      for (const q of m.quiz) p.q[q.id] = [q.correct, true];
      for (const [id, t] of Object.entries(m.tasks)) {
        if (t.mode === mode && omit && SOZ_PROGRESS_CORE.phases.indexOf(t.phase) >= SOZ_PROGRESS_CORE.phases.indexOf(omit)) delete p.t[id];
        else p.t[id] = t.signature;
      }
      SOZ_PROGRESS.write(p); SOZ_API.setMode(mode);
    }''', [mode, omit])


def watch(page, base):
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}')
            if response.url.startswith(base) and response.status >= 400 else None)
    return errors


def source_tasks(page, phase, mode):
    return page.evaluate(r'''args => {
      const [phase, mode] = args;
      const doc = new DOMParser().parseFromString(SOZPAED.pages[phase + '.html'], 'text/html');
      const panel = doc.querySelector('[data-mode-panel="' + mode + '"]');
      return [...panel.querySelectorAll('.assignment-frame')].map(card => ({
        id: card.dataset.taskId,
        text: card.querySelector('.assignment-body').textContent,
        minutes: Number(card.querySelector('.assignment-time').textContent.match(/([\d]+(?:[.,]\d+)?)\s*Min/i)[1].replace(',', '.')),
        operators: [...card.querySelectorAll('.assignment-body strong.operator')].map(s => s.textContent)
      }));
    }''', [phase, mode])


def verify_matrix(browser, base, lesson):
    count = 0
    for mode in range(1, 6):
        context = browser.new_context(viewport={'width': 1024, 'height': 768}, reduced_motion='reduce')
        context.add_init_script('const frozenNow=Date.now(); Date.now=()=>frozenNow;')
        context.add_init_script("navigator.canShare=()=>true;navigator.share=async({files})=>{window.sharedWorkbook={name:files[0].name,size:files[0].size,type:files[0].type};}")
        page = context.new_page()
        errors = watch(page, base)
        for phase, budget in zip(PHASES, lesson['budgets']):
            page.goto(base + phase + '.html'); ready(page); unlock(page, mode, phase)
            assert_pupil_modes_hidden(page)
            expected = source_tasks(page, phase, mode)
            assert expected, (lesson['id'], mode, phase)
            for task in expected:
                assert not re.match(r'^(?:Ihr fachlicher Pflichtkern:|Pflichtkern:|Pflichtvergleich:|Mindestanforderung:|Mindeststandard:|Ab dieser Phase dürfen|Ab hier (?:kann|darf) der freigegebene KI-Assistent)', task['text'].strip()), (lesson['id'], mode, phase, task['id'], 'Guidance was exposed as an independent completion task')
            assert math.isclose(sum(task['minutes'] for task in expected), budget, abs_tol=1e-8), (lesson['id'], mode, phase)
            assert page.locator('.task-original-preview:visible').count() == len(expected)
            assert page.locator('.material-access,.phase-materials').count() == 1
            assert page.evaluate('''()=>{const d=JSON.parse(JSON.stringify(SOZPAED));return JSON.stringify(SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser()))===JSON.stringify(SOZ_PROGRESS_META)}''')
            page.locator('[data-share-workbook]:visible').first.click()
            page.wait_for_function('!!window.sharedWorkbook')
            shared = page.evaluate('sharedWorkbook')
            filename = f'GoodNotes_Phase_{phase}_W{mode}.pdf'
            assert shared['name'] == filename and shared['type'] == 'application/pdf'
            assert shared['size'] == len(page.request.get(base + 'pdf/' + filename).body())
            for index, task in enumerate(expected):
                preview = page.locator('.task-original-preview:visible').nth(index)
                assert clean(preview.text_content()) == clean(task['text']), (lesson['id'], phase, mode, index, 'truncated overview')
                preview.click()
                focus = page.locator('.task-accordion[open]')
                assert focus.count() == 1
                assert clean(focus.locator('.assignment-body').text_content()) == clean(task['text']), (lesson['id'], phase, mode, index, 'focus text')
                assert focus.locator('.assignment-body strong.operator').all_text_contents() == task['operators']
                assert focus.locator('.assignment-body').evaluate('''body=>[...body.querySelectorAll('p')].every(p=>[...p.querySelectorAll('strong.operator')].filter(s=>/^[A-ZÄÖÜ]/.test(s.textContent.trim())).length<=1)'''), (lesson['id'], phase, mode, index, 'Commands are not separated into paragraphs')
                assert focus.locator('.focus-symbol-strip .assignment-social,.focus-symbol-strip .focus-phase-form').count() == 1, (lesson['id'], phase, mode, index, 'Duplicate or missing social form')
                form = task_form(lesson, phase, mode, index + 1)
                social = focus.locator('.focus-symbol-strip .assignment-social')
                assert social.get_attribute('data-workform') == form['kind']
                assert social.locator('small').inner_text() == form['label']
                assert social.locator('svg').count() == 1
                assert page.locator('.task-original-preview:visible').count() == 0, page.evaluate('''()=>({body:document.body.className,visible:[...document.querySelectorAll('.task-original-preview')].filter(e=>e.checkVisibility()).map(e=>({id:e.closest('.assignment-frame').dataset.taskId,card:e.closest('.assignment-frame').className,display:getComputedStyle(e).display,open:e.closest('.assignment-frame').querySelector('details').open}))})''')
                assert focus.locator('.task-summary a').count() == 0
                focus.locator('.task-summary').click()
                assert page.locator('.task-accordion[open]').count() == 1, 'Header unexpectedly collapsed'
                assert focus.locator('.ais-chat-logo svg').is_visible()
                assert focus.locator('.focus-competence-copy p').inner_text() == page.evaluate("SOZPAED.competencies.find(c=>c.label==='Fachkompetenz').statement")
                assert focus.locator('.task-summary').evaluate("e=>getComputedStyle(e).outlineStyle==='none'")
                assert focus.evaluate('e=>Math.abs(e.querySelector(".focus-competence").getBoundingClientRect().y-e.querySelector(".focus-toolbar").getBoundingClientRect().y)<2')
                seconds = round(task['minutes'] * 60)
                assert focus.locator('.focus-countdown').inner_text() == f'{seconds // 60:02}:{seconds % 60:02}', (lesson['id'], phase, mode, index, seconds)
                checkbox = focus.locator('[data-task-complete]')
                assert checkbox.get_attribute('data-task-id') == task['id']
                assert not checkbox.is_checked() and focus.locator('.focus-next').is_disabled(), (lesson['id'], phase, mode, index, task['id'], checkbox.is_checked(), focus.locator('.focus-next').is_disabled(), page.evaluate('SOZ_PROGRESS.read().t'))
                assert focus.locator('..').evaluate('e=>getComputedStyle(e).borderLeftColor') == 'rgb(0, 155, 217)'
                checkbox.check()
                assert focus.locator('.focus-next').is_enabled()
                assert focus.locator('[data-task-complete]').get_attribute('data-task-id') == task['id'], 'Unexpected automatic advance'
                footer = focus.locator('.focus-task-footer')
                left = footer.locator('.focus-back-actions').bounding_box()
                middle = footer.locator('label').bounding_box()
                right = footer.locator('.focus-next').bounding_box()
                assert left['x'] < middle['x'] < right['x']
                assert page.locator('.footer-utils [data-document-pdf]').is_visible()
                assert page.locator('[data-document-pdf]').count() == 1
                if index + 1 < len(expected):
                    focus.locator('.focus-next').click()
                    assert page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id') == expected[index + 1]['id']
                    page.locator('.task-accordion[open] .focus-back-actions>button').click()
                else:
                    focus.locator('.focus-back-actions>button').click()
                card = page.locator(f'.assignment-frame[data-task-id="{task["id"]}"]')
                assert card.evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(243, 248, 231)'
                assert card.locator('.task-done-check').is_visible()
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                count += 1
            # All current task marks are now set. The phase footer may proceed.
            assert page.evaluate('args=>SOZ_PROGRESS_CORE.phaseComplete(SOZ_PROGRESS.read(),SOZ_PROGRESS_META,...args)', [phase, mode])
        assert not errors, errors
        context.close()
        print('PASS:', lesson['id'], 'path', mode, 'all phase budgets and every complete task, timer, manual completion/next, blue focus/green finished card', flush=True)
    return count


def verify_gates(browser, base, lesson):
    context = browser.new_context(); page = context.new_page(); errors = watch(page, base)
    for mode in range(1, 6):
        for phase, successor in zip(PHASES[:-1], PHASES[1:]):
            page.goto(base + phase + '.html'); ready(page); unlock(page, mode)
            page.evaluate('''args=>{const [phase, mode]=args,p=SOZ_PROGRESS.read();
                const id=Object.entries(SOZ_PROGRESS_META.tasks).find(([,t])=>t.phase===phase&&t.mode===mode)[0];
                delete p.t[id];SOZ_PROGRESS.write(p);}''', [phase, mode])
            assert page.locator(f'.stations [data-learning-page="{successor}.html"]').get_attribute('aria-disabled') == 'true'
            assert page.locator('.page-turn a').last.get_attribute('aria-disabled') == 'true'
            page.goto(base + successor + '.html'); ready(page)
            page.evaluate('mode=>SOZ_API.setMode(mode)', mode)
            assert page.locator('.lesson-content').is_hidden()
            assert page.locator('[data-phase-gate]').is_visible()
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'all 25 phase transitions block navigation and direct access when a previous task is incomplete', flush=True)


def verify_materials_and_layout(browser, base, lesson):
    context = browser.new_context(viewport={'width': 1024, 'height': 768}, reduced_motion='reduce')
    context.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new DOMException('Denied','SecurityError')}})")
    page = context.new_page(); errors = watch(page, base)
    for mode in range(1, 6):
        page.goto(base + 'informieren.html'); ready(page); unlock(page, mode)
        page.locator('.task-original-preview:visible').first.click()
        task = page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')
        first_material = page.locator('.material-access a[href^="m"],.phase-materials a[href^="m"]').first
        first_material.click()
        materials = page.locator('.material-switch a').count()
        assert materials >= 1
        for index in range(materials):
            if index:
                page.locator('.material-switch summary').click()
                page.locator('.material-switch a').nth(index).click()
            assert page.locator('.return-task').is_visible()
            assert page.locator('.return-task').evaluate('e=>e.parentElement===document.body')
            assert page.locator('.return-task-inline,.material-phase-turn').count() == 0
            assert page.locator('.material-topbar [data-document-pdf]').count() == 0
            assert page.locator('[data-document-pdf]').count() == 1
            assert page.locator('.footer-utils [data-document-pdf]').is_visible()
            assert page.locator('.material-switch:visible').count() == 1
            assert page.locator('.material-phase-links a').count() == 8
            assert page.locator('.lesson-content>.hero').is_hidden()
            assert page.locator('[data-share-workbook]:visible').count() == 0
            assert page.evaluate('SOZ_MATERIAL_RETURN.read().task') == task
            assert page.evaluate('Number(document.body.dataset.mode)') == mode
            assert page.locator('.return-task').get_attribute('href').startswith('informieren.html?aufgabe=')
            assert page.evaluate('document.querySelector(".lesson-content").compareDocumentPosition(document.querySelector(".material-phase-navigation")) & Node.DOCUMENT_POSITION_FOLLOWING')
            # Material-phase links obey the same gate as their full pages.
            page.evaluate('''mode=>{const p=SOZ_PROGRESS.read(),id=Object.entries(SOZ_PROGRESS_META.tasks).find(([,t])=>t.phase==='informieren'&&t.mode===mode)[0];delete p.t[id];SOZ_PROGRESS.write(p);}''', mode)
            assert page.locator('.material-phase-links [data-learning-page="planen.html"]').get_attribute('aria-disabled') == 'true'
            unlock(page, mode)
        page.locator('.return-task').click(); ready(page)
        assert page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id') == task
        aliases = page.evaluate('''mode=>{
          const m=SOZ_PROGRESS_META,found=[];
          for(const phase of ['bewerten','reflektieren']){
            const entry=Object.entries(m.migration?.tasks||{}).find(([id,g])=>m.tasks[id]?.phase===phase&&m.tasks[id]?.mode===mode&&g.signature===m.tasks[id].signature&&g.from.some(old=>!Object.prototype.hasOwnProperty.call(m.tasks,old.id)));
            if(entry){const [target,group]=entry;found.push({target,old:group.from.find(old=>!Object.prototype.hasOwnProperty.call(m.tasks,old.id)).id,phase});}
          }
          return found;
        }''', mode)
        for alias in aliases:
            page.goto(base + 'm1.html?rueckaufgabe=' + alias['old'].replace(':', '%3A'))
            assert page.evaluate('SOZ_MATERIAL_RETURN.read().task') == alias['target']
            assert page.locator('.return-task').get_attribute('href').startswith(alias['phase'] + '.html?aufgabe=')
            page.locator('.return-task').click(); ready(page)
            assert page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id') == alias['target']
    for width, height in WIDTHS:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(base + 'index.html')
        assert_pupil_modes_hidden(page)
        verify_story_image(page, base, lesson, 'orientation')
        headings = [heading.strip() for heading in page.locator('.lesson-content h2').all_text_contents()]
        assert 'Einordnung' not in headings and 'Fünf alternative Lernwege' not in headings
        assert page.locator('.series-ways').count() == 0
        assert page.locator('.material-access,.phase-materials,[data-share-workbook]').count() == 0
        assert page.locator('.orientation-priority p').inner_text() == page.evaluate('SOZPAED.priorityStatement')
        details = page.locator('.orientation-competence-list')
        assert details.locator('p').count() == 4
        assert all(text.startswith('Ich ') for text in details.locator('p').all_text_contents())
        cards = details.locator(':scope>article,:scope>div')
        assert cards.count() == 4
        rectangles = [cards.nth(i).bounding_box() for i in range(4)]
        if width >= 600:
            assert abs(rectangles[0]['y'] - rectangles[1]['y']) <= 1
            assert abs(rectangles[2]['y'] - rectangles[3]['y']) <= 1
            assert rectangles[1]['x'] > rectangles[0]['x']
            assert abs(rectangles[2]['x'] - rectangles[0]['x']) <= 1
            assert rectangles[2]['y'] >= max(rectangles[0]['y'] + rectangles[0]['height'], rectangles[1]['y'] + rectangles[1]['height']) - 1
        else:
            assert all(abs(rectangles[i]['x'] - rectangles[0]['x']) <= 1 for i in range(4))
            assert all(rectangles[i + 1]['y'] > rectangles[i]['y'] for i in range(3))
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert page.evaluate("getComputedStyle(document.body,'::before').position==='fixed'&&getComputedStyle(document.body,'::before').backgroundSize==='cover'")
        page.goto(base + 'handlungssituation.html')
        assert_pupil_modes_hidden(page)
        verify_story_image(page, base, lesson, 'situation')
        assert page.locator('[data-share-workbook]').count() == 0
        assert page.locator('.tools-bar:visible').count() == 0
        page.goto(base + 'informieren.html'); ready(page); unlock(page, 1)
        page.locator('.task-original-preview:visible').first.click()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        if width >= 768:
            assert page.locator('.task-accordion[open]').evaluate('e=>Math.abs(e.querySelector(".focus-competence").getBoundingClientRect().y-e.querySelector(".focus-toolbar").getBoundingClientRect().y)<2')
        page.locator('.material-access a[href^="m"],.phase-materials a[href^="m"]').first.click()
        page.locator('.material-switch summary').click()
        for material_index in range(page.locator('.material-switch a').count()):
            if material_index:
                page.locator('.material-switch a').nth(material_index).click()
                page.locator('.material-switch summary').click()
            assert page.locator('.material-switch>nav').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            assert page.locator('.material-switch a').last.is_visible()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), (lesson['id'], width, material_index)
        for scroll in [0, 500, 2000]:
            page.evaluate('y=>scrollTo(0,y)', scroll)
            rectangle = page.locator('.return-task').bounding_box()
            assert 0 <= rectangle['y'] and rectangle['y'] + rectangle['height'] <= height
            assert page.locator('.return-task').evaluate('e=>{const r=e.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2).closest(".return-task")===e}')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    page.evaluate("()=>{const v=visualViewport;Object.defineProperty(v,'height',{configurable:true,value:520});Object.defineProperty(v,'offsetTop',{configurable:true,value:40});v.dispatchEvent(new Event('resize'));}")
    rectangle = page.locator('.return-task').bounding_box()
    assert rectangle['y'] + rectangle['height'] <= 560
    page.evaluate("()=>{delete visualViewport.height;delete visualViewport.offsetTop;visualViewport.dispatchEvent(new Event('resize'));}")
    page.goto(base + 'm1.html?rueckaufgabe=constructor')
    assert page.locator('.return-task').get_attribute('aria-disabled') == 'true'
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'every material/path with denied storage, exact task return, minimal UI/gates; hidden pupil mode controls, source images and 2x2 competencies from 600px; orientation/focus/materials at four widths', flush=True)


def verify_quiz_layout(browser, base, lesson):
    context = browser.new_context(reduced_motion='reduce')
    page = context.new_page(); errors = watch(page, base)
    for width, height in WIDTHS:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(base + 'handlungssituation.html')
        page.wait_for_function("document.querySelector('[data-situation-quiz]')?.dataset.quizReady==='true'")
        assert_pupil_modes_hidden(page)
        questions = page.locator('[data-situation-quiz] script[type="application/json"]').evaluate('e=>JSON.parse(e.textContent)')
        assert len(questions) == 5
        for question in questions:
            assert len(question['options']) == 6
            panel = page.locator(f'[data-quiz-question="{question["id"]}"]')
            panel.evaluate('e=>e.closest("details").open=true')
            options = panel.locator(':scope>label')
            assert options.count() == 6
            rectangles = [options.nth(i).bounding_box() for i in range(6)]
            assert all(rectangle['height'] > 0 for rectangle in rectangles)
            assert all(abs(rectangles[i]['x'] - rectangles[0]['x']) <= 1 for i in range(6))
            assert all(abs(rectangles[i]['width'] - rectangles[0]['width']) <= 1 for i in range(6))
            assert all(rectangles[i + 1]['y'] >= rectangles[i]['y'] + rectangles[i]['height'] - 1 for i in range(5)), (lesson['id'], width, question['id'], 'Options overlap or share a row')
            assert panel.locator('input[type="radio"]').count() == 6
            panel.locator(f'input[value="{question["correct"]}"]').check()
            panel.locator('[data-quiz-submit]').click()
            assert panel.locator('[data-quiz-feedback]').get_attribute('data-result') == 'correct'
            assert panel.locator('..').locator('[data-quiz-marker]').inner_text() == ''
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'five authentic MC questions with six vertically stacked choices, correct submission and no redundant ticks at all four widths', flush=True)


def verify_timer_and_help(browser, base, lesson):
    context = browser.new_context(viewport={'width': 768, 'height': 1024}, reduced_motion='reduce')
    context.add_init_script('''
      const testNow=Date.now();window.testOffset=0;Date.now=()=>testNow+testOffset;
      window.testChimes=0;
      window.AudioContext=class{constructor(){this.state='running';this.currentTime=0;this.destination={}}
        createOscillator(){return {frequency:{value:0},connect(){},start(){window.testChimes++},stop(){}}}
        createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}}}};
    ''')
    page = context.new_page(); errors = watch(page, base); popups = []
    page.on('popup', lambda popup: popups.append(popup))
    page.route('https://app.ais-chat.schule/**', lambda route: route.fulfill(body='<html><input aria-label="Frage"></html>', content_type='text/html'))
    page.goto(base + 'informieren.html'); ready(page); unlock(page)
    first = source_tasks(page, 'informieren', 1)[0]
    total = round(first['minutes'] * 60)
    page.locator('.task-original-preview:visible').first.click()
    focus = page.locator('.task-accordion[open]')
    assert focus.locator('.focus-countdown').evaluate('e=>getComputedStyle(e).color') == 'rgb(175, 202, 11)'
    page.evaluate('offset=>testOffset=offset', total * 500)
    half = total // 2
    page.wait_for_function('text=>document.querySelector(".task-accordion[open] .focus-countdown").textContent===text', arg=f'{half // 60:02}:{half % 60:02}')
    assert focus.locator('.focus-countdown').evaluate('e=>getComputedStyle(e).color') == 'rgb(17, 17, 17)'
    focus.locator('.focus-timer-row button').click()
    saved = focus.locator('.focus-countdown').inner_text()
    page.evaluate('testOffset+=60000')
    page.wait_for_timeout(250)
    assert focus.locator('.focus-countdown').inner_text() == saved
    focus.locator('.focus-timer-row button').click()
    task = focus.locator('[data-task-complete]').get_attribute('data-task-id')
    page.locator('.material-access a[href^="m"],.phase-materials a[href^="m"]').first.click()
    if page.locator('.material-switch a').count() > 1:
        page.locator('.material-switch summary').click()
        page.locator('.material-switch a').nth(1).click()
    page.locator('.return-task').click(); ready(page)
    assert focus.locator('[data-task-complete]').get_attribute('data-task-id') == task
    assert focus.locator('.focus-countdown').inner_text() == saved, 'Material round trip reset the remaining orientation time'
    # Re-arm sound in the new document with a real timer-button interaction.
    focus.locator('.focus-timer-row button').click()
    focus.locator('.focus-timer-row button').click()
    page.evaluate('offset=>testOffset+=offset', total * 500)
    page.wait_for_function('document.querySelector(".task-accordion[open] .focus-countdown").textContent==="00:00"')
    assert focus.locator('.focus-countdown').evaluate('e=>getComputedStyle(e).color') == 'rgb(180, 35, 24)'
    assert focus.locator('.focus-timer-row button').is_hidden()
    assert focus.locator('.focus-sound').is_visible() and '🔔' in focus.locator('.focus-sound').inner_text()
    assert page.evaluate('testChimes') > 0
    focus.locator('.focus-sound input').uncheck()
    assert not focus.locator('.focus-sound input').is_checked()
    focus.get_by_role('button', name='AIS.chat KI-Hilfe öffnen').click()
    assert page.get_by_text('KI-Hilfe · Löppt-Pilot', exact=True).is_visible()
    assert page.get_by_text('Hilfe zur Selbsthilfe · Deine Lösung erarbeitest du selbst.', exact=True).is_visible()
    page.frame_locator('.ais-help-frame').get_by_label('Frage').fill('Welcher nächste Schritt hilft mir?')
    assert not popups
    page.get_by_role('button', name='Schließen', exact=True).click()
    assert page.locator('.task-accordion[open]').count() == 1
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'green/black/red countdown, pause, retained remaining time across materials, end chime/mute bell, continued task and same-page AIS help dialog mock', flush=True)


def verify_teacher(browser, base, lesson):
    context = browser.new_context(viewport={'width': 1024, 'height': 768}, accept_downloads=True)
    page = context.new_page(); errors = watch(page, base)
    page.goto(base + 'lehrkraft.html')
    page.locator('#teacher-pin').fill('wrong'); page.locator('#teacher-unlock').click()
    assert page.locator('#teacher-panel').is_hidden()
    page.evaluate("SOZ_CONFIG.pinHash=[...'2468'].reduce((v,c)=>v*31+c.charCodeAt(0),0)")
    page.locator('#teacher-pin').fill('2468'); page.locator('#teacher-unlock').click()
    assert page.locator('#teacher-panel').is_visible()
    page.locator('[data-edit-page]').select_option('informieren.html')
    editor = page.locator('[data-page-editor]')
    assert page.evaluate('''()=>{
      const d=JSON.parse(JSON.stringify(SOZPAED)),doc=new DOMParser().parseFromString(d.pages['informieren.html'],'text/html');
      doc.querySelector('.assignment-time').textContent=' (ca. 11,5 Min.)';d.pages['informieren.html']=doc.body.innerHTML;
      const m=SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser());
      return JSON.stringify(m.tasks)===JSON.stringify(SOZ_PROGRESS_META.tasks);
    }'''), 'A pure orientation-time edit invalidated existing task signatures'
    editor.locator('.assignment-body').first.evaluate("e=>(e.querySelector('p,li')||e).append(document.createTextNode(' Verifikationsbeleg nur im Test.'))")
    editor.locator('.assignment-time').first.evaluate("e=>e.textContent=' (ca. 11,5 Min.)'")
    task = editor.locator('.assignment-frame').first.get_attribute('data-task-id')
    page.locator('[data-save-page]').click()
    with page.expect_download(timeout=60000) as event:
        page.locator('[data-export-ims]').click()
    exported = Path('/tmp') / f'{lesson["id"]}_Verifier_Editor.zip'
    event.value.save_as(exported)
    with zipfile.ZipFile(exported) as archive:
        assert archive.testzip() is None
        data = payload(archive.read('lesson-data.js'))
        assert 'Verifikationsbeleg nur im Test.' in data['pages']['informieren.html']
        assert '(ca. 11,5 Min.)' in data['pages']['informieren.html']
        assert payload(archive.read('progress-meta.js'))['id'] == lesson['id']
        exported_media = payload(archive.read('media-map.js'))
        for role, image in lesson['images'].items():
            assert archive.read(image['file']) == (REPO / 'Fachbereiche/BRC/LG01/quellen/Bilder' / Path(image['file']).name).read_bytes()
            assert hashlib.sha256(archive.read(image['file'])).hexdigest() == image['sha256']
            assert exported_media['slots'][role]['src'] == image['file']
        for element in ET.fromstring(archive.read('imsmanifest.xml')).iter():
            if element.tag.split('}')[-1] == 'file':
                assert element.attrib['href'] in archive.namelist()
    page.goto(base + 'informieren.html'); ready(page); unlock(page)
    assert 'Verifikationsbeleg nur im Test.' in page.locator('.task-original-preview:visible').first.text_content()
    page.locator('.task-original-preview:visible').first.click()
    focus = page.locator('.task-accordion[open]')
    assert focus.locator('[data-task-complete]').get_attribute('data-task-id') == task
    assert 'Verifikationsbeleg nur im Test.' in focus.locator('.assignment-body').text_content()
    assert focus.locator('.focus-countdown').inner_text() in ['11:30', '11:29']
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'teacher PIN, saved real task and decimal-time override in overview/focus, current SCORM export with complete manifest', flush=True)


def scorm_context(browser):
    context = browser.new_context()
    context.add_init_script('''
      const key='verifier-cmi:'+location.pathname.replace(/[^/]+$/,'');
      window.testCMIKey=key;
      window.testCMI=JSON.parse(localStorage.getItem(key)||'null')||{
        'cmi.core.student_id':'test-learner','cmi.core.lesson_mode':'normal',
        'cmi.suspend_data':'','cmi.interactions._count':'0'};
      window.testCommits=0;
      window.API={LMSInitialize:()=> 'true',LMSGetValue:k=>testCMI[k]||'',
        LMSGetLastError:()=> '0',LMSSetValue:(k,v)=>{testCMI[k]=v;localStorage.setItem(key,JSON.stringify(testCMI));return 'true'},
        LMSCommit:()=>{testCommits++;return 'true'},LMSFinish:()=> 'true'};
    ''')
    return context


def verify_scorm(browser, base, lesson):
    context = scorm_context(browser)
    page = context.new_page(); errors = watch(page, base)
    page.goto(base + 'scorm.html'); page.wait_for_function("SOZ_SCORM?.kind==='moodle'")
    evidence = 'Kompetenzbeleg ' + lesson['id']
    page.evaluate('''evidence=>{const p=SOZ_SCORM.read();p.o=true;for(const q of SOZ_PROGRESS_META.quiz)p.q[q.id]=[q.correct,true];
      p.a.assessments[SOZ_PROGRESS_META.competencies[0].id]={after:3,evidence};SOZ_SCORM.update(p);
      document.querySelector('[data-scorm-frame]').src='informieren.html';}''', evidence)
    page.wait_for_function("document.querySelector('[data-scorm-frame]').contentWindow.document.body?.dataset.taskFocusReady==='true'")
    frame = page.frame_locator('[data-scorm-frame]')
    frame.locator('.task-original-preview:visible').first.click()
    task = frame.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')
    frame.locator('.task-accordion[open] [data-task-complete]').check()
    assert page.evaluate('task=>SOZ_SCORM.read().t[task]===SOZ_PROGRESS_META.tasks[task].signature', task)
    assert page.evaluate('evidence=>testCMI["cmi.suspend_data"].length>0&&testCommits>0&&Object.values(testCMI).includes(evidence)', evidence)
    assert page.evaluate('SOZ_SCORM.read().l') == lesson['id']
    assert page.evaluate('testCMI["cmi.core.lesson_location"]') == 'informieren.html'
    report_ids = page.evaluate(r'Object.entries(testCMI).filter(([k])=>/cmi\.interactions\.\d+\.id$/.test(k)).map(([,v])=>v)')
    assert report_ids and all(lesson['id'] in item for item in report_ids)
    page.reload()
    page.wait_for_function("document.querySelector('[data-scorm-frame]').contentWindow.document.body?.dataset.taskFocusReady==='true'")
    assert frame.locator(f'[data-task-complete][data-task-id="{task}"]').is_checked()
    assert page.evaluate('SOZ_SCORM.read().a.assessments[SOZ_PROGRESS_META.competencies[0].id].evidence') == evidence
    assert page.evaluate('testCMI["cmi.core.lesson_status"]') == 'incomplete'
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'SCORM 1.2 API commit, correctly namespaced reports and exact saved task/competency resume after full reload', flush=True)


def verify_migration(browser, base, lesson):
    baseline = json.loads((REPO / 'Fachbereiche/BRC/LG01/quellen/Fortschritt_Vor_Gruppierung.json').read_text())[lesson['folder']]
    context = scorm_context(browser)
    page = context.new_page(); errors = watch(page, base)
    page.goto(base + 'scorm.html'); page.wait_for_function("SOZ_SCORM?.kind==='moodle'")
    legacy = page.evaluate('''baseline=>{
      const p=SOZ_PROGRESS_CORE.initial(SOZ_PROGRESS_META,1);
      p.o=true;p.w=baseline.orientationSignature;p.v=baseline.quizSignature;
      p.b='reflektieren.html';p.r=17;
      for(const t of baseline.tasks)p.t[t.id]=t.signature;
      for(const q of SOZ_PROGRESS_META.quiz)p.q[q.id]=[q.correct,true];
      SOZ_PROGRESS_META.competencies.forEach((c,i)=>p.a.assessments[c.id]={after:i%4+1,evidence:'Erhaltener Beleg '+c.id});
      p.a.feedback='Bestehendes Fremdfeedback';p.a.nextGoal='Bestehender nächster Lernschritt';
      return p;
    }''', baseline)
    assert baseline['quizSignature'] == page.evaluate('SOZ_PROGRESS_META.quizSignature'), 'Quiz content changed despite a pure layout update'
    for mode in range(1, 6):
        legacy['m'] = mode
        result = page.evaluate('''raw=>{
          const m=SOZ_PROGRESS_META,p=SOZ_PROGRESS_CORE.sanitize(raw,m,raw.m);
          return {state:p,every:Object.entries(m.tasks).every(([id,t])=>p.t[id]===t.signature),
            phases:SOZ_PROGRESS_CORE.phases.map(phase=>SOZ_PROGRESS_CORE.phaseComplete(p,m,phase,raw.m)),
            complete:SOZ_PROGRESS_CORE.allComplete(p,m)};
        }''', legacy)
        assert result['every'] and all(result['phases']) and result['complete'], (lesson['id'], mode, result)
        assert result['state']['o'] and result['state']['w'] == page.evaluate('SOZ_PROGRESS_META.orientationSignature')
        assert result['state']['a'] == legacy['a']
        assert result['state']['r'] == 17 and result['state']['b'] == 'reflektieren.html'
        assert result['state']['m'] == mode
        chosen = json.loads(json.dumps(legacy))
        chosen['t'] = {task['id']: task['signature'] for task in baseline['tasks'] if task['mode'] == mode}
        chosen_result = page.evaluate('''raw=>{
          const m=SOZ_PROGRESS_META,p=SOZ_PROGRESS_CORE.sanitize(raw,m,raw.m);
          return {complete:SOZ_PROGRESS_CORE.allComplete(p,m),mode:p.m,a:p.a,
            own:Object.keys(p.t).every(id=>m.tasks[id].mode===raw.m)};
        }''', chosen)
        assert chosen_result['complete'] and chosen_result['mode'] == mode and chosen_result['own']
        assert chosen_result['a'] == legacy['a']
        # An old peer-review block with one missing item cannot complete the
        # new grouped review task. Preserve all other recorded work/reports.
        partial = json.loads(json.dumps(chosen))
        missing = [task for task in baseline['tasks'] if task['phase'] == 'bewerten' and task['mode'] == mode][-1]
        del partial['t'][missing['id']]
        partial_result = page.evaluate('''raw=>{
          const m=SOZ_PROGRESS_META,p=SOZ_PROGRESS_CORE.sanitize(raw,m,raw.m),
            target=Object.entries(m.tasks).find(([,t])=>t.phase==='bewerten'&&t.mode===raw.m)[0];
          return {done:!!p.t[target],phase:SOZ_PROGRESS_CORE.phaseComplete(p,m,'bewerten',raw.m),
            previous:SOZ_PROGRESS_CORE.phaseComplete(p,m,'durchfuehren',raw.m),a:p.a};
        }''', partial)
        assert not partial_result['done'] and not partial_result['phase']
        assert partial_result['previous'] and partial_result['a'] == legacy['a']
    foreign = json.loads(json.dumps(legacy)); foreign['l'] = 'unrelated-lesson'
    assert page.evaluate('raw=>Object.keys(SOZ_PROGRESS_CORE.sanitize(raw,SOZ_PROGRESS_META,1).t).length===0', foreign)
    legacy['m'] = 1
    legacy['t'] = {task['id']: task['signature'] for task in baseline['tasks'] if task['mode'] == 1}
    # Real startup path: LMSGetValue receives the previous compressed payload,
    # rather than calling the new update API with already migrated data.
    page.evaluate('''raw=>{
      testCMI['cmi.suspend_data']=SOZ_SCORM_CODEC.encode(raw);
      testCMI['cmi.interactions._count']='29';
      testCMI['cmi.core.lesson_location']='reflektieren.html';
      localStorage.setItem(testCMIKey,JSON.stringify(testCMI));
      // The still-open initial page must not overwrite this simulated LMS
      // restore fixture in its beforeunload commit. The next document gets
      // the normal mock API from the context init script again.
      API.LMSSetValue=()=> 'true';
    }''', legacy)
    page.reload()
    page.wait_for_function("SOZ_SCORM?.kind==='moodle'")
    page.wait_for_function("document.querySelector('[data-scorm-frame]').contentWindow.document.body?.dataset.taskFocusReady==='true'")
    resumed = page.evaluate('SOZ_SCORM.read()')
    assert resumed['a'] == legacy['a'] and resumed['r'] == 17 and resumed['o']
    assert page.evaluate('SOZ_PROGRESS_CORE.allComplete(SOZ_SCORM.read(),SOZ_PROGRESS_META)')
    assert page.evaluate('testCMI["cmi.core.lesson_status"]') == 'completed'
    target = page.evaluate("Object.entries(SOZ_PROGRESS_META.tasks).find(([,t])=>t.phase==='reflektieren'&&t.mode===1)[0]")
    assert page.frame_locator('[data-scorm-frame]').locator(f'[data-task-complete][data-task-id="{target}"]').is_checked()
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'legacy all-done migration in all five paths, partial peer-review stays open, old orientation/reports retained, foreign lesson rejected, actual compressed SCORM resume remains completed', flush=True)


def verify_orientation_migration_guard(browser, base, lesson, actual_export=False):
    baseline = json.loads((REPO / 'Fachbereiche/BRC/LG01/quellen/Fortschritt_Vor_Gruppierung.json').read_text())[lesson['folder']]
    context = browser.new_context(accept_downloads=True)
    page = context.new_page(); errors = watch(page, base)
    page.goto(base + 'lehrkraft.html')
    original_meta = page.evaluate('SOZ_PROGRESS_META')
    assert original_meta['migration']['orientationSignature'] == original_meta['orientationSignature']
    legacy = page.evaluate('''old=>{
      const p=SOZ_PROGRESS_CORE.initial(SOZ_PROGRESS_META,1);
      p.o=true;p.w=old.orientationSignature;p.v=old.quizSignature;
      for(const t of old.tasks)p.t[t.id]=t.signature;
      for(const q of SOZ_PROGRESS_META.quiz)p.q[q.id]=[q.correct,true];
      p.a.assessments[SOZ_PROGRESS_META.competencies[0].id]={after:3,evidence:'Erhaltener Orientierungsbeleg'};
      return p;
    }''', baseline)
    result = page.evaluate('''raw=>{
      const m=SOZ_PROGRESS_META,changed=JSON.parse(JSON.stringify(m));
      changed.orientationSignature=SOZ_PROGRESS_CORE.hash('Verbindlich neuer Orientierungsinhalt '+m.orientationSignature);
      const before=SOZ_PROGRESS_CORE.sanitize(raw,m,1),after=SOZ_PROGRESS_CORE.sanitize(raw,changed,1);
      return {accepted:before.o,changedAccepted:after.o,sameTasks:JSON.stringify(before.t)===JSON.stringify(after.t),sameReports:JSON.stringify(before.a)===JSON.stringify(after.a)};
    }''', legacy)
    assert result['accepted'] and not result['changedAccepted']
    assert result['sameTasks'] and result['sameReports']
    if actual_export:
        page.evaluate("SOZ_CONFIG.pinHash=[...'2468'].reduce((v,c)=>v*31+c.charCodeAt(0),0)")
        page.locator('#teacher-pin').fill('2468'); page.locator('#teacher-unlock').click()
        page.locator('[data-edit-page]').select_option('index.html')
        page.locator('[data-page-editor] .relevance p').first.evaluate("e=>e.append(document.createTextNode(' Neuer verbindlicher Orientierungsauftrag im Export.'))")
        page.locator('[data-save-page]').click()
        with page.expect_download(timeout=60000) as event:
            page.locator('[data-export-ims]').click()
        exported = Path('/tmp') / f'{lesson["id"]}_Orientation_Guard_Export.zip'
        event.value.save_as(exported)
        with zipfile.ZipFile(exported) as archive:
            assert archive.testzip() is None
            edited = payload(archive.read('progress-meta.js'))
            data = payload(archive.read('lesson-data.js'))
            assert 'Neuer verbindlicher Orientierungsauftrag im Export.' in data['pages']['index.html']
            assert edited['orientationSignature'] != original_meta['orientationSignature']
            assert edited['migration']['orientationSignature'] == original_meta['orientationSignature']
            assert data['progressMigration']['orientationSignature'] == original_meta['orientationSignature']
            assert edited['tasks'] == original_meta['tasks']
            assert not page.evaluate('args=>SOZ_PROGRESS_CORE.sanitize(args[0],args[1],1).o', [legacy, edited])
    assert not errors, errors; context.close()
    print('PASS:', lesson['id'], 'orientation alias requires the original target signature, later content changes invalidate only the read mark' + ('; actual teacher export retains target guard' if actual_export else ''), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series', nargs='?', type=Path, default=REPO / 'Fachbereiche/BRC/LG01/series.json')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--lesson', help='Only these comma-separated lesson folders, e.g. LS01,LS02')
    parser.add_argument('--only-artifacts', action='store_true')
    parser.add_argument('--skip-task-matrix', action='store_true')
    parser.add_argument('--matrix-only', action='store_true')
    parser.add_argument('--migration-only', action='store_true')
    parser.add_argument('--orientation-guard-only', action='store_true')
    args = parser.parse_args()
    raw = json.loads(args.series.read_text())
    lessons = raw if isinstance(raw, list) else raw['lessons']
    assert len(lessons) == 6
    source = args.source
    if source is None:
        committed = REPO / 'Fachbereiche/BRC/LG01/quellen/Reihenplan.md'
        candidates = ([committed] if committed.is_file() else []) + list(args.series.parent.glob('*Quell*.md')) + list(Path('/workspace/attachments').rglob('BRC_LG01_PlugAndPlay_Gesamtreihe_5_Lernwege_Narrativ (2).md'))
        assert candidates, 'Pass --source with the uploaded Markdown plan'
        source = candidates[0]
    verify_artifacts(args.series, lessons, source)
    if args.only_artifacts:
        return
    selected = [lesson for lesson in lessons if not args.lesson or lesson['folder'] in args.lesson.split(',')]
    assert selected
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(REPO)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as play:
            browser = play.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
            task_count = 0
            for lesson in selected:
                base = f'http://127.0.0.1:{server.server_port}/' + lesson_root(args.series, lesson).relative_to(REPO).as_posix() + '/'
                if args.orientation_guard_only:
                    verify_migration(browser, base, lesson)
                    verify_orientation_migration_guard(browser, base, lesson, lesson == selected[0])
                    continue
                if args.migration_only:
                    verify_migration(browser, base, lesson)
                    continue
                if not args.skip_task_matrix:
                    task_count += verify_matrix(browser, base, lesson)
                if args.matrix_only:
                    continue
                verify_gates(browser, base, lesson)
                verify_materials_and_layout(browser, base, lesson)
                verify_quiz_layout(browser, base, lesson)
                verify_scorm(browser, base, lesson)
                verify_migration(browser, base, lesson)
                verify_orientation_migration_guard(browser, base, lesson, lesson == selected[0])
                if lesson == selected[0]:
                    verify_teacher(browser, base, lesson)
                    verify_timer_and_help(browser, base, lesson)
            browser.close()
            print('PASS: all selected packages complete;', task_count, 'tasks checked in the full matrix; native Moodle/AIS/GoodNotes still require app checks', flush=True)
    finally:
        server.shutdown(); server.server_close()


if __name__ == '__main__':
    main()
