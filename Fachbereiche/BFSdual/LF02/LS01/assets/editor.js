(() => {
  'use strict';
  const api = window.BFS_EDITOR;
  const $ = selector => document.querySelector(selector);
  const status = text => { $('[data-teacher-status]').textContent = text; };
  const sources = $('#editor-page');
  const lock = $('#teacher-login');
  const unlock = $('#teacher-unlock');
  const pin = $('#teacher-pin');
  unlock.addEventListener('click',()=>{
    const hash=[...pin.value].reduce((n,c)=>n*31+c.charCodeAt(0),0);
    if (hash!==1509442) {$('#teacher-login-message').textContent='PIN nicht korrekt.';return;}
    lock.hidden=true;$('#teacher-panel').hidden=false;sources.focus();
  });
  pin.addEventListener('keydown',event=>{if(event.key==='Enter')unlock.click();});
  const upload = $('#editor-source');
  const output = $('#editor-fields');
  let state = api.read(), manifestText, manifest, sourceArchive, files, current;
  const office = document.body.hasAttribute('data-office');
  const names = {
    peer: 'Peer-Check', feedback: 'Feedback', knowledge: 'Wissens-Check'
  };

  function manifestFiles(xml) {
    const doc = new DOMParser().parseFromString(xml, 'application/xml');
    if (doc.querySelector('parsererror') || doc.documentElement.getAttribute('identifier') !== api.id) {
      throw new Error('Das ZIP gehört zu einer anderen Lernsituation.');
    }
    const resource = doc.getElementsByTagNameNS('*', 'resource')[0];
    if (!resource) throw new Error('Die SCORM-Ressource fehlt.');
    const paths = [...resource.getElementsByTagNameNS('*', 'file')].map(e => e.getAttribute('href'));
    for (const p of paths) {
      const path = decodeURIComponent(p);
      if (/^[a-z]+:|^\/|\\|(^|\/)\.\.(\/|$)/i.test(path)) throw new Error('Ungültiger Paketpfad.');
    }
    return {doc, resource, paths};
  }

  async function get(name, as = 'string') {
    const raw = decodeURIComponent(name);
    if (sourceArchive) {
      const entry = sourceArchive.file(raw) || sourceArchive.file(name);
      if (!entry) throw new Error('Paketdatei fehlt: ' + name);
      return entry.async(as);
    }
    const res = await fetch(new URL(name, api.root), {credentials:'same-origin', cache:'no-store'});
    if (!res.ok) throw new Error('Paketdatei fehlt: ' + name);
    return as === 'string' ? res.text() : res.arrayBuffer();
  }

  const element = (tag, text, cls) => {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (cls) el.className = cls;
    return el;
  };
  function input(label, value, change, type = 'text') {
    const row = element('label', label);
    const field = element(type === 'textarea' ? 'textarea' : 'input');
    if (type !== 'textarea') field.type = type;
    field.value = value || '';
    field.addEventListener('input', () => change(field.value, field));
    row.append(field);
    return row;
  }
  function commit(message) {
    try { api.save(state); status(message); return true; }
    catch { status('Browser-Speicher voll oder deaktiviert. Bearbeitungen sind für den ZIP-Export in dieser Sitzung verfügbar.'); return false; }
  }
  function pending() { status('Änderungen bereit zum Speichern.'); }
  function rowFor(node) {
    const key = node.dataset.editText;
    const original = node.textContent.trim();
    if (!original) return;
    output.append(input(original.slice(0, 100), state.texts[key] ?? original, val => {
      state.texts[key] = val;
      pending();
    }, 'textarea'));
  }
  function imageFor(node, activePage) {
    const key = node.dataset.editImage;
    const details = element('details');
    const old = {alt: node.alt, ...state.images[key]};
    details.append(element('summary', node.alt || 'Bild'), input('Alternativtext', old.alt, alt => {
      state.images[key] = {...state.images[key], alt};
      pending();
    }));
    const uploadRow = element('label','Bilddatei');
    const field = element('input');field.type='file';field.accept='image/png,image/jpeg,image/webp,image/gif';
    const image = element('img');
    image.alt=old.alt;
    image.src=old.src || new URL(old.file || node.getAttribute('src'), old.file ? api.root : new URL(activePage, api.root));
    field.addEventListener('change',()=>{
      const file=field.files[0];
      if (!file) return;
      if (!/^image\/(png|jpeg|webp|gif)$/.test(file.type) || file.size>10*1024*1024) {
        status('Bildformat oder Dateigröße prüfen. PNG, JPEG, WebP oder GIF bis 10 MB.'); return;
      }
      const reader=new FileReader();
      reader.onload=()=>{
        state.images[key]={src:reader.result, alt:state.images[key]?.alt || old.alt};
        image.src=reader.result;
        pending();
      };
      reader.onerror=()=>status('Die Bilddatei konnte nicht gelesen werden.');
      reader.readAsDataURL(file);
    });
    const reset=element('button','Bild zurücksetzen');
    reset.type='button';
    reset.addEventListener('click',()=>{delete state.images[key];commit('Bild zurückgesetzt.');open(current);});
    uploadRow.append(field);details.append(image,uploadRow,reset);output.append(details);
  }
  function checkFor(node) {
    const key=node.dataset.editCheck;
    const details=element('details');
    const config=state.checks[key] ||= {
      correct:node.dataset.answer ?? node.dataset.right, feedback:node.dataset.feedback ?? node.dataset.explain
    };
    details.append(element('summary',node.querySelector('legend')?.textContent || 'Frage'));
    node.querySelectorAll('[data-edit-text]').forEach(text=>{
      const id=text.dataset.editText;
      details.append(input(text.textContent.trim(),state.texts[id] ?? text.textContent.trim(),v=>{
        state.texts[id]=v;pending();
      }));
    });
    const count=node.querySelectorAll('[data-edit-text]').length-1;
    details.append(input('Index der richtigen Antwort (0 bis '+(count-1)+')',config.correct,(v, el)=>{
      const valid=/^\d+$/.test(v) && Number(v)<count;
      el.setCustomValidity(valid?'':'Antwortindex prüfen.');
      el.reportValidity();
      if (valid) {config.correct=v;pending();}
    }),input('Rückmeldung',config.feedback,v=>{config.feedback=v;pending();},'textarea'));
    output.append(details);
  }

  async function open(page) {
    if (!page) return;
    current=page;
    const requested=page;
    try {
      let source;
      if (office) {
        const raw=(await get('data.js')).trim();
        const data=JSON.parse(raw.slice('window.LESSON='.length,-1));
        const route=page.split('#')[1];
        source=data.pages[route];
        if (route==='handlungssituation') {
          const doc=new DOMParser().parseFromString(source,'text/html');
          data.quiz0.forEach((q,i)=>{
            const card=element('fieldset');const key='index.html#handlungssituation::office-check-'+(i+1);
            card.dataset.editCheck=key;card.dataset.right=q.k[0];card.dataset.explain=q.f;
            const question=element('legend',q.q);question.dataset.editText=key+'-q';card.append(question);
            q.o.forEach((answer,n)=>{const text=element('span',answer);text.dataset.editText=key+'-a'+n;card.append(text);});
            doc.body.append(card);
          });
          source=doc.body.innerHTML;
        }
      } else source=await get(page);
      if (current!==requested) return;
      const doc=new DOMParser().parseFromString(source,'text/html');
      output.replaceChildren();
      for (const node of doc.querySelectorAll('[data-edit-text], [data-edit-image], fieldset[data-edit-check]')) {
        if (node.matches('fieldset')) checkFor(node);
        else if (node.matches('img')) imageFor(node,page);
        else if (!node.closest('fieldset[data-edit-check]')) rowFor(node);
      }
      for (const link of doc.querySelectorAll('a[data-edit-link]')) {
        const key=link.dataset.editLink;
        output.append(input('Link · '+link.textContent.trim(),state.references[key] ?? link.getAttribute('href'),v=>{
          state.references[key]=v.trim();pending();
        }));
      }
      if (!output.children.length) output.textContent='Diese Seite enthält keine bearbeitbaren Felder.';
      const href=new URL(page,api.root);
      href.searchParams.set('bfs-vorschau','1');
      $('[data-preview-page]').href=href.href;
    } catch (error) { status(error.message); }
  }

  async function load(file) {
    sourceArchive=file ? await JSZip.loadAsync(file) : null;
    manifestText=await get('imsmanifest.xml');
    manifest=manifestFiles(manifestText);
    files=office
      ? ['index','handlungssituation','informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren'].map(route=>'index.html#'+route)
      : manifest.paths.filter(p=>p.endsWith('.html') && !['scorm.html','lehrkraft.html','druckansicht.html'].includes(p));
    const labels={'index':'Orientierung','handlungssituation':'Handlungssituation','informieren':'Informieren','planen':'Planen','entscheiden':'Entscheiden','durchfuehren':'Durchführen','bewerten':'Bewerten','reflektieren':'Reflektieren','begriffstraining':'Fachbegriffscheck','ls-glossar':'Glossar','materialien':'Materialübersicht'};
    sources.replaceChildren(...files.map(p=>{
      const option=element('option',labels[p.split('#').at(-1).replace(/\.html$/,'')] || p);
      option.value=p;return option;
    }));
    if (files.includes(current)) sources.value=current;
    await open(sources.value);
    $('[data-export-ims]').disabled=false;
  }

  $('[data-moodle-fields]').replaceChildren(...Object.entries(names).map(([id,label])=>input('Moodle-Aktivität '+label,state.links[id] || '',(v,el)=>{
    const url=api.safeURL(v.trim());
    el.setCustomValidity(v.trim()&&!url?'Bitte eine vollständige Moodle-Adresse eingeben.':'');
    if (!v.trim()||url) {state.links[id]=url;pending();}
  },'url')));
  sources.addEventListener('change',()=>open(sources.value));
  upload.addEventListener('change',async ()=>{
    try { $('[data-export-ims]').disabled=true;await load(upload.files[0]);status('Paket geladen.'); }
    catch (error) {status(error.message);}
  });
  $('[data-save-page]').addEventListener('click',()=>commit('Bearbeitungen im Browser gespeichert.'));
  $('[data-preview-page]').addEventListener('click',event=>{
    if (!commit('Vorschau mit gespeichertem Entwurf geöffnet.')) event.preventDefault();
  });
  $('[data-reset-page]').addEventListener('click',()=>{
    if (!current || !confirm('Lokale Änderungen dieser Seite zurücksetzen?')) return;
    const prefix=decodeURIComponent(current)+'::';
    for (const group of ['texts','images','checks','references']) {
      for (const key of Object.keys(state[group])) if (key.startsWith(prefix)) {
        if (Object.hasOwn(api.defaults[group],key)) state[group][key]=api.defaults[group][key];
        else delete state[group][key];
      }
    }
    commit('Seite zurückgesetzt.');open(current);
  });

  $('[data-export-ims]').addEventListener('click',async event=>{
    const button=event.currentTarget;button.disabled=true;status('SCORM wird zusammengestellt …');
    try {
      const copy=JSON.parse(JSON.stringify(state));
      const zip=new JSZip();
      const updated=manifestFiles(manifestText);
      const paths=updated.paths;
      for (let offset=0;offset<paths.length;offset+=8) {
        await Promise.all(paths.slice(offset,offset+8).filter(p=>p!=='assets/editor-config.js').map(async p=>{
          zip.file(decodeURIComponent(p),await get(p,'arraybuffer'));
        }));
      }
      for (const [id,value] of Object.entries(copy.images)) {
        const match=/^data:image\/(png|jpeg|gif|webp);base64,([a-z0-9+/=]+)$/i.exec(value.src || '');
        if (!match) continue;
        const name='assets/editor-images/'+id.replace(/[^a-z\d]/gi,'-')+'.'+(match[1]==='jpeg'?'jpg':match[1]);
        zip.file(name,match[2],{base64:true});value.file=name;delete value.src;
        if (!paths.includes(name)) {
          const node=updated.doc.createElementNS(updated.resource.namespaceURI,'file');
          node.setAttribute('href',name);updated.resource.append(node);
        }
      }
      zip.file('imsmanifest.xml',new XMLSerializer().serializeToString(updated.doc));
      zip.file('assets/editor-config.js','window.BFS_EDITOR_CONFIG='+JSON.stringify({id:api.id,...copy}).replaceAll('<','\\u003c')+';\n');
      const blob=await zip.generateAsync({type:'blob',compression:'DEFLATE'});
      const link=element('a');const url=URL.createObjectURL(blob);
      link.href=url;link.download=api.id+'_Bearbeitet_SCORM.zip';link.click();
      setTimeout(()=>URL.revokeObjectURL(url),30000);
      status('Bearbeitetes SCORM heruntergeladen.');
    } catch (error) {status('Export fehlgeschlagen. '+error.message);}
    finally {button.disabled=false;}
  });
  if (location.protocol==='file:') status('Wähle für die lokale Bearbeitung die zugehörige SCORM-ZIP aus.');
  else load().catch(error=>status(error.message));
})();
