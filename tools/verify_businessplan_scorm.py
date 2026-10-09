#!/usr/bin/env python3
"""Verify the uploaded business-plan content, all five paths, timing and export."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse, functools, http.server, json, re, subprocess, threading, zipfile
import xml.etree.ElementTree as ET

REPO=Path(__file__).resolve().parents[1]
PHASES=['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren']
TIME_SPAN=r'<span class="assignment-time" data-time-ui=""> \(ca\. \d+ Min\.\)</span>'


def payload(raw):return json.loads(raw.decode().split('=',1)[1].strip().rstrip(';'))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def unlock_phases(page,mode):
    page.evaluate('''mode=>{const m=SOZ_PROGRESS_META,p=SOZ_PROGRESS.read();p.m=mode;for(const q of m.quiz)p.q[q.id]=[q.correct,true];for(const [id,t]of Object.entries(m.tasks))p.t[id]=t.signature;SOZ_PROGRESS.write(p);SOZ_API.setMode(mode);}''',mode)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('folder',type=Path);args=parser.parse_args()
    root=args.folder
    plan=json.loads((REPO/'tools/businessplan_aufgabenzeiten.json').read_text())
    with zipfile.ZipFile(args.source) as source:
        old=payload(source.read('lesson-data.js'));new=payload((root/'lesson-data.js').read_bytes())
        restored=json.loads(json.dumps(new))
        for phase in PHASES:restored['pages'][phase+'.html']=re.sub(TIME_SPAN,'',restored['pages'][phase+'.html'])
        assert restored==old,'Content changed beyond timing spans'
        for name in ['progress-meta.js','mode-config.js','Konfiguration.json','media-map.js','media-map.json','assets/scorm.js','assets/scorm-codec.js']:
            assert source.read(name)==(root/name).read_bytes(),name
        for name in source.namelist():
            if name.startswith('pdf/') or re.search(r'\.(jpg|png|svg|otf)$',name):assert source.read(name)==(root/name).read_bytes(),name
    meta=payload((root/'progress-meta.js').read_bytes());assert len(meta['tasks'])==83
    assert len(re.findall(TIME_SPAN,(root/'lesson-data.js').read_text().replace('\\"','"')))==83
    for phase,budget in plan['phaseBudgets'].items():
        for mode,minutes in plan['minutesByMode'][phase].items():
            assert sum(minutes)==budget
            assert len(minutes)==sum(t['phase']==phase and t['mode']==int(mode) for t in meta['tasks'].values())
    assert sum(plan['phaseBudgets'].values())==810
    for path in root.glob('assets/*.js'):subprocess.run(['node','--check',str(path)],check=True,capture_output=True)
    manifest=ET.fromstring((root/'imsmanifest.xml').read_bytes())
    for node in manifest.iter():
        if node.tag.split('}')[-1]=='file':assert (root/node.attrib['href']).is_file()
    print('PASS: unchanged editorial content/media/PDFs/SCORM IDs, 83 task times, all 30 phase sums, JavaScript and manifest',flush=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
    images=REPO/'Pruefberichte';images.mkdir(exist_ok=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            for mode in range(1,6):
                context=browser.new_context(viewport={'width':1024,'height':768});page=context.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                for phase in PHASES:
                    page.goto(base+phase+'.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'")
                    unlock_phases(page,mode)
                    expected=plan['minutesByMode'][phase][str(mode)]
                    assert page.locator('.task-original-preview:visible').count()==len(expected)
                    assert page.locator('details.material-access,details.phase-materials').count()==1
                    # Recomputing metadata during export must preserve original signatures.
                    assert page.evaluate('''()=>{const d=JSON.parse(JSON.stringify(SOZPAED)),m=SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser());return JSON.stringify(m)===JSON.stringify(SOZ_PROGRESS_META)}''')
                    for i,minutes in enumerate(expected):
                        page.locator('.task-original-preview:visible').nth(i).click()
                        focus=page.locator('.task-accordion[open]');assert focus.count()==1
                        timer=focus.locator('.focus-countdown').inner_text()
                        assert timer in [f'{minutes:02}:00',f'{minutes-1:02}:59'],(phase,mode,i,timer)
                        assert focus.locator('.focus-phase-form').inner_text().strip()
                        assert focus.locator('.ais-chat-logo svg').is_visible()
                        assert focus.locator('.focus-countdown').is_visible()
                        assert focus.evaluate('(e)=>Math.abs(e.querySelector(".focus-competence").getBoundingClientRect().y-e.querySelector(".focus-toolbar").getBoundingClientRect().y)<2')
                        focus.locator('summary').click();assert page.locator('.task-accordion[open]').count()==1
                        checkbox=focus.locator('[data-task-complete]');id=checkbox.get_attribute('data-task-id')
                        # Previously completed task remains checked after time allocation.
                        assert checkbox.is_checked()
                        checkbox.uncheck();assert focus.locator('.focus-next').is_disabled()
                        checkbox.check();assert focus.locator('.focus-next').is_enabled()
                        assert focus.locator('[data-task-complete]').get_attribute('data-task-id')==id,'Unexpected automatic next'
                        bounds=[focus.locator('.focus-task-footer '+s).bounding_box() for s in ['button:first-child','label','button:last-child']]
                        assert bounds[0]['x']<bounds[1]['x']<bounds[2]['x']
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                        focus.locator('.focus-task-footer>button').first.click()
                        card=page.locator(f'.assignment-frame[data-task-id="{id}"]')
                        assert card.locator('.task-done-check').is_visible()
                        assert card.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(243, 248, 231)'
                assert not errors,errors
                print('PASS: path',mode,'all six phases and every task: full content, timer, header, manual next, green completion, layout',flush=True)
                context.close()

            # Incomplete phase locks both normal navigation and direct page access.
            context=browser.new_context();page=context.new_page()
            for mode in range(1,6):
                for index,phase in enumerate(PHASES[:-1]):
                    page.goto(base+phase+'.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'");unlock_phases(page,mode)
                    missing=page.evaluate('''args=>{const [phase,mode]=args,id=Object.entries(SOZ_PROGRESS_META.tasks).find(([id,t])=>t.phase===phase&&t.mode===mode)[0],p=SOZ_PROGRESS.read();delete p.t[id];SOZ_PROGRESS.write(p);return id}''',[phase,mode])
                    nextpage=PHASES[index+1]+'.html'
                    assert page.locator(f'.stations [data-learning-page="{nextpage}"]').get_attribute('aria-disabled')=='true'
                    assert page.locator('.page-turn a').last.get_attribute('aria-disabled')=='true'
                    page.goto(base+nextpage);page.wait_for_function("document.body.dataset.taskFocusReady==='true'")
                    page.evaluate('mode=>SOZ_API.setMode(mode)',mode)
                    assert page.locator('.lesson-content').is_hidden(),(mode,phase,page.evaluate('document.body.dataset.mode'))
                    assert page.locator('[data-phase-gate]').is_visible()
            context.close();print('PASS: 25 phase transitions locked in navigation and direct access',flush=True)

            # Timer colours, pause, end chime and retaining the clock through materials.
            context=browser.new_context(viewport={'width':768,'height':1024});page=context.new_page()
            context.add_init_script('''window.testChimes=0;window.AudioContext=class{constructor(){this.state='running';this.currentTime=0;this.destination={}}createOscillator(){return {frequency:{value:0},connect(){},start(){window.testChimes++},stop(){}}}createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}}}};''')
            page.goto(base+'informieren.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'");unlock_phases(page,1)
            page.evaluate('''()=>{const realNow=Date.now.bind(Date);window.testOffset=0;Date.now=()=>realNow()+window.testOffset;}''')
            page.locator('.task-original-preview:visible').first.click();focus=page.locator('.task-accordion[open]')
            assert focus.locator('.focus-countdown').evaluate('(e)=>getComputedStyle(e).color')=='rgb(175, 202, 11)'
            page.evaluate('testOffset=450000');page.wait_for_function("document.querySelector('.task-accordion[open] .focus-countdown').textContent==='07:30'")
            assert focus.locator('.focus-countdown').evaluate('(e)=>getComputedStyle(e).color')=='rgb(17, 17, 17)'
            focus.locator('.focus-timer-row button').click();paused=focus.locator('.focus-countdown').inner_text()
            page.evaluate('testOffset+=60000');assert focus.locator('.focus-countdown').inner_text()==paused
            focus.locator('.focus-timer-row button').click();page.evaluate('testOffset+=450000')
            page.wait_for_function("document.querySelector('.task-accordion[open] .focus-countdown').textContent==='00:00'")
            assert focus.locator('.focus-countdown').evaluate('(e)=>getComputedStyle(e).color')=='rgb(180, 35, 24)'
            assert focus.locator('.focus-timer-row button').is_hidden()
            assert page.evaluate('testChimes')==6
            focus.locator('.focus-next').click();focus=page.locator('.task-accordion[open]');id=focus.locator('[data-task-complete]').get_attribute('data-task-id')
            focus.locator('.focus-sound input').uncheck();page.evaluate('testOffset+=20000')
            page.wait_for_function("document.querySelector('.task-accordion[open] .focus-countdown').textContent==='34:40'")
            page.locator('.phase-materials a[href="m2.html"],.material-access a[href="m2.html"]').first.click()
            assert page.locator('.navigation').is_hidden()
            assert page.locator('.material-switch:visible').count()==1
            assert page.locator('.material-switch a').count()==10
            assert page.locator('[data-share-workbook]:visible').count()==0
            page.locator('.material-switch a[href="m3.html"]').click();page.locator('.return-task').click()
            page.wait_for_function("document.body.dataset.taskFocusReady==='true'")
            assert page.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id')==id
            value=page.locator('.task-accordion[open] .focus-countdown').inner_text();assert value in ['34:40','34:39'],value
            page.route('https://app.ais-chat.schule/**',lambda route:route.fulfill(body='<html><input aria-label="Frage"></html>',content_type='text/html'))
            page.get_by_role('button',name='AIS.chat KI-Hilfe öffnen').first.click()
            assert page.get_by_text('KI-Hilfe · Löppt-Pilot',exact=True).is_visible()
            page.frame_locator('.ais-help-frame').get_by_label('Frage').fill('Wie gehe ich vor?')
            page.get_by_role('button',name='Schließen',exact=True).click();assert page.locator('.task-accordion[open]').count()==1
            context.close();print('PASS: green/black/red timer, pause/resume, chime, material-only navigation, same-task return with retained time, AIS dialog mock',flush=True)

            # Every material offers the complete action cycle without bypassing gates.
            context=browser.new_context(viewport={'width':768,'height':1024});page=context.new_page()
            for mode in range(1,6):
                for material in range(1,11):
                    page.goto(base+f'm{material}.html');unlock_phases(page,mode)
                    assert page.locator('.material-phase-navigation:visible').count()==1
                    assert page.locator('.material-phase-links a[href]').count()==8
                    assert page.locator('.material-phase-turn a[href]').count()==2
                    assert page.locator('.material-switch:visible').count()==1
                    assert page.locator('[data-share-workbook]:visible').count()==0
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                    page.evaluate('''mode=>{const p=SOZ_PROGRESS.read();const id=Object.entries(SOZ_PROGRESS_META.tasks).find(([id,t])=>t.mode===mode&&t.phase==='informieren')[0];delete p.t[id];SOZ_PROGRESS.write(p);}''',mode)
                    assert page.locator('.material-phase-links [data-learning-page="planen.html"]').get_attribute('aria-disabled')=='true'
                    assert page.locator('.material-phase-turn a').last.get_attribute('aria-disabled')=='true'
                    assert page.locator('.material-phase-turn a').first.get_attribute('href')=='informieren.html'
            page.goto(base+'planen.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'");unlock_phases(page,1)
            page.locator('.task-original-preview:visible').first.click()
            page.goto(base+'m10.html');unlock_phases(page,1)
            assert page.locator('.material-phase-turn a').first.get_attribute('href')=='planen.html'
            assert page.locator('.material-phase-turn a').last.get_attribute('href')=='entscheiden.html'
            page.locator('.material-phase-turn a').last.click();assert page.url.endswith('entscheiden.html')
            page.goto(base+'m1.html');page.locator('.material-phase-links a[href="informieren.html"]').click();assert page.url.endswith('informieren.html')
            context.close();print('PASS: all ten materials in five paths: complete phase navigation, contextual back/next, phase locks and real phase transitions',flush=True)

            # Teacher edit is the actual source used by the accordion and export.
            context=browser.new_context(viewport={'width':1024,'height':768},accept_downloads=True);page=context.new_page()
            page.goto(base+'lehrkraft.html')
            page.locator('#teacher-pin').fill('not-a-pin');page.locator('#teacher-unlock').click();assert page.locator('#teacher-panel').is_hidden()
            page.evaluate("SOZ_CONFIG.pinHash=[...'2468'].reduce((v,c)=>v*31+c.charCodeAt(0),0)")
            page.locator('#teacher-pin').fill('2468');page.locator('#teacher-unlock').click();assert page.locator('#teacher-panel').is_visible()
            page.locator('[data-edit-page]').select_option('informieren.html')
            page.locator('[data-page-editor] .assignment-time').nth(0).evaluate("e=>e.textContent=' (ca. 12 Min.)'")
            page.locator('[data-page-editor] .assignment-time').nth(1).evaluate("e=>e.textContent=' (ca. 38 Min.)'")
            page.locator('[data-save-page]').click()
            # Real download action fetches current UI rather than obsolete embedded data.
            with page.expect_download(timeout=30000) as event:page.locator('[data-export-ims]').click()
            exported=Path('/tmp/BRC_LG01_LS03_Editor_Export.zip');event.value.save_as(exported)
            with zipfile.ZipFile(exported) as archive:
                assert archive.testzip() is None
                assert 'timerState' in archive.read('assets/runtime.js').decode()
                assert '(ca. 12 Min.)' in payload(archive.read('lesson-data.js'))['pages']['informieren.html']
                assert payload(archive.read('progress-meta.js'))==meta
                for node in ET.fromstring(archive.read('imsmanifest.xml')).iter():
                    if node.tag.split('}')[-1]=='file':assert node.attrib['href'] in archive.namelist()
            page.goto(base+'informieren.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'");unlock_phases(page,1)
            page.locator('.task-original-preview:visible').first.click()
            assert page.locator('.task-accordion[open] .focus-countdown').inner_text() in ['12:00','11:59']
            context.close();print('PASS: teacher PIN, timing edit, saved accordion change, actual current SCORM export, stable task signatures',flush=True)

            # Original Moodle reporting remains byte-identical; exercise it through API.
            context=browser.new_context();context.add_init_script('''window.testCMI={'cmi.core.student_id':'test-learner','cmi.core.lesson_mode':'normal','cmi.suspend_data':'','cmi.interactions._count':'0'};window.testCommits=0;window.API={LMSInitialize:()=> 'true',LMSGetValue:k=>testCMI[k]||'',LMSGetLastError:()=> '0',LMSSetValue:(k,v)=>{testCMI[k]=v;return 'true'},LMSCommit:()=>{testCommits++;return 'true'},LMSFinish:()=> 'true'};''')
            page=context.new_page();page.goto(base+'scorm.html');page.wait_for_function("window.SOZ_SCORM?.kind==='moodle'")
            page.evaluate('''()=>{const p=SOZ_SCORM.read();for(const q of SOZ_PROGRESS_META.quiz)p.q[q.id]=[q.correct,true];p.a.assessments[SOZ_PROGRESS_META.competencies[0].id]={after:3,evidence:'Bestehender Kompetenzbeleg'};SOZ_SCORM.update(p);document.querySelector('iframe').src='informieren.html';}''')
            page.wait_for_function("document.querySelector('iframe').contentWindow.document.body?.dataset.taskFocusReady==='true'")
            frame=page.frame_locator('[data-scorm-frame]');frame.locator('.task-original-preview:visible').first.click()
            id=frame.locator('.task-accordion[open] [data-task-complete]').get_attribute('data-task-id');frame.locator('.task-accordion[open] [data-task-complete]').check()
            assert page.evaluate('id=>SOZ_SCORM.read().t[id]===SOZ_PROGRESS_META.tasks[id].signature',id)
            assert page.evaluate("testCMI['cmi.suspend_data'].length>0&&testCommits>0&&Object.values(testCMI).includes('Bestehender Kompetenzbeleg')")
            page.evaluate("document.querySelector('iframe').contentWindow.location.reload()")
            page.wait_for_function("document.querySelector('iframe').contentWindow.document.body?.dataset.taskFocusReady==='true'")
            assert frame.locator(f'[data-task-complete][data-task-id="{id}"]').is_checked()
            assert page.evaluate("testCMI['cmi.core.lesson_status']==='incomplete'")
            context.close();print('PASS: SCORM API commits, existing competency reports, original task IDs and reload',flush=True)

            for width,height in [(1024,768),(768,1024),(390,844)]:
                context=browser.new_context(viewport={'width':width,'height':height});page=context.new_page();page.goto(base+'informieren.html');page.wait_for_function("document.body.dataset.taskFocusReady==='true'");unlock_phases(page,1)
                page.locator('.task-original-preview:visible').first.click()
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                if width==1024:page.screenshot(path=str(images/'BRC_LG01_LS03_Aufgabenfokus.png'),full_page=True)
                page.goto(base+'lehrkraft.html');page.evaluate("SOZ_CONFIG.pinHash=[...'2468'].reduce((v,c)=>v*31+c.charCodeAt(0),0)");page.locator('#teacher-pin').fill('2468');page.locator('#teacher-unlock').click()
                page.locator('[data-export-ims]').scroll_into_view_if_needed();assert page.locator('[data-export-ims]').is_visible()
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                context.close();print('PASS: learner/editor viewport',width,height,flush=True)
            browser.close()
    finally:server.shutdown();server.server_close()
    print('PASS: all package checks complete',flush=True)


if __name__=='__main__':main()
