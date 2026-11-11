/* Tradiert: W1 only; existing task identities are retained. */
(()=>{'use strict';
const D=window.SOZPAED,C=window.SOZ_CONFIG||{};if(!D||window.SOZ_TEACHER_VIEW)return;
const key='soz-teacher-view:'+D.id+':'+location.pathname.replace(/[^/]+$/,'')+':'+(C.packageRevision||'base');
let value=null;try{value=JSON.parse(sessionStorage.getItem(key)||'null');}catch{}
const active=value?.active===true;let learner='';try{learner=window.parent.SOZ_SCORM?.learner||'';}catch{}
window.SOZ_TEACHER_VIEW={active,learner,get mode(){return 1;}};
function remember(mode){value={active:true,mode:1};sessionStorage.setItem(key,JSON.stringify(value));}
function init(){
 try{if(window.parent!==window){const notice=window.parent.document.querySelector('[data-scorm-notice]');if(notice){notice.hidden=active||!window.parent.SOZ_SCORM?.message;if(!active)notice.textContent=window.parent.SOZ_SCORM?.message||'';}}}catch{}
 document.querySelectorAll('.footer-utils a[href="lehrkraft.html"]').forEach(a=>{a.innerHTML="<svg class=\"editor-settings-icon\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\" stroke-linecap=\"round\" stroke-linejoin=\"round\" aria-hidden=\"true\"><path d=\"m9 3-1 3-3 1-2 3 2 2-1 3 2 3 3-1 2 2h3l1-3 3-1 2-3-2-2 1-3-2-3-3 1-2-2z\"/><circle cx=\"12\" cy=\"11\" r=\"3\"/></svg><span>Editor</span>";a.setAttribute('aria-label','Editor öffnen');});
 const panel=document.querySelector('#teacher-panel')||(document.body.dataset.teacher?document.querySelector('.lesson-content'):null);
 if(panel){
  const section=document.createElement('section');section.className='teacher-card';
  const title=document.createElement('h2');title.textContent='Lernsituation als Lehrkraft ansehen';
  const explanation=document.createElement('p');explanation.textContent='Alle Phasen direkt öffnen und die Lernsituation testen. Der Teststand ist vom Lernstand der Lernenden getrennt.';
  const button=document.createElement('button');button.className='primary';button.dataset.startTeacherView='';button.textContent='Lehrkräfteansicht starten';
  button.addEventListener('click',()=>{if(panel.hidden)return;try{remember(window.SOZ_API?.getSettings().mode||C.mode);location.href='index.html';}catch{explanation.textContent='Die Lehrkräfteansicht benötigt Sitzungsspeicher. Bitte das Paket in einem Browserfenster öffnen, das Speicherung erlaubt.';}});
  section.append(title,explanation,button);panel.prepend(section);
 }
 if(!active||document.body.dataset.teacher||document.body.dataset.page==='druckansicht.html')return;
 document.body.classList.add('teacher-view-active');
 const bar=document.createElement('aside');bar.className='teacher-view-bar no-print';bar.setAttribute('aria-label','Lehrkräfteansicht');
 const label=document.createElement('strong');label.textContent='Lehrkräfteansicht · Alle Phasen frei';
 const paths=document.createElement('label');paths.textContent='Lernweg ';
 const select=document.createElement('select');select.setAttribute('aria-label','Lernweg in der Lehrkräfteansicht');
 for(const n of (window.SOZ_API?.availableModes?.()||[...new Set(Object.values(window.SOZ_PROGRESS_META?.tasks||{}).map(t=>Number(t.mode)))].sort((a,b)=>a-b))){const option=document.createElement('option');option.value=n;option.textContent='Weg '+n;select.append(option);}select.value=window.SOZ_API?.getSettings().mode||value.mode;
 select.addEventListener('change',()=>{remember(select.value);try{sessionStorage.removeItem('teacher:task-focus-return:'+D.id);}catch{}const next=new URL(location.href);next.searchParams.delete('aufgabe');next.searchParams.delete('rueckaufgabe');location.replace(next.href);});paths.append(select);if(select.options.length<2)paths.hidden=true;
 const exit=document.createElement('button');exit.textContent='Lernendenansicht';exit.dataset.exitTeacherView='';exit.addEventListener('click',()=>{sessionStorage.removeItem(key);location.reload();});
 bar.append(label,paths,exit);document.body.prepend(bar);
 const measure=()=>document.body.style.setProperty('--teacher-view-height',bar.getBoundingClientRect().height+'px');measure();new ResizeObserver(measure).observe(bar);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();

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

/* Shared XP UI from IDN. */
/* Shared form 1.8.8: 100 XP from the existing checks; progress stays package-owned. */
(() => {
  'use strict';
  const K = window.SOZ_PROGRESS_CORE, meta = window.SOZ_PROGRESS_META;
  if (!K || typeof K.grading !== 'function' || K.grading.__xp100) return;
  const original = K.grading;
  // The older compatibility core has no term test: 25 task + 15 situation XP.
  // Allocate the same 5:3 ratio directly in hundredths, so item badges sum to 100.
  // Native 100-XP cores, their first-attempt rules and completion gates stay intact.
  const nativeMaximum = meta ? Number(original(K.initial(meta, 1), meta).maxPoints || 100) : 100;
  if (nativeMaximum === 40) {
    K.taskPoints = (data, id, mode = 1) => {
      const ids = Object.keys(data.tasks || {}).filter(key => data.tasks[key].mode === Number(mode));
      return K.sharePoints(62.5, ids.length, ids.indexOf(id));
    };
    K.situationValue = (state, data, id) => {
      const base = K.sharePoints(37.5, data.quiz.length, data.quiz.findIndex(question => question.id === id));
      const factor = state.qh?.[id] || state.qf?.[id] === false ? 0.6 : 1;
      return Math.round(base * factor * 100) / 100;
    };
  }
  const grading = function(state, data) {
    const grade = original.call(this, state, data);
    return {...grade, maxPoints: 100};
  };
  grading.__xp100 = true;
  K.grading = grading;
})();
(() => {
  'use strict';
  const format = n => Number(n || 0).toLocaleString('de-DE', {maximumFractionDigits: 2});
  const tier = n => n >= 90 ? 'gold' : n >= 75 ? 'silver' : n >= 50 ? 'bronze' : 'dark';
  const tierName = n => n >= 90 ? 'Gold' : n >= 75 ? 'Silber' : n >= 50 ? 'Bronze' : 'Start';
  const reduced = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const icon = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"/><path d="m12 6 1.8 3.6 4 .6-2.9 2.8.7 4-3.6-1.9L8.4 17l.7-4-2.9-2.8 4-.6Z"/></svg>';
  function markup(points, earned = false, title = '') {
    const safeTitle = String(title).replace(/[&"<>]/g, c => ({'&':'&amp;','"':'&quot;','<':'&lt;','>':'&gt;'}[c]));
    return '<span class="point-badge' + (earned ? ' point-earned' : '') + '" title="' + safeTitle + '">' + icon + '<span>' + (earned ? '' : '+') + format(points) + ' XP</span></span>';
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
    popup.textContent = '+' + format(points) + ' XP';
    popup.setAttribute('role', 'status');
    const rect = anchor.getBoundingClientRect();
    popup.style.left = Math.max(8, Math.min(innerWidth - 150, rect.left)) + 'px';
    popup.style.top = Math.max(10, Math.min(innerHeight - 44, rect.top - 30)) + 'px';
    document.body.append(popup);
    setTimeout(() => popup.remove(), reduced() ? 1600 : 1250);
  }
  let positionObserver = null;
  function mount() {
    // Keep the compact score at the top right of the current learning view.
    // The SCORM host keeps only the persistent unfinished-test reminder.
    if (document.querySelector('[data-scorm-frame]')) return null;
    const page = document.body.dataset.page || '';
    if (document.body.dataset.teacher || page === 'druckansicht.html') return null;
    const focus = document.body.classList.contains('task-focus')
      ? document.querySelector('.task-accordion[open] .task-focus-panel') : null;
    const navigation = document.querySelector('.navigation, .b-phase-overview');
    const heading = navigation?.querySelector('.nav-heading .eyebrow');
    if (heading && heading.textContent !== 'Phasenübersicht') heading.textContent = 'Phasenübersicht';
    const target = focus || (/^m\d+\.html$/.test(page) ? document.querySelector('.main') : navigation);
    if (!target) return null;
    let row = document.querySelector('[data-phase-points]');
    if (!row) {
      row = document.createElement('div');
      row.className = 'phase-points-row no-print';
      row.dataset.phasePoints = '';
    }
    if (row.parentElement !== target) target.prepend(row);
    let el = row.querySelector('[data-point-float]');
    if (!el) {
      el = document.createElement('aside');
      el.className = 'point-float no-print';
      el.dataset.pointFloat = '';
      el.innerHTML = '<div class="points-battery" role="progressbar" aria-label="Aktueller SCORM-Punktestand" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span class="points-battery-track"><span class="points-battery-fill"></span></span><strong class="points-battery-label">0 / 100 XP</strong></div><span class="points-live sr-only" aria-live="polite" aria-atomic="true"></span>';
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
    const maximum=grade.maxPoints||100;const points = Math.max(0, Math.min(maximum, Number(grade.points) || 0));
    const last = el.dataset.points === undefined ? null : Number(el.dataset.points);
    const track = el.querySelector('.points-battery');
    el.dataset.points = String(points);
    el.dataset.tier = tier(points/maximum*100);
    track.setAttribute('aria-valuemax',String(maximum));track.setAttribute('aria-valuenow', String(points));
    track.setAttribute('aria-valuetext', format(points) + ' von '+maximum+' XP; ' + tierName(points/maximum*100));
    el.querySelector('.points-battery-fill').style.width = (points/maximum*100) + '%';
    el.querySelector('.points-battery-label').textContent = format(points) + ' / '+maximum+' XP';
    el.title = 'XP aus dem gespeicherten Lernstand: '+format(points)+' / '+maximum;
    if (animate && last !== null && points > last) {
      el.querySelector('.points-live').textContent = '+' + format(points - last) + ' XP. Jetzt ' + format(points) + ' von '+maximum+' XP.';
      if (!reduced() && el.animate) el.animate([{transform:'scale(1)'},{transform:'scale(1.04)'},{transform:'scale(1)'}], {duration:420});
    }
  }
  window.SOZ_POINTS_UI = {format, tier, markup, badge, award, render};
})();
