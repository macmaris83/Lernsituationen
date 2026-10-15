(()=>{'use strict';const D=window.SOZPAED,C=window.SOZ_CONFIG||{},meta=window.SOZ_PROGRESS_META,K=window.SOZ_PROGRESS_CORE;if(!D||!meta||!K)return;const teacher=!!document.body.dataset.teacher,print=document.body.dataset.page==='druckansicht.html';let bridge=null;
try{if(window.parent!==window&&window.parent.SOZ_SCORM)bridge=window.parent.SOZ_SCORM;}catch{}
const localKey='soz-tasks:'+D.id+':'+location.pathname.replace(/[^/]+$/,'');let local=K.initial(meta,C.mode),error='',saved=false;
if(!bridge)try{const s=localStorage.getItem(localKey);if(s)local=K.sanitize(JSON.parse(s),meta,C.mode);}catch{error='Der Browser erlaubt keine Speicherung.';}
const read=()=>bridge?K.sanitize(bridge.read(),meta,C.mode):K.clone(local);
let mounted=false;
function write(p){if(teacher||print)return false;let ok;if(bridge)ok=bridge.update(p);else try{local=K.sanitize(p,meta,C.mode);localStorage.setItem(localKey,JSON.stringify(local));ok=true;error='';}catch{ok=false;error='Speichern im Browser ist gesperrt.';}saved=!!ok;if(mounted)render();return ok;}
function stateMessage(){if(bridge?.message)return bridge.message;if(bridge?.kind==='moodle')return bridge.lastSaved?'In Moodle gespeichert.':'Fortschritt aus Moodle geladen.';return error||'Auf diesem Gerät im Browser gespeichert.';}
function render(){if(teacher||print)return;const p=read(),mode=Number(document.body.dataset.mode)||Number(C.mode)||1;for(const a of document.querySelectorAll('.stations [data-learning-page]')){const page=a.dataset.learningPage;let done=page==='index.html'?p.o:page==='handlungssituation.html'?K.quizComplete(p,meta):K.phaseComplete(p,meta,page.replace('.html',''),mode);a.parentElement.classList.toggle('visited',done);const marker=a.querySelector('.station-check');if(marker)marker.hidden=!done;}
 for(const input of document.querySelectorAll('[data-task-complete]')){const t=meta.tasks[input.dataset.taskId];input.checked=!!t&&p.t[input.dataset.taskId]===t.signature;input.disabled=!!bridge?.readOnly||!!K.blockedBy(p,meta,document.body.dataset.page,mode);input.closest('.assignment-frame')?.classList.toggle('task-is-complete',input.checked);}
 for(const input of document.querySelectorAll('[data-orientation-complete]')){input.checked=p.o;input.disabled=!!bridge?.readOnly||!!K.blockedBy(p,meta,document.body.dataset.page,mode);}
 const page=document.body.dataset.page,phase=page?.replace('.html','');const tasks=Object.entries(meta.tasks).filter(([,t])=>t.phase===phase&&t.mode===mode),done=tasks.filter(([k,t])=>p.t[k]===t.signature).length;
 for(const el of document.querySelectorAll('[data-task-progress]'))el.textContent=`${done} von ${tasks.length} Aufgaben erledigt`;
 for(const el of document.querySelectorAll('[data-progress-status]'))el.textContent=stateMessage();
 renderAccess(p,mode);
}
const phaseLabels={handlungssituation:'Handlungssituation',informieren:'Informieren',planen:'Planen',entscheiden:'Entscheiden',durchfuehren:'Durchführen',bewerten:'Bewerten',reflektieren:'Reflektieren'};
function accessMessage(phase){return phase==='handlungssituation'?'Beantworte zuerst alle Fragen der Handlungssituation richtig und prüfe deine Antworten.':'Markiere zuerst alle Aufgaben der Phase „'+phaseLabels[phase]+'“ im aktuellen Lernweg als erledigt.';}
function linkPage(a){const href=a.dataset.lockedHref||a.getAttribute('href');if(!href)return null;try{const url=new URL(href,location.href);if(url.origin!==location.origin)return null;const here=new URL('.',location.href);if(new URL('.',url).href!==here.href)return null;return url.pathname.split('/').pop();}catch{return null;}}
function renderAccess(p,mode){
 for(const a of document.querySelectorAll('a[href],a[data-locked-href]')){
  const page=linkPage(a);if(!page)continue;
  const blocked=K.blockedBy(p,meta,page,mode);
  if(blocked){
   if(!a.dataset.lockedHref){a.dataset.lockedHref=a.getAttribute('href');a.dataset.lockedTitle=a.getAttribute('title')||'';}
   a.removeAttribute('href');a.setAttribute('aria-disabled','true');a.setAttribute('role','link');a.tabIndex=0;a.title=accessMessage(blocked);a.classList.add('phase-locked');
  }else if(a.dataset.lockedHref){
   a.setAttribute('href',a.dataset.lockedHref);a.title=a.dataset.lockedTitle;delete a.dataset.lockedHref;delete a.dataset.lockedTitle;a.removeAttribute('aria-disabled');a.removeAttribute('role');a.removeAttribute('tabindex');a.classList.remove('phase-locked');
  }
 }
 const content=document.querySelector('.lesson-content');if(!content)return;
 const blocked=K.blockedBy(p,meta,document.body.dataset.page,mode);
 let notice=document.querySelector('[data-phase-gate]');
 if(blocked){
  if(!notice){notice=document.createElement('section');notice.className='notice phase-gate';notice.dataset.phaseGate='';notice.setAttribute('role','status');content.before(notice);}
  notice.replaceChildren();const message=document.createElement('p');message.textContent='Diese Phase ist noch gesperrt. '+accessMessage(blocked);
  const back=document.createElement('a');back.className='button';back.href=blocked+'.html';back.textContent='Zur Phase „'+phaseLabels[blocked]+'“';notice.append(message,back);
 }
 if(notice)notice.hidden=!blocked;content.hidden=!!blocked;
}
function setMode(mode){if(teacher||print)return;const p=read();p.m=Number(mode);write(p);}
function quiz(id,value,submitted){const p=read();if(value)p.q[id]=[value,!!submitted];else delete p.q[id];write(p);}
function mount(){if(mounted||teacher||print)return;mounted=true;document.body.dataset.progressReady='true';
 const preventLocked=event=>{const a=event.target.closest?.('a');if(!a)return;const target=linkPage(a);if(target&&K.blockedBy(read(),meta,target,Number(document.body.dataset.mode)||Number(C.mode)||1)){event.preventDefault();event.stopImmediatePropagation();}};
 document.addEventListener('click',preventLocked,true);
 document.addEventListener('keydown',event=>{if(event.key==='Enter')preventLocked(event);},true);
const page=document.body.dataset.page;for(const input of document.querySelectorAll('[data-task-complete]'))input.addEventListener('change',()=>{const p=read();if(K.blockedBy(p,meta,page,Number(document.body.dataset.mode)||Number(C.mode)||1))return;K.setTask(p,meta,input.dataset.taskId,input.checked);write(p);});for(const input of document.querySelectorAll('[data-orientation-complete]'))input.addEventListener('change',()=>{const p=read();p.o=input.checked;write(p);});
 if(meta.resumePages.includes(page)&&!K.blockedBy(read(),meta,page,Number(document.body.dataset.mode)||Number(C.mode)||1)){const p=read();p.b=page;p.m=Number(document.body.dataset.mode)||Number(C.mode)||1;write(p);}render();if(bridge){const unsubscribe=bridge.subscribe(render);window.addEventListener('pagehide',unsubscribe,{once:true});}
 if(bridge?.message&&!document.querySelector('[data-progress-status]')){const s=document.createElement('p');s.dataset.progressStatus='';s.className='progress-counter no-print';s.setAttribute('role','status');document.querySelector('.lesson-content')?.appendChild(s);render();}
}
window.SOZ_PROGRESS={read,write,mount,render,setMode,quiz,reset(){const p=K.initial(meta,read().m);return write(p);},get kind(){return bridge?.kind||'preview';},get readOnly(){return !!bridge?.readOnly;},get learner(){return bridge?.learner||'';},get initialMode(){return C.allowStudentMode?read().m:Number(C.mode)||1;},get storageMessage(){return stateMessage();}};
})();
