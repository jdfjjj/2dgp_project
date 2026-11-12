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


FONT_SETS = {
    'main': ['C:/Windows/Fonts/malgunbd.ttf', '/System/Library/Fonts/AppleSDGothicNeo.ttc',
             os.path.join(game_settings.BASE_DIR, 'font.ttf'), 'C:/Windows/Fonts/malgun.ttf'],
    'title': [os.path.join(game_settings.BASE_DIR, 'font_title.ttf')],
    'clean': ['C:/Windows/Fonts/malgun.ttf', '/System/Library/Fonts/AppleSDGothicNeo.ttc'],
    'bold': ['C:/Windows/Fonts/malgunbd.ttf', '/System/Library/Fonts/AppleSDGothicNeo.ttc'],
    'pixel': [os.path.join(game_settings.BASE_DIR, 'font1.ttf')],
}
_fonts = {}


def get_font(size, style='main'):
    key = (style, size)
    if key in _fonts:
        return _fonts[key]
    font = None
    for path in FONT_SETS[style]:
        if os.path.exists(path):
            try:
                font = load_font(path, size)
                break
            except Exception:
                font = None
    if font is None and style != 'main':
        font = get_font(size, 'main')
    _fonts[key] = font
    return font


def text_width(font, s, size):
    try:
        import ctypes
        from sdl2.sdlttf import TTF_SizeUTF8
        w, h = ctypes.c_int(), ctypes.c_int()
        TTF_SizeUTF8(font.font, s.encode('utf-8'), ctypes.byref(w), ctypes.byref(h))
        if w.value > 0:
            return w.value
    except Exception:
        pass
    return len(s) * size * 0.6


def draw_str(s, x, y, size, align, layers, style):
    font = get_font(size, style)
    if font is None:
        return
    s = str(s)
    if align != 'left':
        tw = text_width(font, s, size)
        x -= tw / 2 if align == 'center' else tw
    for dx, dy, col in layers:
        font.draw(x + dx, y + dy, s, col)


def say(s, x, y, size=20, color='w', align='left', style='main'):
    d = max(2, size // 12)
    draw_str(s, x, y, size, align, [(d, -d, (0, 0, 0)), (0, 0, COLORS[color])], style)


def say_logo(s, x, y, size, align='center'):
    d = max(2, size // 14)
    b = (0, 0, 0)
    layers = [(-d, 0, b), (d, 0, b), (0, d, b), (0, -d, b), (d * 2, -d * 2, b),
              (d, -d, (150, 105, 25)), (0, 0, (255, 215, 110))]
    draw_str(s, x, y, size, align, layers, 'title')