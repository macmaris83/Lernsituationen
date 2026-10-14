#!/usr/bin/env python3
"""Exercise every new BRC lesson and check the deliverable SCORM archives.

The Markdown phase budgets are read independently of the generator.  These are
Chromium/API simulations; native Moodle, AIS and GoodNotes are not simulated as
if their embedding/share behavior had been verified on a real iPad.
"""
from __future__ import annotations

import argparse
import functools
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
WIDTHS = [(1024, 768), (768, 1024), (390, 844)]


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
    path = Path(lesson['zip'])
    return path if path.is_absolute() else REPO / path


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


def verify_artifacts(series, lessons, source):
    independent = read_plan_budgets(source)
    identities, competency_ids = set(), set()
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
        for script in root.glob('assets/*.js'):
            subprocess.run(['node', '--check', str(script)], check=True, capture_output=True)
        verify_manifest(root)
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
    collection = REPO / 'Downloads/BRC_LG01_PlugAndPlay_Gesamtreihe_SCORM.zip'
    with zipfile.ZipFile(collection) as archive:
        assert archive.testzip() is None
        for lesson in lessons:
            path = zip_path(series, lesson)
            names = [name for name in archive.namelist() if Path(name).name == path.name]
            assert len(names) == 1, (path.name, names)
            assert archive.read(names[0]) == path.read_bytes(), path.name
    print('PASS: collective download contains exactly the checked six individual SCORM packages', flush=True)


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
            expected = source_tasks(page, phase, mode)
            assert expected, (lesson['id'], mode, phase)
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
    for width, height in WIDTHS:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(base + 'index.html')
        assert page.locator('.material-access,.phase-materials,[data-share-workbook]').count() == 0
        assert page.locator('.orientation-priority p').inner_text() == page.evaluate('SOZPAED.priorityStatement')
        details = page.locator('.orientation-competence-list')
        assert details.locator('p').count() == 4
        assert all(text.startswith('Ich ') for text in details.locator('p').all_text_contents())
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert page.evaluate("getComputedStyle(document.body,'::before').position==='fixed'&&getComputedStyle(document.body,'::before').backgroundSize==='cover'")
        page.goto(base + 'handlungssituation.html')
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
    print('PASS:', lesson['id'], 'every material in every path with denied storage: exact task return, minimal UI and gates; orientation/focus/materials at three widths', flush=True)


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


def verify_scorm(browser, base, lesson):
    context = browser.new_context()
    context.add_init_script('''
      const key='verifier-cmi:'+location.pathname.replace(/[^/]+$/,'');
      window.testCMI=JSON.parse(localStorage.getItem(key)||'null')||{
        'cmi.core.student_id':'test-learner','cmi.core.lesson_mode':'normal',
        'cmi.suspend_data':'','cmi.interactions._count':'0'};
      window.testCommits=0;
      window.API={LMSInitialize:()=> 'true',LMSGetValue:k=>testCMI[k]||'',
        LMSGetLastError:()=> '0',LMSSetValue:(k,v)=>{testCMI[k]=v;localStorage.setItem(key,JSON.stringify(testCMI));return 'true'},
        LMSCommit:()=>{testCommits++;return 'true'},LMSFinish:()=> 'true'};
    ''')
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series', nargs='?', type=Path, default=REPO / 'Reihen/BRC_LG01/series.json')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--lesson', help='Only these comma-separated lesson folders, e.g. LS01,LS02')
    parser.add_argument('--only-artifacts', action='store_true')
    parser.add_argument('--skip-task-matrix', action='store_true')
    parser.add_argument('--matrix-only', action='store_true')
    args = parser.parse_args()
    raw = json.loads(args.series.read_text())
    lessons = raw if isinstance(raw, list) else raw['lessons']
    assert len(lessons) == 6
    source = args.source
    if source is None:
        committed = REPO / 'Quellen/BRC_LG01/Reihenplan.md'
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
                if not args.skip_task_matrix:
                    task_count += verify_matrix(browser, base, lesson)
                if args.matrix_only:
                    continue
                verify_gates(browser, base, lesson)
                verify_materials_and_layout(browser, base, lesson)
                verify_scorm(browser, base, lesson)
                if lesson == selected[0]:
                    verify_teacher(browser, base, lesson)
                    verify_timer_and_help(browser, base, lesson)
            browser.close()
            print('PASS: all selected packages complete;', task_count, 'tasks checked in the full matrix; native Moodle/AIS/GoodNotes still require app checks', flush=True)
    finally:
        server.shutdown(); server.server_close()


if __name__ == '__main__':
    main()
