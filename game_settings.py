import os
from pico2d import SDLK_w, SDLK_a, SDLK_s, SDLK_d

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
KEY_UP = (SDLK_w,)
KEY_DOWN = (SDLK_s,)
KEY_LEFT = (SDLK_a,)
KEY_RIGHT = (SDLK_d,)
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

# ─────────── 층 배경 테마 ───────────
THEMES = [
    dict(name='VIOLET CRYPT', floor=(44, 38, 62), line=(28, 24, 42), wall=(74, 64, 102), wdark=(36, 30, 54)),
    dict(name='MOSSY HALLS', floor=(36, 46, 44), line=(22, 30, 28), wall=(60, 80, 72), wdark=(28, 40, 36)),
    dict(name='EMBER VAULT', floor=(56, 36, 36), line=(34, 20, 22), wall=(94, 56, 52), wdark=(46, 26, 26)),
    dict(name='FROST CELLAR', floor=(36, 46, 64), line=(22, 28, 42), wall=(68, 86, 116), wdark=(32, 40, 58)),
    dict(name='THE ABYSS', floor=(30, 22, 40), line=(16, 10, 24), wall=(58, 40, 80), wdark=(24, 16, 36)),
]


# ─────────── 적 ───────────
ENEMY_DEF = {                    # row: enemies.png 줄, walk/chase: 배회/추격 속도(km/h), r: 충돌 반지름
    'blob': dict(row=0, hp=1, walk=3.1, chase=5.3, r=10),
}
DETECT_BASE = 95                 # 적이 알아채는 기본 거리 (px). 여기에 내 빛 반경의 절반을 더함
CLOSE_DETECT = 52                # 이 거리 안이면 벽과 상관없이 무조건 알아챔
LOSE_TIME = 2.5                  # 놓친 뒤 이 시간이 지나면 포기 (초)


def clampf(v, lo, hi):
    return max(lo, min(hi, v))