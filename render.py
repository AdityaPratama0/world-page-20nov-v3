#!/usr/bin/env python3
"""Render stories.json as a deterministic, single-page broadsheet."""
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 26
PAPER, INK, BODY = "#f5f0e4", "#15120e", "#2c2822"
MUTED, RULE, RED = "#6d655a", "#c3b8a4", "#8f1d22"
FD = Path("/usr/share/fonts/opentype/urw-base35")
DISPLAY = FD / "P052-Bold.otf"
ITALIC = FD / "P052-Italic.otf"
ROMAN = FD / "P052-Roman.otf"
TEXT = FD / "NimbusRoman-Regular.otf"
TEXT_B = FD / "NimbusRoman-Bold.otf"
LABEL = FD / "NimbusSansNarrow-Bold.otf"
ROOT = Path(__file__).resolve().parent

with (ROOT / "stories.json").open(encoding="utf-8") as handle:
    data = json.load(handle)

im = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(im)
_fonts = {}


def font(path, size):
    key = (str(path), size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(str(path), size)
    return _fonts[key]


def width(s, f):
    box = d.textbbox((0, 0), s, font=f)
    return box[2] - box[0]


def bottom(x, y, s, f):
    """Return the rendered glyph bottom, including the font's descent."""
    return d.textbbox((x, y), s, font=f)[3]


def check(s, f, limit):
    measured = width(s, f)
    assert measured <= limit, ("text overflow", s, measured, limit)
    return measured


def put(x, y, s, size, fill=INK, face=ROMAN, limit=None, anchor=None):
    f = font(face, size)
    measured = width(s, f)
    if limit is not None:
        check(s, f, limit)
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)
    return measured


def caps(x, y, s, size, fill=INK, limit=None, anchor=None):
    return put(x, y, s.upper(), size, fill, LABEL, limit, anchor)


def wrap(s, f, limit):
    words = s.split()
    assert words, ("empty text", s)
    lines, line = [], ""
    for word in words:
        check(word, f, limit)
        trial = f"{line} {word}".strip()
        if width(trial, f) <= limit:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    for line in lines:
        check(line, f, limit)
    return lines


def paragraph(x, y, s, size, fill, limit, leading, face=TEXT, max_lines=None):
    f = font(face, size)
    lines = wrap(s, f, limit)
    assert max_lines is None or len(lines) <= max_lines, ("too many lines", s, len(lines), max_lines)
    block_bottom = y
    for n, line in enumerate(lines):
        line_y = y + n * leading
        put(x, line_y, line, size, fill, face, limit)
        block_bottom = max(block_bottom, bottom(x, line_y, line, f))
    return block_bottom, len(lines)


def line_block(x, y, lines, size, fill, limit, leading, face):
    """Draw supplied lines and return their true bounding-box bottom."""
    f = font(face, size)
    block_bottom = y
    for n, line in enumerate(lines):
        line_y = y + n * leading
        put(x, line_y, line, size, fill, face, limit)
        block_bottom = max(block_bottom, bottom(x, line_y, line, f))
    return block_bottom


def rule(y, thick=1, x1=M, x2=W-M):
    d.line((x1, y, x2, y), fill=RULE, width=thick)


def band_end(bottom, next_rule, name):
    assert bottom < next_rule, ("band crosses rule", name, bottom, next_rule)


# Top strip, masthead, folio, deck.
d.rectangle((0, 0, W, 16), fill=INK)
caps(M, 3, "THE WORLD IN ONE DAY", 8, "white", 240)
caps(W-M, 3, "45 STORIES · EVERY CONTINENT · ONE DAY'S REPORTING", 8, "white", 430, "ra")
put(M, 20, "THE WORLD DESK", 52, INK, DISPLAY, 620)
put(W-M, 39, "All the world, one day at a time.", 12, MUTED, ITALIC, 320, "ra")
caps(W-M, 59, "FOUNDED 2023 · ONE SHEET, EVERY MORNING", 8, MUTED, 320, "ra")
band_end(79, 88, "masthead")
rule(88, 2)
caps(M, 93, data["volume"], 8.5, BODY, 220)
caps(W/2, 92, data["date_line"], 10.5, INK, 270, "ma")
caps(W-M, 93, data["edition"], 8.5, BODY, 260, "ra")
band_end(105, 108, "folio")
rule(108)
deck_end, _ = paragraph(M, 112, data["deck"], 11.5, RED, W-2*M, 15, ITALIC, 2)
band_end(deck_end, 150, "deck")
rule(150)

