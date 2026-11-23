# news-image-20261123 v2 — one-page newspaper of Monday 23 November 2026.
# Pure Python 3.13 standard library only: no Pillow, no network, no random,
# no clock. The image is drawn pixel by pixel and written as a PNG by a
# hand-rolled encoder (struct + zlib). Two runs write identical bytes.

import os
import struct
import zlib

W = 1024
H = 1024

# --- palette ---------------------------------------------------------------
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (178, 28, 28)
DARKRED = (122, 16, 16)
BLUE = (28, 68, 128)
GREEN = (34, 110, 60)
SKY = (178, 214, 235)
SEA = (64, 120, 170)
SAND = (226, 198, 138)
GREY = (110, 110, 104)
LIGHTGREY = (214, 210, 198)
ORANGE = (214, 110, 20)
YELLOW = (232, 190, 40)
WHITE = (255, 255, 255)

# --- 5x7 pixel font (7 rows, 5 bits each) -----------------------------------
# Written from scratch for this entry.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    '-': (0, 0, 0, 0x1F, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '•': (0, 0x04, 0x0E, 0x0E, 0x0E, 0x04, 0),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=False):
        if fill:
            for yy in range(-r, r + 1):
                half = int((r * r - yy * yy) ** 0.5)
                self.fill_rect(cx - half, cy + yy, half * 2 + 1, 1, c)
            return
        x = 0
        y = r
        d = 3 - 2 * r
        while y >= x:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                           (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, c)
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6

    def poly(self, pts, c):
        # Filled polygon, scanline fill.
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), 1, c)

    def text(self, x, y, s, scale=1, c=INK):
        cx = x
        for ch in s:
            g = FONT.get(ch.upper(), FONT[' '])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale=1, c=INK):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def wrap(self, x, y, max_w, s, scale=1, c=INK, leading=None):
        # Word-wrap; returns y after the last line.
        if leading is None:
            leading = 7 * scale + 3
        words = s.split(' ')
        lines = []
        cur = ''
        for wd in words:
            trial = wd if not cur else cur + ' ' + wd
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        yy = y
        for ln in lines:
            self.text(x, yy, ln, scale, c)
            yy += leading
        return yy


def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        return out + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


# --- drawn art -------------------------------------------------------------
def draw_globe(cv, cx, cy, r):
    # Sky disc, sea, land blobs, and a red crack: the climate talks break.
    cv.circle(cx, cy, r, SKY, fill=True)
    for rr in (r, r - 1, r - 2):
        cv.circle(cx, cy, rr, BLUE)
    # Continents, rough blobs.
    cv.poly([(cx - r + 14, cy - 30), (cx - r + 52, cy - 52), (cx - 20, cy - 44),
             (cx - 8, cy - 18), (cx - r + 26, cy - 6)], GREEN)
    cv.poly([(cx + 6, cy - 46), (cx + 44, cy - 58), (cx + r - 18, cy - 30),
             (cx + r - 34, cy - 2), (cx + 18, cy - 14)], GREEN)
    cv.poly([(cx - 30, cy + 18), (cx + 8, cy + 10), (cx + 26, cy + 34),
             (cx - 4, cy + 52), (cx - r + 22, cy + 40)], GREEN)
    cv.poly([(cx + 34, cy + 22), (cx + r - 26, cy + 16), (cx + r - 12, cy + 44),
             (cx + 44, cy + 58)], GREEN)
    # Meridians, clipped to the disc.
    for k in range(-2, 3):
        dx = k * r // 3
        half = int((r * r - dx * dx) ** 0.5)
        cv.line(cx + dx, cy - half + 6, cx + dx, cy + half - 6, (120, 170, 210), 1)
    cv.line(cx - r + 8, cy, cx + r - 8, cy, (120, 170, 210), 1)
    # The crack, jagged, dark red.
    crack = [(cx - 52, cy - r + 6), (cx - 30, cy - 58), (cx - 44, cy - 20),
             (cx - 12, cy + 4), (cx - 30, cy + 34), (cx + 2, cy + 58),
             (cx - 8, cy + r - 10)]
    for i in range(len(crack) - 1):
        cv.line(crack[i][0], crack[i][1], crack[i + 1][0], crack[i + 1][1], DARKRED, 4)
    # Red NO DEAL stamp.
    cv.fill_rect(cx - 78, cy - 8, 156, 34, RED)
    cv.rect(cx - 78, cy - 8, 156, 34, WHITE, 2)
    cv.text_center(cx, cy + 3, 'NO DEAL', 2, WHITE)


