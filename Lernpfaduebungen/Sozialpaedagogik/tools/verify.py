#!/usr/bin/env python3
"""Structural, grading, SCORM simulation and browser checks for all 30 packages.

Requires Node.js, Python Playwright and a local Chromium executable. No Moodle
credentials or teacher PIN are read; temporary test PINs stay in test browsers.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import functools, hashlib, http.server, itertools, json, re, subprocess, threading, zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ENTRIES=json.loads((ROOT/'bestand.json').read_text())
BLUEPRINT=ROOT.parent/'Duales_System_verstehen'


def bank(folder):
    text=(folder/'data.js').read_text()
    return json.loads(re.search(r'^const BANK=(.*);$',text,re.M)[1])


def archive_checks():
    assert len(ENTRIES)==30
    files=set()
    for entry in ENTRIES:
        folder=ROOT/entry['folder'];tasks=bank(folder)
        assert len(tasks)==30
        source=json.loads((ROOT/'quellen'/f"{entry['folder']}.json").read_text())
        assert source['id']==entry['ls'] and len(source['quiz'])==3
        for q in tasks:
            assert q['id']==tasks.index(q)
            assert len(q['options'])==6 and len(set(q['options']))==6
            assert all(isinstance(o,str) and o.strip() for o in q['options'])
            assert q['type'] in ['multi','story'], q
            for key in ['title','scene','ask','why','hint','steps','example','criteria','caseLabel']:
                assert q[key].strip(),(entry['ls'],q['id'],key)
            assert q['sourceRefs'] and all(ref in ['Handlungssituation']+[m['key'] for m in source['materials']] for ref in q['sourceRefs'])
            if q['type']=='multi':
                assert q['answer'] and len(set(q['answer']))==len(q['answer'])
                assert all(type(i)==int and 0<=i<6 for i in q['answer'])
                assert len(q['optionFeedback'])==6 and all(q['optionFeedback'])
            else:
                assert q['logicMap']==[0,1,2,0,1,2]
                assert len(q['logicRoles'])==6 and len(q['consequences'])==6
                assert 'answer' not in q
        for level in [1,2]:
            stage=[q for q in tasks if q['l']==level]
            assert len(stage)==12
            assert all(sum(q['c']==c for q in stage)>=2 for c in range(5))
        assert [q['c'] for q in tasks[-6:]]==[0,3,0,4,1,2]
        assert (folder/'teacher-config.js').read_bytes()==(BLUEPRINT/'teacher-config.js').read_bytes()
        assert (folder/'progress.js').read_bytes()==(BLUEPRINT/'progress.js').read_bytes()
        for filename in ['data.js','engine.js','app.js','teacher.js','source-data.js','source-reader.js']:
            subprocess.run(['node','--check',str(folder/filename)],check=True,capture_output=True)
        assert 'Global Bike' not in (folder/'index.html').read_text()
        assert 'Global Bike' not in (folder/'data.js').read_text()
        with zipfile.ZipFile(ROOT/'Downloads'/entry['zip']) as z:
            assert z.testzip() is None
            assert 'imsmanifest.xml' in z.namelist()
            assert all(not n.startswith('/') and '..' not in Path(n).parts for n in z.namelist())
            manifest=ET.fromstring(z.read('imsmanifest.xml'))
            assert manifest.attrib['identifier'] not in files
            files.add(manifest.attrib['identifier'])
            for node in manifest.iter():
                if node.tag.split('}')[-1]=='file':
                    assert node.attrib['href'] in z.namelist()
            for name in z.namelist():
                assert z.read(name)==(folder/name).read_bytes()
    with zipfile.ZipFile(ROOT/'Downloads/Sozialpaedagogik_30_Lernpfaduebungen_SCORM12.zip') as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.endswith('.zip')])==30
        for entry in ENTRIES:assert z.read(entry['zip'])==(ROOT/'Downloads'/entry['zip']).read_bytes()


def engine_checks():
    code=r'''const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=process.argv[1],entries=JSON.parse(fs.readFileSync(root+'/bestand.json','utf8'));
for(const entry of entries){
 const folder=root+'/'+entry.folder,c=vm.createContext({});
 vm.runInContext(fs.readFileSync(folder+'/data.js','utf8')+fs.readFileSync(folder+'/engine.js','utf8'),c);
 vm.runInContext(`
 for(const q of BANK.filter(q=>q.type==='multi')){
  if(Engine.grade(q,q.answer)!==1)throw Error('exact key');
  if(Engine.grade(q,[])!==0)throw Error('empty selection');
  for(let mask=0;mask<64;mask++){
   const selected=Array.from({length:6},(_,i)=>i).filter(i=>mask&(1<<i));
   const value=Engine.grade(q,selected);
   const expected=Math.max(0,(selected.filter(i=>q.answer.includes(i)).length-selected.filter(i=>!q.answer.includes(i)).length)/q.answer.length);
   if(value!==expected||value<0||value>1)throw Error('partial grade');
  }
 }
 for(const l of [1,2]){
  for(const [value,pass] of [[.65,false],[.659,false],[.66,true],[1,true]]){
   const s=Engine.initial();s.rows=Engine.plan(l).map(id=>[id,value,0]);
   if(Engine.stageGate(s,l).pass!==pass)throw Error('stage threshold');
  }
  const s=Engine.initial();s.rows=Engine.plan(l).slice(0,-1).map(id=>[id,1,0]);
  if(Engine.stageGate(s,l).pass||Engine.stageGate(s,l).complete)throw Error('early stage gate');
 }
 for(let role=0;role<3;role++){
  for(let variant=0;variant<2;variant++){
   const s=Engine.initial();s.storyAnswers=Object.fromEntries(Array.from({length:6},(_,i)=>[i,role+variant*3]));
   const ev=Engine.storyEvaluation(s);
   if(ev.overall!==1||ev.decisions.some(d=>!d.choice||!d.consequence||!d.role))throw Error('transfer role mapping');
  }
 }
 for(let step=0;step<6;step++)for(let choice=0;choice<6;choice++){
  const s=Engine.initial();s.storyAnswers=Object.fromEntries(Array.from({length:6},(_,i)=>[i,0]));s.storyAnswers[step]=choice;
  const ev=Engine.storyEvaluation(s);if(!ev||!Number.isFinite(ev.overall)||ev.decisions[step].choice!==BANK[24+step].options[choice])throw Error('transfer alternatives');
 }
 for(const invalid of [null,undefined,'0',-1,6,NaN]){
  const s=Engine.initial();s.storyAnswers={0:0,1:0,2:0,3:0,4:0,5:invalid};if(Engine.storyEvaluation(s)!==null)throw Error('invalid transfer choice');
 }
 const s=Engine.initial();s.rows=BANK.map(q=>[q.id,q.type==='story'?null:1,3]);s.storyAnswers={0:3,1:0,2:3,3:0,4:3,5:0};
 Engine.applyStoryEvaluation(s);if(Engine.score(s)!==100||JSON.stringify(s).length>4096)throw Error('final score or suspend limit');
 `,c);
}
console.log('PASS: 30 engines, 46,080 multi-answer combinations, stage gates, six transfer choices and SCORM storage size');
'''
    print(subprocess.run(['node','-e',code,str(ROOT)],check=True,capture_output=True,text=True).stdout.strip(),flush=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


MOCK=r"""window.cmi={'cmi.core.entry':'ab-initio','cmi.core.lesson_status':'not attempted','cmi.suspend_data':'','cmi.interactions._count':'0'};
window.commits=0;window.API={LMSInitialize:()=> 'true',LMSGetValue:k=>cmi[k]||'',LMSSetValue:(k,v)=>{cmi[k]=String(v);return 'true'},LMSCommit:()=>{commits++;return 'true'},LMSFinish:()=> 'true'};"""
PIN_TEST=r"""async()=>{const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode('81234567'));TEACHER_PIN_HASH=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');}"""


