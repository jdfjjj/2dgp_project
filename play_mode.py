from pico2d import get_events, clear_canvas, update_canvas, SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE

from game_settings import W, H
import game_framework
import game_world
import darkness
import level
import server
from player import Player
from enemy import Enemy
from draw_util import box
import title_mode


def init():
    game_world.clear()
    level.build()
    game_world.add_object(level.LevelView(), game_world.LAYER_FLOOR)
    server.enemies = []
    server.orbs = []
    for x, y in level.spawns:
        server.enemies.append(Enemy('blob', x, y))
    game_world.add_objects(server.enemies, game_world.LAYER_CHAR)
    server.player = Player(*level.start)
    game_world.add_object(server.player, game_world.LAYER_CHAR)
    game_world.add_object(darkness.Darkness(), game_world.LAYER_DARK)


def finish():
    game_world.clear()


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
        else:
            server.player.handle_event(e)


def update():
    game_world.update()


def draw():
    clear_canvas()
    box('dark', 0, 0, W, H)
    game_world.render()
    update_canvas()
