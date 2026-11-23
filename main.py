#!/usr/bin/env python3
"""Render 23 November 2026's world news as one 1024x1024 front-page image.

Reads news.json next to this script and writes /output/entry.png
(or $MAKEFUN_OUTPUT_PATH). Deterministic: fixed geometry, fixed fonts,
no clock, no randomness, no network. Each story card carries a picture
panel drawn procedurally with Pillow (no image assets) above its tag,
headline and summary. If Pillow cannot be imported, the bundled
entry.png is copied to the output path instead.

The six stories are a mixed set — tech, conflict, diplomacy, space,
sport and crime — with only one war story, per the reader's request.
"""

import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.environ.get("MAKEFUN_OUTPUT_PATH") or "/output/entry.png"

W, H = 1024, 1024
PAGE_BG = (14, 26, 43)
CARD_BG = (22, 39, 62)
CARD_LINE = (42, 63, 92)
CREAM = (242, 232, 201)
GOLD = (201, 168, 106)
HEADLINE = (242, 237, 227)
SUMMARY = (185, 194, 207)
FOOTER = (138, 148, 164)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# One accent colour per story, in news.json order.
ACCENTS = [
    (118, 185, 0),    # Nvidia: green
    (198, 91, 78),    # Hormuz: red
    (217, 164, 65),   # Manila: gold
    (91, 141, 201),   # SpaceX: blue
    (95, 168, 107),   # FIFA: green
    (217, 123, 63),   # Sinaloa: orange
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


def scene_nvidia(draw, x, y, w, h):
    """AI chip on a dark board, traces fanning out, shares arrow up."""
    draw.rectangle([x, y, x + w, y + h], fill=(8, 24, 16))
    # circuit traces from the chip to the edges
    for ty in (18, 34, 74, 90):
        draw.line([x + 8, y + ty, x + 168, y + ty], fill=(38, 92, 54), width=2)
        draw.ellipse([x + 4, y + ty - 3, x + 10, y + ty + 3], fill=(118, 185, 0))
    for tx in (300, 330, 360, 390):
        draw.line([x + tx, y + 8, x + tx, y + 100], fill=(38, 92, 54), width=2)
        draw.ellipse([x + tx - 3, y + 4, x + tx + 3, y + 10], fill=(118, 185, 0))
    # chip: dark square, gold pins, glowing core
    draw.rectangle([x + 168, y + 22, x + 282, y + 86], fill=(16, 34, 22),
                   outline=(118, 185, 0), width=3)
    for px in range(180, 274, 16):
        draw.line([x + px, y + 14, x + px, y + 22], fill=(201, 168, 106), width=3)
        draw.line([x + px, y + 86, x + px, y + 94], fill=(201, 168, 106), width=3)
    for py in range(34, 78, 16):
        draw.line([x + 160, y + py, x + 168, y + py], fill=(201, 168, 106), width=3)
        draw.line([x + 282, y + py, x + 290, y + py], fill=(201, 168, 106), width=3)
    draw.rectangle([x + 198, y + 42, x + 252, y + 66], fill=(118, 185, 0))
    draw.rectangle([x + 206, y + 48, x + 244, y + 60], fill=(190, 235, 120))
    # rising arrow, bottom-left to top-right, over the board
    draw.line([x + 300, y + 96, x + 350, y + 66, x + 395, y + 44, x + 430, y + 18],
              fill=(150, 220, 80), width=4)
    draw.polygon([(x + 430, y + 18), (x + 414, y + 16), (x + 428, y + 32)],
                 fill=(150, 220, 80))
    pct_font = load_font(SANS_BOLD, 17)
    draw.text((x + 356, y + 6), "+33%", font=pct_font, fill=(150, 220, 80))


def scene_hormuz(draw, x, y, w, h):
    """Night strait: three tankers in convoy crossing a dashed blockade line."""
    sky(draw, x, y, w, h, (14, 20, 38), (44, 56, 84))
    stars(draw, x, y, [(30, 12, 1), (120, 20, 2), (220, 10, 1), (330, 16, 2),
                       (410, 12, 1), (70, 30, 1), (280, 28, 1)], (220, 226, 236))
    # low orange glow on the horizon
    draw.ellipse([x + 330, y + 34, x + 420, y + 62], fill=(190, 110, 50))
    draw.ellipse([x + 350, y + 42, x + 400, y + 58], fill=(230, 160, 70))
    # sea
    draw.rectangle([x, y + 62, x + w, y + h], fill=(13, 30, 50))
    draw.line([x, y + 62, x + w, y + 62], fill=(90, 120, 150), width=1)
    # dashed red blockade line across the sea
    for dx in range(0, w, 26):
        draw.line([x + dx, y + 84, x + dx + 14, y + 84], fill=(198, 91, 78), width=3)
    # three tanker silhouettes, light slate so they read on the sea
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
    # wake lines
    for wx in (60, 210, 350):
        draw.line([x + wx, y + 92, x + wx + 26, y + 92], fill=(90, 120, 150), width=1)
        draw.line([x + wx + 8, y + 100, x + wx + 30, y + 100], fill=(70, 100, 130), width=1)


def scene_manila(draw, x, y, w, h):
    """Two flags side by side — US left, Philippines right — with a $2.4B pill."""
    mid = x + w // 2
    # --- US flag: stripes + blue canton with dot stars
    for i in range(7):
        fill = (178, 34, 52) if i % 2 == 0 else (240, 240, 238)
        draw.rectangle([x, y + i * h // 7, mid, y + (i + 1) * h // 7], fill=fill)
    draw.rectangle([x, y, x + 92, y + 58], fill=(40, 60, 110))
    for sx in range(8, 88, 16):
        for sy in range(8, 54, 14):
            draw.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                         fill=(240, 240, 238))
    # --- Philippine flag: white triangle, blue over red, small sun
    draw.rectangle([mid, y, x + w, y + h // 2], fill=(0, 56, 168))
    draw.rectangle([mid, y + h // 2, x + w, y + h], fill=(206, 17, 38))
    draw.polygon([(mid, y), (mid, y + h), (mid + 96, y + h // 2)],
                 fill=(240, 240, 238))
    draw.ellipse([mid + 30, y + 44, mid + 50, y + 64], fill=(253, 209, 0))
    draw.ellipse([mid + 36, y + 50, mid + 44, y + 58], fill=(240, 240, 238))
    # --- gold pill with the price, centred on the seam
    draw.rounded_rectangle([x + 168, y + 36, x + 282, y + 72], radius=18,
                           fill=(201, 168, 106), outline=(242, 232, 201), width=2)
    pill_font = load_font(SANS_BOLD, 20)
    label = "$2.4B"
    lw = draw.textlength(label, font=pill_font)
    draw.text((x + (w - lw) / 2, y + 42), label, font=pill_font, fill=(20, 26, 40))


def scene_spacex(draw, x, y, w, h):
    """Falcon 9 climbing at dawn from Vandenberg, flame and smoke below."""
    sky(draw, x, y, w, h, (28, 40, 72), (226, 132, 66))
    stars(draw, x, y, [(24, 12, 1), (90, 20, 2), (150, 10, 1), (210, 18, 1),
                       (60, 34, 1), (180, 30, 2)], (232, 236, 244))
    # ground and pad
    draw.rectangle([x, y + 92, x + w, y + h], fill=(24, 22, 30))
    draw.rectangle([x + 296, y + 86, x + 360, y + 92], fill=(52, 52, 58))
    # launch tower to the left of the rocket
    draw.rectangle([x + 262, y + 22, x + 270, y + 92], fill=(90, 92, 98))
    for ty in (30, 46, 62, 78):
        draw.line([x + 262, y + ty, x + 288, y + ty], fill=(90, 92, 98), width=3)
    # rocket body, nose cone, flame
    draw.rectangle([x + 300, y + 26, x + 322, y + 86], fill=(238, 238, 234))
    draw.polygon([(x + 300, y + 26), (x + 311, y + 8), (x + 322, y + 26)],
                 fill=(200, 40, 40))
    draw.rectangle([x + 300, y + 40, x + 322, y + 44], fill=(40, 60, 110))
    draw.polygon([(x + 302, y + 86), (x + 311, y + 108), (x + 320, y + 86)],
                 fill=(240, 138, 36))
    draw.polygon([(x + 306, y + 86), (x + 311, y + 100), (x + 316, y + 86)],
                 fill=(245, 197, 66))
    # smoke clouds at the base
    for sx, sy, sr in ((292, 92, 12), (312, 96, 14), (336, 92, 11), (352, 98, 9)):
        draw.ellipse([x + sx - sr, y + sy - sr // 2, x + sx + sr, y + sy + sr // 2],
                     fill=(150, 150, 156))
    # turnaround time, top-left
    time_font = load_font(SANS_BOLD, 16)
    draw.text((x + 14, y + 10), "32h 03m", font=time_font, fill=(242, 232, 201))
    sub_font = load_font(SANS, 11)
    draw.text((x + 14, y + 30), "pad turnaround", font=sub_font, fill=(226, 200, 150))
    # second tiny rocket silhouette far left, the previous launch
    draw.rectangle([x + 96, y + 62, x + 104, y + 86], fill=(120, 124, 130))
    draw.polygon([(x + 96, y + 62), (x + 100, y + 54), (x + 104, y + 62)],
                 fill=(120, 124, 130))


def scene_fifa(draw, x, y, w, h):
    """Soccer pitch, big ball, gold trophy, 48 teams."""
    draw.rectangle([x, y, x + w, y + h], fill=(30, 100, 56))
    draw.rectangle([x + 10, y + 8, x + w - 10, y + h - 8], outline=(240, 240, 240), width=2)
    draw.line([x + 10, y + h // 2, x + w - 10, y + h // 2], fill=(240, 240, 240), width=2)
    draw.ellipse([x + 196, y + 22, x + 254, y + 86], outline=(240, 240, 240), width=2)
    # soccer ball, centre-left
    cx, cy, r = x + 116, y + 54, 34
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(244, 244, 242))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(40, 40, 40), width=2)
    px, py = cx, cy
    draw.polygon([(px - 9, py - 12), (px + 9, py - 12), (px + 14, py + 4),
                  (px, py + 14), (px - 14, py + 4)], fill=(30, 30, 30))
    for bx, by in ((cx - 24, cy - 18), (cx + 24, cy - 18), (cx - 28, cy + 14),
                   (cx + 28, cy + 14), (cx, cy - 28)):
        draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(30, 30, 30))
    # gold trophy, right
    tx = x + 330
    draw.polygon([(tx, y + 34), (tx + 44, y + 34), (tx + 38, y + 62),
                  (tx + 6, y + 62)], fill=(232, 183, 70))
    draw.arc([tx - 8, y + 34, tx + 6, y + 52], 90, 270, fill=(232, 183, 70), width=3)
    draw.arc([tx + 38, y + 34, tx + 52, y + 52], 270, 90, fill=(232, 183, 70), width=3)
    draw.rectangle([tx + 18, y + 62, tx + 26, y + 74], fill=(232, 183, 70))
    draw.rectangle([tx + 8, y + 74, tx + 36, y + 80], fill=(232, 183, 70))
    # 48 teams, top-right
    num_font = load_font(SANS_BOLD, 22)
    draw.text((x + 384, y + 12), "48", font=num_font, fill=(242, 232, 201))
    team_font = load_font(SANS_BOLD, 11)
    draw.text((x + 384, y + 38), "TEAMS", font=team_font, fill=(242, 232, 201))


def scene_sinaloa(draw, x, y, w, h):
    """Night raid over Guasave: helicopters, searchlights, rooftops."""
    sky(draw, x, y, w, h, (8, 12, 26), (26, 32, 56))
    stars(draw, x, y, [(30, 14, 1), (120, 10, 2), (200, 16, 1), (300, 12, 2),
                       (400, 18, 1), (70, 26, 1), (250, 26, 1), (360, 30, 1)],
          (220, 226, 236))
    # rooftops along the bottom, a few lit windows
    draw.rectangle([x, y + 88, x + w, y + h], fill=(12, 14, 24))
    for bx, bw, bh in ((0, 90, 12), (100, 70, 18), (180, 110, 10), (300, 80, 16),
                       (390, 60, 12)):
        draw.rectangle([x + bx, y + 88 - bh, x + bx + bw, y + 88], fill=(20, 22, 34))
    for wx, wy in ((24, 80), (130, 76), (220, 82), (330, 78), (410, 80)):
        draw.rectangle([x + wx, y + wy, x + wx + 5, y + wy + 5], fill=(232, 183, 70))
    # helicopter 1, upper left, beam sweeping down-right
    hx, hy = x + 96, y + 30
    draw.ellipse([hx - 26, hy - 8, hx + 26, hy + 8], fill=(70, 74, 82))
    draw.line([hx + 24, hy, hx + 52, hy - 6], fill=(70, 74, 82), width=4)
    draw.line([hx - 34, hy - 12, hx + 34, hy - 12], fill=(150, 152, 158), width=3)
    draw.polygon([(hx - 6, hy + 6), (hx + 10, hy + 6), (hx + 78, y + 88),
                  (hx + 52, y + 88)], fill=(240, 230, 180))
    # helicopter 2, upper right, beam sweeping down-left
    hx2, hy2 = x + 340, y + 22
    draw.ellipse([hx2 - 24, hy2 - 7, hx2 + 24, hy2 + 7], fill=(70, 74, 82))
    draw.line([hx2 - 22, hy2, hx2 - 48, hy2 - 5], fill=(70, 74, 82), width=4)
    draw.line([hx2 - 32, hy2 - 11, hx2 + 32, hy2 - 11], fill=(150, 152, 158), width=3)
    draw.polygon([(hx2 - 8, hy2 + 5), (hx2 + 8, hy2 + 5), (hx2 - 44, y + 88),
                  (hx2 - 70, y + 88)], fill=(240, 230, 180))
    # red beacon dots on the helicopters
    draw.ellipse([hx - 4, hy - 16, hx + 2, hy - 10], fill=(220, 60, 60))
    draw.ellipse([hx2 - 2, hy2 - 15, hx2 + 4, hy2 - 9], fill=(220, 60, 60))


SCENES = [scene_nvidia, scene_hormuz, scene_manila,
          scene_spacex, scene_fifa, scene_sinaloa]


def render():
    from PIL import Image, ImageDraw

    with open(os.path.join(HERE, "news.json"), encoding="utf-8") as f:
        data = json.load(f)

    img = Image.new("RGB", (W, H), PAGE_BG)
    draw = ImageDraw.Draw(img)

    # masthead
    title_font = load_font(SERIF_BOLD, 44)
    title = data["title"]
    tw = draw.textlength(title, font=title_font)
    draw.text(((W - tw) / 2, 26), title, font=title_font, fill=CREAM)
    sub_font = load_font(SANS, 16)
    sub = data["subtitle"]
    sw = draw.textlength(sub, font=sub_font)
    draw.text(((W - sw) / 2, 88), sub, font=sub_font, fill=GOLD)
    draw.line([36, 120, W - 36, 120], fill=GOLD, width=2)

    # 2x3 grid of cards
    margin, gutter_x, gutter_y = 36, 20, 18
    card_w = (W - 2 * margin - gutter_x) // 2
    card_h = 258
    grid_top = 138
    for i, story in enumerate(data["stories"]):
        row, col = divmod(i, 2)
        cx = margin + col * (card_w + gutter_x)
        cy = grid_top + row * (card_h + gutter_y)
        accent = ACCENTS[i % len(ACCENTS)]
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h],
                               radius=10, fill=CARD_BG, outline=CARD_LINE, width=1)
        # picture panel
        px, py, pw, ph = cx + 8, cy + 8, card_w - 16, 108
        panel = Image.new("RGB", (pw, ph), CARD_BG)
        pdraw = ImageDraw.Draw(panel)
        SCENES[i % len(SCENES)](pdraw, 0, 0, pw, ph)
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw, ph], radius=8, fill=255)
        img.paste(panel, (px, py), mask)
        # tag, headline, summary
        tag_font = load_font(SANS_BOLD, 13)
        draw.text((cx + 14, cy + 124), story["tag"], font=tag_font, fill=accent)
        head_font, head_lines = fit_text(draw, story["headline"], SERIF_BOLD,
                                         20, card_w - 28, 2, 16)
        hy = cy + 143
        for line in head_lines:
            draw.text((cx + 14, hy), line, font=head_font, fill=HEADLINE)
            hy += head_font.size + 4
        sum_font, sum_lines = fit_text(draw, story["summary"], SANS,
                                       14, card_w - 28, 3, 12)
        sy = hy + 4
        for line in sum_lines:
            draw.text((cx + 14, sy), line, font=sum_font, fill=SUMMARY)
            sy += sum_font.size + 4

    # footer: sources, wrapped to two centred lines
    foot_font = load_font(SANS, 12)
    foot_lines = wrap(draw, data["sources"], foot_font, W - 2 * margin)
    fy = 962
    for line in foot_lines[:2]:
        lw = draw.textlength(line, font=foot_font)
        draw.text(((W - lw) / 2, fy), line, font=foot_font, fill=FOOTER)
        fy += 16

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
