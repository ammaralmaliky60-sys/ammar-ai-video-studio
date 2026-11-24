# ASSET MANIFEST — THE COURT WITHIN

## Voice-over (PHASE 2)
| ID | المسار | SHA-256 | الحجم | المدة (ث) | المصدر | الترخيص/الحالة |
|---|---|---|---|---|---|---|
| VO_CH01 | `public/audio/voiceover/01_Summons.mp3` | `dddec4996214991e4d236f91fb1e4cb536c0f714b4a2c2f1cf6a2ea282ff7803` | 483,379 | 29.152653 | صاحب المشروع — ElevenLabs — أرشيف `KHAYBAR_V2.2_VOICEOVER.zip` | مُنتَج بحساب صاحب المشروع؛ حقوق الاستخدام التجاري تتبع شروط خطة ElevenLabs الخاصة به (لم يُتحقق منها) |
| VO_CH02 | `public/audio/voiceover/02_Witness.mp3` | `bf7daefa050a4d668cea6b59196952726b75fbb446419a6149caa8f2d4d782fc` | 594,974 | 36.127347 | صاحب المشروع — ElevenLabs — أرشيف `KHAYBAR_V2.2_VOICEOVER.zip` | مُنتَج بحساب صاحب المشروع؛ حقوق الاستخدام التجاري تتبع شروط خطة ElevenLabs الخاصة به (لم يُتحقق منها) |
| VO_CH03 | `public/audio/voiceover/03_Quran.mp3` | `ace45acc203c783418e73bbc83bff87607322f90bb0fb2b7a4e725fda46076b7` | 672,714 | 40.986122 | صاحب المشروع — ElevenLabs — أرشيف `KHAYBAR_V2.2_VOICEOVER.zip` | مُنتَج بحساب صاحب المشروع؛ حقوق الاستخدام التجاري تتبع شروط خطة ElevenLabs الخاصة به (لم يُتحقق منها) |
| VO_CH04 | `public/audio/voiceover/04_Justice.mp3` | `b32ce9798bccc7e5cbdba9d081c4b29ae03a18fb32f55ccfdae77d4034224004` | 712,421 | 43.467755 | صاحب المشروع — ElevenLabs — أرشيف `KHAYBAR_V2.2_VOICEOVER.zip` | مُنتَج بحساب صاحب المشروع؛ حقوق الاستخدام التجاري تتبع شروط خطة ElevenLabs الخاصة به (لم يُتحقق منها) |
| VO_CH05 | `public/audio/voiceover/05_Reveal.mp3` | `2836ac1d3d1bdb86544887646811921e38de83a954c8efad854a652a21ade1b3` | 594,974 | 36.127347 | صاحب المشروع — ElevenLabs — أرشيف `KHAYBAR_V2.2_VOICEOVER.zip` | مُنتَج بحساب صاحب المشروع؛ حقوق الاستخدام التجاري تتبع شروط خطة ElevenLabs الخاصة به (لم يُتحقق منها) |
| VO_CH06 | `public/audio/voiceover/06_Imam_Kadhim.mp3` | `801d77a5584157ceadbe0c60da182105abbd6abee67490e76516890bce5540cc` | 933,939 | 57.312653 | صاحب المشروع — ElevenLabs — أرشيف `KHAYBAR_V2.2_VOICEOVER.zip` | مُنتَج بحساب صاحب المشروع؛ حقوق الاستخدام التجاري تتبع شروط خطة ElevenLabs الخاصة به (لم يُتحقق منها) |
| VO_CH07 | `public/audio/voiceover/07_Final_Verdict.mp3` | `acbb3675f43a635102c6e5f06af10dbd6d76b3b7347379c8a43e4bd596a3ca3c` | 452,868 | 27.245714 | صاحب المشروع — ElevenLabs — أرشيف `KHAYBAR_V2.2_VOICEOVER.zip` | مُنتَج بحساب صاحب المشروع؛ حقوق الاستخدام التجاري تتبع شروط خطة ElevenLabs الخاصة به (لم يُتحقق منها) |

## Alignment data (PHASE 2 — مولّدة محلياً، بيانات لا أصول)
| المسار | المحتوى |
|---|---|
| `docs/alignment/WHISPER_TRANSCRIPTS.json` | تفريغ Whisper الخام مع توقيت الكلمات واحتمالاتها |
| `docs/alignment/ANCHORS_ALIGNMENT.json` | 51 مرسى دلالي بالتوقيت المحلي والعام والإطار ودرجة التطابق |
| `docs/alignment/COMPLETENESS_CHECK.json` | مقارنة 95 سطراً من السيناريو مع التفريغ |
الأداة: faster-whisper 1.2.1 (MIT) + نموذج Whisper small (MIT، OpenAI؛ تحويل Systran). النموذج والبيئة **خارج المستودع** ولم يُرفعا.

## Brand (منسوخة من `ccr-8a7d9a45-oav171` — متطابقة بايت-ببايت، انظر TECHNICAL_PLAN §8.1)
| المسار | الحالة |
|---|---|
| `brand/design-tokens/tokens.json`, `brand/logo/**` | ملك المشروع — لا تُعدَّل |
| `src/brand/*`, `src/components/KhaybarLogo.tsx`, `src/compositions/KhaybarOutro.tsx` | ملك المشروع |
| `public/brand/reference/khaybar-outro-short.mp4` | 2.500ث، 1080×1920، 30fps، H.264، **بلا مسار صوت** (مقاس بـ ffprobe) |

## مفقود
SFX / Ambience / Foley (لا يوجد أي ملف في المشروع أو الفروع المفحوصة) · الصور المرجعية الـ17 · النماذج والخامات · ملفات الخطوط المحلية.

