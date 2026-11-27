/* Shared form 1.8.8: 100 XP from the existing checks; progress stays package-owned. */
(() => {
  'use strict';
  const K = window.SOZ_PROGRESS_CORE, meta = window.SOZ_PROGRESS_META;
  if (!K || typeof K.grading !== 'function' || K.grading.__xp100) return;
  const original = K.grading;
  // The older compatibility core has no term test: 25 task + 15 situation XP.
  // Allocate the same 5:3 ratio directly in hundredths, so item badges sum to 100.
  // Native 100-XP cores, their first-attempt rules and completion gates stay intact.
  const nativeMaximum = meta ? Number(original(K.initial(meta, 1), meta).maxPoints || 100) : 100;
  if (nativeMaximum === 40) {
    K.taskPoints = (data, id, mode = 1) => {
      const ids = Object.keys(data.tasks || {}).filter(key => data.tasks[key].mode === Number(mode));
      return K.sharePoints(62.5, ids.length, ids.indexOf(id));
    };
    K.situationValue = (state, data, id) => {
      const base = K.sharePoints(37.5, data.quiz.length, data.quiz.findIndex(question => question.id === id));
      const factor = state.qh?.[id] || state.qf?.[id] === false ? 0.6 : 1;
      return Math.round(base * factor * 100) / 100;
    };
  }
  const grading = function(state, data) {
    const grade = original.call(this, state, data);
    return {...grade, maxPoints: 100};
  };
  grading.__xp100 = true;
  K.grading = grading;
})();
(() => {
  'use strict';
  const format = n => Number(n || 0).toLocaleString('de-DE', {maximumFractionDigits: 2});
  const tier = n => n >= 90 ? 'gold' : n >= 75 ? 'silver' : n >= 50 ? 'bronze' : 'dark';
  const tierName = n => n >= 90 ? 'Gold' : n >= 75 ? 'Silber' : n >= 50 ? 'Bronze' : 'Start';
  const reduced = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const icon = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="m12 6 1.8 3.6 4 .6-2.9 2.8.7 4-3.6-1.9L8.4 17l.7-4-2.9-2.8 4-.6Z"/></svg>';
  function markup(points, earned = false, title = '') {
    const safeTitle = String(title).replace(/[&"<>]/g, c => ({'&':'&amp;','"':'&quot;','<':'&lt;','>':'&gt;'}[c]));
    return '<span class="point-badge' + (earned ? ' point-earned' : '') + '" title="' + safeTitle + '">' + icon + '<span>' + (earned ? '' : '+') + format(points) + ' XP</span></span>';
  }
  function badge(points, earned, title) {
    const template = document.createElement('template');
    template.innerHTML = markup(points, earned, title);
    return template.content.firstElementChild;
  }
  function award(anchor, points) {
    if (!anchor || !points) return;
    document.querySelectorAll('.point-reward').forEach(el => el.remove());
    const popup = document.createElement('span');
    popup.className = 'point-reward';
    popup.textContent = '+' + format(points) + ' XP';
    popup.setAttribute('role', 'status');
    const rect = anchor.getBoundingClientRect();
    popup.style.left = Math.max(8, Math.min(innerWidth - 150, rect.left)) + 'px';
    popup.style.top = Math.max(10, Math.min(innerHeight - 44, rect.top - 30)) + 'px';
    document.body.append(popup);
    setTimeout(() => popup.remove(), reduced() ? 1600 : 1250);
  }
  let positionObserver = null;
  function mount() {
    // Keep the compact score at the top right of the current learning view.
    // The SCORM host keeps only the persistent unfinished-test reminder.
    if (document.querySelector('[data-scorm-frame]')) return null;
    const page = document.body.dataset.page || '';
    if (document.body.dataset.teacher || page === 'druckansicht.html') return null;
    const focus = document.body.classList.contains('task-focus')
      ? document.querySelector('.task-accordion[open] .task-focus-panel') : null;
    const navigation = document.querySelector('.navigation, .b-phase-overview');
    const heading = navigation?.querySelector('.nav-heading .eyebrow');
    if (heading && heading.textContent !== 'Phasenübersicht') heading.textContent = 'Phasenübersicht';
    const target = focus || (/^m\d+\.html$/.test(page) ? document.querySelector('.main') : navigation);
    if (!target) return null;
    let row = document.querySelector('[data-phase-points]');
    if (!row) {
      row = document.createElement('div');
      row.className = 'phase-points-row no-print';
      row.dataset.phasePoints = '';
    }
    if (row.parentElement !== target) target.prepend(row);
    let el = row.querySelector('[data-point-float]');
    if (!el) {
      el = document.createElement('aside');
      el.className = 'point-float no-print';
      el.dataset.pointFloat = '';
      el.innerHTML = '<div class="points-battery" role="progressbar" aria-label="Aktueller SCORM-Punktestand" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span class="points-battery-track"><span class="points-battery-fill"></span></span><strong class="points-battery-label">0 / 100 XP</strong></div><span class="points-live sr-only" aria-live="polite" aria-atomic="true"></span>';
      row.append(el);
    }
    if (!positionObserver && window.MutationObserver) {
      positionObserver = new MutationObserver(() => mount());
      positionObserver.observe(document.body, {attributes:true, attributeFilter:['class']});
    }
    return el;
  }
  function render(grade, animate = true) {
    const el = mount();
    if (!el) return;
    const maximum=grade.maxPoints||100;const points = Math.max(0, Math.min(maximum, Number(grade.points) || 0));
    const last = el.dataset.points === undefined ? null : Number(el.dataset.points);
    const track = el.querySelector('.points-battery');
    el.dataset.points = String(points);
    el.dataset.tier = tier(points/maximum*100);
    track.setAttribute('aria-valuemax',String(maximum));track.setAttribute('aria-valuenow', String(points));
    track.setAttribute('aria-valuetext', format(points) + ' von '+maximum+' XP; ' + tierName(points/maximum*100));
    el.querySelector('.points-battery-fill').style.width = (points/maximum*100) + '%';
    el.querySelector('.points-battery-label').textContent = format(points) + ' / '+maximum+' XP';
    el.title = 'XP aus dem gespeicherten Lernstand: '+format(points)+' / '+maximum;
    if (animate && last !== null && points > last) {
      el.querySelector('.points-live').textContent = '+' + format(points - last) + ' XP. Jetzt ' + format(points) + ' von '+maximum+' XP.';
      if (!reduced() && el.animate) el.animate([{transform:'scale(1)'},{transform:'scale(1.04)'},{transform:'scale(1)'}], {duration:420});
    }
  }
  window.SOZ_POINTS_UI = {format, tier, markup, badge, award, render};
})();
