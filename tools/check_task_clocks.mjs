// Usage: node tools/check_task_clocks.mjs PREVIEW_ROOT
// Optional: PLAYWRIGHT_MODULE, CHROMIUM_PATH, START_LS, END_LS.
// Timer states are seeded through the app's existing session-storage format.
// Audio assertions wrap the native Web Audio nodes; they do not simulate sound.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

if (!process.argv[2]) throw new Error('Usage: node tools/check_task_clocks.mjs PREVIEW_ROOT');
const root=path.resolve(process.argv[2]);
assert.ok(fs.existsSync(root), 'Build the preview before checking its task clocks: '+root);
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const mime={'.js':'text/javascript','.css':'text/css','.html':'text/html','.png':'image/png','.svg':'image/svg+xml','.pdf':'application/pdf','.otf':'font/otf'};
const server=http.createServer((request,response)=>{
 const file=path.resolve(root,'.'+decodeURI(request.url.split('?')[0]));
 if (!file.startsWith(root+path.sep)) {response.writeHead(403);response.end();return;}
 try {response.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');response.end(fs.readFileSync(file));}
 catch {response.writeHead(404);response.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port;
let browser;
const results=[],errors=[];

function observeNativeAudio() {
 const Native=window.AudioContext||window.webkitAudioContext;
 window.__clockAudio={nativeAvailable:!!Native,constructed:[],starts:[],gains:[]};
 window.__clockAudioContexts=[];
 if (!Native) return;
 const trace=window.__clockAudio;
 function AuditedAudioContext(...args) {
  const context=new Native(...args);
  window.__clockAudioContexts.push(context);
  trace.constructed.push({native:context instanceof Native,initialState:context.state});
  const createOscillator=context.createOscillator.bind(context);
  context.createOscillator=()=>{
   const oscillator=createOscillator();
   const start=oscillator.start.bind(oscillator);
   oscillator.start=(...args)=>{
    const result=start(...args);
    trace.starts.push({when:args[0]??0,currentTime:context.currentTime,state:context.state,frequency:oscillator.frequency.value});
    return result;
   };
   return oscillator;
  };
  const createGain=context.createGain.bind(context);
  context.createGain=()=>{
   const gain=createGain();
   for (const name of ['setValueAtTime','linearRampToValueAtTime','exponentialRampToValueAtTime']) {
    const original=gain.gain[name].bind(gain.gain);
    gain.gain[name]=(...args)=>{
     const result=original(...args);
     trace.gains.push({method:name,value:args[0],when:args[1],state:context.state});
     return result;
    };
   }
   return gain;
  };
  return context;
 }
 Object.setPrototypeOf(AuditedAudioContext,Native);
 AuditedAudioContext.prototype=Native.prototype;
 if (window.AudioContext) window.AudioContext=AuditedAudioContext;
 if (window.webkitAudioContext) window.webkitAudioContext=AuditedAudioContext;
}

async function ready(page) {
 await page.waitForFunction(()=>window.SOZ_READY&&document.body.dataset.taskFocusReady==='true');
}

function firstCard(page,mode) {
 return page.locator(`[data-mode-panel="${mode}"] .assignment-frame`).first();
}

async function closeFocus(page) {
 const back=page.locator('.task-accordion[open] .focus-back-actions button');
 if (await back.count()) await back.click();
}

async function seedAndOpen(page,mode,remaining) {
 await closeFocus(page);
 const seeded=await firstCard(page,mode).evaluate((card,remaining)=>{
  const ui=card.querySelector('.assignment-time[data-minutes]:not([data-phase-budget])');
  if (!ui) throw new Error('An individual task duration is missing.');
  const total=Math.round(Number(ui.dataset.minutes)*60);
  const key=(window.SOZ_TEACHER_VIEW?.active?'teacher:':'')+'task-focus-clock:'+SOZPAED.id+':'+location.pathname.replace(/[^/]+$/,'')+':'+card.dataset.taskId;
  const value=remaining==='full'?total:remaining==='half'?total/2:remaining;
  if (!Number.isInteger(value)||value<0||value>total) throw new Error('Invalid clock test state.');
  sessionStorage.setItem(key,JSON.stringify({total,remaining:value}));
  return {key,total,remaining:value,taskId:card.dataset.taskId};
 },remaining);
 assert.ok(seeded.key.startsWith('teacher:task-focus-clock:'),'Teacher clocks must be separate from learner clocks.');
 await page.reload();
 await ready(page);
 const card=firstCard(page,mode);
 await card.locator('.task-original-preview').click();
 assert.equal(await card.locator('.task-accordion[open]').count(),1);
 assert.equal(await card.locator('.focus-clock svg').isVisible(),true);
 assert.equal(await card.locator('.focus-countdown').isVisible(),true);
 assert.equal(await card.locator('.focus-sound input').isVisible(),true);
 assert.equal(await card.locator('.focus-sound input').isChecked(),true);
 return {card,...seeded};
}

const color=card=>card.locator('.focus-countdown').evaluate(element=>getComputedStyle(element).color);
const seconds=async card=>{
 const [minutes,value]=(await card.locator('.focus-countdown').innerText()).split(':').map(Number);
 return minutes*60+value;
};

async function checkMode(page,lesson,mode) {
 const choose=page.locator('.teacher-view-bar select');
 if (await choose.inputValue()!==String(mode)) {
  await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded'}),choose.selectOption(String(mode))]);
  await ready(page);
 }
 let state=await seedAndOpen(page,mode,'full');
 let card=state.card;
 assert.equal(await color(card),'rgb(175, 202, 11)',lesson+' W'+mode+' starts green');
 const pause=card.locator('.focus-timer-row > button');
 assert.equal(await pause.innerText(),'Pause');
 await pause.click();
 assert.equal(await pause.innerText(),'Fortsetzen');
 const paused=await seconds(card);
 if (mode!==1) {
  assert.equal(await card.locator('.focus-sound input').isChecked(),true);
  await card.locator('.focus-sound input').uncheck();
  assert.equal(await card.locator('.focus-sound input').isChecked(),false);
  await card.locator('.focus-sound input').check();
  await pause.click();
  assert.equal(await pause.innerText(),'Pause');
  await closeFocus(page);
  console.log('PASS',lesson,'W'+mode,'clock, work-form duration, pause/resume and gong controls');
  return {mode,minutes:state.total/60,clockControls:true,pauseResumeControls:true,gongToggle:true};
 }
 await page.waitForTimeout(1150);
 assert.equal(await seconds(card),paused,'Paused clocks must stop.');
 const saved=await page.evaluate(key=>JSON.parse(sessionStorage.getItem(key)),state.key);
 assert.equal(saved.remaining,paused);
 await page.reload();
 await ready(page);
 card=firstCard(page,mode);
 await card.locator('.task-original-preview').click();
 assert.equal(await seconds(card),paused,'Reload must retain remaining time.');
 const resumedButton=card.locator('.focus-timer-row > button');
 await resumedButton.click();
 assert.equal(await resumedButton.innerText(),'Fortsetzen');
 await resumedButton.click();
 assert.equal(await resumedButton.innerText(),'Pause');
 await page.waitForFunction(({mode,paused})=>{
  const time=document.querySelector(`[data-mode-panel="${mode}"] .assignment-frame .focus-countdown`).textContent;
  const [minutes,seconds]=time.split(':').map(Number);
  return minutes*60+seconds<paused;
 },{mode,paused});
 await resumedButton.click();

 state=await seedAndOpen(page,mode,'half');
 card=state.card;
 await card.locator('.focus-timer-row > button').click();
 assert.equal(await color(card),'rgb(17, 17, 17)',lesson+' W'+mode+' midpoint is black');

 state=await seedAndOpen(page,mode,1);
 card=state.card;
 // The deliberately one-second timer hides Pause during Playwright's normal
 // stability wait. Use a real click without that wait to toggle before expiry.
 await card.locator('.focus-sound input').uncheck({force:true});
 await card.locator('.focus-alarm').waitFor({state:'visible'});
 assert.equal(await seconds(card),0);
 assert.equal(await color(card),'rgb(180, 35, 24)',lesson+' W'+mode+' expires red');
 assert.equal(await card.locator('.focus-timer-row > button').isVisible(),false,'No Fortsetzen button after expiry.');
 assert.match(await card.locator('.focus-timer-note').innerText(),/weiterarbeiten/i);
 const quiet=await page.evaluate(()=>window.__clockAudio);
 assert.equal(quiet.starts.length,0,'Disabled gong must not start an oscillator.');
 const completion=card.locator('.task-accordion[open] [data-task-complete]');
 await completion.check();
 assert.equal(await card.locator('.focus-next').isEnabled(),true,'Expired time must allow completion and manual progression.');
 assert.equal(await card.getAttribute('data-task-id'),state.taskId);
 assert.equal(await card.locator('.task-accordion[open]').count(),1,'Expiry/checking must not navigate automatically.');

 state=await seedAndOpen(page,mode,1);
 card=state.card;
 await page.waitForFunction(()=>window.__clockAudioContexts.some(context=>context.state==='running'));
 await card.locator('.focus-alarm').waitFor({state:'visible'});
 await page.waitForFunction(()=>window.__clockAudio.starts.length>=6);
 const audible=await page.evaluate(()=>({
  ...window.__clockAudio,
  states:window.__clockAudioContexts.map(context=>context.state),
 }));
 assert.equal(audible.nativeAvailable,true);
 assert.ok(audible.constructed.length>0&&audible.constructed.every(context=>context.native));
 assert.equal(audible.starts.length,6,'The native gong schedules three pulses with two tones each.');
 assert.ok(audible.starts.every(start=>start.state==='running'));
 assert.ok(audible.gains.filter(gain=>gain.method==='linearRampToValueAtTime'&&gain.value>0).length>=6,
  'The native audio graph must schedule positive gains, not only silent oscillators.');
 await closeFocus(page);
 console.log('PASS',lesson,'W'+mode,'clock, pause/resume, reload, green/black/red, quiet and native audible gong, expiry permits work');
 return {mode,minutes:state.total/60,pauseResume:true,reloadRemaining:true,greenBlackRed:true,
  silentGongNoOscillators:true,nativeGongStarts:audible.starts.length,positiveGainRamp:true,expiryAllowsWork:true};
}

async function checkLesson(number) {
 const lesson='LS'+String(number).padStart(2,'0'),url=base+'/'+lesson+'/';
 const context=await browser.newContext({viewport:{width:1024,height:768},hasTouch:true,reducedMotion:'reduce'});
 await context.addInitScript(observeNativeAudio);
 const page=await context.newPage();
 page.setDefaultTimeout(10000);
 page.on('pageerror',error=>errors.push(lesson+': '+error.message));
 try {
  await page.goto(url+'lehrkraft.html');
  await page.waitForFunction(()=>window.SOZ_READY);
  const metadata=await page.evaluate(()=>{
   let cards=0,timed=0,invalid=0;
   for (const phase of SOZ_PROGRESS_CORE.phases) {
    const document=new DOMParser().parseFromString(SOZPAED.pages[phase+'.html'],'text/html');
    for (const card of document.querySelectorAll('.assignment-frame')) {
     cards++;
     const times=card.querySelectorAll('.assignment-time[data-minutes]:not([data-phase-budget])');
     const value=Number(times[0]?.dataset.minutes);
     if (times.length===1&&value>0&&Number.isInteger(value*2)) timed++;
     else invalid++;
    }
   }
   return {cards,timed,invalid};
  });
  assert.ok(metadata.cards>0);
  assert.equal(metadata.invalid,0,lesson+' every task needs one positive half-minute duration.');
  assert.equal(metadata.timed,metadata.cards);
  assert.equal(await page.locator('[data-start-teacher-view]').isVisible(),false);
  await page.locator('#teacher-pin').fill('1234');
  await page.locator('#teacher-unlock').click();
  await page.locator('[data-start-teacher-view]').click();
  await page.waitForURL('**/index.html');
  await page.goto(url+'informieren.html');
  await ready(page);
  assert.equal(await page.locator('.teacher-view-bar').isVisible(),true);
  const modes=[];
  for (let mode=1;mode<=5;mode++) modes.push(await checkMode(page,lesson,mode));
  results.push({lesson,tasks:metadata.cards,taskTimesPresent:true,teacherLogin:true,modes});
 } catch (error) {
  await page.screenshot({path:'/tmp/task-clock-failure-'+lesson+'.png',fullPage:true}).catch(()=>{});
  console.error('CLOCK FAILURE',lesson,await page.evaluate(()=>({
   mode:document.body.dataset.mode,
   open:[...document.querySelectorAll('.task-accordion[open]')].map(details=>({
    task:details.closest('.assignment-frame')?.dataset.taskId,
    timer:details.querySelector('.focus-countdown')?.textContent,
    checked:details.querySelector('.focus-sound input')?.checked,
   })),audio:window.__clockAudio,
  })).catch(()=>null));
  throw error;
 } finally {await context.close();}
}

try {
 browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/tmp/biocasa-browser/chromium',headless:true,
  args:['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']});
 const first=Number(process.env.START_LS||1),last=Number(process.env.END_LS||6);
 // One context at a time leaves room for the independent layout/learner checks.
 for (let lesson=first;lesson<=last;lesson++) await checkLesson(lesson);
 assert.deepEqual(errors,[]);
 const report=path.join(path.dirname(root),'Uhren_Pruefung.json');
 fs.writeFileSync(report,JSON.stringify(results.sort((a,b)=>a.lesson.localeCompare(b.lesson)),null,2)+'\n');
 console.log('PASS',results.length,'packages; report',report);
} finally {await browser?.close();server.close();}
