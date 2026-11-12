#!/usr/bin/env python
"""Build the hand-off folder for each labeller: everything they need to see, and nothing else.

    uv run python shared/scripts/04_make_labeller_handoff.py

Reads data/labels/{pilot_30,labeller_sheet}.csv (from 02_make_label_sample.py) and notes/LABELLING_GUIDE_FOR_LABELLERS.md.
Writes data/labels/handoff/grader_kit/ and grader_kit.zip, the ONE kit every grader receives:

    00_BACKGROUND_AND_ASSIGNMENT.html / .md   one page: the study, the grader's assignment (rows, forms, hours), the scale table
    00_BACKGROUND_FORM.xlsx          the grader's professional background, to fill and return (the online twin is buildBackgroundForm())
    00_START_HERE_WALKTHROUGH.html / .md   the step-by-step procedure (from notes/WALKTHROUGH_LABELLERS.md)
    SCALE_TABLE.png, 04_FORM_PREVIEW.html  the 7-point scale as a picture; a mock of one online form with real rows
    01_LABELLING_GUIDE.html / .md    the grading rules (HTML is self-contained and printable)
    02_pilot.xlsx / .csv             the 30-row calibration pilot (everyone grades all of it)
    03_main.xlsx / .csv              the main sheet, all rows, cut into blocks by the `block` column; nobody is assigned rows: a grader does whole blocks
    SCALE_STRIP.png                  the 1-7 legend strip shown above every rating question

The .xlsx sheets have a `scale` tab and drop-down validation on `rating` (1 to 7, each with its name) and `hedged`, a frozen header, wrapped text and the three columns to fill
highlighted; the .csv is the same content for anyone who prefers a plain file.  Returned files go in data/labels/returned/ and are
read by 03_label_agreement.py (xlsx or csv).  The master files that name the model are never copied here.
"""
from __future__ import annotations
import base64, html, io, re, shutil, sys
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_scale import SCALE, FORM_CHOICES, ENTRIES  # noqa: E402
from label_render import row_card, scale_image, scale_strip  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; HAND = LAB / "handoff"
FORM_BATCH = 50  # rows per online form; keep equal to BATCH in shared/forms/make_label_forms.gs
SCALE_HELP = "\n".join(f"{pt} = {name}: {d}" for pt, u, name, d in SCALE)  # the definitions printed under every rating question
GUIDE = ROOT / "notes" / "LABELLING_GUIDE_FOR_LABELLERS.md"; WALK = ROOT / "notes" / "WALKTHROUGH_LABELLERS.md"
FILL = ["rating", "hedged", "note"]
WIDTH = {"row_id": 8, "block": 7, "task_family": 22, "dataset_description": 24, "answer_type": 10, "question": 50, "context": 50, "table": 50, "choices": 24,
         "gold_answer": 28, "accepted_alternatives": 20, "gold_is_a_list": 12, "model_final_answer": 32, "model_full_reply": 50, "rating": 28, "hedged": 9, "note": 24}
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
    ju, jh = cols.index("rating") + 1, cols.index("hedged") + 1
    sc = wb.create_sheet("scale"); sc.append(["Rating", "Converted later to", "Name", "When to use it", "", "drop-down entry"])
    for (pt, u, name, d), entry in zip(SCALE, ENTRIES): sc.append([pt, u, name, d, "", entry])
    for j, w in enumerate([8, 18, 28, 110, 3, 34], 1): sc.column_dimensions[get_column_letter(j)].width = w
    for c in sc[1]: c.font = hdr; c.fill = fill_hdr
    for row in sc.iter_rows(min_row=2): 
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
    sc.append([]); sc.append(["", "", "Anchors", "7 = I would accept this as the reference answer; 4 = half of it is right; 1 = nothing is right. Between two neighbouring ratings choose the lower. Yes/no answers use only 7 or 1. You record the rating; the 0-1 value is computed afterwards."])
    sc.append(["", "", "hedged", "1 when the final answer offers more than one candidate, a range where one value was asked, or will not commit; otherwise 0."])
    dv_u = DataValidation(type="list", formula1=f"=scale!$F$2:$F${len(SCALE) + 1}", allow_blank=True, showErrorMessage=True, errorTitle="rating", error="Pick a rating from 1 to 7 from the list (see the scale tab)")
    dv_h = DataValidation(type="list", formula1='"0,1"', allow_blank=True, showErrorMessage=True, errorTitle="hedged", error="Use 0 or 1")
    ws.add_data_validation(dv_u); ws.add_data_validation(dv_h)
    dv_u.add(f"{get_column_letter(ju)}2:{get_column_letter(ju)}{n}"); dv_h.add(f"{get_column_letter(jh)}2:{get_column_letter(jh)}{n}")
    ws.freeze_panes = "B2"; ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{n}"
    wb.save(path)


