import test from 'node:test';
import assert from 'node:assert/strict';
import '../dist/flow-player.js';

function harness({reduced=false,gate=()=>true,webAnimations='available'}={}){
 let clock=0,id=0;const timers=new Map(),animations=[];
 const node=(rect={left:0,top:0,width:800,height:700,bottom:700})=>({dataset:{},style:{},children:[],hidden:true,textContent:'',classList:{values:new Set(),add(...xs){xs.forEach(x=>this.values.add(x));},remove(...xs){xs.forEach(x=>this.values.delete(x));},has(x){return this.values.has(x);}},getAttribute(k){return this[k]??null;},setAttribute(k,v){this[k]=v;},contains(child){return child===this||this.children.some(c=>c.contains(child));},getBoundingClientRect:()=>rect,appendChild(child){this.children.push(child);child.parent=this;},remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);},animate(){const a={paused:false,cancelled:false,pause(){this.paused=true;},play(){this.paused=false;},cancel(){this.cancelled=true;}};animations.push(a);return a;}});
 const host=node(),play=node(),status=node(),box=node();
 const sources=['280','288'].map((account,i)=>Object.assign(node({left:10,top:80+i*50,width:300,height:40,bottom:120+i*50}),{dataset:{targetAccount:account,amountText:'200,00 €',flowLabel:account}}));
 const targets=sources.map((s,i)=>Object.assign(node({left:10,top:300+i*80,width:300,height:70,bottom:370+i*80}),{dataset:{miniTarget:s.dataset.targetAccount}}));
 host.ownerDocument={createElement:()=>{const n=node();if(webAnimations==='missing')n.animate=null;if(webAnimations==='throws')n.animate=()=>{throw Error('Unavailable in this web view');};return n;},createElementNS:()=>node()};
 host.dataset.miniSignature='entry-1';const scope={querySelectorAll:()=>[host]};
 host.querySelector=s=>s==='[data-mini-play]'?play:s==='[data-mini-status]'?status:s==='[data-mini-check]'?box:targets.find(t=>s==='[data-mini-target="'+t.dataset.miniTarget+'"]')||null;
 host.querySelectorAll=s=>s==='[data-mini-flow]'?sources:s==='[data-mini-target]'?targets:[...sources,...targets];
 const player=BioCasaFlows.create({schedule:(fn,delay)=>{const n=++id;timers.set(n,{fn,due:clock+delay});return n;},cancel:n=>timers.delete(n),now:()=>clock,reduced:()=>reduced,beforeSecond:gate});
 function advance(ms){const end=clock+ms;while(true){const next=[...timers].sort((a,b)=>a[1].due-b[1].due)[0];if(!next||next[1].due>end)break;clock=next[1].due;timers.delete(next[0]);next[1].fn();}clock=end;}
 return {player,host,scope,play,status,box,sources,targets,timers,animations,advance};
}
test('Pfeil und Betrag fliegen zur richtigen Position; Pause hält Bewegung und Folgepfeil an',()=>{
 const h=harness();h.player.play(h.host);assert.equal(h.player.getState().index,0);assert.equal(h.host.children.length,1);assert.ok(h.targets[0].classList.has('mini-target-active'));h.advance(500);h.player.play(h.host);assert.equal(h.animations[0].paused,true);h.advance(5000);assert.equal(h.player.getState().index,0);h.player.play(h.host);h.advance(1000);assert.ok(h.targets[0].classList.has('mini-arrived'));h.advance(650);assert.equal(h.player.getState().index,1);h.advance(2150);assert.equal(h.player.getState().phase,'done');assert.equal(h.host.children.length,0);
});
test('Vor dem zweiten Pfeil ist der Check zwingend: weder Weiter noch Abspielen umgehen ihn',()=>{
 let prompts=0;const h=harness({gate:()=>{prompts++;return false;}});h.player.play(h.host);h.advance(2150);assert.equal(h.player.getState().phase,'checking');assert.equal(h.animations.length,1);h.player.next(h.host);h.player.play(h.host);h.advance(5000);assert.equal(h.animations.length,1);assert.equal(prompts,3);assert.equal(h.player.continueAfterCheck(h.host),true);assert.equal(h.player.getState().index,1);h.advance(2150);assert.equal(h.player.getState().phase,'done');assert.equal(h.animations.length,2);
});
test('Manueller Ablauf und reduzierte Bewegung erhalten dieselbe Check-Unterbrechung',()=>{
 const h=harness({reduced:true,gate:()=>false});h.player.next(h.host);assert.equal(h.player.getState().phase,'arrived');assert.equal(h.animations.length,0);h.player.next(h.host);assert.equal(h.player.getState().phase,'checking');h.player.continueAfterCheck(h.host);assert.equal(h.player.getState().index,1);assert.equal(h.player.getState().phase,'arrived');h.player.next(h.host);assert.equal(h.player.getState().phase,'done');assert.equal(h.timers.size,0);
});
test('Abbruch bei Navigation entfernt laufende Flüge und alle verzögerten Schritte',()=>{
 const h=harness();h.player.play(h.host);h.player.stop();h.advance(10000);assert.equal(h.player.getState(),null);assert.equal(h.host.children.length,0);assert.equal(h.timers.size,0);assert.equal(h.animations[0].cancelled,true);assert.equal(h.sources[0].classList.has('mini-flow-active'),false);
});

