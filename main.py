#!/usr/bin/env python3
"""Render 23 November 2026's world news as one 1024x1024 front-page image.

Reads news.json next to this script and writes /output/entry.png
(or $MAKEFUN_OUTPUT_PATH). Deterministic: fixed geometry, fixed fonts,
no clock, no randomness, no network.

Editorial concept — THE ATLAS OF A DAY: the news as geography.
One day, pinned to the map. The page is organised around a world map:
the six lead stories are numbered red pins on it, and every other
story is an amber dot. A UTC timeline runs under the masthead, a
numbers band counts the day, a legend explains how sure each story
is, and the remaining 29 stories run as a compact three-column
register. No grid of equal cards (22 Nov), no broadsheet lead story
(the early 23 Nov "Handover") — the map is the hierarchy. Slate ink
on pale paper, teal and amber accents, red only for the pins.

The 35 stories and every fact are the verified ones in news.json /
verification.md (39-story deduped pool, 10 genuinely independent
ranking passes). If Pillow cannot be imported, the bundled entry.png
is copied to the output path instead.
"""

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.environ.get("MAKEFUN_OUTPUT_PATH") or "/output/entry.png"

W, H = 1024, 1024
MARGIN = 40
CW = W - 2 * MARGIN  # 944 content width

# Atlas palette: pale paper, slate ink, teal + amber accents, red pins.
PAPER = (250, 250, 247)
INK = (24, 34, 44)
MUTED = (105, 115, 125)
TEAL = (13, 110, 110)
AMBER = (198, 122, 20)
RED = (188, 52, 40)
RULE = (24, 34, 44)
CARD = (255, 255, 255)
CARD_LINE = (210, 216, 220)
TILE = (235, 238, 240)
SEA = (222, 231, 236)
LAND = (176, 190, 198)
LAND_LINE = (140, 158, 170)
GRID = (200, 210, 216)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

LABEL_COLOR = {"REPORTED": TEAL, "CLAIM": AMBER, "ONGOING": RED}

# --- world map: simplified continent outlines in (lon, lat) ---
NORTH_AMERICA = [(-168, 66), (-156, 71), (-140, 70), (-128, 71), (-115, 73),
                 (-100, 73), (-90, 74), (-85, 70), (-80, 73), (-70, 62),
                 (-65, 60), (-60, 55), (-55, 52), (-60, 47), (-65, 44),
                 (-70, 42), (-74, 39), (-75, 35), (-80, 32), (-81, 26),
                 (-84, 30), (-89, 29), (-91, 19), (-87, 15), (-83, 9),
                 (-79, 8), (-82, 9), (-86, 12), (-88, 14), (-92, 15),
                 (-95, 17), (-97, 20), (-100, 22), (-105, 23), (-110, 25),
                 (-114, 29), (-120, 34), (-124, 42), (-124, 48), (-128, 54),
                 (-135, 58), (-145, 60), (-155, 58), (-162, 55), (-168, 60)]
GREENLAND = [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74),
             (-25, 78), (-35, 80), (-50, 80), (-58, 76), (-60, 70),
             (-55, 64), (-50, 60)]
SOUTH_AMERICA = [(-79, 9), (-76, 5), (-79, 0), (-81, -5), (-79, -9),
                 (-76, -14), (-71, -18), (-70, -22), (-70, -28), (-72, -35),
                 (-73, -42), (-73, -50), (-68, -55), (-66, -50), (-65, -45),
                 (-63, -40), (-59, -35), (-54, -33), (-50, -30), (-44, -24),
                 (-40, -20), (-37, -13), (-35, -8), (-35, -5), (-40, -3),
                 (-44, -2), (-50, 0), (-53, 4), (-57, 6), (-62, 9),
                 (-68, 11), (-72, 12), (-76, 10)]
AFRICA = [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
          (38, 22), (43, 12), (48, 11), (51, 10), (46, 5), (42, 0),
          (40, -6), (38, -12), (35, -18), (33, -25), (30, -30), (26, -34),
          (20, -35), (17, -32), (14, -25), (12, -18), (10, -8), (9, -1),
          (5, 4), (-2, 5), (-8, 4), (-13, 8), (-16, 12), (-17, 15),
          (-16, 20), (-14, 25), (-10, 30), (-6, 33)]
