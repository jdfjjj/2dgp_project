from pico2d import get_events, clear_canvas, update_canvas, SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE

import game_settings
from game_settings import W, H
import game_framework
import game_world
import darkness
import level
import server
import items
import hud
from player import Player
from enemy import Enemy
from draw_util import box
import title_mode
import gameover_mode


def init():
    game_world.clear()
    level.build()
    game_world.add_object(level.LevelView(), game_world.LAYER_FLOOR)
    server.light_t = game_settings.START_LIGHT
    server.dead_t = 0.0
    server.play_time = 0.0
    server.enemies = []
    server.orbs = []
    server.pickups = []
    for x, y in level.spawns:
        server.enemies.append(Enemy('blob', x, y))
    game_world.add_objects(server.enemies, game_world.LAYER_CHAR)
    for x, y in level.random_spots(game_settings.SHARD_COUNT, level.start, 150):
        server.pickups.append(items.Pickup(x, y))
    game_world.add_objects(server.pickups, game_world.LAYER_ITEM)
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
    dt = game_framework.frame_time
    game_world.update()
    server.update_light(dt)
    server.check_contacts()
    if server.player.hearts > 0:
        server.play_time += dt
    if server.dead_t > 0:                      # 쓰러지고 잠깐 뒤 게임 오버
        server.dead_t -= dt
        if server.dead_t <= 0:
            game_framework.change_mode(gameover_mode)


def draw():
    clear_canvas()
    box('dark', 0, 0, W, H)
    game_world.render()
    hud.draw()
    update_canvas()
