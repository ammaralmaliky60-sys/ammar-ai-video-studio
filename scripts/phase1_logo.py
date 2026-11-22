#!/usr/bin/env python3
"""
KHAYBAR — Phase 1 logo architecture generator.

Builds three real-vector logo proposals (SVG) from geometry measured on the
original identity video (references/khaybar-original.mp4, frame @4.5s).

All shapes are computed paths (no embedded raster, no fonts).
Run:  python3 scripts/phase1_logo.py
"""
import json
import math
import os
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "brand", "logo", "archive", "phase-1-proposals")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# Approved palette (brief §5). Flat Official Gold only in phase 1.
# ---------------------------------------------------------------------------
C = {
    "bg": "#071F26",
    "gold": "#D4AA61",
    "ivory": "#F4E9D3",
    "turq": "#2DB9B6",
    "surface": "#153840",
}

# ---------------------------------------------------------------------------
# 1) WORDMARK — reconstruction of the original «خيبر» (reference R0)
#    Units: stroke t = 10. Measured px / 3.5 (original stroke = 35px).
#    Origin: x=0 at the tip of the ra tail, y=0 at the bottom of the baseline.
#    Every slanted stroke is exactly 45°, as in the original.
# ---------------------------------------------------------------------------
T = 10.0
D45 = T * math.sqrt(2)  # horizontal width of a 45° stroke of thickness T


def wordmark_r0():
    parts = []
    # baseline (connecting stroke)
    parts.append(box(28.3, -T, 104.0, 0))
    # ر — final ra: 45° tail descending to the lower-left
    tail_bottom = 18.3
    parts.append(Polygon([(28.3, -T), (28.3 - (tail_bottom + T), tail_bottom),
                          (28.3 - (tail_bottom + T) + D45, tail_bottom), (28.3 + D45, -T)]))
    # ب tooth, ي tooth
    tooth_top = -25.4
    parts.append(box(46.3, tooth_top, 46.3 + T, -T + 0.01))
    parts.append(box(73.7, tooth_top, 73.7 + T, -T + 0.01))
    # خ — initial kha: top bar + 45° diagonal down to the baseline
    kb_top, kb_bot = -37.4, -27.4
    kx_r = 148.0
    parts.append(box(101.0, kb_top, kx_r, kb_bot))
    parts.append(Polygon([(kx_r, kb_top), (kx_r + kb_top, 0), (kx_r + kb_top - D45, 0),
                          (kx_r - D45, kb_top)]))
    body = unary_union(parts).buffer(0)
    # dots
    kha_dot = diamond(122.6, -48.3, 4.9)
    turq_dots = [diamond(51.4, 13.7, 7.1),            # ب  (one dot)
                 diamond(69.7, 13.7, 7.1), diamond(88.0, 13.7, 7.1)]  # ي (two dots)
    return {"body": body, "kha_dot": kha_dot, "turq": turq_dots}


def diamond(cx, cy, h):
    return Polygon([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)])


def poly_to_d(geom, tx):
    """Shapely polygon(s) -> SVG path data with transform tx(x,y)->(X,Y)."""
    geoms = getattr(geom, "geoms", [geom])
    d = []
    for g in geoms:
        for ring in [g.exterior, *g.interiors]:
            pts = list(ring.coords)[:-1]
            # drop collinear points for a clean editable path
            clean = []
            n = len(pts)
            for i, p in enumerate(pts):
                a, b = pts[i - 1], pts[(i + 1) % n]
                cross = (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])
                if abs(cross) > 1e-6:
                    clean.append(p)
            seg = []
            for i, (x, y) in enumerate(clean):
                X, Y = tx(x, y)
                seg.append(("M" if i == 0 else "L") + f"{X:.2f} {Y:.2f}")
            d.append(" ".join(seg) + " Z")
    return " ".join(d)


def word_bounds(w):
    allg = unary_union([w["body"], w["kha_dot"], *w["turq"]])
    return allg.bounds  # minx, miny, maxx, maxy


