/* Original BioCasa Klappfragen with persistent state and v1.8 HS progress bridge. */
(function(){
  'use strict';
  if(window.__BRC_MICROCHECKS_INITIALIZED)return;
  window.__BRC_MICROCHECKS_INITIALIZED=true;
  const script=document.currentScript;
  const id=String(document.body?.dataset.lsId||window.SOZPAED?.id||window.BRC_PACKAGE_ID||location.pathname);
  const lesson=id.match(/ls[-_ ]?(\d{2})/i);
  const KEY_PREFIX=String(window.BRC_MICROCHECK_PREFIX||script?.dataset.storagePrefix||(lesson?'brc_ls'+lesson[1]+'_microcheck_v1:':'brc_microcheck_v1:'+id+':'));
  const restored=new WeakSet();
  let storage;try{storage=window.SOZ_TEACHER_VIEW?.active?sessionStorage:localStorage;}catch(e){storage={getItem(){return null;},setItem(){}};}
  function keyFor(group){const radio=group.querySelector('input[type="radio"]');return radio?KEY_PREFIX+radio.name:null;}
  function quizId(group){
    if(document.body.dataset.page!=='handlungssituation.html')return null;
    const radio=group.querySelector('input[type="radio"]');
    const wanted=group.dataset.quizId||radio?.name;
    return window.SOZ_PROGRESS_META?.quiz?.some(q=>q.id===wanted)?wanted:null;
  }
  function feedbackFor(group,value,checked){
    const feedback=group.querySelector('.micro-feedback');if(!feedback)return;
    if(!checked||value===null){feedback.textContent='';delete feedback.dataset.state;group.classList.remove('quiz-is-complete');return;}
    const correct=Number(group.dataset.correct)===Number(value);
    feedback.textContent=(correct?'Richtig. ':'Noch nicht. Lies die Stelle noch einmal: ')+group.dataset.explanation;
    feedback.dataset.state=correct?'right':'wrong';
    feedback.hidden=false;
    group.classList.toggle('quiz-is-complete',correct);
  }
  function syncProgress(group,value,checked){
    const quiz=quizId(group),P=window.SOZ_PROGRESS;
    if(quiz&&P&&!P.readOnly){P.quiz(quiz,value,!!checked);try{storage.setItem(KEY_PREFIX+'progress-migrated:'+quiz,'1');}catch(e){}}
  }
  function save(group,checked,sync){
    const key=keyFor(group);if(!key)return;
    const selected=group.querySelector('input[type="radio"]:checked');
    const value=selected?selected.value:null;
    if(!window.SOZ_PROGRESS?.readOnly)try{storage.setItem(key,JSON.stringify({value:value,checked:!!checked,open:group.open}));}catch(e){}
    if(sync)syncProgress(group,value,checked);
  }
  function restore(){
    document.querySelectorAll('.micro-question').forEach(group=>{
      if(restored.has(group))return;restored.add(group);
      const key=keyFor(group);if(!key)return;
      let state;try{state=JSON.parse(storage.getItem(key)||'null');}catch(e){}
      const quiz=quizId(group),P=window.SOZ_PROGRESS;
      if(quiz&&P){
        const entry=P.read()?.q?.[quiz];
        if(entry)state={value:entry[0],checked:entry[1],open:state?.open};
        else{
          let migrated=false;try{migrated=storage.getItem(KEY_PREFIX+'progress-migrated:'+quiz)==='1';}catch(e){}
          if(migrated)state={value:null,checked:false,open:state?.open};
        }
      }
      if(!state)return;
      group.querySelectorAll('input[type="radio"]').forEach(input=>{input.checked=state.value!==null&&input.value===String(state.value);});
      if(typeof state.open==='boolean')group.open=state.open;
      feedbackFor(group,state.value,!!state.checked);
      if(quiz&&state.value!==null)syncProgress(group,String(state.value),!!state.checked);
    });
  }
  document.addEventListener('change',function(event){
    if(!event.target.matches('.micro-question input[type="radio"]'))return;
    const group=event.target.closest('.micro-question');
    feedbackFor(group,event.target.value,false);save(group,false,true);
  });
  document.addEventListener('toggle',function(event){if(event.target.matches('.micro-question'))save(event.target,!!event.target.querySelector('.micro-feedback')?.dataset.state,false);},true);
  document.addEventListener('click',function(event){
    const button=event.target.closest('.micro-check-button');if(!button)return;
    const group=button.closest('.micro-question');if(!group)return;
    const selected=group.querySelector('input[type="radio"]:checked');
    const feedback=group.querySelector('.micro-feedback');
    if(!selected){if(feedback){feedback.textContent='Bitte wähle zuerst eine Antwort.';feedback.hidden=false;feedback.dataset.state='wrong';}save(group,false,true);return;}
    feedbackFor(group,selected.value,true);save(group,true,true);
  });
  function mount(){
    restore();
    const root=document.querySelector('.lesson-content')||document.body;
    new MutationObserver(changes=>{if(changes.some(change=>Array.from(change.addedNodes).some(node=>node.nodeType===1&&(node.matches?.('.micro-question')||node.querySelector?.('.micro-question')))))restore();}).observe(root,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})();
