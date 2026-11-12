#!/usr/bin/env python
"""Turn what graders send back into one returned file per grader, identified by email address and stored under a code.

    uv run python shared/scripts/05_forms_to_returned.py responses/*.csv                    # Google Forms, main round
    uv run python shared/scripts/05_forms_to_returned.py --pilot responses_pilot/*.csv      # Google Forms, pilot
    uv run python shared/scripts/05_forms_to_returned.py --sheets inbox/*.xlsx              # spreadsheets sent back by graders
    uv run python shared/scripts/05_forms_to_returned.py --background background.csv inbox/00_BACKGROUND_FORM_*.xlsx
    uv run python shared/scripts/05_forms_to_returned.py responses/*.csv --alias "old@x.org=new@y.org"

Who is who.  A grader is identified by their email address everywhere: every Google Form records it ("Email Address" column of
the response file), a returned spreadsheet carries it in its file name (03_main_<address>.xlsx, 02_pilot_<address>.xlsx), and
the background form asks for it.  The address links a person's background, pilot and blocks.  This script replaces it at once
by a code (g01, g02, ... in order of first appearance).  The table address -> code is data/labels/grader_registry.csv, which
is git-ignored and is the only place an address is stored; returned files, graders.csv and everything downstream carry the
code only.  Keep the files graders send (the inbox, the downloaded responses) outside the repository.

Forms.  Each response CSV has one line per submission and columns "Timestamp", "Email Address", "<row_id> · Rating",
"<row_id> · Hedged?", "<row_id> · Note".  For every grader the script keeps their latest submission per form, fills the blind
sheet (data/labels/labeller_sheet.csv or pilot_30.csv) and writes data/labels/returned/03_main_<code>.csv (02_pilot_<code>.csv).
Ratings are kept as 1-7 ("6", or "6 Correct, cosmetic defect" reduced to "6"); "Yes" / "No" become 1 / 0.

--sheets copies returned spreadsheets into data/labels/returned/ under the grader's code.  Pilot or main is read from the file
name (02_pilot / 03_main); a newer file from the same grader replaces the older one.

--background takes the response CSV of the "Grader background and assignment" form and / or filled 00_BACKGROUND_FORM xlsx
files.  It writes one line per grader, latest answer, without the address, to data/labels/graders.csv (git-ignored: it
describes people), then lists graders who rated answers but filed no background form, and background forms with no ratings.

--alias "second@address=first@address" merges a person's second address into their first.  Afterwards run
03_label_agreement.py --check all.
"""
from __future__ import annotations
import argparse, difflib, re, shutil, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_scale import rating  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; RET = LAB / "returned"; REG = LAB / "grader_registry.csv"
COL = re.compile(r"^\s*([RP]\d+)\s*[·|:\-]\s*(rating|hedged|note)\b", re.I)
EMAILC = re.compile(r"^\s*(your\s+)?(e-?mail( address)?|username)\b", re.I)
ADDR = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")


def addr_in_name(path: Path) -> str:
    """The email address in a returned file's name, without the 02_pilot_ / 03_main_ / 00_BACKGROUND_FORM_ prefix."""
    stem = re.sub(r"^(02_pilot|03_main|00_BACKGROUND_FORM)[\s_-]*", "", path.stem, flags=re.I)
    m = ADDR.search(stem); return m.group(0).lower() if m else ""


def mask(e: str) -> str:
    at = e.find("@"); return (e[:2] + "***") if at < 1 else e[:min(3, at)] + "***" + e[at:]


