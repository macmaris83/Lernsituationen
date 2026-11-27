window.BFS_XP={"terms": [{"key": "begriffstraining.html::check-1", "answer": 2}, {"key": "begriffstraining.html::check-2", "answer": 2}, {"key": "begriffstraining.html::check-3", "answer": 0}, {"key": "begriffstraining.html::check-4", "answer": 2}, {"key": "begriffstraining.html::check-5", "answer": 1}, {"key": "begriffstraining.html::check-6", "answer": 0}, {"key": "begriffstraining.html::check-7", "answer": 2}, {"key": "begriffstraining.html::check-8", "answer": 1}, {"key": "begriffstraining.html::check-9", "answer": 1}, {"key": "begriffstraining.html::check-10", "answer": 1}]};

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
window.BFS_LF06_PHASES={"index.html": {"common": [], "A": [], "B": [], "C": []}, "handlungssituation.html": {"common": ["BFSDUAL-LF06-LS02-L01", "BFSDUAL-LF06-LS02-L02", "BFSDUAL-LF06-LS02-L03", "BFSDUAL-LF06-LS02-L04"], "A": [], "B": [], "C": []}, "informieren.html": {"common": ["BFSDUAL-LF06-LS02-T01", "BFSDUAL-LF06-LS02-T02"], "A": [], "B": [], "C": []}, "begriffstraining.html": {"common": [], "A": [], "B": [], "C": []}, "planen.html": {"common": ["BFSDUAL-LF06-LS02-T04"], "A": [], "B": [], "C": []}, "entscheiden.html": {"common": ["BFSDUAL-LF06-LS02-T05", "BFSDUAL-LF06-LS02-T06", "BFSDUAL-LF06-LS02-T07"], "A": [], "B": [], "C": []}, "durchfuehren.html": {"common": ["BFSDUAL-LF06-LS02-T09", "BFSDUAL-LF06-LS02-T10"], "A": ["BFSDUAL-LF06-LS02-T08"], "B": ["BFSDUAL-LF06-LS02-T08-B"], "C": ["BFSDUAL-LF06-LS02-T08-C"]}, "bewerten.html": {"common": ["BFSDUAL-LF06-LS02-T11", "BFSDUAL-LF06-LS02-T12-ABGABE", "BFSDUAL-LF06-LS02-T12", "BFSDUAL-LF06-LS02-T12-RUECKMELDUNG"], "A": [], "B": [], "C": []}, "reflektieren.html": {"common": ["BFSDUAL-LF06-LS02-T15"], "A": [], "B": [], "C": []}};
