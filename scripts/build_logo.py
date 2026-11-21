#!/usr/bin/env python3
"""
KHAYBAR 2.0 — final logo system generator.

Approved direction: proposal B (Wide Mihrab), star and small diamond removed,
three turquoise diamonds kept as the letter dots, word in ivory.

ONE geometry source -> every version (flat, cinematic, avatar, small, mono,
mark, wordmark, horizontal lockup). Flat and cinematic share identical paths;
only paint differs (verified by scripts/qa_logo.py).

Run:  python3 scripts/build_logo.py
"""
import json
import math
import os

from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK = json.load(open(os.path.join(ROOT, "brand", "design-tokens", "tokens.json"), encoding="utf-8"))
C = {k: v["value"] for k, v in TOK["color"]["brand"].items()}
G = {k: v["value"] for k, v in TOK["color"]["derived"].items() if not k.startswith("_")}
OUT = os.path.join(ROOT, "brand", "logo")


# ===========================================================================
# 1. WORDMARK «خيبر» — W1 (final)
#    Grid unit: stroke T = 10. y = 0 is the bottom of the baseline stroke,
#    negative is up. Every slanted stroke is 45°. Every counter is 18.
# ===========================================================================
T = 10.0
D = T * math.sqrt(2)          # horizontal width of a 45° stroke
CNT = 18.0                    # counter (gap) between vertical events
TOOTH_TOP = -28.0             # tooth tops align with the kha bar's lower edge
KHA_TOP = -38.0               # kha bar: -38 .. -28
DESC = 18.0                   # ra tail depth = bottom of the diamonds
DOT = 7.0                     # half-diagonal of every dot (all four identical)
DOT_GAP = 4.0                 # dot to stroke clearance


def wordmark():
    xr = 28.0                               # ra: top-left corner of its tail
    t1 = xr + CNT                           # ب tooth
    t2 = t1 + T + CNT                       # ي tooth
    kj = t2 + T + CNT                       # kha diagonal meets the baseline (inner edge)
    k_out_c = kj + T + D                    # x + y = const for the kha's outer edge (at y=-10 -> kj + D)
    # inner edge: x + y = kj - T ; outer edge: x + y = kj - T + D
    inner_c = kj - T
    outer_c = inner_c + D
    tip_x = outer_c - KHA_TOP               # kha top-right tip
    base_end = outer_c                      # outer edge at y = 0

    parts = [
        box(xr, -T, base_end, 0),                                        # baseline
        Polygon([(xr, -T), (xr - T - DESC, DESC),                        # ر tail
                 (xr - T - DESC + D, DESC), (xr + D, -T)]),
        box(t1, TOOTH_TOP, t1 + T, -T + 0.001),                          # ب
        box(t2, TOOTH_TOP, t2 + T, -T + 0.001),                          # ي
        box(kj, KHA_TOP, tip_x - 0.001, KHA_TOP + T),                    # خ bar
        Polygon([(tip_x, KHA_TOP), (base_end, 0), (inner_c, 0),         # خ diagonal
                 (inner_c - KHA_TOP, KHA_TOP)]),
    ]
    body = unary_union(parts).buffer(0)
    # dots — ب one dot under its tooth, ي two dots centred under its tooth,
    # equal pitch so the three read as one row (the original's signature).
    c1 = t1 + T / 2
    pitch = ((t2 + T / 2) - c1) / 1.5
    dy = DOT_GAP + DOT
    turq = [diamond(c1 + i * pitch, dy, DOT) for i in range(3)]
    kha_dot = diamond((kj + tip_x) / 2, KHA_TOP - DOT_GAP - DOT, DOT)
    return dict(body=body, kha_dot=kha_dot, turq=turq,
                grid=dict(xr=xr, t1=t1, t2=t2, kj=kj, tip_x=tip_x, pitch=pitch))


def diamond(cx, cy, h):
    return Polygon([(cx, cy - h), (cx + h, cy), (cx, cy + h), (cx - h, cy)])


def bounds(geoms):
    return unary_union(geoms).bounds


# ===========================================================================
# 2. LATIN «KHAYBAR» — constructed in the same system (stroke, 45°, flush cuts)
# ===========================================================================
LH, LT = 60.0, 9.0  # cap height, stroke


