/* Integration test for the repository's static SCORM applications. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const packages=JSON.parse(fs.readFileSync(path.join(root,'master-katalog.json'))).packages.filter(p=>p.typ==='Lernsituation'||['VORLAGE-TRADIERT','VORLAGE-FUENF-LERNWEGE'].includes(p.id));
const server=http.createServer((req,res)=>{
 const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));
 if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404).end();return;}
 res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.pdf':'application/pdf'})[path.extname(file)]||'application/octet-stream');
 fs.createReadStream(file).pipe(res);
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const output=path.join(root,'test-results/form185');fs.mkdirSync(output,{recursive:true});
 try{
  for(const item of packages){
   const context=await browser.newContext({viewport:{width:1024,height:768}}),page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   const base='http://127.0.0.1:'+server.address().port+'/'+item.master+'/';
   await page.route('**/*',route=>route.request().url().startsWith('http://127.0.0.1:')?route.continue():route.abort());
   await page.goto(base+'index.html');
   await page.waitForFunction(()=>window.SOZ_READY===true);
   assert.equal(await page.locator('[data-share-workbook]').count(),0,item.id+': no orientation workbook');
   assert.equal(await page.locator('.lesson-content .material-access').count(),0,item.id+': no orientation materials');
   assert.equal(await page.locator('[data-package-version]').first().innerText(),'Version '+item.version,item.id);
   if(await page.locator('[data-video-skip]').count()){await page.locator('[data-video-skip]').click();await page.goto(base+'index.html');await page.waitForFunction(()=>window.SOZ_READY===true);}
   await page.locator('[data-orientation-complete]').check();
   await page.reload();await page.waitForFunction(()=>window.SOZ_READY===true);
   assert.equal(await page.locator('[data-orientation-complete]').isChecked(),true,item.id+': orientation saved');
   for(const width of [390,1024]){
    await page.setViewportSize({width,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,item.id+': orientation overflow '+width);
   }
   // Seed outside the video page: its pagehide handler saves its real player state.
   await page.goto(base+'handlungssituation.html');await page.waitForFunction(()=>window.SOZ_READY===true);
   // Seed an ordinary test learner with all prerequisites, leaving one task open.
   await page.evaluate(()=>{
    const K=SOZ_PROGRESS_CORE,M=SOZ_PROGRESS_META,p=K.initial(M,1);p.o=true;
    for(const id of Object.keys(M.tasks))K.setTask(p,M,id,true);
    for(const q of M.quiz){p.q[q.id]=[q.correct,true];p.qf||={};p.qf[q.id]=true;}
    if(M.orientationVideo)p.ov={signature:M.orientationVideo.signature,duration:100,ranges:[[0,100]],answers:Object.fromEntries(M.orientationVideo.questions.map(q=>[q.id,q.correct])),attempts:{},ended:true,complete:true};
    if(M.flashcard)p.fc={schema:1,version:3,id:M.id,signature:M.flashcard.signature,complete:true,started:true,known:M.flashcard.terms,total:M.flashcard.terms,pending:0,data:{state:{results:Array.from({length:M.flashcard.terms},()=>({latest:{correct:true}}))}}};
    const first=Object.keys(M.tasks).find(id=>M.tasks[id].phase==='informieren'&&M.tasks[id].mode===1);delete p.t[first];
    if(!SOZ_PROGRESS.write(p))throw Error('Test progress not saved');
   });
   await page.goto(base+'informieren.html');await page.waitForFunction(()=>window.SOZ_READY===true);
   const task=page.locator('[data-mode-panel="1"] .assignment-frame').first();
   await task.locator('.task-original-preview').click();
   assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('task-focus')),true,item.id+': focus');
   assert.equal(await page.locator('[data-phase-points]').isVisible(),true,item.id+': XP in focus');
   if(item.id!=='VORLAGE-TRADIERT')assert.equal(await page.locator('.task-focus-panel .assignment-kind:visible').count(),0,item.id+': no theory/practice');
   // Material menu opens on the same page and returns to the exact task.
   const materials=page.locator('.lesson-content details.material-access');
   if(await materials.count()){
    if(!await materials.getAttribute('open'))await materials.locator('summary').click();
    const link=materials.locator('a.material-link').first();
    if(await link.count()){
     await link.click();await page.waitForFunction(()=>window.SOZ_READY===true);
     const back=page.locator('.return-task');
     assert.equal(await back.count(),1,item.id+': material return');
     await back.click();await page.waitForFunction(()=>window.SOZ_READY===true);
     assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('task-focus')),true,item.id+': returned focus');
    }
   }
   await page.locator('.task-focus-panel [data-task-complete]').check();
   assert.equal(await page.locator('.focus-next:visible').isEnabled(),true,item.id+': manual next');
   await page.goto(base+'reflektieren.html');await page.waitForFunction(()=>window.SOZ_READY===true);
   const complete=page.locator('[data-complete-package]');
   assert.equal(await complete.isEnabled(),true,item.id+': complete enabled '+JSON.stringify(await page.evaluate(()=>({grade:SOZ_PROGRESS_CORE.grading(SOZ_PROGRESS.read(),SOZ_PROGRESS_META),video:SOZ_PROGRESS.read().ov,flashcard:SOZ_PROGRESS.read().fc?.complete}))));
   await complete.click();
   assert.equal(await complete.innerText(),'Lernpaket abgeschlossen',item.id+': explicit completion');
   await page.reload();await page.waitForFunction(()=>window.SOZ_READY===true);
   assert.equal(await complete.innerText(),'Lernpaket abgeschlossen',item.id+': completion restored');
   const learnerBefore=await page.evaluate(()=>JSON.stringify(SOZ_PROGRESS.read()));
   await page.evaluate(()=>{const key='soz-teacher-view:'+SOZPAED.id+':'+location.pathname.replace(/[^/]+$/,'')+':'+(SOZ_CONFIG.packageRevision||'base');sessionStorage.setItem(key,JSON.stringify({active:true,mode:1}));});
   await page.goto(base+'informieren.html');await page.waitForFunction(()=>window.SOZ_READY===true);
   assert.equal(await page.evaluate(()=>SOZ_TEACHER_VIEW.active),true,item.id+': teacher test mode');
   assert.equal(await page.evaluate(()=>SOZ_PROGRESS.completed),false,item.id+': own incomplete teacher test');
   await page.locator('[data-mode-panel="1"] .assignment-frame').first().locator('.task-original-preview').click();
   await page.locator('.task-focus-panel [data-task-complete]').check();
   await page.locator('[data-exit-teacher-view]').click();await page.waitForFunction(()=>window.SOZ_READY===true);
   assert.equal(await page.evaluate(()=>JSON.stringify(SOZ_PROGRESS.read())),learnerBefore,item.id+': learner state untouched by teacher test');
   assert.deepEqual(errors,[],item.id+': browser errors');
   if(['BRC-LG01-LS01','BRC-LG05-LS04','VORLAGE-TRADIERT','GESCHICHTE-J1914-Deutsches_Reich'].includes(item.id))await page.screenshot({path:path.join(output,item.id+'.png'),fullPage:true});
   console.log('PASS browser',item.id);
   await context.close();
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;server.close();});
