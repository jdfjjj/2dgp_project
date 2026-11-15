import math

import game_framework
import game_settings
import level
import server
import effects
from draw_util import img_draw


class Orb:
    """던진 빛 구슬: 날아가다가 적이나 벽에 닿거나 최대 거리에 가면 떨어져서 잠시 주변을 밝힘
    (어둠 위의 이펙트 레이어에 넣어서 어두운 곳에서도 보임)"""

    def __init__(self, x, y, fx, fy):
        self.x, self.y = x, y
        self.vx, self.vy = fx * game_settings.ORB_SPEED, fy * game_settings.ORB_SPEED
        self.r = 5
        self.dist = 0.0
        self.flying = True
        self.life = server.ST['orb_life']
        self.clock = 0.0

    def update(self):
        dt = game_framework.frame_time
        self.clock += dt
        if self.flying:
            self.fly(dt)
        else:
            self.life -= dt
            if self.life <= 0:
                server.remove_orb(self)

    def fly(self, dt):
        dx, dy = self.vx * dt, self.vy * dt
        if level.ch_at(self.x + dx, self.y + dy) == '#':    # 벽에 닿으면 그 앞에 떨어짐
            self.land()
            return
        self.x += dx
        self.y += dy
        self.dist += math.hypot(dx, dy)
        for e in server.enemies:
            if math.hypot(e.x - self.x, e.y - self.y) < e.r + self.r + 4:
                server.orb_hit(e)
                self.land()
                return
        if self.dist >= game_settings.ORB_RANGE:
            self.land()

    def land(self):
        self.flying = False
        effects.burst(self.x, self.y, 'px_gold', 10, 90)

    def light(self):
        """이 구슬이 밝히는 빛 (x, y, 반경). 꺼지기 전 1초 동안 점점 작아짐"""
        if self.flying:
            return self.x, self.y, 44
        k = min(1.0, self.life)
        return self.x, self.y, game_settings.ORB_LIGHT * (0.3 + 0.7 * k)

    def draw(self):
        k = 1.0 if self.flying else min(1.0, self.life)
        flick = 0.8 + 0.2 * math.sin(self.clock * 12)
        img_draw('glow_y', self.x, self.y, 48 * k, 48 * k, 0.8 * flick)
        img_draw('i_light', self.x, self.y, 18, 18, k)
