# Mirrors the features enabled in RgoVP/rules.mk (minus the Oryx/ZSA-only ones).
CONSOLE_ENABLE = no
COMMAND_ENABLE = no
SPACE_CADET_ENABLE = no
CAPS_WORD_ENABLE = yes
COMBO_ENABLE = yes
REPEAT_KEY_ENABLE = yes

# The upstream Halcyon Ferris definition enables RGB matrix, but the board has no LEDs.
RGB_MATRIX_ENABLE = no
