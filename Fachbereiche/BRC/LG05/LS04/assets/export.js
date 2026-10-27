(()=>{'use strict';
const encode=s=>{const bytes=new TextEncoder().encode(s);let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));return btoa(binary);};
const decode=s=>new TextDecoder().decode(Uint8Array.from(atob(s),c=>c.charCodeAt(0)));
function replaceContent(source,content,page){
 const startTag='<div class="lesson-content">';const start=source.indexOf(startTag);const finish=source.indexOf('</div></main>',start+startTag.length);
 if(start<0||finish<0)throw Error('Bearbeitungsbereich fehlt in '+page+'. Export abgebrochen.');
 return source.slice(0,start+startTag.length)+content+source.slice(finish);
}

function manifestPaths(xml){const doc=new DOMParser().parseFromString(xml,'application/xml');if(doc.querySelector('parsererror'))throw Error('Die Paketdateiliste ist ungültig.');const resources=[...doc.getElementsByTagNameNS('*','resource')];if(!resources.some(r=>r.getAttribute('href')==='scorm.html'&&r.getAttributeNS('http://www.adlnet.org/xsd/adlcp_rootv1p2','scormtype')==='sco'))throw Error('Bitte das aktuelle SCORM-1.2-Paket als Quelle auswählen. Ein IMS-Paket kann nicht exportiert werden.');const paths=[...doc.getElementsByTagNameNS('*','file')].map(el=>el.getAttribute('href')).filter(Boolean);return [...new Set(['imsmanifest.xml',...paths])].filter(name=>!['package-data.js','goodnotes-share-data.js'].includes(name));}
const OPTIONAL_EXPORT_FILES=new Set(['README.txt','README_5_STUFEN.txt','MOODLE_SETUP.txt','Paketversion.json','Konfiguration.json']);
function syntheticOptional(name){
 if(name==='Konfiguration.json')return JSON.stringify(window.SOZ_API?.getSettings?.()||window.SOZ_CONFIG||{},null,2);
 if(name==='Paketversion.json')return JSON.stringify({version:'1.8.2',packageFormat:'SCORM 1.2',title:window.SOZPAED?.title||''},null,2);
 return 'SCORM 1.2 · '+(window.SOZPAED?.title||'Lernpaket')+'\nDieses Einzelpaket in Moodle als SCORM-Lernpaket importieren. Startdatei: scorm.html.\n';
}
function looksLikeHTML(bytes){const head=new TextDecoder().decode(bytes.slice(0,256)).trimStart();return /^(?:<!doctype\s+html|<html(?:\s|>))/i.test(head);}
async function readFiles(sourceZip){
 let archive=null,xml;
 if(sourceZip){archive=await JSZip.loadAsync(sourceZip);const manifest=archive.file('imsmanifest.xml');if(!manifest)throw Error('Das ausgewählte ZIP enthält kein SCORM-Manifest.');xml=await manifest.async('string');}
 else{if(location.protocol==='file:')throw Error('Bitte das zugehörige SCORM-ZIP im Feld für den lokalen Export auswählen.');const response=await fetch('imsmanifest.xml',{credentials:'same-origin',cache:'no-store'});if(!response.ok)throw Error('Die Paketdateiliste konnte nicht geladen werden.');xml=await response.text();}
 const names=manifestPaths(xml),files={};
 for(let start=0;start<names.length;start+=8){await Promise.all(names.slice(start,start+8).map(async name=>{
  if(/^(?:[a-z]+:|\/)|(^|\/)\.\.(\/|$)/i.test(name))throw Error('Ungültiger Paketpfad: '+name);
  try{
   let bytes;
   if(archive){const entry=archive.file(name);if(!entry)throw Error('nicht gefunden');bytes=await entry.async('uint8array');}
   else{const response=await fetch(name,{credentials:'same-origin',cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);bytes=new Uint8Array(await response.arrayBuffer());}
   if(!/\.html?$/i.test(name)&&looksLikeHTML(bytes))throw Error('Anmeldeseite statt Paketdatei');
   let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));files[name]=btoa(binary);
  }catch(err){if(OPTIONAL_EXPORT_FILES.has(name)){files[name]=encode(syntheticOptional(name));return;}throw Error('Die benötigte Paketdatei „'+name+'“ konnte nicht geladen werden. Bitte die Moodle-Anmeldung und den Zugriff auf die Paketdateien prüfen.');}
 }));}
 return files;
}
function updateManifest(files){const doc=new DOMParser().parseFromString(decode(files['imsmanifest.xml']),'application/xml');const resource=doc.getElementsByTagNameNS('*','resource')[0];if(!resource)throw Error('SCORM-Ressource fehlt.');for(const el of [...resource.children])if(el.localName==='file')el.remove();for(const name of Object.keys(files).filter(name=>name!=='imsmanifest.xml').sort()){const node=doc.createElementNS(resource.namespaceURI,'file');node.setAttribute('href',name);resource.append(node);}files['imsmanifest.xml']=encode(new XMLSerializer().serializeToString(doc));}

