(()=>{'use strict';
const encode=s=>{const bytes=new TextEncoder().encode(s);let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));return btoa(binary);};
const decode=s=>new TextDecoder().decode(Uint8Array.from(atob(s),c=>c.charCodeAt(0)));
function replaceContent(source,content,page){
 const startTag='<div class="lesson-content">';const start=source.indexOf(startTag);const finish=source.indexOf('</div></main>',start+startTag.length);
 if(start<0||finish<0)throw Error('Bearbeitungsbereich fehlt in '+page+'. Export abgebrochen.');
 return source.slice(0,start+startTag.length)+content+source.slice(finish);
}

function manifestPaths(xml){const doc=new DOMParser().parseFromString(xml,'application/xml');if(doc.querySelector('parsererror'))throw Error('Die Paketdateiliste ist ungültig.');const paths=[...doc.getElementsByTagNameNS('*','file')].map(el=>el.getAttribute('href')).filter(Boolean);return [...new Set(['imsmanifest.xml',...paths])].filter(name=>!['package-data.js','goodnotes-share-data.js'].includes(name));}
async function readFiles(sourceZip){let archive=null,xml,prefix='';if(sourceZip){archive=await JSZip.loadAsync(sourceZip);if(!archive.file('lesson-data.js'))prefix='LS_'+window.SOZPAED.id.replace('.','_')+'/';const manifest=archive.file(prefix+'imsmanifest.xml');if(!manifest)throw Error('Das ausgewählte ZIP enthält diese Lernsituation nicht.');xml=await manifest.async('string');const sourceData=archive.file(prefix+'lesson-data.js');if(!sourceData)throw Error('Die Lernsituationsdaten fehlen im ausgewählten ZIP.');const sourceText=await sourceData.async('string');const sourceLesson=JSON.parse(sourceText.slice(sourceText.indexOf('=')+1).trim().replace(/;$/,''));if(sourceLesson.id!==window.SOZPAED.id)throw Error('Das ausgewählte SCORM gehört zu einer anderen Lernsituation.');}else{if(location.protocol==='file:')throw Error('Bitte das zugehörige SCORM-ZIP im Feld für den lokalen Export auswählen.');const response=await fetch('imsmanifest.xml',{credentials:'same-origin',cache:'no-store'});if(!response.ok)throw Error('Die Paketdateiliste konnte nicht geladen werden.');xml=await response.text();}const names=manifestPaths(xml),files={};for(let start=0;start<names.length;start+=8){await Promise.all(names.slice(start,start+8).map(async name=>{if(/^(?:[a-z]+:|\/)|(^|\/)\.\.(\/|$)/i.test(name))throw Error('Ungültiger Paketpfad: '+name);if(archive){const entry=archive.file(prefix+name);if(!entry)throw Error('Paketdatei fehlt: '+name);files[name]=await entry.async('base64');}else{const response=await fetch(name,{credentials:'same-origin',cache:'no-store'});if(!response.ok)throw Error('Paketdatei fehlt: '+name);const bytes=new Uint8Array(await response.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));files[name]=btoa(binary);}}));}return files;}
function updateManifest(files){const doc=new DOMParser().parseFromString(decode(files['imsmanifest.xml']),'application/xml');const resource=doc.getElementsByTagNameNS('*','resource')[0];if(!resource)throw Error('SCORM-Ressource fehlt.');for(const el of [...resource.children])if(el.localName==='file')el.remove();for(const name of Object.keys(files).filter(name=>name!=='imsmanifest.xml').sort()){const node=doc.createElementNS(resource.namespaceURI,'file');node.setAttribute('href',name);resource.append(node);}files['imsmanifest.xml']=encode(new XMLSerializer().serializeToString(doc));}

function prepareFiles(base,data,settings){
 const files={...base};const cfg=JSON.parse(JSON.stringify(settings));const edited={...data,pages:{...data.pages}};const changed=[];
 for(const [page,content]of Object.entries(cfg.overrides||{})){
  if(!Object.prototype.hasOwnProperty.call(data.pages,page)||!Object.prototype.hasOwnProperty.call(files,page))throw Error('Unbekannte bearbeitete Seite: '+page);
  if(typeof content!=='string')throw Error('Ungültiger Seiteninhalt: '+page);
  files[page]=encode(replaceContent(decode(files[page]),content,page));edited.pages[page]=content;changed.push(page);
 }
 const K=window.SOZ_PROGRESS_CORE;if(!K)throw Error('Fortschrittslogik fehlt.');
 const meta=K.metadataFrom(edited,new DOMParser());
 for(const page of ['index.html',...K.phases.map(p=>p+'.html')]){files[page]=encode(replaceContent(decode(files[page]),edited.pages[page],page));}
 files['progress-meta.js']=encode('window.SOZ_PROGRESS_META='+JSON.stringify(meta)+';\n');
 cfg.mode=Number(cfg.mode);if(!meta.availableModes.includes(cfg.mode))cfg.mode=meta.availableModes[0];if(!Number.isInteger(cfg.mode)||!meta.availableModes.includes(cfg.mode))throw Error('Ungültige Unterstützungsstufe.');
 cfg.overrides={};cfg.packageRevision=new Date().toISOString()+'-'+Math.random().toString(36).slice(2,10);
 files['lesson-data.js']=encode('window.SOZPAED='+JSON.stringify(edited)+';\n');
 for(const [id,value]of Object.entries(cfg.media||{})){if(typeof value.src==='string'&&value.src.startsWith('data:')){const match=value.src.match(/^data:image\/(png|jpeg|webp|gif);base64,([A-Za-z0-9+/=\s]+)$/);if(!match)throw Error('Das Bildformat ist nicht exportierbar: '+id);const name='assets/images/custom-'+id.replace(/[^a-zA-Z0-9_-]/g,'_')+'.'+(match[1]==='jpeg'?'jpg':match[1]);files[name]=match[2].replace(/\s/g,'');value.src=name;}}
 files['mode-config.js']=encode('window.SOZ_CONFIG='+JSON.stringify(cfg)+';\n');
 files['Konfiguration.json']=encode(JSON.stringify(cfg,null,2));
 delete files['package-data.js'];delete files['goodnotes-share-data.js'];updateManifest(files);
 return {files,config:cfg,data:edited,changed};
}
window.SOZ_EXPORT={readFiles,prepareFiles,replaceContent,encode,decode};
})();
