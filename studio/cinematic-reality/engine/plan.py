#!/usr/bin/env python3
"""Edit plan: EDL (pause trimming), scene schedule, camera paths, word cues, caption chunks, render jobs."""
import json, math, random
from sim import simulate

FPS = 30
# ---- speech islands (source seconds) and kept gaps -------------------------------------------
SEGS_SRC = [(0.21, 2.85), (4.04, 4.93), (5.55, 7.12), (8.65, 9.58), (10.15, 18.51), (19.25, 24.91), (25.47, 28.17), (30.10, 36.46)]
EDL = []
o = 0
for a, b in SEGS_SRC:
    fa, fb = round(a*FPS), round(b*FPS)
    EDL.append({'src0': fa, 'src1': fb, 'out0': o})
    o += fb - fa
NF = o
DUR = NF/FPS


def s2o(t):
    f = t*FPS
    for e in EDL:
        if e['src0'] - 0.5 <= f <= e['src1'] + 0.5:
            return (e['out0'] + f - e['src0'])/FPS
    raise ValueError(t)


# word cues (source seconds) -> output seconds
W = {k: s2o(v) for k, v in {
    'hatha': 0.51, 'kalaud1': 1.93, 'claude2': 4.34, 'khalli_huna': 5.80, 'sura': 6.22, 'iran': 6.52, 'claude3': 8.95,
    'khalli5': 10.40, 'sawda': 11.10, 'khalli6': 13.08, 'mandhar': 13.62, 'tabii': 13.98, 'khalli7': 16.04, 'bahr': 17.39,
    'alwan': 19.95, 'kitaba': 20.55, 'khalliha': 21.25, 'lawn': 21.70, 'aswad': 22.02, 'sawiha': 23.78, 'sufur': 24.08,
    'khalli10': 26.02, 'kalima': 26.20, 'iraq': 26.50, 'bilawn': 26.95, 'ahmar': 27.15, 'end10': 27.47,
    'khalli11': 30.80, 'niqat': 31.15, 'i12': 32.65, 'i13': 34.41, 'end13': 35.56}.items()}

CAPS_SRC = [("هذا الفيديو", 0.51, 1.12), ("جاي أصوّره", 1.12, 1.93), ("بالكلاود", 1.93, 2.55),
            ("كلاود", 4.34, 4.68), ("خلّي هنا", 5.80, 6.22), ("صورة إيران", 6.22, 6.82), ("كلاود", 8.95, 9.33),
            ("خلّي الخلفية", 10.40, 11.10), ("سودة", 11.10, 11.48), ("خلّي الخلفية", 13.08, 13.62), ("منظر طبيعي", 13.62, 14.35),
            ("خلّي الخلفية", 16.04, 17.39), ("بحر", 17.39, 17.81), ("الألوان", 19.95, 20.55), ("للكتابة", 20.55, 21.25),
            ("خلّيها", 21.25, 21.70), ("لون أسود", 21.70, 22.55), ("سوّيها", 23.78, 24.08), ("صفر", 24.08, 24.36),
            ("خلّي كلمة", 26.02, 26.50), ("العراق", 26.50, 26.95), ("بلون أحمر", 26.95, 27.47), ("خلّي نقاط", 30.80, 31.71)]
ACCENT = {"سودة": "#F3F1ED", "بحر": "#8FD3FF", "لون أسود": "#F3F1ED", "صفر": "#F5C518", "العراق": "#E8343A", "بلون أحمر": "#E8343A"}
caps = []
for i, (txt, a, b) in enumerate(CAPS_SRC):
    oa, ob = s2o(a), s2o(b)
    nxt = s2o(CAPS_SRC[i+1][1]) if i+1 < len(CAPS_SRC) else DUR
    caps.append({'text': txt, 's': round(oa, 3), 'e': round(min(nxt, ob + 0.45), 3), 'color': ACCENT.get(txt, '#FFFFFF'), 'accent': txt in ACCENT})

