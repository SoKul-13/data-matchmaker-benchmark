# v6: the four calibration versions on one shared suite, with the rigor additions applied to all of them

v6 is not a fifth method. It is v2, v3, v4 and v5 re-run side by side on one shared data folder (the evidence top-30 datasets plus
OfficeQA) with the same additions applied to each: exhaustive or Latin-hypercube search designs, nested (honest) selection, transfer tests,
correctness on known-quality anchors, leaderboards under the naive / deployed / calibrated rules, saved parameters with standard errors,
saved bootstrap draws, and Friedman / Nemenyi / Holm-corrected significance. Every version writes a `REPORT.md` that is assembled from its
`output/` files, so numbers in the text always match the files.

| Folder | What it is | Report |
|---|---|---|
| `v2_gridsearch/` | audit of v1's four hand-set weights: **exhaustive** 1,771-point grid, plateau, nested selection, LODO / LOFO, anchors, leaderboards, significance | `v2_gridsearch/REPORT.md` |
| `v3_aggregation/` | eight aggregation views, **all 255 combinations** with member parameters (BT strengths + SE, Rasch abilities + SE, Kemeny cost), LHS and lattice mixes, split-half honesty, leaderboards under native / exact match | `v3_aggregation/REPORT.md` |
| `v4_random_search/` | nine-component composite: Dirichlet vs Latin-hypercube vs uniform designs (100 each, 20 seeds), nested selection, transfer, anchors, leaderboards, significance | `v4_random_search/REPORT.md` |
| `v5_metric_library/` | the anchor-calibrated ensemble (unchanged pipeline) + designs looked up in its exhaustive grid + leaderboards with significance under exact match / native / ensemble / top-5 | `v5_metric_library/REPORT.md` |
| `shared/src/` | one copy of the scorer (`metrics/`), pooling, adapters (34), inference, plus new `search/` (sampling, fast rank agreement, nested selection, audit helpers), `stats/` (significance, parameters with SE, leaderboard writer), `views.py`, `families.py` | – |
| `shared/scripts/` | `00a_build_item_pool.py` (pools, 150 items, 100 answered per dataset), `00_run_models.py` (temperature 0, per-model rate caps, per-row decoding record) | – |
| `config/` | `datasets.toml` (33 pools; finqa and financebench disabled), `models.toml` (13 models, temperature 0, rpm / rpd caps) | – |
| `data/` | `pool/` (one JSONL per dataset), `predictions/` (one JSONL per model, shared by all versions), `raw/` (symlink to the raw downloads) | – |
| `notes/` | `00_STATUS_AND_PLAN.md`, `CODE_FLOW.md`, `HUMAN_LABELLING_PROTOCOL.md`, `RUN_MODELS.md` | – |

Run everything (minutes, from cached answers): `bash v2_gridsearch/scripts/run_all.sh`, `bash v3_aggregation/scripts/run_all.sh`,
`bash v4_random_search/scripts/run_all.sh`, `bash v5_metric_library/scripts/run_all.sh`. The model run (the only paid step) is described in
`notes/RUN_MODELS.md` and is not started by any of these.

Status (2026-09-27): the model run is complete (31 datasets × 10 models × 100 items; Gemini 3.1 Pro left out by Google's daily quota) and all four reports are on the full data; findings in `notes/00_STATUS_AND_PLAN.md`.
