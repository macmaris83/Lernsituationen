/* All entries in one lesson page share the same AIS.chat conversation. */
(() => {
  "use strict";
  const url = "https://app.ais-chat.schule/ua/characters/2b7bdc3e-19fb-4b9d-baaf-4c17ad2b83d0/dialog?inviteCode=QLDYEBIV";
  let enabled = false;
  let dialog;
  let opener;
  function openPilot(event) {
    opener = event.currentTarget;
    if (!dialog) {
      dialog = document.createElement("dialog");
      dialog.className = "ais-help-dialog";
      dialog.setAttribute("aria-labelledby", "lf-pilot-title");
      dialog.innerHTML = '<header class="ais-help-heading"><strong id="lf-pilot-title">KI-Hilfe · Löppt-Pilot</strong><button type="button" autofocus>Schließen</button></header><p class="ais-help-note">Hilfe zur Selbsthilfe · Deine Lösung erarbeitest du selbst.</p><iframe class="ais-help-frame" title="Löppt-Pilot in AIS.chat"></iframe><p class="ais-help-info"><a target="_blank" rel="noopener noreferrer">Löppt-Pilot in einem neuen Tab öffnen ↗</a></p>';
      dialog.querySelector("a").href = url;
      dialog.querySelector("iframe").src = url;
      dialog.querySelector("button").addEventListener("click", () => dialog.close());
      // Keep Escape inside the dialog so that closing it leaves the current task open.
      dialog.addEventListener("keydown", e => {
        if (e.key === "Escape") { e.stopPropagation(); e.preventDefault(); dialog.close(); }
      });
      dialog.addEventListener("close", () => opener?.focus({preventScroll:true}));
      document.body.append(dialog);
    }
    if (!dialog.open) dialog.showModal();
  }
  function button() {
    const entry = document.createElement("button");
    entry.type = "button";
    entry.className = "lf-pilot-button";
    entry.dataset.loepptPilot = "";
    entry.setAttribute("aria-haspopup", "dialog");
    entry.title = "KI-Hilfe zur Selbsthilfe in AIS.chat öffnen";
    entry.innerHTML = '<span class="ais-chat-logo"><svg xmlns="http://www.w3.org/2000/svg" width="142" height="32" viewBox="0 0 142 32" role="img" aria-label="AIS.chat"><title>AIS.chat</title><g fill="none" stroke="#4e248c" stroke-width="3.3" stroke-linecap="round"><rect x="3" y="5" width="20" height="8" rx="4"/><path d="M16 18h7M22 22h2"/></g><text x="33" y="25" fill="#4e248c" font-family="Arial,Helvetica,sans-serif" font-size="23">AIS.chat</text></svg></span>KI-Hilfe öffnen';
    entry.addEventListener("click", openPilot);
    return entry;
  }
  window.LFPilot = {
    url,
    enable() {
      enabled = true;
      const bar = document.querySelector("#inhalt > .gb-intro");
      if (bar && !document.querySelector("[data-loeppt-pilot]")) {
        const entry = document.createElement("aside");
        entry.className = "focus-ai-help no-print";
        entry.append(button());
        bar.after(entry);
      }
    },
    addTaskEntry(panel) {
      if (!enabled) return;
      const aside = document.createElement("aside");
      aside.className = "focus-ai-help";
      aside.append(button());
      panel.append(aside);
    }
  };
})();

window.LFPilot?.enable();