def hours(n):
    h = n * 45 / 3600
    if h < 0.6: return "about 25 minutes"
    if h < 1.25: return "about an hour"
    if h < 1.75: return "about an hour and a half"
    return f"about {h:.0f} hours" + (f" (about {h / 5:.0f} working days)" if h >= 10 else "")


def brief_md(main_df, n_pilot):
    n_main = len(main_df); blocks = main_df.block.astype(int); n_blocks = blocks.nunique(); bsize = int(blocks.value_counts().max()); h = n_main * 45 / 3600
    n_src = main_df.dataset_description.nunique(); per_src = main_df.dataset_description.value_counts()
    per_txt = f"{per_src.min()}" if per_src.min() == per_src.max() else f"{per_src.min()} to {per_src.max()}"
    share = main_df.answer_type.value_counts(normalize=True); name = {"boolean": "yes/no judgements", "text": "short text", "numeric": "numbers", "freeform": "sentences"}
    mix = ", ".join(f"{100 * v:.0f} % {name.get(t, t)}" for t, v in share.items())
    scale_rows = "\n".join(f"| **{pt}** | {name_} | {d} | {u} |" for pt, u, name_, d in SCALE)
    return f"""# Background and assignment

## Background: what this study is

AI systems are now asked to work with data: to decide whether two records describe the same product or person, to map the columns of one table onto another, to answer questions from tables and from financial filings. To compare such systems, their answers are marked by an automatic scoring program. Before anyone relies on that program, its marks have to be compared with the judgement of people who work with this kind of data. That comparison is what you are helping with.

You will see answers that different AI systems gave to questions, each next to a reference answer. You decide how correct each answer is. You never see which system wrote an answer, and you are not asked about style or reasoning, only about whether the final answer is right.

Every answer is graded independently by several graders, and their ratings are combined. Where the ratings are far apart, an adjudicator decides. You are identified by your email address, which links your background form to your ratings and lets us reach you. Before any analysis it is replaced by a code; neither your name nor your address appears in any publication or shared file, and the publication will only describe the group's professional background in a sentence.

## Your assignment

| Step | What | Amount | Time |
|---|---|---|---|
| 1 | Decide which email address you will use, and use that one everywhere | | 1 minute |
| 2 | Read this page, the labelling guide and the walkthrough | 3 short documents | about 30 minutes |
| 3 | Fill the background form | one short form | 5 minutes |
| 4 | Pilot: grade the practice answers, then join the review call | {n_pilot} answers | about 25 minutes + a 20-minute call |
| 5 | Main round: grade whole blocks, as many as you agreed | {n_blocks} blocks of {bsize} answers exist ({n_main:,} answers); one block = one online form | about {bsize * 45 / 60:.0f} minutes per block (all {n_blocks} blocks: about {h:.0f} hours) |
| 6 | Submit each form, or return the spreadsheet named with your email address | | |

Which blocks: nobody is assigned particular blocks. The allocation sheet lists every block with the number of graders it has so far; take the one that still needs the most, and finish a block before starting another.

What you record, per answer: a `rating` from 1 to 7 (below) and `hedged`, yes or no. A note is optional. You record the whole number; we convert it to a value between 0 and 1 afterwards.

The questions: {per_txt} from each of {n_src} public benchmarks, drawn at random so that each benchmark's kinds of question appear in the same proportions as in the benchmark itself, and no question appears twice. By answer type: {mix}. The blocks are a random mix of all of them.

## The scale: a rating from 1 to 7

| Rating | Name | When to use it | Converted later to |
|---|---|---|---|
{scale_rows}

Anchors: **7** = I would accept this as the reference answer; **4** = half of it is right; **1** = nothing is right. Between two neighbouring ratings choose the lower. Yes/no answers use only 7 or 1. `hedged` is yes when the final answer offers more than one candidate, a range where one value was asked, or will not commit.

## Ground rules

* Grade on your own. Do not discuss answers with other graders before the pilot review.
* Do not look anything up. Grade only against the reference and the material shown, even if you doubt the reference (write a note).
* Grade the final answer, not the reasoning and not the writing.
* Do whole blocks, and at most two blocks in one sitting; consistency matters more than speed.
"""


