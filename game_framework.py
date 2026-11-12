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


def push_mode(mode):
    global stack
    if len(stack) > 0:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    global stack
    if len(stack) > 0:
        stack[-1].finish()
        stack.pop()
    if len(stack) > 0:
        stack[-1].resume()


def quit():
    global running
    running = False


def run(start_mode):
    global running, stack
    running = True
    stack = [start_mode]
    start_mode.init()

    while running:
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()
        delay(0.004)                         # CPU를 너무 많이 쓰지 않게 잠깐 쉼

    while len(stack) > 0:
        stack[-1].finish()
        stack.pop()