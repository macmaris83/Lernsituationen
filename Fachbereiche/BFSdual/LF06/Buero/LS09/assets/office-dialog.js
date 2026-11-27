(() => {
  'use strict';
  if (typeof HTMLDialogElement === 'undefined' || !HTMLDialogElement.prototype.showModal) return;
  const panel=document.createElement('dialog');
  panel.className='office-glossary-panel';
  panel.setAttribute('aria-label','Fachbegriff nachschlagen');
  const frame=document.createElement('iframe');
  frame.title='Fachbegriff und Erklärung';
  panel.append(frame);
  document.body.append(panel);
  let source;
  document.addEventListener('click',event=>{
    const link=event.target.closest('a[href]');
    if (!link || event.defaultPrevented || event.button!==0 || event.ctrlKey ||
        event.metaKey || event.shiftKey || event.altKey) return;
    const url=new URL(link.href,location.href);
    if (url.origin!==location.origin || url.pathname!==new URL('ls-glossar.html',location.href).pathname || !url.hash) return;
    event.preventDefault();
    source=link;
    url.searchParams.set('eingebettet','1');
    frame.src=url.href;
    panel.showModal();
  });
  window.addEventListener('message',event=>{
    if (event.source===frame.contentWindow && event.origin===location.origin &&
        event.data==='bfs-glossar-schliessen' && panel.open) panel.close();
  });
  panel.addEventListener('close',()=>{
    frame.removeAttribute('src');
    source?.focus({preventScroll:true});
  });
})();
