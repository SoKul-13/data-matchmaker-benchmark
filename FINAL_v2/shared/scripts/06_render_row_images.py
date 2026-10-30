#!/usr/bin/env python
"""Render each row's table and context to a PNG in a monospace font, for the Google Forms route.

    uv run python shared/scripts/06_render_row_images.py            # data/labels/forms_images/<row_id>.png for the main sheet and the pilot

Upload the folder's contents to a Drive folder named `labelling_images` (the name set in shared/forms/make_label_forms.gs); the form
builder then shows the image on the row's page above the record-style text.  Rows with neither table nor context get no image.
"""
from __future__ import annotations
from pathlib import Path
import textwrap
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; OUT = LAB / "forms_images"
FONT_CANDIDATES = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf", "/Library/Fonts/Courier New.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
WIDTH_CHARS, FONT_PX, MAX_LINES = 110, 15, 120


def font():
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            try: return ImageFont.truetype(f, FONT_PX)
            except OSError: pass
    return ImageFont.load_default()


def render(text: str, path: Path, fnt):
    lines = []
    for ln in text.split("\n"):
        lines.extend(textwrap.wrap(ln, WIDTH_CHARS, replace_whitespace=False, drop_whitespace=False) or [""])
    if len(lines) > MAX_LINES: lines = lines[:MAX_LINES] + [f"[... {len(lines) - MAX_LINES} more lines; see the spreadsheet ...]"]
    cw = fnt.getlength("M"); lh = int(FONT_PX * 1.35)
    img = Image.new("RGB", (int(cw * WIDTH_CHARS) + 40, lh * len(lines) + 40), "white"); d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines): d.text((20, 20 + i * lh), ln, fill="black", font=fnt)
    img.save(path, optimize=True)


def main():
    OUT.mkdir(exist_ok=True); fnt = font(); n = 0
    for f in ["labeller_sheet.csv", "pilot_30.csv"]:
        d = pd.read_csv(LAB / f, dtype=str).fillna("")
        for _, r in d.iterrows():
            parts = [p for p in [r.table, r.context] if p.strip()]
            if not parts: continue
            render("\n\n".join(parts), OUT / f"{r.row_id}.png", fnt); n += 1
    print(f"{n} images -> {OUT.relative_to(ROOT)} (upload to a Drive folder named 'labelling_images')")


if __name__ == "__main__":
    main()
