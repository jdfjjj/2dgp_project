import os
import math
import struct
import zlib

from pico2d import load_image

import game_settings
import draw_util

ASSET_VERSION = 'w1'


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