import test from 'node:test';
import assert from 'node:assert/strict';
import {builderComplete} from './fixtures/learning.mjs';
import '../dist/booking-checks.js';
import '../dist/drafts.js';
import '../dist/storage.js';
const B=BioCasa,K=BioCasaChecks,D=BioCasaDidactics;
const correct={accounts:'0',balance:'0',change:'0',posting:'0'};
const context=(key,topic='accounts',lines=D.receiptLines('deposit'))=>({key,topic,lines});
test('Vier sprachlich klare Single-Choice-Fragen haben genau eine richtige Aussage und wechselnde Positionen',()=>{
 const questions=K.questions(context('one'));assert.equal(questions.length,4);for(const q of questions){assert.equal(q.options.length,3);assert.equal(new Set(q.options.map(o=>o.label)).size,3);assert.equal(q.options.filter(o=>o.value==='0').length,1);}assert.ok(questions.some(q=>q.options[0].value!=='0'));assert.equal(K.check(context('one'),correct).ok,true);for(const id of Object.keys(correct))assert.equal(K.check(context('one'),{...correct,[id]:'1'}).ok,false);
});
test('Mehrung/Minderung und Bilanzseite folgen der Kontoart, auch bei Aufwand, Steuern und Korrekturen',()=>{
 const cases=[['rent','income','670 · Mieten, Pachten → Mehrung'],['truck','tax','260 · Vorsteuer'],['sale','income','GuV → Eigenkapital auf der Passivseite']];
 for(const [id,topic,term] of cases){const c=context(id,topic,D.receiptLines(id));assert.ok(K.questions(c).some(q=>q.correct.includes(term)));assert.equal(K.topic(c.lines),topic);}
 const ret=context('return','returns',[B.L('5000',20000),B.L('480',3800),B.L('240',0,23800)]);assert.equal(K.topic(ret.lines),'returns');assert.ok(K.questions(ret).find(q=>q.id==='change').correct.includes(B.byId['5000'].name+' → Minderung'));
});
test('Erste drei Buchungen je Thema werden geprüft; Wiederholung zählt nicht doppelt und ein neues Thema startet neu',()=>{
 let s=B.newState();for(let n=1;n<=3;n++){const c=context('case-'+n);assert.equal(K.status(s,c).ordinal,n);assert.equal(K.status(s,c).required,true);s=K.record(s,c,correct).state;assert.equal(K.status(s,c).required,false);s=K.record(s,c,correct).state;assert.equal(s.bookingChecks.length,n);}
 assert.equal(K.status(s,context('case-4')).required,false);assert.equal(K.status(s,context('rent','income',D.receiptLines('rent'))).required,true);
 const changed=context('case-1','accounts',[B.L('280',10000),B.L('288',0,10000)]);assert.equal(K.status(s,changed).required,true);assert.equal(K.record(s,changed,correct).state.bookingChecks.length,3);assert.equal(s.entries.length,0);assert.equal(s.learning,null);
});
test('Falsche Antworten oder eine unpassende Kontierung erzeugen keinen Nachweis und keine Buchung',()=>{
 const s=B.newState(),c={...context('case'),expected:D.receiptLines('furniture')};assert.equal(K.record(s,c,correct).state,null);assert.equal(K.record(s,context('case'),{...correct,posting:'2'}).state,null);assert.equal(s.bookingChecks,undefined);assert.equal(s.entries.length,0);
});
test('Nachweise überstehen SCORM und Import, bleiben begrenzt und passen mit allen Lernschritten in den Speicher',()=>{
 let s=builderComplete();for(const topic of K.TOPICS)for(let i=0;i<3;i++)s=K.record(s,context(topic+i,topic),correct).state;
 for(const c of D.RECEIPTS)s=B.post(s,{date:c.date,reference:c.reference,text:c.entryText,lines:D.receiptLines(c.id)}).state;
 const packed=B.pack(s),copy=B.unpack(packed);assert.deepEqual(copy.bookingChecks,s.bookingChecks);assert.equal(copy.bookingChecks.length,18);assert.equal(BioCasaLearning.progress(copy).stage,9);const compressed=BioCasaStorage.compress(JSON.stringify(packed));assert.ok(compressed.length<=4096,compressed.length);assert.deepEqual(B.unpack(JSON.parse(BioCasaStorage.decompress(compressed))).bookingChecks,s.bookingChecks);
 assert.throws(()=>K.validate([...s.bookingChecks,s.bookingChecks[0]]));assert.throws(()=>K.validate([[99,'abc','def']]));assert.throws(()=>B.unpack({...packed,q:[[0,'<img>','x']]}));
});
