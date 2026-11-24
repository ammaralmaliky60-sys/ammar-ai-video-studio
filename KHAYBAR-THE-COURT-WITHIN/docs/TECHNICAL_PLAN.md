# TECHNICAL PLAN — THE COURT WITHIN

PHASE 0 — مسودة للمراجعة (لم يُنفَّذ أي رندر أو تثبيت بعد).

## 1. البيئة المفحوصة فعلياً
| البند | النتيجة الفعلية |
|---|---|
| Node.js / npm | v22.23.5 / 10.9.9 |
| ffmpeg / ffprobe | 6.1.1 ✅ |
| Chromium + Playwright | مثبت مسبقاً (`/opt/pw-browsers`, headless shell 1243) ✅ |
| CPU / RAM / Disk | 4 أنوية / 15GB / ~60GB متاحة |
| GPU | ❌ لا يوجد (`/dev/dri` غير موجود) |
| WebGL في Chromium | ✅ **WebGL2 عبر SwiftShader (برمجي على المعالج)**، MAX_TEXTURE_SIZE=8192 — اختُبر فعلياً بسكربت Playwright |
| Remotion (npm registry) | أحدث إصدار 4.0.546؛ فرع الهوية مثبّت على 4.0.541 |
| Three.js (npm) | 0.187.0 |
| الشبكة | npm و Google Fonts / GitHub متاحة عبر الوكيل |
| الحاوية | سحابية مؤقتة: أي ملف غير مدفوع إلى GitHub يضيع عند انتهاء الجلسة |

## 2. القرار التقني المقترح
- **Remotion 4.0.541** (نفس إصدار فرع الهوية لتجنب تحديث الاعتماديات) + `@remotion/three` بنفس الإصدار + `three` + `@react-three/fiber`.
- أساس المشروع: **نقل (نسخ) نظام الهوية من فرع `ccr-8a7d9a45` إلى `KHAYBAR-THE-COURT-WITHIN/`** دون تعديل الشعار — يتطلب موافقتك.
- الرندر: `--gl=swiftshader` (أو angle)، `--concurrency=2..3`، اختبارات بـ 540×960 أولاً.
- الخطوط: ملفات `.woff2/.ttf` محلية في `public/fonts/` (IBM Plex Sans Arabic، Amiri، Amiri Quran، Cinzel — جميعها OFL) + `delayRender` حتى اكتمال التحميل.
- النصوص الدينية: طبقات HTML/CSS في Remotion فوق مشهد Three.js (لا نص عربي داخل WebGL). نصوص الأعذار المحفورة: Canvas texture مرسوم من نفس الخط ثم يُطبَّق كخريطة Normal/Alpha على الكتل.

## 3. الهيكل المقترح
```
KHAYBAR-THE-COURT-WITHIN/
  public/{audio/{voiceover,ambience,foley,sfx},references,textures,models,fonts,brand}
  src/{scenes,components,three,shaders,transitions,typography,lighting,audio,config}
  docs/  previews/  renders/
```
`src/config/` يضم: tokens (مستوردة من الهوية)، camera presets (24/35/50/85mm → FOV رأسي لإطار 9:16)، lighting phases (7 مراحل)، safe-zones.

## 4. الحتمية (Deterministic Rendering)
- كل حركة من `useCurrentFrame()`؛ لا `Date.now`/`Math.random`/`requestAnimationFrame` مستقل.
- `random(seed)` من Remotion لكل الجزيئات والشظايا.
- التشقق والانهيار: هندسة مكسورة مسبقاً (Voronoi محسوب ببذرة ثابتة) + منحنيات حركة محسوبة — **لا محاكاة فيزيائية حية**.
- الجزيئات: `InstancedMesh` بمواقع دالة في رقم الإطار.

