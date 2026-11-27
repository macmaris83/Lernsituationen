(() => {
  'use strict';
  const root=new URL('../',document.currentScript.src);
  const isOffice=typeof window.BFS_OFFICE_PATH==='function';
  const preview=window.BFS_EDITOR?.preview;
  const valid=value=>['A','B','C'].includes(value);
  const destination=new URL(isOffice?'index.html#durchfuehren':'durchfuehren.html',root);
  const choose=new URL(isOffice?'index.html#entscheiden':'entscheiden.html',root);

  function selected() {
    if (isOffice) return window.BFS_OFFICE_PATH();
    if (window.GB) return window.GB.getPath();
    try {
      const session=window.parent.GlobalBikeSCORMSession;
      if (session) return session.read().path;
    } catch { /* The package may be opened directly. */ }
    try {
      const id=window.GB_PACKAGE_ID || window.BFS_EDITOR?.id;
      return JSON.parse(localStorage.getItem(id+':'+root.pathname+(preview?':editor-preview':'')) || 'null')?.path;
    } catch { return ''; }
  }
  function matches(target) {
    return target.origin===destination.origin && target.pathname===destination.pathname &&
      (!isOffice || target.hash===destination.hash);
  }
  function refresh() {
    const path=selected();
    const available=valid(path);
    if (!available && !preview && matches(new URL(location.href))) {
      choose.searchParams.set('wahl-erforderlich','1');
      location.replace(choose.href);
      return;
    }
    for (const anchor of document.querySelectorAll('a[href]')) {
      if (!matches(new URL(anchor.href,location.href))) continue;
      if (available) anchor.removeAttribute('aria-disabled');
      else anchor.setAttribute('aria-disabled','true');
      if (available) anchor.removeAttribute('title');
      else anchor.title='Wähle zuerst ein Lernpaket in Entscheiden.';
      anchor.classList.toggle('bfs-path-locked',!available);
    }
    document.querySelectorAll('[data-bfs-choice-status]').forEach(node=>{
      node.textContent=available?'Lernpaket '+path+' gewählt.':'Wähle A, B oder C, um „Durchführen“ freizuschalten.';
    });
  }
  document.addEventListener('click',event=>{
    const anchor=event.target.closest('a[href]');
    if (!anchor || valid(selected()) || !matches(new URL(anchor.href,location.href))) return;
    event.preventDefault();
    if (anchor.closest('.page-turn') && !isOffice) document.querySelector('.assignment-frame[data-bfs-choice] .task-summary')?.focus();
  },true);
  window.addEventListener('bfs-progress',refresh);
  window.addEventListener('bfs-office-progress',refresh);
  window.addEventListener('hashchange',refresh);
  window.addEventListener('pageshow',refresh);
  refresh();
})();
