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
   if(['BRC-LG01-LS04','BRC-LG01-LS05'].includes(item.id)){
    const titleCard=page.locator('.lesson-content>.card.hero');
    assert.equal(await titleCard.count(),1,item.id+': framed lesson heading');
    assert.equal(await titleCard.locator('h1').innerText(),item.title);
    assert.ok(await titleCard.evaluate(e=>parseFloat(getComputedStyle(e).borderTopWidth)>0),item.id+': visible heading border');
   }
   if(item.id==='BRC-LG01-LS05'){
    const orientation=await page.evaluate(()=>{
     const actual=SOZ_PROGRESS_CORE.metadataFrom(JSON.parse(JSON.stringify(SOZPAED)),new DOMParser());
     return {actual:actual.orientationSignature,expected:SOZ_PROGRESS_META.orientationSignature};
    });
    assert.equal(orientation.actual,orientation.expected,item.id+': framed orientation and metadata agree');
   }
   if(item.id==='BRC-LG01-LS04'){
    const audit=await page.evaluate(()=>{
     const d=JSON.parse(JSON.stringify(SOZPAED));
     const actual=SOZ_PROGRESS_CORE.metadataFrom(d,new DOMParser());
     const paths=SOZ_API.availableModes().map(mode=>{
      let numbers=[],minutes=0;
      for(const phase of SOZ_PROGRESS_CORE.phases){
       const doc=new DOMParser().parseFromString(SOZPAED.pages[phase+'.html'],'text/html');
       const cards=[...doc.querySelectorAll(`[data-mode-panel="${mode}"] .assignment-frame`)];
       numbers.push(...cards.map(c=>Number(c.dataset.taskNumber)));
       minutes+=cards.reduce((s,c)=>s+Number(c.querySelector('[data-minutes]').dataset.minutes),0);
      }
      return {mode,numbers,minutes};
     });
     return {title:SOZPAED.title,actual,expected:SOZ_PROGRESS_META,paths};
    });
    assert.equal(audit.title,'Bei Business-Angels pitchen');
    for(const field of ['tasks','quiz','quizSignature','orientationSignature'])assert.deepEqual(audit.actual[field],audit.expected[field],item.id+': current content metadata '+field);
    for(const p of audit.paths){assert.deepEqual(p.numbers,[1,2,3,4,5,6,7,8,9]);assert.equal(p.minutes,270);}
   }
   if(item.id!=='VORLAGE-FUENF-LERNWEGE'){
    // Stored editor preferences and stale links must not reintroduce another path.
    const single=await page.evaluate(()=>{
     const s=SOZ_API.getSettings();s.learningPaths={1:{label:'Tradiert'},5:{label:'Alt'}};s.allowStudentMode=true;
     SOZ_API.setMode(5,false);
     return {mode:SOZ_API.getSettings().mode,modes:SOZ_API.availableModes(),choice:SOZ_API.getSettings().allowStudentMode};
    });
    assert.deepEqual(single,{mode:1,modes:[1],choice:false},item.id+': only the traditional path');
    const inventory=await page.evaluate(()=>({
      modes:[...new Set(Object.values(SOZ_PROGRESS_META.tasks).map(t=>t.mode))],
      phases:SOZ_PROGRESS_CORE.phases.map(phase=>{
        const doc=new DOMParser().parseFromString(SOZPAED.pages[phase+'.html'],'text/html');
        return {phase,panels:[...doc.querySelectorAll('[data-mode-panel]')].map(e=>e.dataset.modePanel),numbers:[...doc.querySelectorAll('.assignment-frame')].map(e=>Number(e.dataset.taskNumber))};
      })
    }));
    assert.deepEqual(inventory.modes,[1],item.id+': W1 metadata only');
    for(const phase of inventory.phases)assert.deepEqual([...new Set(phase.panels)],['1'],item.id+': removed path panels '+phase.phase);
    for(const phase of inventory.phases)assert.ok(phase.numbers.length>=1&&phase.numbers.length<=4,item.id+': one to four assignments in '+phase.phase);
    const numbers=inventory.phases.flatMap(phase=>phase.numbers);
    assert.deepEqual(numbers,numbers.map((_,i)=>i+1),item.id+': continuous task numbering across all phases');
   }
   const emptyXP=await page.evaluate(()=>{
    const grade=SOZ_PROGRESS_CORE.grading(SOZ_PROGRESS.read(),SOZ_PROGRESS_META);
    const battery=document.querySelector('[data-phase-points] .points-battery');
    return {points:grade.points,max:grade.maxPoints,ariaMax:battery?.getAttribute('aria-valuemax'),label:battery?.querySelector('.points-battery-label')?.textContent};
   });
   assert.deepEqual(emptyXP,{points:0,max:100,ariaMax:'100',label:'0 / 100 XP'},item.id+': consistent empty 100-XP battery');
   assert.equal(await page.locator('[data-share-workbook]').count(),0,item.id+': no orientation workbook');
   assert.equal(await page.locator('.lesson-content .material-access').count(),0,item.id+': no orientation materials');
   assert.equal(await page.locator('[data-package-version]').first().innerText(),'Version '+item.version,item.id);
   assert.equal(await page.evaluate(()=>SOZ_CONFIG.formVersion),'1.8.8',item.id+': common form');
   assert.equal(await page.locator('.page-footer [data-phase-points],.b-footer [data-phase-points]').count(),0,item.id+': compact XP above the lesson');
   assert.equal(await page.locator('[data-package-score-summary],[data-package-score-label]').count(),0,item.id+': no duplicate XP summary');
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
   assert.equal(await page.locator('.lesson-content [data-mode-panel]>.phase-meta:visible').count(),0,item.id+': redundant phase time and work-form block is hidden');
   const phaseWorkbook=page.locator('.lesson-content .phase-workbook-import:visible,.main>.tools-bar:visible').filter({has:page.locator('[data-share-workbook]')});
   assert.equal(await phaseWorkbook.count(),1,item.id+': current phase workbook import remains visible');
   assert.equal(await phaseWorkbook.locator('[data-share-workbook]').isVisible(),true,item.id+': phase workbook import button remains available');
   if(item.id==='BRC-LG01-LS05'){
    // Regression for the reported bundled task: both views need the same three
    // readable instruction blocks, including the separate interim submission.
    const bundled=page.locator('[data-mode-panel="1"] .assignment-frame[data-task-number="4"]');
    assert.equal(await bundled.count(),1,item.id+': reported task 4 exists');
    const original=await bundled.evaluate(card=>{
     const source=new DOMParser().parseFromString(SOZPAED.pages['informieren.html'],'text/html');
     const task=[...source.querySelectorAll('[data-mode-panel="1"] .assignment-frame')].find(e=>e.dataset.taskId===card.dataset.taskId);
     if(!task)throw Error('Original bundled task is missing');
     const text=[...task.querySelectorAll('.assignment-body p')].map(p=>p.textContent).join(' ').replace(/\s+/g,' ').trim();
     return {id:card.dataset.taskId,signature:card.dataset.taskSignature,text};
    });
    const assertInstructionSpacing=async(selector,label)=>{
     const actual=await bundled.locator(selector).evaluate(copy=>{
      const paragraphs=[...copy.querySelectorAll('p')].filter(p=>p.textContent.trim());
      const boxes=paragraphs.map(p=>p.getBoundingClientRect());
      return {text:paragraphs.map(p=>p.textContent).join(' ').replace(/\s+/g,' ').trim(),
       paragraphs:paragraphs.map(p=>p.textContent.trim()),
       gaps:boxes.slice(1).map((rect,i)=>rect.top-boxes[i].bottom)};
     });
     assert.equal(actual.paragraphs.length,3,item.id+': three instruction paragraphs '+label);
     for(const [index,start] of ['Analysieren','Arbeiten','Zwischensicherung'].entries())assert.ok(actual.paragraphs[index].startsWith(start),item.id+': paragraph '+(index+1)+' starts with '+start+' '+label);
     assert.match(actual.paragraphs[1],/^Arbeiten Sie die Schritte heraus,/,item.id+': separable operator remains together '+label);
     assert.equal(actual.text,original.text,item.id+': complete original instruction text '+label);
     for(const gap of actual.gaps)assert.ok(gap>=12,item.id+': visible paragraph spacing '+label+' ('+gap+'px)');
     assert.equal(await bundled.getAttribute('data-task-id'),original.id,item.id+': unchanged task ID '+label);
     assert.equal(await bundled.getAttribute('data-task-signature'),original.signature,item.id+': unchanged task signature '+label);
    };
    for(const width of [390,1024]){
     await page.setViewportSize({width,height:844});
     await assertInstructionSpacing('.task-original-preview','overview '+width);
     await page.screenshot({path:path.join(output,item.id+'-task4-overview-'+width+'.png'),fullPage:true,animations:'disabled'});
     await bundled.locator('.task-original-preview').click();
     await page.waitForFunction(()=>document.body.classList.contains('task-focus'));
     await page.evaluate(()=>Promise.all(document.getAnimations().filter(a=>a.effect?.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{}))));
     await assertInstructionSpacing('.task-focus-panel .assignment-body','focus '+width);
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,item.id+': reported task focus overflow '+width);
     await page.screenshot({path:path.join(output,item.id+'-task4-focus-'+width+'.png'),fullPage:true,animations:'disabled'});
     await bundled.locator('.focus-back-actions button').click();
     await page.waitForFunction(()=>!document.body.classList.contains('task-focus'));
     await assertInstructionSpacing('.task-original-preview','returned overview '+width);
    }
   }
   const task=page.locator('[data-mode-panel="1"] .assignment-frame').first();
   await task.locator('.task-original-preview').click();
   assert.equal(await page.locator('body').evaluate(e=>e.classList.contains('task-focus')),true,item.id+': focus');
   const clock=task.locator('.task-focus-panel .focus-countdown');
   const hasTaskTime=await page.evaluate(id=>{
    const markup=SOZ_API.getSettings().overrides?.[document.body.dataset.page]||SOZPAED.pages[document.body.dataset.page];
    const source=new DOMParser().parseFromString(markup,'text/html');
    const original=[...source.querySelectorAll('.assignment-frame')].find(e=>e.dataset.taskId===id);
    if(!original)throw Error('Original task missing: '+id);
    return /(\d+(?:[.,]\d+)?)\s*Min/i.test(original.querySelector('.assignment-time')?.textContent||'');
   },await task.getAttribute('data-task-id'));
   assert.equal(await clock.count(),hasTaskTime?1:0,item.id+': clock uses original task time only');
   if(hasTaskTime){
   assert.equal(await clock.getAttribute('role'),'timer',item.id+': accessible clock');
   assert.equal(await task.locator('.task-focus-panel [aria-label="Signalton bei Zeitablauf"]').count(),1,item.id+': gong control');
   const startedClock=await clock.innerText();
   await page.waitForFunction(previous=>document.querySelector('.task-accordion[open] .focus-countdown')?.textContent!==previous,startedClock);
   await task.locator('.task-focus-panel .focus-timer-row button').click();
   assert.equal(await task.locator('.task-focus-panel .focus-timer-row button').innerText(),'Fortsetzen',item.id+': paused clock');
   const pausedClock=await clock.innerText();
   await task.locator('.focus-back-actions button').click();
   await task.locator('.task-original-preview').click();
   const asSeconds=value=>value.split(':').map(Number).reduce((minutes,seconds)=>minutes*60+seconds);
   const reopenedClock=asSeconds(await clock.innerText()),pausedSeconds=asSeconds(pausedClock);
   assert.ok(reopenedClock<=pausedSeconds&&reopenedClock>=pausedSeconds-2,item.id+': retained clock in same task');
   }
   assert.equal(await page.locator('[data-phase-points]').isVisible(),true,item.id+': XP in focus');
   assert.equal(await page.locator('.task-focus-panel>[data-phase-points]').count(),1,item.id+': common XP placement');
   for(const width of [390,1024]){
    await page.setViewportSize({width,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,item.id+': task focus overflow '+width);
   }
   if(['BRC-LG01-LS01','VORLAGE-TRADIERT','GESCHICHTE-IDN'].includes(item.id)){
    await page.evaluate(()=>Promise.all(document.getAnimations().filter(a=>a.effect?.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{}))));
    await page.screenshot({path:path.join(output,item.id+'-focus.png'),fullPage:true,animations:'disabled'});
   }
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
   const fullXP=await page.evaluate(()=>{
    const grade=SOZ_PROGRESS_CORE.grading(SOZ_PROGRESS.read(),SOZ_PROGRESS_META);
    const battery=document.querySelector('[data-phase-points] .points-battery');
    return {points:grade.points,max:grade.maxPoints,ariaMax:battery?.getAttribute('aria-valuemax'),ariaNow:battery?.getAttribute('aria-valuenow'),label:battery?.querySelector('.points-battery-label')?.textContent};
   });
   assert.deepEqual(fullXP,{points:100,max:100,ariaMax:'100',ariaNow:'100',label:'100 / 100 XP'},item.id+': perfect work earns and displays exactly 100 XP');
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

   if(item.id!=='VORLAGE-FUENF-LERNWEGE'){
    // Editor scripts initialize even when their existing login panel is closed.
    // Exercise their public data/export API without changing PIN or authentication.
    await page.goto(base+'lehrkraft.html');await page.waitForFunction(()=>window.SOZ_READY===true);
    const metadata=await page.evaluate(()=>{
     const rebuilt=SOZ_PROGRESS_CORE.metadataFrom(JSON.parse(JSON.stringify(SOZPAED)),new DOMParser());
     return {ids:Object.keys(rebuilt.tasks).sort(),expected:Object.keys(SOZ_PROGRESS_META.tasks).sort(),modes:[...new Set(Object.values(rebuilt.tasks).map(t=>t.mode))]};
    });
    assert.deepEqual(metadata.ids,metadata.expected,item.id+': editor metadata retains every W1 task');
    assert.deepEqual(metadata.modes,[1],item.id+': editor metadata contains W1 only');
    await page.evaluate(()=>{
     const stale=JSON.parse(JSON.stringify(SOZ_API.getSettings()));
     stale.mode=5;stale.allowStudentMode=true;stale.learningPaths={1:{label:'Tradiert'},5:{label:'Alt'}};
     stale.overrides={...(stale.overrides||{}),'informieren.html':SOZPAED.pages['informieren.html']+'<section data-mode-panel="5"><article class="assignment-frame"><div class="assignment-body"><p>Veralteter W5-Testauftrag</p></div></article></section>'};
     const key=SOZ_API.key+':settings:'+(SOZ_CONFIG.packageRevision||'base')+':'+location.pathname.replace(/[^/]+$/,'');
     localStorage.setItem(key,JSON.stringify(stale));
    });
    await page.reload();await page.waitForFunction(()=>window.SOZ_READY===true);
    const restoredEditor=await page.evaluate(()=>{
     const settings=SOZ_API.getSettings(),doc=new DOMParser().parseFromString(settings.overrides['informieren.html'],'text/html');
     return {mode:settings.mode,choice:settings.allowStudentMode,paths:Object.keys(settings.learningPaths),
      panels:[...new Set([...doc.querySelectorAll('[data-mode-panel]')].map(e=>e.dataset.modePanel))],
      choices:[...document.querySelectorAll('[data-teacher-mode] option')].map(e=>e.value),
      editor:!!document.querySelector('[data-page-editor]')};
    });
    assert.deepEqual(restoredEditor,{mode:1,choice:false,paths:['1'],panels:['1'],choices:['1'],editor:true},item.id+': stored editor preferences cannot restore removed paths');
    const exported=await page.evaluate(async()=>{
     await SOZ_API.loadScript('assets/export.js');
     const E=SOZ_EXPORT,K=SOZ_PROGRESS_CORE,xml=await (await fetch('imsmanifest.xml')).text();
     const manifest=new DOMParser().parseFromString(xml,'application/xml');
     const names=[...new Set(['imsmanifest.xml',...[...manifest.getElementsByTagNameNS('*','file')].map(e=>e.getAttribute('href')).filter(Boolean)])];
     // Binary assets are opaque to prepareFiles. Keep their real file names with
     // empty test payloads; load the actual HTML/manifest that the exporter edits.
     const source=Object.fromEntries(names.map(name=>[name,'']));source['imsmanifest.xml']=E.encode(xml);
     await Promise.all(['index.html',...K.phases.map(p=>p+'.html')].map(async name=>{
      const response=await fetch(name);if(!response.ok)throw Error('Missing export input '+name);source[name]=E.encode(await response.text());
     }));
     const settings=JSON.parse(JSON.stringify(SOZ_API.getSettings()));settings.mode=5;settings.allowStudentMode=true;
     settings.overrides={'informieren.html':SOZPAED.pages['informieren.html']+'<section data-mode-panel="5"><article class="assignment-frame"><div class="assignment-body"><p>Veralteter W5-Testauftrag</p></div></article></section>'};
     const out=E.prepareFiles(source,SOZPAED,settings);
     const parse=source=>JSON.parse(source.slice(source.indexOf('=')+1).trim().replace(/;$/,''));
     const meta=parse(E.decode(out.files['progress-meta.js']));
     const panels=K.phases.map(phase=>{
      const doc=new DOMParser().parseFromString(E.decode(out.files[phase+'.html']),'text/html');
      return [...new Set([...doc.querySelectorAll('[data-mode-panel]')].map(e=>e.dataset.modePanel))];
     });
     const exportedManifest=new DOMParser().parseFromString(E.decode(out.files['imsmanifest.xml']),'application/xml');
     return {mode:out.config.mode,choice:out.config.allowStudentMode,paths:Object.keys(out.config.learningPaths),
      tasks:meta.tasks,expected:SOZ_PROGRESS_META.tasks,panels,
      files:Object.keys(out.files).sort(),
      expectedFiles:[...new Set([...names.filter(n=>!['package-data.js','goodnotes-share-data.js'].includes(n)),'lesson-data.js','progress-meta.js','mode-config.js','Konfiguration.json'])].sort(),
      manifest:[...exportedManifest.getElementsByTagNameNS('*','file')].map(e=>e.getAttribute('href')).sort()};
    });
    assert.equal(exported.mode,1,item.id+': exported mode');assert.equal(exported.choice,false,item.id+': exported selection disabled');
    assert.deepEqual(exported.paths,['1'],item.id+': exported path configuration');
    assert.deepEqual(exported.tasks,exported.expected,item.id+': exported W1 task IDs and signatures preserved');
    for(const panels of exported.panels)assert.deepEqual(panels,['1'],item.id+': exported HTML removes obsolete override panel');
    assert.deepEqual(exported.files,exported.expectedFiles,item.id+': export does not resurrect deleted files');
    assert.deepEqual(exported.manifest,exported.files.filter(name=>name!=='imsmanifest.xml'),item.id+': complete exported manifest');
    assert.equal(exported.files.some(name=>/(?:^|[-_/])W[2-5](?=[._/-]|$)/i.test(name)),false,item.id+': no alternative path files in export');
   }
   assert.deepEqual(errors,[],item.id+': browser errors');
   if(['BRC-LG01-LS01','BRC-LG05-LS04','VORLAGE-TRADIERT','GESCHICHTE-J1914-Deutsches_Reich'].includes(item.id))await page.screenshot({path:path.join(output,item.id+'.png'),fullPage:true});
   console.log('PASS browser',item.id);
   await context.close();
  }
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;server.close();});

