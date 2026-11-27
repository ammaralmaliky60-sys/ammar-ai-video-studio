#!/usr/bin/env python3
"""Render text (Arabic-aware, RTL via raqm) to a signed distance field .npy for the 3D text object.
Usage: make_sdf.py "TEXT" FONT.ttf OUT.npy [--w 2048] [--h 640] [--box 6.0] [--range 0.5] [--lang ar] [--size 0]
Prints JSON with box size (world) for the shader (uTxtBox.xy, z=range).
"""
import argparse, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt

ap = argparse.ArgumentParser()
ap.add_argument('text'); ap.add_argument('font'); ap.add_argument('out')
ap.add_argument('--w', type=int, default=2048); ap.add_argument('--h', type=int, default=640)
ap.add_argument('--box', type=float, default=6.0, help='world width of the texture rect')
ap.add_argument('--range', type=float, default=0.5, help='world range of the encoded distance')
ap.add_argument('--lang', default='ar'); ap.add_argument('--fill', type=float, default=0.86)
ap.add_argument('--tracking', type=int, default=0)
ap.add_argument('--hfill', type=float, default=0.72)
a = ap.parse_args()

W, H = a.w, a.h
# fit text to fill% of width or 70% height
lo, hi = 20, 2000
kw = dict(direction='rtl', language=a.lang) if a.lang == 'ar' else {}
for _ in range(20):
    mid = (lo + hi) // 2
    f = ImageFont.truetype(a.font, mid, layout_engine=ImageFont.Layout.RAQM)
    bb = ImageDraw.Draw(Image.new('L',(8,8))).multiline_textbbox((0,0), a.text, font=f, align='center', spacing=int(mid*0.08), **kw)
    if (bb[2]-bb[0]) <= W*a.fill and (bb[3]-bb[1]) <= H*a.hfill:
        lo = mid
    else:
        hi = mid
f = ImageFont.truetype(a.font, lo, layout_engine=ImageFont.Layout.RAQM)
bb = ImageDraw.Draw(Image.new('L',(8,8))).multiline_textbbox((0,0), a.text, font=f, align='center', spacing=int(lo*0.08), **kw)
img = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(img)
x = (W - (bb[2]-bb[0]))/2 - bb[0]; y = (H - (bb[3]-bb[1]))/2 - bb[1]
d.multiline_text((x, y), a.text, font=f, fill=255, align='center', spacing=int(lo*0.08), **kw)
m = np.asarray(img).astype(np.float32)/255.0
inside = m > 0.5
din = distance_transform_edt(inside); dout = distance_transform_edt(~inside)
sd_px = dout - din  # negative inside
# sub-pixel edge refinement from antialias coverage
sd_px = sd_px - (m - 0.5)*np.where(np.abs(sd_px) <= 1.5, 1.0, 0.0)
px = a.box / W
from scipy.ndimage import gaussian_filter
sd_px = gaussian_filter(sd_px, 1.6)
sd_w = sd_px*px
enc = np.clip(0.5 + sd_w/a.range, 0.0, 1.0).astype(np.float32)
np.save(a.out, enc)
Image.fromarray((m*255).astype(np.uint8)).save(a.out.replace('.npy', '_mask.png'))
print(json.dumps({'box': [a.box, a.box*H/W], 'range': a.range, 'font_px': lo}))
