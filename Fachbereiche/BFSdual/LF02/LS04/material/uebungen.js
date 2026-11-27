(() => {
  'use strict';

  function prepareExercises() {
    for (const area of document.querySelectorAll('[data-exercise]')) {
      const cards = Array.from(area.querySelectorAll('fieldset[data-answer]'));
      const progress = area.querySelector('.material-check-progress');
      const isCheck = area.dataset.exercise === 'm8';
      const saved = isCheck ? window.GB?.getCheck?.() : null;
      const values = cards.map((card, index) => {
        const answer = Array.isArray(saved) ? saved[index] : null;
        return Number.isInteger(answer) && answer >= 0 && answer < card.querySelectorAll('input[type="radio"]').length ? answer : null;
      });

      function showCard(card, value) {
        const feedback = card.querySelector('.answer-feedback');
        const link = card.querySelector('.quiz-source');
        const isCorrect = value === Number(card.dataset.answer);
        feedback.textContent = value === null ? '' : (isCorrect ? 'Richtig. ' : 'Prüfe deine Wahl noch einmal. ') + card.dataset.feedback;
        feedback.dataset.result = value === null ? '' : isCorrect ? 'correct' : 'retry';
        link.hidden = value === null;
      }

      function countAnswers() {
        const completed = values.filter(v => v !== null).length;
        progress.textContent = completed + ' von ' + cards.length + (isCheck ? ' Begriffen bearbeitet' : ' Fragen bearbeitet');
      }

      function save() {
        if (isCheck) window.GB?.saveCheck?.(values.slice());
      }

      cards.forEach((card, index) => {
        const radios = card.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => {
          radio.checked = values[index] === Number(radio.value);
          radio.addEventListener('change', () => {
            if (!radio.checked) return;
            values[index] = Number(radio.value);
            showCard(card, values[index]);
            countAnswers();
            save();
          });
        });
        showCard(card, values[index]);
      });
      countAnswers();

      area.querySelector('.material-reset').addEventListener('click', () => {
        if (values.every(v => v === null)) return;
        if (isCheck && !window.confirm('Alle ausgewählten Antworten in diesem Fachbegriffscheck zurücksetzen?')) return;
        cards.forEach((card, index) => {
          values[index] = null;
          for (const el of card.querySelectorAll('input[type="radio"]')) el.checked = false;
          showCard(card, null);
        });
        countAnswers();
        save();
      });
    }
    if (location.hash) {
      const anchor = document.getElementById(decodeURIComponent(location.hash.slice(1)));
      if (anchor?.closest('details')) {
        anchor.closest('details').open = true;
        anchor.scrollIntoView();
      }
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', prepareExercises, {once: true});
  else prepareExercises();
})();
