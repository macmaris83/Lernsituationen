const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const zlib = require('node:zlib');

const root = process.env.LS_TEST_MASTER ? path.resolve(__dirname, '..', process.env.LS_TEST_MASTER) : path.resolve(__dirname, '../Fachbereiche/Geschichte/IdentitaetUndNation/Lernpaket');
const source = file => fs.readFileSync(path.join(root, file), 'utf8');

function session(data = {}, faults = {}) {
  const stored = data;
  const cache = {...stored};
  const calls = {commit: 0, finish: 0, set: 0};
  const listeners = {};
  const context = {
    console, Uint8Array, setTimeout, clearTimeout,
    btoa: text => Buffer.from(text, 'binary').toString('base64'),
    atob: text => Buffer.from(text, 'base64').toString('binary'),
    location: {pathname: '/lesson/scorm.html'},
    document: {body:{dataset:{},classList:{contains:()=>false}},querySelector: () => null, addEventListener() {}},
    localStorage: {getItem: () => null, setItem() {}, removeItem() {}},
    addEventListener(name, handler) {listeners[name] = handler;},
    pako: {
      deflate: text => zlib.deflateSync(text),
      inflate: bytes => zlib.inflateSync(bytes).toString('utf8')
    },
    API: {
      LMSInitialize: () => 'true',
      LMSGetLastError: () => '0',
      LMSGetValue: key => cache[key] ?? ({'cmi.core.student_id': 'learner-1', 'cmi.core.lesson_mode': 'normal', 'cmi.interactions._count': '0'}[key] || ''),
      LMSSetValue(key, value) {calls.set++; cache[key] = value; return 'true';},
      LMSCommit() {
        calls.commit++;
        if (faults.commit) {faults.commit--; return 'false';}
        Object.assign(stored, cache);
        return 'true';
      },
      LMSFinish() {
        calls.finish++;
        if (faults.finish) {faults.finish--; return 'false';}
        Object.assign(stored, cache);
        return 'true';
      }
    }
  };
  context.window = context;
  context.parent = context;
  vm.createContext(context);
  vm.runInContext(source('assets/progress-core.js'), context);
  vm.runInContext(source('progress-meta.js'), context);
  for (const name of ['reference-score-core.js', 'fachbegriffscheck-preserve.js', 'revision185-core.js', 'scorm-diagnostics.js']) {
    if (fs.existsSync(path.join(root, 'assets', name))) vm.runInContext(source('assets/' + name), context);
  }
  context.SOZPAED = {id: context.SOZ_PROGRESS_META.id};
  context.SOZ_CONFIG = {mode: 1};
  vm.runInContext(source('assets/scorm-codec.js'), context);
  vm.runInContext(source('assets/scorm.js'), context);
  return {context, bridge: context.SOZ_SCORM, stored, calls, listeners};
}

function fullState(s) {
  const K = s.context.SOZ_PROGRESS_CORE, M = s.context.SOZ_PROGRESS_META;
  const p = K.initial(M, 1);
  p.o = true;
  for (const id of Object.keys(M.tasks)) K.setTask(p, M, id, true);
  for (const q of M.quiz) {p.q[q.id] = [q.correct, true]; p.qf[q.id] = true;}
  if (M.flashcard) p.fc = {schema: 1, version: 3, id: M.id, signature: M.flashcard.signature, complete: true, started: true, known: M.flashcard.terms, total: M.flashcard.terms, pending: 0, data: {state: {results: Array.from({length: M.flashcard.terms}, () => ({latest: {correct: true}}))}}};
  if (M.orientationVideo) p.ov = {signature:M.orientationVideo.signature,duration:100,ranges:[[0,100]],answers:Object.fromEntries(M.orientationVideo.questions.map(q=>[q.id,q.correct])),attempts:{},ended:true,complete:true};
  assert.equal(K.allComplete(p, M), true);
  assert.equal(K.grading(p, M).points, 100);
  assert.equal(K.grading(p, M).maxPoints, 100);
  return p;
}

