# CINEMATIC REALITY engine (v2 motion graphics)

Turns a talking-head selfie into a 9:16 cinematic edit: real-time-raymarched 3D worlds (black studio + volumetric
spot, mountains with valley fog, ocean, waving flags, physics spheres, extruded 3D Arabic/Latin text) rendered in
headless Chromium (WebGL2 / SwiftShader, CPU only), the matted speaker relit into each world, and the v2
motion-graphics layer (virtual camera, portal / whip / shockwave transitions, kinetic Arabic captions, chapter
markers, voice waveform, foreground bokeh, bloom + anamorphic streaks).

Layout: engine/ (all code, run from here)  engine/tex/ (flag textures)  fonts/ (OFL)  scripts/ (ASR + matte)

Run order (cwd = engine/):
 1  ffmpeg ingest -> src/raw.mp4 (30 fps, 1080x1920, audio aac)
 2  ASR: scripts/whisper_onnx.py <sherpa-onnx-whisper-large-v3|turbo dir> audio16.wav seg.json --lang ar
    (models: github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-*.tar.bz2)
 3  matte: python3 ../scripts/matte.py src/raw.mp4 src/raw_fg.webm   (needs ~/models/rvm_resnet50_fp32.onnx)
 4  python3 track.py src/raw.mp4 src/raw_fg.webm track.json
 5  edit plan.py for the new video: SEGS_SRC (speech islands + kept gaps), W (word cues), CAPS_SRC/ACCENT,
    scene schedule + per-scene camera/text uniforms, PERSON grades; then python3 plan.py
 6  3D text: python3 make_sdf.py "<word>" ../fonts/Vazirmatn-Black.ttf tex/<name>.npy --box 6
 7  renders: for k in <jobs>; do python3 render.py job_$k.json; done   (renders/<scene>/<frame>.png)
 8  audio_edit.wav: concat the EDL segments with 12/15 ms fades + highpass 60 + loudnorm I=-16
 9  python3 comp2.py out/video.mp4 ; ffmpeg mux with audio_edit.wav (-c:v copy -c:a aac 192k -shortest)
 QA: python3 comp2.py --stills test 0,120,... before the full pass.
Chromium flags (in render.py): --use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist
