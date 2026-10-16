/* BioCasa Rechnungswesen · fachlicher Kern · alle Geldwerte in Cent */
(function (root) {
'use strict';
const DATA=root.BioCasaData?.current,year=DATA?.caseYear||2026;
const PERIOD={start:year+'-10-01',end:year+'-12-31',days:90,label:'Okt.–Dez. '+year,year,previous:year+'-09-30'};
const ACCOUNTS=[{"id": "057", "name": "Gebäudeeinrichtungen · Mietereinbauten", "type": "asset", "group": "Anlagevermögen", "opening": 14800000}, {"id": "073", "name": "Anlagen für Wärme/Kälte · Tiefkühllager", "type": "asset", "group": "Anlagevermögen", "opening": 18500000}, {"id": "076", "name": "Verpackungsanlagen · Siegeleinheit", "type": "asset", "group": "Anlagevermögen", "opening": 2000000}, {"id": "082", "name": "Werkzeuge und Prüfmittel", "type": "asset", "group": "Anlagevermögen", "opening": 400000}, {"id": "084", "name": "Fuhrpark · Kühltransporter", "type": "asset", "group": "Anlagevermögen", "opening": 6800000}, {"id": "085", "name": "Sonstige Betriebsausstattung · Entwicklungsküche", "type": "asset", "group": "Anlagevermögen", "opening": 4200000}, {"id": "086", "name": "Büromaschinen und IT", "type": "asset", "group": "Anlagevermögen", "opening": 2400000}, {"id": "087", "name": "Büromöbel und Geschäftsausstattung", "type": "asset", "group": "Anlagevermögen", "opening": 1600000}, {"id": "160", "name": "Sonstige Finanzanlagen · Mietkaution", "type": "asset", "group": "Anlagevermögen", "opening": 1500000}, {"id": "200", "name": "Rohstoffe/Fertigungsmaterial", "type": "asset", "group": "Umlaufvermögen", "opening": 0, "stock": true}, {"id": "202", "name": "Hilfsstoffe · Verpackungen", "type": "asset", "group": "Umlaufvermögen", "opening": 0, "stock": true}, {"id": "210", "name": "Unfertige Erzeugnisse", "type": "asset", "group": "Umlaufvermögen", "opening": 0}, {"id": "220", "name": "Fertige Erzeugnisse", "type": "asset", "group": "Umlaufvermögen", "opening": 0}, {"id": "240", "name": "Forderungen aus Lieferungen und Leistungen", "type": "asset", "group": "Umlaufvermögen", "opening": 0}, {"id": "260", "name": "Vorsteuer", "type": "asset", "group": "Umlaufvermögen", "opening": 10811000}, {"id": "269", "name": "Übrige sonstige Forderungen", "type": "asset", "group": "Umlaufvermögen", "opening": 0}, {"id": "280", "name": "Guthaben bei Kreditinstituten · Bank", "type": "asset", "group": "Umlaufvermögen", "opening": 16039000}, {"id": "288", "name": "Kasse", "type": "asset", "group": "Umlaufvermögen", "opening": 0}, {"id": "290", "name": "Aktive Rechnungsabgrenzung · ARA", "type": "asset", "group": "Aktive Rechnungsabgrenzung", "opening": 6200000}, {"id": "300", "name": "Gezeichnetes Kapital · Stammkapital", "type": "equity", "group": "Eigenkapital", "opening": 5000000}, {"id": "310", "name": "Kapitalrücklage", "type": "equity", "group": "Eigenkapital", "opening": 31250000}, {"id": "340", "name": "Jahresüberschuss/Jahresfehlbetrag", "type": "equity", "group": "Eigenkapital", "opening": 0}, {"id": "380", "name": "Steuerrückstellungen", "type": "liability", "group": "Rückstellungen", "opening": 0}, {"id": "391", "name": "Rückstellungen für Gewährleistung", "type": "liability", "group": "Rückstellungen", "opening": 0}, {"id": "393", "name": "Sonstige Rückstellungen", "type": "liability", "group": "Rückstellungen", "opening": 0}, {"id": "420", "name": "Kurzfristige Bankverbindlichkeiten", "type": "liability", "group": "Kurzfristiges Fremdkapital", "opening": 0}, {"id": "425", "name": "Langfristige Bankverbindlichkeiten", "type": "liability", "group": "Langfristiges Fremdkapital", "opening": 49000000}, {"id": "440", "name": "Verbindlichkeiten aus Lieferungen und Leistungen", "type": "liability", "group": "Kurzfristiges Fremdkapital", "opening": 0}, {"id": "480", "name": "Umsatzsteuer", "type": "liability", "group": "Kurzfristiges Fremdkapital", "opening": 0}, {"id": "483", "name": "Verbindlichkeiten gegenüber Finanzbehörden", "type": "liability", "group": "Kurzfristiges Fremdkapital", "opening": 0}, {"id": "489", "name": "Übrige sonstige Verbindlichkeiten", "type": "liability", "group": "Kurzfristiges Fremdkapital", "opening": 0}, {"id": "490", "name": "Passive Rechnungsabgrenzung · PRA", "type": "liability", "group": "Passive Rechnungsabgrenzung", "opening": 0}, {"id": "5000", "name": "Umsatzerlöse für eigene Erzeugnisse", "type": "revenue", "group": "Erträge", "opening": 0}, {"id": "5081", "name": "Miet- und Pachterlöse", "type": "revenue", "group": "Erträge", "opening": 0}, {"id": "5201", "name": "Bestandsveränderungen · unfertige Erzeugnisse", "type": "revenue", "group": "Erträge", "opening": 0}, {"id": "5202", "name": "Bestandsveränderungen · fertige Erzeugnisse", "type": "revenue", "group": "Erträge", "opening": 0}, {"id": "5410", "name": "Sonstige Erlöse · Anlagenabgänge", "type": "revenue", "group": "Erträge", "opening": 0}, {"id": "5480", "name": "Erträge aus Auflösung von Rückstellungen", "type": "revenue", "group": "Erträge", "opening": 0}, {"id": "5710", "name": "Zinserträge", "type": "revenue", "group": "Finanzergebnis", "opening": 0}, {"id": "600", "name": "Aufwendungen für Rohstoffe/Fertigungsmaterial", "type": "expense", "group": "Materialkosten", "opening": 0}, {"id": "602", "name": "Aufwendungen für Hilfsstoffe", "type": "expense", "group": "Materialkosten", "opening": 0}, {"id": "604", "name": "Aufwendungen für Verpackungsmaterial", "type": "expense", "group": "Materialkosten", "opening": 0}, {"id": "605", "name": "Aufwendungen für Energie", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "616", "name": "Fremdinstandhaltung", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "620", "name": "Löhne", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "630", "name": "Gehälter", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "640", "name": "Arbeitgeberanteil Sozialversicherung", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "652", "name": "Abschreibungen auf Sachanlagen", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "655", "name": "Außerplanmäßige Abschreibungen", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "670", "name": "Mieten, Pachten", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "671", "name": "Leasing", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "673", "name": "Gebühren", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "677", "name": "Rechts- und Beratungskosten", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "680", "name": "Büromaterial", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "687", "name": "Werbung", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "690", "name": "Versicherungsbeiträge", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "696", "name": "Verluste aus Anlagenabgängen", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "698", "name": "Zuführungen Gewährleistungsrückstellungen", "type": "expense", "group": "Betriebliche Kosten", "opening": 0}, {"id": "751", "name": "Zinsaufwendungen", "type": "expense", "group": "Finanzergebnis", "opening": 0}, {"id": "770", "name": "Gewerbesteuer", "type": "expense", "group": "Ertragsteuern", "opening": 0}, {"id": "771", "name": "Körperschaftsteuer", "type": "expense", "group": "Ertragsteuern", "opening": 0}];
const PRODUCTS=[
 {id:'BC-R01',name:'Pizza-Rohstoffmix',detail:'Bio-Zutaten · Bewertungsmodell',unit:'kg',account:'200',expense:'600',cost:400,price:400,opening:0,min:400,color:'#dba66d'},
 {id:'BC-V01',name:'Pizzakarton & Folie',detail:'Hilfsstoff · ein Verpackungsset',unit:'Sets',account:'202',expense:'602',cost:50,price:50,opening:0,min:500,color:'#8ea67b'},
 {id:'BC-R02',name:'Bio-Mozzarella',detail:'Rohstoff · zusätzlicher Übungsartikel',unit:'kg',account:'200',expense:'600',cost:750,price:750,opening:0,min:100,color:'#729e9c'}
];
if(DATA){for(const a of ACCOUNTS)a.opening=root.BioCasaData.amount(DATA.openingBalances[a.id]||0);for(const p of PRODUCTS){const d=DATA.products.find(d=>d.id===p.id);p.cost=p.price=root.BioCasaData.amount(d.cost);p.opening=d.opening;p.min=d.minimum;}}
const byId=Object.fromEntries(ACCOUNTS.map(a=>[a.id,a]));
const clone=x=>JSON.parse(JSON.stringify(x));
const L=(account,debit=0,credit=0)=>({account,debit,credit});
const sum=(arr,fn)=>arr.reduce((s,x)=>s+fn(x),0);
const activeSign=a=>(a.type==='asset'||a.type==='expense')?1:-1;
function money(text){
 const s=String(text??'').trim().replace(/\s|€/g,'');
 if(!/^\d+(?:[.,]\d{1,2})?$/.test(s))throw Error('Gib einen positiven Betrag ohne Tausendertrennzeichen ein, z. B. 200,00.');
 const [a,b='']=s.split(/[.,]/);const n=Number(a)*100+Number((b+'00').slice(0,2));
 if(!Number.isSafeInteger(n)||n>1000000000)throw Error('Der Betrag ist für diesen Übungsbetrieb zu groß.');
 return n;
}
function dateOK(date){if(typeof date!=='string'||date<PERIOD.start||date>PERIOD.end||!/^\d{4}-(10|11|12)-[0-3]\d$/.test(date))return false;return !isNaN(Date.parse(date+'T00:00:00Z'))&&new Date(date+'T00:00:00Z').toISOString().slice(0,10)===date;}
function validateLines(lines){
 if(!Array.isArray(lines)||lines.length<2||lines.length>16)throw Error('Eine Buchung benötigt 2 bis 16 Kontenzeilen.');
 for(const l of lines){
  if(!byId[l.account])throw Error('Wähle in jeder Zeile ein gültiges Konto.');
  if(!Number.isSafeInteger(l.debit)||!Number.isSafeInteger(l.credit)||l.debit<0||l.credit<0||l.debit>1000000000||l.credit>1000000000)throw Error('Kontobeträge müssen gültige, nicht negative Centwerte sein.');
  if((l.debit===0)===(l.credit===0))throw Error('Jede Zeile benötigt genau einen Betrag: im Soll oder im Haben.');
 }
 if(sum(lines,l=>l.debit)!==sum(lines,l=>l.credit))throw Error('Soll und Haben sind noch nicht ausgeglichen.');
}
function newState(seed=true){return {v:1,seed,entries:[],reflection:'',level:'w2',view:'home',revision:0,learning:null,drafts:null,savedAt:null,importedAt:null};}
function inventoryDraft({productId,kind,qty,price,tax,date=PERIOD.end,text='',reference='',settlement='440'}){
 const p=PRODUCTS.find(x=>x.id===productId);
 if(!p)throw Error('Wähle einen Artikel.');
 if(!['purchase','consumption','loss'].includes(kind))throw Error('Wähle eine gültige Materialbewegung.');
 if(!Number.isInteger(qty)||qty<1||qty>100000)throw Error('Die Menge muss eine positive ganze Zahl in der Artikeleinheit sein.');
 if(![0,7,19].includes(tax))throw Error('Wähle einen Übungssteuersatz.');
 if(price!==p.cost)throw Error('Im Prototyp gilt der feste Einstandspreis des Artikels.');
 const net=qty*price,vat=kind==='purchase'?Math.round(net*tax/100):0;
 let lines;
 if(kind==='purchase'){
  if(!['440','280','288'].includes(settlement))throw Error('Wähle Verbindlichkeiten, Bank oder Kasse.');
  lines=[L(p.account,net),...(vat?[L('260',vat)]:[]),L(settlement,0,net+vat)];
 }else lines=[L(p.expense,net),L(p.account,0,net)];
 return {date,text:text||({purchase:'Materialzugang',consumption:'Materialentnahme',loss:'Bestandsverlust'}[kind]+' · '+p.name),reference,lines,movement:{productId,qty:kind==='purchase'?qty:-qty,kind,net:kind==='purchase'?net:0,vat},task:null};
}
function makeSeed(){
 const out=[];const push=e=>out.push({...e,id:out.length+1,source:'seed',reversalOf:null,task:null});
 const raw=(date,text,reference,lines)=>push({date,text,reference,lines,movement:null});
 push(inventoryDraft({date:'2026-10-02',productId:'BC-R01',kind:'purchase',qty:2000,price:400,tax:0,settlement:'440',reference:'G1 / ER-01',text:'LS02 G1 · Rohstoffe auf Ziel · ohne Steuer'}));
 raw('2026-10-03','LS02 G2 · Büromöbel per Bank','G2 / ER-02 + BA-01',[L('087',120000),L('280',0,120000)]);
 raw('2026-10-04','LS02 G3 · Bargeld vom Bankkonto abgehoben','G3 / BA-02 + KB-01',[L('288',200000),L('280',0,200000)]);
 raw('2026-10-05','LS02 G4 · Teilzahlung an Lieferanten','G4 / BA-03',[L('440',300000),L('280',0,300000)]);
 raw('2026-10-06','LS02 G5 · Lieferantenschuld durch Darlehen abgelöst','G5 / V-01',[L('440',200000),L('425',0,200000)]);
 raw('2026-10-07','LS02 G6 · Küche durch zusätzliches Darlehen finanziert','G6 / ER-03 + D-01',[L('085',450000),L('425',0,450000)]);
 raw('2026-10-08','LS02 G7 · freiwillige Sondertilgung im Übungsfenster','G7 / BA-04',[L('425',500000),L('280',0,500000)]);
 push(inventoryDraft({date:'2026-10-09',productId:'BC-V01',kind:'purchase',qty:2000,price:50,tax:0,settlement:'280',reference:'G8 / ER-04 + BA-05',text:'LS02 G8 · Verpackungsvorrat per Bank · ohne Steuer'}));
 // Eigenständige OS-Erprobungsbelege. Keine vollständige Jahreschronik aus LS08.
 push(inventoryDraft({date:'2026-11-10',productId:'BC-R01',kind:'consumption',qty:1000,price:400,tax:0,settlement:'440',reference:'OS-01',text:'OS-Übung · Rohstoffentnahme für verkaufte Pizza-Charge'}));
 raw('2026-11-15','OS-Übung · eigene Bio-Pizzen verkauft · 7 % USt','OS-02',[L('280',2675000),L('5000',0,2500000),L('480',0,175000)]);
 raw('2026-11-18','OS-Übung · Hallenmiete','OS-03',[L('670',890000),L('280',0,890000)]);
 raw('2026-11-21','OS-Übung · Gehälter, vereinfacht','OS-04',[L('630',500000),L('280',0,500000)]);
 raw('2026-11-25','OS-Übung · Energiekosten · 19 % Vorsteuer','OS-05',[L('605',60000),L('260',11400),L('280',0,71400)]);
 raw('2026-12-30','OS-Übung · lineare Abschreibung Siegeleinheit','OS-06',[L('652',100000),L('076',0,100000)]);
 raw('2026-12-31','OS-Übung · Zinsaufwand','OS-07',[L('751',20000),L('280',0,20000)]);
 return out;
}
const SEED=DATA?DATA.demoEntries.map((e,i)=>({date:e.date,text:e.text,reference:e.reference,id:i+1,source:'seed',reversalOf:null,task:null,lines:e.lines.map(l=>L(l[0],root.BioCasaData.amount(l[1]),root.BioCasaData.amount(l[2]))),movement:e.movement?{...e.movement,net:root.BioCasaData.amount(e.movement.net),vat:root.BioCasaData.amount(e.movement.vat)}:null})):makeSeed();
function journal(state){return [...(state.seed?clone(SEED):[]),...state.entries];}
function snapshot(state,cutoff=PERIOD.end){
 const entries=journal(state).filter(e=>e.date<=cutoff);
 const balances=Object.fromEntries(ACCOUNTS.map(a=>[a.id,a.opening]));
 const quantities=Object.fromEntries(PRODUCTS.map(p=>[p.id,p.opening]));
 const sold=Object.fromEntries(PRODUCTS.map(p=>[p.id,0]));
 const productRevenue=Object.fromEntries(PRODUCTS.map(p=>[p.id,0]));
 for(const e of entries){for(const l of e.lines)balances[l.account]+=activeSign(byId[l.account])*(l.debit-l.credit);
  if(e.movement){const m=e.movement;quantities[m.productId]+=m.qty;if(m.kind==='consumption'||m.kind==='loss'){sold[m.productId]-=m.qty;}}
 }
 const revenue=balances['5000'];
 const allRevenue=sum(ACCOUNTS.filter(a=>a.type==='revenue'),a=>balances[a.id]);
 const otherRevenue=allRevenue-revenue;
 const expenses=sum(ACCOUNTS.filter(a=>a.type==='expense'),a=>balances[a.id]);
 const profit=allRevenue-expenses;
 const assets=sum(ACCOUNTS.filter(a=>a.type==='asset'),a=>balances[a.id]);
 const liabilities=sum(ACCOUNTS.filter(a=>a.type==='liability'),a=>balances[a.id]);
 const bookedEquity=sum(ACCOUNTS.filter(a=>a.type==='equity'),a=>balances[a.id]);
 const equity=bookedEquity+profit,operatingRevenue=allRevenue-balances['5710'],tax=balances['770']+balances['771'];
 const cogs=balances['600']+balances['602']+balances['604'];
 const ebit=profit+balances['751']-balances['5710']+tax;
 const depreciation=balances['652']+balances['655'];
 return {entries,balances,quantities,sold,productRevenue,revenue,otherRevenue,allRevenue,operatingRevenue,expenses,profit,assets,liabilities,bookedEquity,equity,passives:liabilities+equity,cash:balances['280']+balances['288'],cogs,ebit,ebitda:ebit+depreciation,depreciation,stock:balances['200']+balances['202']};
}

function validateEntryShape(entry){
 if(!entry||!dateOK(entry.date))throw Error('Buchungsdatum muss zwischen dem 01.10. und 31.12.'+year+' liegen.');
 if(typeof entry.text!=='string'||!entry.text.trim()||entry.text.length>120)throw Error('Der Buchungstext benötigt 1 bis 120 Zeichen.');
 if(typeof entry.reference!=='string'||entry.reference.length>40)throw Error('Die Belegnummer darf höchstens 40 Zeichen haben.');
 validateLines(entry.lines);
 if(entry.movement){const m=entry.movement;
  if(!PRODUCTS.some(p=>p.id===m.productId)||!Number.isInteger(m.qty)||m.qty===0||Math.abs(m.qty)>100000||!['purchase','consumption','loss'].includes(m.kind)||!Number.isSafeInteger(m.net)||!Number.isSafeInteger(m.vat))throw Error('Ungültige Lagerverknüpfung.');
 }
}
function checkState(state){
 const entries=journal(state),ids=new Set();const seen=[];
 for(const e of entries){validateEntryShape(e);if(!Number.isInteger(e.id)||e.id<1||ids.has(e.id))throw Error('Doppelte oder ungültige Buchungsnummer.');ids.add(e.id);
  if(e.reversalOf){const orig=seen.find(x=>x.id===e.reversalOf);
   if(!orig||orig.reversalOf||seen.some(x=>x.reversalOf===orig.id)||e.date<orig.date)throw Error('Ungültige Stornoreferenz.');
   if(JSON.stringify(e.lines)!==JSON.stringify(orig.lines.map(l=>L(l.account,l.credit,l.debit))))throw Error('Storno muss die Originalbuchung vollständig umkehren.');
   const expected=orig.movement?{...orig.movement,qty:-orig.movement.qty,net:-orig.movement.net,vat:-orig.movement.vat}:null;
   if(JSON.stringify(e.movement||null)!==JSON.stringify(expected))throw Error('Lagerstorno passt nicht zum Original.');
  }else{
   if(e.movement){const m=e.movement,p=PRODUCTS.find(p=>p.id===m.productId);
    if((m.kind==='purchase'&&m.qty<0)||(m.kind!=='purchase'&&m.qty>0)||m.net<0||m.vat<0)throw Error('Lagerbewegungsrichtung ist ungültig.');
    const stockDelta=sum(e.lines.filter(l=>l.account===p.account),l=>l.debit-l.credit);
    if(stockDelta!==m.qty*p.cost)throw Error('Warenwert und Artikelmenge stimmen nicht überein.');
    if(m.kind==='purchase'&&m.net!==m.qty*p.cost)throw Error('Wareneingang benötigt den festen Einstandspreis.');
   }else if(e.lines.some(l=>byId[l.account]?.stock))throw Error('Warenbestand bitte über den Lagerbereich buchen, damit Stückzahlen und Bilanz zusammenpassen.');
  }
  seen.push(e);
 }
 const quantities=Object.fromEntries(PRODUCTS.map(p=>[p.id,p.opening]));
 const cash={'280':byId['280'].opening,'288':byId['288'].opening};
 for(const e of [...entries].sort((a,b)=>a.date.localeCompare(b.date)||a.id-b.id)){
  if(e.movement){quantities[e.movement.productId]+=e.movement.qty;if(quantities[e.movement.productId]<0)throw Error('Diese Buchung würde zu einem negativen Lagerbestand führen – gegebenenfalls auch an einem früheren Buchungsdatum.');}
  for(const id of Object.keys(cash)){cash[id]+=sum(e.lines.filter(l=>l.account===id),l=>l.debit-l.credit);if(cash[id]<0)throw Error('Der verfügbare Bank- oder Kassenbestand reicht am Buchungsdatum nicht aus. Im Übungsbetrieb gibt es keinen Kontokorrentkredit.');}
 }
 const s=snapshot(state);
 if(s.assets!==s.passives)throw Error('Bilanz ist nicht ausgeglichen.');
 if(s.stock!==sum(PRODUCTS,p=>s.quantities[p.id]*p.cost))throw Error('Lager und Finanzbuchhaltung stimmen nicht überein.');
 return true;
}
function post(state,draft){
 validateEntryShape(draft);
 if(state.entries.length>=60)throw Error('Dieser Übungsversuch enthält bereits 60 zusätzliche Buchungen. Exportiere ihn und beginne bei Bedarf einen neuen Versuch.');
 const entries=journal(state);const e={date:draft.date,text:draft.text.trim(),reference:draft.reference,lines:clone(draft.lines),movement:draft.movement?clone(draft.movement):null,task:draft.task||null,id:Math.max(0,...entries.map(x=>x.id))+1,source:'learner',reversalOf:null};
 const next=clone(state);next.entries.push(e);next.revision++;checkState(next);return {state:next,entry:e};
}
function reverse(state,id){
 const orig=journal(state).find(e=>e.id===id);
 if(!orig||orig.reversalOf||journal(state).some(e=>e.reversalOf===id))throw Error('Diese Buchung kann nicht erneut storniert werden.');
 const next=clone(state);const entries=journal(state);
 const e={id:Math.max(0,...entries.map(e=>e.id))+1,date:PERIOD.end,text:('Storno · '+orig.text).slice(0,120),reference:'ST-'+id,lines:orig.lines.map(l=>L(l.account,l.credit,l.debit)),movement:orig.movement?{...orig.movement,qty:-orig.movement.qty,net:-orig.movement.net,vat:-orig.movement.vat}:null,task:null,source:'learner',reversalOf:id};
 if(next.entries.length>=60)throw Error('Der Versuch ist voll. Exportiere den Stand und beginne einen neuen Versuch.');
 next.entries.push(e);next.revision++;checkState(next);return {state:next,entry:e};
}
function metrics(state){
 const s=snapshot(state),initial=snapshot(newState(false),PERIOD.previous);
 const averageStock=(initial.stock+s.stock)/2,turnover=averageStock>0?s.cogs/averageStock:null;
 const shortDebt=sum(ACCOUNTS.filter(a=>a.group==='Kurzfristiges Fremdkapital'),a=>s.balances[a.id]);
 const avgAssets=(initial.assets+s.assets)/2,avgEquity=(initial.equity+s.equity)/2;
 const ratio=(a,b)=>b>0?a/b:null;
 return {...s,averageStock,turnover,storageDays:turnover>0?PERIOD.days/turnover:null,shortDebt,averageAssets:avgAssets,averageEquity:avgEquity,equityRatio:ratio(s.equity,s.assets),liquidity1:ratio(s.cash,shortDebt),liquidity2:ratio(s.cash+s.balances['240'],shortDebt),margin:ratio(s.ebit,s.revenue),capitalTurnover:ratio(s.revenue,avgAssets),roi:ratio(s.ebit,avgAssets),equityReturn:ratio(s.profit,avgEquity),db:s.operatingRevenue-s.cogs,fixed:s.expenses-s.cogs-s.balances['751']-s.balances['770']-s.balances['771'],simpleCashflow:s.profit+s.depreciation};
}
function effect(state,draft){const before=snapshot(state);const result=post(state,draft);const after=snapshot(result.state);return {before,after,entry:result.entry,changes:ACCOUNTS.filter(a=>before.balances[a.id]!==after.balances[a.id]).map(a=>({...a,before:before.balances[a.id],after:after.balances[a.id],delta:after.balances[a.id]-before.balances[a.id]}))};}
function taskStatus(state){
 const j=journal(state),live=state.entries.filter(e=>!e.reversalOf&&!j.some(x=>x.reversalOf===e.id));
 const net=(e,a)=>sum(e.lines.filter(l=>l.account===a),l=>l.debit-l.credit);
 return {bank:live.some(e=>e.task==='bank'&&net(e,'280')===20000&&net(e,'288')===-20000&&e.lines.every(l=>['280','288'].includes(l.account))),stock:live.some(e=>e.task==='stock'&&e.movement?.productId==='BC-R02'&&e.movement.kind==='purchase'&&e.movement.qty===200&&e.movement.net===150000&&e.movement.vat===10500&&net(e,'200')===150000&&net(e,'260')===10500&&net(e,'440')===-160500&&e.lines.every(l=>['200','260','440'].includes(l.account))),analysis:state.reflection.trim().length>=80};
}
function pack(state){return {v:1,s:state.seed?1:0,e:state.entries.map(e=>[e.id,e.date,e.text,e.reference,e.lines.map(l=>[ACCOUNTS.findIndex(a=>a.id===l.account),l.debit,l.credit]),e.movement?[PRODUCTS.findIndex(p=>p.id===e.movement.productId),e.movement.qty,e.movement.kind,e.movement.net,e.movement.vat]:null,e.reversalOf||null,e.task||null]),r:state.reflection,l:state.level,w:state.view,n:state.revision,p:state.learning||null,d:state.drafts||null,t:state.savedAt||null,u:state.importedAt||null,...(state.bookingChecks?.length?{q:state.bookingChecks}:{}),...(state.accountClosures?.length?{c:state.accountClosures}:{}),...(DATA?{h:root.BioCasaData.identity}:{})};}
function unpack(data){
 if(!data||data.v!==1||![0,1].includes(data.s)||!Array.isArray(data.e)||data.e.length>60)throw Error('Diese Datei ist kein gültiger BioCasa-Übungsstand (Version 1).');
 if(DATA&&((data.h!=null&&data.h!==root.BioCasaData.identity)||(data.h==null&&!root.BioCasaData.legacyCompatible)))throw Error('Die Sicherung gehört zu einer anderen Datenbasis oder einem anderen Schuljahr. Öffne das passende Kurspaket oder beginne einen neuen Moodle-Versuch.');
 const s=newState(!!data.s);
 s.entries=data.e.map(e=>({id:e[0],date:e[1],text:e[2],reference:e[3],lines:e[4].map(l=>L(ACCOUNTS[l[0]]?.id,l[1],l[2])),movement:e[5]?{productId:PRODUCTS[e[5][0]]?.id,qty:e[5][1],kind:e[5][2],net:e[5][3],vat:e[5][4]}:null,reversalOf:e[6]||null,task:['bank','stock'].includes(e[7])?e[7]:null,source:'learner'}));
 if(typeof data.r!=='string'||data.r.length>600)throw Error('Der Auswertungstext darf höchstens 600 Zeichen enthalten.');
 for(const [key,field] of [['t','savedAt'],['u','importedAt']]){if(data[key]!=null){if(typeof data[key]!=='string'||data[key].length>40||!Number.isFinite(Date.parse(data[key])))throw Error('Ungültiges Sicherungsdatum.');s[field]=data[key];}}
 if(data.p!=null){if(typeof data.p!=='object'||JSON.stringify(data.p).length>3000)throw Error('Ungültiger Lernfortschritt.');s.learning=root.BioCasaLearning?root.BioCasaLearning.validateStored(data.p):clone(data.p);}
 if(data.d!=null){if(!root.BioCasaDrafts)throw Error('Die Eingabewiederherstellung ist noch nicht geladen.');s.drafts=root.BioCasaDrafts.validate(data.d);}
 if(data.q!=null){if(!root.BioCasaChecks)throw Error('Die Buchungschecks sind noch nicht geladen.');s.bookingChecks=root.BioCasaChecks.validate(data.q);}
 if(data.c!=null){if(!root.BioCasaAccounts)throw Error('Die Kontenansicht ist noch nicht geladen.');s.accountClosures=root.BioCasaAccounts.validate(data.c,s);}
 s.reflection=data.r;s.level=['w1','w2','w3','w4','w5'].includes(data.l)?data.l:'w2';s.view=['home','inventory','booking','reports','stock','control','tasks','help'].includes(data.w)?data.w:'home';s.revision=Number.isInteger(data.n)&&data.n>=0?data.n:0;checkState(s);return s;
}
const api={PERIOD,ACCOUNTS,PRODUCTS,byId,L,SEED,clone,sum,money,dateOK,newState,journal,snapshot,inventoryDraft,validateLines,checkState,post,reverse,metrics,effect,taskStatus,pack,unpack};
if(DATA){root.BioCasaData.validate(DATA,ACCOUNTS,PRODUCTS);checkState(newState());}
root.BioCasa=Object.freeze(api);
})(globalThis);