# Region index. Widths are proportional to measured label widths.
regions = data["regions"]
assert sum(item[1] for item in regions) == 45, ("region total", regions)
gap = 3
available = W - 2*M - gap*(len(regions)-1)
label_font = font(LABEL, 8)
needs = [width(f"{name.upper()} {count}", label_font) + 12 for name, count, _ in regions]
extra = available - sum(needs)
assert extra >= 0, ("region index overflow", needs, available)
x = M
for i, ((name, count, color), need) in enumerate(zip(regions, needs)):
    block = need + extra / len(regions)
    if i == len(regions)-1:
        block = W-M-x
    d.rectangle((x, 154, x+block, 172), fill=color)
    caps(x+6, 158, f"{name} {count}", 8, "white", block-12)
    x += block + gap
band_end(172, 176, "region index")

# Day in numbers.
rule(176)
caps(M, 180, "THE DAY IN NUMBERS", 7.2, MUTED, 180)
cell = (W-2*M)/5
assert len(data["stats"]) == 5
for i, (number, caption) in enumerate(data["stats"]):
    x = M+i*cell
    if i:
        d.line((x-7, 186, x-7, 212), fill=RULE)
    text_x = x+3
    put(text_x, 184, number, 17, INK, DISPLAY, cell-12)
    caps(text_x, 203, caption, 7.2, MUTED, cell-12)
band_end(212, 216, "numbers")
rule(216)


def lead_art(kind, x, y, w, h):
    if kind == "summit":
        colors = ["#d6deda", "#c9d4d0", "#bcc9c5", "#afbeb9"]
        for i, color in enumerate(colors):
            d.rectangle((x, y+i*h/4, x+w, y+(i+1)*h/4), fill=color)
        for cx in (x+w*.18, x+w*.5, x+w*.82):
            d.ellipse((cx-24, y+28, cx+24, y+76), fill="#596260")
        d.rectangle((x, y+67, x+w, y+h), fill="#343b39")
        for cx, color in zip((x+w*.2, x+w*.5, x+w*.8), ("#b63431", "#b63431", "#31577d")):
            d.rectangle((cx-9, y+64, cx+9, y+81), fill=color)
    elif kind == "court":
        d.rectangle((x, y, x+w, y+h), fill="#ddd5c5")
        d.polygon((x+25,y+28, x+w/2,y+5, x+w-25,y+28), fill="#9f927c")
        d.rectangle((x+25,y+28,x+w-25,y+36), fill="#aa9d87")
        for i in range(5):
            cx=x+42+i*(w-84)/4
            d.rectangle((cx,y+36,cx+10,y+h-8), fill="#c4baa7")
        d.line((x+w/2,y+14,x+w/2,y+62),fill="#665d50",width=2)
        d.line((x+w/2-22,y+26,x+w/2+22,y+26),fill="#665d50",width=2)
    elif kind == "cop":
        d.rectangle((x,y,x+w,y+h),fill="#d2dadd")
        d.ellipse((x+38,y+8,x+132,y+102),fill="#abbcc2")
        d.ellipse((x+58,y+28,x+112,y+82),outline="#81989f",width=2)
        d.rectangle((x+146,y+24,x+158,y+72),outline=RED,width=2)
        d.ellipse((x+141,y+65,x+163,y+87),fill=RED)
        for i in range(4):
            d.line((x+8,y+15+i*21,x+w-8,y+15+i*21),fill="#eef1f1",width=2)
    else:
        raise AssertionError(("unknown lead art", kind))


