#!/usr/bin/env python3
"""Compositor v2: same plates as comp.py + the advanced motion-graphics layer (mg.py).
Usage: comp2.py OUT.mp4 | comp2.py --stills DIR f1,f2,...
"""
import math, os, subprocess, sys, time
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comp as C
import mg

W, H, FPS, NF, TL = C.W, C.H, C.FPS, C.NF, C.TL
caps = [dict(c) for c in TL['captions']]; caps[0]['s'] = 0.0
CAM = mg.Camera(TL)
CAPS = mg.Captions(caps)
CHAP = mg.Chapters(TL)
WAVE = mg.VoiceWave(C.R + '/audio_edit.wav', caps)
PART = mg.Particles()
HEAD = (540.0, 610.0)       # face anchor in the source framing


def shake_off(si):
    dx, dy = (C.trk[min(si, len(C.trk) - 1)] - C.ref)[:2]
    return float(np.clip(dx*0.8, -45, 45)), float(np.clip(dy*0.8, -55, 55))


def warp(img, M, border=cv2.BORDER_REFLECT):
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=border)


def virtual_bg(scene, f, si, sb):
    bg = C.load_bg(scene, f)
    M = mg.compose3(mg.affine_scale(sb, 540, 760), C.shake_matrix(si))
    return warp(bg, M)


def compose(f, room_rgb, fg):
    t = f/FPS
    si = C.src_index(f)
    A, B, p, tr = C.scene_state(t)
    sp, sb = CAM.scales(t, f)
    alpha = fg[..., 3].astype(np.float32)/255.0
    prgb = fg[..., :3].astype(np.float32)/255.0
    room = room_rgb.astype(np.float32)/255.0
    room_g = np.clip((room - 0.5)*1.08 + 0.5, 0, 1)*np.array([1.02, 1.0, 0.97], np.float32)
    room_g = C.room_overlays(room_g, f)

    def pM(dy):
        return mg.affine_scale(sp, HEAD[0], HEAD[1] + dy, dy)

    PA = C.PERSON[A]
    flash = 0.0; part_mix = [(A, 1.0)]
    if B is None:
        dy = PA['dy']; P = PA
        bg = warp(room_g, pM(0), cv2.BORDER_REPLICATE) if A == 'room' else virtual_bg(A, f, si, sb)
    else:
        PB = C.PERSON[B]; typ = tr['type']; e = mg.ease(p)
        bgB = virtual_bg(B, f, si, sb)
        part_mix = [(A, 1 - e), (B, e)]
        if typ == 'lightsout':
            dy = PB['dy']*e; P = C.lerp_params(PA, PB, e)
            k = min(1.0, p*2.2)
            flick = 1.0 - (0.5*abs(math.sin(p*40.0)) if 0.15 < p < 0.55 else 0.0)
            roomk = (1 - k)*flick
            bg = warp(room_g, pM(dy), cv2.BORDER_CONSTANT)*roomk + bgB*(1 - roomk)
        elif typ == 'sunrise':      # portal opening from behind the head
            dy = PB['dy']; P = C.lerp_params(PA, PB, e)
            bgA = virtual_bg(A, f, si, sb)
            bg, _ = mg.portal(bgA, bgB, p, HEAD[0], HEAD[1] + dy + 40, maxR=1650, ring_col=(1.0, 0.82, 0.55))
        elif typ in ('whipLeft', 'whipUp'):
            dy = PA['dy']*(1 - e) + PB['dy']*e; P = C.lerp_params(PA, PB, e)
            bgA = virtual_bg(A, f, si, sb)
            bg = mg.whip(bgA, bgB, p, typ == 'whipLeft')
        else:                       # shockwave into the studio
            dy = PB['dy']; P = C.lerp_params(PA, PB, e)
            bgA = virtual_bg(A, f, si, sb)
            bg, _ = mg.portal(bgA, bgB, p, 540, 520, maxR=1900, ring_col=(1.0, 1.0, 1.0), width=110)
            flash = max(0.0, 1.0 - abs(2*p - 0.6))*0.22
    # speaker
    M = pM(dy)
    alpha_s = warp(alpha, M, cv2.BORDER_CONSTANT); prgb_s = warp(prgb, M, cv2.BORDER_CONSTANT)
    if A == 'room' and B is None:
        lit = np.clip((prgb_s - 0.5)*1.08 + 0.5, 0, 1)*np.array([1.02, 1.0, 0.97], np.float32)
    else:
        lit = C.relight(prgb_s, alpha_s, P, bg)
    a3 = alpha_s[..., None]
    out = bg*(1 - a3) + lit*a3
    if flash > 0:
        out = out + flash*(1.0 - out)
    # foreground particles (in front of the speaker: depth layering)
    sh = shake_off(si)
    for sc, k in part_mix:
        out = PART.draw(out, sc, t, k, sh)
    # optics: bloom + anamorphic streaks (scene-aware threshold)
    out = mg.optics(np.clip(out, 0, 1.4), A if (B is None or p < 0.5) else B)
    # graphics
    out = np.clip(out, 0, 1)
    out = CHAP.draw(out, t)
    out = WAVE.draw(out, t)
    out = CAPS.draw(out, t)
    # finish: S-curve, vignette, edge chroma, grain
    out = np.clip(out, 0, 1)
    out = out + 0.06*(out - out*out)*np.where(out > 0.5, 1, -1)
    if not hasattr(compose, 'vig'):
        r2 = ((mg.XX - W/2)/(W*0.75))**2 + ((mg.YY - H/2)/(H*0.75))**2
        compose.vig = (1 - 0.2*np.clip(r2, 0, 1.5))[..., None].astype(np.float32)
    out = out*compose.vig
    out = mg.chroma_edges(out)
    g = cv2.resize(C.GRAIN[f % len(C.GRAIN)], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    lum = out.mean(2, keepdims=True)
    out = out + g*0.017*(0.4 + 0.6*np.sqrt(np.clip(lum*(1 - lum)*4, 0, 1)))
    return (np.clip(out, 0, 1)*255 + 0.5).astype(np.uint8)


def main():
    if sys.argv[1] == '--stills':
        outdir = sys.argv[2]; os.makedirs(outdir, exist_ok=True)
        want = sorted(int(x) for x in sys.argv[3].split(','))
        rs, rf = C.readers()
        for f in want:
            si = C.src_index(f)
            Image.fromarray(compose(f, rs.get(si), rf.get(si))).save(f'{outdir}/c_{f:05d}.png'); print('still', f, flush=True)
        return
    out = sys.argv[1]
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out],
                           stdin=subprocess.PIPE)
    rs, rf = C.readers(); t0 = time.time()
    for f in range(NF):
        si = C.src_index(f)
        enc.stdin.write(compose(f, rs.get(si), rf.get(si)).tobytes())
        if f % 30 == 0: print(f'comp2 {f}/{NF} {(time.time()-t0)/(f+1):.2f}s/f', flush=True)
    enc.stdin.close(); enc.wait(); print('done', out)


if __name__ == '__main__':
    main()