EURASIA = [(-10, 36), (-9, 43), (-4, 48), (-1, 50), (3, 51), (6, 54),
           (8, 57), (10, 59), (14, 56), (18, 56), (21, 55), (24, 58),
           (26, 60), (30, 62), (30, 66), (35, 67), (40, 68), (48, 68),
           (55, 68), (62, 70), (70, 72), (78, 73), (85, 75), (95, 76),
           (105, 77), (115, 74), (125, 72), (135, 71), (145, 72),
           (155, 70), (165, 69), (175, 66), (178, 65), (173, 62),
           (170, 60), (162, 56), (158, 53), (156, 50), (150, 55),
           (145, 59), (142, 54), (140, 46), (138, 40), (135, 35),
           (132, 33), (129, 34), (126, 36), (122, 38), (120, 33),
           (118, 28), (114, 22), (110, 20), (108, 14), (105, 10),
           (102, 8), (99, 10), (97, 14), (94, 17), (91, 22), (89, 22),
           (86, 20), (83, 17), (80, 13), (77, 8), (75, 10), (73, 16),
           (70, 20), (67, 23), (63, 25), (60, 25), (57, 26), (54, 27),
           (52, 28), (50, 29), (48, 30), (45, 30), (42, 32), (40, 34),
           (38, 36), (36, 36), (33, 36), (30, 36), (27, 37), (24, 36),
           (22, 37), (20, 39), (18, 40), (16, 42), (14, 44), (12, 44),
           (10, 44), (8, 44), (5, 43), (3, 42), (0, 40), (-2, 37),
           (-6, 36), (-9, 37)]
UK = [(-5, 50), (-3, 53), (-2, 55), (-1, 57), (-3, 58), (-5, 56),
      (-6, 54), (-5, 51)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (125, -33),
             (130, -32), (135, -35), (138, -35), (140, -38), (145, -38),
             (150, -37), (153, -32), (153, -27), (150, -23), (146, -19),
             (142, -15), (142, -11), (140, -17), (136, -15), (132, -12),
             (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 36), (140, 38),
         (141, 41), (142, 44), (144, 44), (143, 42), (141, 39), (140, 36),
         (139, 34), (137, 33), (135, 33), (133, 31)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -20), (48, -24),
              (45, -25), (44, -20)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
               (174, -41), (172, -43), (169, -46)]
INDONESIA = [(105, -6), (110, -7), (115, -8), (120, -9), (125, -9),
             (130, -3), (135, -4), (140, -8)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              UK, AUSTRALIA, JAPAN, MADAGASCAR, NEW_ZEALAND]

# Map frame (right of the lead column).
MAP_X0, MAP_Y0, MAP_W, MAP_H = 372, 158, 612, 338


def proj(lon, lat):
    """Equirectangular: lon -180..180, lat 84..-58 -> map pixels."""
    x = MAP_X0 + (lon + 180) / 360 * MAP_W
    y = MAP_Y0 + (84 - lat) / 142 * MAP_H
    return x, y


