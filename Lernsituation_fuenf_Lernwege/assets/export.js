(()=>{'use strict';
const encode=s=>{const bytes=new TextEncoder().encode(s);let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));return btoa(binary);};
const decode=s=>new TextDecoder().decode(Uint8Array.from(atob(s),c=>c.charCodeAt(0)));
function replaceContent(source,content,page){
 const startTag='<div class="lesson-content">';const start=source.indexOf(startTag);const finish=source.indexOf('</div></main>',start+startTag.length);
 if(start<0||finish<0)throw Error('Bearbeitungsbereich fehlt in '+page+'. Export abgebrochen.');
 return source.slice(0,start+startTag.length)+content+source.slice(finish);
}
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
 cfg.mode=Number(cfg.mode);if(!Number.isInteger(cfg.mode)||cfg.mode<1||cfg.mode>5)throw Error('Ungültige Unterstützungsstufe.');
 cfg.overrides={};cfg.packageRevision=new Date().toISOString()+'-'+Math.random().toString(36).slice(2,10);
 files['lesson-data.js']=encode('window.SOZPAED='+JSON.stringify(edited)+';\n');
 files['mode-config.js']=encode('window.SOZ_CONFIG='+JSON.stringify(cfg)+';\n');
 files['Konfiguration.json']=encode(JSON.stringify(cfg,null,2));
 delete files['package-data.js'];
 return {files,config:cfg,data:edited,changed};
}
window.SOZ_EXPORT={prepareFiles,replaceContent,encode,decode};
})();
