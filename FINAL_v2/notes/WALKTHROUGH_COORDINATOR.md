# Coordinator walkthrough: running the human labelling from start to finish

For the person who loads the data, hands it out, checks what comes back and puts it into the pipeline. The researcher does not label.
Everything happens in `FINAL_v2/`; commands are run from that directory with `uv run python ...`.

## 0. What exists already

| Path | What |
|---|---|
| `data/labels/sample_master.csv`, `pilot_master.csv` | the drawn sample with its secret columns (dataset, item, model, judge scores). Researcher only. |
| `data/labels/handoff/grader_kit.zip` | the one kit every grader receives (walkthrough, guide, pilot and main sheets as xlsx + csv) |
| `data/labels/labeller_sheet.csv`, `assignments.csv` | the blind main sheet with its `assigned_to` column, and the same assignment in long form |
| `data/labels/agreement_by_stratum.csv` | written by the comparison: α with bootstrap intervals per answer type, task family and dataset |
| `data/labels/returned/` | empty folder where finished files go |
| `notes/LABELLING_GUIDE_FOR_LABELLERS.md` | the rules (also inside each zip) |
| `notes/WALKTHROUGH_LABELLERS.md` | the grader procedure (also inside the kit as `00_START_HERE_WALKTHROUGH`) |
| `notes/HUMAN_LABELLING_PROTOCOL.md` | the design and the paper-side rationale |
| `notes/GOOGLE_FORMS_OPTION.md` | how to run the same thing through Google Forms instead of spreadsheets |

If the sample ever has to be redrawn (new models, new items), run in order
`shared/scripts/02_make_label_sample.py` then `shared/scripts/04_make_labeller_handoff.py`; both are deterministic (seed 20260923).

## 1. Understand what is being labelled

One row = one answer from one model to one benchmark item. Default layout: 100 rows from each of the 31 datasets (3,100 rows), 5 graders (letters A to E) who each grade every row, about 39 hours each, so five labels per row; change with `02_make_label_sample.py --labellers N --per-row k`, or `--stratify type --n 400` for the small design. The 3,100 rows are drawn with an equal share per model inside each dataset and a quarter from judge-versus-exact-match disagreement cases. The original small design was 401 main rows: 100 per answer type (numeric, boolean, text, free-form), an equal share per model inside each type, every dataset at least 5 rows, and a quarter of the rows drawn from answers where exact match and the deployed judge disagree by at least 0.5 (these are the rows that decide which scorer humans side with). Plus 30 pilot rows from the same design, disjoint from the main rows.

Graders see the task family, the question, the material, the gold answer and alternatives, and the model's final answer. They do not see the model name, the judge's score, or any dataset id. They fill `utility` (1 / 0.75 / 0.5 / 0.25 / 0) and `hedged` (0 / 1), with an optional `note`, on the rows whose `assigned_to` contains their letter. Extra rows they label voluntarily are used as extra labels.

## 2. Recruit and brief

* Graders who read tables, filings or data records professionally (analysts, data engineers, annotators). Record the group's background in one line; it goes in the paper.
* An adjudicator (can be you). They see all labels and notes for the disputed rows only.
* Brief: send everyone the same `grader_kit.zip` and, separately, each person's letter (keep a private list of who is which letter). Tell them the pilot comes first and that a 20-minute call follows it. Agree a return channel (email or a shared drive folder).

## 3. Hand out

Send `grader_kit.zip` to every grader with their letter. Never send `sample_master.csv`, `pilot_master.csv` or anything from `v2_gridsearch/output/`.

## 4. Pilot round

1. Everyone returns the pilot as `02_pilot_<letter>.xlsx` (or `.csv`). Copy them into `data/labels/returned/`; add the letter to the name yourself if a grader forgot.
2. Check each file on its own:
   `uv run python shared/scripts/03_label_agreement.py --pilot --check A` (and so on per letter). This reports missing row ids, blank cells, values outside the scale, and extra columns. Send the grader the list if anything fails.
