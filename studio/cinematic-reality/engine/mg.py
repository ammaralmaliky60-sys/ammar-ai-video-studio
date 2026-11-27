"""Advanced motion-graphics layer for the compositor:
virtual camera (push-ins, keyword punches, cut-ins, parallax, dolly zoom), premium transitions (portal, shockwave,
whip with chroma split + light streak), kinetic Arabic typography (per-word mask-rise, colour-coded keywords with
gradient + glow + underline sweep), chapter markers, voice waveform, foreground bokeh, bloom + anamorphic streaks + CA.
"""
import math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
import os
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts') + '/'
F_SEMI = FONTS + 'IBMPlexSansArabic-SemiBold.ttf'
F_BOLD = FONTS + 'IBMPlexSansArabic-Bold.ttf'
F_REG = FONTS + 'IBMPlexSansArabic-Regular.ttf'
F_LIGHT = FONTS + 'IBMPlexSansArabic-Light.ttf'
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


def clamp01(x): return min(max(x, 0.0), 1.0)
def ease(x): x = clamp01(x); return x*x*(3-2*x)
def eout(x): x = clamp01(x); return 1 - (1-x)**3
def eio(x): x = clamp01(x); return 4*x*x*x if x < 0.5 else 1 - (-2*x+2)**3/2


# ================================================================ virtual camera
class Camera:
    def __init__(self, TL):
        Wd = TL['words']
        # keyword punches (time, strength)
        self.punch = [(Wd['iran'], 1.0), (Wd['sawda'], 1.2), (Wd['mandhar'], 0.8), (Wd['bahr'], 0.9), (Wd['kitaba'], 0.7),
                      (Wd['aswad'], 1.0), (Wd['sufur'], 1.0), (Wd['iraq'], 1.0), (Wd['ahmar'], 1.1), (Wd['niqat'], 0.9), (Wd['i13'], 0.8)]
        self.edl = TL['edl']
        # alternate framing on each jump cut (two-camera feel)
        self.alt = [1.00, 1.08, 1.00, 1.07, 1.00, 1.06, 1.00, 1.05]
        self.trans = {tr['type']: tr for tr in TL['trans']}
        self.sched_starts = sorted([tr['t'] for tr in TL['trans']])

    def seg(self, f):
        for i, e in enumerate(self.edl):
            if e['out0'] <= f < e['out0'] + e['src1'] - e['src0']:
                return i
        return len(self.edl) - 1

    def punch_amt(self, t):
        s = 0.0
        for tk, k in self.punch:
            x = t - tk
            if -0.02 < x < 1.6:
                a = eout(x/0.14) if x < 0.14 else math.exp(-(x - 0.14)/0.45)
                s += k*a
        return s

    def scales(self, t, f):
        # slow push since the last world change
        last = 0.0
        for ts in self.sched_starts:
            if t >= ts: last = ts
        push = 1.0 + 0.03*ease((t - last)/6.0)
        sp = self.alt[self.seg(f)]*push*(1.0 + 0.035*self.punch_amt(t))
        sb = 1.0 + (sp - 1.0)*0.5
        # dolly-zoom settle of the new world after portal / shockwave
        for typ, amp, dur in (('sunrise', 0.20, 1.3), ('flash', 0.14, 1.0), ('whipLeft', 0.08, 0.7), ('whipUp', 0.08, 0.7)):
            tr = self.trans[typ]; x = t - (tr['t'] + tr['dur']*0.3)
            if 0 <= x < dur:
                sb *= 1.0 + amp*(1.0 - eout(x/dur))
        return sp, sb


def affine_scale(s, ax, ay, dy=0.0):
    """translate by dy then scale about (ax, ay)"""
    return np.array([[s, 0, ax - s*ax], [0, s, s*dy + ay - s*ay]], np.float32)


def compose3(A, B):
    """A after B (2x3 affines)"""
    a = np.vstack([A, [0, 0, 1]]); b = np.vstack([B, [0, 0, 1]])
    return (a @ b)[:2].astype(np.float32)


