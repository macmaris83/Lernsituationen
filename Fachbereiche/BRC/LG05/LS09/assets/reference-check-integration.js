(()=>{'use strict';const P=window.SOZ_PROGRESS,K=window.SOZ_PROGRESS_CORE,M=window.SOZ_PROGRESS_META;if(!P||!K||!M)return;
function refresh(){P.render();window.RENO_FLASHCARD_PACKAGE?.mountReminder(document,document.body.dataset.page);}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',refresh,{once:true});else refresh();
window.addEventListener('storage',event=>{if(event.key?.includes('soz-tasks:'))location.reload();});
})();
