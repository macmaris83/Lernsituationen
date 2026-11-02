/* Persistent, clickable video follow-up in the same player margin as the term check. */
(()=>{'use strict';
 const frame=document.querySelector('[data-scorm-frame]'),host=frame&&window.SOZ_SCORM,P=window.SOZ_PROGRESS;
 try{if(!host&&window.parent!==window&&window.parent.SOZ_SCORM)return;}catch{}
 if(!host&&!P)return;
 const owner=host||P,K=window.SOZ_PROGRESS_CORE,M=window.SOZ_PROGRESS_META;
 if(!K||!M?.orientationVideo)return;
 const body=document.body;
 function allowed(){let d=document,w=window;if(frame){try{d=frame.contentDocument;w=frame.contentWindow;}catch{return false;}}return !!d?.body&&!d.body.dataset.teacher&&!w?.SOZ_TEACHER_VIEW?.active&&!['lehrkraft.html','erwartungshorizont.html','druckansicht.html'].includes(d.body.dataset.page);}
 function layout(){
  const pill=document.getElementById('orientation-video-reminder'),fc=document.getElementById('reno-fc-package-reminder');
  if(!pill){delete body.dataset.videoReminderOpen;body.style.removeProperty('--video-reminder-next-top');body.style.removeProperty('--video-reminders-space');return;}
  body.dataset.videoReminderOpen='';body.style.setProperty('--video-reminder-next-top',Math.ceil(pill.getBoundingClientRect().bottom+8)+'px');
  body.style.setProperty('--video-reminders-space',Math.ceil(Math.max(pill.getBoundingClientRect().bottom,fc?.getBoundingClientRect().bottom||0)+10)+'px');
 }
 function open(){
  if(!host){location.assign('index.html#orientation-video-player');return;}
  if(!host.readOnly){const next=host.read();next.b='index.html';if(host.update(next)!==true)return;}
  frame.src='index.html#orientation-video-player';
 }
 function render(){
  const s=owner.read(),video=s.ov,show=allowed()&&video?.skipped===true&&!K.orientationVideoComplete(s,M);
  let pill=document.getElementById('orientation-video-reminder');
  if(!show){pill?.remove();layout();return;}
  if(!pill){pill=document.createElement('button');pill.id='orientation-video-reminder';pill.type='button';pill.className='orientation-video-reminder';const dot=document.createElement('span');dot.className='orientation-video-reminder-dot';dot.setAttribute('aria-hidden','true');const copy=document.createElement('span');const title=document.createElement('strong');title.dataset.videoReminderTitle='';const detail=document.createElement('small');detail.dataset.videoReminderDetail='';copy.append(title,detail);pill.append(dot,copy);pill.addEventListener('click',open);body.prepend(pill);}
  const qs=M.orientationVideo.questions||[],done=qs.filter(q=>video.answers?.[q.id]===q.correct).length;
  pill.querySelector('[data-video-reminder-title]').textContent='Video noch offen · '+done+'/'+qs.length+' Fragen';
  pill.querySelector('[data-video-reminder-detail]').textContent='Ansehen und Fragen nacharbeiten';
  pill.setAttribute('aria-label','Orientierungsvideo noch nicht erledigt. '+done+' von '+qs.length+' Fragen gelöst. Zum Video zurückkehren.');
  layout();
 }
 host?.subscribe(render);frame?.addEventListener('load',render);window.addEventListener('soz-progress',render);window.addEventListener('orientation-video-progress',render);window.addEventListener('resize',layout,{passive:true});
 render();
})();