def load_font(path, size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if not cur or draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, font_path, size, max_w, max_lines, min_size):
    """Shrink the font until the text fits in max_lines; return (font, lines)."""
    while size > min_size:
        font = load_font(font_path, size)
        lines = wrap(draw, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
        size -= 1
    font = load_font(font_path, min_size)
    return font, wrap(draw, text, font, max_w)[:max_lines]


def fit_one_line(draw, text, font_path, size, max_w, min_size):
    """Shrink until the text fits on one line; truncate with ellipsis if needed."""
    while size > min_size:
        font = load_font(font_path, size)
        if draw.textlength(text, font=font) <= max_w:
            return font, text
        size -= 1
    font = load_font(font_path, min_size)
    while text and draw.textlength(text + "…", font=font) > max_w:
        text = text[:-1]
    return font, text + "…" if text else text


def draw_map(draw, featured, secondary):
    """Stylised world map: pale sea, graticule, slate continents,
    red numbered pins for the six lead stories, amber dots for the rest."""
    from PIL import ImageFont  # noqa: F401  (kept local for symmetry)
    draw.rectangle([MAP_X0, MAP_Y0, MAP_X0 + MAP_W, MAP_Y0 + MAP_H], fill=SEA)
    # graticule every 30 degrees
    for lon in range(-150, 181, 30):
        x, _ = proj(lon, 0)
        draw.line([x, MAP_Y0, x, MAP_Y0 + MAP_H], fill=GRID, width=1)
    for lat in (60, 30, 0, -30):
        _, y = proj(0, lat)
        draw.line([MAP_X0, y, MAP_X0 + MAP_W, y], fill=GRID, width=1)
    # continents
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    for lon, lat in INDONESIA:
        x, y = proj(lon, lat)
        draw.ellipse([x - 4, y - 3, x + 4, y + 3], fill=LAND,
                     outline=LAND_LINE)
    # equator label
    _, eq_y = proj(0, 0)
    eq_font = load_font(SANS, 9)
    draw.text((MAP_X0 + 6, eq_y + 3), "EQUATOR", font=eq_font, fill=MUTED)
    # map title + caption on the empty Arctic strip
    t_font = load_font(SANS_BOLD, 11)
    draw.text((MAP_X0 + 8, MAP_Y0 + 6), "THE WORLD, 23 NOVEMBER 2026",
              font=t_font, fill=INK)
    c_font = load_font(SANS, 10)
    cap = "PINS 1–6 = LEAD STORIES · DOTS = THE REST"
    cw = draw.textlength(cap, font=c_font)
    draw.text((MAP_X0 + MAP_W - cw - 8, MAP_Y0 + 7), cap, font=c_font,
              fill=MUTED)
    # secondary stories: small amber dots
    for s in secondary:
        x, y = proj(s["lon"], s["lat"])
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=AMBER,
                     outline=INK)
    # lead stories: red numbered pins
    pin_font = load_font(SANS_BOLD, 12)
    for s in featured:
        x, y = proj(s["lon"], s["lat"])
        draw.ellipse([x - 11, y - 11, x + 11, y + 11], fill=RED,
                     outline=INK, width=2)
        label = str(s["num"])
        lw = draw.textlength(label, font=pin_font)
        draw.text((x - lw / 2, y - 8), label, font=pin_font,
                  fill=(255, 255, 255))
    draw.rectangle([MAP_X0, MAP_Y0, MAP_X0 + MAP_W, MAP_Y0 + MAP_H],
                   outline=INK, width=2)


def icon_kyiv(draw, x, y, s):
    """Two apartment blocks, one hit: amber burst above a broken roof."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=(52, 58, 68))
    draw.rectangle([x + 10, y + 26, x + 24, y + 48], fill=(240, 240, 238))
    draw.rectangle([x + 30, y + 18, x + 46, y + 48], fill=(200, 204, 208))
    draw.line([x + 30, y + 18, x + 38, y + 10, x + 46, y + 18],
              fill=(200, 204, 208), width=2)
    for dx, dy in ((-6, -8), (0, -10), (6, -8), (-9, -3), (9, -3)):
        draw.line([x + 38 + dx // 2, y + 12 + dy // 2, x + 38 + dx, y + 12 + dy],
                  fill=(240, 170, 60), width=2)
    for wy in (32, 40):
        draw.line([x + 13, y + wy, x + 21, y + wy], fill=(52, 58, 68), width=1)
        draw.line([x + 33, y + wy, x + 43, y + wy], fill=(52, 58, 68), width=1)


def icon_ebola(draw, x, y, s):
    """White medical cross on teal."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=TEAL)
    draw.rectangle([x + 24, y + 10, x + 32, y + 46], fill=(255, 255, 255))
    draw.rectangle([x + 10, y + 24, x + 46, y + 32], fill=(255, 255, 255))


