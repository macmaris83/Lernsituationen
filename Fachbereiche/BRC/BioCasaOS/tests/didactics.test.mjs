import test from 'node:test';
import assert from 'node:assert/strict';
import {answers,builderAnswers,builderComplete,inventoryDone,foundations} from './fixtures/learning.mjs';
import '../dist/drafts.js';
import '../dist/storage.js';
const B=BioCasa,L=BioCasaLearning,D=BioCasaDidactics;
test('Inventarentwurf wird erst mit sämtlichen Zuordnungen vollständig; graue Werte und Nullbestände bleiben enthalten',()=>{
 const empty=D.inventoryModel();assert.equal(empty.complete,false);assert.equal(empty.pending.length,D.POSITIONS.length);
 const m=D.inventoryModel(builderAnswers.inventar);assert.equal(m.complete,true);assert.equal(m.assets,85250000);assert.equal(m.debts,49000000);assert.equal(m.equity,36250000);assert.deepEqual(m.rows.filter(r=>r.deferred).map(r=>r.id),['160','260','290']);assert.equal(m.rows.find(r=>r.id==='288').opening,0);assert.deepEqual(m.groups.map(g=>g.code),['A.I','A.II','A.III','B']);
 const a={...builderAnswers.inventar,i057:'uv'};assert.equal(L.check('inventar',a).ok,false);delete a.i057;assert.equal(D.inventoryModel(a).complete,false);
});
test('Bilanz übernimmt jede Inventarposition genau einmal und setzt das Reinvermögen als Eigenkapital hinzu',()=>{
 const inv=D.inventoryModel(builderAnswers.inventar),m=D.balanceModel(inv,builderAnswers.balance);assert.equal(m.complete,true);assert.equal(m.assets.total,inv.assets);assert.equal(m.passives.total,inv.assets);assert.equal(m.rows.length,inv.rows.length+1);assert.equal(new Set(m.rows.map(r=>r.id)).size,m.rows.length);assert.equal(m.passives.rows.find(r=>r.id==='EK').opening,inv.equity);assert.ok(m.assets.rows.every(r=>r.kind!=='debt'&&r.kind!=='equity'));
 assert.equal(L.check('balance',{...builderAnswers.balance,b057:'passives'}).ok,false);assert.equal(L.check('balance',{...builderAnswers.balance,equitySide:'assets'}).ok,false);const x={...builderAnswers.balance};delete x.b076;assert.equal(L.check('balance',x).ok,false);
});
test('Wiederholte Kontenentscheidungen prüfen jede Kontoart, Veränderung und Seite bei Bestands- und Erfolgskonten',()=>{
 for(const id of ['accounts','income']){assert.equal(L.check(id,builderAnswers[id]).ok,true);for(const field of Object.keys(D.decisionAnswers(id))){const wrong={...builderAnswers[id],[field]:'wrong'};const result=L.check(id,wrong);assert.equal(result.ok,false,id+field);assert.ok(result.wrong.some(w=>w.field===field));}}
 assert.equal(builderAnswers.accounts.r3s,'d');assert.equal(builderAnswers.income.r1f,'e');assert.equal(builderAnswers.income.r3f,'b');assert.equal(builderAnswers.income.r4t,'rev');
});
test('Neue Arbeitsergebnisse und alle Nachweise überstehen SCORM-Speicherung; alte geprüfte Stände behalten ihren Fortschritt',()=>{
 const s=builderComplete();assert.equal(L.progress(s).stage,9);const packed=B.pack(s);assert.ok(JSON.stringify(packed.p).length<=3000);s.drafts=BioCasaDrafts.validate({learning:builderAnswers,book:{receiptId:'truck',date:'2026-12-31',text:'angefangen',reference:'OS-BE-05',bankGuess:'',balanceGuess:'',lines:[{side:'debit',account:'084',amount:'40000,'},{side:'credit',account:'280',amount:''}]}});const raw=BioCasaStorage.compress(JSON.stringify(B.pack(s)));assert.ok(raw.length<=4096,raw.length);assert.deepEqual(B.unpack(JSON.parse(BioCasaStorage.decompress(raw))),s);assert.equal(L.progress(foundations()).stage,4);
});
test('Neue Formularentwürfe bleiben ohne Prüfung gesperrt und schreiben keine Zahlen in das Journal',()=>{
 const s=inventoryDone(),before=B.snapshot(s);s.drafts={learning:builderAnswers};assert.equal(L.progress(s).stage,1);assert.equal(L.canOpen(s,'reports'),false);let x=s;for(const id of ['inventar','balance','accounts'])x=L.record(x,id,builderAnswers[id]).state;assert.deepEqual(B.snapshot(x),before);assert.equal(x.entries.length,0);
});
test('Vier Bilanzsimulationen sind ausgeglichen, richtig bezeichnet und verändern niemals einen Übungsstand',()=>{
 const s=B.newState(),before=B.pack(s),deltas={assetSwap:0,liabilitySwap:0,increase:30000,decrease:-20000};
 for(const c of D.BALANCE_DEMOS){const e=D.balanceDemo(c.id);assert.equal(e.before.assets,e.before.passives);assert.equal(e.after.assets,e.after.passives);assert.equal(e.after.assets-e.before.assets,deltas[c.id]);assert.equal(D.classifyEffect(e).id,c.id);assert.equal(e.after.profit,0);}assert.deepEqual(B.pack(s),before);
});
test('Tatsächliche Buchungen werden einschließlich Erfolgswirkung statt pauschalem Passivtausch eingeordnet',()=>{
 const s=foundations();assert.equal(D.classifyEffect(B.effect(s,{date:B.PERIOD.end,text:'Einzahlung',reference:'',lines:[B.L('280',20000),B.L('288',0,20000)]})).id,'assetSwap');
 const rent=B.effect(s,{date:B.PERIOD.end,text:'Miete',reference:'',lines:[B.L('670',100000),B.L('280',0,100000)]});assert.equal(D.classifyEffect(rent).id,'success');assert.equal(rent.after.equity-rent.before.equity,-100000);
});
test('Fiktive Belege werden fachlich geprüft, nur einmal aktiv gebucht und nach Storno wieder verfügbar',()=>{
 const expected={deposit:[B.L('280',20000),B.L('288',0,20000)],furniture:[B.L('087',120000),B.L('280',0,120000)],rent:[B.L('670',100000),B.L('280',0,100000)],sale:[B.L('240',60000),B.L('5000',0,60000)],truck:[B.L('084',4000000),B.L('260',760000),B.L('280',0,4760000)],energy:[B.L('605',60000),B.L('260',11400),B.L('280',0,71400)]};
 let state=builderComplete();for(const c of D.RECEIPTS){assert.equal(c.lines.reduce((n,r)=>n+r[1],0),c.total);assert.equal(D.checkReceipt(c.id,{lines:expected[c.id]}),true);assert.equal(D.checkReceipt(c.id,{lines:[B.L('280',c.total),B.L('425',0,c.total)]}),false);assert.equal(D.receiptPosted(state,c.id),false);const p=B.post(state,{date:c.date,reference:c.reference,text:c.entryText,lines:expected[c.id]});state=p.state;assert.equal(D.receiptPosted(state,c.id),true);if(c.id==='deposit'){state=B.reverse(state,p.entry.id).state;assert.equal(D.receiptPosted(state,c.id),false);}}
});
test('Unfertige Buchungssätze erzeugen nur eine Vorschau mit den tatsächlich gewählten Konten',()=>{
 const s=foundations(),before=B.pack(s),start=B.snapshot(s);
 const partial=D.previewRows(s,[{account:'280',side:'debit',amount:'200'},{account:'',side:'credit',amount:''}]);assert.equal(partial.balanced,false);assert.equal(partial.pending,1);assert.equal(partial.after.balances['280'],start.balances['280']+20000);assert.equal(partial.changes.length,1);
 const full=D.previewRows(s,[{account:'280',side:'debit',amount:'200'},{account:'288',side:'credit',amount:'200'}]);assert.equal(full.balanced,true);assert.equal(D.classifyEffect(full).id,'assetSwap');assert.equal(full.after.assets,start.assets);assert.deepEqual(B.pack(s),before);
 const wrong=D.previewRows(s,[{account:'280',side:'credit',amount:'200'},{account:'288',side:'debit',amount:'200'}]);assert.equal(wrong.after.balances['280'],start.balances['280']-20000);assert.equal(wrong.after.balances['288'],start.balances['288']+20000);
});
test('Erste Kontenentscheidungen visualisieren eigene Eingaben, ohne eine Musterkontierung einzutragen',()=>{
 const s=foundations(),c=D.DECISIONS.accounts[0];assert.equal(D.previewDecision(s,'accounts',{},c).lines.length,0);
 const a={r1a:'087',r1s:'d',r2a:'288',r2s:'c'},p=D.previewDecision(s,'accounts',a,c);assert.ok(p.changes.some(x=>x.id==='087'));assert.equal(p.changes.some(x=>x.id==='280'),false);assert.equal(p.balanced,true);assert.equal(s.entries.length,0);
});
