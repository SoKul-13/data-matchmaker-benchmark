#!/usr/bin/env python
"""Render every row as a card image, plus the scale table and the 1-7 legend strip, for the Google Forms route.

    uv run python shared/scripts/06_render_row_images.py            # data/labels/forms_images/<row_id>.png + scale_table.png + scale_strip.png

A card shows the row's key fields as a two-column table (question, reference answer, the system's final answer highlighted), the
data table as a real grid, and the context as wrapped text (see label_render.py).  Upload the folder's contents to a Drive folder
named `labelling_images` (the name set in shared/forms/make_label_forms.gs); the form builder then shows the card on the row's page
and the scale table on the first page of every form.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_render import row_card, scale_image, scale_strip  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; OUT = LAB / "forms_images"


def main():
    if OUT.exists():
        for f in OUT.glob("*.png"): f.unlink()
    OUT.mkdir(exist_ok=True); n = 0
    scale_image(OUT / "scale_table.png"); scale_strip(OUT / "scale_strip.png")
    for f in ["labeller_sheet.csv", "pilot_30.csv"]:
        d = pd.read_csv(LAB / f, dtype=str).fillna("")
        for _, r in d.iterrows():
            row_card(r, OUT / f"{r.row_id}.png"); n += 1
    mb = sum(p.stat().st_size for p in OUT.glob("*.png")) / 1e6
    print(f"{n} row cards + scale_table.png + scale_strip.png -> {OUT.relative_to(ROOT)} ({mb:.0f} MB); upload to a Drive folder named 'labelling_images'")


if __name__ == "__main__":
    main()
