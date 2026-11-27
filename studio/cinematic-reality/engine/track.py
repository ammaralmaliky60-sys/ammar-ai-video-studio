#!/usr/bin/env python3
"""Track the handheld camera motion from the static room background (person masked out).
Writes per-source-frame cumulative similarity motion of the background in output pixels (1080x1920):
  {fps, frames:[{dx,dy,rot,scale}]}
"""
import json, subprocess, sys
import numpy as np, cv2

SRC = sys.argv[1]; FG = sys.argv[2]; OUT = sys.argv[3]
W, H = 540, 960; S = 1080 / W


def frames_rgb(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W*H)
        if len(b) < W*H: break
        yield np.frombuffer(b, np.uint8).reshape(H, W)


def frames_alpha(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-i', path, '-vf', f'scale={W}:{H},format=rgba', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W*H*4)
        if len(b) < W*H*4: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 4)[..., 3]


prev = None; prev_mask = None
acc = np.eye(3)
res = []
for i, (g, al) in enumerate(zip(frames_rgb(SRC), frames_alpha(FG))):
    mask = (cv2.dilate((al > 20).astype(np.uint8), np.ones((25, 25), np.uint8)) == 0).astype(np.uint8)*255
    if prev is not None:
        m = cv2.bitwise_and(mask, prev_mask)
        pts = cv2.goodFeaturesToTrack(prev, 400, 0.005, 8, mask=m)
        M = None
        if pts is not None and len(pts) > 12:
            nxt, st, err = cv2.calcOpticalFlowPyrLK(prev, g, pts, None, winSize=(31, 31), maxLevel=3)
            ok = st.ravel() == 1
            if ok.sum() > 10:
                M, inl = cv2.estimateAffinePartial2D(pts[ok], nxt[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
        if M is None:
            M = np.array([[1, 0, 0], [0, 1, 0]], float)
        acc = np.vstack([M, [0, 0, 1]]) @ acc
    a = acc
    sc = float(np.sqrt(a[0, 0]**2 + a[1, 0]**2)); rot = float(np.arctan2(a[1, 0], a[0, 0]))
    res.append({'dx': float(a[0, 2]*S), 'dy': float(a[1, 2]*S), 'rot': rot, 'scale': sc})
    prev, prev_mask = g, mask
    if i % 100 == 0:
        print(i, res[-1], flush=True)
json.dump({'fps': 30, 'frames': res}, open(OUT, 'w'))
print('frames', len(res))
