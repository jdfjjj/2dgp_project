import os
from pico2d import load_font

import game_settings

IMG = {}                 # 이름 → 이미지
OFF = [0, 0]             # 화면 흔들림 오프셋

COLORS = {'w': (240, 236, 250), 'y': (255, 215, 110), 'r': (255, 90, 110), 'g': (150, 142, 175),
          'o': (255, 160, 80), 'p': (220, 205, 245), 'l': (200, 170, 255), 'k': (24, 14, 40),
          'd': (90, 60, 150)}


def set_smooth(on):
    try:
        from sdl2 import SDL_SetHint, SDL_HINT_RENDER_SCALE_QUALITY
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b'1' if on else b'0')
    except Exception:
        pass


def img_draw(img, x, y, w, h, alpha=1.0, rad=0.0, flip=''):
    if isinstance(img, str):
        img = IMG[img]
    if alpha < 0.999:
        if alpha <= 0.01:
            return
        img.opacify(alpha)
    if rad or flip:
        img.composite_draw(rad, flip, x + OFF[0], y + OFF[1], w, h)
    else:
        img.draw(x + OFF[0], y + OFF[1], w, h)
    if alpha < 0.999:
        img.opacify(1.0)


def box(name, x1, y1, x2, y2, alpha=1.0):
    if x2 > x1 and y2 > y1:
        img_draw(name, (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1, alpha)