#!/usr/bin/env python3
"""Person cut-out with Robust Video Matting (ONNX, CPU) -> transparent VP9 WebM for Remotion.
Usage: matte.py SRC.mp4 OUT_fg.webm [--model rvm_resnet50_fp32.onnx] [--ratio 0] [--width 1080] [--legacy]
Also writes OUT_fg.alpha.mp4 (grayscale matte, handy for QA).

v3 clean-up (after the first field test showed a dirty outline and a smoky microphone):
- ResNet50 RVM by default (mobilenet is the fallback): keeps things the speaker holds / talks into (podcast mics,
  stands, cables) solid instead of half-transparent smoke; ~3 fps on 2 CPUs.
- specks and far-away haze removed, small interior holes filled, body interior forced opaque.
- edge snapped to the image with a colour guided filter, then the soft transition tightened (no blurry rim).
- edge colours decontaminated: pixels in the soft rim take the subject's own colour (normalised convolution of the
  confident interior), so the source wall no longer shows as a grey/dark halo on cream or black paper.
"""
import argparse, json, os, subprocess, sys, time
import numpy as np
import onnxruntime as ort
from scipy.ndimage import binary_fill_holes, distance_transform_edt, gaussian_filter, label
import cv2

def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height,r_frame_rate,nb_frames:format=duration', '-of', 'json', path],
                         capture_output=True, text=True).stdout
    d = json.loads(out); s = d['streams'][0]
    num, den = s['r_frame_rate'].split('/')
    return int(s['width']), int(s['height']), float(num) / float(den), float(d['format']['duration'])

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)

def _box(x, r):
    return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1), borderType=cv2.BORDER_REFLECT)

