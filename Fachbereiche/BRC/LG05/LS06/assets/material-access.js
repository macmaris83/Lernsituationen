/* BRC 1.8.3 material access: a single native details menu, never an absolute popup. */
(()=>{'use strict';
function normalize(section){
 if(section.dataset.materialAccessReady)return;
 const grid=section.querySelector('.material-grid,.material-menu');
 if(!grid)return;
 section.dataset.materialAccessReady='true';
 section.classList.add('material-access');
 grid.classList.remove('material-menu');grid.classList.add('material-grid');
 if(!grid.getAttribute('aria-label'))grid.setAttribute('aria-label','Materialien');
 for(const a of grid.querySelectorAll('a.material-link')){
  if(a.querySelector('b'))continue;
  const match=a.textContent.trim().match(/^(M\d+)\s*[·:–-]?\s*(.*)$/s);
  if(!match)continue;
  const number=document.createElement('b');number.textContent=match[1];
  const title=document.createElement('span');title.textContent=' · '+match[2];
  a.replaceChildren(number,title);
 }
}
function scan(){
 if(document.body.dataset.page==='index.html')return;
 document.querySelectorAll('.lesson-content .material-access,.lesson-content .phase-materials').forEach(normalize);
 window.SOZ_MATERIAL_RETURN?.decorate();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
})();

/* Document surfaces from Materialvorlagen/; change chrome only, never article.paper.
 * Profiles describe the existing documents, including mixed business-document sets.
 * An explicit data-material-view on .app takes precedence for future/editor materials.
 */
(()=>{'use strict';
const surfaces={
 outlook:{name:'Outlook',tabs:'Nachricht · Korrespondenz',kind:'E-Mail'},
 onenote:{name:'OneNote',tabs:'Notizen · Arbeitsunterlagen',kind:'Notiz / Arbeitsblatt'},
 teams:{name:'Microsoft Teams',tabs:'Beiträge · Dateien · Besprechungsnotizen',kind:'Chat / Besprechung'},
 sap:{name:'SAP S/4HANA',tabs:'Geschäftsvorgänge · Daten · Belege',kind:'Geschäftsunterlagen'},
 acrobat:{name:'Adobe Acrobat Reader',tabs:'Werkzeuge · Kommentieren · Ansicht',kind:'PDF-Unterlage'}
};
const profiles={
 'BRC-LG01-LS01':[
  ['teams','Besprechungsprotokoll'],['onenote','Profilkarten'],
  ['onenote','Research-Memo'],['outlook','Nachrichtensammlung'],
  ['onenote','Beratungsnotiz'],['acrobat','Prozesshandbuch'],
  ['onenote','Fachwissen'],['onenote','KI-Arbeitshilfe']
 ],
 'BRC-LG01-LS02':[
  ['outlook','E-Mail'],['onenote','Standortnotiz'],
  ['onenote','Arbeitsnotiz'],['acrobat','Quellenmappe'],
  ['onenote','Beratungsvermerk'],['onenote','Fachwissen'],['onenote','KI-Arbeitshilfe']
 ],
 'BRC-LG01-LS03':[
  ['onenote','Businessplan-Arbeitshilfe'],['onenote','Entwicklungsakte'],
  ['acrobat','Marktresearch-Bericht'],['onenote','Optionenblatt'],
  ['sap','Finanz- und Betriebsdaten'],['onenote','Fachwissen'],['onenote','KI-Arbeitshilfe']
 ],
 'BRC-LG01-LS04':[
  ['onenote','Kurzbriefing'],['outlook','Einladung'],
  ['onenote','Gestaltungshilfe'],['sap','Kapitalübersicht'],
  ['onenote','Rollenhilfe'],['onenote','Rückmeldebogen'],
  ['onenote','Fachwissen'],['onenote','KI-Arbeitshilfe']
 ],
 'BRC-LG01-LS05':[
  ['outlook','E-Mail'],['teams','Teams-Chat'],
  ['sap','Vertragsübersicht'],['acrobat','Gesetzes- und IHK-Akte'],
  ['onenote','Entscheidungsraster'],['onenote','Telefonnotiz'],
  ['onenote','Fachwissen'],['onenote','KI-Arbeitshilfe']
 ],
 'BRC-LG01-LS06':[
  ['sap','Auftragsunterlagen und Korrespondenz'],['sap','Konditionenvergleich'],
  ['sap','Lieferbelege und Reklamation'],['acrobat','Gesetzesakte'],
  ['teams','Besprechungsprotokoll'],['sap','Personal- und Kapazitätsakte'],
  ['onenote','Fachwissen'],['onenote','KI-Arbeitshilfe']
 ]
};
profiles['LS-MASTER']=profiles['BRC-LG01-LS03'];
function presentMaterials(){
 const page=(document.body.dataset.page||'').match(/^m(\d+)\.html$/);
 if(!page)return;
 const profile=profiles[window.SOZPAED?.id]?.[Number(page[1])-1];
 document.querySelectorAll('.source-document .app').forEach(app=>{
  const explicit=app.dataset.materialView;
  const view=explicit||(profile&&profile[0]);
  const surface=surfaces[view];
  if(!surface)return; // Existing LG05 and historical-source designs remain authoritative.
  const label=app.querySelector('.viewerbar strong');
  const bar=app.querySelector('.subbar');
  if(!label||!bar)return;
  for(const name of Object.keys(surfaces))app.classList.remove(name);
  app.classList.add(view);
  label.textContent=surface.name;
  const tabs=document.createElement('span');tabs.textContent=surface.tabs;
  const kind=document.createElement('span');kind.className='material-kind';
  kind.textContent=explicit?surface.kind:profile[1];
  bar.replaceChildren(tabs,kind);
 });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',presentMaterials);else presentMaterials();
})();

