#!/usr/bin/env python3
"""Final compositor: 3D backgrounds + tracked camera shake + relit speaker + title + captions + grain.
Usage: comp.py OUT.mp4            (full render, video only; audio muxed by mux step)
       comp.py --stills DIR f1,f2 (write selected output frames as PNG)
"""
import json, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = os.environ.get('CR_WORK', os.path.dirname(os.path.abspath(__file__)))          # work dir: timeline.json, renders/, job_*.json
SRC = os.environ.get('CR_SRC', R + '/src/raw.mp4')        # 30 fps 1080x1920 ingest of the selfie
FG = os.environ.get('CR_FG', R + '/src/raw_fg.webm')       # RVM matte (VP9 + alpha) of the same clip
_FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts')
W, H = 1080, 1920
TL = json.load(open(f'{R}/timeline.json'))
FPS = TL['fps']; NF = TL['nf']
TRK = json.load(open(f'{R}/track.json'))['frames']
OVERLAYS = []   # 3D layers rendered over the real room (title, Iranian flag): (name, {frame: fade}, shadow offset, shadow strength)
for _n, _off, _st in (('title', (26, 14), 0.38), ('flagroom', (24, 18), 0.30)):
    _j = json.load(open(f'{R}/job_{_n}.json'))
    OVERLAYS.append((_n, {int(fr['name'][:5]): fr['alpha_fade'] for fr in _j['frames']}, _off, _st))
TITLE_FADE = OVERLAYS[0][1]


def room_overlays(plate, f):
    for name, fades, (oy, ox), st in OVERLAYS:
        if f not in fades or fades[f] <= 0.0: continue
        tp = f'{R}/renders/{name}/{f:05d}.png'
        if not os.path.exists(tp): continue
        ti = cv2.imread(tp, cv2.IMREAD_UNCHANGED).astype(np.float32)/255.0
        ti = ti[..., [2, 1, 0, 3]]; ta = ti[..., 3:4]*fades[f]
        shd = cv2.GaussianBlur(ta[..., 0], (0, 0), 16)
        shd = np.roll(np.roll(shd, oy, axis=0), ox, axis=1)[..., None]
        plate = plate*(1 - st*shd)
        plate = plate*(1 - ta) + ti[..., :3]*ta
    return plate
FONT_REG = _FONTS + '/IBMPlexSansArabic-SemiBold.ttf'
FONT_BOLD = _FONTS + '/IBMPlexSansArabic-Bold.ttf'

# ---------------------------------------------------------------- timeline helpers
EDL = TL['edl']


def src_index(f):
    if f < 6:
        return 12          # hold an open-eyed frame for the first 0.2 s (silence; thumbnail)
    for e in EDL:
        if e['out0'] <= f < e['out0'] + (e['src1'] - e['src0']):
            return e['src0'] + (f - e['out0'])
    e = EDL[-1]; return e['src1'] - 1


ORDER = ['room', 'black', 'mountain', 'sea', 'flag', 'studio']
TR = {tr['a']: tr for tr in TL['trans']}


def ease(x):
    x = min(max(x, 0.0), 1.0); return x*x*(3-2*x)


def scene_state(t):
    """returns (sceneA, sceneB, p, trans) ; p=0 -> fully A"""
    cur = 'room'
    for s in ORDER[1:]:
        prev = ORDER[ORDER.index(s)-1]
        if t >= TR[prev]['t']:
            cur = s
    prev_i = ORDER.index(cur) - 1
    # in transition out of previous?
    if prev_i >= 0:
        tr = TR[ORDER[prev_i]]
        if tr['t'] <= t < tr['t'] + tr['dur']:
            return tr['a'], tr['b'], (t - tr['t'])/tr['dur'], tr
    return cur, None, 0.0, None


# ---------------------------------------------------------------- camera shake from tracking
trk = np.array([[d['dx'], d['dy'], d['rot'], d['scale']] for d in TRK])
# robustify: clip per-frame jumps (tracker glitches on the low-texture curtain), re-integrate, light smoothing
_d = np.diff(trk, axis=0)
_d[:, 0] = np.clip(_d[:, 0], -9, 9); _d[:, 1] = np.clip(_d[:, 1], -9, 9); _d[:, 2] = np.clip(_d[:, 2], -0.005, 0.005)
_d[:, 3] = np.clip(_d[:, 3], -0.004, 0.004)
trk = np.vstack([trk[:1], trk[:1] + np.cumsum(_d, axis=0)])
from scipy.ndimage import gaussian_filter1d
trk = gaussian_filter1d(trk, 1.5, axis=0)
ref = np.median(trk, axis=0)


