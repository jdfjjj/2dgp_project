import os
import ctypes

from pico2d import load_image

import game_settings
import resources

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
ALPHA_CUT = bytes(0 if a <= 40 else 1 for a in range(256))     # 거의 투명한 점은 무시
ON = b'\x01'
PIXEL_VER = 2                    # 도트 변환 방식이 바뀌면 숫자를 올려서 그림을 다시 만듦


def _set_smooth(on):
    try:
        from sdl2 import SDL_SetHint, SDL_HINT_RENDER_SCALE_QUALITY
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b'1' if on else b'0')
    except Exception:
        pass


def _surface_bytes(path):
    """PNG를 RGBA 바이트로 읽음 → (너비, 높이, 바이트)"""
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
        px = b''.join(data[y * pitch: y * pitch + w * 4] for y in range(h))
        return w, h, px
    except Exception as ex:
        print('그림 읽기 실패:', ex)
        return None


def _alpha_rows(path):
    """PNG의 투명도 값을 줄 단위로 읽음 (0: 투명, 1: 그림 있음)"""
    got = _surface_bytes(path)
    if not got:
        return None
    w, h, px = got
    return [px[y * w * 4 + 3: (y + 1) * w * 4: 4].translate(ALPHA_CUT) for y in range(h)]


def _pixelate(w, h, px, f):
    """f배 작게 줄인 도트 그림을 만듦.
    색은 칸 가운데 픽셀 색을 그대로 써서 또렷하게, 절반쯤 이상 찬 칸만 그려서 테두리를 깔끔하게"""
    nw, nh = max(1, int(w / f)), max(1, int(h / f))
    out = bytearray(nw * nh * 4)
    for ty in range(nh):
        y0 = int(ty * f)
        y1 = min(h, max(y0 + 1, int((ty + 1) * f)))
        cy = min(h - 1, int((ty + 0.5) * f))
        for tx in range(nw):
            x0 = int(tx * f)
            x1 = min(w, max(x0 + 1, int((tx + 1) * f)))
            cx = min(w - 1, int((tx + 0.5) * f))
            n = filled = 0
            first = -1
            for y in range(y0, y1):
                base = y * w * 4
                for x in range(x0, x1):
                    n += 1
                    if px[base + x * 4 + 3] > 40:
                        filled += 1
                        if first < 0:
                            first = base + x * 4
            if filled * 2 < n:
                continue
            i = (cy * w + cx) * 4
            if px[i + 3] <= 40:
                i = first
            o = (ty * nw + tx) * 4
            out[o], out[o + 1], out[o + 2], out[o + 3] = px[i], px[i + 1], px[i + 2], 255
    return nw, nh, out


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


def _analyze(rows_a, cols, rows, name):
    """줄과 칸을 찾아서, 칸마다 (왼쪽, 위, 너비, 높이, 발 x)와 줄마다 보통 키를 구함"""
    ih, iw = len(rows_a), len(rows_a[0])
    cw = iw // cols
    bands = _bands([ON in r for r in rows_a], max(2, ih // (rows * 25)))
    if bands:
        tallest = max(b - a for a, b in bands)
        bands = [(a, b) for a, b in bands if b - a >= tallest * 0.3]
    if len(bands) != rows:
        print('[sheet] %s: 줄을 %d개 찾았어요 (예상 %d개). 똑같이 나눠서 씁니다.'
              % (name, len(bands), rows))
        ch = ih // rows
        bands = [(r * ch, (r + 1) * ch - 1) for r in range(rows)]
    frames = {}
    for r, (y0, y1) in enumerate(bands):
        for c in range(cols):
            frames[(c, r)] = _measure(rows_a, c * cw, (c + 1) * cw, y0, y1)
    row_h = {}
    for r in range(rows):
        hs = sorted(f[3] for (c, rr), f in frames.items() if rr == r and f)
        row_h[r] = hs[len(hs) // 2] if hs else (bands[r][1] - bands[r][0] + 1)
    return frames, row_h


def _pixel_version(src, cols, rows, pixel):
    """원본을 줄여서 '첫 줄 키 = pixel' 인 도트 그림을 만들어 escape_assets에 저장 (처음 한 번만)"""
    stem = os.path.splitext(os.path.basename(src))[0]
    dst = os.path.join(game_settings.GEN_DIR, '%s_px%d_v%d.png' % (stem, pixel, PIXEL_VER))
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    got = _surface_bytes(src)
    if not got:
        return src
    w, h, px = got
    rows_a = [px[y * w * 4 + 3: (y + 1) * w * 4: 4].translate(ALPHA_CUT) for y in range(h)]
    _, row_h = _analyze(rows_a, cols, rows, os.path.basename(src))
    f = row_h[0] / float(pixel)
    if f <= 1:
        return src
    print('도트 그림 만드는 중... %s (처음 한 번만)' % os.path.basename(src))
    nw, nh, out = _pixelate(w, h, px, f)
    os.makedirs(game_settings.GEN_DIR, exist_ok=True)
    resources.write_png(dst, nw, nh, lambda x, y: out[(y * nw + x) * 4:(y * nw + x) * 4 + 4])
    return dst


class Sheet:
    def __init__(self, path, cols, rows, per_row=False, pixel=None):
        name = os.path.basename(path)
        if pixel:
            path = _pixel_version(path, cols, rows, pixel)
        self.pixel = bool(pixel)
        _set_smooth(not self.pixel)               # 도트는 부드럽게 늘리지 않고 계단식으로 키움
        self.image = load_image(path)
        _set_smooth(False)
        self.per_row = per_row                    # True면 줄마다 따로 키를 맞춤 (적처럼 줄마다 다른 그림)
        rows_a = _alpha_rows(path)
        if rows_a:
            if rows_a[0][0] and rows_a[-1][-1]:
                print('[sheet] %s 배경이 투명하지 않은 것 같아요. 배경을 지워 주세요.' % name)
            self.frames, self.row_h = _analyze(rows_a, cols, rows, name)
        else:
            cw, ch = self.image.w // cols, self.image.h // rows
            self.frames = {(c, r): (c * cw, r * ch, cw, ch, cw / 2) for r in range(rows) for c in range(cols)}
            self.row_h = {r: ch for r in range(rows)}
        self.ref_h = self.row_h[0]

    def draw(self, col, row, x, y, height, flip='', sx=1.0, sy=1.0, rad=0.0, alpha=1.0):
        """(x, y) = 발 위치, height = 화면에 보일 키(px). 도트 그림은 가장 가까운 정수 배로 그림"""
        f = self.frames.get((col, row))
        if not f:
            return
        left, top, bw, bh, foot = f
        k = height / (self.row_h[row] if self.per_row else self.ref_h)
        if self.pixel:
            k = max(1, round(k))
        w, h = bw * k * sx, bh * k * sy
        dx = (bw / 2 - foot) * k * sx
        if flip:
            dx = -dx
        bottom = self.image.h - (top + bh)
        if alpha < 0.999:
            self.image.opacify(alpha)
        self.image.clip_composite_draw(left, bottom, bw, bh, rad, flip,
                                       round(x + dx), round(y + h / 2), w, h)
        if alpha < 0.999:
            self.image.opacify(1.0)


_cache = {}


def load(name, cols, rows, per_row=False, pixel=None):
    """images/name 이 있으면 Sheet, 없으면 None (한 번만 불러옴). pixel을 주면 도트 버전으로"""
    key = (name, pixel)
    if key not in _cache:
        path = os.path.join(IMG_DIR, name)
        _cache[key] = Sheet(path, cols, rows, per_row, pixel) if os.path.exists(path) else None
    return _cache[key]