# ================================================================ transitions
def portal(bgA, bgB, p, cx, cy, maxR=1500.0, ring_col=(1.0, 0.85, 0.6), width=70.0):
    r = maxR*eio(p)
    d = np.sqrt((XX - cx)**2 + (YY - cy)**2) + 1e-3
    inside = np.clip((r + width*0.5 - d)/width, 0, 1)
    ring = np.exp(-((d - r)/(width*0.55))**2)
    if r < 2: return bgA, ring*0
    disp = ring*38.0
    ux, uy = (XX - cx)/d, (YY - cy)/d
    out = np.empty_like(bgB)
    for c, k in ((0, 1.25), (1, 1.0), (2, 0.75)):          # chromatic refraction at the rim
        mx = XX - ux*disp*k; my = YY - uy*disp*k
        out[..., c] = cv2.remap(bgB[..., c], mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    m = inside[..., None]
    res = bgA*(1 - m) + out*m
    glow = ring[..., None]*np.array(ring_col, np.float32)*0.85*(1.0 - 0.6*p)
    return res + glow*(1 - res), ring


def whip(bgA, bgB, p, horizontal):
    e = eio(p); spd = max(0.0, 6*p*(1 - p))
    if horizontal:
        o = int(e*W)
        bg = np.empty_like(bgA); bg[:, :W - o] = bgA[:, o:]; bg[:, W - o:] = bgB[:, :o]
        L = int(spd*90)
        if L >= 3:
            k = np.zeros((1, L), np.float32); k[0, :] = 1.0/L
            bg = cv2.filter2D(bg, -1, k)
        ca = int(spd*14)
        if ca > 0:
            bg[..., 0] = np.roll(bg[..., 0], ca, axis=1); bg[..., 2] = np.roll(bg[..., 2], -ca, axis=1)
        seam = W - o
        streak = np.exp(-((XX[0] - seam)/(60 + 140*spd))**2)[None, :, None]
    else:
        o = int(e*H)
        bg = np.empty_like(bgA); bg[o:, :] = bgA[:H - o, :]; bg[:o, :] = bgB[H - o:, :]
        L = int(spd*110)
        if L >= 3:
            k = np.zeros((L, 1), np.float32); k[:, 0] = 1.0/L
            bg = cv2.filter2D(bg, -1, k)
        ca = int(spd*14)
        if ca > 0:
            bg[..., 0] = np.roll(bg[..., 0], ca, axis=0); bg[..., 2] = np.roll(bg[..., 2], -ca, axis=0)
        seam = o
        streak = np.exp(-((YY[:, 0] - seam)/(60 + 160*spd))**2)[:, None, None]
    bg = bg + streak*np.array([1.0, 0.92, 0.8], np.float32)*0.55*spd
    # zoom pulse at the middle of the whip
    z = 1.0 + 0.06*spd
    if z > 1.001:
        bg = cv2.warpAffine(bg, affine_scale(z, W/2, H/2), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return bg


# ================================================================ kinetic typography
ACC = {'سودة': 'black', 'أسود': 'black', 'صفر': 'yellow', 'العراق': 'red', 'أحمر': 'red', 'بحر': 'blue', 'منظر': 'green', 'طبيعي': 'green',
       'إيران': 'white2', 'نقاط': 'white2', 'كلاود': 'cyan', 'بالكلاود': 'cyan'}
GRAD = {'yellow': ((255, 232, 110), (240, 170, 0)), 'red': ((255, 105, 105), (210, 14, 26)), 'blue': ((175, 230, 255), (40, 150, 225)),
        'green': ((190, 250, 200), (60, 190, 100)), 'black': ((40, 40, 40), (5, 5, 5)), 'white2': ((255, 255, 255), (225, 225, 230)),
        'cyan': ((255, 255, 255), (215, 242, 255)), 'brand': ((255, 120, 190), (226, 23, 141))}
GLOW = {'yellow': (255, 200, 40), 'red': (255, 40, 50), 'blue': (60, 170, 255), 'green': (80, 220, 120), 'black': (255, 255, 255),
        'white2': (255, 255, 255), 'cyan': (90, 210, 255), 'brand': (235, 40, 150)}
LINE = {'yellow': (255, 205, 30), 'red': (240, 40, 50), 'blue': (70, 180, 255), 'green': (90, 220, 120), 'black': (245, 245, 245),
        'white2': (245, 245, 245), 'cyan': (110, 220, 255), 'brand': (240, 60, 160)}


def word_sprite(word, style):
    acc = style is not None
    size = 90 if acc else 74
    font = ImageFont.truetype(F_BOLD if acc else F_SEMI, size, layout_engine=ImageFont.Layout.RAQM)
    kw = dict(direction='rtl', language='ar')
    asc, desc = font.getmetrics()
    bb = font.getbbox(word, anchor='ls', **kw)
    pad = 46
    w = bb[2] - bb[0] + 2*pad; h = asc + desc + 2*pad
    base = (pad - bb[0], pad + asc)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).text(base, word, font=font, fill=255, anchor='ls', **kw)
    m = np.asarray(mask).astype(np.float32)/255.0
    if acc:
        c0, c1 = GRAD[style]
        ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        top = pad + asc + bb[1]; ys = np.clip((np.arange(h)[:, None] - top)/max(1, (bb[3]-bb[1])), 0, 1)
        fill = np.stack([(c0[i]*(1-ys) + c1[i]*ys)*np.ones((1, w)) for i in range(3)], -1)/255.0
    else:
        fill = np.ones((h, w, 3), np.float32)
    # shadow (soft, down) + glow (accent)
    sh = cv2.GaussianBlur(np.roll(m, 5, axis=0), (0, 0), 9)*0.65
    rgb = np.zeros((h, w, 3), np.float32); a = np.zeros((h, w), np.float32)
    # shadow layer
    rgb = rgb*(1 - sh[..., None]); a = a + sh*(1 - a)
    if acc:
        g = cv2.GaussianBlur(m, (0, 0), 11 if style == 'black' else 14)*(1.0 if style == 'black' else 0.75)
        gc = np.array(GLOW[style], np.float32)/255.0
        rgb = rgb*(1 - g[..., None]) + gc*g[..., None]; a = a + g*(1 - a)
    rgb = rgb*(1 - m[..., None]) + fill*m[..., None]; a = a + m*(1 - a)
    rgb = rgb/np.maximum(a[..., None], 1e-4)
    return {'rgb': rgb.astype(np.float32), 'a': np.clip(a, 0, 1).astype(np.float32), 'w': w, 'h': h, 'base_y': pad + asc,
            'ink': (pad, pad + bb[2] - bb[0]), 'style': style}


class Captions:
    def __init__(self, caps, y=1555):
        self.y = y; self.items = []
        for c in caps:
            words = c['text'].split(' ')
            sprites = [word_sprite(wd, ACC.get(wd)) for wd in words]
            lens = [max(1, len(wd)) for wd in words]
            dur = max(0.2, c['e'] - c['s'])
            starts, acc = [], 0
            for L in lens:
                starts.append(c['s'] + dur*0.80*acc/sum(lens)); acc += L
            if c.get('ws'): starts = list(c['ws'])
            gap = -54  # sprites carry padding; negative gap = word spacing ~ 38 px
            total = sum(s['w'] for s in sprites) + gap*(len(sprites) - 1)
            xr = W/2 + total/2; xs = []
            for s in sprites:                      # RTL: first word on the right
                xs.append(xr - s['w']); xr -= s['w'] + gap
            self.items.append(dict(c, sprites=sprites, starts=starts, xs=xs))

    def draw(self, frame, t):
        for it in self.items:
            if not (it['s'] - 0.02 <= t < it['e']): continue
            k_out = 1.0 - ease((t - (it['e'] - 0.09))/0.09)
            for sp, ws, x in zip(it['sprites'], it['starts'], it['xs']):
                lt = t - ws
                if it['s'] <= 0.0: lt = max(lt, 1.0)
                if lt < 0 and it['s'] > 0.0: continue
                k = eout(lt/0.24)
                rgb, a = sp['rgb'], sp['a']
                blur = (1 - k)*5.0 + (1 - k_out)*4.0
                if blur > 0.4:
                    rgb = cv2.GaussianBlur(rgb, (0, 0), blur); a = cv2.GaussianBlur(a, (0, 0), blur)
                hgt = sp['h']
                # mask-rise: reveal from the baseline upwards
                cut = int((1 - k)*hgt*0.9)
                a = a.copy()
                if cut > 0: a[:cut] *= np.linspace(0, 1, cut, dtype=np.float32)[:, None]**3
                sc = 1.0 + 0.08*(1 - k)
                yoff = (1 - k)*26 - (1 - k_out)*12
                x0 = int(x + sp['w']*(1 - sc)/2); y0 = int(self.y - sp['base_y']*sc + 26 + yoff)
                if abs(sc - 1) > 0.01:
                    nw, nh = int(sp['w']*sc), int(hgt*sc)
                    rgb = cv2.resize(rgb, (nw, nh)); a = cv2.resize(a, (nw, nh))
                al = a*k*k_out
                self._blit(frame, rgb, al, x0, y0)
                # underline sweep for keywords (right -> left)
                if sp['style'] in ('black', 'yellow', 'red', 'blue', 'green', 'brand'):
                    u = eout((lt - 0.10)/0.32)
                    if u > 0:
                        i0, i1 = sp['ink']; ln = int((i1 - i0)*u)
                        yb = int(self.y + 46); xr = int(x + i1)
                        col = np.array(LINE[sp['style']], np.float32)/255.0
                        x_a = max(0, xr - ln); x_b = min(W, xr)
                        if x_b > x_a:
                            frame[yb:yb+5, x_a:x_b] = frame[yb:yb+5, x_a:x_b]*(1 - 0.95*k_out) + col*0.95*k_out
        return frame

    @staticmethod
    def _blit(frame, rgb, al, x0, y0):
        h, w = al.shape
        xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w), min(H, y0 + h)
        if xb <= xa or yb <= ya: return
        s_rgb = rgb[ya - y0:yb - y0, xa - x0:xb - x0]; s_a = al[ya - y0:yb - y0, xa - x0:xb - x0][..., None]
        frame[ya:yb, xa:xb] = frame[ya:yb, xa:xb]*(1 - s_a) + s_rgb*s_a


