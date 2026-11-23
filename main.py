#!/usr/bin/env python3
"""Render 23 November 2026's world news as one 1024x1024 front-page image.

Reads news.json next to this script and writes /output/entry.png
(or $MAKEFUN_OUTPUT_PATH). Deterministic: fixed geometry, fixed fonts,
no clock, no randomness, no network.

Editorial concept — THE HANDOVER: power changes hands all day.
A CEO returns (Nvidia), a kingpin falls (Sinaloa), an alliance is
renegotiated with strings attached (Manila), a blockade is tested
(Hormuz), a record is broken (SpaceX), the game expands to four
nations (Women's World Cup). The page is built around that idea, not
around a grid: one dominant lead story, two supporting stories, and
a text-only briefs strip — a classic broadsheet, not yesterday's
dark 2x3 card grid. Cream paper, black ink, one red accent.

The six stories and every fact are the verified ones in news.json /
verification.md; only the headlines are re-angled to the theme.
If Pillow cannot be imported, the bundled entry.png is copied to
the output path instead.
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

# Broadsheet palette: cream paper, black ink, one red accent.
PAPER = (247, 243, 232)
INK = (28, 28, 32)
MUTED = (110, 105, 95)
RED = (172, 32, 48)
RULE = (28, 28, 32)
HEADLINE = (28, 28, 32)
SUMMARY = (58, 56, 52)
FOOTER = (110, 105, 95)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Accent colour per story, in news.json order.
ACCENTS = [
    (46, 120, 60),    # Nvidia: green
    (172, 32, 48),    # Hormuz: red
    (150, 110, 40),   # Manila: gold
    (40, 80, 140),    # SpaceX: blue
    (40, 110, 70),    # FIFA: green
    (170, 90, 40),    # Sinaloa: rust
]


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


def sky(draw, x, y, w, h, top, bottom, bands=12):
    for i in range(bands):
        t = i / (bands - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        y0 = y + i * h // bands
        y1 = y + (i + 1) * h // bands
        draw.rectangle([x, y0, x + w, y1], fill=c)


def stars(draw, x, y, points, color=(232, 236, 244)):
    for fx, fy, r in points:
        draw.ellipse([x + fx - r, y + fy - r, x + fx + r, y + fy + r], fill=color)


def scene_nvidia_wide(draw, x, y, w, h):
    """Wide lead picture: one big AI chip on a dark board, shares arrow up.

    Drawn for a wide panel (944x200). Chip left-of-centre, circuit
    traces radiating across the board, a rising arrow and +33% right.
    """
    draw.rectangle([x, y, x + w, y + h], fill=(8, 24, 16))
    # long circuit traces across the board
    for ty in (26, 52, 148, 174):
        draw.line([x + 12, y + ty, x + w - 12, y + ty], fill=(38, 92, 54), width=2)
        draw.ellipse([x + 8, y + ty - 3, x + 14, y + ty + 3], fill=(118, 185, 0))
        draw.ellipse([x + w - 14, y + ty - 3, x + w - 8, y + ty + 3],
                     fill=(118, 185, 0))
    # vertical traces on the far right
    for tx in (w - 90, w - 60, w - 30):
        draw.line([x + tx, y + 8, x + tx, y + 60], fill=(38, 92, 54), width=2)
        draw.ellipse([x + tx - 3, y + 4, x + tx + 3, y + 10], fill=(118, 185, 0))
    # the chip: big, centred left, gold pins, glowing green core
    cx0, cy0, cx1, cy1 = x + 190, y + 45, x + 390, y + 155
    draw.rectangle([cx0, cy0, cx1, cy1], fill=(16, 34, 22),
                   outline=(118, 185, 0), width=4)
    for px in range(cx0 + 14, cx1 - 8, 22):
        draw.line([x + px, y + 33, x + px, cy0], fill=(201, 168, 106), width=4)
        draw.line([x + px, cy1, x + px, y + 167], fill=(201, 168, 106), width=4)
    for py in range(cy0 + 16, cy1 - 8, 22):
        draw.line([x + 178, y + py, cx0, y + py], fill=(201, 168, 106), width=4)
        draw.line([cx1, y + py, x + 402, y + py], fill=(201, 168, 106), width=4)
    draw.rectangle([x + 248, y + 78, x + 332, y + 122], fill=(118, 185, 0))
    draw.rectangle([x + 262, y + 88, x + 318, y + 112], fill=(190, 235, 120))
    # rising arrow across the right half
    draw.line([x + 470, y + 176, x + 600, y + 128, x + 720, y + 88, x + 850, y + 42],
              fill=(150, 220, 80), width=5)
    draw.polygon([(x + 850, y + 42), (x + 826, y + 38), (x + 846, y + 62)],
                 fill=(150, 220, 80))
    pct_font = load_font(SANS_BOLD, 34)
    draw.text((x + 700, y + 8), "+33%", font=pct_font, fill=(150, 220, 80))
    sub_font = load_font(SANS, 13)
    draw.text((x + 704, y + 52), "in early trading", font=sub_font,
              fill=(226, 200, 150))


def scene_hormuz(draw, x, y, w, h):
    """Night strait: three tankers in convoy crossing a dashed blockade line."""
    sky(draw, x, y, w, h, (14, 20, 38), (44, 56, 84))
    stars(draw, x, y, [(30, 12, 1), (120, 20, 2), (220, 10, 1), (330, 16, 2),
                       (410, 12, 1), (70, 30, 1), (280, 28, 1)], (220, 226, 236))
    draw.ellipse([x + 330, y + 34, x + 420, y + 62], fill=(190, 110, 50))
    draw.ellipse([x + 350, y + 42, x + 400, y + 58], fill=(230, 160, 70))
    draw.rectangle([x, y + 62, x + w, y + h], fill=(13, 30, 50))
    draw.line([x, y + 62, x + w, y + 62], fill=(90, 120, 150), width=1)
    for dx in range(0, w, 26):
        draw.line([x + dx, y + 84, x + dx + 14, y + 84], fill=(198, 91, 78), width=3)
    for tx, tw in ((30, 120), (180, 104), (316, 112)):
        draw.polygon([(x + tx, y + 66), (x + tx + tw, y + 66),
                      (x + tx + tw - 8, y + 78), (x + tx + 8, y + 78)],
                     fill=(58, 76, 98))
        draw.rectangle([x + tx + tw - 34, y + 56, x + tx + tw - 20, y + 66],
                       fill=(58, 76, 98))
        draw.ellipse([x + tx + tw - 31, y + 52, x + tx + tw - 23, y + 60],
                     fill=(232, 163, 61))
        draw.line([x + tx, y + 66, x + tx + tw, y + 66],
                  fill=(140, 160, 180), width=1)
    for wx in (60, 210, 350):
        draw.line([x + wx, y + 92, x + wx + 26, y + 92], fill=(90, 120, 150), width=1)
        draw.line([x + wx + 8, y + 100, x + wx + 30, y + 100], fill=(70, 100, 130), width=1)


def scene_manila(draw, x, y, w, h):
    """Two flags side by side — US left, Philippines right — with a $2.4B pill."""
    mid = x + w // 2
    for i in range(7):
        fill = (178, 34, 52) if i % 2 == 0 else (240, 240, 238)
        draw.rectangle([x, y + i * h // 7, mid, y + (i + 1) * h // 7], fill=fill)
    draw.rectangle([x, y, x + 92, y + 58], fill=(40, 60, 110))
    for sx in range(8, 88, 16):
        for sy in range(8, 54, 14):
            draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                         fill=(240, 240, 238))
    draw.rectangle([mid, y, x + w, y + h // 2], fill=(0, 56, 168))
    draw.rectangle([mid, y + h // 2, x + w, y + h], fill=(206, 17, 38))
    draw.polygon([(mid, y), (mid, y + h), (mid + 96, y + h // 2)],
                 fill=(240, 240, 238))
    draw.ellipse([mid + 30, y + 44, mid + 50, y + 64], fill=(253, 209, 0))
    draw.ellipse([mid + 36, y + 50, mid + 44, y + 58], fill=(240, 240, 238))
    draw.rounded_rectangle([x + 168, y + 36, x + 282, y + 72], radius=18,
                           fill=(201, 168, 106), outline=(242, 232, 201), width=2)
    pill_font = load_font(SANS_BOLD, 20)
    label = "$2.4B"
    lw = draw.textlength(label, font=pill_font)
    draw.text((x + (w - lw) / 2, y + 42), label, font=pill_font, fill=(20, 26, 40))


def render():
    from PIL import Image, ImageDraw

    with open(os.path.join(HERE, "news.json"), encoding="utf-8") as f:
        data = json.load(f)
    stories = data["stories"]

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- masthead: theme kicker, title, dateline, double rule
    kick_font = load_font(SANS_BOLD, 15)
    kicker = "P O W E R   C H A N G E S   H A N D S"
    kw = draw.textlength(kicker, font=kick_font)
    draw.text(((W - kw) / 2, 24), kicker, font=kick_font, fill=RED)

    title_font = load_font(SERIF_BOLD, 46)
    title = data["title"]
    tw = draw.textlength(title, font=title_font)
    draw.text(((W - tw) / 2, 46), title, font=title_font, fill=INK)

    sub_font = load_font(SANS, 13)
    sub = data["subtitle"]
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((W - sw) / 2, 106), sub, font=sub_font, fill=MUTED)

    draw.line([MARGIN, 130, W - MARGIN, 130], fill=RULE, width=2)
    draw.line([MARGIN, 134, W - MARGIN, 134], fill=RULE, width=1)

    # --- lead story: full-width picture, red tag, huge headline, summary
    lead = stories[0]
    panel = Image.new("RGB", (CW, 200), PAPER)
    pdraw = ImageDraw.Draw(panel)
    scene_nvidia_wide(pdraw, 0, 0, CW, 200)
    img.paste(panel, (MARGIN, 148))

    tag_font = load_font(SANS_BOLD, 14)
    draw.text((MARGIN, 360), lead["tag"], font=tag_font, fill=RED)
    head_font, head_lines = fit_text(draw, lead["headline"], SERIF_BOLD,
                                     38, CW, 2, 28)
    hy = 382
    for line in head_lines:
        draw.text((MARGIN, hy), line, font=head_font, fill=HEADLINE)
        hy += head_font.size + 4
    sum_font, sum_lines = fit_text(draw, lead["summary"], SANS,
                                   15, CW, 2, 13)
    sy = hy + 6
    for line in sum_lines:
        draw.text((MARGIN, sy), line, font=sum_font, fill=SUMMARY)
        sy += sum_font.size + 5

    draw.line([MARGIN, 500, W - MARGIN, 500], fill=RULE, width=1)

    # --- supporting stories: two columns, picture + tag + headline + summary
    mid_top = 516
    col_w = (CW - 24) // 2
    for i, story in enumerate(stories[1:3]):
        cx = MARGIN + i * (col_w + 24)
        panel = Image.new("RGB", (col_w, 104), PAPER)
        pdraw = ImageDraw.Draw(panel)
        if i == 0:
            scene_hormuz(pdraw, 0, 0, col_w, 104)
        else:
            scene_manila(pdraw, 0, 0, col_w, 104)
        img.paste(panel, (cx, mid_top))
        accent = ACCENTS[i + 1]
        draw.text((cx, mid_top + 112), story["tag"], font=tag_font, fill=accent)
        h_font, h_lines = fit_text(draw, story["headline"], SERIF_BOLD,
                                   19, col_w, 2, 16)
        hy = mid_top + 132
        for line in h_lines:
            draw.text((cx, hy), line, font=h_font, fill=HEADLINE)
            hy += h_font.size + 3
        s_font, s_lines = fit_text(draw, story["summary"], SANS,
                                   13, col_w, 3, 11)
        sy = hy + 4
        for line in s_lines:
            draw.text((cx, sy), line, font=s_font, fill=SUMMARY)
            sy += s_font.size + 4
    # vertical rule between the two columns
    draw.line([MARGIN + col_w + 12, mid_top, MARGIN + col_w + 12, 752],
              fill=RULE, width=1)
    draw.line([MARGIN, 762, W - MARGIN, 762], fill=RULE, width=1)

    # --- the day in brief: text-only strip, three columns, vertical rules
    brief_font = load_font(SANS_BOLD, 13)
    brief_title = "THE DAY IN BRIEF"
    bw = draw.textlength(brief_title, font=brief_font)
    bcx = W // 2
    draw.line([MARGIN, 786, bcx - bw / 2 - 14, 786], fill=RULE, width=1)
    draw.line([bcx + bw / 2 + 14, 786, W - MARGIN, 786], fill=RULE, width=1)
    draw.text((bcx - bw / 2, 776), brief_title, font=brief_font, fill=INK)

    brief_top = 802
    brief_w = (CW - 2 * 24) // 3
    for j, story in enumerate(stories[3:6]):
        bx = MARGIN + j * (brief_w + 24)
        accent = ACCENTS[j + 3]
        btag_font = load_font(SANS_BOLD, 12)
        draw.text((bx, brief_top), story["tag"], font=btag_font, fill=accent)
        h_font, h_lines = fit_text(draw, story["headline"], SERIF_BOLD,
                                   17, brief_w, 2, 14)
        hy = brief_top + 20
        for line in h_lines:
            draw.text((bx, hy), line, font=h_font, fill=HEADLINE)
            hy += h_font.size + 3
        s_font, s_lines = fit_text(draw, story["summary"], SANS,
                                   12, brief_w, 3, 11)
        sy = hy + 4
        for line in s_lines:
            draw.text((bx, sy), line, font=s_font, fill=SUMMARY)
            sy += s_font.size + 4
        if j < 2:
            draw.line([bx + brief_w + 12, brief_top, bx + brief_w + 12, 948],
                      fill=RULE, width=1)

    # --- footer: sources, wrapped to two centred lines
    foot_font = load_font(SANS, 11)
    foot_lines = wrap(draw, data["sources"], foot_font, CW)
    fy = 962
    for line in foot_lines[:2]:
        lw = draw.textlength(line, font=foot_font)
        draw.text(((W - lw) / 2, fy), line, font=foot_font, fill=FOOTER)
        fy += 15

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
