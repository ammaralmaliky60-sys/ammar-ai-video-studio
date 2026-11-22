// Render an SVG at a target width keeping its aspect ratio (transparent PNG).
// usage: node scripts/render_svg_fit.js <in.svg> <out.png> <width>
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [inp, out, width] = process.argv.slice(2);
  const svg = fs.readFileSync(inp, 'utf8');
  const m = svg.match(/viewBox="([\d.\-]+) ([\d.\-]+) ([\d.]+) ([\d.]+)"/);
  const w = parseInt(width, 10), h = Math.round(w * parseFloat(m[4]) / parseFloat(m[3]));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: w, height: h } });
  await p.setContent(`<html><body style="margin:0;background:transparent">${svg.replace('<svg ', `<svg style="width:${w}px;height:${h}px;display:block" `)}</body></html>`);
  await p.screenshot({ path: out, omitBackground: true });
  await b.close();
})();
