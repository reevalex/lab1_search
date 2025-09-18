from utils import Position

# Game setups
SEEDS = 4
PITS_PER_PLAYER = 6  # PLAYABLE pits per player

# AI setup
AI_WAIT_TIME = 200  # in ms. Minimum time that the AI waits before playing the move it computed

# Do not touch what's below

# Font settings
FONT_SIZE = 36
TEXT_COLOR = (255, 255, 255)

# Board interface setup
PIT_RADIUS = 40
BOARD_COLOR = (139, 69, 19)
BOARD_COLOR_DARK = (110, 50, 10)
PIT_COLOR = (205, 133, 63)
PIT_COLOR_DARK = (175, 110, 46)
PIT_COLOR_LIGHT = (215, 145, 75)
SEED_COLOR = (0, 0, 0)

# Shortcuts
TOTAL_PITS = (PITS_PER_PLAYER + 1 ) * 2
PLAYER_0_STORE = PITS_PER_PLAYER
PLAYER_1_STORE = TOTAL_PITS - 1

# Screen sizes
WIDTH = 800
HEIGHT = 400

# Colors
COLORS = {'light': (170, 170, 170),
          'dark': (100, 100, 100),
          }

# Debug colors
DCOL_AI = "cyan"
DCOL_GAME = "red"
