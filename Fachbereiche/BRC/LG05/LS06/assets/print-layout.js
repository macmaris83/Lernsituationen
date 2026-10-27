/* Complete, unclipped print view. Lesson data and progress identifiers stay untouched. */
(()=>{'use strict';
const page=document.body.dataset.page;
if(page!=='druckansicht.html')return;
const root=()=>document.querySelector('[data-print-content]');
const fields='textarea,select,input:not([type=radio]):not([type=checkbox]):not([type=button]):not([type=submit]):not([type=hidden])';
function mirrorField(field){
  if(field.closest('.no-print'))return;
  let mirror=field.nextElementSibling;
  if(!mirror?.hasAttribute('data-print-field')){
    mirror=document.createElement('div');
    mirror.className='print-field-value';
    mirror.dataset.printField='';
    mirror.setAttribute('aria-hidden','true');
    field.after(mirror);
    field.dataset.printOriginal='';
  }
  const value=field.tagName==='SELECT'?field.selectedOptions[0]?.textContent||'':field.value;
  mirror.textContent=value||'\u00a0';
  mirror.classList.toggle('print-field-empty',!String(value||'').trim());
  mirror.classList.toggle('print-field-multiline',field.tagName==='TEXTAREA');
}
function prepare(){
  const content=root();if(!content)return null;
  const printButton=document.querySelector('[data-print]');
  if(printButton&&!document.querySelector('[data-print-return]')){
    const back=document.createElement('button');back.type='button';back.dataset.printReturn='';
    back.textContent='Zurück zur Lernsituation';
    back.addEventListener('click',()=>{
      let previous=null;try{previous=new URL(document.referrer);}catch{}
      const folder=location.pathname.replace(/[^/]*$/,'');
      if(history.length>1&&previous?.origin===location.origin&&previous.pathname.startsWith(folder)&&!previous.pathname.endsWith('/druckansicht.html'))history.back();
      else location.assign('index.html');
    });
    printButton.after(back);
  }
  content.querySelectorAll('details').forEach(detail=>{detail.open=true;});
  content.querySelectorAll('[data-delayed-material]').forEach(element=>{element.hidden=false;});
  // Other learning pathways remain hidden. A complete document means every chapter
  // of the selected pathway, not five duplicate sets of assignments.
  const mode=Number(document.body.dataset.mode)||1;
  content.querySelectorAll('[data-mode-panel]').forEach(element=>{element.hidden=Number(element.dataset.modePanel)!==mode;});
  // MC markup is already present in the document, while the interactive MC
  // controller is intentionally absent. Restore choices without event dispatch
  // or calls to progress.quiz()/write().
  const answers=window.SOZ_PROGRESS?.read?.().q||{};
  content.querySelectorAll('[data-quiz-question]').forEach(panel=>{
    const saved=answers[panel.dataset.quizQuestion];if(!saved)return;
    panel.querySelectorAll('input[type="radio"]').forEach(input=>{input.checked=input.value===String(saved[0]);});
  });
  content.querySelectorAll(fields).forEach(mirrorField);
  content.querySelectorAll('table').forEach(table=>{
    const columns=Math.max(0,...[...table.rows].map(row=>[...row.cells].reduce((sum,cell)=>sum+(cell.colSpan||1),0)));
    table.dataset.printColumns=String(columns);
    if(columns>4)table.classList.add('print-wide-table');
  });
  document.body.classList.add('print-document');
  return content;
}
const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
async function ready(){
  delete document.body.dataset.printReady;
  // Each invocation checks current resources. A click can arrive while the
  // initial preview is settling and introduce a newly edited image or font.
  for(;;){
    prepare();
    if(document.fonts?.ready)await document.fonts.ready;
    const images=[...root()?.querySelectorAll('img')||[]];
    const sources=images.map(image=>image.currentSrc||image.src);
    await Promise.all(images.map(async image=>{
      image.loading='eager';
      if(image.decode){try{await image.decode();}catch{}}
      else if(!image.complete)await new Promise(resolve=>{image.addEventListener('load',resolve,{once:true});image.addEventListener('error',resolve,{once:true});});
    }));
    // Media and stored accordion states are restored by the existing runtimes.
    // Reopen after those synchronous restores and allow two complete layouts.
    prepare();await frame();await frame();prepare();
    const current=[...root()?.querySelectorAll('img')||[]];
    if(document.fonts?.status==='loading'||current.length!==images.length||current.some((image,index)=>image!==images[index]||!image.complete||(image.currentSrc||image.src)!==sources[index]))continue;
    break;
  }
  document.body.dataset.printReady='true';
  return root();
}
async function printDocument(){await ready();window.print();}
window.SOZ_PRINT={prepare,ready,print:printDocument};
// Accordion opening for this separate print document must not overwrite a saved
// learner accordion preference in the interactive lesson.
document.addEventListener('toggle',event=>{if(root()?.contains(event.target))event.stopImmediatePropagation();},true);
document.addEventListener('input',event=>{if(root()?.contains(event.target)&&event.target.matches(fields))mirrorField(event.target);});
document.addEventListener('change',event=>{if(root()?.contains(event.target)&&event.target.matches(fields))mirrorField(event.target);});
window.addEventListener('beforeprint',prepare);
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{void ready();},{once:true});
else void ready();
})();
