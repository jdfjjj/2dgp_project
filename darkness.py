import math

import game_framework
import game_settings
import server
from game_settings import W, HUD_Y, CELL, LIGHT_CORE
from draw_util import box, img_draw


def draw_darkness(lights):
    """화면을 CELL 크기 칸으로 나눠서, 칸마다 빛들을 기준으로 어둠의 진하기를 정함.
    lights: [(x, y, 반경), ...]  빛 가운데(LIGHT_CORE)는 완전히 밝고, 바깥으로 갈수록 빠르게 어두워짐.
    빛이 여러 개 겹치면 더 밝아짐"""
    for gy in range(0, HUD_Y, CELL):
        run = None                                   # 완전히 어두운 칸이 이어지는 시작 위치
        for gx in range(0, W, CELL):
            cx, cy = gx + CELL / 2, gy + CELL / 2
            a = 1.0
            for lx, ly, rad in lights:
                d = math.hypot(cx - lx, cy - ly) / rad
                if d < 1.0:
                    t = max(0.0, (d - LIGHT_CORE) / (1 - LIGHT_CORE))
                    a *= t * t * (3 - 2 * t)
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
        lights = ([(p.x, p.y + 20, rad)] + [o.light() for o in server.orbs] +
                  [(e.x, e.y + 10, game_settings.THIEF_LIGHT) for e in server.enemies if e.carry > 0])
        draw_darkness(lights)
        p.draw_aim()                                                      # 공격 범위 부채꼴
        img_draw('glow_y', p.x, p.y + 20, rad * 2.2, rad * 2.2, 0.06)     # 빛이 닿는 곳의 따뜻한 기운
        hx, hy = p.hand()
        img_draw('glow_y', hx, hy, 40, 40, 0.7 + 0.15 * math.sin(t * 11))  # 손의 빛
        img_draw('glow_w', hx, hy, 8, 8, 0.9)
        for e in server.enemies:                                          # 내려찍기 경고 원, 적 눈빛과 !, ?
            e.draw_warn()
            e.draw_mark()
