(()=>{'use strict';
const D=window.SOZPAED,C=window.SOZ_CONFIG||{};if(!D)return;
const key='soz-teacher-view:'+D.id+':'+location.pathname.replace(/[^/]+$/,'')+':'+(C.packageRevision||'base');
let value=null;try{value=JSON.parse(sessionStorage.getItem(key)||'null');}catch{}
const active=value?.active===true;let learner='';try{learner=window.parent.SOZ_SCORM?.learner||'';}catch{}
window.SOZ_TEACHER_VIEW={active,learner,get mode(){return Number(value?.mode)||Number(C.mode)||1;}};
function remember(mode){value={active:true,mode:Number(mode)||1};sessionStorage.setItem(key,JSON.stringify(value));}
function init(){
 try{if(window.parent!==window){const notice=window.parent.document.querySelector('[data-scorm-notice]');if(notice){notice.hidden=active||!window.parent.SOZ_SCORM?.message;if(!active)notice.textContent=window.parent.SOZ_SCORM?.message||'';}}}catch{}
 document.querySelectorAll('.footer-utils a[href="lehrkraft.html"]').forEach(a=>{a.innerHTML="<svg class=\"editor-settings-icon\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"m9 3-1 3-3 1-2 3 2 2-1 3 2 3 3-1 2 2h3l1-3 3-1 2-3-2-2 1-3-2-3-3 1-2-2z\"/><circle cx=\"12\" cy=\"11\" r=\"3\"/></svg><span>Editor</span>";a.setAttribute('aria-label','Editor öffnen');});
 const panel=document.querySelector('#teacher-panel');
 if(panel){
  const section=document.createElement('section');section.className='teacher-card';
  const title=document.createElement('h2');title.textContent='Rundgang durch die Lernsituation';
  const explanation=document.createElement('p');explanation.textContent='Alle Phasen in der Lernendenansicht direkt öffnen. Eingaben im Rundgang werden getrennt vom Lernfortschritt gespeichert. Lösungen stehen in der separaten Lehrkräftedatei.';
  const button=document.createElement('button');button.className='primary';button.dataset.startTeacherView='';button.textContent='Rundgang starten';
  button.addEventListener('click',()=>{if(panel.hidden)return;try{remember(window.SOZ_API?.getSettings().mode||C.mode);location.href='index.html';}catch{explanation.textContent='Die Der Rundgang benötigt Sitzungsspeicher. Bitte das Paket in einem Browserfenster öffnen, das Speicherung erlaubt.';}});
  section.append(title,explanation,button);panel.prepend(section);
 }
 if(!active||document.body.dataset.teacher||document.body.dataset.page==='druckansicht.html')return;
 document.body.classList.add('teacher-view-active');
 const bar=document.createElement('aside');bar.className='teacher-view-bar no-print';bar.style.zIndex='10020';bar.setAttribute('aria-label','Lehrkräfteansicht');
 const label=document.createElement('strong');label.textContent='Rundgang · Alle Phasen frei';
 const paths=document.createElement('label');paths.textContent='Lernweg ';
 const select=document.createElement('select');select.setAttribute('aria-label','Lernweg in der Lehrkräfteansicht');
 for(let n=1;n<=5;n++){const option=document.createElement('option');option.value=n;option.textContent='Weg '+n;select.append(option);}select.value=window.SOZ_API?.getSettings().mode||value.mode;
 select.addEventListener('change',()=>{remember(select.value);try{sessionStorage.removeItem('teacher:task-focus-return:'+D.id);}catch{}const next=new URL(location.href);next.searchParams.delete('aufgabe');next.searchParams.delete('rueckaufgabe');location.replace(next.href);});paths.append(select);
 const exit=document.createElement('button');exit.textContent='Lernendenansicht';exit.dataset.exitTeacherView='';exit.addEventListener('click',()=>{sessionStorage.removeItem(key);location.reload();});
 bar.append(label,paths,exit);document.body.prepend(bar);
 const measure=()=>document.body.style.setProperty('--teacher-view-height',bar.getBoundingClientRect().height+'px');measure();new ResizeObserver(measure).observe(bar);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