def shake_matrix(si, overscan=1.07):
    dx, dy, rot, sc = trk[min(si, len(trk)-1)] - np.array([ref[0], ref[1], ref[2], 0.0])
    dx = float(np.clip(dx*0.8, -45, 45)); dy = float(np.clip(dy*0.8, -55, 55)); rot = float(np.clip(rot*0.8, -0.025, 0.025))
    s = overscan*float(np.clip(sc/ref[3], 0.97, 1.03))
    c, sn = math.cos(rot)*s, math.sin(rot)*s
    cx, cy = W/2, H/2
    return np.array([[c, -sn, cx - c*cx + sn*cy + dx], [sn, c, cy - sn*cx - c*cy + dy]], np.float32)


# ---------------------------------------------------------------- readers (monotonic)
class Reader:
    def __init__(self, cmd, shape):
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)
        self.shape = shape; self.n = int(np.prod(shape)); self.idx = -1; self.cur = None

    def get(self, i):
        while self.idx < i:
            b = self.p.stdout.read(self.n)
            if len(b) < self.n:
                return self.cur
            self.cur = np.frombuffer(b, np.uint8).reshape(self.shape); self.idx += 1
        return self.cur


def readers():
    rs = Reader(['ffmpeg', '-v', 'error', '-i', SRC, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], (H, W, 3))
    rf = Reader(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-i', FG, '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], (H, W, 4))
    return rs, rf


_cache = {}


def load_bg(scene, f):
    key = (scene, f)
    if key in _cache: return _cache[key]
    path = f'{R}/renders/{scene}/{f:05d}.png'
    if not os.path.exists(path):
        # nearest available frame
        d = f'{R}/renders/{scene}'
        av = sorted(int(x[:5]) for x in os.listdir(d)) if os.path.isdir(d) else []
        if not av: return np.zeros((H, W, 3), np.float32)
        path = f'{d}/{min(av, key=lambda a: abs(a-f)):05d}.png'
    im = cv2.cvtColor(cv2.imread(path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
    if len(_cache) > 8: _cache.clear()
    _cache[key] = im
    return im


# ---------------------------------------------------------------- captions
def make_caption(text, color, accent):
    size = 88 if accent else 72
    font = ImageFont.truetype(FONT_BOLD if accent else FONT_REG, size, layout_engine=ImageFont.Layout.RAQM)
    kw = dict(direction='rtl', language='ar')
    bb = font.getbbox(text, **kw)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    pad = 40
    img = Image.new('RGBA', (tw + 2*pad, th + 2*pad + 20), (0, 0, 0, 0))
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pad - bb[0], pad - bb[1] + 4), text, font=font, fill=(0, 0, 0, 170), **kw)
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    d = ImageDraw.Draw(img)
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    d.text((pad - bb[0], pad - bb[1]), text, font=font, fill=rgb + (255,), **kw)
    out = Image.alpha_composite(sh, img)
    return np.asarray(out).astype(np.float32)/255.0


CAPS = []
TL['captions'][0]['s'] = 0.0
for c in TL['captions']:
    CAPS.append(dict(c, img=make_caption(c['text'], c['color'], c['accent'])))
CAP_Y = 1560


def draw_captions(frame, t):
    for c in CAPS:
        if not (c['s'] - 0.02 <= t < c['e']): continue
        k_in = 1.0 if c['s'] <= 0.0 else ease((t - c['s'])/0.10); k_out = 1.0 - ease((t - (c['e'] - 0.07))/0.07)
        a = k_in*k_out
        if a <= 0.01: continue
        im = c['img']
        blur = (1 - k_in)*6
        if blur > 0.3:
            im = cv2.GaussianBlur(im, (0, 0), blur)
        h, w = im.shape[:2]
        x0 = W//2 - w//2; y0 = int(CAP_Y - h/2 + (1 - k_in)*14)
        xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w), min(H, y0 + h)
        sub = im[ya - y0:yb - y0, xa - x0:xb - x0]
        al = sub[..., 3:4]*a
        frame[ya:yb, xa:xb] = frame[ya:yb, xa:xb]*(1 - al) + sub[..., :3]*al
    return frame


