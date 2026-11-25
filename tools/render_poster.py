#!/usr/bin/env python3
"""Render the one-image front page for make.fun's news-image-20261125 bounty.

Reads news.json (the day's verified stories) and draws a newspaper-style
poster at 2048x2048, downscaled to 1024x1024 as entry.png at the repo root.
Deterministic: fixed layout, fixed seed, no clocks, no network.
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SS = 2  # supersampling factor
W = 1024 * SS
H = 1024 * SS

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "news.json").read_text(encoding="utf-8"))

NOTO = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = f"{NOTO}/NotoSerifDisplay-Black.ttf"
SERIF_XBOLD = f"{NOTO}/NotoSerifDisplay-ExtraBold.ttf"
SERIF_BOLD = f"{NOTO}/NotoSerif-Bold.ttf"
SANS = f"{NOTO}/NotoSans-Regular.ttf"
SANS_BOLD = f"{NOTO}/NotoSans-Bold.ttf"
SANS_SEMI = f"{NOTO}/NotoSans-SemiBold.ttf"

PAPER = (248, 244, 236)
INK = (22, 19, 14)
RED = (163, 22, 33)
GREY = (96, 90, 80)
HAIR = (178, 168, 150)
NAVY_TOP = (24, 42, 63)
NAVY_BOT = (11, 20, 32)


def F(path, size):
    return ImageFont.truetype(path, size * SS)


def text_w(draw, s, font):
    return draw.textlength(s, font=font)


def spaced_w(draw, s, font, tracking):
    return sum(text_w(draw, ch, font) for ch in s) + tracking * SS * max(0, len(s) - 1)


def draw_spaced(draw, xy, s, font, fill, tracking):
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=font, fill=fill)
        x += text_w(draw, ch, font) + tracking * SS
    return x


def wrap(draw, s, font, max_w):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, xy, s, font, fill, max_w, leading):
    x, y = xy
    for line in wrap(draw, s, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading * SS
    return y


def skyline(draw, box):
    """Abstract night skyline of Riyadh's financial district with the PIF Tower."""
    x0, y0, x1, y1 = [v * SS for v in box]
    for i in range(int(y1 - y0)):  # vertical gradient
        t = i / max(1, (y1 - y0))
        col = tuple(int(NAVY_TOP[c] + (NAVY_BOT[c] - NAVY_TOP[c]) * t) for c in range(3))
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=col)
    rng = random.Random(20261125)
    # moon
    mx, my, mr = x1 - 52 * SS, y0 + 40 * SS, 15 * SS
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(233, 226, 205))
    # background buildings
    bx = x0 + 8 * SS
    base = y1
    while bx < x1 - 10 * SS:
        bw = rng.randint(22, 40) * SS
        bh = rng.randint(38, 92) * SS
        draw.rectangle([bx, base - bh, bx + bw, base], fill=(30, 52, 74))
        for _ in range(rng.randint(3, 9)):
            wx = bx + rng.randint(3, max(4, int(bw / SS) - 6)) * SS
            wy = base - rng.randint(6, max(7, int(bh / SS) - 6)) * SS
            draw.rectangle([wx, wy, wx + 2.4 * SS, wy + 3.2 * SS], fill=(214, 186, 110))
        bx += bw + rng.randint(4, 10) * SS
    # the PIF Tower: tall slab with its signature arch notch near the top
    tw = 58 * SS
    tcx = x0 + (x1 - x0) * 0.46
    ttop = y0 + 16 * SS
    draw.rectangle([tcx - tw / 2, ttop, tcx + tw / 2, base], fill=(44, 74, 102))
    draw.rectangle([tcx - tw / 2, ttop, tcx - tw / 2 + 3 * SS, base], fill=(86, 122, 152))
    notch_w, notch_h = 20 * SS, 34 * SS
    ny = ttop + 20 * SS
    draw.polygon(
        [(tcx - notch_w / 2, ny + notch_h), (tcx, ny), (tcx + notch_w / 2, ny + notch_h)],
        fill=NAVY_TOP,
    )
    for i in range(9):  # lit window rows on the tower
        wy = ttop + 66 * SS + i * 15 * SS
        if wy > base - 10 * SS:
            break
        draw.line([(tcx - tw / 2 + 7 * SS, wy), (tcx + tw / 2 - 7 * SS, wy)], fill=(120, 158, 188), width=max(1, SS))
    # impact burst, mid-facade
    ex, ey = tcx + tw / 2 + 4 * SS, ttop + 118 * SS
    pts = []
    for i in range(16):
        r = (17 if i % 2 == 0 else 7) * SS
        import math

        a = math.pi * i / 8
        pts.append((ex + r * math.cos(a), ey + r * math.sin(a) * 0.82))
    draw.polygon(pts, fill=(232, 177, 60))
    draw.ellipse([ex - 6 * SS, ey - 6 * SS, ex + 6 * SS, ey + 6 * SS], fill=(198, 44, 32))
    # smoke wisps
    for dx, dy, r in [(2, -30, 9), (16, -40, 12), (30, -30, 8)]:
        draw.ellipse(
            [ex + dx * SS - r * SS, ey + dy * SS - r * SS * 0.55, ex + dx * SS + r * SS, ey + dy * SS + r * SS * 0.55],
            fill=(120, 128, 138),
        )


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 52  # side margin (final px)
    RIGHT = 1024 - MX

    # frame: double rule
    d.rectangle([16 * SS, 16 * SS, (1024 - 16) * SS, (1024 - 16) * SS], outline=INK, width=2 * SS)
    d.rectangle([22 * SS, 22 * SS, (1024 - 22) * SS, (1024 - 22) * SS], outline=INK, width=1 * SS)

    # ---- masthead ----
    name_f = F(SERIF_BLACK, 34)
    tag_f = F(SANS_BOLD, 12.5)
    d.text((MX * SS, 36 * SS), DATA["paper_name"], font=name_f, fill=INK)
    tag = "ONE DAY · ONE IMAGE · THE WHOLE WORLD"
    tw = spaced_w(d, tag, tag_f, 1.6)
    draw_spaced(d, (RIGHT * SS - tw, 49 * SS), tag, tag_f, RED, 1.6)
    d.rectangle([MX * SS, 80 * SS, RIGHT * SS, 84 * SS], fill=RED)
    d.line([MX * SS, 89 * SS, RIGHT * SS, 89 * SS], fill=INK, width=1 * SS)
    date_f = F(SERIF_BLACK, 46)
    d.text((MX * SS, 97 * SS), DATA["date_line"], font=date_f, fill=INK)
    strap_f = F(SANS_SEMI, 14.5)
    d.text((MX * SS, 152 * SS), DATA["strap"], font=strap_f, fill=GREY)

    # ---- lead story ----
    y = 178
    kick_f = F(SANS_BOLD, 13.5)
    draw_spaced(d, (MX * SS, y * SS), DATA["lead"]["kicker"], kick_f, RED, 1.8)
    y += 20
    head_f = F(SERIF_BLACK, 52)
    y = para(d, (MX * SS, y * SS), DATA["lead"]["headline"], head_f, INK, 600 * SS, 59) / SS
    y += 4
    body_f = F(SANS, 16)
    y = para(d, (MX * SS, y * SS), DATA["lead"]["body"], body_f, (40, 36, 30), 592 * SS, 22.5) / SS
    lead_bottom = y
    # visual panel
    vx0, vy0, vx1, vy1 = 668, 178, RIGHT, 382
    skyline(d, (vx0, vy0, vx1, vy1))
    d.rectangle([vx0 * SS, vy0 * SS, vx1 * SS, vy1 * SS], outline=INK, width=1 * SS)
    cap_f = F(SANS_SEMI, 12.5)
    para(d, (vx0 * SS, (vy1 + 8) * SS), DATA["lead"]["caption"], cap_f, GREY, (vx1 - vx0) * SS, 17)
    y = max(lead_bottom, vy1 + 42) + 8
    d.line([MX * SS, y * SS, RIGHT * SS, y * SS], fill=INK, width=2 * SS)
    y += 14

    # ---- story cards: 2 columns x 3 rows ----
    chip_f = F(SANS_BOLD, 11.5)
    card_head_f = F(SERIF_BOLD, 20)
    card_body_f = F(SANS, 14)
    col_w = 448
    col_x = [MX, MX + col_w + 24]
    for row in range(3):
        row_bottom = y
        for col in range(2):
            card = DATA["cards"][row * 2 + col]
            cx = col_x[col]
            cy = y
            draw_spaced(d, (cx * SS, cy * SS), card["chip"], chip_f, RED, 1.4)
            cy += 17
            cy = para(d, (cx * SS, cy * SS), card["headline"], card_head_f, INK, col_w * SS, 24) / SS
            cy += 2
            cy = para(d, (cx * SS, cy * SS), card["body"], card_body_f, (52, 48, 42), col_w * SS, 19) / SS
            row_bottom = max(row_bottom, cy)
        y = row_bottom + 9
        if row < 2:
            d.line([MX * SS, (y - 6) * SS, RIGHT * SS, (y - 6) * SS], fill=HAIR, width=1 * SS)

    # ---- around the world ----
    d.line([MX * SS, y * SS, RIGHT * SS, y * SS], fill=INK, width=2 * SS)
    y += 10
    sec_f = F(SANS_BOLD, 13)
    draw_spaced(d, (MX * SS, y * SS), "AROUND THE WORLD", sec_f, INK, 1.8)
    y += 17
    mini_head_f = F(SANS_BOLD, 14)
    mini_f = F(SANS, 14)
    col3_w = 296
    col3_x = [MX, MX + col3_w + 16, MX + 2 * (col3_w + 16)]
    bottom = y
    for i, item in enumerate(DATA["around"]):
        cx = col3_x[i]
        lead_in = item["lead"] + " — "
        lead_w = text_w(d, lead_in, mini_head_f)
        words = item["text"].split()
        first, rest = "", []
        for wi, word in enumerate(words):
            trial = word if not first else first + " " + word
            if text_w(d, trial, mini_f) <= col3_w * SS - lead_w or not first:
                first = trial
            else:
                rest = words[wi:]
                break
        else:
            rest = []
        cy = y
        d.text((cx * SS, cy * SS), lead_in.rstrip(), font=mini_head_f, fill=INK)
        d.text((cx * SS + lead_w, cy * SS), first, font=mini_f, fill=(52, 48, 42))
        cy += 18
        for line in wrap(d, " ".join(rest), mini_f, col3_w * SS) if rest else []:
            d.text((cx * SS, cy * SS), line, font=mini_f, fill=(52, 48, 42))
            cy += 18
        bottom = max(bottom, cy)
    y = bottom + 10

    # ---- the day in numbers ----
    band_y1 = 1024 - 100
    d.rectangle([36 * SS, band_y1 * SS, (1024 - 36) * SS, (band_y1 + 58) * SS], fill=INK)
    num_f = F(SERIF_XBOLD, 29)
    lab_f = F(SANS_BOLD, 10)
    cell_w = (1024 - 72) / 5
    for i, n in enumerate(DATA["numbers"]):
        cx = 36 + i * cell_w
        nw = text_w(d, n["value"], num_f)
        d.text((cx * SS + (cell_w * SS - nw) / 2, (band_y1 + 5) * SS), n["value"], font=num_f, fill=(250, 246, 238))
        lab_lines = wrap(d, n["label"], lab_f, (cell_w - 14) * SS)
        ly = band_y1 + 37
        for line in lab_lines[:2]:
            lw = text_w(d, line, lab_f)
            d.text((cx * SS + (cell_w * SS - lw) / 2, ly * SS), line, font=lab_f, fill=(206, 198, 182))
            ly += 12
    title = "THE DAY IN NUMBERS"
    tf = F(SANS_BOLD, 11)
    twd = spaced_w(d, title, tf, 1.8)
    draw_spaced(d, ((1024 * SS - twd) / 2, (band_y1 - 16) * SS), title, tf, RED, 1.8)

    # ---- footer ----
    foot_f = F(SANS_SEMI, 11.5)
    fw = text_w(d, DATA["footer"], foot_f)
    d.text(((1024 * SS - fw) / 2, (1024 - 36) * SS), DATA["footer"], font=foot_f, fill=GREY)

    print("content bottom before numbers band:", round(y), "(band starts", band_y1, ")")
    img = img.resize((1024, 1024), Image.LANCZOS)
    out = ROOT / "entry.png"
    img.save(out, optimize=True)
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