def _strokes(lines, w):
    shapes = [LineString(p).buffer(LT / 2, cap_style=2, join_style=2, mitre_limit=4) for p in lines]
    return unary_union(shapes).intersection(box(0, -LH, w, 0))


def latin_letters():
    h, t, e = LH, LT, LT          # e: overshoot beyond the clip box
    c = 12.0                      # 45° chamfer
    L = {}
    w = 40.0
    j = t
    L["K"] = (_strokes([[(t/2, e), (t/2, -h - e)],
                        [(j - 2, -h/2 + 2), (j - 2 + h, -h/2 + 2 - h)],
                        [(j + 6, -h/2 + 6 - 8), (j + 6 + h, -h/2 + 6 - 8 + h)]], w), w)
    w = 42.0
    L["H"] = (_strokes([[(t/2, e), (t/2, -h - e)], [(w - t/2, e), (w - t/2, -h - e)],
                        [(0, -h/2), (w, -h/2)]], w), w)
    w = 44.0
    L["A"] = (_strokes([[(t/2, e), (t/2, -h + t/2 + c), (t/2 + c, -h + t/2), (w - t/2 - c, -h + t/2),
                         (w - t/2, -h + t/2 + c), (w - t/2, e)],
                        [(0, -h * 0.42), (w, -h * 0.42)]], w), w)
    w = 46.0
    m = -h + w / 2
    L["Y"] = (_strokes([[(-e, -h - e), (w / 2, m)], [(w + e, -h - e), (w / 2, m)],
                        [(w / 2, m), (w / 2, e)]], w), w)
    w = 42.0
    mid = -h / 2 - 1
    L["B"] = (_strokes([[(t/2, e), (t/2, -h - e)],
                        [(0, -h + t/2), (w - 4 - t/2 - c*0.6, -h + t/2), (w - 4 - t/2, -h + t/2 + c*0.6),
                         (w - 4 - t/2, mid - c*0.6), (w - 4 - t/2 - c*0.6, mid), (0, mid)],
                        [(0, mid), (w - t/2 - c*0.7, mid), (w - t/2, mid + c*0.7),
                         (w - t/2, -t/2 - c*0.7), (w - t/2 - c*0.7, -t/2), (0, -t/2)]], w), w)
    w = 42.0
    L["R"] = (_strokes([[(t/2, e), (t/2, -h - e)],
                        [(0, -h + t/2), (w - t/2 - c*0.7, -h + t/2), (w - t/2, -h + t/2 + c*0.7),
                         (w - t/2, mid - c*0.7), (w - t/2 - c*0.7, mid), (0, mid)],
                        [(w * 0.42, mid), (w * 0.42 + h, mid + h)]], w), w)
    return L


def latin_word(text="KHAYBAR", track=26.0):
    L = latin_letters()
    x, shapes = 0.0, []
    from shapely import affinity
    for ch in text:
        g, w = L[ch]
        shapes.append(affinity.translate(g, x, 0))
        x += w + track
    return unary_union(shapes), x - track


# ===========================================================================
# 3. SVG HELPERS
# ===========================================================================
def poly_d(geom, tx):
    geoms = getattr(geom, "geoms", [geom])
    out = []
    for g in geoms:
        if g.is_empty:
            continue
        for ring in [g.exterior, *g.interiors]:
            pts = list(ring.coords)[:-1]
            n, clean = len(pts), []
            for i, p in enumerate(pts):
                a, b = pts[i - 1], pts[(i + 1) % n]
                if abs((p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])) > 1e-6:
                    clean.append(p)
            out.append("M" + " L".join(f"{tx(x, y)[0]:.2f} {tx(x, y)[1]:.2f}" for x, y in clean) + " Z")
    return " ".join(out)


def arch_band(cx, cy, ro, ri, yb):
    return (f"M{cx-ro:.2f} {yb:.2f} V{cy:.2f} A{ro:.2f} {ro:.2f} 0 0 1 {cx+ro:.2f} {cy:.2f} "
            f"V{yb:.2f} H{cx+ri:.2f} V{cy:.2f} A{ri:.2f} {ri:.2f} 0 0 0 {cx-ri:.2f} {cy:.2f} V{yb:.2f} Z")


def arch_opening(cx, cy, r, yb):
    return f"M{cx-r:.2f} {yb:.2f} V{cy:.2f} A{r:.2f} {r:.2f} 0 0 1 {cx+r:.2f} {cy:.2f} V{yb:.2f} Z"


