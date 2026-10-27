/* One-time import of answers from the earlier BioCasa MC view. */
(()=>{'use strict';
const C=window.RENO_FLASHCARD_CONFIG,B=window.BRC_KNOWLEDGE_DATA,P=window.SOZ_PROGRESS,F=window.RENO_FLASHCARD_PACKAGE;
if(P?.kind==='moodle')return;
if(!C||!B||!P||!F?.isHosted||F.readOnly||document.body.dataset.teacher)return;
const storage=window.SOZ_TEACHER_VIEW?.active?sessionStorage:localStorage;
const marker='biocasa-reference-check-import:'+C.id+':'+C.signature;
try{
 if(storage.getItem(marker)==='1'||P.read().fc)return;
 const old=JSON.parse(storage.getItem((window.SOZ_TEACHER_VIEW?.active?'teacher:':'')+'brc-knowledge:'+B.lesson+':'+B.signature)||'null');
 if(!old?.answers){storage.setItem(marker,'1');return;}
 const questions=B.questions,indices=new Map(questions.map((q,i)=>[q.id,i]));
 const order=[...new Set([...(old.order||[]).filter(id=>indices.has(id)),...questions.map(q=>q.id)])];
 const answer=(q,value)=>({correct:value.value===q.correct,certainty:'unsure',selected:value.value,selectedText:q.options.find(o=>o.id===value.value)?.text||'',source:'first',at:0,uid:'legacy-'+q.id});
 const results=questions.map(q=>{const v=old.answers[q.id],a=v?.submitted?answer(q,v):null;return {first:a,latest:a,bonus:0,history:a?[a]:[]};});
 const queue=order.map((id,index)=>{const q=questions[indices.get(id)],a=results[indices.get(id)].latest;return {uid:'card-'+(index+1),i:indices.get(id),reason:'initial',variantIndex:0,options:q.options.map(o=>[o.id,o.text,o.id===q.correct]),answered:a?.correct===true,answer:a?.correct?a:null,reinforcement:false,triggerUid:''};});
 const pending=queue.filter(q=>!q.answered).length,known=results.filter(r=>r.latest?.correct).length,done=known===questions.length&&!pending;
 const cursor=Math.max(0,queue.findIndex(q=>!q.answered)),current=questions[queue[cursor].i],draft=old.answers[current.id];
 const started=results.some(r=>r.latest)||!!draft?.value;
 const state={stage:done?'summary':started?'check':'intro',started:!!started,checkFinished:done,phaseIndex:3,cursor,queue,serial:queue.length,appearances:Object.fromEntries(questions.map(q=>[q.id,1])),practiceReturn:null,practiceDraft:null,results,selected:done?null:draft?.value||null,certainty:null,feedback:null,acknowledged:false,endedBy:done?'Check abgeschlossen':'',jokerUses:[]};
 if(F.save({version:3,cardIds:C.terms.map(t=>t.id),state},{complete:done,known,total:questions.length,pending,started:!!started,acknowledged:false}))storage.setItem(marker,'1');
}catch{}
})();
