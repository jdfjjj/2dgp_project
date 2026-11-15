import os
from pico2d import SDLK_w, SDLK_a, SDLK_s, SDLK_d, SDLK_SPACE

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
MOUSE_LEFT = 1                   # 마우스 왼쪽 버튼: 공격
ATTACK_TIME = 0.16               # 공격 자세를 보여 주는 시간 (초)
KEY_THROW = (SDLK_SPACE,)        # 빛 던지기
THROW_TIME = 0.15                # 던지는 자세를 보여 주는 시간 (초)
ORB_SPEED = 420                  # 빛 구슬이 날아가는 속도 (px/s)
ORB_RANGE = 300                  # 빛 구슬이 날아가는 최대 거리 (px)
ORB_LIGHT = 70                   # 떨어진 빛 구슬이 밝히는 반경 (px)
STUN_TIME = 0.9                  # 빛 구슬에 맞은 적이 기절하는 시간 (초)
MAX_HEARTS = 3                   # 하트 개수
INVULN_TIME = 1.3                # 맞은 뒤 무적 시간 (초)
HURT_TIME = 0.35                 # 피격 그림을 보여 주는 시간 (초)
PLAYER_KNOCK = 520               # 맞았을 때 밀려나는 속도 (px/s). 약 65px 밀려서 적이 부채꼴 끝에 걸림
DEATH_DELAY = 1.0                # 쓰러진 뒤 게임 오버 화면까지 (초)

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
LIGHT_DECAY = 0.25               # 1초에 줄어드는 빛
SHARD_LIGHT = 7                  # 빛 조각 하나로 채워지는 빛
SHARD_COUNT = 6                  # 맵에 놓이는 빛 조각 수
CELL = 16                        # 어둠 칸 크기 (버벅이면 24로)
LIGHT_CORE = 0.2                 # 빛 반경 중 완전히 밝은 가운데 비율 (바깥으로 갈수록 빠르게 어두워짐)
PLAYER_SCALE = 2
BASE_STATS = dict(speed=kmph_to_pps(PLAYER_SPEED_KMPH), light_cap=20.0, sight=190.0,
                  reach=72.0, arc=110.0, slash_cd=0.42, dmg=1,       # 공격 사거리, 각도, 대기시간, 피해
                  throw_cost=1.5, throw_cd=0.35, orb_life=5.0)     # 던지기 비용, 대기시간, 빛 구슬 지속시간

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
    'thief': dict(row=2, hp=2, walk=3.1, chase=5.9, r=11),
    'brute': dict(row=3, hp=5, walk=2.0, chase=3.5, r=14, armor=True),
}
DETECT_BASE = 95                 # 적이 알아채는 기본 거리 (px). 여기에 내 빛 반경의 절반을 더함
CLOSE_DETECT = 52                # 이 거리 안이면 벽과 상관없이 무조건 알아챔
LOSE_TIME = 2.5                  # 놓친 뒤 이 시간이 지나면 포기 (초)
KILL_LIGHT = 1                   # 적을 처치하면 차는 빛
THIEF_STEAL = 3                  # 빛 도둑이 훔치는 빛
THIEF_SLOW = 0.65                # 빛을 들고 달아날 때 속도 배율
THIEF_LIGHT = 40                 # 훔친 빛을 든 빛 도둑 주변이 밝은 반경 (px)
EXPOSE_TIME = 4.0                # 빛 구슬에 맞은 큰 그림자의 갑옷이 벗겨지는 시간 (초)
SLAM_RANGE = 70                  # 이 거리 안이면 내려찍기 준비 (px)
SLAM_RADIUS = 88                 # 내려찍기 범위 (px)
SLAM_WINDUP = 0.75               # 빨간 원을 보여 주는 시간 (초)
SLAM_RECOVER = 0.9               # 내려찍은 뒤 멈춰 있는 시간 (초)
SLAM_CD = 2.2                    # 다음 내려찍기까지 (초)
SLAM_DMG = 2                     # 내려찍기 피해 (하트)


def clampf(v, lo, hi):
    return max(lo, min(hi, v))