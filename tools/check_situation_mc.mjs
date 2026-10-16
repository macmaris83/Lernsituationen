/** Verify situation MC via real touch taps, including read-only SCORM review. */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
if(!process.argv[2])throw new Error('Usage: node tools/check_situation_mc.mjs PREVIEW_ROOT');
const root=path.resolve(process.argv[2]);
const first=Number(process.env.START_LS||1),last=Number(process.env.END_LS||6);
const server=http.createServer((req,res)=>{try{const file=path.join(root,decodeURI(req.url.split('?')[0]));res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':file.endsWith('.png')?'image/png':file.endsWith('.jpg')?'image/jpeg':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']});
const results=[];
async function quizFrame(page){const f=page.frames().find(f=>f!==page.mainFrame());await f.waitForFunction(()=>window.SOZ_READY);return f;}
async function tapAnswer(frame,q,value){const panel=frame.locator(`[data-quiz-question="${q.id}"]`);const details=panel.locator('..');if(await details.getAttribute('open')===null)await details.locator('summary').tap();const option=panel.locator(`.quiz-answer:has(input[value="${value}"])`);await option.locator('span').tap();assert.equal(await option.locator('input').isChecked(),true,`${q.id}: touch on answer text must select radio`);await panel.locator('[data-quiz-submit]').tap();return panel;}
try{
 for(let n=first;n<=last;n++)for(const mode of ['none','normal','browse','review']){
  const context=await browser.newContext({viewport:{width:1024,height:768},hasTouch:true,isMobile:true});
  if(mode!=='none')await context.addInitScript(mode=>{if(top!==self)return;const key='mc-test-store:'+location.pathname;let saved={};try{saved=JSON.parse(sessionStorage.getItem(key)||'{}');}catch{};window.LMS_STORE={'cmi.core.lesson_mode':mode==='review'?'normal':mode,'cmi.core.student_id':'mc-test','cmi.core.lesson_status':'not attempted',...saved};window.LMS_WRITES=[];window.API={LMSInitialize:()=> 'true',LMSGetValue:k=>LMS_STORE[k]||'',LMSGetLastError:()=> '0',LMSSetValue:(k,v)=>{LMS_WRITES.push([k,v]);LMS_STORE[k]=v;sessionStorage.setItem(key,JSON.stringify(LMS_STORE));return 'true';},LMSCommit:()=> 'true',LMSFinish:()=> 'true'};},mode);
  const page=await context.newPage();await page.goto(`${base}/LS${String(n).padStart(2,'0')}/scorm.html`);let frame=await quizFrame(page);
  await frame.locator('[data-orientation-complete]').check();await frame.locator('a[data-learning-page="handlungssituation.html"]').first().tap();await frame.waitForFunction(()=>document.querySelector('[data-situation-quiz]')?.dataset.quizReady==='true');
  const questions=await frame.evaluate(()=>JSON.parse(document.querySelector('[data-situation-quiz] script').textContent));assert.equal(questions.length,5);
  let reviewSnapshot;
  if(mode==='review'){
   await tapAnswer(frame,questions[0],questions[0].correct);
   await page.evaluate(()=>{LMS_STORE['cmi.core.lesson_mode']='review';sessionStorage.setItem('mc-test-store:'+location.pathname,JSON.stringify(LMS_STORE));});
   await page.reload();frame=await quizFrame(page);await frame.waitForFunction(()=>document.querySelector('[data-situation-quiz]')?.dataset.quizReady==='true');
   assert.equal(await frame.evaluate(()=>SOZ_PROGRESS.readOnly),true);assert.equal(await frame.locator('[data-quiz-practice-note]').count(),1);
   reviewSnapshot=await page.evaluate(()=>JSON.stringify(LMS_STORE));
  }
  const wrong=questions[0].options.find(o=>o.value!==questions[0].correct).value;
  const wrongPanel=await tapAnswer(frame,questions[0],wrong);assert.equal(await wrongPanel.locator('[data-quiz-feedback]').getAttribute('data-result'),'wrong');
  for(const q of questions){const panel=await tapAnswer(frame,q,q.correct);assert.equal(await panel.locator('[data-quiz-feedback]').getAttribute('data-result'),'correct');}
  assert.match(await frame.locator('[data-quiz-progress]').textContent(),/Alle 5/);
  if(mode==='review'){
   assert.equal(await page.evaluate(()=>JSON.stringify(LMS_STORE)),reviewSnapshot);assert.equal(await page.evaluate(()=>LMS_WRITES.length),0);assert.equal(await frame.evaluate(()=>SOZ_PROGRESS.read().q.q2),undefined);
   await page.reload();frame=await quizFrame(page);assert.match(await frame.locator('[data-quiz-progress]').textContent(),/1 von 5/);
   // Enter the authenticated teacher preview, then restore the learner record.
   await frame.locator('.footer-utils a[href="lehrkraft.html"]').tap();await frame.locator('#teacher-pin').fill('1234');await frame.locator('#teacher-unlock').tap();await frame.locator('[data-start-teacher-view]').tap();await frame.waitForFunction(()=>document.body.classList.contains('teacher-view-active'));
   await frame.locator('a[data-learning-page="handlungssituation.html"]').first().tap();await frame.waitForFunction(()=>document.querySelector('[data-situation-quiz]')?.dataset.quizReady==='true');
   await tapAnswer(frame,questions[1],questions[1].correct);assert.equal(await frame.evaluate(()=>SOZ_PROGRESS.read().q.q2[0]),questions[1].correct);assert.equal(await page.evaluate(()=>JSON.stringify(LMS_STORE)),reviewSnapshot);
   await frame.locator('[data-exit-teacher-view]').tap();await frame.waitForFunction(()=>window.SOZ_READY&&!document.body.classList.contains('teacher-view-active'));assert.equal(await frame.evaluate(()=>SOZ_PROGRESS.read().q.q2),undefined);assert.equal(await frame.locator('[data-quiz-practice-note]').count(),1);assert.equal(await page.evaluate(()=>JSON.stringify(LMS_STORE)),reviewSnapshot);
  }else{
   assert.equal(await frame.evaluate(()=>SOZ_PROGRESS_CORE.quizComplete(SOZ_PROGRESS.read(),SOZ_PROGRESS_META)),true);
   await page.reload();frame=await quizFrame(page);await frame.waitForFunction(()=>document.querySelector('[data-situation-quiz]')?.dataset.quizReady==='true');assert.match(await frame.locator('[data-quiz-progress]').textContent(),/Alle 5/);
  }
  results.push({lesson:n,mode,touchSelection:true,feedback:true,restored:true,reviewWrites:mode==='review'?0:undefined});console.log(`LS${n} ${mode}: PASS`);await context.close();
 }
 console.log(JSON.stringify({passed:true,cases:results.length,results},null,2));
}finally{await browser.close();server.close();}
