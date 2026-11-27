(() => {
  "use strict";
  const script = document.currentScript;
  const root = new URL("../",script.src);
  const role = script.dataset.materialPage;
  const phaseNames = new Set(["handlungssituation","informieren","planen","entscheiden","durchfuehren","bewerten","reflektieren"]);
  const records = window.BFS_MATERIAL_LIST || [];
  const file = location.pathname.split("/").pop();
  const getPhase = value => phaseNames.has(value) ? value : "";
  const pagePhase = getPhase(file.replace(/\.html$/,""));
  const here = new URL(location.href);
  const isInside = url => url.origin===root.origin && url.pathname.startsWith(root.pathname);
  const packageURL = href => new URL(href,root);
  const materialTarget = url => isInside(url) && (/^material\/.*\.html$/i.test(url.pathname.slice(root.pathname.length)) || url.pathname===packageURL("materialien.html").pathname);
  const validTask = value => typeof value==="string" && /^[\w.:-]{1,160}$/.test(value) ? value : "";
  const fromPhase = getPhase(here.searchParams.get("bfsPhase"));
  const fromTask = fromPhase ? validTask(here.searchParams.get("bfsTask")) : "";
  function putLabel(anchor,title) {
    const code = title.match(/^((?:M|Ü)\d+[a-z]?)\s*[·:–-]\s*(.+)$/);
    const name = document.createElement("span");
    anchor.replaceChildren();
    if (code) {
      const strong = document.createElement("b"); strong.textContent=code[1];
      anchor.append(strong); name.textContent=" · "+code[2];
    } else name.textContent=title;
    anchor.append(name);
  }
  function materialMenu() {
    const block=document.createElement("details");
    block.className="card phase-materials material-access bfs-material-access";
    block.dataset.bfsMaterialMenu="";
    const summary=document.createElement("summary"); summary.textContent="Materialzugriff";
    const nav=document.createElement("nav"); nav.className="material-grid"; nav.setAttribute("aria-label","Materialien und Übungen");
    records.forEach((rec,index)=>{
      const a=document.createElement("a");
      a.className="material-link"; a.dataset.bfsMref=String(index);
      a.href=packageURL(rec.href); putLabel(a,rec.title);
      if(new URL(a.href).pathname===here.pathname) a.setAttribute("aria-current","page");
      nav.append(a);
    });
    const directory=document.createElement("a");
    directory.className="material-link bfs-directory"; directory.href=packageURL("materialien.html");directory.textContent="Materialübersicht";
    nav.append(directory); block.append(summary,nav);
    return block;
  }
  function taskInFocus() {
    if (!document.body.classList.contains("task-focus")) return "";
    const open=document.querySelector(".assignment-frame > .task-accordion[open]");
    return validTask(open?.closest("[data-task-id]")?.dataset.taskId);
  }
  function addReturnInfo(anchor) {
    if (!anchor?.hasAttribute("href") || anchor.hasAttribute("download") || anchor.matches("[data-bfs-material-return]")) return;
    let u;
    try {u=new URL(anchor.getAttribute("href"),location.href);} catch {return;}
    if (!materialTarget(u)) return;
    const phase=pagePhase || fromPhase;
    if (!phase) return;
    u.searchParams.set("bfsPhase",phase);
    const id=pagePhase ? taskInFocus() : fromTask;
    if (id) u.searchParams.set("bfsTask",id); else u.searchParams.delete("bfsTask");
    // Retain relative addresses for offline SCORM exports and its separate iframe root.
    const prefix = new URL(".",location.href).pathname.slice(root.pathname.length).split("/").filter(Boolean).map(()=>"../").join("");
    const value=prefix+u.pathname.slice(root.pathname.length)+u.search+u.hash;
    if(anchor.getAttribute("href")!==value) anchor.setAttribute("href",value);
  }
  function goBack() {
    if (!fromPhase) return null;
    const a=document.createElement("a");a.className="bfs-material-return";a.dataset.bfsMaterialReturn="";
    const u=packageURL(fromPhase+".html");
    if(fromTask) u.searchParams.set("bfsTask",fromTask);
    if(here.searchParams.has("bfs-vorschau"))u.searchParams.set("bfs-vorschau","");
    a.href=u; a.textContent=fromTask?"Zurück zur Aufgabe":"Zurück zur Phase";
    return a;
  }
  function replaceDirectoryButtons() {
    for (const a of document.querySelectorAll("a[href]")) {
      const href=a.getAttribute("href");
      if (!/^(?:\.\.\/)*materialien\.html(?:[?#].*)?$/.test(href)) continue;
      if (a.closest(".bfs-material-access") || !/^(Materialien\s*(?:&|und)\s*Übungen|Zur Materialübersicht|Materialübersicht)$/i.test(a.textContent.trim()))continue;
      a.setAttribute("data-bfs-replaced","");
      const parent=a.parentElement;
      if (parent?.matches("nav,.material-top,p") && [...parent.children].every(c=>c.hasAttribute("data-bfs-replaced")) && !Array.from(parent.childNodes).some(n=>n.nodeType===3&&n.textContent.trim())) parent.setAttribute("data-bfs-replaced","");
    }
  }
  function install() {
    if (role==="office") { office(); return; }
    if(role==="material" || (role==="directory"&&fromPhase)) {
      const strip=document.createElement("div"); strip.className="bfs-material-strip";
      const back=goBack(); if(back)strip.append(back);
      if(role==="material")strip.append(materialMenu());
      const host=document.querySelector(".bfs-material-brand") || document.querySelector("main > header:not(.material-top)");
      if (role==="directory") document.querySelector(".lesson-content > :first-child")?.after(strip);
      else if(document.querySelector("[data-bfs-material-slot]")) document.querySelector("[data-bfs-material-slot]").append(strip);
      else if(host) host.after(strip);
      else {
        const target=document.querySelector(".material-top") || document.querySelector("main") || document.body;
        if(target===document.body)target.prepend(strip); else target.before(strip);
      }
    }
    if(role!=="directory")replaceDirectoryButtons();
    for(const a of document.querySelectorAll("[data-bfs-mref]")) {
      const entry=records[Number(a.dataset.bfsMref)];
      if(!entry)continue;
      const settings=window.BFS_EDITOR?.current;
      const label=settings?.texts?.[entry.textKey];
      if(typeof label==="string" && label.trim())putLabel(a,label);
      const edited=settings?.links?.[entry.linkKey];
      if (typeof edited==="string" && edited.trim() && edited!==entry.href) {
        try {
          const link=new URL(edited,root);
          if (isInside(link) || ["http:","https:"].includes(link.protocol)) a.href=link;
        } catch {}
      }
    }
    const annotate=()=>document.querySelectorAll("a[href]").forEach(addReturnInfo);
    annotate();
    for(const event of ["pointerdown","contextmenu","click"]) document.addEventListener(event,ev=>addReturnInfo(ev.target.closest?.("a[href]")),true);
    if (pagePhase) new MutationObserver(annotate).observe(document.body,{attributes:true,attributeFilter:["class"]});
    const wanted=validTask(here.searchParams.get("bfsTask"));
    if(role==="phase" && wanted) {
      const card=Array.from(document.querySelectorAll(".assignment-frame[data-task-id]")).find(c=>c.dataset.taskId===wanted && !c.closest("[hidden]"));
      const trigger=card?.querySelector(".task-summary");
      if(trigger && !card.querySelector(".task-accordion[open]"))trigger.click();
      if(trigger) {
        const u=new URL(location.href);u.searchParams.delete("bfsTask");
        try {history.replaceState(history.state,"",u);}catch{}
      }
    }
  }
  function office() {
    const page=document.getElementById("page"), source=window.LESSON?.pages?.informieren;
    if (!page || !source) return;
    const catalog=document.createElement("template");catalog.innerHTML=source;
    const headings=[...catalog.content.children].filter(el=>el.matches("details")).map(el=>el.querySelector("summary")?.textContent.trim()||"").filter(t=>/^M\d+\s*[·–-]/.test(t));
    const docs=headings.map((title,index)=>({title,index}));
    if(!docs.length)return;
    // The same materials are already real documents in this single-page master.
    // Open their own disclosure at #informieren to retain live glossary and media.
    let destination=null,previous="";
    function update() {
      const active=location.hash.slice(1)||"index";
      if(page.querySelector(":scope > [data-bfs-material-menu]"))return;
      if(!phaseNames.has(active))return;
      const panel=materialMenu(),nav=panel.querySelector("nav");nav.replaceChildren();
      for(const doc of docs) {
        const a=document.createElement("a");a.className="material-link";a.href="#informieren";putLabel(a,doc.title);
        a.addEventListener("click",event=>{
          if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
          event.preventDefault(); if(active!=="informieren")previous=active;
          destination=doc.index;
          if(active==="informieren")reveal();else location.hash="informieren";
        });
        nav.append(a);
      }
      page.prepend(panel);
      if(active==="informieren")reveal();
      function reveal(){
        if(destination===null)return;
        const doc=[...page.querySelectorAll(":scope > details")].filter(el=>!el.hasAttribute("data-bfs-material-menu") && /^M\d+\s*[·–-]/.test(el.querySelector("summary")?.textContent.trim()||""))[destination];
        if(!doc)return;
        doc.open=true;panel.open=false;destination=null;
        if(previous && !doc.querySelector("[data-bfs-material-return]")){
          const back=document.createElement("a");back.href="#"+previous;back.textContent="Zurück zur Phase";back.className="bfs-material-return";back.dataset.bfsMaterialReturn="";doc.querySelector("summary").after(back);
        }
        doc.querySelector("summary")?.focus({preventScroll:true});doc.scrollIntoView({block:"start"});
      }
    }
    new MutationObserver(update).observe(page,{childList:true});update();
  }
  if(document.readyState!=="complete")document.addEventListener("DOMContentLoaded",install,{once:true});
  else install();
})();
