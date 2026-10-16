/* Feste Lernsystematik: Sollkonten an Habenkonten. Persistierte Buchungen bleiben unverändert. */
(function(root){
'use strict';
const B=root.BioCasa;
const blankLine=side=>({side,account:'',amount:''});
const initialLines=()=>[blankLine('debit'),blankLine('credit')];
function orderedDraft(rows){
 if(!Array.isArray(rows)||rows.some(r=>!r||!['debit','credit'].includes(r.side)))throw Error('Jede Kontenzeile muss fest zu Soll oder Haben gehören.');
 return [...rows.filter(r=>r.side==='debit'),...rows.filter(r=>r.side==='credit')];
}
function toLines(rows){
 const ordered=orderedDraft(rows);
 if(!ordered.some(r=>r.side==='debit')||!ordered.some(r=>r.side==='credit'))throw Error('Mindestens ein Sollkonto und ein Habenkonto sind erforderlich.');
 if(ordered.length>16)throw Error('Eine Buchung darf höchstens 16 Kontenzeilen enthalten.');
 return ordered.map(r=>{const raw=String(r.amount??'').trim(),amount=raw?B.money(raw):0;return B.L(r.account,r.side==='debit'?amount:0,r.side==='credit'?amount:0);});
}
function orderedLines(lines){return [...lines.filter(l=>l.debit>0),...lines.filter(l=>!l.debit)];}
root.BioCasaComposer=Object.freeze({blankLine,initialLines,orderedDraft,toLines,orderedLines});
})(globalThis);
