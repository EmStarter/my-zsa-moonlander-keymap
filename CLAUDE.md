# CLAUDE.md

QMK keymaps for two keyboards that share one layout:

- **ZSA Moonlander** (`RgoVP/`): the source of truth. Edited partly in Oryx, partly by hand.
- **splitkb Halcyon Ferris rev1** (`ferris/`): 3x5+2, *generated* from `RgoVP/` by `ferris/generate.py`.

The Moonlander layout only uses 34 keys, so the Ferris mirrors it 1:1. Keys outside those 34 get dropped.

## Layout

| Path | What it is |
|---|---|
| `RgoVP/` | Moonlander keymap from Oryx (layout ID `RgoVP`), plus hand-written QMK additions |
| `ferris/generate.py` | Converts `RgoVP/` into `ferris/keymap.c`, `config.h`, `i18n.h` |
| `ferris/rules.mk` | Hand-maintained (the only Ferris file that isn't generated) |
| `keymap-viz/` | `keymap2yaml.py` (keymap.c → keymap-drawer YAML) and `draw.sh` |
| `docs/*.svg` | Rendered keymaps, committed by CI |
| `qmk_firmware/` | Submodule: ZSA's QMK fork, used for Moonlander builds only |
| `Dockerfile` | Build image for the Moonlander workflow |
| `flake.nix` | `nix run` draws the SVGs locally; `nix develop` gives keymap-drawer and python3 |

## Branches and the Oryx merge flow

- `oryx`: contains only raw Oryx exports. CI commits to it. **Never commit to it by hand.**
- `main`: the Oryx exports merged with custom QMK code.

The **Fetch and build layout** workflow (manual `workflow_dispatch`) downloads the latest Oryx source, commits it to `oryx`, merges `oryx` into `main` with `-Xignore-all-space`, bumps the submodule, builds the Moonlander `.bin`, and then calls **Build Ferris layout**.

Because every Oryx sync is a git merge into `RgoVP/keymap.c`, hand edits there must not conflict with Oryx's regenerated sections:

- Don't edit the `keymaps[]` array, `combo*`/`key_combos`, `chordal_hold_layout` or the `DUAL_FUNC_*` defines by hand. Change those in Oryx.
- Put custom code in the blank-line gaps that Oryx keeps stable, or in new functions after `process_record_user`. Examples: the `REP_L2` define near the top, and `remember_last_key_user` at the end.
- Custom keys are bound in Oryx as a placeholder `LT(...)` so the keymap array matches Oryx exactly, and the tap is then intercepted in `process_record_user`. For example, `REP_L2 = LT(2, KC_F13)` gives Repeat Key on tap and layer 2 on hold.
- `remember_last_key_user` must keep returning `false` for `REP_L2`. Without it, Repeat repeats itself, so nothing happens. If an Oryx merge drops it, add it back.

## Ferris generation

- **Never edit `ferris/keymap.c`, `config.h` or `i18n.h` by hand.** Change `RgoVP/` or `generate.py` instead, then run `python3 ferris/generate.py` from the repo root.
- The generator moves the Moonlander pinky columns up one row, renames old ZSA-fork keycodes to their upstream names (`RENAMES`), turns RGB keys into `KC_NO`, drops the `RGB_SLD` handler, and strips Moonlander-only config (serial number, RGB matrix tuning). It exits on errors, e.g. leftover `rawhid_state` or a layer that isn't 72 keys.
- The Ferris builds against **upstream** QMK (`ghcr.io/qmk/qmk_cli`), not the ZSA fork, as keyboard `splitkb/halcyon/ferris/rev1` with keymap `mirror`.
- When you add a QMK feature to `RgoVP/rules.mk`, mirror it in `ferris/rules.mk` unless it is Oryx/ZSA-only.

## Commands

```sh
python3 ferris/generate.py      # regenerate ferris/ from RgoVP/
nix run                         # regenerate ferris/ and redraw docs/keymap.svg + docs/ferris-keymap.svg
```

No local firmware build is set up. Builds run in GitHub Actions:

- **Moonlander:** run *Fetch and build layout* by hand. Pushing to `main` does **not** rebuild it. Flash the artifact with Keymapp.
- **Ferris:** *Build Ferris layout* runs on pushes that touch `RgoVP/`, `ferris/`, `keymap-viz/` or its own workflow file, after each Oryx fetch, or by hand. It commits the regenerated `ferris/` and `docs/` back to `main`, so `git pull` after it runs. To flash, double-tap reset and copy the `.uf2` onto each half.

keymap-drawer is pinned to the same version in `build-ferris.yml` (pipx) and in `flake.lock` (nixpkgs) so the SVGs come out identical. Bump both together.

## Conventions

- CI commit prefixes: `✨(oryx)`, `✨(qmk)`, `🤖(ferris)`. Human commits are plain imperative sentences.
- After changing custom keycodes or labels, check that `keymap-viz/keymap2yaml.py` still renders them. It derives `DUAL_FUNC_*` labels from the handlers in `process_record_user`.
