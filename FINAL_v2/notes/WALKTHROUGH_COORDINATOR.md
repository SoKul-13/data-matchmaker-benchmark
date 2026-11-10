# Coordinator walkthrough: running the human labelling from start to finish

For the person who hands out the work, checks what comes back and puts it into the pipeline. The researcher does not grade.
Everything happens in `FINAL_v2/`; commands are run from that directory with `uv run python ...`.

## 0. What exists

| Path | What |
|---|---|
| `data/labels/sample_master.csv`, `pilot_master.csv` | the drawn sample with its secret columns (dataset, item, model, judge scores, question sub-type). Researcher only. |
| `data/labels/labeller_sheet.csv`, `pilot_30.csv` | the blind sheets: 1,550 answers in 31 blocks of 50 (`block` column), and 30 pilot answers |
| `data/labels/handoff/grader_kit.zip` | the one kit every grader receives: background and assignment page, background form, walkthrough, guide, pilot and main sheets (xlsx + csv), scale pictures, form preview |
| `data/labels/forms_images/` | one card picture per answer plus the scale table and the 1 to 7 legend strip, for the online forms (not in git; `06_render_row_images.py`) |
| `shared/forms/make_label_forms.gs` | builds the online forms, the background form and the allocation sheet |
| `data/labels/returned/` | where graders' files go, one per grader |
| `config/labelling.toml` | how ratings are aggregated into one label per answer |
| `notes/` | `LABELLING_GUIDE_FOR_LABELLERS.md` (the rules), `WALKTHROUGH_LABELLERS.md`, `GOOGLE_FORMS_OPTION.md`, `HUMAN_LABELLING_PROTOCOL.md` |

To redraw the sample: `02_make_label_sample.py`, then `06_render_row_images.py`, then `04_make_labeller_handoff.py`; all deterministic (seed 20260923).

## 1. How the labelling is organised

* **The sample.** 1,550 answers: 50 distinct questions from each of the 31 datasets, drawn at random within question sub-types in proportion to the dataset's own mix, one model's answer per question, models balanced. Plus 30 pilot answers from other questions.
* **No letters, no fixed number of graders.** Each grader chooses a grader ID (for example `ab12`) and uses it on every form and file. Whoever returns work under an ID is a grader. People can join late or stop early.
* **Blocks.** The answers are shuffled and cut into 31 blocks of 50, about 38 minutes each. One block is one online form, or one value of the `block` column in the spreadsheet. A grader does whole blocks, as many as agreed. Blocks are a random mix of datasets and answer types, so every block is equally representative.
* **Coverage instead of assignment.** Nobody is assigned blocks. The target is a number of ratings per answer (3 by default, `[targets] labels_per_answer`). The allocation sheet (Forms route) and `coverage.csv` (any route) show, per block, how many graders it has and how many more it needs; graders take the block that needs the most.
* **What a grader records.** `rating`, a whole number from 1 (wrong or no answer) to 7 (correct), each rating named and defined on the form and the sheet; `hedged`, 0 or 1; an optional `note`. The scripts convert the rating to a utility on the 0 to 1 line, (rating − 1) / 6. Graders never see the model name, the judge's score or the dataset id.

## 2. Recruit and brief

* Graders who read tables, filings or data records professionally. Each fills the background form (role, years of experience, familiarity with the four task families, ground rules); the paper's sentence about the graders comes from those answers.
* An adjudicator (can be you) for the answers whose ratings are far apart.
* Send every grader the same `grader_kit.zip`, or on the Forms route the guide, the background-form link and the pilot link. Tell them to choose an ID. Agree how many blocks each will do and by when.
* Never send `sample_master.csv`, `pilot_master.csv` or anything from `v2_gridsearch/output/`.

## 3. Pilot round (everyone, 30 answers)

1. Collect: spreadsheet graders send `02_pilot_<id>.xlsx`; copy it into `data/labels/returned/`. Forms route: download the pilot form's responses and run `uv run python shared/scripts/05_forms_to_returned.py --pilot path/pilot.csv`, which writes one file per grader ID.
2. Validate: `uv run python shared/scripts/03_label_agreement.py --pilot --check all`. In the pilot every answer must be rated.
3. Compare: `uv run python shared/scripts/03_label_agreement.py --pilot`. It prints Krippendorff's α with a bootstrap interval, pairwise exact and within-one-rating agreement, agreement per answer type and task family, a line per grader (mean and gap to the others), and writes `pilot_adjudication_queue.csv` with the answers whose ratings are more than two points apart.
4. Review call over that queue: for each answer, find the rule that was read differently and say which reading is right. If a rule was unclear, edit the guide, re-run `04_make_labeller_handoff.py` and resend the guide. A grader whose gap is far above the rest gets a one-to-one, or is left out with `exclude` in the config.
5. Go ahead when pilot α ≥ 0.6 and within-one-rating agreement ≥ 0.85; otherwise clarify and run a second pilot (`02_make_label_sample.py --seed <new>` gives a new pilot only if you also keep the main sample: simpler is to reuse the first 30 answers of an unused block).

