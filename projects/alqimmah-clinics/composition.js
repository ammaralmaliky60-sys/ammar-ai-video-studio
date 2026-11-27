// Alqimmah Clinics — Dr. Zaid Noori clinic hours spot.
// Timeline follows analysis/03-edit-plan.json; word timings come from analysis/02-transcript.json.
import {
  GlassCard, KineticWord, DotRow, Clock, MapPin, LowerThird,
  BracesIllustration, Captions, Logo,
} from '../../studio/lib/components.js';
import { interpolate, presence, spring, clamp, Easing } from '../../studio/lib/motion.js';

export const meta = { fps: 30, width: 1080, height: 1920, durationFrames: 404 };

export const brand = {
  colors: { accent: '#E2178D', berry: '#932065', purple: '#582466', plum: '#481246', graphite: '#3E3F40' },
  logoMark: '/projects/alqimmah-clinics/brand/alqimmah-logo-mark.png',
  logoFull: '/projects/alqimmah-clinics/brand/alqimmah-logo-full.png',
};

// Caption groups as word-index ranges into transcript.words; key = stays highlighted.
const GROUPS = [[0, 3], [4, 4], [5, 7], [8, 10], [11, 13], [14, 15], [16, 16], [17, 18], [19, 22], [23, 24], [25, 25]];
const KEYWORDS = new Set([4, 7, 10, 13, 15, 22, 23, 24]);
const END_CARD = 339; // 11.30s "القمة"

export function buildCaptions(words, fps) {
  return GROUPS.map(([a, b], gi) => {
    const ws = words.slice(a, b + 1).map((w, k) => ({
      text: w.text, f: Math.round(w.start * fps), endF: Math.round(w.end * fps) + 2, key: KEYWORDS.has(a + k),
    }));
    const next = GROUPS[gi + 1] ? Math.round(words[GROUPS[gi + 1][0]].start * fps) : END_CARD;
    return { inF: ws[0].f - 3, outF: Math.min(next - 1, ws[ws.length - 1].endF + 30), words: ws };
  });
}

export const sfx = [
  { name: 'whoosh', f: 28, gain: 0.10 },
  { name: 'tick', f: 56, gain: 0.08 }, { name: 'tick', f: 74, gain: 0.08 },
  { name: 'whoosh', f: 92, gain: 0.09 }, { name: 'pop', f: 139, gain: 0.10 },
  { name: 'whoosh', f: 160, gain: 0.08 },
  { name: 'tick', f: 272, gain: 0.07 }, { name: 'tick', f: 280, gain: 0.07 }, { name: 'tick', f: 288, gain: 0.07 },
  { name: 'shimmer', f: 339, gain: 0.07 },
];