# ---- scene schedule (output seconds) -----------------------------------------------------------
T_BLACK = W['sawda'] - 0.05          # lights out
T_MT = W['mandhar'] - 0.08           # sunrise reveal
T_SEA = W['bahr'] - 0.10             # whip pan
T_FLAG = W['end10'] + 0.10           # whip up
T_STUDIO = W['niqat'] - 0.12         # light dissolve
SCHED = {'room': [0.0, T_BLACK + 0.30], 'black': [T_BLACK, T_MT + 0.75], 'mountain': [T_MT, T_SEA + 0.30],
         'sea': [T_SEA - 0.05, T_FLAG + 0.35], 'flag': [T_FLAG - 0.05, T_STUDIO + 0.30], 'studio': [T_STUDIO - 0.05, DUR]}
TRANS = [{'type': 'lightsout', 't': T_BLACK, 'dur': 0.30, 'a': 'room', 'b': 'black'},
         {'type': 'sunrise', 't': T_MT, 'dur': 0.70, 'a': 'black', 'b': 'mountain'},
         {'type': 'whipLeft', 't': T_SEA, 'dur': 0.27, 'a': 'mountain', 'b': 'sea'},
         {'type': 'whipUp', 't': T_FLAG, 'dur': 0.27, 'a': 'sea', 'b': 'flag'},
         {'type': 'flash', 't': T_STUDIO, 'dur': 0.30, 'a': 'flag', 'b': 'studio'}]


def ease(x):
    x = min(max(x, 0.0), 1.0); return x*x*(3-2*x)


def eout(x):
    x = min(max(x, 0.0), 1.0); return 1 - (1-x)**3


def nrm(v):
    n = math.sqrt(sum(x*x for x in v)); return [x/n for x in v]


def frames_for(scene):
    a, b = SCHED[scene]
    return list(range(max(0, int(math.floor(a*FPS))), min(NF, int(math.ceil(b*FPS)) + 1)))


POST = dict(uMode=0, uFocus=0, uMaxCoc=0, uExposure=1.0, uSat=1.05, uTint=[1, 1, 1], uContrast=1.04, uVignette=0.22)
TXT_OFF = {'uTxtBox': [6, 1.875, 0.5, 0], 'uTxtMat': [0, 0, 0, 0.05], 'uTxtPos': [0, -100, 0, 1], 'uTxtRot': [0, 0, 0, 0.3],
           'uTxtCol': [1, 1, 1, 0.3], 'uTxtCol2': [1, 1, 1, 0], 'uTxtDir': 1.0}
jobs = {}

# title over the room ---------------------------------------------------------------------------
fr = []
T_TITLE_OUT = EDL[1]['out0']/FPS - 0.02
for f in range(0, int(T_TITLE_OUT*FPS) + 1):
    t = f/FPS
    k = eout((t - (T_TITLE_OUT - 0.36))/0.36)           # exit
    yaw = 0.10*math.sin(t*0.9) - 0.05
    U = dict(uTime=t, uCamPos=[0, 0, 0], uCamTgt=[0, 0, -10], uRoll=0.0, uFov=60.0, uShift=[0, 0], uSunDir=[0, 1, 0],
             uTxtBox=[6, 3.2227, 0.5, 1], uTxtPos=[0, 2.66 + 0.9*k, -6.0 + 3.2*k, 0.50], uTxtRot=[yaw, -0.06, 0.0, 0.17],
             uTxtCol=[0.95, 0.92, 0.86, 0.14], uTxtMat=[1.0, 1.0, 0.0, 0.035], uTxtCol2=[0.95, 0.92, 0.86, 0.0], uTxtDir=-1.0,
             uSheen=((t*0.55) % 1.4), uTxtFill=0.0)
    P = dict(POST, uMode=1, uVignette=0.0, uExposure=1.0, uContrast=1.0)
    fr.append({'name': f'{f:05d}.png', 'U': U, 'P': P, 'alpha_fade': 1.0 - k})
jobs['title'] = dict(scene='title', W=1080, H=1920, RW=2160, RH=3840, includes=['common.glsl', 'textobj.glsl'],
                     textures={'uTxtA': 'tex/title.npy', 'uTxtB': 'tex/title.npy'}, frames=fr)

