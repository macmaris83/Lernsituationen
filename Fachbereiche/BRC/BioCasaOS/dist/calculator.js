/* Kleine Plus/Minus-Rechenhilfe. Keine Kontenabfrage oder Aufgabenlösung; die Oberfläche übernimmt nur bestätigte eigene Ergebnisse. */
(function(root){
'use strict';
function create(){
 let input='',total=null,operator=null,expression='',fresh=false,error='';
 const format=n=>new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n/100);
 const reset=()=>{input='';total=null;operator=null;expression='';fresh=false;error='';};
 const view=()=>({display:input||format(total??0),expression,error,value:fresh&&!error?total:null});
 function commit(){
  if(!input)return;
  const [whole,part='']=input.split(','),amount=Number(whole||0)*100+Number(part.padEnd(2,'0'));
  const next=total===null||!operator?amount:operator==='+'?total+amount:total-amount;
  if(!Number.isSafeInteger(next)||Math.abs(next)>999999999999)throw Error('Die Zahl ist zu groß. Lösche die Rechnung mit C.');
  total=next;input='';
 }
 function press(key){
  error='';
  if(key==='clear'){reset();return view();}
  if(/^\d$/.test(key)||key===','){
   if(fresh){reset();}
   if(key===','){if(!input.includes(','))input=(input||'0')+',';}
   else if(input.length<13&&(!input.includes(',')||input.split(',')[1].length<2))input=input==='0'?key:input+key;
  }else if(key==='back'){if(fresh)reset();else input=input.slice(0,-1);}
  else if(key==='+'||key==='-'){
   try{commit();if(total===null)total=0;operator=key;expression=format(total)+' '+(key==='-'?'−':'+');fresh=false;}catch(e){error=e.message;}
  }else if(key==='equals'){
   try{const tail=input;commit();if(total===null)total=0;expression=operator&&tail?expression+' '+tail+' =':expression;operator=null;fresh=true;}catch(e){error=e.message;}
  }
  return view();
 }
 return Object.freeze({press,view});
}
root.BioCasaCalculator=Object.freeze({create});
})(globalThis);