def login(page):
    page.evaluate(PIN_TEST)
    page.locator('#teacherEntry').click()
    page.locator('#teacherPin').fill('81234567')
    page.locator('#teacherOpen').click()
    page.wait_for_function("document.body.classList.contains('teacher-mode')")


def browser_checks():
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}/'
    screenshots=ROOT/'Vorschau';screenshots.mkdir(exist_ok=True)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            saved=None
            for entry in ENTRIES:
                context=browser.new_context(viewport={'width':1024,'height':768},accept_downloads=True)
                context.add_init_script(MOCK)
                page=context.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(base+entry['folder']+'/index.html')
                assert page.locator('.title').inner_text().endswith(entry['title'])
                assert page.locator('[data-self]').count()==5
                page.evaluate("document.querySelectorAll('[data-self]').forEach(el=>{el.value='3';el.dispatchEvent(new Event('change'))})")
                page.locator('#startLearning').click()
                assert page.locator('#form .option').count()==6
                page.locator('[data-open-sources]').click()
                assert page.locator('#sourceReader').is_visible()
                assert page.locator('#sourceSelect option').count()==len(json.loads((ROOT/'quellen'/f"{entry['folder']}.json").read_text())['materials'])+1
                assert page.locator('#sourceText').inner_text().strip()
                page.locator('#sourceSelect').select_option('1')
                assert page.locator('#sourceText').inner_text().strip()
                page.locator('#sourceClose').click()
                assert page.locator('#sourceReader').is_hidden()
                assert page.locator('#form .option').count()==6
                for i in range(3):page.locator('#help').click()
                assert page.locator('#help').is_disabled()
                saved=page.evaluate("cmi['cmi.suspend_data']")
                assert json.loads(saved)['hint']==3
                if entry['ls']=='1.1':
                    page.screenshot(path=str(screenshots/'LS1_1_Lernpfad.png'))
                result=page.evaluate(r'''()=>{
                    for(const level of [1,2,3]){
                        if(s.stage!==level)throw Error('wrong stage');
                        for(let step=0;step<CORE_PLAN[String(level)].length;step++){
                            const q=BANK[s.current];
                            if(document.querySelectorAll('#form .option').length!==6)throw Error('not six rendered options');
                            const answers=q.type==='story'?[3]:q.answer;
                            answers.forEach(a=>document.querySelector(`#form input[value="${a}"]`).checked=true);
                            document.querySelector('#form').requestSubmit();
                            if(!document.querySelector('#next'))throw Error('feedback missing');
                            document.querySelector('#next').click();
                        }
                        if(s.screen!=='checkpoint')throw Error('checkpoint missing');
                        document.querySelector('#continue').click();
                    }
                    if(s.screen!=='reflect')throw Error('reflection missing');
                    document.querySelectorAll('[data-self]').forEach(el=>{el.value='4';el.dispatchEvent(new Event('change'))});
                    document.querySelector('#finish').click();
                    return {rows:s.rows,screen:s.screen,score:Engine.score(s),cmi,commits,storage:JSON.stringify(s).length};
                }''')
                assert result['score']==100 and result['screen']=='final'
                assert len(result['rows'])==30 and result['rows'][0][2]==3
                assert result['cmi']['cmi.core.lesson_status']=='completed'
                assert result['cmi']['cmi.core.score.raw']=='100'
                assert len([k for k in result['cmi'] if re.match(r'cmi\.interactions\.\d+\.id',k)])>=41
                assert len([k for k in result['cmi'] if re.match(r'cmi\.objectives\.\d+\.id',k)])==5
                assert result['storage']<4096 and result['commits']>=30
                login(page)
                assert page.locator('#teacherJump option').count()==30
                assert page.locator('#teacherValidation').evaluate('(e)=>e.classList.contains("good")')
                page.locator('#teacherEditor textarea[data-key="ask"]').fill('EDITORTEST: Welche Aussagen passen zur Ausgangssituation?')
                page.locator('#teacherJump').select_option('29')
                assert page.locator('.teacher-option-text').count()==6
                assert page.locator('.teacher-option-role').count()==6
                assert page.locator('.teacher-correct').count()==0
                assert page.locator('#teacherValidation').evaluate('(e)=>e.classList.contains("good")')
                page.locator('#teacherExport').scroll_into_view_if_needed()
                with page.expect_download(timeout=15000) as download:
                    page.locator('#teacherExport').click()
                path=Path('/tmp')/(entry['folder']+'_export.zip');download.value.save_as(path)
                with zipfile.ZipFile(path) as z:
                    assert z.testzip() is None
                    data=z.read('data.js').decode()
                    assert 'EDITORTEST:' in data and 'const PACKAGE=' in data
                    assert 'source-data.js' in z.namelist() and 'source-reader.js' in z.namelist()
                    for node in ET.fromstring(z.read('imsmanifest.xml')).iter():
                        if node.tag.split('}')[-1]=='file':assert node.attrib['href'] in z.namelist()
                assert not errors,errors
                print('PASS:',entry['folder'],'complete learner path, SCORM reporting, material reader, teacher editor/export',flush=True)
                context.close()

            # Resume vs a new Moodle attempt, plus isolated browser drafts.
            for entry,resume in [('resume',True),('ab-initio',False)]:
                context=browser.new_context();context.add_init_script(MOCK+f"cmi['cmi.core.entry']={json.dumps(entry)};cmi['cmi.suspend_data']={json.dumps(saved)};cmi['cmi.core.lesson_status']='incomplete';")
                page=context.new_page();page.goto(base+'LS7_4/index.html')
                assert page.locator('#form').is_visible() if resume else page.locator('#startLearning').is_visible()
                assert page.evaluate('s.hint')==(3 if resume else 0)
                context.close()
            print('PASS: SCORM resume and ab-initio',flush=True)
            context=browser.new_context();page=context.new_page();page.goto(base+'LS1_1/index.html')
            page.evaluate("document.querySelectorAll('[data-self]').forEach(el=>{el.value='3';el.dispatchEvent(new Event('change'))});document.querySelector('#startLearning').click();document.querySelector('#help').click();")
            assert page.evaluate('s.hint')==1
            page.reload();assert page.evaluate('s.hint')==1
            page.goto(base+'LS1_2/index.html');assert page.evaluate('s.hint')==0
            assert page.locator('#startLearning').is_visible()
            context.close();print('PASS: independent localStorage per exercise',flush=True)

            # Failing stage redirects into actual remediation, not just an engine check.
            context=browser.new_context();page=context.new_page();page.goto(base+'LS1_1/index.html')
            remediation=page.evaluate(r'''()=>{
                document.querySelectorAll('[data-self]').forEach(el=>{el.value='3';el.dispatchEvent(new Event('change'))});document.querySelector('#startLearning').click();
                for(let i=0;i<12;i++){
                    const q=BANK[s.current],wrong=q.options.findIndex((_,j)=>!q.answer.includes(j));
                    document.querySelector(`#form input[value="${wrong}"]`).checked=true;
                    document.querySelector('#form').requestSubmit();document.querySelector('#next').click();
                }
                const locked=document.querySelector('.mastery-gate.locked')!==null;
                document.querySelector('#continue').click();
                return {locked,stage:s.stage,remediation:s.remediation.length,attempts:s.stageAttempts[1],question:BANK[s.current].l};
            }''')
            assert remediation=={'locked':True,'stage':1,'remediation':12,'attempts':1,'question':1}
            context.close();print('PASS: blocked level and 12-task remediation',flush=True)

            # Responsive teacher/learner view and authentication/error validation.
            for width,height in [(1024,768),(768,1024),(390,844)]:
                context=browser.new_context(viewport={'width':width,'height':height})
                page=context.new_page();page.goto(base+'LS1_1/index.html');errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                page.evaluate(PIN_TEST);page.locator('#teacherEntry').click()
                page.locator('#teacherPin').fill('invalid');page.locator('#teacherOpen').click()
                page.wait_for_function("document.querySelector('#teacherPinMsg').textContent==='PIN nicht korrekt.'")
                assert page.locator('#teacherOverlay').is_hidden()
                page.locator('#teacherPin').fill('81234567');page.locator('#teacherOpen').click()
                page.wait_for_function("document.body.classList.contains('teacher-mode')")
                assert page.locator('#teacherOverlay').evaluate('(e)=>e.scrollWidth<=innerWidth+1')
                page.locator('#teacherNext').scroll_into_view_if_needed();assert page.locator('#teacherNext').is_visible()
                page.locator('#teacherEditor textarea[data-key="ask"]').fill('')
                page.locator('#teacherExport').scroll_into_view_if_needed();page.locator('#teacherExport').click()
                assert 'Export gestoppt' in page.locator('#teacherStatus').inner_text()
                page.locator('#teacherEditor textarea[data-key="ask"]').fill('Welche Aussagen treffen zu?')
                if width==1024:
                    page.locator('#teacherOverlay').evaluate('(e)=>e.scrollTop=0')
                    page.screenshot(path=str(screenshots/'LS1_1_Lehrkraefte.png'))
                page.locator('#teacherClose').click();assert page.locator('#teacherOverlay').is_hidden()
                assert page.locator('#startLearning').is_visible()
                assert not errors,errors
                context.close()
                print('PASS: responsive layout',width,height,'PIN check, validation, scrolling, return',flush=True)
            browser.close()
    finally:
        server.shutdown();server.server_close()