class Who:
    """Email address -> grader code, kept in the private registry."""

    def __init__(self, aliases):
        self.alias = {k.strip().lower(): v.strip().lower() for k, v in aliases}
        bad = [x for kv in self.alias.items() for x in kv if not ADDR.fullmatch(x)]
        if bad: raise SystemExit(f"--alias takes two email addresses, second=first; not an address: {bad}")
        self.reg = pd.read_csv(REG, dtype=str) if REG.exists() else pd.DataFrame(columns=["grader", "email", "first_seen"])
        # an address merged into another by --alias gives up its own code (its earlier returned files are then stale)
        self.stale = sorted(self.reg.grader[self.reg.email.isin(list(self.alias))]); self.reg = self.reg[~self.reg.grader.isin(self.stale)].reset_index(drop=True)
        self.codes = dict(zip(self.reg.email, self.reg.grader)); self.new = 0; self.invalid = set()

    @staticmethod
    def column(df):
        em = [c for c in df.columns if EMAILC.match(str(c))]
        return em[0] if em and df[em[0]].notna().any() else None

    def key(self, value) -> str:
        e = str(value).strip().lower(); e = self.alias.get(e, e)
        if not ADDR.fullmatch(e):
            if e and e != "nan": self.invalid.add(mask(e))
            return ""
        if e not in self.codes:
            used = {int(m.group(1)) for m in (re.match(r"g(\d+)$", str(c)) for c in list(self.codes.values()) + self.stale) if m}
            self.codes[e] = f"g{(max(used) + 1 if used else 1):02d}"; self.new += 1
            self.reg.loc[len(self.reg)] = [self.codes[e], e, pd.Timestamp.now().strftime("%Y-%m-%d")]
        return self.codes[e]

    def save(self):
        if self.new or self.stale: self.reg.sort_values("grader").to_csv(REG, index=False)
        if self.new: print(f"{self.new} new grader code(s) added to {REG.relative_to(ROOT)} (private: never share or commit it)")
        if self.invalid: print("NOT AN EMAIL ADDRESS, submissions skipped (ask the grader, or fix the response file):", sorted(self.invalid))
        old = [f.name for c in self.stale for f in RET.glob(f"0[23]_*_{c}.*")]
        if self.stale: print(f"merged away by --alias: {self.stale}" + (f"; delete their stale files in {RET.relative_to(ROOT)}: {old}" if old else ""))
        loc = [(e, e.split("@")[0]) for e in self.reg.email]; flat = lambda x: re.sub(r"[^a-z0-9]", "", x)  # noqa: E731
        twin = [(mask(a), mask(b)) for i, (a, x) in enumerate(loc) for b, y in loc[i + 1:] if flat(x) == flat(y) or difflib.SequenceMatcher(None, x, y).ratio() >= 0.85]
        if twin: print('addresses that may be one person (merge with --alias "second@address=first@address"):', twin)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pilot", action="store_true", help="the response CSVs are from the pilot form")
    ap.add_argument("--alias", action="append", default=[], metavar="SECOND=FIRST", help="merge a person's second address into their first")
    ap.add_argument("--sheets", nargs="+", default=[], metavar="FILE", help="returned spreadsheets named 03_main_<address>.xlsx / 02_pilot_<address>.xlsx")
    ap.add_argument("--background", nargs="+", default=[], metavar="FILE", help="background form responses (.csv) and / or filled 00_BACKGROUND_FORM .xlsx files")
    ap.add_argument("csvs", nargs="*", help="Google Forms response CSVs"); a = ap.parse_args()
    if not (a.csvs or a.sheets or a.background): ap.error("give response CSVs, --sheets, --background, or a combination")
    who = Who([x.split("=", 1) for x in a.alias]); RET.mkdir(exist_ok=True)
    if a.csvs: convert(a, who)
    if a.sheets: sheets(a.sheets, who)
    if a.background: background(a.background, who)
    who.save()
    print(f"next: uv run python shared/scripts/03_label_agreement.py {'--pilot ' if a.pilot else ''}--check all")


def sheets(paths, who):
    """Spreadsheet route: file names carry the address; copy each file into returned/ under the grader's code."""
    for f in map(Path, paths):
        addr = addr_in_name(f); kind = re.search(r"(02_pilot|03_main)", f.name)
        if not addr or not kind or f.suffix.lower() not in (".xlsx", ".csv"):
            print(f"{f.name}: skipped (expected 03_main_<email address>.xlsx or 02_pilot_<email address>.xlsx)"); continue
        gid = who.key(addr)
        if not gid: continue
        for old in RET.glob(f"{kind.group(1)}_{gid}.*"): old.unlink()   # the newer file replaces the older one, whatever its type
        dst = RET / f"{kind.group(1)}_{gid}{f.suffix.lower()}"; shutil.copyfile(f, dst)
        print(f"{mask(addr):28s} -> {dst.relative_to(ROOT)}")