# ---------------------------------------------------------------- person relighting
def lerp_params(pa, pb, k):
    out = {}
    for key in pa:
        va, vb = pa[key], pb[key]
        if isinstance(va, list): out[key] = [va[i]*(1-k) + vb[i]*k for i in range(len(va))]
        else: out[key] = va*(1-k) + vb*k
    return out


def relight(rgb, a, P, bg):
    """rgb, bg float [0,1] HxWx3 ; a HxW alpha. returns relit rgb"""
    c = rgb*P['exp']*np.array(P['temp'], np.float32)
    c = (c - 0.45)*P['contrast'] + 0.45 + P['lift']
    l = (c*np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(2, keepdims=True)
    c = np.clip(l + (c - l)*P['sat'], 0, 1.5)
    # edge geometry (computed at half res for speed)
    small = cv2.resize(a, (W//2, H//2), interpolation=cv2.INTER_AREA)
    bl = cv2.GaussianBlur(small, (0, 0), 5)
    gx = cv2.Sobel(bl, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(bl, cv2.CV_32F, 0, 1, ksize=3)
    gn = np.sqrt(gx*gx + gy*gy) + 1e-6
    nx, ny = -gx/gn, -gy/gn                       # outward normal (screen)
    band = np.clip(small*(1.0 - bl)*3.0, 0, 1)
    if max(P['rim']) > 0:
        L = np.array(P['rimDir'], np.float32); L /= np.linalg.norm(L) + 1e-6
        wdir = np.clip(nx*L[0] + ny*L[1], 0, 1)**1.3
        rim = cv2.resize(band*wdir, (W, H))[..., None]
        c = c + rim*np.array(P['rim'], np.float32)*0.55*(0.35 + 0.65*c.mean(2, keepdims=True)**0.5)
    if P['wrap'] > 0:
        bgs = cv2.resize(cv2.GaussianBlur(cv2.resize(bg, (W//4, H//4)), (0, 0), 6), (W, H))
        wrap = cv2.resize(np.clip(small*(1.0 - cv2.GaussianBlur(small, (0, 0), 9))*2.2, 0, 1), (W, H))[..., None]*P['wrap']
        c = c*(1 - wrap*0.6) + bgs*wrap*0.6 + bgs*wrap*0.25
    if P.get('fall', 0) > 0:
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        c = c*(1 - P['fall']*np.clip((y - 0.35)/0.65, 0, 1))
    return np.nan_to_num(np.clip(c, 0, 1.2))


def shift_layer(img, dy):
    if abs(dy) < 0.5: return img
    M = np.float32([[1, 0, 0], [0, 1, dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def motion_blur(img, length, horizontal):
    L = int(length)
    if L < 3: return img
    k = np.zeros((L, L), np.float32)
    if horizontal: k[L//2, :] = 1.0/L
    else: k[:, L//2] = 1.0/L
    return cv2.filter2D(img, -1, k)


# ---------------------------------------------------------------- frame
rng = np.random.default_rng(3)
GRAIN = [rng.normal(0, 1, (H//2, W//2)).astype(np.float32) for _ in range(8)]
PERSON = TL['person']
for k in PERSON: PERSON[k].setdefault('fall', 0.0)
PERSON['black']['fall'] = 0.45
PERSON['black']['rim'] = [2.2, 2.0, 1.75]; PERSON['black']['exp'] = 0.68


def scene_bg(scene, f, si, room_rgb):
    if scene == 'room':
        return room_rgb
    bg = load_bg(scene, f)
    return cv2.warpAffine(bg, shake_matrix(si), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def compose(f, room_rgb, fg):
    t = f/FPS
    si = src_index(f)
    A, B, p, tr = scene_state(t)
    alpha = fg[..., 3].astype(np.float32)/255.0
    prgb = fg[..., :3].astype(np.float32)/255.0
    room = room_rgb.astype(np.float32)/255.0
    # room grade (cinematic): gentle contrast, warm mids, cooler shadows
    room_g = np.clip((room - 0.5)*1.08 + 0.5, 0, 1)*np.array([1.02, 1.0, 0.97], np.float32)
    room_g = room_overlays(room_g, f)   # 3D title / flag sit in the room, behind the speaker (occlusion by the matte below)

    bgA = scene_bg(A, f, si, room_g)
    PA = PERSON[A]
    if B is None:
        bg = bgA; P = PA; dy = PA['dy']; flash = 0.0
    else:
        bgB = scene_bg(B, f, si, room_g); PB = PERSON[B]
        typ = tr['type']; e = ease(p); flash = 0.0
        if typ == 'lightsout':
            k = min(1.0, p*2.2)
            flick = 1.0 - (0.5*abs(math.sin(p*40.0)) if 0.15 < p < 0.55 else 0.0)
            roomk = (1 - k)*flick
            bg = shift_layer(bgA, PB['dy']*e)*roomk + bgB*(1 - roomk)
            P = lerp_params(PA, PB, e); dy = PB['dy']*e
        elif typ == 'sunrise':
            bg = bgA*(1 - e) + bgB*e; P = lerp_params(PA, PB, e); dy = PB['dy']
        elif typ in ('whipLeft', 'whipUp'):
            off = e; spd = 6*p*(1-p)   # derivative of smoothstep
            if typ == 'whipLeft':
                o = int(off*W)
                bg = np.zeros_like(bgA); bg[:, :W - o] = bgA[:, o:]; bg[:, W - o:] = bgB[:, :o]
                bg = motion_blur(bg, spd*W/FPS*3.0*0.5, True)
            else:
                o = int(off*H)
                bg = np.zeros_like(bgA); bg[o:, :] = bgA[:H - o, :]; bg[:o, :] = bgB[H - o:, :]
                bg = motion_blur(bg, spd*H/FPS*3.0*0.35, False)
            P = lerp_params(PA, PB, e); dy = PA['dy']*(1-e) + PB['dy']*e
        else:  # flash
            bg = bgA*(1 - e) + bgB*e
            flash = max(0.0, 1.0 - abs(2*p - 1))*0.55
            P = lerp_params(PA, PB, e); dy = PB['dy']
    # person
    if dy != 0:
        alpha_s = shift_layer(alpha, dy); prgb_s = shift_layer(prgb, dy)
    else:
        alpha_s, prgb_s = alpha, prgb
    if A == 'room' and B is None:
        lit = prgb_s
        lit = np.clip((lit - 0.5)*1.08 + 0.5, 0, 1)*np.array([1.02, 1.0, 0.97], np.float32)
    else:
        lit = relight(prgb_s, alpha_s, P, bg)
    a3 = alpha_s[..., None]
    out = bg*(1 - a3) + lit*a3
    if flash > 0:
        out = out + flash*(1.0 - out)*0.9
    # captions
    out = draw_captions(out, t)
    # global finish: filmic curve, vignette, grain
    out = np.clip(out, 0, 1)
    out = out + 0.06*(out - out*out)*np.where(out > 0.5, 1, -1)   # mild S-curve
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) if not hasattr(compose, 'vig') else (None, None)
    if not hasattr(compose, 'vig'):
        r2 = ((xx - W/2)/(W*0.75))**2 + ((yy - H/2)/(H*0.75))**2
        compose.vig = (1 - 0.18*np.clip(r2, 0, 1.5))[..., None].astype(np.float32)
    out = out*compose.vig
    g = cv2.resize(GRAIN[f % len(GRAIN)], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    lum = out.mean(2, keepdims=True)
    out = out + g*0.018*(0.4 + 0.6*np.sqrt(np.clip(lum*(1-lum)*4, 0, 1)))
    return (np.clip(out, 0, 1)*255 + 0.5).astype(np.uint8)


def main():
    if sys.argv[1] == '--stills':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        want = sorted(int(x) for x in sys.argv[3].split(','))
        rs, rf = readers()
        for f in want:
            si = src_index(f)
            img = compose(f, rs.get(si), rf.get(si))
            Image.fromarray(img).save(f'{outdir}/c_{f:05d}.png'); print('still', f, flush=True)
        return
    out = sys.argv[1]
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    rs, rf = readers()
    import time; t0 = time.time()
    for f in range(NF):
        si = src_index(f)
        img = compose(f, rs.get(si), rf.get(si))
        enc.stdin.write(img.tobytes())
        if f % 30 == 0: print(f'comp {f}/{NF} {(time.time()-t0)/(f+1):.2f}s/f', flush=True)
    enc.stdin.close(); enc.wait()
    print('done', out)


if __name__ == '__main__':
    main()
