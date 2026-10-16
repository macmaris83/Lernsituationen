import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {builderComplete} from './fixtures/learning.mjs';
const dist=new URL('../dist/',import.meta.url),code=name=>fs.readFileSync(new URL(name,dist),'utf8');
function model(change=null,{preview=false,local=new Map(),api=null}={}){
 const listeners={},win={location:{pathname:preview?'/preview.html':'/index.html'},localStorage:{getItem:k=>local.get(k)||null,setItem:(k,v)=>local.set(k,v)},document:{addEventListener(){}},addEventListener:(k,fn)=>listeners[k]=fn,dispatchEvent(){},CustomEvent:class{constructor(type,o){this.type=type;this.detail=o.detail;}}};win.parent=win;if(api)win.API=api;
 const c=vm.createContext({window:win,TextEncoder,TextDecoder,btoa,atob,Intl,Date,Map,Set,JSON,console});
 vm.runInContext(code('data-defaults.js'),c);vm.runInContext(code('data-config.js'),c);c.BioCasaDataConfig=JSON.parse(JSON.stringify(c.BioCasaDataConfig));if(change)change(c.BioCasaDataConfig);
 for(const f of ['dataset.js','engine.js','composer.js','didactics.js','course-config.js','release.js','inventory-cases.js','later-lessons.js','learning.js','tutorials.js','drafts.js','booking-checks.js','storage.js'])vm.runInContext(code(f),c);
 return {c,B:c.BioCasa,D:c.BioCasaData,L:c.BioCasaLearning,I:c.BioCasaInventur,T:c.BioCasaTutorials,win,local};
}
const plain=x=>JSON.parse(JSON.stringify(x));
test('Klasse-11-Datensatz übernimmt die belegten MD-Eröffnungswerte und zeigt zusätzliche Annahmen mit Rechenweg',()=>{
 const {B,D,c}=model(),opening=B.snapshot(B.newState(false));assert.equal(opening.assets,85250000);assert.equal(opening.liabilities,49000000);assert.equal(opening.equity,36250000);assert.equal(B.byId['280'].opening,16039000);assert.equal(B.byId['300'].opening,5000000);assert.equal(B.byId['310'].opening,31250000);assert.equal(D.legacyCompatible,true);assert.equal(D.current.grade,11);assert.equal(D.current.demoEntries.filter(e=>e.origin==='md').length,8);assert.equal(c.BioCasaDidactics.RECEIPTS.length,9);assert.ok(D.current.assumptions.some(a=>a.basis.includes('300 × 0,40')));assert.ok(D.current.bookReferences.inventory[0].pages.includes('196'));assert.ok(D.current.bookReferences.accrual[0].pages.includes('302'));
 assert.deepEqual(plain(B.snapshot(B.newState())),plain(BioCasa.snapshot(BioCasa.newState())));
});
test('Neues Schuljahr ändert Falljahr, Belege, Inventurnachweise, Inventar und Bilanz aus derselben Basis',()=>{
 const {B,D,I,c}=model(d=>{d.caseYear=2027;d.schoolYear='2027/28';for(const e of [...d.demoEntries,...d.receipts])e.date='2027'+e.date.slice(4);d.openingBalances['280']+=1000;d.openingBalances['310']+=1000;});
 assert.equal(B.PERIOD.year,2027);assert.equal(B.dateOK('2027-11-15'),true);assert.equal(B.dateOK('2026-11-15'),false);assert.equal(B.SEED[0].date,'2027-10-02');assert.equal(c.BioCasaDidactics.RECEIPTS[0].date,'2027-12-31');assert.ok(I.byId.documents.story.includes('161.390'));assert.equal(I.check('documents',{method:'documents',bank:'161390',loan:'490000',creditLine:'exclude'}).ok,true);assert.equal(I.check('documents',{method:'documents',bank:'160390',loan:'490000',creditLine:'exclude'}).ok,false);
 const answers=Object.fromEntries(c.BioCasaDidactics.POSITIONS.map(r=>[r.field,r.kind])),inv=c.BioCasaDidactics.inventoryModel(answers);assert.equal(inv.assets,85350000);assert.equal(inv.equity,36350000);assert.equal(D.legacyCompatible,false);assert.equal(B.pack(B.newState()).h,D.identity);
});
test('Anfängliche Vorratsmengen werden mit Finanzwerten abgeglichen und erscheinen im Inventar nicht doppelt',()=>{
 const {B,c}=model(d=>{d.products[0].opening=100;d.openingBalances['200']=400;d.openingBalances['280']-=400;});const m=c.BioCasaDidactics.inventoryModel();assert.equal(m.rows.filter(r=>r.id==='200').length,1);assert.equal(B.snapshot(B.newState(false)).quantities['BC-R01'],100);assert.equal(B.snapshot(B.newState(false)).balances['200'],40000);
});
test('Geänderte Belegbeträge stehen auch im betrieblichen Tutorial; Antwortkennungen bleiben stabil',()=>{
 const {B,T}=model(d=>{d.demoEntries[12].lines=[['605',700,0],['260',133,0],['280',0,833]];});const c=T.info(B.SEED[12]);assert.ok(c.story.includes('833 €'));assert.ok(c.story.includes('700 €'));assert.ok(c.choices.some(([value,label])=>value==='600'&&label==='700 €'));assert.equal(c.answer,'600');
});
test('Uploads mit falscher Bilanz, Salden, Daten, Preisen oder HTML werden abgewiesen',()=>{
 const {D,B}=model();const invalid=[d=>{d.openingBalances['280']++;},d=>{d.openingBalances['999']=0;},d=>{d.openingBalances['076']=100;d.openingBalances['280']+=19900;},d=>{d.demoEntries[0].lines[0][1]++;},d=>{d.demoEntries[0].date='2026-02-31';},d=>{d.products[0].cost=5;},d=>{d.receipts[0].total++;},d=>{d.label='<img src=x>';},d=>{d.bookReferences.inventory[0].pages='irgendwo';},d=>{d.schoolYear='2027/28';},d=>{d.demoEntries[0].lines=[['280',8000,0],['425',0,8000]];}];for(const change of invalid){const d=D.clone(D.current);change(d);assert.throws(()=>D.validate(d,B.ACCOUNTS,B.PRODUCTS));}
});
test('Gleiche Datenbasis nimmt alte Stände wieder auf; anderes Schuljahr und neue Salden werden nicht vermischt',()=>{
 const a=model(),state=a.B.pack(a.B.newState()),old=plain(state);delete old.h;assert.equal(a.B.unpack(old).seed,true);const b=model(d=>{d.openingBalances['280']+=100;d.openingBalances['310']+=100;});assert.throws(()=>b.B.unpack(state),/andere.*Datenbasis/);assert.throws(()=>b.B.unpack(old),/andere.*Datenbasis/);
 const ref=model(d=>{d.source.bookEdition='Neue schulische Ausgabe';d.bookReferences.inventory[0].pages='200–201';});assert.equal(ref.D.identity,a.D.identity);assert.equal(ref.B.unpack(state).seed,true);
});
test('Moodle schützt einen nicht passenden bisherigen Versuch vor automatischem Überschreiben',()=>{
 const old=model(),encoded=old.c.BioCasaStorage.compress(JSON.stringify(old.B.pack(old.B.newState()))),data={'cmi.suspend_data':encoded};const api={LMSInitialize:()=> 'true',LMSGetValue:k=>data[k]||'',LMSSetValue(k,v){data[k]=v;return 'true';},LMSCommit:()=> 'true'};
 const x=model(d=>{d.openingBalances['280']+=100;d.openingBalances['310']+=100;},{api}),s=x.c.BioCasaStorage.createStorage(x.win);const state=s.load();assert.equal(s.status.kind,'error');assert.ok(s.status.detail.includes('anderen Datenbasis'));assert.throws(()=>s.save(state));assert.equal(data['cmi.suspend_data'],encoded);
});
test('Lehrkräfte-Datensatz wird nur in der Vorschau verwendet; der Schülerstart behält die Paketbasis',()=>{
 const a=model(),d=a.D.shiftYear(a.D.current,2027),local=new Map([['biocasa-os:teacher-dataset',JSON.stringify(d)]]);assert.equal(model(null,{preview:true,local}).B.PERIOD.year,2027);assert.equal(model(null,{local}).B.PERIOD.year,2026);
});
test('Alle Lernschritte, 18 Checks und neun eigene Belege passen mit Datenkennung in den SCORM-Speicher',()=>{
 const {B,c}=model();let s=B.unpack(BioCasa.pack(builderComplete()));const K=c.BioCasaChecks,lines=c.BioCasaDidactics.receiptLines('deposit');for(const topic of K.TOPICS)for(let i=0;i<3;i++)s=K.record(s,{key:topic+i,topic,lines},{accounts:'0',balance:'0',change:'0',posting:'0'}).state;for(const r of c.BioCasaDidactics.RECEIPTS)s=B.post(s,{date:r.date,text:r.entryText,reference:r.reference,lines:c.BioCasaDidactics.receiptLines(r.id)}).state;const encoded=c.BioCasaStorage.compress(JSON.stringify(B.pack(s)));assert.ok(encoded.length<=4096,encoded.length);assert.equal(B.unpack(JSON.parse(c.BioCasaStorage.decompress(encoded))).entries.length,9);
});
