import math

from transitions import Machine
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDL_MOUSEMOTION

import game_settings
import game_framework
import level
import sheet
from draw_util import img_draw

PIXEL = 33             # 도트 그림의 주인공 키 (px)
PLAYER_HEIGHT = PIXEL * 2        # 화면에 보일 키 = 도트 2배
ROWS = {                         # player.png 줄 번호: (바라보는 쪽, 동작)
    ('side', 'idle'): 0, ('side', 'walk'): 1,
    ('back', 'idle'): 4, ('back', 'walk'): 5,
    ('front', 'idle'): 6, ('front', 'walk'): 7,
}
SPEED = game_settings.kmph_to_pps(game_settings.PLAYER_SPEED_KMPH)   # 16강: 10.7 km/h → 약 190 px/s
IDLE_FPS = 3                     # 대기 동작: 1초에 넘기는 장 수


def walk_frames_per_second():
    """16강: 1초에 넘길 걷기 그림 장 수 = 속도(m/s) / 한 걸음 주기 길이(m) × 한 주기 장 수"""
    speed_mps = SPEED / game_settings.PIXEL_PER_METER
    return speed_mps / game_settings.STRIDE_LENGTH_M * game_settings.WALK_FRAMES_PER_STRIDE


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
        p.draw_frame('idle', int(p.frame))


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
        p.frame = (p.frame + walk_frames_per_second() * game_framework.frame_time) % 4
        p.walk()

    def draw(self, p):
        p.draw_frame('walk', int(p.frame))


class Player:
    image = None                 # 12강: 그림은 클래스 변수로 한 번만 불러와서 같이 씀

    def __init__(self, x, y):
        if Player.image is None:
            Player.image = sheet.load('player.png', 4, 8, pixel=PIXEL,
                                      groups=((0, 1, 2, 3), (4, 5), (6, 7)))   # 옆, 뒤, 앞모습 묶음
        self.x, self.y = x, y
        self.r = 12              # 충돌 반지름
        self.face = 1            # 옆모습일 때 1: 오른쪽, -1: 왼쪽
        self.view = 'side'       # side: 옆모습, back: 뒷모습(위를 봄), front: 앞모습(아래를 봄)
        self.fx, self.fy = 1.0, 0.0   # 바라보는 방향 (2주차에 공격·던지기 방향으로 씀)
        self.frame = 0.0
        self.held = set()        # 지금 누르고 있는 이동키
        self.mouse = (x + 100, y)     # 마우스 위치 (게임 화면 좌표)
        self.mouse_aim = False        # 멈춘 뒤 마우스를 움직였을 때만 마우스 쪽을 봄

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
        elif e.type == SDL_MOUSEMOTION:
            self.mouse = (e.x, game_settings.H - 1 - e.y)
            self.mouse_aim = True

    def input_dir(self):
        held = self.held
        mx = int(any(k in held for k in game_settings.KEY_RIGHT)) - int(any(k in held for k in game_settings.KEY_LEFT))
        my = int(any(k in held for k in game_settings.KEY_UP)) - int(any(k in held for k in game_settings.KEY_DOWN))
        return mx, my

    def update_aim(self):
        """걷는 중엔 걷는 방향, 멈춘 뒤 마우스를 움직이면 마우스 쪽을 바라봄"""
        mx, my = self.input_dir()
        if mx or my:
            ln = math.hypot(mx, my)
            ax, ay = mx / ln, my / ln
            self.mouse_aim = False                 # 걷는 동안은 마우스 방향을 쓰지 않음
        elif self.mouse_aim:
            dx, dy = self.mouse[0] - self.x, self.mouse[1] - (self.y + 20)
            d = math.hypot(dx, dy)
            if d < 8:                              # 커서가 캐릭터 위에 있으면 그대로
                return
            ax, ay = dx / d, dy / d
        else:
            return                                 # 멈춘 뒤 마우스를 안 움직였으면 걷던 방향 그대로
        self.fx, self.fy = ax, ay
        if abs(ax) > 0.15:
            self.face = 1 if ax > 0 else -1
        self.view = 'back' if ay > 0.75 else ('front' if ay < -0.75 else 'side')

    def walk(self):
        mx, my = self.input_dir()
        ln = math.hypot(mx, my)                    # 대각선도 같은 속도로
        d = SPEED * game_framework.frame_time
        level.move(self, mx / ln * d, my / ln * d)

    def feet(self):
        return self.y - self.r

    def hand(self):
        """손에 든 빛의 위치 (바라보는 쪽에 따라 다름)"""
        f = self.feet()
        if self.view == 'back':
            return self.x + 7, f + 25
        if self.view == 'front':
            return self.x + 11, f + 16
        return self.x + self.face * 12, f + 17

    def update(self):
        self.update_aim()
        self.states[self.state].do(self)

    def draw(self):
        img_draw('shadow', self.x, self.feet() + 2, 34, 9, 0.9)
        self.states[self.state].draw(self)

    def draw_frame(self, kind, col):
        row = ROWS[(self.view, kind)]
        flip = 'h' if self.view == 'side' and self.face < 0 else ''
        Player.image.draw(col, row, self.x, self.feet(), PLAYER_HEIGHT, flip)
