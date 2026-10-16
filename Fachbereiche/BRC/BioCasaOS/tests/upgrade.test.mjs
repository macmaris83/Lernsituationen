import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

test('Versionswechsel übernimmt einen mit 0.10 erzeugten Moodle-Stand samt Nachweisen, Buchungen und unfertigen Eingaben',()=>{
 const fixture=JSON.parse(fs.readFileSync(new URL('./fixtures/upgrade-0.10.json',import.meta.url),'utf8'));
 const c=vm.createContext({TextEncoder,TextDecoder,btoa,atob,Intl,Date,Map,Set,JSON,console});
 for(const file of ['data-defaults.js','data-config.js','dataset.js','engine.js','composer.js','didactics.js','course-config.js','release.js','inventory-cases.js','later-lessons.js','learning.js','drafts.js','booking-checks.js','accounts.js','storage.js'])vm.runInContext(fs.readFileSync(new URL('../dist/'+file,import.meta.url),'utf8'),c);
 const data={'cmi.suspend_data':fixture.suspendData,'cmi.core.student_id':'synthetic-upgrade-test','cmi.core.lesson_mode':'normal'},writes=[],local=new Map();
 const w={API:{LMSInitialize:()=> 'true',LMSGetValue:k=>data[k]||'',LMSSetValue:(k,v)=>{writes.push(k);data[k]=v;return 'true';},LMSCommit:()=> 'true',LMSFinish:()=> 'true'},location:{pathname:'/same-scorm-activity/index.html'},localStorage:{getItem:k=>local.get(k)||null,setItem:(k,v)=>local.set(k,v)},addEventListener(){},dispatchEvent(){},CustomEvent:class{}};
 w.parent=w;
 const storage=c.BioCasaStorage.createStorage(w),state=storage.load(),plain=x=>JSON.parse(JSON.stringify(x));
 assert.equal(writes.length,0,'Wiederaufnahme darf den alten Stand nicht überschreiben');
 assert.deepEqual(plain(c.BioCasa.pack(state)),fixture.packed);
 assert.deepEqual(plain(c.BioCasa.snapshot(state)),fixture.snapshot);
 assert.equal(c.BioCasaLearning.progress(state).done,fixture.done);
 assert.equal(state.drafts.book.lines[0].amount,'200,');
 assert.equal(state.drafts.inventoryCases.permanent.quantity,'73');
 assert.deepEqual(plain(state.drafts.focus),[62,1,1,1,6]);
 storage.save(state);
 assert.deepEqual(JSON.parse(c.BioCasaStorage.decompress(data['cmi.suspend_data'])),fixture.packed);
 assert.ok(data['cmi.suspend_data'].length<=4096);
});
