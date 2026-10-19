#!/usr/bin/env python3
"""Check editable Moodle previews and protected SCORM resume in real iframes.

Run without roots for two templates and one package from each BioCasa set;
--all includes all six packages from both sets. Explicit package roots override
the defaults. --upgrade-from work/input-v1.4 adds actual old-package fixtures
for the delivery packages, including an already completed orientation.
The LMS is a local, persistent SCORM 1.2 API simulation.
"""
import argparse
import base64
import copy
import functools
import hashlib
import http.server
import json
from pathlib import Path
import threading
import traceback
import zlib

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
CASES = [(mode, payload) for mode in ('normal', 'browse')
         for payload in ('valid', 'foreign', 'schema', 'corrupt')]
CASES += [('browse', 'empty')]
CASES += [('review', payload) for payload in ('valid', 'foreign', 'schema', 'corrupt')]


def js_payload(path):
    source = path.read_text()
    return json.loads(source[source.index('=') + 1:].strip().removesuffix(';'))


def fixture(meta):
    return {'s': 1, 'l': meta['id'], 'm': 1,
            't': {key: task['signature'] for key, task in meta['tasks'].items()},
            'o': False, 'w': meta['orientationSignature'],
            'q': {q['id']: [q['correct'], True] for q in meta['quiz']},
            'v': meta['quizSignature'], 'b': 'index.html',
            'a': {'assessments': {c['id']: {'after': 3, 'evidence': 'Erhaltener Beleg ' + c['id']}
                                  for c in meta['competencies']},
                  'feedback': 'Erhaltenes Fremdfeedback',
                  'nextGoal': 'Erhaltener nächster Lernschritt'}, 'r': 3}


def encode(value):
    return 'SOZ2:' + base64.b64encode(zlib.compress(json.dumps(value, ensure_ascii=False).encode())).decode()


API_INIT = '''options => {
  if (self !== top) return;
  const key = 'scorm-resume-test:' + location.pathname;
  let previous;
  try { previous = JSON.parse(sessionStorage.getItem(key)); } catch {}
  window.testCMI = previous?.values || options.values;
  window.testCalls = previous?.calls || [];
  const record = (type, key, value) => {
    testCalls.push({type, key, value});
    sessionStorage.setItem(keyName, JSON.stringify({values:testCMI, calls:testCalls}));
  };
  const keyName = key;
  window.API = {
    LMSInitialize: () => 'true',
    LMSGetValue: key => { record('get', key); return testCMI[key] || ''; },
    LMSGetLastError: () => '0',
    LMSSetValue: (key, value) => { testCMI[key] = value; record('set', key, value); return 'true'; },
    LMSCommit: () => { record('commit'); return 'true'; },
    LMSFinish: () => { record('finish'); return 'true'; }
  };
}'''


def ready_frame(page):
    page.wait_for_function('document.querySelector("[data-scorm-frame]")?.contentWindow?.SOZ_READY===true')
    return next(frame for frame in page.frames if frame != page.main_frame)


