#!/usr/bin/env python3
"""
أضف شعار خيبر على صورة أو فيديو — KHAYBAR 2.0 (needs ffmpeg/ffprobe only).

  python3 add_logo.py INPUT [-o OUTPUT] [--mode auto|watermark|outro|both]
                      [--corner top-left|top-right|bottom-left|bottom-right]
                      [--size 0.11] [--opacity 0.9] [--variant mark|mono|flat|cinematic]
                      [--short-outro]

Defaults: image -> watermark in the top-left corner.
          video -> watermark on the whole video + official outro appended.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
LOGOS = {
    "mark": "logo/khaybar-mark-on-image-512.png",
    "mono": "logo/khaybar-logo-mono-ivory-1024.png",
    "flat": "logo/khaybar-logo-flat-1024.png",
    "cinematic": "logo/khaybar-logo-cinematic-1024.png",
}
OUTRO = {False: "video/khaybar-outro.mp4", True: "video/khaybar-outro-short.mp4"}
BG = "0x071F26"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg failed:\n" + r.stderr[-2000:])
    return r.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries",
               "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", path])
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    num, den = (v.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1) if float(num) else 30.0
    return int(v["width"]), int(v["height"]), has_audio, fps, float(d["format"].get("duration") or 0)


def position(W, H, corner, logo_w):
    m = round(W * 0.045)
    vertical = H > W * 1.3
    top = max(m, round(H * 0.094)) if vertical else m          # clear the platform's top bar
    bottom = max(m, round(H * 0.22)) if vertical else m        # clear caption / account name
    right = max(m, round(W * 0.14)) if vertical else m         # clear the like/comment buttons
    x = m if "left" in corner else W - logo_w - right
    y = top if corner.startswith("top") else H - logo_w - bottom
    return x, y


def watermark_filter(W, H, a):
    lw = max(48, round(W * a.size))
    x, y = position(W, H, a.corner, lw)
    return (f"[1:v]scale={lw}:-1:flags=lanczos,format=rgba,colorchannelmixer=aa={a.opacity}[lg];"
            f"[0:v][lg]overlay={x}:{y}:format=auto"), lw, (x, y)


def main():
    ap = argparse.ArgumentParser(description="Add the KHAYBAR logo to an image or a video.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--mode", default="auto", choices=["auto", "watermark", "outro", "both"])
    ap.add_argument("--corner", default="top-left", choices=["top-left", "top-right", "bottom-left", "bottom-right"])
    ap.add_argument("--size", type=float, default=0.11, help="logo width as a fraction of the frame width")
    ap.add_argument("--opacity", type=float, default=0.9)
    ap.add_argument("--variant", default="mark", choices=list(LOGOS))
    ap.add_argument("--short-outro", action="store_true")
    a = ap.parse_args()
    a.opacity = min(1.0, max(0.6, a.opacity))  # keep the mark legible

    src = a.input
    is_image = os.path.splitext(src)[1].lower() in IMAGE_EXT
    base, ext = os.path.splitext(src)
    out = a.output or f"{base}-khaybar{'.png' if is_image and ext.lower() == '.png' else ('.jpg' if is_image else '.mp4')}"
    logo = os.path.join(ASSETS, LOGOS[a.variant])
    W, H, has_audio, fps, dur = probe(src)

    if is_image:
        f, lw, xy = watermark_filter(W, H, a)
        run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", logo, "-filter_complex", f,
             "-frames:v", "1", "-update", "1", "-q:v", "2", out])
        print(json.dumps(dict(output=out, type="image", size=[W, H], logo_width=lw, position=xy)))
        return

    mode = "both" if a.mode == "auto" else a.mode
    fps = round(fps) if fps else 30
    outro = os.path.join(ASSETS, OUTRO[a.short_outro])
    o_dur = probe(outro)[4]
    inputs = ["-i", src, "-i", logo]
    chain = []
    if mode in ("watermark", "both"):
        f, lw, xy = watermark_filter(W, H, a)
        chain.append(f + "[wm]")
        main_v = "[wm]"
    else:
        main_v, xy, lw = "[0:v]", None, 0
    if mode in ("outro", "both"):
        inputs += ["-i", outro, "-f", "lavfi", "-t", f"{o_dur}", "-i", "anullsrc=r=48000:cl=stereo"]
        chain.append(f"{main_v}fps={fps},format=yuv420p,setsar=1[v0]")
        chain.append(f"[2:v]fps={fps},scale={W}:{H}:force_original_aspect_ratio=decrease,"
                     f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={BG},format=yuv420p,setsar=1[v1]")
        if has_audio:
            chain.append("[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];[3:a]aformat=channel_layouts=stereo[a1]")
            chain.append("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
            maps = ["-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
        else:
            chain.append("[v0][v1]concat=n=2:v=1:a=0[v]")
            maps = ["-map", "[v]"]
    else:
        chain.append(f"{main_v}format=yuv420p[v]")
        maps = ["-map", "[v]"] + (["-map", "0:a", "-c:a", "copy"] if has_audio else [])
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chain), *maps,
         "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-movflags", "+faststart", out])
    total = probe(out)[4]
    print(json.dumps(dict(output=out, type="video", mode=mode, size=[W, H], logo_width=lw, position=xy,
                          input_seconds=round(dur, 2), output_seconds=round(total, 2))))


if __name__ == "__main__":
    main()
