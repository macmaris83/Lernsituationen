(function(){
'use strict';
const e=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const dialog=document.createElement('dialog');dialog.id='sourceReader';
dialog.innerHTML='<div class="source-top"><h2>Fall und Materialien</h2><button type="button" id="sourceClose" aria-label="Materialansicht schließen">Schließen</button></div><label for="sourceSelect">Material auswählen</label><select id="sourceSelect"></select><article id="sourceText"></article>';
document.body.appendChild(dialog);
const materials=[{key:'Handlungssituation',title:'Handlungssituation',text:SOURCES.case},...SOURCES.materials];
const select=dialog.querySelector('select');select.innerHTML=materials.map((m,i)=>`<option value="${i}">${e(m.title)}</option>`).join('');
function show(){const m=materials[Number(select.value)];dialog.querySelector('article').innerHTML=`<h3>${e(m.title)}</h3>`+m.text.split(/\n\n+/).map(p=>`<p>${e(p)}</p>`).join('')+(m.links?.length?'<h4>Originalquellen aus dem Material</h4><ul>'+m.links.map(l=>`<li><a href="${e(l.url)}" target="_blank" rel="noopener noreferrer">${e(l.label)}</a></li>`).join('')+'</ul>':'');dialog.scrollTop=0;}
select.onchange=show;dialog.querySelector('#sourceClose').onclick=()=>dialog.close();
document.addEventListener('click',event=>{if(!event.target.closest('[data-open-sources]'))return;select.value='0';show();dialog.showModal();});
})();