# Three lead reports.
assert len(data["leads"]) == 3
lead_widths = (388, 290, 290)
x = M
for i, (story, colw) in enumerate(zip(data["leads"], lead_widths)):
    y, art_h = 222, 96
    lead_art(story["art"], x, y, colw, art_h)
    d.rectangle((x, y+81, x+colw, y+96), fill=RED)
    caps(x+5, y+84, story["tag"], 7.8, "white", colw-10)
    cursor = y+101
    hsize = 20 if i == 0 else 18
    assert 1 <= len(story["head"]) <= 3
    headline_bottom = line_block(x, cursor, story["head"], hsize, INK, colw,
                                 hsize+1, DISPLAY)
    body_y = headline_bottom+5
    body_bottom, _ = paragraph(x, body_y, story["body"], 8.6, BODY, colw, 9.8, TEXT)
    credit_y = body_bottom+4
    caps(x, credit_y, story["credit"], 7, MUTED, colw)
    credit_bottom = bottom(x, credit_y, story["credit"].upper(), font(LABEL, 7))
    band_end(credit_bottom, 452, f"lead {i+1}")
    x += colw+12
rule(458, 2)


def secondary_art(i, x, y, w, color):
    d.rectangle((x,y,x+w,y+40), fill="#e8e2d4")
    if i == 0:
        d.polygon((x+w*.3,y+29,x+w*.5,y+3,x+w*.7,y+29),fill=color)
        d.line((x+w*.37,y+18,x+w*.63,y+18),fill=PAPER,width=2)
        for k in range(5):
            d.ellipse((x+8+k*13,y+5+(k%2)*7,x+11+k*13,y+8+(k%2)*7),fill="white")
    elif i == 1:
        for k,h in enumerate((8,13,19,25)):
            d.rectangle((x+9+k*12,y+29-h,x+17+k*12,y+29),fill=color)
        d.ellipse((x+w-28,y+4,x+w-8,y+24),fill=color)
        put(x+w-18,y+6,"¥",11,PAPER,DISPLAY,16,"ma")
    elif i == 2:
        for k in range(7):
            d.line((x+7+k*12,y+9,x+5+k*12,y+29),fill=color,width=2)
        d.rectangle((x+8,y+27,x+w-8,y+29),fill=color)
        d.rectangle((x+21,y+8,x+49,y+24),fill=color)
    elif i == 3:
        d.ellipse((x+8,y+2,x+22,y+16),fill=color)
        for k in range(3):
            d.polygon((x+25+k*23,y+13,x+44+k*23,y+13,x+40+k*23,y+27,x+21+k*23,y+27),fill=color)
    else:
        d.line((x+5,y+10,x+w-5,y+10),fill=color,width=2)
        d.polygon((x+18,y+19,x+34,y+12,x+34,y+26),fill=color)
        d.ellipse((x+31,y+15,x+47,y+23),fill=color)
        for k in range(3):
            d.line((x+8+k*7,y+29,x+11+k*7,y+17),fill=color,width=2)


# Five secondary cards.
assert len(data["secondaries"]) == 5
card_w=(W-2*M-40)/5
for i, (tag, headline, summary, color) in enumerate(data["secondaries"]):
    x=M+i*(card_w+10)
    secondary_art(i,x,464,card_w,color)
    d.rectangle((x,494,x+card_w,504),fill=color)
    caps(x+4,495,tag,6.8,"white",card_w-8)
    headline_bottom,_=paragraph(x,508,headline,10,INK,card_w,11.5,TEXT_B,2)
    summary_y=headline_bottom+4
    summary_bottom,_=paragraph(x,summary_y,summary,7.6,MUTED,card_w,9.2,TEXT,2)
    band_end(summary_bottom,562,f"secondary {i+1}: {headline}")
rule(562,2)

# Map panel.
put(M,568,"WHERE IT HAPPENED",10.5,INK,DISPLAY,220)
mx,my,mw,mh=M,584,300,162
d.rectangle((mx,my,mx+mw,my+mh),fill="#eae4d6",outline=RULE)
land="#cfc6b2"
polys=[[(14,50),(36,22),(78,18),(98,42),(82,62),(54,66),(40,88),(18,78)],
       [(86,88),(110,100),(114,134),(100,156),(90,122)],
       [(132,34),(186,20),(244,28),(288,56),(264,78),(212,70),(188,94),(158,80)],
       [(166,88),(202,90),(216,126),(190,150),(170,122)],
       [(242,118),(274,124),(282,144),(250,148)]]
