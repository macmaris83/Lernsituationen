/* Reference ReNo scoring and battery, adapted without replacing v1.8 task identities. */
(()=>{'use strict';
const K=window.SOZ_PROGRESS_CORE;if(!K||K.__referenceScoreCore)return;
K.__referenceScoreCore=true;
const phases=K.phases;
const phaseComplete=(...args)=>K.phaseComplete(...args);
const quizComplete=(...args)=>K.quizComplete(...args);
const originalInitial=K.initial,originalSanitize=K.sanitize,originalMetadataFrom=K.metadataFrom;
function availableModes(meta){return [...new Set(Object.values(meta.tasks||{}).map(t=>Number(t.mode)))].filter(n=>Number.isInteger(n)&&n>0).sort((a,b)=>a-b);}
K.initial=function(meta,mode){return {...originalInitial.call(this,meta,mode),qf:{},qn:{},qh:{},rl:1};};
K.sanitize=function(raw,meta,mode){
 const p=originalSanitize.call(this,raw,meta,mode);p.qf={};p.qn={};p.qh={};p.rl=1;
 if(!raw||raw.s!==1||raw.l!==meta.id)return p;
 if(raw.v===p.v)for(const q of meta.quiz||[]){
  const first=raw.qf?.[q.id];
  if(typeof first==='boolean'||first===null)p.qf[q.id]=first;
  else if(!raw.qf&&p.q[q.id])p.qf[q.id]=null;
  if(raw.qh?.[q.id]===true)p.qh[q.id]=true;
  const tries=raw.qn?.[q.id];if(Number.isInteger(tries)&&tries>0&&tries<=1000000)p.qn[q.id]=tries;
 }
 if(raw.rl===2)p.rl=2;return p;
};
K.metadataFrom=function(data,parser){
 const meta=originalMetadataFrom.call(this,data,parser);
 meta.flashcard=data.flashcard||null;meta.availableModes=availableModes(meta);
 if(meta.flashcard?.fileName&&!meta.resumePages.includes(meta.flashcard.fileName))meta.resumePages.push(meta.flashcard.fileName);
 return meta;
};
function flashcardValid(p,meta){const f=meta.flashcard,c=p.fc;return !!f&&!!c&&c.schema===1&&c.version===3&&c.id===meta.id&&c.signature===f.signature;}
function flashcardComplete(p,meta){return !meta.flashcard||(flashcardValid(p,meta)&&p.fc.complete===true);}
function flashcardCanContinue(p,meta){return !meta.flashcard||(flashcardValid(p,meta)&&(p.fc.complete===true||p.fc.acknowledged===true));}
function blockedBy(p,meta,page,mode=p.m){
 if(window.SOZ_TEACHER_VIEW?.active)return null;
 if(page==='handlungssituation.html')return p.o?null:'index';
 const check=meta.flashcard?.fileName===page;const index=phases.indexOf(page.replace('.html',''));
 if(index<0&&!check)return null;
 if(!p.o)return 'index';
 if(!quizComplete(p,meta))return 'handlungssituation';
 if(check)return phaseComplete(p,meta,'informieren',mode)?null:'informieren';
 for(const phase of phases.slice(0,index)){if(!phaseComplete(p,meta,phase,mode))return phase;if(phase==='informieren'&&!flashcardCanContinue(p,meta))return meta.flashcard.fileName.replace('.html','');}
 return null;
}
function allComplete(p,meta){return p.o&&p.w===meta.orientationSignature&&quizComplete(p,meta)&&phases.every(x=>phaseComplete(p,meta,x))&&flashcardComplete(p,meta);}
// Allocate exact hundredths so the visible item values sum to their budget.
function sharePoints(budget,count,index){if(!count||index<0||index>=count)return 0;const units=Math.round(budget*100);return (Math.floor(units/count)+(index<units%count?1:0))/100;}
function taskPoints(meta,id,mode=1){const ids=Object.keys(meta.tasks||{}).filter(k=>meta.tasks[k].mode===Number(mode));return sharePoints(25,ids.length,ids.indexOf(id));}
function situationValue(p,meta,id){const index=meta.quiz.findIndex(q=>q.id===id),base=sharePoints(15,meta.quiz.length,index);return Math.round(base*((p.qh?.[id]===true||p.qf?.[id]===false)?0.6:1)*100)/100;}
function preparationComplete(p,meta){return p.o&&p.w===meta.orientationSignature&&quizComplete(p,meta)&&phases.every(x=>phaseComplete(p,meta,x));}
function grading(p,meta){
 const tasks=Object.entries(meta.tasks||{}).filter(([,t])=>t.mode===Number(p.m||1));
 const taskScore=tasks.reduce((sum,[id,t])=>sum+(p.t?.[id]===t.signature?taskPoints(meta,id,p.m):0),0);
 const situationScore=(meta.quiz||[]).reduce((sum,q)=>sum+(p.v===meta.quizSignature&&p.q?.[q.id]?.[1]===true&&p.q[q.id][0]===q.correct?situationValue(p,meta,q.id):0),0);
 const termsTotal=Number.isInteger(meta.flashcard?.terms)?meta.flashcard.terms:0;
 const results=flashcardValid(p,meta)&&Array.isArray(p.fc.data?.state?.results)?p.fc.data.state.results.slice(0,termsTotal):[];
 const termsCorrect=results.filter(r=>r?.latest?.correct===true).length;
 const termScore=results.reduce((sum,r,i)=>sum+(r?.latest?.correct===true?sharePoints(60,termsTotal,i):0),0);
 const round=n=>Math.round((n+Number.EPSILON)*100)/100;
 const points=round(Math.min(100,taskScore+situationScore+termScore));
 const recorded=(meta.quiz||[]).filter(q=>typeof p.qf?.[q.id]==='boolean');
 return {points,taskPoints:round(taskScore),situationPoints:round(situationScore),termPoints:round(termScore),termsCorrect,termsTotal,tasksDone:tasks.filter(([id,t])=>p.t?.[id]===t.signature).length,tasksTotal:tasks.length,situationFirstCorrect:recorded.filter(q=>p.qf[q.id]===true).length,situationCounted:recorded.length,situationLegacy:(meta.quiz||[]).filter(q=>p.qf?.[q.id]===null).length,termsFirstCorrect:results.filter(r=>(r?.first||r?.history?.[0])?.correct===true).length,ready:preparationComplete(p,meta)&&points>=75};
}

Object.assign(K,{availableModes,flashcardValid,flashcardComplete,flashcardCanContinue,blockedBy,allComplete,grading,sharePoints,taskPoints,situationValue,preparationComplete});
})();

