(()=>{'use strict';
let details=[],groups=[];
window.addEventListener('beforeprint',()=>{
 if(groups.length||details.length)return;
 details=[...document.querySelectorAll('details')].map(el=>[el,el.open]);
 details.forEach(([el])=>el.open=true);
 for(const check of document.querySelectorAll('.phase-check')){
  let section=check.previousElementSibling;
  while(section&&!section.matches('.phase-mode:not([hidden])'))section=section.previousElementSibling;
  if(!section)continue;
  const last=[...section.querySelectorAll('.assignment-frame')].pop();
  if(!last)continue;
  const wrapper=document.createElement('div');wrapper.className='phase-print-end';
  groups.push({wrapper,last,check,parent:check.parentNode,next:check.nextSibling});
  last.before(wrapper);wrapper.append(last,check);
 }
});
window.addEventListener('afterprint',()=>{
 for(const {wrapper,last,check,parent,next}of groups){wrapper.replaceWith(last);parent.insertBefore(check,next);}
 groups=[];details.forEach(([el,open])=>el.open=open);details=[];
});
})();
