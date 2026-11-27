// Reusable motion-graphics components. Each returns an HTML/SVG string for a given frame.
// ctx = { frame, fps, brand }   brand = { colors:{...}, font, logoMark, logoFull }
import { interpolate, spring, presence, clamp, Easing } from './motion.js';

const px = (n) => `${n.toFixed(2)}px`;

/* ---------- Glass card: frosted brand panel used for all info-band elements ---------- */
export function GlassCard(ctx, { inF, outF, x = 540, y = 380, w = 820, h = 260, children = '', from = 'up' }) {
  const p = presence(ctx.frame, inF, outF, 12, 9);
  if (p <= 0) return '';
  const s = spring(ctx.frame, inF, { damping: 16 });
  const dy = from === 'up' ? (1 - s) * -40 : 0;
  const dx = from === 'right' ? (1 - s) * 90 : 0;
  const reveal = clamp(s * 1.15) * 100; // mask wipe, right-to-left (RTL)
  const c = ctx.brand.colors;
  return `<div class="card" style="left:${px(x - w / 2)};top:${px(y - h / 2)};width:${w}px;height:${h}px;
    opacity:${p};transform:translate(${px(dx)},${px(dy)}) scale(${0.94 + 0.06 * s});
    clip-path:inset(0 0 0 ${100 - reveal}% round 34px);
    background:linear-gradient(135deg, ${c.plum}e6, #1a0820d9);
    border:1.5px solid ${c.accent}66;">${children}</div>`;
}

/* ---------- Kinetic word: spring pop with magenta underline that draws on ---------- */
export function KineticWord(ctx, { text, at, size = 96, weight = 800, color = '#fff', underline = true }) {
  const s = spring(ctx.frame, at, { stiffness: 210, damping: 14 });
  const u = Easing.out(clamp((ctx.frame - at - 4) / 12));
  return `<span class="kw" style="font-size:${size}px;font-weight:${weight};color:${color};
    opacity:${clamp(s * 1.4)};transform:scale(${0.6 + 0.4 * s});display:inline-block;position:relative">${text}
    ${underline ? `<i style="position:absolute;right:0;bottom:-6px;height:7px;border-radius:4px;width:${u * 100}%;background:${ctx.brand.colors.accent}"></i>` : ''}</span>`;
}

/* ---------- Sequential dots (days of week, steps, visits) ---------- */
export function DotRow(ctx, { count, startF, step = 3, size = 22, gap = 14, labels = null }) {
  const c = ctx.brand.colors;
  let out = '';
  for (let i = 0; i < count; i++) {
    const s = spring(ctx.frame, startF + i * step, { stiffness: 260, damping: 15 });
    out += `<span style="display:inline-flex;flex-direction:column;align-items:center;gap:8px;margin:0 ${gap / 2}px">
      <b style="width:${size}px;height:${size}px;border-radius:50%;display:block;
      background:${s > 0.05 ? c.accent : 'transparent'};border:2px solid ${c.accent}aa;
      transform:scale(${0.4 + 0.6 * Math.max(s, 0.001)});box-shadow:0 0 ${18 * s}px ${c.accent}99"></b>
      ${labels ? `<small style="font-size:26px;opacity:${clamp(s)}">${labels[i]}</small>` : ''}</span>`;
  }
  return `<div style="display:flex;direction:rtl;align-items:center">${out}</div>`;
}

/* ---------- Clock: hand sweeps between hours in sync with speech ---------- */
export function Clock(ctx, { size = 150, keys }) {
  // keys: [{f, hour}] -> hand angle interpolated (eased) between keyframes
  const c = ctx.brand.colors;
  const fs = keys.map((k) => k.f), hs = keys.map((k) => k.hour);
  const hour = interpolate(ctx.frame, fs, hs, Easing.inOut);
  const ang = hour * 30; // 12h dial
  let ticks = '';
  for (let i = 0; i < 12; i++) {
    const a = (i * 30 * Math.PI) / 180, r1 = i % 3 ? 62 : 56;
    ticks += `<line x1="${50 + Math.sin(a) * r1 * 0.75}" y1="${50 - Math.cos(a) * r1 * 0.75}" x2="${50 + Math.sin(a) * 47}" y2="${50 - Math.cos(a) * 47}" stroke="#fff" stroke-opacity="${i % 3 ? 0.35 : 0.9}" stroke-width="${i % 3 ? 1.5 : 3}" stroke-linecap="round"/>`;
  }
  const start = keys[1] ? keys[1].hour * 30 : 0;
  const swept = Math.max(0, ang - start);
  const arc = (a0, a1) => {
    const r = 44, p = (a) => [50 + Math.sin((a * Math.PI) / 180) * r, 50 - Math.cos((a * Math.PI) / 180) * r];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    return `M50 50 L${x0} ${y0} A${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1} ${y1} Z`;
  };
  return `<svg width="${size}" height="${size}" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="48" fill="#ffffff10" stroke="${c.accent}" stroke-width="2.5"/>
    ${swept > 0.5 ? `<path d="${arc(start, ang)}" fill="${c.accent}" fill-opacity="0.28"/>` : ''}
    ${ticks}
    <line x1="50" y1="50" x2="${50 + Math.sin((ang * Math.PI) / 180) * 36}" y2="${50 - Math.cos((ang * Math.PI) / 180) * 36}" stroke="${c.accent}" stroke-width="5" stroke-linecap="round"/>
    <line x1="50" y1="50" x2="50" y2="20" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".85"/>
    <circle cx="50" cy="50" r="4.5" fill="#fff"/></svg>`;
}

