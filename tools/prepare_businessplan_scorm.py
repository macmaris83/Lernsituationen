#!/usr/bin/env python3
"""Apply the approved LS UI to an uploaded business-plan SCORM, preserving content.

Usage: python tools/prepare_businessplan_scorm.py SOURCE.zip OUTPUT_DIRECTORY
Only approved technical files, cache query strings and requested task times change.
Task wording, signatures, configuration, source media and PDFs stay unchanged.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, zipfile
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / 'Lernsituation_fuenf_Lernwege'
TECHNICAL = ['assets/runtime.js', 'assets/styles.css', 'assets/progress-core.js',
             'assets/progress.js', 'assets/teacher.js', 'assets/export.js']


def replace_once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new)


def businessplan_timer(runtime):
    """Use each task's assigned time and retain it through material round trips."""
    marker = 'function draw(r){'
    helpers = r"""function timerState(total,key){const base={total,remaining:total,running:false,deadline:0,key};try{const saved=JSON.parse(sessionStorage.getItem(key)||'null');if(saved&&saved.total===total&&Number.isInteger(saved.remaining)&&saved.remaining>=0&&saved.remaining<=total)base.remaining=saved.remaining;}catch{}return base;}
function saveClock(t){try{sessionStorage.setItem(t.key,JSON.stringify({total:t.total,remaining:t.remaining}));}catch{}}
"""
    runtime = replace_once(runtime, marker, helpers + marker)
    runtime = replace_once(runtime,
        'if(previous>0)chime(r);}draw(r);}',
        'if(previous>0)chime(r);}if(previous!==t.remaining)saveClock(t);draw(r);}')
    runtime = replace_once(runtime,
        'tick(r);t.running=false;draw(r);}',
        'tick(r);t.running=false;saveClock(t);draw(r);}')
    runtime = replace_once(runtime,
        'close(false);active=r;r.details.open=true;',
        'close(false);active=r;refresh(r);r.details.open=true;')
    runtime = replace_once(runtime,
        'if(seconds){timers.set(card,{total:seconds,remaining:seconds,running:false,deadline:0});',
        "if(seconds){const key='task-focus-clock:'+D.id+':'+location.pathname.replace(/[^/]+$/,'')+':'+card.dataset.taskId;timers.set(card,timerState(seconds,key));")
    # Display the working form using its unchanged wording from the upload.
    runtime = replace_once(runtime,
        'summary.append(strip);',
        r"const phaseForm=card.closest('[data-mode-panel]')?.querySelectorAll('.phase-meta p')[1];if(phaseForm&&!card.querySelector('.assignment-social')){const form=element('span','focus-phase-form');const icon=phaseForm.querySelector('svg');if(icon)form.append(icon.cloneNode(true));const formText=phaseForm.querySelector('span')?.textContent.replace(/^Arbeitsform:\s*/,'').trim();if(formText)form.append(element('span','',formText));strip.append(form);}summary.append(strip);")
    return runtime + MATERIAL_PHASE_NAV


MATERIAL_PHASE_NAV = r"""
/* Material access to the complete action cycle; retain the same-task shortcut. */
(()=>{
const D=window.SOZPAED;if(!D||!/^m\d+\.html$/.test(document.body.dataset.page||''))return;
const main=document.querySelector('.main');if(!main)return;
const phases=[['index.html','Orientierung'],['handlungssituation.html','Handlungssituation'],['informieren.html','Informieren'],['planen.html','Planen'],['entscheiden.html','Entscheiden'],['durchfuehren.html','Durchführen'],['bewerten.html','Bewerten'],['reflektieren.html','Reflektieren']];
let saved;try{saved=JSON.parse(sessionStorage.getItem('task-focus-return:'+D.id)||'null');}catch{}
const origin=phases.findIndex(([name])=>name===saved?.page),current=origin>=0?origin:2;
const nav=document.createElement('nav');nav.className='material-phase-navigation';nav.setAttribute('aria-label','Vollständige Handlung');
const heading=document.createElement('strong');heading.textContent='Phasenübersicht';nav.append(heading);
const links=document.createElement('div');links.className='material-phase-links';
function link(index,label){const a=document.createElement('a');a.className='button';a.href=phases[index][0];a.dataset.learningPage=phases[index][0];a.textContent=label||phases[index][1];return a;}
phases.forEach((phase,index)=>links.append(link(index)));nav.append(links);
main.querySelector('.material-switch')?.after(nav);
const turn=document.createElement('nav');turn.className='material-phase-turn';turn.setAttribute('aria-label','Zurück oder weiter in der vollständigen Handlung');
turn.append(link(current,'← Zurück · '+phases[current][1]));
if(current<phases.length-1)turn.append(link(current+1,'Weiter · '+phases[current+1][1]+' →'));
main.append(turn);window.SOZ_PROGRESS?.render();
})();
"""


