#!/usr/bin/env python3
"""Parse RgoVP/keymap.c into a keymap-drawer YAML spec.

Handles the QMK LAYOUT_moonlander keymaps array, mod-taps / layer-taps,
this layout's custom keycodes (REP_L2, DUAL_FUNC_*), and the source-side
combos (comboN arrays + key_combos[] outputs). Re-run after any Oryx sync.

Usage: python3 keymap2yaml.py path/to/keymap.c > keymap.yaml
"""
import re
import sys

# --- friendly labels -------------------------------------------------------

SCALAR = {
    "KC_TRANSPARENT": "▽", "KC_NO": "", "KC_SPACE": "Spc", "KC_BSPC": "Bksp",
    "KC_ENTER": "Enter", "KC_TAB": "Tab", "KC_ESCAPE": "Esc", "KC_DELETE": "Del",
    "KC_CAPS": "Caps", "KC_PGDN": "PgDn", "KC_PAGE_UP": "PgUp",
    "KC_LEFT": "←", "KC_RIGHT": "→", "KC_UP": "↑", "KC_DOWN": "↓",
    "KC_LEFT_ALT": "LAlt", "KC_LEFT_CTRL": "LCtl", "KC_LEFT_GUI": "LGui",
    "KC_LEFT_SHIFT": "LSft", "KC_RIGHT_ALT": "RAlt", "KC_RIGHT_GUI": "RGui",
    "KC_RIGHT_SHIFT": "RSft", "KC_RIGHT_CTRL": "RCtl",
    "KC_PC_CUT": "Cut", "KC_PC_COPY": "Copy", "KC_PC_PASTE": "Paste", "KC_PC_UNDO": "Undo",
    "KC_AUDIO_MUTE": "Mute", "KC_AUDIO_VOL_UP": "Vol+", "KC_AUDIO_VOL_DOWN": "Vol-",
    "KC_MEDIA_PREV_TRACK": "Prev", "KC_MEDIA_NEXT_TRACK": "Next", "KC_MEDIA_PLAY_PAUSE": "Play",
    "KC_MS_UP": "M↑", "KC_MS_DOWN": "M↓", "KC_MS_LEFT": "M←", "KC_MS_RIGHT": "M→",
    "KC_MS_BTN1": "LMB", "KC_MS_BTN2": "RMB", "KC_MS_BTN3": "MMB",
    "KC_MS_WH_UP": "Wh↑", "KC_MS_WH_DOWN": "Wh↓", "KC_MS_WH_LEFT": "Wh←", "KC_MS_WH_RIGHT": "Wh→",
    "KC_MS_ACCEL0": "Acc0", "KC_MS_ACCEL1": "Acc1", "KC_MS_ACCEL2": "Acc2",
    "QK_BOOT": "Boot", "AU_TOGG": "Audio", "RGB_TOG": "RGB", "RGB_SLD": "RGB Solid",
    "RGB_MODE_FORWARD": "RGB Mode", "RGB_VAD": "Val-", "RGB_VAI": "Val+",
    "RGB_SPD": "Spd-", "RGB_SPI": "Spd+", "RGB_HUD": "Hue-", "RGB_HUI": "Hue+",
    "CW_TOGG": "Caps Word",
    # shifted symbols / punctuation
    "KC_DQUO": '"', "KC_DOT": ".", "KC_COMMA": ",", "KC_SLASH": "/",
    "KC_RABK": ">", "KC_LABK": "<", "KC_EQUAL": "=", "KC_BSLS": "\\",
    "KC_SCLN": ";", "KC_QUOTE": "'", "KC_RPRN": ")", "KC_LPRN": "(",
    "KC_CIRC": "^", "KC_PERC": "%", "KC_DLR": "$", "KC_RBRC": "]", "KC_LBRC": "[",
    "KC_PLUS": "+", "KC_ASTR": "*", "KC_AMPR": "&", "KC_PIPE": "|", "KC_TILD": "~",
    "KC_RCBR": "}", "KC_LCBR": "{", "KC_UNDS": "_", "KC_MINUS": "-", "KC_GRAVE": "`",
    "KC_HASH": "#", "KC_AT": "@", "KC_EXLM": "!", "KC_COLN": ":",
    "KC_KP_PLUS": "+", "KC_KP_COMMA": ",", "KC_KP_DOT": ".",
    "KC_KP_ASTERISK": "*", "KC_KP_SLASH": "/",
}

MODMAP = {
    "MOD_LALT": "LAlt", "MOD_RALT": "RAlt", "MOD_LCTL": "LCtl", "MOD_RCTL": "RCtl",
    "MOD_LGUI": "LGui", "MOD_RGUI": "RGui", "MOD_LSFT": "LSft", "MOD_RSFT": "RSft",
    "MOD_HYPR": "Hyper", "MOD_MEH": "Meh",
}

