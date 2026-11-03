/* 1.8.5 compatibility: extend existing cores; never replace content signatures. */
(()=>{'use strict';
const K=window.SOZ_PROGRESS_CORE;if(!K||K.__form185)return;K.__form185=true;
const originalInitial=K.initial,originalSanitize=K.sanitize,originalBlocked=K.blockedBy,originalMetadata=K.metadataFrom;
K.initial=function(meta,mode){return {qf:{},qn:{},qh:{},...originalInitial(meta,mode)};};
K.sanitize=function(raw,meta,mode){const p=originalSanitize(raw,meta,mode);p.qf||={};p.qn||={};p.qh||={};if(raw?.s===1&&raw.l===meta.id){if(raw.o===true&&(meta.legacyOrientationSignatures||[]).includes(raw.w)&&K.orientationVideoCanContinue(p,meta))p.o=true;if(raw.v===meta.quizSignature)for(const q of meta.quiz||[]){const first=raw.qf?.[q.id];if(typeof first==='boolean'||first===null)p.qf[q.id]=first;else if(!raw.qf&&p.q[q.id])p.qf[q.id]=null;const n=raw.qn?.[q.id];if(Number.isInteger(n)&&n>0)p.qn[q.id]=Math.min(n,1000000);if(raw.qh?.[q.id]===true)p.qh[q.id]=true;}}return p;};
K.metadataFrom=function(data,parser){const meta=originalMetadata(data,parser);meta.legacyOrientationSignatures=[...new Set([...(meta.legacyOrientationSignatures||[]),...(data.form185LegacyOrientationSignatures||[])])];return meta;};
K.blockedBy=function(p,meta,page,mode=p.m){if(window.SOZ_TEACHER_VIEW?.active)return null;if(page==='handlungssituation.html')return p.o?null:'index';if(K.phases.includes(page.replace('.html',''))&&!p.o)return 'index';return originalBlocked(p,meta,page,mode);};
K.orientationVideoCanContinue||=()=>true;
K.orientationVideoComplete||=()=>true;
K.flashcardComplete||=((p,meta)=>!meta.flashcard||p.fc?.complete===true);
K.flashcardValid||=((p,meta)=>!!meta.flashcard&&p.fc?.id===meta.id&&p.fc?.signature===meta.flashcard.signature);
K.sharePoints||=((budget,count,index)=>{if(!count||index<0||index>=count)return 0;const units=Math.round(budget*100);return (Math.floor(units/count)+(index<units%count?1:0))/100;});
K.taskPoints||=((meta,id,mode=1)=>{const ids=Object.keys(meta.tasks||{}).filter(k=>meta.tasks[k].mode===Number(mode));return K.sharePoints(25,ids.length,ids.indexOf(id));});
K.situationValue||=((p,meta,id)=>Math.round(K.sharePoints(15,meta.quiz.length,meta.quiz.findIndex(q=>q.id===id))*((p.qh?.[id]||p.qf?.[id]===false)?0.6:1)*100)/100);
// Masters without a term test keep their existing tasks and HS check (40 XP).
// No artificial term content or automatic extra credit is introduced.
K.grading||=function(p,meta){const tasks=Object.entries(meta.tasks).filter(([,t])=>t.mode===Number(p.m));const taskPoints=tasks.reduce((s,[id,t])=>s+(p.t[id]===t.signature?K.taskPoints(meta,id,p.m):0),0),situationPoints=meta.quiz.reduce((s,q)=>s+(p.v===meta.quizSignature&&p.q[q.id]?.[1]&&p.q[q.id][0]===q.correct?K.situationValue(p,meta,q.id):0),0),round=n=>Math.round(n*100)/100;return {points:round(taskPoints+situationPoints),taskPoints:round(taskPoints),situationPoints:round(situationPoints),termPoints:0,termsTotal:0,termsCorrect:0,tasksDone:tasks.filter(([id,t])=>p.t[id]===t.signature).length,tasksTotal:tasks.length,maxPoints:40,ready:K.allComplete(p,meta)};};
})();
