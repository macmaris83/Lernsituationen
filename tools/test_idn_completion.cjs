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
  assert.equal(K.grading(p, M).points, M.flashcard ? 100 : 40);
  return p;
}

// Finishing all work only saves progress; the explicit action sets completion.
const first = session();
assert.equal(first.bridge.update(fullState(first)), true);
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
assert.equal(finishCase.context.SOZ_PROGRESS_CORE.grading(finishCase.bridge.read(), finishCase.context.SOZ_PROGRESS_META).points, finishCase.context.SOZ_PROGRESS_META.flashcard ? 100 : 40);

// Reload can also recover the successful final commit after a finish failure.
const recovered = session(finishCase.stored);
assert.equal(recovered.bridge.completed, true);
assert.equal(recovered.bridge.readOnly, true);

console.log('SCORM completion regression passed (autosave, explicit finish, reopen, stale state, commit failure, finish failure, retry, unchanged XP).');
