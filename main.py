"""Passport of the Republic of Zarnovia (a country that does not exist).

Draws a complete open passport spread, 1024x1024, to /output/entry.png:
left page = data page (drawn portrait, fields, MRZ with real ICAO check
digits); right page = visa and arrival/departure stamps from the two
neighbouring countries, plus the telling paperwork detail: Zarnovia only
lets travellers through on a 72-hour mountain-transit permit.

All details agree with each other: the passport was issued 12 JUN 2024,
every stamp is after that date and before the 12 JUN 2034 expiry, and the
visa was issued by the Ostrana consulate on the day of the Ostrana entry
stamp. No network, Pillow only.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

CREAM = (246, 241, 227)
PAGE_EDGE = (214, 203, 175)
INK = (31, 42, 55)
NAVY = (30, 58, 95)
LABEL = (90, 107, 125)
FAINT = (168, 178, 190)
PHOTO_BG = (199, 211, 222)
SKIN = (232, 197, 160)
SKIN_SH = (214, 176, 138)
HAIR = (58, 42, 30)
JACKET = (38, 52, 74)
STAMP_BLUE = (31, 78, 156)
STAMP_PURPLE = (107, 63, 160)
STAMP_RED = (163, 51, 39)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Load a DejaVu font, falling back to Pillow's default bitmap font."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default()


F_TITLE = font("DejaVuSans-Bold.ttf", 19)
F_SUB = font("DejaVuSans-Bold.ttf", 15)
F_LABEL = font("DejaVuSans.ttf", 10)
F_VALUE = font("DejaVuSans-Bold.ttf", 15)
F_VALUE2 = font("DejaVuSans.ttf", 13)
F_MRZ = font("DejaVuSansMono-Bold.ttf", 16)
F_STAMP = font("DejaVuSansMono-Bold.ttf", 14)
F_STAMP_SM = font("DejaVuSansMono-Bold.ttf", 11)
F_VISA = font("DejaVuSans-Bold.ttf", 19)
F_VISA_BODY = font("DejaVuSans.ttf", 12)
F_NOTE = font("DejaVuSerif.ttf", 11)
F_NOTE_IT = font("DejaVuSerif.ttf", 11)
F_SIG = font("DejaVuSerif.ttf", 19)
F_SMALL = font("DejaVuSans.ttf", 9)


# ---------------------------------------------------------------- ICAO MRZ
def mrz_check(text):
    """ICAO 9303 check digit: weights 7, 3, 1; A=10 .. Z=35, '<'=0."""
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(text):
        if ch == "<":
            v = 0
        elif ch.isdigit():
            v = int(ch)
        else:
            v = ord(ch) - 55
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    """Two 44-char MRZ lines for holder MIRA KOVAC, doc ZN4829107."""
    line1 = "P<ZNVKOVAC<<MIRA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "ZN4829107"
    dob = "880314"
    exp = "340612"
    personal = "<" * 14
    body = (
        doc + mrz_check(doc)
        + "ZNV" + dob + mrz_check(dob)
        + "F" + exp + mrz_check(exp)
        + personal + mrz_check(personal)
    )
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- helpers
def spaced(text, gap=" "):
    """Fake letter-spacing for small-caps headers."""
    return gap.join(list(text.replace(" ", "   ")))


def guilloche(draw, box, color, waves=7, amp=5, step=9):
    """Fine sine-wave security lines across a rectangle."""
    x0, y0, x1, y1 = box
    for k in range(waves):
        yb = y0 + (k + 1) * (y1 - y0) / (waves + 1)
        pts = []
        x = x0
        while x <= x1:
            pts.append((x, yb + amp * math.sin((x - x0) / 46.0 + k)))
            x += step
        draw.line(pts, fill=color, width=1)


def coat_of_arms(draw, cx, cy, s):
    """Shield with three mountain peaks, a star and wavy rivers."""
    w, h = s, int(s * 1.18)
    x0, y0 = cx - w // 2, cy - h // 2
    # shield outline
    shield = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + int(h * 0.62)),
              (cx, y0 + h), (x0, y0 + int(h * 0.62))]
    draw.polygon(shield, fill=(232, 226, 205), outline=NAVY, width=2)
    # three peaks
    base = y0 + int(h * 0.66)
    draw.polygon([(x0 + 4, base), (x0 + int(w * 0.30), y0 + int(h * 0.22)),
                  (x0 + int(w * 0.52), base)], fill=NAVY)
    draw.polygon([(x0 + int(w * 0.34), base), (x0 + int(w * 0.58), y0 + int(h * 0.12)),
                  (x0 + int(w * 0.82), base)], fill=(70, 96, 130))
    draw.polygon([(x0 + int(w * 0.62), base), (x0 + int(w * 0.82), y0 + int(h * 0.30)),
                  (x0 + w - 4, base)], fill=NAVY)
    # star above the middle peak
    sx, sy, r = cx, y0 + int(h * 0.10), max(3, s // 14)
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    draw.polygon(star, fill=(176, 138, 44))
    # wavy rivers at the foot
    for j, yy in enumerate((base + 4, base + 9)):
        pts = [(x0 + 6 + t, yy + 2 * math.sin(t / 7.0 + j)) for t in range(0, w - 12, 4)]
        draw.line(pts, fill=(70, 96, 130), width=1)


def stamp_layer(text_lines, color, w, h, angle, font_main=F_STAMP, font_sm=F_STAMP_SM):
    """One ink stamp on its own RGBA layer, rotated, slightly uneven."""
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = layer.width // 2, layer.height // 2
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], radius=8,
                        outline=color + (215,), width=3)
    d.rounded_rectangle([25, 25, 15 + w, 15 + h], radius=6,
                        outline=color + (190,), width=1)
    y = 20 + 16
    for i, (txt, f) in enumerate(text_lines):
        d.text((cx, y), txt, font=f, fill=color + (225,), anchor="mm")
        y += 17 if i == 0 else 15
    return layer.rotate(angle, resample=Image.BICUBIC, expand=False)


def draw_portrait(draw, box):
    """Stylised engraved passport portrait of the holder, Mira Kovac."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=PHOTO_BG)
    # fine engraved horizontal lines
    for yy in range(y0 + 4, y1 - 4, 5):
        draw.line([(x0 + 2, yy), (x1 - 2, yy)], fill=(186, 199, 210), width=1)
    cx = (x0 + x1) // 2
    # shoulders / jacket
    draw.pieslice([cx - 78, y0 + h - 78, cx + 78, y0 + h + 60],
                  180, 360, fill=JACKET)
    draw.polygon([(cx - 46, y1), (cx - 14, y0 + 138), (cx + 14, y0 + 138),
                  (cx + 46, y1)], fill=(244, 244, 240))  # shirt V
    draw.polygon([(cx - 16, y0 + 140), (cx, y0 + 168), (cx + 16, y0 + 140)],
                 fill=(92, 40, 48))  # small tie
    # neck
    draw.rectangle([cx - 13, y0 + 108, cx + 13, y0 + 142], fill=SKIN_SH)
    # head
    draw.ellipse([cx - 34, y0 + 34, cx + 34, y0 + 116], fill=SKIN)
    # ears
    draw.ellipse([cx - 40, y0 + 66, cx - 30, y0 + 88], fill=SKIN)
    draw.ellipse([cx + 30, y0 + 66, cx + 40, y0 + 88], fill=SKIN)
    # hair: dark frame, centre part, locks down past the ears
    draw.pieslice([cx - 38, y0 + 22, cx + 38, y0 + 96], 180, 360, fill=HAIR)
    draw.polygon([(cx - 38, y0 + 60), (cx - 30, y0 + 34), (cx - 22, y0 + 58),
                  (cx - 30, y0 + 62)], fill=HAIR)
    draw.polygon([(cx + 38, y0 + 60), (cx + 30, y0 + 34), (cx + 22, y0 + 58),
                  (cx + 30, y0 + 62)], fill=HAIR)
    draw.rectangle([cx - 38, y0 + 58, cx - 31, y0 + 108], fill=HAIR)
    draw.rectangle([cx + 31, y0 + 58, cx + 38, y0 + 108], fill=HAIR)
    # brows
    draw.arc([cx - 24, y0 + 62, cx - 6, y0 + 74], 200, 340, fill=HAIR, width=2)
    draw.arc([cx + 6, y0 + 62, cx + 24, y0 + 74], 200, 340, fill=HAIR, width=2)
    # eyes
    for ex in (cx - 15, cx + 15):
        draw.ellipse([ex - 6, y0 + 74, ex + 6, y0 + 82], fill=(250, 250, 248))
        draw.ellipse([ex - 3, y0 + 75, ex + 3, y0 + 81], fill=(40, 32, 26))
    # nose
    draw.line([(cx, y0 + 82), (cx - 2, y0 + 96)], fill=SKIN_SH, width=2)
    draw.arc([cx - 5, y0 + 94, cx + 5, y0 + 102], 0, 180, fill=SKIN_SH, width=2)
    # mouth
    draw.arc([cx - 9, y0 + 104, cx + 9, y0 + 114], 15, 165, fill=(150, 80, 70), width=2)
    # cheek shading
    draw.arc([cx - 30, y0 + 88, cx - 12, y0 + 104], 90, 180, fill=SKIN_SH, width=1)
    draw.arc([cx + 12, y0 + 88, cx + 30, y0 + 104], 0, 90, fill=SKIN_SH, width=1)


