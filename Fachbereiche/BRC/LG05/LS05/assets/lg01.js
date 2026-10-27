(()=>{'use strict';
const D=window.SOZPAED;if(!D)return;const printView=document.body.dataset.page==='druckansicht.html';
const P=window.SOZ_PROGRESS,A=window.SOZ_API,base=(window.SOZ_TEACHER_VIEW?.active?'teacher:':'')+'biocasa:'+D.id+':'+D.version+':'+(P?.learner||'local')+':';
const store=(key,value)=>{try{localStorage.setItem(base+key,JSON.stringify(value));return true}catch{return false}};
const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(base+key))??fallback}catch{return fallback}};
if(document.body.dataset.page==='druckansicht.html')document.querySelectorAll('.quiz-check>details,.microchecks>.micro-question').forEach(d=>d.open=true);
// The teacher area is deliberately available without a PIN.
if(document.body.dataset.teacher)return;

for(const det of document.querySelectorAll('details[data-quiz-open]')){const k='quiz-open:'+det.dataset.quizOpen;det.open=printView||read(k,false);if(!printView)det.addEventListener('toggle',()=>store(k,det.open));}
for(const det of document.querySelectorAll('.micro-question[data-micro-id]')){
 const key=(det.closest('[data-print-source]')?.dataset.printSource||document.body.dataset.page)+':'+det.dataset.microId,saved=read(key,{}),feedback=det.querySelector('.micro-feedback');let submitted=!!saved.submitted;det.open=printView||!!saved.open;
 const inputs=[...det.querySelectorAll(':scope > .micro-body > label input')],textarea=det.querySelector('textarea');for(const i of inputs)i.checked=i.value===saved.value;if(textarea)textarea.value=saved.text||'';
 const state=()=>({open:det.open,value:inputs.find(i=>i.checked)?.value||'',text:textarea?.value||'',submitted});
 function show(){if(!feedback)return;const v=inputs.find(i=>i.checked)?.value;if(!submitted){feedback.textContent='';return}if(v===undefined){feedback.textContent='Wählen Sie zuerst eine Antwort.';return}const ok=v===det.dataset.correct;feedback.dataset.result=ok?'correct':'wrong';feedback.textContent=(ok?'Richtig. ':'Noch nicht richtig. ')+det.dataset.explanation;}
 if(printView){show();continue;}
 det.addEventListener('toggle',()=>store(key,state()));inputs.forEach(i=>i.addEventListener('change',()=>{submitted=false;show();store(key,state())}));textarea?.addEventListener('input',()=>store(key,state()));
 det.querySelector('[data-micro-submit]')?.addEventListener('click',()=>{submitted=true;show();if(!store(key,state()))feedback.textContent+=' Der Browser konnte die Antwort nicht speichern.';});show();
}
})();