def trapezoid(cx, y, w_top, w_bot, h):
    return f"M{cx-w_top/2:.2f} {y:.2f} H{cx+w_top/2:.2f} L{cx+w_bot/2:.2f} {y+h:.2f} H{cx-w_bot/2:.2f} Z"


def ring_d(cx, cy, r_out, r_in):
    """Annulus as a filled path (clean vector, scales without stroke issues)."""
    return (f"M{cx-r_out:.2f} {cy:.2f} A{r_out:.2f} {r_out:.2f} 0 1 0 {cx+r_out:.2f} {cy:.2f} "
            f"A{r_out:.2f} {r_out:.2f} 0 1 0 {cx-r_out:.2f} {cy:.2f} Z "
            f"M{cx-r_in:.2f} {cy:.2f} A{r_in:.2f} {r_in:.2f} 0 1 1 {cx+r_in:.2f} {cy:.2f} "
            f"A{r_in:.2f} {r_in:.2f} 0 1 1 {cx-r_in:.2f} {cy:.2f} Z")


def dots_d(cx, cy, r, n, rad):
    parts = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        parts.append(f"M{x-rad:.2f} {y:.2f} a{rad} {rad} 0 1 0 {2*rad} 0 a{rad} {rad} 0 1 0 {-2*rad} 0 Z")
    return " ".join(parts)


# ===========================================================================
# 4. MASTER GEOMETRY (1000 × 1000 emblem)
# ===========================================================================
CX = CY = 500.0
SPEC = {
    # size variants share the arch architecture; small/avatar simplify detail
    "full":   dict(R=470, ring=9,  dots=True,  bands=(24, 5, 24), word_w=452, word_cy=505, th=(9, 20)),
    "avatar": dict(R=470, ring=16, dots=False, bands=(26, 6, 26), word_w=470, word_cy=500, th=(9, 22)),
    "small":  dict(R=470, ring=24, dots=False, bands=(30, 9, 30), word_w=470, word_cy=498, th=(10, 26)),
}
ARCH = dict(top=150.0, ro=314.0, leg=748.0)
TH_SLOPE = 1.0  # threshold ends at 45°


def geometry(variant="full"):
    s = SPEC[variant]
    w = wordmark()
    R = s["R"]
    b1, gap, b2 = s["bands"]
    ro = ARCH["ro"]
    acy = ARCH["top"] + ro
    yb = ARCH["leg"]
    ri1 = ro - b1
    ro2 = ri1 - gap
    ri2 = ro2 - b2
    th_gap, th_h = s["th"]
    w_top = 2 * ro + 20
    w_bot = w_top + 2 * th_h * TH_SLOPE
    minx, miny, maxx, maxy = bounds([w["body"], w["kha_dot"], *w["turq"]])
    sc = s["word_w"] / (maxx - minx)
    ox = CX - (minx + maxx) / 2 * sc
    oy = s["word_cy"] - (miny + maxy) / 2 * sc

    def tw(x, y):
        return ox + x * sc, oy + y * sc

    g = dict(
        R=R,
        disc=f"M{CX-R} {CY} A{R} {R} 0 1 0 {CX+R} {CY} A{R} {R} 0 1 0 {CX-R} {CY} Z",
        ring=ring_d(CX, CY, R, R - s["ring"]),
        dots=dots_d(CX, CY, R - s["ring"] - 15, 120, 2.6) if s["dots"] else None,
        arch=[arch_band(CX, acy, ro, ri1, yb), arch_band(CX, acy, ro2, ri2, yb)],
        opening=arch_opening(CX, acy, ri2, yb),
        threshold=trapezoid(CX, yb + th_gap, w_top, w_bot, th_h),
        word_body=poly_d(w["body"], tw),
        kha_dot=poly_d(w["kha_dot"], tw),
        turq=[poly_d(t, tw) for t in w["turq"]],
        meta=dict(word_scale=round(sc, 4), word_stroke=round(T * sc, 2), opening=round(2 * ri2, 1),
                  arch_outer=2 * ro, threshold_bottom=yb + th_gap + th_h, threshold_w=round(w_bot, 1)),
    )
    return g