def field(draw, x, y, label, value, value_font=F_VALUE):
    draw.text((x, y), label, font=F_LABEL, fill=LABEL)
    draw.text((x, y + 13), value, font=value_font, fill=INK)


# ---------------------------------------------------------------- spread
def build():
    img = Image.new("RGB", (W, H), (43, 47, 54))
    draw = ImageDraw.Draw(img)

    # two cream pages with a gutter shadow
    draw.rectangle([24, 24, 500, 1000], fill=CREAM, outline=PAGE_EDGE, width=2)
    draw.rectangle([524, 24, 1000, 1000], fill=CREAM, outline=PAGE_EDGE, width=2)
    draw.rectangle([500, 24, 524, 1000], fill=(120, 110, 92))
    draw.line([(512, 24), (512, 1000)], fill=(60, 54, 44), width=2)

    # ---------------- left page: data page ----------------
    guilloche(draw, (30, 30, 494, 994), (214, 222, 230), waves=16, amp=4)

    coat_of_arms(draw, 262, 78, 52)
    draw.text((262, 122), spaced("REPUBLIC OF ZARNOVIA"), font=F_TITLE,
              fill=NAVY, anchor="ma")
    draw.text((262, 150), spaced("PASSPORT  ·  PASSEPORT"), font=F_SUB,
              fill=INK, anchor="ma")
    draw.line([(48, 176), (476, 176)], fill=NAVY, width=2)
    draw.line([(48, 180), (476, 180)], fill=NAVY, width=1)

    # photo
    draw.rectangle([48, 196, 208, 376], outline=NAVY, width=2)
    draw_portrait(draw, (50, 198, 206, 374))
    draw.text((128, 384), "PHOTOGRAPH", font=F_SMALL, fill=LABEL, anchor="ma")

    # fields right of the photo
    fx = 232
    field(draw, fx, 196, "TYPE / TYPE", "P")
    field(draw, fx + 70, 196, "CODE / CODE", "ZNV")
    field(draw, fx + 150, 196, "PASSPORT No.", "ZN4829107")
    field(draw, fx, 246, "SURNAME / NOM", "KOVAC")
    field(draw, fx, 296, "GIVEN NAMES / PRÉNOMS", "MIRA")
    field(draw, fx, 346, "NATIONALITY / NATIONALITÉ", "ZARNOVIAN")
    field(draw, fx, 396, "DATE OF BIRTH / DATE DE NAISSANCE", "14 MAR 1988")
    field(draw, fx, 446, "PLACE OF BIRTH / LIEU DE NAISSANCE", "DRENOVAC")
    field(draw, fx, 496, "SEX / SEXE", "F")
    field(draw, fx, 546, "DATE OF ISSUE / DATE DE DÉLIVRANCE", "12 JUN 2024")
    field(draw, fx, 596, "DATE OF EXPIRY / DATE D'EXPIRATION", "12 JUN 2034")
    field(draw, fx, 646, "AUTHORITY / AUTORITÉ",
          "MINISTRY OF THE INTERIOR", F_VALUE2)
    draw.text((fx, 678), "DRENOVAC", font=F_VALUE2, fill=INK)

    # holder's signature under the photo
    draw.text((128, 716), "Mira Kovac", font=F_SIG, fill=(40, 52, 90),
              anchor="ma")
    draw.line([(58, 748), (198, 748)], fill=INK, width=1)
    draw.text((128, 754), "HOLDER'S SIGNATURE", font=F_SMALL, fill=LABEL,
              anchor="ma")

    # the telling detail, printed on the data page itself
    draw.text((262, 800), "—  MOUNTAIN TRANSIT  —", font=F_LABEL, fill=NAVY,
              anchor="ma")
    draw.text((262, 818),
              "Holder must carry a mountain transit permit",
              font=F_NOTE, fill=INK, anchor="ma")
    draw.text((262, 836),
              "when crossing the Drenovac Pass.",
              font=F_NOTE, fill=INK, anchor="ma")

    # machine-readable zone
    draw.rectangle([36, 868, 488, 988], fill=(238, 234, 220),
                   outline=NAVY, width=1)
    l1, l2 = mrz_lines()
    draw.text((262, 882), l1, font=F_MRZ, fill=INK, anchor="ma")
    draw.text((262, 916), l2, font=F_MRZ, fill=INK, anchor="ma")
    draw.text((262, 956), "P<ZNV  ·  ZARNOVIA  ·  ICAO 9303",
              font=F_SMALL, fill=LABEL, anchor="ma")

    # ---------------- right page: visas and stamps ----------------
    draw.text((762, 44), spaced("VISAS"), font=F_SUB, fill=NAVY, anchor="ma")
    draw.line([(548, 66), (976, 66)], fill=NAVY, width=2)

    # transit visa box
    draw.rectangle([548, 84, 976, 268], outline=NAVY, width=2)
    draw.rectangle([554, 90, 970, 262], outline=NAVY, width=1)
    draw.text((762, 104), "TRANSIT VISA", font=F_VISA, fill=NAVY, anchor="ma")
    draw.text((762, 132), "VALID FOR MOUNTAIN TRANSIT ONLY — 72 HOURS",
              font=F_VISA_BODY, fill=INK, anchor="ma")
    draw.text((762, 152), "SINGLE ENTRY VIA DRENOVAC PASS",
              font=F_VISA_BODY, fill=INK, anchor="ma")
    draw.text((762, 172), "No. TV-2025-0117", font=F_VISA_BODY, fill=INK,
              anchor="ma")
    draw.text((762, 192),
              "Issued 02 MAR 2025 — Ostrana Consulate, Drenovac",
              font=F_VISA_BODY, fill=INK, anchor="ma")
    draw.text((762, 220),
              "Fee stamp below. Not valid for stays beyond the pass.",
              font=F_VISA_BODY, fill=(90, 90, 90), anchor="ma")

    # fee stamp, stamped over the visa box corner
    fee = stamp_layer([("TRANSIT FEE", F_STAMP), ("40 ZN — PAID", F_STAMP)],
                      STAMP_RED, 150, 46, -14)
    img.paste(fee, (806, 236), fee)

    # faint watermark coat of arms behind the stamps
    wm = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    coat_of_arms(ImageDraw.Draw(wm), 150, 150, 190)
    alpha = wm.split()[3].point(lambda a: a * 30 // 255)
    wm.putalpha(alpha)
    img.paste(wm, (612, 560), wm)

    # arrival / departure stamps — all after the 12 JUN 2024 issue date
    stamps = [
        ([("BELVARIA", F_STAMP), ("ENTRY", F_STAMP_SM),
          ("03 SEP 2024", F_STAMP)], STAMP_BLUE, 170, 62, -9, (600, 300)),
        ([("BELVARIA", F_STAMP), ("EXIT", F_STAMP_SM),
          ("17 SEP 2024", F_STAMP)], STAMP_BLUE, 170, 62, 7, (800, 330)),
        ([("OSTRANA", F_STAMP), ("ENTRY", F_STAMP_SM),
          ("02 MAR 2025", F_STAMP)], STAMP_PURPLE, 170, 62, -6, (600, 430)),
        ([("OSTRANA", F_STAMP), ("EXIT", F_STAMP_SM),
          ("21 MAR 2025", F_STAMP)], STAMP_PURPLE, 170, 62, 9, (800, 460)),
        ([("BELVARIA", F_STAMP), ("ENTRY", F_STAMP_SM),
          ("08 AUG 2025", F_STAMP)], STAMP_RED, 170, 62, -4, (700, 580)),
    ]
    for lines, color, w, h, ang, pos in stamps:
        layer = stamp_layer(lines, color, w, h, ang)
        img.paste(layer, pos, layer)

    # bilingual note at the foot of the visa page
    draw = ImageDraw.Draw(img)
    draw.line([(548, 780), (976, 780)], fill=NAVY, width=1)
    draw.text((762, 796),
              "This passport is issued in Zarnovian and English.",
              font=F_NOTE, fill=INK, anchor="ma")
    draw.text((762, 814),
              "Ovaj pasoš izdaje se na zarnovskom i engleskom jeziku.",
              font=F_NOTE, fill=INK, anchor="ma")
    draw.text((762, 840),
              "The bearer is a citizen of the Republic of Zarnovia",
              font=F_NOTE, fill=INK, anchor="ma")
    draw.text((762, 858),
              "and is entitled to the protection of its consulates.",
              font=F_NOTE, fill=INK, anchor="ma")
    draw.text((762, 900), "No. ZN4829107  ·  32 PAGES  ·  ZARNOVIA",
              font=F_SMALL, fill=LABEL, anchor="ma")

    # ---------------- slight wear: creases and edge rub ----------------
    wear = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wear)
    wd.line([(24, 300), (500, 260)], fill=(120, 110, 88, 40), width=2)
    wd.line([(524, 700), (1000, 660)], fill=(120, 110, 88, 36), width=2)
    wd.line([(700, 24), (660, 1000)], fill=(255, 255, 255, 18), width=3)
    img.paste(wear, (0, 0), wear)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
