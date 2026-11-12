import os
import math
import struct
import zlib

from pico2d import load_image

import game_settings
import draw_util

ASSET_VERSION = 'w1c'


def gp(name):
    return os.path.join(game_settings.GEN_DIR, name)


def write_png(path, w, h, pixel):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw.extend(max(0, min(255, int(c))) for c in pixel(x, y))

    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)))
        f.write(chunk(b'IDAT', zlib.compress(bytes(raw), 9)))
        f.write(chunk(b'IEND', b''))


def rgba(c, a=255):
    return (c[0], c[1], c[2], c[3] if len(c) > 3 else a)


def shade(col, d):
    return (col[0] + d, col[1] + d, col[2] + d, col[3])


def mix(a, b, t):
    return (a[0] * (1 - t) + b[0] * t, a[1] * (1 - t) + b[1] * t, a[2] * (1 - t) + b[2] * t)


def noise(x, y, seed=0):
    n = (x * 374761393 + y * 668265263 + seed * 2147483647) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return (n & 0xffff) / 65535.0


def vary(col, n, amt):
    d = (n - 0.5) * 2 * amt
    return (col[0] + d, col[1] + d, col[2] + d, col[3])


NAMES = []
SMOOTH = set()
REBUILD = [False]
OUTLINE = (12, 8, 20, 255)


def gen(name, w, h, fn, smooth=False):
    NAMES.append(name)
    if smooth:
        SMOOTH.add(name)
    if REBUILD[0]:
        write_png(gp(name + '.png'), w, h, fn)


def _inside(px, py, pts):
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


