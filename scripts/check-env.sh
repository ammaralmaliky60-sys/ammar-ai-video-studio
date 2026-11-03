#!/usr/bin/env bash
# Verify the machine can build and render HyperFrames videos.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
node_major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
if (( node_major >= 22 )); then echo "✓ Node.js $(node -v)"; else echo "✗ Node.js 22+ required (found: $(node -v 2>/dev/null || echo none))"; fail=1; fi
if command -v ffmpeg >/dev/null; then echo "✓ $(ffmpeg -version | head -1 | cut -d' ' -f1-3)"; else echo "✗ FFmpeg not found"; fail=1; fi
if command -v ffprobe >/dev/null; then echo "✓ ffprobe present"; else echo "✗ ffprobe not found"; fail=1; fi
echo "— hyperframes doctor —"
"$ROOT/scripts/hf.sh" doctor --json 2>/dev/null \
  | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const j=JSON.parse(s.slice(s.indexOf("{")));for(const c of j.checks||[])console.log(`${c.ok?"✓":"·"} ${c.name}: ${c.detail}`);})' \
  || echo "(doctor output could not be parsed)"
exit $fail
