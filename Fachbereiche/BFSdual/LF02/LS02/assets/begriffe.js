(() => {
  'use strict';
  const cards = [...document.querySelectorAll('#check fieldset')];
  if (!cards.length) return;
  const previous = window.GB?.getCheck();
  const choices = Array.isArray(previous) && previous.length === cards.length ? [...previous] : Array(cards.length).fill(null);
  function draw(card, i) {
    const answer = choices[i], right = Number(card.dataset.right);
    for (const input of card.querySelectorAll('input')) input.checked = Number(input.value) === answer;
    const msg = card.querySelector('.quiz-reply');
    msg.textContent = answer === null ? '' : (answer === right ? 'Richtig. ' : 'Schau noch einmal auf den Begriff. ') + card.dataset.explain;
    card.dataset.result = answer === null ? '' : answer === right ? 'richtig' : 'offen';
  }
  function summary() {
    const missing = cards.filter((card, i) => choices[i] !== null && choices[i] !== Number(card.dataset.right));
    const viewed = choices.filter(x => x !== null).length;
    const text = viewed + ' von ' + cards.length + ' Begriffen bearbeitet.';
    document.getElementById('quiz-result').textContent = text + (missing.length ? ' Zum Nachschlagen: ' + missing.map(c => c.querySelector('legend').textContent.replace(/^\d+\. /,'')).join(', ') + '.' : '');
  }
  cards.forEach((card,i) => {
    draw(card,i);
    card.addEventListener('change', event => {
      if (!event.target.matches('input[type="radio"]')) return;
      choices[i] = Number(event.target.value);
      window.GB?.saveCheck(choices);
      draw(card,i);summary();
    });
  });
  document.getElementById('reset-quiz').addEventListener('click',() => { choices.fill(null);window.GB?.saveCheck(choices);cards.forEach(draw);summary(); });
  summary();
})();
