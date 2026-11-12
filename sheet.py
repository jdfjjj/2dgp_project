import os
import ctypes

from pico2d import load_image

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
ALPHA_CUT = bytes(0 if a <= 40 else 1 for a in range(256))     # 거의 투명한 점은 무시
ON = b'\x01'


def _set_smooth(on):
    try:
        from sdl2 import SDL_SetHint, SDL_HINT_RENDER_SCALE_QUALITY
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b'1' if on else b'0')
    except Exception:
        pass


def _alpha_rows(path):
    """PNG의 투명도 값을 줄 단위로 읽음 (0: 투명, 1: 그림 있음)"""
    try:
        import sdl2
        from sdl2.sdlimage import IMG_Load
        fmt = getattr(sdl2, 'SDL_PIXELFORMAT_RGBA32', None) or sdl2.SDL_PIXELFORMAT_ABGR8888
        surf = IMG_Load(path.encode('utf-8'))
        if not surf:
            return None
        conv = sdl2.SDL_ConvertSurfaceFormat(surf, fmt, 0)
        sdl2.SDL_FreeSurface(surf)
        if not conv:
            return None
        s = conv.contents
        w, h, pitch = s.w, s.h, s.pitch
        data = ctypes.string_at(s.pixels, pitch * h)
        sdl2.SDL_FreeSurface(conv)
        return [data[y * pitch + 3: y * pitch + w * 4: 4].translate(ALPHA_CUT) for y in range(h)]
    except Exception as ex:
        print('시트 분석 실패:', ex)
        return None


def _bands(flags, gap=12):
    """그림이 있는 줄들을 덩어리로 묶음"""
    bands, start, last = [], None, None
    for i, f in enumerate(flags):
        if not f:
            continue
        if start is None:
            start = i
        elif i - last > gap:
            bands.append((start, last))
            start = i
        last = i
    if start is not None:
        bands.append((start, last))
    return bands


def _measure(rows, x0, x1, y0, y1):
    """한 칸에서 (왼쪽, 위, 너비, 높이, 발 x)를 찾음"""
    ys = [y for y in range(y0, y1 + 1) if ON in rows[y][x0:x1]]
    if not ys:
        return None
    top, bottom = ys[0], ys[-1]
    left, right = x1, x0
    for y in ys:
        seg = rows[y][x0:x1]
        a, b = seg.find(ON), seg.rfind(ON)
        if a >= 0:
            left = min(left, x0 + a)
            right = max(right, x0 + b)
    bh = bottom - top + 1
    band = max(2, int(bh * 0.08))
    xs = sorted(x for y in range(bottom - band, bottom + 1)
                for x in range(left, right + 1) if rows[y][x])
    foot = (xs[len(xs) // 2] if xs else (left + right) / 2) - left
    return left, top, right - left + 1, bh, foot


class Sheet:
    def __init__(self, path, cols, rows, per_row=False):
        _set_smooth(True)
        self.image = load_image(path)
        _set_smooth(False)
        self.per_row = per_row                    # True면 줄마다 따로 키를 맞춤 (적처럼 줄마다 다른 그림)
        iw, ih = self.image.w, self.image.h
        cw = iw // cols
        name = os.path.basename(path)
        rows_a = _alpha_rows(path)

        bands = None
        if rows_a:
            if rows_a[0][0] and rows_a[-1][-1]:
                print('[sheet] %s 배경이 투명하지 않은 것 같아요. 배경을 지워 주세요.' % name)
            bands = _bands([ON in r for r in rows_a])
            if bands:
                tallest = max(b - a for a, b in bands)
                bands = [(a, b) for a, b in bands if b - a >= tallest * 0.3]
            if len(bands) != rows:
                print('[sheet] %s: 줄을 %d개 찾았어요 (예상 %d개). 똑같이 나눠서 씁니다.'
                      % (name, len(bands), rows))
                bands = None
        if bands is None:
            ch = ih // rows
            bands = [(r * ch, (r + 1) * ch - 1) for r in range(rows)]

        self.frames = {}
        for r, (y0, y1) in enumerate(bands):
            for c in range(cols):
                x0 = c * cw
                if rows_a:
                    self.frames[(c, r)] = _measure(rows_a, x0, x0 + cw, y0, y1)
                else:
                    self.frames[(c, r)] = (x0, y0, cw, y1 - y0 + 1, cw / 2)
        self.row_h = {}
        for r in range(rows):
            hs = sorted(f[3] for (c, rr), f in self.frames.items() if rr == r and f)
            self.row_h[r] = hs[len(hs) // 2] if hs else (bands[r][1] - bands[r][0] + 1)
        self.ref_h = self.row_h[0]

    def draw(self, col, row, x, y, height, flip='', sx=1.0, sy=1.0, rad=0.0, alpha=1.0):
        """(x, y) = 발 위치, height = 화면에 보일 키(px)"""
        f = self.frames.get((col, row))
        if not f:
            return
        left, top, bw, bh, foot = f
        k = height / (self.row_h[row] if self.per_row else self.ref_h)
        w, h = bw * k * sx, bh * k * sy
        dx = (bw / 2 - foot) * k * sx
        if flip:
            dx = -dx
        bottom = self.image.h - (top + bh)
        if alpha < 0.999:
            self.image.opacify(alpha)
        self.image.clip_composite_draw(left, bottom, bw, bh, rad, flip, x + dx, y + h / 2, w, h)
        if alpha < 0.999:
            self.image.opacify(1.0)


_cache = {}


def load(name, cols, rows, per_row=False):
    """images/name 이 있으면 Sheet, 없으면 None (한 번만 불러옴)"""
    if name not in _cache:
        path = os.path.join(IMG_DIR, name)
        _cache[name] = Sheet(path, cols, rows, per_row) if os.path.exists(path) else None
    return _cache[name]
