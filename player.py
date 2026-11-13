import math

from pico2d import SDL_KEYDOWN, SDL_KEYUP

import game_settings
import game_framework
import sheet
from draw_util import img_draw

PIXEL = 37                       # 도트 그림의 주인공 키 (px)
PLAYER_HEIGHT = PIXEL * 2        # 화면에 보일 키 = 도트 2배
ROW_IDLE = 0                     # player.png에서 옆모습 대기 줄
SPEED = 180                      # 1초에 움직이는 거리 (px)


class Player:
    image = None                 # 12강: 그림은 클래스 변수로 한 번만 불러와서 같이 씀

    def __init__(self, x, y):
        if Player.image is None:
            Player.image = sheet.load('player.png', 4, 8, pixel=PIXEL)
        self.x, self.y = x, y
        self.r = 12              # 충돌 반지름
        self.face = 1            # 1: 오른쪽을 봄, -1: 왼쪽을 봄
        self.frame = 0.0
        self.clock = 0.0
        self.held = set()        # 지금 누르고 있는 이동키

    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key in game_settings.KEY_MOVE:
            self.held.add(e.key)
        elif e.type == SDL_KEYUP:
            self.held.discard(e.key)

    def input_dir(self):
        held = self.held
        mx = int(any(k in held for k in game_settings.KEY_RIGHT)) - int(any(k in held for k in game_settings.KEY_LEFT))
        my = int(any(k in held for k in game_settings.KEY_UP)) - int(any(k in held for k in game_settings.KEY_DOWN))
        return mx, my

    def feet(self):
        return self.y - self.r

    def update(self):
        dt = game_framework.frame_time
        self.clock += dt
        self.frame = (self.clock * 3) % 4          # 대기 동작 (1초에 3장)
        mx, my = self.input_dir()
        if mx or my:
            if mx:
                self.face = mx
            ln = math.hypot(mx, my)                # 대각선도 같은 속도로
            self.x += mx / ln * SPEED * dt
            self.y += my / ln * SPEED * dt

    def draw(self):
        img_draw('shadow', self.x, self.feet() + 2, 34, 9, 0.9)
        Player.image.draw(int(self.frame), ROW_IDLE, self.x, self.feet(), PLAYER_HEIGHT,
                          '' if self.face > 0 else 'h')
