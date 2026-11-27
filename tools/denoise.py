"""Local spectral denoiser (numpy only).
Learns a noise profile from given quiet ranges, applies a smoothed Wiener-style gain with a floor,
so speech stays natural. Usage: python3 tools/denoise.py in.wav out.wav 5.55-5.95,10.0-10.35,12.6-13.4 [strength]"""
import sys, wave, numpy as np
src, dst, ranges = sys.argv[1], sys.argv[2], sys.argv[3]
k = float(sys.argv[4]) if len(sys.argv) > 4 else 1.6
w = wave.open(src); sr = w.getframerate(); ch = w.getnchannels()
a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
if ch > 1: a = a.reshape(-1, ch).mean(1)
n, hop = 2048, 512
win = np.sqrt(np.hanning(n + 1)[:-1])
pad = np.concatenate([np.zeros(n), a, np.zeros(n)])
frames = np.stack([pad[i:i + n] * win for i in range(0, len(pad) - n, hop)])
S = np.fft.rfft(frames, axis=1); P = np.abs(S) ** 2
t = (np.arange(len(frames)) * hop - n) / sr
mask = np.zeros(len(frames), bool)
for r in ranges.split(','):
    s, e = map(float, r.split('-')); mask |= (t >= s) & (t + n / sr <= e)
noise = np.median(P[mask], axis=0) * 1.0 + np.mean(P[mask], axis=0) * 0.5
# a-priori SNR (decision-directed) Wiener gain
G = np.ones_like(P); prev = np.zeros(P.shape[1])
for i in range(len(P)):
    post = np.maximum(P[i] / (k * noise + 1e-12) - 1, 0)
    prio = 0.96 * (prev / (k * noise + 1e-12)) + 0.04 * post
    g = prio / (1 + prio); G[i] = g; prev = (g ** 2) * P[i]
floor = 10 ** (-18 / 20)                     # max 18 dB reduction: avoids "underwater" artefacts
G = np.maximum(G, floor)
# smooth gains across frequency and time to suppress musical noise
ker = np.ones(5) / 5
G = np.apply_along_axis(lambda r: np.convolve(r, ker, 'same'), 1, G)
G = np.apply_along_axis(lambda c: np.convolve(c, np.ones(3) / 3, 'same'), 0, G)
Y = np.fft.irfft(S * G, n, axis=1) * win
out = np.zeros(len(pad))
for j, i in enumerate(range(0, len(pad) - n, hop)): out[i:i + n] += Y[j]
out = out[n:n + len(a)] / (np.sum(win ** 2) / hop)
out = np.clip(out, -1, 1)
o = wave.open(dst, 'w'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
o.writeframes((out * 32767).astype(np.int16).tobytes()); o.close()
print('noise frames used:', int(mask.sum()))
