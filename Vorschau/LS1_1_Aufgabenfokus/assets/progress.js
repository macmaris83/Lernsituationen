(()=>{'use strict';const D=window.SOZPAED,C=window.SOZ_CONFIG||{},meta=window.SOZ_PROGRESS_META,K=window.SOZ_PROGRESS_CORE;if(!D||!meta||!K)return;const teacher=!!document.body.dataset.teacher,print=document.body.dataset.page==='druckansicht.html';let bridge=null;
try{if(window.parent!==window&&window.parent.SOZ_SCORM)bridge=window.parent.SOZ_SCORM;}catch{}
const localKey='soz-tasks:'+D.id+':'+location.pathname.replace(/[^/]+$/,'');let local=K.initial(meta,C.mode),error='',saved=false;
if(!bridge)try{const s=localStorage.getItem(localKey);if(s)local=K.sanitize(JSON.parse(s),meta,C.mode);}catch{error='Der Browser erlaubt keine Speicherung.';}
const read=()=>bridge?K.sanitize(bridge.read(),meta,C.mode):K.clone(local);
let mounted=false;
function write(p){if(teacher||print)return false;let ok;if(bridge)ok=bridge.update(p);else try{local=K.sanitize(p,meta,C.mode);localStorage.setItem(localKey,JSON.stringify(local));ok=true;error='';}catch{ok=false;error='Speichern im Browser ist gesperrt.';}saved=!!ok;if(mounted)render();return ok;}
function stateMessage(){if(bridge?.message)return bridge.message;if(bridge?.kind==='moodle')return bridge.lastSaved?'In Moodle gespeichert.':'Fortschritt aus Moodle geladen.';return error||'Auf diesem Gerät im Browser gespeichert.';}
function render(){const p=read(),mode=Number(document.body.dataset.mode)||Number(C.mode)||1;for(const a of document.querySelectorAll('.stations [data-learning-page]')){const page=a.dataset.learningPage;let done=page==='index.html'?p.o:page==='handlungssituation.html'?K.quizComplete(p,meta):K.phaseComplete(p,meta,page.replace('.html',''),mode);a.parentElement.classList.toggle('visited',done);const marker=a.querySelector('.station-check');if(marker)marker.hidden=!done;}
 for(const input of document.querySelectorAll('[data-task-complete]')){const t=meta.tasks[input.dataset.taskId];input.checked=!!t&&p.t[input.dataset.taskId]===t.signature;input.disabled=!!bridge?.readOnly;input.closest('.assignment-frame')?.classList.toggle('task-is-complete',input.checked);}
 for(const input of document.querySelectorAll('[data-orientation-complete]')){input.checked=p.o;input.disabled=!!bridge?.readOnly;}
 const page=document.body.dataset.page,phase=page?.replace('.html','');const tasks=Object.entries(meta.tasks).filter(([,t])=>t.phase===phase&&t.mode===mode),done=tasks.filter(([k,t])=>p.t[k]===t.signature).length;
 for(const el of document.querySelectorAll('[data-task-progress]'))el.textContent=`${done} von ${tasks.length} Aufgaben erledigt`;
 for(const el of document.querySelectorAll('[data-progress-status]'))el.textContent=stateMessage();
}
function setMode(mode){if(teacher||print)return;const p=read();p.m=Number(mode);write(p);}
function quiz(id,value,submitted){const p=read();if(value)p.q[id]=[value,!!submitted];else delete p.q[id];write(p);}
function mount(){if(mounted||teacher||print)return;mounted=true;document.body.dataset.progressReady='true';const page=document.body.dataset.page;for(const input of document.querySelectorAll('[data-task-complete]'))input.addEventListener('change',()=>{const p=read();K.setTask(p,meta,input.dataset.taskId,input.checked);write(p);});for(const input of document.querySelectorAll('[data-orientation-complete]'))input.addEventListener('change',()=>{const p=read();p.o=input.checked;write(p);});
 if(meta.resumePages.includes(page)){const p=read();p.b=page;p.m=Number(document.body.dataset.mode)||Number(C.mode)||1;write(p);}render();if(bridge){const unsubscribe=bridge.subscribe(render);window.addEventListener('pagehide',unsubscribe,{once:true});}
 if(bridge?.message&&!document.querySelector('[data-progress-status]')){const s=document.createElement('p');s.dataset.progressStatus='';s.className='progress-counter no-print';s.setAttribute('role','status');document.querySelector('.lesson-content')?.appendChild(s);render();}
}
window.SOZ_PROGRESS={read,write,mount,render,setMode,quiz,reset(){const p=K.initial(meta,read().m);return write(p);},get kind(){return bridge?.kind||'preview';},get readOnly(){return !!bridge?.readOnly;},get learner(){return bridge?.learner||'';},get initialMode(){return C.allowStudentMode?read().m:Number(C.mode)||1;},get storageMessage(){return stateMessage();}};
})();
