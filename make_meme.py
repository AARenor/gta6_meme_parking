#!/usr/bin/env python3
"""Rebuild the Vice City parking citation meme from make.fun's press kit.

The joke lives in the paperwork: a loading-zone ticket written thirteen years
after the car was left on Ocean Drive, with the fine paid by the owner's AI
agent out of a make.fun bounty. Everything is drawn with Pillow from the brand
files, at 1080x1350, so the picture can be rebuilt from source at any time.

    python3 make_meme.py --out meme.png --press-kit <folder> --fonts <folder> --measure

The press kit and fonts are read, never modified; the mark is placed as it
ships (only trimmed of transparent padding and scaled uniformly).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 64

INK = (25, 20, 25)
SOFT = (96, 88, 94)
HAIR = (211, 204, 208)
PAPER = (247, 244, 239)
MAGENTA = (188, 12, 124)

# Section anchors, so the render and the audit cannot drift apart.
STAMP = (604, 516, 1016, 900)
REMARKS_RULE = 918
FOOTER_RULE = 1170

# The calendar does the arithmetic; nothing here is a made-up figure.
PARKED_SINCE = date(2013, 9, 17)  # GTA V's launch day
ISSUED = date(2026, 11, 21)
DAYS_PARKED = (ISSUED - PARKED_SINCE).days
BASE_FINE = 65.00
METER_RATE = 0.25
METER_FEE = round(DAYS_PARKED * METER_RATE, 2)
TOTAL_DUE = round(BASE_FINE + METER_FEE, 2)


def money(value: float) -> str:
    return f"${value:,.2f}"


def lum(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


@dataclass
class Block:
    name: str
    box: tuple[int, int, int, int]
    ink: tuple[int, int, int]
    size: int


class Sheet:
    """A paper sheet that remembers where every mark landed."""

    def __init__(self, bg: tuple[int, int, int]) -> None:
        self.image = Image.new("RGB", (W, H), bg)
        self.draw = ImageDraw.Draw(self.image)
        self.blocks: list[Block] = []
        self._fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}

    def font(self, path: Path, size: int) -> ImageFont.FreeTypeFont:
        key = (str(path), size)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(str(path), size)
        return self._fonts[key]

    def text(
        self,
        name: str,
        xy: tuple[float, float],
        body: str,
        font: ImageFont.FreeTypeFont,
        fill: tuple[int, int, int],
        tracking: float = 0.0,
        align: str = "left",
    ) -> tuple[int, int, int, int]:
        x, y = xy
        if align != "left":
            width = sum(font.getlength(ch) for ch in body) + tracking * max(len(body) - 1, 0)
            x = x - width if align == "right" else x - width / 2
        box = self.draw.textbbox((x, y), body, font=font)
        if tracking:
            cursor = x
            for ch in body:
                self.draw.text((cursor, y), ch, font=font, fill=fill)
                cursor += font.getlength(ch) + tracking
        else:
            self.draw.text((x, y), body, font=font, fill=fill)
        self.blocks.append(Block(name, box, fill, font.size))
        return box

    def rule(self, y: int, thickness: int = 1, colour: tuple[int, int, int] = HAIR,
             x0: int = MARGIN, x1: int = W - MARGIN) -> None:
        self.draw.rectangle([x0, y, x1, y + thickness - 1], fill=colour)

    def dashes(self, y: int, x0: int = MARGIN, x1: int = W - MARGIN,
               dash: int = 12, gap: int = 10, colour: tuple[int, int, int] = HAIR) -> None:
        x = x0
        while x < x1:
            self.draw.rectangle([x, y, min(x + dash, x1), y + 1], fill=colour)
            x += dash + gap

    def paste_mark(self, name: str, path: Path, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        """Trim the transparent margin, then scale uniformly into the box."""
        mark = Image.open(path).convert("RGBA")
        bounds = mark.getbbox()
        if bounds:
            mark = mark.crop(bounds)
        slot_w, slot_h = box[2] - box[0], box[3] - box[1]
        scale = min(slot_w / mark.width, slot_h / mark.height)
        size = (max(1, round(mark.width * scale)), max(1, round(mark.height * scale)))
        mark = mark.resize(size, Image.LANCZOS)
        left = box[0] + (slot_w - size[0]) // 2
        top = box[1] + (slot_h - size[1]) // 2
        self.image.paste(mark, (left, top), mark)
        placed = (left, top, left + size[0], top + size[1])
        self.blocks.append(Block(name, placed, MAGENTA, size[1]))
        return placed


def dotted(draw: ImageDraw.ImageDraw, y: int, x0: int, x1: int, step: int = 11) -> None:
    for x in range(x0, x1 - 2, step):
        draw.point((x, y), fill=(150, 142, 148))


def build(press_kit: Path, fonts: Path) -> tuple[Image.Image, Sheet]:
    sheet = Sheet(PAPER)
    d = sheet.draw

    bold = lambda s: sheet.font(fonts / "Inter-Bold.ttf", s)
    semi = lambda s: sheet.font(fonts / "Inter-SemiBold.ttf", s)
    med = lambda s: sheet.font(fonts / "Inter-Medium.ttf", s)
    mono = lambda s: sheet.font(fonts / "JetBrainsMono-Bold.ttf", s)

    # ---------- letterhead ----------
    sheet.text("city", (MARGIN, 52), "CITY OF VICE CITY", bold(30), INK, tracking=5)
    sheet.text("citation-no", (W - MARGIN, 58), "CITATION NO. VC-13-0917", semi(17), INK, tracking=1, align="right")
    sheet.text("department", (MARGIN, 93), "DEPARTMENT OF PARKING ENFORCEMENT · LEONIDA", semi(16), SOFT, tracking=2)
    sheet.text("issued", (W - MARGIN, 93), "ISSUED 21 NOV 2026", semi(16), SOFT, tracking=1, align="right")
    sheet.rule(122, 3, INK)

    sheet.text("title", (MARGIN, 132), "PARKING CITATION", bold(72), INK, tracking=1)
    sheet.text("subtitle", (MARGIN, 214), "OVERTIME METER · LOADING ZONE · OCEAN DRIVE", semi(17), SOFT, tracking=2)
    sheet.rule(242, 1)

    # ---------- ruled form ----------
    label_size, value_size = 16, 38
    rows = [
        (250, "VEHICLE", "white Infernus", "PLATE", "LUCIA-6"),
        (320, "OWNER", "Jason & Lucia", "PARKED SINCE · GTA V LAUNCH", "17 SEP 2013"),
        (390, "METER", "unfed since 2013", None, None),
        (460, "LOCATION", "Ocean Drive & 8th, Vice City, Leonida", None, None),
    ]
    for index, (y, label, value, label2, value2) in enumerate(rows):
        sheet.text(f"label-{label}", (MARGIN, y), label, semi(label_size), SOFT, tracking=2)
        sheet.text(f"value-{label}", (MARGIN, y + 22), value, semi(value_size), INK)
        if label2 and value2:
            sheet.text(f"label-{label2}", (640, y), label2, semi(label_size), SOFT, tracking=2)
            sheet.text(f"value-{label2}", (640, y + 22), value2, semi(value_size), INK)
        if index < len(rows) - 1:
            sheet.rule(y + 68, 1)

    # ---------- payment stub ----------
    sheet.dashes(544, MARGIN, 588)
    sheet.text("stub-head", (MARGIN, 550), "PAYMENT STUB — DETACH AND KEEP", semi(14), SOFT, tracking=3)

    charges = [
        ("BASE FINE", money(BASE_FINE), False),
        (f"{DAYS_PARKED:,} DAYS @ $0.25", money(METER_FEE), False),
        ("WAITING FOR GTA VI", "$0.00", False),
        ("TOTAL DUE", money(TOTAL_DUE), True),
    ]
    y = 580
    for label, amount, strong in charges:
        size = 27 if strong else 24
        f = mono(size) if strong else semi(size)
        if strong:
            sheet.rule(y - 10, 2, INK, MARGIN, 568)
        box = sheet.text(f"charge-{label}", (MARGIN, y), label, f, INK)
        amount_font = mono(32)
        amount_box = d.textbbox((0, 0), amount, font=amount_font)
        width = amount_box[2] - amount_box[0]
        sheet.text(f"amount-{label}", (568 - width, y - (4 if strong else 2)), amount, amount_font, INK)
        dotted(d, y + size + 6, box[2] + 12, 568 - width - 12)
        y += 48

    # ---------- paid stamp (the ghost is the clerk) ----------
    sx0, sy0, sx1, sy1 = STAMP
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=10, outline=MAGENTA, width=5)
    d.rounded_rectangle([sx0 + 10, sy0 + 10, sx1 - 10, sy1 - 10], radius=6, outline=MAGENTA, width=2)
    sheet.text("stamp-paid", ((sx0 + sx1) / 2, sy0 + 18), "PAID", bold(80), MAGENTA, align="center")
    sheet.paste_mark("mark", press_kit / "mark-1024.png", (sx0 + 96, sy0 + 129, sx1 - 96, sy0 + 304))
    sheet.text("stamp-name", ((sx0 + sx1) / 2, sy0 + 316), "make.fun", bold(47), INK, align="center")

    # ---------- payment ----------
    sheet.text("paid-by", (MARGIN, 768), "PAID BY THE OWNER'S AI AGENT", bold(30), MAGENTA, tracking=1)
    sheet.text("paid-note", (MARGIN, 810), "make.fun bounty payout. The agent earned it.", med(21), SOFT)

    # ---------- the line that lands it ----------
    sheet.rule(REMARKS_RULE, 3, INK)
    sheet.text("remarks-label", (MARGIN, 930), "OFFICER'S REMARKS", semi(15), SOFT, tracking=3)
    sheet.text("remarks-small", (MARGIN, 956), "THIRTEEN YEARS LATER", semi(21), MAGENTA, tracking=4)
    sheet.text("punch-1", (MARGIN - 3, 984), "GTA VI LOADED.", bold(74), INK)
    sheet.text("punch-2", (MARGIN - 3, 1066), "THE CAR DIDN'T.", bold(74), INK)

    # ---------- footer ----------
    sheet.rule(FOOTER_RULE, 1)
    for x in range(MARGIN, W - MARGIN, 16):
        d.line([x, 1182, x + 8, 1182], fill=(182, 174, 179), width=2)
    sheet.paste_mark("lockup", press_kit / "lockup-2400.png", (MARGIN, 1192, MARGIN + 380, 1296))
    sheet.text("fine-print", (MARGIN, 1302), "FORM VC-13 · CITY OF VICE CITY · PAGE 1 OF 1", semi(13), SOFT, tracking=2)

    tagline = [
        "People and their AI agents",
        "win real money on make.fun.",
        "This citation was paid from one.",
    ]
    ty = 1198
    for line in tagline:
        sheet.text(f"tagline-{ty}", (W - MARGIN, ty), line, semi(26), INK, align="right")
        ty += 32

    return sheet.image, sheet


def measure(sheet: Sheet, image: Image.Image) -> None:
    def block(name: str) -> Block:
        for b in sheet.blocks:
            if b.name == name:
                return b
        raise KeyError(name)

    p1, p2 = block("punch-1"), block("punch-2")
    top = min(p1.box[1], p2.box[1])
    bottom = max(p1.box[3], p2.box[3])
    height = bottom - top
    ratio = contrast(p1.ink, PAPER)
    mark = block("mark")
    mark_h = mark.box[3] - mark.box[1]
    lock = block("lockup")
    name = block("stamp-name")

    view = 480 / 1350  # the judge's view: a 4:5 picture fitted in 768x480
    side = 480 / 1080  # a 480 px square shrink

    print("image            :", image.size, image.mode)
    print("punchline        : 'GTA VI LOADED. THE CAR DIDN'T.'")
    print("  bbox           :", (min(p1.box[0], p2.box[0]), top, max(p1.box[2], p2.box[2]), bottom))
    print("  height         :", height, "px; two lines of", p1.size, "px")
    print("  ink / behind   :", p1.ink, "on", PAPER)
    print("  luminance      : %.4f vs %.4f, contrast %.1f:1" % (lum(p1.ink), lum(PAPER), ratio))
    print("  at 480 square  : %.1f px tall" % (height * side))
    print("  in judge view  : %.1f px tall (384x480)" % (height * view))
    print("make.fun mark    :", mark_h, "px tall, %0.1f%% of the shorter side" % (100 * mark_h / min(W, H)))
    print("  at 480 square  : %.1f px tall" % (mark_h * side))
    print("  in judge view  : %.1f px tall" % (mark_h * view))
    print("stamp wordmark   :", name.size, "px text; %.1f px in judge view" % (name.size * view))
    print("footer lockup    : %d px tall, %d px wide; %.1f px tall in judge view"
          % (lock.box[3] - lock.box[1], lock.box[2] - lock.box[0], (lock.box[3] - lock.box[1]) * view))
    print("lowest mark     :", max(b.box[3] for b in sheet.blocks), "of", H)

    for b in sheet.blocks:
        if b.box[0] < 0 or b.box[1] < 0 or b.box[2] > W or b.box[3] > H:
            print("OUT OF PAGE     :", b.name, b.box)

    collisions = []
    for i, a in enumerate(sheet.blocks):
        for b in sheet.blocks[i + 1:]:
            ox = min(a.box[2], b.box[2]) - max(a.box[0], b.box[0])
            oy = min(a.box[3], b.box[3]) - max(a.box[1], b.box[1])
            if ox > 2 and oy > 2:
                collisions.append((a.name, b.name, ox, oy))
    print("collisions      :", collisions if collisions else "none")

    print("clearances      :")
    print("  punchline to footer rule :", FOOTER_RULE - bottom, "px")
    print("  stamp box                : y %d-%d; mark y %d-%d, pad above %d px, below %d px"
          % (STAMP[1], STAMP[3], mark.box[1], mark.box[3], mark.box[1] - STAMP[1], STAMP[3] - mark.box[3]))
    print("  remarks rule to stamp    :", REMARKS_RULE - STAMP[3], "px")

    print("verdicts        :")
    print("  punchline readable at 480 px:", "yes" if height * view >= 18 else "NO")
    print("  ghost readable at 480 px     :", "yes" if mark_h * view >= 45 else "NO")
    print("  contrast >= 4.5:1            :", "yes" if ratio >= 4.5 else "NO")


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=here / "meme.png")
    parser.add_argument("--press-kit", type=Path, required=True,
                        help="make.fun press kit folder (mark-1024.png, lockup-2400.png)")
    parser.add_argument("--fonts", type=Path, required=True,
                        help="folder with Inter-Bold.ttf, Inter-SemiBold.ttf, Inter-Medium.ttf and JetBrainsMono-Bold.ttf")
    parser.add_argument("--measure", action="store_true", help="print legibility numbers for the render")
    args = parser.parse_args()

    image, sheet = build(args.press_kit, args.fonts)
    image.save(args.out, "PNG", optimize=True)
    print("wrote", args.out, image.size)
    if args.measure:
        measure(sheet, image)


if __name__ == "__main__":
    main()
