# v3 notes — read in this order

Everything numbered 01–07 describes the **current v3 pipeline** (`../scripts/01–06`, `../src/`). The
`background/` folder holds the earlier v2 method documents that led here; read them only for history.

| # | File | Read it to learn | Corresponds to |
|---|---|---|---|
| 00 | `00_PLAIN_ENGLISH_GUIDE.md` | the whole project in plain language: goal, glossary of every technical term, v1/v2/v3 step by step with motive, pros, cons and what each proves | everything |
| 01 | `01_GOAL_AND_CONSTRAINTS.md` | the goal; what was not possible / cost money or time; the alternative taken with pros and cons; the choice made per section | the whole design |
| 02 | `02_DESIGN_SPACE.md` | every alternative for every stage (§0–16), the decision flow, the bundles, the recommended hybrid, the IRT generalisation method, the 100-metric plan | why v3 looks the way it does |
| 03 | `03_PIPELINE_FLOW.md` | each stage: inputs, what is computed, outputs, and the design decisions embedded | `scripts/01_compute_matrix.py` … `06_report.py` |
| 04 | `04_RESULTS.md` | **auto-generated** live numbers: selected metrics, ensemble weights, baselines, probes, LODO, leaderboard, caveats | `output/`, `paper/` |
| 05 | `05_CONFERENCE_READINESS.md` | honest NeurIPS assessment: blocking gaps, serious gaps, presentation, realistic path | what the paper still needs |
| 06 | `06_USER_TODO.md` | everything only you can do (prediction run, keys, billing, optional data, labels) | `scripts/00_run_models.py`, `.env` |
| 07 | `07_MODEL_CATALOGUE.md` | which models are in consideration, their status, how to activate them | `config/models.toml` |
| 08 | `08_CODE_FLOW.md` | every script, function, input and output file, results as run, what still needs to run | the whole folder |
| B1–B4 | `background/` | the v2 account (what was done and why, rank-rule worked example, Kendall τ, gold answers, dataset recommendations, v1/v2/recommended comparison) | history |

Quick map from a pipeline stage to its note:

```
00_run_models.py / 00a_build_item_pool.py  ->  06_USER_TODO, 07_MODEL_CATALOGUE, 03_PIPELINE_FLOW §0
01_compute_matrix.py  (100 metrics, anchors) ->  03_PIPELINE_FLOW §1, 02_DESIGN_SPACE §16 (library), 01_GOAL (semantic family off)
02_select_metrics.py  (dedupe, selection)   ->  03_PIPELINE_FLOW §2, 04_RESULTS (selected metrics, LODO ρ)
03_grid_weights.py    (grid, top-100)       ->  03_PIPELINE_FLOW §3, 02_DESIGN_SPACE §G/§E, 04_RESULTS (ensemble, baselines)
04_leaderboard.py     (pooling)             ->  03_PIPELINE_FLOW §4, background/B1 §12–14 (rank rules, Kendall τ)
05_validate.py        (LODO, severity, probes) -> 03_PIPELINE_FLOW §5, 04_RESULTS (validation), 05_CONFERENCE_READINESS
06_report.py          (figures, paper)      ->  04_RESULTS, ../paper/main.pdf
```
