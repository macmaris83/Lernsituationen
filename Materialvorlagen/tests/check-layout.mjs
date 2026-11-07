/** Layout smoke check and review artifacts; does not test lessons or SCORM. */
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const { chromium } = createRequire(import.meta.url)('playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(here);
const output = process.env.MATERIAL_QA_OUTPUT || await fs.mkdtemp(path.join(os.tmpdir(), 'material-layout-'));
await fs.mkdir(output, { recursive: true });
const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROMIUM_EXECUTABLE ? { executablePath: process.env.CHROMIUM_EXECUTABLE } : {}),
});
const report = { browser: browser.version(), results: [], failures: [] };
const context = await browser.newContext();
// Fixtures are self-contained. Unexpected network access is a test failure.
await context.route(/^https?:/, route => {
  report.failures.push(`Unexpected network request: ${route.request().url()}`);
  return route.abort();
});
const page = await context.newPage();
page.on('pageerror', error => report.failures.push(error.message));

async function inspect(label, expectedText) {
  const result = await page.evaluate(() => {
    const paper = document.querySelector('article.paper');
    const selectors = 'h1,h2,h3,p,td,th,dt,dd';
    const clipped = [...paper.querySelectorAll(selectors)]
      .filter(el => el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 2)
      .map(el => el.textContent.trim().slice(0, 90));
    return {
      viewport: innerWidth,
      pageWidth: document.documentElement.scrollWidth,
      clipped,
      text: paper.textContent.replace(/\s+/g, ' ').trim(),
    };
  });
  if (result.pageWidth > result.viewport + 2) report.failures.push(`${label}: page overflow`);
  if (result.clipped.length) report.failures.push(`${label}: clipped text: ${result.clipped.join(' | ')}`);
  if (expectedText && expectedText !== result.text) report.failures.push(`${label}: content changed with viewport`);
  report.results.push({ label, viewport: result.viewport, pageWidth: result.pageWidth, clipped: result.clipped });
  return result.text;
}

async function checkTableReachability(label) {
  const regions = page.locator('.table-wrap');
  for (let index = 0; index < await regions.count(); index++) {
    const region = regions.nth(index);
    const info = await region.evaluate(el => ({
      overflow: el.scrollWidth > el.clientWidth + 2,
      keyboardFocus: el.tabIndex === 0,
      name: el.getAttribute('aria-label'),
    }));
    if (!info.overflow) continue;
    if (!info.keyboardFocus || !info.name) report.failures.push(`${label}: scroll region lacks focus or name`);
    await region.focus();
    await page.keyboard.press('ArrowRight');
    await page.waitForTimeout(180);
    if (await region.evaluate(el => el.scrollLeft === 0)) report.failures.push(`${label}: table cannot scroll by keyboard`);
    const endReachable = await region.evaluate(el => {
      el.scrollLeft = el.scrollWidth;
      const last = el.querySelector('tr:last-child > :last-child');
      const reachable = last.getBoundingClientRect().right <= el.getBoundingClientRect().right + 2;
      el.scrollLeft = 0;
      el.blur();
      return reachable;
    });
    if (!endReachable) report.failures.push(`${label}: last column is unreachable`);
  }
}

try {
  for (const name of ['notiz', 'angebot', 'kosten', 'modelldaten']) {
    await page.emulateMedia({ media: 'screen' });
    await page.goto(pathToFileURL(path.join(here, `${name}.html`)).href);
    let originalText;
    for (const width of [1280, 768, 375, 320]) {
      await page.setViewportSize({ width, height: 900 });
      await page.evaluate(() => document.fonts.ready);
      originalText = await inspect(`${name}/${width}`, originalText);
      await checkTableReachability(`${name}/${width}`);
      if (width !== 320) await page.screenshot({ path: path.join(output, `${name}-${width}.png`), fullPage: true });
    }
    await page.setViewportSize({ width: 794, height: 1123 });
    await page.emulateMedia({ media: 'print' });
    await inspect(`${name}/print`, originalText);
    const chromeVisible = await page.locator('.viewerbar, .subbar, .probe-intro').evaluateAll(elements => elements.some(el => getComputedStyle(el).display !== 'none'));
    if (chromeVisible) report.failures.push(`${name}: application chrome visible in print`);
    await page.pdf({ path: path.join(output, `${name}.pdf`), format: 'A4', printBackground: true, margin: { top: '15mm', right: '12mm', bottom: '15mm', left: '12mm' } });
  }

  // Shared CSS also serves five existing shells. Exercise long titles and tables
  // without adding fictitious mails, chats or ERP documents to the lesson materials.
  const css = await fs.readFile(path.join(root, 'assets/material-views.css'), 'utf8');
  const stress = '<h1>Dokumentationsübersicht zur Arbeitsplatz- und Kapazitätsplanung</h1><p>Formatprüfung mit einem langen Verweis: <span class="wrap-value">https://beispiel.invalid/unterlagen/arbeitsplatzplanung-und-kapazitaetsvergleich</span></p><table><thead><tr><th scope="col">Dokumentbezeichnung</th><th scope="col" class="numeric">Betrag</th></tr></thead><tbody><tr><td>Arbeitsplatzplanung mit längerer ergänzender Beschreibung</td><td class="numeric">1.240,00 €</td></tr></tbody></table>';
  for (const type of ['acrobat', 'outlook', 'onenote', 'teams', 'sap', 'excel']) {
    const html = (await fs.readFile(path.join(root, `${type}.html`), 'utf8'))
      .replace(/<link[^>]+rel="stylesheet"[^>]*>/, `<style>${css}</style>`)
      .replaceAll('[Dokumenttitel]', 'Arbeitsplatzplanung und Kapazitätsvergleich')
      .replace(/<article class="paper">[\s\S]*?<\/article>/, `<article class="paper">${stress}</article>`);
    await page.emulateMedia({ media: 'screen' });
    await page.setContent(html);
    let originalText;
    for (const width of [1280, 768, 375, 320]) {
      await page.setViewportSize({ width, height: 900 });
      originalText = await inspect(`${type}-shell/${width}`, originalText);
    }
    await page.emulateMedia({ media: 'print' });
    await page.setViewportSize({ width: 794, height: 1123 });
    await inspect(`${type}-shell/print`, originalText);
  }
} finally {
  await browser.close();
  await fs.writeFile(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
}
console.log(`${report.results.length} layout checks; ${report.failures.length} failures. Review artifacts: ${output}`);
if (report.failures.length) {
  console.error(report.failures.join('\n'));
  process.exitCode = 1;
}
