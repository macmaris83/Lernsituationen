(()=>{
 'use strict';
 const P=window.SOZ_PROGRESS,K=window.SOZ_PROGRESS_CORE,M=window.SOZ_PROGRESS_META;
 if(!P||!K||!M||document.body.dataset.teacher||document.body.dataset.page==='druckansicht.html'||document.querySelector('[data-scorm-frame]'))return;
 let busy=false,notice='';
 const format=n=>Number(n||0).toLocaleString('de-DE',{maximumFractionDigits:2});
 const endPage=document.body.dataset.page==='reflektieren.html';
 function message(){
  if(notice)return notice;
  if(P.completed)return P.storageMessage;
  const p=P.read(),g=K.grading(p,M);
  if(K.allComplete(p,M))return 'Alle Aufgaben und Checks sind erledigt. Du kannst das Lernpaket abschließen.';
  const remaining=[];
  if(!p.o)remaining.push('Orientierung bestätigen');
  if(g.tasksDone<g.tasksTotal)remaining.push((g.tasksTotal-g.tasksDone)+' Aufgaben erledigen');
  if(!K.quizComplete(p,M))remaining.push('Handlungssituationscheck abschließen');
  if(!K.flashcardComplete(p,M))remaining.push('Fachbegriffe-Check abschließen');
  return 'Noch offen: '+remaining.join(' · ')+'.';
 }
 function finish(){
  if(busy)return;
  busy=true;notice='';paint();
  try{
   const ok=typeof P.complete==='function'&&P.complete();
   if(!ok)notice=P.storageMessage||'Der Abschluss konnte nicht gespeichert werden. Bitte erneut versuchen.';
  }catch{notice='Der Abschluss konnte nicht gespeichert werden. Bitte erneut versuchen.';}
  busy=false;paint();
 }
 function paint(){
  const p=P.read(),g=K.grading(p,M);
  window.SOZ_POINTS_UI?.render(g,true);
  const row=document.querySelector('[data-phase-points]');
  if(row){
   row.setAttribute('aria-label','XP und Punkte dieser Lernsituation');
   let summary=row.querySelector('[data-package-score-summary]');
   if(!summary){summary=document.createElement('div');summary.className='package-score-summary';summary.dataset.packageScoreSummary='';row.append(summary);}
   const text='Aufgaben '+format(g.taskPoints)+'/25 · Handlungssituation '+format(g.situationPoints)+'/15 · Begriffscheck '+format(g.termPoints)+'/60';
   if(summary.textContent!==text)summary.textContent=text;
   let label=row.querySelector('[data-package-score-label]');
   if(!label){label=document.createElement('strong');label.className='package-score-label';label.dataset.packageScoreLabel='';label.textContent='Deine XP';row.prepend(label);}
   let status=row.querySelector('[data-package-completion-status]');
   if(endPage||P.completed){
    if(!status){status=document.createElement('p');status.className='package-completion-status';status.dataset.packageCompletionStatus='';status.setAttribute('role','status');status.setAttribute('aria-live','polite');row.append(status);}
    const value=message();if(status.textContent!==value)status.textContent=value;
   }
  }
  for(const button of document.querySelectorAll('[data-complete-package]')){
   button.disabled=busy||P.completed||P.readOnly||!K.allComplete(p,M);
   button.textContent=busy?'Abschluss wird gespeichert …':P.completed?'Lernpaket abgeschlossen':'Lernpaket abschließen';
   button.setAttribute('aria-busy',String(busy));
   if(!button.dataset.completionBound){button.dataset.completionBound='1';button.addEventListener('click',finish);}
  }
 }
 window.addEventListener('soz-progress',paint);
 window.addEventListener('focus',paint);
 const observer=new MutationObserver(()=>{
  const footer=document.querySelector('.page-footer,.b-footer');
  if(footer&&!footer.querySelector('[data-point-float]'))paint();
 });
 observer.observe(document.body,{childList:true,subtree:true});
 paint();
 window.SOZ_PACKAGE_COMPLETION={render:paint,complete:finish};
})();
