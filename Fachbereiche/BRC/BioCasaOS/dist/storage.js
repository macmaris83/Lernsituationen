/* SCORM 1.2 + lokaler Übungsmodus. Keine externen Dienste oder Bibliotheken. */
(function(root){
'use strict';
function compress(input){
 const bytes=new TextEncoder().encode(input);if(bytes.length>250000)throw Error('Übungsstand zu groß.');
 let dict,next,codes=[256],word='';const reset=()=>{dict=new Map();for(let i=0;i<256;i++)dict.set(String.fromCharCode(i),i);next=258;};reset();
 for(const byte of bytes){const ch=String.fromCharCode(byte),both=word+ch;if(dict.has(both)){word=both;continue;}codes.push(dict.get(word));if(next<4096)dict.set(both,next++);else{codes.push(256);reset();}word=ch;}
 if(word)codes.push(dict.get(word));codes.push(257);
 let accum=0,bits=0,out='';for(const code of codes){accum=(accum<<12)|code;bits+=12;while(bits>=8){bits-=8;out+=String.fromCharCode((accum>>bits)&255);accum&=(1<<bits)-1;}}if(bits)out+=String.fromCharCode((accum<<(8-bits))&255);
 return 'BC1:'+btoa(out);
}
function decompress(input){
 if(typeof input!=='string'||!input.startsWith('BC1:')||input.length>200000)throw Error('Unbekanntes Speicherformat.');
 const raw=atob(input.slice(4));let dict,next,old='',out='',accum=0,bits=0,done=false;
 const reset=()=>{dict=Array.from({length:256},(_,i)=>String.fromCharCode(i));next=258;old='';};reset();
 for(let i=0;i<raw.length&&!done;i++){accum=(accum<<8)|raw.charCodeAt(i);bits+=8;if(bits<12)continue;bits-=12;const code=(accum>>bits)&4095;accum&=(1<<bits)-1;
  if(code===256){reset();continue;}if(code===257){done=true;break;}
  const word=dict[code]??(code===next&&old?old+old[0]:null);if(word===null)throw Error('Beschädigter Übungsstand.');
  out+=word;if(out.length>250000)throw Error('Übungsstand überschreitet das Leselimit.');if(old&&next<4096)dict[next++]=old+word[0];old=word;
 }
 if(!done)throw Error('Unvollständiger Übungsstand.');
 return new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(out,c=>c.charCodeAt(0)));
}
function findAPI(start){
 const scan=w=>{const seen=new Set();for(let n=0;w&&n<25&&!seen.has(w);n++){seen.add(w);try{if(w.API&&typeof w.API.LMSInitialize==='function')return w.API;if(w.parent===w)break;w=w.parent;}catch{break;}}return null;};
 const found=scan(start);if(found)return found;try{return start.opener?scan(start.opener):null;}catch{return null;}
}
function createStorage(win){
 const B=root.BioCasa;let api=root.BioCasaTeacherPreview?null:findAPI(win),connected=false,finished=false,blocked=false,lastState=null,beforeFlush=null;const initFailed=!!api;const start=Date.now();
 let status={kind:'local',text:'Browsermodus',detail:'Dein Stand wird nur in diesem Browser gespeichert. In Moodle wird er dem laufenden Versuch zugeordnet.'};
 const ok=x=>x===true||x==='true';const call=(method,...args)=>{try{return api?.[method](...args);}catch{return false;}};
 if(api&&ok(call('LMSInitialize',''))){connected=true;status={kind:'lms',text:'Moodle verbunden',detail:'Dein Übungsstand wird im aktuellen Moodle-Versuch gespeichert.'};}else{api=null;if(initFailed)status={kind:'error',text:'Moodle-Verbindung fehlgeschlagen',detail:'Die Moodle-Schnittstelle hat den Start nicht bestätigt. Sichere Änderungen über Export; sie können derzeit nur lokal gespeichert werden.'};}
 let mode='normal';if(connected)mode=call('LMSGetValue','cmi.core.lesson_mode')||'normal';
 const readOnly=mode==='browse'||mode==='review';
 if(readOnly)status={kind:'local',text:'Moodle-Vorschau',detail:'Du bist im Vorschau- oder Wiederholungsmodus. Änderungen werden nur lokal gesichert; für einen persönlichen Stand die Aktivität als laufenden Versuch öffnen.'};
 const id=connected?String(call('LMSGetValue','cmi.core.student_id')||'anonymous'):'preview';
 const learnerName=connected?String(call('LMSGetValue','cmi.core.student_name')||''):'';
 const key='biocasa-os-v1:'+win.location.pathname+':'+id+':'+mode+(root.BioCasaData&&!root.BioCasaData.legacyCompatible?':'+root.BioCasaData.identity:'')+(root.BioCasaTeacherPreview?':teacher-preview':'');
 const localGet=()=>{try{return win.localStorage.getItem(key);}catch{return null;}};
 const localSet=x=>{try{win.localStorage.setItem(key,x);return true;}catch{return false;}};
 function notify(){if(typeof win.dispatchEvent==='function')win.dispatchEvent(new win.CustomEvent('biocasa-storage',{detail:status}));}
 function load(){
  const encoded=connected?call('LMSGetValue','cmi.suspend_data'):localGet();
  if(encoded===false&&connected){blocked=true;status={kind:'error',text:'Moodle-Stand nicht lesbar',detail:'Die Schnittstelle hat den vorhandenen Stand nicht bestätigt. Er wird nicht überschrieben. Bitte die Aktivität neu öffnen oder eine Sicherung importieren.'};lastState=B.newState();return lastState;}
  if(!encoded||encoded===false){lastState=B.newState();return lastState;}
  try{lastState=B.unpack(JSON.parse(decompress(encoded)));return lastState;}catch(e){
   blocked=connected&&!readOnly;status={kind:'error',text:'Stand konnte nicht geladen werden',detail:(e.message||'Der gespeicherte Stand ist nicht lesbar.')+' Importiere eine Sicherung oder starte bewusst neu. Der alte Moodle-Stand wird bis dahin nicht überschrieben.'};lastState=B.newState();return lastState;
  }
 }
 function sessionTime(){const c=Math.floor((Date.now()-start)/10),h=Math.floor(c/360000),m=Math.floor(c/6000)%60,s=Math.floor(c/100)%60;return String(Math.min(9999,h)).padStart(4,'0')+':'+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')+'.'+String(c%100).padStart(2,'0');}
 function encode(s){return compress(JSON.stringify(B.pack(s)));}
 function assertFits(s){const encoded=encode(s);if(connected&&!readOnly&&encoded.length>4096)throw Error('Der Speicher dieses Moodle-Versuchs ist voll. Diese Änderung wurde nicht in Moodle übernommen. Sichere deinen Stand über Export.');return encoded;}
 function save(s,{unlock=false}={}){
  if(unlock)blocked=false;
  if(blocked)throw Error('Bitte zuerst eine Sicherung importieren oder den Versuch über „Neustart“ bewusst zurücksetzen.');
  const encoded=assertFits(s);lastState=s;const local=localSet(encoded);
  if(connected&&!readOnly&&!finished){
   const tasks=B.taskStatus(s),complete=root.BioCasaLearning?root.BioCasaLearning.progress(s).complete:tasks.bank&&tasks.stock&&tasks.analysis;
   const results=[call('LMSSetValue','cmi.suspend_data',encoded),call('LMSSetValue','cmi.core.lesson_location',s.view),call('LMSSetValue','cmi.core.lesson_status',complete?'completed':'incomplete'),call('LMSSetValue','cmi.core.exit','suspend'),call('LMSSetValue','cmi.core.session_time',sessionTime())];
   if(results.every(ok)&&ok(call('LMSCommit','')))status={kind:'lms',text:'In Moodle gespeichert',detail:'Stand und Bearbeitungsstatus sind im laufenden Moodle-Versuch gespeichert. Es wird keine Note übertragen.'};
   else status={kind:'error',text:local?'Nur lokal gesichert':'Speicherung fehlgeschlagen',detail:local?'Moodle hat die Speicherung nicht bestätigt. Sichere den aktuellen Stand über „Export“, bevor du die Aktivität verlässt.':'Der Stand konnte weder in Moodle noch in diesem Browser gesichert werden. Bitte sofort exportieren.'};
  }else if(!local)status={kind:'error',text:'Nicht gespeichert',detail:'Der Browser blockiert die Speicherung. Bitte sichere deinen Stand über „Export“. In einem normalen Moodle-Versuch wird die Moodle-Schnittstelle genutzt.'};
  else if(!connected&&initFailed)status={kind:'error',text:'Nur lokal gesichert',detail:'Die Moodle-Verbindung ist nicht initialisiert. Bitte vor dem Verlassen eine Sicherung exportieren.'};
  else if(!connected)status={kind:'local',text:'Im Browser gespeichert',detail:'Dieser Stand liegt nur in diesem Browser. Für einen Gerätewechsel bitte exportieren und am Zielgerät importieren.'};
  notify();return {encoded,status};
 }
 function flush(){if(blocked||finished)return;try{if(beforeFlush)beforeFlush();if(lastState)save(lastState);}catch{status={kind:'error',text:'Sicherung nicht bestätigt',detail:'Bitte den Stand exportieren, bevor du die Aktivität verlässt.'};notify();}}
 function finish(){if(finished)return;flush();if(connected){call('LMSSetValue','cmi.core.exit','suspend');call('LMSSetValue','cmi.core.session_time',sessionTime());call('LMSCommit','');call('LMSFinish','');}finished=true;}
 if(win.addEventListener){win.addEventListener('beforeunload',flush);win.addEventListener('pagehide',e=>{if(e.persisted)flush();else finish();});}
 const visibilityTarget=win.document?.addEventListener?win.document:win;
 visibilityTarget.addEventListener?.('visibilitychange',()=>{if(win.document?.visibilityState==='hidden')flush();});
 return {load,save,flush,finish,encode,assertFits,connected,readOnly,setBeforeFlush(fn){beforeFlush=fn;},get learnerName(){return learnerName;},get status(){return status;},get capacity(){return lastState?{used:encode(lastState).length,max:4096}:null;}};
}
root.BioCasaStorage={compress,decompress,findAPI,createStorage};
})(globalThis);
