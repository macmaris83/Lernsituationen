(function () {
  'use strict';

  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));
  const glossaryId = value => value.trim().toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, '').replace(/\s+/g, '-');

  function inline(text) {
    const format = value => escape(value).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    let result = '';
    let start = 0;
    for (const match of text.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g)) {
      const [token, label, target] = match;
      result += format(text.slice(start, match.index));
      if (target.startsWith('https://')) {
        result += `<a href="${escape(target)}" target="_blank" rel="noopener noreferrer">${format(label)}</a>`;
      } else if (target.startsWith('#')) {
        result += `<a href="${escape(target)}" data-glossary="${escape(target.slice(1))}">${format(label)}</a>`;
      } else {
        result += format(label);
      }
      start = match.index + token.length;
    }
    return result + format(text.slice(start));
  }

  function table(lines) {
    const cells = line => line.trim().slice(1, -1).split('|').map(cell => cell.trim());
    const header = cells(lines[0]).map(cell => `<th scope="col">${inline(cell)}</th>`).join('');
    const body = lines.slice(2).map(line => {
      return '<tr>' + cells(line).map(cell => `<td>${inline(cell)}</td>`).join('') + '</tr>';
    }).join('');
    return `<div class="source-table" tabindex="0" role="region" aria-label="Materialtabelle"><table><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table></div>`;
  }

  function blocks(text) {
    return text.trim().split(/\n\s*\n/).map(block => {
      const lines = block.split('\n');
      if (lines.length > 1 && lines.every(line => line.startsWith('|'))) return table(lines);
      if (lines.every(line => line.startsWith('- '))) {
        return '<ul>' + lines.map(line => `<li>${inline(line.slice(2))}</li>`).join('') + '</ul>';
      }
      if (lines.every(line => /^\d+\. /.test(line))) {
        return '<ol>' + lines.map(line => `<li>${inline(line.replace(/^\d+\. /, ''))}</li>`).join('') + '</ol>';
      }
      if (lines.every(line => line.startsWith('>'))) {
        const quoted = lines.map(line => inline(line.replace(/^> ?/, ''))).join('<br>');
        return `<blockquote>${quoted}</blockquote>`;
      }
      if (lines.length === 1 && /^#{3,5} /.test(lines[0])) {
        const heading = lines[0].replace(/^#+ /, '');
        return `<h4 data-glossary-id="${escape(glossaryId(heading))}">${inline(heading)}</h4>`;
      }
      return `<p>${lines.map(inline).join('<br>')}</p>`;
    }).join('');
  }

  const dialog = document.createElement('dialog');
  dialog.id = 'sourceReader';
  dialog.setAttribute('aria-labelledby', 'sourceTitle');
  dialog.innerHTML = '<div class="source-top"><h2 id="sourceTitle">Fall und Materialien</h2><button type="button" id="sourceClose">Schließen</button></div><label for="sourceSelect">Material auswählen</label><select id="sourceSelect"></select><article id="sourceText"></article>';
  document.body.appendChild(dialog);

  const materials = [{ key: 'Handlungssituation', title: 'Handlungssituation', text: SOURCES.case }, ...SOURCES.materials];
  const select = dialog.querySelector('select');
  const article = dialog.querySelector('article');
  select.innerHTML = materials.map((material, index) => `<option value="${index}">${escape(material.title)}</option>`).join('');

  function show() {
    const material = materials[Number(select.value)];
    article.innerHTML = `<h3>${escape(material.title)}</h3>` + blocks(material.text);
    dialog.scrollTop = 0;
  }

  select.onchange = show;
  dialog.querySelector('#sourceClose').onclick = () => dialog.close();
  article.addEventListener('click', event => {
    const link = event.target.closest('[data-glossary]');
    if (!link) return;
    event.preventDefault();
    const index = materials.findIndex(material => material.key === 'Glossar');
    if (index < 0) return;
    select.value = index;
    show();
    const anchor = decodeURIComponent(link.dataset.glossary);
    const heading = [...article.querySelectorAll('[data-glossary-id]')].find(node => node.dataset.glossaryId === anchor);
    heading?.scrollIntoView({ block: 'start' });
  });
  document.addEventListener('click', event => {
    if (!event.target.closest('[data-open-sources]')) return;
    select.value = '0';
    show();
    dialog.showModal();
  });
})();
