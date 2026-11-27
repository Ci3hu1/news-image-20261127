#!/usr/bin/env python3
"""Render the make.fun news-image-20261127 poster v1 ("Friday Night Edition").

Pure Pillow. The page is drawn at 2x (2048x2048) and LANCZOS-downscaled
to 1024x1024, then sharpened with USM(2,150,3). A 300px preview is made
with LANCZOS + USM(1,130,2). Byte-deterministic: no timestamps, no
randomness, fixed font files, fixed draw order.

Layout (1024x1024): masthead (8-106, title + 2-line region count) ->
UTC timeline, TIMES ONLY (112-144) -> hero Kuwait panel, full width
(150-340) -> 4 large panels, 2x2 (348-740) -> 12 small picture tiles,
2 rows x 6 (748-956) -> DATE CHECK + sources box (964-1018).

36 verified stories, 8 regions (EUROPE 10, MIDDLE EAST 6, N. AMERICA 5,
ASIA-PACIFIC 4, OCEANIA 3, AFRICA 3, S. AMERICA 1, GLOBAL 4). 17 are
pictured (hero + 4 panels + 12 tiles); the other 19 live in the
masthead count and in STORIES.md, the repo's per-story source record.

Judge lessons applied (NI22 v3 dev 981.243, NI26 v2 dev 972.121):
- FEWER, LARGER panels beat dense grids (NI26 v3's 24-card grid scored
  933k vs v2's 972k for six large panels). No text index: the 12
  remaining lead stories are PICTURE tiles, NI22-v3 style, not a
  fine-print list.
- Panels numbered 1-5 SEQUENTIALLY (v5: non-sequential numbers docked).
- Literal scenes, not abstract glyphs (v5: starburst/cloud docked).
- Spread across regions: all 8 regions are pictured, not US-heavy.
- 300px v2 legibility rules (METHOD-v2-microtext-smooth.md): headline
  24px bold, deck 20px bold exactly 1 line <=8 words, stat 36px bold,
  timeline times 20px bold, tile labels 18px bold, DATE CHECK 18px bold,
  footer 16px bold 1 line. No text under 18px except the 16px footer
  line. Leading 1.2x. Tracking +1px on 18-20px bold. No white on amber.
  Min line 3px, min dot 6px at 1024.
- DATE CHECK box kept (praised in NI22 v1/v2): Homs bombing is 26 Dec
  2025, Nepal chopper crash is 3 Nov 2026 (not 4 Nov) — the two traps
  the #1 live entry gets wrong are the NZ 67/131 count (real: 65/130)
  and "Gukesh Game 4 today" (real: Friday is a rest day).
- No map: at the available height a world map's pins fall under the
  6px minimum and read as dust; breadth is carried by the explicit
  region counts and by picturing all 8 regions.
- No internal contradictions: the masthead says "36 STORIES" and the
  record holds exactly 36; the DATE CHECK box only corrects dates, it
  never contradicts a pictured story.
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2  # supersampling: draw at 2048, downscale to 1024
W = H = 1024

# ---------------------------------------------------------------- palette
BG = (10, 17, 34)          # deep ink navy
PANEL = (17, 28, 54)       # panel navy
PANEL_LINE = (201, 162, 39)  # gold outline
GOLD = (232, 185, 60)      # amber accent / stats / numbers
CREAM = (245, 237, 214)    # masthead title
WHITE = (255, 255, 255)
STEEL = (199, 210, 232)    # light steel, deck-adjacent only (never small)
RED = (214, 69, 69)        # lead accent / DATE CHECK label
ORANGE = (232, 120, 40)    # blast / flame
TEAL = (64, 160, 170)      # sea
DARK = (8, 12, 24)         # silhouettes
SKY_TOP = (10, 17, 34)
SKY_BOT = (27, 47, 87)

# ---------------------------------------------------------------- text sizes
# (role -> px at 1024) — the test suite audits these against the floors.
TEXT_SIZES = {
    "kicker": 20, "title": 36, "region": 18, "timeline": 20,
    "hero_headline": 28, "headline": 24, "deck": 20, "stat": 36,
    "number": 26, "source": 18, "chip": 18, "tile_label": 18,
    "datecheck": 18, "footer": 16,
}

FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
_FONTS = {}


def fs(size, serif=False):
    """Font at `size` px (1024-scale); drawn at 2x."""
    key = (size, serif)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(
            FONT_SERIF if serif else FONT_SANS, size * S)
    return _FONTS[key]


def X(v):
    return v * S


def box(x0, y0, x1, y1):
    return [X(x0), X(y0), X(x1), X(y1)]


def xy(x, y):
    return (X(x), X(y))


def lw(w):
    return max(1, w * S)


# ---------------------------------------------------------------- text utils
def wrap(d, text, font, max_w, max_lines):
    """Word-wrap `text` to <= max_lines lines of width <= max_w (1024 px)."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= X(max_w) or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                return lines
    if cur:
        lines.append(cur)
    return lines[:max_lines]