# ===========================================================================
# 5. PAINTS
# ===========================================================================
def paint(style):
    if style == "flat":
        return dict(defs="", disc=C["primaryBackground"], gold=C["heritageGold"], ivory=C["warmIvory"],
                    turq=C["insightTurquoise"], ring=C["heritageGold"], glow=None, pattern=False)
    if style == "cinematic":
        defs = f"""
  <radialGradient id="k-disc" cx="50%" cy="44%" r="58%">
    <stop offset="0" stop-color="{C['secondarySurface']}"/>
    <stop offset=".72" stop-color="{G['backgroundDeep']}"/>
    <stop offset="1" stop-color="{C['primaryBackground']}"/>
  </radialGradient>
  <linearGradient id="k-gold" gradientUnits="userSpaceOnUse" x1="250" y1="150" x2="760" y2="800">
    <stop offset="0" stop-color="{G['goldHighlight']}"/>
    <stop offset=".34" stop-color="{C['heritageGold']}"/>
    <stop offset=".62" stop-color="{G['goldShadow']}"/>
    <stop offset=".82" stop-color="{G['goldLight']}"/>
    <stop offset="1" stop-color="{C['heritageGold']}"/>
  </linearGradient>
  <linearGradient id="k-ring" gradientUnits="userSpaceOnUse" x1="120" y1="80" x2="880" y2="920">
    <stop offset="0" stop-color="{G['goldHighlight']}"/>
    <stop offset=".3" stop-color="{C['heritageGold']}"/>
    <stop offset=".55" stop-color="{G['goldShadow']}"/>
    <stop offset=".78" stop-color="{G['goldLight']}"/>
    <stop offset="1" stop-color="{G['goldShadow']}"/>
  </linearGradient>
  <linearGradient id="k-ivory" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{G['ivoryHighlight']}"/>
    <stop offset="1" stop-color="{G['ivoryShadow']}"/>
  </linearGradient>
  <linearGradient id="k-turq" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{G['turquoiseLight']}"/>
    <stop offset=".55" stop-color="{C['insightTurquoise']}"/>
    <stop offset="1" stop-color="{G['turquoiseDeep']}"/>
  </linearGradient>
  <radialGradient id="k-glow" cx="50%" cy="46%" r="62%">
    <stop offset="0" stop-color="{C['heritageGold']}" stop-opacity=".20"/>
    <stop offset="1" stop-color="{C['heritageGold']}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="k-pattern" width="80" height="80" patternUnits="userSpaceOnUse">
    <g fill="none" stroke="{C['heritageGold']}" stroke-width="1.2">
      <rect x="20" y="20" width="40" height="40"/>
      <rect x="20" y="20" width="40" height="40" transform="rotate(45 40 40)"/>
      <path d="M0 0 L20 20 M80 0 L60 20 M0 80 L20 60 M80 80 L60 60"/>
    </g>
  </pattern>"""
        return dict(defs=defs, disc="url(#k-disc)", gold="url(#k-gold)", ivory="url(#k-ivory)",
                    turq="url(#k-turq)", ring="url(#k-ring)", glow="url(#k-glow)", pattern=True)
    if style == "mono-ivory":
        v = C["warmIvory"]
        return dict(defs="", disc=None, gold=v, ivory=v, turq=v, ring=v, glow=None, pattern=False)
    if style == "mono-dark":
        v = C["primaryBackground"]
        return dict(defs="", disc=None, gold=v, ivory=v, turq=v, ring=v, glow=None, pattern=False)
    raise ValueError(style)


