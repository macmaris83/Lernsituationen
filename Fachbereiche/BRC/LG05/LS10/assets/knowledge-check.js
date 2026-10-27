(()=>{'use strict';
const data=window.BRC_KNOWLEDGE_DATA;
if(!data||!Array.isArray(data.questions)||!data.questions.length)return;
const teacher=!!window.SOZ_TEACHER_VIEW?.active;
const store=teacher?sessionStorage:localStorage;
const key=(teacher?'teacher:':'')+'brc-knowledge:'+data.lesson+':'+data.signature;
const questions=data.questions,byId=new Map(questions.map(q=>[q.id,q]));
const roots=[...document.querySelectorAll('[data-knowledge-check]')];
let storageOK=true;
function shuffle(values){const out=[...values];for(let i=out.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[out[i],out[j]]=[out[j],out[i]];}return out;}
function fresh(){return {schema:1,lesson:data.lesson,signature:data.signature,order:shuffle(questions.map(q=>q.id)),optionOrder:{},answers:{},active:''};}
let state=fresh();
try{
 const saved=JSON.parse(store.getItem(key)||'null');
 if(saved?.schema===1&&saved.lesson===data.lesson&&saved.signature===data.signature){
  const ids=(saved.order||[]).filter(id=>byId.has(id));
  state.order=[...new Set([...ids,...state.order])];
  for(const q of questions){
   const previous=saved.answers?.[q.id],valid=q.options.some(o=>o.id===previous?.value);
   if(valid)state.answers[q.id]={value:previous.value,submitted:previous.submitted===true,correct:previous.submitted===true&&previous.value===q.correct,attempts:Math.max(0,Number(previous.attempts)||0)};
   const order=saved.optionOrder?.[q.id];
   if(Array.isArray(order)&&order.length===q.options.length&&new Set(order).size===q.options.length&&order.every(id=>q.options.some(o=>o.id===id)))state.optionOrder[q.id]=order;
  }
  if(byId.has(saved.active))state.active=saved.active;
 }
}catch{storageOK=false;}
function done(){return questions.filter(q=>state.answers[q.id]?.correct).length;}
function complete(){return done()===questions.length;}
function snapshot(){return JSON.parse(JSON.stringify({...state,correct:done(),total:questions.length,complete:complete(),storageOK}));}
function announce(){window.dispatchEvent(new CustomEvent('brc-knowledge-change',{detail:snapshot()}));}
function save(){try{store.setItem(key,JSON.stringify(state));storageOK=true;}catch{storageOK=false;}announce();}
function node(tag,cls,text){const element=document.createElement(tag);if(cls)element.className=cls;if(text!==undefined)element.textContent=text;return element;}
function focusCard(root){const el=root.querySelector('[data-knowledge-heading]');el?.focus({preventScroll:true});root.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}
function active(){
 const id=state.active;
 if(id&&byId.has(id)&&!state.answers[id]?.correct)return byId.get(id);
 return byId.get(state.order.find(k=>!state.answers[k]?.correct));
}
function renderRoot(root){
 root.replaceChildren();root.classList.add('knowledge-check');
 const count=done(),all=complete(),status=node('div','knowledge-status'),badge=node('span','knowledge-badge',all?'Wissenscheck abgeschlossen':'Wissenscheck offen');
 badge.dataset.complete=String(all);status.append(badge,node('span','knowledge-count',count+' / '+questions.length+' Begriffe sicher'));root.append(status);
 const progress=node('progress','knowledge-progress');progress.max=questions.length;progress.value=count;progress.setAttribute('aria-label','Richtig beantwortete Fachbegriffe');root.append(progress);
 if(all){
  const card=node('section','card knowledge-complete');card.append(node('h2','','Alle Fachbegriffe richtig zugeordnet'),node('p','','Du hast alle '+questions.length+' Begriffe geprüft. Weiter geht es mit der Phase Planen.'));
  const review=node('details','knowledge-review');review.append(node('summary','','Begriffe und BioCasa-Beispiele nachlesen'));
  for(const q of questions){const item=node('article','knowledge-review-item');item.append(node('h3','',q.term),node('p','',q.definition),node('p','muted',q.context));review.append(item);}card.append(review);root.append(card);return;
 }
 const q=active();state.active=q.id;
 if(!state.optionOrder[q.id])state.optionOrder[q.id]=shuffle(q.options.map(o=>o.id));
 const answer=state.answers[q.id]||{value:'',submitted:false,correct:false,attempts:0};
 const card=node('section','card quiz-check knowledge-card');card.dataset.knowledgeQuestion=q.id;
 const eyebrow=node('p','eyebrow',q.group.replace(/^\d+\s*·\s*/,''));
 const heading=node('h2','knowledge-term',q.term);heading.tabIndex=-1;heading.dataset.knowledgeHeading='';
 card.append(eyebrow,heading);
 const fieldset=node('fieldset','knowledge-options');fieldset.append(node('legend','',q.prompt));
 const inputs=[];
 for(const id of state.optionOrder[q.id]){
  const option=q.options.find(o=>o.id===id),label=node('label','quiz-answer knowledge-answer'),input=node('input');
  input.type='radio';input.name='knowledge-'+q.id;input.value=id;input.checked=answer.value===id;
  input.addEventListener('change',()=>{state.answers[q.id]={...answer,value:id,submitted:false,correct:false};save();render();});
  label.append(input,node('span','',option.text));fieldset.append(label);inputs.push(input);
 }
 card.append(fieldset);
 const actions=node('div','quiz-actions knowledge-actions'),check=node('button','primary','Antwort prüfen');check.type='button';check.disabled=!answer.value;
 check.addEventListener('click',()=>{
  const value=state.answers[q.id]?.value;if(!value)return;
  state.answers[q.id]={value,submitted:true,correct:value===q.correct,attempts:(Number(state.answers[q.id]?.attempts)||0)+1};
  // Keep this term visible until the learner explicitly continues.
  state.active=q.id;save();renderSubmitted(root,q);
 });actions.append(check);card.append(actions);root.append(card);
 if(answer.submitted)showFeedback(root,q,answer);
 if(!storageOK)root.append(node('p','knowledge-storage-message','Der Browser konnte den Checkstand nicht speichern.'));
}
function showFeedback(root,q,answer){
 const card=root.querySelector('[data-knowledge-question]');if(!card)return;
 card.querySelector('.knowledge-feedback')?.remove();
 const feedback=node('div','quiz-feedback knowledge-feedback');feedback.setAttribute('role','status');feedback.dataset.result=answer.correct?'correct':'wrong';
 if(answer.correct){feedback.append(node('p','','Richtig. '+q.definition),node('p','knowledge-context','BioCasa: '+q.context));
  const next=node('button','primary knowledge-next',complete()?'Auswertung anzeigen':'Nächster Begriff');next.type='button';
  next.addEventListener('click',()=>{state.active='';save();render();focusCard(root);});card.querySelector('.knowledge-actions').append(next);
  card.querySelectorAll('input[type=radio],.knowledge-actions>button:first-child').forEach(e=>e.disabled=true);
 }else{const other=byId.get(answer.value);feedback.append(node('p','',other?'Noch nicht richtig. Diese Erklärung gehört zum Begriff „'+other.term+'“. Prüfe die übrigen Erklärungen.':'Noch nicht richtig. Prüfe die Erklärungen erneut.'));}
 card.append(feedback);
}
function renderSubmitted(root,q){
 // renderRoot advances passed terms by design; retain the submitted term for feedback.
 const answer=state.answers[q.id];
 if(answer.correct){
  const saved=answer.correct;answer.correct=false;renderRoot(root);answer.correct=saved;
  const count=done();root.querySelector('.knowledge-count').textContent=count+' / '+questions.length+' Begriffe sicher';root.querySelector('progress').value=count;
  const badge=root.querySelector('.knowledge-badge');badge.textContent=complete()?'Wissenscheck abgeschlossen':'Wissenscheck offen';badge.dataset.complete=String(complete());
  showFeedback(root,q,answer);
 }else{renderRoot(root);}
}
function render(){for(const root of roots)renderRoot(root);}
window.BRC_KNOWLEDGE={read:snapshot,complete,key,render,total:questions.length};
render();save();
window.addEventListener('storage',event=>{if(event.key!==key||!event.newValue)return;try{const next=JSON.parse(event.newValue);if(next.lesson===data.lesson&&next.signature===data.signature){state=next;render();announce();}}catch{}});
})();
