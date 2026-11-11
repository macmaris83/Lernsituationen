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
const baseStyles=fs.readFileSync(process.env.MATERIAL_BASE_STYLE||path.join(root,'Formmaster/assets/styles.css'),'utf8');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox'],...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
 let checked=0,preserved=0;
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
     const before=await page.evaluate(({html,id,name})=>{
      document.body.dataset.page=name;window.SOZPAED={id};
      const doc=new DOMParser().parseFromString(html,'text/html');
      const source=doc.querySelector('.source-document');
      if(source)document.body.append(source);
      else document.body.innerHTML=html;
      window.originalPaper=document.querySelector('.paper');
      window.originalView=document.querySelector('.app')?.outerHTML;
      return {paper:window.originalPaper?.outerHTML||null,view:window.originalView||null,file:document.querySelector('.viewerbar .file')?.textContent||null};
     },{html,id:data.id,name});
     await page.addScriptTag({content:asset});
     const after=await page.evaluate(()=>({
      paper:document.querySelector('.paper')?.outerHTML||null,
      sameNode:document.querySelector('.paper')===window.originalPaper,
      view:document.querySelector('.app')?.outerHTML||null,
      classes:[...(document.querySelector('.app')?.classList||[])],
      kind:document.querySelector('.material-kind')?.textContent,
      file:document.querySelector('.viewerbar .file')?.textContent||null,
      viewerbar:document.querySelector('.viewerbar')?.textContent||'',
      overflow:document.documentElement.scrollWidth>innerWidth+2
     }));
     const label=data.id+' '+name+' '+width;
     assert.equal(after.paper,before.paper,label+': exact original material markup');
     assert.equal(after.sameNode,true,label+': original DOM nodes/listeners retained');
     assert.equal(after.file,before.file,label+': original document title retained');
     if(expected[data.id]){
      const surface=expected[data.id].split(' ')[Number(name.match(/\d+/)[0])-1];
      assert.ok(after.classes.includes(surface),label+': document type');
      assert.ok(after.kind,label+': visible document kind');
      if(surface!=='acrobat'){
       assert.doesNotMatch(after.viewerbar,/Acrobat|\.pdf\b/i,label+': no misleading PDF application or filename');
       assert.doesNotMatch(after.kind,/PDF/i,label+': document kind matches non-PDF surface');
      }
      assert.equal(after.overflow,false,label+': no horizontal page overflow');
      checked++;
     }else{
      assert.equal(after.view,before.view,label+': existing subject-specific surface preserved');
      preserved++;
     }
    }
   }
  }
  console.log(`Material surfaces: ${checked} updated views, ${preserved} existing views, original content and DOM nodes retained.`);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
