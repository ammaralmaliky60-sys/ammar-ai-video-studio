import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { KhaybarLogo } from "../components/KhaybarLogo";
import { useBrandFonts } from "../brand/fonts";
import { color, font } from "../brand/tokens";

/** Every timing is in seconds and can be overridden per video. */
export type OutroTiming = {
  threshold: [number, number];
  arch: [number, number];
  ring: [number, number];
  word: [number, number];
  dots: [number, number];
  metallic: [number, number];
  tagline: [number, number];
  handle: [number, number];
};

export type KhaybarOutroProps = {
  totalSeconds: number;
  showTagline: boolean;
  tagline: string;
  showHandle: boolean;
  platforms: string;
  handle: string;
  timing: OutroTiming;
};

export const outroDefaults: KhaybarOutroProps = {
  totalSeconds: 3.4,
  showTagline: true,
  tagline: "بالعقل نقرأ… وبالبصيرة نرى",
  showHandle: true,
  platforms: "TIKTOK · INSTAGRAM",
  handle: "@bab.5aybar",
  timing: {
    threshold: [0.0, 0.28],
    arch: [0.12, 0.6],
    ring: [0.3, 0.95],
    word: [0.6, 1.08],
    dots: [1.0, 1.32],
    metallic: [1.25, 1.7],
    tagline: [1.7, 2.1],
    handle: [1.9, 2.3],
  },
};

const ease = Easing.bezier(0.22, 1, 0.36, 1);

export const KhaybarOutro: React.FC<KhaybarOutroProps> = (p) => {
  useBrandFonts();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const prog = ([a, b]: [number, number]) =>
    interpolate(t, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });

  const reveal = {
    threshold: prog(p.timing.threshold),
    arch: prog(p.timing.arch),
    ring: prog(p.timing.ring),
    word: prog(p.timing.word),
    dots: interpolate(t, p.timing.dots, [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    metallic: prog(p.timing.metallic),
  };
  // the logo settles: a very small scale-in while it builds, then still
  const settle = interpolate(t, [0, p.timing.metallic[1]], [0.965, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  const tg = prog(p.timing.tagline);
  const hd = prog(p.timing.handle);

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(70% 45% at 50% 40%, ${color.secondarySurface} 0%, ${color.primaryBackground} 72%)`,
        direction: "rtl",
      }}
    >
      <div style={{ position: "absolute", left: 140, top: 340, width: 800, height: 800, transform: `scale(${settle})` }}>
        <KhaybarLogo size={800} reveal={reveal} />
      </div>

      {p.showTagline ? (
        <div
          style={{
            position: "absolute",
            top: 1205,
            width: "100%",
            textAlign: "center",
            fontFamily: font.display,
            fontWeight: 500,
            fontSize: 52,
            color: color.warmIvory,
            opacity: tg,
            transform: `translateY(${(1 - tg) * 18}px)`,
          }}
        >
          {p.tagline}
        </div>
      ) : null}

      {p.showHandle ? (
        <div
          style={{
            position: "absolute",
            top: p.showTagline ? 1330 : 1230,
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 18,
            opacity: hd,
            transform: `translateY(${(1 - hd) * 14}px)`,
            direction: "ltr",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
            <div style={{ width: 150 * hd, height: 2, background: color.heritageGold, opacity: 0.7 }} />
            <div style={{ width: 14, height: 14, background: color.insightTurquoise, transform: "rotate(45deg)" }} />
            <div style={{ width: 150 * hd, height: 2, background: color.heritageGold, opacity: 0.7 }} />
          </div>
          <div style={{ fontFamily: font.latin, fontWeight: 500, fontSize: 26, letterSpacing: 9, color: color.heritageGold }}>
            {p.platforms}
          </div>
          <div style={{ fontFamily: font.latin, fontWeight: 500, fontSize: 50, color: color.warmIvory }}>{p.handle}</div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
