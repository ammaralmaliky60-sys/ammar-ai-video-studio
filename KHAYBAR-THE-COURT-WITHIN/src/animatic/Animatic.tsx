/**
 * THE COURT WITHIN — Cinematic ANIMATIC (planning instrument, NOT the final film).
 * Low-cost SVG/2.5D stand-ins driven by docs/SHOT_LIST.json and the measured audio timeline.
 * Fully frame-driven and deterministic (no Date / Math.random / timers).
 */
import React from "react";
import {
  AbsoluteFill, Audio, Easing, interpolate, OffthreadVideo, random, Sequence, staticFile, useCurrentFrame,
} from "remotion";
import shotList from "../../docs/SHOT_LIST.json";
import timeline from "../config/timeline.json";
import { color, derived } from "../brand/tokens";
import { FONT, useFilmFonts } from "../typography/fonts";
import { SACRED, SacredId } from "../typography/sacredText";

type Shot = (typeof shotList.shots)[number];
const W = 1080, H = 1920;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.bezier(0.4, 0, 0.2, 1);
const lerp = (f: number, a: number, b: number, from = 0, to = 1) => interpolate(f, [a, b], [from, to], { ...clamp, easing: ease });

/* ---------- lighting journey (7 phases) ---------- */
const PHASE_BG: Record<number, [string, string]> = {
  1: ["#02090b", color.primaryBackground],
  2: ["#05141a", "#10262b"],
  3: ["#020607", "#0a1a1e"],
  4: ["#061a20", color.secondarySurface],
  5: ["#0b1c20", "#3a3322"],
  6: ["#13282b", "#5a4a2e"],
  7: ["#3b3424", "#efe2c4"],
};

/* ---------- primitives ---------- */
const Figure: React.FC<{ x: number; y: number; s?: number; rim?: string; o?: number; glow?: number }> = ({ x, y, s = 1, rim = color.insightTurquoise, o = 1, glow = 0 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} opacity={o}>
    {glow > 0 && <ellipse cx={0} cy={-150} rx={110} ry={220} fill={color.heritageGold} opacity={0.18 * glow} />}
    {/* faceless human silhouette: no facial features by design */}
    <circle cx={0} cy={-300} r={34} fill="#05090a" stroke={rim} strokeWidth={3} />
    <path d="M-30 -262 Q0 -250 30 -262 L58 -150 L46 -20 L22 -20 L14 -110 L-14 -110 L-22 -20 L-46 -20 L-58 -150 Z" fill="#05090a" stroke={rim} strokeWidth={3} />
  </g>
);

/** KHAYBAR-inspired arch outline (frame of mirror / knowledge arch / gateway). */
const archPath = (cx: number, top: number, w: number, h: number) => {
  const r = w / 2;
  return `M${cx - r} ${top + h} L${cx - r} ${top + r} A${r} ${r} 0 0 1 ${cx + r} ${top + r} L${cx + r} ${top + h} Z`;
};
const Arch: React.FC<{ cx?: number; top: number; w: number; h: number; fill?: string; stroke?: string; sw?: number; o?: number }> = ({ cx = W / 2, top, w, h, fill = "none", stroke = color.heritageGold, sw = 8, o = 1 }) => (
  <path d={archPath(cx, top, w, h)} fill={fill} stroke={stroke} strokeWidth={sw} opacity={o} />
);

const Cracks: React.FC<{ cx: number; cy: number; amount: number; seed: string; glow?: number }> = ({ cx, cy, amount, seed, glow = 0 }) => {
  const n = 14;
  return (
    <g>
      {Array.from({ length: n }).map((_, i) => {
        const a = (i / n) * Math.PI * 2 + random(`${seed}a${i}`) * 0.4;
        const len = (180 + random(`${seed}l${i}`) * 420) * amount;
        const mx = cx + Math.cos(a) * len * 0.5 + (random(`${seed}m${i}`) - 0.5) * 60 * amount;
        const my = cy + Math.sin(a) * len * 0.5 + (random(`${seed}n${i}`) - 0.5) * 60 * amount;
        return <polyline key={i} points={`${cx},${cy} ${mx},${my} ${cx + Math.cos(a) * len},${cy + Math.sin(a) * len}`} fill="none"
          stroke={glow > 0 ? derived.goldLight : color.warmIvory} strokeWidth={2 + glow * 3} opacity={0.75} />;
      })}
    </g>
  );
};