def draw_icon(cv, x, y, kind):
    # Small 44x40 pictograms for the story boxes.
    if kind == 'missile':
        cv.line(x + 8, y + 34, x + 34, y + 8, INK, 3)
        cv.poly([(x + 34, y + 8), (x + 40, y + 4), (x + 38, y + 14)], RED)
        cv.poly([(x + 8, y + 34), (x + 2, y + 40), (x + 12, y + 38)], ORANGE)
        cv.circle(x + 22, y + 12, 4, YELLOW, fill=True)
    elif kind == 'building':
        cv.fill_rect(x + 6, y + 6, 32, 30, GREY)
        for yy in (12, 20, 28):
            for xx in (11, 19, 27):
                cv.fill_rect(x + xx, y + yy, 5, 5, YELLOW)
        cv.poly([(x + 22, y + 6), (x + 38, y + 6), (x + 38, y + 22),
                 (x + 30, y + 14), (x + 26, y + 22)], PAPER)
        cv.poly([(x + 6, y + 36), (x + 16, y + 30), (x + 26, y + 36)], INK)
        cv.poly([(x + 22, y + 36), (x + 32, y + 30), (x + 40, y + 36)], INK)
    elif kind == 'factory':
        cv.fill_rect(x + 4, y + 20, 34, 16, GREY)
        cv.fill_rect(x + 8, y + 6, 6, 16, INK)
        cv.fill_rect(x + 18, y + 10, 6, 12, INK)
        cv.poly([(x + 20, y + 18), (x + 24, y + 4), (x + 28, y + 18)], ORANGE)
        cv.poly([(x + 26, y + 18), (x + 30, y + 8), (x + 34, y + 18)], RED)
        cv.fill_rect(x + 10, y + 26, 5, 5, YELLOW)
        cv.fill_rect(x + 22, y + 26, 5, 5, YELLOW)
    elif kind == 'exam':
        cv.fill_rect(x + 10, y + 4, 24, 32, WHITE)
        cv.rect(x + 10, y + 4, 24, 32, INK, 2)
        for yy in (12, 19, 26):
            cv.hline(x + 14, y + yy, 16, INK, 1)
        cv.line(x + 6, y + 8, x + 38, y + 34, RED, 4)
        cv.line(x + 38, y + 8, x + 6, y + 34, RED, 4)
    elif kind == 'flags':
        cv.line(x + 10, y + 6, x + 10, y + 38, INK, 2)
        cv.fill_rect(x + 10, y + 6, 16, 5, ORANGE)
        cv.fill_rect(x + 10, y + 11, 16, 5, WHITE)
        cv.fill_rect(x + 10, y + 16, 16, 5, GREEN)
        cv.line(x + 32, y + 6, x + 32, y + 38, INK, 2)
        cv.fill_rect(x + 32, y + 6, 16, 18, RED)
        cv.poly([(x + 32, y + 6), (x + 48, y + 15), (x + 32, y + 24)], BLUE)
        cv.line(x + 8, y + 38, x + 40, y + 38, INK, 2)
    elif kind == 'robot':
        cv.fill_rect(x + 12, y + 10, 20, 20, GREY)
        cv.rect(x + 12, y + 10, 20, 20, INK, 2)
        cv.line(x + 22, y + 10, x + 22, y + 4, INK, 2)
        cv.circle(x + 22, y + 4, 3, RED, fill=True)
        cv.fill_rect(x + 16, y + 17, 4, 4, RED)
        cv.fill_rect(x + 24, y + 17, 4, 4, RED)
        cv.hline(x + 16, y + 25, 12, INK, 2)