BACKGROUND_QUESTIONS = [
    ("Your email address (the same one on every form and in every file name)", "name@example.org"), ("Current role or profession", "e.g. financial analyst, data engineer, accountant, data annotator"),
    ("Years of professional work with data tables, databases or financial documents", "less than 1 / 1 to 3 / 4 to 7 / 8 to 15 / more than 15"),
    ("Highest degree and field", ""),
    ("Familiarity: deciding whether two records are the same product, person or publication", "never done it / occasionally / regularly / it is my job"),
    ("Familiarity: mapping a column of one table to a column of another", "never done it / occasionally / regularly / it is my job"),
    ("Familiarity: answering questions by reading a table", "never done it / occasionally / regularly / it is my job"),
    ("Familiarity: reading financial statements and filings", "never done it / occasionally / regularly / it is my job"),
    ("English reading level", "native / fluent / working knowledge"), ("Have you graded or annotated data before?", "no / once or twice / regularly"),
    ("I have read the labelling guide", "yes"), ("I will grade on my own and not discuss answers before the pilot review", "yes"),
    ("I will not look anything up", "yes"), ("I will grade the final answer, not the reasoning or the writing", "yes"),
    ("How many blocks do you plan to grade, and by when?", ""), ("Anything we should know (optional)", ""),
]


def write_background_form(path: Path):
    wb = Workbook(); ws = wb.active; ws.title = "background"; ws.append(["Question", "Choices / hint", "Your answer"])
    for q, hint in BACKGROUND_QUESTIONS: ws.append([q, hint, ""])
    for j, w in enumerate([70, 55, 45], 1): ws.column_dimensions[get_column_letter(j)].width = w
    for c in ws[1]: c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="DDE6F0")
    for i in range(2, len(BACKGROUND_QUESTIONS) + 2):
        ws.cell(i, 3).fill = PatternFill("solid", fgColor="FFF4CC")
        for j in (1, 2, 3): ws.cell(i, j).alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"; wb.save(path)


