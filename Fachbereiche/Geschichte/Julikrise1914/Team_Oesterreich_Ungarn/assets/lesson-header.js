(()=>{'use strict';const K=window.SOZ_PROGRESS_CORE,M=window.SOZ_PROGRESS_META;if(!K||!M)return;
// The dedicated term-check bridge owns the sole open-test reminder.
document.querySelectorAll('[data-check-reminder]').forEach(el=>el.remove());delete document.body.dataset.pointsHost;
if(document.querySelector('[data-scorm-frame]'))return;const P=window.SOZ_PROGRESS;if(!P)return;
function render(){if(document.body.dataset.teacher||window.SOZ_TEACHER_VIEW?.active||document.body.dataset.page==='druckansicht.html')return;window.SOZ_POINTS_UI?.render(K.grading(P.read(),M));}
render();window.addEventListener('soz-progress',render);
})();
