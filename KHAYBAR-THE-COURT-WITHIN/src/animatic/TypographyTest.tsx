import React from "react";
import { AbsoluteFill } from "remotion";
import { color } from "../brand/tokens";
import { FONT, useFilmFonts } from "../typography/fonts";
import { SACRED } from "../typography/sacredText";

/** Glyph-integrity test sheet for the sacred texts (not part of the film). */
export const TypographyTest: React.FC = () => {
  useFilmFonts();
  const block = (id: "Q01" | "Q02" | "H01", size: number) => {
    const s = SACRED[id];
    return (
      <div style={{ marginBottom: 70, textAlign: "center" }}>
        <div style={{ fontFamily: FONT.editorial, fontSize: 30, color: color.insightTurquoise }}>{id}</div>
        {s.lines.map((l) => (
          <div key={l} style={{ fontFamily: FONT[s.font], fontSize: size, lineHeight: 1.9, color: color.warmIvory }}>{l}</div>
        ))}
        <div style={{ fontFamily: FONT.editorial, fontSize: 36, color: color.heritageGold }}>{s.reference}</div>
      </div>
    );
  };
  return (
    <AbsoluteFill style={{ background: color.primaryBackground, direction: "rtl", padding: 60, justifyContent: "center" }}>
      {block("Q01", 74)}
      {block("Q02", 64)}
      {block("H01", 54)}
      <div style={{ fontFamily: FONT.editorial, fontSize: 56, color: color.warmIvory, textAlign: "center" }}>
        تخيّل لو كل عذر گُلته بحياتك… صار دليل ضدّك
      </div>
    </AbsoluteFill>
  );
};
