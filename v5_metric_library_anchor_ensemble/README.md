# Data Matchmaker Benchmark v3 — 100 answer-level metrics, anchor-calibrated selection, grid-searched weight ensemble

v3 replaces the hand-picked composite (v1) and the model-tuned composite (v2) with a metric that is
calibrated **without ranking any model**: a library of **100 answer-level metrics**, a set of
**synthetic answers of known quality** (anchors) on every dataset, **selection** of the metrics that
predict quality out of dataset, and a **grid search** over the selected metrics' weights (plus a hedge
penalty) whose **100 best weightings are averaged** into the final score. Datasets' own metrics stay as
a baseline column and a fidelity term. Everything is reproducible from cached predictions in minutes.

Paper: [paper/main.pdf](paper/main.pdf). Notes, in reading order, with a stage-to-note map: [notes/README.md](notes/README.md) (01 goal and constraints → 02 design space → 03 pipeline flow → 04 results (auto) → 05 conference readiness → 06 your to-do → 07 model catalogue; v2 history in `notes/background/`).

## Pipeline

```
data/pool/<dataset>.jsonl (items, golds, aliases, types)      data/predictions/<model>.jsonl (cached)
        │                                                              │
        ▼ 01_compute_matrix.py  ──────────────────────────────────────┘
   100 metrics per (model, item)  +  100 metrics per synthetic anchor (every dataset, ~13k answers)
        │
        ▼ 02_select_metrics.py   dedupe |Spearman| ≥ .95 → agreement floor → forward selection with LODO stop
   k selected metrics (here: tok_f1, num_decay_2p5, bigram_rec)
        │
        ▼ 03_grid_weights.py     simplex grid × hedge penalty λ → objective on anchors + native fidelity → top-100 ensemble
        │
        ▼ 04_leaderboard.py      ensemble score per answer → per-dataset means → z-normalise → Borda/Kemeny → bootstrap
        │
        ▼ 05_validate.py         leave-one-dataset-out, severity-scale perturbation, per-operator probes
        ▼ 06_report.py           figures, tables, numbers.tex, notes/04_RESULTS.md → paper
```
`scripts/run_all.sh` runs 01–06 and compiles the paper (about 6 minutes; `05` is the slow step).
`scripts/00_run_models.py` collects predictions for datasets that lack them (costs API money; see notes/06_USER_TODO.md).

## Headline (4 models × 7 datasets with predictions; 14 datasets of anchors)

See `notes/04_RESULTS.md` for the live numbers. In short: three metrics are selected out of 100 (token F1,
graded numeric error, bigram recall); the 100-best-weighting ensemble is dominated by graded numeric
error with a hedge penalty ≈ 0.6; it beats every single metric on anchor agreement, correct-vs-wrong
separation and the score given to wrong answers, while the typed native metric keeps the edge on
native fidelity by construction; leave-one-dataset-out agreement barely moves; the leaderboard's top is
gpt-5.5 / claude-sonnet-5 with overlapping intervals below.

## Layout
```
src/metrics/library.py        the 100 metrics (families, registry, compute_all)
src/metrics/                  normalisation, answer typing, the v2 9-component set (kept for comparison)
src/anchors/ladder.py         typed error operators + utility scale → synthetic anchors
src/calibration/select.py     dedupe, anchor agreement, NNLS, LODO forward selection
src/calibration/grid.py       simplex grid, hedge gate, objective terms (ρ, AUC, JS, wrong→, native τ)
src/pooling/rank_aggregation.py  Borda, Kemeny, Copeland, RRF, mean-z, bootstrap
src/adapters/                 14 dataset adapters; src/inference/  provider clients
scripts/00–06, run_all.sh     the pipeline;  scripts/00a_build_item_pool.py  builds pools
config/datasets.toml, models.toml
data/pool, data/predictions   items and cached model outputs
output/                       matrices, metric_table.csv, selected.json, grid_all.csv, ensemble.json, leaderboard.*, validation.json, probes.csv, lodo.csv
paper/, notes/, tests/
```

## Use the metric in code
```python
import json, numpy as np, sys; sys.path.insert(0, "src")
from metrics.library import compute_all, METRIC_NAMES
from calibration.grid import gated_scores
ens = json.load(open("output/ensemble.json"))
v = compute_all("FINAL ANSWER: 14.5%", "0.14464", ["14%"])
score = gated_scores(v[None, ens["selected_idx"]], v[None, ens["hedge_col"]], np.array(ens["top_weightings"])).mean()
```

## Reproduce
```bash
uv sync && scripts/run_all.sh
uv run pytest tests -q            # 39 tests
```
Human labels instead of synthetic anchors: `uv run python scripts/02_select_metrics.py --labels labels.csv`
(columns `uid,dataset,model,label` with label in {0, 0.5, 1}), then 03–06.