## SFX — متطلبات مبدئية (لا تُولَّد الآن)
الأصول المتاحة لإعادة الاستخدام: **لا يوجد أي ملف صوتي/مؤثر** في المشروع أو فروعه المفحوصة؛ خاتمة خيبر بلا صوت.
لا موسيقى، لا خلفيات لحنية أو إيقاعية. الآيات والرواية: بلا مؤثرات درامية (Ambience خافت فقط أو صمت).

| # | المؤثر | الفصل | التصنيف | ملاحظة المواصفات |
|---|---|---|---|---|
| 1 | تشقق المرآة (crack spread) | CH01 | **Essential** | 1–1.5ث، WAV 48k، ذيل نظيف، يتزامن مع انتشار التشقق |
| 2 | شظايا زجاج معلقة / tinkle | CH01, CH05 | **Essential · Reusable** | طبقات قصيرة 0.3–2ث |
| 3 | عبور بوابة المرآة (whoosh غير موسيقي + هواء) | CH01 | **Essential** | 1–2ث |
| 4 | Room tone للمحكمة (صدى قاعة حجرية/خشبية) | CH01–CH05 | **Essential · Reusable** | حلقة ≥30ث قابلة للتكرار بلا قطع |
| 5 | ضربة مطرقة خشبية | CH01/CH02 | **Essential · Reusable** | ضربة جافة + صدى قاعة، 2–3 تنويعات |
| 6 | أوراق الأدلة | CH02 | Optional · Reusable | 0.5–1.5ث |
| 7 | انتقال الذكرى (شظية → مشهد) | CH02 | Pending Animatic | — |
| 8 | تشكّل كتلة بازلت + سقوط حجر | CH02 | **Essential · Reusable** | 3 تنويعات ثقل، low-end محسوب لا يغطي الصوت |
| 9 | تشقق الحجر (hairline → fracture) | CH03, CH05 | **Essential · Reusable** | — |
| 10 | حركة الميزان (معدن/سلسلة خفيفة) | CH04 | **Essential** | خافت، لا يتعارض مع المقارنات الثلاث |
| 11 | كشف الهوية (نبضة منخفضة غير موسيقية + صمت) | CH05 | Pending Animatic | — |
| 12 | انهيار الجدار | CH05 | **Essential** | 2–4ث، يليه صمت درامي |
| 13 | تفكك المحكمة (تلاشٍ/غبار) | CH05 | Optional | — |
| 14 | جو الحل الهادئ (هواء ناعم) | CH06–CH07 | **Essential · Reusable** | حلقة ≥30ث، منخفضة جداً تحت الرواية |
| 15 | تحول المطرقة → مرآة | CH06 | Pending Animatic | بعد انتهاء الرواية لا أثناءها |
| 16 | تحول المرآة → باب | CH07 | Pending Animatic | — |
| 17 | خطوات الشخصية | CH01, CH07 | Optional · Reusable | على حجر/خشب |
| 18 | جو هواء مفتوح | CH07 | Optional | — |
| 19 | توقيع صوتي لخيبر | Outro | Optional · Pending Animatic | الخاتمة الحالية صامتة؛ قرارك |

لا يُطلب توليد أي منها الآن. القائمة النهائية بالمدد تُثبت بعد Animatic.

## PHASE 3 — Animatic (منشأة محلياً)
| المسار | النوع | الحالة |
|---|---|---|
| `src/index.ts`, `src/Root.tsx` | Remotion entry (AnimaticFull, AnimaticOpening, TypographyTest) | مصدر |
| `src/animatic/Animatic.tsx` | Animatic SVG/2.5D حتمي | مصدر — ليس الفيلم النهائي |
| `src/animatic/TypographyTest.tsx` | لوحة اختبار سلامة الحروف | مصدر |
| `src/typography/fonts.ts`, `src/typography/sacredText.ts` | تحميل الخطوط + النصوص المقدسة المتحققة | مصدر |
| `src/config/timeline.json` | خط زمني مضغوط (95 سطراً + 7 فصول + خاتمة) | بيانات مشتقة |
| `previews/animatic/*` | معاينات منخفضة الدقة | انظر PROGRESS للمسارات الفعلية |

**خطوط جديدة (npm، OFL-1.1، محلية):** `@fontsource/ibm-plex-sans-arabic@5.3.0`، `@fontsource/amiri@5.3.0`، `@fontsource/amiri-quran@5.3.0`. `node_modules/` مستثنى من Git.
**لم يُضف** Three.js ولا نماذج ولا خامات في هذه المرحلة.

## GATE 3A — Look Development
| المسار | المحتوى |
|---|---|
| `src/lookdev/lookdev_frames.py` | مشهد Blender/Cycles الحتمي للإطارات A/B/C |
| `previews/lookdev/frame-{A,B,C}-1080x1920.png`, `lookdev-contact-sheet.png` | إطارات تجريبية للمراجعة |
الأدوات والأصول الخارجية (Blender، MPFB، suits01 CC0، Poly Haven CC0) موثقة مع مصادرها وتراخيصها وتحقق السلامة في `docs/LOOKDEV.md` §4 — **غير مضافة إلى المستودع**.

## GATE 3A V2
| المسار | المحتوى |
|---|---|
| `public/references/REF_01.jpg … REF_20.jpg` | مراجع بصرية (WebP) — **للتحليل فقط، حقوق الرندر غير مثبتة**؛ لا تدخل أي إطار أو فيديو |
| `docs/REFERENCE_GUIDE.md` | دليل المالك للمراجع |
| `src/lookdev/lookdev_frames_v2.py` | مشهد V2 |
| `previews/lookdev/frame-{A,B,C}-V2-1080x1920.png`, `v1-vs-v2-comparison.png` | مراجعة |
حزمة الشعر `hair01` (CC0، 227.8 MB) خارج المستودع.