## 5. المخاطر التقنية (مرتبة حسب الخطورة)
| # | الخطر | الأثر | التخفيف |
|---|---|---|---|
| R1 | **لا GPU — WebGL برمجي** | رندر Three.js بطيء جداً مع Bloom/DoF/Volumetrics/ظلال ناعمة؛ قد يصل إلى ثوانٍ لكل إطار → 300ث = 9000 إطار | POC بدقة منخفضة لقياس زمن الإطار فعلياً؛ تخفيف المؤثرات بعد المعالجة؛ Baking للإضاءة في الخامات؛ رندر طبقات منفصلة (Compositing)؛ أو الرندر النهائي على جهازك إن كان لديك GPU |
| R2 | **الشخصية البشرية الواقعية مجهولة الملامح** | لا يوجد نموذج؛ بناؤها إجرائياً لن يبلغ الواقعية المطلوبة؛ الحركة تحتاج Rig | تحتاج نموذجاً جاهزاً مرخّصاً (CC0/مشتري) أو حلاً سينمائياً: صورة ظلية بإضاءة خلفية (Silhouette/Rim light) تخفي التفاصيل وتخدم «مجهول الملامح» — **قرار يعود لك** |
| R3 | تحول المطرقة ← المرآة (POC 03) | قد يبدو Morph الهندسي مشوهاً | انتقال مخفي عبر وميض ضوئي/دوران/Rack focus — بديل يُعرض عليك قبل اعتماده |
| R4 | نص عربي محفور ثلاثي الأبعاد | تشكيل الحروف غير مدعوم في TextGeometry | Canvas 2D بالخط الحقيقي (يدعم التشكيل) → texture |
| R5 | الذاكرة وتسرّب موارد WebGL بين الإطارات | انهيار الرندر الطويل | تقسيم الفيلم إلى Compositions لكل فصل وتجميعها بـ ffmpeg |
| R6 | ضياع العمل عند انتهاء الحاوية | فقدان الملفات | Commits محلية + **Push إلى فرع الجلسة فقط بإذنك** |
| R7 | دقة النصوص الدينية | خطأ عقدي/تحريري | SOURCES.md؛ لا يُعتمد نص لم يُتحقق منه؛ الرسم القرآني يُطابق مع مصحف معتمد (مثل نص تنزيل/مصحف المدينة) |
| R8 | مدة الرندر الكامل | استهلاك وقت | رندر لكل مشهد على حدة، والكامل مرة واحدة في PHASE 8–9 |

## 6. خطة المراحل (ملخص)
| المرحلة | المخرج | البوابة |
|---|---|---|
| 0 Audit | هذه الوثائق | **GATE 0 ← الآن** |
| 1 Script & Sources | SCRIPT.md, SOURCES.md، تقسيم التسجيل وتوجيهات الأداء | GATE 1 |
| 2 VO Intake | فحص الصوت، AUDIO_CUES.json، قائمة SFX | GATE 2 |
| 3 Animatic | STORYBOARD.md + Animatic تخطيطي متزامن (540×960) | GATE 3 |
| 4 POC | POC 01/02/03 + قياس زمن الإطار (يبدأ بـ POC 02 أو 01 حسب قرار الشخصية) | GATE 4 |
| 5 World Build | المحكمة، الأدوات، الخامات، الإضاءة، المحراب، Style Frames | GATE 5 |
| 6 Scenes | دفعات مشاهد | GATE 6 |
| 7 Sound | مكساج بلا موسيقى (-14 إلى -16 LUFS، ≤ -1 dBTP) | GATE 7 |
| 8 QA | QUALITY_CHECKLIST.md | GATE 8 |
| 9 Delivery | MP4 H.264 yuv420p AAC 48kHz faststart + تقرير | — |

ملاحظة: يمكن بدء POC 02 (جدار الأعذار) تقنياً قبل استلام الصوت لأنه لا يعتمد على التوقيت — فقط إن أذنت بتقديم PHASE 4 جزئياً.

## 7. ترشيد الاستهلاك
- لا إعادة قراءة لفروع الهوية: ما يلزم موثق هنا.
- إعادة استخدام tokens/fonts/KhaybarLogo/KhaybarOutro بدل إعادة بنائها.
- تثبيت الاعتماديات مرة واحدة بإصدارات مثبتة.
- اختبارات 540×960 ومقاطع قصيرة؛ لا رندر كامل قبل PHASE 8.
- PROGRESS.md نقطة استئناف لكل جلسة.