def png_uri(img):
    b = io.BytesIO(); img.quantize(64).save(b, format="PNG", optimize=True); return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def form_preview(main_df: pd.DataFrame, path: Path):
    """A mock of one online form (first page + three real answers), laid out as shared/forms/make_label_forms.gs builds it."""
    d = main_df.fillna(""); nb = d.block.astype(int).nunique(); bsize = int(d.block.value_counts().max())
    picks = [d[d.task_family.str.startswith("entity")].iloc[0], d[(d.table != "") & (d.answer_type == "numeric")].iloc[0], d[d.answer_type == "freeform"].iloc[0]]
    css = """body{background:#f0ebf8;font-family:Roboto,Arial,sans-serif;margin:0;padding:24px 0;color:#202124}
.card{background:#fff;border:1px solid #dadce0;border-radius:8px;max-width:760px;margin:0 auto 12px;padding:22px}.head{border-top:10px solid #673ab7}
h1{font-size:28px;font-weight:400;margin:0 0 8px}h2{font-size:16px;font-weight:500;margin:0 0 6px}.help{font-size:13.5px;color:#5f6368;white-space:pre-wrap;line-height:1.55}
.req{color:#d93025}.opt{margin:8px 0;font-size:14px}.dot{display:inline-block;width:18px;height:18px;border:2px solid #5f6368;border-radius:50%;vertical-align:middle}
.scale{display:flex;align-items:flex-end;justify-content:space-between;margin-top:14px;font-size:13px;color:#202124}.scale .end{width:120px;color:#5f6368}.scale .end.r{text-align:right}
.scale .pt{text-align:center;flex:1}.scale .pt span{display:block;margin:6px auto 0}
.short{border-bottom:1px solid #dadce0;color:#80868b;font-size:14px;padding:6px 0;width:60%}img{max-width:100%;border:1px solid #dadce0}
.note{max-width:760px;margin:0 auto 18px;font-size:13px;color:#5f6368}.sep{max-width:760px;margin:26px auto 8px;text-align:center;font-size:13px;color:#5f6368;border-top:1px dashed #b0a8c4;padding-top:8px}
.btn{display:inline-block;background:#673ab7;color:#fff;padding:8px 22px;border-radius:4px;font-size:14px}.nav{max-width:760px;margin:0 auto 12px}.muted{opacity:.75}"""
    strip = png_uri(scale_strip())
    o = [f"<!doctype html><html><head><meta charset='utf-8'><title>Form preview</title><style>{css}</style></head><body>",
         "<p class='note'>Preview of an online grading form, built from real answers. Google's own styling differs slightly; the content and order are the same.</p>",
         f"<div class='card head'><h1>Answer grading, block 1 of {nb}</h1><div class='help'>{bsize} answers, about {bsize * 45 / 60:.0f} minutes. One answer per page: read the card, give a rating from 1 to 7, say whether the answer hedges, press Next.</div></div>",
         "<div class='card'><h2>Email <span class='req'>*</span></h2><div class='help'>Recorded by the form. Use the same address on every form: it links your forms to each other.</div><div class='short'>your.name@example.org</div></div>",
         "<div class='card'><h2>How to grade</h2><div class='help'>1. Grade the system's FINAL answer (yellow on the card) against the reference answer (green). Not the reasoning, not the writing.\n"
         "2. Rating: 7 = I would accept it as the reference answer, 4 = half of it is right, 1 = nothing is right. Between two neighbouring ratings, choose the lower. Yes/no answers are only 7 or 1.\n"
         "3. Hedged = Yes when the final answer offers more than one candidate, a range where one value was asked, or will not commit.\n"
         "4. Do not look anything up. If you doubt the reference, grade against it anyway and leave a note.</div></div>",
         f"<div class='card'><h2>The scale</h2><img src='{png_uri(scale_image())}'></div>",
         "<div class='nav'><span class='btn'>Next</span></div>"]
    pts = "".join(f"<div class='pt'>{i}<span class='dot'></span></div>" for i in range(1, 8))
    for k, r in enumerate(picks):
        rid = r.row_id
        o.append(f"<div class='sep'>page {k + 2} of {bsize + 1}: one answer per page</div>")
        o.append(f"<div class='card head'><h1 style='font-size:22px'>Answer {k + 1} of {bsize}</h1></div>")
        o.append(f"<div class='card'><h2>{rid}</h2><img src='{png_uri(row_card(r))}'></div>")
        o.append(f"<div class='card'><h2>Rating guide</h2><img src='{strip}'></div>")
        o.append(f"<div class='card'><h2>{rid} · Rating <span class='req'>*</span></h2><div class='help'>How correct is the final answer?</div><div class='scale'><div class='end'>Wrong or no answer</div>{pts}<div class='end r'>Correct</div></div></div>")
        o.append(f"<div class='card'><h2>{rid} · Hedged? <span class='req'>*</span></h2><div class='help'>More than one candidate, a range where one value was asked, or no commitment.</div><div class='opt'><span class='dot'></span>&nbsp; No</div><div class='opt'><span class='dot'></span>&nbsp; Yes</div></div>")
        o.append(f"<div class='card'><h2>{rid} · Note</h2><div class='help'>Optional. A few words when unsure or when the rules did not fit.</div><div class='short'>Your answer</div></div>")
        o.append(f"<div class='card muted'><h2>Only if needed: the system's full reply</h2><div class='help'>{html.escape(str(r.model_full_reply)[:1200])}</div></div>")
        o.append("<div class='nav'><span class='btn'>Back</span> <span class='btn'>Next</span></div>")
    o.append("</body></html>"); path.write_text("".join(o))