## 4. Main round

1. Share the allocation sheet (Forms route: run `refreshAllocation` whenever you want the counts updated) or tell spreadsheet graders which blocks to take.
2. Collect as often as you like. Forms: download all forms' responses into one folder and run `uv run python shared/scripts/05_forms_to_returned.py folder/*.csv`. It lists every grader ID with answers and forms, warns when two IDs look like the same person, and `--alias "typed=id"` merges them. Spreadsheets: copy `03_main_<id>.xlsx` into `returned/`; a newer file replaces the older.
3. Validate: `uv run python shared/scripts/03_label_agreement.py --check all`. Per grader it lists the blocks completed and any block only partly rated. Problems are fixed by the grader, never by you.
4. Run `uv run python shared/scripts/03_label_agreement.py`. It reports ratings per answer and per grader, agreement with intervals (per answer type and family on screen, per dataset in `agreement_by_stratum.csv`), the drift line per grader, and writes
   * `coverage.csv`: per block, minimum and median ratings per answer, who graded it, and how many more graders it needs for the target;
   * `adjudication_queue.csv`: answers with a wide disagreement, with every grader's rating and note;
   * `human_labels.csv` and `human_correctness.{csv,json}` for the answers resolved so far.
5. Send more graders to the blocks listed as needing them, and repeat from step 2. The run ends with "complete" when no answer is under-covered or waiting.

## 5. Aggregation: how several ratings become one label

Set in `config/labelling.toml`, or per run with flags.

| Setting | Values | Default | Meaning |
|---|---|---|---|
| `method` / `--aggregate` | `mean`, `median`, `mode`, `trimmed` | `mean` | mean of the converted ratings; middle rating; most frequent rating; mean after dropping the lowest and highest when there are four or more |
| `min_labels` / `--min-labels` | whole number | 2 | ratings an answer needs before it gets a label; fewer is "under-covered" |
| `queue_span` / `--queue-span` | points | 2 | ratings more than this many points apart are a wide disagreement |
| `on_disagreement` / `--on-disagreement` | `adjudicate`, `aggregate` | `adjudicate` | wide disagreements wait for the adjudicator, or are aggregated like the rest |
| `hedged` | `majority`, `any` | `majority` | hedged if most graders say so (a tie counts as a wide disagreement), or if any does |
| `exclude` / `--exclude` | grader IDs | none | graders whose ratings are left out |
| `[targets] labels_per_answer` | whole number | 3 | what coverage and allocation aim for |

`human_labels.csv` always carries `utility_mean`, `utility_median` and `utility_mode` next to the chosen `utility`, so the paper can show that the conclusions do not depend on the choice. The settings used are stored in `human_correctness.json`.

## 6. Adjudication

The adjudicator opens `adjudication_queue.csv` (question, reference, final answer, every grader's rating and note; no model names) and fills `data/labels/adjudicated.csv` with `row_id, rating, hedged`, the rating a whole number from 1 to 7 like the graders'. Re-run the agreement script to merge. With `on_disagreement = "aggregate"` this step is skipped.

## 7. Into the paper

When the run says "complete": `bash paper/scripts/rebuild_all.sh --paper`. The v2 Overleaf package gains `tables/human_correctness.tex` and copies the label files into `paper/v2/data/`. Quote the table beside the synthetic-anchor table. Optionally v5: `v6_top30_significance/v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv`.

Report: number of answers, number of graders and ratings per answer (minimum, median), the sampling design, grader backgrounds, pilot size and what it changed, α on the rating and on hedged with intervals (overall, per type, per family, per dataset), the aggregation settings, the number of adjudicated answers, and the `human_correctness` table. State that graders were blind to model identity and judge scores and that the pilot answers were discarded.

## 8. What the checks catch

| Check | Where | Fails when |
|---|---|---|
| every row of the sheet present, columns and read-only cells untouched | `--check` | rows deleted, a filtered view saved, a column renamed, a question edited |
| `rating` a whole number from 1 to 7, `hedged` 0 or 1 | `--check` | a 0 to 1 value such as 0.83, a 0, an 8, free text |
| no half-filled row | `--check` | rating without hedged, or the reverse |
| pilot fully rated | `--check --pilot` | a skipped pilot answer |
| blocks completed or partly rated | `--check` (listed, not an error) | a grader stopped mid-block |
| the same person under two IDs | `05_forms_to_returned.py` (warning) | `sam` on one form, `sam k` on another |
| a grader far from the others | comparison, per-grader line | drift; re-brief or exclude |
| coverage | `coverage.csv` | blocks below the target number of ratings |
