(()=>{
  'use strict';
  const page=document.body.dataset.page||'';
  if(!window.BBSCalculator||!(/^(informieren|planen|entscheiden|durchfuehren|bewerten|reflektieren|m\d+)\.html$/.test(page))||document.body.dataset.teacher||document.querySelector('.bbs-calculator'))return;
  const id=window.SOZPAED?.id||document.body.dataset.lsId||'lernangebot';
  const key='bbs-calculator:'+id+':'+location.pathname.replace(/[^/]+$/,'');
  let saved={};try{saved=JSON.parse(sessionStorage.getItem(key)||'{}')||{};}catch{}
  const calculator=new BBSCalculator(saved.calculation);
  const launcher=document.createElement('button');launcher.type='button';launcher.className='bbs-calculator-launcher';launcher.setAttribute('aria-label','Rechner öffnen');launcher.setAttribute('aria-expanded','false');launcher.setAttribute('aria-controls','bbs-calculator-panel');
  launcher.innerHTML='<svg viewBox="0 0 24 28" fill="none" aria-hidden="true"><rect x="2" y="1" width="20" height="26" rx="5" stroke="currentColor" stroke-width="1.7"/><rect x="6" y="5" width="12" height="5" rx="1" fill="#afca0b"/><path d="M7 15h2m6 0h2M7 21h2m6 0h2" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg><span>Rechner</span>';
  const panel=document.createElement('section');panel.id='bbs-calculator-panel';panel.className='bbs-calculator';panel.hidden=true;panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','false');panel.setAttribute('aria-labelledby','bbs-calculator-title');panel.setAttribute('aria-describedby','bbs-calculator-help');
  panel.innerHTML='<div class="bbs-calc-header"><button type="button" class="bbs-calc-drag" aria-label="Rechner verschieben. Mit Touch ziehen oder Pfeiltasten verwenden." aria-keyshortcuts="ArrowUp ArrowDown ArrowLeft ArrowRight"><span id="bbs-calculator-title">Rechner</span></button><button type="button" class="bbs-calc-close" aria-label="Rechner schließen">×</button></div><p id="bbs-calculator-help" class="bbs-calc-sr">Am Kopf verschieben. Grundrechenarten und Prozent. Auch mit der Tastatur bedienbar.</p><div class="bbs-calc-expression" aria-hidden="true"></div><output class="bbs-calc-display" tabindex="0" aria-label="Eingabe und Ergebnis">0</output><div class="bbs-calc-keys"></div><div class="bbs-calc-sr" role="status" aria-live="polite" data-calc-status></div>';
  const keys=[['AC','AC','utility'],['±','Vorzeichen wechseln','utility'],['%','Prozent','utility'],['/','Geteilt','operator'],['7'],['8'],['9'],['*','Mal','operator'],['4'],['5'],['6'],['-','Minus','operator'],['1'],['2'],['3'],['+','Plus','operator'],['0'],[',','Dezimalkomma'],['=','Ergebnis','equals']];
  const symbols={'/':'÷','*':'×','-':'−'};
  for(const [value,label,kind]of keys){const button=document.createElement('button');button.type='button';button.className='bbs-calc-key';button.dataset.key=value;button.dataset.kind=kind||'number';button.textContent=symbols[value]||value;button.setAttribute('aria-label',label||value);panel.querySelector('.bbs-calc-keys').append(button);}
  document.body.append(launcher,panel);
  const display=panel.querySelector('output'),expression=panel.querySelector('.bbs-calc-expression'),status=panel.querySelector('[data-calc-status]'),handle=panel.querySelector('.bbs-calc-drag');
  let position=Array.isArray(saved.position)&&saved.position.length===2&&saved.position.every(Number.isFinite)?saved.position.slice():null;
  function persist(){try{sessionStorage.setItem(key,JSON.stringify({open:!panel.hidden,position,calculation:calculator.snapshot()}));}catch{}}
  function bounds(){const v=window.visualViewport;return {left:(v?.offsetLeft||0)+10,top:(v?.offsetTop||0)+10,width:v?.width||innerWidth,height:v?.height||innerHeight};}
  function place(){if(panel.hidden)return;const b=bounds();panel.style.maxHeight=Math.max(60,b.height-20)+'px';const r=panel.getBoundingClientRect();if(!position)position=[b.left,b.top+Math.max(0,b.height-r.height-86)];position[0]=Math.max(b.left,Math.min(position[0],b.left+b.width-r.width-20));position[1]=Math.max(b.top,Math.min(position[1],b.top+b.height-r.height-20));panel.style.left=position[0]+'px';panel.style.top=position[1]+'px';}
  function draw(announce=false){display.textContent=calculator.display;display.toggleAttribute('data-long',calculator.display.length>11);display.title=calculator.error||calculator.display;expression.textContent=calculator.expression;if(announce)status.textContent=calculator.error||'Ergebnis '+calculator.display;persist();}
  function show(focus=true){panel.hidden=false;launcher.setAttribute('aria-expanded','true');launcher.setAttribute('aria-label','Rechner schließen');place();draw();if(focus)display.focus({preventScroll:true});persist();}
  function hide(){panel.hidden=true;launcher.setAttribute('aria-expanded','false');launcher.setAttribute('aria-label','Rechner öffnen');persist();launcher.focus({preventScroll:true});}
  launcher.addEventListener('click',()=>panel.hidden?show():hide());panel.querySelector('.bbs-calc-close').addEventListener('click',hide);
  function press(value){calculator.press(value);draw(value==='='||!!calculator.error);}
  panel.querySelector('.bbs-calc-keys').addEventListener('click',event=>{const button=event.target.closest('[data-key]');if(button)press(button.dataset.key);});
  panel.addEventListener('keydown',event=>{if(event.ctrlKey||event.altKey||event.metaKey)return;if(event.key==='Escape'){event.preventDefault();event.stopPropagation();hide();return;}if(event.key==='Enter'&&event.target.tagName==='BUTTON')return;const key=event.key==='Enter'?'=':event.key==='Delete'?'AC':event.key;if(/^[0-9.,+*/%=-]$/.test(key)||key==='Backspace'||key==='AC'){event.preventDefault();event.stopPropagation();press(key);}});
  let drag=null;
  handle.addEventListener('pointerdown',event=>{if(event.button!==0)return;event.preventDefault();place();drag={id:event.pointerId,x:event.clientX,y:event.clientY,left:position[0],top:position[1]};handle.setPointerCapture(event.pointerId);panel.classList.add('is-dragging');});
  handle.addEventListener('pointermove',event=>{if(!drag||event.pointerId!==drag.id)return;position=[drag.left+event.clientX-drag.x,drag.top+event.clientY-drag.y];place();});
  const finish=event=>{if(!drag||event.pointerId!==drag.id)return;drag=null;panel.classList.remove('is-dragging');persist();};
  handle.addEventListener('pointerup',finish);handle.addEventListener('pointercancel',finish);handle.addEventListener('lostpointercapture',()=>{drag=null;panel.classList.remove('is-dragging');});
  handle.addEventListener('keydown',event=>{if(!event.key.startsWith('Arrow'))return;event.preventDefault();const step=event.shiftKey?24:8;position[0]+=event.key==='ArrowLeft'?-step:event.key==='ArrowRight'?step:0;position[1]+=event.key==='ArrowUp'?-step:event.key==='ArrowDown'?step:0;place();persist();});
  const reflow=()=>{place();persist();};window.addEventListener('resize',reflow,{passive:true});window.visualViewport?.addEventListener('resize',reflow,{passive:true});window.visualViewport?.addEventListener('scroll',reflow,{passive:true});window.addEventListener('pagehide',persist);
  if(saved.open)show(false);else draw();
})();
