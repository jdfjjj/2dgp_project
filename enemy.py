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

    def feet(self):
        return self.y - self.r

    def update(self):
        self.frame = (self.frame + 6 * game_framework.frame_time) % 4

    def draw(self):
        h = ENEMY_PX[self.row] * 2
        img_draw('shadow', self.x, self.feet() + 2, h * 0.9, h * 0.25, 0.8)
        Enemy.image.draw(int(self.frame), self.row, self.x, self.feet(), h,
                         '' if self.face > 0 else 'h')
