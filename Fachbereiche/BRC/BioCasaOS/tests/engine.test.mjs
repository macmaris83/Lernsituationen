import test from 'node:test';
import assert from 'node:assert/strict';
import '../dist/engine.js';
import '../dist/storage.js';
const B=globalThis.BioCasa;
const draft=(lines,text='Übung')=>({date:B.PERIOD.end,text,reference:'TEST',lines});
test('Eröffnungswerte entsprechen LS01: Vermögen 852500, Stammkapital 50000, Rücklage 312500, Darlehen 490000',()=>{
 const s=B.snapshot(B.newState(false));assert.equal(s.assets,85250000);assert.equal(s.equity,36250000);assert.equal(s.balances['300'],5000000);assert.equal(s.balances['310'],31250000);assert.equal(s.balances['425'],49000000);assert.equal(s.cash,16039000);assert.equal(s.stock,0);assert.equal(s.assets,s.passives);
});
test('OS-Demostand ist centgenau konsistent: Roh-/Hilfsstoffe, GuV und Bilanz',()=>{
 const s=B.newState();assert.equal(B.checkState(s),true);const m=B.metrics(s);assert.equal(m.stock,500000);assert.equal(m.cogs,400000);assert.equal(m.revenue,2500000);assert.equal(m.profit,530000);assert.equal(m.ebit,550000);assert.equal(m.ebitda,650000);assert.equal(m.assets,m.passives);
});
test('Bank 200 im Soll an Kasse: Bank steigt, Kasse sinkt, Bilanzsumme und Erfolg unverändert',()=>{
 const s=B.newState(),x=B.snapshot(s),e=B.effect(s,draft([B.L('280',20000),B.L('288',0,20000)]));assert.equal(e.after.balances['280']-x.balances['280'],20000);assert.equal(e.after.balances['288']-x.balances['288'],-20000);assert.equal(e.after.assets,x.assets);assert.equal(e.after.profit,x.profit);assert.deepEqual(s,B.newState());
});
test('Ertrag erhöht Gesamt-Eigenkapital, nicht Stammkapital oder Kapitalrücklage',()=>{
 const s=B.newState(false),x=B.snapshot(s),p=B.post(s,draft([B.L('280',20000),B.L('5000',0,20000)])),y=B.snapshot(p.state);assert.equal(y.assets-x.assets,20000);assert.equal(y.equity-x.equity,20000);assert.equal(y.balances['300'],x.balances['300']);assert.equal(y.balances['310'],x.balances['310']);
});
test('Ausgeglichene Mehrzeilenbuchungen sind erlaubt; fehlerhafte Beträge und Konten werden blockiert',()=>{
 for(const lines of [[B.L('280',20000)],[B.L('280',20000),B.L('288',0,19999)],[B.L('280',-100),B.L('288',0,-100)],[B.L('280',Infinity),B.L('288',0,Infinity)]])assert.throws(()=>B.post(B.newState(),draft(lines)));
 assert.throws(()=>B.post(B.newState(),draft([B.L('200',100),B.L('280',0,100)])),/Lagerbereich/);
});
test('Rohstoffeinkauf mit Steuer aktiviert Vorräte; erst Verbrauch wird Aufwand',()=>{
 let s=B.newState(false),x=B.snapshot(s);s=B.post(s,B.inventoryDraft({productId:'BC-R02',kind:'purchase',qty:200,price:750,tax:7,settlement:'440'})).state;let y=B.snapshot(s);assert.equal(y.stock-x.stock,150000);assert.equal(y.balances['260']-x.balances['260'],10500);assert.equal(y.balances['440'],160500);assert.equal(y.profit,0);
 s=B.post(s,B.inventoryDraft({productId:'BC-R02',kind:'consumption',qty:100,price:750,tax:0})).state;y=B.snapshot(s);assert.equal(y.profit,-75000);assert.equal(y.cogs,75000);assert.equal(y.stock,75000);assert.equal(y.quantities['BC-R02'],100);
});
test('Eigene Erzeugnisse: Bestandsmehrung über 220/5202, Verkauf über Erlös und Forderung',()=>{
 let s=B.newState(false);s=B.post(s,draft([B.L('220',100000),B.L('5202',0,100000)])).state;let x=B.snapshot(s);assert.equal(x.otherRevenue,100000);assert.equal(x.revenue,0);assert.equal(x.profit,100000);
 s=B.post(s,draft([B.L('240',214000),B.L('5000',0,200000),B.L('480',0,14000)])).state;x=B.snapshot(s);assert.equal(x.revenue,200000);assert.equal(x.balances['220'],100000);assert.equal(x.assets,x.passives);
});
test('Storno kehrt Finanz- und Lagerwirkung vollständig um und bleibt sichtbar',()=>{
 const s=B.newState(),before=B.snapshot(s),p=B.post(s,B.inventoryDraft({productId:'BC-R02',kind:'purchase',qty:200,price:750,tax:7})),r=B.reverse(p.state,p.entry.id),after=B.snapshot(r.state);assert.deepEqual(after.balances,before.balances);assert.deepEqual(after.quantities,before.quantities);assert.equal(after.entries.length,before.entries.length+2);assert.throws(()=>B.reverse(r.state,p.entry.id),/erneut/);
});
test('Negative Lager- und Kassenbestände werden auch bei Rückdatierung verhindert',()=>{
 assert.throws(()=>B.post(B.newState(),B.inventoryDraft({productId:'BC-R02',kind:'consumption',qty:1,price:750,tax:0})),/negativen Lagerbestand/);
 assert.throws(()=>B.post(B.newState(),draft([B.L('280',200001),B.L('288',0,200001)])),/reicht/);
});
test('Dreimonatskennzahlen und ROI-Zerlegung verwenden gleiche Bezugsbasis',()=>{
 const m=B.metrics(B.newState());assert.equal(m.storageDays,90/m.turnover);assert.equal(m.averageStock,m.stock/2);assert.ok(Math.abs(m.roi-m.margin*m.capitalTurnover)<1e-12);assert.equal(B.metrics(B.newState(false)).storageDays,null);
});
test('Export/Import und Kompression bewahren Storno, Datum, Umlaute und Emoji',()=>{
 let s=B.newState();const p=B.post(s,draft([B.L('280',20000),B.L('288',0,20000)],'Öl, Grüße & €'));s=B.reverse(p.state,p.entry.id).state;s.reflection='Grüße 👩🏽‍💻 '.repeat(12);assert.deepEqual(B.unpack(B.pack(s)),s);const enc=BioCasaStorage.compress(JSON.stringify(B.pack(s)));assert.equal(BioCasaStorage.decompress(enc),JSON.stringify(B.pack(s)));assert.ok(enc.length<=4096);
});
test('Kompression behandelt Wörterbuchwechsel und beschädigte Daten',()=>{
 const input=Array.from({length:28000},(_,i)=>String.fromCodePoint(32+(i*77+i*i)%1000)).join('');assert.equal(BioCasaStorage.decompress(BioCasaStorage.compress(input)),input);assert.throws(()=>BioCasaStorage.decompress('broken'));assert.throws(()=>BioCasaStorage.decompress('BC1:AA=='));
});
test('Nachweise erfordern fachlich passende Buchung und werden nach Storno aufgehoben',()=>{
 let p=B.post(B.newState(),{...draft([B.L('280',20000),B.L('288',0,20000)]),task:'bank'});assert.equal(B.taskStatus(p.state).bank,true);assert.equal(B.taskStatus(B.reverse(p.state,p.entry.id).state).bank,false);
 const d=B.inventoryDraft({productId:'BC-R02',kind:'purchase',qty:200,price:750,tax:0});p=B.post(B.newState(),{...d,task:'stock'});assert.equal(B.taskStatus(p.state).stock,false);
});
test('Datumsprüfung erlaubt nur gültige Tage des Rumpfgeschäftsjahrs',()=>{
 for(const d of ['2026-11-31','2026-09-30','2026-01-31','2027-01-01'])assert.equal(B.dateOK(d),false);assert.equal(B.dateOK('2026-11-30'),true);
});
