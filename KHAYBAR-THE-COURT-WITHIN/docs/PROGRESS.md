# PROGRESS — THE COURT WITHIN

| البند | الحالة |
|---|---|
| Project Status | Pre-production |
| Current Phase | PHASE 1 — SCRIPT AND SOURCES LOCK (جزئي) → **متوقف: بانتظار السيناريو V2.1** |
| Approval Status | GATE 0: ✅ موافقة مشروطة (2026-11-24). GATE 1: ⏳ |
| Render Status | لا رندر. لا npm install بعد. |

## Approved Decisions
`CREATIVE_DIRECTION.md` (بما فيها قسم «قرارات GATE 0»).

## Completed Tasks
- PHASE 0: فحص المستودع والبيئة؛ وثائق التدقيق. Push `348dd0a` إلى `ccr-42be31ff-39y1is` (متحقق عبر `git ls-remote`).
- نسخ مكونات هوية خيبر 2.0 من `ccr-8a7d9a45-oav171` بايت-ببايت (متحقق بالهاش) دون تعديل الشعار.
- هيكل المجلدات حسب الوثيقة (§26) + `.gitignore` + `package.json` مثبت الإصدارات.
- PHASE 1 (جزئي): `SOURCES.md` — مطابقة القيامة 14–15 (Tanzil) ورواية الكافي ج2 باب محاسبة العمل ح2 (Thaqalayn).

## Modified / Created Files
- `docs/`: CREATIVE_DIRECTION.md, TECHNICAL_PLAN.md, PROGRESS.md (محدَّثة)، SOURCES.md (جديد)، `docs/brand/*` (منسوخ).
- `brand/**`, `src/brand/**`, `src/components/KhaybarLogo.tsx`, `src/compositions/KhaybarOutro.tsx`, `tsconfig.json`, `remotion.config.ts`, `public/brand/reference/khaybar-outro-short.mp4` (منسوخة).
- `package.json`, `.gitignore`, `.gitkeep` للمجلدات الفارغة (جديدة).

## Pending (من صاحب المشروع)
1. **النص الكامل للسيناريو V2.1** ← حاجز PHASE 1.
2. بقية الآيات والروايات مع إحالاتها.
3. اعتماد رسم الآية (عثماني/إملائي) وصيغة عرض الرواية.
4. تأكيد ص453 وبيانات الطبعة.
5. الصور المرجعية الـ17 (قبل PHASE 3).

## Known Issues
- الصفحة 453 والطبعة غير متحققتين (النسخة الرقمية بلا أرقام صفحات).
- النسخة الرقمية تضع «(صلى الله عليه وآله)» بعد «أبي الحسن الماضي»، والترجمة الإنجليزية تخطئ في هويته — يُطابق مع الطبعة الورقية.
- لا GPU — الرندر برمجي (يُقاس في POC).
- `src/index.ts` و`Root.tsx` غير منشأين؛ المشروع غير قابل للتشغيل بعد (متعمد — لا تثبيت قبل PHASE 4).

## Next Action
عند استلام V2.1: إنشاء `SCRIPT.md` (النص المنطوق نظيفاً، تقسيم المقاطع للتسجيل، توجيهات الأداء والوقفات في ملف/قسم منفصل لا يُقرأ في ElevenLabs)، واستكمال SOURCES.md لكل دليل → GATE 1.

## Resume Instructions
1. الفرع `ccr-42be31ff-39y1is`؛ اقرأ هذا الملف ثم `CREATIVE_DIRECTION.md` ثم `SOURCES.md`.
2. لا تُعِد فحص البيئة (TECHNICAL_PLAN §1) ولا نسخ الهوية (§8.1).
3. لا تتجاوز GATE 1 دون موافقة.
