#!/usr/bin/env python
"""Build the hand-off folder for each labeller: everything they need to see, and nothing else.

    uv run python shared/scripts/04_make_labeller_handoff.py

Reads data/labels/{pilot_30,labeller_sheet,assignments}.csv (from 02_make_label_sample.py) and notes/LABELLING_GUIDE_FOR_LABELLERS.md.
Writes data/labels/handoff/grader_kit/ and grader_kit.zip, the ONE kit every grader receives:

    00_START_HERE_WALKTHROUGH.html / .md   the step-by-step procedure (from notes/WALKTHROUGH_LABELLERS.md)
    01_LABELLING_GUIDE.html / .md    the grading rules (HTML is self-contained and printable)
    02_pilot.xlsx / .csv             the 30-row calibration pilot (everyone grades all of it)
    03_main.xlsx / .csv              the main sheet, all rows; `assigned_to` lists the graders who own each row; a grader filters to their letter

The .xlsx sheets have drop-down validation on `utility` and `hedged`, a frozen header, wrapped text and the three columns to fill
highlighted; the .csv is the same content for anyone who prefers a plain file.  Returned files go in data/labels/returned/ and are
read by 03_label_agreement.py (xlsx or csv).  The master files that name the model are never copied here.
"""
from __future__ import annotations
import html, re, shutil
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; HAND = LAB / "handoff"
GUIDE = ROOT / "notes" / "LABELLING_GUIDE_FOR_LABELLERS.md"; WALK = ROOT / "notes" / "WALKTHROUGH_LABELLERS.md"
FILL = ["utility", "hedged", "note"]
WIDTH = {"row_id": 8, "assigned_to": 11, "task_family": 22, "dataset_description": 24, "answer_type": 10, "question": 50, "context": 50, "table": 50, "choices": 24,
         "gold_answer": 28, "accepted_alternatives": 20, "gold_is_a_list": 12, "model_final_answer": 32, "model_full_reply": 50, "utility": 9, "hedged": 9, "note": 24}
XL_MAX = 32000


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return t


