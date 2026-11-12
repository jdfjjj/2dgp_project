from pico2d import open_canvas, close_canvas, hide_lattice

open_canvas(960, 640)
try:
    hide_lattice()
except Exception:
    pass
close_canvas()