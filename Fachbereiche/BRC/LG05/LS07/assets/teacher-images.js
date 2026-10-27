(()=>{'use strict';if(!document.body.dataset.teacher)return;
const editor=document.querySelector('[data-page-editor]'),save=document.querySelector('[data-save-page]');if(!editor||!save)return;
const details=document.createElement('details');details.className='teacher-card';details.innerHTML='<summary>Bilder auf dieser Seite</summary><div class="teacher-image-list"></div>';save.closest('section').append(details);const list=details.querySelector('div');
function refresh(){
 list.replaceChildren();const images=[];
 for(const image of editor.querySelectorAll('img:not(.book-ref-icon):not(.assignment-goodnotes)'))images.push({image,src:image.src,alt:image.alt});
 for(const frame of editor.querySelectorAll('iframe[srcdoc]')){const doc=new DOMParser().parseFromString(frame.srcdoc,'text/html');[...doc.images].forEach((image,index)=>images.push({frame,index,src:image.getAttribute('src'),alt:image.alt}));}
 if(!images.length){list.textContent='Auf dieser Seite sind keine austauschbaren Bilder vorhanden.';return;}
 for(const record of images){const row=document.createElement('label');row.className='teacher-image-row';const preview=document.createElement('img');preview.src=record.src;preview.alt=record.alt||'Bildvorschau';const field=document.createElement('span');const name=document.createElement('span');name.textContent=record.alt||'Bild';const input=document.createElement('input');input.type='file';input.accept='image/png,image/jpeg,image/webp,image/gif';input.setAttribute('aria-label','Ersatzbild auswählen');field.append(name,input);row.append(preview,field);list.append(row);
 input.addEventListener('change',()=>{const f=input.files[0];if(!f||!/^image\//.test(f.type))return;const reader=new FileReader();reader.onload=()=>{if(record.frame){const doc=new DOMParser().parseFromString(record.frame.srcdoc,'text/html');doc.images[record.index].src=reader.result;record.frame.srcdoc='<!doctype html>'+doc.documentElement.outerHTML;}else{record.image.src=reader.result;record.image.removeAttribute('srcset');const slot=record.image.closest('[data-media-key]');if(slot){const id=slot.dataset.mediaKey,settings=window.SOZ_API.getSettings();settings.media={...(settings.media||{}),[id]:{src:reader.result,alt:record.alt}};window.SOZ_API.saveSettings();}}preview.src=reader.result;};reader.readAsDataURL(f);});}
}
details.addEventListener('toggle',()=>{if(details.open)refresh();});document.querySelector('[data-edit-page]').addEventListener('change',refresh);document.querySelector('[data-reset-page]').addEventListener('click',()=>setTimeout(refresh,0));
})();
