#!/usr/bin/env bash
# Check, render and VERIFY a project. Success is reported only after ffprobe reads the file.
#   scripts/render.sh <project> [draft|looks|delivery]   (default: delivery)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:?usage: render.sh <project> [draft|looks|delivery]}"
QUALITY="${2:-delivery}"
DIR="$ROOT/projects/$NAME"
[[ -f "$DIR/index.html" ]] || { echo "✗ no project at $DIR"; exit 1; }
cd "$DIR"
mkdir -p renders
OUT="renders/$NAME.mp4"
"$ROOT/scripts/hf.sh" lint
"$ROOT/scripts/hf.sh" check
rm -f "$OUT"
"$ROOT/scripts/hf.sh" render --quality "$QUALITY" -o "$OUT"

# --- verification -----------------------------------------------------------
[[ -s "$OUT" ]] || { echo "✗ render produced no file: $OUT"; exit 1; }
expected="$(node -e 'const m=require("fs").readFileSync("index.html","utf8").match(/data-composition-id="main"[^>]*?data-duration="([\d.]+)"/);process.stdout.write(m?m[1]:"")')"
actual="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
frames="$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$OUT")"
echo "✓ $DIR/$OUT"
echo "  size: $(du -h "$OUT" | cut -f1) · duration: ${actual}s (root data-duration: ${expected:-?}s) · frames: $frames"
if [[ -n "$expected" ]]; then
  node -e "process.exit(Math.abs($actual-$expected) <= 0.1 ? 0 : 1)" \
    || { echo "✗ duration mismatch"; exit 1; }
fi
