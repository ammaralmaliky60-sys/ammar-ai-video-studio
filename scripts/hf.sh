#!/usr/bin/env bash
# Run the pinned HyperFrames CLI.
# Uses the installed Claude Code plugin's launcher when present (pins the plugin's CLI version),
# otherwise falls back to the exact npm version pinned below.
set -euo pipefail
HF_VERSION="${HF_VERSION:-0.9.9}"
PLUGIN_CLI="$(ls -d "$HOME"/.claude/plugins/cache/hyperframes/hyperframes/*/skills/hyperframes/scripts/plugin-cli.mjs 2>/dev/null | sort -V | tail -1 || true)"
if [[ -n "${PLUGIN_CLI}" && -f "${PLUGIN_CLI}" ]]; then
  exec node "${PLUGIN_CLI}" "$@"
else
  exec npx --yes "hyperframes@${HF_VERSION}" "$@"
fi