def guided_filter(I, p, r=6, eps=2e-4, sub=2):
    """fast colour guided filter (He et al.): I HxWx3 float 0..1 guide, p HxW float -> HxW (edge-aware alpha)"""
    H, W = p.shape
    Is = cv2.resize(I, (W // sub, H // sub), interpolation=cv2.INTER_AREA)
    ps = cv2.resize(p, (W // sub, H // sub), interpolation=cv2.INTER_AREA)
    rs = max(1, r // sub)
    mI = [_box(Is[..., c], rs) for c in range(3)]
    mp = _box(ps, rs)
    cov = [_box(Is[..., c] * ps, rs) - mI[c] * mp for c in range(3)]
    v = {}
    for i in range(3):
        for j in range(i, 3):
            v[i, j] = _box(Is[..., i] * Is[..., j], rs) - mI[i] * mI[j] + (eps if i == j else 0)
    a11, a12, a13, a22, a23, a33 = v[0, 0], v[0, 1], v[0, 2], v[1, 1], v[1, 2], v[2, 2]
    i11 = a22 * a33 - a23 * a23; i12 = a13 * a23 - a12 * a33; i13 = a12 * a23 - a13 * a22
    i22 = a11 * a33 - a13 * a13; i23 = a12 * a13 - a11 * a23; i33 = a11 * a22 - a12 * a12
    det = a11 * i11 + a12 * i12 + a13 * i13
    ak = [(i11 * cov[0] + i12 * cov[1] + i13 * cov[2]) / det,
          (i12 * cov[0] + i22 * cov[1] + i23 * cov[2]) / det,
          (i13 * cov[0] + i23 * cov[1] + i33 * cov[2]) / det]
    b = mp - ak[0] * mI[0] - ak[1] * mI[1] - ak[2] * mI[2]
    ma = [cv2.resize(_box(x, rs), (W, H), interpolation=cv2.INTER_LINEAR) for x in ak]
    mb = cv2.resize(_box(b, rs), (W, H), interpolation=cv2.INTER_LINEAR)
    return ma[0] * I[..., 0] + ma[1] * I[..., 1] + ma[2] * I[..., 2] + mb

def clean_alpha(img, al, margin, gf_r, tight):
    H, W = al.shape
    al = np.clip((al - 0.02) / 0.96, 0, 1)
    core = al > 0.5
    lab, n = label(core)
    if n > 1:  # specks: keep only blobs >= 2 % of the biggest one (body); their haze goes too
        sizes = np.bincount(lab.ravel()); sizes[0] = 0
        core = (sizes >= 0.02 * sizes.max())[lab]
    if n:
        far = distance_transform_edt(~core[::4, ::4]) > 6   # > ~24 px from the body = haze / smoke
        far = cv2.resize(far.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST).astype(bool)
        al = np.where(far, 0.0, al)
    holes = binary_fill_holes(core) & ~core  # shiny forehead, glare - small interior holes only
    if holes.any():
        hl, hn = label(holes)
        sizes = np.bincount(hl.ravel())
        small = np.isin(hl, np.nonzero((sizes < 0.01 * al.size) & (np.arange(len(sizes)) > 0))[0])
        al = np.where(small, 1.0, al)
    # body interior fully opaque (computed at 1/4 res; keeps a soft margin along the outline)
    lo = al[::4, ::4] > 0.15
    inner = (distance_transform_edt(lo) > margin).astype(np.float32)
    inner = cv2.resize(gaussian_filter(inner, 1.2), (W, H), interpolation=cv2.INTER_LINEAR)
    al = np.maximum(al, np.clip(inner * 1.25 - 0.1, 0, 1)).astype(np.float32)
    if gf_r:  # snap the outline to the real edge in the picture
        al = guided_filter(img.astype(np.float32) / 255, al, gf_r, 2e-4)
    return smoothstep(tight[0], tight[1], np.clip(al, 0, 1)).astype(np.float32)

def decontaminate(img, al, lo=0.55, hi=0.985):
    """soft-rim pixels take the subject's own colour (normalised convolution of the confident interior, at 1/2 res)"""
    H, W = al.shape
    f = img.astype(np.float32) / 255
    fs = cv2.resize(f, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    conf = (cv2.resize(al, (W // 2, H // 2), interpolation=cv2.INTER_AREA) > 0.97).astype(np.float32)
    ext = None
    for s in (1.5, 5.0, 14.0):
        num = cv2.GaussianBlur(fs * conf[..., None], (0, 0), s)
        den = cv2.GaussianBlur(conf, (0, 0), s)[..., None]
        e = num / np.maximum(den, 1e-4)
        ext = e if ext is None else np.where(den > 0.03, e, ext)
    ext = cv2.resize(ext, (W, H), interpolation=cv2.INTER_LINEAR)
    out = img.copy()
    band = (al > 0.002) & (al < hi)  # only the rim changes (a few % of the pixels)
    w = smoothstep(lo, hi, al[band])[:, None]
    out[band] = (np.clip(f[band] * w + ext[band] * (1 - w), 0, 1) * 255 + 0.5).astype(np.uint8)
    return out

def legacy_alpha(al, margin, W, H):
    al = np.clip((al - 0.04) / 0.92, 0, 1)
    hard = al > 0.5
    holes = binary_fill_holes(hard) & ~hard
    if holes.any():
        lab, nlab = label(holes)
        if nlab:
            sizes = np.bincount(lab.ravel())
            small = np.isin(lab, np.nonzero((sizes < 0.01 * al.size) & (np.arange(len(sizes)) > 0))[0])
            al = np.where(small, 1.0, al)
    lo = al[::4, ::4] > 0.15
    inner = (distance_transform_edt(lo) > margin).astype(np.float32)
    inner = cv2.resize(gaussian_filter(inner, 1.2), (W, H), interpolation=cv2.INTER_LINEAR)
    return np.maximum(al, np.clip(inner * 1.25 - 0.1, 0, 1))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out')
    m = os.path.expanduser('~/models')
    ap.add_argument('--model', default=None, help='default: rvm_resnet50_fp32.onnx, else rvm_mobilenetv3_fp32.onnx')
    ap.add_argument('--ratio', type=float, default=0.0, help='downsample ratio (0=auto: ~512px long side)')
    ap.add_argument('--width', type=int, default=0, help='resize width (0=keep)')
    ap.add_argument('--threads', type=int, default=0)
    ap.add_argument('--gf', type=int, default=6, help='guided-filter radius for the edge snap (0=off)')
    ap.add_argument('--tight', default='0.12,0.88', help='alpha remap lo,hi (tightens the soft rim)')
    ap.add_argument('--crf', type=int, default=24)
    ap.add_argument('--legacy', action='store_true', help='v2 behaviour: no edge snap, no colour decontamination')
    a = ap.parse_args()
    model = a.model or next((p for p in (f'{m}/rvm_resnet50_fp32.onnx', f'{m}/rvm_mobilenetv3_fp32.onnx') if os.path.exists(p)), None)
    if not model: sys.exit('no RVM model in ~/models (run scripts/assets.sh)')
    if 'mobilenet' in model and not a.model:
        print('note: rvm_resnet50_fp32.onnx missing - mobilenet fallback (mics / held objects may come out smoky)', flush=True)
    W, H, fps, dur = probe(a.src)
    if a.width and a.width != W:
        H = int(round(H * a.width / W / 2) * 2); W = a.width
    ratio = a.ratio or min(1.0, 512 / max(W, H))
    tight = tuple(float(x) for x in a.tight.split(','))
    so = ort.SessionOptions()
    if a.threads: so.intra_op_num_threads = a.threads
    sess = ort.InferenceSession(model, so, providers=['CPUExecutionProvider'])
    rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    dr = np.array([ratio], np.float32)
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', a.src, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', f'{fps}', '-i', '-',
                            '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', str(a.crf), '-deadline', 'realtime',
                            '-cpu-used', '8', '-row-mt', '1', '-auto-alt-ref', '0', a.out], stdin=subprocess.PIPE)
    alpha_enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{W}x{H}', '-r', f'{fps}', '-i', '-',
                                  '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', a.out.rsplit('.', 1)[0] + '.alpha.mp4'],
                                 stdin=subprocess.PIPE)
    n = 0; t0 = time.time(); fsize = W * H * 3
    margin = max(3.0, 0.012 * H / 4)
    fade = max(2, int(0.03 * H)); yy = np.arange(H, dtype=np.float32)
    top_ramp = np.clip(yy / fade, 0, 1); top_ramp = (top_ramp * top_ramp * (3 - 2 * top_ramp))[:, None]
    print(f'model {os.path.basename(model)}, ratio {ratio:.3f}, {"legacy" if a.legacy else "clean"} post', flush=True)
    while True:
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize: break
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        src = (img.astype(np.float32) / 255.0).transpose(2, 0, 1)[None]
        fgr, pha, *rec = sess.run(None, {'src': src, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': dr})
        al = np.clip(pha[0, 0], 0, 1)
        if a.legacy:
            al = legacy_alpha(al, margin, W, H) * top_ramp
            col = img
        else:
            al = clean_alpha(img, al, margin, a.gf, tight) * top_ramp  # soften the source's top edge (heads cut by the frame)
            col = decontaminate(img, al)
        a8 = (al * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(np.dstack([col, a8]).tobytes()); alpha_enc.stdin.write(a8.tobytes())
        n += 1
        if n % 60 == 0:
            el = time.time() - t0
            print(f'{n} frames, {n / el:.2f} fps, eta {(dur * fps - n) / (n / el):.0f}s', flush=True)
    enc.stdin.close(); alpha_enc.stdin.close(); enc.wait(); alpha_enc.wait(); dec.wait()
    print(f'done {n} frames in {time.time() - t0:.0f}s ->', a.out)

if __name__ == '__main__':
    main()
