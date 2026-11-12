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
