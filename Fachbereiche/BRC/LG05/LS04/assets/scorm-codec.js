/* Lossless SCORM 1.2 state compression. SOZ2 remains readable; SOZ3 groups
   identical JSON structures and delta-encodes integer columns such as timestamps.
   Answer history, queue, feedback, score and learner reflections are preserved. */
(()=>{'use strict';
const compress=value=>{const bytes=window.pako.deflate(JSON.stringify(value),{level:9});let bin='';for(let i=0;i<bytes.length;i+=8192)bin+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(bin);};
const expand=value=>JSON.parse(window.pako.inflate(Uint8Array.from(atob(value),c=>c.charCodeAt(0)),{to:'string'}));
function pack(value){
 const strings=[],stringIds=new Map(),schemas=[],schemaIds=new Map(),groups=[],ids=new Map(),active=new Set();
 const string=s=>{if(!stringIds.has(s)){stringIds.set(s,strings.length);strings.push(s);}return stringIds.get(s);};
 function visit(v){
  if(v===null||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return v;
  if(typeof v==='string')return[-1,string(v)];
  if(!v||typeof v!=='object'||active.has(v))throw Error('Nicht speicherbarer Paketfortschritt.');
  active.add(v);const key=JSON.stringify(v);if(ids.has(key)){active.delete(v);return ids.get(key);}
  const array=Array.isArray(v),keys=array?null:Object.keys(v),schemaKey=JSON.stringify(keys);let schema;
  if(!schemaIds.has(schemaKey)){schema=schemas.length;schemaIds.set(schemaKey,schema);schemas.push(keys&&keys.map(string));groups.push([]);}else schema=schemaIds.get(schemaKey);
  const row=groups[schema].length,ref=[schema,row];ids.set(key,ref);groups[schema].push(null);
  groups[schema][row]=array?v.map(visit):keys.map(k=>visit(v[k]));active.delete(v);return ref;
 }
 function column(values){
  if(values.length<3||!values.every(Number.isSafeInteger))return values;
  const deltas=values.map((n,i)=>i?n-values[i-1]:n);return deltas.every(Number.isSafeInteger)?['d',...deltas]:values;
 }
 const root=visit(value),tables=groups.map((rows,i)=>schemas[i]===null?[null,rows]:[schemas[i],schemas[i].map((_,k)=>column(rows.map(row=>row[k])))]);
 return[strings,tables,root];
}
function unpack(payload){
 if(!Array.isArray(payload)||payload.length!==3||!Array.isArray(payload[0])||!Array.isArray(payload[1]))throw Error('Ungültiger gespeicherter Paketfortschritt.');
 const[strings,tables,root]=payload,active=new Set();
 const string=id=>{if(!Number.isInteger(id)||id<0||id>=strings.length||typeof strings[id]!=='string')throw Error('Ungültiger Textverweis im Paketfortschritt.');return strings[id];};
 const expanded=tables.map(table=>{if(!Array.isArray(table)||table.length!==2||!Array.isArray(table[1]))throw Error('Ungültige gespeicherte Tabelle.');if(table[0]===null)return table;return[table[0],table[1].map(column=>{if(!Array.isArray(column))throw Error('Ungültige gespeicherte Spalte.');if(column[0]!=='d')return column;let sum=0;return column.slice(1).map(v=>{if(!Number.isSafeInteger(v))throw Error('Ungültiger gespeicherter Zahlenwert.');sum+=v;if(!Number.isSafeInteger(sum))throw Error('Ungültige gespeicherte Zahl.');return sum;});})];});
 function visit(v){
  if(v===null||typeof v==='boolean'||typeof v==='number')return v;
  if(!Array.isArray(v)||v.length!==2||!Number.isInteger(v[0])||!Number.isInteger(v[1]))throw Error('Ungültiger Verweis im Paketfortschritt.');
  if(v[0]===-1)return string(v[1]);const schema=v[0],row=v[1],key=schema+':'+row;
  if(schema<0||schema>=expanded.length||row<0||active.has(key))throw Error('Ungültige gespeicherte Struktur.');active.add(key);
  const[fields,columns]=expanded[schema];let out;
  if(fields===null){if(!Array.isArray(columns[row]))throw Error('Ungültige gespeicherte Liste.');out=columns[row].map(visit);}
  else{if(!Array.isArray(fields)||fields.length!==columns.length||fields.length&&row>=columns[0].length)throw Error('Ungültiges gespeichertes Objekt.');out={};for(let i=0;i<fields.length;i++)Object.defineProperty(out,string(fields[i]),{value:visit(columns[i][row]),enumerable:true,writable:true,configurable:true});}
  active.delete(key);return out;
 }
 return visit(root);
}
function encode(value){const standard='SOZ2:'+compress(value),compact='SOZ3:'+compress(pack(value));return compact.length<standard.length?compact:standard;}
function decode(value){if(value.startsWith('SOZ3:'))return unpack(expand(value.slice(5)));if(value.startsWith('SOZ2:'))return expand(value.slice(5));return JSON.parse(value);}
window.SOZ_SCORM_CODEC={encode,decode};
})();
