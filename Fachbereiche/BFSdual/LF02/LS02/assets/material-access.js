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
 outlook:{name:'Outlook',icon:'O',tabs:'Nachricht · Korrespondenz',kind:'E-Mail',railTitle:'E-Mail',rail:['Posteingang','Entwürfe','Gesendet','Archiv']},
 onenote:{name:'OneNote',icon:'N',tabs:'Notizen · Arbeitsunterlagen',kind:'Notiz / Arbeitsblatt',railTitle:'Notizbuch',rail:['Notizen','Unterlagen','Besprechungen']},
 teams:{name:'Microsoft Teams',icon:'T',tabs:'Beiträge · Dateien · Besprechungsnotizen',kind:'Chat / Besprechung',railTitle:'Zusammenarbeit',rail:['Chat','Teams','Kalender','Dateien']},
 sap:{name:'SAP S/4HANA',icon:'S',tabs:'Geschäftsvorgänge · Daten · Belege',kind:'Geschäftsunterlagen',railTitle:'Navigation',rail:['Übersicht','Vorgänge','Belege','Auswertungen']},
 acrobat:{name:'Adobe Acrobat Reader',icon:'PDF',tabs:'Werkzeuge · Kommentieren · Ansicht',kind:'PDF-Unterlage',railTitle:'Dokument',rail:['Seiten','Lesezeichen']}
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
function element(tag,className,text){
 const node=document.createElement(tag);node.className=className;
 if(text)node.textContent=text;
 return node;
}
function decorateChrome(app,view,surface,profile,explicit){
 if(app.dataset.materialSurface==='v2')return;
 const viewer=app.querySelector('.viewerbar'),label=viewer?.querySelector('strong');
 const bar=app.querySelector('.subbar'),canvas=app.querySelector('.canvas');
 if(!label||!bar||!canvas||!canvas.querySelector('article.paper'))return;
 // Existing subject-specific surfaces retain their title and document meaning.
 const kindText=profile&&!explicit?profile[1]:(bar.querySelector('.material-kind')?.textContent||surface.kind);
 if(profile||explicit){
  for(const name of Object.keys(surfaces))app.classList.remove(name);
  app.classList.add(view);label.textContent=surface.name;
 }
 const icon=element('span','material-app-icon',surface.icon);icon.setAttribute('aria-hidden','true');label.before(icon);
 viewer.querySelector('.dots')?.setAttribute('aria-hidden','true');
 const tools=[...viewer.children].find(node=>node!==label&&/^[—\s□×]+$/.test(node.textContent));
 if(tools){tools.classList.add('material-window-tools');tools.setAttribute('aria-hidden','true');}
 const search=element('span','material-search','⌕  Suchen');search.setAttribute('aria-hidden','true');
 (viewer.querySelector('.grow')||tools)?.before(search);
 if(!search.parentNode)viewer.append(search);
 const tabs=surface.tabs.split(' · ').map((text,index)=>element('span','material-tab'+(index?'':' is-active'),text));
 const kind=element('span','material-kind',kindText);bar.replaceChildren(...tabs,kind);
 // The chrome is a static document frame. No non-functional links or controls
 // are introduced, and the original paper and all its event listeners stay intact.
 const workspace=element('div','material-workspace'),rail=element('aside','material-rail');
 rail.setAttribute('aria-hidden','true');rail.append(element('span','material-rail-title',surface.railTitle));
 surface.rail.forEach((text,index)=>rail.append(element('span','material-rail-item'+(index?'':' is-active'),text)));
 canvas.before(workspace);workspace.append(rail,canvas);
 app.dataset.materialView=view;app.dataset.materialSurface='v2';
}
function presentMaterials(){
 const page=(document.body.dataset.page||'').match(/^m(\d+)\.html$/);
 if(!page)return;
 const profile=profiles[window.SOZPAED?.id]?.[Number(page[1])-1];
 document.querySelectorAll('.source-document .app').forEach(app=>{
  const explicit=app.dataset.materialView;
  const existing=Object.keys(surfaces).find(name=>app.classList.contains(name));
  const view=explicit||(profile&&profile[0])||existing;
  const surface=surfaces[view];
  if(!surface)return; // Historical source layouts without these app classes stay intact.
  decorateChrome(app,view,surface,profile,explicit);
 });
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',presentMaterials);else presentMaterials();
})();


