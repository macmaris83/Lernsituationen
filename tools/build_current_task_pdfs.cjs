/* Rebuild only the PDFs of deliberately regrouped current W1 masters.
 * Never regenerates lesson content. Run after task_slimming.py, with Playwright.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),cp=require('node:child_process'),crypto=require('node:crypto');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const phases=['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren'];
const labels={informieren:'Informieren',planen:'Planen',entscheiden:'Entscheiden',durchfuehren:'Durchführen',bewerten:'Bewerten',reflektieren:'Reflektieren'};
const payload=file=>JSON.parse(fs.readFileSync(file,'utf8').split(/=(.*)/s)[1].trim().replace(/;$/,''));
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const readJSON=file=>JSON.parse(fs.readFileSync(file,'utf8'));
const reportFile=path.join(root,'tools/fixtures/task-slimming-report.json');
const catalog=readJSON(path.join(root,'master-katalog.json')).packages;
const report=readJSON(reportFile);
const targets=report.packages.filter(p=>p.pdfChanged===true).map(p=>catalog.find(c=>c.id===p.id));
if(targets.some(p=>!p))throw Error('Unknown package in task-slimming report');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const qaFile=path.join(root,'tools/fixtures/current-task-pdfs.json');
const previous=fs.existsSync(qaFile)?readJSON(qaFile):[];
function inputHash(item){const folder=path.join(root,item.master),d=payload(path.join(folder,'lesson-data.js'));return hash(JSON.stringify({data:{title:d.title,pages:d.pages,printOrder:d.printOrder,workbooks:d.workbooks,printPdfs:d.printPdfs},groups:report.packages.find(p=>p.id===item.id).groups,css:fs.readdirSync(path.join(folder,'assets')).filter(f=>f.endsWith('.css')).sort().map(f=>fs.readFileSync(path.join(folder,'assets',f),'utf8')),builder:fs.readFileSync(__filename,'utf8'),verifier:fs.readFileSync(path.join(__dirname,'verify_current_task_pdfs.py'),'utf8')}));}
function currentPDFs(item,signature){const entries=previous.filter(e=>e.id===item.id);return entries.length>=7&&entries.every(e=>e.inputHash===signature&&fs.existsSync(path.join(root,e.master,e.file))&&hash(fs.readFileSync(path.join(root,e.master,e.file)))===e.sha256);}
function answerSpaces(item,flat){const file=path.join(root,item.master,'pdf/answer-space.json');if(!fs.existsSync(file))return;const original=readJSON(file),current={},groups=report.packages.find(p=>p.id===item.id).groups;
 for(const t of flat){const group=groups[t.phase].find(g=>g.id===t.id),entries=(group?.from||[t.id]).map(id=>original[typeof id==='string'?id:id.id]).filter(Boolean);current[t.id]={lines:entries.length?entries.reduce((n,e)=>n+Number(e.lines||0),0):8,area:entries.some(e=>e.area==='grid')?'grid':'lines',reason:entries.map(e=>e.reason).filter(Boolean).join(' ')};t.answerSpace=current[t.id];}fs.writeFileSync(file,JSON.stringify(current,null,2)+'\n');}
function retainCurrentPrintModes(){for(const item of catalog){const file=path.join(root,item.master,'assets/pdf-task-times.js');if(!fs.existsSync(file))continue;const before=fs.readFileSync(file,'utf8'),old="const printByMode={};for(let mode=1;mode<=5;mode++){const file=result.data.printPdfs?.[mode]||result.data.printPdf;if(files[file])printByMode[mode]=files[file];}",replacement="const printByMode={};for(const [mode,file]of Object.entries(result.data.printPdfs||{'1':result.data.printPdf})){if(files[file])printByMode[mode]=files[file];}";if(before.includes(old))fs.writeFileSync(file,before.replace(old,replacement));}}
const css=`@page{size:A4;margin:16mm 14mm 17mm}*{box-sizing:border-box}body{margin:0;font:10.5pt/1.45 Arial,Helvetica,sans-serif;color:#173a63;background:#fff}h1{font-size:21pt;line-height:1.18;margin:3mm 0 4mm}h2{font-size:14pt;line-height:1.2;color:#007fac;margin:4mm 0}h3{font-size:12pt}p{margin:2.5mm 0}ul,ol{padding-left:6mm}li{margin:1.5mm 0}.phase{break-before:page}.phase:first-child{break-before:auto}.eyebrow{font-size:9pt;color:#58717e;letter-spacing:.03em}.task{border:1px solid #b8dfee;border-radius:3mm;padding:4mm;margin:5mm 0;break-inside:avoid}.task.long-task{break-inside:auto}.task-header{display:flex;gap:3mm;align-items:center;break-after:avoid}.number{display:inline-flex;justify-content:center;align-items:center;background:#009bd9;color:#fff;font-weight:700;min-width:8mm;height:8mm;border-radius:50%;font-size:12pt}.task-header strong{font-size:11pt}.social{margin-left:auto;font-size:9pt;color:#36566c;text-align:right}.social svg{width:5mm;height:5mm;vertical-align:middle}.goodnotes{width:6mm;height:6mm;object-fit:contain}.pdf-task-time{display:block!important;color:#365f7c!important;font-family:Arial,Helvetica,sans-serif!important;font-size:9pt!important;line-height:13pt!important;width:150pt;margin:2mm 0 3mm!important;white-space:nowrap!important;break-after:avoid}.body p,.body li{orphans:3;widows:3}.body>p:first-child{margin-top:0}.body .book-line{display:block;font-size:9pt;color:#58717e;margin:3mm 0}.body .book-ref-icon{height:6mm;width:auto;vertical-align:middle;margin-right:2mm}.body svg{width:5mm;height:5mm}.body img:not(.book-ref-icon){max-width:100%;height:auto}.body table{border-collapse:collapse;width:100%;table-layout:auto;font-size:9.5pt}.body th,.body td{border:1px solid #b8dfee;padding:2mm;overflow-wrap:anywhere}.body .table-scroll{overflow:visible;min-width:0}.writing-space{height:38mm;margin-top:4mm;background:repeating-linear-gradient(to bottom,#fff 0,#fff 7mm,#d8e7ef 7.1mm,#fff 7.3mm);border-top:1px solid #d8e7ef;break-inside:avoid}.work-note{font-size:9pt;color:#58717e}a{color:inherit;text-decoration:none}footer{font-size:8pt;color:#58717e}button,input,select,textarea,script,.no-print,.sr-only,.assignment-time,[data-task-complete]{display:none!important}`;
const timerCSS='.pdf-task-time{display:block!important;grid-column:1/-1;color:#365f7c!important;font-family:Arial,Helvetica,sans-serif!important;font-size:9pt!important;line-height:13pt!important;width:150pt!important;margin:2mm 0 3mm!important;white-space:nowrap!important;break-after:avoid}';
const writingCSS='.writing-space{height:auto;background:none;break-inside:auto}.writing-row{height:7mm;border-bottom:1px solid #d8e7ef;break-inside:avoid}.writing-space.grid .writing-row{background:repeating-linear-gradient(to right,transparent 0,transparent 6.8mm,#e3edf2 7mm);border-bottom-color:#e3edf2}';
const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'})[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);});
function pickFiles(master,data){
 const folder=path.join(root,master),lg05=fs.existsSync(path.join(folder,'goodnotes/page-informieren.js'));
 const phaseFiles=Object.fromEntries(phases.map(p=>[p,lg05?'pdf/pages/'+p+'-W1.pdf':'pdf/GoodNotes_Phase_'+p+'_W1.pdf']));
 const workbook=data.workbooks?.['1']||data.workbook;
 const prints=fs.readdirSync(path.join(folder,'pdf')).filter(n=>/Gesamtdruck/i.test(n)&&/\.pdf$/i.test(n)&&!/(?:Weg|_W)[2-5]/i.test(n));
 const print=data.printPdfs?.['1']||data.printPdf||(prints.length===1?'pdf/'+prints[0]:null);
 if(!workbook||!print)throw Error('Unambiguous current workbook/print PDF required: '+master);
 for(const file of [...Object.values(phaseFiles),workbook,print])if(!fs.existsSync(path.join(folder,file)))throw Error('Refusing to add a new PDF path: '+master+'/'+file);
 return {lg05,phaseFiles,workbook,print};
}
async function getTasks(page,data){return page.evaluate(({data,phases})=>{
 const result={};for(const phase of phases){const doc=new DOMParser().parseFromString(data.pages[phase+'.html'],'text/html');
 result[phase]=[...doc.querySelectorAll('.assignment-frame')].filter(c=>c.closest('[data-mode-panel]')?.dataset.modePanel==='1').map(c=>{
  const original=c.querySelector('.assignment-body');if(!original)throw Error('Task body missing');const body=original.cloneNode(true);
  const time=c.querySelector('[data-minutes]'),match=c.querySelector('.assignment-time')?.textContent.match(/(\d+(?:[.,]\d+)?)\s*Min/i);
  const minutes=Number(c.dataset.taskMinutes||time?.dataset.minutes||(match?match[1].replace(',','.'):NaN));
  if(!Number.isFinite(minutes)||minutes<=0)throw Error('Current task time missing: '+c.dataset.taskId);
  body.querySelectorAll('.assignment-time,.no-print,button,input,script').forEach(e=>e.remove());
  const social=c.querySelector('.assignment-social');const label=c.dataset.workformLabel||social?.textContent.trim()||'';
  return {phase,id:c.dataset.taskId,mode:1,number:Number(c.dataset.taskNumber),minutes,html:body.innerHTML,text:body.textContent.replace(/\s+/g,' ').trim(),social:label,socialIcon:social?.querySelector('svg')?.outerHTML||'',goodnotes:c.querySelector('img.assignment-goodnotes')?.getAttribute('src')||'assets/goodnotes.png'};
 });if(result[phase].length<1||result[phase].length>4)throw Error('Phase must have 1–4 current tasks: '+phase);}
 return result;
},{data,phases});}
function phaseMarkup(item,data,phase,tasks){return `<section class="phase"><header><div class="eyebrow">BBS 1 Aurich · ${escape(item.id)}</div><h1>${escape(data.title)}</h1><h2>${escape(data.pageTitles?.[phase+'.html']||labels[phase])}</h2><p class="work-note">Arbeitsheft · ${tasks.length===1?'eine Aufgabe':tasks.length+' Aufgaben'} · ${escape(String(tasks.reduce((n,t)=>n+t.minutes,0)).replace('.',','))} Minuten</p></header>${tasks.map(t=>`<article class="task" data-pdf-task-id="${escape(t.id)}"><header class="task-header"><span class="number">${t.number}</span><strong>Aufgabe ${t.number}</strong><img class="goodnotes" src="${escape(t.goodnotes)}" alt=""><span class="social">${t.socialIcon} ${escape(t.social)}</span></header><span class="pdf-task-time">ca. ${String(t.minutes).replace('.',',')} Minuten</span><div class="body">${t.html}</div><div class="writing-space ${t.answerSpace?.area==='grid'?'grid':''}" aria-label="Raum für Notizen und eigene Ergebnisse">${'<div class="writing-row"></div>'.repeat(t.answerSpace?.lines||8)}</div></article>`).join('')}</section>`;}
async function readyImages(page){await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r;})));const broken=[...document.images].filter(i=>i.src.startsWith('http://127.0.0.1:')&&!i.naturalWidth).map(i=>i.src);if(broken.length)throw Error('Missing PDF images: '+broken.join(', '));});}
async function writeWorkbook(page,base,item,data,chapters,file){
 await page.setContent('<!doctype html><html lang="de"><head><base href="'+base+'"><meta charset="utf-8"><title>'+escape(data.title)+'</title><style>'+css+writingCSS+'</style></head><body>'+chapters.join('')+'</body></html>',{waitUntil:'load'});await readyImages(page);
 await page.evaluate(()=>document.querySelectorAll('.task').forEach(e=>{if(e.getBoundingClientRect().height>800)e.classList.add('long-task');}));
 await page.pdf({path:file,printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="width:100%;margin:0 14mm;font:8px Arial;color:#58717e;display:flex;justify-content:space-between"><span>BBS 1 Aurich · '+escape(item.id)+'</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'});
}
async function main(){
 retainCurrentPrintModes();const pending=targets.map(item=>({item,inputHash:inputHash(item)})).filter(entry=>!currentPDFs(entry.item,entry.inputHash));if(!pending.length){console.log('Current task PDFs already match current W1 content.');return;}
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const qa=[];
 try{for(const {item,inputHash:signature} of pending){const folder=path.join(root,item.master),data=payload(path.join(folder,'lesson-data.js')),files=pickFiles(item.master,data),base='http://127.0.0.1:'+server.address().port+'/'+item.master+'/';
 const context=await browser.newContext({viewport:{width:1100,height:900}}),page=await context.newPage();
 await page.route('**/*',route=>route.request().url().startsWith('http://127.0.0.1:')?route.continue():route.abort());
 await page.goto('about:blank');const tasks=await getTasks(page,data),flat=phases.flatMap(p=>tasks[p]);answerSpaces(item,flat);
 for(const phase of phases){const file=files.phaseFiles[phase];await writeWorkbook(page,base,item,data,[phaseMarkup(item,data,phase,tasks[phase])],path.join(folder,file));qa.push({id:item.id,master:item.master,file,kind:'phase',phase,tasks:tasks[phase]});}
 if(files.workbook!==files.print){await writeWorkbook(page,base,item,data,phases.map(p=>phaseMarkup(item,data,p,tasks[p])),path.join(folder,files.workbook));qa.push({id:item.id,master:item.master,file:files.workbook,kind:'workbook',tasks:flat});}
 await page.goto(base+'druckansicht.html');await page.waitForFunction(()=>window.SOZ_READY===true);await page.emulateMedia({media:'print'});
 await page.evaluate(({flat})=>{const byId=new Map(flat.map(t=>[t.id,t])),seen=[];for(const card of document.querySelectorAll('.assignment-frame')){if(card.closest('[data-mode-panel]')?.dataset.modePanel!=='1')continue;const t=byId.get(card.dataset.taskId);if(!t)throw Error('Print task not registered: '+card.dataset.taskId);const visibleNumber=Number(card.querySelector('.assignment-number')?.textContent.trim());if(visibleNumber!==t.number||Number(card.dataset.taskNumber)!==t.number)throw Error('Visible print numbering differs from current task: '+t.id);if(!card.getClientRects().length)throw Error('Current task hidden from print: '+t.id);seen.push(t.id);card.querySelectorAll('.assignment-time').forEach(e=>e.remove());const time=document.createElement('span');time.className='pdf-task-time';time.textContent='ca. '+String(t.minutes).replace('.',',')+' Minuten';const body=card.querySelector('.assignment-body');body.before(time);}if(JSON.stringify(seen)!==JSON.stringify(flat.map(t=>t.id)))throw Error('Print task order/count differs from current phases');}, {flat});
 await page.addStyleTag({content:timerCSS});await readyImages(page);await page.pdf({path:path.join(folder,files.print),printBackground:true,preferCSSPageSize:true});qa.push({id:item.id,master:item.master,file:files.print,kind:'print',tasks:flat});
 const b64=file=>fs.readFileSync(path.join(folder,file)).toString('base64');
 for(const phase of phases){const file=files.phaseFiles[phase];if(files.lg05)fs.writeFileSync(path.join(folder,'goodnotes/page-'+phase+'.js'),'window.BRC_CURRENT_PDF_FILES='+JSON.stringify({'page:1':{file,base64:b64(file)}})+';\n');else fs.writeFileSync(path.join(folder,'goodnotes-phase-'+phase+'-W1.js'),'window.GOODNOTES_PHASES=Object.assign(window.GOODNOTES_PHASES||{},'+JSON.stringify({[phase+':1']:b64(file)})+');\n');}
 if(files.lg05){fs.writeFileSync(path.join(folder,'workbook-data.js'),'window.BRC_GOODNOTES_PDF_BY_MODE='+JSON.stringify({'1':b64(files.workbook)})+';\n');fs.writeFileSync(path.join(folder,'print-data.js'),'window.BRC_PRINT_PDF_BY_MODE='+JSON.stringify({'1':b64(files.print)})+';\nwindow.BRC_PRINT_PDF=window.BRC_PRINT_PDF_BY_MODE[1];\n');}
 for(const entry of qa.filter(e=>e.id===item.id))entry.inputHash=signature;
 await context.close();console.log('PDFs rebuilt from current task content:',item.id,flat.length,'tasks');
 }}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
 const output=path.join(root,'test-results/current-task-pdfs');fs.mkdirSync(output,{recursive:true});const plan=path.join(output,'pdf-build-plan.json');fs.writeFileSync(plan,JSON.stringify(qa,null,2));
 const result=cp.spawnSync(process.env.PYTHON||'python3',[path.join(root,'tools/verify_current_task_pdfs.py'),'--root',root,'--plan',plan],{stdio:'inherit'});if(result.status!==0)throw Error('PDF verification failed');
}
main().catch(error=>{console.error(error);process.exitCode=1;server.close();});