const Hall: React.FC<{ zoom?: number; fx?: number; fy?: number; dim?: number; children?: React.ReactNode }> = ({ zoom = 1, fx = W / 2, fy = 1100, dim = 0, children }) => (
  <g transform={`translate(${fx} ${fy}) scale(${zoom}) translate(${-fx} ${-fy})`}>
    {/* high windows + volumetric shafts */}
    {[300, 540, 780].map((x, i) => (
      <g key={x}>
        <rect x={x - 40} y={260} width={80} height={220} fill={derived.goldHighlight} opacity={0.35} />
        <polygon points={`${x - 40},480 ${x + 40},480 ${x + 160 - i * 60},1500 ${x - 120 - i * 40},1500`} fill={derived.goldHighlight} opacity={0.06} />
      </g>
    ))}
    {/* columns */}
    {[90, 230, 850, 990].map((x) => <rect key={x} x={x - 38} y={200} width={76} height={1450} fill="#0b1a1d" stroke={color.secondarySurface} strokeWidth={4} />)}
    {/* judge bench */}
    <rect x={300} y={820} width={480} height={240} fill="#2a1c12" stroke={color.heritageGold} strokeWidth={3} />
    {/* witness stand */}
    <rect x={780} y={1040} width={150} height={150} fill="#24180f" stroke={derived.goldShadow} strokeWidth={2} />
    {/* accused platform */}
    <rect x={420} y={1500} width={240} height={40} fill="#1a120c" stroke={color.heritageGold} strokeWidth={2} />
    <rect x={0} y={1640} width={W} height={280} fill="#060c0e" />
    {children}
    <rect x={0} y={0} width={W} height={H} fill="#000" opacity={dim} />
  </g>
);

const Block: React.FC<{ x: number; y: number; w?: number; h?: number; text?: string; o?: number; cracked?: number }> = ({ x, y, w = 300, h = 170, text, o = 1, cracked = 0 }) => (
  <g opacity={o}>
    <rect x={x - w / 2} y={y - h / 2} width={w} height={h} fill="#141618" stroke="#2c3134" strokeWidth={4} />
    {text && <text x={x} y={y + 14} textAnchor="middle" direction="rtl" fontFamily={FONT.editorial} fontWeight={600} fontSize={34}
      fill="#3b4246" stroke="#000" strokeWidth={0.6} opacity={1 - cracked * 0.8}>{text}</text>}
    {cracked > 0 && <Cracks cx={x} cy={y} amount={cracked * 0.35} seed={`blk${x}${y}`} glow={1} />}
  </g>
);

const Scale: React.FC<{ tilt: number; same?: boolean; labels?: [string, string] }> = ({ tilt, same, labels }) => {
  const cx = W / 2, cy = 820, arm = 330, a = (tilt * Math.PI) / 180;
  const lx = cx - Math.cos(a) * arm, ly = cy - Math.sin(a) * arm, rx = cx + Math.cos(a) * arm, ry = cy + Math.sin(a) * arm;
  const pan = (x: number, y: number, k: string, lab?: string, heavy?: boolean) => (
    <g key={k}>
      <line x1={x} y1={y} x2={x - 90} y2={y + 260} stroke={color.heritageGold} strokeWidth={3} />
      <line x1={x} y1={y} x2={x + 90} y2={y + 260} stroke={color.heritageGold} strokeWidth={3} />
      <path d={`M${x - 120} ${y + 260} Q${x} ${y + 330} ${x + 120} ${y + 260} Z`} fill={derived.goldShadow} />
      <rect x={x - 45} y={y + 200} width={90} height={60} fill={same ? "#26292b" : heavy ? "#1b1d1f" : "#3a3f42"} />
      {lab && <text x={x} y={y + 400} textAnchor="middle" direction="rtl" fontFamily={FONT.editorial} fontWeight={600} fontSize={44} fill={color.warmIvory}>{lab}</text>}
    </g>
  );
  return (
    <g>
      <rect x={cx - 170} y={1420} width={340} height={70} fill="#111315" stroke="#2c3134" strokeWidth={4} />
      <rect x={cx - 14} y={cy} width={28} height={600} fill={color.heritageGold} />
      <line x1={lx} y1={ly} x2={rx} y2={ry} stroke={color.heritageGold} strokeWidth={14} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={22} fill={derived.goldLight} />
      {pan(lx, ly, "l", labels?.[0], true)}
      {pan(rx, ry, "r", labels?.[1])}
    </g>
  );
};

