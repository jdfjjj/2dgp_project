import math

from transitions import Machine
from pico2d import SDL_KEYDOWN, SDL_KEYUP

import game_settings
import game_framework
import level
import sheet
from draw_util import img_draw

PIXEL = 37                       # 도트 그림의 주인공 키 (px)
PLAYER_HEIGHT = PIXEL * 2        # 화면에 보일 키 = 도트 2배
ROW_IDLE, ROW_WALK = 0, 1        # player.png 줄: 옆모습 대기, 옆모습 걷기
SPEED = 180                      # 1초에 움직이는 거리 (px)
IDLE_FPS, WALK_FPS = 3, 8        # 1초에 넘기는 애니메이션 장 수


class Idle:
    """서 있기: 대기 동작, 이동키를 누르면 RUN으로"""

    def enter(self, p):
        p.frame = 0.0

    def exit(self, p):
        pass

    def do(self, p):
        p.frame = (p.frame + IDLE_FPS * game_framework.frame_time) % 4
        if p.input_dir() != (0, 0):
            p.move_start()

    def draw(self, p):
        p.draw_frame(ROW_IDLE, int(p.frame))


class Run:
    """걷기: 이동하면서 걷기 동작, 이동키를 다 떼면 IDLE로"""

    def enter(self, p):
        p.frame = 0.0

    def exit(self, p):
        pass

    def do(self, p):
        if p.input_dir() == (0, 0):
            p.move_stop()
            return
        p.frame = (p.frame + WALK_FPS * game_framework.frame_time) % 4
        p.walk()

    def draw(self, p):
        p.draw_frame(ROW_WALK, int(p.frame))


class Player:
    image = None                 # 12강: 그림은 클래스 변수로 한 번만 불러와서 같이 씀

    def __init__(self, x, y):
        if Player.image is None:
            Player.image = sheet.load('player.png', 4, 8, pixel=PIXEL)
        self.x, self.y = x, y
        self.r = 12              # 충돌 반지름
        self.face = 1            # 1: 오른쪽을 봄, -1: 왼쪽을 봄
        self.frame = 0.0
        self.held = set()        # 지금 누르고 있는 이동키

        # 13강 상태 머신: 언제 어떤 상태로 바뀌는지는 transitions가, 상태마다 할 일은 상태 클래스가
        self.states = {'IDLE': Idle(), 'RUN': Run()}
        self.machine = Machine(model=self, states=list(self.states), initial='IDLE',
                               auto_transitions=False, ignore_invalid_triggers=True,
                               before_state_change='_exit_state', after_state_change='_enter_state')
        self.machine.add_transition('move_start', 'IDLE', 'RUN')
        self.machine.add_transition('move_stop', 'RUN', 'IDLE')
        self.states[self.state].enter(self)

    def _exit_state(self):
        self.states[self.state].exit(self)

    def _enter_state(self):
        self.states[self.state].enter(self)

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

    def walk(self):
        mx, my = self.input_dir()
        if mx:
            self.face = mx
        ln = math.hypot(mx, my)                    # 대각선도 같은 속도로
        d = SPEED * game_framework.frame_time
        level.move(self, mx / ln * d, my / ln * d)

    def feet(self):
        return self.y - self.r

    def update(self):
        self.states[self.state].do(self)

    def draw(self):
        img_draw('shadow', self.x, self.feet() + 2, 34, 9, 0.9)
        self.states[self.state].draw(self)

    def draw_frame(self, row, col):
        Player.image.draw(col, row, self.x, self.feet(), PLAYER_HEIGHT, '' if self.face > 0 else 'h')
