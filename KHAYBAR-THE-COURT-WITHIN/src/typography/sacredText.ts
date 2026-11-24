/**
 * Verified on-screen sacred texts — single source: docs/SOURCES.md.
 * DO NOT edit, fracture, distort, dissolve or animate individual glyphs.
 */
export const SACRED = {
  Q01: {
    lines: ["بَلِ ٱلْإِنسَٰنُ عَلَىٰ نَفْسِهِۦ بَصِيرَةٌۭ", "وَلَوْ أَلْقَىٰ مَعَاذِيرَهُۥ"],
    reference: "القيامة: ١٤–١٥",
    font: "quran" as const,
  },
  Q02: {
    lines: ["كُونُوا۟ قَوَّٰمِينَ بِٱلْقِسْطِ شُهَدَآءَ لِلَّهِ", "وَلَوْ عَلَىٰٓ أَنفُسِكُمْ"],
    reference: "النساء: من الآية ١٣٥",
    font: "quran" as const,
  },
  H01: {
    lines: [
      "لَيْسَ مِنَّا مَنْ لَمْ يُحَاسِبْ نَفْسَهُ فِي كُلِّ يَوْمٍ،",
      "فَإِنْ عَمِلَ حَسَناً اسْتَزَادَ اللهَ،",
      "وَإِنْ عَمِلَ سَيِّئاً اسْتَغْفَرَ اللهَ مِنْهُ وَتَابَ إِلَيْهِ",
    ],
    speaker: "الإمام موسى الكاظم عليه السلام",
    reference: "الكافي — الشيخ الكليني — ج٢ — باب محاسبة العمل — ح٢",
    font: "narration" as const,
  },
} as const;
export type SacredId = keyof typeof SACRED;
