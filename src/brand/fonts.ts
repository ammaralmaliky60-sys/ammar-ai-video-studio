import "@fontsource/noto-kufi-arabic/arabic-500.css";
import "@fontsource/noto-kufi-arabic/arabic-700.css";
import "@fontsource/ibm-plex-mono/latin-400.css";
import "@fontsource/ibm-plex-mono/latin-500.css";
import { useEffect, useState } from "react";
import { continueRender, delayRender } from "remotion";

/** Blocks rendering until the brand fonts are ready (no fallback-font frames). */
export const useBrandFonts = () => {
  const [handle] = useState(() => delayRender("brand fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load('500 54px "Noto Kufi Arabic"', "بالعقل نقرأ"),
      document.fonts.load('500 40px "IBM Plex Mono"', "@bab.5aybar"),
    ]).finally(() => continueRender(handle));
  }, [handle]);
};
