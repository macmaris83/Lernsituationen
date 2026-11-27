(() => {
  'use strict';
  const api = window.BFS_EDITOR;
  const $ = selector => document.querySelector(selector);
  const status = text => {
    const node = $('[data-teacher-status]');
    if (node.textContent !== text) node.textContent = text;
  };
  const sources = $('#editor-page');
  const lock = $('#teacher-login');
  const unlock = $('#teacher-unlock');
  const pin = $('#teacher-pin');
  unlock.addEventListener('click',()=>{
    const hash=[...pin.value].reduce((n,c)=>n*31+c.charCodeAt(0),0);
    if (hash!==1509442) {$('#teacher-login-message').textContent='PIN nicht korrekt.';return;}
    lock.hidden=true;$('#teacher-panel').hidden=false;
    (sources.disabled ? upload : sources).focus();
  });
  pin.addEventListener('keydown',event=>{if(event.key==='Enter')unlock.click();});
  const upload = $('#editor-source');
  const tabs = [...document.querySelectorAll('[data-editor-tab]')];
  const panels = Object.fromEntries(tabs.map(tab => [tab.dataset.editorTab,document.getElementById(tab.getAttribute('aria-controls'))]));
  const lookup = $('#editor-filter');
  const empty = $('[data-editor-empty]');
  const preview = $('[data-preview-page]');
  const resetPage = $('[data-reset-page]');
  let saveTimer = null;
  let activeTab = 'content';
  let pageRequest = 0;
  const textGroups = new Map();
  let state = api.read(), sourceDefaults=api.defaults, manifestText, manifest, sourceArchive, files, current;
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

  async function get(name, as = 'string', archive = sourceArchive) {
    const raw = decodeURIComponent(name);
    if (archive) {
      const entry = archive.file(raw) || archive.file(name);
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
    const row = element('label');
    if (label) row.append(element('span',label,'editor-label'));
    const field = element(type === 'textarea' ? 'textarea' : 'input');
    if (type !== 'textarea') field.type = type;
    field.value = value ?? '';
    if (type === 'textarea') field.rows = Math.min(5, Math.max(2, Math.ceil(field.value.length / 72)));
    field.addEventListener('input', () => change(field.value, field));
    row.append(field);
    return row;
  }
  function commit(message) {
    clearTimeout(saveTimer);
    saveTimer=null;
    try { api.save(state); status(message); return true; }
    catch { status('Browser-Speicher voll oder deaktiviert. Bearbeitungen sind für den ZIP-Export in dieser Sitzung verfügbar.'); return false; }
  }
  function pending() {
    clearTimeout(saveTimer);
    status('Entwurf wird gespeichert …');
    saveTimer=setTimeout(()=>commit('Entwurf lokal gespeichert.'),450);
  }
  window.addEventListener('pagehide',()=>{if(saveTimer!==null) commit('Entwurf lokal gespeichert.');});
  document.addEventListener('keydown',event=>{
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase()==='s' && lock.hidden) {
      event.preventDefault();
      commit('Entwurf lokal gespeichert.');
    }
  });

  function filterText() {
    const q=lookup.value.trim().toLocaleLowerCase('de');
    const rows=[...panels.content.querySelectorAll('[data-editor-text-row]')];
    for (const row of rows) {
      const field=row.querySelector('textarea');
      row.hidden=Boolean(q && !field?.value.toLocaleLowerCase('de').includes(q));
    }
    for (const group of panels.content.querySelectorAll('details')) {
      group.hidden=Boolean(q && !group.querySelector('[data-editor-text-row]:not([hidden])'));
      if (q && !group.hidden) group.open=true;
    }
    const missing=Boolean(q && activeTab==='content' && rows.every(row=>row.hidden));
    empty.hidden=!missing;
    if (missing) empty.textContent='Keine passenden Textfelder.';
  }
  lookup.addEventListener('input',filterText);

  function selectTab(key, focus=false) {
    activeTab=key;
    for (const tab of tabs) {
      const selected=tab.dataset.editorTab===key;
      tab.setAttribute('aria-selected',String(selected));
      tab.tabIndex=selected?0:-1;
      panels[tab.dataset.editorTab].hidden=!selected;
      if (selected && focus) tab.focus();
    }
    lookup.closest('label').hidden=key!=='content' || panels.content.querySelectorAll('[data-editor-text-row]').length<10;
    filterText();
  }

  for (const tab of tabs) {
    tab.addEventListener('click',()=>selectTab(tab.dataset.editorTab));
    tab.addEventListener('keydown',event=>{
      const available=tabs.filter(item=>!item.hidden);
      const index=available.indexOf(tab);
      const next={ArrowRight:(index+1)%available.length,ArrowLeft:(index-1+available.length)%available.length,Home:0,End:available.length-1}[event.key];
      if (next===undefined) return;
      event.preventDefault();selectTab(available[next].dataset.editorTab,true);
    });
  }

  function rowFor(node) {
    const key=node.dataset.editText;
    const original=node.textContent;
    if (!original.trim()) return;
    const label=/^H[1-6]$/.test(node.tagName)?'Überschrift':node.tagName==='A'?'Linktext':node.tagName==='FIGCAPTION'?'Bildunterschrift':'Text';
    const row=input(label,state.texts[key] ?? original,val=>{
      state.texts[key]=val;
      pending();
    },'textarea');
    row.dataset.editorTextRow='';
    const section=node.closest('.assignment-frame,.extra-task,.glossary-entry,main section');
    const group=textGroups.get(section);
    (group || panels.content).append(row);
  }

  function makeTextGroups(doc) {
    textGroups.clear();
    const fields=[...doc.querySelectorAll('[data-edit-text]:not(fieldset[data-edit-check] *)')];
    if (fields.length<18) return;
    const sectionOf=node=>node.closest('.assignment-frame,.extra-task,.glossary-entry,main section');
    const sections=[...new Set(fields.map(sectionOf))];
    const named=sections.filter(section=>section?.querySelector('h2,h3,h4'));
    if (named.length<2) return;
    for (const section of sections) {
      const group=element('details');
      const heading=section?.querySelector('h2,h3,h4');
      group.append(element('summary',heading?.textContent.trim() || 'Allgemeiner Text'));
      group.open=textGroups.size===0;
      panels.content.append(group);
      textGroups.set(section,group);
    }
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
        state.images[key]={src:reader.result, alt:state.images[key]?.alt ?? old.alt};
        image.src=reader.result;
        pending();
      };
      reader.onerror=()=>status('Die Bilddatei konnte nicht gelesen werden.');
      reader.readAsDataURL(file);
    });
    const reset=element('button','Bild zurücksetzen');
    reset.type='button';
    reset.addEventListener('click',()=>{
      if (Object.hasOwn(sourceDefaults.images,key)) state.images[key]=structuredClone(sourceDefaults.images[key]);
      else delete state.images[key];
      commit('Bild zurückgesetzt.');open(current);
    });
    uploadRow.append(field);details.append(image,uploadRow,reset);panels.media.append(details);
  }
  function checkFor(node) {
    const key=node.dataset.editCheck;
    const details=element('details');
    const config=state.checks[key] || {
      correct:node.dataset.answer ?? node.dataset.right, feedback:node.dataset.feedback ?? node.dataset.explain
    };
    const [question,...answers]=node.querySelectorAll('[data-edit-text]');
    if (!question) return;
    const questionText=state.texts[question.dataset.editText] ?? question.textContent.trim();
    const summary=element('summary',questionText || 'Frage');
    details.append(summary,input('Frage',questionText,value=>{
      state.texts[question.dataset.editText]=value;
      summary.textContent=value || 'Frage';
      pending();
    }));
    const choices=element('fieldset');
    choices.append(element('legend','Richtige Antwort auswählen','editor-check-label'));
    answers.forEach((answer,index)=>{
      const row=element('div','','editor-answer');
      const correct=element('input');
      correct.type='radio';correct.name='is-correct:'+key;correct.value=String(index);
      correct.checked=Number(config.correct)===index;
      correct.setAttribute('aria-label','Antwort '+(index+1)+' ist richtig');
      correct.addEventListener('change',()=>{
        if (!correct.checked) return;
        config.correct=correct.value;state.checks[key]=config;pending();
      });
      row.append(correct,input('Antwort '+(index+1),state.texts[answer.dataset.editText] ?? answer.textContent.trim(),value=>{
        state.texts[answer.dataset.editText]=value;pending();
      }));
      choices.append(row);
    });
    details.append(choices,input('Rückmeldung',config.feedback,value=>{
      config.feedback=value;state.checks[key]=config;pending();
    },'textarea'));
    panels.checks.append(details);
  }

  async function open(page) {
    if (!page) return;
    current=page;
    const request=++pageRequest;
    preview.removeAttribute('href');
    preview.setAttribute('aria-disabled','true');
    resetPage.disabled=true;
    try {
      let source;
      if (office && page.startsWith('index.html#')) {
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
      if (request!==pageRequest) return;
      const doc=new DOMParser().parseFromString(source,'text/html');
      for (const panel of Object.values(panels)) panel.replaceChildren();
      lookup.value='';
      makeTextGroups(doc);
      for (const node of doc.querySelectorAll('[data-edit-text], [data-edit-image], fieldset[data-edit-check]')) {
        if (node.matches('fieldset')) checkFor(node);
        else if (node.matches('img')) imageFor(node,page);
        else if (!node.closest('fieldset[data-edit-check]')) rowFor(node);
      }
      for (const link of doc.querySelectorAll('a[data-edit-link]')) {
        const key=link.dataset.editLink;
        panels.links.append(input(link.textContent.trim() || 'Link',state.references[key] ?? link.getAttribute('href'),v=>{
          state.references[key]=v.trim();pending();
        }));
      }
      const available=tabs.filter(tab=>{
        tab.hidden=!panels[tab.dataset.editorTab].children.length;
        return !tab.hidden;
      });
      $('.editor-tablist').hidden=!available.length;
      const preferred=page==='begriffstraining.html'?'checks':'content';
      selectTab(available.some(tab=>tab.dataset.editorTab===preferred)?preferred:available[0]?.dataset.editorTab);
      if (!available.length) {
        empty.textContent='Diese Seite enthält keine bearbeitbaren Felder.';
        empty.hidden=false;
      }
      const href=new URL(page,api.root);
      href.searchParams.set('bfs-vorschau','1');
      preview.href=href.href;
      preview.setAttribute('aria-disabled','false');
      resetPage.disabled=false;
    } catch (error) { if (request===pageRequest) status(error.message); }
  }

  async function load(file) {
    const archive=file ? await JSZip.loadAsync(file) : null;
    const xml=await get('imsmanifest.xml','string',archive);
    const parsed=manifestFiles(xml);
    if (file) {
      // Exported BFS packages store their authored content in a literal JS configuration.
      const raw=await get('assets/editor-config.js','string',archive);
      const match=/^\s*window\.BFS_EDITOR_CONFIG=(.*);\s*$/s.exec(raw);
      if (!match) throw new Error('Die Editor-Konfiguration im ZIP ist ungültig.');
      const data=JSON.parse(match[1]);
      if (data.id!==api.id) throw new Error('Die Editor-Konfiguration gehört zu einer anderen Lernsituation.');
      const defaults=Object.fromEntries(Object.keys(api.defaults).map(k=>[k,data[k] || {}]));
      for (const entry of Object.values(defaults.images)) {
        const filename = entry?.file || '';
        const ext=/^assets\/editor-images\/[a-z0-9-]+\.(png|jpg|gif|webp)$/i.exec(filename)?.[1];
        if (ext) {
          const mime=ext.toLowerCase()==='jpg'?'jpeg':ext.toLowerCase();
          entry.src='data:image/'+mime+';base64,'+await get(filename,'base64',archive);
        }
      }
      sourceDefaults=defaults;
      state=structuredClone(sourceDefaults);
      for (const field of document.querySelectorAll('[data-moodle-fields] input')) {
        field.value=state.links[field.dataset.moodleSetting] || '';
      }
    }
    sourceArchive=archive;
    manifestText=xml;
    manifest=parsed;
    files=office
      ? [...['index','handlungssituation','informieren','planen','entscheiden','durchfuehren','bewerten','reflektieren'].map(route=>'index.html#'+route),'ls-glossar.html']
      : manifest.paths.filter(p=>p.endsWith('.html') && !['scorm.html','lehrkraft.html','druckansicht.html'].includes(p));
    const labels={'index':'Orientierung','handlungssituation':'Handlungssituation','informieren':'Informieren','planen':'Planen','entscheiden':'Entscheiden','durchfuehren':'Durchführen','bewerten':'Bewerten','reflektieren':'Reflektieren','begriffstraining':'Fachbegriffscheck','ls-glossar':'Glossar','materialien':'Materialübersicht'};
    const workflow=element('optgroup');workflow.label='Lernablauf';
    const materials=element('optgroup');materials.label='Materialien';
    const other=element('optgroup');other.label='Weitere Seiten';
    const titles=new Map();
    if (files.includes('materialien.html')) {
      try {
        const doc=new DOMParser().parseFromString(await get('materialien.html'),'text/html');
        for (const link of doc.querySelectorAll('a[href^="material/"]')) {
          titles.set(decodeURIComponent(link.getAttribute('href').split(/[?#]/)[0]),link.textContent.trim());
        }
      } catch { /* A title is optional for a material page. */ }
    }
    const order=['index','handlungssituation','informieren','begriffstraining','planen','entscheiden','durchfuehren','bewerten','reflektieren'];
    const routeOf=path=>path.split('#').at(-1).replace(/\.html$/,'');
    const orderOf=path=>{
      const i=order.indexOf(routeOf(path));
      return i < 0 ? order.length : i;
    };
    for (const path of [...files].sort((a,b)=>orderOf(a)-orderOf(b))) {
      const decoded=decodeURIComponent(path);
      const route=routeOf(path);
      const opt=element('option',labels[route] || titles.get(decoded) || decoded.split('/').at(-1).replace(/\.html$/,''));
      opt.value=path;
      const group=path.startsWith('material/')?materials:labels[route] && !['ls-glossar','materialien'].includes(route)?workflow:other;
      group.append(opt);
    }
    sources.replaceChildren(...[workflow,materials,other].filter(group=>group.children.length));
    sources.disabled=false;
    let previous=current;
    if (!previous) {
      try { previous=sessionStorage.getItem(api.id+':editor-page'); } catch {}
    }
    if (files.includes(previous)) sources.value=previous;
    await open(sources.value);
    $('[data-export-ims]').disabled=false;

  }

  $('[data-moodle-fields]').replaceChildren(...Object.entries(names).map(([id,label])=>{
    const row=input('Moodle-Aktivität '+label,state.links[id] || '',(v,el)=>{
      const url=api.safeURL(v.trim());
      el.setCustomValidity(v.trim()&&!url?'Bitte eine vollständige Moodle-Adresse eingeben.':'');
      if (!v.trim()||url) {state.links[id]=url;pending();}
    },'url');
    row.querySelector('input').dataset.moodleSetting=id;
    return row;
  }));
  sources.addEventListener('change',()=>{
    try {sessionStorage.setItem(api.id+':editor-page',sources.value);} catch {}
    open(sources.value);
  });
  upload.addEventListener('change',async ()=>{
    const file=upload.files[0];
    if (!file) return;
    if (saveTimer!==null) commit('Entwurf lokal gespeichert.');
    const button=$('[data-export-ims]');
    button.disabled=true;upload.disabled=true;
    try {await load(file);status('Paket geladen.');}
    catch (error) {status(error.message);button.disabled=!manifest;}
    finally {upload.disabled=false;}
  });
  preview.addEventListener('click',event=>{
    if (preview.getAttribute('aria-disabled')==='true' || !commit('Entwurf lokal gespeichert.')) event.preventDefault();
  });
  $('[data-reset-page]').addEventListener('click',()=>{
    if (!current || !confirm('Lokale Änderungen dieser Seite zurücksetzen?')) return;
    const prefix=decodeURIComponent(current)+'::';
    for (const group of ['texts','images','checks','references']) {
      for (const key of Object.keys(state[group])) if (key.startsWith(prefix)) {
        if (Object.hasOwn(sourceDefaults[group],key)) state[group][key]=sourceDefaults[group][key];
        else delete state[group][key];
      }
    }
    commit('Seite zurückgesetzt.');open(current);
  });

  $('[data-export-ims]').addEventListener('click',async event=>{
    const button=event.currentTarget;
    if (saveTimer!==null) commit('Entwurf lokal gespeichert.');
    button.disabled=true;upload.disabled=true;status('SCORM wird zusammengestellt …');
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
    finally {button.disabled=false;upload.disabled=false;}
  });
  if (location.protocol==='file:') {
    $('#editor-options').open=true;
    status('Öffne die zugehörige SCORM-ZIP.');
  }
  else load().catch(error=>status(error.message));
})();