// Every learning situation uses one consistent, exactly allocated 100-XP scale.
// This changes no completion gate and introduces no automatic credit for an
// absent term check. Native 100-XP packages retain their 25/15/60 weighting.
{
  const s=session(),K=s.context.SOZ_PROGRESS_CORE,M=s.context.SOZ_PROGRESS_META;
  const round=n=>Math.round(n*100)/100;
  const empty=K.initial(M,1),emptyGrade=K.grading(empty,M);
  assert.equal(emptyGrade.points,0,'a new learner starts at zero XP');
  assert.equal(emptyGrade.maxPoints,100,'every package has a 100-XP maximum');
  assert.equal(K.allComplete(empty,M),false,'an empty 100-XP scale does not unlock completion');
  const taskBudget=M.flashcard?25:62.5,situationBudget=M.flashcard?15:37.5;
  const tasks=Object.keys(M.tasks).filter(id=>M.tasks[id].mode===1);
  assert.equal(round(tasks.reduce((sum,id)=>sum+K.taskPoints(M,id,1),0)),taskBudget,'visible task awards sum exactly to their budget');
  assert.equal(round(M.quiz.reduce((sum,q)=>sum+K.situationValue(empty,M,q.id),0)),situationBudget,'visible situation awards sum exactly to their budget');
  const partial=K.initial(M,1);K.setTask(partial,M,tasks[0],true);
  assert.equal(K.grading(partial,M).points,K.taskPoints(M,tasks[0],1),'one completed task earns only its allocated XP');
  assert.equal(K.allComplete(partial,M),false,'partial XP never bypasses the completion gate');
  const taskOnly=K.initial(M,1);
  for(const id of tasks)K.setTask(taskOnly,M,id,true);
  assert.equal(K.grading(taskOnly,M).points,taskBudget,'task-only progress retains the task category weight');
  assert.equal(K.allComplete(taskOnly,M),false,'tasks alone do not bypass the situation/term checks');
  const situationOnly=K.initial(M,1);
  for(const q of M.quiz){situationOnly.q[q.id]=[q.correct,true];situationOnly.qf[q.id]=true;}
  assert.equal(K.grading(situationOnly,M).points,situationBudget,'situation-only progress retains the situation category weight');
  for(const [i,q] of M.quiz.entries()){
    const penalized=K.clone(situationOnly);penalized.qf[q.id]=false;
    assert.equal(K.situationValue(penalized,M,q.id),round(K.sharePoints(situationBudget,M.quiz.length,i)*0.6),'existing first-attempt penalty remains proportional');
  }
  if(!M.flashcard){
    const sample={...M,tasks:{'0:1:1':{phase:'informieren',mode:1,signature:'sample-a'},'0:1:2':{phase:'informieren',mode:1,signature:'sample-b'}},quiz:[{id:'sample-q1',correct:0},{id:'sample-q2',correct:0}]};
    const half=K.initial(sample,1);K.setTask(half,sample,'0:1:1',true);half.q['sample-q1']=[0,true];half.qf['sample-q1']=true;
    assert.equal(K.grading(half,sample).points,50,'half of both existing categories is exactly 50 of 100 XP');
  }
  const all=fullState(s);
  assert.equal(K.grading(all,M).points,100,'all perfect work earns exactly 100 XP');
  assert.equal(s.bridge.update(partial),true,'partial XP can be saved to SCORM');
  const resumed=session(s.stored),restored=resumed.bridge.read();
  assert.equal(resumed.context.SOZ_PROGRESS_CORE.grading(restored,resumed.context.SOZ_PROGRESS_META).points,K.grading(partial,M).points,'saved progress retains its XP after reopening');
  assert.equal(JSON.stringify(restored.t),JSON.stringify(partial.t),'XP display scaling does not rewrite task signatures');
}

