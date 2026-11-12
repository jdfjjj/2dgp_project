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