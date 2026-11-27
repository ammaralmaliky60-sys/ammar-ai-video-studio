#!/usr/bin/env python3
"""Cinematic Reality plan for the Alqimmah Clinics clip (room kept as the world; no matte).
Writes timeline.json + render jobs (job_text1/clock/text2/teeth.json). Run from anywhere.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, '../../../studio/cinematic-reality/engine'))
TEX = HERE + '/tex'
FPS = 30
NF = 396                      # 13.2 s (tail trimmed after the last word + end-card hold)
STRIP_H = 800                 # 3D overlay strip rendered for y 0..800 of the frame

# accent colour (#E2178D) in linear RGB
ACCENT_LIN = [round(((c/255 + 0.055)/1.055)**2.4, 4) for c in (0xE2, 0x17, 0x8D)]

def eio(x): x = min(max(x, 0), 1); return 4*x**3 if x < 0.5 else 1 - (-2*x + 2)**3/2
def eout(x): x = min(max(x, 0), 1); return 1 - (1 - x)**3
def lin(f, a, b): return min(max((f - a)/(b - a), 0), 1)
def spring(f, f0, k=170, d=14):
    t = (f - f0)/FPS
    if t <= 0: return 0.0
    w0 = math.sqrt(k); z = d/(2*w0); wd = w0*math.sqrt(1 - z*z)
    return 1 - math.exp(-z*w0*t)*(math.cos(wd*t) + z*w0/wd*math.sin(wd*t))

# ---------------------------------------------------------------- words (seconds, from analysis/02-transcript.json)
W = {'daily': 1.00, 'third': 1.88, 'ninth': 2.48, 'clinics': 3.42, 'qimma': 4.16, 'qadisiya': 4.64,
     'ani': 6.70, 'ortho': 8.64, 'awal': 9.08, 'bawal': 9.32, 'qimma2': 11.30, 'sahih': 12.06}

# captions in the speaker's dialect (start, end, text). Accent words get the brand style.
CAPS = [
    (0.00, 0.98, 'متواجدين إن شاء الله'), (1.00, 1.52, 'يوميًا'),
    (1.54, 2.22, 'من الساعة الثالثة'), (2.24, 2.98, 'إلى الساعة التاسعة'),
    (3.00, 4.50, 'في عيادات القمة'), (4.52, 5.32, 'في القادسية'),
    (5.34, 6.68, 'وأكيد'), (6.70, 7.30, 'آني متواجد'),
    (7.32, 9.06, 'على متابعة حالات التقويم'), (9.08, 9.90, 'أول بأول'),
    (9.92, 11.25, 'وأكيد'), (11.30, 13.20, 'القمة اختياركم صحيح'),
]
ACCENTS = ['يوميًا', 'الثالثة', 'التاسعة', 'القمة', 'القادسية', 'التقويم', 'بأول', 'صحيح']

timeline = dict(
    fps=FPS, nf=NF, strip_h=STRIP_H,
    words=W,
    captions=[dict(s=s, e=e, text=t) for s, e, t in CAPS],
    accents=ACCENTS,
    # camera: hard cut-ins on phrase boundaries (two-camera feel) + keyword punches
    cuts=[0.0, 1.54, 3.00, 5.34, 7.32, 9.76, 11.30],
    punches=[(W['daily'], 0.9), (W['third'], 0.6), (W['ninth'], 0.8), (W['qimma'], 1.1), (W['qadisiya'], 0.9),
             (W['ani'], 0.6), (W['ortho'], 1.0), (W['bawal'], 0.6), (W['qimma2'], 1.2)],
    worlds=[0.0, 1.50, 3.05, 7.30, 11.30],
    chapters=[dict(t=1.00, num='٠١', lab='يوميًا'), dict(t=3.40, num='٠٢', lab='عيادات القمة'),
              dict(t=8.60, num='٠٣', lab='التقويم')],
    lower_third=dict(f0=162, f1=222, name='د. زيد نوري الشريفي', title='طبيب أسنان'),
    end_card=dict(f0=339),
    # overlay layers: (job, first frame, last frame, fade-in frames, fade-out frames)
    layers=[('text1', 0, 52, 0, 8), ('clock', 46, 96, 0, 8), ('text2', 92, 172, 0, 8), ('teeth', 219, 302, 0, 8)],
)

# ---------------------------------------------------------------- render jobs
POST = dict(uMode=1.0, uFocus=0.0, uMaxCoc=0.0, uExposure=1.2, uSat=1.0, uTint=[1, 1, 1], uContrast=1.0, uVignette=0.0)
BOX = [6.0, 1.875, 0.5, 1.0]
CHROME = [0.95, 0.95, 0.97, 0.12]
MAG = ACCENT_LIN + [0.0]


def cam(fov, z=10.0, y=0.0, yaw=0.0):
    return dict(uCamPos=[z*math.sin(yaw), y, z*math.cos(yaw)], uCamTgt=[0, 0, 0], uRoll=0.0, uFov=fov, uShift=[0, 0])


def text_frame(f, reveal, morph, wipe, glow, sheen, pin=None, scale=1.0):
    t = f/FPS
    U = cam(31.0)
    U.update(uTime=t, uTxtBox=BOX, uTxtPos=[0, 0, 0, scale], uTxtRot=[0.10*math.sin(t*0.9), -0.04, morph, 0.26],
             uTxtCol=CHROME, uTxtMat=[1.0, reveal, glow, 0.045], uTxtCol2=MAG[:3] + [wipe], uTxtDir=1.0, uTxtFill=0.30,
             uSheen=sheen, uPin=pin or [0, 0, 0, 0], uPinCol=ACCENT_LIN + [0])
    return dict(name=f'{f:05d}.png', U=U, P=dict(POST, uExposure=1.55, uContrast=1.06))


def job(name, scene, frames, textures=None):
    j = dict(scene=scene, W=1080, H=STRIP_H, includes=['common.glsl'] + (['textobj.glsl'] if scene == 'alq_text' else []),
             textures=textures or {}, frames=frames, out=f'{HERE}/renders/{name}', skip_existing=True)
    json.dump(j, open(f'{HERE}/job_{name}.json', 'w'))
    return len(frames)


# 1) intro title (frame 0 fully built) -> morph to "يوميًا" -> magenta repaint
fr = []
for f in range(0, 53):
    morph = eio(lin(f, 29, 35)); wipe = eout(lin(f, 35, 45))
    sheen = -0.2 + 1.4*lin(f, 2, 26) if f < 30 else -0.2 + 1.4*lin(f, 38, 52)
    fr.append(text_frame(f, 1.0, morph, wipe, 0.0, sheen, scale=1.0 + 0.04*lin(f, 0, 52)))
n1 = job('text1', 'alq_text', fr, {'uTxtA': TEX + '/clinic.npy', 'uTxtB': TEX + '/daily.npy'})

# 2) chrome clock: pops in, hand to 3 on "الثالثة", sweeps to 9 on "التاسعة"
fr = []
for f in range(46, 97):
    t = f/FPS
    s = min(1.0, spring(f, 46, 200, 16))
    hour = 3*eio(lin(f, 48, 58)) + 6*eio(lin(f, 74, 87))
    U = cam(30.0, 8.6, 0.30, 0.12*math.sin(t*0.8) - 0.06)
    U.update(uTime=t, uHour=hour, uArc0=3.0 if hour >= 3 else -1.0, uScale=max(s, 0.001), uSheen=-0.2 + 1.4*lin(f, 50, 90), uAccent=ACCENT_LIN)
    fr.append(dict(name=f'{f:05d}.png', U=U, P=POST))
n2 = job('clock', 'alq_clock', fr)

# 3) "عيادات القمة" assembles right->left, repaints magenta on "القمة", morphs to "القادسية" + pin drop
fr = []
for f in range(92, 173):
    reveal = eio(lin(f, 98, 124)); glow = 0.8*(1 - lin(f, 118, 130))
    wipe = eout(lin(f, 125, 136)); morph = eio(lin(f, 139, 149))
    ps = spring(f, 140, 220, 12)
    pin = [0.0, 1.25 + 3.5*(1 - min(ps, 1.0)) + 0.0, 0.25, 0.75*min(1.0, (f - 140)/4)] if f >= 140 else None
    fr.append(text_frame(f, reveal, morph, wipe, glow, -0.2 + 1.4*lin(f, 128, 160), pin=pin))
n3 = job('text2', 'alq_text', fr, {'uTxtA': TEX + '/clinic.npy', 'uTxtB': TEX + '/qadisiya.npy'})

# 4) teeth + braces: crowns pop in, brackets centre-out on "حالات التقويم", archwire on "التقويم", ligatures
fr = []
order = [2, 3, 1, 4, 0, 5]
for f in range(219, 303):
    t = f/FPS
    s = min(1.0, spring(f, 220, 160, 15))
    br = [0.0]*6
    for k, i in enumerate(order):
        br[i] = max(0.0, min(1.0, spring(f, 244 + 2*k, 320, 18)))
    U = cam(30.0, 9.6, 0.9, 0.16*math.sin(t*0.7 - 5.0))
    U.update(uTime=t, uScale=max(s, 0.001), uBrA=br[:4], uBrB=br[4:], uWire=eio(lin(f, 258, 272)),
             uSheen=-0.2 + 1.4*lin(f, 262, 296), uAccent=ACCENT_LIN)
    fr.append(dict(name=f'{f:05d}.png', U=U, P=POST))
n4 = job('teeth', 'alq_teeth', fr)

json.dump(timeline, open(f'{HERE}/timeline.json', 'w'), ensure_ascii=False, indent=1)
print('jobs', n1, n2, n3, n4, 'frames; timeline ok')