3. Compare: `uv run python shared/scripts/03_label_agreement.py --pilot`. It prints Krippendorff's α (ordinal, any number of graders) on utility, pairwise exact and within-one-level agreement, α (nominal) on hedged, agreement per answer type, a per-grader drift check (mean gap to the others on shared rows), a confusion table, and writes `data/labels/pilot_adjudication_queue.csv` with every row whose labels span more than one level.
4. Hold the review call over that queue (one call for everyone, or a short note per grader). For each row, find the rule that was misread and say which reading is right. A grader whose drift gap is far above the rest gets a one-to-one. If a rule itself was unclear, edit `notes/LABELLING_GUIDE_FOR_LABELLERS.md`, re-run `04_make_labeller_handoff.py`, and resend the guide (the sheets do not change).
5. Threshold: pilot α ≥ 0.6 and within-one-level ≥ 0.9 means go ahead. Below that, clarify the guide and run a second pilot of 30 (draw with `02_make_label_sample.py --pilot 30 --seed <new seed>` and hand out only the new `pilot_X` files).

## 5. Main round

1. Everyone returns `03_main_<letter>`. Copy into `data/labels/returned/`.
2. Check each: `uv run python shared/scripts/03_label_agreement.py --check A` per letter. Fix with the grader until clean (a grader fixes their own file; you never edit labels).
3. Compare: `uv run python shared/scripts/03_label_agreement.py`. Record the printed numbers; they go in the paper: α with 95% bootstrap intervals overall, per answer type and per task family on screen, per dataset in `agreement_by_stratum.csv`. Target: α ≥ 0.80 overall, 0.67 as the floor; report the per-type and per-dataset values whatever they are.
4. `data/labels/adjudication_queue.csv` is written: rows whose labels span more than one level, whose hedged votes tie, or that are missing a label, with every label and note in one column.

## 6. Adjudication

The adjudicator fills `data/labels/adjudicated.csv` with three columns: `row_id, utility, hedged`, one line per queued row, values on the same scale. They may read the question, gold, final answer and all notes; they do not see model names either (the queue file has none).

Rows not in the queue are resolved automatically: when all labels lie within one level of each other, the final utility is their mean (three labels of 0.75, 1, 1 give 0.917); `hedged` is the majority vote.

## 7. Merge and produce the paper numbers

`uv run python shared/scripts/03_label_agreement.py` once more. With `adjudicated.csv` present it writes:

* `data/labels/human_labels.csv`: dataset, uid, model, utility, hedged, label (utility rounded to 0 / 0.5 / 1 for the v5 selector), n_labels, labellers, adjudicated, min and max raw utility, the judge's v1 and exact-match scores, row_id.
* `data/labels/human_correctness.csv` and `.json`: every v2 leaderboard rule (exact match, v1, top1 to top5, best anchor, Pareto knee) scored on the labelled rows against the human utility: Spearman ρ, AUC correct-vs-wrong, mean score on human-wrong answers, hedge gap, and ρ between the rule's model ranking and the human model ranking on those rows.

Then `bash paper/scripts/rebuild_all.sh --paper`. The v2 Overleaf package gains `tables/human_correctness.tex` and copies the three label files into `paper/v2/data/`. Quote the table beside the synthetic-anchor table (`anchors_rules`) in the Results. Optionally run v5 with real labels: `v6_top30_significance/v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv`.

## 8. What to report in the paper

Number of rows and labels per row, the sampling design (section 1 above), grader backgrounds, α on utility and on hedged with the per-type breakdown, the number of adjudicated rows, and the `human_correctness` table. State that graders were blind to model identity and judge scores and that the pilot rows were discarded.

## 9. Checks the scripts perform for you

| Check | Where | Fails when |
|---|---|---|
| every row of the sheet present, and every assigned row labelled | `--check`, and counted in the comparison | a row was deleted, a filtered view was saved, or an assigned row was skipped |
| `utility` in {0, 0.25, 0.5, 0.75, 1}, `hedged` in {0, 1} | `--check` | typed value, "0,75", "yes" |
| no blanks | `--check` (listed), comparison (counted and queued) | skipped rows |
| only the three editable columns changed | `--check` | a renamed or added column, or an edited read-only cell |
| agreement thresholds and per-grader drift | printed by the comparison | α below target: more pilot; one grader far off: re-brief or drop their labels |