def md_to_html(md: str, title: str) -> str:
    lines = md.splitlines(); out = []; i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "): out.append(f"<h1>{inline(ln[2:])}</h1>"); i += 1; continue
        if ln.startswith("## "): out.append(f"<h2>{inline(ln[3:])}</h2>"); i += 1; continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            th = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>"); continue
        if ln.startswith("* "):
            items = []
            while i < len(lines) and lines[i].startswith("* "): items.append(lines[i][2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
        if re.match(r"\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i]): items.append(re.sub(r"^\d+\. ", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>"); continue
        if ln.strip(): out.append(f"<p>{inline(ln)}</p>")
        i += 1
    css = """body{font:16px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#1a1a1a}
h1{font-size:1.7rem}h2{margin-top:2rem;border-bottom:1px solid #ccc;padding-bottom:.2rem}table{border-collapse:collapse;width:100%;margin:.8rem 0;font-size:.92rem}
th,td{border:1px solid #bbb;padding:.35rem .5rem;vertical-align:top;text-align:left}th{background:#eef2f7}tbody tr:nth-child(even){background:#fafafa}
code{background:#f1f1f1;padding:.05rem .3rem;border-radius:3px;font-size:.9em}li{margin:.2rem 0}@media print{body{font-size:12px;max-width:none}h2{page-break-after:avoid}}"""
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{css}</style></head><body>{''.join(out)}</body></html>"


def write_xlsx(df: pd.DataFrame, path: Path, sheet: str):
    wb = Workbook(); ws = wb.active; ws.title = sheet
    cols = list(df.columns); ws.append(cols)
    for _, r in df.iterrows():
        row = []
        for c in cols:
            v = "" if pd.isna(r[c]) else str(r[c])
            if len(v) > XL_MAX: v = v[:XL_MAX - 60] + "\n[... cut: see the .csv for the full text ...]"
            row.append(v)
        ws.append(row)
    hdr = Font(bold=True); fill_hdr = PatternFill("solid", fgColor="DDE6F0"); fill_edit = PatternFill("solid", fgColor="FFF4CC")
    for j, c in enumerate(cols, 1):
        cell = ws.cell(1, j); cell.font = hdr; cell.fill = fill_hdr
        ws.column_dimensions[get_column_letter(j)].width = WIDTH.get(c, 16)
    n = len(df) + 1
    for j, c in enumerate(cols, 1):
        for i in range(2, n + 1):
            ws.cell(i, j).alignment = Alignment(wrap_text=True, vertical="top")
            if c in FILL: ws.cell(i, j).fill = fill_edit
    for i in range(2, n + 1): ws.row_dimensions[i].height = 110
    ju, jh = cols.index("utility") + 1, cols.index("hedged") + 1
    dv_u = DataValidation(type="list", formula1='"1,0.75,0.5,0.25,0"', allow_blank=True, showErrorMessage=True, errorTitle="utility", error="Use one of 1, 0.75, 0.5, 0.25, 0")
    dv_h = DataValidation(type="list", formula1='"0,1"', allow_blank=True, showErrorMessage=True, errorTitle="hedged", error="Use 0 or 1")
    ws.add_data_validation(dv_u); ws.add_data_validation(dv_h)
    dv_u.add(f"{get_column_letter(ju)}2:{get_column_letter(ju)}{n}"); dv_h.add(f"{get_column_letter(jh)}2:{get_column_letter(jh)}{n}")
    ws.freeze_panes = "B2"; ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{n}"
    wb.save(path)


def hours(n):
    h = n * 45 / 3600
    return "about 25 minutes" if h < 0.6 else f"about {h:.0f} hour{'s' if h >= 1.5 else ''}" if h < 1.25 or h >= 1.5 else "about an hour"


def main():
    guide_md = GUIDE.read_text(); guide_html = md_to_html(guide_md, "Labelling guide")
    pilot = pd.read_csv(LAB / "pilot_30.csv", dtype=str); main_df = pd.read_csv(LAB / "labeller_sheet.csv", dtype=str)
    asg = pd.read_csv(LAB / "assignments.csv"); per = asg.groupby("labeller").size(); letters = sorted(per.index)
    if HAND.exists(): shutil.rmtree(HAND)
    d = HAND / "grader_kit"; d.mkdir(parents=True)
    walk = (WALK.read_text().replace("{N_MAIN}", str(len(main_df))).replace("{N_MAIN_PLUS1}", str(len(main_df) + 1))
            .replace("{N_MINE}", f"{per.min()} to {per.max()}" if per.min() != per.max() else str(per.min()))
            .replace("{HOURS}", hours(per.max())).replace("{LETTERS}", f"{letters[0]} to {letters[-1]}").replace("{K}", str(main_df.assigned_to.iloc[0].count(" ") + 1)))
    (d / "00_START_HERE_WALKTHROUGH.md").write_text(walk); (d / "00_START_HERE_WALKTHROUGH.html").write_text(md_to_html(walk, "Start here"))
    (d / "01_LABELLING_GUIDE.md").write_text(guide_md); (d / "01_LABELLING_GUIDE.html").write_text(guide_html)
    pilot.to_csv(d / "02_pilot.csv", index=False); write_xlsx(pilot, d / "02_pilot.xlsx", "pilot")
    main_df.to_csv(d / "03_main.csv", index=False); write_xlsx(main_df, d / "03_main.xlsx", "main")
    shutil.make_archive(str(HAND / "grader_kit"), "zip", HAND, "grader_kit")
    print(f"grader_kit: {len(list(d.iterdir()))} files, pilot {len(pilot)} rows, main {len(main_df)} rows, graders {letters[0]}-{letters[-1]} with {per.min()}-{per.max()} rows each -> {HAND / 'grader_kit.zip'}")
    (LAB / "returned").mkdir(exist_ok=True)
    (LAB / "returned" / "README.md").write_text(f"""# Returned labels

Every grader returns the same two files; name them with the grader's letter ({letters[0]} to {letters[-1]}) on receipt if the grader did not:

    02_pilot_<letter>.xlsx (or .csv)      03_main_<letter>.xlsx (or .csv)

Validate each file first: `uv run python shared/scripts/03_label_agreement.py [--pilot] --check <letter>`.
Google Forms responses: convert with `shared/scripts/05_forms_to_returned.py --labeller <letter> [--pilot] responses/*.csv` first.

Then, from FINAL_v2:

    uv run python shared/scripts/03_label_agreement.py --pilot    # pilot agreement + pilot_adjudication_queue.csv (for the review call)
    uv run python shared/scripts/03_label_agreement.py            # main agreement + adjudication_queue.csv
    # resolve the queue into data/labels/adjudicated.csv (columns row_id, utility, hedged), then
    uv run python shared/scripts/03_label_agreement.py            # merges into data/labels/human_labels.csv + human_correctness.{{csv,json}}

Then `bash paper/scripts/rebuild_all.sh --paper` (adds tables/human_correctness.tex to the v2 Overleaf package); optionally
v6_top30_significance/v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv.
""")
    print("returned/ folder ready:", LAB / "returned")


if __name__ == "__main__":
    main()
