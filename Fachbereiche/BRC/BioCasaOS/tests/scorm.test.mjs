import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import '../dist/engine.js';
import '../dist/didactics.js';
import '../dist/course-config.js';
import '../dist/release.js';
import '../dist/inventory-cases.js';
import '../dist/later-lessons.js';
import '../dist/learning.js';
import '../dist/drafts.js';
import '../dist/storage.js';
import {foundations,complete} from './fixtures/learning.mjs';
const B=BioCasa;
function mock({suspend='',failInit=false,failCommit=false,mode='normal',blockedLocal=false,learner='learner-7',name='Dirks, Maris'}={}){
 const data={'cmi.suspend_data':suspend,'cmi.core.student_id':learner,'cmi.core.student_name':name,'cmi.core.lesson_mode':mode},calls=[],local=new Map(),events={};
 const api={LMSInitialize:()=>failInit?'false':'true',LMSGetValue:k=>data[k]||'',LMSSetValue:(k,v)=>{calls.push(['set',k,v]);data[k]=v;return 'true';},LMSCommit:()=>{calls.push(['commit']);return failCommit?'false':'true';},LMSFinish:()=>{calls.push(['finish']);return 'true';}};
 const w={API:api,location:{pathname:'/mod_scorm/content/17/index.html'},localStorage:{getItem:k=>local.get(k)||null,setItem:(k,v)=>{if(blockedLocal)throw Error('blocked');local.set(k,v);}},CustomEvent:class{constructor(type,o){this.type=type;this.detail=o.detail;}},dispatchEvent(){},addEventListener:(n,f)=>events[n]=f};w.parent=w;return {w,data,calls,local,events};
}
test('SCORM speichert und liest den vollständigen Stand; kein Score wird geschrieben',()=>{
 const m=mock(),s=BioCasaStorage.createStorage(m.w);let state=s.load();state=B.post(state,{date:B.PERIOD.end,text:'Einzahlung',reference:'B1',lines:[B.L('280',20000),B.L('288',0,20000)],task:'bank'}).state;s.save(state);
 assert.equal(s.status.kind,'lms');assert.equal(m.data['cmi.core.lesson_status'],'incomplete');assert.equal(m.data['cmi.core.exit'],'suspend');assert.ok(m.data['cmi.suspend_data'].length<=4096);assert.equal(m.calls.some(c=>c[1]?.includes('score')),false);
 const reopened=BioCasaStorage.createStorage(mock({suspend:m.data['cmi.suspend_data']}).w);assert.deepEqual(reopened.load(),state);
});
test('Ein neuer Moodle-Versuch übernimmt keinen alten lokalen Stand automatisch',()=>{
 const m=mock();m.local.set('biocasa-os-v1:'+m.w.location.pathname+':learner-7:normal',BioCasaStorage.compress(JSON.stringify(B.pack({...B.newState(false),reflection:'Alter Versuch'}))));const s=BioCasaStorage.createStorage(m.w);assert.equal(s.load().seed,true);assert.equal(s.load().reflection,'');
});
test('Moodle speichert ohne Browser-localStorage; Fehler bei Commit werden deutlich gemeldet',()=>{
 const a=mock({blockedLocal:true}),s=BioCasaStorage.createStorage(a.w);s.save(s.load());assert.equal(s.status.kind,'lms');const b=mock({failCommit:true}),t=BioCasaStorage.createStorage(b.w);t.save(t.load());assert.equal(t.status.kind,'error');assert.equal(t.status.text,'Nur lokal gesichert');
});
test('Initialisierungsfehler kann nicht als erfolgreiche Moodle-Speicherung erscheinen',()=>{
 const m=mock({failInit:true}),s=BioCasaStorage.createStorage(m.w);s.save(s.load());assert.equal(s.connected,false);assert.equal(s.status.kind,'error');
});
test('Neun geprüfte Lernschritte setzen abgeschlossen; freiwillige Vertiefungen sind nicht erforderlich',()=>{
 const m=mock(),s=BioCasaStorage.createStorage(m.w);let x=complete(foundations(s.load()));x=B.post(x,{date:B.PERIOD.end,text:'Einzahlung',reference:'B1',lines:[B.L('280',20000),B.L('288',0,20000)],task:'bank'}).state;x=B.post(x,{...B.inventoryDraft({productId:'BC-R02',kind:'purchase',qty:200,price:750,tax:7}),task:'stock'}).state;x.reflection='Eigenständige Auswertung mit Kennzahl und konkretem Wert, Maßnahme und Grenze der Aussage.'.repeat(2);s.save(x);assert.equal(m.data['cmi.core.lesson_status'],'completed');
});
test('Beschädigter Moodle-Stand wird bis zu Import oder bewusstem Reset nicht überschrieben',()=>{
 const m=mock({suspend:'corrupt'}),s=BioCasaStorage.createStorage(m.w);const x=s.load();assert.equal(s.status.kind,'error');assert.throws(()=>s.save(x),/zuerst/);assert.equal(m.data['cmi.suspend_data'],'corrupt');s.save(x,{unlock:true});assert.ok(m.data['cmi.suspend_data'].startsWith('BC1:'));
});
test('Speicherlimit wird vor einer Änderung geprüft und schützt den vorherigen Versuch',()=>{
 const m=mock(),s=BioCasaStorage.createStorage(m.w);let x=s.load();s.save(x);const previous=m.data['cmi.suspend_data'];for(let i=0;i<60;i++)x=B.post(x,{date:B.PERIOD.end,text:createHash('sha512').update('text'+i).digest('hex').slice(0,120),reference:createHash('sha256').update('ref'+i).digest('hex').slice(0,40),lines:[B.L('280',1),B.L('288',0,1)]}).state;
 assert.throws(()=>s.save(x),/Speicher/);assert.equal(m.data['cmi.suspend_data'],previous);
});
test('Review liest den vorherigen Versuch, überschreibt ihn aber nicht',()=>{
 const x=B.newState(false);x.reflection='Vorheriger Versuch';const encoded=BioCasaStorage.compress(JSON.stringify(B.pack(x))),m=mock({suspend:encoded,mode:'review'}),s=BioCasaStorage.createStorage(m.w);const loaded=s.load();assert.equal(loaded.reflection,x.reflection);loaded.reflection='Nur lokal';s.save(loaded);assert.equal(m.data['cmi.suspend_data'],encoded);assert.equal(m.calls.length,0);
});
test('Verschachtelte Moodle-Frames werden erkannt; Session wird genau einmal beendet',()=>{
 const m=mock(),child={parent:m.w};assert.equal(BioCasaStorage.findAPI(child),m.w.API);const s=BioCasaStorage.createStorage(m.w);s.save(s.load());s.finish();s.finish();assert.equal(m.calls.filter(c=>c[0]==='finish').length,1);assert.match(m.data['cmi.core.session_time'],/^\d{4}:\d{2}:\d{2}\.\d{2}$/);
});

