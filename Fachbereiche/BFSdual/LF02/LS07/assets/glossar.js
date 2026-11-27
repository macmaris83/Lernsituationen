(() => {
  'use strict';
  const params = new URLSearchParams(location.search);
  const panel = document.querySelector('[data-glossary-panel]');
  const entrySlot = panel.querySelector('[data-glossary-entry]');
  const deck = document.querySelector('[data-glossary-deck]');
  const empty = document.querySelector('[data-glossary-empty]');
  const back = panel.querySelector('[data-glossary-back]');
  const folder = new URL('.', location.href);
  const preview = params.has('bfs-vorschau');
  const embedded = params.has('eingebettet') && window.parent !== window;

  function linkToSource() {
    const raw = params.get('from');
    // The link can only return to an HTML page inside this SCORM folder.
    if (!raw || raw.startsWith('/') || /^[a-z][a-z0-9+.-]*:/i.test(raw)) return null;
    let url;
    try {
      url = new URL(raw, folder);
      const pathname = decodeURIComponent(url.pathname);
      const base = decodeURIComponent(folder.pathname);
      if (url.origin !== folder.origin || !pathname.startsWith(base) ||
          !/^[^\\?#]+\.html$/.test(pathname.slice(base.length)) ||
          pathname.slice(base.length)==='ls-glossar.html') return null;
    } catch { return null; }
    if (preview) url.searchParams.set('bfs-vorschau', '1');
    return url;
  }

  const source = linkToSource();
  if (source) {
    back.href = source;
    back.hidden = false;
    // Browser history preserves the exact scroll position and current answers.
    // A copied or directly opened link still has an explicit return URL.
    back.addEventListener('click', event => {
      if (embedded) {
        event.preventDefault();
        window.parent.postMessage('bfs-glossar-schliessen', location.origin==='null'?'*':location.origin);
        return;
      }
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0 ||
          history.length <= 1 || !document.referrer) return;
      const ref = new URL(document.referrer);
      const expected = new URL(source);
      expected.searchParams.delete('glossarStelle');
      if (ref.origin === expected.origin && ref.pathname === expected.pathname) {
        event.preventDefault();
        history.back();
      }
    });
  }
  function closeEntry() {
    if (source) back.click();
    else if (typeof panel.close === 'function') panel.close();
    else panel.hidden = true;
  }
  panel.addEventListener('cancel', event => {
    event.preventDefault();
    closeEntry();
  });
  panel.querySelector('[data-glossary-close]').addEventListener('click', closeEntry);
  if (embedded) document.addEventListener('keydown',event=>{
    if (event.key==='Escape') closeEntry();
  });

  let term;
  try { term = decodeURIComponent(location.hash.slice(1)); }
  catch { term = ''; }
  const entry = [...deck.children].find(card => card.id === term);
  if (!entry) return;

  deck.hidden = false;
  empty.hidden = true;
  entrySlot.append(entry);
  if (embedded) {
    document.body.dataset.glossaryEmbedded='';
    deck.hidden=true;
    panel.setAttribute('open','');
  } else if (typeof panel.showModal === 'function') {
    panel.showModal();
  } else {
    // Older webviews still show the same complete entry as an accessible card.
    panel.setAttribute('open', '');
    panel.classList.add('glossary-panel-fallback');
    deck.setAttribute('inert', '');
    deck.setAttribute('aria-hidden', 'true');
  }
  panel.querySelector('[data-glossary-close]').hidden = Boolean(source);
  entry.querySelector('h2')?.focus({preventScroll: true});
})();
