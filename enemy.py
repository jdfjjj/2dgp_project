import math
import random

import game_framework
import game_settings
import level
import server
import sheet
from draw_util import img_draw, say

ENEMY_PX = {0: 16, 1: 16, 2: 20, 3: 30, 4: 44}   # 적 종류(줄)마다 도트 키. 화면에는 2배로 그림
WANDER_TIME = (1.0, 2.5)                         # 한 방향으로 어슬렁거리는 시간 (초)
MARK_TIME = 0.9                                  # 머리 위 !, ? 가 떠 있는 시간 (초)


class Enemy:
    image = None                 # 12강: 적 그림은 클래스 변수로 한 번만 불러와서 모든 적이 같이 씀

    def __init__(self, kind, x, y):
        if Enemy.image is None:
            Enemy.image = sheet.load('enemies.png', 4, 5, per_row=True,
                                     pixel=ENEMY_PX[0], heights=ENEMY_PX)
        d = game_settings.ENEMY_DEF[kind]
        self.kind = kind
        self.row = d['row']
        self.hp = d['hp']
        self.walk_speed = game_settings.kmph_to_pps(d['walk'])
        self.chase_speed = game_settings.kmph_to_pps(d['chase'])
        self.x, self.y = x, y
        self.r = d['r']                          # 충돌 반지름
        self.face = 1
        self.frame = random.random() * 4         # 적마다 움직임이 어긋나 보이게
        self.state = 'wander'                    # wander: 어슬렁거림, chase: 쫓아옴
        self.dir = (0.0, 0.0)
        self.timer = 0.0
        self.last_seen = None                    # 마지막으로 주인공을 본 위치
        self.lost_t = 0.0
        self.mark, self.mark_t = '', 0.0
        self.pick_wander()

    def feet(self):
        return self.y - self.r

    def pick_wander(self):
        if random.random() < 0.3:
            self.dir = (0.0, 0.0)                # 잠깐 멈춰 있기
        else:
            a = random.uniform(0, math.tau)
            self.dir = (math.cos(a), math.sin(a))
        self.timer = random.uniform(*WANDER_TIME)

    def wander(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.pick_wander()
        self.step(self.dir[0] * self.walk_speed * dt, self.dir[1] * self.walk_speed * dt)

    def step(self, dx, dy):
        ox, oy = self.x, self.y
        level.move(self, dx, dy)
        if abs(dx) > 0.01:
            self.face = 1 if dx > 0 else -1
        moved = abs(self.x - ox) + abs(self.y - oy)
        if self.state == 'wander' and (dx or dy) and moved < 0.01:
            self.pick_wander()                   # 벽에 막히면 다른 방향으로

    def show_mark(self, mark):
        self.mark, self.mark_t = mark, MARK_TIME

    def sees(self, p):
        d = math.hypot(p.x - self.x, p.y - self.y)
        if d < game_settings.CLOSE_DETECT:
            return True
        reach = game_settings.DETECT_BASE + server.light_radius() * 0.5   # 빛이 밝을수록 멀리서 알아챔
        return d < reach and level.can_see(self.x, self.y, p.x, p.y)

    def chase(self, dt, p):
        if self.sees(p):
            self.last_seen = (p.x, p.y)
            self.lost_t = 0.0
        else:
            self.lost_t += dt
        tx, ty = self.last_seen
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        if self.lost_t > game_settings.LOSE_TIME or (self.lost_t > 0 and d < 6):
            self.state = 'wander'                # 놓쳤으면 포기
            self.show_mark('?')
            self.pick_wander()
            return
        if d > 1:
            s = self.chase_speed * dt
            self.step(dx / d * s, dy / d * s)

    def update(self):
        dt = game_framework.frame_time
        self.frame = (self.frame + 6 * dt) % 4
        self.mark_t = max(0.0, self.mark_t - dt)
        p = server.player
        if self.state == 'wander':
            self.wander(dt)
            if self.sees(p):
                self.state = 'chase'
                self.last_seen, self.lost_t = (p.x, p.y), 0.0
                self.show_mark('!')
        else:
            self.chase(dt, p)

    def draw(self):
        h = ENEMY_PX[self.row] * 2
        img_draw('shadow', self.x, self.feet() + 2, h * 0.9, h * 0.25, 0.8)
        Enemy.image.draw(int(self.frame), self.row, self.x, self.feet(), h,
                         '' if self.face > 0 else 'h')

    def draw_mark(self):
        """머리 위 !, ? (어둠 위에 그려서 어두운 곳에서도 보임)"""
        if self.mark_t > 0:
            h = ENEMY_PX[self.row] * 2
            say(self.mark, self.x, self.feet() + h + 14, 22,
                'y' if self.mark == '!' else 'g', 'center', 'pixel')
