/* Keep only edited task durations in the packaged PDFs synchronized. */
(()=>{'use strict';
const phases=['informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren'];
const scripts=new Map(),cache=new Map();
const encode=bytes=>{let s='';for(let i=0;i<bytes.length;i+=32768)s+=String.fromCharCode(...bytes.subarray(i,i+32768));return btoa(s);};
const decode=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
const encodeText=s=>encode(new TextEncoder().encode(s));
const decodeText=s=>new TextDecoder().decode(decode(s));
function load(src,ready){if(ready())return Promise.resolve();if(!scripts.has(src))scripts.set(src,new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=src;script.onload=()=>ready()?resolve():reject(Error('PDF-Baustein konnte nicht geladen werden.'));script.onerror=()=>{scripts.delete(src);reject(Error('PDF-Baustein konnte nicht geladen werden.'));};document.head.append(script);}));return scripts.get(src);}
const key=(phase,taskId,mode)=>phase+':'+taskId+':'+mode;
function collectChanges(settings=window.SOZ_API?.getSettings?.()||window.SOZ_CONFIG||{},data=window.SOZPAED){
 const changes={};if(!data)return changes;
 for(const phase of phases){const page=phase+'.html',override=settings.overrides?.[page];if(typeof override!=='string')continue;
  const original=new DOMParser().parseFromString(data.pages[page]||'','text/html');
  const originalTimes=new Map([...original.querySelectorAll('.assignment-frame[data-task-id]')].map(c=>[c.dataset.taskId,Number(c.dataset.taskMinutes)]));
  const edited=new DOMParser().parseFromString(override,'text/html');
  for(const card of edited.querySelectorAll('.assignment-frame[data-task-id][data-task-minutes]')){
   const minutes=Number(card.dataset.taskMinutes),id=card.dataset.taskId,mode=Number(card.dataset.sourceMode||card.closest('[data-mode-panel]')?.dataset.modePanel);
   if(!originalTimes.has(id)||!Number.isFinite(minutes)||minutes<0.5||minutes>480||!mode||minutes===originalTimes.get(id))continue;
   changes[key(phase,id,mode)]=minutes;
  }
 }
 return changes;
}
async function dependencies(){await Promise.all([load('assets/pdf-lib.min.js',()=>!!window.PDFLib),load('assets/pdf-task-times-map.js',()=>!!window.BRC_PDF_TIME_MAP)]);}
function updatesFor(file,map,changes){return (map[file]||[]).map(entry=>({entry,minutes:changes[key(entry.phase,entry.taskId,Number(entry.mode))]})).filter(v=>Number.isFinite(v.minutes)&&v.minutes!==Number(v.entry.originalMinutes));}
async function patchWithMap(file,base64,changes,map){
 const updates=updatesFor(file,map,changes);if(!updates.length)return base64;
 const {PDFDocument,StandardFonts,rgb}=window.PDFLib;const doc=await PDFDocument.load(decode(base64)),font=await doc.embedFont(StandardFonts.Helvetica),pages=doc.getPages();
 for(const {entry:e,minutes}of updates){
  const page=pages[e.page];if(!page)throw Error('PDF-Zeitfeld liegt außerhalb des Dokuments: '+file);
  if(![e.x,e.y,e.width,e.height].every(Number.isFinite)||e.width<=0||e.height<=0)throw Error('Ungültige PDF-Zeitposition: '+file);
  const color=e.color||[0.23,0.38,0.47],background=e.background||[1,1,1],size=Number(e.fontSize)||9,text='ca. '+String(minutes).replace('.',',')+' Minuten';
  const fontSize=Math.min(size,(e.width-2)*size/font.widthOfTextAtSize(text,size));
  page.drawRectangle({x:e.x,y:page.getHeight()-e.y-e.height,width:e.width,height:e.height,color:rgb(...background)});
  page.drawText(text,{x:e.x+1,y:page.getHeight()-e.y-(Number(e.baselineFromTop)||e.height-2),size:fontSize,font,color:rgb(...color)});
 }
 return encode(await doc.save());
}
async function patchBase64(file,base64,settings){
 const changes=collectChanges(settings);if(!Object.keys(changes).length)return base64;
 await dependencies();const relevant=updatesFor(file,window.BRC_PDF_TIME_MAP,changes);if(!relevant.length)return base64;
 const fingerprint=JSON.stringify(relevant.map(u=>[u.entry.taskId,u.entry.mode,u.entry.phase,u.minutes]));
 const previous=cache.get(file);if(previous?.base64===base64&&previous.fingerprint===fingerprint)return previous.promise;
 const promise=patchWithMap(file,base64,changes,window.BRC_PDF_TIME_MAP);cache.set(file,{base64,fingerprint,promise});return promise;
}
function parseAssignment(base64,prefix){const source=decodeText(base64).trim();if(!source.startsWith(prefix))throw Error('PDF-Datenformat ist nicht lesbar.');return JSON.parse(source.slice(prefix.length).replace(/;\s*$/,''));}
async function prepareExport(result,settings){
 const changes=collectChanges(settings);if(!Object.keys(changes).length)return result;
 await dependencies();const files=result.files;
 const map=files['assets/pdf-task-times-map.js']?parseAssignment(files['assets/pdf-task-times-map.js'],'window.BRC_PDF_TIME_MAP='):JSON.parse(JSON.stringify(window.BRC_PDF_TIME_MAP));
 for(const [file,entries]of Object.entries(map)){if(!files[file]||!updatesFor(file,map,changes).length)continue;files[file]=await patchWithMap(file,files[file],changes,map);for(const entry of entries){const minutes=changes[key(entry.phase,entry.taskId,Number(entry.mode))];if(Number.isFinite(minutes))entry.originalMinutes=minutes;}}
 for(const phase of phases){const file='goodnotes/page-'+phase+'.js';if(!files[file])continue;const bundle=parseAssignment(files[file],'window.BRC_CURRENT_PDF_FILES=');for(const entry of Object.values(bundle))if(files[entry.file])entry.base64=files[entry.file];files[file]=encodeText('window.BRC_CURRENT_PDF_FILES='+JSON.stringify(bundle)+';\n');}
 const printByMode={};for(let mode=1;mode<=5;mode++){const file=result.data.printPdfs?.[mode]||result.data.printPdf;if(files[file])printByMode[mode]=files[file];}
 files['print-data.js']=encodeText('window.BRC_PRINT_PDF_BY_MODE='+JSON.stringify(printByMode)+';\nwindow.BRC_PRINT_PDF=window.BRC_PRINT_PDF_BY_MODE[Number(window.SOZ_CONFIG?.mode)||1];\n');
 const workbooks={};for(const [mode,file]of Object.entries(result.data.workbooks||{}))if(files[file])workbooks[mode]=files[file];
 files['workbook-data.js']=encodeText('window.BRC_GOODNOTES_PDF_BY_MODE='+JSON.stringify(workbooks)+';\n');
 files['assets/pdf-task-times-map.js']=encodeText('window.BRC_PDF_TIME_MAP='+JSON.stringify(map)+';\n');
 return result;
}
window.BRC_PDF_TASK_TIMES={collectChanges,patchBase64,prepareExport};
})();