# custom keycodes: tap/hold semantics live in process_record_user
CUSTOM = {
    "REP_L2": {"t": "Repeat", "h": "L2"},
    "DUAL_FUNC_0": {"t": "(", "h": "RGui"},
    "DUAL_FUNC_1": {"t": "#", "h": "LAlt"},
    "DUAL_FUNC_2": {"t": "@", "h": "LCtl"},
    "DUAL_FUNC_3": {"t": "!", "h": "LGui"},
    "DUAL_FUNC_4": {"t": ":", "h": "LSft"},
    "DUAL_FUNC_5": {"t": "{", "h": "RAlt"},
    "DUAL_FUNC_6": {"t": "{", "h": "LAlt"},
    "DUAL_FUNC_7": {"t": "}", "h": "RAlt"},
}

LAYER_NAMES = ["Base", "Nav", "Mouse", "Num", "Sym", "Fn", "Media"]


def scalar(tok):
    if tok in SCALAR:
        return SCALAR[tok]
    if tok.startswith("KC_"):
        rest = tok[3:]
        if len(rest) == 1 or rest.isdigit():
            return rest
        return rest.replace("_", " ").title()
    return tok


def label(tok):
    """Map a normalized (no-space) keycode token to a keymap-drawer key spec."""
    if tok in CUSTOM:
        return dict(CUSTOM[tok])
    m = re.match(r"^MT\((MOD_\w+),(.+)\)$", tok)
    if m:
        return {"t": scalar_of(m.group(2)), "h": MODMAP.get(m.group(1), m.group(1))}
    m = re.match(r"^LT\((\d+),(.+)\)$", tok)
    if m:
        return {"t": scalar_of(m.group(2)), "h": "L" + m.group(1)}
    m = re.match(r"^([LR])(ALT|CTL|GUI|SFT)\((.+)\)$", tok)
    if m:
        side = "L" if m.group(1) == "L" else "R"
        mod = {"ALT": "A", "CTL": "C", "GUI": "G", "SFT": "S"}[m.group(2)]
        return f"{side}{mod}-{scalar_of(m.group(3))}"
    m = re.match(r"^OSM\((MOD_\w+)\)$", tok)
    if m:
        return "OSM " + MODMAP.get(m.group(1), m.group(1))
    m = re.match(r"^(OSL|TO|MO|TG|DF|TT)\((\d+)\)$", tok)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return scalar(tok)


def scalar_of(tok):
    """Label for something known to be a plain (possibly nested) keycode."""
    out = label(tok)
    return out if isinstance(out, str) else tok


# --- parsing ---------------------------------------------------------------

def split_top(s):
    out, depth, cur = [], 0, ""
    for c in s:
        if c == "(":
            depth += 1; cur += c
        elif c == ")":
            depth -= 1; cur += c
        elif c == "," and depth == 0:
            t = cur.strip()
            if t and t != "COMBO_END":
                out.append(t)
            cur = ""
        else:
            cur += c
    t = cur.strip()
    if t and t != "COMBO_END":
        out.append(t)
    return out


def norm(tok):
    return re.sub(r"\s+", "", tok)


def parse_layers(text):
    layers = {}
    order = []
    for m in re.finditer(r"\[(\d+)\]\s*=\s*LAYOUT_moonlander\(", text):
        idx = int(m.group(1))
        start = j = m.end()
        depth = 1
        while depth > 0:
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
            j += 1
        body = text[start:j - 1]
        toks = [norm(t) for t in split_top(body)]
        name = LAYER_NAMES[idx] if idx < len(LAYER_NAMES) else f"L{idx}"
        layers[name] = toks
        order.append(name)
    return layers, order


def parse_combos(text, base_tokens):
    # comboN[] = { keyA, keyB, COMBO_END };
    defs = {}
    for m in re.finditer(r"const uint16_t PROGMEM (combo\d+)\[\]\s*=\s*\{(.+?)\}", text, re.S):
        keys = [norm(t) for t in split_top(m.group(2))]
        defs[m.group(1)] = keys
    # COMBO(comboN, OUTPUT)
    combos = []
    for m in re.finditer(r"COMBO\((combo\d+),\s*(.+?)\)\s*,", text):
        name, out = m.group(1), norm(m.group(2))
        keys = defs.get(name)
        if not keys:
            continue
        pos = []
        for k in keys:
            if k in base_tokens:
                pos.append(base_tokens.index(k))
        if len(pos) != len(keys):
            sys.stderr.write(f"warn: {name} keys not all found on base layer: {keys}\n")
            continue
        out_lbl = label(out)
        out_lbl = out_lbl if isinstance(out_lbl, str) else out.replace("OSM(", "OSM ").rstrip(")")
        combos.append({"p": pos, "k": out_lbl})
    return combos


# --- key classification (drives per-key colour via CSS class) --------------

NAV = {"KC_LEFT", "KC_RIGHT", "KC_UP", "KC_DOWN", "KC_PGDN", "KC_PAGE_UP",
       "KC_HOME", "KC_END"}
