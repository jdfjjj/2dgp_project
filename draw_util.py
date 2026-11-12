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