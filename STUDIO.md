# استوديو الموشن گرافيك — HyperFrames

هذا المستودع مُجهّز لإنتاج فيديوهات موشن گرافيك بـ [HyperFrames](https://hyperframes.heygen.com)
(HTML + GSAP → MP4، تصيير حتمي إطاراً بإطار).

## المتطلبات

| الأداة | الإصدار المُتحقَّق منه |
| --- | --- |
| Node.js | 22+ (تم التحقق على v22.23.4) |
| FFmpeg / ffprobe | تم التحقق على 6.1.1 |
| Chrome / Chromium | يكتشفه HyperFrames تلقائياً (`hf.sh browser ensure` إن لم يوجد) |
| HyperFrames CLI | مثبّت على `0.9.9` |

تحقق من البيئة: `scripts/check-env.sh`

## إضافة Claude Code

الإضافة الرسمية `hyperframes@hyperframes` مُعلنة في `.claude/settings.json` (نطاق المشروع)،
لذلك أي جلسة Claude Code تفتح هذا المستودع ستعرض تثبيتها وتحمّل مهارات
`/hyperframes:hyperframes` و`hyperframes-cli` و`hyperframes-registry` و`media-use` وغيرها.

## البنية

```
.claude/settings.json        إضافة HyperFrames الرسمية (marketplace: heygen-com/hyperframes)
scripts/
  hf.sh                      يشغّل CLI المثبّت (مُشغّل الإضافة إن وُجد، وإلا npx hyperframes@0.9.9)
  check-env.sh               فحص Node 22+ وFFmpeg و`hyperframes doctor`
  new-project.sh <name> [template]   مشروع جديد داخل projects/
  render.sh <name> [draft|looks|delivery]   lint + check + render + تحقق ffprobe
templates/
  title-card-5s/             بطاقة عنوان 5 ثوانٍ قابلة لإعادة الاستخدام (متغيرات: tagline, accent)
projects/
  <name>/
    index.html               التكوين الجذر (المدة، المقاس، تركيب المشاهد)
    compositions/*.html      مشهد واحد لكل ملف داخل <template>
    assets/fonts, assets/media
    renders/                 مخرجات MP4 (مُتجاهلة في git افتراضياً)
    hyperframes.json, package.json (يثبّت hyperframes@0.9.9), CLAUDE.md
```

## سير العمل

```bash
scripts/new-project.sh eid-promo title-card-5s   # أو بدون قالب لمشروع فارغ
# حرّر projects/eid-promo/index.html و compositions/
scripts/hf.sh snapshot --at 1,3     # (من داخل مجلد المشروع) صور PNG للمراجعة
scripts/hf.sh preview --background  # معاينة Studio في المتصفح
scripts/render.sh eid-promo draft       # تكرار سريع
scripts/render.sh eid-promo delivery    # النسخة النهائية
```

`render.sh` لا يطبع ✓ إلا بعد أن يقرأ ffprobe الملف ويطابق مدته `data-duration` للتكوين الجذر.

## قواعد أساسية (من مهارة HyperFrames)

- كل عنصر مؤقّت: `class="clip"` و`data-start` و`data-duration` بالثواني.
- كل تكوين يسجّل خطاً زمنياً متوقفاً: `window.__timelines["<id>"] = gsap.timeline({ paused: true })`.
- لا `Date.now()` ولا `Math.random()` غير مبذور ولا مؤقتات ولا `repeat: -1`.
- الخطوط غير المضمّنة تحتاج `@font-face` لملف في `assets/fonts/` — **مهم للعربية**: الخطوط
  المضمّنة لاتينية فقط، لذا أضف خطاً عربياً (مثل Cairo أو Tajawal بصيغة woff2) قبل كتابة نص عربي.

## مشروع الاختبار

`projects/ammar-creative-studio-test` — بطاقة عنوان **AMMAR CREATIVE STUDIO**، 5 ثوانٍ،
1920×1080، 30fps، H.264. الملف المُصيَّر محفوظ في
`projects/ammar-creative-studio-test/renders/ammar-creative-studio-test.mp4`.
