from pico2d import open_canvas, close_canvas, hide_lattice

import game_settings
import game_framework
import title_mode

open_canvas(game_settings.W, game_settings.H)
try:
    hide_lattice()
except Exception:
    pass
game_framework.run(title_mode)
close_canvas()