test('Vor dem Schließen und bei iPad-Hintergrundwechsel werden auch die letzten Eingaben gesichert',()=>{
 const m=mock();m.w.document={visibilityState:'hidden',addEventListener:(name,fn)=>m.events['doc-'+name]=fn};const s=BioCasaStorage.createStorage(m.w);let x=s.load();s.save(x);s.setBeforeFlush(()=>{x.drafts={learning:{inventory:{quantity:'962,'}}};x.savedAt='2026-10-15T11:30:00.000Z';s.save(x);});m.events['doc-visibilitychange']();const reopened=BioCasaStorage.createStorage(mock({suspend:m.data['cmi.suspend_data']}).w).load();assert.equal(reopened.drafts.learning.inventory.quantity,'962,');assert.equal(reopened.savedAt,x.savedAt);assert.equal(BioCasaLearning.progress(reopened).stage,0);m.events.pagehide({persisted:false});assert.equal(m.calls.filter(c=>c[0]==='finish').length,1);
});
test('Persönliche Zuordnung nutzt das Moodle-Konto; Namen werden nicht in Sicherungen kopiert',()=>{
 const a=mock({learner:'one',name:'Schüler Eins'}),s=BioCasaStorage.createStorage(a.w);s.save(s.load());assert.equal(s.learnerName,'Schüler Eins');assert.equal(JSON.stringify(B.pack(s.load())).includes('Schüler Eins'),false);assert.ok([...a.local.keys()][0].includes(':one:'));const b=mock({learner:'two'}),t=BioCasaStorage.createStorage(b.w);t.save(t.load());assert.ok([...b.local.keys()][0].includes(':two:'));
});
