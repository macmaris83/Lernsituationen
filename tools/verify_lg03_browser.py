#!/usr/bin/env python3
"""Browser checks for the twelve LG03 packages using the approved LS06 shell.

For an internal HTML draft use --allow-missing-images --skip-pdf.  These flags
are recorded as limitations in the report and must be omitted for final files.
Real Moodle, AIS authentication and the native GoodNotes handoff are outside
these Chromium/API simulations.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import re
import threading
import traceback
import xml.etree.ElementTree as ET
import zipfile

from playwright.sync_api import sync_playwright

from verify_brc_series import (clean, payload, ready, source_tasks,
                               unlock, verify_gates, verify_scorm,
                               verify_timer_and_help, watch)

REPO = Path(__file__).resolve().parents[1]
PHASES = ['informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren']
STATIONS = ['index.html', 'handlungssituation.html'] + [x + '.html' for x in PHASES]
WIDTHS = [(390, 844), (768, 1024), (1024, 768)]


def require(value, *context):
    if not value:
        raise AssertionError(' · '.join(map(str, context)))


def no_overflow(page, label):
    value = page.evaluate('({page:document.documentElement.scrollWidth,viewport:innerWidth})')
    require(value['page'] <= value['viewport'] + 1, label, 'page overflow', value)


def readable_numbers(page, label):
    broken = page.evaluate(r'''()=>[...document.querySelectorAll('.source-document td')].flatMap(td=>{
      const value=td.textContent.trim();if(!/^[+−-]?\d[\d., %€]*$/.test(value))return [];
      const range=document.createRange();range.selectNodeContents(td);
      const lines=[...range.getClientRects()].filter(r=>r.width>0&&r.height>0).map(r=>r.y);
      return lines.length&&Math.max(...lines)-Math.min(...lines)>3?[value]:[];
    })''')
    require(not broken, label, 'numeric table cells wrap across lines', broken)


def pdf_footer(page):
    link = page.locator('[data-document-pdf]')
    require(link.count() == 1, 'exactly one PDF utility', page.url)
    require(page.locator('.footer-utils [data-document-pdf]').is_visible(), 'PDF beside teacher', page.url)
    require(link.locator('svg').count() == 1, 'PDF icon')
    require('Gesamtdokument als PDF' in link.inner_text(), 'PDF label')
    require('LG03_' in link.get_attribute('href'), 'LG03 PDF path')


def original_images(root):
    path = REPO / 'Quellen/BRC_LG03/Bildzuordnung.json'
    return json.loads(path.read_text(encoding='utf-8')).get(str(int(root.name[2:])), {}) if path.is_file() else {}


def verify_picture(page, root, role):
    """Check real decoded pixels and proportional, uncropped presentation."""
    slots = json.loads((root / 'media-map.json').read_text(encoding='utf-8'))['slots']
    slot = slots[role]
    original = original_images(root)[role]
    figure = page.locator(f'figure.story-photo[data-media-key="{role}"]')
    require(figure.count() == 1 and figure.is_visible(), root.name, role, 'one visible original-picture figure')
    picture = figure.locator('img')
    require(picture.count() == 1 and picture.is_visible(), root.name, role, 'one visible image')
    require(picture.get_attribute('src') == slot['src'], root.name, role, 'assigned original image URL')
    require(picture.get_attribute('alt') == slot['alt'] and slot['alt'].strip(), root.name, role, 'assigned alternate description')
    require(figure.locator('.photo-viewport').count() == 0 and not slot.get('crop'), root.name, role, 'no crop viewport or media crop')
    page.wait_for_function('e=>e.complete&&e.naturalWidth>0&&e.naturalHeight>0', arg=picture.element_handle())
    geometry = picture.evaluate('''image=>{
      const r=image.getBoundingClientRect(),f=image.closest('figure').getBoundingClientRect(),s=getComputedStyle(image);
      return {natural:[image.naturalWidth,image.naturalHeight],width:r.width,height:r.height,
        left:r.left,right:r.right,top:r.top,bottom:r.bottom,
        figure:{left:f.left,right:f.right,top:f.top,bottom:f.bottom},
        fit:s.objectFit,transform:s.transform,clip:s.clipPath,position:s.position};
    }''')
    require(geometry['natural'] == original['dimensions'], root.name, role, 'decoded original dimensions', geometry)
    require(geometry['width'] > 0 and geometry['height'] > 0, root.name, role, 'nonempty rendered image')
    expected_height = geometry['width'] * geometry['natural'][1] / geometry['natural'][0]
    require(abs(geometry['height'] - expected_height) <= 1.5, root.name, role, 'original aspect ratio preserved', geometry)
    require(geometry['fit'] != 'cover' and geometry['transform'] == 'none' and geometry['clip'] == 'none',
            root.name, role, 'no CSS crop or transform', geometry)
    bounds = geometry['figure']
    require(geometry['left'] >= bounds['left'] - 1.5 and geometry['right'] <= bounds['right'] + 1.5
            and geometry['top'] >= bounds['top'] - 1.5 and geometry['bottom'] <= bounds['bottom'] + 1.5,
            root.name, role, 'full image rectangle inside figure', geometry)


def verify_identity(root, skip_pdf, allow_missing_images):
    data = payload(root / 'lesson-data.js')
    meta = payload(root / 'progress-meta.js')
    require(data['id'] == meta['id'] == 'BRC-LG03-' + root.name, root.name, 'unique LG03 identity')
    require(len(meta['tasks']) == 30, root.name, 'one complete phase action in each of 30 phase/path combinations')
    for mode in range(1, 6):
        for phase in PHASES:
            require(sum(t['mode'] == mode and t['phase'] == phase for t in meta['tasks'].values()) == 1,
                    root.name, phase, mode, 'one original phase action')
    for name in ['runtime.js', 'progress.js', 'progress-core.js', 'teacher.js',
                 'export.js', 'scorm.js', 'scorm-codec.js', 'situation.js', 'lg01.js']:
        require((root / 'assets' / name).read_bytes() ==
                (REPO / 'Reihen/BRC_LG01/LS06/assets' / name).read_bytes(), root.name, name, 'approved JS differs')
    slots = json.loads((root / 'media-map.json').read_text())['slots']
    if not allow_missing_images:
        require(set(slots) == {'orientation', 'situation'}, root.name, 'both original images required')
    originals = original_images(root)
    for role, item in slots.items():
        require((root / item['src']).is_file() and item.get('alt'), root.name, role, 'image + alt text')
        require(role in originals, root.name, role, 'original image assignment')
        original = originals[role]
        require(Path(item['src']).name == original['filename'], root.name, role, 'correct original filename')
        source = REPO / 'Quellen/BRC_LG03/Bilder' / original['filename']
        require(source.is_file(), root.name, role, 'original source file')
        source_bytes = source.read_bytes()
        require((root / item['src']).read_bytes() == source_bytes, root.name, role, 'package uses unchanged original image bytes')
        require(hashlib.sha256(source_bytes).hexdigest() == original['sha256'], root.name, role, 'original image SHA256')
    if not skip_pdf:
        for phase in PHASES:
            for mode in range(1, 6):
                require((root / f'pdf/GoodNotes_Phase_{phase}_W{mode}.pdf').is_file(), root.name, phase, mode, 'phase PDF')
                require((root / f'goodnotes-phase-{phase}-W{mode}.js').is_file(), root.name, phase, mode, 'share payload')
        require((root / f'pdf/LG03_{root.name}_Gesamtdruck_A4.pdf').is_file(), root.name, 'total PDF')
    return data, meta


def verify_tasks(browser, base, lesson, skip_pdf):
    checked = 0
    for mode in range(1, 6):
        context = browser.new_context(viewport={'width': 1024, 'height': 768}, reduced_motion='reduce')
        context.add_init_script('const frozenNow=Date.now();Date.now=()=>frozenNow;')
        context.add_init_script("navigator.canShare=()=>true;navigator.share=async({files})=>{window.sharedWorkbook={name:files[0].name,size:files[0].size,type:files[0].type};}")
        page = context.new_page(); errors = watch(page, base)
        for phase in PHASES:
            page.goto(base + phase + '.html'); ready(page); unlock(page, mode, phase)
            require(page.locator('.stations [data-learning-page]').count() == 8, 'eight stations', phase)
            require(page.locator('.material-access,.phase-materials').count() == 1, 'one material access', phase)
            expected = source_tasks(page, phase, mode)
            require(len(expected) == 1, lesson['id'], mode, phase, 'one full action')
            task = expected[0]
            require(task['minutes'] == lesson['phaseBudgets'][phase], lesson['id'], mode, phase, 'original budget')
            require(page.locator('[data-student-mode]:visible').count() == 0, 'choice disabled by default')
            if not skip_pdf:
                page.locator('[data-share-workbook]:visible').first.click()
                page.wait_for_function('!!window.sharedWorkbook')
                shared = page.evaluate('sharedWorkbook')
                name = f'GoodNotes_Phase_{phase}_W{mode}.pdf'
                require(shared['name'] == name and shared['type'] == 'application/pdf', 'current phase/path GoodNotes payload', shared)
                require(shared['size'] == len(page.request.get(base + 'pdf/' + name).body()), 'GoodNotes byte size')
            preview = page.locator('.task-original-preview:visible')
            require(preview.count() == 1 and clean(preview.text_content()) == clean(task['text']), 'complete overview text')
            preview.click(); focus = page.locator('.task-accordion[open]')
            require(focus.count() == 1, 'one open task')
            require(clean(focus.locator('.assignment-body').text_content()) == clean(task['text']), 'complete focused text')
            require(focus.locator('.task-summary a').count() == 0, 'no heading links')
            focus.locator('.task-summary').click()
            require(focus.is_visible(), 'heading does not collapse')
            require(focus.locator('.focus-competence-copy p').inner_text().startswith('Ich '), 'Ich competency')
            require(focus.locator('.ais-chat-logo svg').is_visible(), 'inline AIS logo')
            require(focus.locator('.focus-countdown').inner_text() == f'{task["minutes"]:02.0f}:00', 'phase countdown')
            checkbox = focus.locator('[data-task-complete]')
            require(not checkbox.is_checked() and focus.locator('.focus-next').is_disabled(), 'manual completion initially required')
            checkbox.check()
            require(focus.locator('.focus-next').is_enabled(), 'manual next enabled')
            require(focus.locator('[data-task-complete]').get_attribute('data-task-id') == task['id'], 'no automatic advance')
            pdf_footer(page)
            focus.locator('.focus-next').click()
            require(page.locator('.task-accordion[open]').count() == 0, 'last action returns to phase overview')
            require(page.url.endswith(phase + '.html'), 'no automatic phase advance')
            card = page.locator(f'.assignment-frame[data-task-id="{task["id"]}"]')
            require(card.evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(243, 248, 231)', 'green completed card')
            no_overflow(page, lesson['id'] + '/' + phase)
            checked += 1
        require(not errors, lesson['id'], mode, errors)
        context.close()
    return checked


def verify_quizzes(browser, base):
    context = browser.new_context(reduced_motion='reduce'); page = context.new_page(); errors = watch(page, base)
    for width, height in WIDTHS:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(base + 'handlungssituation.html')
        page.wait_for_function("document.querySelector('[data-situation-quiz]')?.dataset.quizReady==='true'")
        questions = page.locator('[data-situation-quiz] script[type="application/json"]').evaluate('e=>JSON.parse(e.textContent)')
        require(len(questions) == 5, 'five situation checks')
        for q in questions:
            require(len(q['options']) == 6, 'six options')
            panel = page.locator(f'[data-quiz-question="{q["id"]}"]')
            panel.evaluate('e=>e.closest("details").open=true')
            options = panel.locator(':scope>label')
            rectangles = [options.nth(i).bounding_box() for i in range(6)]
            require(all(rectangles[i + 1]['y'] >= rectangles[i]['y'] + rectangles[i]['height'] - 1 for i in range(5)), 'vertical choices', width)
            wrong = next(x['value'] for x in q['options'] if x['value'] != q['correct'])
            panel.locator(f'input[value="{wrong}"]').check(); panel.locator('[data-quiz-submit]').click()
            require(panel.locator('[data-quiz-feedback]').get_attribute('data-result') == 'wrong', 'wrong feedback')
            require(panel.locator('..').locator('summary').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(238, 248, 253)', 'blue unresolved question')
            panel.locator(f'input[value="{q["correct"]}"]').check(); panel.locator('[data-quiz-submit]').click()
            require(panel.locator('[data-quiz-feedback]').get_attribute('data-result') == 'correct', 'correct feedback')
            require(panel.locator('..').locator('summary').evaluate('e=>getComputedStyle(e).backgroundColor') == 'rgb(243, 248, 231)', 'green solved question')
            require(panel.locator('..').locator('[data-quiz-marker]').inner_text() == '', 'no extra checkmark')
        no_overflow(page, 'quiz ' + str(width))
    page.reload(); require(page.locator('.quiz-is-complete').count() == 5, 'quiz persistence')
    require(not errors, errors); context.close()


def verify_materials(browser, base, lesson):
    context = browser.new_context(viewport={'width': 768, 'height': 1024}, reduced_motion='reduce')
    context.add_init_script("Object.defineProperty(window,'sessionStorage',{get(){throw new DOMException('Denied','SecurityError')}})")
    page = context.new_page(); errors = watch(page, base)
    visits = 0
    for mode in range(1, 6):
        page.goto(base + 'informieren.html'); ready(page); unlock(page, mode)
        page.locator('.task-original-preview:visible').click()
        task = page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')
        page.locator('.material-access a,.phase-materials a').first.click()
        page.locator('.material-switch').wait_for(state='visible')
        count = page.locator('.material-switch a').count()
        require(count > 0, 'material count')
        for index in range(count):
            if index:
                page.locator('.material-switch summary').click(); page.locator('.material-switch a').nth(index).click()
            # Link clicks can resolve before the new document's bottom scripts
            # finish.  Wait for the actual material controls, created after the
            # return API, rather than reading that API during page loading.
            page.locator('.material-switch').wait_for(state='visible')
            page.locator('.return-task').wait_for(state='visible')
            require('rueckaufgabe=' in page.url, 'task in URL')
            require(page.evaluate('SOZ_MATERIAL_RETURN.read().task') == task, 'correct task without session storage')
            require(page.evaluate('Number(document.body.dataset.mode)') == mode, 'material mode retained')
            require(page.locator('.return-task').is_visible(), 'floating return')
            require(page.locator('.return-task').evaluate('e=>e.parentElement===document.body'), 'floating return outside content frame')
            require(page.locator('.material-phase-links a').count() == 8, 'all eight material phase links')
            require(page.locator('.material-switch:visible').count() == 1, 'one material switch')
            require(page.locator('[data-share-workbook],.material-phase-turn,.return-task-inline').count() == 0, 'compact material controls')
            pdf_footer(page)
            page.evaluate('''mode=>{const p=SOZ_PROGRESS.read(),id=Object.entries(SOZ_PROGRESS_META.tasks).find(([,t])=>t.phase==='informieren'&&t.mode===mode)[0];delete p.t[id];SOZ_PROGRESS.write(p);}''', mode)
            require(page.locator('.material-phase-links [data-learning-page="planen.html"]').get_attribute('aria-disabled') == 'true', 'material cannot bypass phase gate')
            unlock(page, mode); no_overflow(page, 'material ' + str(index)); visits += 1
        page.locator('.return-task').click(); ready(page)
        require(page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id') == task, 'exact task return')
    page.goto(base + 'm1.html?rueckaufgabe=constructor')
    require(page.locator('.return-task').get_attribute('aria-disabled') == 'true', 'invalid return disabled')
    require(not errors, errors); context.close()
    return visits


def verify_layout(browser, base, lesson, root, report_dir, allow_missing_images):
    context = browser.new_context(reduced_motion='reduce'); page = context.new_page(); errors = watch(page, base)
    materials = sorted(root.glob('m*.html'), key=lambda p: int(p.stem[1:]))
    picture_views = 0
    for width, height in WIDTHS:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(base + 'index.html')
        require(page.locator('.material-access,.phase-materials,[data-share-workbook]').count() == 0, 'clean orientation')
        require(page.locator('.series-ways,[data-mode-label]:visible,.phase-mode-title:visible').count() == 0, 'no alternate path overview')
        headings = page.locator('.lesson-content h2').all_text_contents()
        require('Einordnung' not in headings and not any('Lehrkräft' in h or 'Erwartungshorizont' in h for h in headings), 'no teacher notes in orientation')
        require(page.locator('.orientation-competence-list p').count() == 4, 'four further competencies')
        require(page.locator('.orientation-priority p').inner_text().startswith('Ich '), 'priority competency')
        require(page.evaluate("getComputedStyle(document.body,'::before').position==='fixed'&&getComputedStyle(document.body,'::before').backgroundSize==='cover'"), 'fixed campus background')
        no_overflow(page, 'orientation ' + str(width)); pdf_footer(page)
        if root.name == 'LS01' and width == 1024:
            page.screenshot(path=str(report_dir / 'LS01_Orientierung_1024.png'), full_page=True)
        if not allow_missing_images:
            verify_picture(page, root, 'orientation'); picture_views += 1
            if root.name in ('LS01', 'LS08'):
                page.screenshot(path=str(report_dir / f'{root.name}_Orientierung_{width}.png'), full_page=True)
        page.goto(base + 'handlungssituation.html')
        require(page.locator('[data-share-workbook]').count() == 0, 'no introductory GoodNotes import')
        no_overflow(page, 'situation ' + str(width)); pdf_footer(page)
        if not allow_missing_images:
            verify_picture(page, root, 'situation'); picture_views += 1
            if root.name in ('LS01', 'LS08'):
                page.screenshot(path=str(report_dir / f'{root.name}_Handlungssituation_{width}.png'), full_page=True)
        page.goto(base + 'informieren.html'); ready(page); unlock(page, 1, 'informieren')
        # A long open material list occupies most of a narrow screen.  Collapse
        # its real summary control before opening the task, as a learner can.
        chooser = page.locator('details.material-access[open],details.phase-materials[open]')
        if chooser.count():
            chooser.locator(':scope>summary').click()
        page.locator('.task-original-preview:visible').click(); no_overflow(page, 'focus ' + str(width)); pdf_footer(page)
        if width >= 768:
            require(page.locator('.task-accordion[open]').evaluate('e=>Math.abs(e.querySelector(".focus-competence").getBoundingClientRect().y-e.querySelector(".focus-toolbar").getBoundingClientRect().y)<2'), 'competency and clock aligned')
        if root.name == 'LS08' and width == 768:
            page.screenshot(path=str(report_dir / 'LS08_Aufgabenfokus_768.png'), full_page=True)
        for material in materials:
            page.goto(base + material.name)
            page.locator('.material-switch summary').click()
            require(page.locator('.material-switch>nav').evaluate('e=>e.scrollWidth<=e.clientWidth+1'), 'material chooser fits')
            no_overflow(page, material.name + ' ' + str(width))
            readable_numbers(page, material.name + ' ' + str(width))
            if root.name == 'LS08' and width in (390, 768) and (material.name == 'm1.html' or re.search('Betriebsabrechnungsbogen|BAB', lesson['pageTitles'].get(material.name, ''), re.I)):
                page.screenshot(path=str(report_dir / f'LS08_{material.stem}_BAB_{width}.png'), full_page=True)
    page.emulate_media(media='print')
    require(page.evaluate("getComputedStyle(document.body,'::before').display==='none'"), 'no decorative print background')
    require(not errors, errors); context.close()
    return picture_views


def verify_teacher(browser, base, lesson, root, report_dir):
    context = browser.new_context(viewport={'width': 1024, 'height': 768}, accept_downloads=True)
    page = context.new_page(); errors = watch(page, base)
    page.goto(base + 'lehrkraft.html')
    page.locator('#teacher-pin').fill('0000'); page.locator('#teacher-unlock').click()
    require(page.locator('#teacher-panel').is_hidden(), 'wrong PIN rejected')
    page.evaluate("SOZ_CONFIG.pinHash=[...'2468'].reduce((v,c)=>v*31+c.charCodeAt(0),0)")
    page.locator('#teacher-pin').fill('2468'); page.locator('#teacher-unlock').click()
    require(page.locator('[data-allow-mode]').is_visible(), 'teacher controls student choice')
    page.locator('[data-allow-mode]').check()
    require(page.evaluate('SOZ_API.getSettings().allowStudentMode'), 'choice setting saved')
    page.locator('[data-teacher-mode]').select_option('3')
    page.locator('[data-edit-page]').select_option('informieren.html')
    marker = ' Verifikationsbeleg nur im isolierten Testbrowser.'
    page.locator('[data-page-editor] .assignment-body').first.evaluate('(e,t)=>(e.querySelector("p,li")||e).append(document.createTextNode(t))', marker)
    page.locator('[data-save-page]').click()
    with page.expect_download(timeout=120000) as event:
        page.locator('[data-export-ims]').click()
    exported = report_dir / f'{root.name}_Test_Editor_Export.zip'
    event.value.save_as(exported)
    with zipfile.ZipFile(exported) as z:
        require(z.testzip() is None and 'imsmanifest.xml' in z.namelist(), 'valid exported root ZIP')
        data = payload(z.read('lesson-data.js')); cfg = payload(z.read('mode-config.js'))
        require(marker.strip() in data['pages']['informieren.html'], 'edited source exported')
        require(marker.strip() in z.read('informieren.html').decode(), 'edited HTML exported')
        require(cfg['allowStudentMode'] is True and cfg['mode'] == 3, 'teacher selection exported')
        for element in ET.fromstring(z.read('imsmanifest.xml')).iter():
            if element.tag.split('}')[-1] == 'file':
                require(element.attrib['href'] in z.namelist(), 'export manifest entry exists', element.attrib['href'])
        for name in ('runtime.js', 'styles.css', 'teacher.js', 'progress-core.js', 'export.js'):
            require(z.read('assets/' + name) == (root / 'assets' / name).read_bytes(), 'export uses current asset', name)
        for role, slot in json.loads((root / 'media-map.json').read_text())['slots'].items():
            require(z.read(slot['src']) == (root / slot['src']).read_bytes(), role, 'edited export preserves original image bytes')
    page.goto(base + 'informieren.html'); ready(page); unlock(page)
    require(marker.strip() in page.locator('.task-original-preview:visible').text_content(), 'saved edit after navigation')
    page.reload(); ready(page); unlock(page)
    page.locator('.task-original-preview:visible').click()
    require(marker.strip() in page.locator('.task-accordion[open] .assignment-body').text_content(), 'saved edit after reload and in focus')
    require(not errors, errors); context.close()
    # Read the exported configuration through a route; no production files are changed.
    context = browser.new_context()
    context.route('**/mode-config.js', lambda route: route.fulfill(body='window.SOZ_CONFIG=' + json.dumps(cfg) + ';', content_type='application/javascript'))
    page = context.new_page(); page.goto(base + 'index.html')
    require(page.locator('[data-student-mode]').is_visible(), 'student choice enabled by exported config')
    page.locator('[data-student-mode]').select_option('5'); page.reload()
    require(page.locator('[data-student-mode]').input_value() == '5', 'student choice persists')
    context.close()
    exported.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--series', type=Path, default=REPO / 'Reihen/BRC_LG03')
    parser.add_argument('--only', type=int, nargs='+')
    parser.add_argument('--allow-missing-images', action='store_true')
    parser.add_argument('--skip-pdf', action='store_true')
    parser.add_argument('--report-dir', type=Path, default=REPO / 'work/lg03')
    parser.add_argument('--checks', nargs='+', choices=['tasks', 'quiz', 'gates', 'materials', 'layout', 'help', 'teacher', 'scorm'],
                        default=['tasks', 'quiz', 'gates', 'materials', 'layout', 'help', 'teacher', 'scorm'])
    args = parser.parse_args(); args.report_dir.mkdir(parents=True, exist_ok=True)
    roots = [args.series / f'LS{x:02d}' for x in args.only] if args.only else sorted(args.series.glob('LS[0-9][0-9]'))
    require(roots, 'No generated LG03 packages')
    report = {'scope': [p.name for p in roots], 'checks': args.checks, 'draftMissingImagesAllowed': args.allow_missing_images,
              'pdfPayloadChecksSkipped': args.skip_pdf, 'results': [], 'limitations': [
                  'Chromium/API simulation only; native Moodle app, AIS login and native GoodNotes handoff require the real classroom system.']}
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(REPO)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    failed = False
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
            for root in roots:
                base = f'http://127.0.0.1:{server.server_port}/' + root.resolve().relative_to(REPO).as_posix() + '/'
                data, _meta = verify_identity(root, args.skip_pdf, args.allow_missing_images)
                lesson = {**data, 'folder': root.name, 'budgets': [data['phaseBudgets'][x] for x in PHASES]}
                jobs = {
                    'tasks': lambda: verify_tasks(browser, base, lesson, args.skip_pdf),
                    'quiz': lambda: verify_quizzes(browser, base),
                    'gates': lambda: verify_gates(browser, base, lesson),
                    'materials': lambda: verify_materials(browser, base, lesson),
                    'layout': lambda: verify_layout(browser, base, lesson, root, args.report_dir, args.allow_missing_images),
                    'help': lambda: verify_timer_and_help(browser, base, lesson),
                    'teacher': lambda: verify_teacher(browser, base, lesson, root, args.report_dir),
                    'scorm': lambda: verify_scorm(browser, base, lesson),
                }
                for name in args.checks:
                    result = {'lesson': root.name, 'check': name}
                    try:
                        result['count'] = jobs[name](); result['status'] = 'PASS'
                        print('PASS:', root.name, name, flush=True)
                    except Exception as error:
                        result.update(status='FAIL', error=str(error), traceback=traceback.format_exc()); failed = True
                        print('FAIL:', root.name, name, str(error), flush=True)
                    report['results'].append(result)
                    (args.report_dir / 'browser_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
            browser.close()
    finally:
        server.shutdown(); server.server_close()
        (args.report_dir / 'browser_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