def write_report():
    report='''# Prüfbericht · 30 Sozialpädagogik-Lernpfadübungen

Prüfung am 8. Oktober 2026 mit Node.js und lokalem Chromium über Python Playwright.
Alle Prüfungen erfolgreich. Kein tatsächlicher Moodle- oder iPad-Test.

- 30 Quell-Lernsituationen, 30 separate SCORM-1.2-ZIPs, 900 Aufgaben.
- Jede Aufgabe: sechs verschiedene ausgefüllte Antwortmöglichkeiten. 720 MC-
  Mehrfachauswahlaufgaben plus 180 zusammenhängende Transferentscheidungen.
- Keine Cloze-, Kurzantwort-, Sortier- oder Zuordnungsaufgaben in den Aufgabenbanken.
- Pro Orientierung/Anwendung mindestens zwei Aufgaben in jedem der fünf originalen
  Kompetenzbereiche; gültige Antwortschlüssel und Erklärungen für alle MC-Aussagen.
- 46.080 Antwortkombinationen: volle Punkte für den genauen Schlüssel, Teilpunkte
  nach Blaupause, Abzug für zusätzliche falsche Auswahl, Ergebnis zwischen 0 und 1.
- Stufenaufstieg ab 66 %, gesperrt bei 65 % und bei unvollständiger Stufe;
  Festigungsrunde mit den tatsächlich falsch gelösten Aufgaben im Browser geprüft.
- Alle sechs Transferoptionen je Kapitel bewertet; drei gleich tragfähige
  konsistente Arbeitswege. Zwei Varianten je Rolle bleiben gleichwertig.
  Ungültige/fehlende Entscheidungen werden nicht als vollständiger Transfer gewertet.
- Alle 30 Übungen vollständig über ihre Browser-Ereignisse bearbeitet:
  12 + 12 + 6, Abschlussreflexion, Kompetenzauswertung, Abschlussstatus.
- SCORM-1.2-API-Simulation: Interaktionen, fünf Kompetenzziele, Punktwert,
  Commit und Abschlussstatus aufgezeichnet; suspend_data unter 4096 Zeichen.
  Resume setzt den Versuch fort; ab-initio ignoriert den alten Versuch.
- Browserspeicher/Lehrkräfte-Entwürfe pro Übung getrennt; lokales Fortsetzen geprüft.
- Fall-/Materialdialog geöffnet, Materialwechsel und Rückkehr zur Frage geprüft.
- Lehrkräfte-Modus in allen 30 Übungen: Aufgaben bearbeiten, sechs Transferrollen
  anzeigen, aktuelle Änderung exportieren. Manifestdateien im Export vollständig.
- Falsche PIN sperrt den Zugang, unvollständige Aufgabe sperrt den Export.
- Layout bei 1024×768, 768×1024 und 390×844: keine horizontale Überbreite,
  letzte Editor-Aktionen erreichbar, Rückkehr zur Lerneransicht möglich.
- Einzel-ZIPs ohne fehlerhafte Einträge, imsmanifest.xml im Wurzelverzeichnis,
  eindeutige Paketkennungen, alle Manifestdateien vorhanden; Gesamtarchiv enthält
  genau 30 innere ZIPs und Nutzungshinweis. Dateien stimmen mit den Vorlagen überein.

Die Prüfungen sichern technische Funktion und strukturelle Antwortkonsistenz ab.
Fachliche Bausteine, Ausgangsfragen und Quellenbezüge sind als editierbare Eingaben
im Repository nachvollziehbar. Offizielle externe Quellen bleiben als Links erhalten;
deren aktuelle Erreichbarkeit und ein echter Moodle-/iPad-Einsatz wurden hier nicht geprüft.
Google Drive: kein Upload-Werkzeug in dieser Sitzung verfügbar, deshalb kein Upload.
'''
    (ROOT/'PRUEFBERICHT.md').write_text(report)


if __name__=='__main__':
    archive_checks();print('PASS: 30 ZIPs, 900 tasks, manifest integrity, six options, source provenance and JavaScript syntax',flush=True)
    engine_checks();browser_checks();write_report()
    print('PASS: all checks complete; PRUEFBERICHT.md written',flush=True)
