# PROGRESS — THE COURT WITHIN

| البند | الحالة |
|---|---|
| Project Status | Pre-production |
| Current Phase | PHASE 3 — CINEMATIC ANIMATIC (منجز v0.1) → **GATE 3 — AWAITING USER CREATIVE APPROVAL** |
| Approval Status | GATE 0: ✅ · GATE 1: ✅ **مُغلق** (السيناريو V2.2 معتمد رسمياً؛ المصادر متحققة مع قيود موثقة) · GATE 2: ✅ **مُغلق** (2026-11-24 — مراجعة المالك البشرية: نطق 03/04/06 سليم؛ لا إعادة توليد) · GATE 3: ⏳ |
| Render Status | لا رندر. لا npm install. |
| Script | **V2.2 — APPROVED** (`SCRIPT.md`) |
| Narration | 7 ملفات مستوردة ومفحوصة — 270.419591ث |

## Approved Decisions
`CREATIVE_DIRECTION.md` (بما فيها قسم «قرارات GATE 0»).

## GATE 1 — Partial Approval Decisions (2026-11-24)
1. الآيات: رسم عثماني من مصدر موثوق + خط Amiri Quran بعد اختبار الحروف والتشكيل.
2. لفظ رواية الإمام الكاظم ع معتمد كما في `SOURCES.md` (H01).
3. الإحالة: الكافي — الكليني — ج2 — باب محاسبة العمل — ح2 (بلا رقم صفحة).
4. ملاحظات النسخة الرقمية موثقة؛ الترجمة الإنجليزية لا يُعتمد عليها في هوية الإمام.
5. لا خلط مع رواية كتاب الزهد.
6. الرواية في المحراب المعرفي بخط Amiri، ثابتة ومقروءة.
7. **تقسيم التعليق الصوتي المعتمد (7 ملفات، `public/audio/voiceover/`):**
   `01_Summons.mp3` · `02_Witness.mp3` · `03_Quran.mp3` · `04_Justice.mp3` · `05_Reveal.mp3` · `06_Imam_Kadhim.mp3` · `07_Final_Verdict.mp3`
8. ممنوع حالياً: فحص البيئة، تثبيت المكتبات، الرندر، توليد الصوت، كتابة سيناريو بديل.

## PHASE 2 — Results (2026-11-24)
- استيراد `KHAYBAR_V2.2_VOICEOVER.zip`: 7 ملفات بالضبط، بلا تعديل؛ SHA-256 مطابق بعد النسخ.
- فحص تقني كامل (`AUDIO_AUDIT.md`): سليم تقنياً؛ لا أخطاء فك ترميز ولا Clipping. MP3 mono 44.1kHz 128kb/s.
- الفصل 01 أخفض جهارة: −24.4 LUFS (أخفض بـ 3.6 LU من الأعلى) — يُعالج في PHASE 7.
- `AUDIO_CUES.json`: خط زمني مؤقت = 8550 إطاراً (285.0ث) شامل الخاتمة 2.5ث وفواصل مؤقتة 11.97ث؛ المتبقي حتى 300ث = 15.0ث.
- كل المراسي الدلالية = `null / PENDING_VERIFICATION` (لا تفريغ آلي ولا استماع).

## PHASE 3 — Animatic v0.1 (2026-11-24)
- GitHub: `3654fc4` كان مرفوعاً مسبقاً (تحقق `git ls-remote`) — لم يُكرر الرفع.
- **الصور المرجعية الـ17: لم تصل** (BLOCKED) — موثق في REFERENCE_AUDIT.md؛ لم يُخترع أي وصف.
- `SHOT_LIST.json`: 56 لقطة، 0 → 8550 إطاراً، متصلة بلا فجوات؛ `STORYBOARD.md` و`SFX_CUE_SHEET.md` مولّدان منها.
- الطباعة المقدسة: Amiri Quran / Amiri — عرض تقني متحقق (Chromium = HarfBuzz/raqm، بلا glyphs مفقودة)؛ الاعتماد البصري النهائي لك (`previews/animatic/typography-test.png`).
- Animatic Remotion حتمي (SVG/2.5D) + الصوت الأصلي + خاتمة خيبر الرسمية (mp4 مرجعي).
- معاينات فعلية: `previews/animatic/animatic-full-540x960.mp4` (8550 إطاراً، 285.013ث، H.264+AAC، 286ث رندر على CPU بتزامن 4) · `previews/animatic/opening-preview-540x960.mp4` (12.13ث، مقتطع من الكامل) · `previews/animatic/typography-test.png`.

