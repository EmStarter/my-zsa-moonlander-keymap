# Oryx with custom QMK

This repository allows combining the convenience of [Oryx’s](https://www.zsa.io/oryx) graphical layout editing with the power of [QMK](https://qmk.fm), allowing you to customize your Oryx layout with advanced QMK features like Achordion and Repeat Key, while automating firmware builds through GitHub Actions.

For a detailed guide, check out the full [blog post here](https://blog.zsa.io/oryx-custom-qmk-features).

## How it works

Each time you run the GitHub Action, the workflow will:
1. Fetch the latest changes made in Oryx.
2. Merge them with any QMK features you've added in the source code.
3. Build the firmware, incorporating modifications from both Oryx and your custom source code.

## How to use

1. Fork this repository (be sure to **uncheck the "Copy the main branch only" option**).
2. To initialize the repository with your layout:
   - Go to the **Actions** tab.
   - Select **Fetch and build layout**.
   - Click **Run workflow**.
   - Input your layout ID and keyboard type (your layout must be public in Oryx), then run the workflow.
   - (To avoid having to input values each time, you can modify the default values at the top of the `.github/workflows/fetch-and-build-layout.yml` file).
3. A folder containing your layout will be generated at the root of the repository.
4. You can now add your custom QMK features to this folder:
   - Edit `config.h`, `keymap.c` and `rules.mk` according to the [QMK documentation](https://github.com/qmk/qmk_firmware/tree/master/docs/features).
   - Commit and push to the **main** branch.
5. You can continue editing your layout through Oryx:
   - Make your changes in Oryx. 
   - Optionally, add a description of your changes in the **Some notes about what you changed** field; if provided, this will be used as commit message.
   - Confirm changes by clicking the **Compile this layout** button.
6. To build the firmware (including both Oryx and code modifications), rerun the GitHub Action. The firmware will be available for download in the action’s artifacts.
7. Flash your downloaded firmware using [Keymapp](https://www.zsa.io/flash#flash-keymap).
8. Enjoy!

## Halcyon Ferris mirror

`ferris/` holds a keymap for the splitkb Halcyon Ferris rev1 (3x5+2) generated from the Moonlander layout, which only uses 34 keys. The Moonlander's pinky columns sit one row lower; the generator moves them back up so every finger has a plain 3-row column.

- `ferris/generate.py` rewrites `ferris/keymap.c`, `config.h` and `i18n.h` from `RgoVP/`. CI runs it and commits the result back to `main` whenever it changes, so after an Oryx sync just `git pull`; don't edit the generated files. `ferris/rules.mk` is hand-maintained.
- The **Build Ferris layout** workflow regenerates the keymap and builds it against upstream QMK. It runs after **Fetch and build layout**, on pushes touching `RgoVP/` or `ferris/`, or manually. Flash the `.uf2` by double-tapping the reset button and copying it onto the RPI-RP2 drive (once per half).
- The same workflow redraws `docs/keymap.svg` (Moonlander) and `docs/ferris-keymap.svg` and commits them when they change. Locally, `nix run` does the same drawing (`keymap-viz/draw.sh`).
- Keys outside the 34 (e.g. the top row of layer 6) are dropped; the generator lists them. The Ferris has no LEDs, so RGB keys become `KC_NO` and RGB matrix is disabled in `ferris/rules.mk`.

## Oryx Chrome extension

To make building even easier, [@nivekmai](https://github.com/nivekmai) created an [Oryx Chrome extension](https://chromewebstore.google.com/detail/oryx-extension/bocjciklgnhkejkdfilcikhjfbmbcjal) to be able to trigger the GitHub Actions from inside Oryx itself.