/* Compact reward UI, shared by the SCORM host and local previews. */
(() => {
  'use strict';
  const format = n => Number(n || 0).toLocaleString('de-DE', {maximumFractionDigits: 2});
  const tier = n => n >= 90 ? 'gold' : n >= 75 ? 'silver' : n >= 50 ? 'bronze' : 'dark';
  const tierName = n => n >= 90 ? 'Gold' : n >= 75 ? 'Silber' : n >= 50 ? 'Bronze' : 'Start';
  const reduced = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const icon = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="m12 6 1.8 3.6 4 .6-2.9 2.8.7 4-3.6-1.9L8.4 17l.7-4-2.9-2.8 4-.6Z"/></svg>';
  function markup(points, earned = false, title = '') {
    const safeTitle = String(title).replace(/[&"<>]/g, c => ({'&':'&amp;','"':'&quot;','<':'&lt;','>':'&gt;'}[c]));
    return '<span class="point-badge' + (earned ? ' point-earned' : '') + '" title="' + safeTitle + '">' + icon + '<span>' + (earned ? '' : '+') + format(points) + ' Punkte</span></span>';
  }
  function badge(points, earned, title) {
    const template = document.createElement('template');
    template.innerHTML = markup(points, earned, title);
    return template.content.firstElementChild;
  }
  function award(anchor, points) {
    if (!anchor || !points) return;
    document.querySelectorAll('.point-reward').forEach(el => el.remove());
    const popup = document.createElement('span');
    popup.className = 'point-reward';
    popup.textContent = '+' + format(points) + ' Punkte';
    popup.setAttribute('role', 'status');
    const rect = anchor.getBoundingClientRect();
    popup.style.left = Math.max(8, Math.min(innerWidth - 150, rect.left)) + 'px';
    popup.style.top = Math.max(10, Math.min(innerHeight - 44, rect.top - 30)) + 'px';
    document.body.append(popup);
    setTimeout(() => popup.remove(), reduced() ? 1600 : 1250);
  }
  let positionObserver = null;
  function mount() {
    // The score belongs to the visible lesson, above its phase navigation.
    // The SCORM host keeps only the persistent unfinished-test reminder.
    if (document.querySelector('[data-scorm-frame]')) return null;
    const page = document.body.dataset.page || '';
    if (document.body.dataset.teacher || page === 'druckansicht.html') return null;
    const material = /^m\d+\.html$/.test(page);
    const focus = document.body.classList.contains('task-focus') ? document.querySelector('.task-accordion[open] .task-focus-panel') : null;
    const target = focus || (material ? document.querySelector('.material-topbar') : document.querySelector('.navigation, .b-phase-overview'));
    if (!target) return null;
    let row = document.querySelector('[data-phase-points]');
    if (!row) {
      row = document.createElement('div');
      row.className = 'phase-points-row no-print';
      row.dataset.phasePoints = '';
    }
    if (row.parentElement !== target) material && !focus ? target.append(row) : target.prepend(row);
    let el = row.querySelector('[data-point-float]');
    if (!el) {
      el = document.createElement('aside');
      el.className = 'point-float no-print';
      el.dataset.pointFloat = '';
      el.innerHTML = '<div class="points-battery" role="progressbar" aria-label="Aktueller SCORM-Punktestand" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span class="points-battery-track"><span class="points-battery-fill"></span></span><strong class="points-battery-label">0 / 100 Punkte</strong></div><span class="points-live sr-only" aria-live="polite" aria-atomic="true"></span>';
      row.append(el);
    }
    if (!positionObserver && window.MutationObserver) {
      positionObserver = new MutationObserver(() => mount());
      positionObserver.observe(document.body, {attributes:true, attributeFilter:['class']});
    }
    return el;
  }
  function render(grade, animate = true) {
    const el = mount();
    if (!el) return;
    const points = Math.max(0, Math.min(100, Number(grade.points) || 0));
    const last = el.dataset.points === undefined ? null : Number(el.dataset.points);
    const track = el.querySelector('.points-battery');
    el.dataset.points = String(points);
    el.dataset.tier = tier(points);
    track.setAttribute('aria-valuenow', String(points));
    track.setAttribute('aria-valuetext', format(points) + ' von 100 Punkten; ' + tierName(points));
    el.querySelector('.points-battery-fill').style.width = points + '%';
    el.querySelector('.points-battery-label').textContent = format(points) + ' / 100 Punkte';
    el.title = 'SCORM: ' + format(grade.taskPoints) + '/25 Bearbeitung · ' + format(grade.situationPoints) + '/15 Handlungssituation · ' + format(grade.termPoints) + '/60 Fachbegriffe. Bronze ab 50, Silber ab 75, Gold ab 90 Punkten. Abgabe und Partnerfeedback werden gesondert in Moodle nachgewiesen.';
    if (animate && last !== null && points > last) {
      el.querySelector('.points-live').textContent = '+' + format(points - last) + ' Punkte. Jetzt ' + format(points) + ' von 100 Punkten.';
      if (!reduced() && el.animate) el.animate([{transform:'scale(1)'},{transform:'scale(1.04)'},{transform:'scale(1)'}], {duration:420});
    }
  }
  window.SOZ_POINTS_UI = {format, tier, markup, badge, award, render};
})();
