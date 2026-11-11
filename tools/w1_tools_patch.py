"""Bounded source/test changes for the W1-only conversion (not a content generator)."""
from pathlib import Path
import json
import re

def replace(text, old, new, count=1):
    found=text.count(old)
    if found!=count:raise ValueError(f'Expected {count} occurrence(s), found {found}: {old[:100]}')
    return text.replace(old,new)

CORE_CHECK = r'''
// W1-only releases retain W1 marks and normalize obsolete path preferences.
// Marks belonging to a deleted path must never satisfy a W1 assignment.
{
  const K=first.context.SOZ_PROGRESS_CORE,M=first.context.SOZ_PROGRESS_META;
  const modes=[...new Set(Object.values(M.tasks).map(t=>t.mode))];
  if(modes.length===1&&modes[0]===1){
    assert.equal(K.initial(M,5).m,1,'initial state rejects a removed learning path');
    const original=fullState(first), foreign=JSON.parse(JSON.stringify(original));
    foreign.m=5;foreign.t={};
    for(const [id,t] of Object.entries(M.tasks))foreign.t[id.replace(/:1:/,':5:')]=t.signature;
    foreign.a.feedback='Bestehendes Feedback';foreign.a.nextGoal='Mein Lernziel';
    const restored=K.sanitize(foreign,M,5);
    assert.equal(restored.m,1,'obsolete path normalizes to W1');
    assert.equal(Object.keys(restored.t).length,0,'removed path marks are not reinterpreted');
    assert.equal(K.allComplete(restored,M),false,'obsolete path cannot bypass the gates');
    assert.equal(JSON.stringify(restored.a),JSON.stringify(foreign.a),'competency evidence survives');
    const mixed=JSON.parse(JSON.stringify(foreign));Object.assign(mixed.t,original.t);
    const kept=K.sanitize(mixed,M,5);
    assert.equal(JSON.stringify(kept.t),JSON.stringify(original.t),'all matching W1 signatures survive');
    assert.equal(K.allComplete(kept,M),true,'preserved W1 work still completes');
  }
}
'''