/* ---------- text layers (HTML for correct Arabic shaping) ---------- */
const Impact: React.FC<{ text: string; o: number; y?: number; gold?: boolean; size?: number }> = ({ text, o, y = 1460, gold, size = 104 }) => (
  <div style={{ position: "absolute", top: y, left: 90, right: 90, textAlign: "center", direction: "rtl", fontFamily: FONT.editorial, fontWeight: 600,
    fontSize: size, color: gold ? color.heritageGold : color.warmIvory, opacity: o, textShadow: "0 4px 30px rgba(0,0,0,.7)" }}>{text}</div>
);

const SacredPanel: React.FC<{ id: SacredId; o: number }> = ({ id, o }) => {
  const s = SACRED[id];
  const big = s.font === "quran";
  return (
    <div style={{ position: "absolute", top: big ? 700 : 640, left: 120, right: 120, textAlign: "center", direction: "rtl", opacity: o }}>
      {"speaker" in s && <div style={{ fontFamily: FONT.narration, fontSize: 46, color: color.heritageGold, marginBottom: 26 }}>{s.speaker}</div>}
      {s.lines.map((l) => (
        <div key={l} style={{ fontFamily: FONT[s.font], fontSize: big ? 76 : 56, lineHeight: big ? 2.0 : 1.85, color: color.warmIvory }}>{l}</div>
      ))}
      <div style={{ fontFamily: FONT.editorial, fontSize: 38, color: color.heritageGold, marginTop: 30 }}>{s.reference}</div>
    </div>
  );
};

/* ---------- scene renderer ---------- */
const anchorF = (shot: Shot, i = 0) => shot.anchors[i]?.frame ?? shot.start_frame;