def icon_sanctions(draw, x, y, s):
    """Oil barrel with a diagonal cut: the lifeline, severed."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=(44, 44, 52))
    draw.rounded_rectangle([x + 16, y + 12, x + 40, y + 44], radius=4,
                           fill=(198, 122, 20))
    draw.line([x + 16, y + 20, x + 40, y + 20], fill=(44, 44, 52), width=2)
    draw.line([x + 16, y + 36, x + 40, y + 36], fill=(44, 44, 52), width=2)
    draw.line([x + 8, y + 48, x + 48, y + 8], fill=(240, 240, 238), width=4)


def icon_eu(draw, x, y, s):
    """Circle of stars on EU blue."""
    import math
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=(40, 80, 140))
    cx, cy, r = x + 28, y + 28, 15
    for i in range(8):
        a = math.pi * 2 * i / 8 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(253, 209, 0))


def icon_ship(draw, x, y, s):
    """A warship listing to one side over wave lines."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=(38, 84, 110))
    draw.polygon([(x + 8, y + 34), (x + 48, y + 26), (x + 44, y + 38),
                  (x + 12, y + 42)], fill=(240, 240, 238))
    draw.rectangle([x + 26, y + 20, x + 30, y + 28], fill=(240, 240, 238))
    for wy in (46, 50):
        draw.line([x + 8, y + wy, x + 20, y + wy], fill=(180, 210, 225),
                  width=2)
        draw.line([x + 26, y + wy, x + 40, y + wy], fill=(180, 210, 225),
                  width=2)


def icon_chip(draw, x, y, s):
    """An AI chip, gold pins, glowing green core."""
    draw.rounded_rectangle([x, y, x + s, y + s], radius=8, fill=(16, 34, 22))
    for px in range(x + 14, x + 44, 8):
        draw.line([px, y + 6, px, y + 14], fill=(201, 168, 106), width=2)
        draw.line([px, y + 42, px, y + 50], fill=(201, 168, 106), width=2)
    for py in range(y + 14, y + 44, 8):
        draw.line([x + 6, py, x + 14, py], fill=(201, 168, 106), width=2)
        draw.line([x + 42, py, x + 50, py], fill=(201, 168, 106), width=2)
    draw.rectangle([x + 16, y + 16, x + 40, y + 40], fill=(16, 34, 22),
                   outline=(118, 185, 0), width=2)
    draw.rectangle([x + 22, y + 22, x + 34, y + 34], fill=(118, 185, 0))


ICONS = {1: icon_kyiv, 2: icon_ebola, 3: icon_sanctions,
         4: icon_eu, 5: icon_ship, 6: icon_chip}


