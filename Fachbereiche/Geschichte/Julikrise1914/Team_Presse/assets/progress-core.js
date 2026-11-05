(()=>{'use strict';
const phases=['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren'];
const clone=x=>JSON.parse(JSON.stringify(x));
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(16).padStart(8,'0');}
const text=e=>(e.textContent||'').replace(/\s+/g,' ').trim();
function availableModes(meta){return [...new Set(Object.values(meta.tasks||{}).map(t=>Number(t.mode)))].filter(n=>Number.isInteger(n)&&n>0).sort((a,b)=>a-b);}
function sanitizeOrientationVideo(raw,meta){
 const cfg=meta.orientationVideo;if(!cfg||!raw||raw.signature!==cfg.signature)return null;
 const duration=Number.isFinite(raw.duration)?Math.min(86400,Math.max(0,raw.duration)):0;
 const sorted=(Array.isArray(raw.ranges)?raw.ranges:[]).slice(0,256).filter(r=>Array.isArray(r)&&r.length===2&&r.every(Number.isFinite)).map(r=>[Math.max(0,r[0]),Math.min(duration,Math.max(0,r[1]))]).filter(r=>r[1]>r[0]).sort((a,b)=>a[0]-b[0]);
 const ranges=[];for(const r of sorted){const last=ranges[ranges.length-1];if(last&&r[0]<=last[1]+0.15)last[1]=Math.max(last[1],r[1]);else ranges.push([...r]);}
 const bounded=ranges.slice(0,128).map(r=>r.map(n=>Math.round(n*100)/100));
 const covered=bounded.reduce((sum,r)=>sum+r[1]-r[0],0),ratio=Number(cfg.requiredRatio)||0.98;
 const answers={},attempts={};for(const q of cfg.questions||[]){const value=raw.answers?.[q.id];if(q.options.some(o=>o.id===value))answers[q.id]=value;const n=raw.attempts?.[q.id];if(Number.isInteger(n)&&n>0)attempts[q.id]=Math.min(100000,n);}
 const questionsDone=(cfg.questions||[]).every(q=>answers[q.id]===q.correct),ended=raw.ended===true;
 return {signature:cfg.signature,duration:Math.round(duration*100)/100,ranges:bounded,answers,attempts,ended,skipped:raw.skipped===true,complete:raw.complete===true&&ended&&questionsDone&&duration>0&&covered/duration>=ratio};
}
function orientationVideoComplete(p,meta){return !meta.orientationVideo||sanitizeOrientationVideo(p.ov,meta)?.complete===true;}
function orientationVideoCanContinue(p,meta){return orientationVideoComplete(p,meta)||sanitizeOrientationVideo(p.ov,meta)?.skipped===true;}

function initial(meta,mode){return {s:1,l:meta.id,m:Number(mode)||1,t:{},o:false,ov:null,w:meta.orientationSignature,q:{},qf:{},qn:{},qh:{},v:meta.quizSignature,b:'index.html',a:{assessments:{},feedback:'',nextGoal:''},r:null,k:{},ks:meta.knowledgeSignature,ka:{level:null,evidence:''}};}
function sanitize(raw,meta,mode){const p=initial(meta,mode);if(!raw||raw.s!==1||raw.l!==meta.id)return p;if(raw.ks===meta.knowledgeSignature){for(const q of meta.knowledge||[]){const a=raw.k?.[q.id];if(Array.isArray(a)&&q.options.includes(a[0])&&typeof a[1]==='boolean')p.k[q.id]=[a[0],a[1]];}p.ka={level:Number.isInteger(raw.ka?.level)&&raw.ka.level>=1&&raw.ka.level<=4?raw.ka.level:null,evidence:String(raw.ka?.evidence||'').slice(0,255)};}if(raw.fc&&raw.fc.schema===1&&raw.fc.version===3&&raw.fc.id===meta.id&&typeof raw.fc.signature==='string'&&raw.fc.data!==undefined)p.fc=clone(raw.fc);p.m=Number.isInteger(raw.m)&&availableModes(meta).includes(raw.m)?raw.m:p.m;for(const [k,v]of Object.entries(raw.t||{})){if(meta.tasks[k]?.signature===v)p.t[k]=v;}p.ov=sanitizeOrientationVideo(raw.ov,meta);p.o=raw.o===true&&raw.w===p.w&&orientationVideoCanContinue(p,meta);if(raw.v===p.v)for(const q of meta.quiz){const a=raw.q?.[q.id];if(Array.isArray(a)&&q.options.includes(a[0])&&typeof a[1]==='boolean')p.q[q.id]=[a[0],a[1]];const first=raw.qf?.[q.id];if(typeof first==='boolean'||first===null)p.qf[q.id]=first;else if(!raw.qf&&p.q[q.id])p.qf[q.id]=null;if(raw.qh?.[q.id]===true)p.qh[q.id]=true;const tries=raw.qn?.[q.id];if(Number.isInteger(tries)&&tries>0&&tries<=1000000)p.qn[q.id]=tries;}if(meta.resumePages.includes(raw.b))p.b=raw.b;for(const c of meta.competencies||[]){const a=raw.a?.assessments?.[c.id]||{};p.a.assessments[c.id]={after:Number.isInteger(a.after)&&a.after>=1&&a.after<=4?a.after:null,evidence:String(a.evidence||'')};}p.a.feedback=String(raw.a?.feedback||'');p.a.nextGoal=String(raw.a?.nextGoal||'');if(Number.isInteger(raw.r)&&raw.r>=0&&raw.r<=100000)p.r=raw.r;return p;}
function phaseComplete(p,meta,phase,mode=p.m){const ts=Object.entries(meta.tasks).filter(([,t])=>t.phase===phase&&t.mode===Number(mode));return ts.length>0&&ts.every(([k,t])=>p.t[k]===t.signature);}
function quizComplete(p,meta){return meta.quiz.length>0&&p.v===meta.quizSignature&&meta.quiz.every(q=>p.q[q.id]?.[0]===q.correct&&p.q[q.id]?.[1]===true);}
function flashcardValid(p,meta){const f=meta.flashcard,c=p.fc;return !!f&&!!c&&c.schema===1&&c.version===3&&c.id===meta.id&&c.signature===f.signature;}
function flashcardComplete(p,meta){return !meta.flashcard||(flashcardValid(p,meta)&&p.fc.complete===true);}
function flashcardCanContinue(p,meta){return !meta.flashcard||(flashcardValid(p,meta)&&(p.fc.complete===true||p.fc.acknowledged===true));}
function knowledgeSolved(p,meta){return flashcardComplete(p,meta);}
function knowledgeComplete(p,meta){return flashcardComplete(p,meta);}

function blockedBy(p,meta,page,mode=p.m){if(window.SOZ_TEACHER_VIEW?.active)return null;
 if(page==='handlungssituation.html')return p.o&&orientationVideoCanContinue(p,meta)?null:'index';
 const check=page===(meta.flashcard?.fileName||'begriffstraining.html'),index=phases.indexOf(page.replace('.html',''));
 if(index<0&&!check)return null;
 if(!p.o||!orientationVideoCanContinue(p,meta))return 'index';
 if(!quizComplete(p,meta))return 'handlungssituation';
 if(check)return phaseComplete(p,meta,'informieren',mode)?null:'informieren';
 for(const phase of phases.slice(0,index)){if(!phaseComplete(p,meta,phase,mode))return phase;if(phase==='informieren'&&!flashcardCanContinue(p,meta))return (meta.flashcard?.fileName||'begriffstraining.html').replace('.html','');}
 return null;
}

function allComplete(p,meta){return preparationComplete(p,meta)&&flashcardComplete(p,meta)&&orientationVideoComplete(p,meta);}
// Exact point budgets from the supplied reference, using existing history answers.
function sharePoints(budget,count,index){if(!count||index<0||index>=count)return 0;const units=Math.round(budget*100);return (Math.floor(units/count)+(index<units%count?1:0))/100;}
function taskPoints(meta,id,mode=1){const ids=Object.keys(meta.tasks||{}).filter(k=>meta.tasks[k].mode===Number(mode));return sharePoints(25,ids.length,ids.indexOf(id));}
function situationValue(p,meta,id){const index=meta.quiz.findIndex(q=>q.id===id),base=sharePoints(15,meta.quiz.length,index);return Math.round(base*((p.qh?.[id]===true||p.qf?.[id]===false)?0.6:1)*100)/100;}
function preparationComplete(p,meta){return p.o&&orientationVideoCanContinue(p,meta)&&p.w===meta.orientationSignature&&quizComplete(p,meta)&&phases.every(x=>phaseComplete(p,meta,x));}
function grading(p,meta){
 const tasks=Object.entries(meta.tasks||{}).filter(([,t])=>t.mode===Number(p.m||1));
 const taskScore=tasks.reduce((sum,[id,t])=>sum+(p.t?.[id]===t.signature?taskPoints(meta,id,p.m):0),0);
 const situationScore=(meta.quiz||[]).reduce((sum,q)=>sum+(p.v===meta.quizSignature&&p.q?.[q.id]?.[1]===true&&p.q[q.id][0]===q.correct?situationValue(p,meta,q.id):0),0);
 const termsTotal=Number.isInteger(meta.flashcard?.terms)?meta.flashcard.terms:0;
 const results=flashcardValid(p,meta)&&Array.isArray(p.fc.data?.state?.results)?p.fc.data.state.results.slice(0,termsTotal):[];
 const termsCorrect=results.filter(r=>r?.latest?.correct===true).length;
 const termScore=results.reduce((sum,r,i)=>sum+(r?.latest?.correct===true?sharePoints(60,termsTotal,i):0),0);
 const round=n=>Math.round((n+Number.EPSILON)*100)/100,points=round(Math.min(100,taskScore+situationScore+termScore));
 const recorded=(meta.quiz||[]).filter(q=>typeof p.qf?.[q.id]==='boolean');
 return {points,taskPoints:round(taskScore),situationPoints:round(situationScore),termPoints:round(termScore),termsCorrect,termsTotal,tasksDone:tasks.filter(([id,t])=>p.t?.[id]===t.signature).length,tasksTotal:tasks.length,situationFirstCorrect:recorded.filter(q=>p.qf[q.id]===true).length,situationCounted:recorded.length,situationLegacy:(meta.quiz||[]).filter(q=>p.qf?.[q.id]===null).length,termsFirstCorrect:results.filter(r=>(r?.first||r?.history?.[0])?.correct===true).length,ready:preparationComplete(p,meta)&&points>=75};
}

function setTask(p,meta,k,done){if(!meta.tasks[k])return;if(done)p.t[k]=meta.tasks[k].signature;else delete p.t[k];}
function decorate(root,phase){for(const panel of root.querySelectorAll('[data-mode-panel]')){const mode=Number(panel.dataset.modePanel);let number=0;for(const a of panel.querySelectorAll('.assignment-frame')){number++;const body=a.querySelector('.assignment-body');if(!body)throw Error('Auftragsinhalt fehlt.');const id=phases.indexOf(phase)+':'+mode+':'+number;a.dataset.taskId=id;a.dataset.taskSignature=hash(text(body));let label=a.querySelector('[data-completion-label]');if(!label){label=root.ownerDocument.createElement('label');label.className='task-completion no-print';label.dataset.completionLabel='';label.setAttribute('contenteditable','false');label.innerHTML='<input type="checkbox" data-task-complete><span class="sr-only">Aufgabe erledigt</span>';a.appendChild(label);}const input=label.querySelector('input');input.dataset.taskId=id;input.setAttribute('aria-label','Aufgabe '+number+' als erledigt markieren');input.removeAttribute('checked');input.setAttribute('disabled','');input.checked=false;}}
}
function taskNumbers(data,parser,overrides={}){const result={},totals={};for(const phase of phases){const source=overrides[phase+'.html']||data.pages[phase+'.html'];const doc=parser.parseFromString(source,'text/html');for(const panel of doc.querySelectorAll('[data-mode-panel]')){const mode=Number(panel.dataset.modePanel);for(const card of panel.querySelectorAll('.assignment-frame')){totals[mode]=(totals[mode]||0)+1;result[card.dataset.taskId]=totals[mode];}}}return result;}
function numberData(data,parser){const numbers=taskNumbers(data,parser);for(const phase of phases){const doc=parser.parseFromString('<div>'+data.pages[phase+'.html']+'</div>','text/html');for(const card of doc.querySelectorAll('.assignment-frame')){const n=numbers[card.dataset.taskId];card.dataset.taskNumber=n;const number=card.querySelector('.assignment-number');if(number){number.textContent=n;number.setAttribute('aria-label','Aufgabe '+n);}card.querySelector('[data-task-complete]')?.setAttribute('aria-label','Aufgabe '+n+' als erledigt markieren');}data.pages[phase+'.html']=doc.body.firstElementChild.innerHTML;}}

function metadataFrom(data,parser){const tasks={};for(const phase of phases){const doc=parser.parseFromString('<div>'+data.pages[phase+'.html']+'</div>','text/html');decorate(doc.body,phase);for(const a of doc.querySelectorAll('.assignment-frame')){const k=a.dataset.taskId;tasks[k]={phase,mode:Number(a.closest('[data-mode-panel]').dataset.modePanel),signature:a.dataset.taskSignature};}data.pages[phase+'.html']=doc.body.firstElementChild.innerHTML;}
 numberData(data,parser);const modes=availableModes({tasks});for(const phase of phases)for(const mode of modes)if(!Object.values(tasks).some(t=>t.phase===phase&&t.mode===mode))throw Error('Aufträge fehlen in '+phase+', Lernweg '+mode+'.');
 const doc=parser.parseFromString('<div>'+data.pages['handlungssituation.html']+'</div>','text/html');const payload=doc.querySelector('[data-situation-quiz] script[type="application/json"]');const qs=payload?JSON.parse(payload.textContent):[];if(!qs.length)throw Error('Der Kurztest der Handlungssituation fehlt.');const quiz=qs.map(q=>({id:q.id,correct:q.correct,options:q.options.map(a=>a.value)}));
 const index=parser.parseFromString('<div>'+data.pages['index.html']+'</div>','text/html');if(!index.querySelector('[data-orientation-completion]')){const el=index.createElement('section');el.className='orientation-completion no-print';el.dataset.orientationCompletion='';el.setAttribute('contenteditable','false');el.innerHTML='<label><input type="checkbox" data-orientation-complete>Orientierung gelesen</label><p class="progress-counter" data-progress-status role="status"></p>';index.body.firstElementChild.appendChild(el);}index.querySelectorAll('[data-orientation-complete]').forEach(e=>{e.removeAttribute('checked');e.setAttribute('disabled','');e.checked=false;});data.pages['index.html']=index.body.firstElementChild.innerHTML;index.querySelectorAll('[data-orientation-completion]').forEach(e=>e.remove());
 const kd=parser.parseFromString('<div>'+(data.pages['begriffstraining.html']||'')+'</div>','text/html'),kp=kd.querySelector('[data-begriffs-quiz] script[type="application/json"]'),kqs=kp?JSON.parse(kp.textContent):[];if(!kqs.length&&!data.flashcard)throw Error('Die Begriffsaufgaben fehlen.');const knowledge=kqs.map(q=>({id:q.id,correct:q.correct,options:q.options.map(a=>a.value)}));
 return {orientationVideo:data.orientationVideo||null,flashcard:data.flashcard||null,legacyTaskDictionaries:data.legacyTaskDictionaries||{},knowledge,knowledgeSignature:hash(JSON.stringify(kqs)),id:data.id,availableModes:modes,competencies:data.competencies.map(c=>({id:c.id,label:c.label})),tasks,quiz,quizSignature:hash(JSON.stringify(qs)),orientationSignature:hash(text(index.body)),resumePages:[...new Set([...Object.keys(data.pages).filter(p=>!['lehrkraft.html','erwartungshorizont.html','druckansicht.html'].includes(p)),...(data.flashcard?[data.flashcard.fileName]:[])])]};}
window.SOZ_PROGRESS_CORE={orientationVideoCanContinue,orientationVideoComplete,sanitizeOrientationVideo,flashcardValid,flashcardComplete,flashcardCanContinue,preparationComplete,grading,sharePoints,taskPoints,situationValue,availableModes,phases,clone,hash,text,initial,sanitize,phaseComplete,quizComplete,knowledgeSolved,knowledgeComplete,blockedBy,allComplete,setTask,decorate,metadataFrom,taskNumbers,numberData};
})();

/* Metallic point UI from supplied reference. */
/* Shared form 1.8.8 presentation; scoring and persistent progress remain package-owned. */
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
