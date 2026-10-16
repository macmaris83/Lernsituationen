// Usage: PLAYWRIGHT_MODULE=... CHROMIUM_PATH=... node tools/check_task_card_form.mjs PREVIEW_ROOT
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';

const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(process.argv[2]);
const colorsOnly=process.argv.includes('--colors-only');
const mime={'.js':'text/javascript','.css':'text/css','.html':'text/html','.png':'image/png','.svg':'image/svg+xml','.pdf':'application/pdf','.otf':'font/otf'};
const server=http.createServer((request,response)=>{
 const file=path.resolve(root,'.'+decodeURI(request.url.split('?')[0]));
 if(!file.startsWith(root+path.sep)){response.writeHead(403);response.end();return;}
 try{response.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');response.end(fs.readFileSync(file));}
 catch{response.writeHead(404);response.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,headless:true,args:['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']});
const phases=['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren'];
const results=[],errors=[];

async function check(number){
 const lesson='LS'+String(number).padStart(2,'0'),url=base+'/'+lesson+'/';
 const context=await browser.newContext({viewport:{width:1024,height:768},hasTouch:true,reducedMotion:'reduce'});
 const page=await context.newPage();
 page.setDefaultTimeout(10000);
 page.on('pageerror',error=>errors.push(lesson+': '+error.message));
 try{
  await page.goto(url+'lehrkraft.html');
  await page.waitForFunction(()=>window.SOZ_READY);
  const meta=await page.evaluate(()=>{
   const original=SOZ_PROGRESS_META,rebuilt=SOZ_PROGRESS_CORE.metadataFrom(structuredClone(SOZPAED),new DOMParser());
   return {tasks:JSON.stringify(original.tasks)===JSON.stringify(rebuilt.tasks),quiz:original.quizSignature===rebuilt.quizSignature,orientation:original.orientationSignature===rebuilt.orientationSignature,count:Object.keys(original.tasks).length};
  });
  assert.equal(meta.tasks,true,lesson+' task signatures');
  assert.equal(meta.quiz,true);assert.equal(meta.orientation,true);
  await page.locator('#teacher-pin').fill('1234');
  await page.locator('#teacher-unlock').click();
  await page.locator('[data-start-teacher-view]').click();
  await page.waitForURL('**/index.html');
  let checked=0;
  for(const phase of colorsOnly?[]:phases){
   await page.goto(url+phase+'.html');
   await page.waitForFunction(()=>document.body.dataset.taskFocusReady==='true');
   assert.equal(await page.locator('.focus-phase-form').count(),0,lesson+' has legacy phase-form fallback');
   const metadata=await page.evaluate(()=>[...document.querySelectorAll('.assignment-frame')].every(card=>{
    const icon=card.querySelector('.task-summary .assignment-social');
    return icon?.querySelector('svg')&&icon.querySelector('small')?.textContent.trim()&&card.querySelector('.task-original-preview .assignment-time[data-minutes]');
   }));
   assert.equal(metadata,true,lesson+' '+phase+' complete metadata');
   for(let mode=1;mode<=5;mode++){
    // Use the actual authenticated selector, which persists the active path.
    // A temporary setMode(...,false) is reverted by a later settings refresh.
    const selector=page.locator('.teacher-view-bar select');
    if(await selector.inputValue()!==String(mode)){
     await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded'}),selector.selectOption(String(mode))]);
     await page.waitForFunction(()=>document.body.dataset.taskFocusReady==='true');
    }
    const card=page.locator(`[data-mode-panel="${mode}"] .assignment-frame`).first();
    if(number===1&&phase==='informieren'&&mode===1)await card.screenshot({path:'/tmp/lg01-task-form-overview.png'});
    await card.locator('.task-original-preview').click();
    assert.equal(await page.locator('.task-accordion[open]:visible').count(),1);
    assert.equal(await card.locator('.focus-timer').isVisible(),true);
    assert.equal(await card.locator('.focus-countdown').count(),1,'complete master task clock');
    assert.equal(await card.locator('.focus-sound input').isChecked(),true);
    const columns=await card.locator('.focus-task-heading').evaluate(element=>getComputedStyle(element).gridTemplateColumns.split(' ').length);
    assert.equal(columns,2,lesson+' tablet competence/time columns');
    const box=card.locator('.task-accordion[open] [data-task-complete]'),next=card.locator('.focus-next');
    assert.equal(await next.isDisabled(),true);
    await box.check();
    assert.equal(await next.isEnabled(),true);
    assert.equal(await card.locator('.task-accordion').getAttribute('open'),'');
    if(number===1&&phase==='informieren'&&mode===1){
     await card.screenshot({path:'/tmp/lg01-task-form-focus.png'});
     await page.setViewportSize({width:390,height:844});
     assert.equal(await card.locator('.focus-task-heading').evaluate(element=>getComputedStyle(element).gridTemplateColumns.split(' ').length),1);
     assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
     await page.screenshot({path:'/tmp/lg01-task-form-phone.png',fullPage:true});
     await page.setViewportSize({width:1024,height:768});
    }
    await card.locator('.focus-back-actions button').click();
    assert.equal(await card.evaluate(element=>getComputedStyle(element).backgroundColor),'rgb(243, 248, 231)');
    checked++;
   }
  }
  await page.goto(url+'informieren.html');
  await page.waitForFunction(()=>document.body.dataset.taskFocusReady==='true');
  const finalSelector=page.locator('.teacher-view-bar select');
  if(await finalSelector.inputValue()!=='1'){
   await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded'}),finalSelector.selectOption('1')]);
   await page.waitForFunction(()=>document.body.dataset.taskFocusReady==='true');
  }
  let card=page.locator('[data-mode-panel="1"] .assignment-frame').first();
  await card.locator('.task-original-preview').click();
  const completion=card.locator('.task-accordion[open] [data-task-complete]');
  await completion.uncheck();
  assert.equal(await card.evaluate(element=>getComputedStyle(element).borderTopColor),'rgb(0, 155, 217)');
  await completion.check();
  await card.locator('.focus-back-actions button').click();
  assert.equal(await card.evaluate(element=>getComputedStyle(element).backgroundColor),'rgb(243, 248, 231)');
  await page.reload();await page.waitForFunction(()=>document.body.dataset.taskFocusReady==='true');
  card=page.locator('[data-mode-panel="1"] .assignment-frame').first();
  assert.equal(await card.evaluate(element=>getComputedStyle(element).backgroundColor),'rgb(243, 248, 231)');
  await card.locator('.task-original-preview').click();
  assert.equal(await card.locator('.task-accordion[open] [data-task-complete]').isChecked(),true);
  await card.locator('.task-accordion[open] [data-task-complete]').uncheck();
  assert.equal(await card.evaluate(element=>getComputedStyle(element).borderTopColor),'rgb(0, 155, 217)');
  assert.equal(await page.locator('.footer-utils a[href="lehrkraft.html"]').textContent(),'Editor');
  const result={lesson,tasks:meta.count,signaturesPreserved:true,phaseModeFocusChecks:checked,blueOpenGreenCompleted:true,colorSurvivesReload:true};
  results.push(result);console.log('PASS',JSON.stringify(result));
 }finally{await context.close();}
}

try{
 // Two independent packages at a time keep the browser checks responsive.
 const start=Number(process.env.START_LS||1),end=Number(process.env.END_LS||6);
 for(let first=start;first<=end;first+=2){
  await Promise.all([check(first),...(first+1<=end?[check(first+1)]:[])]);
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(path.dirname(root),colorsOnly?'Farben_Pruefung.json':'Browser_Pruefung.json'),JSON.stringify(results.sort((a,b)=>a.lesson.localeCompare(b.lesson)),null,2)+'\n');
}finally{await browser.close();server.close();}