def main():
    guide_md = GUIDE.read_text(); guide_html = md_to_html(guide_md, "Labelling guide")
    pilot = pd.read_csv(LAB / "pilot_30.csv", dtype=str); main_df = pd.read_csv(LAB / "labeller_sheet.csv", dtype=str)
    n_blocks = main_df.block.astype(int).nunique(); bsize = int(main_df.block.value_counts().max())
    if HAND.exists(): shutil.rmtree(HAND)
    d = HAND / "grader_kit"; d.mkdir(parents=True)
    walk = (WALK.read_text().replace("{N_MAIN_PLUS1}", str(len(main_df) + 1)).replace("{N_MAIN}", f"{len(main_df):,}").replace("{N_BLOCKS}", str(n_blocks))
            .replace("{MIN_BLOCK}", f"{bsize * 45 / 60:.0f}").replace("{BLOCK}", str(bsize)))
    brief = brief_md(main_df, len(pilot))
    (d / "00_BACKGROUND_AND_ASSIGNMENT.md").write_text(brief); (d / "00_BACKGROUND_AND_ASSIGNMENT.html").write_text(md_to_html(brief, "Background and assignment"))
    write_background_form(d / "00_BACKGROUND_FORM.xlsx"); scale_image(d / "SCALE_TABLE.png"); scale_strip(d / "SCALE_STRIP.png"); form_preview(main_df, d / "04_FORM_PREVIEW.html")
    (d / "00_START_HERE_WALKTHROUGH.md").write_text(walk); (d / "00_START_HERE_WALKTHROUGH.html").write_text(md_to_html(walk, "Start here"))
    (d / "01_LABELLING_GUIDE.md").write_text(guide_md); (d / "01_LABELLING_GUIDE.html").write_text(guide_html)
    pilot.to_csv(d / "02_pilot.csv", index=False); write_xlsx(pilot, d / "02_pilot.xlsx", "pilot")
    main_df.to_csv(d / "03_main.csv", index=False); write_xlsx(main_df, d / "03_main.xlsx", "main")
    shutil.make_archive(str(HAND / "grader_kit"), "zip", HAND, "grader_kit")
    print(f"grader_kit: {len(list(d.iterdir()))} files, pilot {len(pilot)} answers, main {len(main_df)} answers in {n_blocks} blocks of {bsize} -> {HAND / 'grader_kit.zip'}")
    (LAB / "returned").mkdir(exist_ok=True)
    (LAB / "returned" / "README.md").write_text(f"""# Returned labels

One file per grader, named with the grader's code (g01, g02, ...), never with a name or an address:

    02_pilot_<code>.xlsx (or .csv)      03_main_<code>.xlsx (or .csv)

Graders are identified by email address. `shared/scripts/05_forms_to_returned.py` turns addresses into codes and writes the files here;
do not copy files in by hand. The address-to-code table is data/labels/grader_registry.csv (git-ignored, private).

Google Forms route:   `uv run python shared/scripts/05_forms_to_returned.py [--pilot] responses/*.csv`
Spreadsheet route:    `uv run python shared/scripts/05_forms_to_returned.py --sheets inbox/03_main_<address>.xlsx ...` (keep the inbox outside the repository)
Background forms:     `uv run python shared/scripts/05_forms_to_returned.py --background background.csv [inbox/00_BACKGROUND_FORM_<address>.xlsx ...]`

Then, from FINAL_v2:

    uv run python shared/scripts/03_label_agreement.py --check all [--pilot]   # validate every returned file
    uv run python shared/scripts/03_label_agreement.py --pilot                 # pilot agreement + pilot_adjudication_queue.csv (for the review call)
    uv run python shared/scripts/03_label_agreement.py                         # agreement, coverage.csv (blocks that need graders), adjudication_queue.csv, human_labels.csv

Aggregation (mean / median / mode / trimmed, minimum ratings per answer, what counts as a wide disagreement, adjudicate or not, graders to
exclude) is set in `config/labelling.toml` or by flags. The adjudicator resolves the queue in `data/labels/adjudicated.csv`
(columns row_id, rating, hedged; rating 1 to 7); re-run the script to merge.

Then `bash paper/scripts/rebuild_all.sh --paper` (adds tables/human_correctness.tex to the v2 Overleaf package); optionally
v6_top30_significance/v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv.
""")
    print("returned/ folder ready:", LAB / "returned")


if __name__ == "__main__":
    main()