def _background_rows(path, who):
    """One dict per grader from a Forms response CSV, or from one filled 00_BACKGROUND_FORM workbook."""
    p = Path(path)
    if p.suffix.lower() == ".xlsx":
        t = pd.read_excel(p, dtype=str, header=0).fillna("")
        q, ans = t.columns[0], t.columns[-1]; d = {str(r[q]).strip(): str(r[ans]).strip() for _, r in t.iterrows() if str(r[q]).strip()}
        key = next((k for k in d if EMAILC.match(k)), None); addr = d.pop(key, "") if key else ""
        addr = addr or addr_in_name(p)
        gid = who.key(addr)
        if not gid: print(f"{p.name}: no email address in the form or the file name, skipped"); return []
        return [{"grader": gid, "Timestamp": pd.Timestamp(p.stat().st_mtime, unit="s").strftime("%Y/%m/%d %H:%M:%S"), "source": "spreadsheet", **d}]
    b = pd.read_csv(p, dtype=str); idc = who.column(b)
    if not idc: raise SystemExit(f"{path}: no email column. Is this the background form's response file, and does the form collect email addresses?")
    b = b[b[idc].notna()].copy(); b["grader"] = b[idc].map(who.key); b = b[b.grader != ""].drop(columns=[idc]); b["source"] = "form"
    return b.to_dict("records")


def background(paths, who):
    """Index the background answers by grader code and cross-check them against the returned rating files."""
    rows = [r for p in paths for r in _background_rows(p, who)]
    if not rows: print("background: nothing usable found"); return
    b = pd.DataFrame(rows).fillna("")
    if "Timestamp" in b.columns: b = b.sort_values("Timestamp")
    again = sorted(b.grader[b.grader.duplicated()].unique())
    b = b.drop_duplicates("grader", keep="last"); b = b[["grader"] + [c for c in b.columns if c != "grader"]].sort_values("grader")
    b.to_csv(LAB / "graders.csv", index=False)
    rated = {}
    for f in sorted(RET.glob("0[23]_*_*.*")):
        m = re.match(r"0[23]_(pilot|main)_(.+)\.(csv|xlsx)$", f.name)
        if m: rated.setdefault(m.group(2), set()).add(m.group(1))
    have = set(b.grader); print(f"background: {len(have)} grader(s) -> {(LAB / 'graders.csv').relative_to(ROOT)}")
    if again: print("  filed more than once (latest kept):", again)
    miss = sorted(set(rated) - have); idle = sorted(have - set(rated))
    if miss: print("  RATED BUT NO BACKGROUND FORM (ask them to fill it; look the address up in grader_registry.csv):", miss)
    if idle: print("  background form but no ratings returned yet:", idle)
    if not miss: print(f"  every grader with ratings ({len(rated)}) has a background form")


def convert(a, who):
    base = pd.read_csv(LAB / ("pilot_30.csv" if a.pilot else "labeller_sheet.csv"), dtype=str).set_index("row_id")
    got: dict[str, dict] = {}; forms: dict[str, set] = {}; seen: dict[str, set] = {}
    for f in a.csvs:
        r = pd.read_csv(f, dtype=str); idc = who.column(r)
        if not idc: print(f"{f}: NO EMAIL COLUMN, skipped. The form must collect email addresses (Settings > Responses), see checkEmailMode()"); continue
        cols = [(c, COL.match(str(c))) for c in r.columns]; cols = [(c, m.group(1).upper(), m.group(2).lower()) for c, m in cols if m]
        r = r[r[idc].notna()].copy(); r["_gid"] = r[idc].map(who.key)
        for raw, gid in zip(r[idc], r["_gid"]): seen.setdefault(gid, set()).add(mask(str(raw).strip().lower()))
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
    if not got: print("no submissions found in the response files"); return
    pre = "02_pilot_" if a.pilot else "03_main_"
    print(f"{'grader':8s} {'answers':>8s} {'forms':>6s}  address")
    for gid in sorted(got):
        sheet = base.copy(); unknown = [rid for rid in got[gid] if rid not in sheet.index]
        for rid, vals in got[gid].items():
            if rid in sheet.index:
                for k, v in vals.items(): sheet.loc[rid, k] = v
        for old in RET.glob(f"{pre}{gid}.*"): old.unlink()
        sheet.reset_index().to_csv(RET / f"{pre}{gid}.csv", index=False)
        print(f"{gid:8s} {sum('rating' in v for v in got[gid].values()):8d} {len(forms[gid]):6d}  {sorted(seen[gid])}" + (f"  ({len(unknown)} unknown row ids ignored)" if unknown else ""))
    print(f"wrote {len(got)} file(s) to {RET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
