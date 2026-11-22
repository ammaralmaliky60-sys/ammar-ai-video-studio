// Render SVG files to PNG with the pre-installed Chromium.
// usage: node scripts/render_svgs.js <out_dir> <size> <file.svg>...
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [outDir, size, ...files] = process.argv.slice(2);
  const px = parseInt(size, 10);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: px, height: px }, deviceScaleFactor: 1 });
  for (const f of files) {
    const svg = fs.readFileSync(f, 'utf8');
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg.replace('<svg ', `<svg style="width:${px}px;height:${px}px;display:block" `)}</body></html>`);
    const out = path.join(outDir, path.basename(f, '.svg') + `-${px}.png`);
    await page.screenshot({ path: out, omitBackground: true });
  }
  await browser.close();
})();
