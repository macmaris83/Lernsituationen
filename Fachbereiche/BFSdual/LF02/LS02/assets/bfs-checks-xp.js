(() => {
  'use strict';
  const api = window.GB;
  const office = window.BFS_OFFICE_XP;
  const ui = window.SOZ_POINTS_UI;
  if (!ui || (!api && !office)) return;
  const config = window.BFS_XP || {};
  const share = (total, count, index) => count > 0 && index >= 0
    ? (Math.floor(total*100/count) + (index < total*100 % count ? 1 : 0))/100 : 0;
  if (!document.querySelector('.navigation,.b-phase-overview') && document.querySelector('fieldset[data-edit-check]')) {
    const mount=document.createElement('div');mount.className='b-phase-overview no-print';
    document.querySelector('main')?.prepend(mount);
  }
  const roots = () => [...document.querySelectorAll('fieldset[data-situation-question]')];

  for (const card of roots()) {
    card.addEventListener('change',event=>{
      const choice=event.target.closest('input[type="radio"]');
      if (choice) api.answerSituation(card.dataset.situationQuestion,Number(choice.value),Number(card.dataset.right));
    });
  }

  function badge(anchor, points, earned, title) {
    let box=anchor.querySelector(':scope > [data-bfs-xp]');
    if (!box) {
      box=document.createElement('span');box.dataset.bfsXp='';
      box.className='task-point-value no-print';anchor.append(box);
    }
    const key=points+':'+earned;
    if (box.dataset.value!==key) {
      box.dataset.value=key;
      box.replaceChildren(ui.badge(points,earned,title));
    }
  }

  function render() {
    if (!api) {
      const grade=office();
      ui.render(grade);
      const cards=[...document.querySelectorAll('#quiz0 fieldset')];
      cards.forEach((card,i)=>badge(card.querySelector('legend'),share(60,cards.length,i),grade.correct[i],'XP für diese Frage'));
      return;
    }
    const state=api.snapshot();
    const required=window.GB_REQUIREMENTS;
    const situation=required.responses || [];
    const tasks=[...required.common.filter(id=>!situation.includes(id)), ...(required[state.path] || required.A || [])];
    const persisted=state.responses;
    let points=tasks.reduce((sum,id,i)=>sum+(state.done.includes(id)?share(25,tasks.length,i):0),0);
    points+=situation.reduce((sum,id,i)=>{
      if (!state.done.includes(id)) return sum;
      const first=String(persisted[id] || '').split(':')[1];
      return sum + share(15,situation.length,i)*(first==='0' ? .6:1);
    },0);
    const corrections=config.terms.map(({answer,key})=>Number(window.BFS_EDITOR?.current.checks[key]?.correct ?? answer));
    points+=corrections.reduce((sum,right,i)=>{
      if (state.check?.[i]!==right) return sum;
      const first=state.checkFirst?.[i] ?? state.check?.[i];
      return sum + share(60,corrections.length,i)*(first===right?1:.6);
    },0);
    ui.render({points:Math.round(points*100)/100,maxPoints:100});
    for (const card of roots()) {
      const id=card.dataset.situationQuestion;
      const response=persisted[id];
      const choice=typeof response==='string' && response.startsWith('mc:') ? Number(response.split(':')[2]) : -1;
      const correct=state.done.includes(id);
      for (const input of card.querySelectorAll('input')) {
        input.checked=Number(input.value)===choice;
        input.disabled=correct || api.readOnly;
      }
      const message=card.querySelector('[data-situation-feedback]');
      message.textContent=correct ? 'Richtig.' : choice>=0 ? 'Die Antwort passt noch nicht. Versuche es erneut.' : '';
      badge(card.querySelector('legend'),share(15,situation.length,situation.indexOf(id)),correct,'XP für diese Frage');
    }
    for (const card of document.querySelectorAll('.assignment-frame[data-task-id]')) {
      let idx=tasks.indexOf(card.dataset.taskId);
      if (idx<0 && card.dataset.path) {
        idx=[...required.common.filter(id=>!situation.includes(id)),...(required[card.dataset.path] || [])].indexOf(card.dataset.taskId);
      }
      for (const node of card.querySelectorAll('.task-summary,.task-focus-panel')) if(idx>=0) {
        badge(node,share(25,tasks.length,idx),state.done.includes(card.dataset.taskId),'XP für diesen Arbeitsauftrag');
      }
    }
    for (const [i,card] of [...document.querySelectorAll('fieldset[data-edit-check]')].entries()) {
      if (!card.matches('[data-edit-check^="begriffstraining.html"]')) continue;
      badge(card.querySelector('legend'),share(60,corrections.length,i),state.check?.[i]===corrections[i],'XP für diesen Fachbegriff');
    }
  }
  window.addEventListener('bfs-progress',render);
  window.addEventListener('bfs-office-progress',render);
  render();
})();
