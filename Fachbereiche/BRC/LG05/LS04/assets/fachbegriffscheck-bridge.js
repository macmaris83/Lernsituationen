/*
 * Prepared adapter for the supplied SOZ_SCORM / SOZ_PROGRESS_CORE packages.
 * This does not change the uploaded packages or create a separate SCORM session.
 * No LMSInitialize/LMSFinish, score writes, or direct suspend_data writes occur here.
 *
 * REQUIRED LATER PACKAGE INSTALLATION, in this order:
 * 1. Keep progress-meta.js and assets/progress-core.js. Immediately AFTER them,
 *    but synchronously BEFORE assets/scorm.js, execute getEarlyPreserveHook().
 *    The original sanitizer otherwise discards saved fc before an iframe can run.
 * 2. Keep the original pako, codec and scorm.js. AFTER scorm.js, add ONE persistent
 *    hidden iframe in scorm.html:
 *      <iframe hidden aria-hidden="true" tabindex="-1"
 *        src="TESTFILENAME?package-bridge=1" title="Flashcard-Paketanschluss"
 *        style="display:none!important"></iframe>
 *    It must be a sibling of, not a replacement for, iframe[data-scorm-frame].
 *    This loads the adapter even when the learner never opens the test manually.
 * 3. Copy this self-contained test HTML into the package and declare its filename
 *    as a <file href="..."/> in the existing manifest resource. Link to it after
 *    Informieren. Do not rename existing task IDs or initialize another LMS API.
 * 4. The adapter adds the test to resumePages, preserves fc when legacy phase
 *    writers omit it, and ANDs whole-LS completion with fc.complete. A manual phase
 *    jump never completes the test. The red fixed pill lives in the parent player,
 *    so it stays visible while the learning iframe scrolls, including when the test
 *    has never started. Parent SOZ_SCORM.reset() deliberately clears fc as well.
 *
 * The seven HTML deliverables only prepare this connection. Until the required
 * parent hook and persistent iframe are installed, these are standalone previews.
 */
