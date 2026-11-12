from pico2d import get_events, clear_canvas, update_canvas, SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE

import game_framework


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
            game_framework.quit()


def update():
    pass


def draw():
    clear_canvas()
    update_canvas()