#!/usr/bin/env bash
# Create a new HyperFrames project under projects/.
#   scripts/new-project.sh <name> [template]      e.g. scripts/new-project.sh eid-promo title-card-5s
# Without a template you get HyperFrames' own blank scaffold.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="${1:?usage: new-project.sh <name> [template]}"
TEMPLATE="${2:-}"
[[ "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "✗ name must be kebab-case (a-z, 0-9, -)"; exit 1; }
DEST="$ROOT/projects/$NAME"
[[ -e "$DEST" ]] && { echo "✗ $DEST already exists"; exit 1; }
cd "$ROOT/projects"
"$ROOT/scripts/hf.sh" init "$NAME" --non-interactive
if [[ -n "$TEMPLATE" ]]; then
  SRC="$ROOT/templates/$TEMPLATE"
  [[ -d "$SRC" ]] || { echo "✗ unknown template: $TEMPLATE (see templates/)"; exit 1; }
  cp -R "$SRC/." "$DEST/"
fi
mkdir -p "$DEST/assets/fonts" "$DEST/assets/media" "$DEST/compositions" "$DEST/renders"
echo "✓ projects/$NAME ready${TEMPLATE:+ (from template $TEMPLATE)}"
echo "  next: scripts/render.sh $NAME draft"
