# خاتمة خيبر 2.0 (KhaybarOutro)

تحل محل التوقيع القديم `khaybar-signature.mp4`.

| الملف | المدة | المحتوى |
|---|---|---|
| `exports/video/khaybar-outro.mp4` | 3.4 ث | الشعار ← الشعار اللفظي ← المنصات واسم الحساب |
| `exports/video/khaybar-outro-short.mp4` | 2.5 ث | الشعار ← المنصات واسم الحساب |

المواصفات: 1080×1920، 30 إطاراً في الثانية، H.264 بصيغة yuv420p، بلا مسار صوت.

## تسلسل الحركة (بالثواني، وكلها قابلة للتعديل)
| العنصر | البداية–النهاية |
|---|---|
| العتبة تنبسط من الوسط | 0.00–0.28 |
| القوس ينمو من العتبة | 0.12–0.60 |
| الدائرة تكتمل | 0.30–0.95 |
| «خيبر» تُكتب من اليمين إلى اليسار | 0.60–1.08 |
| النقاط: الخاء، ثم الياء، ثم الباء | 1.00–1.32 |
| الانتقال إلى الذهبي المعدني | 1.25–1.70 |
| الشعار اللفظي | 1.70–2.10 |
| المنصات واسم الحساب | 1.90–2.30 |

## التشغيل
```bash
npm install
npm run studio                       # معاينة وتعديل في Remotion Studio
export PW_CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell   # أو احذف --browser-executable على جهازك
npm run render:outro                 # -> exports/video/khaybar-outro.mp4
```
لتغيير المدة أو النص مرّر `--props` بقيم `KhaybarOutroProps`، كما في `src/compositions/KhaybarOutro.tsx`.

## البنية
- `src/components/KhaybarLogo.tsx`: الشعار الرسمي كمكوّن React. ثابت افتراضياً، ويقبل `reveal` للتحريك.
- `src/brand/logoPaths.json`: مسارات الشعار، يولّدها `scripts/build_logo.py`. لا تُعدَّل يدوياً.
- `src/brand/tokens.ts`: الألوان، تُقرأ من `brand/design-tokens/tokens.json`.
- الخطوط: Noto Kufi Arabic للشعار اللفظي، وIBM Plex Mono لاسم الحساب. كلاهما برخصة OFL عبر Fontsource، وهما مؤقتان حتى اعتماد النظام الطباعي.

ملاحظة الترخيص: Remotion مجاني للأفراد والشركات حتى 3 موظفين، وما فوق ذلك يحتاج رخصة شركة (remotion.dev/license).

## مهارة الهوية
`skills/khaybar-brand/` (والملف المضغوط `exports/khaybar-brand-skill.zip`): مهارة تحمل الشعار والخاتمة والألوان والقواعد، وتحل محل مهارة «توقيع خيبر».
