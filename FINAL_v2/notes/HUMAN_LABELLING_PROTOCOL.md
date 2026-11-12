# Human labelling protocol: real judgements beside the synthetic anchors

**Status 2026-11-11: the kit is complete and tested end to end** (sample drawn, grader kit built, Google Forms generator written, agreement and
merge scripts tested on simulated returns from both routes and the simulated files deleted). No human labels exist yet.

Purpose: v2's correctness step and v5 validate the scoring rule against *synthetic* answers of known utility. Reviewers will ask for human
judgements. This protocol produces them at a size that supports a per-dataset table: every figure about the judge then has a real-label
counterpart with a confidence interval.

## 1. Design at a glance

| Element | Choice | Why |
|---|---|---|
| Rows | 1,550 = 50 per dataset × 31 datasets | per-dataset Spearman ρ within about ±0.09; overall and per-family figures tight |
| Questions | 50 **distinct** questions per dataset, drawn by stratified random sampling over question sub-types (the pool's sub-task label × answer type) with proportional allocation | every sampled question has the same weight, and each dataset's sample mirrors its own mix of question types (largest gap between sample share and dataset share of any sub-type: 1 percentage point; 10 sub-types that hold a single question each have no row) |
| Answers | one model's answer per question; models balanced (4 or 5 rows per model per dataset, 138 to 146 per model overall) | no model dominates |
| Informative cases | up to a quarter of a dataset's rows show an answer on which exact match and the deployed composite disagree by ≥ 0.5; this only steers *which model's answer* is shown, never which question is drawn | these rows decide which scorer people side with (54 rows in the current draw) |
| Scale | graders record a **rating from 1 to 7** (1 wrong or no answer … 7 correct), each rating named and defined on the sheet and under every form question; the scripts convert afterwards to a utility, (rating − 1) / 6 = 0.00, 0.17, 0.33, 0.50, 0.67, 0.83, 1.00; `hedged` 0/1; optional note | Likert-style intuition for the grader, values on the same 0-1 line as the judge and the synthetic anchors for the analysis; a recorded 1 can never be mistaken for "fully correct" |
| Graders | any number, no letters or IDs: each grader is identified by their email address (stored only as a code, `g01`...) and does whole blocks; graders are whoever returns work | people can join late or stop early; nothing has to be re-drawn when the head count changes |
| Blocks | the shuffled answers are cut into 31 blocks of 50 (one online form each, about 38 minutes); every block is a random mix of datasets and answer types | a grader's subset is representative whatever blocks they take |
| Coverage | target 3 ratings per answer (`config/labelling.toml`); the allocation sheet and `coverage.csv` show which blocks still need graders | replaces assignment |
| Time | about 38 minutes per block; all 31 blocks are about 19 hours; 3 ratings on every answer are about 58 person-hours in all | |
| Pilot | 30 rows from questions not in the main sample, graded by everyone, discussed, discarded | calibration |
| Adjudication | answers whose ratings are more than two points apart, or tied on hedged; the adjudicator also gives a 1-7 rating; can be switched off | only wide disagreements need a decision |
| Aggregation | configurable in `config/labelling.toml` or by flags: mean (default), median, mode or trimmed mean of the converted ratings; minimum ratings per answer; what counts as a wide disagreement; adjudicate or aggregate; graders to exclude. `human_labels.csv` always carries the mean, median and mode side by side | the paper can show the conclusions do not depend on the choice |

Seed 20260923; `02_make_label_sample.py --stratify type --n 400` reproduces the earlier small design; `--block-size n`,
`--per-dataset n`, `--allocation equal` (the same number of questions for every sub-type instead of proportional), `--disagree-share s` change the layout. The scale lives in one place, `shared/scripts/label_scale.py`.

## 2. Workflow

| Step | Command / file |
|---|---|
| Draw the sample (done) | `uv run python shared/scripts/02_make_label_sample.py` → `data/labels/labeller_sheet.csv` (with its `block` column), `sample_master.csv` (researcher only; has `_stratum`, model, judge scores), `pilot_30.csv` |
| Build the kit (done) | `uv run python shared/scripts/04_make_labeller_handoff.py` → `data/labels/handoff/grader_kit.zip`: background and assignment page, background form, walkthrough, guide, pilot and main sheets (xlsx with a `scale` tab and a labelled drop-down, and csv), scale picture, form preview |
| Row cards for Forms (done; not in git) | `uv run python shared/scripts/06_render_row_images.py` → `data/labels/forms_images/<row_id>.png` + `scale_table.png` |
| Online forms (optional route) | `shared/forms/make_label_forms.gs`: `buildBackgroundForm()`, `buildForms()` (one form per block), `refreshAllocation()` (work list with live counts of graders per block); see `notes/GOOGLE_FORMS_OPTION.md` |
| Give every grader | the same `grader_kit.zip` (or the form links plus the guide); each uses one email address throughout |
| Collect returns | `data/labels/returned/02_pilot_<code>` and `03_main_<code>` (`.xlsx` or `.csv`), written by `shared/scripts/05_forms_to_returned.py`, which turns addresses into codes: spreadsheets with `--sheets inbox/*.xlsx`; Forms responses are converted with `shared/scripts/05_forms_to_returned.py [--pilot] responses/*.csv`, one file per grader ID found |
| Validate | `uv run python shared/scripts/03_label_agreement.py [--pilot] --check all` (all rows present, ratings whole numbers 1 to 7, no half-filled row, read-only cells untouched; lists each grader's completed and partly rated blocks) |
| Pilot review | `uv run python shared/scripts/03_label_agreement.py --pilot` → α with bootstrap interval, per type and family, per-grader drift, `pilot_adjudication_queue.csv`; tighten the guide if α < 0.6 |
| Main round (repeat as work arrives) | `uv run python shared/scripts/03_label_agreement.py` → the same statistics, `agreement_by_stratum.csv` (per type, family, dataset), `coverage.csv` (blocks that need graders), `adjudication_queue.csv`, and `human_labels.csv` for the answers resolved so far |
| Adjudicate | the adjudicator fills `data/labels/adjudicated.csv` (`row_id, rating, hedged`; rating 1 to 7) for every queued row |
| Merge + correctness | re-run `03_label_agreement.py` until it says "complete" → `human_labels.csv` and `human_correctness.{csv,json}`: every v2 leaderboard rule scored on the labelled rows against the human utility (ρ, AUC of human-correct ≥ 0.8 vs human-wrong ≤ 0.2, wrong-mean, hedge gap, model-ranking ρ) |
| Into the paper | `bash paper/scripts/rebuild_all.sh --paper` → `paper/v2/tables/human_correctness.tex` and the label files in `paper/v2/data/`; optionally v5: `02_select_metrics.py --labels data/labels/human_labels.csv` (`label` = utility rounded to 0 / 0.5 / 1) |

Walkthroughs: `notes/WALKTHROUGH_LABELLERS.md` (in the kit), `notes/WALKTHROUGH_COORDINATOR.md` (you). The rules given to graders are
`notes/LABELLING_GUIDE_FOR_LABELLERS.md`.

## 3. Graders

People who read tables, filings or data records for a living (analysts, data engineers, accountants, annotators with a data-management
background). Each is identified by their email address and fills the background form (role, years of experience, familiarity with the four task families, ground
rules); the paper describes the group in one sentence from those answers. The researcher never labels. Never give graders
`sample_master.csv` or `pilot_master.csv`. The number of graders is open: a dropout only lowers coverage on the blocks they had not
reached, which `coverage.csv` shows, and anyone new can pick those blocks up after doing the pilot.

## 4. What is reported

* Answers, number of graders, ratings per answer (minimum and median), sampling design (section 1), grader backgrounds, pilot size and
  what the pilot changed in the guide, and the aggregation settings used.
* Krippendorff's α (ordinal) on the rating and α (nominal) on hedged with 95 % bootstrap intervals: overall, per answer type, per task family,
  per dataset; pairwise exact and within-one-rating agreement; number of adjudicated rows. Target α ≥ 0.80 overall, 0.67 as the floor for
  tentative conclusions.
* Judge against people: the `human_correctness` table beside the synthetic-anchor table, and human-human agreement beside judge-human
  agreement.
* Sub-types are sampled in proportion to the dataset's mix, so per-dataset figures need no reweighting; `_stratum` in `sample_master.csv`
  records each row's sub-type for breakdowns.
* Graders were blind to model identity and judge scores; pilot rows were discarded; guide, sheets and raw labels are released.

## 5. Effort

Three ratings on each of 1,550 answers are 4,650 ratings, about 58 person-hours, however many people share them (for example 10
graders doing 9 or 10 blocks each, about 6 hours). The only step of the paper that cannot be automated.