# Iranian flag standing in the room ("خلّي هنا صورة إيران") ---------------------------------------------
fr = []
T_IR = W['iran'] - 0.05
for f in range(int(T_IR*FPS) - 2, int((T_BLACK + 0.32)*FPS) + 1):
    t = f/FPS
    rev = eout((t - T_IR)/0.55)
    U = dict(uTime=t, uCamPos=[0, 0, 0], uCamTgt=[0, 0, -10], uRoll=0.0, uFov=60.0, uShift=[0, 0], uSunDir=[0, 1, 0],
             uFl=[-1.413, 2.315, -5.0, 1.526], uFl2=[0.872, 0.30, 2.2, max(rev, 0.001)])
    P = dict(POST, uMode=1, uVignette=0.0, uExposure=1.0, uContrast=1.0, uSat=1.04)
    fr.append({'name': f'{f:05d}.png', 'U': U, 'P': P, 'alpha_fade': ease((t - T_IR + 0.10)/0.25)})
jobs['flagroom'] = dict(scene='flagroom', W=1080, H=1920, RW=2160, RH=3840, includes=['common.glsl'],
                        textures={'uFlag': 'tex/ir_flag.png'}, frames=fr)

# black studio ----------------------------------------------------------------------------------
fr = []
for f in frames_for('black'):
    t = f/FPS; lt = t - T_BLACK
    on = 0.0 if lt < 0.12 else min(1.0, (lt-0.12)/0.12)
    if 0.12 <= lt < 0.42: on *= (0.55 + 0.45*abs(math.sin(lt*95.0)))  # flicker on
    U = dict(uTime=t, uCamPos=[0, 1.6, -0.22*lt], uCamTgt=[0, 1.45, -10 - 0.22*lt], uRoll=0.0, uFov=58.0, uShift=[0, -0.15],
             uSunDir=[0, 1, 0], uSpot=[0, 9.0, -6.8, on], uSpot2=[0, 0, -5.6, 0.19], uAmbient=max(0.0, 1.0 - lt/0.25))
    fr.append({'name': f'{f:05d}.png', 'U': U, 'P': dict(POST, uExposure=1.15, uVignette=0.35, uFocus=1.2, uMaxCoc=3.0)})
jobs['black'] = dict(scene='black', W=1080, H=1920, RW=1080, RH=1920, includes=['common.glsl'], frames=fr)

# mountains ---------------------------------------------------------------------------------------
fr = []
sun_mt = nrm([1.0, 0.36, -0.55])
for f in frames_for('mountain'):
    t = f/FPS; lt = t - T_MT
    pos = [-300 + 4*lt, 750 + 4.0*lt, 1500 - 26*lt]
    U = dict(uTime=t, uCamPos=pos, uCamTgt=[pos[0] + 100, pos[1] - 150, pos[2] - 1000], uRoll=0.0, uFov=60.0, uShift=[0, -0.06],
             uSunDir=sun_mt, uMt=[2000, 520, 0.0016, 1000], uAmp=800.0, uReveal=ease(lt/0.7)*0.97 + 0.03)
    fr.append({'name': f'{f:05d}.png', 'U': U, 'P': dict(POST, uExposure=0.92, uSat=1.12, uContrast=1.06, uVignette=0.25)})
jobs['mountain'] = dict(scene='mountain', W=1080, H=1920, RW=540, RH=960, includes=['common.glsl'], frames=fr)

# sea + 3D text ----------------------------------------------------------------------------------
sun_sea = nrm([-0.20, 0.13, -1.0])
BLACKC = [0.012, 0.012, 0.012]; WHITEC = [0.80, 0.79, 0.76]; YEL = [1.0, 0.66, 0.0]; RED = [0.78, 0.012, 0.02]


def text_state(t):
    """material/animation state of the morphing word through the sea + flag scenes"""
    rev = eout((t - W['kitaba'])/0.55)
    glow = 1.0 - ease((t - W['kitaba'])/0.6)
    a_black = ease((t - W['aswad'])/0.30)
    base = [WHITEC[i]*(1 - a_black) + BLACKC[i]*a_black for i in range(3)]
    rough = 0.28*(1 - a_black) + 0.12*a_black
    col2 = YEL; prog = eout((t - W['sufur'])/0.45)
    if t >= W['ahmar']:
        base = YEL; col2 = RED; prog = eout((t - W['ahmar'])/0.40); rough = 0.14
    morph = ease((t - W['iraq'])/0.45)
    return dict(rev=rev, glow=glow, base=base, rough=rough, col2=col2, prog=prog, morph=morph)


