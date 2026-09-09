# v3 — complete code flow (aggregation views from the literature, mixed by grid search)

## Purpose
Use each dataset's own metric for every answer (no composite), implement eight published ways of turning per-dataset results into one model
score, and grid-search how to mix them with an objective built from the reliability papers.

## Folder tree
```
v3_literature_aggregation/
  data/pool, data/predictions   identical to v2's (7 datasets × 40 real items; 4 models)
  src/metrics/                  same library as v2 (normalize, answer_types, components, composite)
  src/pooling/rank_aggregation.py  same as v2
  src/views.py                  per_dataset_table; view_mean_raw; view_baseline_norm_mean; view_z_mean; view_mean_win_rate; view_borda; view_kemeny_score;
                                _bt_fit + view_bradley_terry; view_irt_ability; all_views; standardise
  scripts/01_native_scores.py   step 1
  scripts/02_gridsearch_views.py step 2
  scripts/run_all.sh
  notes/01_LITERATURE_REVIEW.md ten papers: summary, findings, math, sources
  notes/02_MATH.md              every formula
  output/                       native_item_scores.csv, random_baseline.json, views.csv, grid_views.csv, best.json, leaderboard.md, fig_views.png/pdf
```

## Step 1 — `scripts/01_native_scores.py`
Reads pool + predictions as in v2. For each (model, item): `component_dict(...)`, keep score = component named by the item's native_metric
(num_tol for numeric, em for text/boolean, rouge_l for free-form). Random baseline per dataset b_d = 0.5 × (share of boolean items).
Writes `output/native_item_scores.csv` (model, dataset, uid, answer_type, metric, score) and `output/random_baseline.json`.

## Step 2 — `scripts/02_gridsearch_views.py`
Reads the two files above. `all_views(items, baseline)` → table V (4 models × 8 views):
mean_raw = mean_d S_md; baseline_norm_mean = mean_d max(0,(S_md−b_d)/(1−b_d)); z_mean = mean_d (S_md−μ_d)/σ_d; mean_win_rate = mean_d fraction of
other models beaten (ties ½); borda = mean_d (M − rank_d); kemeny_score = M − position in the Kemeny consensus of the per-dataset rankings;
bradley_terry = β from `_bt_fit(W)` where W[i,j] = number of items where i outscored j (ties ½), fitted by L-BFGS on the BT log-likelihood with a
0.01 ridge; irt_ability = θ from a Rasch fit on y = 1[score ≥ 0.5] (L-BFGS, ridge). `standardise(V)` → Z (each view z-scored across models).
Bootstrap: 100 resamples of items within each dataset; all eight views recomputed per resample → Zb (100 × 4 × 8).
Reference rankings: Copeland ranking of the S_md table; Kemeny consensus of the eight single-view rankings.
Candidates (109 × 8): eight unit vectors, uniform, 100 random rows of `simplex_grid(8, 0.05)` (seed 20260909).
For each w: mixed score s = Z·w; r = ranks; stability = mean_b τ(ranks(Zb[b]·w), r); transitivity = τ(r, Copeland); reference = τ(r, Kemeny);
J = 0.5·stability + 0.25·transitivity + 0.25·reference.
Writes `output/views.csv`, `output/grid_views.csv` (rank, label, w_<view>×8, stability, transitivity, reference, J, rank_<model>×4),
`output/best.json` (best w + terms, uniform_J, single_view_J, mixed_score, mixed_rank, rank_ci95_items, single_view_ranks, kemeny_reference_rank),
`output/leaderboard.md`, `output/fig_views.png/pdf`.

## Diagram
```
pool + predictions ──01_native_scores.py──► native_item_scores.csv (+ random_baseline.json)
        │ 02_gridsearch_views.py
        ├─ all_views ──► V (4×8) ──standardise──► Z
        ├─ 100 item bootstraps ──► Zb (100×4×8)
        ├─ Copeland ranking, Kemeny consensus of single-view rankings
        └─ 109 mixes w: s = Z·w → J(w) = .5 stability + .25 transitivity + .25 reference
                ▼
views.csv  grid_views.csv  best.json  leaderboard.md  fig_views.png
```

## Results as run
Best: pure bradley_terry (J 0.867; stability 0.90, transitivity 1.0, reference 0.67). Single views: kemeny 0.818, irt 0.815, z_mean 0.788,
mean_win_rate 0.757, borda 0.756, mean_raw 0.547, baseline_norm 0.458; uniform mix 0.798. Final: gpt-5.5 > claude-sonnet-5 > claude-opus-5 > gpt-5.4-mini;
rank CIs [1,1], [2,3], [2,4], [3,4].

## What still needs to be run
Nothing for this folder as specified. With more models/items (copy predictions from v5 after its run) the BT and IRT views become better determined; re-run `scripts/run_all.sh` (~1 min).
