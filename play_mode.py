from pico2d import get_events, clear_canvas, update_canvas, SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE

from game_settings import W, H
import game_framework
from draw_util import box, say
import title_mode


def init():
    pass


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
            game_framework.change_mode(title_mode)


def update():
    pass


def draw():
    clear_canvas()
    box('dark', 0, 0, W, H)
    say('플레이 모드', W / 2, H / 2 + 20, 32, 'l', 'center')
    say('ESC를 누르면 타이틀로 돌아가요', W / 2, H / 2 - 30, 18, 'g', 'center')
    update_canvas()