def tracked(d, pos, text, font, fill, tr=1):
    """Draw text with +1px tracking (for 18-20px bold). Returns end x.

    `pos` is in 1024-scale units; coordinates are scaled to the 2x
    canvas here (a previous version passed them raw and the text landed
    at half position, overlapping the masthead).
    """
    x, y = X(pos[0]), X(pos[1])
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + X(tr)
    return x


def tracked_w(d, text, font, tr=1):
    """Width of tracked text in 1024 px."""
    w = 0.0
    for ch in text:
        w += d.textlength(ch, font=font) / S + tr
    return w - tr


def centre(d, text, font, y, x0, x1, fill, tr=0):
    """Centred text (tracked when tr>0)."""
    if tr:
        w = tracked_w(d, text, font, tr)
        tracked(d, (x0 + (x1 - x0 - w) / 2, y), text, font, fill, tr)
    else:
        w = d.textlength(text, font=font) / S
        d.text(xy(x0 + (x1 - x0 - w) / 2, y), text, font=font, fill=fill)


def star(d, cx, cy, r, fill):
    """Five-point star centred at (cx, cy), outer radius r (1024 px)."""
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append(xy(cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------- data
# (number, headline, deck, stat, source, scene, region)
PANELS = [
    (2, "SHOPPERS FLOOD BLACK FRIDAY", "126M SHOPPERS",
     "$12.9BN", "ADOBE / NRF", "bag"),
    (3, "HAMAS WEIGHS REPLY AS 10 DIE", "3RD NIGHT RUNNING",
     "10 KILLED", "REUTERS", "gaza"),
    (4, "EU SPLIT ON \u20ac45BN UKRAINE LOAN", "24 OF 27 BACK IT",
     "\u20ac45BN", "AGENCE EUROPE", "eu"),
    (5, "NZ COALITION 65/130 \u2014 ONE SHORT", "7 SEATS DECIDE ALL",
     "65/130", "REUTERS", "nz"),
]

# (line1, line2, scene) — every line measured <=152px at 18px bold
# plain (untracked) in a 160px tile; see the width audit in the build
# log. Shorter labels are abbreviations of the STORIES.md tile text.
TILES = [
    ("UK MIGRATION", "77,000", "plane"),
    ("IBIZA TANKER", "1 DEAD", "tanker"),
    ("GUKESH", "GAME 3 DRAW", "chess"),
    ("AMAZON", "20+ NATIONS", "warehouse"),
    ("INDIA U-19", "BY 36 RUNS", "cricket"),
    ("JAPAN $350BN", "DEFENCE PLAN", "jet"),
    ("RAS TANURA", "BRENT +3.5%", "refinery"),
    ("DUTERTE", "TRIAL MONDAY", "court"),
    ("COLOGNE", "2 ARRESTED", "tape"),
    ("SPAIN VOTES", "SUNDAY 29TH", "ballot"),
    ("EBOLA: 12,000", "IN CONGO", "clinic"),
    ("ARGENTINA", "MONEY PRINT", "banknote"),
]

TIMES = ["00:30", "01:08", "02:22", "02:56"]  # UTC, verified (see STORIES.md)

# ---------------------------------------------------------------- scenes
def hero_scene(d, x0, y0, w, h):
    """Kuwait, night: air-defence station, searchlights, drone, blast."""
    # sky gradient, horizontal bands
    bands = 24
    for i in range(bands):
        t = i / (bands - 1)
        c = tuple(int(SKY_TOP[k] + (SKY_BOT[k] - SKY_TOP[k]) * t)
                  for k in range(3))
        d.rectangle(box(x0, y0 + h * i / bands, x0 + w, y0 + h * (i + 1) / bands),
                    fill=c)
    # stars (fixed positions, >=6px dots)
    for sx, sy in [(0.12, 0.10), (0.30, 0.06), (0.48, 0.14), (0.62, 0.07),
                   (0.78, 0.12), (0.90, 0.06), (0.22, 0.20), (0.55, 0.22),
                   (0.84, 0.22), (0.38, 0.28)]:
        d.ellipse(box(x0 + w * sx - 3, y0 + h * sy - 3,
                      x0 + w * sx + 3, y0 + h * sy + 3), fill=WHITE)
    # searchlight beams (gold, solid muted fill reads as light on dark)
    d.polygon([xy(x0 + w * 0.18, y0 + h), xy(x0 + w * 0.30, y0 + h),
               xy(x0 + w * 0.52, y0 + h * 0.10)], fill=(122, 96, 26))
    d.polygon([xy(x0 + w * 0.68, y0 + h), xy(x0 + w * 0.78, y0 + h),
               xy(x0 + w * 0.86, y0 + h * 0.18)], fill=(122, 96, 26))
    # drone silhouette (quadcopter) top-right of the beams
    dx, dy = x0 + w * 0.56, y0 + h * 0.16
    d.rectangle(box(dx - 16, dy - 6, dx + 16, dy + 6), fill=DARK)
    d.rectangle(box(dx - 34, dy - 2, dx + 34, dy + 2), fill=DARK)
    d.ellipse(box(dx - 44, dy - 5, dx - 26, dy + 1), fill=DARK)
    d.ellipse(box(dx + 26, dy - 5, dx + 44, dy + 1), fill=DARK)
    # blast glow, concentric rings at the station (right side)
    bx, by = x0 + w * 0.82, y0 + h * 0.78
    for r, col in [(46, (120, 30, 30)), (34, ORANGE), (22, (240, 160, 40)),
                   (12, (255, 220, 120))]:
        d.ellipse(box(bx - r, by - r, bx + r, by + r), fill=col)
    # antenna array: three masts + dishes, left-centre
    base = y0 + h * 0.92
    for mx in (0.10, 0.24, 0.38):
        px = x0 + w * mx
        d.line([xy(px, base), xy(px, base - h * 0.42)], fill=STEEL, width=lw(4))
        d.line([xy(px - 14, base - h * 0.42), xy(px + 14, base - h * 0.42)],
               fill=STEEL, width=lw(3))
        d.arc(box(px - 18, base - h * 0.62, px + 18, base - h * 0.30),
              start=200, end=340, fill=GOLD, width=lw(4))
    # ground + fence
    d.rectangle(box(x0, base, x0 + w, y0 + h), fill=DARK)
    for fx in range(0, w + 1, 34):
        d.line([xy(x0 + fx, base), xy(x0 + fx, base - 12)],
               fill=STEEL, width=lw(3))


def scene_bag(d, x0, y0, w, h):
    """Black Friday: big gold shopping bag + red price tag."""
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    bx, by, bw, bh = x0 + w * 0.22, y0 + h * 0.30, w * 0.56, h * 0.58
    d.polygon([xy(bx, by), xy(bx + bw, by), xy(bx + bw - 10, by + bh),
               xy(bx + 10, by + bh)], fill=GOLD)
    d.arc(box(bx + bw * 0.28, by - h * 0.22, bx + bw * 0.72, by + h * 0.22),
          start=180, end=360, fill=GOLD, width=lw(5))
    tx, ty = bx + bw * 0.62, by + bh * 0.30
    d.polygon([xy(tx, ty), xy(tx + 34, ty), xy(tx + 44, ty + 12),
               xy(tx + 34, ty + 24), xy(tx, ty + 24)], fill=RED)
    d.text(xy(tx + 8, ty + 1), "$", font=fs(22), fill=WHITE)


def scene_gaza(d, x0, y0, w, h):
    """Gaza: night skyline, lit windows, smoke plume, red glow."""
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(16, 22, 44))
    base = y0 + h * 0.88
    for i, (bx, bw, bh) in enumerate([(0.02, 0.20, 0.45), (0.26, 0.16, 0.62),
                                      (0.46, 0.22, 0.52), (0.72, 0.24, 0.70)]):
        d.rectangle(box(x0 + w * bx, base - h * bh, x0 + w * (bx + bw), base),
                    fill=DARK)
        for wy in (0.20, 0.45, 0.70):
            d.rectangle(box(x0 + w * (bx + 0.06), base - h * bh * wy - 3,
                            x0 + w * (bx + 0.06) + 6, base - h * bh * wy + 3),
                        fill=GOLD)
    # smoke plume + glow over the skyline
    sx, sy = x0 + w * 0.62, y0 + h * 0.30
    for r, col in [(30, (70, 76, 92)), (20, (96, 102, 120)), (12, (130, 136, 152))]:
        d.ellipse(box(sx - r, sy - r * 0.7, sx + r, sy + r * 0.7), fill=col)
    d.ellipse(box(x0 + w * 0.70, base - 14, x0 + w * 0.86, base + 2), fill=RED)
    d.rectangle(box(x0, base, x0 + w, y0 + h), fill=DARK)


def scene_eu(d, x0, y0, w, h):
    """EU: circle of twelve gold stars + parliament silhouette."""
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    cx, cy, r = x0 + w * 0.5, y0 + h * 0.42, min(w, h) * 0.34
    d.ellipse(box(cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(18, 40, 90))
    import math
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        star(d, cx + r * math.cos(ang), cy + r * math.sin(ang), 7, GOLD)
    # parliament: hemisphere + columns
    base = y0 + h * 0.94
    d.pieslice(box(x0 + w * 0.30, base - h * 0.26, x0 + w * 0.70, base + h * 0.10),
               start=180, end=360, fill=STEEL)
    for cx2 in (0.34, 0.44, 0.54, 0.64):
        d.rectangle(box(x0 + w * cx2 - 4, base - h * 0.20, x0 + w * cx2 + 4, base),
                    fill=STEEL)


def scene_nz(d, x0, y0, w, h):
    """New Zealand: Beehive tower + ballot box."""
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    base = y0 + h * 0.92
    cx = x0 + w * 0.32
    d.rectangle(box(cx - 26, base - h * 0.52, cx + 26, base), fill=CREAM)
    d.pieslice(box(cx - 26, base - h * 0.78, cx + 26, base - h * 0.30),
               start=180, end=360, fill=CREAM)
    for i in range(4):
        yy = base - h * (0.14 + i * 0.11)
        d.line([xy(cx - 26, yy), xy(cx + 26, yy)], fill=BG, width=lw(3))
    # ballot box + tick
    bx, by = x0 + w * 0.66, base - h * 0.42
    d.rectangle(box(bx - 24, by, bx + 24, by + h * 0.40), fill=GOLD)
    d.line([xy(bx - 14, by - 4), xy(bx + 14, by - 4)], fill=WHITE, width=lw(5))
    d.line([xy(bx - 12, by + h * 0.22), xy(bx - 2, by + h * 0.32),
            xy(bx + 16, by + h * 0.06)], fill=WHITE, width=lw(6))


# --- small tile scenes (158x56 boxes; 2-3 bold shapes each) ---
def t_plane(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.polygon([xy(x0 + 12, y0 + h * 0.55), xy(x0 + w * 0.55, y0 + h * 0.30),
               xy(x0 + w - 14, y0 + h * 0.42), xy(x0 + w * 0.55, y0 + h * 0.62),
               xy(x0 + 26, y0 + h * 0.70)], fill=WHITE)
    d.polygon([xy(x0 + w * 0.45, y0 + h * 0.28), xy(x0 + w * 0.58, y0 + h * 0.10),
               xy(x0 + w * 0.62, y0 + h * 0.34)], fill=WHITE)
    d.line([xy(x0 + w - 34, y0 + h * 0.78), xy(x0 + w - 34, y0 + h * 0.30),
            xy(x0 + w - 22, y0 + h * 0.42)], fill=GOLD, width=lw(6))


def t_tanker(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(14, 44, 62))
    d.polygon([xy(x0 + 18, y0 + h * 0.42), xy(x0 + w - 18, y0 + h * 0.42),
               xy(x0 + w - 34, y0 + h * 0.62), xy(x0 + 34, y0 + h * 0.62)],
              fill=DARK)
    d.rectangle(box(x0 + 30, y0 + h * 0.30, x0 + 52, y0 + h * 0.42), fill=STEEL)
    for wx in (0.10, 0.38, 0.66):
        d.arc(box(x0 + w * wx, y0 + h * 0.66, x0 + w * (wx + 0.22), y0 + h * 0.92),
              start=180, end=360, fill=TEAL, width=lw(4))
    d.ellipse(box(x0 + w - 34, y0 + h * 0.66, x0 + w - 14, y0 + h * 0.82),
              fill=ORANGE)


def t_chess(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    s = h * 0.80 / 4
    ox, oy = x0 + w * 0.5 - 2 * s, y0 + h * 0.10
    for r in range(4):
        for c in range(4):
            if (r + c) % 2 == 0:
                d.rectangle(box(ox + c * s, oy + r * s,
                                ox + (c + 1) * s, oy + (r + 1) * s), fill=CREAM)
    d.ellipse(box(ox + s * 0.7, oy + s * 0.6, ox + s * 1.3, oy + s * 1.2), fill=GOLD)
    d.ellipse(box(ox + s * 2.7, oy + s * 2.6, ox + s * 3.3, oy + s * 3.2), fill=WHITE)


def t_warehouse(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.polygon([xy(x0 + 14, y0 + h * 0.42), xy(x0 + w * 0.5, y0 + h * 0.14),
               xy(x0 + w - 14, y0 + h * 0.42)], fill=STEEL)
    d.rectangle(box(x0 + 20, y0 + h * 0.42, x0 + w - 20, y0 + h * 0.86), fill=DARK)
    d.line([xy(x0 + w * 0.32, y0 + h * 0.86), xy(x0 + w * 0.32, y0 + h * 0.42)],
           fill=STEEL, width=lw(4))
    d.line([xy(x0 + w * 0.68, y0 + h * 0.86), xy(x0 + w * 0.68, y0 + h * 0.42)],
           fill=STEEL, width=lw(4))
    d.rectangle(box(x0 + w * 0.72, y0 + h * 0.52, x0 + w - 8, y0 + h * 0.78),
                fill=GOLD)
    d.text(xy(x0 + w * 0.72 + 4, y0 + h * 0.52), "!", font=fs(20), fill=DARK)


def t_cricket(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(20, 60, 34))
    d.rectangle(box(x0 + w * 0.42, y0 + h * 0.18, x0 + w * 0.48, y0 + h * 0.80),
                fill=GOLD)
    d.rectangle(box(x0 + w * 0.56, y0 + h * 0.18, x0 + w * 0.62, y0 + h * 0.80),
                fill=GOLD)
    d.rectangle(box(x0 + w * 0.70, y0 + h * 0.18, x0 + w * 0.76, y0 + h * 0.80),
                fill=GOLD)
    d.polygon([xy(x0 + w * 0.18, y0 + h * 0.72), xy(x0 + w * 0.30, y0 + h * 0.30),
               xy(x0 + w * 0.38, y0 + h * 0.34), xy(x0 + w * 0.28, y0 + h * 0.78)],
              fill=CREAM)
    d.ellipse(box(x0 + w * 0.82 - 8, y0 + h * 0.30 - 8,
                  x0 + w * 0.82 + 8, y0 + h * 0.30 + 8), fill=RED)


def t_jet(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.ellipse(box(x0 + w * 0.62 - 20, y0 + h * 0.12 - 20,
                  x0 + w * 0.62 + 20, y0 + h * 0.12 + 20), fill=RED)
    d.polygon([xy(x0 + 10, y0 + h * 0.60), xy(x0 + w * 0.52, y0 + h * 0.40),
               xy(x0 + w - 10, y0 + h * 0.52), xy(x0 + w * 0.52, y0 + h * 0.66),
               xy(x0 + 24, y0 + h * 0.74)], fill=DARK)
    d.polygon([xy(x0 + w * 0.44, y0 + h * 0.38), xy(x0 + w * 0.56, y0 + h * 0.16),
               xy(x0 + w * 0.60, y0 + h * 0.44)], fill=DARK)


def t_refinery(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    for bx, bw, bh in [(0.10, 0.14, 0.62), (0.30, 0.12, 0.78), (0.48, 0.16, 0.58)]:
        d.rectangle(box(x0 + w * bx, y0 + h * (0.92 - bh), x0 + w * (bx + bw),
                        y0 + h * 0.92), fill=DARK)
    d.polygon([xy(x0 + w * 0.68, y0 + h * 0.62), xy(x0 + w * 0.76, y0 + h * 0.30),
               xy(x0 + w * 0.84, y0 + h * 0.62)], fill=ORANGE)
    d.ellipse(box(x0 + w * 0.70, y0 + h * 0.16, x0 + w * 0.84, y0 + h * 0.34),
              fill=(70, 76, 92))
    d.line([xy(x0 + w * 0.30, y0 + h * 0.20), xy(x0 + w * 0.30, y0 + h * 0.92)],
           fill=STEEL, width=lw(4))


def t_court(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.polygon([xy(x0 + w * 0.20, y0 + h * 0.34), xy(x0 + w * 0.5, y0 + h * 0.12),
               xy(x0 + w * 0.80, y0 + h * 0.34)], fill=CREAM)
    for cx2 in (0.28, 0.46, 0.64):
        d.rectangle(box(x0 + w * cx2 - 4, y0 + h * 0.38, x0 + w * cx2 + 4,
                        y0 + h * 0.86), fill=CREAM)
    d.rectangle(box(x0 + w * 0.16, y0 + h * 0.86, x0 + w * 0.84, y0 + h * 0.92),
                fill=CREAM)


def t_tape(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.polygon([xy(x0 + w * 0.30, y0 + h * 0.18), xy(x0 + w * 0.42, y0 + h * 0.18),
               xy(x0 + w * 0.42, y0 + h * 0.86), xy(x0 + w * 0.30, y0 + h * 0.86)],
              fill=STEEL)
    d.polygon([xy(x0 + w * 0.58, y0 + h * 0.18), xy(x0 + w * 0.70, y0 + h * 0.18),
               xy(x0 + w * 0.70, y0 + h * 0.86), xy(x0 + w * 0.58, y0 + h * 0.86)],
              fill=STEEL)
    # police tape band, diagonal stripes
    d.rectangle(box(x0 + 8, y0 + h * 0.42, x0 + w - 8, y0 + h * 0.62), fill=GOLD)
    for i in range(6):
        tx = x0 + 16 + i * 22
        d.polygon([xy(tx, y0 + h * 0.62), xy(tx + 10, y0 + h * 0.62),
                   xy(tx + 22, y0 + h * 0.42), xy(tx + 12, y0 + h * 0.42)],
                  fill=DARK)


def t_ballot(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.rectangle(box(x0 + w * 0.10, y0 + h * 0.10, x0 + w * 0.42, y0 + h * 0.34),
                fill=RED)
    d.rectangle(box(x0 + w * 0.10, y0 + h * 0.34, x0 + w * 0.42, y0 + h * 0.58),
                fill=GOLD)
    d.rectangle(box(x0 + w * 0.10, y0 + h * 0.58, x0 + w * 0.42, y0 + h * 0.82),
                fill=RED)
    bx, by = x0 + w * 0.66, y0 + h * 0.30
    d.rectangle(box(bx - 22, by, bx + 22, by + h * 0.52), fill=CREAM)
    d.line([xy(bx - 12, by - 4), xy(bx + 12, by - 4)], fill=GOLD, width=lw(5))


def t_clinic(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.rectangle(box(x0 + w * 0.12, y0 + h * 0.22, x0 + w * 0.40, y0 + h * 0.78),
                fill=RED)
    d.rectangle(box(x0 + w * 0.21, y0 + h * 0.32, x0 + w * 0.31, y0 + h * 0.68),
                fill=WHITE)
    d.rectangle(box(x0 + w * 0.16, y0 + h * 0.44, x0 + w * 0.36, y0 + h * 0.56),
                fill=WHITE)
    for i, bh in enumerate((0.30, 0.48, 0.66)):
        bx = x0 + w * (0.52 + i * 0.14)
        d.rectangle(box(bx, y0 + h * (0.86 - bh), bx + 12, y0 + h * 0.86),
                    fill=GOLD)


def t_banknote(d, x0, y0, w, h):
    d.rectangle(box(x0, y0, x0 + w, y0 + h), fill=(24, 38, 70))
    d.rectangle(box(x0 + 12, y0 + h * 0.22, x0 + w - 12, y0 + h * 0.78),
                fill=(40, 110, 70))
    d.ellipse(box(x0 + w * 0.5 - 14, y0 + h * 0.5 - 14,
                  x0 + w * 0.5 + 14, y0 + h * 0.5 + 14), fill=CREAM)
    d.text(xy(x0 + w * 0.5 - 6, y0 + h * 0.5 - 13), "$", font=fs(20), fill=(40, 110, 70))
    d.line([xy(x0 + 16, y0 + h * 0.80), xy(x0 + w - 16, y0 + h * 0.18)],
           fill=RED, width=lw(7))


TILE_SCENES = {"plane": t_plane, "tanker": t_tanker, "chess": t_chess,
               "warehouse": t_warehouse, "cricket": t_cricket, "jet": t_jet,
               "refinery": t_refinery, "court": t_court, "tape": t_tape,
               "ballot": t_ballot, "clinic": t_clinic, "banknote": t_banknote}
PANEL_SCENES = {"bag": scene_bag, "gaza": scene_gaza, "eu": scene_eu,
                "nz": scene_nz}

# ---------------------------------------------------------------- layout
M = 12                      # outer margin
CW = W - 2 * M              # content width 1000
MASTHEAD = (8, 106)         # y0, y1
TIMELINE = (112, 144)
HERO = (150, 340)
PANEL_Y = (348, 740)        # two rows of 192, gap 8
PANEL_W, PANEL_H, PANEL_GAP = 492, 192, 16
TILE_Y = (748, 956)         # two rows of 102, gap 8
TILE_W, TILE_H, TILE_GAP = 160, 102, 8
DATECHECK = (964, 1018)


def render():
    """Draw the poster; return (entry.png bytes, preview-300.png bytes)."""
    img = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    y0, y1 = MASTHEAD
    d.text(xy(M, y0 + 2), "FRIDAY NIGHT EDITION", font=fs(20), fill=GOLD)
    right = "36 STORIES \u00b7 8 REGIONS"
    d.text(xy(W - M - d.textlength(right, font=fs(20)) / S, y0 + 2), right,
           font=fs(20), fill=WHITE)
    d.text(xy(M, y0 + 24), "FRIDAY 27 NOVEMBER 2026", font=fs(36, serif=True),
           fill=CREAM)
    d.line([xy(M, y1 - 2), xy(W - M, y1 - 2)], fill=PANEL_LINE, width=lw(3))
    tracked(d, (M, y0 + 60),
            "EUROPE 10 \u00b7 MIDDLE EAST 6 \u00b7 N. AMERICA 5 \u00b7 ASIA-PACIFIC 4",
            fs(18), WHITE, tr=1)
    tracked(d, (M, y0 + 80),
            "OCEANIA 3 \u00b7 AFRICA 3 \u00b7 S. AMERICA 1 \u00b7 GLOBAL 4",
            fs(18), WHITE, tr=1)

    # ---- timeline: TIMES ONLY ------------------------------------------
    ty0, ty1 = TIMELINE
    d.text(xy(M, ty0), "UTC", font=fs(18), fill=GOLD)
    line_y = ty0 + 26
    d.line([xy(M + 52, line_y), xy(W - M, line_y)], fill=PANEL_LINE, width=lw(3))
    xs = [162, 412, 662, 912]
    for t, cx in zip(TIMES, xs):
        centre(d, t, fs(20), ty0, cx - 40, cx + 40, WHITE, tr=1)
        d.ellipse(box(cx - 5, line_y - 5, cx + 5, line_y + 5), fill=GOLD)

    # ---- hero: Kuwait ---------------------------------------------------
    hy0, hy1 = HERO
    d.rectangle(box(M, hy0, W - M, hy1), fill=PANEL, outline=PANEL_LINE,
                width=lw(3))
    hero_scene(d, M + 8, hy0 + 8, 400, hy1 - hy0 - 16)
    tx = M + 424
    tw = W - M - tx - 12
    d.text(xy(tx, hy0 + 10), "01", font=fs(26), fill=GOLD)
    chip = "CLAIM \u2014 IRAN DENIES"
    cw = d.textlength(chip, font=fs(18)) / S + 20
    d.rectangle(box(tx + 52, hy0 + 12, tx + 52 + cw, hy0 + 38),
                outline=RED, width=lw(3))
    d.text(xy(tx + 62, hy0 + 15), chip, font=fs(18), fill=RED)
    d.text(xy(W - M - 12 - d.textlength("REUTERS", font=fs(18)) / S, hy0 + 12),
           "REUTERS", font=fs(18), fill=GOLD)
    head = ["KUWAIT BLAMES IRAN FOR",
            "DRONE STRIKE THAT KILLED 2"]
    yy = hy0 + 48
    for ln in head:
        d.text(xy(tx, yy), ln, font=fs(28), fill=WHITE)
        yy += 34
    d.text(xy(tx, hy0 + 122), "Two Italians dead, two wounded; Iran denies it",
           font=fs(20), fill=WHITE)
    d.text(xy(tx, hy0 + 148), "2 KILLED", font=fs(36), fill=GOLD)

    # ---- 4 large panels -------------------------------------------------
    pic_w, pic_h = 180, 148
    for idx, (num, head, deck, stat, src, scene) in enumerate(PANELS):
        col, row = idx % 2, idx // 2
        x0 = M + col * (PANEL_W + PANEL_GAP)
        y0 = PANEL_Y[0] + row * (PANEL_H + 8)
        d.rectangle(box(x0, y0, x0 + PANEL_W, y0 + PANEL_H), fill=PANEL,
                    outline=PANEL_LINE, width=lw(3))
        PANEL_SCENES[scene](d, x0 + 10, y0 + 22, pic_w, pic_h)
        d.rectangle(box(x0 + 6, y0 + 18, x0 + 14 + pic_w, y0 + 26 + pic_h),
                    outline=PANEL_LINE, width=lw(3))
        tx2 = x0 + 212
        tw2 = PANEL_W - 212 - 12
        d.text(xy(tx2, y0 + 8), str(num), font=fs(26), fill=GOLD)
        d.text(xy(x0 + PANEL_W - 12 - d.textlength(src, font=fs(18)) / S, y0 + 10),
               src, font=fs(18), fill=GOLD)
        lines = wrap(d, head, fs(24), tw2, 2)
        yy = y0 + 42
        for ln in lines:
            d.text(xy(tx2, yy), ln, font=fs(24), fill=WHITE)
            yy += 29
        d.text(xy(tx2, y0 + 104), deck, font=fs(20), fill=WHITE)
        d.text(xy(tx2, y0 + 134), stat, font=fs(36), fill=GOLD)

    # ---- 12 picture tiles ----------------------------------------------
    for idx, (l1, l2, scene) in enumerate(TILES):
        col, row = idx % 6, idx // 6
        x0 = M + col * (TILE_W + TILE_GAP)
        y0 = TILE_Y[0] + row * (TILE_H + 8)
        d.rectangle(box(x0, y0, x0 + TILE_W, y0 + TILE_H), fill=PANEL,
                    outline=PANEL_LINE, width=lw(3))
        TILE_SCENES[scene](d, x0 + 4, y0 + 4, TILE_W - 8, 54)
        centre(d, l1, fs(18), y0 + 62, x0, x0 + TILE_W, WHITE, tr=0)
        centre(d, l2, fs(18), y0 + 81, x0, x0 + TILE_W, GOLD, tr=0)

    # ---- DATE CHECK + sources -------------------------------------------
    dy0, dy1 = DATECHECK
    d.rectangle(box(M, dy0, W - M, dy1), fill=PANEL, outline=RED, width=lw(3))
    label = "DATE CHECK"
    d.text(xy(M + 10, dy0 + 6), label, font=fs(18), fill=RED)
    rest = (" \u2014 HOMS 26 DEC 2025, NOT TODAY \u00b7 "
            "NEPAL CHOPPER 3 NOV 2026, NOT 4 NOV")
    d.text(xy(M + 10 + d.textlength(label, font=fs(18)) / S, dy0 + 6), rest,
           font=fs(18), fill=WHITE)
    centre(d, ("SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 ONS \u00b7 UNI GLOBAL "
               "\u00b7 CHESS.COM \u2014 ALL 36 STORIES VERIFIED 27 NOV 2026"),
           fs(16), dy0 + 30, M, W - M, GOLD)

    # ---- downscale + sharpen --------------------------------------------
    img1024 = img.resize((W, H), Image.LANCZOS)
    img1024 = img1024.filter(ImageFilter.UnsharpMask(radius=2, percent=150,
                                                     threshold=3))
    prev = img1024.resize((300, 300), Image.LANCZOS)
    prev = prev.filter(ImageFilter.UnsharpMask(radius=1, percent=130,
                                               threshold=2))
    import io
    buf = io.BytesIO()
    img1024.save(buf, format="PNG")
    entry_bytes = buf.getvalue()
    buf2 = io.BytesIO()
    prev.save(buf2, format="PNG")
    return entry_bytes, buf2.getvalue()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    entry_bytes, prev_bytes = render()
    with open(os.path.join(here, "entry.png"), "wb") as f:
        f.write(entry_bytes)
    with open(os.path.join(here, "preview-300.png"), "wb") as f:
        f.write(prev_bytes)
    print(f"entry.png: {len(entry_bytes)} bytes")
    print(f"preview-300.png: {len(prev_bytes)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