/* ---------- Animated number (counts in sync, tabular) ---------- */
export function AnimatedNumber(ctx, { keys, format = (v) => String(Math.round(v)), size = 72 }) {
  const v = interpolate(ctx.frame, keys.map((k) => k.f), keys.map((k) => k.v), Easing.inOut);
  return `<span style="font-size:${size}px;font-weight:800;font-variant-numeric:tabular-nums;direction:ltr;display:inline-block">${format(v)}</span>`;
}

/* ---------- Map pin with drop + bounce ---------- */
export function MapPin(ctx, { at, size = 70 }) {
  const s = spring(ctx.frame, at, { stiffness: 240, damping: 11 });
  const c = ctx.brand.colors;
  if (ctx.frame < at) return `<span style="display:inline-block;width:${size}px"></span>`;
  return `<svg width="${size}" height="${size * 1.25}" viewBox="0 0 40 50" style="transform:translateY(${(1 - s) * -60}px);opacity:${clamp(s * 2)};overflow:visible">
    <ellipse cx="20" cy="48" rx="${8 * s}" ry="2" fill="#000" opacity=".35"/>
    <path d="M20 47 C20 47 4 30 4 18 A16 16 0 1 1 36 18 C36 30 20 47 20 47 Z" fill="${c.accent}"/>
    <circle cx="20" cy="18" r="6.5" fill="#fff"/></svg>`;
}

/* ---------- Lower third: name + title, accent bar draws, name wipes RTL ---------- */
export function LowerThird(ctx, { inF, outF, name, title, x = 500, y = 360 }) {
  const p = presence(ctx.frame, inF, outF, 8, 10);
  if (p <= 0) return '';
  const c = ctx.brand.colors;
  const bar = Easing.outQuint(clamp((ctx.frame - inF) / 14));
  const wipe = Easing.out(clamp((ctx.frame - inF - 6) / 16));
  const t2 = Easing.out(clamp((ctx.frame - inF - 14) / 12));
  return `<div style="position:absolute;right:${1080 - x - 380}px;top:${y - 110}px;width:760px;opacity:${p};direction:rtl">
    <div style="display:flex;gap:26px;align-items:stretch">
      <i style="width:10px;border-radius:5px;background:linear-gradient(${c.accent},${c.purple});transform:scaleY(${bar});transform-origin:top"></i>
      <div style="padding:14px 34px 18px;border-radius:28px;background:linear-gradient(135deg, ${c.plum}eb, #1a0820e0);border:1.5px solid ${c.accent}55">
        <div style="font-size:66px;font-weight:800;white-space:nowrap;clip-path:inset(0 0 0 ${(1 - wipe) * 100}%)">${name}</div>
        <div style="font-size:40px;font-weight:500;color:#f3d6e8;opacity:${t2};transform:translateY(${(1 - t2) * 14}px);display:flex;align-items:center;gap:14px">
          ${ToothIcon(ctx, { size: 40 })}${title}</div>
      </div></div></div>`;
}

/* ---------- Clean tooth line icon ---------- */
export function ToothIcon(ctx, { size = 48, color = null }) {
  const col = color || ctx.brand.colors.accent;
  return `<svg width="${size}" height="${size}" viewBox="0 0 48 48" fill="none" stroke="${col}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round">
    <path d="M14 6c-6 0-9 5-9 11 0 6 3 9 4 14 1 6 2 13 6 13 3 0 3-6 5-10 1-2 2-3 4-3s3 1 4 3c2 4 2 10 5 10 4 0 5-7 6-13 1-5 4-8 4-14 0-6-3-11-9-11-4 0-6 2-10 2S18 6 14 6z"/></svg>`;
}

