(() => {
  'use strict';
  const area=document.querySelector('[data-office-pilot]');
  const button=area?.querySelector('button');
  if (!button) return;
  const phases=new Set(['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren']);
  function update() {area.hidden=!phases.has(location.hash.slice(1));}
  update();window.addEventListener('hashchange',update);
  button.addEventListener('click',()=>{
    let dialog=document.querySelector('.ais-help-dialog');
    if (!dialog) {
      dialog=document.createElement('dialog');
      dialog.className='ais-help-dialog';
      dialog.setAttribute('aria-label','KI-Hilfe · Löppt-Pilot');
      const head=document.createElement('header');
      head.className='ais-help-heading';
      const title=document.createElement('strong');
      title.textContent='KI-Hilfe · Löppt-Pilot';
      const close=document.createElement('button');close.type='button';close.textContent='Schließen';
      close.addEventListener('click',()=>dialog.close());
      head.append(title,close);
      const note=document.createElement('p');note.className='ais-help-note';note.textContent='Hilfe zur Selbsthilfe · Deine Lösung erarbeitest du selbst.';
      const frame=document.createElement('iframe');frame.className='ais-help-frame';frame.title='AIS-Chat – KI-Hilfe';frame.src=area.dataset.pilotUrl;
      dialog.append(head,note,frame);document.body.append(dialog);
    }
    if (!dialog.open) dialog.showModal();
  });
})();
