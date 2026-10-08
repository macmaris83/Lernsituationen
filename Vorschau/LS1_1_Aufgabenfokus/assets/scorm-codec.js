(()=>{'use strict';
function packed(v){const bytes=window.pako.deflate(JSON.stringify(v));let b='';for(let i=0;i<bytes.length;i+=8192)b+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(b);}
function unpacked(v){return JSON.parse(window.pako.inflate(Uint8Array.from(atob(v),c=>c.charCodeAt(0)),{to:'string'}));}
function dictionary(){const tasks=window.SOZ_PROGRESS_META.tasks,ids=Object.keys(tasks).sort();return {tasks,ids,hash:window.SOZ_PROGRESS_CORE.hash(JSON.stringify(ids.map(id=>[id,tasks[id].signature])))};}
function encode(v){const d=dictionary(),bits=new Uint8Array(Math.ceil(d.ids.length/8));d.ids.forEach((id,i)=>{if(v.t?.[id]===d.tasks[id].signature)bits[i>>3]|=1<<(i%8);});let bin='';for(const b of bits)bin+=String.fromCharCode(b);return 'SOZ3:'+packed({...v,t:undefined,tb:btoa(bin),th:d.hash});}
function decode(v){if(v.startsWith('SOZ2:'))return unpacked(v.slice(5));if(!v.startsWith('SOZ3:'))return JSON.parse(v);const p=unpacked(v.slice(5)),d=dictionary();p.t={};if(p.th===d.hash){const bits=Uint8Array.from(atob(p.tb||''),c=>c.charCodeAt(0));d.ids.forEach((id,i)=>{if((bits[i>>3]||0)&(1<<(i%8)))p.t[id]=d.tasks[id].signature;});}delete p.tb;delete p.th;return p;}
window.SOZ_SCORM_CODEC={encode,decode};
})();