## ⛔ GATE 3A — CINEMATIC VISUAL LOOK DEVELOPMENT (أُضيف بتوجيه المالك، 2026-11-24)
- **المالك لا يعتمد المستوى البصري للـ Animatic** (رسوم هندسية مسطحة). Animatic v0.1 = **مرجع توقيت ومزامنة فقط**، لا مرجع للمظهر.
- التقدم متوقف عند GATE 3. المطلوب: 3 إطارات سينمائية تجريبية (A المرآة، B الكسر، C المحكمة) بمستوى واقعي بعد بيان الجدوى التقنية.
- عائق: الصور المرجعية الـ17 ما زالت غير موجودة في البيئة.

## Decisions Requiring User Approval (GATE 3)
1. الإيقاع والسرد في Animatic (56 لقطة).
2. تصميم الخطاف: الكسر الرئيسي عند «صار دليل ضدّك» F84 (2.8ث)؛ المحكمة تظهر **داخل الشظية** من ≈F198 (6.6ث، على «رجع حتى يشهد عليك») والدخول الكامل عند «وفجأة» F261 (8.7ث) — أي بعد مرجع «4 ثوانٍ» في الوثيقة الأم، لأن التسجيل الفعلي يضع «وفجأة… بمحكمة غريبة» عند 8.7ث. البديل: تقديم ظهور المحكمة في الشظية إلى ≈F135.
3. ظهور العنوان «المحكمة التي بداخلك» عند ≈F291 (9.7ث) لمدة 2.5ث.
4. الطباعة المقدسة (لوحة الاختبار).
5. تسليم الصور المرجعية الـ17 لمراجعة التأطير.
6. إذن رفع commit المرحلة الثالثة.

## PHASE 2 Finalization (2026-11-24)
- Push `1a0eb88` إلى `ccr-42be31ff-39y1is` — متحقق عبر `git ls-remote` (بعد فحص الفرع والشجرة والمحتوى والأسرار).
- Faster-Whisper small/CPU/int8 في venv معزول خارج المستودع؛ 95.96ث للملفات السبعة.
- الاكتمال الآلي: 95/95 سطراً، 0 كلام زائد، 0 Audio Tags منطوقة.
- المراسي: 51/51 مستخرجة آلياً (50 عالية الثقة، 1 منخفضة)، **8 تحتاج تحققاً يدوياً**. لا شيء موسوم «متحقق يدوياً».
- فترات Q01/Q02/H01 محددة للاستماع الإلزامي (AUDIO_AUDIT §5.3).
- الخط الزمني المؤقت دون تغيير: 8550 إطاراً (285.0ث)، فواصل 1.5/2.0/1.5/1.5/2.5/1.5/1.47.

## Remaining to close GATE 2
1. استماعك البشري لـ Q01 (03: 4.5–11.1ث)، Q02 (04: 29.9–36.2ث)، H01 (06: 11.7–24.4ث) — خاصة «عَمِلَ» مقابل «عامل» المرصودة آلياً.
2. قرارك: هل يحتاج أي ملف إعادة توليد؟ (لا دليل تقني على ذلك).
3. الاعتماد الصريح لـ GATE 2.
4. إذن منفصل لرفع commit المرحلة الحالية.

