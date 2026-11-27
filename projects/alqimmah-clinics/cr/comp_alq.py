#!/usr/bin/env python3
"""Cinematic Reality compositor for the Alqimmah clip (room kept as the world, no matte).
Room plate (graded) + 3D overlay strips (with soft wall shadow) under a virtual camera, then the v2 motion-graphics
layer: kinetic captions, chapter markers, lower third, end card, bloom/anamorphic streaks, S-curve, vignette, grain.
Usage: comp_alq.py OUT.mp4 | comp_alq.py --stills DIR f1,f2,...
"""
import json, math, os, subprocess, sys, time
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../../studio/cinematic-reality/engine')))
import mg

W, H = 1080, 1920
TL = json.load(open(HERE + '/timeline.json'))
FPS, NF, STRIP_H = TL['fps'], TL['nf'], TL['strip_h']
STRIP_Y = -30                      # strip placement (top of the 3D band in frame px)
FACE = (540.0, 650.0)              # camera anchor (face)
BG_DIR = PROJ + '/build/bg'
ACCENT = np.array([0xE2, 0x17, 0x8D], np.float32)/255.0

# ---------------------------------------------------------------- captions (exact word cues)
words = json.load(open(PROJ + '/analysis/02-transcript.json'))['words']
caps, k = [], 0
for c in TL['captions']:
    n = len(c['text'].split(' '))
    caps.append(dict(c, ws=[words[k + i]['start'] for i in range(n)])); k += n
caps[0]['s'] = 0.0; caps[0]['ws'][0] = 0.0
for a in TL['accents']: mg.ACC[a] = 'brand'
CAPS = mg.Captions(caps, y=1050)

# ---------------------------------------------------------------- chapter markers (moved below the platform top UI)
class Chap(mg.Chapters):
    def __init__(self, spec, total):
        self.items = [dict(t=s['t'], num=mg._text_img(s['num'], mg.F_BOLD, 74), tot=mg._text_img('/ ' + total, mg.F_LIGHT, 38, (225, 225, 230)),
                           lab=mg._text_img(s['lab'], mg.F_SEMI, 46, (245, 245, 245))) for s in spec]
CHAP = Chap(TL['chapters'], '٠' + str(len(TL['chapters'])).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')))
CHAP_DY = 150                      # skill default y=92 sits under Instagram/TikTok top UI


def draw_chapters(frame, t, xr=372, y=560):
    """Chapter marker on the plain wall left of the speaker (skill layout, relocated out of the 3D band/UI)."""
    for it in CHAP.items:
        lt = t - it['t']
        if not (0 <= lt < 2.6): continue
        ko = 1.0 - mg.ease((lt - 2.25)/0.35)
        ln = int(190*mg.eout(lt/0.35))
        frame[y+86:y+90, xr-ln:xr] = frame[y+86:y+90, xr-ln:xr]*(1 - 0.92*ko) + 0.92*ko
        if ln > 4: cv2.circle(frame, (xr - ln, y + 88), 7, (1.0, 1.0, 1.0), -1, lineType=cv2.LINE_AA)
        for key, dy, t0 in (('num', 0, 0.08), ('tot', 28, 0.16), ('lab', 104, 0.22)):
            rgb, a = it[key]; k = mg.eout((lt - t0)/0.3)
            if k <= 0: continue
            h, w = a.shape
            x0 = xr - it['num'][1].shape[1] - w + 26 if key == 'tot' else xr - w + 24
            aa = a.copy(); cut = int((1 - k)*h)
            if cut > 0: aa[:cut] = 0
            mg.Captions._blit(frame, rgb, aa*k*ko, x0, int(y + dy - 24 + (1 - k)*18))
    return frame


# ---------------------------------------------------------------- camera
def camera_scale(t):
    cuts = TL['cuts']; alt = [1.00, 1.08, 1.00, 1.07, 1.00, 1.06, 1.00, 1.05]
    seg = max(i for i, c in enumerate(cuts) if t >= c)
    last = max(w for w in TL['worlds'] if t >= w)
    push = 1.0 + 0.03*mg.ease((t - last)/6.0)
    p = 0.0
    for tk, s in TL['punches']:
        x = t - tk
        if -0.02 < x < 1.6:
            p += s*(mg.eout(x/0.14) if x < 0.14 else math.exp(-(x - 0.14)/0.45))
    return alt[seg % len(alt)]*push*(1.0 + 0.035*p)


# ---------------------------------------------------------------- overlays
def layer_alpha(name, f):
    for n, a, b, fi, fo in TL['layers']:
        if n == name and a <= f <= b:
            k = 1.0
            if fo and f > b - fo: k = 1 - mg.ease((f - (b - fo))/fo)
            return k
    return 0.0


def load_overlay(f):
    """premultiplied rgb + alpha of all 3D layers active at frame f, in frame space (pre-camera)."""
    rgb = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32)
    for n, a, b, fi, fo in TL['layers']:
        k = layer_alpha(n, f)
        p = f'{HERE}/renders/{n}/{f:05d}.png'
        if k <= 0 or not os.path.exists(p): continue
        im = np.asarray(Image.open(p).convert('RGBA')).astype(np.float32)/255.0
        y0 = STRIP_Y; ys, ye = max(0, y0), min(H, y0 + STRIP_H)
        part = im[ys - y0:ye - y0]
        a_ = part[..., 3]*k; c_ = part[..., :3]*a_[..., None]
        rgb[ys:ye] = c_ + rgb[ys:ye]*(1 - a_[..., None]); al[ys:ye] = a_ + al[ys:ye]*(1 - a_)
    return rgb, al


