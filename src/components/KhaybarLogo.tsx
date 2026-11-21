import React, { useId } from "react";
import paths from "../brand/logoPaths.json";
import { color, derived } from "../brand/tokens";

export type LogoVariant = "full" | "avatar" | "small";

type LogoGeometry = {
  R: number; disc: string; ring: string; dots: string | null; arch: string[]; opening: string;
  threshold: string; word_body: string; kha_dot: string; turq: string[];
  ring_width: number; arch_top: number; arch_leg: number;
};

/** 0 = hidden, 1 = fully built. All default to 1 (static logo). */
export type LogoReveal = {
  threshold?: number;
  arch?: number;
  ring?: number;
  word?: number;
  dots?: number; // 0..1 across the four dots (kha dot, then ي ي, then ب — right to left)
  metallic?: number; // cross-fade Flat Official Gold -> Cinematic Metallic Gold
};

type Props = {
  variant?: LogoVariant;
  reveal?: LogoReveal;
  /** draw the dark disc behind the emblem */
  disc?: boolean;
  size?: number;
  style?: React.CSSProperties;
};

const clamp = (v: number) => Math.max(0, Math.min(1, v));

/**
 * KHAYBAR 2.0 official emblem. Geometry comes from scripts/build_logo.py
 * (src/brand/logoPaths.json) — identical to brand/logo/*.svg. Never redraw it here.
 */
export const KhaybarLogo: React.FC<Props> = ({ variant = "full", reveal = {}, disc = true, size = 1000, style }) => {
  const g = (paths as unknown as Record<LogoVariant, LogoGeometry>)[variant];
  const uid = useId().replace(/:/g, "");
  const id = (n: string) => `${n}-${uid}`;
  const r = {
    threshold: clamp(reveal.threshold ?? 1),
    arch: clamp(reveal.arch ?? 1),
    ring: clamp(reveal.ring ?? 1),
    word: clamp(reveal.word ?? 1),
    dots: clamp(reveal.dots ?? 1),
    metallic: clamp(reveal.metallic ?? 0),
  };
  const ringMid = g.R - g.ring_width / 2;
  const C = 2 * Math.PI * ringMid;
  const archTop = g.arch_top - 4;
  const archY = g.arch_leg - r.arch * (g.arch_leg - archTop);
  const dotList = [g.kha_dot, g.turq[2], g.turq[1], g.turq[0]];
  const dotScale = (i: number) => {
    const t = clamp(r.dots * dotList.length - i);
    return 1 - Math.pow(1 - t, 3);
  };

  const layer = (finish: "flat" | "cinematic") => {
    const cin = finish === "cinematic";
    const gold = cin ? `url(#${id("gold")})` : color.heritageGold;
    const ringFill = cin ? `url(#${id("ringg")})` : color.heritageGold;
    const ivory = cin ? `url(#${id("ivory")})` : color.warmIvory;
    const turq = cin ? `url(#${id("turq")})` : color.insightTurquoise;
    return (
      <g>
        <g mask={`url(#${id("ringmask")})`}>
          <path d={g.ring} fill={ringFill} fillRule="evenodd" />
          {g.dots ? <path d={g.dots} fill={gold} opacity={0.8} /> : null}
        </g>
        {cin ? <path d={g.opening} fill={`url(#${id("glow")})`} /> : null}
        <g clipPath={`url(#${id("archclip")})`} fill={gold}>
          {g.arch.map((d) => (
            <path key={d} d={d} />
          ))}
        </g>
        <path d={g.threshold} fill={gold} transform={`translate(500 0) scale(${r.threshold} 1) translate(-500 0)`} />
        <path d={g.word_body} fill={ivory} clipPath={`url(#${id("wordclip")})`} />
        {dotList.map((d, i) => (
          <path
            key={d}
            d={d}
            fill={i === 0 ? ivory : turq}
            style={{ transformBox: "fill-box", transformOrigin: "center", transform: `scale(${dotScale(i)})` }}
          />
        ))}
      </g>
    );
  };

  return (
    <svg viewBox="0 0 1000 1000" width={size} height={size} style={style} aria-label="خيبر KHAYBAR">
      <defs>
        <mask id={id("ringmask")} maskUnits="userSpaceOnUse" x="0" y="0" width="1000" height="1000">
          <circle
            cx={500}
            cy={500}
            r={ringMid - 10}
            fill="none"
            stroke="#fff"
            strokeWidth={g.ring_width + 60}
            strokeDasharray={C}
            strokeDashoffset={C * (1 - r.ring)}
            transform="rotate(-90 500 500)"
          />
        </mask>
        <clipPath id={id("archclip")}>
          <rect x={0} y={archY} width={1000} height={Math.max(0, g.arch_leg + 2 - archY)} />
        </clipPath>
        <clipPath id={id("wordclip")}>
          <rect x={830 - r.word * 660} y={0} width={r.word * 660} height={1000} />
        </clipPath>
        <radialGradient id={id("disc")} cx="50%" cy="44%" r="58%">
          <stop offset="0" stopColor={color.secondarySurface} />
          <stop offset=".72" stopColor={derived.backgroundDeep} />
          <stop offset="1" stopColor={color.primaryBackground} />
        </radialGradient>
        <linearGradient id={id("gold")} gradientUnits="userSpaceOnUse" x1="250" y1="150" x2="760" y2="800">
          <stop offset="0" stopColor={derived.goldHighlight} />
          <stop offset=".34" stopColor={color.heritageGold} />
          <stop offset=".62" stopColor={derived.goldShadow} />
          <stop offset=".82" stopColor={derived.goldLight} />
          <stop offset="1" stopColor={color.heritageGold} />
        </linearGradient>
        <linearGradient id={id("ringg")} gradientUnits="userSpaceOnUse" x1="120" y1="80" x2="880" y2="920">
          <stop offset="0" stopColor={derived.goldHighlight} />
          <stop offset=".3" stopColor={color.heritageGold} />
          <stop offset=".55" stopColor={derived.goldShadow} />
          <stop offset=".78" stopColor={derived.goldLight} />
          <stop offset="1" stopColor={derived.goldShadow} />
        </linearGradient>
        <linearGradient id={id("ivory")} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={derived.ivoryHighlight} />
          <stop offset="1" stopColor={derived.ivoryShadow} />
        </linearGradient>
        <linearGradient id={id("turq")} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={derived.turquoiseLight} />
          <stop offset=".55" stopColor={color.insightTurquoise} />
          <stop offset="1" stopColor={derived.turquoiseDeep} />
        </linearGradient>
        <radialGradient id={id("glow")} cx="50%" cy="46%" r="62%">
          <stop offset="0" stopColor={color.heritageGold} stopOpacity={0.2} />
          <stop offset="1" stopColor={color.heritageGold} stopOpacity={0} />
        </radialGradient>
      </defs>
      {disc ? (
        <>
          <path d={g.disc} fill={color.primaryBackground} opacity={clamp(Math.max(r.arch, r.ring) * 1.4)} />
          <path d={g.disc} fill={`url(#${id("disc")})`} opacity={r.metallic} />
        </>
      ) : null}
      {r.metallic < 1 ? <g opacity={1}>{layer("flat")}</g> : null}
      {r.metallic > 0 ? <g opacity={r.metallic}>{layer("cinematic")}</g> : null}
    </svg>
  );
};