## Decisions Requiring User Approval (GATE 2) — previous list
1. اعتماد نتائج الفحص التقني.
2. **مراجعة بشرية** للنطق في 03 و04 و06 واكتمال النص في الملفات السبعة (لم أستمع إليها).
3. هل تسمح بتفريغ محلي مساعد (Whisper، نموذج متوسط الحجم، مجاني) لاستخراج توقيتات المراسي؟ وإلا تُحدد المراسي يدوياً في Animatic.
4. اعتماد الفواصل المؤقتة بين الفصول (1.5/2.0/1.5/1.5/2.5/1.5/1.47ث) كنقطة انطلاق لـ Animatic.

## Completed Tasks
- PHASE 0: فحص المستودع والبيئة؛ وثائق التدقيق. Push `348dd0a` إلى `ccr-42be31ff-39y1is` (متحقق عبر `git ls-remote`).
- نسخ مكونات هوية خيبر 2.0 من `ccr-8a7d9a45-oav171` بايت-ببايت (متحقق بالهاش) دون تعديل الشعار.
- هيكل المجلدات حسب الوثيقة (§26) + `.gitignore` + `package.json` مثبت الإصدارات.
- PHASE 1 (جزئي): `SOURCES.md` — مطابقة القيامة 14–15 (Tanzil) ورواية الكافي ج2 باب محاسبة العمل ح2 (Thaqalayn).

## Modified / Created Files
- PHASE 2: `docs/SCRIPT.md`, `docs/AUDIO_AUDIT.md`, `docs/AUDIO_CUES.json`, `docs/ASSET_MANIFEST.md` (جديدة)؛ `docs/SOURCES.md`, `docs/PROGRESS.md` (محدثة)؛ `public/audio/voiceover/*.mp3` (7 ملفات مستوردة).
- `docs/`: CREATIVE_DIRECTION.md, TECHNICAL_PLAN.md, PROGRESS.md (محدَّثة)، SOURCES.md (جديد)، `docs/brand/*` (منسوخ).
- `brand/**`, `src/brand/**`, `src/components/KhaybarLogo.tsx`, `src/compositions/KhaybarOutro.tsx`, `tsconfig.json`, `remotion.config.ts`, `public/brand/reference/khaybar-outro-short.mp4` (منسوخة).
- `package.json`, `.gitignore`, `.gitkeep` للمجلدات الفارغة (جديدة).

## Pending (من صاحب المشروع)
1. اعتماد GATE 2 + المراجعة البشرية للنطق.
2. الصور المرجعية الـ17 (قبل PHASE 3).

## Known Issues
- الصفحة 453 غير متحققة — محسوم: لا تُعرض.
- النسخة الرقمية تضع «(صلى الله عليه وآله)» بعد «أبي الحسن الماضي»، والترجمة الإنجليزية تخطئ في هويته — يُطابق مع الطبعة الورقية.
- لا GPU — الرندر برمجي (يُقاس في POC).
- `src/index.ts` و`Root.tsx` غير منشأين؛ المشروع غير قابل للتشغيل بعد (متعمد — لا تثبيت قبل PHASE 4).

## Next Action
بعد اعتماد GATE 3 فقط: PHASE 4 — Technical POC (POC 01 Mirror Portal، POC 02 Excuse Wall، POC 03 Gavel→Mirror). لا انتقال تلقائي.

## Resume Instructions
1. الفرع `ccr-42be31ff-39y1is`؛ اقرأ هذا الملف ثم `CREATIVE_DIRECTION.md` ثم `SOURCES.md`.
2. لا تُعِد فحص البيئة (TECHNICAL_PLAN §1) ولا نسخ الهوية (§8.1).
3. لا تتجاوز GATE 3 دون موافقة. Animatic: `npx remotion studio src/index.ts` (AnimaticFull / AnimaticOpening). المتصفح: `--browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell`. البيانات الصوتية في `AUDIO_AUDIT.md` و`AUDIO_CUES.json` — لا تُعِد القياس.
