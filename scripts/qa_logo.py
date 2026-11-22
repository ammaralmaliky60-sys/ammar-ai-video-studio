#!/usr/bin/env python3
"""QA for the final logo: SVG validity, vector-only, flat/cinematic geometric identity, contrast."""
import glob, json, os, re, sys
import xml.etree.ElementTree as ET
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = "{http://www.w3.org/2000/svg}"
fails, report = [], {}

for f in sorted(glob.glob(os.path.join(ROOT, "brand/logo/*/*.svg"))):
    if "/archive/" in f:
        continue
    rel = os.path.relpath(f, ROOT)
    txt = open(f, encoding="utf-8").read()
    try:
        root = ET.fromstring(txt)
    except ET.ParseError as e:
        fails.append(f"{rel}: XML parse error {e}"); continue
    bad = [t for t in ("image", "text", "foreignObject", "script") if list(root.iter(NS + t))]
    if bad: fails.append(f"{rel}: contains non-vector/unsafe elements {bad}")
    if re.search(r"nan|inf", " ".join(p.get("d", "") for p in root.iter(NS + "path")), re.I):
        fails.append(f"{rel}: NaN/inf in path data")
    if "data:" in txt: fails.append(f"{rel}: embedded data URI")
    report[rel] = dict(paths=len(list(root.iter(NS + "path"))), bytes=len(txt.encode()))

def geo(path):
    r = ET.parse(os.path.join(ROOT, path)).getroot()
    shapes = [p for p in r.iter(NS + "path") if p.get("id") not in ("opening-glow", "disc")]
    in_defs = {id(p) for d in r.iter(NS + "defs") for p in d.iter(NS + "path")}
    return sorted(p.get("d") for p in shapes if id(p) not in in_defs)
same = geo("brand/logo/official/khaybar-logo-flat.svg") == geo("brand/logo/official/khaybar-logo-cinematic.svg")
if not same: fails.append("flat and cinematic geometry differ")

def lum(h):
    c = [int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def cr(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True); return round((x + .05) / (y + .05), 2)
contrast = {f"{a} on #071F26": cr(a, "#071F26") for a in ("#D4AA61", "#F4E9D3", "#2DB9B6")}
contrast["#F4E9D3 word vs #D4AA61 arch"] = cr("#F4E9D3", "#D4AA61")

out = dict(files=report, flat_cinematic_identical=same, contrast=contrast, failures=fails)
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open(os.path.join(ROOT, "docs", "logo-qa-report.json"), "w"), indent=1, ensure_ascii=False)
sys.exit(1 if fails else 0)