class Canvas:
    """원·다각형으로 픽셀 그림을 그리는 도화지.
    칸마다 '재질' 글자를 기록해 두고, 저장할 때 재질별 색 + 빛(오른쪽 위) + 외곽선을 입힌다."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.m = [[None] * w for _ in range(h)]

    def put(self, x, y, mat):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.m[y][x] = mat

    def rect(self, x1, y1, x2, y2, mat):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.put(x, y, mat)

    def ellipse(self, cx, cy, rx, ry, mat, keep=None):
        for y in range(self.h):
            for x in range(self.w):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    if keep is None or self.m[y][x] in keep:
                        self.m[y][x] = mat

    def poly(self, pts, mat, keep=None):
        for y in range(self.h):
            for x in range(self.w):
                if _inside(x + 0.5, y + 0.5, pts) and (keep is None or self.m[y][x] in keep):
                    self.m[y][x] = mat

    def save(self, name, pal, silhouette=None, grad=False):
        m, w, h = self.m, self.w, self.h

        def mat(x, y):
            return m[y][x] if 0 <= x < w and 0 <= y < h else None

        def flat(c):
            return isinstance(pal[c][0], (int, float))

        def px(x, y):
            gx, gy = x - 1, y - 1
            c = mat(gx, gy)
            if c is None:
                if any(mat(gx + dx, gy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    return silhouette or OUTLINE
                return (0, 0, 0, 0)
            if silhouette:
                return silhouette
            if flat(c):
                return rgba(pal[c])
            light, mid, dark = pal[c]
            if grad and gy > h * 0.6:
                mid = mix(mid, dark, 0.45)
            if mat(gx + 1, gy) is None or mat(gx, gy - 1) is None or mat(gx + 1, gy - 1) is None:
                return rgba(light)
            if mat(gx - 1, gy) is None or mat(gx, gy + 1) is None:
                return rgba(dark)
            below = mat(gx, gy + 1)
            if below is not None and below != c and not flat(below):
                return rgba(dark)
            col = rgba(mid)
            if noise(gx, gy, len(name)) > 0.86:
                col = shade(col, -8)
            return col
        gen(name, w + 2, h + 2, px)


# ─────────── 타일 (32×32) ───────────
BARREL_PAL = {'W': ((130, 100, 120), (88, 64, 86), (54, 38, 56)), 'V': (62, 44, 62),
              'R': ((156, 150, 176), (104, 98, 126), (62, 58, 80)),
              'P': ((122, 94, 114), (84, 62, 82), (52, 36, 52)), 'Q': (40, 28, 42)}


def barrel_canvas():
    c = Canvas(26, 24)
    for y in range(2, 24):
        t = (y - 13) / 11.0
        half = 10.5 - 2.0 * t * t
        for x in range(26):
            if abs(x + 0.5 - 13) <= half:
                c.m[y][x] = 'W'
    for x in (6, 11, 16, 21):
        for y in range(5, 23):
            if c.m[y][x] == 'W':
                c.m[y][x] = 'V'
    for y in (8, 9, 17, 18):
        for x in range(26):
            if c.m[y][x] in ('W', 'V'):
                c.m[y][x] = 'R'
    c.ellipse(13, 3, 10.3, 2.6, 'P')
    c.ellipse(13, 3, 8.2, 1.6, 'Q', keep={'P'})
    return c


CRACK = {(5, 6), (6, 7), (7, 7), (8, 8), (8, 9), (9, 10), (10, 10), (11, 11), (11, 12),
         (21, 20), (22, 21), (22, 22), (23, 23), (24, 23), (25, 24), (26, 25)}


def floor_fn(th, seed, cracked):
    base, line = rgba(th['floor']), rgba(th['line'])

    def px(x, y):
        sx, sy, lx, ly = x // 16, y // 16, x % 16, y % 16
        if lx == 0 or ly == 0:
            return line
        col = shade(base, (noise(sx, sy, seed * 7) - 0.5) * 10)
        if lx == 1 or ly == 1:
            col = shade(col, 9)
        elif lx == 15 or ly == 15:
            col = shade(col, -10)
        col = vary(col, noise(x, y, seed), 5)
        if noise(x, y, seed + 50) > 0.93:
            col = shade(col, -10)
        if cracked and (x, y) in CRACK:
            col = shade(col, -22)
        return col
    return px


def wall_fn(th):
    base, dk = rgba(th['wall']), rgba(th['wdark'])

    def px(x, y):
        row, ly = y // 8, y % 8
        off = 8 if row % 2 else 0
        lx = (x + off) % 16
        if ly == 7 or lx == 15:
            return dk
        col = shade(base, (noise((x + off) // 16, row, 3) - 0.5) * 12)
        if ly == 0:
            col = shade(col, 18)
        elif lx == 0:
            col = shade(col, 8)
        elif ly == 6:
            col = shade(col, -16)
        elif lx == 14:
            col = shade(col, -10)
        return vary(col, noise(x, y, 3), 5)
    return px


# ─────────── 빛 효과 ───────────
def glow_fn(color, size=128):
    c = (size - 1) / 2

    def px(x, y):
        a = max(0.0, 1.0 - math.hypot(x - c, y - c) / c) ** 2
        return (color[0], color[1], color[2], 255 * a)
    return px


def shadow_px(x, y):
    d = ((x - 15.5) / 16) ** 2 + ((y - 4.5) / 5) ** 2
    return (0, 0, 0, 120 * (1 - d)) if d < 1 else (0, 0, 0, 0)


SOLIDS = {
    'dark': (0, 0, 0, 255), 'shade': (0, 0, 0, 170), 'panel': (18, 14, 30, 235),
    'bar_light': (190, 160, 255, 255), 'px_white': (240, 240, 255, 255), 'px_lav': (200, 170, 255, 255),
    'px_gold': (255, 215, 110, 255), 'bar_gold': (255, 230, 140, 255),
}


def build_images():
    os.makedirs(game_settings.GEN_DIR, exist_ok=True)
    ver = gp('version.txt')
    try:
        with open(ver) as f:
            REBUILD[0] = f.read().strip() != ASSET_VERSION
    except Exception:
        REBUILD[0] = True
    if REBUILD[0]:
        print('그림 만드는 중... (처음 한 번만)')

    barrel_canvas().save('barrel', BARREL_PAL)
    for i, th in enumerate(game_settings.THEMES):
        gen('t_floor%da' % i, 32, 32, floor_fn(th, i + 1, False))
        gen('t_floor%db' % i, 32, 32, floor_fn(th, i + 1, True))
        gen('t_wall%d' % i, 32, 32, wall_fn(th))
    gen('glow_w', 128, 128, glow_fn((255, 250, 255)), True)
    gen('glow_l', 128, 128, glow_fn((190, 160, 255)), True)
    gen('glow_y', 128, 128, glow_fn((255, 210, 90)), True)
    gen('shadow', 32, 10, shadow_px, True)
    for name, col in SOLIDS.items():
        gen(name, 1, 1, lambda x, y, col=col: col)

    if REBUILD[0]:
        with open(ver, 'w') as f:
            f.write(ASSET_VERSION)


def load_images():
    for n in NAMES:
        draw_util.set_smooth(n in SMOOTH)
        draw_util.IMG[n] = load_image(gp(n + '.png'))
    draw_util.set_smooth(False)


def prepare():
    """캔버스를 열기 전에: 그림 파일이 없으면 만든다"""
    build_images()


def load():
    """캔버스를 연 뒤에: 그림을 불러온다"""
    load_images()