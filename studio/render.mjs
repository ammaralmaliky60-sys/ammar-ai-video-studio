// Frame-accurate renderer: Chromium (Playwright) draws each frame, FFmpeg encodes.
// Usage:
//   node studio/render.mjs <projectDir> <sourceVideo> [--still 60,120] [--from 0 --to 404] [--out file.mp4] [--safe]
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const args = process.argv.slice(2);
const projectDir = path.resolve(args[0]);
const source = path.resolve(args[1]);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const stills = opt('--still', null)?.split(',').map(Number);
const safe = args.includes('--safe');

const build = path.join(projectDir, 'build');
const bgDir = path.join(build, 'bg');
const outDir = path.join(build, stills ? 'stills' : 'frames');
fs.mkdirSync(outDir, { recursive: true });

// 1) Base plate: decode (auto-rotated), Lanczos upscale to 1080x1920, light sharpen. Cached.
if (!fs.existsSync(path.join(bgDir, '0001.jpg'))) {
  fs.mkdirSync(bgDir, { recursive: true });
  execFileSync('ffmpeg', ['-v', 'error', '-i', source, '-vf',
    'scale=1080:1920:flags=lanczos,unsharp=5:5:0.45:5:5:0', '-q:v', '1', path.join(bgDir, '%04d.jpg')]);
}
const bgCount = fs.readdirSync(bgDir).length;

// 2) Static server so ES modules + assets load over http.
const types = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const base = `http://127.0.0.1:${server.address().port}`;
const rel = (p) => '/' + path.relative(ROOT, p).split(path.sep).join('/');

const proxy = process.env.HTTPS_PROXY || process.env.https_proxy;
const browser = await chromium.launch(proxy ? { proxy: { server: proxy, bypass: '127.0.0.1' } } : {});
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));
await page.goto(`${base}/studio/lib/stage.html`);

const meta = await page.evaluate(async ({ comp, transcript, bgDir, bgCount, safe }) => {
  const mod = await import(comp);
  const tr = await (await fetch(transcript)).json();
  const caps = mod.buildCaptions(tr.words, mod.meta.fps);
  await document.fonts.load('800 60px Tajawal'); await document.fonts.load('700 60px Tajawal'); await document.fonts.load('500 60px Tajawal');
  const bg = document.getElementById('bg'), fx = document.getElementById('fx'), grade = document.getElementById('grade');
  if (safe) {
    document.getElementById('safe').style.display = 'block';
    document.getElementById('safe').innerHTML = `<div style="position:absolute;left:0;right:0;top:0;height:220px;background:#f003"></div>
      <div style="position:absolute;left:0;right:0;bottom:0;height:420px;background:#f003"></div>
      <div style="position:absolute;right:0;top:220px;bottom:420px;width:150px;background:#f003"></div>`;
  }
  window.renderFrame = async (frame) => {
    const ctx = { frame, fps: mod.meta.fps, brand: mod.brand };
    const r = mod.render(ctx, caps);
    bg.src = `${bgDir}/${String(Math.min(frame + 1, bgCount)).padStart(4, '0')}.jpg`;
    await bg.decode();
    bg.style.transform = `scale(${r.zoom})`;
    grade.setAttribute('style', r.grade);
    fx.innerHTML = r.html;
    await Promise.all([...fx.querySelectorAll('img')].map((i) => i.decode().catch(() => {})));
  };
  return { ...mod.meta, sfx: mod.sfx };
}, { comp: rel(path.join(projectDir, 'composition.js')), transcript: rel(path.join(projectDir, 'analysis/02-transcript.json')), bgDir: rel(bgDir), bgCount, safe });

const from = Number(opt('--from', 0)), to = Number(opt('--to', meta.durationFrames));
const frames = stills || Array.from({ length: to - from }, (_, i) => from + i);
const stage = page.locator('#stage');
const t0 = Date.now();
for (const f of frames) {
  await page.evaluate((fr) => window.renderFrame(fr), f);
  await stage.screenshot({ path: path.join(outDir, `${String(f).padStart(4, '0')}.${stills ? 'png' : 'jpg'}`), type: stills ? 'png' : 'jpeg', ...(stills ? {} : { quality: 95 }) });
  if (!stills && f % 50 === 0) console.log(`frame ${f}/${to}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}
await browser.close(); server.close();
if (stills) { console.log('stills ->', outDir); process.exit(0); }

// 3) Encode: H.264 + AAC. Voice cleaned (high-pass, light FFT denoise, -14 LUFS); SFX mixed underneath.
const out = path.resolve(opt('--out', path.join(build, 'render.mp4')));
const sfxDir = path.join(ROOT, 'studio/assets/sfx');
const inputs = ['-framerate', String(meta.fps), '-start_number', String(from), '-i', path.join(outDir, '%04d.jpg'),
  '-ss', (from / meta.fps).toFixed(3), '-t', ((to - from) / meta.fps).toFixed(3), '-i', source];
let filter = `[1:a]aresample=48000,highpass=f=80,afftdn=nr=10:nf=-40,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[voice]`;
const mix = ['[voice]'];
meta.sfx.filter((s) => s.f >= from && s.f < to).forEach((s, i) => {
  inputs.push('-i', path.join(sfxDir, `${s.name}.wav`));
  const ms = Math.round(((s.f - from) / meta.fps) * 1000);
  filter += `;[${i + 2}:a]aresample=48000,volume=${s.gain * 2},adelay=${ms}|${ms}[s${i}]`;
  mix.push(`[s${i}]`);
});
filter += `;${mix.join('')}amix=inputs=${mix.length}:normalize=0:duration=first[a]`;
execFileSync('ffmpeg', ['-v', 'error', '-y', ...inputs, '-filter_complex', filter, '-map', '0:v', '-map', '[a]',
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(meta.fps),
  '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest', out], { stdio: 'inherit' });
console.log('rendered ->', out);
