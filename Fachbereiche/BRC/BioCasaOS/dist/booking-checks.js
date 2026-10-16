/* Vier Verständnisfragen vor dem zweiten Zahlenweg. Nachweise bleiben getrennt vom Fachjournal. */
(function(root){
'use strict';
const B=root.BioCasa;
const TOPICS=['accounts','income','tax','further','returns','accrual'];
const TITLES=['Bestandskonten','Erfolgskonten','Vor- und Umsatzsteuer','Weitere Buchungen','Retouren','Zeitliche Erfolgsabgrenzung'];
const euro=n=>new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR'}).format(n/100);
function hash(text){let n=2166136261;for(const c of text){n^=c.charCodeAt(0);n=Math.imul(n,16777619);}return (n>>>0).toString(36);}
function canonical(lines){return JSON.stringify([...new Set(lines.map(l=>l.account))].sort().map(id=>[id,B.sum(lines.filter(l=>l.account===id),l=>l.debit),B.sum(lines.filter(l=>l.account===id),l=>l.credit)]));}
function topic(lines){const ids=lines.map(l=>l.account);if(ids.some(id=>['290','490','269','489'].includes(id)))return 'accrual';if(ids.includes('480')&&lines.some(l=>l.account==='5000'&&l.debit))return 'returns';if(ids.some(id=>['260','480','483'].includes(id)))return 'tax';if(ids.some(id=>['652','655','5201','5202','210','220'].includes(id)))return 'further';if(ids.some(id=>['expense','revenue'].includes(B.byId[id]?.type)))return 'income';return 'accounts';}
function validate(value){
 if(!Array.isArray(value)||value.length>18)throw Error('Ungültige Buchungschecks.');
 const seen=new Set(),counts={};return value.map(r=>{if(!Array.isArray(r)||r.length!==3||!Number.isInteger(r[0])||r[0]<0||r[0]>=TOPICS.length||!r.slice(1).every(x=>typeof x==='string'&&/^[a-z0-9]{1,7}$/.test(x))||seen.has(r[0]+':'+r[1])||(counts[r[0]]=(counts[r[0]]||0)+1)>3)throw Error('Ungültiger Nachweis eines Buchungschecks.');seen.add(r[0]+':'+r[1]);return [...r];});
}
function identity(context){return [TOPICS.indexOf(context.topic||topic(context.lines)),hash(context.key),hash(canonical(context.lines))];}
function status(state,context){const id=identity(context),rows=state.bookingChecks||[],saved=rows.find(r=>r[0]===id[0]&&r[1]===id[1]),count=rows.filter(r=>r[0]===id[0]).length;return {required:saved?saved[2]!==id[2]:count<3,done:!!saved&&saved[2]===id[2],ordinal:saved?rows.filter(r=>r[0]===id[0]).indexOf(saved)+1:Math.min(3,count+1),topic:TOPICS[id[0]],title:TITLES[id[0]],eligible:!context.expected||canonical(context.lines)===canonical(context.expected)};}
function questions(context){
 const lines=context.expected||context.lines,unique=[...new Set(lines.map(l=>l.account))],name=id=>id+' · '+B.byId[id].name,join=xs=>xs.join('; ');
 const fake=['087','425','280','288','084','440'].find(id=>!unique.includes(id))||B.ACCOUNTS.find(a=>!unique.includes(a.id)).id;
 const accounts=join(unique.map(name)),other=join([...unique.slice(0,-1),fake].map(name));
 const where=(id,wrong=false)=>{const t=B.byId[id].type;if(['expense','revenue'].includes(t))return wrong?'unmittelbar Aktiva':'GuV → Eigenkapital auf der Passivseite';const asset=t==='asset';return (asset!==wrong)?'Aktiva · links':'Passiva · rechts';};
 const sides=join(unique.map(id=>name(id)+' → '+where(id))),swapped=join(unique.map(id=>name(id)+' → '+where(id,true)));
 const delta=id=>B.sum(lines.filter(l=>l.account===id),l=>(['asset','expense'].includes(B.byId[id].type)?1:-1)*(l.debit-l.credit));
 const direction=(id,invert=false)=>name(id)+' → '+(delta(id)===0?'unverändert':(delta(id)>0)!==invert?'Mehrung':'Minderung');
 const changes=join(unique.map(id=>direction(id))),opposite=join(unique.map(id=>direction(id,true)));
 const sentence=(flip=false)=>['debit','credit'].map((side,i)=>{const original=flip?(side==='debit'?'credit':'debit'):side;return (i?'Haben: ':'Soll: ')+join(lines.filter(l=>l[original]>0).map(l=>name(l.account)+' '+euro(l[original])));}).join(' | ');
 const definitions=[
  {id:'accounts',title:'Welche Konten sind an diesem Geschäftsvorfall beteiligt?',correct:accounts,wrong:[other,'Nur '+name(unique[0])],hint:'Zerlege den betrieblichen Vorgang: Welche Werte erhält BioCasa, welche gibt das Unternehmen ab oder schuldet es?'},
  {id:'balance',title:'Welche Bilanzseite ist jeweils betroffen?',correct:sides,wrong:[swapped,'Die Kontoseite Soll ist immer Aktiva, Haben ist immer Passiva.'],hint:'Bestandskonten gehören zu Aktiva oder Passiva. Aufwand und Ertrag verändern das Eigenkapital über die GuV; Soll und Haben sind Kontoseiten.'},
  {id:'change',title:'Welche Konten nehmen zu, welche nehmen ab?',correct:changes,wrong:[opposite,'Alle beteiligten Konten bleiben unverändert.'],hint:'Prüfe jedes Konto einzeln. Mehrung oder Minderung beschreibt die Veränderung des Kontostands, nicht automatisch Soll oder Haben.'},
  {id:'posting',title:'Welche Beträge werden im Soll und welche im Haben gebucht?',correct:sentence(),wrong:[sentence(true),'Alle Beträge werden im Soll gebucht.'],hint:'Leite die Buchungsseite aus Kontoart und Veränderung ab: Aktiv- und Aufwandszugänge im Soll, Passiv- und Ertragszugänge im Haben. Minderungen stehen jeweils gegenüber.'}
 ];
 return definitions.map((q,i)=>{const answers=[q.correct,...q.wrong];const offset=parseInt(hash(context.key+q.id),36)%3;return {...q,options:answers.map((label,n)=>({value:String(n),label})).slice(offset).concat(answers.map((label,n)=>({value:String(n),label})).slice(0,offset))};});
}
function check(context,input){const wrong=questions(context).filter(q=>input[q.id]!=='0');return {ok:!wrong.length,correct:4-wrong.length,total:4,wrong};}
function record(state,context,input){const info=status(state,context),result=check(context,input);if(!info.eligible||!result.ok)return {state:null,result,eligible:info.eligible};const next=B.clone(state),id=identity(context);next.bookingChecks=validate(next.bookingChecks||[]);const index=next.bookingChecks.findIndex(r=>r[0]===id[0]&&r[1]===id[1]);if(index>=0)next.bookingChecks[index]=id;else if(next.bookingChecks.filter(r=>r[0]===id[0]).length<3)next.bookingChecks.push(id);next.revision++;return {state:next,result,eligible:true};}
root.BioCasaChecks=Object.freeze({TOPICS,topic,validate,status,questions,check,record,canonical});
})(globalThis);
