window.BFS_XP={"terms": [{"key": "begriffstraining.html::check-1", "answer": 1}, {"key": "begriffstraining.html::check-2", "answer": 0}, {"key": "begriffstraining.html::check-3", "answer": 2}, {"key": "begriffstraining.html::check-4", "answer": 1}, {"key": "begriffstraining.html::check-5", "answer": 2}, {"key": "begriffstraining.html::check-6", "answer": 0}, {"key": "begriffstraining.html::check-7", "answer": 2}, {"key": "begriffstraining.html::check-8", "answer": 2}, {"key": "begriffstraining.html::check-9", "answer": 1}, {"key": "begriffstraining.html::check-10", "answer": 0}]};

window.BFS_LF06_GRADE = state => {
  const r = window.GB_REQUIREMENTS;
  const done = new Set(state.done);
  const share = (points, count, index) =>
    (Math.floor(Math.round(100 * points) / count) + Number(index < Math.round(100 * points) % count)) / 100;
  const situation = r.responses;
  const ids = [...r.common.filter(id => !situation.includes(id)), ...(r[state.path] || r.A)];
  const tasks = ids.filter(id => id !== r.choice);
  let score = r.choice && state.path && done.has(r.choice) ? 1.92 : 0;
  tasks.forEach((id, i) => {
    if (done.has(id)) score += share(r.choice ? 23.08 : 25, tasks.length, i);
  });
  situation.forEach((id, i) => {
    if (done.has(id)) score += share(15, situation.length, i) * (String(state.responses[id]).split(':')[1] === '0' ? .6 : 1);
  });
  const terms = window.BFS_XP.terms;
  terms.forEach(({answer, key}, i) => {
    const right = Number(window.BFS_EDITOR?.current.checks[key]?.correct ?? answer);
    if (state.check?.[i] !== right) return;
    score += share(60, terms.length, i) * ((state.checkFirst?.[i] ?? right) === right ? 1 : .6);
  });
  return Math.round(100 * score) / 100;
};
window.BFS_LF06_PHASES={"index.html": {"common": [], "A": [], "B": [], "C": []}, "handlungssituation.html": {"common": ["BFSDUAL-LF06-LS08-L01", "BFSDUAL-LF06-LS08-L02", "BFSDUAL-LF06-LS08-L03", "BFSDUAL-LF06-LS08-L04"], "A": [], "B": [], "C": []}, "informieren.html": {"common": ["BFSDUAL-LF06-LS08-T01"], "A": [], "B": [], "C": []}, "begriffstraining.html": {"common": [], "A": [], "B": [], "C": []}, "planen.html": {"common": ["BFSDUAL-LF06-LS08-T03"], "A": [], "B": [], "C": []}, "entscheiden.html": {"common": ["BFSDUAL-LF06-LS08-T04", "BFSDUAL-LF06-LS08-T05"], "A": [], "B": [], "C": []}, "durchfuehren.html": {"common": ["BFSDUAL-LF06-LS08-T07"], "A": ["BFSDUAL-LF06-LS08-T06"], "B": ["BFSDUAL-LF06-LS08-T06-B"], "C": ["BFSDUAL-LF06-LS08-T06-C"]}, "bewerten.html": {"common": ["BFSDUAL-LF06-LS08-T08", "BFSDUAL-LF06-LS08-T09-ABGABE", "BFSDUAL-LF06-LS08-T09", "BFSDUAL-LF06-LS08-T09-RUECKMELDUNG"], "A": [], "B": [], "C": []}, "reflektieren.html": {"common": ["BFSDUAL-LF06-LS08-T12"], "A": [], "B": [], "C": []}};