const Scene: React.FC<{ shot: Shot; f: number }> = ({ shot, f }) => {
  const s = shot.start_frame, e = shot.end_frame, p = lerp(f, s, e), lf = f - s;
  const [bgA, bgB] = PHASE_BG[shot.lighting_phase] ?? PHASE_BG[2];
  let svg: React.ReactNode = null, html: React.ReactNode = null;
  const fade = (a: number, d = 12) => lerp(f, a, a + d);

  switch (shot.animatic_scene) {
    case "mirror": {
      const major = anchorF(shot, 1); // «صار دليل ضدّك»
      const hair = lerp(f, s + 15, major, 0, 0.35);
      const big = lerp(f, major, major + 10, 0, 1);
      const z = 1 + p * 0.08 + big * 0.03;
      svg = (<g transform={`translate(540 960) scale(${z}) translate(-540 -960)`}>
        <Arch top={360} w={760} h={1200} fill="#081e25" sw={10} />
        <Figure x={540} y={1380} s={1.6} rim={color.insightTurquoise} o={0.75} />
        <Cracks cx={600} cy={820} amount={hair + big * 0.75} seed="mirror" glow={big} />
        {big > 0 && <circle cx={600} cy={820} r={30 + big * 40} fill={derived.goldHighlight} opacity={0.5 * (1 - big) + 0.15} />}
      </g>);
      break;
    }
    case "shards": case "mask_shards": {
      const k = shot.animatic_scene === "shards" ? 16 : 3;
      svg = (<g>{Array.from({ length: k }).map((_, i) => {
        const x = 120 + random(`sx${i}`) * 840, y = 300 + random(`sy${i}`) * 1300, d = 0.6 + random(`sd${i}`) * 0.9;
        const sc = (k === 3 ? 2.2 : 1) * d * (1 + p * 0.5), rot = (random(`sr${i}`) - 0.5) * 40 + p * 20 * (random(`sq${i}`) - 0.5);
        // background shards recede/darken so the hero shard reads clearly
        return (<g key={i} opacity={k === 3 ? 1 : 0.55} transform={`translate(${k === 3 ? 270 + i * 270 : x} ${k === 3 ? 960 : y}) rotate(${rot}) scale(${k === 3 ? sc : sc * 0.8})`}>
          <polygon points="-80,-120 70,-100 95,60 -20,130 -100,40" fill="#0c2a31" stroke={color.warmIvory} strokeWidth={2} opacity={0.9} />
          {k === 3 && <Figure x={0} y={90} s={0.35} rim={color.insightTurquoise} />}
        </g>);
      })}
      {shot.animatic_scene === "shards" && (() => {
        // HERO shard: grows toward camera; courtroom reflection appears inside on «رجع حتى يشهد عليك»
        const g = 1.6 + p * 1.4, reveal = lerp(f, s + (e - s) * 0.5, s + (e - s) * 0.68);
        return (<g transform={`translate(600 900) rotate(${-8 + p * 6}) scale(${g})`}>
          <clipPath id="hero"><polygon points="-80,-120 70,-100 95,60 -20,130 -100,40" /></clipPath>
          <polygon points="-80,-120 70,-100 95,60 -20,130 -100,40" fill="#0c2a31" stroke={derived.goldLight} strokeWidth={3} />
          <g clipPath="url(#hero)" opacity={reveal}><g transform="scale(0.17) translate(-540 -1050)"><Hall><Figure x={540} y={1500} s={0.6} /></Hall></g></g>
        </g>);
      })()}</g>);
      break;
    }
    case "portal": {
      const t = lerp(f, s, s + 40);
      svg = (<g>
        <Hall zoom={1.35 - lerp(f, s + 20, e) * 0.3}><Figure x={540} y={1500} s={0.6} /></Hall>
        <g opacity={1 - t}><rect width={W} height={H} fill="#081e25" />
          <polygon points={`${540 - 900 * t - 60},${960 - 1300 * t - 90} ${540 + 900 * t + 60},${960 - 1200 * t - 80} ${540 + 950 * t + 80},${960 + 1300 * t + 60} ${540 - 950 * t - 100},${960 + 1250 * t + 40}`} fill="none" stroke={color.warmIvory} strokeWidth={6} /></g>
      </g>);
      const tIn = s + 30, tOut = Math.min(e - 5, tIn + 75);
      html = <div style={{ position: "absolute", top: 260, left: 80, right: 180, textAlign: "center", direction: "rtl", fontFamily: FONT.editorial, fontWeight: 600, fontSize: 104,
        color: color.heritageGold, opacity: lerp(f, tIn, tIn + 15) * (1 - lerp(f, tOut, tOut + 10)), letterSpacing: 2, textShadow: "0 6px 40px rgba(0,0,0,.8)" }}>المحكمة التي بداخلك</div>;
      break;
    }
    case "court_wide": case "court_ots": {
      const ots = shot.animatic_scene === "court_ots";
      svg = <Hall zoom={ots ? 1.25 : 1 + p * 0.12} fx={ots ? 540 + (p - 0.5) * 300 : 540}><Figure x={540} y={1500} s={0.6} />
        <Figure x={540} y={830} s={0.5} rim={derived.goldShadow} o={0.8} /><Figure x={855} y={1060} s={0.45} rim={derived.goldShadow} o={0.7} />
        {ots && <Figure x={300} y={2300} s={2.6} rim={color.insightTurquoise} />}</Hall>;
      if (shot.id === "S01_04") html = <Impact text="التهمة؟" o={fade(anchorF(shot) + 50) * (1 - lerp(f, e - 10, e))} />;
      break;
    }
    case "court_judge": case "reveal_judge": {
      const hit = shot.id === "S02_01" ? lerp(f, s, s + 6) : 0;
      svg = <Hall zoom={2.1} fy={900}><Figure x={540} y={830} s={0.5} rim={derived.goldShadow} />
        <rect x={600} y={800} width={70} height={22} fill="#3a2414" stroke={color.heritageGold} strokeWidth={2} transform={`rotate(${-20 + hit * 20} 600 811)`} /></Hall>;
      break;
    }
    case "court_witness": case "reveal_witness":
      svg = <Hall zoom={2.2} fx={855} fy={1060}><Figure x={855} y={1060} s={0.45} rim={derived.goldShadow} /></Hall>;
      break;
    case "evidence":
      svg = <g><rect width={W} height={H} fill="#081417" />{Array.from({ length: 9 }).map((_, i) => (
        <rect key={i} x={140 + random(`ex${i}`) * 700} y={1700 - ((lf * (2 + random(`ev${i}`) * 3) + random(`ey${i}`) * 1500) % 1700)} width={150} height={200}
          fill={color.warmIvory} opacity={0.25 + random(`eo${i}`) * 0.4} transform={`rotate(${(random(`er${i}`) - 0.5) * 50})`} />))}</g>;
      break;
    case "mirror_hint":
      svg = <Hall zoom={1 + p * 1.2} fx={420} fy={860}><polygon points="380,840 450,830 470,860 400,880" fill="#0c2a31" stroke={color.insightTurquoise} strokeWidth={3} />
        <Figure x={540} y={1500} s={0.6} /></Hall>;
      break;
    case "memory":
      svg = <g transform={`translate(540 960) scale(${1 + p * 1.6}) translate(-540 -960)`}>
        <polygon points="240,560 840,600 900,1300 300,1380 180,900" fill="#0c2a31" stroke={color.warmIvory} strokeWidth={4} />
        <Figure x={460} y={1200} s={0.7} rim={color.insightTurquoise} o={0.8} />
        <Figure x={660} y={1200} s={0.7} rim="#7f8c8f" o={0.8 - p * 0.4} /></g>;
      break;
    case "block": case "blocks_low": case "wall_rise": case "wall_stack": case "prison": case "prison_slit": {
      const all = ["چنت معصّب", "ما چنت أريد مشاكل", "مو بس آني… الكل چان يحچي"];
      const idx = shot.id === "S02_03" ? 0 : shot.id === "S02_05" ? 1 : 2;
      const top = shot.animatic_scene === "prison" || shot.animatic_scene === "prison_slit";
      const ring = shot.animatic_scene === "wall_rise" ? lerp(f, s, e) : ["wall_stack", "prison", "prison_slit"].includes(shot.animatic_scene) ? 1 : 0;
      const drop = (k: number) => interpolate(f, [s, s + 14], [-700, 0], { ...clamp, easing: Easing.in(Easing.quad) }) * (k === idx && shot.animatic_scene === "block" ? 1 : 0);
      svg = top ? (<g><rect width={W} height={H} fill="#020405" />
        {Array.from({ length: 12 }).map((_, i) => { const a = (i / 12) * Math.PI * 2; return <rect key={i} x={540 + Math.cos(a) * 300 - 70} y={960 + Math.sin(a) * 300 - 40} width={140} height={80} fill="#141618" stroke="#2c3134" strokeWidth={3} transform={`rotate(${(a * 180) / Math.PI + 90} ${540 + Math.cos(a) * 300} ${960 + Math.sin(a) * 300})`} />; })}
        <circle cx={540} cy={960} r={34} fill="#05090a" stroke={color.insightTurquoise} strokeWidth={3} />
        <rect x={530} y={0} width={20} height={960} fill={derived.goldHighlight} opacity={shot.animatic_scene === "prison_slit" ? 0.35 : 0.12 + (1 - p) * 0.1} /></g>)
        : (<g><Hall dim={0.45 + ring * 0.35} zoom={1.4} fy={1300}>
          <Figure x={540} y={1500} s={0.6} /></Hall>
          {all.map((t, k) => (k <= idx || shot.animatic_scene !== "block") && <Block key={k} x={[260, 820, 540][k]} y={1500 + drop(k) - (k === 2 ? 220 : 0)} text={t} />)}
          {ring > 0 && Array.from({ length: Math.round(ring * 10) }).map((_, i) => <Block key={`r${i}`} x={90 + (i % 5) * 225} y={1720 - Math.floor(i / 5) * 175 - (shot.animatic_scene === "wall_stack" ? lerp(f, s + i * 3, s + i * 3 + 8) * 0 : 0)} w={210} h={160} />)}</g>);
      break;
    }
    case "arch_text": case "arch_name": {
      const id: SacredId | null = shot.id === "S03_02" ? "Q01" : shot.id === "S04_06" ? "Q02" : shot.id === "S06_03" ? "H01" : null;
      const textIn = id === "H01" ? s : anchorF(shot, id ? 1 : 0) - 8;
      svg = <g><rect width={W} height={H} fill="#000" opacity={0.35} />
        <Arch top={420} w={940} h={1180} fill="rgba(7,31,38,0.85)" sw={6} o={lerp(f, s, s + 20)} /></g>;
      html = <>{id ? <SacredPanel id={id} o={lerp(f, textIn, textIn + 15)} />
        : <div style={{ position: "absolute", top: 860, left: 120, right: 120, textAlign: "center", direction: "rtl", fontFamily: FONT.narration, fontSize: 64, color: color.heritageGold, opacity: fade(s + 10, 20) }}>الإمام موسى الكاظم عليه السلام</div>}
        {shot.id === "S03_02" && <Impact text="القرآن الكريم" o={fade(s, 10) * (1 - lerp(f, anchorF(shot, 1) - 12, anchorF(shot, 1)))} y={900} size={70} />}</>;
      break;
    }
    case "wall_hairline": case "crack_light": case "self_reflection": {
      const glow = shot.animatic_scene === "crack_light" ? 0.4 + p * 0.6 : 0.3;
      svg = <g><rect width={W} height={H} fill="#060809" />
        {Array.from({ length: 15 }).map((_, i) => <Block key={i} x={140 + (i % 4) * 270} y={420 + Math.floor(i / 4) * 300} w={250} h={280} />)}
        <Cracks cx={540} cy={900} amount={0.25 + p * 0.25} seed="wall" glow={glow} />
        {shot.animatic_scene === "self_reflection" && <><Figure x={360} y={1700} s={1.4} /><Figure x={720} y={1500} s={1.1} rim={derived.goldShadow} o={0.45} /></>}</g>;
      break;
    }
    case "scale": case "scale_contrast": case "scale_paradox": case "scale_return": {
      const base = { S04_01: 0, S04_02: -8, S04_03: -14, S04_04: -20, S04_05: -20, S04_07: -20 }[shot.id as "S04_01"] ?? 0;
      const prev = { S04_02: 0, S04_03: -8, S04_04: -14 }[shot.id as "S04_02"];
      const tilt = shot.id === "S04_07" ? interpolate(p, [0, 1], [-20, -6]) : prev !== undefined ? interpolate(lerp(f, s + 30, s + 60), [0, 1], [prev, base]) : base;
      const labels: Record<string, [string, string]> = { S04_02: ["قليل احترام", "چنت معصّب"], S04_03: ["خذلك", "حكمة"], S04_04: ["إساءة", "فضفضة"] };
      svg = <g transform={shot.id === "S04_05" ? "translate(540 900) scale(1.3) translate(-540 -900)" : undefined}><Scale tilt={tilt} same={shot.id === "S04_05"} labels={labels[shot.id]} /></g>;
      if (shot.id === "S04_05") html = <Impact text="نفس الفعل…" o={fade(s + 4)} y={300} />;
      break;
    }
    case "reveal_orbit": case "identity": case "identity_all": case "reflections": {
      const base = shot.animatic_scene === "reveal_orbit" ? p * 120 : shot.id === "S05_04" ? 120 : shot.id === "S05_05" ? 240 : 360;
      const ang = shot.animatic_scene === "identity" || shot.animatic_scene === "identity_all" ? base - 20 + lerp(f, s, s + 20) * 20 : base;
      const who = { S05_04: 0, S05_05: 1, S05_06: 3 }[shot.id as "S05_04"] ?? -1;
      const pos = [0, 1, 2].map((i) => { const a = ((ang + i * 120) * Math.PI) / 180; return { x: 540 + Math.sin(a) * 300, y: 1250 + Math.cos(a) * 110, d: (Math.cos(a) + 2) / 3 }; });
      svg = <g><rect width={W} height={H} fill="#070d0f" />
        {pos.sort((a, b) => a.d - b.d).map((q, i) => <Figure key={i} x={q.x} y={q.y + 250} s={0.9 * q.d + 0.3}
          rim={who === 3 || who === i ? color.heritageGold : derived.goldShadow} glow={who === 3 || who === i ? lerp(f, s, s + 10) : 0}
          o={shot.animatic_scene === "reflections" && i < 2 ? 1 - p : 1} />)}
        {shot.animatic_scene === "reflections" && <Cracks cx={540} cy={700} amount={0.4} seed="refl" />}</g>;
      const imp: Record<string, string> = { S05_04: "القاضي… إنت", S05_05: "والشاهد… إنت", S05_06: "والمتهم… هم إنت" };
      if (imp[shot.id]) html = <Impact text={imp[shot.id]} o={fade(s + 2, 8)} y={360} gold={shot.id === "S05_06"} />;
      if (shot.id === "S05_07") html = <Impact text="بداخلك" o={fade(anchorF(shot) + 18)} y={360} gold />;
      break;
    }
    case "cracks_spread": case "stillness": case "collapse": {
      const c = shot.animatic_scene === "collapse" ? lerp(f, s + 20, s + 90) : 0;
      svg = <g><rect width={W} height={H} fill="#060809" />
        <rect width={W} height={H} fill={derived.goldHighlight} opacity={c * 0.7} />
        {Array.from({ length: 15 }).map((_, i) => { const bx = 140 + (i % 4) * 270, by = 420 + Math.floor(i / 4) * 300;
          return <g key={i} transform={`translate(${(bx - 540) * c * 1.5} ${c * c * 900}) rotate(${c * (random(`cr${i}`) - 0.5) * 60} ${bx} ${by})`}>
            <Block x={bx} y={by} w={250} h={280} cracked={shot.animatic_scene === "cracks_spread" ? p : 1} o={1 - c * 0.8} /></g>; })}
        <Figure x={540} y={1700} s={1.1} rim={c > 0.5 ? color.heritageGold : color.insightTurquoise} /></g>;
      break;
    }
    case "open_space": case "stage1": case "stage2": case "stage3": {
      svg = <g><Arch top={520} w={760} h={1000} sw={5} o={shot.animatic_scene === "open_space" ? 0.25 : 0.6} />
        {shot.animatic_scene === "stage1" && <circle cx={540} cy={900} r={330} fill="none" stroke={color.heritageGold} strokeWidth={6} strokeDasharray={`${p * 2073} 2073`} />}
        {shot.animatic_scene === "stage2" && Array.from({ length: 40 }).map((_, i) => <circle key={i} cx={540 + (random(`px${i}`) - 0.5) * 600 * (1 - p * 0.6)} cy={900 + (random(`py${i}`) - 0.5) * 700 * (1 - p * 0.6)} r={6} fill={derived.goldLight} opacity={0.4 + p * 0.5} />)}
        {shot.animatic_scene === "stage3" && <><rect x={390} y={1180} width={300} height={200} fill="#2a2a28" /><polyline points="420,1200 520,1290 480,1330 660,1370" fill="none" stroke={color.heritageGold} strokeWidth={8} strokeDasharray={`${p * 400} 400`} /></>}
        <Figure x={540} y={1720} s={1.0} rim={color.heritageGold} /></g>;
      const lab: Record<string, string> = { S06_04: "أولاً: المحاسبة كل يوم", S06_05: "ثانياً: إذا سويت خير", S06_06: "وثالثاً: إذا أخطأت" };
      if (lab[shot.id]) html = <Impact text={lab[shot.id]} o={fade(s + 4)} y={300} size={78} />;
      if (shot.id === "S06_06") html = <><Impact text={lab[shot.id]} o={fade(s + 4) * (1 - lerp(f, anchorF(shot, 1) - 10, anchorF(shot, 1)))} y={300} size={78} />
        <div style={{ position: "absolute", top: 300, left: 90, right: 90, textAlign: "center", direction: "rtl", fontFamily: FONT.narration, fontSize: 84, color: color.heritageGold, opacity: fade(anchorF(shot, 1), 15) }}>استغفر الله… وتُب إليه</div></>;
      break;
    }
    case "gavel_mirror": {
      const m = lerp(f, s + 30, e - 20);
      svg = <g transform={`rotate(${(1 - m) * -25} 540 900)`}>
        <g opacity={1 - m}><rect x={380} y={820} width={320} height={110} rx={20} fill="#3a2414" stroke={color.heritageGold} strokeWidth={6} /><rect x={525} y={930} width={30} height={380} fill="#3a2414" /></g>
        <g opacity={m} transform={`translate(540 980) scale(${0.3 + m * 0.7}) translate(-540 -980)`}><Arch top={400} w={640} h={1060} fill="#0d2a31" sw={10} /><Figure x={540} y={1380} s={1.2} o={0.7} /></g>
        <Figure x={540} y={1850} s={0.9} rim={color.heritageGold} o={m} /></g>;
      break;
    }
    case "mirror_whole": case "questions": case "block_dissolve":
      svg = <g><Arch top={360} w={760} h={1200} fill="#0b2228" sw={10} /><Figure x={540} y={1380} s={1.6} o={0.8} rim={color.heritageGold} />
        {shot.animatic_scene === "block_dissolve" && <Block x={540} y={1650} text="عذر جديد؟" o={1 - lerp(f, anchorF(shot, 1) - 20, anchorF(shot, 1) + 10)} />}</g>;
      if (shot.animatic_scene === "questions") html = <>{shot.anchors.map((a, i) => (
        <div key={i} style={{ position: "absolute", top: 1610 + i * 0, left: 80, right: 80, textAlign: "center", direction: "rtl", fontFamily: FONT.editorial, fontSize: 58, color: color.warmIvory,
          opacity: lerp(f, (a.frame ?? s) - 4, (a.frame ?? s) + 8) * (1 - lerp(f, (shot.anchors[i + 1]?.frame ?? e + 99) - 8, shot.anchors[i + 1]?.frame ?? e + 99)) }}>
          {a.text.replace(/^\[question \d\] /, "")}</div>))}</>;
      break;
    case "gateway": case "final_text": {
      const g = shot.animatic_scene === "gateway" ? p : 1;
      svg = <g><Arch top={360 - g * 260} w={760 + g * 260} h={1200 + g * 380} fill={derived.ivoryHighlight} sw={12 + g * 6} />
        <Figure x={540} y={1650 - g * 180} s={1.4 - g * 0.6} rim={color.heritageGold} /></g>;
      if (shot.animatic_scene === "final_text") html = <>
        <div style={{ position: "absolute", top: 260, left: 60, right: 60, textAlign: "center", direction: "rtl", fontFamily: FONT.editorial, fontWeight: 600, fontSize: 96, color: color.primaryBackground, opacity: fade(anchorF(shot, 0)) }}>قبل لا تحاسب غيرك…</div>
        <div style={{ position: "absolute", top: 420, left: 60, right: 60, textAlign: "center", direction: "rtl", fontFamily: FONT.editorial, fontWeight: 600, fontSize: 140, color: derived.goldShadow, opacity: fade(anchorF(shot, 1)) }}>حاسب نفسك</div></>;
      break;
    }
    default: svg = null;
  }
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 35%, ${bgB} 0%, ${bgA} 75%)` }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute" }}>{svg}</svg>
      {html}
    </AbsoluteFill>
  );
};

/* ---------- review overlays (animatic only) ---------- */
const SAFE = { top: 160, bottom: 420, right: 160, left: 60 };
const Overlays: React.FC<{ shot: Shot; f: number; safe: boolean }> = ({ shot, f, safe }) => {
  const line = timeline.lines.find((l) => f >= l.s && f < l.e + 8);
  const near = shot.anchors.find((a) => a.frame !== null && f >= a.frame && f < a.frame + 20);
  const tc = `${Math.floor(f / 1800)}:${String(Math.floor((f / 30) % 60)).padStart(2, "0")}.${String(f % 30).padStart(2, "0")}`;
  const sacred = shot.animatic_scene === "arch_text";
  return (
    <>
      <div style={{ position: "absolute", top: 24, left: 24, right: 24, display: "flex", justifyContent: "space-between", fontFamily: FONT.editorial, fontSize: 30,
        color: color.insightTurquoise, direction: "ltr", opacity: 0.85 }}>
        <span>ANIMATIC · {shot.id} · {shot.chapter}</span><span>F{f} · {tc}</span>
      </div>
      {near && <div style={{ position: "absolute", top: 70, left: 24, fontFamily: FONT.editorial, fontSize: 28, color: near.manual ? "#ffb35c" : color.heritageGold, direction: "rtl" }}>
        ⚑ {near.text}{near.manual ? " — يحتاج تحققاً يدوياً" : ""}</div>}
      {line && !sacred && <div style={{ position: "absolute", bottom: SAFE.bottom + 20, left: 80, right: SAFE.right, textAlign: "center", direction: "rtl", fontFamily: FONT.editorial,
        fontSize: 40, color: color.warmIvory, background: "rgba(0,0,0,.45)", padding: "10px 18px", borderRadius: 10 }}>{line.text}</div>}
      {safe && <svg width={W} height={H} style={{ position: "absolute" }}>
        <rect x={SAFE.left} y={SAFE.top} width={W - SAFE.left - SAFE.right} height={H - SAFE.top - SAFE.bottom} fill="none" stroke="#ff5c5c" strokeWidth={2} strokeDasharray="12 10" opacity={0.55} />
      </svg>}
    </>
  );
};

export type AnimaticProps = { showSafeZones: boolean; showOverlays: boolean };

export const Animatic: React.FC<AnimaticProps> = ({ showSafeZones, showOverlays }) => {
  useFilmFonts();
  const f = useCurrentFrame();
  const shot = (shotList.shots.find((x) => f >= x.start_frame && f < x.end_frame) ?? shotList.shots[shotList.shots.length - 1]) as Shot;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {timeline.chapters.map((c) => (
        <Sequence key={c.id} from={c.start} durationInFrames={c.frames} layout="none"><Audio src={staticFile(c.file)} /></Sequence>
      ))}
      {shot.animatic_scene === "outro" ? (
        <Sequence from={timeline.outro.start} durationInFrames={timeline.outro.frames}><OffthreadVideo src={staticFile(timeline.outro.file)} muted /></Sequence>
      ) : (
        <Scene shot={shot} f={f} />
      )}
      {showOverlays && shot.animatic_scene !== "outro" && <Overlays shot={shot} f={f} safe={showSafeZones} />}
    </AbsoluteFill>
  );
};
