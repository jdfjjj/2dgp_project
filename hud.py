import server
from game_settings import H, HUD_Y
from draw_util import img_draw, box

BAR_X, BAR_W, BAR_H = 150, 240, 12       # 빛 게이지 위치와 크기


def draw():
    """화면 위쪽 정보창 (지금은 빛 게이지만, 하트는 다음에 추가)"""
    y = (HUD_Y + H) / 2
    draw_light_bar(y)


def draw_light_bar(y):
    cap = server.ST['light_cap']
    k = max(0.0, min(1.0, server.light_t / cap))
    img_draw('glow_y', BAR_X - 22, y, 34, 34, 0.5)
    img_draw('i_light', BAR_X - 22, y, 18, 18)
    box('px_white', BAR_X - 2, y - BAR_H / 2 - 2, BAR_X + BAR_W + 2, y + BAR_H / 2 + 2, 0.25)
    box('panel', BAR_X, y - BAR_H / 2, BAR_X + BAR_W, y + BAR_H / 2)
    box('bar_gold', BAR_X, y - BAR_H / 2, BAR_X + BAR_W * k, y + BAR_H / 2)
    tick = BAR_X + BAR_W * (4 / cap)                 # 이 아래로 내려가면 시야가 좁아지기 시작
    box('px_white', tick - 1, y - BAR_H / 2, tick + 1, y + BAR_H / 2, 0.5)
