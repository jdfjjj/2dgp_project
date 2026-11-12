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

# ─────────── 물리 단위 (16강) : 타일 한 칸(32px) = 0.5m ───────────
PIXEL_PER_METER = 32.0 / 0.5


def kmph_to_pps(kmph):
    return kmph * 1000.0 / 3600.0 * PIXEL_PER_METER


PLAYER_SPEED_KMPH = 10.7         # 가볍게 뛰는 속도 (약 190 px/s)
STRIDE_LENGTH_M = 1.2            # 한 걸음 주기의 길이
WALK_FRAMES_PER_STRIDE = 4       # 한 걸음 주기에 들어가는 애니메이션 장 수

# ─────────── 빛 / 시야 ───────────
LIGHT_BASE = 46                  # 빛이 없을 때 시야 (px)
START_LIGHT = 8.0                # 층 시작할 때 빛
CELL = 16                        # 어둠 칸 크기 (버벅이면 24로)
PLAYER_SCALE = 2
BASE_STATS = dict(speed=kmph_to_pps(PLAYER_SPEED_KMPH), light_cap=20.0, sight=190.0)