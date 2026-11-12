import math
import random

from pico2d import (get_events, clear_canvas, update_canvas, SDL_QUIT, SDL_KEYDOWN,
                    SDL_MOUSEMOTION, SDL_MOUSEBUTTONDOWN, SDLK_ESCAPE, SDLK_SPACE, SDLK_RETURN)

import game_settings
from game_settings import W, H
import game_framework
import draw_util
from draw_util import img_draw, box, say, draw_str, COLORS
import sheet

_rng = random.Random(7)
ICONS = []                                   # 배경에 떠다니는 빛 조각과 그림자
while len(ICONS) < 24:
    ix, iy = _rng.uniform(30, W - 30), _rng.uniform(30, H - 30)
    if (110 < ix < 850 and 420 < iy < 580) or (300 < ix < 660 and 120 < iy < 380):
        continue
    if (100 < ix < 290 and 110 < iy < 330) or (670 < ix < 860 and 110 < iy < 330):
        continue
    ICONS.append((ix, iy, _rng.choice(('shard', 'shadow')), _rng.uniform(0, 6.28)))

clock = 0.0
hero = None
foes = None


def init():
    global clock, hero, foes
    clock = 0.0
    hero = sheet.load('player.png', 4, 4)
    foes = sheet.load('enemies.png', 4, 5, per_row=True)


def finish():
    pass


def pause():
    pass


def resume():
    pass


def handle_events():
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()


def update():
    global clock
    clock += game_framework.frame_time


def draw():
    clear_canvas()
    t = clock
    box('dark', 0, 0, W, H)
    for ix, iy, kind, ph in ICONS:
        bob = math.sin(t * 1.5 + ph) * 4
        a = 0.35 + 0.2 * math.sin(t * 2 + ph)
        if kind == 'shard':
            img_draw('glow_y', ix, iy + bob, 34, 34, a * 0.5)
            img_draw('px_gold', ix, iy + bob, 9, 9, a + 0.25, math.pi / 4)
        elif foes:
            foes.draw(int(t * 4 + ph) % 4, 0, ix, iy + bob - 10, 22, alpha=a + 0.1)
    draw_util.say_logo(game_settings.TITLE, W / 2, H - 150, 80)
    update_canvas()