# ---------------------------------------------------------------------------
# 2) SHARED GEOMETRY HELPERS
# ---------------------------------------------------------------------------
def arch_band(cx, cy, ro, ri, yb):
    """Inverted-U band: semicircular crown (center cx,cy) + straight legs to yb."""
    return (f"M{cx-ro:.2f} {yb:.2f} V{cy:.2f} A{ro:.2f} {ro:.2f} 0 0 1 {cx+ro:.2f} {cy:.2f} "
            f"V{yb:.2f} H{cx+ri:.2f} V{cy:.2f} A{ri:.2f} {ri:.2f} 0 0 0 {cx-ri:.2f} {cy:.2f} "
            f"V{yb:.2f} Z")


def arch_opening(cx, cy, r, yb):
    return (f"M{cx-r:.2f} {yb:.2f} V{cy:.2f} A{r:.2f} {r:.2f} 0 0 1 {cx+r:.2f} {cy:.2f} "
            f"V{yb:.2f} Z")


def star8(cx, cy, r, inner_ratio=0.0):
    """8-point star made of two squares (the original's Rub el Hizb-like star)."""
    sq1 = Polygon([(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
                   for a in (0, 90, 180, 270)])
    sq2 = Polygon([(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
                   for a in (45, 135, 225, 315)])
    s = unary_union([sq1, sq2])
    if inner_ratio:
        ri = r * inner_ratio
        i1 = Polygon([(cx + ri * math.cos(math.radians(a + 22.5)), cy + ri * math.sin(math.radians(a + 22.5)))
                      for a in (0, 90, 180, 270)])
        i2 = Polygon([(cx + ri * math.cos(math.radians(a + 22.5)), cy + ri * math.sin(math.radians(a + 22.5)))
                      for a in (45, 135, 225, 315)])
        s = s.difference(unary_union([i1, i2]))
    return s


def ident(x, y):
    return x, y


def platform(cx, y, w_top, w_bot, h):
    return (f"M{cx-w_top/2:.2f} {y:.2f} H{cx+w_top/2:.2f} L{cx+w_bot/2:.2f} {y+h:.2f} "
            f"H{cx-w_bot/2:.2f} Z")


def dotted_ring(cx, cy, r, n, dot_r):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(f'<circle cx="{cx + r*math.cos(a):.2f}" cy="{cy + r*math.sin(a):.2f}" r="{dot_r}"/>')
    return "".join(out)


PATTERN = """
  <pattern id="{pid}" width="80" height="80" patternUnits="userSpaceOnUse">
    <g fill="none" stroke="{gold}" stroke-width="1.2" opacity=".55">
      <rect x="20" y="20" width="40" height="40"/>
      <rect x="20" y="20" width="40" height="40" transform="rotate(45 40 40)"/>
      <path d="M0 0 L20 20 M80 0 L60 20 M0 80 L20 60 M80 80 L60 60"/>
    </g>
  </pattern>"""


# ---------------------------------------------------------------------------
# 3) PROPOSALS
# ---------------------------------------------------------------------------
PROPOSALS = {
    "A": dict(
        name_ar="الباب الأصيل",
        name_en="Faithful Portal",
        cx=500, arch_top=160, ro=272, band1=26, gap=5, band2=26, leg_bottom=740,
        plat=dict(gap=10, h=24, w_top=636, w_bot=676),
        star=dict(r=42, inner=0.48, mode="crown", rel=0.36),
        word=dict(width=362, bottom=694),
        ring=dict(r=470, stroke=7, dots=True, inner_line=True),
        pattern=True,
    ),
    "B": dict(
        name_ar="المحراب المتّسع",
        name_en="Wide Mihrab",
        cx=500, arch_top=140, ro=318, band1=24, gap=5, band2=24, leg_bottom=742,
        plat=dict(gap=9, h=20, w_top=690, w_bot=720),
        star=dict(r=30, inner=0.46, mode="keystone"),
        word=dict(width=468, bottom=694),
        ring=dict(r=470, stroke=7, dots=True, inner_line=True),
        pattern=True,
    ),
    "C": dict(
        name_ar="البوابة المحكمة",
        name_en="Sealed Gate",
        cx=500, arch_top=150, ro=290, band1=42, gap=0, band2=0, leg_bottom=748,
        plat=None,
        base=dict(h=42),
        star=dict(r=36, inner=0.44, mode="crown", rel=0.45),
        word=dict(width=416, bottom=704),
        ring=dict(r=468, stroke=14, dots=False, inner_line=False),
        pattern=False,
    ),
}


def build(key, p, word, variant="full"):
    """variant: full | small (no pattern/dots, heavier hairlines)."""
    small = variant == "small"
    cx, cy0 = p["cx"], 500
    R = p["ring"]["r"]
    els = []
    defs = []

    # background disc + soft radial light
    defs.append(f'''
  <radialGradient id="bg{key}" cx="50%" cy="46%" r="55%">
    <stop offset="0" stop-color="{C['surface']}"/>
    <stop offset="1" stop-color="{C['bg']}"/>
  </radialGradient>
  <clipPath id="disc{key}"><circle cx="{cx}" cy="{cy0}" r="{R}"/></clipPath>''')
    els.append(f'<rect width="1000" height="1000" fill="{C["bg"]}"/>')
    els.append(f'<circle cx="{cx}" cy="{cy0}" r="{R}" fill="url(#bg{key})"/>')

    if p.get("pattern") and not small:
        defs.append(PATTERN.format(pid=f"pat{key}", gold=C["gold"]))
        els.append(f'<g clip-path="url(#disc{key})" opacity=".09"><rect width="1000" height="1000" fill="url(#pat{key})"/></g>')

    # ring system
    rg = p["ring"]
    sw = rg["stroke"] * (1.35 if small and rg["stroke"] < 10 else 1)
    els.append(f'<circle id="ring" cx="{cx}" cy="{cy0}" r="{R - sw/2:.2f}" fill="none" stroke="{C["gold"]}" stroke-width="{sw:.2f}"/>')
    if rg.get("dots") and not small:
        els.append(f'<g id="ring-dots" fill="{C["gold"]}" opacity=".85">{dotted_ring(cx, cy0, R - 24, 120, 2.6)}</g>')
    if rg.get("inner_line") and not small:
        els.append(f'<circle cx="{cx}" cy="{cy0}" r="{R-42}" fill="none" stroke="{C["gold"]}" stroke-width="1.4" opacity=".35"/>')
    if key == "C":
        # inner hairline ring at a legible distance (survives small sizes)
        els.append(f'<circle cx="{cx}" cy="{cy0}" r="{R-34}" fill="none" stroke="{C["gold"]}" stroke-width="{5 if small else 4}" opacity="{1 if small else .9}"/>')

    # arch
    ro = p["ro"]
    acy = p["arch_top"] + ro  # crown centre (springline)
    if p["leg_bottom"] is None:
        # legs descend until they meet the inner ring circle (Proposal C)
        r_in = R - 34
        yb = cy0 + math.sqrt(r_in**2 - ro**2)
    else:
        yb = p["leg_bottom"]
    ri1 = ro - p["band1"]
    arch_paths = [arch_band(cx, acy, ro, ri1, yb)]
    open_r = ri1
    if p["band2"]:
        ro2 = ri1 - p["gap"]
        ri2 = ro2 - p["band2"]
        arch_paths.append(arch_band(cx, acy, ro2, ri2, yb))
        open_r = ri2
    clip = ""

    # glow inside opening (subtle, flat-friendly)
    defs.append(f'''
  <radialGradient id="glow{key}" cx="50%" cy="38%" r="65%">
    <stop offset="0" stop-color="{C['gold']}" stop-opacity=".16"/>
    <stop offset="1" stop-color="{C['gold']}" stop-opacity="0"/>
  </radialGradient>''')
    if not small:
        els.append(f'<path d="{arch_opening(cx, acy, open_r, yb)}" fill="url(#glow{key})"/>')

    els.append(f'<g id="arch" fill="{C["gold"]}"{clip}>' + "".join(f'<path d="{d}"/>' for d in arch_paths) + "</g>")

    # platform / threshold
    if p.get("plat"):
        pl = p["plat"]
        els.append(f'<path id="threshold" fill="{C["gold"]}" d="{platform(cx, yb + pl["gap"], pl["w_top"], pl["w_bot"], pl["h"])}"/>')
    if p.get("base"):
        # closed gate: base joins both legs into one continuous frame
        els.append(f'<rect id="threshold" x="{cx-ro:.2f}" y="{yb-0.5:.2f}" width="{2*ro:.2f}" height="{p["base"]["h"]+0.5}" fill="{C["gold"]}"/>')

    # star
    st = p["star"]
    if st["mode"] == "crown" and small:
        star = None  # crown star dropped at small sizes: the word takes the opening
    elif st["mode"] == "crown":
        sy = acy - open_r * st["rel"]
        star = star8(cx, sy, st["r"], st["inner"])
    else:  # keystone: sits on the arch apex, cut out of the bands
        band_total = ro - open_r
        sy = p["arch_top"] + band_total / 2
        halo = star8(cx, sy, st["r"] + 9)
        els.append(f'<path fill="{C["bg"]}" d="{poly_to_d(halo, ident)}"/>')
        star = star8(cx, sy, st["r"], st["inner"])
    if star is not None:
        els.append(f'<path id="star" fill="{C["ivory"]}" fill-rule="evenodd" d="{poly_to_d(star, ident)}"/>')

    # wordmark inside the arch
    minx, miny, maxx, maxy = word_bounds(word)
    if small:
        # small-size lockup: word fills the opening, centred in the usable opening
        s = (2 * open_r * 0.9) / (maxx - minx)
        top_lim = acy - open_r * (0.55 if st["mode"] == "crown" else 0.75)
        bot_lim = yb - 0.06 * open_r
        mid = (top_lim + bot_lim) / 2
        oy = mid - (miny + maxy) / 2 * s
    else:
        s = p["word"]["width"] / (maxx - minx)
        oy = p["word"]["bottom"] - maxy * s
    ox = cx - (minx + maxx) / 2 * s

    def tw(x, y):
        return ox + x * s, oy + y * s

    els.append(f'<g id="wordmark"><path class="wm" fill="{C["ivory"]}" d="{poly_to_d(word["body"], tw)}"/>'
               f'<path class="wm" fill="{C["ivory"]}" d="{poly_to_d(word["kha_dot"], tw)}"/>'
               f'<g id="turquoise-diamonds" fill="{C["turq"]}">' +
               "".join(f'<path d="{poly_to_d(t, tw)}"/>' for t in word["turq"]) + "</g></g>")

    meta = dict(word_scale=round(s, 3), word_stroke_px=round(T * s, 1), band_px=p["band1"],
                opening_width=round(2 * open_r, 1), arch_outer_width=2 * ro,
                arch_height=round(yb - p["arch_top"], 1), leg_bottom=round(yb, 1))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">\n'
           f'<title>KHAYBAR — Proposal {key} ({p["name_en"]})</title>\n'
           f'<defs>{"".join(defs)}\n</defs>\n' + "\n".join(els) + "\n</svg>\n")
    return svg, meta


def wordmark_svg(word):
    minx, miny, maxx, maxy = word_bounds(word)
    pad = 12
    s = 6
    W, H = (maxx - minx + 2 * pad) * s, (maxy - miny + 2 * pad) * s

    def tw(x, y):
        return (x - minx + pad) * s, (y - miny + pad) * s
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">\n'
            f'<title>KHAYBAR wordmark — R0 reconstruction of the original</title>\n'
            f'<rect width="100%" height="100%" fill="{C["bg"]}"/>\n'
            f'<path fill="{C["ivory"]}" d="{poly_to_d(word["body"], tw)}"/>\n'
            f'<path fill="{C["ivory"]}" d="{poly_to_d(word["kha_dot"], tw)}"/>\n'
            f'<g fill="{C["turq"]}">' + "".join(f'<path d="{poly_to_d(t, tw)}"/>' for t in word["turq"]) +
            "</g>\n</svg>\n")


if __name__ == "__main__":
    w = wordmark_r0()
    with open(os.path.join(OUT, "wordmark-R0-reconstruction.svg"), "w") as f:
        f.write(wordmark_svg(w))
    metas = {}
    for k, p in PROPOSALS.items():
        for variant in ("full", "small"):
            svg, meta = build(k, p, w, variant)
            fn = f"khaybar-proposal-{k}.svg" if variant == "full" else f"khaybar-proposal-{k}-small.svg"
            with open(os.path.join(OUT, fn), "w") as f:
                f.write(svg)
        metas[k] = dict(name_ar=p["name_ar"], name_en=p["name_en"], **meta)
    with open(os.path.join(OUT, "proposals-meta.json"), "w") as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)
    print(json.dumps(metas, ensure_ascii=False, indent=2))
