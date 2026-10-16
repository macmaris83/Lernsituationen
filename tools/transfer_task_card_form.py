#!/usr/bin/env python3
"""Apply current GitHub task-card metadata to the supplied, unchanged tasks.

The UI comes from the catalogue master. Existing instruction wording, progress
identities, signatures, materials and original workbooks stay with the supplied
package. Phase budgets are clearly labelled as phase budgets, not task timers.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
from lxml import html

from transfer_scorm_design import archive, content_of, manifest, payload, read_archive, sha
from individualize_scorm_tasks import PHASES
from task_card_workforms import apply_task_workforms

ROOT = Path(__file__).resolve().parents[1]
CARD = './/*[contains(concat(" ",normalize-space(@class)," ")," assignment-frame ")]'
BODY = './*[contains(concat(" ",normalize-space(@class)," ")," assignment-body ")]'
TIME_UI = './/*[contains(concat(" ",normalize-space(@class)," ")," assignment-time ")][@data-time-ui]'


def fragment(source):
    return html.fragment_fromstring(source, create_parent='div')


def body_text(body):
    body = copy.deepcopy(body)
    for node in body.xpath(TIME_UI):
        node.getparent().remove(node)
    return re.sub(r'\s+', ' ', body.text_content()).strip()


def phase_budgets(data):
    """Repeat the supplied budget as removable UI, without allocating new times."""
    count = 0
    for phase in PHASES:
        page = phase + '.html'
        if page not in data.get('pages', {}):
            continue
        before_count = count
        doc = fragment(data['pages'][page])
        for panel in doc.xpath('.//*[@data-mode-panel]'):
            source = panel.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," phase-meta ")]/p[1]')
            if not source:
                continue
            value = re.sub(r'^Arbeitszeit:\s*', '', source[0].text_content().strip())
            if not value:
                continue
            icon = source[0].xpath('.//svg')
            for card in panel.xpath(CARD):
                body = card.xpath(BODY)[0]
                if body.xpath(TIME_UI):
                    continue
                label = html.Element('span', {'class': 'assignment-time', 'data-time-ui': 'true',
                    'data-phase-budget': 'true', 'data-phase-budget-value': value,
                    'title': 'Arbeitszeit für die gesamte Phase'})
                if icon:
                    label.append(copy.deepcopy(icon[0]))
                text = html.Element('span')
                text.text = 'Arbeitszeit der Phase: ' + value
                label.append(text)
                body.append(label)
                count += 1
        if count > before_count:
            data['pages'][page] = ''.join(html.tostring(child, encoding='unicode') for child in doc)
    return count


FOCUS_PHASE_BUDGET = r'''
 const phaseBudget=body.querySelector('.assignment-time[data-phase-budget]');
 if(!seconds&&phaseBudget){const timer=element('div','focus-timer focus-phase-budget'),row=element('div','focus-timer-row'),icon=element('span','focus-clock');icon.innerHTML=clockSvg;const value=element('span','focus-phase-budget-value',phaseBudget.dataset.phaseBudgetValue);row.append(icon,value);timer.append(element('p','focus-timer-note','Arbeitszeit der Phase'),row,element('p','focus-timer-note','Gemeinsames Zeitbudget für die Aufgaben dieser Phase.'));tools.append(timer);}
'''

REFRESH_PHASE_BUDGET = r'''
 const budgetUI=body.querySelector('.assignment-time[data-phase-budget]'),currentPhaseTime=card.closest('[data-mode-panel]')?.querySelector('.phase-meta p:first-child');if(budgetUI&&currentPhaseTime){const value=currentPhaseTime.textContent.trim().replace(/^Arbeitszeit:\s*/,'');budgetUI.dataset.phaseBudgetValue=value;const label=budgetUI.querySelector('span');if(label)label.textContent='Arbeitszeit der Phase: '+value;}
'''

TASK_FORM_CSS = '''/* Same task-card and focus styles as the current catalogue master. */
.focus-phase-budget-value{min-width:0;font-size:.9rem;line-height:1.4;text-align:right;color:#173a63}
.focus-phase-budget .focus-timer-row{align-items:center}
'''


def patch_runtime(root):
    path = root / 'assets/runtime.js'
    source = path.read_text()
    old = "const originalTime=card.querySelector('.assignment-time');"
    new = "const originalTime=card.querySelector('.assignment-time:not([data-phase-budget])');"
    assert source.count(old) == 1, 'Unexpected task runtime; inspect current master first.'
    source = source.replace(old, REFRESH_PHASE_BUDGET + new)
    target = ' for(const paragraph of [...body.querySelectorAll(\'p\')])'
    assert source.count(target) == 1
    source = source.replace(target, FOCUS_PHASE_BUDGET + target)
    path.write_text(source)
    (root / 'assets/task-form.css').write_text(TASK_FORM_CSS)
    for path in root.glob('*.html'):
        markup = path.read_text()
        if '<div class="lesson-content">' in markup:
            path.write_text(markup.replace('</head>', '<link rel="stylesheet" href="assets/task-form.css"></head>'))


def validate_unchanged(before, after, meta):
    assert set(before['pages']) == set(after['pages'])
    for key, value in before.items():
        if key != 'pages':
            assert after[key] == value, key
    for page, markup in before['pages'].items():
        if page.replace('.html', '') not in PHASES:
            assert after['pages'][page] == markup, page
            continue
        a, b = fragment(markup), fragment(after['pages'][page])
        old = {card.get('data-task-id'): card for card in a.xpath(CARD)}
        new = {card.get('data-task-id'): card for card in b.xpath(CARD)}
        assert old.keys() == new.keys(), page
        for task, card in old.items():
            updated = new[task]
            assert body_text(card.xpath(BODY)[0]) == body_text(updated.xpath(BODY)[0]), task
            for attribute in ['data-task-id', 'data-task-number', 'data-task-signature', 'data-task-stable-id', 'data-source-task']:
                assert card.get(attribute) == updated.get(attribute), (task, attribute)
            assert updated.get('data-task-signature') == meta['tasks'][task]['signature'], task
            assert len(updated.xpath('./span[contains(concat(" ",normalize-space(@class)," ")," assignment-social ")]')) == 1, task


def transfer(raw, root, canonical):
    files = read_archive(raw)
    for name, content in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    before = payload(files['lesson-data.js'])
    data = copy.deepcopy(before)
    report = apply_task_workforms(data, canonical)
    report['phaseBudgets'] = phase_budgets(data)
    validate_unchanged(before, data, payload(files['progress-meta.js']))
    (root / 'lesson-data.js').write_text('window.SOZPAED=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    for phase in PHASES:
        page = phase + '.html'
        source = (root / page).read_text()
        start = source.index('<div class="lesson-content">') + len('<div class="lesson-content">')
        end = source.index('</div></main>', start)
        (root / page).write_text(source[:start] + data['pages'][page] + source[end:])
    patch_runtime(root)
    manifest(root, files['imsmanifest.xml'])
    assert (root / 'progress-meta.js').read_bytes() == files['progress-meta.js']
    for name, content in files.items():
        if name.startswith('pdf/') or name in ['mode-config.js', 'media-map.js', 'media-map.json', 'Konfiguration.json']:
            assert (root / name).read_bytes() == content, name
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--version', default='1.3')
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve().is_relative_to(ROOT):
        parser.error('Choose a new output folder outside the repository.')
    if not re.fullmatch(r'\d+\.\d+', args.version):
        parser.error('Use a two-part display version.')
    args.output.mkdir(parents=True)
    catalog = json.loads((ROOT / 'master-katalog.json').read_text())
    entries = read_archive(args.source.read_bytes())
    reports, combined = [], {}
    for name, raw in entries.items():
        if not name.endswith('.zip'):
            continue
        ls = re.search(r'LS\d{2}', name)[0]
        item = next(x for x in catalog['packages'] if x['id'] == 'BRC-LG01-' + ls)
        master = ROOT / item['master']
        canonical = payload((master / 'lesson-data.js').read_bytes())
        root = args.output / 'preview' / ls
        report = transfer(raw, root, canonical)
        for css in ['styles.css', 'phases.css', 'lg01.css']:
            assert (root / 'assets' / css).read_bytes() == (master / 'assets' / css).read_bytes(), css
        target = re.sub(r'_v\d+\.\d+_', '_v' + args.version + '_', name)
        archive(args.output / target, {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()})
        combined[target] = (args.output / target).read_bytes()
        report.update(lesson=ls, sourceSha256=sha(raw), archiveSha256=sha(combined[target]))
        reports.append(report)
        print(ls, json.dumps({k:v for k,v in report.items() if not isinstance(v,list)}, ensure_ascii=False), flush=True)
    if not reports:
        raise ValueError('No learning packages found.')
    report = {'packageVersion': args.version, 'designCommit': subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT, text=True).strip(), 'packages': reports}
    report_bytes = (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode()
    (args.output / 'Aufgabenform_Pruefung.json').write_bytes(report_bytes)
    combined['Aufgabenform_Pruefung.json'] = report_bytes
    if 'Bitte_zuerst_lesen.txt' in entries:
        combined['Bitte_zuerst_lesen.txt'] = entries['Bitte_zuerst_lesen.txt'].replace(b'Lernpakete 1.2', ('Lernpakete ' + args.version).encode())
    archive(args.output / ('BioCasa_LG01_Moodle_Lernpakete_v' + args.version + '.zip'), combined)


if __name__ == '__main__':
    main()