# ================================================================ chapter markers (top-right)
def _text_img(txt, font_path, size, color=(255, 255, 255), rtl=True):
    font = ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
    kw = dict(direction='rtl', language='ar') if rtl else {}
    bb = font.getbbox(txt, **kw); pad = 24
    im = Image.new('L', (bb[2]-bb[0]+2*pad, bb[3]-bb[1]+2*pad), 0)
    ImageDraw.Draw(im).text((pad-bb[0], pad-bb[1]), txt, font=font, fill=255, **kw)
    m = np.asarray(im).astype(np.float32)/255.0
    sh = np.clip(cv2.GaussianBlur(m, (0, 0), 7)*1.1, 0, 0.8)
    a = np.clip(m + sh*(1 - m), 0, 1)
    rgb = (np.array(color, np.float32)/255.0)[None, None, :]*np.ones_like(m)[..., None]
    rgb = rgb*(m/np.maximum(a, 1e-4))[..., None]
    return rgb.astype(np.float32), a.astype(np.float32)


class Chapters:
    def __init__(self, TL):
        Tt = {tr['b']: tr['t'] + tr['dur']*0.5 for tr in TL['trans']}
        spec = [('black', '٠١', 'سودة'), ('mountain', '٠٢', 'منظر طبيعي'), ('sea', '٠٣', 'بحر'), ('flag', '٠٤', 'العراق'), ('studio', '٠٥', 'نقاط')]
        self.items = []
        for sc, num, lab in spec:
            self.items.append(dict(t=Tt[sc], num=_text_img(num, F_BOLD, 74), tot=_text_img('/ ٠٥', F_LIGHT, 38, (225, 225, 230)),
                                   lab=_text_img(lab, F_SEMI, 46, (245, 245, 245))))

    def draw(self, frame, t):
        for it in self.items:
            lt = t - it['t']
            if not (0 <= lt < 2.6): continue
            ko = 1.0 - ease((lt - 2.25)/0.35)
            xr = 1022; y = 92
            # line draws right->left
            ln = int(190*eout(lt/0.35))
            frame[y+86:y+90, xr-ln:xr] = frame[y+86:y+90, xr-ln:xr]*(1 - 0.92*ko) + 0.92*ko
            # small dot at the line start
            if ln > 4:
                cv2.circle(frame, (xr - ln, y + 88), 7, (1.0, 1.0, 1.0), -1, lineType=cv2.LINE_AA)
            for key, dx, dy, t0 in (('num', 0, 0, 0.08), ('tot', None, 28, 0.16), ('lab', 0, 104, 0.22)):
                rgb, a = it[key]
                k = eout((lt - t0)/0.3)
                if k <= 0: continue
                h, w = a.shape
                if key == 'tot':
                    nw = it['num'][1].shape[1]; x0 = xr - nw - w + 26
                else:
                    x0 = xr - w + 24
                y0 = int(y + (dy or 0) - 24 + (1 - k)*18)
                aa = a.copy(); cut = int((1 - k)*h)
                if cut > 0: aa[:cut] = 0
                Captions._blit(frame, rgb, aa*k*ko, x0, y0)
        return frame


