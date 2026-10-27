(()=>{'use strict';const D=window.SOZPAED,A=window.SOZ_API;if(!D||!A)return;
const page=document.body.dataset.page,mode=()=>Number(document.body.dataset.mode)||Number(window.SOZ_CONFIG.mode)||1;
const modeNames=['','Stark geführt','Geführt','Begleitet','Teiloffen','Löppt'];
for(const select of document.querySelectorAll('[data-teacher-mode],[data-student-mode]'))for(const option of select.options)option.textContent=option.value+' · '+modeNames[Number(option.value)];
function pdfFile(encoded,name){const binary=atob(encoded),bytes=new Uint8Array(binary.length);for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);return new File([bytes],name,{type:'application/pdf'});}
async function share(file){try{if(navigator.canShare?.({files:[file]}))await navigator.share({files:[file],title:file.name});else A.blobDownload(file,file.name);}catch(error){if(error.name!=='AbortError')A.blobDownload(file,file.name);}}
const prepared=new Map();
function prepare(file,encoded){if(!file||!encoded)return Promise.reject(Error('Die PDF fehlt im Paket.'));const old=prepared.get(file);if(old?.source===encoded)return old.promise;const promise=(window.BRC_PDF_TASK_TIMES?.patchBase64(file,encoded)||Promise.resolve(encoded)).then(value=>pdfFile(value,file.split('/').pop()));prepared.set(file,{source:encoded,promise});return promise;}
document.addEventListener('click',event=>{const button=event.target.closest('[data-share-workbook]');if(!button)return;event.preventDefault();event.stopImmediatePropagation();const file=D.workbooks[String(mode())],encoded=window.BRC_GOODNOTES_PDF_BY_MODE?.[String(mode())];prepare(file,encoded).then(share).catch(()=>{});},true);
const documentButton=document.querySelector('[data-share-document]');let documentFile=null,documentKey='';
function prepareDocument(){
 if(!documentButton)return;const n=mode(),file=D.printPdfs?.[String(n)]||D.printPdf,encoded=window.BRC_PRINT_PDF_BY_MODE?.[String(n)]||window.BRC_PRINT_PDF;
 if(documentKey===file)return;documentKey=file;documentFile=null;documentButton.disabled=true;
 prepare(file,encoded).then(value=>{if(documentKey!==file)return;documentFile=value;documentButton.disabled=false;}).catch(()=>{if(documentKey!==file)return;documentButton.disabled=true;documentButton.title='Die PDF konnte nicht mit den aktuellen Arbeitszeiten vorbereitet werden. Bitte die Seite erneut öffnen.';});
}
documentButton?.addEventListener('click',()=>{if(documentFile)void share(documentFile);});
new MutationObserver(prepareDocument).observe(document.body,{attributes:true,attributeFilter:['data-mode']});prepareDocument();
// Embedded document surfaces keep their original exact content and fit their height.
function fitFrame(frame){try{const d=frame.contentDocument;if(!d?.body)return;const fit=()=>{frame.style.height=Math.ceil(Math.max(d.body.getBoundingClientRect().height,d.body.scrollHeight)+8)+'px';};fit();new ResizeObserver(fit).observe(d.body);}catch{}}
for(const frame of document.querySelectorAll('iframe[srcdoc]')){frame.addEventListener('load',()=>fitFrame(frame));fitFrame(frame);}
})();
