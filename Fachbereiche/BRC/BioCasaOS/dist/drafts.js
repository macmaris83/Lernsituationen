/* Unfertige Eingaben sind keine Kompetenznachweise und keine Buchungen. */
(function(root){
'use strict';
const B=root.BioCasa,L=root.BioCasaLearning;
function validate(value){
 if(value==null)return null;
 const fail=()=>{throw Error('Ungültige unfertige Eingaben in der Sicherung.');};
 if(typeof value!=='object'||Array.isArray(value)||JSON.stringify(value).length>12000)fail();
 const obj=x=>{if(!x||typeof x!=='object'||Array.isArray(x))fail();return x;};
 const str=(x,max=40)=>{if(typeof x!=='string'||x.length>max)fail();return x;};
 const choice=(x,choices)=>{if(!choices.includes(x))fail();return x;};
 const result={};
 if(value.focus!=null){const f=value.focus;if(!Array.isArray(f)||f.length!==5||!f.every(Number.isInteger)||f[0]<35||f[0]>65||!f.slice(1,4).every(v=>v===0||v===1)||f[4]<0||f[4]>7)fail();result.focus=[...f];}
 if(value.learning!=null){result.learning={};for(const [id,a] of Object.entries(obj(value.learning))){if(!L.fields[id])fail();result.learning[id]={};for(const [key,v] of Object.entries(obj(a))){if(!L.fields[id].includes(key))fail();result.learning[id][key]=str(v);}}}
 if(value.inventoryCases!=null){result.inventoryCases={};for(const [id,a] of Object.entries(obj(value.inventoryCases))){const c=root.BioCasaInventur.byId[id];if(!c)fail();result.inventoryCases[id]={};for(const [key,v] of Object.entries(obj(a))){if(!c.fields.some(f=>f.name===key))fail();result.inventoryCases[id][key]=str(v);}}}
 if(value.inventoryCase!=null)result.inventoryCase=choice(value.inventoryCase,root.BioCasaInventur.CASES.map(c=>c.id));
 if(value.learningStep!=null)result.learningStep=choice(value.learningStep,root.BioCasaLearning.STEPS.map(c=>c.id));
 if(value.book!=null){const b=obj(value.book);if(!Array.isArray(b.lines)||b.lines.length<2||b.lines.length>16)fail();result.book={date:str(b.date,10),reference:str(b.reference),text:str(b.text,120),bankGuess:choice(b.bankGuess,['','up','down','same']),balanceGuess:choice(b.balanceGuess,['','up','down','same']),lines:b.lines.map(line=>{obj(line);const side=choice(line.side,['debit','credit']),account=str(line.account,5);if(account&&!B.byId[account])fail();return {side,account,amount:str(line.amount)};})};if(!['debit','credit'].every(side=>result.book.lines.some(l=>l.side===side)))fail();if(b.receiptId!=null)result.book.receiptId=choice(b.receiptId,root.BioCasaDidactics.RECEIPTS.map(c=>c.id));}
 if(value.stock!=null){const s=obj(value.stock);result.stock={productId:choice(s.productId,B.PRODUCTS.map(p=>p.id)),kind:choice(s.kind,['purchase','consumption','loss']),qty:str(s.qty),price:str(s.price),tax:choice(s.tax,['0','7','19']),date:str(s.date,10),reference:str(s.reference),text:str(s.text,120),settlement:choice(s.settlement,['440','280','288'])};}
 if(value.sim!=null){const s=obj(value.sim);result.sim={productId:choice(s.productId,['P1','P2','P3']),price:str(s.price),cost:str(s.cost),qty:str(s.qty),fixed:str(s.fixed)};}
 if(value.reflection!=null)result.reflection=str(value.reflection,600);
 for(const [key,choices] of [['activeTask',[null,'bank','stock','analysis']],['bookingTab',['draft','journal']],['reportTab',['balance','income','accounts','lesson-balance','lesson-accounts']],['inventoryTab',['inventory','inventar']]])if(value[key]!==undefined)result[key]=choice(value[key],choices);
 if(value.caseDraft!=null){const c=obj(value.caseDraft);if(!Number.isInteger(c.id)||c.id<1||c.id>15)fail();result.caseDraft={id:c.id,answer:str(c.answer)};}
 return result;
}
root.BioCasaDrafts=Object.freeze({validate});
})(globalThis);
