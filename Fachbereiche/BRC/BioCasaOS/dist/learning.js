/* Lernfortschritt: belegte Antworten statt bloßer Klick-Freischaltungen. */
(function(root){
'use strict';
const B=root.BioCasa,I=root.BioCasaInventur,D=root.BioCasaDidactics;
const STEPS=[
 {id:'inventory',title:'Inventur',subtitle:'Fünf Fälle zu Aufnahmeart und Verfahren lösen',route:'inventory'},
 {id:'inventar',title:'Inventar',subtitle:'Vermögen und Schulden ordnen',route:'inventory'},
 {id:'balance',title:'Bilanz',subtitle:'Mittelverwendung und Mittelherkunft verbinden',route:'reports'},
 {id:'accounts',title:'Bestandskonten',subtitle:'Die Bilanz in Konten auflösen',route:'reports'},
 {id:'income',title:'Erfolgskonten',subtitle:'Aufwendungen, Erträge und Zahlungen unterscheiden',route:'tasks'},
 {id:'tax',title:'Vor- & Umsatzsteuer',subtitle:'Nettowert und Steuer getrennt buchen',route:'tasks'},
 {id:'further',title:'Weitere Buchungen',subtitle:'Anlagen und eigene Erzeugnisse fortschreiben',route:'tasks'},
 {id:'returns',title:'Retouren',subtitle:'Warenrücksendungen und Rechnungskorrekturen verstehen',route:'tasks'},
 {id:'accrual',title:'Zeitliche Erfolgsabgrenzung',subtitle:'ARA und PRA am Jahreswechsel bilden',route:'tasks'}
];
const fields={
 inventory:['quantity','value','method','ownership'],
 inventar:['vehicle','deposit','vat','prepaid','loan','assets','debts','equity'],
 balance:['bankSide','loanSide','leftTotal','rightTotal'],
 accounts:['bankStart','loanStart','bankAmount','loanAmount','assetIncrease','debtIncrease']
};
const newInventarFields=['vehicle','furniture','bank','loan','basicAssets','debts','equity'];
fields.inventar=[...new Set([...fields.inventar,...newInventarFields])];
for(const [id,c] of Object.entries(root.BioCasaLater.LESSONS))fields[id]=c.fields.map(f=>f.name);
fields.inventar.push('schema',...D.POSITIONS.map(a=>a.field));
fields.balance.push('schema','equitySide',...D.POSITIONS.map(a=>a.sideField));
for(const id of ['accounts','income'])fields[id].push('schema',...D.decisionFields(id).map(f=>f.name));
if(root.BioCasaAccounts)fields.accounts.push(...root.BioCasaAccounts.openingAccounts.flatMap(root.BioCasaAccounts.openingKeys),'bankSaldo','bankCloseSide','loanSaldo','loanCloseSide','bankCounter','bankCounterSide','loanCounter','loanCounterSide');
for(const id of Object.keys(fields))fields[id]=[...new Set(fields[id])];
const DEFERRED=['160','260','290'],deferredValue=B.sum(DEFERRED,id=>B.byId[id].opening);
function empty(){return {answers:{},cases:[],inventoryCases:{}};}
function data(state){return state.learning||empty();}
function stateForPractice(){return B.newState(false);}
function check(id,a={}){
 if(root.BioCasaLater.LESSONS[id])return root.BioCasaLater.check(id,a);
 if(id==='inventory')return I.check('flour',a);
 const initial=B.snapshot(B.newState(false),B.PERIOD.previous);
 const money=(name,target)=>{try{return B.money(a[name])===target;}catch{return false;}};
 let criteria;
 if(id==='inventar')criteria=[['vehicle',a.vehicle==='av','Der Kühltransporter dient BioCasa längerfristig.'],['deposit',a.deposit==='av','Die langfristig rückzahlbare Kaution ist ein Vermögensanspruch.'],['vat',a.vat==='uv','Die bestätigte Vorsteuer ist eine Forderung gegenüber dem Finanzamt.'],['prepaid',a.prepaid==='rap','Die Leasingvorauszahlung betrifft künftige Nutzungszeiträume.'],['loan',a.loan==='debt','Das Darlehen begründet eine Rückzahlungsverpflichtung.'],['assets',money('assets',initial.assets),'Addiere die bestätigten Vermögenswerte einschließlich Vorauszahlung.'],['debts',money('debts',initial.liabilities),'Erfasse nur tatsächlich bestehende Schulden, nicht die ungenutzte Kreditlinie.'],['equity',money('equity',initial.equity),'Reinvermögen ist Vermögen abzüglich Schulden.']];
 if(id==='inventar'&&a.basicAssets!==undefined)criteria=[['vehicle',a.vehicle==='av','Der Kühltransporter dient BioCasa längerfristig.'],['furniture',a.furniture==='av','Büromöbel werden längerfristig betrieblich genutzt.'],['bank',a.bank==='uv','Bankguthaben gehört zum kurzfristig verfügbaren Vermögen.'],['loan',a.loan==='debt','Das Darlehen ist eine Rückzahlungsverpflichtung.'],['basicAssets',money('basicAssets',initial.assets-deferredValue),'Addiere nur die aktiven Grundlagenpositionen. Die grauen Positionen ergänzt OS separat.'],['debts',money('debts',initial.liabilities),'Übernimm die bestätigten Schulden.'],['equity',money('equity',initial.equity),'Nutze das vollständige Vermögen einschließlich des vorgegebenen Zusatzbetrags und ziehe die Schulden ab.']];
 if(id==='balance')criteria=[['bankSide',a.bankSide==='assets','Die Bank zeigt, wofür Mittel zur Verfügung stehen.'],['loanSide',a.loanSide==='passives','Die Darlehensschuld erklärt die Herkunft eines Teils der Mittel.'],['leftTotal',money('leftTotal',initial.assets),'Aktiva übernehmen die Summe des Vermögens aus dem Inventar.'],['rightTotal',money('rightTotal',initial.passives),'Passiva setzen sich aus Eigenkapital und Schulden zusammen.']];
 if(id==='accounts')criteria=[['bankStart',a.bankStart==='debit','Bank ist ein Aktivkonto: Anfangsbestand auf der Seite des Vermögens.'],['loanStart',a.loanStart==='credit','Das langfristige Darlehen ist ein Passivkonto.'],['bankAmount',money('bankAmount',initial.balances['280']),'Übernimm nur den tatsächlichen Anfangsbestand des Bankkontos.'],['loanAmount',money('loanAmount',initial.balances['425']),'Übernimm die ausgezahlte Darlehensschuld.'],['assetIncrease',a.assetIncrease==='debit','Ein Aktivkonto nimmt auf derselben Seite zu wie sein Anfangsbestand.'],['debtIncrease',a.debtIncrease==='credit','Ein Passivkonto nimmt auf derselben Seite zu wie sein Anfangsbestand.']];
 if(!criteria)throw Error('Unbekannter Lernschritt.');
 if(id==='accounts'&&['3','4'].includes(a.schema)){const A=root.BioCasaAccounts;for(const row of A.openingAccounts){if(['280','425'].includes(row.id))continue;const [side,value]=A.openingKeys(row);criteria.push([value,money(value,row.opening),'Übernimm den Anfangsbestand für Konto '+row.id+' aus deiner Bilanz.'],[side,a[side]===(row.type==='asset'?'debit':'credit'),'Prüfe die Bilanzseite und die Eröffnungsseite von Konto '+row.id+'.']);}for(const [account,value,side] of [['280','bankSaldo','bankCloseSide'],['425','loanSaldo','loanCloseSide','bankCounter','bankCounterSide','loanCounter','loanCounterSide']]){const m=A.practice(stateForPractice(),account);criteria.push([value,money(value,m.amount),'Addiere Soll und Haben einschließlich Anfangsbestand; ermittle die Differenz.'],[side,a[side]===m.side,'Der Saldo gehört zum Abschluss auf die wertmäßig kleinere Seite.']);}}
 if(id==='accounts'&&a.schema==='4')for(const [account,prefix] of [['280','bank'],['425','loan']]){const target=root.BioCasaAccounts.closing(root.BioCasaAccounts.practice(stateForPractice(),account));criteria.push([prefix+'Counter',a[prefix+'Counter']===target.counter,'Bestandskonten werden über das Schlussbilanzkonto abgeschlossen; Erfolgskonten über die GuV.'],[prefix+'CounterSide',a[prefix+'CounterSide']===target.counterSide,'Die Gegenbuchung steht auf der anderen Kontoseite als der Abschlusseintrag im ursprünglichen Konto.']);}
 if(a.schema==='2'&&id==='inventar')for(const row of D.POSITIONS)if(!['vehicle','furniture','bank','loan'].includes(row.field))criteria.push([row.field,a[row.field]===row.kind,row.name+': Prüfe dauerhafte Nutzung, kurzfristige Verfügbarkeit oder Rückzahlungsverpflichtung.']);
 if(a.schema==='2'&&id==='balance'){
  for(const row of D.POSITIONS)if(!['bankSide','loanSide'].includes(row.sideField))criteria.push([row.sideField,a[row.sideField]===(row.kind==='debt'?'passives':'assets'),row.name+': Übernimm die Position aus dem Inventar auf die passende Bilanzseite.']);
  criteria.push(['equitySide',a.equitySide==='passives','Reinvermögen wird zu Eigenkapital. Prüfe, ob es Verwendung oder Herkunft von Mitteln erklärt.']);
 }
 if(['2','3'].includes(a.schema)&&id==='accounts'){const extra=D.checkDecisions(id,a),wrong=criteria.filter(x=>!x[1]).map(([field,ok,hint])=>({field,hint}));return {ok:!wrong.length&&!extra.wrong.length,correct:criteria.length+extra.total-wrong.length-extra.wrong.length,total:criteria.length+extra.total,wrong:[...wrong,...extra.wrong]};}
 const wrong=criteria.filter(x=>!x[1]);return {ok:wrong.length===0,correct:criteria.length-wrong.length,total:criteria.length,wrong:wrong.map(([field,ok,hint])=>({field,hint}))};
}
function progress(state,now=Date.now()){
 const preview=!!root.BioCasaTeacherPreview?.enabled,answers=data(state).answers||{},inventory=I.progress(data(state)),release=root.BioCasaRelease.status(now);let stage=inventory.complete?1:0;
 if(stage===1&&release.allowed)for(const step of STEPS.slice(1)){if(check(step.id,answers[step.id]).ok)stage++;else break;}
 return {stage,steps:STEPS.map((s,i)=>({...s,done:i<stage,unlocked:preview||i===0||(i<=stage&&(i!==1||release.allowed))})),bank:B.taskStatus(state).bank,complete:stage===STEPS.length,done:stage,total:STEPS.length,cases:(data(state).cases||[]).length,inventory,release};
}
function accessStage(state){return root.BioCasaTeacherPreview?.enabled?STEPS.length:progress(state).stage;}
function canOpen(state,route){if(root.BioCasaTeacherPreview?.enabled)return true;const n=progress(state).stage;if(route==='reports')return n>=2;if(['booking','stock','control'].includes(route))return n>=4;return true;}
function lockReason(state,route){const p=progress(state);if(p.inventory.complete&&!p.release.allowed)return 'Inventar wartet auf die Freigabe der Lehrkraft.';return p.stage<2?'Zuerst fünf Inventurfälle und das Inventar bearbeiten.':p.stage<3?'Zuerst die Bilanzaufgabe lösen.':'Zuerst die Bilanz in Bestandskonten auflösen.';}
function recordInventory(state,id,input){
 const c=I.byId[id];if(!c)throw Error('Unbekannte Inventuraufgabe.');const result=I.check(id,input);if(!result.ok)return {state:null,result};const next=B.clone(state);next.learning=B.clone(data(state));next.learning.inventoryCases=next.learning.inventoryCases||{};const answer=Object.fromEntries(c.fields.map(f=>[f.name,String(input[f.name]??'').slice(0,40)]));if(id==='flour')next.learning.answers.inventory=answer;else next.learning.inventoryCases[id]=answer;next.revision++;return {state:next,result};
}
function record(state,id,input){
 if(id==='inventory')return recordInventory(state,'flour',input);
 const index=STEPS.findIndex(s=>s.id===id);if(index<0)throw Error('Unbekannter Lernschritt.');if(!progress(state).steps[index].unlocked)throw Error('Zuerst die vorherigen Aufgaben lösen und gegebenenfalls die Freigabe der Lehrkraft abwarten.');
 const result=check(id,input);if(!result.ok)return {state:null,result};const next=B.clone(state);next.learning=B.clone(data(state));
 const keys=id==='inventar'&&input.basicAssets!==undefined&&input.schema!=='2'?newInventarFields:fields[id];next.learning.answers[id]=Object.fromEntries(keys.filter(k=>input[k]!==undefined).map(k=>[k,String(input[k]).slice(0,40)]));
 if(id==='inventar'&&input.basicAssets!==undefined)next.learning.answers.inventar.assets=String((B.money(input.basicAssets)+deferredValue)/100);next.revision++;return {state:next,result};
}
function accountStage(id){if(['260','480','483','770','771'].includes(id))return 5;if(['290','490','269','489','380','391','393','5480','698'].includes(id))return 8;if(['160','210','220','5201','5202','5410','652','655','696'].includes(id))return 6;return 4;}
function accountAvailable(state,id){return accessStage(state)>=accountStage(id);}
function validateStored(value){
 if(value==null)return null;
 if(typeof value!=='object'||Array.isArray(value)||!value.answers||typeof value.answers!=='object'||!Array.isArray(value.cases)||value.cases.length>15)throw Error('Ungültiger Lernfortschritt.');
 const out=empty();
 const readAnswers=(input,known)=>{if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Ungültige gespeicherte Antworten.');const answer={};for(const [key,a] of Object.entries(input)){if(!known.includes(key)||typeof a!=='string'||a.length>40)throw Error('Ungültige gespeicherte Antwort.');answer[key]=a;}return answer;};
 for(const [id,answers] of Object.entries(value.answers)){if(!fields[id])throw Error('Ungültiger Lernschritt.');out.answers[id]=readAnswers(answers,fields[id]);}
 if(value.inventoryCases!=null){if(typeof value.inventoryCases!=='object'||Array.isArray(value.inventoryCases))throw Error('Ungültige Inventur-Nachweise.');for(const [id,answers] of Object.entries(value.inventoryCases)){if(!I.byId[id]||id==='flour')throw Error('Ungültige Inventuraufgabe.');out.inventoryCases[id]=readAnswers(answers,I.byId[id].fields.map(f=>f.name));}}
 if(value.cases.some(n=>!Number.isInteger(n)||n<1||n>15)||new Set(value.cases).size!==value.cases.length)throw Error('Ungültiger Übungsfortschritt.');out.cases=[...value.cases];return out;
}
root.BioCasaLearning=Object.freeze({STEPS,fields,empty,data,check,progress,canOpen,lockReason,record,recordInventory,validateStored,DEFERRED,deferredValue,accountStage,accountAvailable,accessStage});
})(globalThis);
