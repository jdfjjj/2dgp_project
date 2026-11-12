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

MENU = ['게임 시작', '조작법', '게임 종료']
BTN_W, BTN_H, BTN_Y, BTN_GAP = 280, 44, 330, 62

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
sel = 0
hero = None
foes = None


def init():
    global clock, sel, hero, foes
    clock = 0.0
    sel = 0
    hero = sheet.load('player.png', 4, 4)
    foes = sheet.load('enemies.png', 4, 5, per_row=True)


def finish():
    pass


def pause():
    pass


def resume():
    pass


def go():
    if sel == 2:
        game_framework.quit()
    # 게임 시작은 플레이 모드를 만든 뒤 연결, 조작법은 4주차에 연결


def handle_events():
    global sel
    for e in get_events():
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key in game_settings.KEY_UP:
                sel = (sel - 1) % len(MENU)
            elif e.key in game_settings.KEY_DOWN:
                sel = (sel + 1) % len(MENU)
            elif e.key in (SDLK_SPACE, SDLK_RETURN):
                go()
            elif e.key == SDLK_ESCAPE:
                game_framework.quit()
        elif e.type in (SDL_MOUSEMOTION, SDL_MOUSEBUTTONDOWN):
            mx, my = e.x, H - 1 - e.y
            for i in range(len(MENU)):
                if abs(mx - W / 2) < BTN_W / 2 and abs(my - (BTN_Y - i * BTN_GAP)) < BTN_H / 2:
                    sel = i
                    if e.type == SDL_MOUSEBUTTONDOWN:
                        go()


def update():
    global clock
    clock += game_framework.frame_time


def draw_button(label, x, y, selected):
    w, h = BTN_W, BTN_H
    if selected:
        img_draw('glow_y', x, y, w * 1.3, h * 2.4, 0.12 + 0.06 * math.sin(clock * 4))
        box('px_gold', x - w / 2 - 2, y - h / 2 - 2, x + w / 2 + 2, y + h / 2 + 2)
        box('bar_gold', x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        draw_str(label, x, y, 22, 'center', [(0, 0, COLORS['k'])], 'pixel')
    else:
        box('px_white', x - w / 2 - 1, y - h / 2 - 1, x + w / 2 + 1, y + h / 2 + 1, 0.25)
        box('panel', x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        draw_str(label, x, y, 22, 'center', [(0, 0, COLORS['g'])], 'pixel')


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

    hx, hy = 190, 160                                    # 주인공
    img_draw('glow_y', hx + 10, hy + 70, 240, 240, 0.16)
    img_draw('shadow', hx, hy + 2, 80, 14, 0.9)
    if hero:
        hero.draw(int(t * 4) % 4, 0, hx, hy + abs(math.sin(t * 2.2)) * 4, 140)

    ex, ey = 770, 160                                    # 적 (큰 그림자)
    img_draw('shadow', ex, ey + 2, 100, 14, 0.9)
    if foes:
        foes.draw(int(t * 3) % 4, 3, ex, ey + math.sin(t * 3) * 3, 120)

    for i, label in enumerate(MENU):
        draw_button(label, W / 2, BTN_Y - i * BTN_GAP, i == sel)
    say('2DGP TERM PROJECT', W / 2, 26, 12, 'g', 'center', 'clean')
    update_canvas()