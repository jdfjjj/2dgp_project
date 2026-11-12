import math

from pico2d import get_events, clear_canvas, update_canvas, SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE

import game_settings
from game_settings import W, H
import game_framework
import draw_util
from draw_util import img_draw, box, say

clock = 0.0


def init():
    global clock
    clock = 0.0


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
    box('dark', 0, 0, W, H)
    img_draw('glow_l', W / 2, H / 2 + 60, 700, 260, 0.12 + 0.04 * math.sin(clock * 2))
    draw_util.say_logo(game_settings.TITLE, W / 2, H / 2 + 60, 72)
    if int(clock * 2) % 2 == 0:
        say('스페이스를 눌러 시작', W / 2, H / 2 - 80, 22, 'p', 'center')
    say('2DGP TERM PROJECT', W / 2, 26, 12, 'g', 'center', 'clean')
    update_canvas()