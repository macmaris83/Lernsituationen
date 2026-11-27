(() => {
  'use strict';
  const script = document.currentScript;
  const root = new URL('../', script.src);
  const page = document.body;
  const published = window.BFS_EDITOR_CONFIG || {};
  const key = 'bfs-editor:' + published.id + ':' + root.pathname;
  const preview = new URLSearchParams(location.search).has('bfs-vorschau');
  const safeURL = value => {
    try {
      const url = new URL(value);
      return ['https:', 'http:'].includes(url.protocol) ? url.href : '';
    } catch { return ''; }
  };
  function read() {
    let draft = {};
    try { draft = JSON.parse(localStorage.getItem(key) || '{}'); } catch {}
    return Object.fromEntries(['texts', 'links', 'images', 'checks','references'].map(
      group => [group, {...published[group], ...draft[group]}]
    ));
  }
  function save(settings) { localStorage.setItem(key, JSON.stringify(settings)); }
  function update(container, settings) {
    for (const node of container.querySelectorAll('[data-edit-text]')) {
      const value = settings.texts[node.dataset.editText];
      if (typeof value === 'string') node.textContent = value;
    }
    for (const node of container.querySelectorAll('[data-edit-link]')) {
      const value=settings.references[node.dataset.editLink];
      if (typeof value==='string' && value.trim() && !/^[\s\u0000-\u001f]*[a-z][a-z0-9+.-]*:/i.test(value)) node.setAttribute('href',value);
      else if (safeURL(value)) node.href=safeURL(value);
    }
    for (const node of container.querySelectorAll('[data-edit-moodle]')) {
      const url = safeURL(settings.links[node.dataset.editMoodle]);
      const slot = node.querySelector('a');
      const pending = node.querySelector('span');
      pending.hidden = Boolean(url);
      slot.hidden = !url;
      if (url) slot.href = url;
      else slot.removeAttribute('href');
    }
    for (const node of container.querySelectorAll('img[data-edit-image]')) {
      const value = settings.images[node.dataset.editImage];
      if (!value) continue;
      if (value.file && /^assets\/editor-images\/[a-z0-9-]+\.(png|jpg|gif|webp)$/i.test(value.file)) {
        node.src = new URL(value.file, root);
      } else if (/^data:image\/(png|jpeg|gif|webp);base64,[a-z0-9+/=]+$/i.test(value.src || '')) {
        node.src = value.src;
      }
      if (typeof value.alt === 'string') node.alt = value.alt;
    }
    for (const node of container.querySelectorAll('fieldset[data-edit-check]')) {
      const value = settings.checks[node.dataset.editCheck];
      if (!value) continue;
      const feedback = Object.hasOwn(node.dataset, 'answer') ? 'feedback' : 'explain';
      const answer = feedback === 'feedback' ? 'answer' : 'right';
      node.dataset[answer] = value.correct;
      node.dataset[feedback] = value.feedback;
    }
  }
  const defaults = Object.fromEntries(['texts','links','images','checks','references'].map(k => [k,published[k] || {}]));
  const settings = preview ? read() : defaults;
  window.BFS_EDITOR = {root, preview, id: published.id, current:settings, read, save, defaults, safeURL, apply: container => update(container, settings)};
  if (page) update(page, settings);
})();
