(()=>{'use strict';
function encode(value){const bytes=window.pako.deflate(JSON.stringify(value));let bin='';for(let i=0;i<bytes.length;i+=8192)bin+=String.fromCharCode(...bytes.subarray(i,i+8192));return 'SOZ2:'+btoa(bin);}
function decode(value){if(!value.startsWith('SOZ2:'))return JSON.parse(value);const bytes=Uint8Array.from(atob(value.slice(5)),c=>c.charCodeAt(0));return JSON.parse(window.pako.inflate(bytes,{to:'string'}));}
window.SOZ_SCORM_CODEC={encode,decode};
})();
