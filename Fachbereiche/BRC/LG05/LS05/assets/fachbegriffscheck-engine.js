/* Standalone terminology test engine. Root: #begriffscheck-app.
   Shell: .b-shell > .b-header, .b-phase-nav, .b-layout(.b-main + .b-sidebar).
   Native form: .b-card, .b-options > label.b-option, .b-confidence-option.
   Buttons: .b-button + .b-primary/.b-secondary. Results: .b-summary/.b-result-list.
   Local persistence or prepared SCORM package bridge; no external assets required. */
(() => {
  'use strict';
  const root = document.getElementById('begriffscheck-app');
  if (!root || window.RENO_FC_BRIDGE_MODE) return;
  const TEST_CONFIG = window.RENO_FLASHCARD_CONFIG;
  const PACKAGE = window.RENO_FLASHCARD_PACKAGE;
  const PHASE_FILES = ['index.html','handlungssituation.html','informieren.html','planen.html','entscheiden.html','durchfuehren.html','bewerten.html','reflektieren.html'];
  const cards = TEST_CONFIG.terms.map(term => ({id: term.id, term: term.term, explanation: term.explanation}));
  const definitions = TEST_CONFIG.terms.map(term => [term.id, term.variants[0]]);
  function shuffle(items) {
    const result = [...items];
    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }
  const schoolLogo = "<svg xmlns=\"http://www.w3.org/2000/svg\" aria-label=\"BBS 1 Aurich Logo\" class=\"bbs1-header-logo\" height=\"51\" viewBox=\"0 0 2048 564\" width=\"185\">\n<title>BBS 1 Aurich – Website</title>\n<path clip-rule=\"evenodd\" d=\"M1859,217L1859,270L1871,270L1871,217ZM1757,217L1756,218L1756,251L1757,252L1757,257L1760,264L1765,269L1769,271L1782,271L1786,269L1792,263L1793,264L1793,270L1805,270L1805,217L1793,217L1792,218L1792,251L1791,254L1783,261L1777,261L1773,259L1770,255L1770,252L1769,251L1769,217ZM1353,217L1353,255L1354,256L1354,259L1358,266L1366,271L1378,271L1384,268L1389,262L1390,263L1390,270L1401,270L1402,269L1402,218L1401,217L1389,217L1389,250L1388,253L1382,260L1379,261L1373,261L1368,257L1366,253L1366,217ZM1904,216L1898,218L1893,221L1886,229L1883,236L1883,251L1887,260L1896,268L1900,269L1903,271L1919,271L1928,267L1930,264L1923,257L1915,261L1908,261L1902,258L1898,253L1896,248L1896,239L1899,232L1903,228L1907,226L1914,226L1919,228L1922,231L1924,230L1930,224L1930,223L1927,220L1918,216ZM1851,216L1843,216L1839,218L1833,225L1832,224L1832,218L1831,217L1820,217L1820,270L1832,270L1832,240L1833,239L1833,236L1840,228L1843,227L1851,227ZM1506,217L1506,270L1518,270L1518,240L1519,239L1519,235L1521,231L1524,228L1528,226L1534,226L1536,227L1541,233L1541,237L1542,238L1542,270L1554,270L1554,231L1553,230L1553,227L1550,222L1547,219L1541,216L1529,216L1525,218L1519,224L1518,223L1518,217ZM1461,216L1451,221L1444,229L1441,237L1441,251L1445,260L1448,264L1452,267L1461,271L1477,271L1486,267L1491,261L1484,255L1477,260L1474,261L1465,261L1460,259L1455,254L1453,249L1455,247L1494,247L1494,237L1493,236L1493,233L1489,225L1483,219L1476,216ZM1453,237L1455,232L1460,227L1464,225L1473,225L1475,226L1481,233L1481,238L1480,239L1455,239ZM1256,216L1250,218L1245,221L1237,231L1236,237L1235,238L1235,249L1236,250L1236,253L1240,261L1248,268L1256,271L1271,271L1280,267L1282,265L1281,262L1280,262L1276,257L1274,257L1272,259L1267,261L1260,261L1257,260L1249,251L1248,248L1248,239L1252,231L1257,227L1260,226L1266,226L1271,228L1275,231L1282,224L1282,223L1278,219L1270,216ZM1706,192L1672,270L1687,270L1691,261L1691,259L1693,256L1693,254L1695,252L1728,252L1730,254L1730,256L1733,261L1736,270L1751,270L1749,263L1742,249L1742,247L1739,242L1739,240L1736,235L1736,233L1733,228L1733,226L1730,221L1730,219L1727,214L1727,212L1724,207L1724,205L1718,192ZM1712,209L1717,220L1722,236L1724,239L1722,241L1701,241L1699,239L1706,223L1709,213ZM1618,192L1596,209L1594,212L1601,220L1616,208L1617,209L1617,270L1630,270L1630,192ZM1862,191L1860,192L1857,196L1857,202L1862,206L1868,206L1872,203L1873,201L1873,196L1872,194L1868,191ZM1210,190L1196,190L1195,191L1189,192L1183,195L1178,200L1175,206L1175,220L1177,224L1183,230L1208,240L1211,243L1213,248L1211,255L1208,258L1200,261L1196,261L1195,260L1189,259L1184,256L1181,252L1180,252L1180,253L1171,261L1176,266L1187,271L1203,272L1204,271L1211,270L1218,266L1221,263L1225,256L1225,253L1226,252L1226,242L1222,234L1216,229L1212,227L1198,223L1192,220L1188,215L1188,209L1189,207L1193,203L1197,201L1207,201L1210,202L1217,207L1225,199L1225,197L1219,193ZM1939,186L1939,270L1951,270L1951,238L1954,231L1959,227L1962,226L1966,226L1970,228L1974,234L1974,238L1975,239L1975,270L1987,270L1987,231L1983,222L1980,219L1974,216L1962,216L1955,220L1952,224L1951,223L1951,186ZM1417,186L1416,187L1416,270L1429,270L1429,187L1428,186ZM1291,186L1291,270L1303,270L1303,240L1304,239L1304,235L1310,228L1314,226L1321,227L1326,233L1326,238L1327,239L1327,270L1339,270L1339,231L1337,225L1332,219L1326,216L1314,216L1310,218L1304,224L1303,223L1303,186ZM1565,84L1565,136L1577,136L1577,84ZM1347,84L1347,121L1348,122L1349,128L1355,135L1363,138L1373,137L1377,135L1383,129L1384,130L1384,136L1396,136L1396,84L1383,84L1383,116L1381,121L1374,127L1366,127L1361,122L1360,119L1360,84ZM1901,82L1890,86L1883,93L1879,101L1878,115L1881,124L1889,133L1902,138L1911,138L1912,137L1915,137L1921,135L1924,133L1929,127L1921,121L1913,127L1901,127L1893,121L1891,115L1892,114L1931,114L1932,112L1931,101L1927,92L1918,84L1912,83L1911,82ZM1891,102L1892,99L1898,93L1903,91L1908,91L1909,92L1912,92L1918,98L1919,104L1918,105L1892,105ZM1792,86L1784,82L1775,82L1768,85L1763,91L1762,90L1762,84L1750,84L1750,136L1762,136L1762,107L1763,106L1763,102L1765,98L1769,94L1773,92L1780,93L1784,97L1786,102L1786,136L1798,136L1798,96L1796,91ZM1703,83L1694,88L1691,91L1686,100L1686,104L1685,105L1685,116L1686,117L1686,120L1691,129L1697,134L1701,136L1704,136L1709,138L1718,138L1719,137L1725,136L1732,132L1735,129L1735,127L1732,124L1727,121L1722,126L1719,127L1708,127L1704,125L1699,120L1698,115L1699,114L1738,114L1738,103L1737,102L1736,96L1733,91L1728,86L1722,83L1719,83L1718,82L1708,82L1707,83ZM1698,101L1700,97L1705,93L1710,91L1715,91L1720,93L1724,97L1726,104L1725,105L1699,105L1698,104ZM1460,82L1450,86L1447,89L1444,96L1444,101L1446,106L1450,110L1457,113L1460,113L1469,116L1472,119L1472,124L1467,128L1459,128L1456,127L1449,122L1442,129L1442,130L1445,133L1454,137L1468,138L1469,137L1475,136L1481,132L1485,124L1485,118L1483,113L1478,108L1459,102L1456,99L1456,96L1457,94L1460,92L1467,91L1472,93L1477,97L1484,90L1485,90L1481,86L1475,83L1471,83L1470,82ZM1339,82L1333,82L1328,84L1321,92L1320,91L1320,84L1308,84L1308,136L1321,136L1321,105L1323,100L1328,95L1333,93L1338,93L1339,94L1340,93L1340,83ZM1259,84L1254,87L1249,92L1244,102L1244,108L1243,109L1244,112L1244,119L1248,127L1254,133L1267,138L1276,138L1277,137L1281,137L1286,135L1294,128L1294,127L1286,121L1282,125L1278,127L1266,127L1259,122L1257,119L1256,115L1257,114L1296,114L1297,113L1297,106L1296,105L1296,100L1294,97L1293,93L1288,87L1280,83L1277,83L1276,82L1266,82L1265,83ZM1256,102L1258,98L1263,93L1269,91L1277,92L1282,96L1284,100L1284,104L1283,105L1257,105ZM1177,58L1177,136L1213,136L1214,135L1218,135L1221,133L1223,133L1232,125L1234,120L1234,108L1233,105L1228,99L1218,95L1224,92L1230,85L1231,82L1231,73L1227,65L1222,61L1213,58ZM1190,103L1192,101L1206,101L1207,102L1213,102L1217,104L1220,107L1221,109L1221,117L1217,122L1210,125L1191,125L1190,124ZM1190,70L1191,69L1209,69L1214,71L1218,77L1217,84L1213,88L1209,90L1191,90L1190,89ZM1034,58L1034,119L1052,119L1053,120L1053,270L1114,270L1114,58ZM1565,59L1563,62L1563,68L1564,70L1567,72L1575,72L1579,67L1579,63L1578,61L1575,58L1572,57ZM971,55L943,56L942,57L936,57L935,58L930,58L925,60L921,60L917,62L914,62L905,65L881,76L861,89L850,98L836,112L827,123L817,138L814,145L812,147L812,149L810,151L810,153L804,165L801,174L801,177L799,181L799,184L797,189L797,193L796,194L795,207L794,208L794,241L795,242L796,255L797,256L797,260L798,261L799,268L800,270L865,270L875,283L883,300L886,309L887,316L888,317L890,341L889,342L888,359L887,360L887,363L886,364L886,367L883,376L876,391L863,409L852,420L837,431L818,440L812,442L809,442L808,443L805,443L804,444L794,445L793,446L770,446L769,445L758,444L757,443L754,443L742,439L729,433L724,429L721,428L713,422L698,407L688,393L685,386L683,384L683,382L680,377L677,368L677,365L675,360L675,355L674,354L674,348L673,347L673,324L672,323L672,315L671,314L670,303L669,302L667,291L662,276L652,255L641,238L627,221L622,217L622,216L621,216L608,204L589,191L569,181L564,180L561,178L552,175L549,175L540,172L536,172L535,171L531,171L530,170L522,170L521,169L505,169L504,168L502,169L486,169L485,170L478,170L477,171L463,173L459,175L459,239L475,233L483,232L484,231L489,231L490,230L518,230L519,231L524,231L536,235L539,235L551,241L553,241L555,243L566,249L576,257L584,265L595,279L604,296L609,311L610,320L611,321L611,326L612,327L612,348L611,349L610,361L607,369L607,372L602,382L602,384L594,398L588,406L572,422L556,433L543,439L531,443L522,444L521,445L516,445L515,446L492,446L491,445L481,444L480,443L477,443L476,442L473,442L467,440L450,432L432,419L418,404L407,387L399,367L399,363L398,362L397,353L396,352L396,59L395,58L335,58L334,59L334,205L333,206L306,188L286,179L274,175L271,175L267,173L263,173L262,172L258,172L252,170L245,170L244,169L228,169L226,168L225,169L200,170L199,171L185,173L181,175L181,240L188,236L197,233L205,232L206,231L211,231L212,230L240,230L241,231L246,231L247,232L255,233L264,236L279,243L287,248L296,255L309,268L318,280L326,295L326,297L330,306L330,309L333,318L333,323L334,324L334,351L333,352L333,357L332,358L331,366L327,378L317,397L314,400L312,404L299,418L280,432L260,441L257,441L253,443L245,444L244,445L238,445L237,446L215,446L214,445L203,444L202,443L199,443L184,438L174,433L159,423L149,414L138,401L126,380L121,365L120,357L119,356L119,351L118,350L118,58L57,58L57,353L58,354L58,362L60,368L60,373L61,374L63,385L68,400L76,417L78,419L81,426L87,435L98,449L121,471L140,484L162,495L164,495L167,497L179,501L182,501L191,504L202,505L203,506L211,506L212,507L241,507L242,506L249,506L250,505L261,504L262,503L273,501L288,496L293,493L295,493L314,483L335,468L348,456L365,435L373,446L387,461L411,480L414,481L421,486L442,496L457,501L460,501L469,504L479,505L480,506L488,506L489,507L518,507L519,506L527,506L528,505L533,505L534,504L538,504L543,502L551,501L554,499L560,498L575,491L577,491L595,481L615,466L632,449L642,436L646,439L654,450L669,465L683,476L695,484L706,489L708,491L710,491L725,498L731,499L738,502L751,504L752,505L757,505L758,506L766,506L767,507L796,507L797,506L805,506L811,504L816,504L817,503L828,501L843,496L864,486L884,473L906,453L919,437L931,418L931,416L933,414L940,398L944,386L944,383L946,379L946,376L947,375L947,371L949,365L949,358L950,357L950,347L951,346L951,329L950,328L949,311L948,310L948,306L947,305L947,301L946,300L944,289L937,271L866,271L864,269L864,267L859,256L859,253L857,248L857,244L856,243L856,237L855,236L855,213L856,212L856,206L857,205L857,201L858,200L859,193L861,190L862,185L867,174L876,160L894,141L902,135L920,125L922,125L925,123L934,120L937,120L942,118L947,118L948,117L956,117L957,116L969,116L971,117ZM1866,53L1854,53L1854,89L1853,90L1849,86L1844,83L1841,83L1840,82L1830,82L1824,84L1818,88L1814,93L1810,103L1810,117L1812,123L1815,128L1823,135L1832,138L1839,138L1849,134L1854,129L1855,130L1855,136L1866,136ZM1835,92L1841,92L1846,94L1852,100L1854,105L1854,115L1850,122L1843,127L1833,127L1831,126L1825,120L1823,116L1823,104L1824,101L1830,94ZM1673,53L1661,53L1661,89L1660,90L1656,86L1647,82L1637,82L1636,83L1633,83L1626,87L1620,94L1617,101L1617,108L1616,109L1617,112L1617,118L1621,127L1628,134L1638,138L1646,138L1654,135L1657,133L1660,129L1661,130L1661,136L1673,136ZM1642,92L1648,92L1654,95L1658,99L1661,106L1661,114L1659,119L1650,127L1640,127L1635,124L1631,119L1629,113L1629,106L1632,99L1637,94ZM1592,53L1592,136L1604,136L1604,53ZM1496,53L1496,136L1508,136L1508,130L1509,129L1511,132L1515,135L1524,138L1531,138L1541,134L1544,132L1549,126L1550,122L1552,119L1553,106L1552,105L1552,100L1549,94L1542,86L1532,82L1522,82L1515,85L1510,89L1509,88L1509,53ZM1521,92L1528,92L1532,94L1538,100L1538,102L1540,105L1540,114L1536,122L1533,125L1529,127L1520,127L1517,126L1511,120L1508,113L1508,107L1510,101L1515,95ZM1441,52L1433,51L1432,52L1427,52L1421,55L1415,63L1414,72L1413,73L1413,83L1412,84L1403,84L1403,93L1412,93L1413,94L1413,136L1426,136L1426,94L1427,93L1438,93L1438,84L1427,84L1426,83L1426,71L1427,70L1427,67L1431,63L1433,62L1439,62L1440,63Z\" fill=\"#FFFFFF\" fill-rule=\"evenodd\"></path>\n</svg>";
  // Replaced by the assembler with {termId: [definitionVariant, ...]}.
  const definitionVariants = Object.fromEntries(TEST_CONFIG.terms.map(term => [term.id, term.variants]));
  const LETTERS = 'ABCDEF';
  const ANSWER_COUNT = 6;
  const STORAGE_KEY = (window.SOZ_TEACHER_VIEW?.active ? 'teacher:' : '') + 'reno-fachbegriffscheck:v3:' + TEST_CONFIG.id + ':' + TEST_CONFIG.signature;
  const STORAGE_VERSION = 3;
  const stations = [
    ['Orientierung', 'Start · Warum · Kompetenzen', 'compass'],
    ['Handlungssituation', 'Handlungssituation', 'message-square-text'],
    ['Informieren', 'Materialien analysieren', 'search'],
    ['Planen', 'Vorgehen strukturieren', 'clipboard-list'],
    ['Entscheiden', 'Entscheidung begründen', 'circle-check'],
    ['Durchführen', 'Handlungsergebnis erstellen', 'signpost'],
    ['Bewerten', 'Ergebnis prüfen', 'star'],
    ['Reflektieren', 'Lernprozess', 'corner-up-right']
  ];
  let state;
  let storageAvailable = true;
  const esc = value => String(value).replace(/[&<>"']/g, x => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[x]));
  const button = (action, label, extra = '') => `<button type="button" class="b-button b-btn ${extra}" data-action="${action}">${label}</button>`;
  const activeStage = () => state.stage === 'check' || state.stage === 'practice';
  const validIndex = value => Number.isInteger(value) && value >= 0 && value < cards.length;
  const validPhase = value => Number.isInteger(value) && value >= 3 && value < stations.length;
  const JOKER_COST = 3;
  const earnedBonus = () => state.results.reduce((sum, result) => sum + result.bonus, 0);
  const bonusBalance = () => Math.max(0, earnedBonus() - state.jokerUses.length * JOKER_COST);
  function freshState() {
    return {stage: 'intro', started: false, checkFinished: false, phaseIndex: 3,
      cursor: 0, queue: [], serial: 0, appearances: {}, practiceReturn: null, practiceDraft: null,
      results: cards.map(() => ({first: null, latest: null, bonus: 0, history: []})),
      selected: null, certainty: null, feedback: null, acknowledged: false, endedBy: '', jokerUses: []};
  }
  function variantText(id, index) {
    const supplied = definitionVariants[id];
    const variants = Array.isArray(supplied) ? supplied.map(value => typeof value === 'string' ? value : value?.text || value?.definition).filter(value => typeof value === 'string' && value.trim()) : [];
    if (variants.length) return variants[index % variants.length];
    return definitions.find(d => d[0] === id)?.[1] || cards.find(c => c.id === id)?.explanation || id;
  }
  function makeOptions(index, appearance, misconception = null) {
    const term = TEST_CONFIG.terms[index];
    const wrong = term.distractors.map(item => [item.id, item.variants[appearance % item.variants.length], false]);
    // Keep an actual previous misconception in the next appearance, including
    // an old ten-option card imported from a previous standalone version.
    let chosen = wrong.find(option => option[0] === misconception);
    if (!chosen && misconception && definitions.some(item => item[0] === misconception)) {
      chosen = [misconception, variantText(misconception, appearance), false];
    }
    const distractors = chosen ? [chosen, ...shuffle(wrong.filter(option => option[0] !== misconception))].slice(0, ANSWER_COUNT - 1) : shuffle(wrong).slice(0, ANSWER_COUNT - 1);
    return shuffle([[term.id, variantText(term.id, appearance), true], ...distractors]);
  }
  function makeEntry(index, reason = 'initial') {
    const card = cards[index];
    const appearance = state.appearances[card.id] || 0;
    state.appearances[card.id] = appearance + 1;
    state.serial += 1;
    const misconception = [...state.results[index].history].reverse().find(answer => !answer.correct && answer.selected !== card.id)?.selected;
    const options = makeOptions(index, appearance, misconception);
    return {uid: `card-${state.serial}`, i: index, reason, variantIndex: appearance, options, answered: false, answer: null,
      reinforcement: false, triggerUid: ''};
  }
  function seedQueue() {
    state.queue = shuffle(cards.map((_, i) => i)).map(i => makeEntry(i));
    state.cursor = 0;
  }
  function pendingEntries() {return state.queue.filter(entry => !entry.answered);}
  function pendingCount() {return pendingEntries().length;}
  function firstPendingIndex() {return state.queue.findIndex(entry => !entry.answered);}
  function current() {return state.queue[state.cursor];}
  function currentCard() {return cards[current().i];}
  function groups() {
    return {known: cards.filter((_, i) => state.results[i].latest?.correct === true), gaps: cards.filter((_, i) => state.results[i].latest?.correct === false), untested: cards.filter((_, i) => state.results[i].latest === null)};
  }
  function complete() {return groups().known.length === cards.length && pendingCount() === 0;}
  function canOpenPhases() {return !!window.SOZ_TEACHER_VIEW?.active || PACKAGE?.readOnly || (state.checkFinished && (complete() || state.acknowledged));}
  function packageStatus() {
    return {complete: complete(), known: groups().known.length, total: cards.length,
      pending: pendingCount(), started: state.started, acknowledged: state.acknowledged};
  }
  function storageLabel() {
    if (PACKAGE?.isHosted) {
      if (PACKAGE.readOnly) return PACKAGE.message || 'Ansichtsmodus · Änderungen werden nicht gespeichert.';
      return storageAvailable ? (PACKAGE.mode === 'moodle' ? 'Im Moodle-Lernpaket gespeichert.' : 'Im Lernpaket auf diesem Gerät gespeichert.')
        : 'Speichern im Lernpaket fehlgeschlagen. ' + (PACKAGE.message || 'Lasse diese Seite geöffnet und versuche es erneut.');
    }
    return storageAvailable ? 'In diesem Browser gespeichert · keine Übertragung an Moodle.' : 'Browser-Speicher nicht verfügbar · lasse diese Seite geöffnet.';
  }
  function save() {
    if (!state) return false;
    if (PACKAGE?.isHosted) {
      if (PACKAGE.readOnly) {storageAvailable = true; return true;}
      try {storageAvailable = PACKAGE.save({version: STORAGE_VERSION, cardIds: cards.map(c => c.id), state}, packageStatus()) === true;}
      catch (_) {storageAvailable = false;}
      return storageAvailable;
    }
    try {window.localStorage.setItem(STORAGE_KEY, JSON.stringify({version: STORAGE_VERSION, cardIds: cards.map(c => c.id), state})); storageAvailable = true;}
    catch (_) {storageAvailable = false;}
    return storageAvailable;
  }
  function pauseAndReturn() {
    // Keep the exact active card, draft and feedback; this is not an end/summary.
    const showError = () => {
      let note = root.querySelector('[data-pause-error]');
      if (!note) {note = document.createElement('p'); note.className = 'b-save-error'; note.dataset.pauseError = ''; note.setAttribute('role', 'alert'); root.querySelector('.b-pause-navigation').after(note);}
      note.textContent = storageLabel();
      note.scrollIntoView?.({block: 'nearest'});
    };
    if (!save()) {showError(); return;}
    if (PACKAGE?.isHosted) {
      if (PACKAGE.navigate('informieren.html')) return;
      storageAvailable = false; showError(); return;
    }
    window.location.assign('informieren.html');
  }
  function cleanAnswer(answer) {
    if (!answer || typeof answer.correct !== 'boolean' || !['sure', 'unsure'].includes(answer.certainty) || typeof answer.selected !== 'string') return null;
    return {correct: answer.correct, certainty: answer.certainty, selected: answer.selected.slice(0, 100),
      selectedText: typeof answer.selectedText === 'string' ? answer.selectedText.slice(0, 1600) : '',
      source: ['first', 'retry', 'practice'].includes(answer.source) ? answer.source : 'first',
      at: Number.isFinite(answer.at) ? answer.at : 0, uid: typeof answer.uid === 'string' ? answer.uid.slice(0, 100) : ''};
  }
  function cleanEntry(entry) {
    if (!entry || !validIndex(entry.i) || typeof entry.uid !== 'string' || !Array.isArray(entry.options) || ![ANSWER_COUNT, 10].includes(entry.options.length)) return null;
    if (!entry.options.every(option => Array.isArray(option) && typeof option[0] === 'string' && typeof option[1] === 'string') || new Set(entry.options.map(o => o[0])).size !== entry.options.length || !entry.options.some(o => o[0] === cards[entry.i].id)) return null;
    let options = entry.options.map(o => [o[0].slice(0, 100), o[1].slice(0, 1600), o[0] === cards[entry.i].id]);
    if (options.length !== ANSWER_COUNT) {
      const selected = entry.answered && entry.answer?.selected;
      const oldChoice = options.find(o => o[0] === selected && !o[2]);
      const correct = options.find(o => o[2]);
      const fresh = makeOptions(entry.i, entry.variantIndex || 0).filter(o => !o[2] && o[0] !== selected);
      options = shuffle([correct, ...(oldChoice ? [oldChoice] : []), ...fresh].slice(0, ANSWER_COUNT));
    }
    return {uid: entry.uid.slice(0, 100), i: entry.i, reason: entry.reason === 'retry' ? 'retry' : 'initial',
      variantIndex: Number.isInteger(entry.variantIndex) && entry.variantIndex >= 0 ? entry.variantIndex : 0,
      options, answered: entry.answered === true, answer: cleanAnswer(entry.answer),
      reinforcement: entry.reinforcement === true,
      triggerUid: typeof entry.triggerUid === 'string' ? entry.triggerUid.slice(0, 100) : ''};
  }
  function restore() {
    let envelope;
    try {if (PACKAGE?.isHosted) envelope = PACKAGE.load(); else {let raw = window.localStorage.getItem(STORAGE_KEY);
        if (!raw) for (const signature of TEST_CONFIG.legacySignatures || []) {raw = window.localStorage.getItem('reno-fachbegriffscheck:v3:' + TEST_CONFIG.id + ':' + signature); if (raw) break;}
        if (!raw) return false; envelope = JSON.parse(raw);} if (!envelope) return false;}
    catch (_) {storageAvailable = false; return false;}
    if (!envelope || envelope.version !== STORAGE_VERSION || !Array.isArray(envelope.cardIds) || envelope.cardIds.join('|') !== cards.map(c => c.id).join('|')) return false;
    const saved = envelope.state;
    if (!saved || !['intro', 'check', 'summary', 'plan', 'practice'].includes(saved.stage) || !Array.isArray(saved.results) || saved.results.length !== cards.length || !Array.isArray(saved.queue) || !saved.queue.length) return false;
    const queue = saved.queue.map(cleanEntry);
    if (queue.some(entry => !entry) || new Set(queue.map(e => e.uid)).size !== queue.length) return false;
    state = freshState();
    state.queue = queue;
    state.cursor = Number.isInteger(saved.cursor) && saved.cursor >= 0 && saved.cursor < queue.length ? saved.cursor : Math.max(0, firstPendingIndex());
    state.serial = Number.isInteger(saved.serial) && saved.serial >= queue.length ? saved.serial : queue.length;
    cards.forEach(card => {state.appearances[card.id] = Number.isInteger(saved.appearances?.[card.id]) && saved.appearances[card.id] >= 0 ? saved.appearances[card.id] : queue.filter(e => cards[e.i].id === card.id).length;});
    state.stage = saved.stage; state.started = saved.started === true; state.checkFinished = saved.checkFinished === true;
    state.phaseIndex = validPhase(saved.phaseIndex) ? saved.phaseIndex : 3;
    state.acknowledged = saved.acknowledged === true;
    state.endedBy = saved.endedBy === 'Zeit abgelaufen' ? 'Check pausiert' : typeof saved.endedBy === 'string' ? saved.endedBy.slice(0, 120) : '';
    state.results = saved.results.map(r => ({first: cleanAnswer(r?.first), latest: cleanAnswer(r?.latest), bonus: r?.bonus === 1 ? 1 : 0,
      history: Array.isArray(r?.history) ? r.history.map(cleanAnswer).filter(Boolean) : []}));
    // Existing attempts have no spending history. Restore each purchase once,
    // within the points actually earned; a removed card is never marked correct.
    for (const use of Array.isArray(saved.jokerUses) ? saved.jokerUses : []) {
      const trigger = state.queue.find(entry => entry.uid === use?.triggerUid && entry.answered && entry.answer?.correct === false);
      if (!trigger || !validIndex(use.i) || use.i === trigger.i || typeof use.removedUid !== 'string' ||
        state.queue.some(entry => entry.uid === use.removedUid) || state.jokerUses.some(old => old.triggerUid === use.triggerUid || old.removedUid === use.removedUid) || bonusBalance() < JOKER_COST) continue;
      state.jokerUses.push({triggerUid: trigger.uid, removedUid: use.removedUid.slice(0, 100), i: use.i});
    }
    state.practiceReturn = saved.practiceReturn?.stage === 'plan' && validPhase(saved.practiceReturn.phaseIndex)
      ? {stage: 'plan', phaseIndex: saved.practiceReturn.phaseIndex} : {stage: 'summary', phaseIndex: state.phaseIndex};
    state.practiceDraft = saved.practiceDraft && typeof saved.practiceDraft.uid === 'string' ? saved.practiceDraft : null;
    if (state.stage === 'intro') {state.started = false; state.checkFinished = false;}
    if (state.stage === 'check') {state.started = true; state.checkFinished = false;}
    if (state.stage === 'practice' && !state.checkFinished) state.stage = 'intro';
    if (state.stage === 'plan' && !canOpenPhases()) state.stage = state.checkFinished ? 'summary' : 'intro';
    if (activeStage()) {
      restoreDraft(saved);
      if (current().answered && !state.feedback) {
        const nextIndex = firstPendingIndex();
        if (nextIndex < 0) {state.stage = 'summary'; state.checkFinished = true;}
        else {state.cursor = nextIndex; state.selected = null; state.certainty = null;}
      }
    }
    return true;
  }
  function restoreDraft(draft) {
    const entry = current();
    state.selected = typeof draft.selected === 'string' && entry.options.some(o => o[0] === draft.selected) ? draft.selected : null;
    state.certainty = ['sure', 'unsure'].includes(draft.certainty) ? draft.certainty : null;
    state.feedback = null;
    if (entry.answered && draft.feedback && state.selected && state.certainty) {
      const correctOption = entry.options.find(o => o[2]);
      state.feedback = {correct: state.selected === correctOption[0], correctId: correctOption[0], correctText: correctOption[1],
        awarded: draft.feedback.awarded === 1 ? 1 : 0, retry: entry.reason === 'retry', practice: state.stage === 'practice',
        added: Array.isArray(draft.feedback.added) ? draft.feedback.added.filter(validIndex) : [],
        jokerTarget: typeof draft.feedback.jokerTarget === 'string' ? draft.feedback.jokerTarget : null,
        jokerUsed: state.jokerUses.some(use => use.triggerUid === entry.uid)};
    }
  }
  function reset() {
    if (!PACKAGE?.isHosted) try {window.localStorage.removeItem(STORAGE_KEY);} catch (_) {storageAvailable = false;}
    state = freshState(); seedQueue(); render();
  }
  function showCurrentCard() {root.querySelector('.b-card')?.scrollIntoView?.({block: 'start', behavior: 'auto'});}
  function start() {
    if (PACKAGE?.readOnly || state.stage !== 'intro') return;
    state.started = true; state.stage = 'check'; render();
  }
  function end(reason) {
    if (PACKAGE?.readOnly) return;
    if (state.stage === 'intro') {state.started = true; state.stage = 'check';}
    if (state.stage !== 'check') return;
    state.stage = 'summary'; state.checkFinished = true; state.endedBy = reason;
    const nextIndex = firstPendingIndex(); if (nextIndex >= 0) state.cursor = nextIndex;
    state.feedback = null; state.selected = null; state.certainty = null; render(); showCurrentCard();
  }
  function beginPractice() {
    if (!state.checkFinished) {showCurrentCard(); return;}
    if (state.stage === 'practice') {render(); showCurrentCard(); return;}
    if (complete()) {state.stage = 'summary'; render(); showCurrentCard(); return;}
    state.practiceReturn = {stage: state.stage === 'plan' ? 'plan' : 'summary', phaseIndex: state.phaseIndex};
    const hostReturn = PHASE_FILES.indexOf(PACKAGE?.returnPage || '');
    if (PACKAGE?.isHosted && validPhase(hostReturn)) state.practiceReturn = {stage: 'plan', phaseIndex: hostReturn};
    const draft = state.practiceDraft;
    const resumeIndex = draft ? state.queue.findIndex(e => e.uid === draft.uid) : -1;
    const nextIndex = firstPendingIndex();
    if (nextIndex < 0) return;
    state.stage = 'practice'; state.cursor = resumeIndex >= 0 && (!state.queue[resumeIndex].answered || draft.feedback) ? resumeIndex : nextIndex;
    state.selected = null; state.certainty = null; state.feedback = null;
    if (state.cursor === resumeIndex) restoreDraft(draft);
    state.practiceDraft = null; render(); showCurrentCard();
  }
  function leavePractice(toSummary = false) {
    if (state.stage !== 'practice') return;
    state.practiceDraft = {uid: current().uid, selected: state.selected, certainty: state.certainty, feedback: state.feedback};
    const destination = state.practiceReturn || {stage: 'summary', phaseIndex: state.phaseIndex};
    state.phaseIndex = validPhase(destination.phaseIndex) ? destination.phaseIndex : 3;
    state.stage = !toSummary && destination.stage === 'plan' && canOpenPhases() ? 'plan' : 'summary';
    state.selected = null; state.certainty = null; state.feedback = null;
    if (PACKAGE?.isHosted && state.stage === 'plan') {save(); if (PACKAGE.navigate(PHASE_FILES[state.phaseIndex])) return; state.stage = 'summary';}
    render(); showCurrentCard();
  }
  function extraCardsForMistake(index) {
    const uncertainCorrect = cards.map((_, i) => i).filter(i => i !== index &&
      state.results[i].latest?.correct === true && state.results[i].latest.certainty === 'unsure');
    const reinforcement = shuffle(uncertainCorrect)[0];
    // Recheck the failed term, plus exactly one eligible term when available.
    // Never substitute a confidently correct, incorrect or untested term.
    const extra = reinforcement === undefined ? [index] : [index, reinforcement];
    extra.forEach((i, position) => state.queue.push({...makeEntry(i, 'retry'),
      triggerUid: current().uid, reinforcement: position === 1}));
    return extra;
  }
  function jokerTarget() {
    if (!activeStage() || !state.feedback || state.feedback.correct || state.feedback.jokerUsed) return null;
    return state.queue.find(entry => entry.uid === state.feedback.jokerTarget && !entry.answered &&
      entry.reinforcement && entry.triggerUid === current().uid && entry.i !== current().i) || null;
  }
  function useJoker() {
    if (PACKAGE?.readOnly || bonusBalance() < JOKER_COST) return;
    const target = jokerTarget();
    if (!target || state.jokerUses.some(use => use.triggerUid === current().uid)) return;
    state.jokerUses.push({triggerUid: current().uid, removedUid: target.uid, i: target.i});
    state.queue.splice(state.queue.indexOf(target), 1);
    state.feedback.added = state.feedback.added.filter(i => i !== target.i);
    state.feedback.jokerUsed = true;
    render();
    root.querySelector('.b-feedback')?.scrollIntoView?.({block: 'nearest', behavior: 'auto'});
  }
  function submit() {
    if (PACKAGE?.readOnly || !activeStage() || state.feedback || !state.selected || !state.certainty) return;
    const entry = current(); if (entry.answered) return;
    const selectedOption = entry.options.find(o => o[0] === state.selected); if (!selectedOption) return;
    const correctOption = entry.options.find(o => o[2]); const correct = selectedOption[0] === correctOption[0];
    const result = state.results[entry.i]; const practice = state.stage === 'practice';
    const answer = {correct, certainty: state.certainty, selected: state.selected, selectedText: selectedOption[1],
      source: practice ? 'practice' : entry.reason === 'retry' ? 'retry' : 'first', at: Date.now(), uid: entry.uid};
    let awarded = 0;
    if (!practice && entry.reason === 'initial' && !result.first) {
      result.first = {...answer};
      awarded = (correct && state.certainty === 'sure') || (!correct && state.certainty === 'unsure') ? 1 : 0;
      result.bonus = awarded;
    }
    entry.answered = true; entry.answer = {...answer};
    result.latest = {...answer}; result.history.push({...answer});
    const added = correct ? [] : extraCardsForMistake(entry.i);
    const target = !correct && state.queue.find(candidate => candidate.reinforcement && candidate.triggerUid === entry.uid);
    state.feedback = {correct, correctId: correctOption[0], correctText: correctOption[1], awarded, retry: entry.reason === 'retry', practice, added,
      jokerTarget: target?.uid || null, jokerUsed: false};
    render();
    root.querySelector('.b-feedback')?.scrollIntoView?.({block: 'nearest', behavior: 'auto'});
  }
  function next() {
    if (!activeStage()) return;
    state.selected = null; state.certainty = null; state.feedback = null;
    const nextIndex = firstPendingIndex();
    if (nextIndex < 0) {
      if (state.stage === 'check') return end('Alle verpflichtenden Karten bearbeitet');
      return leavePractice();
    }
    state.cursor = nextIndex; render(); showCurrentCard();
  }
  function skip() {
    if (PACKAGE?.readOnly || !activeStage() || state.feedback || current().answered) return;
    const [entry] = state.queue.splice(state.cursor, 1); state.queue.push(entry);
    state.cursor = firstPendingIndex(); state.selected = null; state.certainty = null; state.feedback = null;
    render(); showCurrentCard();
  }
  function openPhase(index) {
    if (!validPhase(index) || !canOpenPhases()) return;
    if (window.SOZ_TEACHER_VIEW?.active) { window.location.assign(PHASE_FILES[index]); return; }
    if (state.stage === 'practice') state.practiceDraft = {uid: current().uid, selected: state.selected, certainty: state.certainty, feedback: state.feedback};
    state.phaseIndex = index; state.stage = 'plan';
    if (PACKAGE?.isHosted) {save(); if (PACKAGE.navigate(PHASE_FILES[index])) return; state.stage = 'summary';} state.selected = null; state.certainty = null; state.feedback = null;
    render(); showCurrentCard();
  }
  function reminder() {
    if (PACKAGE?.isHosted || complete()) return '';
    const g = groups(); const running = state.stage === 'check'; const neutral = !state.started || running;
    const title = !state.started ? 'Flashcard-Test bereit' : running ? 'Flashcard-Test läuft' : 'Test offen';
    const text = !state.started ? `${cards.length} Begriffe · nach Informieren.` : running
      ? `${g.known.length}/${cards.length} Begriffe · ${pendingCount()} Karten offen.`
      : `${g.known.length}/${cards.length} Begriffe · ${pendingCount()} Karten offen · zu Hause nachholen.`;
    const details = state.started && !running ? `<small>${g.gaps.length} Begriffe zuletzt falsch · ${g.untested.length} noch ungeprüft</small>` : '';
    return `<section class="b-followup-status ${neutral ? 'is-neutral' : 'has-open'} ${running ? 'is-running' : ''}" aria-label="Lernstatus Fachbegriffe"><span class="b-followup-dot" aria-hidden="true"></span><div class="b-followup-copy"><strong>${title}</strong><span>${text}</span>${details}</div>${button(state.checkFinished ? 'practice' : 'test', state.checkFinished ? 'Öffnen' : 'Zum Test', 'b-secondary')}</section>`;
  }
  function phaseOverview() {
    const planning = state.stage === 'plan'; const finished = complete(); const unlocked = canOpenPhases();
    const activeIndex = planning ? state.phaseIndex : 2;
    return `<section class="b-phase-overview" aria-labelledby="b-phase-heading"><p class="b-phase-overline">Phasenübersicht</p><h2 class="b-phase-heading" id="b-phase-heading">Die acht Stationen der Lernsituation</h2><ol class="b-phase-track">${stations.map(([label, caption, icon], i) => {
      const done = i < 2 || (planning && i === 2); const active = i === activeIndex;
      const test = i === 2 ? `<button type="button" class="b-test-point${finished ? ' is-complete' : state.started && state.checkFinished ? ' has-open' : ''}" data-action="test" aria-label="Fachbegriffscheck${finished ? ' – vollständig' : state.checkFinished ? ' – zur Auswertung' : ' – aktuelle Testseite'}" ${planning ? '' : 'aria-current="page"'} data-tooltip="Fachbegriffscheck"><i data-lucide="clipboard-check" aria-hidden="true"></i></button>` : '';
      const phaseControl = i >= 3
        ? `<button type="button" class="b-phase-node b-phase-link" data-action="phase" data-phase="${i}" aria-label="Phase ${label} öffnen" ${unlocked ? '' : 'disabled'} ${active ? 'aria-current="step"' : ''}><i data-lucide="${icon}" aria-hidden="true"></i></button>`
        : window.SOZ_TEACHER_VIEW?.active ? `<span class="b-phase-node"><a href="${PHASE_FILES[i]}" aria-label="Phase ${label} öffnen"><i data-lucide="${icon}" aria-hidden="true"></i></a>${test}</span>` : `<span class="b-phase-node"><i data-lucide="${icon}" aria-hidden="true"></i>${test}</span>`;
      return `<li class="b-phase-step ${active ? 'is-current' : done ? 'is-done' : i >= 3 && unlocked ? 'is-available' : 'is-locked'}"${active ? ' aria-current="step"' : ''}>${phaseControl}<span class="b-phase-label">${label}</span><span class="b-phase-caption">${caption}</span></li>`;
    }).join('')}</ol></section>`;
  }
  function header() {
    return `<header class="b-header"><div class="b-brand"><strong>Fachbegriffe prüfen</strong><small>Wissen prüfen · Sicherheit einschätzen</small></div><div class="b-header-logo">${schoolLogo}</div></header><div class="b-toolbar"><p class="b-ls-title">${esc(TEST_CONFIG.title)}</p><div class="b-topactions"><span class="b-tag">Begriffscheck</span>${!state.started || complete() ? button('reset', state.started ? 'Neuen Durchlauf starten' : 'Neu starten', 'b-secondary b-btn-ghost') : ''}</div></div>${checkExit()}${phaseOverview()}`;
  }
  function sidebar() {
    const g = groups(); const checked = state.results.filter(r => r.first).length; const bonus = bonusBalance();
    return `<aside class="b-sidebar"><section class="b-side-panel"><p class="b-eyebrow b-kicker">Dein Fachwissen</p><div class="b-stat b-metric"><strong class="b-metric-number">${g.known.length}<span> / ${cards.length}</span></strong><span>Begriffe zuletzt richtig zugeordnet</span></div><div class="b-progress" role="progressbar" aria-label="Zuletzt richtig zugeordnete Begriffe" aria-valuenow="${g.known.length}" aria-valuemin="0" aria-valuemax="${cards.length}"><div class="b-progress-fill b-progress-bar" style="width:${g.known.length / cards.length * 100}%"></div></div><p class="b-pending-count"><strong>Noch ${pendingCount()} Karten im Stapel</strong></p><p class="b-muted">${complete() ? 'Alle Begriffe richtig und alle Pflichtkarten bearbeitet.' : 'Der Test ist erst erledigt, wenn alle Begriffe zuletzt richtig sind und der Pflichtstapel leer ist.'}</p><div class="b-stat b-metric b-bonus"><span class="b-bonus-star" aria-hidden="true">✦</span><div><strong>${bonus} Übungspunkte für Joker verfügbar</strong><p class="b-muted">${earnedBonus()} verdient · ${state.jokerUses.length * JOKER_COST} eingesetzt<br>3 Punkte = 1 Joker</p></div></div><p class="b-muted">${checked} von ${cards.length} Begriffen im Erstcheck erstmals geprüft.</p></section><section class="b-side-panel"><p class="b-eyebrow b-kicker">Deine Begriffe</p><ul class="b-term-list">${cards.map((card, i) => {const r = state.results[i]; const isCurrent = (activeStage() || state.stage === 'intro') && current()?.i === i; const mark = r.latest === null ? '○' : r.latest.correct ? '✓' : '↻'; return `<li class="b-term-row ${isCurrent ? 'b-term-active' : ''}"><span class="b-status ${r.latest?.correct ? 'b-status-good' : r.latest ? 'b-status-warn' : ''}" aria-label="${r.latest === null ? 'Noch nicht geprüft' : r.latest.correct ? 'Zuletzt richtig zugeordnet' : 'Zuletzt falsch'}">${mark}</span><span>${esc(card.term)}</span>${isCurrent ? '<small>aktuell</small>' : ''}</li>`;}).join('')}</ul></section><details class="b-side-panel b-scoring"><summary>Stapel und Beispielwertung</summary><p>Nach jedem Fehler kommt der fehlerhafte Begriff erneut in den Stapel. Zusätzlich wird genau eine andere Karte zufällig ausgewählt, die zuletzt richtig und mit „noch unsicher“ beantwortet wurde. Gibt es keine solche Karte, bleibt es beim Fehlerbegriff. Sicher richtig beantwortete Karten werden dafür nicht ausgewählt.</p><p>„Noch unsicher“ und richtig zählt fachlich vollständig. Diese Karte kann bei einem späteren Fehler als zusätzliche Wiederholung ausgewählt werden.</p><p>25 Bearbeitungspunkte für die Arbeitsaufträge, 15 Punkte für die drei Handlungsfragen und 60 Punkte für die zuletzt richtig zugeordneten Fachbegriffe. Jede Frage bringt 5 Punkte bei richtiger erster Prüfung ohne Hinweis, sonst höchstens 3 nach Korrektur oder mit Hinweis. Die genaue Punktzahl steht am jeweiligen Auftrag oder Begriff. Bei Fachbegriffen bringen auch Wiederholungen volle Punkte. „Noch unsicher“ beeinflusst die SCORM-Punkte nicht. Ab 75 Punkten und nach Bearbeitung aller Phasen ist das SCORM-Punkteziel erreicht; offene Begriffe und Pflichtkarten bleiben als Lernziel sichtbar. Abgabe und Partnerfeedback werden gesondert in Moodle nachgewiesen. Die Reflexionspunkte sind ausschließlich Übungspunkte für Joker und zählen nicht zu den 100 SCORM-Punkten. Je Begriff ist einmal ein solcher Übungspunkt möglich:</p><ul><li>„Sicher“ und richtig: +1.</li><li>„Noch unsicher“ und falsch: +1.</li><li>Andere Kombinationen: +0.</li></ul><p>Auch „unsicher und richtig“ kann ehrlich eingeschätzt sein. Diese Übungspunkte sind vom SCORM-Punktestand getrennt. Zusatzkarten und Nacharbeit bringen keine weiteren Bonuspunkte.</p><p>Für drei Reflexionspunkte kannst du nach einem Fehler die zusätzlich zugeloste Karte abwenden. Entscheide dich vor „Nächste Karte“. Der Fehlerbegriff bleibt verpflichtend. Ohne Zusatzkarte werden keine Punkte ausgegeben.</p></details></aside>`;
  }
  function historyForCard(index) {
    const history = state.results[index].history;
    if (!history.length) return '';
    return `<details class="b-answer-history"><summary>Dein bisheriger Antwortverlauf (${history.length})</summary><ol>${history.map(answer => `<li><strong>${answer.source === 'practice' ? 'Nacharbeit' : answer.source === 'retry' ? 'Zusatzkarte' : 'Erstcheck'} · ${answer.correct ? 'richtig' : 'noch falsch'}</strong><p>${esc(answer.selectedText || answer.selected)}</p><span class="b-muted">Deine Einschätzung: ${answer.certainty === 'sure' ? 'sicher' : 'noch unsicher'}</span></li>`).join('')}</ol></details>`;
  }
  function question() {
    const entry = current(); const card = currentCard(); const inactive = state.stage === 'intro'; const practicing = state.stage === 'practice';
    const locked = inactive || !!state.feedback || !!PACKAGE?.readOnly; const ready = !locked && state.selected && state.certainty;
    const initialPosition = state.results.filter(result => result.first).length + (entry.answered ? 0 : 1);
    const subtitle = practicing ? 'Nacharbeit' : entry.reason === 'retry' ? 'Zusatzkarte · noch einmal prüfen' : `Begriff ${initialPosition} von ${cards.length}`;
    return `<section class="b-card b-panel"><div class="b-card-head"><div><p class="b-eyebrow b-kicker">${subtitle}</p><h1 class="b-term">${esc(card.term)}</h1></div><span class="b-tag">6 Erklärungen · 1 richtig</span></div>${inactive ? `<div class="b-notice b-start-notice"><div><strong>Erst informieren. Jetzt Wissen prüfen.</strong><p>Wähle eine Erklärung und schätze vor dem Prüfen deine Sicherheit ein. Fehlerhafte Begriffe kommen erneut, gegebenenfalls zusammen mit einer zuvor unsicher richtig beantworteten Karte.</p></div>${button('start', 'Begriffscheck starten', 'b-primary b-btn-primary')}</div>` : ''}${practicing ? `<p class="b-lead">Du setzt deinen verbliebenen Stapel fort. Noch ${pendingCount()} Karten sind verpflichtend. Bei einem Fehler kommt der Begriff erneut, zusätzlich höchstens eine zuletzt unsicher richtig beantwortete Karte. Dein Erstcheck und seine Bonuspunkte bleiben erhalten.</p>` : ''}<form id="b-question-form"><fieldset class="b-answer-fieldset" ${locked ? 'disabled' : ''}><legend class="b-question">Welche Erklärung beschreibt „${esc(card.term)}“ am genauesten?</legend><div class="b-options b-options-many">${entry.options.map((option, index) => {let feedbackClass = ''; if (state.feedback) {if (option[0] === state.feedback.correctId) feedbackClass = 'b-correct'; else if (option[0] === state.selected) feedbackClass = 'b-incorrect';} return `<label class="b-option ${feedbackClass}"><input type="radio" name="b-answer" value="${esc(option[0])}" ${state.selected === option[0] ? 'checked' : ''}><span class="b-option-letter" aria-hidden="true">${LETTERS[index]}</span><span class="b-option-text">${esc(option[1])}</span>${state.feedback && option[0] === state.feedback.correctId ? '<span class="b-option-status">Richtig</span>' : ''}</label>`;}).join('')}</div></fieldset><fieldset class="b-confidence" ${locked ? 'disabled' : ''}><legend><span class="b-eyebrow b-kicker">Deine Selbstreflexion</span><span class="b-confidence-title">Wie sicher bist du dir mit deiner Antwort?</span></legend><p class="b-muted b-confidence-help">Wähle deine Einschätzung, bevor du die Lösung siehst.</p><div class="b-confidence-options"><label class="b-confidence-option"><input type="radio" name="b-certainty" value="sure" ${state.certainty === 'sure' ? 'checked' : ''}><span><strong>Ich bin sicher</strong><small>Ich kann meine Auswahl begründen.</small></span></label><label class="b-confidence-option"><input type="radio" name="b-certainty" value="unsure" ${state.certainty === 'unsure' ? 'checked' : ''}><span><strong>Ich bin noch unsicher</strong><small>Ich schwanke oder habe geraten.</small></span></label></div></fieldset>${state.feedback ? feedback(card) : `<div class="b-actions"><p class="b-hint b-muted" data-requirements>${inactive ? 'Starte den Check, um deine Antwort auszuwählen.' : ready ? 'Antwort und Selbsteinschätzung sind ausgewählt.' : 'Wähle eine Erklärung und deine Sicherheit.'}</p><span class="point-action"><button type="button" class="b-button b-btn b-primary b-btn-primary" data-action="check" data-submit ${ready ? '' : 'disabled'}>Antwort prüfen <span aria-hidden="true">→</span></button>${window.SOZ_POINTS_UI.markup(window.SOZ_PROGRESS_CORE.sharePoints(60,cards.length,entry.i),false,'Punkte für diesen zuletzt richtig zugeordneten Begriff. Eine Wiederholung bringt die volle Punktzahl. Sicherheit beeinflusst diese Punkte nicht. Bereits gutgeschriebene Punkte zählen nicht doppelt.')}</span></div>`}</form>${!inactive && !state.feedback ? `<div class="b-subactions">${button('skip', 'Karte nach hinten verschieben', 'b-secondary b-btn-ghost')}<span class="b-muted">Die Karte bleibt verpflichtend im Stapel.</span></div>` : ''}${practicing || entry.reason === 'retry' ? historyForCard(entry.i) : ''}</section>${practicing ? `<div class="b-demo-toolbar"><span class="b-muted">Der verbliebene Pflichtstapel bleibt beim Verlassen erhalten.</span>${button('leave-practice', state.practiceReturn?.stage === 'plan' ? `Zurück zu ${stations[state.practiceReturn.phaseIndex][0]}` : 'Zurück zur Auswertung', 'b-secondary b-btn-ghost')}</div>` : ''}`;
  }
  function feedback(card) {
    const f = state.feedback;
    const reflectionText = f.practice || f.retry ? 'Deine Einschätzung ist im Antwortverlauf gespeichert. Dafür gibt es keine neuen Reflexionspunkte.' : f.correct && state.certainty === 'sure' ? 'Du warst sicher und hast richtig gewählt. Dafür erhältst du +1 Übungspunkt für einen Joker; kein SCORM-Punkt.' : !f.correct && state.certainty === 'unsure' ? 'Du hast deine Unsicherheit erkannt. Dafür erhältst du +1 Übungspunkt für einen Joker; kein SCORM-Punkt.' : f.correct ? 'Deine Antwort ist richtig. Auch eine unsichere Einschätzung kann ehrlich sein. Fachlich zählt diese Antwort vollständig.' : 'Du warst sicher, die Antwort passt aber noch nicht. Nutze die Erklärung und die folgenden Wiederholungen.';
    const addedText = !f.correct ? `<p class="b-extra-cards"><strong>+${f.added.length} ${f.added.length === 1 ? 'Karte' : 'Karten'} im Stapel:</strong> ${f.added.map(i => esc(cards[i].term)).join(', ')}. ${f.jokerUsed ? 'Die zusätzliche Karte wurde mit deinem Joker abgewendet. Der Fehlerbegriff bleibt verpflichtend.' : f.added.length === 1 ? 'Der Fehlerbegriff kommt mit einer veränderten Erklärung erneut. Aktuell gibt es keine weitere zuletzt unsicher richtig beantwortete Karte.' : 'Die Karten kommen später mit veränderten Erklärungen erneut.'}</p>` : '';
    const target = jokerTarget();
    const joker = f.jokerUsed ? '<p class="b-joker-used" role="status">Joker eingesetzt · 3 Reflexionspunkte abgezogen.</p>' : target ? `<div class="b-joker"><div><strong>Zusatzkarte abwenden?</strong><p>„${esc(cards[target.i].term)}“ entfällt für ${JOKER_COST} Reflexionspunkte. Der Fehlerbegriff bleibt.</p><small>${bonusBalance()} Punkte verfügbar${bonusBalance() < JOKER_COST ? ` · noch ${JOKER_COST - bonusBalance()} nötig` : ' · oder Punkte aufheben und weiter'}</small></div><button type="button" class="b-button b-btn b-secondary" data-action="joker" ${PACKAGE?.readOnly || bonusBalance() < JOKER_COST ? 'disabled' : ''}>Joker einsetzen · −${JOKER_COST}</button></div>` : '';
    const label = pendingCount() === 0 ? f.practice ? 'Nacharbeit abschließen' : 'Meine Auswertung ansehen' : 'Nächste Karte →';
    return `<div class="b-feedback ${f.correct ? 'b-feedback-good' : 'b-feedback-warn b-feedback-wrong'}" aria-live="polite"><p class="b-feedback-title"><span aria-hidden="true">${f.correct ? '✓' : '↻'}</span> ${f.correct ? 'Richtig zugeordnet' : 'Diesen Begriff noch einmal überprüfen'}</p><p>${esc(card.explanation)}</p>${addedText}${joker}<div class="b-reflection"><strong>Deine Selbsteinschätzung</strong><p>${reflectionText}</p></div><div class="b-actions"><span class="b-muted">${window.SOZ_POINTS_UI.markup(f.correct ? window.SOZ_PROGRESS_CORE.sharePoints(60,cards.length,current().i) : 0,true,'Aktuell gutgeschriebene SCORM-Punkte dieses Begriffs; nie doppelt.')} · ${f.retry || f.practice ? 'keine neuen Übungspunkte' : `+${f.awarded} Übungspunkte für Joker`}</span>${button('next', label, 'b-primary b-btn-primary')}</div></div>`;
  }
  function resultGroup(title, items, klass, subtitle) {
    return `<section class="b-summary-group ${klass}"><div class="b-result-heading"><h2>${title}</h2><span class="b-result-count">${items.length}</span></div><p class="b-muted">${subtitle}</p>${items.length ? `<ul class="b-result-list b-summary-list">${items.map(c => `<li>${esc(c.term)}</li>`).join('')}</ul>` : '<p class="b-empty">Keine Begriffe in dieser Gruppe.</p>'}</section>`;
  }
  function summary() {
    const g = groups(); const needsWork = !complete(); const firstCorrect = state.results.filter(r => (r.first || r.history?.[0])?.correct === true).length;
    const grade = PACKAGE?.getGrade?.() || {points: state.results.reduce((n,r,i)=>n+(r.latest?.correct?window.SOZ_PROGRESS_CORE.sharePoints(60,cards.length,i):0),0)};
    return `<section class="b-card b-panel b-summary"><p class="b-eyebrow b-kicker">${esc(state.endedBy)} · dein Ergebnis</p><h1>Das kannst du schon. Das ist noch offen.</h1><p class="b-lead">${firstCorrect} Begriffe beim ersten Prüfen richtig. Dein SCORM-Punktestand zählt die zuletzt richtigen Antworten; „noch unsicher“ kostet keine Punkte. Offene Begriffe und Pflichtkarten bleiben dein Lernziel.</p><div class="b-summary-metrics"><div class="b-stat"><strong>${g.known.length} / ${cards.length}</strong><span>Begriffe zuletzt richtig zugeordnet</span></div><div class="b-stat"><strong>${pendingCount()}</strong><span>Karten noch verpflichtend im Stapel</span></div><div class="b-stat"><strong>${bonusBalance()}</strong><span>Übungspunkte für Joker verfügbar · ${earnedBonus()} verdient · ${state.jokerUses.length * JOKER_COST} eingesetzt</span></div></div><div class="point-action b-moodle-grade">${window.SOZ_POINTS_UI.markup(grade.points,true,'Aktueller SCORM-Gesamtpunktestand von 100 Punkten.')}<span class="b-muted">${grade.ready ? 'SCORM-Punkteziel erreicht.' : 'SCORM-Ziel: mindestens 75 Punkte und alle Arbeitsphasen.'}</span></div><details class="point-rules"><summary>Wie zählen die Punkte?</summary><p>25 Bearbeitungspunkte für die Arbeitsaufträge, 15 Punkte für die drei Handlungsfragen und 60 Punkte für die zuletzt richtig zugeordneten Fachbegriffe. Jede Frage bringt 5 Punkte bei richtiger erster Prüfung ohne Hinweis, sonst höchstens 3 nach Korrektur oder mit Hinweis. Die genaue Punktzahl steht am jeweiligen Auftrag oder Begriff. Bei Fachbegriffen bringen auch Wiederholungen volle Punkte. „Noch unsicher“ beeinflusst die SCORM-Punkte nicht. Ab 75 Punkten und nach Bearbeitung aller Phasen ist das SCORM-Punkteziel erreicht; offene Begriffe und Pflichtkarten bleiben als Lernziel sichtbar. Abgabe und Partnerfeedback werden gesondert in Moodle nachgewiesen.</p></details><div class="b-summary-columns">${resultGroup('Zuletzt richtig zugeordnet', g.known, 'b-result-good', 'Diese Inhalte wurden zuletzt richtig erkannt. Zusätzliche Wiederholungskarten können trotzdem im Stapel liegen.')}${resultGroup('Gezielt vorbereiten', g.gaps, 'b-result-warn', 'Bei der letzten Überprüfung war die Antwort noch falsch. Wiederhole diese Inhalte gezielt.')}${resultGroup('Noch nicht geprüft', g.untested, 'b-result-neutral', 'Hier ist noch offen, ob du den Begriff kennst.')}</div>${needsWork ? `<div class="b-notice b-work-order"><p class="b-eyebrow b-kicker">Dein persönlicher Nacharbeitsauftrag</p>${g.gaps.length ? `<p><strong>Bereite gezielt vor:</strong> ${g.gaps.map(c => esc(c.term)).join(', ')}. Erkläre diese Begriffe in eigenen Worten und finde ein passendes Beispiel aus BioCasa.</p>` : ''}${g.untested.length ? `<p><strong>Prüfe zunächst:</strong> ${g.untested.map(c => esc(c.term)).join(', ')}. Wiederhole davon nur die Inhalte, die du noch nicht sicher zuordnen kannst.</p>` : ''}<p><strong>Setze anschließend deinen verbliebenen Stapel fort: ${pendingCount()} Pflichtkarten.</strong> Bei jedem Fehler wird der Begriff wiederholt; zusätzlich kommt höchstens eine zuletzt unsicher richtig beantwortete Karte hinzu. Der Test ist erledigt, wenn alle Begriffe zuletzt richtig zugeordnet sind und der Stapel vollständig bearbeitet ist.</p><p>Dokumentiere dein Ergebnis und stelle es anschließend im vorgesehenen Moodle-Uploadplatz bereit.</p><label class="b-agreement b-ack"><input type="checkbox" data-ack ${state.acknowledged ? 'checked' : ''}><span>Ich habe meinen persönlichen Nacharbeitsauftrag zur Kenntnis genommen. Ich werde die offenen Inhalte vorbereiten, meinen verbliebenen Pflichtstapel bearbeiten und mein Ergebnis im Moodle-Uploadplatz hochladen.</span></label></div>` : `<div class="b-notice b-all-done"><strong>Fachbegriffscheck vollständig erledigt.</strong><p>Alle ${cards.length} Begriffe sind zuletzt richtig zugeordnet und alle verpflichtenden Karten bearbeitet. Du kannst mit Planen fortfahren.</p></div>`}<div class="b-actions"><span class="b-muted">${needsWork ? 'Die Bestätigung ermöglicht den Übergang. Der rote Lernstatus und dein Pflichtstapel bleiben bestehen.' : 'Bereit für die nächste Phase.'}</span><button type="button" class="b-button b-btn b-primary b-btn-primary" data-action="plan" ${canOpenPhases() ? '' : 'disabled'}>Weiter zu Planen →</button></div>${needsWork ? `<div class="b-actions b-practice-actions">${button('practice', 'Verbliebenen Stapel nacharbeiten', 'b-secondary')}<div class="b-copy"><details><summary>Nacharbeitsauftrag zum Übernehmen</summary><textarea class="b-copy-text" readonly aria-label="Dein persönlicher Nacharbeitsauftrag">${esc(workOrder())}</textarea><p class="b-muted">Text markieren und kopieren. Der Upload erfolgt später in Moodle.</p></details></div></div>` : ''}<p class="b-prototype-note b-muted">${PACKAGE?.isHosted ? (PACKAGE.readOnly || !storageAvailable ? esc(storageLabel()) : 'Dein Teststand wird gemeinsam mit dem Lernpaket gespeichert. Ein Datei-Upload ist eine gesonderte Moodle-Aktivität.') : 'Eigenständige HTML: Dein Teststand wird in diesem Browser gespeichert. Die Folgephasen zeigen hier eine Vorschau; ein Moodle-Upload findet hier nicht statt.'}</p></section>`;
  }
  function workOrder() {
    const g = groups(); const lines = ['Mein persönlicher Nacharbeitsauftrag', ''];
    if (g.gaps.length) lines.push(`Gezielt vorbereiten: ${g.gaps.map(c => c.term).join(', ')}.`, 'Erkläre diese Begriffe in eigenen Worten und ergänze ein Beispiel aus BioCasa.', '');
    if (g.untested.length) lines.push(`Noch prüfen: ${g.untested.map(c => c.term).join(', ')}.`, 'Wiederhole davon nur Inhalte, die du noch nicht sicher zuordnen kannst.', '');
    lines.push(`Verbliebenen Pflichtstapel fortsetzen: ${pendingCount()} Karten. Bei einem Fehler kommt der Fehlerbegriff erneut, zusätzlich höchstens eine zuletzt unsicher richtig beantwortete Karte.`,
      `Reflexionspunkte: ${bonusBalance()} verfügbar, ${earnedBonus()} verdient, ${state.jokerUses.length * JOKER_COST} für Joker eingesetzt.`, 'Abschluss: Alle Begriffe zuletzt richtig und alle Pflichtkarten bearbeitet.', 'Dokumentiere dein Ergebnis und lade es im vorgesehenen Moodle-Uploadplatz hoch.');
    return lines.join('\n');
  }
  function plan() {
    const name = stations[state.phaseIndex][0];
    const descriptions = {3: 'Strukturiere dein Vorgehen für die Handlungssituation.', 4: 'Begründe, welches Vorgehen du auswählst.', 5: 'Erstelle dein Handlungsergebnis auf Grundlage deiner Planung.', 6: 'Prüfe dein Ergebnis anhand der vereinbarten Anforderungen.', 7: 'Blicke auf deinen Lernprozess und deine nächsten Lernschritte zurück.'};
    return `<section class="b-card b-panel b-plan"><p class="b-eyebrow b-kicker">Phase-Vorschau · ${state.phaseIndex - 2} von 5 Folgephasen</p><h1>${name}</h1><p class="b-lead">${descriptions[state.phaseIndex]}</p><div class="b-notice"><strong>Hier beginnt später dein eigentlicher Auftrag für die Phase ${name}.</strong><p>In diesem Prototyp kannst du den Wechsel zwischen den Folgephasen ausprobieren.</p></div>${complete() ? `<p>Alle ${cards.length} Begriffe sind zuletzt richtig und dein Pflichtstapel ist leer.</p>` : `<p>Du hast deinen Nacharbeitsauftrag bestätigt. Noch ${pendingCount()} Karten bleiben verpflichtend. Der rote Lernstatus begleitet dich auch in dieser Phase.</p>`}<div class="b-actions">${button('summary', 'Zurück zu meiner Auswertung', 'b-secondary')}${state.phaseIndex < stations.length - 1 ? button('next-phase', `Weiter zu ${stations[state.phaseIndex + 1][0]} →`, 'b-primary b-btn-primary') : ''}</div></section>`;
  }
  function checkExit() {
    if (PACKAGE?.readOnly || !['intro', 'check', 'practice'].includes(state.stage)) return '';
    const practice = state.stage === 'practice';
    const label = practice ? 'Nacharbeit pausieren' : state.stage === 'intro' ? 'Check überspringen und auswerten' : 'Check abkürzen und auswerten';
    return `<aside class="b-check-exit" aria-label="Fachbegriffscheck abkürzen"><p>${practice ? 'Dein Pflichtstapel bleibt gespeichert.' : 'Offene Begriffe bleiben als Nacharbeitsauftrag erhalten.'}</p>${button(practice ? 'leave-practice' : 'end', label, 'b-check-exit-button')}</aside>`;
  }
  let displayedGrade = null;
  function render() {
    save();
    const currentGrade = PACKAGE?.getGrade?.();
    const pointGain = currentGrade && displayedGrade !== null && storageAvailable ? Math.max(0,currentGrade.points-displayedGrade) : 0;
    if(currentGrade)displayedGrade=currentGrade.points;
    root.innerHTML = `${reminder()}${!storageAvailable && PACKAGE?.isHosted ? '<p class="b-save-error" role="alert">' + esc(storageLabel()) + '</p>' : ''}<div class="b-shell b-app">${header()}<div class="b-layout"><main class="b-main">${state.stage === 'summary' ? summary() : state.stage === 'plan' ? plan() : question()}<nav class="b-pause-navigation" aria-label="Zur vorherigen Lernphase">${button('pause', 'zurück', 'b-secondary b-btn-ghost')}</nav></main>${sidebar()}</div><footer class="b-footer"><span>Begriffe verstehen · Sicherheit einschätzen · gezielt weiterlernen</span><span>${esc(storageLabel())}</span></footer></div>`;
    if (typeof lucide !== 'undefined') lucide.createIcons({attrs: {width: 20, height: 20, 'stroke-width': 2}});
    if(pointGain>0)window.SOZ_POINTS_UI.award(root.querySelector('.b-feedback .point-badge'),pointGain);
    window.SOZ_PROGRESS?.render();
  }
  root.addEventListener('change', event => {
    if (event.target.matches('[data-ack]')) {if (PACKAGE?.readOnly) return; state.acknowledged = event.target.checked; render(); return;}
    if (PACKAGE?.readOnly || !activeStage() || state.feedback || current().answered) return;
    if (event.target.name === 'b-answer') state.selected = event.target.value;
    if (event.target.name === 'b-certainty') state.certainty = event.target.value;
    const control = root.querySelector('[data-submit]'); if (control) control.disabled = !state.selected || !state.certainty;
    const hint = root.querySelector('[data-requirements]');
    if (hint) hint.textContent = state.selected && state.certainty ? 'Antwort und Selbsteinschätzung sind ausgewählt.' : state.selected ? 'Wähle noch deine Sicherheit.' : state.certainty ? 'Wähle noch eine Erklärung.' : 'Wähle eine Erklärung und deine Sicherheit.';
    save();
  });
  root.addEventListener('submit', event => {event.preventDefault(); if (event.target.id === 'b-question-form') submit();});
  root.addEventListener('click', event => {
    const control = event.target.closest('[data-action]'); if (!control || control.disabled) return;
    switch (control.dataset.action) {
      case 'pause': pauseAndReturn(); break;
      case 'start': start(); break;
      case 'check': submit(); break;
      case 'joker': useJoker(); break;
      case 'next': if (state.feedback) next(); break;
      case 'skip': skip(); break;
      case 'end': end(state.stage === 'intro' ? 'Check übersprungen' : 'Check abgekürzt'); break;
      case 'save-retry': render(); break;
      case 'reset': if (!PACKAGE?.readOnly && (!state.started || complete())) reset(); break;
      case 'practice': beginPractice(); break;
      case 'leave-practice': leavePractice(); break;
      case 'test':
        if (state.stage === 'practice') leavePractice(true);
        else if (state.checkFinished) {state.stage = 'summary'; render(); showCurrentCard();}
        else showCurrentCard();
        break;
      case 'summary':
        if (state.stage === 'practice') leavePractice(true);
        else if (state.checkFinished) {state.stage = 'summary'; render(); showCurrentCard();}
        break;
      case 'plan': openPhase(3); break;
      case 'phase': openPhase(Number(control.dataset.phase)); break;
      case 'next-phase': if (state.stage === 'plan') openPhase(state.phaseIndex + 1); break;
    }
  });
  if (!restore()) {state = freshState(); seedQueue();}
  if (PACKAGE?.isHosted && state.stage === 'plan') state.stage = 'summary';
  if (PACKAGE?.isHosted && PACKAGE.returnPage && state.checkFinished && !complete() && !PACKAGE.readOnly) beginPractice(); else render();
  window.addEventListener('pagehide', save);
})();
