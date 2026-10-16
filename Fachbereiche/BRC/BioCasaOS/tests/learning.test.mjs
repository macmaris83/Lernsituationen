import test from 'node:test';
import assert from 'node:assert/strict';
import {answers,foundations,inventoryDone,inventoryAnswers,complete} from './fixtures/learning.mjs';
import '../dist/composer.js';
import '../dist/tutorials.js';
import '../dist/drafts.js';
import '../dist/curriculum.js';
const B=BioCasa,L=BioCasaLearning,C=BioCasaComposer,T=BioCasaTutorials;
test('Vier Grundlagen öffnen die Bereiche nur nach fachlich richtigen Antworten in Reihenfolge',()=>{
 let s=B.newState();assert.equal(L.progress(s).stage,0);assert.equal(L.canOpen(s,'reports'),false);assert.equal(L.canOpen(s,'booking'),false);assert.throws(()=>L.record(s,'balance',answers.balance),/vorherigen/);
 const wrong=L.record(s,'inventory',{...answers.inventory,quantity:'1012,5'});assert.equal(wrong.state,null);assert.ok(wrong.result.wrong.some(x=>x.field==='quantity'));
 s=L.record(s,'inventory',answers.inventory).state;assert.equal(L.progress(s).stage,0);assert.equal(L.progress(s).inventory.done,1);s=inventoryDone(s);assert.equal(L.progress(s).stage,1);assert.equal(L.canOpen(s,'reports'),false);
 s=L.record(s,'inventar',answers.inventar).state;assert.equal(L.canOpen(s,'reports'),true);assert.equal(L.canOpen(s,'stock'),false);
 s=L.record(s,'balance',answers.balance).state;assert.equal(L.canOpen(s,'booking'),false);s=L.record(s,'accounts',answers.accounts).state;
 assert.equal(L.progress(s).stage,4);for(const v of ['booking','stock','control'])assert.equal(L.canOpen(s,v),true);assert.equal(L.progress(s).complete,false);
});
test('Lernnachweise verändern weder Buchhaltung noch Lager; gleicher Datenkranz bleibt erhalten',()=>{
 const s=B.newState(),initial=B.snapshot(s),learned=foundations(s);assert.deepEqual(B.snapshot(learned),initial);assert.equal(learned.entries.length,0);
});
test('Falsche importierte Nachweise und nur richtig ausgefüllte Entwürfe entsperren nichts',()=>{
 const s=B.newState();s.drafts={learning:answers};assert.equal(L.progress(s).stage,0);s.learning={answers:structuredClone(answers),cases:[]};s.learning.answers.inventory.quantity='1';assert.equal(L.progress(s).stage,0);assert.equal(L.canOpen(s,'booking'),false);
 const packed=B.pack(foundations());packed.p.answers.balance.leftTotal='abc';const restored=B.unpack(packed);assert.equal(L.progress(restored).stage,2);
});
test('Belegbuchung ist integriert; nach Bestandskonten folgen Erfolg, Steuer, weitere Buchungen, Retouren und Abgrenzung',()=>{
 const s=foundations();assert.deepEqual(L.STEPS.map(x=>x.id),['inventory','inventar','balance','accounts','income','tax','further','returns','accrual']);const p=B.post(s,{date:B.PERIOD.end,text:'Einzahlung aus Kasse',reference:'BE',lines:[B.L('280',20000),B.L('288',0,20000)],task:'bank'});assert.equal(L.progress(p.state).done,4);assert.equal(L.progress(p.state).complete,false);assert.equal(L.progress(complete(p.state)).done,9);assert.equal(L.progress(complete()).complete,true);
});
test('Komponist erzwingt Soll an Haben auch bei zusammengesetztem Kühltransporter-Kauf',()=>{
 const rows=[{side:'credit',account:'280',amount:'47600'},{side:'debit',account:'084',amount:'40000'},{side:'debit',account:'260',amount:'7600'}],before=JSON.stringify(rows),lines=C.toLines(rows);assert.deepEqual(lines.map(x=>x.account),['084','260','280']);assert.equal(JSON.stringify(rows),before);const state=B.post(B.newState(false),{date:B.PERIOD.end,text:'Kühltransporter',reference:'KFZ',lines}).state;assert.equal(B.snapshot(state).balances['084'],10800000);assert.equal(B.snapshot(state).profit,0);
 assert.throws(()=>C.toLines([{side:'credit',account:'280',amount:'200'}]),/Sollkonto/);assert.throws(()=>C.toLines([{side:'other'}]),/fest/);
});
test('Darstellungsreihenfolge lässt die Original- und Stornobuchung unverändert',()=>{
 const s=foundations(),p=B.post(s,{date:B.PERIOD.end,text:'Einzahlung',reference:'B',lines:[B.L('280',20000),B.L('288',0,20000)]}),r=B.reverse(p.state,p.entry.id),before=B.pack(r.state);const sorted=C.orderedLines(r.entry.lines);assert.equal(sorted[0].account,'288');assert.deepEqual(B.pack(r.state),before);assert.equal(B.checkState(B.unpack(before)),true);
});
test('Alle 15 Seed-Belege haben betrieblichen Kontext, Konten-Zuordnung und geprüften Lerncheck',()=>{
 let s=foundations();assert.equal(T.CASES.length,15);for(const e of B.journal(s)){const t=T.info(e);assert.ok(t.story.length>60);for(const line of e.lines)assert.ok(t.parts[line.account],e.id+': '+line.account);assert.equal(T.recordCase(s,e.id,'wrong').state,null);s=T.recordCase(s,e.id,t.answer).state;}
 assert.equal(L.progress(s).cases,15);s=T.recordCase(s,1,T.CASES[0].answer).state;assert.equal(L.progress(s).cases,15);assert.throws(()=>T.recordCase(B.newState(),1,T.CASES[0].answer),/Grundlagen/);
});
test('Unfertige Formulare, Datum und Kontext überstehen einen Export ohne Buchung oder Freigabe',()=>{
 const s=B.newState();s.savedAt='2026-10-15T11:00:00.000Z';s.importedAt='2026-10-15T10:00:00.000Z';s.drafts=BioCasaDrafts.validate({learning:{inventory:{quantity:'962,'}},book:{date:'2026-12-31',reference:'angefangen',text:'Kühltransporter',bankGuess:'',balanceGuess:'',lines:[{side:'debit',account:'084',amount:'40000,'},{side:'credit',account:'280',amount:''}]},reflection:'Noch unfertig',activeTask:'bank',bookingTab:'draft'});const restored=B.unpack(B.pack(s));assert.deepEqual(restored,s);assert.equal(L.progress(restored).stage,0);assert.equal(B.journal(restored).length,15);assert.equal(restored.drafts.book.lines[0].amount,'40000,');
});
test('Ungültige Eingabedateien werden vor der Übernahme verworfen; alte Version-1-Stände bleiben lesbar',()=>{
 const p=B.pack(B.newState());p.d={learning:{unknown:{foo:'bar'}}};assert.throws(()=>B.unpack(p),/Ungültige/);p.d={book:{date:'2026-12-31',text:'X',reference:'',bankGuess:'',balanceGuess:'',lines:[{side:'sideways',account:'280',amount:'1'},{side:'credit',account:'288',amount:'1'}]}};assert.throws(()=>B.unpack(p),/Ungültige/);delete p.d;delete p.p;delete p.t;delete p.u;assert.equal(B.unpack(p).seed,true);assert.equal(L.progress(B.unpack(p)).stage,0);
});
test('Neun Moodle-Lernpakete sind mit Materialien und getrennten Fenstern korrekt zugeordnet',()=>{
 assert.equal(BioCasaCurriculum.length,9);assert.deepEqual(BioCasaCurriculum.map(x=>x.materials.length),[6,7,6,5,6,5,6,6,6]);assert.match(BioCasaCurriculum[1].goal,/G1–G8/);assert.match(BioCasaCurriculum[7].status,/nicht zusätzlich/);assert.equal(JSON.stringify(BioCasaCurriculum).includes('erwartungshorizont.html'),false);
});
