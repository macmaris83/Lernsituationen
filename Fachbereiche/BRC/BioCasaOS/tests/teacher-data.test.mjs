import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const dist=new URL('../dist/',import.meta.url),read=name=>fs.readFileSync(new URL(name,dist));
function teacher(){
 const nodes=new Map(),blobs=[];const node=id=>{if(!nodes.has(id))nodes.set(id,{id,value:'',textContent:'',innerHTML:'',hidden:false,disabled:false,handlers:{},addEventListener(k,fn){this.handlers[k]=fn;}});return nodes.get(id);};
 const form=node('teacher-config');form.elements={namedItem:()=>({value:'automatic'})};form.querySelector=()=>({checked:false});const local=new Map(),win={location:{pathname:'/teacher.html'},localStorage:{getItem:k=>local.get(k)||null,setItem:(k,v)=>local.set(k,v)}};
 const doc={getElementById:node,createElement:()=>({click(){},remove(){}}),body:{appendChild(){}}},url={createObjectURL:b=>{blobs.push(b);return 'blob:test';},revokeObjectURL(){}};
 class Parser{parseFromString(text){return {querySelector:()=>null,getElementsByTagName:()=>[...text.matchAll(/<file href="([^"]+)"/g)].map(m=>({getAttribute:()=>m[1]}))};}}
 const c=vm.createContext({window:win,document:doc,console,Intl,Date,JSON,Map,Set,TextEncoder,TextDecoder,Blob,URL:url,DOMParser:Parser,setTimeout(){},fetch:async name=>({ok:true,text:async()=>read(name).toString(),arrayBuffer:async()=>Uint8Array.from(read(name)).buffer})});
 for(const f of ['data-defaults.js','data-config.js','dataset.js','engine.js','course-config.js','release.js','package-writer.js','teacher.js'])vm.runInContext(read(f).toString(),c);
 const upload=async data=>{const text=JSON.stringify(data),input=node('dataset-upload');input.files=[{name:'daten.json',size:Buffer.byteLength(text),text:async()=>text}];await input.handlers.change({target:input});};
 return {c,nodes,node,blobs,upload};
}
function unzipStored(buffer){const files=new Map();let p=0;while(buffer.readUInt32LE(p)===0x04034b50){const size=buffer.readUInt32LE(p+18),nameLength=buffer.readUInt16LE(p+26),extra=buffer.readUInt16LE(p+28),name=buffer.subarray(p+30,p+30+nameLength).toString(),start=p+30+nameLength+extra;files.set(name,buffer.subarray(start,start+size));p=start+size;}return files;}

test('Lehrkräfte-Upload behält die Auswahl bis zur bewussten Übernahme und weist fehlerhafte Dateien zurück',async()=>{
 const a=teacher(),d=a.c.BioCasaData.shiftYear(a.c.BioCasaData.current,2027);await a.upload(d);assert.equal(a.node('dataset-candidate').hidden,false);assert.ok(a.node('dataset-preview').innerHTML.includes('2026/27'));assert.ok(a.node('dataset-candidate').innerHTML.includes('2027/28'));a.node('dataset-accept').handlers.click();assert.ok(a.node('dataset-preview').innerHTML.includes('2027/28'));d.openingBalances['280']++;await a.upload(d);assert.ok(a.node('dataset-feedback').textContent.includes('nicht übernommen'));assert.ok(a.node('dataset-preview').innerHTML.includes('2027/28'));await a.upload(a.c.BioCasaData.defaultConfig);a.node('dataset-cancel').handlers.click();assert.equal(a.node('dataset-candidate').hidden,true);assert.ok(a.node('dataset-preview').innerHTML.includes('2027/28'));
});
test('Konfiguriertes Moodle-Paket enthält die gewählte Datenbasis und Freigabe; Schülerpaket enthält keinen Lehrkräfte-Uploader',async()=>{
 const a=teacher();a.node('dataset-year').value='2027';a.node('dataset-year').handlers.change();await a.node('teacher-config').handlers.submit({preventDefault(){}});assert.equal(a.blobs.length,1);const files=unzipStored(Buffer.from(await a.blobs[0].arrayBuffer()));assert.equal(files.size,27);assert.ok(files.has('calculator.js'));assert.ok(files.has('data-defaults.js'));assert.ok(files.has('dataset.js'));assert.equal(files.has('teacher.html'),false);assert.equal(files.has('teacher.js'),false);assert.equal(files.has('preview.html'),false);const c=vm.createContext({JSON,Map,Set,Intl,Date});for(const name of ['data-defaults.js','data-config.js','dataset.js','engine.js','course-config.js'])vm.runInContext(files.get(name).toString(),c);assert.equal(c.BioCasa.PERIOD.year,2027);assert.equal(c.BioCasaData.current.schoolYear,'2027/28');assert.equal(c.BioCasaCourseConfig.inventar.mode,'automatic');assert.equal(a.node('download-package').disabled,false);
});
