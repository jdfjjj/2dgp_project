import game_framework
import sheet
from draw_util import img_draw

PIXEL = 37                       # 도트 그림의 주인공 키 (px)
PLAYER_HEIGHT = PIXEL * 2        # 화면에 보일 키 = 도트 2배
ROW_IDLE = 0                     # player.png에서 옆모습 대기 줄


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