# ---------------------------------------------------------------- lower third + end card
LT = TL['lower_third']
LT_NAME = mg._text_img(LT['name'], mg.F_BOLD, 66)
LT_TITLE = mg._text_img(LT['title'], mg.F_SEMI, 42, (248, 214, 236))
LOGO = np.asarray(Image.open(PROJ + '/brand/alqimmah-logo-full.png').convert('RGBA')).astype(np.float32)/255.0


def draw_lower_third(frame, f):
    a, b = LT['f0'], LT['f1']
    if not (a <= f <= b): return frame
    lt = (f - a)/FPS; ko = 1.0 - mg.ease((f - (b - 9))/9)
    xr, y = 960, 300
    ln = int(330*mg.eout(lt/0.4))
    if ln > 0:
        frame[y + 92:y + 98, xr - ln:xr] = frame[y + 92:y + 98, xr - ln:xr]*(1 - 0.95*ko) + ACCENT*0.95*ko
        cv2.circle(frame, (xr - ln, y + 95), 8, tuple(float(c) for c in ACCENT), -1, lineType=cv2.LINE_AA)
    for (rgb, al), dy, t0 in ((LT_NAME, 0, 0.10), (LT_TITLE, 108, 0.26)):
        k = mg.eout((lt - t0)/0.3)
        if k <= 0: continue
        h, w = al.shape; aa = al.copy(); cut = int((1 - k)*h)
        if cut > 0: aa[:cut] = 0
        mg.Captions._blit(frame, rgb, aa*k*ko, xr - w + 24, int(y + dy - 20 + (1 - k)*18))
    return frame


def draw_end_card(frame, f):
    f0 = TL['end_card']['f0']
    if f < f0 - 4: return frame
    lt = (f - f0 + 4)/FPS
    k = mg.eout(lt/0.5)
    # soft dark field behind the logo (logo artwork is designed on black)
    cy = 380
    if not hasattr(draw_end_card, 'grad'):
        yy = np.arange(H, dtype=np.float32)
        g = np.clip(1.0 - (yy - 520)/180, 0, 1)**1.6          # full-width cinematic top gradient
        draw_end_card.grad = g[:, None, None]
    tint = np.array([0.055, 0.02, 0.07], np.float32)
    frame[:] = frame*(1 - 0.86*k*draw_end_card.grad) + tint*0.86*k*draw_end_card.grad
    hgt = int(330*(0.92 + 0.08*k)); wdt = int(LOGO.shape[1]*hgt/LOGO.shape[0])
    lg = cv2.resize(LOGO, (wdt, hgt), interpolation=cv2.INTER_AREA)
    mg.Captions._blit(frame, lg[..., :3], lg[..., 3]*k, 540 - wdt//2, cy - hgt//2 + int((1 - k)*20))
    return frame


# ---------------------------------------------------------------- frame
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 1, (H//2, W//2)).astype(np.float32) for _ in range(8)]
r2 = ((mg.XX - W/2)/(W*0.75))**2 + ((mg.YY - H/2)/(H*0.75))**2
VIG = (1 - 0.2*np.clip(r2, 0, 1.5))[..., None].astype(np.float32)


def compose(f):
    t = f/FPS
    room = np.asarray(Image.open(f'{BG_DIR}/{f + 1:04d}.jpg').convert('RGB')).astype(np.float32)/255.0
    room = np.clip((room - 0.5)*1.08 + 0.5, 0, 1)*np.array([1.02, 1.0, 0.97], np.float32)
    orgb, oal = load_overlay(f)
    if oal.max() > 0:
        # soft curtain shadow of the floating 3D object on the wall
        sh = cv2.GaussianBlur(oal, (0, 0), 14)
        sh = np.roll(np.roll(sh, 14, axis=0), 26, axis=1)*0.38
        room = room*(1 - sh[..., None])
        room = orgb + room*(1 - oal[..., None])
    s = camera_scale(t)
    M = mg.affine_scale(s, FACE[0], FACE[1])
    out = cv2.warpAffine(room, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    out = draw_end_card(out, f)
    out = mg.optics(np.clip(out, 0, 1.4), 'room')
    out = np.clip(out, 0, 1)
    out = draw_chapters(out, t)
    out = draw_lower_third(out, f)
    if f < TL['end_card']['f0'] + 200:
        out = CAPS.draw(out, t)
    out = np.clip(out, 0, 1)
    out = out + 0.06*(out - out*out)*np.where(out > 0.5, 1, -1)
    out = out*VIG
    out = mg.chroma_edges(out)
    g = cv2.resize(GRAIN[f % len(GRAIN)], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    lum = out.mean(2, keepdims=True)
    out = out + g*0.017*(0.4 + 0.6*np.sqrt(np.clip(lum*(1 - lum)*4, 0, 1)))
    return (np.clip(out, 0, 1)*255 + 0.5).astype(np.uint8)


def main():
    if sys.argv[1] == '--stills':
        d = sys.argv[2]; os.makedirs(d, exist_ok=True)
        for f in [int(x) for x in sys.argv[3].split(',')]:
            Image.fromarray(compose(f)).save(f'{d}/c_{f:05d}.png'); print('still', f, flush=True)
        return
    out = sys.argv[1]
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(NF):
        enc.stdin.write(compose(f).tobytes())
        if f % 30 == 0: print(f'comp {f}/{NF} {(time.time() - t0)/(f + 1):.2f}s/f', flush=True)
    enc.stdin.close(); enc.wait(); print('done', out)


if __name__ == '__main__':
    main()
