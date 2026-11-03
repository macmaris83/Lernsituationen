/* BRC 1.8.3 material access: a single native details menu, never an absolute popup. */
(()=>{'use strict';
function normalize(section){
 if(section.dataset.materialAccessReady)return;
 const grid=section.querySelector('.material-grid,.material-menu');
 if(!grid)return;
 section.dataset.materialAccessReady='true';
 section.classList.add('material-access');
 grid.classList.remove('material-menu');grid.classList.add('material-grid');
 if(!grid.getAttribute('aria-label'))grid.setAttribute('aria-label','Materialien');
 for(const a of grid.querySelectorAll('a.material-link')){
  if(a.querySelector('b'))continue;
  const match=a.textContent.trim().match(/^(M\d+)\s*[·:–-]?\s*(.*)$/s);
  if(!match)continue;
  const number=document.createElement('b');number.textContent=match[1];
  const title=document.createElement('span');title.textContent=' · '+match[2];
  a.replaceChildren(number,title);
 }
}
function scan(){
 if(document.body.dataset.page==='index.html')return;
 document.querySelectorAll('.lesson-content .material-access,.lesson-content .phase-materials').forEach(normalize);
 window.SOZ_MATERIAL_RETURN?.decorate();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
})();
