import math
import random

import game_framework
import game_world
from draw_util import img_draw, IMG, say


class Particle:
    """작은 네모 조각 (도트 느낌): 사방으로 튀었다가 사라짐"""

    def __init__(self, x, y, img, speed):
        a = random.uniform(0, math.tau)
        s = random.uniform(0.3, 1.0) * speed
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a) * s, math.sin(a) * s
        self.img = img
        self.life = self.max_life = random.uniform(0.25, 0.5)
        self.size = random.choice((2, 4))

    def update(self):
        dt = game_framework.frame_time
        self.x += self.vx * dt
        self.y += self.vy * dt
        decay = math.exp(-6 * dt)
        self.vx *= decay
        self.vy *= decay
        self.life -= dt
        if self.life <= 0:
            game_world.remove_object(self)

    def draw(self):
        img_draw(self.img, self.x, self.y, self.size, self.size, self.life / self.max_life)


class Slash:
    """공격 이펙트: 부채꼴이 번쩍 빛났다가 사라짐"""
    TIME = 0.15

    def __init__(self, x, y, ang, reach, arc):
        self.x, self.y = x, y
        self.ang, self.reach = ang, reach
        self.name = 'fan%d' % int(round(arc))
        if self.name not in IMG:
            self.name = 'fan110'
        self.t = Slash.TIME

    def update(self):
        self.t -= game_framework.frame_time
        if self.t <= 0:
            game_world.remove_object(self)

    def draw(self):
        k = self.t / Slash.TIME
        s = self.reach * 2 * (1.05 - 0.1 * k)                   # 살짝 퍼지면서 사라짐
        img_draw(self.name, self.x, self.y, s, s, 0.9 * k, self.ang)


class FloatText:
    """위로 떠오르다가 사라지는 글자 (빛 부족 같은 짧은 알림)"""
    TIME = 0.8

    def __init__(self, x, y, s, color, size):
        self.x, self.y = x, y
        self.s, self.color, self.size = s, color, size
        self.t = FloatText.TIME

    def update(self):
        dt = game_framework.frame_time
        self.t -= dt
        self.y += 30 * dt
        if self.t <= 0:
            game_world.remove_object(self)

    def draw(self):
        say(self.s, self.x, self.y, self.size, self.color, 'center', 'pixel')


def burst(x, y, img, n, speed=110):
    """조각 n개를 한꺼번에 흩뿌림"""
    game_world.add_objects([Particle(x, y, img, speed) for _ in range(n)], game_world.LAYER_FX)


def slash(x, y, ang, reach, arc):
    game_world.add_object(Slash(x, y, ang, reach, arc), game_world.LAYER_FX)


def text(x, y, s, color='w', size=22):
    game_world.add_object(FloatText(x, y, s, color, size), game_world.LAYER_FX)
