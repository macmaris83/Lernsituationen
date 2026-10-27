/* Native SCORM report data only. The central SCORM writer owns all API calls. */
(() => {
  'use strict';
  const PHASES = ['informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren'];
  const LABELS = ['Informieren', 'Planen', 'Entscheiden', 'Durchführen', 'Bewerten', 'Reflektieren'];
  const clean = value => String(value ?? '').replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim();
  const short = (value, limit = 255) => {const s = clean(value); return s.length > limit ? s.slice(0, limit - 3) + '...' : s;};
  const ascii = value => clean(value).replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue')
    .replace(/Ä/g, 'Ae').replace(/Ö/g, 'Oe').replace(/Ü/g, 'Ue').replace(/ß/g, 'ss')
    .normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^A-Za-z0-9_-]+/g, '_').replace(/^_+|_+$/g, '');
  const score = value => Math.round(Math.max(0, Math.min(100, Number(value) || 0)) * 100) / 100;
  const answer = value => value && typeof value.correct === 'boolean' && typeof value.selected === 'string' ? value : null;
  const certainty = value => value === 'sure' ? 'sicher' : value === 'unsure' ? 'unsicher' : 'nicht erfasst';
  const list = (values, limit = 210) => {
    if (!values.length) return 'keine';
    let out = '';
    for (let i = 0; i < values.length; i++) {
      const next = out + (out ? '; ' : '') + clean(values[i]);
      const tail = i + 1 < values.length ? '; +' + (values.length - i - 1) + ' weitere' : '';
      if (next.length + tail.length > limit) return out ? out + '; +' + (values.length - i) + ' weitere' : short(next, Math.max(12, limit - tail.length)) + tail;
      out = next;
    }
    return out;
  };
  let cachedHTML = null, cachedQuestions = [];
  function questionsFrom(D) {
    const html = D?.pages?.['handlungssituation.html'] || '';
    if (html === cachedHTML) return cachedQuestions;
    cachedHTML = html; cachedQuestions = [];
    try {
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const el = doc.querySelector('[data-situation-quiz] script[type="application/json"]');
      const parsed = el ? JSON.parse(el.textContent) : [];
      if (Array.isArray(parsed)) cachedQuestions = parsed;
    } catch (_) { /* Missing descriptive text never invents an answer. */ }
    return cachedQuestions;
  }
  function build(p, meta, D) {
    p = p || {}; meta = meta || {}; D = D || {};
    const K = window.SOZ_PROGRESS_CORE;
    const prefix = ascii(meta.id || D.id || 'Lernsituation').slice(0, 50);
    const id = (group, key, title, suffix = '') => [prefix, ascii(group), ascii(key).slice(0, 45), ascii(title).slice(0, 75), ascii(suffix)].filter(Boolean).join('_').slice(0, 200);
    const interactions = [], objectives = [], details = [], detailObjectives = [];
    const interaction = (target, key, response, options = {}) => {
      const row = {id: key, type: 'fill-in', response: short(response), result: options.result || 'neutral', weighting: options.weighting || '0'};
      if (options.correctResponse !== undefined) row.correctResponse = short(options.correctResponse);
      if (options.objectiveId) row.objectiveId = options.objectiveId;
      target.push(row);
    };
    const objective = (target, key, points, status) => target.push({id: key, score: score(points), status});
    const payload = questionsFrom(D);
    const qInfos = (meta.quiz || []).map((q, index) => {
      const source = payload.find(item => item.id === q.id) || {};
      const stored = p.v === meta.quizSignature ? p.q?.[q.id] : null;
      const submitted = Array.isArray(stored) && stored[1] === true && (q.options || []).includes(stored[0]);
      const correct = submitted && stored[0] === q.correct;
      const options = source.options || [];
      const chosen = submitted ? options.find(option => option.value === stored[0]) : null;
      const expected = options.find(option => option.value === q.correct);
      const first = p.v === meta.quizSignature ? p.qf?.[q.id] : undefined;
      const count = p.v === meta.quizSignature && Number.isInteger(p.qn?.[q.id]) && p.qn[q.id] >= 0 ? p.qn[q.id] : null;
      const title = source.question || 'Frage ' + (index + 1);
      return {q, index, title, submitted, correct, first, count,
        response: submitted ? chosen?.text || chosen?.label || stored[0] : 'Noch nicht beantwortet',
        correctResponse: expected?.text || expected?.label || q.correct,
        topic: 'Frage ' + (index + 1) + ': ' + title};
    });
    const config = window.RENO_FLASHCARD_CONFIG;
    const terms = config?.id === meta.id && Array.isArray(config.terms) ? config.terms : [];
    let envelope = null;
    const fcValid = !!p.fc && p.fc.id === meta.id && p.fc.schema === 1 && p.fc.version === 3 && p.fc.signature === meta.flashcard?.signature;
    if (fcValid) try {
      const loaded = window.RENO_FLASHCARD_PACKAGE?.load();
      if (loaded?.version === 3 && Array.isArray(loaded.cardIds) && loaded.cardIds.join('|') === terms.map(term => term.id).join('|') &&
          Array.isArray(loaded.state?.results) && loaded.state.results.length === terms.length && Array.isArray(loaded.state.queue)) envelope = loaded;
    } catch (_) { /* Unavailable saved diagnostics stay unattempted, never failed. */ }
    const state = envelope?.state;
    const queue = state?.queue || [];
    function answerText(term, entry, a) {
      if (!a) return 'Noch nicht beantwortet';
      if (a.selectedText) return a.selectedText;
      const selected = entry?.options?.find(option => option[0] === a.selected);
      if (selected) return selected[1];
      if (a.selected === term.id) return term.variants?.[0] || term.explanation || term.term;
      const distractor = term.distractors?.find(option => option.id === a.selected);
      return distractor?.variants?.[0] || a.selected;
    }
    const termInfos = terms.map((term, index) => {
      const result = state?.results[index] || {};
      const history = Array.isArray(result.history) ? result.history.map(answer).filter(Boolean) : [];
      const latest = answer(result.latest);
      const first = answer(result.first) || history[0] || null;
      const latestEntry = latest ? queue.find(entry => entry.uid === latest.uid) : null;
      const firstEntry = first ? queue.find(entry => entry.uid === first.uid) : null;
      const expected = latestEntry?.options?.find(option => option[0] === term.id);
      const pending = state ? queue.filter(entry => entry.i === index && entry.answered !== true).length : 1;
      return {term, index, latest, first, history, pending,
        response: answerText(term, latestEntry, latest), firstResponse: answerText(term, firstEntry, first),
        correctResponse: expected?.[1] || term.variants?.[0] || term.explanation || term.term};
    });
    const wrong = [...qInfos.filter(q => q.submitted && !q.correct).map(q => q.topic), ...termInfos.filter(t => t.latest?.correct === false).map(t => t.term.term)];
    const untested = [...qInfos.filter(q => !q.submitted).map(q => q.topic), ...termInfos.filter(t => !t.latest).map(t => t.term.term)];
    const recovered = [...qInfos.filter(q => q.first === false && q.correct).map(q => q.topic), ...termInfos.filter(t => t.first?.correct === false && t.latest?.correct === true).map(t => t.term.term)];
    const pendingCorrect = termInfos.filter(t => t.latest?.correct === true && t.pending > 0).map(t => t.term.term);
    interaction(interactions, id('00', 'Foerderbedarf', 'Auf_einen_Blick'),
      'Gezielt üben: ' + list(wrong, 105) + '. Noch nicht geprüft: ' + list(untested, 85) + (pendingCorrect.length ? '. Zusätzliche Pflichtkarten: ' + pendingCorrect.length : '.'));
    interaction(interactions, id('00', 'Aktuell_falsch', 'Gezielt_ueben'), wrong.length ? list(wrong, 250) : 'Keine aktuell falsch beantworteten Fragen oder Begriffe.');
    interaction(interactions, id('00', 'Noch_nicht_geprueft', 'Noch_offen'), untested.length ? list(untested, 250) : 'Alle Fragen und Begriffe wurden geprüft.');
    interaction(interactions, id('00', 'Nach_Wiederholung_geloest', 'Erst_falsch_zuletzt_richtig'), recovered.length ? list(recovered, 210) + '. Zuerst falsch, zuletzt richtig beantwortet.' : 'Keine erfassten Erstfehler mit inzwischen richtiger Antwort.');
    interaction(interactions, id('00', 'Pflichtkarten', 'Trotz_richtiger_Antwort_noch_offen'),
      pendingCorrect.length ? list(pendingCorrect, 210) + '. Zugehörige Pflichtkarten noch bearbeiten.' : 'Keine zusätzlichen Pflichtkarten zu zuletzt richtigen Begriffen offen.');
    const totalObjective = id('01', 'Gesamt', 'Lernsituation');
    const hsObjective = id('02', 'Handlungssituation', 'Aktueller_Lernstand');
    const fcObjective = id('03', 'Fachbegriffe', 'Aktueller_Lernstand');
    const learningComplete = !!K?.allComplete(p, meta);
    const gradeProgress = envelope && p.fc ? {...p, fc: {...p.fc, data: envelope}} : p;
    const grading = K?.grading?.(gradeProgress, meta);
    const done = grading?.ready === true;
    interaction(interactions, id('00', 'Bewertung', 'Transparent'), grading ? score(grading.points) + '/100: Bearbeitung ' + score(grading.taskPoints) + '/25; Handlungsfragen ' + score(grading.situationPoints) + '/15; Fachbegriffe ' + score(grading.termPoints) + '/60. Ziel: 75 und alle Phasen. Unsicherheit ohne Abzug. Abgabe/Peerfeedback extern in Moodle.' : 'Punktestand noch nicht verfügbar.');
    objective(objectives, totalObjective, grading?.points ?? 0, done ? 'completed' : 'incomplete');
    const hsCorrect = qInfos.filter(q => q.correct).length;
    const hsStatus = qInfos.length && hsCorrect === qInfos.length ? 'passed' : qInfos.some(q => q.submitted && !q.correct) ? 'failed' : qInfos.some(q => q.submitted) ? 'incomplete' : 'not attempted';
    objective(objectives, hsObjective, qInfos.length ? 100 * hsCorrect / qInfos.length : 0, hsStatus);
    const fcKnown = termInfos.filter(t => t.latest?.correct === true).length;
    const fcComplete = !!state && terms.length > 0 && fcKnown === terms.length && termInfos.every(t => t.pending === 0) && K?.flashcardComplete(p, meta);
    const fcStatus = fcComplete ? 'passed' : termInfos.some(t => t.latest?.correct === false) ? 'failed' : termInfos.some(t => t.latest) ? 'incomplete' : 'not attempted';
    objective(objectives, fcObjective, terms.length ? 100 * fcKnown / terms.length : 0, fcStatus);
    const open = [];
    if (!(p.o && p.w === meta.orientationSignature)) open.push('Orientierung');
    if (hsStatus !== 'passed') open.push('Handlungssituation');
    if (!fcComplete) open.push('Fachbegriffscheck');
    PHASES.forEach((phase, index) => {
      const tasks = Object.entries(meta.tasks || {}).filter(([, task]) => task.phase === phase && task.mode === Number(p.m || 1));
      const marked = tasks.filter(([key, task]) => p.t?.[key] === task.signature).length;
      const finished = tasks.length > 0 && marked === tasks.length;
      const key = id('04_Phase', phase, 'Bearbeitungsstand');
      objective(objectives, key, tasks.length ? 100 * marked / tasks.length : 0, finished ? 'completed' : marked ? 'incomplete' : 'not attempted');
      interaction(interactions, key, LABELS[index] + ': ' + marked + '/' + tasks.length + ' Aufgaben markiert; ' + score(tasks.reduce((n,[k,t])=>n+(p.t?.[k]===t.signature?K.taskPoints(meta,k,p.m):0),0)) + '/' + score(tasks.reduce((n,[k])=>n+K.taskPoints(meta,k,p.m),0)) + ' Bearbeitungspunkte. Kein Nachweis fachlicher Qualität.', {objectiveId: key});
      if (!finished) open.push(LABELS[index]);
    });
    qInfos.forEach(info => {
      const key = id('HS', info.q.id, info.title);
      objective(detailObjectives, key, info.correct ? 100 : 0, info.correct ? 'passed' : info.submitted ? 'failed' : 'not attempted');
      interaction(details, id('HS', info.q.id, info.title, 'Letzte_Antwort'), info.response,
        {result: info.submitted ? info.correct ? 'correct' : 'wrong' : 'neutral', weighting: info.submitted ? '1' : '0', correctResponse: info.correctResponse, objectiveId: key});
      const first = typeof info.first === 'boolean' ? 'Erstversuch: ' + (info.first ? 'richtig' : 'falsch') : info.first === null ? 'Erstversuch nicht erfasst (Altstand); keine Abwertung' : 'Erstversuch noch nicht erfasst';
      const count = info.count === null ? 'Prüfversuche nicht erfasst' : 'Neu erfasste Prüfversuche: ' + info.count;
      interaction(details, id('HS', info.q.id, info.title, 'Erstversuch_und_Verlauf'), first + '. ' + count + '. Hinweis: ' + (p.qh?.[info.q.id] ? 'genutzt' : 'nicht erfasst/genutzt') + '. Punkte: ' + (info.correct ? score(K.situationValue(p,meta,info.q.id)) : '0') + '/' + score(K.situationValue(p,meta,info.q.id)) + '.', {objectiveId: key});
    });
    termInfos.forEach(info => {
      const key = id('FC', info.term.id, info.term.term);
      const correct = info.latest?.correct === true;
      objective(detailObjectives, key, correct ? 100 : 0, !info.latest ? 'not attempted' : !correct ? 'failed' : info.pending ? 'incomplete' : 'passed');
      interaction(details, id('FC', info.term.id, info.term.term, 'Letzte_Antwort'), info.response,
        {result: info.latest ? correct ? 'correct' : 'wrong' : 'neutral', weighting: info.latest ? '1' : '0', correctResponse: info.correctResponse, objectiveId: key});
      const first = info.first ? 'Erstversuch: ' + (info.first.correct ? 'richtig' : 'falsch') + '; ' + certainty(info.first.certainty) + '. Antwort: ' + info.firstResponse : 'Noch nicht beantwortet';
      interaction(details, id('FC', info.term.id, info.term.term, 'Erstversuch'), first, {objectiveId: key});
      const attempts = info.history.length ? String(info.history.length) : info.latest ? 'nicht erfasst' : '0';
      const errors = info.history.length ? String(info.history.filter(a => !a.correct).length) : info.latest ? 'nicht erfasst' : '0';
      interaction(details, id('FC', info.term.id, info.term.term, 'Lernverlauf'),
        'Antwortversuche: ' + attempts + '; Fehler: ' + errors + '; zuletzt: ' + certainty(info.latest?.certainty) + '; offene Pflichtkarten: ' + info.pending + '. SCORM: ' + score(correct?K.sharePoints(60,terms.length,info.index):0) + '/' + score(K.sharePoints(60,terms.length,info.index)) + ' Punkte. Unsicherheit ohne Abzug.', {objectiveId: key});
    });
    interaction(interactions, totalObjective, done ? 'SCORM-Punkteziel erreicht: ' + score(grading?.points ?? 0) + '/100. Alle Arbeitsphasen markiert. ' + (learningComplete ? 'Alle Fachbegriffe und Pflichtkarten erledigt.' : 'Offene Fachbegriffe/Pflichtkarten bleiben Lernziele.') + ' Abgabe und Peerfeedback separat in Moodle.' : 'Aktuell ' + score(grading?.points ?? 0) + '/100; Ziel 75 und alle Arbeitsphasen. Offen: ' + list(open, 145) + '.', {objectiveId: totalObjective});
    return {interactions: interactions.concat(details), objectives: objectives.concat(detailObjectives)};
  }
  window.SOZ_SCORM_DIAGNOSTICS = {build};
})();
