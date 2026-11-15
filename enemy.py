import math
import random

import game_framework
import game_settings
import level
import server
import sheet
from draw_util import img_draw, say, box

ENEMY_PX = {0: 16, 1: 16, 2: 20, 3: 30, 4: 44}   # 적 종류(줄)마다 도트 키. 화면에는 2배로 그림
WANDER_TIME = (1.0, 2.5)                         # 한 방향으로 어슬렁거리는 시간 (초)
MARK_TIME = 0.9                                  # 머리 위 !, ? 가 떠 있는 시간 (초)
KNOCK_SPEED = 260                                # 맞았을 때 밀려나는 속도 (px/s)


class Enemy:
    image = None                 # 12강: 적 그림은 클래스 변수로 한 번만 불러와서 모든 적이 같이 씀

    def __init__(self, kind, x, y):
        if Enemy.image is None:
            Enemy.image = sheet.load('enemies.png', 4, 5, per_row=True,
                                     pixel=ENEMY_PX[0], heights=ENEMY_PX, eyes=True)
        d = game_settings.ENEMY_DEF[kind]
        self.kind = kind
        self.row = d['row']
        self.hp = d['hp']
        self.max_hp = d['hp']
        self.armor = d.get('armor', False)       # 큰 그림자: 빛을 맞아야 공격이 통함
        self.walk_speed = game_settings.kmph_to_pps(d['walk'])
        self.chase_speed = game_settings.kmph_to_pps(d['chase'])
        self.x, self.y = x, y
        self.r = d['r']                          # 충돌 반지름
        self.face = 1
        self.frame = random.random() * 4         # 적마다 움직임이 어긋나 보이게
        self.clock = 0.0
        self.state = 'wander'                    # wander: 어슬렁, chase: 쫓아옴, flee: 빛을 들고 달아남
        self.dir = (0.0, 0.0)
        self.timer = 0.0
        self.last_seen = None                    # 마지막으로 주인공을 본 위치
        self.lost_t = 0.0
        self.mark, self.mark_t = '', 0.0
        self.kx = self.ky = 0.0                  # 밀려나는 속도
        self.hit_t = 0.0                         # 맞고 밀려나는 남은 시간
        self.stun_t = 0.0                        # 기절 남은 시간
        self.expose_t = 0.0                      # 갑옷이 벗겨진 남은 시간
        self.carry = 0.0                         # 빛 도둑이 훔쳐서 들고 있는 빛
        self.slam_t = 0.0                        # 내려찍기 준비 남은 시간
        self.recover_t = 0.0                     # 내려찍은 뒤 멈춰 있는 남은 시간
        self.slam_cd = 0.0                       # 다음 내려찍기까지 남은 시간
        self.pick_wander()

    def feet(self):
        return self.y - self.r

    def scale(self):
        """큰 그림자는 벨 때마다 조금씩 작아짐 (나머지 적은 그대로)"""
        if not self.armor:
            return 1.0
        return 1.0 - game_settings.BRUTE_SHRINK * (self.max_hp - self.hp)

    # ── 어슬렁거리기 ──
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

    # ── 맞았을 때 ──
    def alert(self):
        """어슬렁거리던 중이면 주인공을 쫓기 시작"""
        if self.state == 'wander':
            p = server.player
            self.state = 'chase'
            self.last_seen, self.lost_t = (p.x, p.y), 0.0
            self.show_mark('!')

    def knock(self, nx, ny):
        """공격에 맞음: 맞은 방향 반대로 밀려남 (큰 그림자는 밀려나지 않고 깜빡이기만)"""
        if self.armor:
            self.hit_t = 0.15
        else:
            self.kx, self.ky = nx * KNOCK_SPEED, ny * KNOCK_SPEED
            self.hit_t = 0.25
        self.alert()

    def stun(self, t):
        """빛 구슬에 맞음: 큰 그림자는 갑옷이 벗겨지고, 나머지는 잠깐 기절"""
        if self.armor:
            self.expose_t = game_settings.EXPOSE_TIME
        else:
            self.stun_t = t
        self.alert()

    def steal(self, amount):
        """빛 도둑: 빛을 훔쳐서 달아나기 시작"""
        self.carry = amount
        self.state = 'flee'

    # ── 발견하고 쫓아오기 ──
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

    def flee(self, dt, p):
        """빛을 든 빛 도둑: 주인공 반대쪽으로 달아남 (느려짐)"""
        dx, dy = self.x - p.x, self.y - p.y
        d = max(1.0, math.hypot(dx, dy))
        s = self.chase_speed * game_settings.THIEF_SLOW * dt
        ox, oy = self.x, self.y
        self.step(dx / d * s, dy / d * s)
        if abs(self.x - ox) + abs(self.y - oy) < 0.01:      # 벽에 막히면 옆으로 비켜 감
            self.step(-dy / d * s, dx / d * s)

    def update_slam(self, dt, p):
        """큰 그림자의 내려찍기: 가까우면 멈춰서 빨간 원을 보여 주고, 잠시 뒤 원 안을 내려찍음.
        준비 중이거나 내려찍은 뒤 쉬는 중이면 True (다른 행동 안 함)"""
        self.slam_cd = max(0.0, self.slam_cd - dt)
        if self.slam_t > 0:
            self.slam_t -= dt
            if self.slam_t <= 0:
                server.slam(self)
                self.recover_t = game_settings.SLAM_RECOVER
                self.slam_cd = game_settings.SLAM_CD
            return True
        if self.recover_t > 0:
            self.recover_t -= dt
            return True
        if (self.state == 'chase' and self.slam_cd <= 0 and
                math.hypot(p.x - self.x, p.y - self.y) < game_settings.SLAM_RANGE):
            self.slam_t = game_settings.SLAM_WINDUP
            return True
        return False

    def update(self):
        dt = game_framework.frame_time
        self.clock += dt
        self.mark_t = max(0.0, self.mark_t - dt)
        self.expose_t = max(0.0, self.expose_t - dt)
        if self.hit_t > 0:                       # 맞고 밀려나는 중엔 다른 행동 안 함
            self.hit_t -= dt
            level.move(self, self.kx * dt, self.ky * dt)
            decay = math.exp(-8 * dt)
            self.kx *= decay
            self.ky *= decay
            return
        if self.stun_t > 0:                      # 기절 중엔 움직이지 않음
            self.stun_t -= dt
            return
        p = server.player
        if self.armor and self.update_slam(dt, p):
            return
        self.frame = (self.frame + 6 * dt) % 4
        if self.state == 'wander':
            self.wander(dt)
            if self.sees(p):
                self.state = 'chase'
                self.last_seen, self.lost_t = (p.x, p.y), 0.0
                self.show_mark('!')
        elif self.state == 'flee':
            self.flee(dt, p)
        else:
            self.chase(dt, p)

    # ── 그리기 ──
    def draw(self):
        s = self.scale()
        h = ENEMY_PX[self.row] * 2 * s
        cy = self.feet() + h * 0.5
        img_draw('shadow', self.x, self.feet() + 2, h * 0.9, h * 0.25, 0.8)
        if self.carry > 0:                       # 훔친 빛을 들고 있으면 빛남
            img_draw('glow_y', self.x, cy, h * 2, h * 2, 0.35 + 0.1 * math.sin(self.clock * 6))
        if self.expose_t > 0:                    # 빛을 맞아 벨 수 있는 동안 금빛이 감돔
            img_draw('glow_y', self.x, cy, h * 1.8, h * 1.8, 0.3 + 0.15 * math.sin(self.clock * 8))
        a = 0.35 if self.hit_t > 0 and int(self.hit_t * 30) % 2 == 0 else 1.0   # 맞으면 깜빡임
        if self.stun_t > 0:
            a = 0.55                                                         # 기절하면 흐려짐
        Enemy.image.draw(int(self.frame), self.row, self.x, self.feet(), ENEMY_PX[self.row] * 2,
                         '' if self.face > 0 else 'h', sx=s, sy=s, alpha=a)
        if self.armor and self.hit_t > 0:        # 베이거나 튕겨 낼 때 하얗게 번쩍
            img_draw('glow_w', self.x, cy, h * 1.3, h * 1.3, 0.5)
        if self.armor:                           # 머리 위 게이지 (빛이 닿는 곳에서만 보임)
            self.draw_gauge(h)

    def draw_gauge(self, h):
        """큰 그림자 머리 위 게이지: 칸 수 = 남은 벨 횟수.
        평소엔 보라(벨 수 없음), 빛을 맞으면 금색(벨 수 있음)이 되고 위의 가는 줄이 남은 시간"""
        n, w, gap = self.max_hp, 10, 2               # 칸 수, 한 칸 너비, 칸 사이
        total = n * w + (n - 1) * gap
        x0 = self.x - total / 2
        y = self.feet() + h + 8
        gold = self.expose_t > 0
        for i in range(n):
            x1 = x0 + i * (w + gap)
            box('panel', x1 - 1, y - 3, x1 + w + 1, y + 3)
            if i < self.hp:
                box('px_gold' if gold else 'px_lav', x1, y - 2, x1 + w, y + 2)
        if gold:
            k = self.expose_t / game_settings.EXPOSE_TIME
            box('px_gold', x0, y + 5, x0 + total * k, y + 6, 0.8)

    def draw_warn(self):
        """내려찍기 범위 (빨간 원, 어둠 위에 그림): 내려찍을 때가 가까울수록 진해짐"""
        if self.slam_t > 0:
            k = 1 - self.slam_t / game_settings.SLAM_WINDUP
            s = game_settings.SLAM_RADIUS * 2
            img_draw('warn', self.x, self.y, s, s, 0.3 + 0.5 * k)

    def draw_mark(self):
        """어둠 위에 그리는 표시: 쫓아올 때 빛나는 눈, 머리 위 !, ? (어두운 곳에서도 보임)"""
        s = self.scale()
        h = ENEMY_PX[self.row] * 2 * s
        if self.state == 'chase' and self.stun_t <= 0:              # 쫓아올 때 그림의 눈이 어둠 속에서 빛남
            Enemy.image.draw(int(self.frame), self.row, self.x, self.feet(), ENEMY_PX[self.row] * 2,
                             '' if self.face > 0 else 'h', sx=s, sy=s,
                             alpha=0.75 + 0.25 * math.sin(self.clock * 8), eyes=True)
        if self.mark_t > 0:                                         # 게이지가 있으면 그 위에
            say(self.mark, self.x, self.feet() + h + (26 if self.armor else 14), 22,
                'r' if self.mark == '!' else 'g', 'center', 'pixel')
