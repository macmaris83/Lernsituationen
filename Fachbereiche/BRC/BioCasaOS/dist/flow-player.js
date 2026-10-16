/* Zahlenwege innerhalb der kleinen Bilanz. Keine Änderung fachlicher Daten. */
(function(root){
'use strict';
function create(options={}){
 const schedule=options.schedule||root.setTimeout,cancel=options.cancel||root.clearTimeout,now=options.now||Date.now;
 const reduced=options.reduced||(()=>!!root.window?.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
 let active=null,serial=0,autoTimer=null;
 const seenAuto=new Set();
 function controls(s,text){const b=s.host.querySelector('[data-mini-play]');if(b){b.textContent=text;b.setAttribute('aria-pressed',String(!!s.timer&&!s.paused));}}
 function status(s,text){const el=s.host.querySelector('[data-mini-status]');if(el)el.textContent=text;}
 function clearMovement(s){for(const a of s.animations)a.cancel();s.animations=[];for(const el of s.overlays)el.remove();s.overlays=[];}
 function stop(){cancel(autoTimer);autoTimer=null;if(!active)return;const s=active;active=null;cancel(s.timer);clearMovement(s);s.host.classList.remove('mini-playing');for(const el of s.host.querySelectorAll('.mini-flow-active,.mini-target-active'))el.classList.remove('mini-flow-active','mini-target-active');const check=s.host.querySelector('[data-mini-check]');if(check)check.hidden=true;controls(s,'Zahlenweg abspielen');}
 function autoplay(scope,{repeat=false}={}){
  if(!scope?.querySelectorAll)return;
  cancel(autoTimer);autoTimer=schedule(()=>{
   autoTimer=null;
   const host=Array.from(scope.querySelectorAll('[data-mini-autoplay="true"]')).find(h=>{
    const rect=h.getBoundingClientRect();
    return h.isConnected!==false&&rect.width>0&&rect.height>0&&(repeat||!seenAuto.has(h.dataset.miniSignature));
   });
   if(!host||(active?.host===host&&active.phase!=='done')||active?.phase==='checking'||active?.paused)return;
   seenAuto.add(host.dataset.miniSignature);start(host,true);
  },500);
 }
 function replace(scope,key,html){
  if(!scope)return false;
  if(scope.getAttribute('data-mini-render-key')===key)return false;
  // An unchanged blur/change must retain the running flight and all quiz inputs.
  if(active&&scope.contains(active.host))stop();
  scope.innerHTML=html;scope.setAttribute('data-mini-render-key',key);return true;
 }
 function later(s,fn,delay){s.remaining=delay;s.callback=fn;s.due=now()+delay;s.timer=schedule(()=>{s.timer=null;if(active===s)fn();},delay);}
 function finish(s){clearMovement(s);s.phase='done';s.host.classList.remove('mini-playing');for(const el of s.host.querySelectorAll('.mini-flow-active,.mini-target-active'))el.classList.remove('mini-flow-active','mini-target-active');for(const el of s.host.querySelectorAll('[data-mini-target]'))el.classList.add('mini-arrived');controls(s,'Noch einmal abspielen');status(s,'Zahlenwege abgeschlossen. Vergleiche die Veränderungen und die Bilanzsumme.');}
 function movement(s,source,target){
  if(reduced()||!target)return;
  const doc=s.host.ownerDocument||root.document,h=s.host.getBoundingClientRect(),a=source.getBoundingClientRect(),b=target.getBoundingClientRect();if(!h.width||!a.width||!b.width)return;
  const sx=a.left-h.left+a.width/2,sy=a.bottom-h.top,tx=b.left-h.left+b.width/2,ty=b.top-h.top+13;
  const overlay=doc.createElement('div');overlay.className='mini-flight-layer';overlay.setAttribute('aria-hidden','true');
  const path=doc.createElementNS('http://www.w3.org/2000/svg','svg'),marker='mini-arrow-'+(++serial);path.setAttribute('width',String(h.width));path.setAttribute('height',String(h.height));path.setAttribute('viewBox','0 0 '+h.width+' '+h.height);
  path.innerHTML='<defs><marker id="'+marker+'" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#007f89" stroke-width="1.5"/></marker></defs><path class="mini-flight-line" d="M'+sx+' '+sy+' L'+tx+' '+ty+'" fill="none" stroke="#007f89" stroke-width="2.5" marker-end="url(#'+marker+')"/>';
  overlay.appendChild(path);const chip=doc.createElement('span');chip.className='mini-flying-amount';chip.textContent=source.dataset.amountText||'';overlay.appendChild(chip);s.host.appendChild(overlay);s.overlays.push(overlay);
  const from='translate('+sx+'px,'+sy+'px) translate(-50%,-50%)',to='translate('+tx+'px,'+ty+'px) translate(-50%,-50%)';
  try{if(!chip.animate)throw Error('Web Animations unavailable');s.animations.push(chip.animate([{transform:from,opacity:1},{transform:to,opacity:1}],{duration:1400,easing:'ease-in-out',fill:'forwards'}));}
  catch{
   // CSS fallback also moves the amount when the embedded web view lacks animate().
   let remaining=1400,started=now();chip.style.transform=from;chip.getBoundingClientRect();
   const resume=()=>{started=now();chip.getBoundingClientRect();chip.style.transition='transform '+remaining+'ms ease-in-out';chip.style.transform=to;};resume();
   s.animations.push({pause(){remaining=Math.max(0,remaining-(now()-started));const current=doc.defaultView?.getComputedStyle(chip).transform||chip.style.transform;chip.style.transition='none';chip.style.transform=current;},play:resume,cancel(){chip.style.transition='none';}});
  }
 }
 function arrive(s){if(active!==s)return;const target=s.target;if(target)target.classList.add('mini-arrived');clearMovement(s);s.phase='arrived';if(s.auto)later(s,()=>show(s,s.index+1),650);else{controls(s,'Zahlenweg abspielen');status(s,'Pfeil '+(s.index+1)+' von '+s.steps.length+' angekommen. Mit „Nächster Pfeil“ weitergehen.');}}
 function show(s,index){
  if(active!==s)return;cancel(s.timer);s.timer=null;clearMovement(s);
  for(const el of s.host.querySelectorAll('.mini-flow-active,.mini-target-active'))el.classList.remove('mini-flow-active','mini-target-active');
  if(index===1&&index<s.steps.length&&!s.checkPassed&&options.beforeSecond){s.phase='checking';s.index=0;if(options.beforeSecond(s.host)===false){controls(s,'Verständnischeck beantworten');status(s,'Vor dem zweiten Zahlenweg: Beantworte den kurzen Verständnischeck.');return;}s.checkPassed=true;}
  if(index>=s.steps.length){finish(s);return;}s.index=index;s.phase='moving';s.paused=false;const source=s.steps[index],target=s.host.querySelector('[data-mini-target="'+source.dataset.targetAccount+'"]');s.target=target;source.classList.add('mini-flow-active');target?.classList.add('mini-target-active');status(s,'Pfeil '+(index+1)+' von '+s.steps.length+': '+source.dataset.flowLabel);s.host.classList.add('mini-playing');
  if(reduced()){target?.classList.add('mini-arrived');if(s.auto){status(s,'Schritt '+(index+1)+' von '+s.steps.length+' · Bewegung reduziert: '+source.dataset.flowLabel);later(s,()=>arrive(s),1500);controls(s,'Pausieren');}else{s.phase='arrived';controls(s,'Zahlenweg abspielen');}return;}
  movement(s,source,target);later(s,()=>arrive(s),1500);controls(s,'Pausieren');
 }
 function start(host,auto=true,index=0){stop();if(!host)return;const steps=Array.from(host.querySelectorAll('[data-mini-flow]'));if(!steps.length)return;const s={host,steps,index:-1,phase:'ready',paused:false,auto,timer:null,animations:[],overlays:[]};active=s;for(const t of host.querySelectorAll('[data-mini-target]'))t.classList.remove('mini-arrived');show(s,index);}
 function play(host){if(active?.host===host&&active.phase==='checking'){options.beforeSecond?.(host);return;}if(active?.host===host&&active.phase!=='done'&&active.timer){const s=active;s.remaining=Math.max(0,s.due-now());cancel(s.timer);s.timer=null;s.paused=true;for(const a of s.animations)a.pause();controls(s,'Fortsetzen');status(s,'Animation pausiert.');return;}if(active?.host===host&&active.paused){const s=active;s.paused=false;for(const a of s.animations)a.play();later(s,s.callback,s.remaining);controls(s,'Pausieren');return;}start(host,true);}
 function next(host){if(active?.host===host){const s=active;if(s.phase==='checking'){options.beforeSecond?.(host);return;}cancel(s.timer);s.timer=null;s.auto=false;s.target?.classList.add('mini-arrived');show(s,s.index+1);}else start(host,false);}
 function continueAfterCheck(host){if(active?.host!==host||active.phase!=='checking')return false;const s=active;s.checkPassed=true;const check=host.querySelector('[data-mini-check]');if(check)check.hidden=true;show(s,1);return true;}
 function relayout(){if(active?.phase==='moving'&&!active.paused)show(active,active.index);}
 return Object.freeze({play,next,stop,autoplay,replace,relayout,continueAfterCheck,getState:()=>active?{index:active.index,phase:active.phase,paused:active.paused,count:active.steps.length}:null});
}
root.BioCasaFlows=Object.freeze({create});
})(globalThis);
