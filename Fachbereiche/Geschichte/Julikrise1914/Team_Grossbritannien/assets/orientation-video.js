/* Interactive orientation video. Uses the existing SCORM learner state only. */
(() => {
  'use strict';
  const D = window.SOZPAED, P = window.SOZ_PROGRESS, cfg = D?.orientationVideo;
  const frame = document.querySelector('[data-orientation-video-player]');
  const panel = document.querySelector('[data-orientation-video-question]');
  if (!cfg || !P || !frame || !panel || document.body.dataset.page !== 'index.html') return;
  const status = document.querySelector('[data-orientation-video-status]');
  const progress = document.querySelector('[data-orientation-video-progress]');
  const play = document.querySelector('[data-video-play]'), pause = document.querySelector('[data-video-pause]');
  const back = document.querySelector('[data-video-back]'), captions = document.querySelector('[data-video-captions]');
  const volume = document.querySelector('[data-video-volume]');
  const skip = document.querySelector('[data-video-skip]');
  const controls = [play, pause, back, captions, volume].filter(Boolean);
  const preview = document.querySelector('[data-video-open]');
  const expanded = document.querySelector('[data-video-expanded]');
  const close = document.querySelector('[data-video-close]');
  let opened = !preview, apiRequested = false;
  const readOnly = () => !!P.readOnly || !!window.SOZ_TEACHER_VIEW?.active || !!document.body.dataset.teacher;
  const num = value => Number.isFinite(Number(value)) ? Number(value) : 0;
  const round = value => Math.round(value * 100) / 100;
  const required = Math.min(1, Math.max(0.5, Number(cfg.requiredRatio) || 0.98));
  const questions = (cfg.questions || []).map(q => ({
    id: q.id, at: q.at === null ? null : num(q.at), question: q.question || q.prompt || '',
    options: (q.options || []).map(o => ({id: String(o.id ?? o.value), text: String(o.text || '')})),
    correct: String(q.correct), feedback: String(q.feedback || ''), hint: String(q.hint || '')
  }));
  function merge(ranges, duration) {
    const sorted = (Array.isArray(ranges) ? ranges : []).filter(r => Array.isArray(r) && r.length === 2)
      .map(r => [Math.max(0, num(r[0])), Math.max(0, num(r[1]))])
      .map(r => [round(r[0]), round(duration > 0 ? Math.min(duration, r[1]) : r[1])])
      .filter(r => r[1] > r[0]).sort((a, b) => a[0] - b[0]);
    const result = [];
    for (const r of sorted) {
      const previous = result[result.length - 1];
      if (previous && r[0] <= previous[1] + 0.15) previous[1] = Math.max(previous[1], r[1]);
      else result.push([...r]);
    }
    return result.length <= 128 ? result : result.sort((a, b) => (b[1] - b[0]) - (a[1] - a[0]))
      .slice(0, 128).sort((a, b) => a[0] - b[0]);
  }
  function clean(raw) {
    const valid = raw?.signature === cfg.signature, duration = valid ? Math.max(0, num(raw.duration)) : 0;
    const out = {signature: cfg.signature, duration, ranges: merge(valid ? raw.ranges : [], duration),
      answers: {}, attempts: {}, ended: valid && raw.ended === true, skipped: valid && raw.skipped === true,
      complete: valid && raw.complete === true};
    if (valid) for (const q of questions) {
      const answer = raw.answers?.[q.id];
      if (q.options.some(o => o.id === answer)) out.answers[q.id] = answer;
      const attempts = raw.attempts?.[q.id];
      if (Number.isInteger(attempts) && attempts > 0) out.attempts[q.id] = Math.min(100000, attempts);
    }
    return out;
  }
  let state = clean(P.read().ov), completeSaved = state.complete, player = null, ready = false;
  let initialized = false, playing = false, anchor = null, timer = null, dirty = false, lastSave = 0;
  let activeQuestion = null, captionsOn = false, questionFeedback = '';
  const answered = q => state.answers[q.id] === q.correct && (state.attempts[q.id] || 0) > 0;
  const allAnswered = () => questions.every(answered);
  const watched = () => state.ranges.reduce((sum, r) => sum + r[1] - r[0], 0);
  const fraction = () => state.duration > 0 ? Math.min(1, watched() / state.duration) : 0;
  const eligible = () => state.duration > 0 && fraction() >= required && state.ended && allAnswered();
  function message(text) {if (status) status.textContent = text;}
  function renderStatus() {
    if (skip) {skip.hidden = completeSaved; skip.disabled = readOnly();}
    const percent = completeSaved ? 100 : Math.min(99, Math.floor(fraction() * 100));
    if (progress) {
      if ('value' in progress) {progress.max = 100; progress.value = percent;}
      progress.setAttribute('aria-valuenow', String(percent));
      progress.setAttribute('aria-valuemin', '0'); progress.setAttribute('aria-valuemax', '100');
      progress.setAttribute('aria-label', 'Angesehener Anteil des Orientierungsvideos');
    }
    const count = questions.filter(answered).length;
    message(completeSaved ? 'Videoauftrag abgeschlossen. Die Handlungssituation ist freigeschaltet.' :
      activeQuestion ? `Videopause · Frage ${questions.indexOf(activeQuestion) + 1} von ${questions.length}.` :
      `${percent} % angesehen · ${count} von ${questions.length} Fragen gelöst. Schau das Video bis zum Ende an.`);
  }
  function persist(force = false) {
    if (readOnly() || (!dirty && !force)) return true;
    const now = performance.now();
    if (!force && now - lastSave < 5000) return true;
    const next = P.read(), stored = clean(next.ov);
    state.duration = Math.max(state.duration, stored.duration);
    state.ranges = merge([...stored.ranges, ...state.ranges], state.duration);
    state.ended ||= stored.ended;
    state.skipped ||= stored.skipped;
    for (const q of questions) if ((stored.attempts[q.id] || 0) > (state.attempts[q.id] || 0)) {
      state.attempts[q.id] = stored.attempts[q.id];
      if (stored.answers[q.id] !== undefined) state.answers[q.id] = stored.answers[q.id];
    }
    state.complete = (state.complete || stored.complete) && eligible();
    next.ov = {signature: state.signature, duration: round(state.duration), ranges: state.ranges.map(r => [...r]),
      answers: {...state.answers}, attempts: {...state.attempts}, ended: state.ended,
      skipped: state.skipped, complete: state.complete};
    if (state.complete || state.skipped) next.o = true;
    if (P.write(next) !== true) {
      message('Der Videofortschritt konnte noch nicht gespeichert werden. Lass die Seite geöffnet und versuche es erneut.');
      return false;
    }
    lastSave = now; dirty = false;
    const confirmed = clean(P.read().ov);
    completeSaved = confirmed.complete && !!P.read().o;
    renderStatus(); P.render?.(); window.dispatchEvent(new Event('orientation-video-progress'));
    return true;
  }
  function duration() {
    try {
      const value = num(player?.getDuration?.());
      if (value > 0 && Math.abs(value - state.duration) > 0.1) {
        state.duration = value; state.ranges = merge(state.ranges, value); dirty = true;
      }
    } catch {}
  }
  const time = () => {try {return Math.max(0, num(player?.getCurrentTime?.()));} catch {return 0;}};
  function sample(allowEnded = false) {
    if (!player || readOnly() || completeSaved) {anchor = null; return;}
    duration();
    const now = performance.now(), position = time();
    let playbackState, rate;
    try {playbackState = player.getPlayerState(); rate = Math.max(0.25, Math.min(4, num(player.getPlaybackRate?.()) || 1));}
    catch {anchor = null; return;}
    const active = opened && playing && !activeQuestion && document.visibilityState !== 'hidden' &&
      (playbackState === 1 || allowEnded && playbackState === 0);
    if (active && anchor && state.duration > 0) {
      const wall = (now - anchor.wall) / 1000, delta = position - anchor.position;
      if (wall > 0 && wall <= 4.5 && delta > 0 && delta <= wall * Math.max(rate, anchor.rate) + 0.75) {
        state.ranges = merge([...state.ranges, [anchor.position, position]], state.duration); dirty = true;
      }
    }
    anchor = active ? {wall: now, position, rate} : null;
    renderStatus(); persist(false);
  }
  function stopSampling() {if (timer) clearInterval(timer); timer = null; anchor = null;}
  function dueQuestion(position) {
    if (completeSaved || readOnly()) return null;
    return questions.find(q => !answered(q) && (q.at === null ? state.ended : position + 0.05 >= q.at)) || null;
  }
  function element(tag, className, text) {
    const node = document.createElement(tag); if (className) node.className = className;
    if (text !== undefined) node.textContent = text; return node;
  }
  function finishIfEligible() {
    if (!eligible()) return false;
    state.complete = true; dirty = true;
    return persist(true) && completeSaved;
  }
  function firstUncovered() {
    const first = state.ranges[0];
    return first && first[0] <= 1.5 ? Math.min(first[1], Math.max(0, state.duration - 0.5)) : 0;
  }
  function continueVideo() {
    const q = activeQuestion;
    if (!q || !answered(q) || readOnly()) return;
    if (!persist(true)) return;
    if (q.at === null) {
      if (finishIfEligible()) {activeQuestion = null; panel.hidden = true; renderStatus(); return;}
      if (!eligible() && state.duration > 0 && fraction() < required) {
        activeQuestion = null; panel.hidden = true; questionFeedback = '';
        const target = firstUncovered(); anchor = null;
        try {player.seekTo(target, true);} catch {}
        message('Einige Videoabschnitte sind noch offen. Schau sie an und lass das Video bis zum Ende laufen.');
        player.playVideo(); return;
      }
    }
    activeQuestion = null; panel.hidden = true; questionFeedback = ''; renderStatus();
    const next = dueQuestion(time());
    if (next) {showQuestion(next); return;}
    player.playVideo();
  }
  function renderQuestion() {
    const q = activeQuestion; if (!q) {panel.hidden = true; return;}
    panel.replaceChildren(); panel.hidden = false;
    const index = questions.indexOf(q) + 1;
    panel.append(element('p', 'video-question-kicker', `Videopause · Frage ${index} von ${questions.length}`));
    const heading = element('h3', '', q.question); heading.id = 'orientation-video-question-heading';
    panel.append(heading); panel.setAttribute('aria-labelledby', heading.id);
    const form = element('form', 'video-question-form'), options = element('fieldset', 'video-question-options');
    options.append(element('legend', 'sr-only', 'Wähle die passende Antwort.'));
    for (const option of q.options) {
      const label = element('label', 'video-question-option'), input = element('input');
      input.type = 'radio'; input.name = 'orientation-video-answer'; input.value = option.id;
      input.checked = state.answers[q.id] === option.id;
      input.disabled = answered(q) || readOnly();
      label.append(input, element('span', '', option.text)); options.append(label);
    }
    form.append(options);
    const feedback = element('p', 'video-question-feedback'); feedback.setAttribute('role', 'status');
    feedback.textContent = answered(q) ? q.feedback : questionFeedback;
    feedback.hidden = !feedback.textContent; form.append(feedback);
    if (answered(q)) {
      const button = element('button', 'button primary', q.at === null ?
        (fraction() >= required ? 'Videoauftrag abschließen' : 'Fehlende Abschnitte ansehen') : 'Video fortsetzen');
      button.type = 'button'; button.dataset.videoQuestionContinue = ''; button.disabled = readOnly();
      button.addEventListener('click', continueVideo); form.append(button);
    } else {
      const button = element('button', 'button primary', 'Antwort prüfen'); button.type = 'submit';
      button.dataset.videoQuestionCheck = ''; button.disabled = readOnly(); form.append(button);
      form.addEventListener('submit', event => {
        event.preventDefault(); if (readOnly() || !activeQuestion || answered(q)) return;
        const selected = form.querySelector('input[name="orientation-video-answer"]:checked');
        if (!selected) {feedback.hidden = false; feedback.textContent = 'Wähle zuerst eine Antwort.'; return;}
        state.answers[q.id] = selected.value; state.attempts[q.id] = Math.min(100000, (state.attempts[q.id] || 0) + 1);
        dirty = true;
        const correct = selected.value === q.correct;
        questionFeedback = correct ? q.feedback : `Noch nicht passend. ${q.hint || 'Überprüfe die Zusammenhänge und versuche es erneut.'}`;
        const saved = persist(true);
        renderQuestion();
        if (!saved) {
          const note = panel.querySelector('.video-question-feedback');
          if (note) {note.hidden = false; note.textContent = 'Deine Antwort konnte noch nicht gespeichert werden. Versuche es über die Schaltfläche erneut.';}
        }
      });
    }
    panel.append(form); renderStatus();
  }
  function showQuestion(q) {
    if (!q || readOnly()) return false;
    activeQuestion = q; questionFeedback = '';
    playing = false; stopSampling();
    try {player?.pauseVideo?.();} catch {}
    persist(true); renderQuestion();
    panel.scrollIntoView?.({block: 'nearest', behavior: 'smooth'});
    return true;
  }
  function enforceQuestion() {
    if (readOnly() || completeSaved) return false;
    if (activeQuestion) {try {player.pauseVideo();} catch {} playing = false; stopSampling(); return true;}
    const q = dueQuestion(time()); return q ? showQuestion(q) : false;
  }
  function startSampling() {
    if (!timer) timer = setInterval(() => {sample(false); enforceQuestion();}, 1000);
  }
  function onPlay() {
    if (!ready) return;
    if (activeQuestion) {renderQuestion(); return;}
    if (!enforceQuestion()) player.playVideo();
  }
  function skipVideo() {
    if (readOnly() || completeSaved) return;
    if (player) sample(false);
    state.skipped = true; dirty = true;
    if (!persist(true) || P.read().ov?.skipped !== true) return;
    playing = false; stopSampling();
    try {player?.pauseVideo?.();} catch {}
    // Stay in the same Moodle player and learner session. Skip also works before
    // the YouTube API has loaded or when the remote player is unavailable.
    let owner = window;
    for (let depth = 0; owner && depth < 10; depth++) {
      try {
        const host = owner.SOZ_SCORM;
        const target = owner.document?.querySelector('[data-scorm-frame]');
        if (host && target && typeof host.read === 'function' && typeof host.update === 'function') {
          const next = host.read(); next.b = 'handlungssituation.html';
          if (host.update(next) === true) target.src = 'handlungssituation.html';
          else message('Der Seitenwechsel konnte noch nicht gespeichert werden. Versuche es erneut.');
          return;
        }
        if (owner.parent === owner) break;
        owner = owner.parent;
      } catch {break;}
    }
    window.location.assign('handlungssituation.html');
  }
  skip?.addEventListener('click', skipVideo);
  play?.addEventListener('click', onPlay);
  pause?.addEventListener('click', () => {if (!ready) return; sample(false); player.pauseVideo(); playing = false; stopSampling(); persist(true);});
  back?.addEventListener('click', () => {
    if (!ready) return; sample(false); const target = Math.max(0, time() - 10); anchor = null;
    player.seekTo(target, true); if (activeQuestion) player.pauseVideo();
  });
  captions?.addEventListener('click', () => {
    if (!ready) return;
    try {
      if (captionsOn) player.unloadModule?.('captions'); else player.loadModule?.('captions');
      captionsOn = !captionsOn; captions.setAttribute('aria-pressed', String(captionsOn));
    } catch {message('Untertitel sind für dieses Video derzeit nicht verfügbar.');}
  });
  volume?.addEventListener('input', () => {
    if (!ready) return;
    const value = Math.max(0, Math.min(100, num(volume.value)));
    try {player.setVolume(value); if (value === 0) player.mute?.(); else player.unMute?.();} catch {}
  });
  controls.forEach(c => {c.disabled = true;}); panel.hidden = true;
  renderStatus();
  // An already confirmed result must not depend on loading the player again.
  if (completeSaved && !readOnly() && !P.read().o) {dirty = true; persist(true);}
  function initialize() {
    if (!opened || initialized || !window.YT?.Player) return;
    initialized = true;
    player = new window.YT.Player(frame, {events: {
      onReady() {
        ready = true; controls.forEach(c => {c.disabled = false;}); duration();
        if (completeSaved) {
          if (!readOnly() && !P.read().o) {dirty = true; persist(true);}
          renderStatus(); return;
        }
        const resume = firstUncovered();
        if (resume > 1 && resume < state.duration - 1) {try {player.seekTo(resume, true);} catch {}}
        renderStatus(); persist(true);
        const due = dueQuestion(Math.max(resume, time()));
        if (due) showQuestion(due);
        else if (state.ended && allAnswered()) {
          const last = [...questions].reverse().find(q => q.at === null);
          if (last) showQuestion(last);
        }
      },
      onStateChange(event) {
        if (event.data === 1) {
          if (!opened) {player.pauseVideo(); playing = false; stopSampling(); return;}
          if (enforceQuestion()) return;
          playing = true; anchor = null; sample(false); startSampling();
        } else if (event.data === 0) {
          sample(true); playing = false; stopSampling();
          if (readOnly() || completeSaved) return;
          state.ended = true; dirty = true;
          // The actual end event is committed before presenting the final check.
          if (!persist(true)) return;
          const q = dueQuestion(state.duration);
          if (q) showQuestion(q); else {finishIfEligible(); renderStatus();}
        } else {
          sample(false); playing = false; stopSampling(); persist(true);
        }
      },
      onError(event) {
        ready = false; controls.forEach(c => {c.disabled = true;}); stopSampling(); playing = false; persist(true);
        message(event.data === 100 ? 'Das Video ist derzeit nicht verfügbar. Bitte informiere deine Lehrkraft.' :
          'Das Video konnte nicht geladen werden. Prüfe deine Verbindung und informiere bei Bedarf deine Lehrkraft.');
      }
    }});
  }
  function loadPlayer() {
    if (apiRequested) {initialize(); return;}
    apiRequested = true;
    const url = new URL('https://www.youtube-nocookie.com/embed/' + encodeURIComponent(cfg.videoId));
    for (const [key, value] of Object.entries({enablejsapi: '1', playsinline: '1', rel: '0', controls: '1', disablekb: '0'})) url.searchParams.set(key, value);
    if (/^https?:$/.test(location.protocol)) url.searchParams.set('origin', location.origin);
    frame.src = url.href; frame.referrerPolicy = 'strict-origin-when-cross-origin'; frame.setAttribute('allowfullscreen', '');
    message('Videoplayer wird geladen.');
    if (window.YT?.Player) initialize();
    else {
      const previous = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function(...args) {try {if (typeof previous === 'function') previous.apply(this, args);} finally {initialize();}};
      if (!document.querySelector('script[src="https://www.youtube.com/iframe_api"]')) {
        const script = document.createElement('script'); script.src = 'https://www.youtube.com/iframe_api'; script.async = true;
        script.onerror = () => message('Der Videoplayer konnte nicht geladen werden. Prüfe deine Verbindung und lade diese Seite erneut.');
        document.head.appendChild(script);
      }
    }
  }
  function openVideo() {
    opened = true;
    if (expanded) expanded.hidden = false;
    if (preview) {preview.hidden = true; preview.setAttribute('aria-expanded', 'true');}
    loadPlayer();
    close?.focus?.();
    expanded?.scrollIntoView?.({block: 'nearest', behavior: 'smooth'});
  }
  function closeVideo() {
    if (ready) {sample(false); try {player.pauseVideo();} catch {}}
    playing = false; stopSampling(); persist(true); opened = false;
    if (expanded) expanded.hidden = true;
    if (preview) {preview.hidden = false; preview.setAttribute('aria-expanded', 'false'); preview.focus?.();}
  }
  preview?.addEventListener('click', openVideo);
  close?.addEventListener('click', closeVideo);
  if (!preview) loadPlayer();
  else if (/^#orientation-video(?:-player|-expanded)?$/.test(location.hash || '')) openVideo();
  window.addEventListener('hashchange', () => {if (/^#orientation-video(?:-player|-expanded)?$/.test(location.hash || '')) openVideo();});
  document.addEventListener('visibilitychange', () => {
    anchor = null;
    if (document.visibilityState === 'hidden') {stopSampling(); persist(true);}
    else if (playing && !activeQuestion) {sample(false); startSampling();}
  });
  window.addEventListener('pagehide', () => {sample(false); persist(true); stopSampling();});
})();