(() => {
  'use strict';
  const config = window.RENO_FLASHCARD_CONFIG || {};
  const terms = Array.isArray(config.terms) ? config.terms : [];
  const ids = terms.map(term => term.id);
  const MARKER = '__RENO_FC_EARLY_PRESERVE_V1__';
  const MANAGER = '__RENO_FC_PACKAGE_MANAGER_V1__';
  const laterPhases = new Set(['planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren']);
  const allowedPages = new Set(['index.html', 'handlungssituation.html', 'informieren.html', 'planen.html', 'entscheiden.html', 'durchfuehren.html', 'bewerten.html', 'reflektieren.html']);
  const fileName = typeof config.fileName === 'string' && /^[A-Za-z0-9_.-]+\.html$/.test(config.fileName) ? config.fileName : '';
  if (fileName) allowedPages.add(fileName);
  try {window.RENO_FC_BRIDGE_MODE = new URLSearchParams(window.location.search || '').get('package-bridge') === '1';}
  catch {window.RENO_FC_BRIDGE_MODE = false;}

  // Self-contained on purpose: callers may execute the returned function source
  // in the parent before this file's config or hidden iframe exists.
  function earlyPreserveHook(w, testFileName, testSignature) {
    'use strict';
    const marker = '__RENO_FC_EARLY_PRESERVE_V1__';
    const K = w.SOZ_PROGRESS_CORE, M = w.SOZ_PROGRESS_META;
    if (!K || !M) throw new Error('Flashcard-Hook muss nach Fortschrittskern und Metadaten geladen werden.');
    if (typeof testFileName === 'string' && /^[A-Za-z0-9_.-]+\.html$/.test(testFileName) && Array.isArray(M.resumePages) && !M.resumePages.includes(testFileName)) M.resumePages.push(testFileName);
    if (w[marker]?.id === M.id && w[marker]?.schema === 1) return;
    const originalSanitize = K.sanitize, originalAllComplete = K.allComplete;
    const valid = fc => !!fc && fc.schema === 1 && fc.id === M.id && fc.version === 3 && typeof fc.signature === 'string' && fc.data !== undefined;
    K.sanitize = function(raw, meta, mode) {
      const p = originalSanitize.call(this, raw, meta, mode);
      if (raw?.s === 1 && raw.l === meta.id && valid(raw.fc)) p.fc = K.clone(raw.fc);
      return p;
    };
    K.allComplete = function(p, meta, ...args) {
      return originalAllComplete.call(this, p, meta, ...args) && valid(p.fc) && (!testSignature || p.fc.signature === testSignature) && p.fc.complete === true;
    };
    w[marker] = {schema: 1, id: M.id, fileName: testFileName || '', signature: testSignature || ''};
  }
  const getEarlyPreserveHook = () => '(' + earlyPreserveHook.toString() + ')(window,' + JSON.stringify(fileName) + ',' + JSON.stringify(config.signature || '') + ');';
  const clone = value => JSON.parse(JSON.stringify(value));
  const pool = [];
  const poolIndex = new Map();
  function addString(value) {if (typeof value === 'string' && !poolIndex.has(value)) {poolIndex.set(value, pool.length); pool.push(value);}}
  for (const term of terms) {
    addString(term.id);
    for (const value of term.variants || []) addString(value);
    addString(term.term); addString(term.explanation);
  }
  for (const term of terms) for (const item of term.distractors || []) {
    addString(item.id);
    for (const text of item.variants || []) addString(text);
  }
  // A generic JSON transform: arrays/objects keep their shape; only known text
  // values become pool references. Escape the two reserved singleton shapes so
  // even ordinary state objects named $s or $e survive the round trip unchanged.
  function pack(value, seen = new Set()) {
    if (typeof value === 'string') return poolIndex.has(value) ? {$s: poolIndex.get(value)} : value;
    if (value === null || typeof value === 'boolean' || typeof value === 'number' && Number.isFinite(value)) return value;
    if (typeof value !== 'object' || seen.has(value)) throw new Error('Der Testzustand enthält nicht speicherbare Werte.');
    seen.add(value);
    let result;
    if (Array.isArray(value)) result = value.map(item => pack(item, seen));
    else {
      const entries = Object.entries(value);
      if (entries.length === 1 && ['$s', '$e'].includes(entries[0][0])) result = {$e: entries.map(([key, item]) => [key, pack(item, seen)])};
      else {result = {}; for (const [key, item] of entries) Object.defineProperty(result, key, {value: pack(item, seen), enumerable: true, writable: true, configurable: true});}
    }
    seen.delete(value); return result;
  }
  function unpack(value) {
    if (value === null || typeof value !== 'object') return value;
    if (Array.isArray(value)) return value.map(unpack);
    const keys = Object.keys(value);
    if (keys.length === 1 && keys[0] === '$s') {
      if (!Number.isInteger(value.$s) || value.$s < 0 || value.$s >= pool.length) throw new Error('Unbekannter Definitionsverweis im gespeicherten Test.');
      return pool[value.$s];
    }
    const entries = keys.length === 1 && keys[0] === '$e' ? value.$e : Object.entries(value);
    if (!Array.isArray(entries)) throw new Error('Der gespeicherte Testzustand ist beschädigt.');
    const result = {};
    for (const pair of entries) {
      if (!Array.isArray(pair) || pair.length !== 2 || typeof pair[0] !== 'string') throw new Error('Der gespeicherte Testzustand ist beschädigt.');
      Object.defineProperty(result, pair[0], {value: unpack(pair[1]), enumerable: true, writable: true, configurable: true});
    }
    return result;
  }
  function validEnvelope(envelope) {
    return !!envelope && envelope.version === 3 && Array.isArray(envelope.cardIds) && envelope.cardIds.length === ids.length &&
      envelope.cardIds.every((id, index) => id === ids[index]) && envelope.state && typeof envelope.state === 'object' && !Array.isArray(envelope.state);
  }
  function validFc(fc, exact = true) {
    return !!fc && fc.schema === 1 && fc.version === 3 && fc.id === config.id && typeof fc.signature === 'string' &&
      (!exact || fc.signature === config.signature || (config.legacySignatures || []).includes(fc.signature)) && fc.data !== undefined;
  }
  function normalizeStatus(status) {
    const n = ids.length;
    const integer = (value, fallback) => Number.isInteger(value) ? Math.max(0, Math.min(n, value)) : fallback;
    return {complete: status?.complete === true, known: integer(status?.known, 0), total: n,
      pending: Number.isInteger(status?.pending) ? Math.max(0, status.pending) : n, started: status?.started === true, acknowledged: status?.acknowledged === true};
  }
  function findHost() {
    if (window.SOZ_TEACHER_VIEW?.active) return null;
    let w = window;
    for (let depth = 0; w && depth < 10; depth++) {
      try {
        if (w.SOZ_SCORM && typeof w.SOZ_SCORM.read === 'function' && typeof w.SOZ_SCORM.update === 'function' && w.SOZ_PROGRESS_CORE && w.SOZ_PROGRESS_META) return w;
        if (w.parent === w) break;
        w = w.parent;
      } catch {break;}
    }
    return null;
  }
  let hostWindow = findHost(), manager = null, localError = '';
  function bootstrapped(w) {return w?.[MARKER]?.schema === 1 && w[MARKER].id === w.SOZ_PROGRESS_META.id;}
  function install(w) {
    const host = w.SOZ_SCORM, K = w.SOZ_PROGRESS_CORE, meta = w.SOZ_PROGRESS_META;
    if (w[MANAGER]) {
      if (w[MANAGER].id !== config.id || w[MANAGER].signature !== config.signature) {localError = 'Der Paketanschluss verwendet eine andere Testversion. Bitte das Lernpaket erneut öffnen.'; return null;}
      return w[MANAGER];
    }
    const m = {id: config.id, signature: config.signature, host, window: w, resetGuard: false, listeners: new Set(), watched: new WeakSet(), frame: null, returnPage: null};
    w[MANAGER] = m;
    m.fc = () => {try {const fc = host.read().fc; return validFc(fc) ? fc : null;} catch {return null;}};
    m.status = () => {const fc = m.fc(); return normalizeStatus(fc || {});};
    m.notify = () => {for (const fn of m.listeners) {try {fn();} catch {}}};
    const originalSanitize = K.sanitize;
    K.sanitize = function(raw, metadata, mode) {
      const p = originalSanitize.call(this, raw, metadata, mode);
      if (metadata.id !== config.id || raw?.s !== 1 || raw.l !== metadata.id) return p;
      let fc = raw.fc;
      if (!Object.prototype.hasOwnProperty.call(raw, 'fc') && !m.resetGuard) {
        try {fc = host.read().fc;} catch {}
      }
      if (validFc(fc, false)) p.fc = clone(fc);
      else delete p.fc;
      return p;
    };
    const originalAllComplete = K.allComplete;
    K.allComplete = function(p, metadata, ...args) {
      return originalAllComplete.call(this, p, metadata, ...args) && (metadata.id !== config.id || validFc(p.fc) && p.fc.complete === true);
    };
    const originalUpdate = host.update.bind(host), originalCommit = typeof host.commit === 'function' ? host.commit.bind(host) : null;
    host.update = function(next) {const ok = originalUpdate(next); m.refresh(); return ok === true;};
    if (originalCommit) host.commit = function() {const ok = originalCommit(); m.refresh(); return ok === true;};
    if (typeof host.reset === 'function') {
      const originalReset = host.reset.bind(host);
      host.reset = function() {m.resetGuard = true; try {return originalReset();} finally {m.resetGuard = false; m.refresh();}};
    }
    if (fileName && Array.isArray(meta.resumePages) && !meta.resumePages.includes(fileName)) meta.resumePages.push(fileName);
    m.refresh = () => {
      try {
        const frame = w.document.querySelector('[data-scorm-frame]');
        if (frame) {
          m.frame = frame;
          if (!m.watched.has(frame)) {m.watched.add(frame); frame.addEventListener('load', m.refresh);}
          const doc = frame.contentDocument || frame.contentWindow?.document;
          if (doc?.body) mountInto(doc, doc.body.dataset.page, m);
        } else if (w.document.body?.dataset.page) mountInto(w.document, w.document.body.dataset.page, m);
      } catch {}
      m.notify();
    };
    if (typeof host.subscribe === 'function') host.subscribe(m.refresh);
    m.refresh();
    return m;
  }
  function ensure() {
    if (manager) return manager;
    hostWindow ||= findHost();
    if (hostWindow) manager = install(hostWindow);
    return manager;
  }
  const reminderLayouts = new WeakMap();
  function reserveReminderSpace(doc, pill) {
    const previous = reminderLayouts.get(doc);
    if (previous?.pill !== pill) {
      previous?.observer?.disconnect();
      if (previous) doc.defaultView?.removeEventListener('resize', previous.update);
      reminderLayouts.delete(doc);
    }
    const body = doc.body;
    let backdrop = doc.getElementById('reno-fc-reminder-backdrop');
    if (!pill) {
      delete body.dataset.fcReminderOpen;
      body.style.removeProperty('--fc-reminder-space');
      backdrop?.remove();
      return;
    }
    body.dataset.fcReminderOpen = '';
    if (!backdrop) {
      backdrop = doc.createElement('div');
      backdrop.id = 'reno-fc-reminder-backdrop';
      backdrop.setAttribute('aria-hidden', 'true');
      body.insertBefore(backdrop, body.firstChild);
    }
    let layout = reminderLayouts.get(doc);
    if (!layout) {
      const update = () => {
        if (pill.isConnected) body.style.setProperty('--fc-reminder-space', Math.ceil(pill.getBoundingClientRect().bottom + 10) + 'px');
      };
      const Observer = doc.defaultView?.ResizeObserver;
      const observer = Observer ? new Observer(update) : null;
      observer?.observe(pill);
      doc.defaultView?.addEventListener('resize', update);
      layout = {pill, observer, update};
      reminderLayouts.set(doc, layout);
    }
    layout.update();
  }
  const styleText = `
    .reno-fc-fixed-pill{position:fixed!important;top:max(10px,env(safe-area-inset-top))!important;right:max(10px,env(safe-area-inset-right))!important;z-index:2147483000!important;display:flex!important;align-items:center!important;gap:10px!important;box-sizing:border-box!important;max-width:calc(100% - 20px)!important;min-height:48px!important;padding:7px 13px!important;border:2px solid #ce3528!important;border-radius:15px!important;background:#fff7f2!important;color:#702c21!important;box-shadow:0 3px 15px #173a6330!important;font:600 14px/1.3 Avenir,'Segoe UI',Arial,sans-serif!important;text-align:left!important;cursor:pointer!important;-webkit-tap-highlight-color:transparent}
    body[data-fc-reminder-open]{padding-top:var(--fc-reminder-space,74px)!important;box-sizing:border-box}
    #reno-fc-reminder-backdrop{position:fixed;inset:0 0 auto;height:var(--fc-reminder-space,74px);background:#f1f6f7;z-index:2147482999;pointer-events:none}
    .reno-fc-fixed-pill:disabled{opacity:1!important;cursor:default!important}
    .reno-fc-fixed-pill .reno-fc-dot{display:block;flex:0 0 22px;width:22px;height:22px;border-radius:50%;background:#d63728;box-shadow:0 0 0 3px #f9d6cb}
    .reno-fc-fixed-pill .reno-fc-pill-copy{display:block;min-width:0;overflow-wrap:anywhere}
    .reno-fc-fixed-pill strong,.reno-fc-fixed-pill small{display:block;margin:0;color:inherit;font:inherit}
    .reno-fc-fixed-pill small{font-size:11px;line-height:1.25;font-weight:400;margin-top:1px}
    .reno-fc-fixed-pill:focus-visible,.reno-fc-test-badge:focus-visible{outline:3px solid #00749e!important;outline-offset:3px}
    .reno-fc-badge-parent{position:relative!important}
    .reno-fc-test-badge{position:absolute!important;left:calc(50% + 5px)!important;top:-13px!important;z-index:8!important;display:grid!important;place-items:center!important;width:44px!important;height:44px!important;min-width:44px!important;min-height:44px!important;padding:10px!important;border:0!important;border-radius:50%!important;background:transparent!important;cursor:pointer!important}
    .reno-fc-test-badge>span{display:grid;place-items:center;box-sizing:border-box;width:24px;height:24px;border:2px solid #fff;border-radius:50%;background:#173a63;color:#fff;font:700 13px/1 'Segoe UI',Arial,sans-serif;box-shadow:0 1px 6px #173a6333}
    .reno-fc-test-badge[data-open="true"]>span{background:#d63728}
    .reno-fc-test-badge[data-complete="true"]>span{background:#afca0b;color:#425b0b}
    @media print{#reno-fc-reminder-backdrop,.reno-fc-fixed-pill,.reno-fc-test-badge{display:none!important}body[data-fc-reminder-open]{padding-top:0!important}}
  `;
  function injectStyle(doc) {
    if (doc.getElementById('reno-fc-package-style')) return;
    const style = doc.createElement('style'); style.id = 'reno-fc-package-style'; style.textContent = styleText;
    (doc.head || doc.body).appendChild(style);
  }
  function phaseName(phase) {return String(phase || '').split(/[?#]/)[0].split('/').pop().replace(/\.html$/, '');}
  function currentStatus(m) {return m ? m.status() : normalizeStatus({});}
  function mountInto(doc, phase, m) {
    if (!doc?.body) return null;
    const status = currentStatus(m);
    const name = phaseName(phase || doc.body.dataset.page);
    const targetDoc = m?.window.document || doc;
    injectStyle(targetDoc); injectStyle(doc);
    let pill = targetDoc.getElementById('reno-fc-package-reminder');
    const teacherPage = !!doc.body.dataset.teacher || !!doc.defaultView?.SOZ_TEACHER_VIEW?.active || ['lehrkraft','erwartungshorizont','druckansicht'].includes(name);
    if (teacherPage || status.complete) {pill?.remove(); pill = null;}
    else {
      if (!pill) {
        pill = targetDoc.createElement('button'); pill.id = 'reno-fc-package-reminder'; pill.type = 'button'; pill.className = 'reno-fc-fixed-pill';
        const dot = targetDoc.createElement('span'); dot.className = 'reno-fc-dot'; dot.setAttribute('aria-hidden', 'true');
        const copy = targetDoc.createElement('span'); copy.className = 'reno-fc-pill-copy';
        const title = targetDoc.createElement('strong'); title.dataset.fcTitle = '';
        const detail = targetDoc.createElement('small'); detail.dataset.fcDetail = '';
        copy.append(title, detail); pill.append(dot, copy);
        pill.addEventListener('click', () => {if (m) m.returnPage = pill.dataset.returnPage || null; navigate(fileName);});
        targetDoc.body.insertBefore(pill, targetDoc.body.firstChild);
      }
      const title = pill.querySelector('[data-fc-title]'), detail = pill.querySelector('[data-fc-detail]');
      if (title) title.textContent = `Test offen · ${status.known}/${status.total}`;
      const blocked = m && !m.host.readOnly && m.window.SOZ_PROGRESS_CORE.blockedBy(m.host.read(),m.window.SOZ_PROGRESS_META,fileName);
      pill.disabled = !!blocked;
      const detailText = blocked ? 'Nach Informieren verfügbar' : !status.started ? 'Noch nicht gestartet' : status.pending ? `${status.pending} Pflichtkarten noch offen` : 'Noch nicht alle Begriffe richtig zugeordnet';
      if (detail) detail.textContent = detailText;
      pill.setAttribute('aria-label', `Flashcard-Test noch offen: ${status.known} von ${status.total} Begriffen richtig. ${detailText}. ${blocked ? 'Zuerst den Lernweg bis Informieren bearbeiten.' : 'Test öffnen.'}`);
      pill.dataset.pending = String(status.pending); pill.dataset.started = String(status.started);
      pill.dataset.returnPage = name + '.html';
    }
    reserveReminderSpace(targetDoc, pill);
    const anchor = doc.querySelector('.stations [data-learning-page="informieren.html"]');
    const li = anchor?.parentElement;
    if (li && anchor.querySelector('.station-icon')) {
      li.classList.add('reno-fc-badge-parent');
      let badge = li.querySelector('.reno-fc-test-badge');
      if (!badge) {
        badge = doc.createElement('button'); badge.type = 'button'; badge.className = 'reno-fc-test-badge';
        const dot = doc.createElement('span'); dot.setAttribute('aria-hidden', 'true'); badge.appendChild(dot);
        badge.addEventListener('click', event => {event.preventDefault(); event.stopPropagation(); if (m && badge.dataset.returnPage) m.returnPage = badge.dataset.returnPage; navigate(fileName);});
        li.appendChild(badge);
      }
      badge.dataset.open = String(!status.complete && (status.started || laterPhases.has(name)));
      badge.dataset.complete = String(status.complete);
      badge.dataset.returnPage = laterPhases.has(name) ? name + '.html' : '';
      badge.firstChild.textContent = status.complete ? '✓' : '•';
      badge.setAttribute('aria-label', `Flashcard-Test öffnen: ${status.complete ? 'vollständig richtig abgeschlossen' : `${status.known} von ${status.total} richtig, ${status.started ? 'noch offen' : 'noch nicht gestartet'}`}.`);
    }
    return pill;
  }
  function message() {
    if (localError) return localError;
    const m = ensure();
    if (!m) return hostWindow ? 'Der Paketanschluss konnte nicht hergestellt werden.' : '';
    if (m.window.SOZ_PROGRESS_META.id !== config.id) return 'Der Flashcard-Test gehört nicht zu dieser Lernsituation.';
    if (!bootstrapped(m.window)) return 'Synchroner Paketanschluss nicht initialisiert. Der Preserve-Hook muss vor assets/scorm.js geladen werden; der Test wird hier nicht gespeichert.';
    if (m.host.message) return String(m.host.message);
    return m.host.lastSaved ? (m.host.kind === 'moodle' ? 'In Moodle gespeichert.' : 'In der Paketvorschau gespeichert.') : (m.host.kind === 'moodle' ? 'Testzustand aus dem Moodle-Paket geladen.' : 'Paketvorschau: Speicherung in diesem Browser.');
  }
  function load() {
    const m = ensure();
    if (!m || !bootstrapped(m.window) || m.window.SOZ_PROGRESS_META.id !== config.id) return null;
    try {
      const fc = m.fc();
      if (!fc) return null;
      const envelope = unpack(fc.data);
      if (!validEnvelope(envelope)) throw new Error('Der gespeicherte Test passt nicht zu diesen Begriffen.');
      return envelope;
    } catch (error) {localError = error.message || 'Der gespeicherte Testzustand konnte nicht gelesen werden.'; return null;}
  }
  function readOnly() {const m = ensure(); return !!hostWindow && (!m || !!m.host.readOnly || !bootstrapped(m.window) || m.window.SOZ_PROGRESS_META.id !== config.id);}
  function save(envelope, status) {
    const m = ensure(); localError = '';
    if (!m || readOnly()) {localError = message() || 'Der Paketanschluss erlaubt keine Speicherung.'; return false;}
    if (!validEnvelope(envelope) || !config.signature || !fileName) {localError = 'Der Testzustand oder seine Paketkennung ist ungültig und wurde nicht gespeichert.'; return false;}
    try {
      const next = m.host.read();
      if (next.l !== config.id || next.s !== 1) throw new Error('Der Testzustand gehört nicht zu diesem Lernpaket.');
      next.fc = {schema: 1, version: 3, id: config.id, signature: config.signature, ...normalizeStatus(status), data: pack(envelope)};
      const codec = m.window.SOZ_SCORM_CODEC;
      if (!codec || typeof codec.encode !== 'function') throw new Error('Der vorhandene Paketcodec fehlt.');
      if (m.host.kind === 'moodle' && codec.encode(next).length > 4096) throw new Error('Der gemeinsame Paketfortschritt überschreitet die SCORM-1.2-Grenze von 4096 Zeichen. Die Speicherung wurde nicht bestätigt.');
      const ok = m.host.update(next) === true;
      if (!ok) {localError = m.host.message || 'Das Lernpaket hat das Speichern des Tests nicht bestätigt.'; m.refresh(); return false;}
      localError = ''; m.refresh(); return true;
    } catch (error) {localError = error.message || 'Der Flashcard-Test konnte nicht gespeichert werden.'; m.refresh(); return false;}
  }
  function navigate(page) {
    const m = ensure();
    if (!m || !allowedPages.has(page)) return false;
    try {
      const target = m.window.document.querySelector('[data-scorm-frame]');
      if (!readOnly()) {
        const next = m.host.read(); next.b = page;
        if (m.host.update(next) !== true) {localError = m.host.message || 'Der Seitenwechsel konnte nicht gespeichert werden.'; return false;}
      }
      if (target) target.src = page;
      else if (!window.RENO_FC_BRIDGE_MODE) window.location.assign(page);
      else return false;
      return true;
    } catch (error) {localError = error.message || 'Die Lernseite konnte nicht geöffnet werden.'; return false;}
  }
  window.RENO_FLASHCARD_PACKAGE = {
    get isHosted() {return !!(ensure() || hostWindow);},
    get readOnly() {return readOnly();},
    get mode() {const m = ensure(); return m ? (m.host.kind === 'preview' ? 'package-preview' : 'moodle') : hostWindow ? 'moodle' : 'standalone';},
    get message() {return message();},
    get learner() {return ensure()?.host.learner || '';},
    get returnPage() {return ensure()?.returnPage || null;},
    getReturnPage() {return ensure()?.returnPage || null;},
    load, save, navigate,
    getGrade() {const m = ensure(); return m?.window.SOZ_PROGRESS_CORE.grading?.(m.host.read(), m.window.SOZ_PROGRESS_META) || null;},
    getStatus() {return currentStatus(ensure());},
    mountReminder(doc, phase) {return mountInto(doc, phase, ensure());},
    refresh() {ensure()?.refresh();},
    subscribe(fn) {const m = ensure(); if (!m || typeof fn !== 'function') return () => {}; m.listeners.add(fn); return () => m.listeners.delete(fn);},
    getEarlyPreserveHook,
    getIntegrationSnippet() {return {requiredOrder: 'metadata + progress-core → synchronous preserve hook → original scorm.js → persistent hidden iframe', beforeScormScript: getEarlyPreserveHook(), fileName,
      hiddenIframe: `<iframe hidden aria-hidden="true" tabindex="-1" src="${fileName}?package-bridge=1" title="Flashcard-Paketanschluss" style="display:none!important"></iframe>`,
      manifestFile: `<file href="${fileName}"/>`, afterInformierenLink: `<a href="${fileName}">Flashcard-Test starten</a>`};}
  };
  ensure();
})();

