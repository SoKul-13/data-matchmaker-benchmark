#!/usr/bin/env python
"""Turn Google Forms response CSVs (built by shared/forms/make_label_forms.gs) back into a returned sheet.

    uv run python shared/scripts/05_forms_to_returned.py --labeller A responses/*.csv
    uv run python shared/scripts/05_forms_to_returned.py --labeller B --pilot responses_pilot/*.csv

Each response CSV has one line per submission and columns "Timestamp", "Your labeller letter", "<row_id> | utility",
"<row_id> | hedged", "<row_id> | note".  Keeps the labeller's latest submission per form, fills the canonical blind sheet
(data/labels/labeller_sheet.csv or pilot_30.csv; only the grader's assigned rows need to be present) and writes data/labels/returned/03_main_<L>.csv (or 02_pilot_<L>.csv).
Then run 03_label_agreement.py --check <L> as usual.
"""
from __future__ import annotations
import argparse, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; RET = LAB / "returned"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--labeller", required=True, help="the labeller's letter"); ap.add_argument("--pilot", action="store_true")
    ap.add_argument("csvs", nargs="+"); a = ap.parse_args()
    a.labeller = a.labeller.strip().upper()
    base = pd.read_csv(LAB / ("pilot_30.csv" if a.pilot else "labeller_sheet.csv"), dtype=str).set_index("row_id")
    got = {}
    for f in a.csvs:
        r = pd.read_csv(f, dtype=str); letter = [c for c in r.columns if c.lower().startswith("your labeller letter")]
        if not letter: print(f"{f}: no labeller-letter column, skipped"); continue
        r = r[r[letter[0]].str.strip().str.upper() == a.labeller]
        if r.empty: print(f"{f}: no submission from labeller {a.labeller}"); continue
        r = r.sort_values("Timestamp").iloc[-1]  # latest submission by this labeller for this form
        for c, v in r.items():
            m = re.fullmatch(r"(\w+) \| (utility|hedged|note)", str(c).strip())
            if m and pd.notna(v) and str(v).strip() != "": got.setdefault(m.group(1), {})[m.group(2)] = str(v).strip()
    for rid, vals in got.items():
        if rid in base.index:
            for k, v in vals.items(): base.loc[rid, k] = v
        else: print(f"unknown row id in responses: {rid}")
    if not a.pilot:
        mine = base.index[base.assigned_to.str.split().apply(lambda v: a.labeller in v)]; missing = [r for r in mine if r not in got]
    else: missing = [r for r in base.index if r not in got]
    out = RET / (f"02_pilot_{a.labeller}.csv" if a.pilot else f"03_main_{a.labeller}.csv"); RET.mkdir(exist_ok=True)
    base.reset_index().to_csv(out, index=False)
    print(f"wrote {out.relative_to(ROOT)}: {len(got)} rows filled from {len(a.csvs)} form file(s); {len(missing)} rows still blank" + (f": {missing[:10]}" if missing else ""))
    print(f"next: uv run python shared/scripts/03_label_agreement.py {'--pilot ' if a.pilot else ''}--check {a.labeller}")


if __name__ == "__main__":
    main()