// Preserve completed work when only layout, references, or task time changed.
function preserveUnchangedTaskSignatures(edited,original,meta,parser){
 const oldMeta=window.SOZ_PROGRESS_META;if(!oldMeta?.tasks)return;
 const fingerprint=card=>{const body=card?.querySelector('.assignment-body')?.cloneNode(true);if(!body)return null;
  body.querySelectorAll('.book-line,.assignment-meta[data-task-meta],.assignment-time[data-time-ui]').forEach(e=>e.remove());
  body.querySelectorAll('a[href="feedback.html"],a[href="#kompetenzcheck"]').forEach(a=>a.textContent='Kompetenzselbstbewertung');
  return (body.textContent||'').replace(/\s+/g,'');};
 for(const phase of window.SOZ_PROGRESS_CORE.phases){const page=phase+'.html';
  const before=parser.parseFromString('<div>'+original.pages[page]+'</div>','text/html');
  const after=parser.parseFromString('<div>'+edited.pages[page]+'</div>','text/html');
  const previous=new Map([...before.querySelectorAll('.assignment-frame[data-task-stable-id]')].map(e=>[e.dataset.taskStableId,fingerprint(e)]));
  for(const card of after.querySelectorAll('.assignment-frame[data-task-id]')){const id=card.dataset.taskId,prior=oldMeta.tasks[id];
   if(prior&&previous.has(id)&&previous.get(id)===fingerprint(card)){meta.tasks[id].signature=prior.signature;card.dataset.taskSignature=prior.signature;}
  }
  edited.pages[page]=after.body.firstElementChild.innerHTML;
 }
}

function prepareFiles(base,data,settings){
 const files={...base};const cfg=JSON.parse(JSON.stringify(settings));const edited={...data,pages:{...data.pages}};const changed=[];
 for(const [page,content]of Object.entries(cfg.overrides||{})){
  if(!Object.prototype.hasOwnProperty.call(data.pages,page)||!Object.prototype.hasOwnProperty.call(files,page))throw Error('Unbekannte bearbeitete Seite: '+page);
  if(typeof content!=='string')throw Error('Ungültiger Seiteninhalt: '+page);
  let normalized=content;if(/^(informieren|planen|entscheiden|durchfuehren|bewerten|reflektieren)\.html$/.test(page)&&window.SOZ_TASK_LAYOUT?.normalize){const temp=document.createElement('div');temp.innerHTML=content;window.SOZ_TASK_LAYOUT.normalize(temp);normalized=temp.innerHTML;}
  files[page]=encode(replaceContent(decode(files[page]),normalized,page));edited.pages[page]=normalized;changed.push(page);
 }
 const K=window.SOZ_PROGRESS_CORE;if(!K)throw Error('Fortschrittslogik fehlt.');
 const parser=new DOMParser();const meta=K.metadataFrom(edited,parser);
 preserveUnchangedTaskSignatures(edited,data,meta,parser);
 for(const page of ['index.html',...K.phases.map(p=>p+'.html')]){files[page]=encode(replaceContent(decode(files[page]),edited.pages[page],page));}
 files['progress-meta.js']=encode('window.SOZ_PROGRESS_META='+JSON.stringify(meta)+';\n');
 cfg.mode=Number(cfg.mode);if(!Number.isInteger(cfg.mode)||cfg.mode<1||cfg.mode>5)throw Error('Ungültige Unterstützungsstufe.');
 cfg.overrides={};delete cfg.previousPackageRevision;cfg.packageRevision=new Date().toISOString()+'-'+Math.random().toString(36).slice(2,10);
 files['lesson-data.js']=encode('window.SOZPAED='+JSON.stringify(edited)+';\n');
 for(const [id,value]of Object.entries(cfg.media||{})){if(typeof value.src==='string'&&value.src.startsWith('data:')){const match=value.src.match(/^data:image\/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=\s]+)$/);if(!match)throw Error('Das Bildformat ist nicht exportierbar: '+id);const name='assets/images/custom-'+id.replace(/[^a-zA-Z0-9_-]/g,'_')+'.'+(match[1]==='jpeg'?'jpg':match[1]);files[name]=match[2].replace(/\s/g,'');value.src=name;}}
 files['mode-config.js']=encode('window.SOZ_CONFIG='+JSON.stringify(cfg)+';\n');
 files['Konfiguration.json']=encode(JSON.stringify(cfg,null,2));
 delete files['package-data.js'];delete files['goodnotes-share-data.js'];updateManifest(files);
 return {files,config:cfg,data:edited,changed};
}
window.SOZ_EXPORT={readFiles,prepareFiles,replaceContent,encode,decode};
})();
