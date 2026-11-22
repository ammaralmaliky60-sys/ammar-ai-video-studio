// Batch-export the final logo SVGs to PNG (transparent unless the SVG paints its own background).
// usage: node scripts/export_logo.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const L = 'brand/logo', O = 'exports/logo';
const JOBS = [
  ['official/khaybar-logo-flat.svg', [512, 1024, 2048]],
  ['official/khaybar-logo-cinematic.svg', [512, 1024, 2048]],
  ['avatar/khaybar-avatar.svg', [320, 1080]],
  ['small/khaybar-logo-small.svg', [32, 48, 64, 128]],
  ['mono/khaybar-logo-mono-ivory.svg', [512, 1024]],
  ['mono/khaybar-logo-mono-dark.svg', [512, 1024]],
  ['mark/khaybar-mark-on-image.svg', [256, 512]],
  ['wordmark/khaybar-wordmark.svg', [1024, 2048]],
  ['wordmark/khaybar-wordmark-latin.svg', [1024, 2048]],
  ['wordmark/khaybar-wordmark-cinematic.svg', [1024, 2048]],
  ['horizontal/khaybar-horizontal.svg', [1200, 2400]],
  ['horizontal/khaybar-horizontal-cinematic.svg', [1200, 2400]],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const [rel, widths] of JOBS) {
    const svg = fs.readFileSync(path.join(ROOT, L, rel), 'utf8');
    const vb = svg.match(/viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"/);
    for (const w of widths) {
      const h = Math.round(w * parseFloat(vb[4]) / parseFloat(vb[3]));
      await p.setViewportSize({ width: w, height: h });
      await p.setContent(`<html><body style="margin:0;background:transparent">${svg.replace('<svg ', `<svg style="width:${w}px;height:${h}px;display:block" `)}</body></html>`);
      const out = path.join(ROOT, O, path.dirname(rel), path.basename(rel, '.svg') + `-${w}.png`);
      fs.mkdirSync(path.dirname(out), { recursive: true });
      await p.screenshot({ path: out, omitBackground: true });
    }
  }
  await b.close();
})();
