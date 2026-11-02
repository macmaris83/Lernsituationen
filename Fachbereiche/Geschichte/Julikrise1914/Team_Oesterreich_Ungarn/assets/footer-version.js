/* The displayed release belongs to this package, independent of learner storage versions. */
(()=>{'use strict';
 let version=String(window.SOZ_CONFIG?.packageVersion||'').trim();
 const existing=document.querySelector('[data-package-version]');
 if(!version&&existing)version=existing.textContent.trim().replace(/^Version\s+/i,'');
 let pending=false;
 function render(){pending=false;if(!version)return;const label='Version '+version;document.querySelectorAll('[data-package-version]').forEach(node=>{if(node.textContent!==label)node.textContent=label;});}
 function schedule(){if(!pending){pending=true;queueMicrotask(render);}}
 window.SOZ_PACKAGE_VERSION={get current(){return version;},refresh:render};
 function init(){render();new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});fetch(new URL('Paketversion.json',document.baseURI),{cache:'no-store'}).then(response=>{if(!response.ok)throw new Error('Version unavailable');return response.json();}).then(data=>{if(typeof data.version==='string'&&data.version.trim()){version=data.version.trim().slice(0,80);render();}}).catch(()=>{});}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
