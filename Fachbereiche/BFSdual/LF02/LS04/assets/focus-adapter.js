// Adapt the unmodified form master's previews to learner-selected paths.
(() => {
  'use strict';
  const cards = [...document.querySelectorAll('.assignment-frame')];
  if (!cards.length) return;
  function visible(card) {
    return !card.closest('[hidden]');
  }
  for (const card of cards) {
    const summary = card.querySelector('.task-summary');
    const title = card.querySelector('.assignment-title')?.textContent;
    if (!summary) continue;
    summary.setAttribute('aria-label', 'Aufgabe bearbeiten: ' + (title || card.dataset.taskNumber));
    card.querySelector('.focus-ai-help')?.remove();
    // Inputs for path selection and saved responses belong to the editable
    // task only. A preview must never submit or create duplicate identifiers.
    const preview = card.querySelector('.task-original-preview');
    if (preview) {
      preview.querySelectorAll('[id]').forEach(node => node.removeAttribute('id'));
      preview.querySelectorAll('input, textarea, select, button, form').forEach(node => node.remove());
      preview.querySelectorAll('label[for]').forEach(node => node.removeAttribute('for'));
      preview.querySelectorAll('[data-response],[data-done]').forEach(node => {delete node.dataset.response; delete node.dataset.done;});
    }
    // Simultaneously suppress unselected variants and support common tasks
    // on both sides of the branching task.
    const next = card.querySelector('.focus-next');
    if (!next) continue;
    next.addEventListener('click', event => {
      event.stopImmediatePropagation();
      if (next.disabled) return;
      const following = cards.slice(cards.indexOf(card) + 1).find(visible);
      window.SOZ_TASK_FOCUS?.close(false);
      if (following) following.querySelector('.task-summary')?.click();
    }, true);
  }
})();