fr = []
for f in frames_for('sea'):
    t = f/FPS; lt = t - T_SEA
    cz = -0.5*lt
    pos = [0, 2.4 + 0.06*math.sin(lt*1.3), cz]
    st = text_state(t)
    yaw = 0.16 - 0.10*ease((t - W['kitaba'])/4.0)
    U = dict(uTime=t + 20.0, uCamPos=pos, uCamTgt=[0.0, pos[1], cz - 10], uRoll=0.004*math.sin(lt*0.9), uFov=60.0, uShift=[0, -0.25],
             uSunDir=sun_sea, uSea=[0.6, 4.0, 0.16, 0.8], uSky=[0.42, 1.0, 0, 0.0006],
             uTxtBox=[6, 1.875, 0.5, 1.0 if t >= W['kitaba'] else 0.0], uTxtPos=[0, 6.3, -26, 2.1], uTxtRot=[yaw, -0.04, st['morph'], 0.36],
             uTxtCol=st['base'] + [st['rough']], uTxtMat=[0.0, st['rev'], st['glow'], 0.06], uTxtCol2=st['col2'] + [st['prog']], uTxtDir=1.0, uTxtFill=0.55)
    fr.append({'name': f'{f:05d}.png', 'U': U, 'P': dict(POST, uExposure=0.82, uSat=1.06, uFocus=22.0, uMaxCoc=2.5, uVignette=0.25)})
jobs['sea'] = dict(scene='sea', W=1080, H=1920, RW=1080, RH=1920, includes=['common.glsl', 'textobj.glsl', 'seafuncs.glsl'],
                   textures={'uTxtA': 'tex/kitaba.npy', 'uTxtB': 'tex/iraq.npy'}, frames=fr)

# flag (same world as the sea; lens shifted up to the sky) ---------------------------------------
fr = []
for f in frames_for('flag'):
    t = f/FPS; lt = t - T_FLAG
    pos = [0.12*lt, 2.4, -0.3*lt]
    U = dict(uTime=t + 20.0, uCamPos=pos, uCamTgt=[pos[0], 2.4, pos[2] - 10], uRoll=0.0, uFov=60.0, uShift=[0, 0.20], uSunDir=sun_sea,
             uSea=[0.6, 4.0, 0.16, 0.8], uSky=[0.42, 1.0, 0, 0.0006],
             uFl=[-3.6, 15.8, -22.0, 7.2], uFl2=[4.8, 1.8, 3.0, 0], **TXT_OFF)
    fr.append({'name': f'{f:05d}.png', 'U': U, 'P': dict(POST, uExposure=0.85, uSat=1.08, uFocus=0, uMaxCoc=0, uVignette=0.25)})
jobs['flag'] = dict(scene='flag', W=1080, H=1920, RW=1080, RH=1920, includes=['common.glsl', 'textobj.glsl', 'seafuncs.glsl'],
                    textures={'uFlag': 'tex/iq_flag.png', 'uTxtA': 'tex/kitaba.npy', 'uTxtB': 'tex/iraq.npy'}, frames=fr)

# studio + physics spheres ---------------------------------------------------------------------------
random.seed(7)
PAL = [[0.012, 0.012, 0.012, 0.10], YEL + [0.16], RED + [0.14], [0.82, 0.81, 0.79, 0.22]]
spawns, cols = [], []


def spawn_wave(t0, n, spread):
    for i in range(n):
        z = random.uniform(-11.0, -5.6)
        xr = 0.42*abs(z)
        spawns.append((t0 + random.uniform(0, spread), random.uniform(-xr, xr), random.uniform(6.5, 10.5), z,
                       random.uniform(0.26, 0.58), random.uniform(-0.5, 0.5), random.uniform(-1.0, 0.0), random.uniform(-0.3, 0.3)))
        cols.append(PAL[len(cols) % 4])


