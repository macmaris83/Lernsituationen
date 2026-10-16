/* Gemeinsame Lernmodelle: ein Datenkranz, nachvollziehbare Arbeitsergebnisse. */
(function(root){
'use strict';
const B=root.BioCasa;
const DEFERRED=['160','260','290'];
const POSITION_KEYS={'084':'vehicle','087':'furniture','280':'bank','425':'loan'};
const POSITIONS=B.ACCOUNTS.filter(a=>(a.opening>0||['084','087','280','425'].includes(a.id))&&['asset','liability'].includes(a.type)&&!DEFERRED.includes(a.id)).map(a=>({...a,field:POSITION_KEYS[a.id]||'i'+a.id,sideField:a.id==='280'?'bankSide':a.id==='425'?'loanSide':'b'+a.id,kind:a.type==='liability'?'debt':a.group==='Anlagevermögen'?'av':'uv'}));
const ZERO=['200','202','240','288'].filter(id=>!POSITIONS.some(a=>a.id===id)).map(id=>({...B.byId[id],kind:'uv',fixed:true}));
const EXTRA=DEFERRED.map(id=>({...B.byId[id],kind:id==='290'?'rap':id==='160'?'av':'uv',fixed:true,deferred:true}));
const KINDS={av:'Anlagevermögen',uv:'Umlaufvermögen',rap:'Aktive Rechnungsabgrenzung',debt:'Schulden',equity:'Eigenkapital'};
const CODES={av:'A.I',uv:'A.II',rap:'A.III',debt:'B',equity:'C'};
function inventoryModel(input={},legacyComplete=false){
 const rows=[...POSITIONS.map(a=>({...a,kind:input[a.field]||((legacyComplete&&input.schema!=='2')?a.kind:null)})),...ZERO,...EXTRA];
 const pending=rows.filter(a=>!['av','uv','debt'].includes(a.kind)&&!a.fixed),complete=!pending.length;
 const total=kind=>B.sum(rows.filter(a=>a.kind===kind),a=>a.opening);
 const assets=total('av')+total('uv')+total('rap'),debts=total('debt');
 return {rows,pending,complete,assets,debts,equity:assets-debts,groups:['av','uv','rap','debt'].map(kind=>({kind,title:KINDS[kind],code:CODES[kind],rows:rows.filter(a=>a.kind===kind),total:total(kind)}))};
}
function balanceModel(inventar,input={},legacyComplete=false){
 const rows=inventar.rows.map(a=>({...a,source:CODES[a.kind],side:a.fixed?'assets':input[POSITIONS.find(p=>p.id===a.id)?.sideField]||((legacyComplete&&input.schema!=='2')?(a.kind==='debt'?'passives':'assets'):null)}));
 rows.push({id:'EK',name:'Eigenkapital · Reinvermögen aus dem Inventar',opening:inventar.equity,kind:'equity',source:'C',side:input.equitySide||((legacyComplete&&input.schema!=='2')?'passives':null)});
 const pending=rows.filter(a=>!['assets','passives'].includes(a.side));
 const side=key=>({rows:rows.filter(a=>a.side===key),total:B.sum(rows.filter(a=>a.side===key),a=>a.opening)});
 return {rows,pending,complete:!pending.length,assets:side('assets'),passives:side('passives')};
}
const DECISIONS={
 accounts:[
  {id:'a',title:'Bargeld auf das Geschäftskonto einzahlen',story:'Christian zahlt 200 € aus der BioCasa-Kasse auf das Bankkonto ein. Beide Bewegungen sind bestätigt. Im Übungsstand ist ausreichend Bargeld vorhanden.',targets:[{prefix:'r1',fragment:'Das Geld steht nun zusätzlich auf dem Geschäftskonto zur Verfügung.',account:'280',family:'b',type:'a',move:'up',side:'d'},{prefix:'r2',fragment:'Der eingezahlte Betrag befindet sich nicht mehr in der Barkasse.',account:'288',family:'b',type:'a',move:'down',side:'c'}]},
  {id:'b',title:'Ein Darlehen teilweise zurückzahlen',story:'BioCasa überweist 5.000 € als reine Tilgung eines bestehenden Bankdarlehens. Es sind weder Zinsen noch Gebühren enthalten.',targets:[{prefix:'r3',fragment:'Die Rückzahlungsverpflichtung gegenüber der Bank wird kleiner.',account:'425',family:'b',type:'p',move:'down',side:'d'},{prefix:'r4',fragment:'Das Geld wird vom Geschäftskonto überwiesen.',account:'280',family:'b',type:'a',move:'down',side:'c'}]}
 ],
 income:[
  {id:'a',title:'Halle im laufenden Monat nutzen',story:'BioCasa bezahlt 1.000 € Hallenmiete für den laufenden Monat über die Bank. Die Nutzung ist eine betriebliche Leistung, die im aktuellen Monat verbraucht wird. Umsatzsteuer bleibt im Grundlagenfall ausgeblendet.',targets:[{prefix:'r1',fragment:'Die betriebliche Hallennutzung wird für diesen Monat verbraucht.',account:'670',family:'e',type:'exp',move:'up',side:'d'},{prefix:'r2',fragment:'Die Zahlung geht vom Geschäftskonto ab.',account:'280',family:'b',type:'a',move:'down',side:'c'}]},
  {id:'b',title:'Eigene Bio-Pizzen auf Ziel liefern',story:'BioCasa liefert eigene Erzeugnisse für 600 € an einen Einzelhändler. Der Kunde bezahlt später. Die vereinbarte Leistung ist bereits erbracht. Umsatzsteuer bleibt hier ausgeblendet.',targets:[{prefix:'r3',fragment:'BioCasa hat einen Zahlungsanspruch gegenüber dem Kunden.',account:'240',family:'b',type:'a',move:'up',side:'d'},{prefix:'r4',fragment:'Der Wert der erbrachten Verkaufsleistung wird erfasst.',account:'5000',family:'e',type:'rev',move:'up',side:'c'}]}
 ]
};
const QUESTION_PARTS=[
 ['a','1 · Welches Konto?',null],
 ['f','2 · Bestandskonto oder Erfolgskonto?',[['b','Bestandskonto'],['e','Erfolgskonto']]],
 ['t','3 · Welche Kontoart?',[['a','Aktives Bestandskonto'],['p','Passives Bestandskonto'],['exp','Aufwandskonto'],['rev','Ertragskonto']]],
 ['m','4 · Zugang oder Abgang?',[['up','Zugang / Zunahme'],['down','Abgang / Abnahme']]],
 ['s','5 · Soll oder Haben?',[['d','Soll · links'],['c','Haben · rechts']]]
];
function decisionFields(id){const options=(id==='accounts'?['280','288','425','087']:['670','280','240','5000']).map(n=>[n,n+' · '+B.byId[n].name]);return (DECISIONS[id]||[]).flatMap(c=>c.targets.flatMap(t=>QUESTION_PARTS.map(([suffix,label,choices])=>({name:t.prefix+suffix,label,options:choices||options}))));}
function decisionAnswers(id){return Object.fromEntries((DECISIONS[id]||[]).flatMap(c=>c.targets.flatMap(t=>Object.entries({a:t.account,f:t.family,t:t.type,m:t.move,s:t.side}).map(([k,v])=>[t.prefix+k,v]))));}
function checkDecisions(id,input){const expected=decisionAnswers(id),wrong=[];for(const [field,value] of Object.entries(expected))if(input[field]!==value){const t=DECISIONS[id].flatMap(c=>c.targets).find(t=>field.startsWith(t.prefix));const q=QUESTION_PARTS.find(q=>field===t.prefix+q[0]);wrong.push({field,hint:t.fragment+' '+q[1].slice(4)+' Prüfe den betrieblichen Vorgang und die passende Kontenregel.'});}return {wrong,total:Object.keys(expected).length};}
const HELPS={
 inventar:{title:'Wie wird aus Nachweisen ein Inventar?',why:'Die Geschäftsführung braucht ein vollständiges Bild: Was ist vorhanden, was schulden wir und was bleibt rechnerisch übrig?',steps:[
  ['Nachweise sammeln','Zählblätter, Kontoauszüge und Verträge belegen Bestand, Menge und Wert am selben Stichtag. Fremdes Eigentum und ungenutzte Kreditlinien werden nicht als eigenes Vermögen ergänzt.',['Inventur','bestätigte Nachweise','bewertete Positionen']],
  ['Vermögen und Schulden ordnen','Langfristig genutzte Vermögenswerte gehören zum Anlagevermögen. Kurzfristig gebundene oder verfügbare Werte gehören zum Umlaufvermögen. Rückzahlungsverpflichtungen sind Schulden.',['dauerhafte Nutzung / kurzfristige Bindung','Vermögen','Rückzahlungsverpflichtung → Schulden']],
  ['In Staffelform aufschreiben','Das Inventar steht untereinander: A. Vermögen mit seinen Gruppen, B. Schulden, C. Reinvermögen. Mengen und Einzelwerte bleiben in den zugehörigen Inventurnachweisen; dieses Startverzeichnis übernimmt deren bestätigte Positionswerte.',['A · Vermögen','B · Schulden','C · Reinvermögen']],
  ['Reinvermögen ermitteln','Vollständiges Vermögen minus Schulden ergibt das Reinvermögen. Graue Positionen werden hier vorgegeben ergänzt; ihre fachliche Vertiefung kommt später.',['Vermögen','− Schulden','= Reinvermögen']]
 ]},
 balance:{title:'Warum wird das Inventar zur Bilanz?',why:'Dasselbe Unternehmen wird aus zwei Blickwinkeln betrachtet: Verwendung und Herkunft der Mittel.',steps:[
  ['Die Werte bleiben dieselben','Übernimm die geprüften Werte und den Stichtag aus dem Inventar. Der Wechsel der Darstellung erzeugt weder neues Vermögen noch eine Zahlung.',['Inventar am Stichtag','gleiche Werte','Bilanz am Stichtag']],
  ['Aktiva stehen links','Die Vermögenspositionen werden auf der linken Seite verdichtet. Anlage- und Umlaufvermögen bleiben als Gruppen erkennbar.',['Vermögen aus A','Aktiva · links','Mittelverwendung']],
  ['Passiva stehen rechts','Das Reinvermögen aus C wird zu Eigenkapital. Zusammen mit den Schulden aus B erklärt es die Finanzierung der Vermögenswerte.',['Reinvermögen + Schulden','Passiva · rechts','Mittelherkunft']],
  ['Beide Seiten abstimmen','Aktiva und Passiva müssen gleich hoch sein. Eine Differenz zeigt eine fehlende, doppelte oder falsch übertragene Position; sie ist kein zusätzlicher Vermögenswert.',['Summe Aktiva','vergleichen','Summe Passiva']]
 ]},
 accounts:{title:'Vom Geschäftsvorfall zu Soll und Haben',why:'Konten machen jede Bestandsveränderung sichtbar, ohne nach jedem Vorgang die gesamte Bilanz neu aufzustellen.',steps:[
  ['Zuerst den Vorgang verstehen','Beschreibe in eigenen Worten, was BioCasa bekommt, abgibt, schuldet oder nicht mehr schuldet. Suche für jeden Teil das passende Konto.',['betrieblicher Vorgang','betroffene Werte','Konten benennen']],
  ['Die Kontoart bestimmen','Ein Bestandskonto bildet Vermögen, Eigenkapital oder Schulden ab. Aktive Bestandskonten stammen aus den Aktiva; passive aus den Passiva. Erfolgskonten werden im nächsten Lernschritt eingeführt.',['Bilanzposition','aktiv oder passiv?','Bestandskonto']],
  ['Zugang oder Abgang unterscheiden','Bestimme die Veränderung für jedes Konto einzeln. Ein Geldabgang und ein Schuldenabgang sind zwei verschiedene Wirkungen desselben Vorgangs.',['Konto 1 verändert sich','Konto 2 verändert sich','jeweils Zugang oder Abgang?']],
  ['Die Kontoseite ableiten','Aktiv: Anfangsbestand und Zugänge im Soll, Abgänge im Haben. Passiv: Anfangsbestand und Zugänge im Haben, Abgänge im Soll. Soll steht links, Haben rechts; beide Wörter bedeuten für sich weder Plus noch Minus.',['Kontoart + Veränderung','passende Regel','Soll an Haben']]
 ]},
 income:{title:'Aufwand, Ertrag und Zahlung unterscheiden',why:'Die GuV soll zeigen, wodurch BioCasa Erfolg erzielt. Eine Geldbewegung allein erklärt das noch nicht.',steps:[
  ['Die Leistung betrachten','Wird in dieser Periode eine betriebliche Leistung verbraucht oder wird eine Leistung erbracht? Prüfe außerdem, ob ein Vermögenswert oder eine Schuld verändert wird.',['betriebliche Leistung','Verbrauch oder Erbringung?','betroffene Konten']],
  ['Bestands- oder Erfolgskonto?','Bestandskonten zeigen vorhandene Werte und Verpflichtungen. Erfolgskonten sammeln Aufwendungen und Erträge einer Periode. Deshalb kann ein Geschäftsvorfall beide Kontoarten berühren.',['Bestand verändert sich','oder Erfolg entsteht?','jedes Konto einzeln prüfen']],
  ['Aufwand oder Ertrag?','Aufwendungen mindern den Erfolg, Erträge erhöhen ihn. Aufwandszugänge stehen im Soll, Ertragszugänge im Haben. Minderungen und Korrekturen stehen jeweils auf der Gegenseite.',['Aufwand → Erfolg sinkt','Ertrag → Erfolg steigt','Zugang oder Korrektur?']],
  ['Zahlung gesondert prüfen','Auf Ziel bedeutet zunächst eine Forderung oder Verbindlichkeit. Eine Tilgung kann Geld und Schulden mindern, ohne Aufwand zu sein. Leite für alle beteiligten Konten die Seite ab.',['Erfolg','Bestandsveränderung','Zahlung separat prüfen']]
 ]},
 tax:{title:'Mehrwertsteuer entlang der Wertschöpfungskette',why:'BioCasa ist ein Industrieunternehmen: Aus eingekauften Zutaten werden eigene Bio-Lebensmittel. Die Steuer muss von den eigentlichen Werten getrennt erkennbar bleiben.',steps:[
  ['BioCasa in der Wertschöpfungskette','Bauernhöfe und Zutatenhersteller liefern Vorleistungen. BioCasa verarbeitet sie zu eigenen Erzeugnissen. Danach können Großhandel und Einzelhandel folgen. Auch direkte Lieferungen an eine Gemeindekantine sind möglich.',['Vorleistungen','Herstellung','Vertrieb und Verbrauch']],
  ['Beim Einkauf: Vorsteuer','Im vereinfachten Modell bezahlt BioCasa für Zutaten 100 € netto plus 7 € Steuer an den Lieferanten. Dieselben 7 € sind für den Lieferanten Umsatzsteuer und für BioCasa abziehbare Vorsteuer. Voraussetzung ist insbesondere eine passende Rechnung für einen berechtigten betrieblichen Bezug.',['BioCasa zahlt 107 € an Lieferanten','100 € Nettowert + 7 € Vorsteuer','7 € Anspruch im Steuersystem']],
  ['Beim Verkauf: Umsatzsteuer','Im getrennten Beispiel liefert BioCasa für 200 € netto plus 14 € Steuer. Bei Zahlung gehen 214 € vom Kunden ein. Die 14 € werden als Umsatzsteuer erfasst; sie sind kein zusätzlicher Erlös. Eine offene Rechnung und ein Zahlungseingang sind zu unterscheiden.',['Kunde zahlt 214 € an BioCasa','200 € Erlös + 14 € Umsatzsteuer','14 € Verpflichtung im Steuersystem']],
  ['Mit dem Finanzamt abrechnen','Im Beispiel: 14 € Umsatzsteuer minus 7 € abziehbare Vorsteuer ergeben 7 € Zahllast. Überwiegt die abziehbare Vorsteuer, entsteht ein Erstattungsüberhang. Die Steuer entsteht somit nicht nochmals als Aufwand oder Ertrag.',['Umsatzsteuer','− abziehbare Vorsteuer','= Zahllast / Erstattungsüberhang']]
 ]},
 further:{title:'Was verändert sich hinter einer weiteren Buchung?',why:'Die Buchhaltung soll Nutzung, vorhandene Werte und Produktion abbilden – auch wenn gerade kein Geld fließt.',steps:[
  ['Den Auslöser benennen','Unterscheide Anschaffung, Nutzung, Herstellung und Verkauf. Dieselbe Maschine kann zunächst angeschafft und später über mehrere Perioden genutzt werden.',['betrieblicher Auslöser','betroffener Wert','passende Periode']],
  ['Nutzung als Wertverbrauch erfassen','Eine Abschreibung verteilt den erfassten Werteverzehr auf die Nutzungsperioden. Eine bereits bezahlte Anlage verursacht dadurch keine zweite Zahlung.',['Anlage wird genutzt','Buchwert verändert sich','Erfolg verändert sich']],
  ['Produktion und Verkauf auseinanderhalten','Unfertige und fertige eigene Erzeugnisse können noch im Betrieb sein. Eine Bestandszunahme ist kein automatischer Verkauf und keine automatische Einzahlung.',['Herstellung','Bestand bewerten','Verkauf gesondert prüfen']],
  ['Wirkungen verbinden','Frage bei jeder Buchung: Welches Konto, welche Kontoart, welche Veränderung und welche Seite? Prüfe zuletzt Bilanz, GuV und Zahlungsfluss getrennt.',['Konten','Bilanz und GuV','Zahlung separat']]
 ]},
 returns:{title:'Was wird bei einer Retoure rückgängig gemacht?',why:'Eine Rücksendung betrifft die Ware und die Abrechnung. Diese beiden Sichtweisen müssen zusammenpassen.',steps:[
  ['Den Ursprung prüfen','Bezieht sich die Rücksendung auf einen Einkauf oder einen Verkauf? Suche den ursprünglichen Beleg und prüfe, ob die Rechnung offen oder bereits bezahlt ist.',['ursprünglicher Geschäftsvorfall','Einkauf oder Verkauf?','Rechnungsstatus']],
  ['Menge und Zustand klären','Zurückkommende Erzeugnisse müssen geprüft werden. Ihre Bestandswirkung hängt davon ab, ob und mit welchem Wert sie wieder verwendbar sind.',['Ware kommt zurück','Zustand prüfen','Bestandswert gesondert ermitteln']],
  ['Abrechnung korrigieren','Eine bestätigte Rechnungskorrektur betrifft Nettowert und zugehörige Steuer. Die ursprüngliche Wirkung wird für den zurückgenommenen Teil umgekehrt.',['bestätigte Korrektur','Nettowert und Steuer','betroffene Konten vermindern']],
  ['Den Geldfluss gesondert betrachten','Bei einer offenen Rechnung kann sich der Zahlungsanspruch ändern, ohne dass Geld fließt. Bei bereits bezahlten Rechnungen ist eine mögliche Erstattung ein eigener Schritt.',['offene Rechnung?','Forderung / Verbindlichkeit prüfen','Zahlung separat prüfen']]
 ]},
 accrual:{title:'Warum grenzen wir Erfolg zeitlich ab?',why:'Der Erfolg eines Jahres soll die Leistung dieses Jahres zeigen. Der Zahlungstag allein reicht dafür nicht aus.',steps:[
  ['Zahlung und Leistungszeitraum trennen','Markiere Zahlungstag und Zeitraum, für den bezahlt wurde. Prüfe dann, welcher Teil in das aktuelle Jahr und welcher ins Folgejahr gehört.',['Zahlungstag','Leistungszeitraum','Jahresgrenze']],
  ['Ausgabe vor dem Stichtag, Aufwand danach','Bei vorausbezahlter Nutzung wird ein bereits erfasster Aufwand für das Folgejahr zunächst abgegrenzt. Die aktive Rechnungsabgrenzung steht auf der Vermögensseite.',['Ausgabe bereits erfolgt','Aufwand gehört später','ARA']],
  ['Einnahme vor dem Stichtag, Ertrag danach','Eine bereits erhaltene Zahlung kann eine Leistung des Folgejahres betreffen. Der vorzeitig erfasste Ertrag wird über die passive Rechnungsabgrenzung verschoben.',['Einnahme bereits erfolgt','Ertrag gehört später','PRA']],
  ['Im richtigen Jahr auflösen','Die Bildung und spätere Auflösung der Abgrenzung ordnen den Erfolg zu. Die bereits erfolgte Zahlung wird dabei nicht wiederholt.',['Abgrenzung am Stichtag','Auflösung in der Leistungsperiode','keine zweite Zahlung']]
 ]}
};
const RECEIPTS=[
 {id:'deposit',min:4,reference:'OS-BE-01',date:'2026-12-31',kind:'Einzahlungsbeleg',partner:'BioCasa GmbH · Kasse / Geschäftskonto',title:'Bargeld auf das Geschäftskonto eingezahlt',text:'Christian nimmt 200 € aus der Barkasse und zahlt sie auf das Geschäftskonto ein. Kassen- und Banknachweis bestätigen beide Bewegungen.',lines:[['Bargeldeinzahlung',20000]],total:20000,netModel:true,entryText:'Übungsbeleg · Bargeldeinzahlung auf Bank'},
 {id:'furniture',min:4,reference:'OS-BE-02',date:'2026-12-31',kind:'Kaufbeleg mit Zahlungsnachweis',partner:'KüstenKontor Büroausstattung · fiktiver Lieferant',title:'Büromöbel für BioCasa',text:'Neue Büromöbel werden geliefert und sofort per Bank bezahlt. Sie werden längerfristig im Betrieb genutzt.',lines:[['Büromöbel · bestätigter Positionswert',120000]],total:120000,netModel:true,entryText:'Übungsbeleg · Büromöbel per Bank'},
 {id:'rent',min:4,reference:'OS-BE-03',date:'2026-12-31',kind:'Mietabrechnung mit Banknachweis',partner:'Schirumer Gewerbehof · fiktiver Vermieter',title:'Hallenmiete für Dezember',text:'Die Nutzung der Halle betrifft vollständig den laufenden Dezember. BioCasa hat den Betrag per Bank überwiesen.',lines:[['Hallenmiete Dezember',100000]],total:100000,netModel:true,entryText:'Übungsbeleg · laufende Hallenmiete'},
 {id:'sale',min:4,reference:'OS-BE-04',date:'2026-12-31',kind:'Ausgangsbeleg · Lieferung auf Ziel',partner:'Frischemarkt Nord · fiktiver Kunde',title:'Eigene Bio-Pizzen geliefert',text:'Die Lieferung eigener Erzeugnisse an den Einzelhändler ist bestätigt. Der Kunde bezahlt später. Dieser Beleg betrachtet nur die Ausgangsrechnung; eine Bestandsentnahme ist separat zu erfassen.',lines:[['Eigene Bio-Pizzen · Lieferwert',60000]],total:60000,netModel:true,entryText:'Übungsbeleg · eigene Erzeugnisse auf Ziel'},
 {id:'truck',min:5,reference:'OS-BE-05',date:'2026-12-31',kind:'Eingangsrechnung mit Banknachweis',partner:'KüstenMobil Nutzfahrzeuge · fiktiver Lieferant',title:'Kühltransporter gekauft und bezahlt',text:'BioCasa übernimmt einen Kühltransporter. Die Rechnung wurde vollständig über die Bank beglichen. Die ausgewiesene Vorsteuer ist im Übungsfall vollständig abzugsfähig.',lines:[['Kühltransporter · netto',4000000],['Umsatzsteuer laut Eingangsrechnung · 19 %',760000]],total:4760000,entryText:'Übungsbeleg · Kühltransporter mit Vorsteuer'},
 {id:'energy',min:5,reference:'OS-BE-06',date:'2026-12-31',kind:'Eingangsrechnung mit Banknachweis',partner:'Nordstrom Gewerbe · fiktiver Versorger',title:'Energie für die Produktion',text:'Die berechnete Energie wurde im laufenden Monat verbraucht. BioCasa bezahlt die Rechnung per Bank. Die Vorsteuer ist im Übungsfall vollständig abzugsfähig.',lines:[['Energieverbrauch · netto',60000],['Umsatzsteuer laut Eingangsrechnung · 19 %',11400]],total:71400,entryText:'Übungsbeleg · laufender Energieverbrauch'}
];
const RECEIPT_LINES={deposit:[B.L('280',20000),B.L('288',0,20000)],furniture:[B.L('087',120000),B.L('280',0,120000)],rent:[B.L('670',100000),B.L('280',0,100000)],sale:[B.L('240',60000),B.L('5000',0,60000)],truck:[B.L('084',4000000),B.L('260',760000),B.L('280',0,4760000)],energy:[B.L('605',60000),B.L('260',11400),B.L('280',0,71400)]};
function receiptPosted(state,id){const c=RECEIPTS.find(c=>c.id===id),j=B.journal(state);return !!c&&j.some(e=>e.reference===c.reference&&!e.reversalOf&&!j.some(r=>r.reversalOf===e.id));}
if(root.BioCasaData){RECEIPTS.splice(0,RECEIPTS.length,...root.BioCasaData.current.receipts.map(r=>({...r,lines:r.lines.map(l=>[l[0],root.BioCasaData.amount(l[1])]),total:root.BioCasaData.amount(r.total)})));for(const r of root.BioCasaData.current.receipts)RECEIPT_LINES[r.id]=r.posting.map(l=>B.L(l[0],root.BioCasaData.amount(l[1]),root.BioCasaData.amount(l[2])));}
function receiptLines(id){return B.clone(RECEIPT_LINES[id]||[]);}
function checkReceipt(id,draft){const expected=RECEIPT_LINES[id];if(!expected)return false;const net=lines=>Object.fromEntries([...new Set(lines.map(l=>l.account))].sort().map(a=>[a,B.sum(lines.filter(l=>l.account===a),l=>l.debit-l.credit)]).filter(r=>r[1]!==0));return JSON.stringify(net(draft.lines))===JSON.stringify(net(expected));}
const BALANCE_DEMOS=[
 {id:'assetSwap',title:'Aktivtausch',story:'BioCasa zahlt 200 € aus einer vorhandenen Barkasse auf das Bankkonto ein. Vermögen wird umgeschichtet.',lines:[B.L('280',20000),B.L('288',0,20000)],why:'Ein Aktivposten steigt, ein anderer sinkt um denselben Betrag. Die Bilanzsumme bleibt gleich.'},
 {id:'liabilitySwap',title:'Passivtausch',story:'Eine Lieferantenschuld über 400 € wird durch ein Bankdarlehen abgelöst. Die Bank zahlt direkt an den Lieferanten; das Geschäftskonto wird nicht berührt.',lines:[B.L('440',40000),B.L('425',0,40000)],why:'Eine Schuld sinkt, eine andere steigt um denselben Betrag. Die Bilanzsumme bleibt gleich.'},
 {id:'increase',title:'Aktiv-Passiv-Mehrung',story:'BioCasa erhält eine Verpackungsanlage für 300 € auf Ziel. Sie ist noch nicht bezahlt. Steuern sind in diesem Grundlagenmodell ausgeblendet.',lines:[B.L('076',30000),B.L('440',0,30000)],why:'Vermögen und Schulden steigen um denselben Betrag. Die Bilanz wird länger.'},
 {id:'decrease',title:'Aktiv-Passiv-Minderung',story:'BioCasa tilgt 200 € eines Darlehens per Bank. Es sind ausschließlich Tilgung und keine Zinsen enthalten.',lines:[B.L('425',20000),B.L('280',0,20000)],why:'Vermögen und Schulden sinken um denselben Betrag. Die Bilanz wird kürzer.'}
];
function classifyEffect(effect){
 const delta=effect.after.assets-effect.before.assets,profit=effect.after.profit-effect.before.profit,changes=effect.changes.filter(a=>a.delta);
 if(profit)return {id:'success',title:'Erfolgswirksame Buchung',note:'Der Erfolg verändert sich um '+(profit/100).toLocaleString('de-DE')+' €. Er erscheint zusätzlich im Eigenkapital. Zahlung und Bilanzsumme gesondert betrachten.'};
 if(delta>0)return {id:'increase',title:'Aktiv-Passiv-Mehrung',note:'Die Summen auf beiden Bilanzseiten steigen gleich stark. Die Bilanzsumme nimmt zu.'};
 if(delta<0)return {id:'decrease',title:'Aktiv-Passiv-Minderung',note:'Die Summen auf beiden Bilanzseiten sinken gleich stark. Die Bilanzsumme nimmt ab.'};
 if(changes.length&&changes.every(a=>a.type==='asset'))return {id:'assetSwap',title:'Aktivtausch',note:'Aktivposten werden wertgleich umgeschichtet. Die Bilanzsumme bleibt gleich.'};
 if(changes.length&&changes.every(a=>['liability','equity'].includes(a.type)))return {id:'liabilitySwap',title:'Passivtausch',note:'Passivposten werden wertgleich umgeschichtet. Die Bilanzsumme bleibt gleich.'};
 return {id:'mixed',title:changes.length?'Zusammengesetzte Bilanzveränderung':'Keine Bilanzveränderung',note:'Die Bilanzsumme bleibt gleich. Prüfe die Veränderungen der einzelnen Positionen.'};
}
function balanceDemo(id){
 const c=BALANCE_DEMOS.find(c=>c.id===id)||BALANCE_DEMOS[0];
 const balances=Object.fromEntries(B.ACCOUNTS.map(a=>[a.id,0]));Object.assign(balances,{'280':100000,'288':50000,'076':100000,'300':150000,'425':60000,'440':40000});
 const snap=values=>{const assets=B.sum(B.ACCOUNTS.filter(a=>a.type==='asset'),a=>values[a.id]),liabilities=B.sum(B.ACCOUNTS.filter(a=>a.type==='liability'),a=>values[a.id]),equity=values['300'];return {balances:values,assets,liabilities,bookedEquity:equity,equity,passives:liabilities+equity,profit:0};};
 const before=snap({...balances});for(const l of c.lines)balances[l.account]+=(B.byId[l.account].type==='asset'?1:-1)*(l.debit-l.credit);const after=snap(balances);
 return {case:c,before,after,changes:B.ACCOUNTS.filter(a=>before.balances[a.id]!==after.balances[a.id]).map(a=>({...a,before:before.balances[a.id],after:after.balances[a.id],delta:after.balances[a.id]-before.balances[a.id]}))};
}
function previewRows(state,rows){
 const lines=[];let pending=0;
 for(const r of rows){try{if(!B.byId[r.account]||!['debit','credit'].includes(r.side))throw Error();const amount=B.money(r.amount);if(amount<=0)throw Error();lines.push(B.L(r.account,r.side==='debit'?amount:0,r.side==='credit'?amount:0));}catch{pending++;}}
 const before=B.snapshot(state),after=B.snapshot({...state,entries:[...state.entries,{id:Math.max(0,...B.journal(state).map(e=>e.id))+1,date:B.PERIOD.end,text:'Vorschau',reference:'',lines,movement:null}]}),debit=B.sum(lines,l=>l.debit),credit=B.sum(lines,l=>l.credit);
 return {before,after,lines,pending,debit,credit,balanced:lines.length>=2&&pending===0&&debit===credit&&debit>0,changes:B.ACCOUNTS.filter(a=>before.balances[a.id]!==after.balances[a.id]).map(a=>({...a,before:before.balances[a.id],after:after.balances[a.id],delta:after.balances[a.id]-before.balances[a.id]})),warnings:['280','288'].filter(id=>after.balances[id]<0).map(id=>'Die gewählte Buchung würde '+B.byId[id].name+' ins Minus bringen. Prüfe den verfügbaren Bestand.')};
}
function previewDecision(state,id,input,c){const amounts={accounts:{a:200,b:5000},income:{a:1000,b:600}};return previewRows(state,c.targets.map(t=>({account:input[t.prefix+'a']||'',side:input[t.prefix+'s']==='d'?'debit':input[t.prefix+'s']==='c'?'credit':'',amount:String(amounts[id][c.id])})));}
root.BioCasaDidactics=Object.freeze({POSITIONS,ZERO,EXTRA,KINDS,CODES,inventoryModel,balanceModel,DECISIONS,QUESTION_PARTS,decisionFields,decisionAnswers,checkDecisions,HELPS,RECEIPTS,receiptLines,checkReceipt,receiptPosted,BALANCE_DEMOS,classifyEffect,balanceDemo,previewRows,previewDecision});
})(globalThis);
