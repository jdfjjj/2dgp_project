import time
from pico2d import delay

running = None
stack = None
frame_time = 0.0
MAX_FRAME_TIME = 0.05        # 창을 끌거나 로딩이 길어져도 한 번에 너무 많이 움직이지 않게


def change_mode(mode):
    global stack
    if len(stack) > 0:
        stack[-1].finish()
        stack.pop()
    stack.append(mode)
    mode.init()