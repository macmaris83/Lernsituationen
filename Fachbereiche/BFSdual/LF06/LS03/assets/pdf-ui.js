(() => {
  'use strict';
  const valid = path => ['A', 'B', 'C'].includes(path);
  const printButton = document.querySelector('[data-print-document]');
  if (printButton) {
    const choice = document.querySelector('#pdf-lernweg');
    const initial = new URLSearchParams(location.search).get('lernweg');
    choice.value = valid(initial) ? initial : '';
    function showPath() {
      document.querySelectorAll('[data-pdf-path]').forEach(section => {
        section.hidden = Boolean(choice.value && choice.value !== section.dataset.pdfPath);
      });
    }
    showPath();
    choice.addEventListener('change', showPath);
    printButton.addEventListener('click', async () => {
      await Promise.all(Array.from(document.images, image => image.decode().catch(() => {})));
      window.print();
    });
    return;
  }

  document.addEventListener('click', async event => {
    const link = event.target.closest('.bfs-phase-export a[download]');
    if (!link || event.defaultPrevented || event.ctrlKey || event.metaKey ||
        !navigator.share || !navigator.canShare || !/^https?:$/.test(location.protocol)) return;
    const name = new URL(link.href).pathname.split('/').at(-1);
    const sample = new File([], name, { type: 'application/pdf' });
    if (!navigator.canShare({ files: [sample] })) return;
    event.preventDefault();
    try {
      const response = await fetch(link.href);
      if (!response.ok) throw new Error('PDF konnte nicht geladen werden');
      const file = new File([await response.blob()], name, { type: 'application/pdf' });
      await navigator.share({ files: [file], title: 'GoodNotes-Export' });
    } catch (error) {
      if (error.name === 'AbortError') return;
      const fallback = document.createElement('a');
      fallback.href = link.href;
      fallback.download = name;
      document.body.append(fallback);
      fallback.click();
      fallback.remove();
    }
  });

  const office = document.querySelector('[data-office-exports]');
  function path() {
    const value = office ? window.BFS_OFFICE_PATH?.() : window.GB?.getPath();
    return valid(value) ? value : '';
  }
  for (const link of document.querySelectorAll('[data-document-pdf]')) {
    link.addEventListener('click', () => {
      const url = new URL(link.getAttribute('href'), location.href);
      if (path()) url.searchParams.set('lernweg', path());
      else url.searchParams.delete('lernweg');
      link.href = url.href;
    });
  }

  if (office) {
    const phases = ['informieren', 'planen', 'entscheiden', 'durchfuehren', 'bewerten', 'reflektieren'];
    const button = office.querySelector('[download]');
    const pick = office.querySelector('[data-export-pick]');
    function showPhase() {
      const phase = location.hash.slice(1);
      office.hidden = !phases.includes(phase);
      const needsPath = phase === 'durchfuehren' && !path();
      button.hidden = needsPath;
      pick.hidden = !needsPath;
      if (!office.hidden && !needsPath) {
        const suffix = phase === 'durchfuehren' ? '-' + path() : '';
        button.href = 'pdf/GoodNotes-LS-6.9-' + phase + suffix + '.pdf';
      }
    }
    showPhase();
    window.addEventListener('hashchange', showPhase);
    return;
  }
  const phaseBox = document.querySelector('[data-phase-exports]');
  if (!phaseBox) return;
  const pick = phaseBox.querySelector('[data-export-pick]');
  if (pick) pick.hidden = Boolean(path());
})();