test('Vollständiger sichtbarer Entwurf startet automatisch; unsichtbare doppelte Vorschauen werden übersprungen',()=>{
 const h=harness({gate:()=>false}),hidden={dataset:{miniSignature:'entry-1'},getBoundingClientRect:()=>({width:0,height:0})};h.scope.querySelectorAll=()=>[hidden,h.host];h.player.autoplay(h.scope);assert.equal(h.player.getState(),null);h.advance(499);assert.equal(h.animations.length,0);h.advance(1);assert.equal(h.animations.length,1);h.advance(2150);assert.equal(h.player.getState().phase,'checking');h.player.autoplay(h.scope);h.advance(500);assert.equal(h.player.getState().phase,'checking');h.player.continueAfterCheck(h.host);h.advance(2150);assert.equal(h.player.getState().phase,'done');h.player.autoplay(h.scope);h.advance(500);assert.equal(h.animations.length,2);h.player.autoplay(h.scope,{repeat:true});h.advance(500);assert.equal(h.animations.length,3);
});
test('Unverändertes input/change erhält den laufenden Pfeil und die Quizantworten; echte Änderung stoppt ihn',()=>{
 const h=harness({gate:()=>false}),container={key:null,innerHTML:'',contains:x=>x===h.host,getAttribute(){return this.key;},setAttribute(k,v){this.key=v;}};
 h.player.replace(container,'200','Vorschau');h.player.autoplay(h.scope);h.advance(500);assert.equal(h.player.getState().phase,'moving');assert.equal(h.player.replace(container,'200','Vorschau'),false);assert.equal(h.animations[0].cancelled,false);h.advance(2150);h.box.answer='Eigene angefangene Antwort';assert.equal(h.player.replace(container,'200','Vorschau'),false);assert.equal(h.player.getState().phase,'checking');assert.equal(h.box.answer,'Eigene angefangene Antwort');assert.equal(h.player.replace(container,'250','Geänderte Vorschau'),true);h.advance(5000);assert.equal(h.player.getState(),null);assert.equal(h.host.children.length,0);
});
test('Navigation vor Autostart verhindert verspätete Flüge; pausierte Abläufe werden nicht automatisch neu gestartet',()=>{
 const h=harness();h.player.autoplay(h.scope);h.player.stop();h.advance(1000);assert.equal(h.animations.length,0);h.player.autoplay(h.scope);h.advance(500);h.player.play(h.host);h.player.autoplay(h.scope,{repeat:true});h.advance(500);assert.equal(h.player.getState().paused,true);assert.equal(h.animations.length,1);
});
test('Ohne Web Animations API oder bei deren Fehler bewegt CSS den Betrag mit Pause und Fortsetzen',()=>{
 for(const webAnimations of ['missing','throws']){const h=harness({webAnimations});h.player.play(h.host);const chip=h.host.children[0].children[1];assert.equal(chip.style.transition,'transform 1400ms ease-in-out');assert.ok(chip.style.transform.includes('313px'));h.advance(500);h.player.play(h.host);assert.equal(chip.style.transition,'none');h.player.play(h.host);assert.equal(chip.style.transition,'transform 900ms ease-in-out');h.advance(1650);assert.equal(h.player.getState().index,1);}
});
test('Reduzierte Bewegung läuft automatisch mit Hervorhebungen und hält trotzdem vor dem zweiten Schritt an',()=>{
 const h=harness({reduced:true,gate:()=>false});h.player.autoplay(h.scope);h.advance(500);assert.equal(h.animations.length,0);assert.ok(h.status.textContent.includes('Bewegung reduziert'));h.advance(2150);assert.equal(h.player.getState().phase,'checking');h.player.continueAfterCheck(h.host);h.advance(2150);assert.equal(h.player.getState().phase,'done');assert.equal(h.animations.length,0);
});
test('iPad-Tastatur und Größenänderung berechnen Pfeilpositionen neu, ohne zweiten Zahlenweg oder Check zu überspringen',()=>{
 const h=harness({gate:()=>false});h.player.play(h.host);h.advance(500);h.player.relayout();assert.equal(h.animations[0].cancelled,true);assert.equal(h.player.getState().index,0);h.advance(2150);assert.equal(h.player.getState().phase,'checking');const count=h.animations.length;h.player.relayout();assert.equal(h.player.getState().phase,'checking');assert.equal(h.animations.length,count);
});
