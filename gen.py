#!/usr/bin/env python3
"""Broadsheet front page: cream stock, Palatino display, Times body.

Vertical rhythm is fixed and asserted: every band's height is computed before it
is drawn, so body copy can never slide under the next rule.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 26

PAPER = "#f5f0e4"
INK = "#15120e"
BODY = "#2c2822"
MUTED = "#6d655a"
RULE = "#c3b8a4"
RED = "#8f1d22"

F = "/usr/share/fonts/opentype/urw-base35/"
DISPLAY = F + "P052-Bold.otf"
DISPLAY_I = F + "P052-Italic.otf"
DISPLAY_R = F + "P052-Roman.otf"
TEXT = F + "NimbusRoman-Regular.otf"
TEXT_B = F + "NimbusRoman-Bold.otf"
TEXT_I = F + "NimbusRoman-Italic.otf"
LABEL = F + "NimbusSansNarrow-Bold.otf"

cache = {}


def font(path, size):
    key = (path, size)
    if key not in cache:
        cache[key] = ImageFont.truetype(path, size)
    return cache[key]


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def tw(s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def text(x, y, s, size, color=INK, path=DISPLAY_R, maxw=None, anchor="la"):
    f = font(path, size)
    w = tw(s, f)
    if maxw is not None:
        assert w <= maxw, ("OVERFLOW", s[:44], w, round(maxw, 1))
    d.text((x, y), s, font=f, fill=color, anchor=anchor if anchor != "la" else None)
    return w


def caps(x, y, s, size, color=INK, maxw=None, anchor="la"):
    return text(x, y, s.upper(), size, color, LABEL, maxw, anchor)


def rule(y, x1=M, x2=W - M, color=RULE, width=1):
    d.line((x1, y, x2, y), fill=color, width=width)


def wrapped(x, y, s, size, color, maxw, leading, path=TEXT, max_lines=None):
    f = font(path, size)
    words, lines, cur = s.split(), [], ""
    for w in words:
        probe = (cur + " " + w).strip()
        if tw(probe, f) <= maxw:
            cur = probe
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lines = lines[:max_lines] if max_lines else lines
    for i, line in enumerate(lines):
        d.text((x, y + i * leading), line, font=f, fill=color)
    return y + len(lines) * leading, len(lines)


# ---------------------------------------------------------------- banner (0-16)
d.rectangle((0, 0, W, 16), fill=INK)
caps(M, 4, "The world in one day", 8.5, PAPER, 300)
caps(W - M, 4, "45 stories · every continent · one day's reporting", 8.5, PAPER, 460, anchor="ra")

# ---------------------------------------------------------------- masthead (20-92)
text(M, 26, "THE WORLD DESK", 52, INK, DISPLAY, 620)
text(W - M, 40, "All the news that fits, printed once.", 12, MUTED, DISPLAY_I, 330, anchor="ra")
caps(W - M, 60, "founded 2023 · one sheet, every morning", 8, MUTED, 330, anchor="ra")
rule(88, width=2)
caps(M, 93, "Vol. IV · No. 325", 8.5, BODY, 170)
caps(W // 2, 92, "Friday 20 November 2026", 10.5, INK, 250, anchor="ma")
caps(W - M, 93, "Late edition · price: one look", 8.5, BODY, 250, anchor="ra")
rule(108)

# ---------------------------------------------------------------- deck (112-148)
deck = ("Trump, Xi and Putin sit at one table in Shenzhen  ·  The World Court finds genocide "
        "in Myanmar  ·  COP31 draft drops the fossil-fuel line")
wrapped(M, 112, deck, 11.5, RED, W - 2 * M, 15, TEXT_I, max_lines=2)
rule(150)

# ---------------------------------------------------------------- index bar (152-170)
REGIONS = [("EUROPE", 5, "#3a5a70"), ("MIDDLE EAST", 5, "#7b4436"), ("ASIA", 12, "#96323f"),
           ("AMERICAS", 11, "#356154"), ("AFRICA", 3, "#77602f"), ("OCEANIA", 5, "#4a4f78"),
           ("GLOBAL", 4, "#575d66")]
assert sum(r[1] for r in REGIONS) == 45
weights = [104, 132, 100, 132, 96, 112, 118]
gap = 3
span = W - 2 * M - gap * (len(REGIONS) - 1)
scale = span / sum(weights)
x = M
for (name, count, color), raw in zip(REGIONS, weights):
    ww = round(raw * scale)
    d.rectangle((x, 154, x + ww, 172), fill=color)
    caps(x + 5, 158, f"{name} {count}", 8, "#ffffff", ww - 9)
    x += ww + gap

# ---------------------------------------------------------------- stats (176-212)
STATS = [("3", "leaders at one table"), ("109–0", "World Court vote"),
         ("$120bn", "COP31 adaptation line"), ("15.9m", "GTA VI pre-orders"),
         ("1.2m", "still without power")]
rule(176)
caps(M, 180, "the day in numbers", 7.2, MUTED, 200)
cell = (W - 2 * M) / len(STATS)
for i, (big, small) in enumerate(STATS):
    sx = M + i * cell
    if i:
        d.line((sx - 7, 186, sx - 7, 212), fill=RULE)
    text(sx, 184, big, 17, INK, DISPLAY, cell - 14)
    caps(sx, 202, small, 7.2, MUTED, cell - 14)
rule(216)

# ---------------------------------------------------------------- leads (220-452)
LEADS = [
    dict(tag="1  SHENZHEN · SUMMIT", head=["Three leaders, one table,", "and no communiqué"],
         body=("Trump, Xi and Putin met in one room for the first time and left without a signed "
               "text. Officials described an understanding on shipping lanes and a carbon-market "
               "working group; neither side released the wording. The host called the meeting "
               "candid, Washington called it useful, and neither word appears in any document."),
         credit="Reuters, AP · Shenzhen", art="summit"),
    dict(tag="2  THE HAGUE · WORLD COURT", head=["Court finds genocide", "in Myanmar"],
         body=("Judges voted 109–0 on the provisional finding and ordered the state to preserve "
               "evidence and report back within four months. The chamber set no timetable for "
               "reparations, which a separate phase will decide."),
         credit="AP · The Hague", art="court"),
    dict(tag="3  COP31 · FINAL DRAFT", head=["Fossil line dropped", "from the draft text"],
         body=("The presidency removed the phrase naming fossil fuels and replaced it with "
               "\"unabated emissions\". Adaptation finance held at $120bn a year, below the figure "
               "the small-island bloc had asked for."),
         credit="AFP · Baku", art="cop"),
]

lead_y = 222
widths = [388, 290, 290]
art_h = 96
xl = M
for i, lead in enumerate(LEADS):
    lw = widths[i]
    ax, top = xl, lead_y
    if lead["art"] == "summit":
        d.rectangle((ax, top, ax + lw, top + art_h), fill="#c9d3d1")
        for k in range(5):
            d.rectangle((ax, top + 10 + k * 15, ax + lw, top + 24 + k * 15), fill=["#bfcac8", "#b4c0be", "#a9b5b3", "#9eaaa8", "#93a09e"][k])
        d.ellipse((ax + 30, top + 30, ax + 96, top + 96), fill="#7f8785")
        d.ellipse((ax + lw // 2 - 33, top + 26, ax + lw // 2 + 33, top + 92), fill="#8d9593")
        d.ellipse((ax + lw - 96, top + 30, ax + lw - 30, top + 96), fill="#7f8785")
        for fx, col in ((0.14, "#b8352f"), (0.5, "#b8352f"), (0.86, "#2f4f7a")):
            d.rectangle((ax + int(lw * fx) - 11, top + art_h - 40, ax + int(lw * fx) + 11, top + art_h - 16), fill=col)
        d.rectangle((ax, top + art_h - 16, ax + lw, top + art_h - 4), fill="#2a3130")
    elif lead["art"] == "court":
        d.rectangle((ax, top, ax + lw, top + art_h), fill="#ddd6c8")
        d.rectangle((ax + 20, top + art_h - 18, ax + lw - 20, top + art_h - 8), fill="#b6ab97")
        for k in range(5):
            cx = ax + 42 + k * ((lw - 84) // 4)
            d.rectangle((cx, top + 34, cx + 11, top + art_h - 18), fill="#cfc6b3")
        d.rectangle((ax + 30, top + 28, ax + lw - 30, top + 36), fill="#a89c86")
        d.polygon([(ax + 30, top + 28), (ax + lw // 2, top + 6), (ax + lw - 30, top + 28)], fill="#9d9179")
        d.line((ax + lw // 2, top + 14, ax + lw // 2, top + 62), fill="#6b6153", width=3)
        d.line((ax + lw // 2 - 22, top + 24, ax + lw // 2 + 22, top + 24), fill="#6b6153", width=2)
    else:
        d.rectangle((ax, top, ax + lw, top + art_h), fill="#cdd4d8")
        d.ellipse((ax + 46, top + 8, ax + 142, top + 104), fill="#9fb0b8")
        d.ellipse((ax + 68, top + 26, ax + 120, top + 78), fill="#7f939c")
        d.rectangle((ax + 140, top + 46, ax + 176, top + 82), fill="#b9c2c6")
        d.rectangle((ax + 140, top + 46, ax + 156, top + 56), fill="#d05a4a")
        for k in range(4):
            d.line((ax + 8, top + 12 + k * 24, ax + lw - 8, top + 24 + k * 24), fill="#e6ebed", width=2)
    d.rectangle((ax, top + art_h - 15, ax + lw, top + art_h), fill=RED)
    caps(ax + 5, top + art_h - 12, lead["tag"], 7.8, "#ffffff", lw - 10)

    hy = top + art_h + 6
    for line in lead["head"]:
        hsize = 20 if i == 0 else 18
        text(ax, hy, line, hsize, INK, DISPLAY, lw)
        hy += hsize + 2
    hy += 3
    hy, n = wrapped(ax, hy, lead["body"], 8.6, BODY, lw, 9.8, TEXT, max_lines=8)
    caps(ax, hy + 2, lead["credit"], 7, MUTED, lw)
    xl += lw + (12 if i < 2 else 0)
    assert hy + 10 < 456, (i, hy)

rule(458, width=2)

# ---------------------------------------------------------------- secondaries (462-556)
SECOND = [
    ("EUROPE", "Winter power pact holds through the first cold snap", "Grid sharing covered 4% of evening demand.", "#3a5a70"),
    ("ASIA", "Tokyo wages outrun prices for the first time since 2021", "Real pay rose 0.4% in October.", "#96323f"),
    ("AMERICAS", "Andes rail link clears its last pass", "Freight opens to 4.2m tonnes a year.", "#356154"),
    ("AFRICA", "Sahel solar grid powers six cities", "The first 220 MW phase entered service.", "#77602f"),
    ("OCEANIA", "Reef treaty adds a no-take zone", "31% of the shelf is now closed to fishing.", "#4a4f78"),
]
sec_y = 464
card_w = (W - 2 * M - 4 * 10) / 5
for i, (tag, head, summ, color) in enumerate(SECOND):
    cx = M + i * (card_w + 10)
    d.rectangle((cx, sec_y, cx + card_w, sec_y + 40), fill="#e8e2d4")
    iw, ih = card_w, 30
    ix, iy = cx, sec_y
    if i == 0:      # winter grid: pylon and snow
        d.polygon([(ix + iw * 0.3, iy + 28), (ix + iw * 0.5, iy + 4), (ix + iw * 0.7, iy + 28)], fill=color)
        d.line((ix + iw * 0.36, iy + 18, ix + iw * 0.64, iy + 18), fill="#e8e2d4", width=2)
        for k in range(4):
            d.ellipse((ix + 8 + k * 9, iy + 6 + (k % 2) * 7, ix + 11 + k * 9, iy + 9 + (k % 2) * 7), fill="#ffffff")
    elif i == 1:    # wages: rising bars and a coin
        for k, h in enumerate((8, 13, 18, 24)):
            d.rectangle((ix + 10 + k * 12, iy + 28 - h, ix + 18 + k * 12, iy + 28), fill=color)
        d.ellipse((ix + iw - 26, iy + 4, ix + iw - 8, iy + 22), fill=color)
        d.text((ix + iw - 22, iy + 7), "¥", font=font(DISPLAY, 11), fill="#f5f0e4")
    elif i == 2:    # rail: sleepers and a locomotive
        for k in range(6):
            d.line((ix + 8 + k * 10, iy + 10, ix + 6 + k * 10, iy + 28), fill=color, width=2)
        d.rectangle((ix + 14, iy + 26, ix + iw - 14, iy + 28), fill=color)
        d.rectangle((ix + 22, iy + 8, ix + 46, iy + 24), fill=color)
        d.rectangle((ix + 26, iy + 11, ix + 34, iy + 16), fill="#e8e2d4")
    elif i == 3:    # solar: sun over panels
        d.ellipse((ix + 8, iy + 2, ix + 22, iy + 16), fill=color)
        for k in range(3):
            d.polygon([(ix + 26 + k * 20, iy + 12), (ix + 44 + k * 20, iy + 12),
                       (ix + 40 + k * 20, iy + 26), (ix + 22 + k * 20, iy + 26)], fill=color)
    else:           # reef: water line, fish, coral
        d.line((ix + 6, iy + 10, ix + iw - 6, iy + 10), fill=color, width=2)
        d.polygon([(ix + 20, iy + 18), (ix + 34, iy + 12), (ix + 34, iy + 24)], fill=color)
        d.rectangle((ix + 34, iy + 16, ix + 44, iy + 20), fill=color)
        for k in range(3):
            d.line((ix + 8 + k * 6, iy + 28, ix + 10 + k * 6, iy + 16), fill=color, width=2)
    d.rectangle((cx, sec_y + 30, cx + card_w, sec_y + 40), fill=color)
    caps(cx + 4, sec_y + 31, tag, 6.8, "#ffffff", card_w - 8)
    hy, _ = wrapped(cx, sec_y + 44, head, 10, INK, card_w, 11.5, TEXT_B, max_lines=2)
    hy2, _ = wrapped(cx, hy + 1, summ, 7.8, MUTED, card_w, 9.2, TEXT, max_lines=2)
    assert hy2 < 556, hy2

rule(562, width=2)

# ---------------------------------------------------------------- map + also on (566-746)
map_y = 568
text(M, map_y, "WHERE IT HAPPENED", 10.5, INK, DISPLAY, 210)
mx, my, mw, mh = M, map_y + 16, 300, 162
d.rectangle((mx, my, mx + mw, my + mh), fill="#eae4d6", outline=RULE)
land = "#cfc6b2"
d.polygon([(mx + 14, my + 50), (mx + 36, my + 22), (mx + 78, my + 18), (mx + 98, my + 42),
           (mx + 82, my + 62), (mx + 54, my + 66), (mx + 40, my + 88), (mx + 18, my + 78)], fill=land)
d.polygon([(mx + 86, my + 88), (mx + 110, my + 100), (mx + 114, my + 134), (mx + 100, my + 156), (mx + 90, my + 122)], fill=land)
d.polygon([(mx + 132, my + 34), (mx + 186, my + 20), (mx + 244, my + 28), (mx + 288, my + 56),
           (mx + 264, my + 78), (mx + 212, my + 70), (mx + 188, my + 94), (mx + 158, my + 80)], fill=land)
d.polygon([(mx + 166, my + 88), (mx + 202, my + 90), (mx + 216, my + 126), (mx + 190, my + 150), (mx + 170, my + 122)], fill=land)
d.polygon([(mx + 242, my + 118), (mx + 274, my + 124), (mx + 282, my + 144), (mx + 250, my + 148)], fill=land)
pins = [(32, 56), (48, 38), (66, 34), (92, 54), (112, 92), (142, 46), (168, 38), (192, 54),
        (204, 102), (236, 68), (258, 34), (276, 134), (92, 126), (152, 114)]
for n, (px_, py_) in enumerate(pins[:8], 1):
    d.ellipse((mx + px_ - 7, my + py_ - 7, mx + px_ + 7, my + py_ + 7), fill=RED)
    d.text((mx + px_, my + py_ - 5), str(n), font=font(LABEL, 8.2), fill="#ffffff", anchor="ma")
caps(mx + 5, my + mh - 11, "numbers match the illustrated reports", 6.8, MUTED, mw - 10)

ax = M + mw + 18
aw = W - M - ax
text(ax, map_y, "ALSO ON FRIDAY", 10.5, INK, DISPLAY, aw)
ALSO = [
    ("Gaza", "tanks cross the Yellow Line in a rare raid"),
    ("Crimea", "the bridge is struck again; traffic halted"),
    ("Bengaluru", "Amazon pledges $7bn for Indian renewables"),
    ("La Paz", "Bolivia declares an El Niño emergency"),
    ("Berlin", "coalition agrees a 2027 defence budget"),
    ("Nairobi", "regional rail freight restarts after repairs"),
    ("Jakarta", "peatland fires fall by a third this month"),
    ("Manila", "storm shelters pass their first night drill"),
    ("Ottawa", "Arctic broadband reaches Nunavut"),
    ("Santiago", "copper talks avert a strike at the mine"),
    ("Brussels", "AI audit rules clear the parliament"),
    ("Seoul", "chip exports reach a yearly high"),
    ("Cairo", "a new subway line opens two months early"),
    ("Lagos", "port backlog clears after a week of delays"),
    ("Sydney", "heat code protects outdoor crews"),
    ("Geneva", "refugee appeal reaches two thirds of target"),
    ("Vienna", "energy agency trims its demand forecast"),
    ("Brasília", "indigenous fund gains independent oversight"),
    ("New York", "markets digest a steady Federal Reserve"),
    ("Doha", "mediators extend the truce draft by a week"),
    ("Paris", "food index falls for a third straight month"),
    ("Oslo", "ocean panel adopts shipping noise limits"),
]
assert len(ALSO) == 22
ALSO = ALSO[:20]
half = 10
col_b = ax + aw / 2 + 10
for i, (place, clause) in enumerate(ALSO):
    cx = ax if i < half else col_b
    row = i % half
    yy = map_y + 16 + row * 14
    f = font(TEXT_B, 8.4)
    lead_txt = f"{i + 9}  {place} "
    d.text((cx, yy), lead_txt, font=f, fill=INK)
    assert tw(lead_txt + clause, f) <= aw / 2 - 10, ("ALSO overflow", place, clause)
    d.text((cx + tw(lead_txt, f), yy), clause, font=font(TEXT, 8.4), fill=BODY)

rule(748, width=2)

# ---------------------------------------------------------------- briefs (752-962)
BRIEFS = [
    ("Warsaw", "Baltic patrols gain two ships."), ("Madrid", "Drought curbs ease after rain."),
    ("Beirut", "Port insurers restore cover."), ("Amman", "Water accord opens a pipeline."),
    ("Hanoi", "Metro line opens ahead of plan."), ("Dhaka", "Garment wage panel sets a floor."),
    ("Kathmandu", "Glacier sensors issue a first alert."), ("Beijing", "Consumer spending edges higher."),
    ("Singapore", "Port queues return to normal."), ("Mexico City", "Clean-bus tender draws six bids."),
    ("Lima", "Anchovy quota rises cautiously."), ("Havana", "Solar imports clear the harbour."),
    ("Accra", "Cocoa traceability goes live."), ("Cape Town", "Reservoirs hold above target."),
    ("Wellington", "Farm methane vote advances."),
    ("Canberra", "Bushfire season opens a month early."),
    ("Reykjavik", "Geothermal plant adds a third turbine."),
]
assert len(BRIEFS) == 17
text(M, 756, "BRIEFS", 10.5, RED, DISPLAY, 70)
caps(M + 54, 759, "the rest of the day, in one line each", 7.6, MUTED, 280)
rule(772)
starts = [M, 356, 684]
for sx in (344, 672):
    d.line((sx, 778, sx, 958), fill=RULE, width=1)
for i, (place, clause) in enumerate(BRIEFS):
    col, row = divmod(i, 6)
    x0, y0 = starts[col], 778 + row * 30
    d.text((x0, y0), place, font=font(TEXT_B, 9), fill=INK)
    wrapped(x0, y0 + 10, clause, 8.2, BODY, 300, 9.4, TEXT, max_lines=2)

rule(964, width=2)
caps(M, 971, "Sources: Reuters, AP, AFP, BBC, Al Jazeera · art and editing: the world desk", 7.2, MUTED, 700)
text(W - M, 970, "45 reports · 20 Nov 2026", 8, INK, TEXT_B, 210, anchor="ra")

assert 3 + len(SECOND) + len(ALSO) + len(BRIEFS) == 45, (len(ALSO), len(BRIEFS))
assert img.size == (W, H)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, "PNG", optimize=True, compress_level=9)
print(f"stories=45 png_bytes={os.path.getsize(out)}")
