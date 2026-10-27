(function earlyPreserveHook(w, testFileName, testSignature) {
    'use strict';
    const marker = '__RENO_FC_EARLY_PRESERVE_V1__';
    const K = w.SOZ_PROGRESS_CORE, M = w.SOZ_PROGRESS_META;
    if (!K || !M) throw new Error('Flashcard-Hook muss nach Fortschrittskern und Metadaten geladen werden.');
    if (typeof testFileName === 'string' && /^[A-Za-z0-9_.-]+\.html$/.test(testFileName) && Array.isArray(M.resumePages) && !M.resumePages.includes(testFileName)) M.resumePages.push(testFileName);
    if (w[marker]?.id === M.id && w[marker]?.schema === 1) return;
    const originalSanitize = K.sanitize, originalAllComplete = K.allComplete;
    const valid = fc => !!fc && fc.schema === 1 && fc.id === M.id && fc.version === 3 && typeof fc.signature === 'string' && fc.data !== undefined;
    K.sanitize = function(raw, meta, mode) {
      const p = originalSanitize.call(this, raw, meta, mode);
      if (raw?.s === 1 && raw.l === meta.id && valid(raw.fc)) p.fc = K.clone(raw.fc);
      return p;
    };
    K.allComplete = function(p, meta, ...args) {
      return originalAllComplete.call(this, p, meta, ...args) && valid(p.fc) && (!testSignature || p.fc.signature === testSignature) && p.fc.complete === true;
    };
    w[marker] = {schema: 1, id: M.id, fileName: testFileName || '', signature: testSignature || ''};
  })(window,"wissenscheck.html","d63a2c7efdf3049a");