/* ---------- Orthodontic illustration: front teeth, brackets, archwire (schematic) ---------- */
export function BracesIllustration(ctx, { teethF, bracketsF, wireF, width = 640, height = 170 }) {
  const c = ctx.brand.colors;
  // Upper anterior teeth, front view: canine, lateral, central | central, lateral, canine.
  // Widths follow typical proportions (central > canine > lateral); canines pointed.
  const teeth = [
    { w: 58, h: 112, cusp: true }, { w: 52, h: 100 }, { w: 70, h: 118 },
    { w: 70, h: 118 }, { w: 52, h: 100 }, { w: 58, h: 112, cusp: true },
  ];
  const total = teeth.reduce((a, t) => a + t.w, 0) + 5 * 6;
  let x = (width - total) / 2, svg = '';
  const draw = Easing.inOut(clamp((ctx.frame - teethF) / 22));
  const pts = [];
  teeth.forEach((t, i) => {
    // gentle arch: outer teeth sit slightly higher
    const lift = [16, 6, 0, 0, 6, 16][i];
    const top = 18 + lift, bot = top + t.h;
    const d = t.cusp
      ? `M${x} ${top + 8} Q${x} ${top} ${x + 8} ${top} L${x + t.w - 8} ${top} Q${x + t.w} ${top} ${x + t.w} ${top + 8} L${x + t.w - 2} ${bot - 30} Q${x + t.w - 6} ${bot - 12} ${x + t.w / 2 + 8} ${bot - 2} Q${x + t.w / 2} ${bot + 2} ${x + t.w / 2 - 8} ${bot - 2} Q${x + 6} ${bot - 12} ${x + 2} ${bot - 30} Z`
      : `M${x} ${top + 8} Q${x} ${top} ${x + 8} ${top} L${x + t.w - 8} ${top} Q${x + t.w} ${top} ${x + t.w} ${top + 8} L${x + t.w - 2} ${bot - 12} Q${x + t.w - 3} ${bot} ${x + t.w - 14} ${bot} L${x + 14} ${bot} Q${x + 3} ${bot} ${x + 2} ${bot - 12} Z`;
    svg += `<path d="${d}" fill="#ffffff" fill-opacity="${0.92 * draw}" stroke="#ffffff" stroke-width="3" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${1 - draw}"/>`;
    pts.push({ cx: x + t.w / 2, cy: top + t.h * 0.52, i });
    x += t.w + 6;
  });
  // gum line
  svg = `<path d="M${(width - total) / 2 - 10} 52 Q${width / 2} -8 ${width - (width - total) / 2 + 10} 52 L${width - (width - total) / 2 + 10} 30 Q${width / 2} -30 ${(width - total) / 2 - 10} 30 Z" fill="${c.accent}" fill-opacity="${0.35 * draw}"/>` + svg;
  // brackets (pop in from centre outward)
  const order = [2, 3, 1, 4, 0, 5];
  pts.forEach((p) => {
    const s = spring(ctx.frame, bracketsF + order.indexOf(p.i) * 2, { stiffness: 300, damping: 16 });
    if (s <= 0) return;
    svg += `<g transform="translate(${p.cx} ${p.cy}) scale(${s})">
      <rect x="-14" y="-12" width="28" height="24" rx="5" fill="#cfd3dc" stroke="${c.purple}" stroke-width="2.5"/>
      <rect x="-9" y="-4" width="18" height="8" rx="2" fill="${c.purple}" opacity=".55"/></g>`;
  });
  // archwire draws through bracket slots
  const wd = Easing.inOut(clamp((ctx.frame - wireF) / 14));
  if (wd > 0) {
    const path = pts.map((p, k) => `${k ? 'L' : 'M'}${p.cx} ${p.cy}`).join(' ');
    svg += `<path d="M${pts[0].cx - 30} ${pts[0].cy - 4} ${path.replace('M', 'L')} L${pts[5].cx + 30} ${pts[5].cy - 4}" fill="none" stroke="${c.accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${1 - wd}"/>`;
  }
  return `<svg width="${width * height / 170}" height="${height}" viewBox="0 0 ${width} 170" style="overflow:visible">${svg}</svg>`;
}

/* ---------- Dynamic captions: word groups, active word highlight, keywords persist ---------- */
export function Captions(ctx, { groups, y = 990, hideAfter = Infinity }) {
  const f = ctx.frame;
  if (f >= hideAfter) return '';
  const c = ctx.brand.colors;
  const g = groups.find((gr) => f >= gr.inF && f < gr.outF);
  if (!g) return '';
  const p = presence(f, g.inF, g.outF, 4, 4);
  const words = g.words.map((w) => {
    const s = spring(f, w.f - 2, { stiffness: 320, damping: 20 });
    const active = f >= w.f && f < w.endF;
    const col = active || (w.key && f >= w.f) ? c.accent : '#ffffff';
    return `<span style="display:inline-block;margin:0 10px;opacity:${clamp(0.25 + s)};color:${col};
      transform:translateY(${(1 - s) * 16}px) scale(${active ? 1.08 : 1});transition:none">${w.text}</span>`;
  }).join('');
  return `<div class="caps" style="top:${y}px;opacity:${p}"><div class="caps-in">${words}</div></div>`;
}

/* ---------- Logo (supplied artwork, unaltered colours and proportions) ---------- */
export function Logo(ctx, { src, height, at, glow = true }) {
  const s = spring(ctx.frame, at, { stiffness: 120, damping: 17 });
  if (s <= 0) return '';
  return `<img src="${src}" style="height:${height}px;width:auto;opacity:${clamp(s * 1.3)};transform:scale(${0.9 + 0.1 * s});
    filter:${glow ? `drop-shadow(0 0 ${24 * s}px ${ctx.brand.colors.accent}55)` : 'none'}">`;
}