def emblem_svg(variant, style, disc=True, square_bg=False, title=""):
    g, p = geometry(variant), paint(style)
    el = []
    if square_bg:
        el.append(f'<rect id="background" width="1000" height="1000" fill="{C["primaryBackground"]}"/>')
    if disc and p["disc"]:
        el.append(f'<path id="disc" fill="{p["disc"]}" d="{g["disc"]}"/>')
        if p["pattern"]:
            el.append(f'<clipPath id="k-clip"><circle cx="{CX}" cy="{CY}" r="{g["R"] - 40}"/></clipPath>')
            el.append('<g id="pattern" clip-path="url(#k-clip)" opacity=".07"><rect width="1000" height="1000" fill="url(#k-pattern)"/></g>')
    el.append(f'<path id="ring" fill="{p["ring"]}" fill-rule="evenodd" d="{g["ring"]}"/>')
    if g["dots"]:
        el.append(f'<path id="ring-dots" fill="{p["gold"]}" opacity=".8" d="{g["dots"]}"/>')
    if p["glow"]:
        el.append(f'<path id="opening-glow" fill="{p["glow"]}" d="{g["opening"]}"/>')
    el.append(f'<g id="arch" fill="{p["gold"]}">' + "".join(f'<path d="{d}"/>' for d in g["arch"]) + "</g>")
    el.append(f'<path id="threshold" fill="{p["gold"]}" d="{g["threshold"]}"/>')
    el.append(f'<g id="wordmark"><path id="word" fill="{p["ivory"]}" d="{g["word_body"]}"/>'
              f'<path id="kha-dot" fill="{p["ivory"]}" d="{g["kha_dot"]}"/>'
              f'<g id="turquoise-diamonds" fill="{p["turq"]}">' + "".join(f'<path d="{d}"/>' for d in g["turq"]) + "</g></g>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">\n'
            f"<title>{title}</title>\n" + (f"<defs>{p['defs']}\n</defs>\n" if p["defs"] else "") +
            "\n".join(el) + "\n</svg>\n"), g["meta"]


def wordmark_svg(style="flat", with_latin=False, bg=False):
    w = wordmark()
    p = paint(style)
    minx, miny, maxx, maxy = bounds([w["body"], w["kha_dot"], *w["turq"]])
    s, pad = 6.0, 14.0
    Wd = (maxx - minx) * s
    lat, lat_w = latin_word()
    lat_s = (Wd * 0.62) / lat_w
    lat_h = LH * lat_s
    gap = 60.0
    H = (maxy - miny) * s + (gap + lat_h if with_latin else 0)
    W = Wd

    def tw(x, y):
        return (x - minx) * s + pad * s, (y - miny) * s + pad * s

    def tl(x, y):
        return (W - lat_w * lat_s) / 2 + x * lat_s + pad * s, (maxy - miny) * s + gap + lat_h + y * lat_s + pad * s

    VW, VH = W + 2 * pad * s, H + 2 * pad * s
    el = []
    if bg:
        el.append(f'<rect width="100%" height="100%" fill="{C["primaryBackground"]}"/>')
    el.append(f'<path id="word" fill="{p["ivory"]}" d="{poly_d(w["body"], tw)}"/>')
    el.append(f'<path id="kha-dot" fill="{p["ivory"]}" d="{poly_d(w["kha_dot"], tw)}"/>')
    el.append(f'<g id="turquoise-diamonds" fill="{p["turq"]}">' + "".join(f'<path d="{poly_d(t, tw)}"/>' for t in w["turq"]) + "</g>")
    if with_latin:
        el.append(f'<path id="latin" fill="{p["gold"]}" d="{poly_d(lat, tl)}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW:.0f} {VH:.0f}" width="{VW:.0f}" height="{VH:.0f}">\n'
            f'<title>KHAYBAR wordmark</title>\n' + (f"<defs>{p['defs']}\n</defs>\n" if p["defs"] else "") +
            "\n".join(el) + "\n</svg>\n")