def transform(path, text):
    path=str(path).replace('\\','/')
    if path=='tools/test_form185_browser.cjs':
        text=replace(text,'const paths=Array.from({length:5},(_,i)=>i+1).map(mode=>{','const paths=SOZ_API.availableModes().map(mode=>{')
        text=replace(text,"if(item.id.startsWith('GESCHICHTE-')){","if(item.id!=='VORLAGE-FUENF-LERNWEGE'){")
        text=replace(text,"assert.deepEqual(single,{mode:1,modes:[1],choice:false},item.id+': only the traditional path');", """assert.deepEqual(single,{mode:1,modes:[1],choice:false},item.id+': only the traditional path');
    const inventory=await page.evaluate(()=>({
      modes:[...new Set(Object.values(SOZ_PROGRESS_META.tasks).map(t=>t.mode))],
      phases:SOZ_PROGRESS_CORE.phases.map(phase=>{
        const doc=new DOMParser().parseFromString(SOZPAED.pages[phase+'.html'],'text/html');
        return {phase,panels:[...doc.querySelectorAll('[data-mode-panel]')].map(e=>e.dataset.modePanel)};
      })
    }));
    assert.deepEqual(inventory.modes,[1],item.id+': W1 metadata only');
    for(const phase of inventory.phases)assert.deepEqual(phase.panels,['1'],item.id+': removed path panels '+phase.phase);""")
    elif path=='tools/test_form185.cjs':
        text=replace(text,"assert.equal(current,baseline,p.id+': persistent task, orientation and quiz signatures must stay unchanged');", """if(p.id==='VORLAGE-FUENF-LERNWEGE'){
  assert.equal(current,baseline,p.id+': five-path template remains unchanged');
 }else{
  const parse=source=>JSON.parse(source.slice(source.indexOf('=')+1).trim().replace(/;$/,''));
  const before=parse(baseline),after=parse(current);
  const w1=Object.fromEntries(Object.entries(before.tasks).filter(([,task])=>task.mode===1));
  assert.deepEqual(after.tasks,w1,p.id+': retain every original W1 ID/signature; remove only other paths');
  for(const field of Object.keys(before).filter(key=>!['tasks','migration','resumePages'].includes(key)))
   assert.deepEqual(after[field],before[field],p.id+': preserve '+field);
  for(const [id,rule] of Object.entries(after.migration?.tasks||{})){
   assert.ok(after.tasks[id]?.mode===1,p.id+': no obsolete task migration');
   assert.deepEqual(rule,before.migration?.tasks?.[id],p.id+': preserve valid W1 migration');
  }
 }""")
    elif path=='tools/test_idn_completion.cjs':
        text=replace(text,"const first = session();","const first = session();\n"+CORE_CHECK)
    elif path=='tools/verify_brc_editorial.py':
        text=replace(text,"for heading,body in split_sections(sections[5],3):", "ways=split_sections(sections[5],3)\n        assert len(ways)==1 and ways[0][0].startswith('Lernweg W1'), (number,'Only traditional source required')\n        for heading,body in ways:")
        text=replace(text,'original material text and all five paths/six phase instructions unchanged','original material text and traditional path/six phase instructions unchanged')
    elif path=='tools/build_brc_series.py':
        text=replace(text,'The latest five-path template supplies the application, editor and SCORM code.','The existing BRC template supplies application, editor and SCORM code.\nOnly the traditional path W1 is generated; its content source is authoritative.')
        text=replace(text,"MODES = ['Stark geführt','Begleitet','Teiloffen','Selbstgesteuert mit Checkpoints','Löppt']","MODES = ['Tradiert']")
        text=replace(text,'assert sorted(modes)==[1,2,3,4,5]','assert sorted(modes)==[1]')
        text=text.replace('for mode in range(1,6):','for mode in (1,):').replace('for m in range(1,6)','for m in (1,)')
        text=replace(text,"cfg.update({'mode':1,","cfg.update({'mode':1,'allowStudentMode':False,'learningPaths':{'1':{'label':'Tradiert'}},")
        text=replace(text,"root.mkdir(exist_ok=True);(root/'pdf').mkdir(exist_ok=True)","root.mkdir(exist_ok=True);(root/'pdf').mkdir(exist_ok=True)\n        for obsolete in root.rglob('*'):\n            if obsolete.is_file() and re.search(r'(?:^|[-_/])W[2-5](?=[._/-]|$)',obsolete.relative_to(root).as_posix(),re.I):obsolete.unlink()")
        text=text.replace('30 phase PDFs','6 phase PDFs').replace('default W1 tasks and all source materials; other ways have books.','traditional W1 tasks and all source materials.')
        text=text.replace('Sechs Einzelpakete, jeweils fünf alternative Lernwege.','Sechs Einzelpakete, jeweils ausschließlich tradierter Lernweg W1.')
        text=text.replace('Die Lehrkraft wählt den Lernweg im vorhandenen Lehrkräftemodus und exportiert bei Bedarf das konfigurierte Paket.','Die Lehrkraft bearbeitet bei Bedarf das Paket im vorhandenen Editor.')
        text=replace(text,'    # Browser DOM parsing is the same operation the approved editor uses.',"""    # Reused BRC engine files must be made W1-compatible before metadataFrom.
    # The explicit regeneration command works on existing, registered masters.
    from migrate_traditional_paths import convert_master
    for _,root,_,_ in built:convert_master(REPO,root.relative_to(REPO).as_posix())
    # Browser DOM parsing is the same operation the approved editor uses.""")
        text=replace(text,'                manifest(root,ls)',"                convert_master(REPO,root.relative_to(REPO).as_posix())\n                manifest(root,ls)")
    elif path=='tools/verify_brc_series.py':
        text=text.replace('for mode in range(1, 6):','for mode in (1,):')
        text=replace(text,"== set(range(1, 6))","== {1}")
        text=replace(text,'assert sum(sum(budgets) for budgets in result.values()) == 3600',r"assert sum(sum(budgets) for budgets in result.values()) == sum(int(h)*45 for h in re.findall(r'\*\*Zeitrichtwert:\*\*\s*(\d+) Unterrichtsstunden',text))")
        text=replace(text,"assert task_total == 440, task_total","assert task_total == sum(sum(counts.get('1',0) for counts in payload(lesson_root(series,lesson)/'lesson-data.js').get('sourceTaskCounts',{}).values()) for lesson in lessons), task_total")
        text=text.replace('total 80 UStd.','current source budgets').replace('440 complete task groups','all traditional task groups').replace('legacy all-done migration in all five paths','legacy all-done migration in the traditional path')
    elif path=='Fachbereiche/BRC/LG01/quellen/Reihenplan.md':
        # Delete complete alternative-path sections, stopping at the next H1–H3.
        text=re.sub(r'^### Lernweg W[2-5][^\n]*\n[\s\S]*?(?=^#{1,3} |\Z)','',text,flags=re.M)
        if re.search(r'^### Lernweg W[2-5]',text,re.M):raise ValueError('Alternative source path remains')
    elif path=='Fachbereiche/BRC/LG01/quellen/Arbeitsformen.json':
        data=json.loads(text)
        data={k:v for k,v in data.items() if len(k.split(':'))<4 or k.split(':')[-2]=='1'}
        text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    elif path=='.github/workflows/current-scorm.yml':
        text=replace(text,'      - name: Master und Manifest-Dateien prüfen', '      - name: Nur tradierten Lernweg und unveränderte W1-Inhalte prüfen\n        run: python3 tools/check_traditional_paths.py\n      - name: Master und Manifest-Dateien prüfen')
    return text

if __name__=='__main__':
    import sys
    root=Path(sys.argv[1])
    paths=['tools/test_form185_browser.cjs','tools/test_form185.cjs','tools/test_idn_completion.cjs','tools/verify_brc_editorial.py','tools/build_brc_series.py','tools/verify_brc_series.py','Fachbereiche/BRC/LG01/quellen/Reihenplan.md','Fachbereiche/BRC/LG01/quellen/Arbeitsformen.json','.github/workflows/current-scorm.yml']
    for path in paths:
        file=root/path
        if file.is_file():file.write_text(transform(path,file.read_text()),encoding='utf-8')