MODS = {"KC_LEFT_ALT", "KC_LEFT_CTRL", "KC_LEFT_GUI", "KC_LEFT_SHIFT",
        "KC_RIGHT_ALT", "KC_RIGHT_GUI", "KC_RIGHT_SHIFT", "KC_RIGHT_CTRL"}
FUNC = {"KC_SPACE", "KC_ENTER", "KC_TAB", "KC_ESCAPE", "KC_BSPC", "KC_DELETE",
        "KC_CAPS"}
SYS_PREFIX = ("KC_AUDIO_", "KC_MEDIA_", "RGB_", "KC_MS_", "KC_PC_")
SYS = {"AU_TOGG", "QK_BOOT", "CW_TOGG", "RGB_SLD", "RGB_TOG",
       "RGB_MODE_FORWARD"}

# every symbol/punctuation keycode that appears in this keymap
SYMS = {
    "KC_DOT", "KC_COMMA", "KC_SLASH", "KC_DQUO", "KC_QUOTE", "KC_SCLN",
    "KC_RABK", "KC_LABK", "KC_EQUAL", "KC_BSLS", "KC_MINUS", "KC_GRAVE",
    "KC_CIRC", "KC_PERC", "KC_DLR", "KC_RBRC", "KC_LBRC", "KC_PLUS",
    "KC_ASTR", "KC_AMPR", "KC_PIPE", "KC_TILD", "KC_RCBR", "KC_LCBR",
    "KC_UNDS", "KC_RPRN", "KC_LPRN", "KC_HASH", "KC_AT", "KC_EXLM",
    "KC_COLN", "KC_KP_PLUS", "KC_KP_COMMA", "KC_KP_DOT", "KC_KP_ASTERISK",
    "KC_KP_SLASH",
}


def classify_scalar(t):
    if re.match(r"^KC_[A-Z]$", t):
        return "alpha"
    if re.match(r"^KC_[0-9]$", t) or re.match(r"^KC_KP_[0-9]$", t):
        return "num"
    if re.match(r"^KC_F[0-9]+$", t):
        return "func"
    if t in NAV:
        return "nav"
    if t in MODS:
        return "mod"
    if t in FUNC:
        return "func"
    if t in SYS or t.startswith(SYS_PREFIX):
        return "sys"
    if t in SYMS:
        return "sym"
    return None


def classify(tok):
    if tok in ("KC_TRANSPARENT", "KC_NO"):
        return "trans"
    if tok == "REP_L2":
        return "layer"
    if tok.startswith("DUAL_FUNC_"):
        return "sym"
    if tok.startswith("MT(") or tok.startswith("OSM("):
        return "mod"
    if re.match(r"^(LT|MO|TO|TG|OSL|DF|TT)\(", tok):
        return "layer"
    m = re.match(r"^[LR](ALT|CTL|GUI|SFT)\((.+)\)$", tok)
    if m:
        return classify_scalar(m.group(2))
    return classify_scalar(tok)


# category -> fill colour
PALETTE = {
    "alpha": "#eef1f5",
    "num":   "#fff2cc",
    "sym":   "#e7d9f6",
    "mod":   "#ffdede",
    "layer": "#d9edd9",
    "nav":   "#d3eef6",
    "sys":   "#ffe3c7",
    "func":  "#e1e8ef",
    "trans": "#fbfcfd",
}


def draw_config_block():
    css = ["/* per-category key colours */"]
    for cls, fill in PALETTE.items():
        css.append("rect.%s { fill: %s; }" % (cls, fill))
    css.append("rect.combo { fill: #cfe3ff; }")
    out = ["draw_config:", "  svg_extra_style: |"]
    out += ["    " + line for line in css]
    return out


# --- YAML emit (hand-rolled, no pyyaml dependency) -------------------------

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def emit_key(tok):
    lbl = label(tok)
    typ = classify(tok)
    if isinstance(lbl, dict):
        parts = ["t: %s" % q(lbl["t"]), "h: %s" % q(lbl["h"])]
        if typ:
            parts.append("type: %s" % q(typ))
        return "{%s}" % ", ".join(parts)
    if typ:
        return "{t: %s, type: %s}" % (q(lbl), q(typ))
    return q(lbl)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "RgoVP/keymap.c"
    text = open(src, encoding="utf-8").read()
    layers, order = parse_layers(text)
    base = layers[order[0]]
    combos = parse_combos(text, base)

    lines = []
    lines.append("layout:")
    lines.append("  qmk_keyboard: zsa/moonlander")
    lines.append("  layout_name: LAYOUT")
    lines.append("layers:")
    for name in order:
        lines.append(f"  {name}:")
        for tok in layers[name]:
            lines.append("    - " + emit_key(tok))
    if combos:
        lines.append("combos:")
        base_name = order[0]
        for c in combos:
            lines.append("  - {p: [%s], k: %s, l: [%s]}"
                         % (", ".join(str(p) for p in c["p"]), q(c["k"]), base_name))
    lines += draw_config_block()
    sys.stdout.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
