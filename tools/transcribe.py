"""Local word-level transcription with faster-whisper. Usage: python3 tools/transcribe.py in.wav out.json [model]"""
import sys, json
import wave, numpy as np
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
model_name = sys.argv[3] if len(sys.argv) > 3 else "large-v3"
w = wave.open(src); audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768  # 16k mono wav from ffmpeg
m = WhisperModel(model_name, device="cpu", compute_type="int8")
segs, info = m.transcribe(audio, language="ar", word_timestamps=True, beam_size=5, vad_filter=False,
    initial_prompt="طبيب أسنان عراقي يتحدث باللهجة العراقية عن الأسنان والتقويم والحشوات والتبييض وعيادات القمة.")
data = {"model": model_name, "language": info.language, "duration": info.duration, "segments": []}
for s in segs:
    data["segments"].append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
        "words": [{"w": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2), "p": round(w.probability, 2)} for w in s.words]})
json.dump(data, open(out, "w"), ensure_ascii=False, indent=1)
for s in data["segments"]:
    print(s["start"], s["end"], s["text"])
    print("   ", " | ".join(f'{w["w"]}@{w["start"]}({w["p"]})' for w in s["words"]))
