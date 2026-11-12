import game_settings
from game_settings import TILE, COLS, ROWS
from draw_util import img_draw

MAP = [                                  # '#' 벽, '.' 바닥, 'B' 나무통, 'P' 시작 위치
    '##############################',
    '#............#...............#',
    '#..P.........#.......B.......#',
    '#............#...............#',
    '#.....####...#....######.....#',
    '#.....#..........#...........#',
    '#.....#....B.....#.....B.....#',
    '#..........................B.#',
    '#####...........#####........#',
    '#...............#............#',
    '#...B...####....#....####....#',
    '#.........#..........#.......#',
    '#.........#....B.....#.......#',
    '#...######...........#..######',
    '#............###.............#',
    '#.B.....................B....#',
    '#............................#',
    '##############################',
]

grid = []                                # grid[줄][칸] = 글자
theme = 0                                # 층 배경 테마 번호
start = (0, 0)                           # 시작 위치 (화면 좌표)


def tile_center(c, r):
    return c * TILE + TILE / 2, game_settings.HUD_Y - r * TILE - TILE / 2


def cell_of(x, y):
    return int(x // TILE), int((game_settings.HUD_Y - y) // TILE)


def ch_at(x, y):
    c, r = cell_of(x, y)
    if 0 <= c < COLS and 0 <= r < ROWS:
        return grid[r][c]
    return '#'


def build(rows=MAP):
    global grid, start
    grid = [list(row) for row in rows]
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == 'P':
                start = tile_center(c, r)
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
        img_draw('shadow', x, y - 11, 28, 8, 0.8)
        img_draw('barrel', x, y + 2, 28, 26)


class LevelView:
    """맵 전체를 그리는 객체 (게임 월드의 바닥 레이어에 넣음)"""

    def update(self):
        pass

    def draw(self):
        for r in range(ROWS):
            for c in range(COLS):
                draw_tile(c, r)
