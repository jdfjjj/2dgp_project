from pico2d import (get_events, clear_canvas, update_canvas, SDL_QUIT, SDL_KEYDOWN,
                    SDLK_ESCAPE, SDLK_SPACE, SDLK_RETURN, SDLK_r, SDLK_q)

from game_settings import W, H
import game_framework
import server
import draw_util
from draw_util import img_draw, box, say
import play_mode
import title_mode

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
        elif e.type == SDL_KEYDOWN and clock > 0.5:      # 쓰러질 때 누르던 키로 바로 넘어가지 않게
            if e.key in (SDLK_r, SDLK_SPACE, SDLK_RETURN):
                game_framework.change_mode(play_mode)
            elif e.key in (SDLK_q, SDLK_ESCAPE):
                game_framework.change_mode(title_mode)


def update():
    global clock
    clock += game_framework.frame_time


def draw():
    clear_canvas()
    box('dark', 0, 0, W, H)
    img_draw('glow_l', W / 2, H / 2 + 90, 700, 240, 0.08)
    draw_util.say_logo('GAME OVER', W / 2, H / 2 + 90, 64)
    t = int(server.play_time)
    say('플레이 시간  %d:%02d' % (t // 60, t % 60), W / 2, H / 2 - 10, 22, 'p', 'center', 'pixel')
    if int(clock * 2) % 2 == 0:
        say('R 다시 하기   ·   Q 메인 화면', W / 2, H / 2 - 90, 20, 'g', 'center', 'pixel')
    update_canvas()
