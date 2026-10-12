#!/usr/bin/env bash
# Draw docs/keymap.svg (Moonlander) and docs/ferris-keymap.svg (Ferris).
# Used by both `nix run` and the Build Ferris layout workflow.
# Needs python3 and keymap-drawer (`keymap` CLI) on PATH.
set -euo pipefail

root="${1:-$PWD}"
mkdir -p "$root/docs"

python3 "$root/keymap-viz/keymap2yaml.py" "$root/RgoVP/keymap.c" \
  > "$root/keymap-viz/keymap.yaml"
keymap draw "$root/keymap-viz/keymap.yaml" > "$root/docs/keymap.svg"
echo "Wrote $root/docs/keymap.svg"

python3 "$root/ferris/generate.py"
python3 "$root/keymap-viz/keymap2yaml.py" "$root/ferris/keymap.c" \
  > "$root/keymap-viz/ferris-keymap.yaml"
keymap draw "$root/keymap-viz/ferris-keymap.yaml" > "$root/docs/ferris-keymap.svg"
echo "Wrote $root/docs/ferris-keymap.svg"