// Grouped assignments migrate only when every original constituent was done.
{
  const s=session(),K=s.context.SOZ_PROGRESS_CORE,M=s.context.SOZ_PROGRESS_META;
  const stages=M.migration?.stages||[];
  const earliest=(entry,before=stages.length)=>{
    for(let i=before-1;i>=0;i--){
      const rule=stages[i].tasks?.[entry.id];
      if(rule?.signature===entry.signature)return rule.from.flatMap(old=>earliest(old,i));
    }
    return [entry];
  };
  for(const [id,rule] of Object.entries(M.migration?.tasks||{})){
    assert.equal(rule.signature,M.tasks[id]?.signature,'migration targets the current assignment signature');
    if(!rule.from?.length)continue;
    const original=K.initial(M,1);
    for(const old of rule.from)original.t[old.id]=old.signature;
    assert.equal(K.sanitize(original,M,1).t[id],rule.signature,'all constituent tasks restore the grouped assignment');
    const earliestMarks=rule.from.flatMap(old=>earliest(old));
    if(stages.length&&earliestMarks.length){
      const historic=K.initial(M,1);
      for(const old of earliestMarks){
        assert.ok(!(old.id in historic.t)||historic.t[old.id]===old.signature,'historical task requirements cannot conflict');
        historic.t[old.id]=old.signature;
      }
      assert.equal(K.sanitize(historic,M,1).t[id],rule.signature,'all historic constituent tasks survive staged migration');
      for(const oldId of Object.keys(historic.t)){
        const partialHistoric=K.clone(historic);delete partialHistoric.t[oldId];
        assert.notEqual(K.sanitize(partialHistoric,M,1).t[id],rule.signature,'a missing historic constituent cannot complete the new group');
      }
    }
    if(rule.from.length>1){
      for(const old of rule.from){
        const incomplete=K.clone(original);delete incomplete.t[old.id];
        assert.notEqual(K.sanitize(incomplete,M,1).t[id],rule.signature,'a missing constituent cannot complete a grouped assignment');
      }
    }
  }
}

// Compact SOZ3 saves encode task marks against a dictionary hash. Keep the
// original dictionary when assignments are grouped, then apply the same AND
// migration after decoding instead of silently discarding the old bitset.
{
  const s=session(),K=s.context.SOZ_PROGRESS_CORE,M=s.context.SOZ_PROGRESS_META;
  for(const dictionary of M.legacyTaskDictionaries||[]){
    const historical=fullState(s);historical.t=Object.fromEntries(Object.entries(dictionary).filter(([,task])=>task.mode===1).map(([id,task])=>[id,task.signature]));
    const encodeHistorical=progress=>{
      s.context.SOZ_PROGRESS_META={...M,tasks:dictionary};
      try{return s.context.SOZ_SCORM_CODEC.encode(progress);}
      finally{s.context.SOZ_PROGRESS_META=M;}
    };
    const encoded=encodeHistorical(historical);
    assert.ok(encoded.startsWith('SOZ3:'),'legacy bitmap fixture uses the original compact save format');
    const reopened=session({'cmi.suspend_data':encoded,'cmi.core.lesson_status':'incomplete'});
    const restored=reopened.bridge.read();
    assert.equal(reopened.context.SOZ_PROGRESS_CORE.allComplete(restored,M),true,'all original bitmap task marks restore grouped completion');
    assert.equal(reopened.context.SOZ_PROGRESS_CORE.grading(restored,M).points,100,'a fully completed original bitmap retains 100 XP');
    for(const [id,rule] of Object.entries(M.migration?.tasks||{})){
      if(rule.from.length<2||!rule.from.every(old=>dictionary[old.id]?.signature===old.signature))continue;
      for(const old of rule.from){
        const partial=K.clone(historical);delete partial.t[old.id];
        const resumed=session({'cmi.suspend_data':encodeHistorical(partial),'cmi.core.lesson_status':'incomplete'});
        assert.notEqual(resumed.bridge.read().t[id],rule.signature,'an incomplete original bitmap never grants the whole group');
        assert.equal(resumed.context.SOZ_PROGRESS_CORE.allComplete(resumed.bridge.read(),M),false,'an incomplete original bitmap cannot finish the package');
      }
    }
  }
}

// Finishing all work only saves progress; the explicit action sets completion.
const first = session();

