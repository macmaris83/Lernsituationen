/* The six phase workbooks follow the 1.8.1 reference. */
(()=>{'use strict';
const D=window.SOZPAED;if(!D||document.body.dataset.teacher)return;
const page=document.body.dataset.page||'';
document.querySelectorAll('[data-share-workbook],.phase-workbook-import,.workbook-link').forEach(e=>e.remove());
if(!/^(informieren|planen|entscheiden|durchfuehren|bewerten|reflektieren)\.html$/.test(page))return;
const menu=document.querySelector('.lesson-content>details.material-access,.lesson-content>details.phase-materials,.lesson-content>section.material-access');
if(!menu)return;
const row=document.createElement('div');row.className='material-actions-row no-print';menu.before(row);row.append(menu);
const imports=document.createElement('div');imports.className='phase-import-row';row.append(imports);
const button=document.createElement('button');button.type='button';button.className='goodnotes-current button';button.dataset.goodnotesCurrent='';
button.innerHTML='<span aria-hidden="true">↗</span><span>In Goodnotes importieren</span>';
const status=document.createElement('span');status.className='goodnotes-status sr-only';status.setAttribute('role','status');imports.append(button,status);
function selected(){const mode=Number(document.body.dataset.mode)||Number(window.SOZ_CONFIG?.mode)||1,key='page:'+mode,files=window.BRC_CURRENT_PDF_FILES||{};return {key,entry:files[key],label:(D.pageTitles[page]||'Diese Phase')+' · Lernweg '+mode};}
function allowed(){const P=window.SOZ_PROGRESS,K=window.SOZ_PROGRESS_CORE;return !P||!K||!K.blockedBy(P.read(),window.SOZ_PROGRESS_META,page,Number(document.body.dataset.mode)||1);}
let prepared=null;
function update(){
 const s=selected();button.dataset.pdfKey=s.key;button.title=s.label+' als PDF in Goodnotes importieren';button.setAttribute('aria-label','In Goodnotes importieren · '+s.label);
 if(s.entry&&(!prepared||prepared.key!==s.key||prepared.source!==s.entry.base64)){
  const current=prepared={key:s.key,source:s.entry.base64,file:s.entry.file,value:null,error:null};
  const patch=window.BRC_PDF_TASK_TIMES?.patchBase64(s.entry.file,s.entry.base64)||Promise.resolve(s.entry.base64);
  patch.then(value=>{current.value=value;if(prepared===current)update();}).catch(error=>{current.error=error;if(prepared===current){status.classList.remove('sr-only');status.textContent='Die PDF konnte nicht mit den aktuellen Arbeitszeiten vorbereitet werden. Bitte die Seite erneut öffnen.';button.disabled=true;}});
 }
 button.disabled=!allowed()||!prepared?.value;
}
button.addEventListener('click',async event=>{
 event.preventDefault();event.stopPropagation();if(!allowed())return;const s=selected();if(!prepared?.value||prepared.key!==s.key)return;
 const binary=atob(prepared.value),bytes=Uint8Array.from(binary,c=>c.charCodeAt(0)),file=new File([bytes],prepared.file.split('/').pop(),{type:'application/pdf'});
 try{if(navigator.canShare?.({files:[file]})){await navigator.share({files:[file],title:s.label+' · '+D.title});status.textContent='PDF zum Import bereitgestellt.';}else{window.SOZ_API.blobDownload(file,file.name);status.textContent='PDF heruntergeladen. Öffne sie anschließend in Goodnotes.';}}
 catch(error){if(error.name!=='AbortError'){window.SOZ_API.blobDownload(file,file.name);status.textContent='PDF heruntergeladen. Öffne sie anschließend in Goodnotes.';}}
});
new MutationObserver(update).observe(document.body,{attributes:true,attributeFilter:['data-mode']});window.SOZ_SCORM?.subscribe?.(update);update();
window.BRC_CURRENT_GOODNOTES={selected,update};
})();
