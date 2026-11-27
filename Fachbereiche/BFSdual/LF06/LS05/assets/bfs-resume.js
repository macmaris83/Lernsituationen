/* Compatible with the shared SCORM master's SOZ2 (Base64/zlib/UTF-8 JSON) codec. */
(() => {
  'use strict';
  const object = v => v !== null && typeof v === 'object' && !Array.isArray(v);
  const own = (v,k) => Object.prototype.hasOwnProperty.call(v,k);
  const message = {
    foreign: 'Der gespeicherte Versuch gehört zu einem anderen Lernpaket.',
    invalid: 'Der gespeicherte Lernstand konnte nicht sicher zugeordnet werden.',
    version: 'Der gespeicherte Versuch verwendet eine andere Lernstandsversion.'
  };
  class StateIssue extends Error {
    constructor(reason) { super(message[reason]); }
  }
  function fail(reason = 'invalid') { throw new StateIssue(reason); }
  function decode(raw) {
    if (!raw) return null;
    try {
      if (typeof raw !== 'string' || raw.length > 131072) fail();
      let text = raw.trim();
      if (text.startsWith('SOZ2:')) {
        const bytes = Uint8Array.from(atob(text.slice(5)), c => c.charCodeAt(0));
        const inflate = new window.pako.Inflate({to: 'string', chunkSize: 8192});
        let length = 0;
        const chunks = [];
        inflate.onData = chunk => {
          length += chunk.length;
          if (length > 131072) fail();
          chunks.push(chunk);
        };
        if (!inflate.push(bytes, true) || inflate.err || !inflate.ended) fail();
        text = chunks.join('');
      }
      const result = JSON.parse(text);
      if (!object(result)) fail();
      return result;
    } catch { fail(); }
  }
  function requireId(state, id) {
    if (['id', 'l'].some(key => own(state,key) && state[key] !== id)) fail('foreign');
  }
  function requireChoices(value, count) {
    return Array.isArray(value) && value.length === count && value.every(n => n === null || (Number.isInteger(n) && n >= 0 && n < 6));
  }
  function lesson(raw, target, requirements, count, safePage) {
    const old = decode(raw);
    if (!old) return target;
    const id = target.id;
    requireId(old, id);
    // LF06 26.11.2026 used {v,l,s} with short IDs inside the SOZ2 envelope.
    if (old.v === 1 && old.l === id && object(old.s) && Array.isArray(old.s.done)) {
      const prior = old.s;
      const known = new Set(['common','A','B','C'].flatMap(key => requirements[key] || []));
      const short = value => value.slice(id.length + 1);
      const wasDone = key => prior.done.includes(short(key));
      for (const key of known) {
        const merged = requirements.legacyGroups?.[key];
        const peerStep = key.replace(/-(ABGABE|RUECKMELDUNG)$/, '');
        if (merged ? merged.every(wasDone) : wasDone(peerStep)) target.done.push(key);
      }
      if ((requirements.A || []).some(wasDone)) target.path = 'A';
      for (const key of requirements.responses || []) {
        const choice = prior.readingPicks?.[short(key)];
        if (Number.isInteger(choice) && choice >= 0 && choice < 6) {
          const missed = prior.readingMisses?.includes(short(key)) || prior.hints?.includes(short(key));
          target.responses[key] = 'mc:' + Number(!missed && target.done.includes(key)) + ':' + choice;
        }
      }
      const choices = values => Array.isArray(values) && values.length === count
        ? values.map(n => Number.isInteger(n) && n >= 0 && n < 6 ? n : null) : null;
      target.check = choices(prior.quiz);
      target.checkFirst = choices(prior.first);
      return target;
    }
    const current = old.id === id && old.v === 1;
    const compact = old.l === id && old.s === 1;
    if (!current && !compact) fail(own(old,'v') || own(old,'s') ? 'version' : 'invalid');
    const ids = new Set(['common','A','B','C','responses'].flatMap(k => requirements[k] || []));
    const knownAnswerIds = new Set(requirements.responses || []);
    if (current && (!Array.isArray(old.done) || !object(old.responses))) fail();
    if (compact && !object(old.t)) fail();
    const checked = new Set();
    if (current) {
      for (const key of old.done) if (typeof key === 'string' && (ids.has(key) || key.startsWith(id+'-'))) checked.add(key);
    } else {
      // Legacy positional task keys refer to a different layout. Match stable task IDs only.
      for (const [key,signature] of Object.entries(old.t)) {
        if (ids.has(key) && (signature === true || (typeof signature === 'string' && /^[0-9a-f]{8}$/i.test(signature)))) checked.add(key);
      }
      const orientation = id+'-T01';
      if (old.o === true && ids.has(orientation)) checked.add(orientation);
    }
    if (object(old.responses)) {
      for (const [key,v] of Object.entries(old.responses)) if (knownAnswerIds.has(key) && typeof v === 'string') target.responses[key] = v;
    }
    target.done = [...checked];
    target.page = safePage(current ? old.page : old.b);
    if (['A','B','C'].includes(old.path)) target.path = old.path;
    if (requireChoices(old.check,count)) target.check = old.check.slice();
    if (requireChoices(old.checkFirst,count)) target.checkFirst = old.checkFirst.slice();
    target.completed = old.completed === true;
    return target;
  }
  function office(raw, target, id, pages) {
    const old = decode(raw);
    if (!old) return {...target, id, version: 1};
    requireId(old, id);
    if (own(old,'version') && old.version !== 1) fail('version');
    if (own(old,'id') && !own(old,'version')) fail('version');
    // Before the office package stored its ID, exactly these five fields formed its format.
    if (!own(old,'id') && (Object.keys(old).sort().join(',') !== 'done,q0,q8,seen,v')) fail();
    if (!object(old.v) || !object(old.q0) || !object(old.q8) || !Array.isArray(old.seen) || typeof old.done !== 'boolean') fail();
    if (old.seen.some(p=>!pages.includes(p))) fail();
    if (Object.keys(old.v).some(k=>!['grund','plan','paket','abgabe','feedback','check0','check1','check2','check3','check4','check5'].includes(k))) fail();
    if (Object.values(old.v).some(v=>typeof v !== 'string' && typeof v !== 'boolean')) fail();
    for (const quiz of [old.q0,old.q8]) {
      if (own(quiz,'a') && (!object(quiz.a) || !Object.values(quiz.a).every(choices => Array.isArray(choices) && choices.every(Number.isInteger)))) fail();
    }
    return {...target, id, version: 1, v:old.v, seen:[...new Set(old.seen)], q0:old.q0, q8:old.q8, done:old.done};
  }
  function practiceNotice(issue, online) {
    return 'Übungsansicht. '+issue.message+' Deine Eingaben gelten für dieses Fenster. '+(online ? 'Für eine Speicherung in Moodle starte einen neuen Versuch in der passenden Aktivität.' : 'Der vorhandene Speicherstand bleibt erhalten.');
  }
  window.BFS_RESUME = {StateIssue,lesson,office,practiceNotice};
})();
