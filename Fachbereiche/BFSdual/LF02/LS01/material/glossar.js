(() => {
  'use strict';
  const query = new URLSearchParams(location.search);
  const source = query.get('von') || '';
  const point = query.get('stelle') || '';
  let target;
  if (/^m[1-5]$/.test(source)) {
    target = 'material/' + source + '.html';
    if (/^wort-[a-z0-9-]+$/.test(point)) target += '#' + point;
  } else if (source === 'check') {
    target = 'begriffstraining.html';
    if (/^BFSDUAL-LF02-LS01-B\d{2}$/.test(point)) target += '#' + point;
  }
  if (target) document.querySelectorAll('.return-to-source').forEach(a => { a.href = target; });
})();
