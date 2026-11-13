import math

import game_framework
import server
from game_settings import W, HUD_Y, CELL
from draw_util import box, img_draw


def draw_darkness(lights):
    """화면을 CELL 크기 칸으로 나눠서, 칸마다 가장 가까운 빛을 기준으로 어둠의 진하기를 정함.
    lights: [(x, y, 반경), ...]  빛 가운데는 밝고 가장자리로 갈수록 어두워짐"""
    for gy in range(0, HUD_Y, CELL):
        run = None                                   # 완전히 어두운 칸이 이어지는 시작 위치
        for gx in range(0, W, CELL):
            cx, cy = gx + CELL / 2, gy + CELL / 2
            a = 1.0
            for lx, ly, rad in lights:
                d = math.hypot(cx - lx, cy - ly) / rad
                if d < 1.0:
                    a = min(a, d * d)
            if a >= 0.999:                           # 완전히 어두운 칸은 모아서 한 번에 그림
                if run is None:
                    run = gx
                continue
            if run is not None:
                box('dark', run, gy, gx, gy + CELL)
                run = None
            if a > 0.02:
                box('dark', gx, gy, gx + CELL, gy + CELL, a)
        if run is not None:
            box('dark', run, gy, W, gy + CELL)


class Darkness:
    """맵 위를 덮는 어둠과 빛 (게임 월드의 어둠 레이어에 넣음)"""

    def __init__(self):
        self.clock = 0.0

    def update(self):
        self.clock += game_framework.frame_time

    def draw(self):
        p = server.player
        t = self.clock
        rad = server.light_radius() * (1 + 0.02 * math.sin(t * 9))       # 빛이 살짝 일렁임
        draw_darkness([(p.x, p.y + 20, rad)])
        img_draw('glow_y', p.x, p.y + 20, rad * 2.2, rad * 2.2, 0.06)     # 빛이 닿는 곳의 따뜻한 기운
        hx, hy = p.hand()
        img_draw('glow_y', hx, hy, 40, 40, 0.7 + 0.15 * math.sin(t * 11))  # 손의 빛
        img_draw('glow_w', hx, hy, 8, 8, 0.9)
