'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function loadExercise(number) {
  const directory = path.join(__dirname, '..', `LS6_${number}`);
  const context = vm.createContext({});
  for (const file of ['data.js', 'engine.js', 'progress.js']) {
    const filename = path.join(directory, file);
    vm.runInContext(fs.readFileSync(filename, 'utf8'), context, { filename });
  }
  return vm.runInContext('({ BANK, Engine, Progress })', context);
}

function checkReserveBank(bank, engine, exercise) {
  assert.equal(bank.length, 78, `${exercise}: Aufgabenbestand`);
  const coreIds = [1, 2, 3].flatMap(level => Array.from(engine.plan(level)));
  assert.deepEqual(coreIds, Array.from({ length: 30 }, (_, id) => id));

  for (const coreId of coreIds.slice(0, 24)) {
    const core = bank[coreId];
    const variants = bank.filter(question => question.coreId === coreId);
    assert.deepEqual(Array.from(variants, question => question.reserveNo), [1, 2],
      `${exercise}: zwei geordnete Reserven zu Kernaufgabe ${coreId + 1}`);
    for (const question of variants) {
      assert.equal(bank[question.id], question);
      assert.equal(question.l, core.l);
      assert.equal(question.c, core.c);
      assert.equal(question.type, 'multi');
      assert.equal(question.options.length, 6);
      assert.equal(new Set(question.options.map(option => option.trim().toLowerCase())).size, 6);
      assert.notEqual(question.ask + question.scene, core.ask + core.scene);
      assert.ok(question.answer.length > 0 && question.answer.length < 6);
      assert.equal(new Set(question.answer).size, question.answer.length);
      assert.ok(question.answer.every(index => Number.isInteger(index) && index >= 0 && index < 6));

      const wrong = question.options.findIndex((_, index) => !question.answer.includes(index));
      assert.equal(engine.grade(question, question.answer), 1);
      assert.equal(engine.grade(question, [wrong]), 0);
    }
    assert.notEqual(variants[0].ask + variants[0].scene, variants[1].ask + variants[1].scene);
  }
}

function checkProgress({ BANK: bank, Engine: engine, Progress: progress }, level, exercise) {
  const label = `${exercise}, Stufe ${level}`;
  const stageIds = Array.from(engine.plan(level));
  assert.equal(stageIds.length, 12);
  let state = engine.initial();
  state.stage = level;

  for (const [index, id] of stageIds.entries()) {
    const question = engine.next(state);
    assert.equal(question.id, id, `${label}: Kernreihenfolge`);
    state.hint = index < 7 ? 0 : 2;
    engine.recordStandard(state, question, index < 7 ? 1 : 0);
  }
  assert.equal(engine.next(state), null);
  assert.equal(engine.stageScore(state, level), 7 / 12);
  assert.equal(engine.stageGate(state, level).pass, false);

  const target = stageIds[7];
  const targetRow = () => Array.from(state.rows.find(row => row[0] === target));
  const checkCoreCount = () => {
    assert.deepEqual(Array.from(state.rows, row => row[0]), stageIds, `${label}: Nachweise`);
    assert.equal(engine.stageRows(state, level).length, 12);
  };

  state.remediation = engine.remediationTargets(state, level);
  assert.deepEqual(Array.from(state.remediation), stageIds.slice(7));
  const first = engine.next(state);
  assert.equal(first.coreId, target);
  assert.equal(first.reserveNo, 1);
  state.hint = 3;
  engine.recordStandard(state, first, 0);
  assert.deepEqual(targetRow(), [target, 0, 2], `${label}: schwächerer Nachweis bleibt unberücksichtigt`);
  assert.equal(engine.next(state).coreId, stageIds[8], `${label}: zum nächsten offenen Lernziel`);
  checkCoreCount();

  // Auch nach Laden eines gespeicherten Lernstands folgt der zweite Stapel.
  state = JSON.parse(JSON.stringify(state));
  state.remediation = engine.remediationTargets(state, level);
  const second = engine.next(state);
  assert.equal(second.coreId, target);
  assert.equal(second.reserveNo, 2);
  assert.notEqual(second.id, first.id);
  state.hint = 1;
  engine.recordStandard(state, second, engine.grade(second, second.answer));

  assert.deepEqual(targetRow(), [target, 1, 1, second.id]);
  assert.equal(engine.stageScore(state, level), 8 / 12);
  assert.equal(engine.stageGate(state, level).pass, true, `${label}: Aufstieg ab 66 %`);
  assert.equal(engine.score(state), 67);
  assert.equal(engine.remediationTargets(state, level).includes(target), false);
  assert.ok(progress.table(state, bank[target].c).includes(progress.escape(second.title)),
    `${label}: die Übersicht zeigt den gewerteten Reservenachweis`);
  checkCoreCount();
}

for (let number = 1; number <= 8; number += 1) {
  const exercise = `LS 6.${number}`;
  try {
    const runtime = loadExercise(number);
    checkReserveBank(runtime.BANK, runtime.Engine, exercise);
    for (const level of [1, 2]) checkProgress(runtime, level, exercise);
    console.log(`${exercise}: 48 Reserven, Wechsel der Stapel und Fortschrittswertung geprüft.`);
  } catch (error) {
    console.error(`Fehler in ${exercise}`);
    throw error;
  }
}
