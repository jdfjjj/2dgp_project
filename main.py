from pico2d import open_canvas, close_canvas, hide_lattice

import game_framework
import title_mode

open_canvas(960, 640)
try:
    hide_lattice()
except Exception:
    pass
game_framework.run(title_mode)
close_canvas()