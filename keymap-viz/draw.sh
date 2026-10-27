#!/usr/bin/env bash
# Draw docs/keymap.svg (Moonlander) and docs/ferris-keymap.svg (Ferris).
# Used by both `nix run` and the Build Ferris layout workflow.
# Needs python3 and keymap-drawer (`keymap` CLI) on PATH.
set -euo pipefail

root="${1:-$PWD}"
mkdir -p "$root/docs"

# keymap-drawer's dark mode leaves the background transparent, which puts light
# labels on white in light-themed viewers. Paint a dark background rect instead
# (a CSS background on <svg> is ignored by some renderers).
draw() {
  keymap draw "$1" | sed '0,/<\/style>/s||</style>\n<rect width="100%" height="100%" fill="#0d1117"/>|'
}

python3 "$root/keymap-viz/keymap2yaml.py" "$root/RgoVP/keymap.c" \
  > "$root/keymap-viz/keymap.yaml"
draw "$root/keymap-viz/keymap.yaml" > "$root/docs/keymap.svg"
echo "Wrote $root/docs/keymap.svg"

python3 "$root/ferris/generate.py"
python3 "$root/keymap-viz/keymap2yaml.py" "$root/ferris/keymap.c" \
  > "$root/keymap-viz/ferris-keymap.yaml"
draw "$root/keymap-viz/ferris-keymap.yaml" > "$root/docs/ferris-keymap.svg"
echo "Wrote $root/docs/ferris-keymap.svg"
