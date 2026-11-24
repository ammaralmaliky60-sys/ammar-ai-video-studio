import raw from "../../brand/design-tokens/tokens.json";

type Entry = { value: string };
const pick = <T extends Record<string, unknown>>(o: T) =>
  Object.fromEntries(
    Object.entries(o)
      .filter(([k]) => !k.startsWith("_"))
      .map(([k, v]) => [k, (v as Entry).value]),
  ) as Record<string, string>;

/** Approved KHAYBAR palette — single source: brand/design-tokens/tokens.json */
export const color = pick(raw.color.brand) as {
  primaryBackground: string;
  heritageGold: string;
  warmIvory: string;
  insightTurquoise: string;
  secondarySurface: string;
};

/** Technical shades for metallic finishes only (not a new palette). */
export const derived = pick(raw.color.derived) as {
  backgroundDeep: string;
  goldHighlight: string;
  goldLight: string;
  goldShadow: string;
  ivoryHighlight: string;
  ivoryShadow: string;
  turquoiseLight: string;
  turquoiseDeep: string;
};

export const font = {
  display: '"Noto Kufi Arabic", sans-serif',
  latin: '"IBM Plex Mono", monospace',
};

export const FPS = 30;
export const FRAME = { width: 1080, height: 1920 };
