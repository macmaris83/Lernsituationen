import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {answers,inventoryAnswers,inventoryDone,foundations,complete} from './fixtures/learning.mjs';
import '../dist/drafts.js';
import '../dist/package-writer.js';
const B=BioCasa,L=BioCasaLearning,R=BioCasaRelease;
function policy(mode,opensAt=null){globalThis.BioCasaCourseConfig={version:1,inventar:{mode,opensAt}};}
test('Alle fünf Inventuraufgaben sind notwendig; vier richtige Fälle öffnen das Inventar nicht',()=>{
 let s=B.newState();for(const id of ['flour','documents','pizza','cutoff'])s=L.recordInventory(s,id,inventoryAnswers[id]).state;assert.equal(L.progress(s).inventory.done,4);assert.equal(L.progress(s).steps[1].unlocked,false);assert.throws(()=>L.record(s,'inventar',answers.inventar),/vorherigen/);assert.equal(L.recordInventory(s,'permanent',{...inventoryAnswers.permanent,physicalCheck:'omit'}).state,null);s=L.recordInventory(s,'permanent',inventoryAnswers.permanent).state;assert.equal(L.progress(s).steps[1].unlocked,true);
});
test('Permanente Inventur behält die körperliche Kontrolle bei und wird von der Aufnahmeart unterschieden',()=>{
 for(const field of ['physicalCheck','axes']){const a={...inventoryAnswers.permanent,[field]:'wrong'};assert.equal(BioCasaInventur.check('permanent',a).ok,false);}assert.equal(BioCasaInventur.check('permanent',{...inventoryAnswers.permanent,quantity:'730'}).ok,true);
});
test('Lehrkraft-Sperre ist eine zusätzliche Voraussetzung und wird durch gespeicherte Lösungen nicht aufgehoben',()=>{
 const s=complete();try{policy('hold');const p=L.progress(s);assert.equal(p.inventory.done,5);assert.equal(p.stage,1);assert.equal(p.steps[1].unlocked,false);assert.equal(L.canOpen(s,'booking'),false);const packed=B.pack(s);packed.release={mode:'automatic'};packed.p.release={mode:'automatic'};const imported=B.unpack(packed);assert.equal(L.progress(imported).stage,1);assert.throws(()=>L.record(imported,'inventar',answers.inventar),/Freigabe/);}finally{policy('automatic');}
});
test('Terminierte Freigabe wird erst ab dem Zeitpunkt und nur bei fünf richtigen Aufgaben wirksam',()=>{
 const t=Date.parse('2026-11-02T07:00:00Z');try{policy('date',new Date(t).toISOString());const s=inventoryDone();assert.equal(L.progress(s,t-1).steps[1].unlocked,false);assert.equal(L.progress(s,t).steps[1].unlocked,true);assert.equal(L.progress(B.newState(),t+1).steps[1].unlocked,false);}finally{policy('automatic');}
});
test('Alte Mehl-Nachweise bleiben als einer von fünf Fällen erhalten; Journal und Zahlen bleiben unverändert',()=>{
 const s=B.newState();s.learning={answers:{inventory:answers.inventory},cases:[]};const before=B.snapshot(s),restored=B.unpack(B.pack(s));assert.equal(L.progress(restored).inventory.done,1);assert.equal(L.progress(restored).stage,0);assert.deepEqual(B.snapshot(restored),before);
});
test('Unfertige zusätzliche Inventurfälle bleiben Entwürfe und überstehen Export und Import',()=>{
 const s=B.newState();s.drafts=BioCasaDrafts.validate({inventoryCase:'permanent',inventoryCases:{permanent:{quantity:'73',timing:'permanent'}}});const result=B.unpack(B.pack(s));assert.deepEqual(result.drafts,s.drafts);assert.equal(L.progress(result).inventory.done,0);
});
test('Inventar nutzt nur einfache Zuordnungen und ergänzt die späteren Werte ohne Änderung des Datenkranzes',()=>{
 const s=inventoryDone(),result=L.record(s,'inventar',answers.inventar).state;assert.equal(L.deferredValue,18511000);assert.equal(result.learning.answers.inventar.assets,'852500');assert.equal(result.learning.answers.inventar.vat,undefined);assert.equal(result.learning.answers.inventar.prepaid,undefined);assert.deepEqual(B.snapshot(result),B.snapshot(s));assert.equal(L.record(s,'inventar',{...answers.inventar,basicAssets:'852500'}).state,null);
});
test('Steuerkonten und ARA/PRA folgen der neuen Lernreihenfolge',()=>{
 let s=foundations();assert.equal(L.accountAvailable(s,'260'),false);assert.equal(L.accountAvailable(s,'290'),false);s=L.record(s,'income',answers.income).state;assert.equal(L.accountAvailable(s,'260'),true);assert.equal(L.accountAvailable(s,'290'),false);for(const id of ['tax','further','returns'])s=L.record(s,id,answers[id]).state;assert.equal(L.accountAvailable(s,'290'),true);assert.equal(L.accountAvailable(s,'490'),true);assert.equal(L.progress(s).complete,false);s=L.record(s,'accrual',answers.accrual).state;assert.equal(L.progress(s).complete,true);
});
test('Terminwerkzeug rechnet Sommer-/Winterzeit in Berlin und weist ungültige Termine zurück',()=>{
 assert.equal(R.berlinInputToISO('2026-01-15T10:00'),'2026-01-15T09:00:00.000Z');assert.equal(R.berlinInputToISO('2026-06-15T10:00'),'2026-06-15T08:00:00.000Z');assert.throws(()=>R.berlinInputToISO('2026-02-31T10:00'));assert.throws(()=>R.berlinInputToISO('2026-03-29T02:30'));assert.throws(()=>R.validate({version:1,inventar:{mode:'date',opensAt:'wrong'}}));const c={version:1,inventar:{mode:'hold',opensAt:null}},context=vm.createContext({});vm.runInContext(R.source(c),context);assert.equal(context.BioCasaCourseConfig.inventar.mode,'hold');
});
test('Paket-Writer erzeugt überprüfbare ZIP-Dateien mit UTF-8-Inhalten und konfigurierter Freigabe',()=>{
 const zip=BioCasaPackage.zip([{name:'imsmanifest.xml',data:'<manifest/>'},{name:'course-config.js',data:R.source({version:1,inventar:{mode:'hold'}})},{name:'text.txt',data:'Grüße aus Aurich'}]);assert.equal(new DataView(zip.buffer).getUint32(0,true),0x04034b50);assert.equal(BioCasaPackage.crc(new TextEncoder().encode('123456789')),0xcbf43926);assert.throws(()=>BioCasaPackage.zip([{name:'../wrong',data:'x'}]));
});