EXTRA_CSS = """
/* The original working form in business-plan task focus. */
.focus-phase-form{display:none;align-items:center;gap:7px;max-width:min(600px,100%);color:#446477;font-size:.74rem;font-weight:500;line-height:1.4}
.task-accordion[open] .focus-phase-form{display:flex}
.focus-phase-form svg{width:24px;height:24px;flex:0 0 24px;color:#618500}
.task-accordion[open] .focus-symbol-strip{min-width:0;max-width:100%}
.material-phase-navigation{border:1px solid #b8dfee;background:#eef8fd;border-radius:12px;padding:10px 12px;margin-bottom:14px}
.material-phase-navigation>strong{display:block;font-size:.8rem;color:#173a63;margin-bottom:7px}
.material-phase-links{display:flex;gap:6px;overflow-x:auto}
.material-phase-links .button{flex:none;white-space:nowrap;font-size:.8rem;padding:7px 10px}
.material-phase-turn{display:flex;justify-content:space-between;gap:12px;margin:20px 0;flex-wrap:wrap}
.material-phase-turn .button{background:#eaf7fd;border-color:#009bd9;color:#006a98}
@media print{.material-phase-navigation,.material-phase-turn{display:none}}
"""


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source_zip',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.source_zip) as archive:
        for name in archive.namelist():
            if name.startswith('/') or '..' in Path(name).parts:raise ValueError(name)
            if name.endswith('/'):continue
            path=args.output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(archive.read(name))
    for name in TECHNICAL:shutil.copyfile(TEMPLATE/name,args.output/name)
    progress=args.output/'assets/progress.js'
    progress.write_text(replace_once(progress.read_text(),
        ' renderAccess(p,mode);\n}',
        ' renderAccess(p,mode);window.SOZ_TASK_FOCUS?.refresh();\n}'))
    # Timing is the user's explicit exception to keeping editorial content 1:1.
    # Include it as a tagged UI span, so a time-only change cannot invalidate
    # previously completed task signatures or Moodle competency evidence.
    plan=json.loads((REPO/'tools/businessplan_aufgabenzeiten.json').read_text())
    data_path=args.output/'lesson-data.js'
    original_data=json.loads(data_path.read_text().split('=',1)[1].strip().rstrip(';'))
    data=json.loads(json.dumps(original_data))
    time_pattern=r'<span class="assignment-time" data-time-ui=""> \(ca\. \d+ Min\.\)</span>'
    for phase,budget in plan['phaseBudgets'].items():
        for mode,minutes in plan['minutesByMode'][phase].items():assert sum(minutes)==budget
        def add_time(match):
            card=match[0];task=re.search(r'data-task-id="([^\"]+)"',card)[1]
            _,mode,number=task.split(':')
            minutes=plan['minutesByMode'][phase][mode][int(number)-1]
            assert minutes>0
            body_start=card.index('<div class="assignment-body">')
            close=card.index('</p>',body_start)
            return card[:close]+f'<span class="assignment-time" data-time-ui=""> (ca. {minutes} Min.)</span>'+card[close:]
        name=phase+'.html'
        data['pages'][name]=re.sub(r'<article class="assignment-frame".*?</article>',add_time,original_data['pages'][name],flags=re.S)
        assert re.sub(time_pattern,'',data['pages'][name])==original_data['pages'][name]
        page=args.output/name
        raw=page.read_text();assert original_data['pages'][name] in raw
        page.write_text(raw.replace(original_data['pages'][name],data['pages'][name],1))
    data_path.write_text('window.SOZPAED='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
    core=args.output/'assets/progress-core.js'
    core.write_text(replace_once(core.read_text(),
        "const text=e=>(e.textContent||'').replace(/\\s+/g,' ').trim();",
        "const text=e=>{const copy=e.cloneNode(true);copy.querySelectorAll('.assignment-time[data-time-ui]').forEach(t=>t.remove());return (copy.textContent||'').replace(/\\s+/g,' ').trim();};"))
    runtime=args.output/'assets/runtime.js'
    runtime.write_text(businessplan_timer(runtime.read_text()))
    css=args.output/'assets/styles.css';css.write_text(css.read_text()+EXTRA_CSS)
    # HTML comes from the upload; only technical cache-busting and the current
    # local ZIP export input are adopted from the approved template.
    for path in args.output.glob('*.html'):
        text=path.read_text()
        text=re.sub(r'((?:assets/(?:runtime\.js|styles\.css|teacher\.js|progress-core\.js|progress\.js))|lesson-data\.js)(?:\?[^"\s]*)?',r'\1?v=businessplan-ui-20261009-materialnav',text)
        if path.name=='lehrkraft.html':
            ref=(TEMPLATE/path.name).read_text()
            field=re.search(r'<label[^>]*>[^<]*<input[^>]*data-source-package[^>]*>.*?</label>',ref,re.S)
            if field and 'data-source-package' not in text:
                text=text.replace('<p data-teacher-status',field[0]+'<p data-teacher-status')
            # The current template uses a direct label. Preserve its exact text.
            if 'data-source-package' not in text:
                source_field=re.search(r'<label>SCORM-ZIP.*?</label>',ref,re.S)
                if source_field:text=text.replace('<p data-teacher-status',source_field[0]+'<p data-teacher-status')
            if 'data-source-package' not in text:
                field='<label>SCORM-ZIP für lokalen Export<input type="file" data-source-package="" accept=".zip,application/zip"></label>'
                text=text.replace('<p data-teacher-status',field+'<p data-teacher-status')
        path.write_text(text)
    # No new dependencies or learning IDs: the original manifest stays intact.
    manifest=ET.fromstring((args.output/'imsmanifest.xml').read_bytes())
    for node in manifest.iter():
        if node.tag.split('}')[-1]=='file':assert (args.output/node.attrib['href']).is_file()
    editorial=['progress-meta.js','mode-config.js','Konfiguration.json','media-map.js','media-map.json']
    with zipfile.ZipFile(args.source_zip) as source:
        for name in source.namelist():
            if name in editorial or name.startswith('pdf/') or (name.startswith('assets/') and name not in TECHNICAL):
                assert source.read(name)==(args.output/name).read_bytes(),name
    print('Prepared:',args.output)
    print('Only requested task times change in lesson data; wording, signatures, configuration, PDFs and media are preserved.')


if __name__=='__main__':main()