for poly in polys:
    d.polygon([(mx+a,my+b) for a,b in poly],fill=land)
for n,(px,py) in enumerate(((32,56),(48,38),(68,34),(94,54),(112,92),(148,46),(178,38),(222,61)),1):
    d.ellipse((mx+px-7,my+py-7,mx+px+7,my+py+7),fill=RED)
    put(mx+px,my+py-5,str(n),8,"white",LABEL,12,"ma")
caps(mx+5,my+mh-11,"PINS MARK THE EIGHT ILLUSTRATED REPORTS",6.8,MUTED,mw-10)
band_end(my+mh,748,"map")

# Twenty one-line items, two columns.
also=data["also"]
assert len(also)==20
ax=M+mw+18
aw=W-M-ax
put(ax,568,"ALSO ON FRIDAY",10.5,INK,DISPLAY,aw)
colw=aw/2-10
also_divider=ax+aw/2+5
d.line((also_divider,584,also_divider,740),fill=RULE,width=1)
for i,(place,clause) in enumerate(also):
    x=ax if i<10 else ax+aw/2+10
    y=584+(i%10)*14
    prefix=f"{i+9}  {place} "
    total=width(prefix,font(TEXT_B,8.4))+width(clause,font(TEXT,8.4))
    assert total <= colw-10, ("also overflow", f"{prefix}{clause}", total, colw-10)
    put(x,y,prefix,8.4,INK,TEXT_B,colw)
    put(x+width(prefix,font(TEXT_B,8.4)),y,clause,8.4,BODY,TEXT,colw-width(prefix,font(TEXT_B,8.4)))
band_end(724,748,"also")
rule(748,2)

# Briefs in columns of 6, 6, 5.
briefs=data["briefs"]
assert len(briefs)==17
put(M,752,"BRIEFS",10.5,RED,DISPLAY,70)
caps(M+54,756,"THE REST OF THE DAY, IN ONE LINE EACH",7.6,MUTED,290)
rule(772)
starts=(M,356,684)
for divider in (344,672):
    d.line((divider,778,divider,958),fill=RULE,width=1)
brief_columns=(briefs[:6],briefs[6:12],briefs[12:])
column_bottoms=[]
for col,items in enumerate(brief_columns):
    last_bottom=778
    step=30 if len(items)==6 else 37.5
    for row,(city,clause) in enumerate(items):
        x,y=starts[col],778+row*step
        put(x,y,city,9,INK,TEXT_B,300)
        city_bottom=bottom(x,y,city,font(TEXT_B,9))
        clause_y=max(y+13,city_bottom+3)
        last_bottom,_=paragraph(x,clause_y,clause,8.2,BODY,300,9.4,TEXT,2)
        next_boundary=778+(row+1)*step if row+1<len(items) else 958
        band_end(last_bottom,next_boundary,f"brief {col+1}.{row+1}: {city} {clause}")
    column_bottoms.append(last_bottom)
assert max(column_bottoms)-min(column_bottoms) <= 8, ("brief column bottoms",column_bottoms)
rule(964,2)
caps(M,971,"SOURCES: REUTERS, AP, AFP, BBC, AL JAZEERA · ART AND EDITING: THE WORLD DESK",7.2,MUTED,720)
put(W-M,970,"45 reports · 20 Nov 2026",8,INK,TEXT_B,210,"ra")
band_end(982,1000,"footer")

story_count=3+len(data["secondaries"])+len(also)+len(briefs)
assert story_count==45, ("story count",story_count)
assert im.size==(1024,1024)
out=ROOT/"entry.png"
im.save(out,"PNG",optimize=True,compress_level=9)
print(f"{story_count} stories placed; {os.path.getsize(out)} bytes")
