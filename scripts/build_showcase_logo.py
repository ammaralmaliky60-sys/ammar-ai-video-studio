#!/usr/bin/env python3
"""Builds showcase/logo/index.html — the final logo review page (RTL, mobile-ready).
Run after build_logo.py, qa_logo.py and export_logo.js."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_logo as BL  # noqa: E402

ROOT = BL.ROOT
LOGO = os.path.join(ROOT, "brand", "logo")
OUT = os.path.join(ROOT, "showcase", "logo", "index.html")
QA = json.load(open(os.path.join(ROOT, "docs", "logo-qa-report.json"), encoding="utf-8"))


def svg(rel, cls=""):
    s = open(os.path.join(LOGO, rel), encoding="utf-8").read()
    s = re.sub(r'\s(width|height)="\d+"', "", s, count=2)
    s = re.sub(r"<title>.*?</title>", "", s)
    return s.replace("<svg ", f'<svg class="{cls}" aria-hidden="true" ', 1)


def construction_svg():
    """Wordmark drawn on its grid: stroke unit, 45° axes, shared alignment lines, counters."""
    w = BL.wordmark()
    gr = w["grid"]
    s, pad = 6.0, 16.0
    minx, miny, maxx, maxy = BL.bounds([w["body"], w["kha_dot"], *w["turq"]])
    LBL = 330.0  # label column on the left
    W, H = (maxx - minx + 2 * pad) * s + LBL, (maxy - miny + 2 * pad) * s

    def tx(x, y):
        return (x - minx + pad) * s + LBL, (y - miny + pad) * s

    lines = []
    for y, lab in [(0, "خط القاعدة"), (-10, ""), (BL.TOOTH_TOP, "أسنان = أسفل الخاء"), (BL.KHA_TOP, "أعلى الخاء"), (BL.DESC, "ذيل الراء = أسفل الماسات")]:
        _, Y = tx(0, y)
        lines.append(f'<line x1="0" x2="{W:.0f}" y1="{Y:.1f}" y2="{Y:.1f}" class="g"/>')
        if lab:
            lines.append(f'<text x="14" y="{Y-7:.1f}" class="gl" direction="ltr" text-anchor="start">{lab}</text>')
    for x in (gr["xr"], gr["t1"], gr["t1"] + 10, gr["t2"], gr["t2"] + 10, gr["kj"]):
        X, _ = tx(x, 0)
        lines.append(f'<line y1="0" y2="{H:.0f}" x1="{X:.1f}" x2="{X:.1f}" class="g"/>')
    # counters
    for a, b in [(gr["xr"], gr["t1"]), (gr["t1"] + 10, gr["t2"]), (gr["t2"] + 10, gr["kj"])]:
        X1, Y = tx(a, -19)
        X2, _ = tx(b, -19)
        lines.append(f'<line x1="{X1:.1f}" x2="{X2:.1f}" y1="{Y:.1f}" y2="{Y:.1f}" class="m"/>'
                     f'<text x="{(X1+X2)/2:.1f}" y="{Y-8:.1f}" class="ml" direction="ltr" text-anchor="middle">18</text>')
    # 45° axes through the ra tail and the kha diagonal
    for c in (gr["xr"] - 10, gr["kj"] - 10):
        x1, y1 = tx(c - BL.DESC - 6, BL.DESC + 6)
        x2, y2 = tx(c + 48, -48)
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="d"/>')
    X, Y = tx(gr["kj"] + 22, -4)
    lines.append(f'<text x="{X:.1f}" y="{Y:.1f}" class="ml" direction="ltr">45°</text>')
    body = (f'<path fill="#F4E9D3" opacity=".92" d="{BL.poly_d(w["body"], tx)}"/>'
            f'<path fill="#F4E9D3" opacity=".92" d="{BL.poly_d(w["kha_dot"], tx)}"/>'
            f'<g fill="#2DB9B6">' + "".join(f'<path d="{BL.poly_d(t, tx)}"/>' for t in w["turq"]) + "</g>")
    return (f'<svg class="construct" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="بناء كلمة خيبر على الشبكة">'
            f'<rect width="100%" height="100%" fill="#071F26"/>{body}{"".join(lines)}</svg>')


def small_row(label, maker, sizes):
    cells = "".join(f'<figure><div class="disc" style="width:{s}px;height:{s}px">{maker(s)}</div><figcaption>{s}</figcaption></figure>' for s in sizes)
    return f'<div class="srow"><div class="slabel">{label}</div>{cells}</div>'


orig = lambda s: f'<img src="assets/original-mark.jpg" width="{s}" height="{s}" alt="">'  # noqa: E731
small_svg = svg("small/khaybar-logo-small.svg")
avatar_svg = svg("avatar/khaybar-avatar.svg")
flat_svg = svg("official/khaybar-logo-flat.svg")
rows_small = "".join([
    small_row("الأصل", orig, (32, 48, 64, 128)),
    small_row("النسخة المبسطة", lambda s: small_svg, (32, 48, 64, 128)),
    small_row("الرسمي الكامل", lambda s: flat_svg, (32, 48, 64, 128)),
])
rows_avatar = "".join([
    small_row("الأصل", orig, (40, 56, 77, 110, 150)),
    small_row("صورة الحساب", lambda s: avatar_svg, (40, 56, 77, 110, 150)),
])

g = json.load(open(os.path.join(LOGO, "logo-geometry.json")))
mf = g["official/khaybar-logo-flat.svg"]
qa_ok = not QA["failures"]

html = f'''<title>شعار خيبر النهائي</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Arabic:wght@400;500;600&family=Noto+Kufi+Arabic:wght@500;700&display=swap">
<style>
/* Layout: one dark brand board. Hero pair (flat / cinematic), then construction, versions, applications, sizes, notes. */
:root {{
  --bg: #071F26; --surface: #153840; --surface-2: #0c2a32; --line: #24505a;
  --gold: #D4AA61; --ivory: #F4E9D3; --muted: #a9bab7; --turq: #2DB9B6;
  --display: "Noto Kufi Arabic", "IBM Plex Sans Arabic", system-ui, sans-serif;
  --body: "IBM Plex Sans Arabic", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, monospace;
  color-scheme: dark;
}}
* {{ box-sizing: border-box }}
body {{ background: var(--bg); color: var(--ivory); font: 16px/1.75 var(--body) }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding-block: 36px 80px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)) }}
h1, h2 {{ font-family: var(--display); line-height: 1.35; text-wrap: balance; margin: 0 }}
h1 {{ font-size: clamp(28px, 5vw, 42px); color: var(--gold) }}
h2 {{ font-size: clamp(21px, 3vw, 27px) }}
h3 {{ margin: 0; font-size: 15px; color: var(--gold); font-weight: 600 }}
p {{ margin: 0; max-width: 68ch }}
.eyebrow {{ font-size: 13px; color: var(--turq); letter-spacing: .02em }}
.lead {{ color: var(--muted) }}
[lang="en"] {{ font-family: var(--mono); font-size: .92em }}
header {{ display: grid; gap: 12px; padding-bottom: 28px; border-bottom: 1px solid var(--line) }}
.status {{ display: inline-flex; gap: 8px; align-items: center; width: fit-content; font-size: 14px;
  padding: 4px 12px; border: 1px solid var(--gold); color: var(--gold); border-radius: 999px }}
.status::before {{ content: ""; width: 8px; height: 8px; background: var(--gold); transform: rotate(45deg) }}
section {{ display: grid; gap: 22px; padding-block: 44px; border-bottom: 1px solid var(--line) }}
.hero {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px }}
figure {{ margin: 0 }}
.plate {{ display: grid; gap: 10px; min-width: 0 }}
.plate svg, .plate img {{ width: 100%; height: auto; display: block }}
.plate .art {{ background: var(--surface-2); border: 1px solid var(--line); border-radius: 8px; padding: clamp(12px, 3vw, 28px) }}
figcaption {{ font-size: 13.5px; color: var(--muted) }}
figcaption b {{ color: var(--ivory); font-weight: 600 }}
.before-after {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 18px; align-items: center }}
.before-after .arrow {{ color: var(--gold); font-size: 28px }}
.construct {{ width: 100%; height: auto; display: block; border-radius: 8px; border: 1px solid var(--line) }}
.construct .g {{ stroke: #2DB9B6; stroke-opacity: .35; stroke-width: 2; stroke-dasharray: 6 6 }}
.construct .d {{ stroke: #D4AA61; stroke-opacity: .7; stroke-width: 2.5; stroke-dasharray: 10 8 }}
.construct .m {{ stroke: #D4AA61; stroke-width: 3 }}
.construct .gl {{ fill: #7fcfcc; font: 500 22px var(--body) }}
.construct .ml {{ fill: #D4AA61; font: 500 24px var(--mono) }}
ul {{ margin: 0; padding-inline-start: 20px }}
li {{ margin-block: 5px }}
li::marker {{ color: var(--gold) }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 28px }}
.two > * {{ min-width: 0 }}
.versions {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px }}
.versions .art {{ aspect-ratio: 1; display: grid; place-items: center; padding: 18px }}
.versions .art svg {{ max-height: 100% }}
.art.on-ivory {{ background: #F4E9D3 }}
.art.on-surface {{ background: var(--surface) }}
.art.wide {{ aspect-ratio: auto }}
.wide-row {{ display: grid; grid-template-columns: 1.6fr 1fr; gap: 18px }}
.wide-row > * {{ min-width: 0 }}
.apps {{ display: grid; grid-template-columns: 0.8fr 1fr 1.2fr; gap: 18px; align-items: start }}
.apps > * {{ min-width: 0 }}
.phone {{ aspect-ratio: 9 / 16; border-radius: 18px; border: 1px solid var(--line); overflow: hidden; position: relative;
  background: radial-gradient(120% 70% at 50% 40%, #12343c 0%, #071F26 70%); display: grid; place-items: center; align-content: center; gap: 4%; padding: 10% }}
.phone svg {{ width: 78%; height: auto }}
.phone .tag {{ font-family: var(--display); color: var(--ivory); font-size: clamp(12px, 1.7vw, 17px); text-align: center }}
.phone .handle {{ font-family: var(--mono); color: var(--gold); font-size: clamp(10px, 1.3vw, 13px); direction: ltr }}
.profile {{ border: 1px solid var(--line); border-radius: 14px; padding: 18px; display: grid; gap: 14px; background: var(--surface-2) }}
.profile .top {{ display: flex; gap: 16px; align-items: center }}
.profile .av {{ width: 86px; height: 86px; border-radius: 50%; overflow: hidden; flex: none; outline: 2px solid #2a3d41 }}
.profile .av svg {{ width: 100%; height: 100% }}
.profile .name {{ font-weight: 600 }}
.profile .handle {{ font-family: var(--mono); color: var(--muted); direction: ltr; text-align: right; font-size: 13.5px }}
.grid9 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px }}
.grid9 span {{ aspect-ratio: 3 / 4; background: linear-gradient(160deg, #1b434c, #0a252c) }}
.grid9 span:first-child {{ background: #071F26; display: grid; place-items: center }}
.grid9 span:first-child svg {{ width: 70% }}
.scene {{ position: relative; aspect-ratio: 16 / 10; border-radius: 10px; overflow: hidden; border: 1px solid var(--line);
  background:
    linear-gradient(180deg, rgba(7,31,38,.15), rgba(7,31,38,.75)),
    radial-gradient(60% 80% at 70% 30%, rgba(212,170,97,.35), transparent 60%),
    repeating-linear-gradient(90deg, #2c3b36 0 14px, #34463f 14px 30px, #26332f 30px 52px),
    #1d2a28 }}
.scene .doc {{ position: absolute; inset: 14% 30% 14% 12%; background: #e9dfc8; border-radius: 3px; transform: rotate(-3deg);
  box-shadow: 0 10px 30px rgba(0,0,0,.45); padding: 6%; display: grid; gap: 6%; align-content: start }}
.scene .doc i {{ display: block; height: 7px; background: #8c7f69; border-radius: 2px; opacity: .55 }}
.scene .wm {{ position: absolute; width: 13%; inset-block-start: 5%; inset-inline-start: 4% }}
.scene .wm svg {{ width: 100%; height: auto; display: block; opacity: .92 }}
.scene .lbl {{ position: absolute; inset-block-end: 6px; inset-inline-end: 10px; font-size: 11px; color: #e9efee; opacity: .8 }}
.tests {{ display: grid; gap: 18px; overflow-x: auto }}
.testbox {{ background: #F4E9D3; border-radius: 8px; padding: 18px; display: grid; gap: 16px; min-width: max-content }}
.srow {{ display: flex; align-items: end; gap: 22px }}
.slabel {{ width: 120px; font-size: 14px; color: #1d2a2c; align-self: center }}
.srow figure {{ display: grid; justify-items: center; gap: 4px }}
.srow figcaption {{ font-family: var(--mono); font-size: 11px; color: #1d2a2c }}
.disc {{ border-radius: 50%; overflow: hidden }}
.disc svg, .disc img {{ width: 100%; height: 100%; display: block }}
table {{ border-collapse: collapse; width: 100%; font-size: 14.5px }}
.tbl {{ overflow-x: auto }}
th, td {{ text-align: right; padding: 9px 10px; border-bottom: 1px solid var(--line); vertical-align: top }}
th {{ color: var(--gold); font-weight: 600 }}
td.num {{ font-family: var(--mono); direction: ltr; text-align: left; white-space: nowrap }}
.ok {{ color: var(--turq) }}
code {{ font-family: var(--mono); font-size: 12.5px; color: var(--muted); direction: ltr; unicode-bidi: embed }}
@media (max-width: 860px) {{
  .hero, .two, .wide-row, .apps {{ grid-template-columns: 1fr }}
  .versions {{ grid-template-columns: repeat(2, minmax(0, 1fr)) }}
  .apps .phone {{ max-width: 300px }}
}}
@media (max-width: 460px) {{ .before-after {{ grid-template-columns: 1fr }} .before-after .arrow {{ transform: rotate(-90deg); justify-self: center }} }}
</style>

<div class="wrap" dir="rtl" lang="ar">
<header>
  <p class="eyebrow">خَيبر 2.0 | <span lang="en">KHAYBAR</span> · <span lang="en" dir="ltr">@bab.5aybar</span></p>
  <h1>الشعار النهائي المعتمد</h1>
  <p class="lead">المحراب المتّسع، بلا نجمة ولا ماسة صغيرة، بالماسات الفيروزية الثلاث، وبكلمة «خيبر» العاجية المطوّرة. نسختان متطابقتان هندسياً: الذهبي الرسمي المسطّح، والذهبي المعدني السينمائي.</p>
  <span class="status">بانتظار موافقتك</span>
</header>

<section aria-labelledby="s-final">
  <h2 id="s-final" class="eyebrow" style="font-family:var(--body);font-size:13px">النسختان الرسميتان</h2>
  <div class="hero">
    <figure class="plate"><div class="art">{svg("official/khaybar-logo-flat.svg")}</div>
      <figcaption><b>الذهبي الرسمي المسطّح.</b> لصورة الحساب والبطاقات والعلامة المائية والطباعة.</figcaption></figure>
    <figure class="plate"><div class="art">{svg("official/khaybar-logo-cinematic.svg")}</div>
      <figcaption><b>الذهبي المعدني السينمائي.</b> للمقدمة والخاتمة والمشاهد. المسارات نفسها، والفرق في التلوين فقط.</figcaption></figure>
  </div>
</section>

<section aria-labelledby="s-ba">
  <p class="eyebrow">من المرجع إلى التنفيذ</p>
  <h2 id="s-ba">الأصل ← خيبر 2.0</h2>
  <div class="before-after">
    <figure class="plate"><img src="assets/original-mark.jpg" alt="الشعار الأصلي من الفيديو" width="800" height="800" style="border-radius:50%"><figcaption>الأصل: لقطة من الفيديو عند 4.5 ثانية.</figcaption></figure>
    <span class="arrow" aria-hidden="true">←</span>
    <figure class="plate">{svg("official/khaybar-logo-flat.svg")}<figcaption>النهائي: الاسم داخل القوس.</figcaption></figure>
  </div>
  <div class="two">
    <div><h3>ما بقي من الأصل</h3><ul>
      <li>القوس نصف الدائري الذهبي بشريطيه المزدوجين والخط الداكن بينهما.</li>
      <li>العتبة الذهبية أسفل القوس، بنهايات مائلة 45°.</li>
      <li>الدائرة الذهبية الكاملة وحلقة النقاط الداخلية.</li>
      <li>نظام الكلمة الكوفي: سماكة واحدة وزاوية 45°.</li>
      <li>الماسات الفيروزية الثلاث نقاطاً لحرفي الياء والباء.</li>
    </ul></div>
    <div><h3>ما تغيّر</h3><ul>
      <li>الاسم انتقل إلى داخل القوس، فصار الشعار وحدة واحدة.</li>
      <li>حُذفت النجمة الثمانية والماسة الصغيرة.</li>
      <li>الألوان على اللوحة المعتمدة بدلاً من ألوان الفيديو الأكثر تشبعاً.</li>
      <li>الدائرة أسمك بثلاث مرات تقريباً، لتبقى ظاهرة في الأحجام الصغيرة.</li>
      <li>اسم <span lang="en">KHAYBAR</span> خرج من الشعار الدائري إلى النسخة الأفقية، لأنه لا يُقرأ داخله.</li>
    </ul></div>
  </div>
</section>

<section aria-labelledby="s-word">
  <p class="eyebrow">التوقيع العربي</p>
  <h2 id="s-word">«خيبر» على شبكتها</h2>
  <p class="lead">رسم متجه حصري، لا خط جاهز. كل الكلمة مبنية على وحدة واحدة هي سماكة الحرف، وعلى زاوية واحدة هي 45°.</p>
  {construction_svg()}
  <div class="two">
    <div><h3>التطوير عن كلمة الأصل</h3><ul>
      <li><b>فراغات متساوية:</b> المسافات بين الراء والباء والياء والخاء كلها 18 وحدة، وكانت في الأصل غير متساوية.</li>
      <li><b>خطوط محاذاة مشتركة:</b> رأسا السنّين على مستوى أسفل شَرطة الخاء، وطرف الشَّرطة الأيسر فوق نقطة التقاء مائل الخاء بالقاعدة.</li>
      <li><b>ذيل الراء</b> ينتهي على مستوى أسفل الماسات، فتستقر الكلمة على خط سفلي واحد.</li>
      <li><b>نقاط موحّدة:</b> نقطة الخاء العاجية بحجم الماسات الفيروزية، وفي منتصف شَرطة الخاء تماماً.</li>
      <li><b>نقاط في موضعها الإملائي:</b> نقطة الباء تحت سنّها، ونقطتا الياء متمركزتان تحت سنّها، والثلاث بمسافات متساوية.</li>
    </ul></div>
    <div class="plate"><div class="art">{svg("wordmark/khaybar-wordmark-latin.svg")}</div>
      <figcaption><b>الكلمة مستقلة مع KHAYBAR.</b> الحروف اللاتينية مرسومة بالنظام نفسه: سماكة واحدة وشطفات 45° بدل الانحناءات.</figcaption></div>
  </div>
</section>

<section aria-labelledby="s-versions">
  <p class="eyebrow">نسخ الشعار</p>
  <h2 id="s-versions">الحزمة</h2>
  <div class="versions">
    <figure class="plate"><div class="art">{svg("avatar/khaybar-avatar.svg")}</div><figcaption><b>صورة الحساب.</b> مربع 1080 بخلفية كاملة، كلمة أكبر، بلا نقاط.</figcaption></figure>
    <figure class="plate"><div class="art">{svg("small/khaybar-logo-small.svg")}</div><figcaption><b>الأحجام الصغيرة.</b> لـ 64 بكسل فأقل: دائرة وأشرطة أسمك.</figcaption></figure>
    <figure class="plate"><div class="art on-surface">{svg("mark/khaybar-mark-on-image.svg")}</div><figcaption><b>فوق الخلفيات المعقدة.</b> الشعار بقرصه الداكن الخاص.</figcaption></figure>
    <figure class="plate"><div class="art on-surface">{svg("mono/khaybar-logo-mono-ivory.svg")}</div><figcaption><b>أحادي عاجي.</b> شفاف، فوق الصور والسطوح الداكنة.</figcaption></figure>
    <figure class="plate"><div class="art on-ivory">{svg("mono/khaybar-logo-mono-dark.svg")}</div><figcaption><b>أحادي داكن.</b> للخلفيات الفاتحة والطباعة بلون واحد.</figcaption></figure>
    <figure class="plate"><div class="art">{svg("wordmark/khaybar-wordmark-cinematic.svg")}</div><figcaption><b>الكلمة السينمائية.</b> عاجي متدرج وماسات بإضاءة خفيفة.</figcaption></figure>
  </div>
  <div class="wide-row">
    <figure class="plate"><div class="art wide">{svg("horizontal/khaybar-horizontal.svg")}</div><figcaption><b>النسخة الأفقية المساعدة.</b> الشعار يمين الفاصل بحسب اتجاه القراءة، ثم الكلمة وKHAYBAR. للبطاقات الختامية والرؤوس العريضة.</figcaption></figure>
    <figure class="plate"><div class="art wide">{svg("wordmark/khaybar-wordmark.svg")}</div><figcaption><b>الكلمة وحدها.</b> توقيع مستقل عن الشعار.</figcaption></figure>
  </div>
</section>

<section aria-labelledby="s-apps">
  <p class="eyebrow">تطبيقات على خلفيات داكنة</p>
  <h2 id="s-apps">في مكانه</h2>
  <div class="apps">
    <figure class="plate"><div class="phone">{svg("official/khaybar-logo-cinematic.svg")}<p class="tag">بالعقل نقرأ… وبالبصيرة نرى</p><p class="handle">@bab.5aybar</p></div>
      <figcaption><b>لقطة الخاتمة 9:16.</b> الشعار المعدني والشعار اللفظي. الخط هنا مؤقت حتى اعتماد النظام الطباعي.</figcaption></figure>
    <figure class="plate"><div class="profile">
        <div class="top"><div class="av">{svg("avatar/khaybar-avatar.svg")}</div>
          <div><div class="name">خَيبر | KHAYBAR</div><div class="handle">@bab.5aybar</div></div></div>
        <div class="grid9"><span>{svg("small/khaybar-logo-small.svg")}</span><span></span><span></span><span></span><span></span><span></span></div>
      </div><figcaption><b>صفحة الحساب.</b> صورة الحساب بحجم 86 بكسل، والنسخة الصغيرة في شبكة المنشورات.</figcaption></figure>
    <figure class="plate"><div class="scene"><div class="doc"><i></i><i style="width:80%"></i><i></i><i style="width:65%"></i><i></i><i style="width:72%"></i></div>
        <div class="wm">{svg("mark/khaybar-mark-on-image.svg")}</div><span class="lbl">مشهد تمثيلي</span></div>
      <figcaption><b>علامة مائية فوق مشهد مزدحم.</b> شعار صغير في الزاوية لا يغطي الوثيقة. نظام العلامة المائية المتكيّفة يأتي في مرحلة الموشن.</figcaption></figure>
  </div>
</section>

<section aria-labelledby="s-sizes">
  <p class="eyebrow">اختبار الأحجام · قص دائري على خلفية فاتحة</p>
  <h2 id="s-sizes">الأحجام الصغيرة</h2>
  <div class="tests">
    <div class="testbox">{rows_small}</div>
    <div class="testbox">{rows_avatar}</div>
  </div>
  <ul>
    <li>عند 48 بكسل تبقى الكلمة والقوس والدائرة واضحة في النسخة المبسطة، وتصبح الماسات الثلاث نقاطاً متتابعة مقروءة.</li>
    <li>عند 32 بكسل يبقى الشكل العام معروفاً: قوس ذهبي فيه كلمة عاجية. هذا أصغر حجم يُستعمل فيه الشعار.</li>
    <li>الشعار الرسمي الكامل لا يُستعمل تحت 128 بكسل، لأن حلقة النقاط والخط الداكن في القوس يذوبان. تحت هذا الحجم تحل محله النسخة المبسطة.</li>
  </ul>
</section>

<section aria-labelledby="s-qa" style="border-bottom:0">
  <p class="eyebrow">ضمان الجودة والقرارات التنفيذية</p>
  <h2 id="s-qa">ملاحظات المرحلة</h2>
  <div class="two">
    <div class="tbl"><table>
      <tr><th>الفحص</th><th>النتيجة</th></tr>
      <tr><td>ملفات SVG صالحة، متجهة بالكامل، بلا صور ولا خطوط ولا نصوص</td><td class="{"ok" if qa_ok else ""}">{"ناجح" if qa_ok else "فشل"} · {len(QA["files"])} ملفاً</td></tr>
      <tr><td>المسطّح والسينمائي متطابقان هندسياً</td><td class="ok">{"ناجح" if QA["flat_cinematic_identical"] else "فشل"}</td></tr>
      <tr><td>تباين العاجي على الخلفية</td><td class="num">{QA["contrast"]["#F4E9D3 on #071F26"]}:1</td></tr>
      <tr><td>تباين الذهبي على الخلفية</td><td class="num">{QA["contrast"]["#D4AA61 on #071F26"]}:1</td></tr>
      <tr><td>تباين الفيروزي على الخلفية</td><td class="num">{QA["contrast"]["#2DB9B6 on #071F26"]}:1</td></tr>
      <tr><td>سماكة حرف الكلمة / شريط القوس</td><td class="num">{mf["word_stroke"]} / 24</td></tr>
      <tr><td>ملفات PNG مصدّرة</td><td class="num">28</td></tr>
    </table></div>
    <div><h3>قرارات تنفيذية اتخذتها داخل الاتجاه المعتمد</h3><ul>
      <li>نقطة الخاء عاجية لأنها جزء من الكلمة، وبحجم الماسات نفسه.</li>
      <li>الكلمة أثقل من شريط القوس، لتكون هي البطل والقوس إطارها.</li>
      <li>حذف الخط الشعري الداخلي الذي كان في المقترح B، لأنه يتقاطع مع العتبة.</li>
      <li>نهايات العتبة مائلة 45°، لتتبع زاوية الكلمة.</li>
      <li>الزخرفة الهندسية الخافتة والتوهج داخل الباب في النسخة السينمائية فقط. النسخة المسطحة نظيفة.</li>
      <li>صورة الحساب والنسخة الصغيرة تُكبّران الكلمة وتسمّكان الدائرة، مع بقاء القوس والعتبة والماسات.</li>
    </ul></div>
  </div>
  <p class="lead">الملفات في <code>brand/logo/</code> و<code>exports/logo/</code>، والتوثيق في <code>docs/logo-final.md</code>.</p>
</section>
</div>
'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT, len(html) // 1024, "KB")