export function render(ctx, captions) {
  const f = ctx.frame;
  const c = brand.colors;

  // Camera: quick hook push-in, slow drift, gentle settle on end card. Anchored on the face.
  const zoom = interpolate(f, [0, 24, 339, 404], [1.0, 1.04, 1.085, 1.05], Easing.inOut);

  // End-card grade: darken top band slightly so the logo reads (face stays untouched).
  const g = presence(f, END_CARD - 6, 404, 14, 1);
  const grade = `background:linear-gradient(180deg, rgba(10,2,14,${0.55 * g}) 0%, rgba(10,2,14,${0.35 * g}) 26%, transparent 42%)`;

  let html = '';

  // 1+2) Schedule card: "يوميًا" + 7 day dots, then clock 3 -> 9 (0.9s – 3.1s)
  html += GlassCard(ctx, {
    inF: 26, outF: 94, y: 372, w: 800, h: 268,
    children: `<div style="display:flex;flex-direction:column;align-items:center;gap:10px;width:100%">
      <div style="display:flex;align-items:center;gap:30px">
        ${KineticWord(ctx, { text: 'يوميًا', at: 29, size: 84 })}
        ${DotRow(ctx, { count: 7, startF: 33, step: 2, size: 20, gap: 12 })}
      </div>
      <div style="display:flex;align-items:center;gap:26px;opacity:${clamp((f - 46) / 8)};transform:translateY(${(1 - clamp((f - 46) / 10)) * 18}px)">
        ${Clock(ctx, { size: 108, keys: [{ f: 46, hour: 0 }, { f: 58, hour: 3 }, { f: 74, hour: 3 }, { f: 86, hour: 9 }] })}
        <span style="font-size:72px;font-weight:800;direction:ltr;opacity:${clamp((f - 56) / 5)}">3:00</span>
        <i style="display:block;height:6px;border-radius:3px;background:${c.accent};width:${90 * Easing.out(clamp((f - 66) / 10))}px"></i>
        <span style="font-size:72px;font-weight:800;direction:ltr;color:${c.accent};display:inline-block;opacity:${clamp((f - 74) / 4)};transform:scale(${0.7 + 0.3 * spring(f, 74, { stiffness: 220, damping: 14 })})">9:00</span>
      </div></div>`,
  });

  // 3) Location card: logo mark + "عيادات القمة" + pin on "القادسية" (3.1s – 5.3s)
  html += GlassCard(ctx, {
    inF: 94, outF: 158, y: 372, w: 800, h: 262, from: 'right',
    children: `<div style="display:flex;align-items:center;gap:34px;direction:rtl">
      <div style="width:200px;height:200px;border-radius:30px;background:#000;display:flex;align-items:center;justify-content:center;box-shadow:inset 0 0 0 1.5px ${c.accent}44">
        ${Logo(ctx, { src: brand.logoMark, height: 170, at: 96, glow: false })}</div>
      <div style="display:flex;flex-direction:column;gap:6px">
        ${KineticWord(ctx, { text: 'عيادات القمة', at: 102, size: 74, underline: false })}
        <div style="display:flex;align-items:center;gap:14px;height:90px">
          ${MapPin(ctx, { at: 137, size: 56 })}
          <span style="font-size:58px;font-weight:700;color:${c.accent};opacity:${clamp((f - 139) / 6)}">القادسية</span>
        </div></div></div>`,
  });

  // 4) Lower third — speaker identity (5.3s – 7.4s)
  html += LowerThird(ctx, { inF: 160, outF: 222, name: 'د. زيد نوري الشريفي', title: 'طبيب أسنان', x: 500, y: 372 });

  // 5) Orthodontics: teeth draw, brackets pop, wire draws on "التقويم", follow-up timeline on "أول بأول"
  const tl = (i, at) => {
    const s = spring(f, at, { stiffness: 260, damping: 15 });
    return `<b style="width:24px;height:24px;border-radius:50%;display:block;background:${s > 0.05 ? c.accent : 'transparent'};
      border:2.5px solid ${c.accent};transform:scale(${0.5 + 0.5 * Math.max(s, 0.01)});box-shadow:0 0 ${16 * s}px ${c.accent}"></b>`;
  };
  const lineP = Easing.out(clamp((f - 270) / 22));
  html += GlassCard(ctx, {
    inF: 219, outF: 300, y: 372, w: 800, h: 270,
    children: `<div style="display:flex;flex-direction:column;align-items:center;gap:6px">
      ${BracesIllustration(ctx, { teethF: 221, bracketsF: 244, wireF: 257, width: 500, height: 140 })}
      <div style="display:flex;align-items:center;gap:28px;margin-top:4px">
        ${KineticWord(ctx, { text: 'التقويم', at: 259, size: 60 })}
        <div style="position:relative;display:flex;gap:46px;align-items:center;opacity:${clamp((f - 268) / 5)}">
          <i style="position:absolute;right:12px;top:11px;height:3px;width:${(70 * 2) * lineP}px;background:${c.accent}88"></i>
          ${tl(0, 272)}${tl(1, 280)}${tl(2, 288)}
        </div>
        <span style="font-size:44px;font-weight:700;opacity:${clamp((f - 272) / 6)}">متابعة أول بأول</span>
      </div></div>`,
  });

  // 6) 9.8s – 11.3s: visual rest (captions only)

  // 7) End card: full logo + slogan, word-synced (11.3s – end)
  const sw = Easing.out(clamp((f - 348) / 14));
  html += GlassCard(ctx, {
    inF: END_CARD - 4, outF: 420, y: 372, w: 800, h: 270,
    children: `<div style="position:absolute;inset:0;background:#000;opacity:.55"></div>
      <div style="position:relative;display:flex;align-items:center;gap:38px;direction:rtl">
        ${Logo(ctx, { src: brand.logoFull, height: 230, at: END_CARD - 2 })}
        <div style="display:flex;flex-direction:column;align-items:flex-start;gap:4px">
          ${KineticWord(ctx, { text: 'القمة..', at: END_CARD, size: 92, underline: false, color: c.accent })}
          <div style="position:relative;font-size:62px;font-weight:800;display:flex;gap:14px">
            <span style="opacity:${clamp((f - 346) / 5)}">اختياركم</span>
            <span style="opacity:${clamp((f - 360) / 5)}">صحيح</span>
            <i style="position:absolute;right:0;bottom:-4px;height:6px;border-radius:3px;background:linear-gradient(270deg,${c.accent},${c.purple});width:${sw * 100}%"></i>
          </div></div></div>`,
  });

  html += Captions(ctx, { groups: captions, y: 975, hideAfter: END_CARD });

  return { zoom, grade, html };
}
