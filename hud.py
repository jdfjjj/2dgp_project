import server
import game_settings
from game_settings import W, H, HUD_Y
from draw_util import img_draw, box

BAR_W, BAR_H = 200, 12                   # 빛 게이지 크기 (화면 가운데, 맵 맨 위에 작게)
BAR_TICKS = 10                           # 게이지를 나누는 칸 수


def draw():
    """화면 위쪽 정보창: 하트, 그 아래 가운데에 빛 게이지"""
    box('px_lav', 0, HUD_Y, W, HUD_Y + 1, 0.25)                      # 정보창 아래 경계선
    draw_hearts((HUD_Y + H) / 2)
    draw_light_bar(HUD_Y - 18)


def draw_hearts(y):
    """하트: 남은 하트는 빨갛게, 잃은 하트는 비어 있게 (도트 3배)"""
    p = server.player
    for i in range(game_settings.MAX_HEARTS):
        name = 'i_heart' if i < p.hearts else 'i_heart_e'
        img_draw(name, 32 + i * 36, y, 27, 24)


def draw_light_bar(y):
    """빛 게이지: 화면 가운데에 칸으로 나뉜 금빛 막대. 차 있는 끝에 빛 번짐"""
    cap = server.ST['light_cap']
    k = max(0.0, min(1.0, server.light_t / cap))
    x1, x2 = W / 2 - BAR_W / 2 + 10, W / 2 + BAR_W / 2 + 10
    box('shade', x1 - 34, y - 14, x2 + 8, y + 14, 0.6)               # 뒤 배경
    img_draw('glow_y', x1 - 18, y, 30 + 16 * k, 30 + 16 * k, 0.25 + 0.55 * k)
    img_draw('i_light', x1 - 18, y, 18, 18)
    box('px_white', x1 - 2, y - BAR_H / 2 - 2, x2 + 2, y + BAR_H / 2 + 2, 0.25)
    box('panel', x1, y - BAR_H / 2, x2, y + BAR_H / 2)
    if k > 0:
        fx = x1 + (x2 - x1) * k
        box('bar_gold', x1, y - BAR_H / 2, fx, y + BAR_H / 2)
        box('px_white', x1, y + 2, fx, y + 5, 0.35)                  # 윗부분 반짝임
        img_draw('glow_y', fx, y, 30, 30, 0.7)
    for i in range(1, BAR_TICKS):                                    # 칸 나눔 선
        tx = x1 + (x2 - x1) * i / BAR_TICKS
        box('panel', tx - 1, y - BAR_H / 2, tx + 1, y + BAR_H / 2, 0.9)
