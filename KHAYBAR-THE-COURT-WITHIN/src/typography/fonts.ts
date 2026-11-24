import "@fontsource/ibm-plex-sans-arabic/arabic-400.css";
import "@fontsource/ibm-plex-sans-arabic/arabic-600.css";
import "@fontsource/ibm-plex-sans-arabic/latin-400.css";
import "@fontsource/amiri/arabic-400.css";
import "@fontsource/amiri/arabic-700.css";
import "@fontsource/amiri-quran/arabic-400.css";
import { useEffect, useState } from "react";
import { continueRender, delayRender } from "remotion";

export const FONT = {
  editorial: '"IBM Plex Sans Arabic", sans-serif',
  narration: '"Amiri", serif',
  quran: '"Amiri Quran", serif',
} as const;

/** Blocks rendering until all film fonts are loaded (no fallback-glyph frames). */
export const useFilmFonts = () => {
  const [handle] = useState(() => delayRender("film fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load('400 60px "IBM Plex Sans Arabic"', "تخيّل"),
      document.fonts.load('600 60px "IBM Plex Sans Arabic"', "تخيّل"),
      document.fonts.load('400 60px "Amiri"', "لَيْسَ مِنَّا"),
      document.fonts.load('400 60px "Amiri Quran"', "بَلِ ٱلْإِنسَٰنُ"),
    ]).finally(() => continueRender(handle));
  }, [handle]);
};