# ================================================================ voice waveform (for "كلاود" commands)
class VoiceWave:
    def __init__(self, wav, caps, fps=30):
        a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                                         capture_output=True).stdout, np.int16).astype(np.float32)/32768.0
        hop = 16000//120
        n = len(a)//hop
        env = np.sqrt(np.array([np.mean(a[i*hop:(i+1)*hop]**2) for i in range(n)]) + 1e-9)
        env = env/np.percentile(env, 98)
        self.env = np.clip(env, 0, 1.2); self.rate = 120
        self.spans = [(c['s'], c['e']) for c in caps if 'كلاود' in c['text']]

    def level(self, t):
        i = int(t*self.rate)
        if i < 0 or i >= len(self.env): return 0.0
        return float(np.mean(self.env[max(0, i-3):i+3]))

    def draw(self, frame, t, y=1668):
        for s, e in self.spans:
            if not (s - 0.05 <= t < e + 0.35): continue
            k = ease((t - s + 0.05)/0.15)*(1 - ease((t - e - 0.1)/0.25))
            lev = self.level(t)
            n = 29; sp = 14
            layer = np.zeros((90*2, n*sp + 40), np.float32)
            for i in range(n):
                prof = math.exp(-((i - n//2)/7.5)**2)
                wob = 0.55 + 0.45*math.sin(i*1.9 + t*17.0)*math.sin(i*0.7 - t*9.0)
                hh = 4 + 100*(lev**0.7)*prof*(0.35 + 0.65*abs(wob))
                x = 20 + i*sp
                cv2.line(layer, (x, int(90 - hh)), (x, int(90 + hh)), 1.0, 5, lineType=cv2.LINE_AA)
            glow = cv2.GaussianBlur(layer, (0, 0), 7)
            col = np.array([0.55, 0.88, 1.0], np.float32)
            h, w = layer.shape; x0 = W//2 - w//2; y0 = y - h//2
            sub = frame[y0:y0+h, x0:x0+w]
            a = np.clip(layer, 0, 1)[..., None]*k; g = glow[..., None]*k*0.9
            sub[:] = sub + g*col*(1 - sub)
            sub[:] = sub*(1 - a) + a*np.array([0.92, 0.98, 1.0], np.float32)
        return frame


# ================================================================ foreground bokeh / particles (in front of the speaker)
def _disc(r, soft, ring=0.0):
    s = int(r*2 + soft*3 + 4)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32); c = (s - 1)/2
    d = np.sqrt((xx - c)**2 + (yy - c)**2)
    m = np.clip((r - d)/max(soft, 0.5) + 0.5, 0, 1)
    if ring > 0: m = m*(1 - ring + ring*np.clip((d/r)**4, 0, 1)*1.6)
    return m.astype(np.float32)


class Particles:
    CFG = {   # count, radius range, softness, opacity, colour, drift (px/s), y-range, ring, x-range
        'black':    [(14, (2, 5), 1.4, 0.55, (1.0, 0.9, 0.72), (4, -12), (60, 900), 0.0, (330, 760)),
                     (5, (34, 70), 16, 0.08, (1.0, 0.85, 0.6), (10, -6), (100, 1700), 0.35, (0, 1080))],
        'mountain': [(6, (55, 100), 28, 0.06, (1.0, 0.95, 0.85), (14, 0), (300, 1800), 0.3, (0, 1080))],
        'sea':      [(14, (3, 8), 3, 0.25, (0.85, 0.95, 1.0), (-30, -18), (1100, 1900), 0.0, (0, 1080)),
                     (7, (40, 90), 22, 0.07, (0.9, 0.97, 1.0), (-12, -4), (400, 1900), 0.4, (0, 1080))],
        'flag':     [(5, (50, 90), 24, 0.06, (1.0, 0.85, 0.65), (10, 0), (400, 1700), 0.35, (0, 1080))],
        'studio':   [(5, (60, 110), 30, 0.045, (1.0, 1.0, 1.0), (8, 0), (400, 1700), 0.3, (0, 1080))],
        'room':     [],
    }

    def __init__(self, seed=11):
        rng = np.random.default_rng(seed)
        self.sets = {}
        for sc, groups in self.CFG.items():
            ps = []
            for n, (r0, r1), soft, op, col, (vx, vy), (y0, y1), ring, (xa, xb) in groups:
                for _ in range(n):
                    r = rng.uniform(r0, r1)
                    ps.append(dict(xa=xa, xb=xb, x=rng.uniform(xa, xb), y=rng.uniform(y0, y1), vx=vx*rng.uniform(0.5, 1.5), vy=vy*rng.uniform(0.5, 1.5),
                                   ph=rng.uniform(0, 6.28), op=op*rng.uniform(0.5, 1.0), col=np.array(col, np.float32),
                                   spr=_disc(r, soft, ring), par=1.0 + r/60.0))
            self.sets[sc] = ps

    def draw(self, frame, scene, t, k=1.0, shake=(0.0, 0.0)):
        if k <= 0: return frame
        for p in self.sets.get(scene, []):
            span = p['xb'] - p['xa'] + 200
            x = p['xa'] - 100 + (p['x'] - p['xa'] + 100 + p['vx']*t + 6*math.sin(t*0.7 + p['ph']) + shake[0]*p['par']) % span
            y = (p['y'] + p['vy']*t + 5*math.cos(t*0.6 + p['ph']) + shake[1]*p['par']) % (H + 200) - 100
            spr = p['spr']; h, w = spr.shape
            x0, y0 = int(x - w/2), int(y - h/2)
            xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + w), min(H, y0 + h)
            if xb <= xa or yb <= ya: continue
            a = spr[ya - y0:yb - y0, xa - x0:xb - x0][..., None]*p['op']*k*(0.75 + 0.25*math.sin(t*2.1 + p['ph']))
            sub = frame[ya:yb, xa:xb]
            sub[:] = sub + a*p['col']*(1.0 - sub*0.5)
        return frame


# ================================================================ optical finishing
BLOOM_T = {'room': 0.94, 'black': 0.50, 'mountain': 0.92, 'sea': 0.91, 'flag': 0.91, 'studio': 0.96}


def optics(img, scene, strength=1.0):
    thr = BLOOM_T.get(scene, 0.9)
    sm = cv2.resize(img, (W//4, H//4), interpolation=cv2.INTER_AREA)
    lum = sm.mean(2, keepdims=True)
    hl = sm*np.clip((lum - thr)/(1.0 - thr + 1e-3), 0, 1)
    bloom = cv2.GaussianBlur(hl, (0, 0), 6) + cv2.GaussianBlur(hl, (0, 0), 20)*0.7
    hl2 = sm*np.clip((lum - max(thr, 0.82))/0.14, 0, 1)**2
    streak = cv2.GaussianBlur(hl2, (0, 0), sigmaX=70, sigmaY=1.2)*np.array([0.55, 0.75, 1.25], np.float32)
    add = cv2.resize(bloom*0.30 + streak*0.8, (W, H), interpolation=cv2.INTER_LINEAR)*strength
    img = img + add*(1.0 - img*0.6)
    return img


def chroma_edges(img, amt=0.0022):
    out = img.copy()
    for c, s in ((0, 1 + amt), (2, 1 - amt)):
        out[..., c] = cv2.warpAffine(img[..., c], affine_scale(s, W/2, H/2), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return out