def horizontal_svg(style="flat"):
    """Emblem (right, RTL lead) + divider + Arabic wordmark over Latin KHAYBAR."""
    g, p = geometry("avatar"), paint(style)
    w = wordmark()
    minx, miny, maxx, maxy = bounds([w["body"], w["kha_dot"], *w["turq"]])
    H = 1000.0
    em_x = 1900.0                       # emblem occupies x 1900..2900
    word_w = 980.0
    s = word_w / (maxx - minx)
    word_h = (maxy - miny) * s
    lat, lat_w = latin_word()
    ls = (word_w * 0.56) / lat_w
    lat_h = LH * ls
    block_h = word_h + 70 + lat_h
    top = (H - block_h) / 2
    right = em_x - 170
    ox = right - word_w - minx * s

    def tw(x, y):
        return ox + x * s, top + (y - miny) * s

    lat_x0 = right - lat_w * ls

    def tl(x, y):
        return lat_x0 + x * ls, top + word_h + 70 + lat_h + y * ls

    el = [f'<g id="emblem" transform="translate({em_x} 0)">',
          f'<path fill="{p["disc"] or C["primaryBackground"]}" d="{g["disc"]}"/>' if p["disc"] else "",
          f'<path fill="{p["ring"]}" fill-rule="evenodd" d="{g["ring"]}"/>',
          f'<path fill="{p["glow"]}" d="{g["opening"]}"/>' if p["glow"] else "",
          f'<g fill="{p["gold"]}">' + "".join(f'<path d="{d}"/>' for d in g["arch"]) + f'<path d="{g["threshold"]}"/></g>',
          f'<path fill="{p["ivory"]}" d="{g["word_body"]} {g["kha_dot"]}"/>',
          f'<g fill="{p["turq"]}">' + "".join(f'<path d="{d}"/>' for d in g["turq"]) + "</g>",
          "</g>",
          f'<rect id="divider" x="{em_x - 87}" y="250" width="4" height="500" fill="{p["gold"] if style != "cinematic" else C["heritageGold"]}" opacity=".7"/>',
          f'<path id="word" fill="{p["ivory"]}" d="{poly_d(w["body"], tw)} {poly_d(w["kha_dot"], tw)}"/>',
          f'<g id="turquoise-diamonds" fill="{p["turq"]}">' + "".join(f'<path d="{poly_d(t, tw)}"/>' for t in w["turq"]) + "</g>",
          f'<path id="latin" fill="{p["gold"]}" d="{poly_d(lat, tl)}"/>']
    vb_x = min(ox + minx * s, lat_x0) - 60
    VW = 2900 - vb_x
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x:.0f} 0 {VW:.0f} 1000" width="{VW:.0f}" height="1000">\n'
            f'<title>KHAYBAR horizontal lockup</title>\n' + (f"<defs>{p['defs']}\n</defs>\n" if p["defs"] else "") +
            "\n".join(e for e in el if e) + "\n</svg>\n")


# ===========================================================================
# 6. BUILD
# ===========================================================================
FILES = {
    "official/khaybar-logo-flat.svg": lambda: emblem_svg("full", "flat", title="KHAYBAR — Official logo, Flat Official Gold"),
    "official/khaybar-logo-cinematic.svg": lambda: emblem_svg("full", "cinematic", title="KHAYBAR — Official logo, Cinematic Metallic Gold"),
    "avatar/khaybar-avatar.svg": lambda: emblem_svg("avatar", "flat", square_bg=True, title="KHAYBAR — Profile avatar"),
    "small/khaybar-logo-small.svg": lambda: emblem_svg("small", "flat", title="KHAYBAR — Small sizes (≤ 64px)"),
    "mono/khaybar-logo-mono-ivory.svg": lambda: emblem_svg("full", "mono-ivory", disc=False, title="KHAYBAR — Mono ivory"),
    "mono/khaybar-logo-mono-dark.svg": lambda: emblem_svg("full", "mono-dark", disc=False, title="KHAYBAR — Mono dark"),
    "mark/khaybar-mark-on-image.svg": lambda: emblem_svg("avatar", "flat", disc=True, title="KHAYBAR — Emblem for complex backgrounds"),
}

if __name__ == "__main__":
    meta = {}
    for rel, fn in FILES.items():
        path = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        svg, m = fn()
        open(path, "w", encoding="utf-8").write(svg)
        meta[rel] = m
    os.makedirs(os.path.join(OUT, "wordmark"), exist_ok=True)
    open(os.path.join(OUT, "wordmark", "khaybar-wordmark.svg"), "w").write(wordmark_svg())
    open(os.path.join(OUT, "wordmark", "khaybar-wordmark-latin.svg"), "w").write(wordmark_svg(with_latin=True))
    open(os.path.join(OUT, "wordmark", "khaybar-wordmark-cinematic.svg"), "w").write(wordmark_svg("cinematic"))
    os.makedirs(os.path.join(OUT, "horizontal"), exist_ok=True)
    open(os.path.join(OUT, "horizontal", "khaybar-horizontal.svg"), "w").write(horizontal_svg("flat"))
    open(os.path.join(OUT, "horizontal", "khaybar-horizontal-cinematic.svg"), "w").write(horizontal_svg("cinematic"))
    meta["wordmark_grid"] = wordmark()["grid"]
    json.dump(meta, open(os.path.join(OUT, "logo-geometry.json"), "w"), indent=2)
    print(json.dumps(meta, indent=1))
