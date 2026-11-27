'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form[data-export]');
  const roleSelector = document.querySelector('#ansicht');
  const status = document.querySelector('#status');

  const fieldsInView = () => Array.from(form.querySelectorAll('textarea'))
    .filter(field => !field.closest('[hidden]'));

  function showRole() {
    if (!roleSelector) return;
    for (const section of form.querySelectorAll('[data-role]')) {
      section.hidden = section.dataset.role !== roleSelector.value;
    }
    status.textContent = '';
  }

  function updatePrintText() {
    for (const field of fieldsInView()) {
      const copy = document.getElementById(field.id + '-druck');
      copy.textContent = field.value.trim();
    }
  }

  function saveText() {
    const lines = [document.querySelector('h1').textContent, 'Global Bike · BFS dual · Lernfeld 6 · LS 6.1'];
    if (roleSelector) lines.push(roleSelector.selectedOptions[0].textContent);
    for (const field of fieldsInView()) {
      lines.push('', field.labels[0].textContent.trim(), field.value.trim() || '____________________________');
    }
    const filename = roleSelector ? 'Peer-Check-' + roleSelector.value : form.dataset.export;
    const file = new Blob(['\uFEFF' + lines.join('\n') + '\n'], {type:'text/plain;charset=utf-8'});
    const url = URL.createObjectURL(file);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename + '.txt';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
    status.textContent = 'Die Textdatei steht im Download Ihres Browsers bereit.';
  }

  roleSelector?.addEventListener('change', showRole);
  showRole();
  for (const field of form.querySelectorAll('textarea')) {
    const copy = document.createElement('div');
    copy.className = 'druckantwort';
    copy.id = field.id + '-druck';
    field.after(copy);
  }
  form.addEventListener('input', () => { status.textContent = ''; });
  window.addEventListener('beforeprint', updatePrintText);
  document.querySelector('#drucken').addEventListener('click', () => {
    updatePrintText();
    window.print();
  });
  document.querySelector('#datei').addEventListener('click', saveText);
  form.addEventListener('submit', event => event.preventDefault());
});
