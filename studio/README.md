# Ammar Motion Studio (zero-install)

Frame-accurate motion graphics for vertical medical/commercial videos.
Uses only tools already on the machine: Chromium (Playwright), FFmpeg, Python, faster-whisper.

- `lib/motion.js` — interpolate / spring / presence / easing (Remotion-style API).
- `lib/components.js` — GlassCard, KineticWord, DotRow, Clock, AnimatedNumber, MapPin, LowerThird,
  ToothIcon, BracesIllustration, Captions, Logo.
- `lib/stage.html` — 1080x1920 stage (Tajawal, RTL).
- `render.mjs` — renders a project's `composition.js` and encodes H.264/AAC (voice cleanup + SFX mix).
- `assets/sfx/` — locally synthesised subtle SFX.
- `../tools/transcribe.py` — local word-level transcription.

```
python3 tools/transcribe.py audio16k.wav analysis/02-transcript.raw.json
node studio/render.mjs projects/<name> <source.mp4> --still 30,120     # preview frames
node studio/render.mjs projects/<name> <source.mp4> --out out.mp4      # full render
```
A project folder holds `brand/`, `analysis/*.json` and `composition.js`.
