#!/usr/bin/env python
"""Turn Google Forms response CSVs (built by shared/forms/make_label_forms.gs) into one returned sheet per grader.

    uv run python shared/scripts/05_forms_to_returned.py responses/*.csv
    uv run python shared/scripts/05_forms_to_returned.py --pilot responses_pilot/*.csv
    uv run python shared/scripts/05_forms_to_returned.py responses/*.csv --alias "sam k=sk01" --alias "SK-01=sk01"

Each response CSV has one line per submission and columns "Timestamp", "Your grader ID", "<row_id> · Rating", "<row_id> · Hedged?",
"<row_id> · Note" (older forms: "<row_id> | rating [Final answer]" etc.).  Graders are whoever appears in "Your grader ID"; IDs are
compared in lower case with punctuation folded to "_".  For every grader the script keeps their latest submission per form, fills
the blind sheet (data/labels/labeller_sheet.csv or pilot_30.csv) and writes data/labels/returned/03_main_<id>.csv (02_pilot_<id>.csv).
Ratings are kept as 1-7 ("6", or "6 Correct, cosmetic defect" reduced to "6"); "Yes" / "No" become 1 / 0.
--alias merges a mistyped ID into the right one.  Then run 03_label_agreement.py --check all.
"""
from __future__ import annotations
import argparse, difflib, re, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_scale import rating  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; RET = LAB / "returned"
COL = re.compile(r"^\s*([RP]\d+)\s*[·|:\-]\s*(rating|hedged|note)\b", re.I)


def norm_id(x) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(x).strip().lower()).strip("_")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pilot", action="store_true"); ap.add_argument("--alias", action="append", default=[], metavar="TYPED=ID")
    ap.add_argument("csvs", nargs="+"); a = ap.parse_args()
    alias = {norm_id(k): norm_id(v) for k, v in (x.split("=", 1) for x in a.alias)}
    base = pd.read_csv(LAB / ("pilot_30.csv" if a.pilot else "labeller_sheet.csv"), dtype=str).set_index("row_id")
    got: dict[str, dict] = {}; forms: dict[str, set] = {}; typed: dict[str, set] = {}
    for f in a.csvs:
        r = pd.read_csv(f, dtype=str); idc = [c for c in r.columns if c.strip().lower().startswith(("your grader id", "your labeller letter"))]
        if not idc: print(f"{f}: no grader-ID column, skipped"); continue
        cols = [(c, COL.match(str(c))) for c in r.columns]; cols = [(c, m.group(1).upper(), m.group(2).lower()) for c, m in cols if m]
        r = r[r[idc[0]].notna()].copy(); r["_gid"] = r[idc[0]].map(lambda x: alias.get(norm_id(x), norm_id(x)))
        for raw, gid in zip(r[idc[0]], r["_gid"]): typed.setdefault(gid, set()).add(str(raw).strip())
        for gid, sub in r.groupby("_gid"):
            if not gid: continue
            last = sub.sort_values("Timestamp").iloc[-1]  # the grader's latest submission of this form
            forms.setdefault(gid, set()).add(Path(f).name)
            for c, rid, field in cols:
                v = last[c]
                if pd.isna(v) or str(v).strip() == "": continue
                val = str(v).strip()
                if field == "rating":
                    x = rating(val); val = val if x != x else str(int(x))   # off-scale values are kept as typed so --check reports them
                elif field == "hedged":
                    val = {"yes": "1", "no": "0"}.get(val.lower(), val); h = re.match(r"^[01]", val); val = h.group(0) if h else val
                got.setdefault(gid, {}).setdefault(rid, {})[field] = val
    if not got: raise SystemExit("no submissions found")
    RET.mkdir(exist_ok=True); pre = "02_pilot_" if a.pilot else "03_main_"
    print(f"{'grader':16s} {'answers':>8s} {'forms':>6s}  typed as")
    for gid in sorted(got):
        sheet = base.copy(); unknown = [rid for rid in got[gid] if rid not in sheet.index]
        for rid, vals in got[gid].items():
            if rid in sheet.index:
                for k, v in vals.items(): sheet.loc[rid, k] = v
        sheet.reset_index().to_csv(RET / f"{pre}{gid}.csv", index=False)
        print(f"{gid:16s} {sum('rating' in v for v in got[gid].values()):8d} {len(forms[gid]):6d}  {sorted(typed[gid])}" + (f"  ({len(unknown)} unknown row ids ignored)" if unknown else ""))
    ids = sorted(got); close = [(x, y) for i, x in enumerate(ids) for y in ids[i + 1:] if difflib.SequenceMatcher(None, x, y).ratio() >= 0.75 or x in y or y in x]
    if close: print("possibly the same person under two IDs (merge with --alias typed=id and re-run):", close)
    print(f"wrote {len(got)} file(s) to {RET.relative_to(ROOT)}; next: uv run python shared/scripts/03_label_agreement.py {'--pilot ' if a.pilot else ''}--check all")


if __name__ == "__main__":
    main()
