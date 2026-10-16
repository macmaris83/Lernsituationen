(()=>{'use strict';
const D=window.SOZPAED,C=window.SOZ_CONFIG||{};if(!D)return;
const key='soz-teacher-view:'+D.id+':'+location.pathname.replace(/[^/]+$/,'')+':'+(C.packageRevision||'base');
let value=null;try{value=JSON.parse(sessionStorage.getItem(key)||'null');}catch{}
const active=value?.active===true;let learner='';try{learner=window.parent.SOZ_SCORM?.learner||'';}catch{}
window.SOZ_TEACHER_VIEW={active,learner,get mode(){return Number(value?.mode)||Number(C.mode)||1;}};
function remember(mode){value={active:true,mode:Number(mode)||1};sessionStorage.setItem(key,JSON.stringify(value));}
function init(){
 try{if(window.parent!==window){const notice=window.parent.document.querySelector('[data-scorm-notice]');if(notice){notice.hidden=active||!window.parent.SOZ_SCORM?.message;if(!active)notice.textContent=window.parent.SOZ_SCORM?.message||'';}}}catch{}
 document.querySelectorAll('.footer-utils a[href="lehrkraft.html"]').forEach(a=>{a.textContent='Editor';a.setAttribute('aria-label','Editor öffnen');});
 const panel=document.querySelector('#teacher-panel');
 if(panel){
  const section=document.createElement('section');section.className='teacher-card';
  const title=document.createElement('h2');title.textContent='Lernsituation als Lehrkraft ansehen';
  const explanation=document.createElement('p');explanation.textContent='Alle Phasen direkt öffnen und die vorhandenen Lösungen anzeigen. Der Teststand ist vom Lernstand der Lernenden getrennt.';
  const button=document.createElement('button');button.className='primary';button.dataset.startTeacherView='';button.textContent='Lehrkräfteansicht starten';
  button.addEventListener('click',()=>{if(panel.hidden)return;try{remember(window.SOZ_API?.getSettings().mode||C.mode);location.href='index.html';}catch{explanation.textContent='Die Lehrkräfteansicht benötigt Sitzungsspeicher. Bitte das Paket in einem Browserfenster öffnen, das Speicherung erlaubt.';}});
  section.append(title,explanation,button);panel.prepend(section);
 }
 if(!active||document.body.dataset.teacher||document.body.dataset.page==='druckansicht.html')return;
 document.body.classList.add('teacher-view-active');
 const bar=document.createElement('aside');bar.className='teacher-view-bar no-print';bar.setAttribute('aria-label','Lehrkräfteansicht');
 const label=document.createElement('strong');label.textContent='Lehrkräfteansicht · Alle Phasen frei';
 const paths=document.createElement('label');paths.textContent='Lernweg ';
 const select=document.createElement('select');select.setAttribute('aria-label','Lernweg in der Lehrkräfteansicht');
 for(let n=1;n<=5;n++){const option=document.createElement('option');option.value=n;option.textContent='Weg '+n;select.append(option);}select.value=window.SOZ_API?.getSettings().mode||value.mode;
 select.addEventListener('change',()=>{remember(select.value);location.reload();});paths.append(select);
 const show=document.createElement('button');show.dataset.showTeacherSolutions='';show.textContent='Lösungen anzeigen';show.addEventListener('click',solutions);
 const exit=document.createElement('button');exit.textContent='Lernendenansicht';exit.dataset.exitTeacherView='';exit.addEventListener('click',()=>{sessionStorage.removeItem(key);location.reload();});
 bar.append(label,paths,show,exit);document.body.prepend(bar);
 const measure=()=>document.body.style.setProperty('--teacher-view-height',bar.getBoundingClientRect().height+'px');measure();new ResizeObserver(measure).observe(bar);
}
function solutions(){
 const dialog=document.createElement('dialog');dialog.className='teacher-solutions';dialog.setAttribute('aria-labelledby','teacher-solutions-title');
 const head=document.createElement('header'),title=document.createElement('h2');title.id='teacher-solutions-title';title.textContent='Lösungen und Erwartungshorizont';
 const close=document.createElement('button');close.textContent='Schließen';close.addEventListener('click',()=>dialog.close());head.append(title,close);
 const content=document.createElement('div');content.className='teacher-solutions-content';
 const doc=new DOMParser().parseFromString(D.pages['handlungssituation.html']||'','text/html');
 const source=doc.querySelector('[data-situation-quiz] script[type="application/json"]');
 if(source){const heading=document.createElement('h3');heading.textContent='Handlungssituation · Richtige Antworten';content.append(heading);const list=document.createElement('ol');
  for(const q of JSON.parse(source.textContent)){const item=document.createElement('li'),question=document.createElement('p'),answer=document.createElement('p');question.textContent=q.question||q.prompt||q.title||q.id;const correct=q.options.find(o=>o.value===q.correct);answer.textContent=correct?.text||correct?.label||q.correct;answer.className='teacher-correct-answer';item.append(question,answer);const note=correct?.feedback||q.feedback?.correct||q.correctFeedback||q.explanation;if(typeof note==='string'){const p=document.createElement('p');p.textContent=note;item.append(p);}list.append(item);}content.append(list);
 }
 const material=document.querySelectorAll('.micro-question[data-correct]');
 if(material.length){const heading=document.createElement('h3');heading.textContent='Dieses Material · Richtige Antworten';content.append(heading);for(const q of material){const block=document.createElement('section'),question=document.createElement('p'),answer=document.createElement('p');question.textContent=q.querySelector('summary')?.textContent||'';const correct=[...q.querySelectorAll('input')].find(i=>i.value===q.dataset.correct);answer.textContent=correct?.closest('label')?.textContent||q.dataset.correct;answer.className='teacher-correct-answer';const note=document.createElement('p');note.textContent=q.dataset.explanation||'';block.append(question,answer,note);content.append(block);}}
 const expected=document.createElement('section');expected.className='teacher-original-expectations';expected.innerHTML=D.pages['erwartungshorizont.html']||'<p>Kein Erwartungshorizont hinterlegt.</p>';expected.querySelectorAll('script').forEach(e=>e.remove());content.append(expected);
 dialog.append(head,content);document.body.append(dialog);dialog.addEventListener('close',()=>dialog.remove(),{once:true});dialog.showModal();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
