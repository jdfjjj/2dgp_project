import os
from pico2d import SDLK_w, SDLK_a, SDLK_s, SDLK_d, SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT

# ─────────── 화면 / 경로 ───────────
W, H = 960, 640
TILE = 32
COLS, ROWS = 30, 18
HUD_Y = ROWS * TILE
IW, IH = COLS - 2, ROWS - 2
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEN_DIR = os.path.join(BASE_DIR, 'escape_assets')
TITLE = 'IN THE DARK'

# ─────────── 키 ───────────
KEY_UP = (SDLK_w, SDLK_UP)
KEY_DOWN = (SDLK_s, SDLK_DOWN)
KEY_LEFT = (SDLK_a, SDLK_LEFT)
KEY_RIGHT = (SDLK_d, SDLK_RIGHT)
KEY_MOVE = KEY_UP + KEY_DOWN + KEY_LEFT + KEY_RIGHT