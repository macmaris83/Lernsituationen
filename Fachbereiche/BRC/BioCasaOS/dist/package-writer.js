/* Kleiner ZIP-Writer ohne externe Bibliothek. ZIP32 / gespeicherte Dateien. */
(function(root){
'use strict';
const encoder=new TextEncoder(),table=Array.from({length:256},(_,i)=>{let n=i;for(let j=0;j<8;j++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
function crc(bytes){let n=0xffffffff;for(const b of bytes)n=table[(n^b)&255]^(n>>>8);return (n^0xffffffff)>>>0;}
function zip(files){if(!Array.isArray(files)||!files.length||files.length>1000)throw Error('Ungültige Paketdateien.');const local=[],central=[],seen=new Set();let offset=0;
 for(const file of files){if(!/^[A-Za-z0-9_.\/-]+$/.test(file.name)||file.name.startsWith('/')||file.name.split('/').some(x=>x==='..')||seen.has(file.name))throw Error('Ungültiger Dateiname im Paket.');seen.add(file.name);const name=encoder.encode(file.name),data=typeof file.data==='string'?encoder.encode(file.data):new Uint8Array(file.data);if(data.length>10000000)throw Error('Paketdatei zu groß.');const checksum=crc(data),l=new Uint8Array(30+name.length),v=new DataView(l.buffer);v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint16(6,0x800,true);v.setUint16(12,33,true);v.setUint32(14,checksum,true);v.setUint32(18,data.length,true);v.setUint32(22,data.length,true);v.setUint16(26,name.length,true);l.set(name,30);local.push(l,data);
  const c=new Uint8Array(46+name.length),cv=new DataView(c.buffer);cv.setUint32(0,0x02014b50,true);cv.setUint16(4,20,true);cv.setUint16(6,20,true);cv.setUint16(8,0x800,true);cv.setUint16(14,33,true);cv.setUint32(16,checksum,true);cv.setUint32(20,data.length,true);cv.setUint32(24,data.length,true);cv.setUint16(28,name.length,true);cv.setUint32(42,offset,true);c.set(name,46);central.push(c);offset+=l.length+data.length;
 }
 const size=central.reduce((n,b)=>n+b.length,0),end=new Uint8Array(22),ev=new DataView(end.buffer);ev.setUint32(0,0x06054b50,true);ev.setUint16(8,files.length,true);ev.setUint16(10,files.length,true);ev.setUint32(12,size,true);ev.setUint32(16,offset,true);const result=new Uint8Array(offset+size+22);let at=0;for(const b of [...local,...central,end]){result.set(b,at);at+=b.length;}return result;
}
root.BioCasaPackage=Object.freeze({zip,crc});
})(globalThis);