# --- page ------------------------------------------------------------------
def build():
    cv = Canvas(W, H, PAPER)
    cv.rect(6, 6, W - 12, H - 12, INK, 4)
    cv.rect(14, 14, W - 28, H - 28, INK, 1)

    # Masthead.
    cv.text_center(W // 2, 34, 'THE WORLD TODAY', 6, INK)
    cv.hline(30, 92, W - 60, INK, 3)
    cv.text_center(W // 2, 102, 'MONDAY 23 NOVEMBER 2026', 2, RED)
    cv.text(30, 104, 'ONE DAY, ONE PAGE', 1, INK)
    cv.text(W - 30 - text_width('ANTALYA - SEOUL - DELHI - GENEVA', 1), 104,
             'ANTALYA - SEOUL - DELHI - GENEVA', 1, INK)
    cv.hline(30, 126, W - 60, INK, 3)

    # Hero: COP31.
    cv.text(30, 142, 'CLIMATE - COP31, ANTALYA', 2, RED)
    cv.text(30, 168, 'COP31 ENDS WITH NO DEAL', 5, INK)
    cv.wrap(30, 218, 540,
            'EU REJECTS FINAL DRAFT AS TOO WEAK. LONGEST CLIMATE SUMMIT ON RECORD ENDS IN COLLAPSE.',
            2, INK)
    cv.wrap(30, 268, 540,
            'Two weeks of talks, two days overtime - and no deal. The EU and others rejected the final draft as too weak on fossil fuels and finance. President Murat Kurum: "We did all that we could." UN chief Guterres: "Deeply disappointed."',
            2, INK)
    draw_globe(cv, 800, 320, 118)
    cv.text_center(800, 452, 'THE ANTALYA PACT THAT NEVER WAS', 1, GREY)
    # Day-in-numbers box, filling the hero's lower left.
    cv.rect(30, 388, 540, 86, INK, 1)
    cv.text(40, 396, 'THE DAY IN NUMBERS', 1, RED)
    cv.text(40, 412, '2 WEEKS OF TALKS - 0 DEALS', 2, INK)
    cv.text(40, 432, '24 BODY BAGS IN CIKANDE', 2, INK)
    cv.text(40, 452, '11 MISSING IN DYMER', 2, INK)
    cv.hline(30, 482, W - 60, INK, 3)

    # Story grid: 3 columns x 2 rows.
    stories = [
        ('missile', 'BAHRAIN', 'BAHRAIN TO IRAN: PAY UP',
         'Manama demands full compensation and UN action after Iranian missiles hit a civilian plant. Two people hurt; Iran claims it hit US Patriot radars.'),
        ('building', 'UKRAINE', 'DRONE FLATTENS FLATS IN DYMER',
         'A Russian drone destroyed a five-storey block north of Kyiv. Two dead and 11 missing as rescuers keep digging through the rubble.'),
        ('factory', 'INDONESIA', '24 BODY BAGS AT CIKANDE',
         'The search resumes today at the burnt candy factory in Banten. 24 body bags are out; 29 workers are still missing. DNA tests will name the dead.'),
        ('exam', 'SOUTH KOREA', 'MINISTER QUITS OVER EXAM CHAOS',
         'Education chief Choi Kyo-jin resigns after last-minute anti-cheating rules sow confusion at the CSAT college entrance exam. Lee Jae Myung accepts.'),
        ('flags', 'INDIA - NEPAL', 'SHAH MEETS MODI IN DELHI',
         "Nepal's PM holds his first talks with Modi today. A reported $2bn aid ask, energy deals and a joint vision document are on the table."),
        ('robot', 'GENEVA', 'NO BAN ON KILLER ROBOTS',
         '128 states agree only to keep talking about autonomous weapons. A binding treaty is put off to 2028; campaigners call it a wasted chance.'),
    ]
    col_w = 312
    row_h = 168
    gx, gy = 30, 498
    for i, (icon, kicker, head, body) in enumerate(stories):
        col = i % 3
        row = i // 3
        x = gx + col * (col_w + 10)
        y = gy + row * (row_h + 8)
        cv.rect(x, y, col_w, row_h, INK, 1)
        cv.text(x + 10, y + 8, kicker, 1, RED)
        draw_icon(cv, x + col_w - 58, y + 6, icon)
        cv.wrap(x + 10, y + 26, col_w - 20 - 54, head, 2, INK)
        cv.hline(x + 10, y + 62, col_w - 20, LIGHTGREY, 1)
        cv.wrap(x + 10, y + 70, col_w - 20, body, 1, INK)

    # Also today strip.
    y = 852
    cv.hline(30, y, W - 60, INK, 3)
    cv.text(30, y + 10, 'ALSO TODAY', 2, RED)
    also = [
        ('HORMUZ', 'TANKERS HIT IN THE STRAIT. THREE TANKERS STRUCK; TWO MORE HIT MINES ON SUNDAY.'),
        ('LIBYA', 'RUSSIAN SHIP HIT IN BENGHAZI. SUSPECTED UKRAINIAN SEA DRONES; CORVETTE CAPSIZES, 10 HURT.'),
        ('MEXICO', "'EL CHAPO ISIDRO' SEIZED. FBI MOST-WANTED CARTEL BOSS CAUGHT IN A SINALOA RAID."),
        ('JAPAN', 'SHURI CASTLE REOPENS. MAIN HALL OPENS TO THE PUBLIC, SEVEN YEARS AFTER THE FIRE.'),
    ]
    ax = 30
    aw = 238
    for tag, txt in also:
        cv.text(ax, y + 36, tag, 1, RED)
        cv.wrap(ax, y + 50, aw, txt, 1, INK)
        ax += aw + 4
    cv.hline(30, 962, W - 60, INK, 3)

    # Footer.
    cv.text_center(W // 2, 974,
                   'SOURCES: REUTERS, AP, AL JAZEERA, BBC, YONHAP, ANTARA, MEA INDIA', 1, GREY)
    cv.text_center(W // 2, 988,
                   'ALL STORIES FIRST REPORTED ON 23 NOV 2026 IN AT LEAST ONE TIME ZONE', 1, GREY)
    return cv


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(out_dir, 'entry.png'))


if __name__ == '__main__':
    main()
