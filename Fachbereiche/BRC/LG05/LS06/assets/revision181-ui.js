/* Version 1.8.1: concise lesson headings and per-task orientation time. */
(() => {
  'use strict';
  const lesson = window.SOZPAED;
  if (!lesson) return;
  const title = String(lesson.title || '').trim();
  if (title) {
    for (const label of document.querySelectorAll('.lesson-content > .hero > .eyebrow')) {
      label.textContent = title;
      label.classList.add('lesson-name');
    }
  }
  // Imported teacher overrides may still carry an obsolete phase-level clock.
  // Only the timer belonging to the open task is displayed.
  document.querySelectorAll('.phase-clock').forEach(clock => clock.remove());
  document.querySelectorAll('.focus-timer-caption').forEach(caption => caption.remove());
})();