spawn_wave(T_STUDIO - 0.35, 20, 0.7)
spawn_wave(W['i13'] - 0.45, 16, 0.8)
st0 = SCHED['studio'][0]
traj = simulate(spawns, st0, DUR + 0.1, fps=FPS, wall_z=-12.0)
T_END_TITLE = W['end13'] + 0.05
fr = []
for k, f in enumerate(frames_for('studio')):
    t = f/FPS; lt = t - T_STUDIO
    idx = min(len(traj) - 1, max(0, f - int(math.floor(st0*FPS))))
    sph = traj[idx] + [[0, -50, 0, 0]]*(40 - len(traj[idx]))
    C = cols + [[1, 1, 1, 0.3]]*(40 - len(cols))
    tr = eout((t - T_END_TITLE)/0.7)
    U = dict(uTime=t, uCamPos=[0, 1.6, -0.25*lt], uCamTgt=[0, 1.5, -10 - 0.25*lt], uRoll=0.0, uFov=58.0, uShift=[0, -0.15], uSunDir=[0, 1, 0],
             uWallZ=-12.0, uLightAmt=1.0, **{'uSph[0]': sum(sph, []), 'uSphC[0]': sum(C, [])},
             uTxtBox=[6, 3.2227, 0.5, 1.0 if t >= T_END_TITLE else 0.0], uTxtPos=[0, 2.58, -4.8, 0.25], uTxtRot=[0.0, 0.0, 0.0, 0.25],
             uTxtCol=[0.10, 0.10, 0.11, 0.12], uTxtMat=[1.0, tr, 1.0 - tr, 0.03], uTxtCol2=[1, 1, 1, 0], uTxtDir=-1.0, uTxtFill=0.0)
    fr.append({'name': f'{f:05d}.png', 'U': U, 'P': dict(POST, uExposure=0.86, uSat=1.04, uFocus=7.5, uMaxCoc=2.5, uVignette=0.22)})
jobs['studio'] = dict(scene='studio', W=1080, H=1920, RW=1080, RH=1920, includes=['common.glsl', 'textobj.glsl'],
                      textures={'uTxtA': 'tex/title.npy', 'uTxtB': 'tex/title.npy'}, frames=fr)

for k, j in jobs.items():
    j['out'] = f'renders/{k}'; j['skip_existing'] = True
    json.dump(j, open(f'job_{k}.json', 'w'))

# person layer placement / grade keys per scene (consumed by comp.py)
PERSON = {
    'room':     dict(dy=0,   exp=1.00, temp=[1.00, 1.00, 1.00], rim=[0, 0, 0], rimDir=[0, -1], wrap=0.0, lift=0.0, contrast=1.06, sat=1.0),
    'black':    dict(dy=130, exp=0.62, temp=[0.97, 0.98, 1.03], rim=[1.25, 1.15, 1.0], rimDir=[0.0, -1.0], wrap=0.15, lift=-0.01, contrast=1.12, sat=0.92),
    'mountain': dict(dy=130, exp=0.97, temp=[1.06, 1.00, 0.93], rim=[1.25, 1.0, 0.75], rimDir=[1.0, -0.35], wrap=0.40, lift=0.0, contrast=1.05, sat=1.0),
    'sea':      dict(dy=130, exp=0.90, temp=[1.02, 1.00, 1.03], rim=[1.25, 1.02, 0.80], rimDir=[-0.35, -1.0], wrap=0.45, lift=0.0, contrast=1.06, sat=1.0),
    'flag':     dict(dy=130, exp=0.95, temp=[1.08, 0.99, 0.90], rim=[1.30, 0.95, 0.65], rimDir=[-1.0, -0.4], wrap=0.40, lift=0.0, contrast=1.05, sat=1.02),
    'studio':   dict(dy=130, exp=1.06, temp=[1.01, 1.00, 0.99], rim=[0.85, 0.85, 0.85], rimDir=[-0.6, -1.0], wrap=0.35, lift=0.012, contrast=1.02, sat=1.0),
}
json.dump({'fps': FPS, 'nf': NF, 'dur': DUR, 'edl': EDL, 'words': W, 'captions': caps, 'sched': SCHED, 'trans': TRANS,
           'person': PERSON, 'title_out': T_TITLE_OUT}, open('timeline.json', 'w'), ensure_ascii=False, indent=1)
print('frames', NF, 'dur', round(DUR, 2))
for k, j in jobs.items():
    print(k, len(j['frames']), j['frames'][0]['name'], j['frames'][-1]['name'])
print({k: round(v, 2) for k, v in W.items()})
