#!/usr/bin/env python3
"""Builds showcase/phase-1/index.html (RTL comparison page) from the phase-1 SVGs.
SVGs are inlined so the page is a faithful vector preview. Run after phase1_logo.py."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, "brand", "logo", "archive", "phase-1-proposals")
OUT = os.path.join(ROOT, "showcase", "phase-1", "index.html")


def svg(name, cls=""):
    s = open(os.path.join(LOGO, name), encoding="utf-8").read()
    s = re.sub(r'\s(width|height)="\d+"', "", s, count=2)
    return s.replace("<svg ", f'<svg class="{cls}" role="img" ', 1)


meta = json.load(open(os.path.join(LOGO, "proposals-meta.json"), encoding="utf-8"))

NOTES = {
    "A": dict(
        idea="أقرب المقترحات إلى المرجع. القوس طويل بنسبة قريبة من الأصل، بشريطين ذهبيين بينهما خط داكن، وعتبة شبه منحرفة أسفله، والنجمة الثمانية في تاج القوس، والاسم في الجزء السفلي من الفتحة.",
        pros=["أعلى درجة استمرارية مع الهوية الحالية.", "النجمة تحتفظ بمكانها داخل الباب.", "العتبة الأصلية باقية كما هي."],
        cons=["أصغر حجم للكلمة بين المقترحات الثلاثة، فتكون أضعفها في صورة الحساب الصغيرة.", "طول القوس يترك فراغاً بين النجمة والكلمة."],
    ),
    "B": dict(
        idea="قوس أعرض يتحول إلى محراب يحتضن الاسم. النجمة انتقلت إلى حجر التاج في قمة القوس، مقطوعة من الشريطين الذهبيين، فتحررت الفتحة كلها للكلمة.",
        pros=["أكبر حضور للكلمة: عرضها نصف قطر الدائرة تقريباً، مثل الأصل تماماً.", "الشريط المزدوج والعتبة باقيان.", "شكل المحراب ينسجم مع بطاقة الحديث المعتمدة «المحراب المعرفي»."],
        cons=["النجمة أصغر، وتتحول إلى نقطة عند 48 بكسل.", "تغيير موضع النجمة يحتاج موافقتك."],
    ),
    "C": dict(
        idea="بوابة مغلقة: شريط ذهبي واحد سميك يلتف من القوس إلى قاعدة متصلة، ودائرة سميكة مع خط داخلي رفيع، بلا نقاط ولا زخرفة خلفية.",
        pros=["الأوضح في الأحجام الصغيرة والعلامة المائية.", "الأسهل في التحريك: مسار واحد يُرسم ثم يُغلق.", "أقل تفاصيل قابلة للضياع."],
        cons=["يفقد الشريط المزدوج، وهو من سمات القوس الأصلي.", "الإطار المغلق أبرد وأقرب إلى اللوحة منه إلى الباب."],
    ),
}

cards = []
for k in "ABC":
    m, n = meta[k], NOTES[k]
    rec = ' <span class="rec">ترشيحي</span>' if k == "B" else ""
    cards.append(f'''
    <article class="prop" id="prop-{k}">
      <div class="prop-art">{svg(f"khaybar-proposal-{k}.svg", "mark")}</div>
      <div class="prop-body">
        <p class="eyebrow">المقترح {k} · <span lang="en">{m["name_en"]}</span></p>
        <h3>{m["name_ar"]}{rec}</h3>
        <p>{n["idea"]}</p>
        <dl class="specs">
          <div><dt>عرض القوس الخارجي</dt><dd>{m["arch_outer_width"]}</dd></div>
          <div><dt>عرض الفتحة</dt><dd>{m["opening_width"]}</dd></div>
          <div><dt>سماكة الشريط</dt><dd>{m["band_px"]}</dd></div>
          <div><dt>سماكة حرف الكلمة</dt><dd>{m["word_stroke_px"]}</dd></div>
        </dl>
        <p class="unit">الوحدات من لوحة 1000×1000.</p>
        <div class="pc">
          <div><h4>نقاط القوة</h4><ul>{"".join(f"<li>{x}</li>" for x in n["pros"])}</ul></div>
          <div><h4>نقاط الضعف</h4><ul>{"".join(f"<li>{x}</li>" for x in n["cons"])}</ul></div>
        </div>
        <p class="files" lang="en" dir="ltr">brand/logo/phase-1/khaybar-proposal-{k}.svg · -small.svg</p>
      </div>
    </article>''')

sizes = (48, 64, 128, 256)
rows = [f'''<div class="srow"><div class="slabel">الأصل</div>{"".join(f'<figure><img class="disc" src="assets/original-mark.jpg" width="{s}" height="{s}" alt="الشعار الأصلي بحجم {s}"><figcaption>{s}</figcaption></figure>' for s in sizes)}</div>''']
for k in "ABC":
    small = svg(f"khaybar-proposal-{k}-small.svg", "disc")
    rows.append(f'''<div class="srow"><div class="slabel">{k} · {meta[k]["name_ar"]}</div>{"".join(f'<figure><div class="discbox" style="width:{s}px;height:{s}px">{small}</div><figcaption>{s}</figcaption></figure>' for s in sizes)}</div>''')

html = f'''<title>خيبر · المرحلة الأولى</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Noto+Kufi+Arabic:wght@500;700&display=swap">
<style>
/* Layout: a single dark review board; reference first, then three proposal plates, then the size test and the decision. */
:root {{
  --bg: #071F26; --surface: #153840; --surface-2: #0d2a32; --line: #24505a;
  --gold: #D4AA61; --ivory: #F4E9D3; --muted: #a9b9b6; --turq: #2DB9B6;
  --display: "Noto Kufi Arabic", "IBM Plex Sans Arabic", system-ui, sans-serif;
  --body: "IBM Plex Sans Arabic", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, monospace;
  color-scheme: dark;
}}
* {{ box-sizing: border-box }}
body {{ background: var(--bg); color: var(--ivory); font: 16px/1.75 var(--body); }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding-block: 40px 80px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }}
h1, h2, h3 {{ font-family: var(--display); line-height: 1.35; text-wrap: balance; margin: 0 }}
h1 {{ font-size: clamp(28px, 5vw, 44px); color: var(--gold) }}
h2 {{ font-size: clamp(21px, 3vw, 28px); color: var(--ivory) }}
h3 {{ font-size: 23px; color: var(--gold) }}
h4 {{ margin: 0 0 4px; font-size: 14px; color: var(--muted); font-weight: 600 }}
p {{ margin: 0; max-width: 68ch }}
.eyebrow {{ font-size: 13px; color: var(--turq); letter-spacing: .02em }}
[lang="en"] {{ font-family: var(--mono); font-size: .92em }}
header {{ display: grid; gap: 12px; padding-bottom: 28px; border-bottom: 1px solid var(--line) }}
.status {{ display: inline-flex; gap: 8px; align-items: center; width: fit-content; font-size: 14px;
  padding: 4px 12px; border: 1px solid var(--gold); color: var(--gold); border-radius: 999px }}
.status::before {{ content: ""; width: 8px; height: 8px; background: var(--gold); transform: rotate(45deg) }}
section {{ display: grid; gap: 20px; padding-block: 44px; border-bottom: 1px solid var(--line) }}
.lead {{ color: var(--muted) }}
.strip {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 6px }}
.strip img {{ display: block; max-width: none; height: 260px; width: auto }}
.ref-grid {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr); gap: 28px; align-items: start }}
.ref-grid img {{ border-radius: 6px; border: 1px solid var(--line); width: 100% }}
table {{ border-collapse: collapse; width: 100%; font-size: 14.5px }}
.tbl {{ overflow-x: auto; min-width: 0 }}
th, td {{ text-align: right; padding: 9px 10px; border-bottom: 1px solid var(--line); vertical-align: top }}
th {{ color: var(--gold); font-weight: 600; white-space: nowrap }}
td.num {{ font-family: var(--mono); font-variant-numeric: tabular-nums; direction: ltr; text-align: left; white-space: nowrap; color: var(--ivory) }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px }}
.two > div {{ min-width: 0 }}
ul {{ margin: 0; padding-inline-start: 20px }}
li {{ margin-block: 4px }}
li::marker {{ color: var(--gold) }}
.key {{ background: var(--surface-2); border-inline-start: 3px solid var(--turq); padding: 14px 18px; border-radius: 4px }}
.swatches {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px }}
.sw {{ display: grid; grid-template-columns: 34px 1fr; gap: 10px; align-items: center; font-size: 13.5px }}
.sw i {{ width: 34px; height: 34px; border-radius: 50%; border: 1px solid var(--line) }}
.sw b {{ display: block; font-weight: 500 }}
.sw span {{ font-family: var(--mono); color: var(--muted); direction: ltr; display: block; text-align: right }}
.word-cmp {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px }}
.word-cmp figure {{ margin: 0; display: grid; gap: 8px; min-width: 0 }}
.word-cmp img, .word-cmp svg {{ width: 100%; height: auto; display: block; border-radius: 6px; border: 1px solid var(--line) }}
figcaption {{ font-size: 13px; color: var(--muted) }}
.toolbar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center }}
.seg {{ display: inline-flex; border: 1px solid var(--line); border-radius: 999px; overflow: hidden }}
.seg button {{ font: inherit; font-size: 14px; color: var(--muted); background: none; border: 0; padding: 6px 14px; cursor: pointer }}
.seg button[aria-pressed="true"] {{ background: var(--gold); color: var(--bg) }}
.seg button:focus-visible {{ outline: 2px solid var(--turq); outline-offset: -2px }}
.props {{ display: grid; gap: 28px }}
.prop {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 32px; align-items: center;
  padding: 24px; background: var(--surface-2); border: 1px solid var(--line); border-radius: 8px }}
.prop-art svg {{ width: 100%; height: auto; display: block; border-radius: 50% }}
.prop-body {{ display: grid; gap: 14px; min-width: 0 }}
.rec {{ font-family: var(--body); font-size: 13px; font-weight: 600; color: var(--bg); background: var(--turq); padding: 2px 10px; border-radius: 999px; vertical-align: middle; margin-inline-start: 6px }}
.specs {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 0 }}
.specs div {{ border: 1px solid var(--line); border-radius: 4px; padding: 8px }}
.specs dt {{ font-size: 12px; color: var(--muted) }}
.specs dd {{ margin: 0; font-family: var(--mono); font-size: 18px; color: var(--gold); font-variant-numeric: tabular-nums }}
.unit {{ font-size: 12.5px; color: var(--muted); margin-top: -6px }}
.pc {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 14.5px }}
.files {{ font-family: var(--mono); font-size: 12px; color: var(--muted); direction: ltr; text-align: right }}
body.gold-word .wm {{ fill: var(--gold) }}
.sizes {{ display: grid; gap: 18px; overflow-x: auto }}
.bgswitch {{ padding: 20px; border-radius: 8px; background: #F4E9D3; transition: background .2s }}
.bgswitch.dark {{ background: #0b0f10 }}
.bgswitch.mid {{ background: #6f7f7c }}
.srow {{ display: flex; align-items: end; gap: 22px; min-width: max-content }}
.slabel {{ width: 150px; font-size: 14px; color: #1d2a2c; align-self: center }}
.bgswitch.dark .slabel, .bgswitch.mid .slabel {{ color: #e9efee }}
.srow figure {{ margin: 0; display: grid; justify-items: center; gap: 4px }}
.srow figcaption {{ font-family: var(--mono); font-size: 11px; color: inherit; opacity: .7 }}
.bgswitch figcaption {{ color: #1d2a2c }}
.bgswitch.dark figcaption, .bgswitch.mid figcaption {{ color: #e9efee }}
.disc, .discbox svg {{ border-radius: 50%; display: block }}
.discbox svg {{ width: 100%; height: 100% }}
.decide ol {{ margin: 0; padding-inline-start: 22px; display: grid; gap: 10px }}
.decide li::marker {{ color: var(--gold); font-family: var(--mono) }}
@media (max-width: 860px) {{
  .ref-grid, .prop, .two, .pc {{ grid-template-columns: 1fr }}
  .specs {{ grid-template-columns: repeat(2, minmax(0, 1fr)) }}
  .prop {{ padding: 16px; gap: 20px }}
  .word-cmp {{ grid-template-columns: 1fr }}
}}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important }} }}
</style>

<div class="wrap" dir="rtl" lang="ar">
<header>
  <p class="eyebrow">خَيبر | <span lang="en">KHAYBAR</span> · <span lang="en" dir="ltr">@bab.5aybar</span></p>
  <h1>المرحلة الأولى: تحليل المرجع وإعادة هندسة الشعار</h1>
  <p class="lead">ثلاثة مقترحات متجهة حقيقية، كلها بالقوس الأصلي المطوّر والدائرة الذهبية الكاملة والاسم داخل القوس، وبالألوان المعتمدة. النسخة هنا هي «الذهبي الرسمي المسطّح»، والنسخة المعدنية مؤجلة إلى المرحلة الثالثة.</p>
  <span class="status">بانتظار اختيارك</span>
</header>

<section aria-labelledby="s-ref">
  <p class="eyebrow">المرجع الأصلي · <span lang="en" dir="ltr">references/khaybar-original.mp4</span></p>
  <h2 id="s-ref">ما يقوله الفيديو الأصلي</h2>
  <p class="lead">الملف 1080×1920، مدته 5.1 ثانية، 30 إطاراً في الثانية، بلا صوت. الشريط التالي لقطات كل نصف ثانية، تبدأ من اليمين.</p>
  <div class="strip"><img src="assets/original-motion-strip.jpg" alt="لقطات متتابعة من فيديو الهوية الأصلية كل نصف ثانية" width="2700" height="480"></div>
  <div class="two">
    <div>
      <h4>تسلسل الحركة الحالية</h4>
      <ul>
        <li><b>0.0–0.5ث</b> شرارة ذهبية ترسم الدائرة.</li>
        <li><b>0.5–1.0ث</b> القوس ينمو من العتبة: التاج نصف الدائري ثم الساقان.</li>
        <li><b>1.0–1.5ث</b> النجمة الثمانية تظهر بتوهج داخل الباب.</li>
        <li><b>1.5–2.5ث</b> كلمة «خيبر» تُكتب من اليمين إلى اليسار، ثم الماسات.</li>
        <li><b>2.5–3.0ث</b> <span lang="en">KHAYBAR</span> ثم سطر المنصات واسم الحساب.</li>
        <li><b>3.0–5.1ث</b> ثبات مع لمعان نقاط الدائرة.</li>
      </ul>
    </div>
    <div class="key">
      <h4>اكتشاف أساسي</h4>
      <p>الماسات الفيروزية الثلاث ليست زخرفة منفصلة، بل هي <b>نقاط الحروف</b>: نقطتا الياء ونقطة الباء. نقطة الخاء ماسة عاجية فوق الكلمة. لذلك حافظت المقترحات الثلاثة على الماسات في موضعها الإملائي تحت الكلمة، ولم تنقلها إلى مكان آخر.</p>
    </div>
  </div>

  <div class="ref-grid">
    <figure style="margin:0;display:grid;gap:8px">
      <img src="assets/original-mark.jpg" alt="الشعار الأصلي في الإطار الأخير" width="800" height="800">
      <figcaption>الإطار عند 4.5ث، مقصوصاً على الدائرة.</figcaption>
    </figure>
    <div class="tbl">
      <table>
        <caption class="eyebrow" style="text-align:right;padding-bottom:6px">القياسات بالبكسل داخل إطار 1080×1920</caption>
        <tr><th>العنصر</th><th>القياس</th><th>الملاحظة</th></tr>
        <tr><td>الدائرة</td><td class="num">r 486 · stroke ≈3</td><td>مركزها (540، 892). خط رفيع جداً (0.3% من القطر) يختفي عند 48 بكسل.</td></tr>
        <tr><td>حلقات داخلية</td><td class="num">r 463 dots · r 445</td><td>نقاط متلألئة وخط شعري، غير مقروءة في الأحجام الصغيرة.</td></tr>
        <tr><td>القوس</td><td class="num">272 × 287</td><td>تاج نصف دائري تام (R=136)، ساقان مستقيمتان. النسبة ارتفاع/عرض ≈1.05.</td></tr>
        <tr><td>الشريطان</td><td class="num">24 + 3 + 25</td><td>شريطان ذهبيان بينهما خط داكن 3 بكسل. الفتحة 168.</td></tr>
        <tr><td>العتبة</td><td class="num">350→431 × 22</td><td>شبه منحرف أعرض من القوس بنسبة 1.6، تفصله فجوة 8 بكسل.</td></tr>
        <tr><td>النجمة</td><td class="num">≈92 / 46</td><td>نجمة ثمانية عاجية بقلب داكن، وتحتها ماسة فيروزية صغيرة (22).</td></tr>
        <tr><td>الكلمة</td><td class="num">500 × 250</td><td>كوفي هندسي، سماكة الحرف 35، كل المائلات بزاوية 45° تماماً.</td></tr>
        <tr><td>الماسات</td><td class="num">50 · pitch 64</td><td>نقاط الياء والباء. نقطة الخاء عاجية (34).</td></tr>
        <tr><td><span lang="en">KHAYBAR</span></td><td class="num">cap ≈12</td><td>مقروءة فقط فوق 256 بكسل.</td></tr>
      </table>
    </div>
  </div>

  <div class="two">
    <div>
      <h4>مواطن القوة</h4>
      <ul>
        <li>كلمة «خيبر» الكوفية مميزة فعلاً، بنظام صارم: سماكة واحدة وزاوية واحدة (45°).</li>
        <li>استخدام الماسات نقاطاً للحروف فكرة ذكية تربط الرمز بالكتابة.</li>
        <li>القوس نصف الدائري بسيط ومقروء ويحمل دلالة الباب.</li>
        <li>لوحة الألوان متماسكة.</li>
      </ul>
    </div>
    <div>
      <h4>مواطن الضعف</h4>
      <ul>
        <li>الشعار من طابقين منفصلين (القوس فوق، الكلمة تحت)، فيصبح طويلاً ويصغر كلاهما داخل الدائرة.</li>
        <li>الدائرة رفيعة جداً، والنقاط والخط الشعري واسم <span lang="en">KHAYBAR</span> تختفي في صورة الحساب.</li>
        <li>الماسة الصغيرة تحت النجمة تنافس الماسات الثلاث وتكرر عنصرها.</li>
        <li>الألوان أكثر تشبعاً من اللوحة المعتمدة، وفيها تدرجات وتوهج قوي.</li>
      </ul>
    </div>
  </div>
</section>

<section aria-labelledby="s-word">
  <p class="eyebrow">ثابت في المقترحات الثلاثة</p>
  <h2 id="s-word">الكلمة: إعادة بناء متجهة للأصل (R0)</h2>
  <p class="lead">أعدت رسم «خيبر» من القياسات مساراً متجهاً نظيفاً: سماكة 10 وحدات، وكل المائلات 45°، والنقاط في مواضعها. استخدمت النسخة نفسها في المقترحات الثلاثة حتى تكون المقارنة على هندسة القوس والتكوين فقط. تحسين الكلمة وتطويرها إلى توقيع نهائي هو عمل المرحلة الثانية.</p>
  <div class="word-cmp">
    <figure><img src="assets/original-word.jpg" alt="كلمة خيبر في الفيديو الأصلي" width="560" height="300"><figcaption>الأصل: لقطة من الفيديو.</figcaption></figure>
    <figure>{svg("wordmark-R0-reconstruction.svg")}<figcaption>R0: مسار متجه، بلا خط جاهز ولا صورة نقطية.</figcaption></figure>
  </div>
  <div class="swatches" aria-label="الألوان المعتمدة المستخدمة">
    <div class="sw"><i style="background:#071F26"></i><div><b>الخلفية الأساسية</b><span>#071F26</span></div></div>
    <div class="sw"><i style="background:#D4AA61"></i><div><b>الذهبي التراثي</b><span>#D4AA61 · 7.9:1</span></div></div>
    <div class="sw"><i style="background:#F4E9D3"></i><div><b>العاجي</b><span>#F4E9D3 · 14.2:1</span></div></div>
    <div class="sw"><i style="background:#2DB9B6"></i><div><b>فيروزي البصيرة</b><span>#2DB9B6 · 7.1:1</span></div></div>
    <div class="sw"><i style="background:#153840"></i><div><b>السطح الثانوي</b><span>#153840</span></div></div>
  </div>
  <p class="unit">النسب هي التباين مقابل الخلفية الأساسية. الثلاثة تتجاوز 7:1.</p>
</section>

<section aria-labelledby="s-props">
  <p class="eyebrow">ثلاثة مقترحات هندسية</p>
  <h2 id="s-props">القوس والاسم داخله</h2>
  <div class="toolbar">
    <span class="lead" style="font-size:14px">لون الكلمة للمعاينة:</span>
    <div class="seg" role="group" aria-label="لون الكلمة">
      <button type="button" id="wm-ivory" aria-pressed="true">عاجي (كالأصل)</button>
      <button type="button" id="wm-gold" aria-pressed="false">ذهبي</button>
    </div>
  </div>
  <div class="props">{"".join(cards)}</div>
</section>

<section aria-labelledby="s-sizes">
  <p class="eyebrow">اختبار الأحجام الصغيرة · قص دائري</p>
  <h2 id="s-sizes">48 و64 و128 و256 بكسل</h2>
  <p class="lead">هذه نسخ الأحجام الصغيرة من كل مقترح: تُحذف النقاط والزخرفة الخلفية، وتُحذف نجمة التاج في A وC، وتكبر الكلمة لتملأ الفتحة. الأصل معروض للمقارنة من الفيديو نفسه.</p>
  <div class="toolbar">
    <span class="lead" style="font-size:14px">خلفية الاختبار:</span>
    <div class="seg" role="group" aria-label="خلفية الاختبار">
      <button type="button" data-bg="" aria-pressed="true">فاتحة</button>
      <button type="button" data-bg="mid" aria-pressed="false">رمادية</button>
      <button type="button" data-bg="dark" aria-pressed="false">داكنة</button>
    </div>
  </div>
  <div class="bgswitch" id="bgswitch"><div class="sizes">{"".join(rows)}</div></div>
  <div class="two">
    <div>
      <h4>النتيجة</h4>
      <ul>
        <li>وضع الاسم داخل القوس يجعل الكلمة أصغر من الأصل عند 48 بكسل في A. في B يعادل عرض الكلمة نصف قطر الدائرة، مثل الأصل.</li>
        <li>C الأوضح في الإطار والدائرة، وB الأوضح في الكلمة.</li>
        <li>الماسات الفيروزية تبقى مرئية في الثلاثة حتى 64 بكسل، وعند 48 تصبح خطاً منقطاً.</li>
      </ul>
    </div>
    <div>
      <h4>ما سيُعالج لاحقاً</h4>
      <ul>
        <li>صورة الحساب النهائية (المرحلة 4) ستكبّر التكوين داخل الدائرة على نموذج «الحضور الواضح».</li>
        <li>سماكة الكلمة ونقطة الخاء تُضبطان للأحجام الصغيرة في المرحلة 2.</li>
      </ul>
    </div>
  </div>
</section>

<section aria-labelledby="s-decide" class="decide" style="border-bottom:0">
  <p class="eyebrow">المطلوب منك</p>
  <h2 id="s-decide">قرار الاعتماد</h2>
  <ol>
    <li>اختر مقترحاً: A أو B أو C. يمكنك أيضاً طلب تعديل محدد عليه، مثل B بقاعدة C.</li>
    <li>النجمة الثمانية: في تاج القوس (A وC)، أم حجر تاج في القمة (B)، أم تُحذف؟ لم تكن ضمن العناصر الإلزامية في الوثيقة، لذا القرار لك.</li>
    <li>الماسة الفيروزية الصغيرة تحت النجمة حذفتها في الثلاثة لأنها تكرر الماسات. هل توافق؟</li>
    <li>لون الكلمة: عاجي كالأصل، أم ذهبي؟ جرّب المفتاح أعلى المقترحات.</li>
  </ol>
  <p class="lead">ترشيحي B: يعطي الكلمة أكبر حضور ممكن داخل القوس، ويبقي النجمة والشريط المزدوج والعتبة، ويتسق مع بطاقة الحديث «المحراب المعرفي».</p>
</section>
</div>

<script>
(() => {{
  const ivory = document.getElementById('wm-ivory'), gold = document.getElementById('wm-gold');
  function setWord(isGold) {{
    document.body.classList.toggle('gold-word', isGold);
    ivory.setAttribute('aria-pressed', String(!isGold));
    gold.setAttribute('aria-pressed', String(isGold));
  }}
  ivory.addEventListener('click', () => setWord(false));
  gold.addEventListener('click', () => setWord(true));
  const box = document.getElementById('bgswitch');
  document.querySelectorAll('[data-bg]').forEach(b => b.addEventListener('click', () => {{
    box.className = 'bgswitch ' + b.dataset.bg;
    document.querySelectorAll('[data-bg]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  }}));
}})();
</script>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", OUT, len(html) // 1024, "KB")
