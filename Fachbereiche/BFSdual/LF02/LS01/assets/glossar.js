(() => {
  const link = document.getElementById('glossar-zurueck');
  if (!link) return;
  const val = new URLSearchParams(location.search).get('from');
  if (val && /^(material\/[\w./% -]+\.html|begriffstraining\.html)(#[\p{L}\d_.:-]+)?$/u.test(val) && !val.includes('..')) {
    link.href=val;
  } else if (document.referrer) {
    try {
      const ref = new URL(document.referrer);
      if (ref.origin===location.origin && ref.pathname.startsWith(new URL('.',location.href).pathname) && ref.href.split('#')[0]!==location.href.split('#')[0]) {
        link.href=ref.href;
        link.addEventListener('click',e=>{if(history.length>1){e.preventDefault();history.back();}});
      }
    } catch {}
  }
})();
