#!/usr/bin/env python3
"""Whisper (sherpa-onnx export) transcription with timestamp tokens, numpy + onnxruntime only.
Usage: whisper_onnx.py MODEL_DIR AUDIO.wav OUT.json [--lang ar] [--prompt TEXT]
"""
import sys, json, base64, argparse, subprocess
import numpy as np
import onnxruntime as ort

SR = 16000; N_FFT = 400; HOP = 160; CHUNK = 30; N_SAMPLES = SR * CHUNK; N_FRAMES = 3000


def mel_filters(n_mels, sr=SR, n_fft=N_FFT):
    def hz_to_mel(f):
        f = np.asarray(f, dtype=np.float64)
        f_sp = 200.0 / 3; mels = f / f_sp
        min_log_hz = 1000.0; min_log_mel = min_log_hz / f_sp; logstep = np.log(6.4) / 27.0
        return np.where(f >= min_log_hz, min_log_mel + np.log(np.maximum(f, 1e-10) / min_log_hz) / logstep, mels)

    def mel_to_hz(m):
        m = np.asarray(m, dtype=np.float64)
        f_sp = 200.0 / 3; freqs = f_sp * m
        min_log_hz = 1000.0; min_log_mel = min_log_hz / f_sp; logstep = np.log(6.4) / 27.0
        return np.where(m >= min_log_mel, min_log_hz * np.exp(logstep * (m - min_log_mel)), freqs)

    fftfreqs = np.linspace(0, sr / 2, 1 + n_fft // 2)
    mel_f = mel_to_hz(np.linspace(hz_to_mel(0.0), hz_to_mel(sr / 2), n_mels + 2))
    fdiff = np.diff(mel_f)
    ramps = mel_f[:, None] - fftfreqs[None, :]
    w = np.zeros((n_mels, len(fftfreqs)))
    for i in range(n_mels):
        lower = -ramps[i] / fdiff[i]; upper = ramps[i + 2] / fdiff[i + 1]
        w[i] = np.maximum(0, np.minimum(lower, upper))
    enorm = 2.0 / (mel_f[2:n_mels + 2] - mel_f[:n_mels])
    return (w * enorm[:, None]).astype(np.float32)


def log_mel(audio, n_mels, filt):
    audio = np.concatenate([audio, np.zeros(N_SAMPLES, np.float32)])
    pad = N_FFT // 2
    x = np.pad(audio, (pad, pad), mode='reflect')
    win = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N_FFT) / N_FFT)).astype(np.float32)
    n = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    frames = x[idx] * win
    spec = np.abs(np.fft.rfft(frames, axis=1)) ** 2  # (n, 201)
    spec = spec[:-1].T
    mel = filt @ spec
    logs = np.log10(np.maximum(mel, 1e-10))
    logs = np.maximum(logs, logs.max() - 8.0)
    return ((logs + 4.0) / 4.0).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model_dir'); ap.add_argument('audio'); ap.add_argument('out')
    ap.add_argument('--lang', default='ar'); ap.add_argument('--prompt', default='')
    ap.add_argument('--beam', type=int, default=1)
    a = ap.parse_args()
    md = a.model_dir.rstrip('/'); name = md.split('/')[-1].replace('sherpa-onnx-whisper-', '')
    so = ort.SessionOptions(); so.intra_op_num_threads = 2; so.enable_cpu_mem_arena = False; so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
    enc = ort.InferenceSession(f'{md}/{name}-encoder.int8.onnx', so, providers=['CPUExecutionProvider'])
    dec = ort.InferenceSession(f'{md}/{name}-decoder.int8.onnx', so, providers=['CPUExecutionProvider'])
    meta = enc.get_modelmeta().custom_metadata_map
    n_mels = int(meta['n_mels']); n_layer = int(meta['n_text_layer']); n_ctx = int(meta['n_text_ctx']); n_state = int(meta['n_text_state'])
    sot = int(meta['sot']); eot = int(meta['eot']); transcribe = int(meta['transcribe']); no_ts = int(meta['no_timestamps'])
    sot_prev = int(meta['sot_prev']); blank = int(meta['blank_id'])
    langs = dict(zip(meta['all_language_codes'].split(','), map(int, meta['all_language_tokens'].split(','))))
    non_speech = [int(t) for t in meta['non_speech_tokens'].split(',') if t]
    ts_begin = no_ts + 1
    vocab = {}
    for line in open(f'{md}/{name}-tokens.txt', encoding='utf-8'):
        p = line.rstrip('\n').split(' ')
        if len(p) == 2:
            vocab[int(p[1])] = base64.b64decode(p[0])

    def detok(ids):
        return b''.join(vocab.get(i, b'') for i in ids if i < eot).decode('utf-8', errors='ignore')

    # prompt tokens (greedy longest-match tokenisation via reverse vocab, best effort)
    prompt_ids = []
    if a.prompt:
        rev = {v: k for k, v in vocab.items()}
        b = (' ' + a.prompt).encode('utf-8'); i = 0
        while i < len(b):
            for j in range(min(len(b), i + 24), i, -1):
                if b[i:j] in rev:
                    prompt_ids.append(rev[b[i:j]]); i = j; break
            else:
                i += 1

    audio = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', a.audio, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                                         capture_output=True).stdout, np.int16).astype(np.float32) / 32768.0
    filt = mel_filters(n_mels)
    mel_all = log_mel(audio, n_mels, filt)  # (n_mels, frames)
    total_frames = int(len(audio) / HOP)
    sot_seq = [sot, langs[a.lang], transcribe]
    suppress = set(non_speech) | {sot, sot_prev, int(meta['sot_lm']), int(meta['no_speech']), int(meta['translate']), transcribe, no_ts} | set(langs.values())
    supp_idx = np.array(sorted(suppress), dtype=np.int64)

    segments = []
    seek = 0
    while seek < total_frames - 20:
        mel = mel_all[:, seek:seek + N_FRAMES]
        if mel.shape[1] < N_FRAMES:
            mel = np.pad(mel, ((0, 0), (0, N_FRAMES - mel.shape[1])), constant_values=mel_all.min())
        seg_dur = min(N_FRAMES, total_frames - seek) * HOP / SR
        ck, cv = enc.run(None, {'mel': mel[None]})
        k = np.zeros((n_layer, 1, n_ctx, n_state), np.float32); v = np.zeros_like(k)
        prefix = ([sot_prev] + prompt_ids[-200:] if prompt_ids else []) + sot_seq
        toks = np.array([prefix], np.int64); offset = np.zeros(1, np.int64)
        out = []
        for step in range(220):
            logits, k, v = dec.run(None, {'tokens': toks, 'in_n_layer_self_k_cache': k, 'in_n_layer_self_v_cache': v,
                                          'n_layer_cross_k': ck, 'n_layer_cross_v': cv, 'offset': offset})
            offset = offset + toks.shape[1]
            lg = logits[0, -1].astype(np.float64).copy()
            lg[supp_idx] = -np.inf
            if step == 0:
                lg[blank] = -np.inf; lg[eot] = -np.inf
                lg[:ts_begin] = -np.inf  # must start with a timestamp
                lg[ts_begin + 50 + 1:] = -np.inf  # max initial timestamp 1.0 s
            else:
                last_ts = out[-1] >= ts_begin
                pen_ts = len(out) < 2 or out[-2] >= ts_begin
                if last_ts:
                    if pen_ts:
                        lg[ts_begin:] = -np.inf
                    else:
                        lg[:eot] = -np.inf
                prev_ts = [t for t in out if t >= ts_begin]
                if prev_ts:
                    lo = prev_ts[-1] if (last_ts and not pen_ts) else prev_ts[-1] + 1
                    lg[ts_begin:lo] = -np.inf
                # beyond segment end -> forbid
                maxts = ts_begin + int(seg_dur / 0.02)
                lg[maxts + 1:] = -np.inf
                # timestamp prob mass rule
                m = lg.max(); p = np.exp(lg - m); p /= p.sum()
                with np.errstate(divide='ignore'):
                    lp = np.log(p)
                ts_lp = np.logaddexp.reduce(lp[ts_begin:]) if np.isfinite(lp[ts_begin:]).any() else -np.inf
                if ts_lp > lp[:ts_begin].max():
                    lg[:ts_begin] = -np.inf
            t = int(np.argmax(lg))
            if t == eot:
                break
            out.append(t)
            toks = np.array([[t]], np.int64)
        # parse timestamp pairs
        cur = None; text_ids = []; last_end = None; local = []
        for t in out:
            if t >= ts_begin:
                ts = (t - ts_begin) * 0.02
                if cur is None:
                    cur = ts; text_ids = []
                else:
                    if text_ids:
                        local.append((cur, ts, detok(text_ids)))
                    last_end = ts; cur = None
                    text_ids = []
            else:
                text_ids.append(t)
        if cur is not None and text_ids:
            local.append((cur, seg_dur, detok(text_ids))); last_end = seg_dur
        base = seek * HOP / SR
        for s0, e0, tx in local:
            segments.append({'s': round(base + s0, 2), 'e': round(base + e0, 2), 'text': tx.strip()})
            print(f'{base+s0:6.2f}-{base+e0:6.2f} {tx.strip()}', flush=True)
        if prompt_ids is not None:
            prompt_ids = prompt_ids + [i for i in out if i < eot]
        if last_end is None or seg_dur < CHUNK - 0.5 or last_end <= 0.5:
            seek += N_FRAMES
        else:
            seek += int(round(last_end * SR / HOP))
    json.dump({'segments': segments}, open(a.out, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