def render():
    from PIL import Image, ImageDraw

    with open(os.path.join(HERE, "news.json"), encoding="utf-8") as f:
        data = json.load(f)
    featured = data["featured"]
    secondary = data["secondary"]

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- masthead: kicker, title, subtitle, double rule
    kick_font = load_font(SANS_BOLD, 13)
    kicker = data["kicker"]
    kw = draw.textlength(kicker, font=kick_font)
    draw.text(((W - kw) / 2, 14), kicker, font=kick_font, fill=TEAL)

    title_font = load_font(SERIF_BOLD, 44)
    tw = draw.textlength(data["title"], font=title_font)
    draw.text(((W - tw) / 2, 34), data["title"], font=title_font, fill=INK)

    sub_font = load_font(SANS, 13)
    sw = draw.textlength(data["subtitle"], font=sub_font)
    draw.text(((W - sw) / 2, 82), data["subtitle"], font=sub_font,
              fill=MUTED)

    draw.line([MARGIN, 100, W - MARGIN, 100], fill=RULE, width=2)
    draw.line([MARGIN, 104, W - MARGIN, 104], fill=RULE, width=1)

    # --- UTC timeline strip (dot positions approximate)
    tl_font = load_font(SANS_BOLD, 10)
    draw.text((MARGIN, 112), "23 NOV 2026 · UTC", font=tl_font, fill=INK)
    cap_font = load_font(SANS, 9)
    cap = "dot positions approximate"
    cw = draw.textlength(cap, font=cap_font)
    draw.text((W - MARGIN - cw, 113), cap, font=cap_font, fill=MUTED)
    tl_y = 132
    draw.line([MARGIN, tl_y, W - MARGIN, tl_y], fill=INK, width=2)
    tick_font = load_font(SANS, 9)
    for hour in (0, 4, 8, 12, 16, 20, 24):
        tx = MARGIN + hour / 24 * CW
        draw.line([tx, tl_y - 4, tx, tl_y + 4], fill=INK, width=2)
        lab = f"{hour:02d}"
        lw = draw.textlength(lab, font=tick_font)
        draw.text((tx - lw / 2, tl_y + 7), lab, font=tick_font, fill=MUTED)
    pin_font = load_font(SANS_BOLD, 9)
    for s in featured:
        px = MARGIN + s["hour"] / 24 * CW
        draw.ellipse([px - 8, tl_y - 8, px + 8, tl_y + 8], fill=RED,
                     outline=INK, width=1)
        lab = str(s["num"])
        lw = draw.textlength(lab, font=pin_font)
        draw.text((px - lw / 2, tl_y - 7), lab, font=pin_font,
                  fill=(255, 255, 255))

    # --- lead column: six numbered cards, one per featured story
    card_x, card_w = MARGIN, 316
    card_h, card_gap = 92, 6
    for i, s in enumerate(featured):
        cy = 156 + i * (card_h + card_gap)
        draw.rounded_rectangle([card_x, cy, card_x + card_w, cy + card_h],
                               radius=6, fill=CARD, outline=CARD_LINE, width=1)
        # icon + number badge
        ICONS[s["num"]](draw, card_x + 10, cy + 18, 56)
        draw.ellipse([card_x + 4, cy + 12, card_x + 22, cy + 30], fill=RED,
                     outline=INK, width=1)
        b_font = load_font(SANS_BOLD, 11)
        blab = str(s["num"])
        bw = draw.textlength(blab, font=b_font)
        draw.text((card_x + 13 - bw / 2, cy + 15), blab, font=b_font,
                  fill=(255, 255, 255))
        tx = card_x + 76
        tw = card_x + card_w - 8 - tx
        # top line: tag left, source + label right
        tag_font = load_font(SANS_BOLD, 11)
        draw.text((tx, cy + 8), s["tag"], font=tag_font, fill=TEAL)
        src_font = load_font(SANS, 9)
        lab_color = LABEL_COLOR[s["label"]]
        src_txt = s["source"] + " · "
        lab_txt = s["label"]
        sw = draw.textlength(src_txt, font=src_font)
        lw = draw.textlength(lab_txt, font=src_font)
        sx = card_x + card_w - 8 - sw - lw
        draw.text((sx, cy + 9), src_txt, font=src_font, fill=MUTED)
        draw.text((sx + sw, cy + 9), lab_txt, font=src_font, fill=lab_color)
        # headline (2 lines) + summary (2 lines)
        h_font, h_lines = fit_text(draw, s["headline"], SERIF_BOLD,
                                   15, tw, 2, 13)
        hy = cy + 24
        for line in h_lines:
            draw.text((tx, hy), line, font=h_font, fill=INK)
            hy += h_font.size + 3
        s_font, s_lines = fit_text(draw, s["summary"], SANS,
                                   11, tw, 2, 10)
        sy = hy + 2
        for line in s_lines:
            draw.text((tx, sy), line, font=s_font, fill=(58, 56, 52))
            sy += s_font.size + 3

    # --- world map (right of the lead column)
    draw_map(draw, featured, secondary)

    # --- the day in numbers
    num_title_font = load_font(SANS_BOLD, 11)
    draw.text((MAP_X0, 504), "THE DAY IN NUMBERS",
              font=num_title_font, fill=INK)
    tile_w, tile_gap = 95, 8
    for i, n in enumerate(data["numbers"]):
        tx = MAP_X0 + i * (tile_w + tile_gap)
        draw.rounded_rectangle([tx, 520, tx + tile_w, 592], radius=6,
                               fill=TILE)
        v_font = load_font(SANS_BOLD, 22)
        vw = draw.textlength(n["value"], font=v_font)
        draw.text((tx + (tile_w - vw) / 2, 528), n["value"], font=v_font,
                  fill=TEAL)
        l_font = load_font(SANS, 9)
        l_lines = wrap(draw, n["label"], l_font, tile_w - 10)
        ly = 556
        for line in l_lines[:2]:
            lw = draw.textlength(line, font=l_font)
            draw.text((tx + (tile_w - lw) / 2, ly), line, font=l_font,
                      fill=MUTED)
            ly += 12

    # --- how sure + regions (right, under the numbers band)
    leg_title_font = load_font(SANS_BOLD, 11)
    draw.text((MAP_X0, 602), "HOW SURE", font=leg_title_font, fill=INK)
    leg_font = load_font(SANS, 10)
    legend = [
        ("REPORTED", "confirmed by multiple sources or official word"),
        ("CLAIM", "asserted by one source or a party, not yet confirmed"),
        ("ONGOING", "still developing; figures may change"),
    ]
    for j, (lab, text) in enumerate(legend):
        ry = 622 + j * 20
        draw.rectangle([MAP_X0, ry + 2, MAP_X0 + 10, ry + 12],
                       fill=LABEL_COLOR[lab])
        draw.text((MAP_X0 + 16, ry), lab + " — " + text, font=leg_font,
                  fill=INK)
    reg_font = load_font(SANS, 10)
    draw.text((MAP_X0, 690), data["regions"], font=reg_font, fill=INK)
    note_font = load_font(SANS, 9)
    note = "Every story names its source. Full verification in verification.md."
    draw.text((MAP_X0, 712), note, font=note_font, fill=MUTED)

    # --- the rest of the day: compact three-column register
    list_title_font = load_font(SANS_BOLD, 12)
    draw.text((MARGIN, 752), "THE REST OF THE DAY — 29 MORE STORIES",
              font=list_title_font, fill=INK)
    col_w = (CW - 2 * 24) // 3  # 298
    row_font = load_font(SANS, 10)
    for j, s in enumerate(secondary):
        col = j // 10
        row = j % 10
        bx = MARGIN + col * (col_w + 24)
        by = 776 + row * 16
        num_txt = f"{s['num']} · "
        src_txt = f" — {s['source']} · "
        lab_txt = s["label"]
        nw = draw.textlength(num_txt, font=row_font)
        sw = draw.textlength(src_txt, font=row_font)
        lw = draw.textlength(lab_txt, font=row_font)
        head_w = col_w - nw - sw - lw - 4
        head_font, head_txt = fit_one_line(draw, s["headline"], SANS, 10,
                                           head_w, 9)
        x = bx
        draw.text((x, by), num_txt, font=row_font, fill=TEAL)
        x += nw
        draw.text((x, by), head_txt, font=head_font, fill=INK)
        x += draw.textlength(head_txt, font=head_font)
        draw.text((x, by), src_txt, font=row_font, fill=MUTED)
        x += sw
        draw.text((x, by), lab_txt, font=row_font,
                  fill=LABEL_COLOR[s["label"]])

    # --- footer: DATE CHECK + sources
    draw.line([MARGIN, 944, W - MARGIN, 944], fill=RULE, width=1)
    foot_font = load_font(SANS, 10)
    foot_lines = wrap(draw, data["datecheck"], foot_font, CW)
    fy = 950
    for line in foot_lines[:3]:
        draw.text((MARGIN, fy), line, font=foot_font, fill=(58, 56, 52))
        fy += 12
    src_font = load_font(SANS, 10)
    src_lines = wrap(draw, data["sources"], src_font, CW)
    fy = 988
    for line in src_lines[:2]:
        lw = draw.textlength(line, font=src_font)
        draw.text(((W - lw) / 2, fy), line, font=src_font, fill=MUTED)
        fy += 12

    out_dir = os.path.dirname(OUTPUT)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    img.save(OUTPUT, "PNG")
    os.chmod(OUTPUT, 0o644)


def main():
    try:
        import PIL  # noqa: F401
    except ImportError:
        bundled = os.path.join(HERE, "entry.png")
        out_dir = os.path.dirname(OUTPUT)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(bundled, OUTPUT)
        os.chmod(OUTPUT, 0o644)
        return 0
    render()
    return 0


if __name__ == "__main__":
    sys.exit(main())
