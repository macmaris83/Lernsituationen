(()=>{'use strict';
const K=window.SOZ_PROGRESS_CORE,D=window.SOZPAED;if(!K||!D)return;
const original=K.blockedBy;
const originalComplete=K.allComplete;
K.allComplete=function(...args){return originalComplete(...args)&&!!window.BRC_KNOWLEDGE?.complete();};
K.blockedBy=function(p,meta,page,mode){
 if(window.SOZ_TEACHER_VIEW?.active||document.body.dataset.teacher)return null;
 if(page==='wissenscheck.html'){
  if(!K.quizComplete(p,meta))return 'handlungssituation';
  if(!K.phaseComplete(p,meta,'informieren',mode))return 'informieren';
  return null;
 }
 const blocked=original(p,meta,page,mode);if(blocked)return blocked;
 if(['planen.html','entscheiden.html','durchfuehren.html','bewerten.html','reflektieren.html'].includes(page)&&!window.BRC_KNOWLEDGE?.complete())return 'wissenscheck';
 return null;
};
window.addEventListener('brc-knowledge-change',()=>window.SOZ_PROGRESS?.render());
})();
