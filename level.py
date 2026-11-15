import math
import random

import game_settings
from game_settings import TILE, COLS, ROWS
from draw_util import img_draw

MAP = [                                  # '#' 벽, '.' 바닥, 'B' 나무통, 'P' 시작 위치, 'E' 적 시작 위치
    '##############################',
    '#............#...............#',
    '#..P.........#.......B...E...#',
    '#............#...............#',
    '#.....####...#....######.....#',
    '#.....#..........#...........#',
    '#.....#....B.....#.....B.....#',
    '#..........................B.#',
    '#####...........#####........#',
    '#.......E.......#............#',
    '#...B...####....#....####....#',
    '#.........#..........#...E...#',
    '#.........#....B.....#.......#',
    '#...######...........#..######',
    '#............###.............#',
    '#.B.........E...........B....#',
    '#............................#',
    '##############################',
]

grid = []                                # grid[줄][칸] = 글자
theme = 0                                # 층 배경 테마 번호
start = (0, 0)                           # 시작 위치 (화면 좌표)
spawns = []


def tile_center(c, r):
    return c * TILE + TILE / 2, game_settings.HUD_Y - r * TILE - TILE / 2


def cell_of(x, y):
    return int(x // TILE), int((game_settings.HUD_Y - y) // TILE)


def ch_at(x, y):
    c, r = cell_of(x, y)
    if 0 <= c < COLS and 0 <= r < ROWS:
        return grid[r][c]
    return '#'


SOLID = '#B'                             # 지나갈 수 없는 칸: 벽, 나무통


def random_spots(n, avoid, min_d):
    """바닥 칸 중에서 avoid 위치와 min_d 이상 떨어진 곳을 겹치지 않게 n개 고름"""
    cells = []
    for r in range(ROWS):
        for c in range(COLS):
            x, y = tile_center(c, r)
            if grid[r][c] == '.' and math.hypot(x - avoid[0], y - avoid[1]) >= min_d:
                cells.append((x, y))
    return random.sample(cells, min(n, len(cells)))


def can_see(x1, y1, x2, y2):
    """두 점 사이에 벽이 없으면 True (8px 간격으로 검사, 나무통은 시야를 가리지 않음)"""
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 8))
    for i in range(1, n):
        t = i / n
        if ch_at(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t) == '#':
            return False
    return True


def blocked(x, y, r):
    """(x, y)가 중심이고 반지름 r인 몸이 벽이나 통에 닿는지 (몸의 네 모서리를 검사)"""
    for px, py in ((x - r, y - r), (x + r, y - r), (x - r, y + r), (x + r, y + r)):
        if ch_at(px, py) in SOLID:
            return True
    return False


def move(o, dx, dy):
    """가로, 세로를 따로 움직여서, 벽에 막혀도 벽을 따라 미끄러지듯 이동"""
    if not blocked(o.x + dx, o.y, o.r):
        o.x += dx
    if not blocked(o.x, o.y + dy, o.r):
        o.y += dy


def build(rows=MAP):
    global grid, start, spawns
    grid = [list(row) for row in rows]
    spawns = []
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == 'P':
                start = tile_center(c, r)
                grid[r][c] = '.'
            elif ch == 'E':
                spawns.append(tile_center(c, r))
                grid[r][c] = '.'


def draw_tile(c, r):
    x, y = tile_center(c, r)
    ch = grid[r][c]
    if ch == '#':
        img_draw('t_wall%d' % theme, x, y, TILE, TILE)
        return
    variant = 'b' if (c * 7 + r * 13) % 11 == 0 else 'a'     # 가끔 금 간 바닥
    img_draw('t_floor%d%s' % (theme, variant), x, y, TILE, TILE)
    if ch == 'B':
        s = 0.8 + ((c * 31 + r * 17) % 4) * 0.1          # 통마다 크기가 조금씩 다름 (0.8 ~ 1.1배)
        img_draw('shadow', x, y - 11, 28 * s, 8 * s, 0.8)
        img_draw('barrel', x, y - 11 + 13 * s, 28 * s, 26 * s)


class LevelView:
    """맵 전체를 그리는 객체 (게임 월드의 바닥 레이어에 넣음)"""

    def update(self):
        pass

    def draw(self):
        for r in range(ROWS):
            for c in range(COLS):
                draw_tile(c, r)
