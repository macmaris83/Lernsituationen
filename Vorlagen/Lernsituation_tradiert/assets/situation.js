(() => {
  'use strict';
  const root = document.querySelector('[data-situation-quiz]');
  if (!root) return;
  let questions;
  try {questions = JSON.parse(root.querySelector('script[type="application/json"]').textContent);} catch {return;}
  const P = window.SOZ_PROGRESS, K = window.SOZ_PROGRESS_CORE, meta = window.SOZ_PROGRESS_META, UI = window.SOZ_POINTS_UI;
  const completed = new Set(), progress = root.querySelector('[data-quiz-progress]');
  const rules = document.createElement('details');
  rules.className = 'point-rules';
  rules.innerHTML = '<summary>Wie zählen die XP?</summary><p>Nur richtig geprüfte Antworten bringen XP. Nach einer falschen Erstprüfung oder einem zuvor geöffneten Hinweis sind 60 Prozent der XP dieser Frage möglich. Ein Hinweis nach einer richtig geprüften Antwort kostet nichts. Weitere Versuche erhöhen die maximale Punktzahl nicht.</p><p>Arbeitsaufträge: 25 XP · Handlungssituation: 15 XP'+(meta.flashcard?' · Fachbegriffe: 60 XP':'')+'. Der Abschluss erfolgt über „Lernpaket abschließen“, wenn alle erforderlichen Aufgaben und Checks erledigt sind.</p>';
  root.prepend(rules);
  function count() {
    progress.textContent = completed.size === questions.length ? `${questions.length} von ${questions.length} Prüffragen richtig. Informieren ist freigeschaltet.` : `${completed.size} von ${questions.length} Prüffragen richtig.`;
    for (const row of root.querySelectorAll('[data-quiz-question]')) row.querySelector('[data-quiz-submit]').textContent = 'Antwort prüfen';
  }
  for (const panel of root.querySelectorAll('[data-quiz-question]')) {
    const q = questions.find(q => q.id === panel.dataset.quizQuestion);
    if (!q) continue;
    const feedback = panel.querySelector('[data-quiz-feedback]'), details = panel.closest('details'), summary = details.querySelector('summary');
    const submit = panel.querySelector('[data-quiz-submit]');
    panel.querySelector('[data-quiz-reset]')?.addEventListener('click',()=>{if(!P.readOnly){P.quiz(q.id,null,false);render();}});
    const point = document.createElement('span');
    point.dataset.questionPoints = q.id;
    submit.after(point);
    const hint = panel.querySelector('.quiz-hint'), hintSummary = hint?.querySelector('summary');
    const hintPoint = document.createElement('span');
    if (hintSummary) {hintPoint.dataset.hintPoints = q.id;hintSummary.append(hintPoint);hintSummary.title = 'Ein Hinweis vor der richtigen Prüfung begrenzt die XP dieser Frage auf 60 Prozent.';}
    function render() {
      const p = P.read(), stored = p.q[q.id], checked = stored?.[1] === true, value = stored?.[0];
      const correct = checked && value === q.correct;
      const valuePoints = K.situationValue(p, meta, q.id);
      const earnedBadge = UI.badge(correct ? valuePoints : 0, correct, correct ? 'Für diese richtig geprüfte Antwort gutgeschrieben.' : checked ? 'Falsche Antwort: 0 XP. Es wurde nichts gutgeschrieben.' : 'Noch keine richtig geprüfte Antwort: 0 XP.');
      if (!correct) {const label = earnedBadge.querySelector('span');if (label) label.textContent = '0 XP';}
      point.replaceChildren(earnedBadge);
      if (hintSummary) {const possible = UI.badge(correct ? valuePoints : (p.qh?.[q.id]||p.qf?.[q.id]===false?valuePoints:Math.round(valuePoints*0.6*100)/100), false, correct ? 'Bereits richtig gelöst; der Hinweis kostet jetzt nichts.' : 'Mit Hinweis sind 60 Prozent der XP dieser Frage möglich.');const label = possible.querySelector('span');if (label) label.textContent = correct ? valuePoints + ' XP' : 'max. ' + (p.qh?.[q.id]||p.qf?.[q.id]===false?valuePoints:Math.round(valuePoints*0.6*100)/100) + ' XP';hintPoint.replaceChildren(possible);}
      for (const input of panel.querySelectorAll('input[type="radio"]')) {input.checked = input.value === value;input.disabled = P.readOnly;}
      submit.disabled = P.readOnly || checked;
      feedback.hidden = !checked;
      if (checked) {
        const option = q.options.find(option => option.value === value);
        feedback.dataset.result = correct ? 'correct' : 'wrong';
        feedback.textContent = (correct ? 'Das passt zur Handlungssituation. ' : '0 XP. Diese Antwort passt noch nicht. ') + (option?.feedback || '');
      } else {feedback.textContent = '';delete feedback.dataset.result;}
      if (correct) completed.add(q.id);else completed.delete(q.id);
      details.classList.toggle('quiz-is-complete', correct);
      panel.closest('details').querySelector('[data-quiz-marker]').textContent = '';
      summary.setAttribute('aria-label', summary.textContent.trim() + (correct ? ' · Richtig gelöst' : ' · Noch nicht gelöst'));
      count();
    }
    if (hintSummary) hintSummary.addEventListener('click', event => {
      if (hint.open || P.readOnly) return;
      event.preventDefault();
      if (P.hint(q.id)) {hint.open = true;render();}
      else {feedback.hidden = false;feedback.dataset.result = 'empty';feedback.textContent = 'Der Hinweis konnte nicht gespeichert werden. Bitte erneut versuchen.';}
    });
    for (const input of panel.querySelectorAll('input[type="radio"]')) input.addEventListener('change', () => {P.quiz(q.id, input.value, false);render();});
    submit.addEventListener('click', () => {
      const selected = panel.querySelector('input[type="radio"]:checked');
      if (!selected) {feedback.hidden = false;feedback.dataset.result = 'empty';feedback.textContent = 'Wählt zunächst eine Antwort aus.';return;}
      const before = K.grading(P.read(), meta).points;
      if (!P.quiz(q.id, selected.value, true)) {render();feedback.hidden = false;feedback.dataset.result = 'empty';feedback.textContent = 'Speichern fehlgeschlagen. Bitte erneut prüfen.';return;}
      render();
      const gain = K.grading(P.read(), meta).points - before;
      if (gain > 0) UI.award(point, gain);

    });
    render();
  }
  count();
  root.dataset.quizReady = 'true';
})();
