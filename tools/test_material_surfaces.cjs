/* Check document-specific UI without rewriting any material content or source nodes. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const sourceRoot=process.env.MATERIAL_SOURCE_ROOT||root;
const expected={
 'BRC-LG01-LS01':'teams onenote onenote outlook onenote acrobat onenote onenote',
 'BRC-LG01-LS02':'outlook onenote onenote acrobat onenote onenote onenote',
 'BRC-LG01-LS03':'onenote onenote acrobat onenote sap onenote onenote',
 'BRC-LG01-LS04':'onenote outlook onenote sap onenote onenote onenote onenote',
 'BRC-LG01-LS05':'outlook teams sap acrobat onenote onenote onenote onenote',
 'BRC-LG01-LS06':'sap sap sap acrobat teams sap onenote onenote',
 'LS-MASTER':'onenote onenote acrobat onenote sap onenote onenote'
};
const catalog=JSON.parse(fs.readFileSync(path.join(sourceRoot,'master-katalog.json'),'utf8'));
const asset=fs.readFileSync(path.join(root,'Formmaster/assets/material-access.js'),'utf8');
const styles=fs.readFileSync(path.join(root,'Formmaster/assets/material-views.css'),'utf8');
assert.equal(styles,fs.readFileSync(path.join(root,'Materialvorlagen/assets/material-views.css'),'utf8'),'shared and standalone material templates use the same stylesheet');
const baseStyles=fs.readFileSync(process.env.MATERIAL_BASE_STYLE||path.join(root,'Formmaster/assets/styles.css'),'utf8');
const surfaceNames=['outlook','onenote','teams','sap','acrobat'];
const output=path.join(root,'test-results/form185');fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox'],...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
 let checked=0,preserved=0;
 const screenshotSurfaces=new Set();let mobileScreenshot=false;
 try{
  const page=await browser.newPage();
  for(const item of catalog.packages.filter(p=>p.typ==='Lernsituation')){
   const file=path.join(sourceRoot,item.master,'lesson-data.js');
   if(!fs.existsSync(file))throw Error('Missing material source: '+file);
   const context={window:{}};vm.runInNewContext(fs.readFileSync(file,'utf8'),context);
   const data=context.window.SOZPAED;
   for(const [name,html] of Object.entries(data.pages).filter(([name])=>/^m\d+\.html$/.test(name))){
    for(const width of [390,1024]){
     await page.setViewportSize({width,height:844});
     await page.setContent('<!doctype html><html lang="de"><head><meta charset="utf-8"></head><body></body></html>');
     await page.addStyleTag({content:baseStyles+'\n'+styles});
     const before=await page.evaluate(({html,id,name,surfaceNames})=>{
      document.body.dataset.page=name;window.SOZPAED={id};
      const doc=new DOMParser().parseFromString(html,'text/html');
      const source=doc.querySelector('.source-document');
      if(source)document.body.append(source);
      else document.body.innerHTML=html;
      window.originalPaper=document.querySelector('.paper');
      window.originalView=document.querySelector('.app')?.outerHTML;
      window.originalCanvas=document.querySelector('.source-document .app .canvas');
      const nodes=root=>{if(!root)return [];const walker=document.createTreeWalker(root,NodeFilter.SHOW_ALL),out=[];while(walker.nextNode())out.push(walker.currentNode);return out;};
      window.originalPaperNodes=nodes(window.originalPaper);
      window.originalChromeControls=new Set([...document.querySelectorAll('.app button,.app input,.app select,.app textarea,.app a[href],.app [role="button"],.app [tabindex]:not([tabindex="-1"]),.app [contenteditable="true"]')].filter(e=>!window.originalPaper?.contains(e)));
      const app=source?.querySelector('.app');
      return {paper:window.originalPaper?.outerHTML||null,view:window.originalView||null,file:document.querySelector('.viewerbar .file')?.textContent||null,
       source:!!source,existing:surfaceNames.find(type=>app?.classList.contains(type))||null,explicit:app?.dataset.materialView||null};
     },{html,id:data.id,name,surfaceNames});
     await page.addScriptTag({content:asset});
     const after=await page.evaluate(()=>{
      const app=document.querySelector('.app'),paper=document.querySelector('.paper');
      const walker=paper?document.createTreeWalker(paper,NodeFilter.SHOW_ALL):null,nodes=[];
      if(walker)while(walker.nextNode())nodes.push(walker.currentNode);
      const addedControls=[...document.querySelectorAll('.app button,.app input,.app select,.app textarea,.app a[href],.app [role="button"],.app [tabindex]:not([tabindex="-1"]),.app [contenteditable="true"]')].filter(e=>!paper?.contains(e)&&!window.originalChromeControls.has(e));
      const rail=app?.querySelector('.material-rail');
      return {paper:paper?.outerHTML||null,sameNode:paper===window.originalPaper,
       sameDescendants:nodes.length===window.originalPaperNodes.length&&nodes.every((node,index)=>node===window.originalPaperNodes[index]),
       view:app?.outerHTML||null,classes:[...(app?.classList||[])],
       kind:app?.querySelector('.material-kind')?.textContent,
       file:document.querySelector('.viewerbar .file')?.textContent||null,
       viewerbar:document.querySelector('.viewerbar')?.textContent||'',
       surface:app?.dataset.materialSurface,viewType:app?.dataset.materialView,
       workspace:app?.querySelectorAll('.material-workspace').length||0,
       originalCanvas:!!window.originalCanvas&&app?.querySelector('.material-workspace>.canvas')===window.originalCanvas,
       rails:app?.querySelectorAll('.material-workspace>.material-rail').length||0,
       railDecorative:rail?.getAttribute('aria-hidden')==='true',
       railHidden:!rail||getComputedStyle(rail).display==='none'||rail.getBoundingClientRect().width===0,
       icons:app?.querySelectorAll('.viewerbar .material-app-icon').length||0,
       searches:app?.querySelectorAll('.viewerbar span.material-search').length||0,
       tabs:app?.querySelectorAll('.subbar .material-tab').length||0,
       addedControls:addedControls.length,
       overflow:document.documentElement.scrollWidth>innerWidth+2};
     });
     const label=data.id+' '+name+' '+width;
     assert.equal(after.paper,before.paper,label+': exact original material markup');
     assert.equal(after.sameNode,true,label+': original DOM nodes/listeners retained');
     assert.equal(after.sameDescendants,true,label+': every original paper descendant retained');
     assert.equal(after.file,before.file,label+': original document title retained');
     const profile=expected[data.id]?.split(' ')[Number(name.match(/\d+/)[0])-1];
     const surface=before.explicit||profile||before.existing;
     if(before.source&&surfaceNames.includes(surface)){
      assert.ok(after.classes.includes(surface),label+': document type');
      if(!profile&&!before.explicit)assert.deepEqual(after.classes.filter(type=>surfaceNames.includes(type)),[before.existing],label+': existing subject-specific application type retained');
      assert.ok(after.kind,label+': visible document kind');
      if(profile&&surface!=='acrobat'){
       assert.doesNotMatch(after.viewerbar,/Acrobat|\.pdf\b/i,label+': no misleading PDF application or filename');
       assert.doesNotMatch(after.kind,/PDF/i,label+': document kind matches non-PDF surface');
      }
      assert.equal(after.surface,'v2',label+': realistic application surface');
      assert.equal(after.viewType,surface,label+': resolved application view');
      assert.equal(after.workspace,1,label+': one application workspace');
      assert.equal(after.originalCanvas,true,label+': original canvas moved without replacement');
      assert.equal(after.rails,1,label+': one decorative navigation rail');
      assert.equal(after.railDecorative,true,label+': static navigation rail hidden from assistive technology');
      if(width===390)assert.equal(after.railHidden,true,label+': decorative rail hidden on mobile');
      assert.equal(after.icons,1,label+': one application badge');
      assert.equal(after.searches,1,label+': static search label');
      assert.ok(after.tabs>0,label+': application tabs');
      assert.equal(after.addedControls,0,label+': no non-functional interactive controls');
      assert.equal(after.overflow,false,label+': no horizontal page overflow');
      // Loading the shared material asset again must leave both chrome and
      // article content untouched, rather than nesting workspaces or badges.
      await page.addScriptTag({content:asset});
      assert.equal(await page.locator('.app').evaluate(e=>e.outerHTML),after.view,label+': idempotent shared asset');
      await page.emulateMedia({media:'print'});
      const print=await page.evaluate(()=>({
       chrome:[...document.querySelectorAll('.source-document .viewerbar,.source-document .subbar,.source-document .material-rail')].every(e=>getComputedStyle(e).display==='none'),
       paper:!!document.querySelector('article.paper')&&getComputedStyle(document.querySelector('article.paper')).display!=='none'
      }));
      assert.equal(print.chrome,true,label+': application chrome hidden in print');
      assert.equal(print.paper,true,label+': original material stays printable');
      await page.emulateMedia({media:'screen'});
      // Keep artifacts compact while showing all five application families,
      // including existing LG05 surfaces and one narrow-screen example.
      if(width===1024&&!screenshotSurfaces.has(surface)&&((item.master.includes('/LG05/')&&['outlook','teams'].includes(surface))||(!['outlook','teams'].includes(surface)&&item.master.includes('/LG01/')))){
       await page.screenshot({path:path.join(output,data.id+'-'+name.replace('.html','')+'-'+surface+'-1024.png'),fullPage:true,animations:'disabled'});
       screenshotSurfaces.add(surface);
      }
      if(width===390&&!mobileScreenshot&&item.master.includes('/LG05/')){
       await page.screenshot({path:path.join(output,data.id+'-'+name.replace('.html','')+'-'+surface+'-390.png'),fullPage:true,animations:'disabled'});mobileScreenshot=true;
      }
      checked++;
     }else{
      assert.equal(after.view,before.view,label+': existing subject-specific surface preserved');
      preserved++;
     }
    }
   }
  }
  for(const surface of surfaceNames){
   const html=fs.readFileSync(path.join(root,'Materialvorlagen',surface+'.html'),'utf8');
   for(const width of [390,1024]){
    await page.setViewportSize({width,height:844});
    await page.setContent('<!doctype html><html lang="de"><head><meta charset="utf-8"></head><body></body></html>');
    await page.addStyleTag({content:styles});
    const template=await page.evaluate(({html})=>{
     const doc=new DOMParser().parseFromString(html,'text/html'),source=doc.querySelector('.source-document');
     if(!source)throw Error('Standalone material template lacks its source frame');
     const originalPaper=source.querySelector('article.paper')?.outerHTML;
     document.body.append(source);
     const app=source.querySelector('.app'),rail=app?.querySelector('.material-rail');
     return {surface:app?.dataset.materialSurface,view:app?.dataset.materialView,
      workspace:app?.querySelectorAll('.material-workspace').length||0,
      rails:app?.querySelectorAll('.material-workspace>.material-rail').length||0,
      mobileRailHidden:!!rail&&(getComputedStyle(rail).display==='none'||rail.getBoundingClientRect().width===0),
      paper:source.querySelector('article.paper')?.outerHTML,originalPaper,
      overflow:document.documentElement.scrollWidth>innerWidth+2};
    },{html});
    const label='Standalone '+surface+' '+width;
    assert.equal(template.surface,'v2',label+': current application chrome');
    assert.equal(template.view,surface,label+': matching material view');
    assert.equal(template.workspace,1,label+': one workspace');
    assert.equal(template.rails,1,label+': one decorative navigation rail');
    if(width===390)assert.equal(template.mobileRailHidden,true,label+': rail hidden on mobile');
    assert.ok(template.paper,label+': placeholder article remains available');
    assert.equal(template.paper,template.originalPaper,label+': placeholder content retained');
    assert.equal(template.overflow,false,label+': no horizontal page overflow');
   }
  }
  assert.deepEqual([...screenshotSurfaces].sort(),surfaceNames.slice().sort(),'representative screenshots cover all five material applications');
  assert.equal(mobileScreenshot,true,'an existing LG05 material is previewed at mobile width');
  console.log(`Material surfaces: ${checked} updated views, ${preserved} historical views; original content, DOM nodes, idempotence, print and responsive layout verified.`);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