// W1-only releases retain W1 marks and normalize obsolete path preferences.
// Marks belonging to a deleted path must never satisfy a W1 assignment.
{
  const K=first.context.SOZ_PROGRESS_CORE,M=first.context.SOZ_PROGRESS_META;
  const modes=[...new Set(Object.values(M.tasks).map(t=>t.mode))];
  if(modes.length===1&&modes[0]===1){
    assert.equal(K.initial(M,5).m,1,'initial state rejects a removed learning path');
    const original=fullState(first), foreign=JSON.parse(JSON.stringify(original));
    foreign.m=5;foreign.t={};
    foreign.a.assessments=Object.fromEntries(M.competencies.map(c=>[c.id,{after:3,evidence:'Vorhandener Arbeitsbeleg'}]));
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

assert.equal(first.bridge.update(fullState(first)), true);
if(first.context.SOZ_PROGRESS_META.flashcard){
  assert.equal(first.stored['cmi.core.score.raw'],'100','existing Moodle grade reports the full 100 XP');
  assert.equal(first.stored['cmi.core.score.max'],'100','existing Moodle grade keeps its 100-point maximum');
}else{
  assert.equal(first.stored['cmi.core.score.raw'],undefined,'XP display does not introduce a Moodle grade into completion-only packages');
}
assert.equal(first.stored['cmi.core.lesson_status'], 'incomplete');
assert.equal(first.stored['cmi.core.exit'], 'suspend');
assert.equal(first.bridge.completed, false);
const resume = session(first.stored);
assert.equal(resume.bridge.completed, false);
assert.equal(resume.bridge.complete(), true);
assert.equal(resume.stored['cmi.core.lesson_status'], 'completed');
assert.equal(resume.stored['cmi.core.exit'], '');
assert.equal(resume.calls.finish, 1);
assert.equal(resume.bridge.completed, true);
assert.equal(resume.bridge.readOnly, true);

// A confirmed Moodle completion survives reopening and remains idempotent.
const completed = session(resume.stored);
assert.equal(completed.bridge.completed, true);
assert.equal(completed.bridge.readOnly, true);
assert.match(completed.bridge.message, /in Moodle abgeschlossen/);
assert.equal(completed.bridge.update(completed.bridge.read()), false);
assert.equal(completed.bridge.complete(), true);
assert.equal(completed.calls.set, 0);
assert.equal(completed.calls.finish, 0);

// A stale completion cannot close a changed/incomplete current package.
const staleData = {...resume.stored};
const incomplete = fullState(completed);
delete incomplete.t[Object.keys(incomplete.t)[0]];
staleData['cmi.suspend_data'] = completed.context.SOZ_SCORM_CODEC.encode(incomplete);
const stale = session(staleData);
assert.equal(stale.bridge.completed, false);
assert.equal(stale.bridge.readOnly, false);
assert.equal(stale.bridge.complete(), false);
assert.equal(stale.bridge.update(stale.bridge.read()), true);
assert.equal(stale.stored['cmi.core.lesson_status'], 'incomplete');

// A failed commit never claims success or closes the API; retry succeeds.
const commitFault = {};
const commitCase = session({}, commitFault);
assert.equal(commitCase.bridge.update(fullState(commitCase)), true);
commitFault.commit = 1;
assert.equal(commitCase.bridge.complete(), false);
assert.equal(commitCase.bridge.completed, false);
assert.equal(commitCase.calls.finish, 0);
assert.equal(commitCase.stored['cmi.core.lesson_status'], 'incomplete');
assert.match(commitCase.bridge.message, /Speichern fehlgeschlagen/);
assert.equal(commitCase.bridge.complete(), true);
assert.equal(commitCase.bridge.completed, true);
assert.equal(commitCase.stored['cmi.core.lesson_status'], 'completed');

// A failed finish keeps the confirmed completion through background saves,
// but does not disable the retry action or invent a successful API close.
const finishFault = {};
const finishCase = session({}, finishFault);
assert.equal(finishCase.bridge.update(fullState(finishCase)), true);
finishFault.finish = 1;
assert.equal(finishCase.bridge.complete(), false);
assert.equal(finishCase.bridge.completed, false);
assert.equal(finishCase.bridge.readOnly, false);
assert.equal(finishCase.stored['cmi.core.lesson_status'], 'completed');
assert.match(finishCase.bridge.message, /Abschluss fehlgeschlagen/);
assert.equal(finishCase.bridge.commit(), true);
assert.equal(finishCase.stored['cmi.core.lesson_status'], 'completed');
assert.equal(finishCase.stored['cmi.core.exit'], '');
assert.equal(finishCase.bridge.complete(), true);
assert.equal(finishCase.bridge.completed, true);
assert.equal(finishCase.calls.finish, 2);
assert.equal(finishCase.context.SOZ_PROGRESS_CORE.grading(finishCase.bridge.read(), finishCase.context.SOZ_PROGRESS_META).points, 100);

// Reload can also recover the successful final commit after a finish failure.
const recovered = session(finishCase.stored);
assert.equal(recovered.bridge.completed, true);
assert.equal(recovered.bridge.readOnly, true);

console.log('SCORM regression passed (100 XP, partial roundtrip, task migration, autosave, explicit finish, reopen, stale state, commit/finish failure, retry).');