def check(browser, base, root, mode, variant, legacy_meta=None):
    meta = js_payload(root / 'progress-meta.js')
    original = fixture(legacy_meta or meta)
    if variant == 'upgrade':
        assert legacy_meta['id'] == meta['id'], 'Upgrade changed the persistent lesson identity'
        original['o'] = True
    value = copy.deepcopy(original)
    if variant == 'foreign':
        value['l'] = (meta['id'].removeprefix('BRC-') if meta['id'].startswith('BRC-LG01-')
                      else 'BRC-' + meta['id'] if meta['id'].startswith('LG01-') else 'unrelated-lesson')
    if variant == 'schema':
        value['s'] = 2
    if mode == 'review':
        value['o'] = True
    raw = '{invalid JSON' if variant == 'corrupt' else '' if variant == 'empty' else encode(value)
    values = {'cmi.core.student_id': 'resume-test-learner',
              'cmi.core.lesson_mode': mode, 'cmi.suspend_data': raw,
              'cmi.core.lesson_location': 'index.html',
              'cmi.core.lesson_status': 'incomplete', 'cmi.interactions._count': '33',
              'cmi.interactions.3.id': 'preserved-competency-report',
              'cmi.interactions.3.student_response': 'Erhaltener Moodle-Kompetenzbeleg'}
    context = browser.new_context(viewport={'width': 1024, 'height': 768})
    context.add_init_script('(' + API_INIT + ')(' + json.dumps({'values': values}) + ')')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        page.goto(base + 'scorm.html')
        frame = ready_frame(page)
        read = lambda: page.evaluate('SOZ_SCORM.read()')
        checkbox = frame.locator('[data-orientation-complete]')
        assert checkbox.count() == 1, 'Orientation completion control missing'
        if mode == 'browse' or (mode == 'normal' and variant not in ('valid', 'upgrade')):
            recovery = mode == 'normal'
            assert page.evaluate('SOZ_SCORM.kind') == ('recovery' if recovery else 'preview'), 'Wrong isolated working mode'
            assert not page.evaluate('SOZ_SCORM.readOnly'), 'Isolated local progress must remain editable'
            assert checkbox.is_enabled(), 'Orientation checkbox disabled in local working mode'
            if recovery:
                message = page.evaluate('SOZ_SCORM.message')
                assert 'nur auf diesem Gerät' in message and 'neuen Versuch' in message, 'Recovery must explain local-only storage and Moodle action'
            initial = read()
            assert not initial['o'] and not initial['t'] and not initial['q'], 'Preview inherited assessed LMS progress'
            assert not initial['a']['feedback'], 'Preview inherited assessed competency feedback'
            checkbox.check()
            assert read()['o'], 'Orientation click did not update local preview'
            first_task = next(iter(meta['tasks']))
            first_question = meta['quiz'][0]
            first_competency = meta['competencies'][0]['id']
            frame.evaluate('''args => {
              const p = SOZ_PROGRESS.read();
              p.t[args.task] = SOZ_PROGRESS_META.tasks[args.task].signature;
              p.q[args.question.id] = [args.question.correct, true];
              p.a.assessments[args.competency] = {after:2, evidence:'Lokaler Vorschau-Beleg'};
              if (!SOZ_PROGRESS.write(p)) throw Error('Local preview write failed');
            }''', {'task': first_task, 'question': first_question, 'competency': first_competency})
            expected = read()
            page.reload()
            frame = ready_frame(page)
            assert read() == expected, 'Local preview progress lost after SCORM reload'
            assert frame.locator('[data-orientation-complete]').is_checked()
            assert page.evaluate('testCMI') == values, 'Preview changed assessed LMS values'
            calls = page.evaluate('testCalls')
            assert not any(c['type'] in ('set', 'commit') for c in calls), 'Preview wrote to or committed LMS'
            if not recovery:
                assert not any(c['type'] == 'get' and c.get('key') == 'cmi.suspend_data' for c in calls), 'Preview read assessed suspend_data'
            else:
                # Conflict recovery must not expose one learner's local work to
                # a second learner using the same device and package directory.
                def switch_learner(learner):
                    page.evaluate('''learner=>{
                      testCMI['cmi.core.student_id']=learner;
                      sessionStorage.setItem('scorm-resume-test:'+location.pathname,
                        JSON.stringify({values:testCMI,calls:testCalls}));
                    }''', learner)
                    page.reload()
                    ready_frame(page)
                switch_learner('second-test-learner')
                second = read()
                assert not second['o'] and not second['t'] and not second['q'], 'Recovery leaked local progress to another learner'
                switch_learner('resume-test-learner')
                assert read() == expected, 'Recovery lost first learner progress after account switch'
                assert page.evaluate('testCMI') == values, 'Recovery changed original Moodle state'
                assert not page.evaluate('testCalls.some(c=>c.type==="set"||c.type==="commit")'), 'Recovery wrote/committed to Moodle'
        elif mode == 'normal' and variant in ('valid', 'upgrade'):
            assert page.evaluate('SOZ_SCORM.kind') == 'moodle'
            assert not page.evaluate('SOZ_SCORM.readOnly') and checkbox.is_enabled()
            restored = read()
            for key in ('t', 'q', 'a', 'r', 'w', 'v', 'l'):
                assert restored[key] == original[key], 'Saved state not restored: ' + key
            assert restored['o'] == original['o'], 'Saved orientation state not restored'
            if original['o']:
                assert checkbox.is_checked(), 'Upgrade reset an already read orientation'
                checkbox.uncheck()
            checkbox.check()
            assert read()['o'], 'Orientation checkbox did not save in Moodle'
            saved = page.evaluate('SOZ_SCORM_CODEC.decode(testCMI["cmi.suspend_data"])')
            assert saved['o'] and saved['t'] == original['t'] and saved['a'] == original['a']
            assert page.evaluate('testCalls.some(c=>c.type==="commit")'), 'No Moodle commit after orientation click'
            page.reload()
            frame = ready_frame(page)
            assert frame.locator('[data-orientation-complete]').is_checked()
            for key in ('t', 'q', 'a', 'r'):
                assert read()[key] == original[key], 'Saved state lost after reload: ' + key
        else:
            assert page.evaluate('SOZ_SCORM.readOnly'), 'Unsafe/review resume must stay read only'
            assert checkbox.is_disabled(), 'Unsafe/review orientation must not write'
            assert not frame.evaluate('''()=>{const p=SOZ_PROGRESS.read();p.o=!p.o;return SOZ_PROGRESS.write(p);}''')
            page.reload()
            frame = ready_frame(page)
            assert frame.locator('[data-orientation-complete]').is_disabled()
            assert page.evaluate('testCMI') == values, 'Protected LMS values changed'
            assert not page.evaluate('testCalls.some(c=>c.type==="set"||c.type==="commit")'), 'Protected state wrote/committed LMS'
            if mode == 'review' and variant == 'valid':
                for key in ('t', 'q', 'a', 'o', 'r'):
                    assert read()[key] == value[key], 'Review lost saved state: ' + key
        assert not errors, errors
        result = {'status': 'PASS', 'mode': mode, 'payload': variant, 'SCORMIframe': True}
        if variant == 'upgrade':
            result['sourceLessonId'] = legacy_meta['id']
            result['targetLessonId'] = meta['id']
            result['preservedTasks'] = len(original['t'])
            result['preservedQuizAnswers'] = len(original['q'])
            result['preservedCompetencyEvidence'] = len(original['a']['assessments'])
            result['orientationRetained'] = True
            version = root / 'Paketversion.json'
            if version.exists():
                result['targetPackageVersion'] = json.loads(version.read_text())
        return result
    finally:
        context.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('roots', nargs='*', type=Path, help='Package roots, absolute or relative to repository')
    ap.add_argument('--all', action='store_true', help='Test both templates and all 12 BioCasa packages')
    ap.add_argument('--delivery', type=Path, default=REPO / 'work/delivery-v1.5/preview')
    ap.add_argument('--upgrade-from', type=Path, help='Unmodified older packages, containing LS01..LS06/progress-meta.js')
    ap.add_argument('--upgrade-only', action='store_true', help='Only exercise older-package SOZ2 upgrade fixtures')
    ap.add_argument('--report', type=Path, default=REPO / 'work/scorm-resume/Pruefung.json')
    ap.add_argument('--chromium', default='/usr/bin/chromium')
    args = ap.parse_args()
    if args.upgrade_only and not args.upgrade_from:
        ap.error('--upgrade-only requires --upgrade-from')
    args.delivery = (args.delivery if args.delivery.is_absolute() else REPO / args.delivery).resolve()
    if args.upgrade_from:
        args.upgrade_from = (args.upgrade_from if args.upgrade_from.is_absolute() else REPO / args.upgrade_from).resolve()
    roots = [(root if root.is_absolute() else REPO / root).resolve() for root in args.roots]
    if not roots:
        roots = [REPO / 'Vorlagen/Lernsituation_tradiert', REPO / 'Vorlagen/Lernsituation_fuenf_Lernwege']
        numbers = range(1, 7) if args.all else (1,)
        for n in numbers:
            roots += [REPO / f'Fachbereiche/BRC/LG01/LS{n:02}', args.delivery.resolve() / f'LS{n:02}']
    for root in roots:
        root.relative_to(REPO)
        assert (root / 'scorm.html').is_file(), root
    if args.upgrade_only and not any(root.parent == args.delivery for root in roots):
        ap.error('--upgrade-only requires roots from --delivery')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(REPO)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    results = []
    complete = False
    def save():
        failed = sum(result['status'] == 'FAIL' for result in results)
        args.report.write_text(json.dumps({'status': 'FAIL' if failed else 'PASS' if complete else 'RUNNING',
            'complete': complete, 'packages': len({result['package'] for result in results}),
            'cases': len(results), 'failed': failed,
            'limits': 'Chromium browser with actual SCORM iframe/runtime and simulated LMS API; no live Moodle or physical iPad.',
            'results': results}, ensure_ascii=False, indent=2) + '\n')
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=args.chromium, args=['--no-sandbox'])
            for root in roots:
                relative = root.relative_to(REPO).as_posix()
                base = f'http://127.0.0.1:{server.server_port}/{relative}/'
                legacy = None
                if args.upgrade_from and root.parent == args.delivery.resolve():
                    legacy = js_payload(args.upgrade_from.resolve() / root.name / 'progress-meta.js')
                cases = ([] if args.upgrade_only else list(CASES)) + ([('normal', 'upgrade')] if legacy else [])
                for mode, variant in cases:
                    try:
                        result = check(browser, base, root, mode, variant, legacy if variant == 'upgrade' else None)
                    except Exception as error:
                        result = {'status': 'FAIL', 'mode': mode, 'payload': variant,
                                  'error': str(error), 'trace': traceback.format_exc(limit=3)}
                    result['package'] = relative
                    result['runtimeSHA256'] = hashlib.sha256((root / 'assets/scorm.js').read_bytes()).hexdigest()
                    results.append(result)
                    print(result['status'], relative, mode, variant, result.get('error', ''), flush=True)
                    save()
            browser.close()
            complete = True
    finally:
        server.shutdown()
        server.server_close()
    save()
    raise SystemExit(1 if any(result['status'] == 'FAIL' for result in results) else 0)


if __name__ == '__main__':
    main()
