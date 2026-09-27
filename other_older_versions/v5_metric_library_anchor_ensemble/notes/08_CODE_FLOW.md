# v5 — complete code flow (100-metric library, anchors, selection, weight ensemble; was "v3")

## Purpose
Score every answer with a library of 100 metrics, calibrate against synthetic answers of known quality (never against the ranked models),
keep only informative metrics, grid-search their weights plus a hedge penalty, average the 100 best weightings, and produce a
difficulty-adjusted leaderboard with two kinds of uncertainty.

## Folder tree
```
v5_metric_library_anchor_ensemble/
  config/datasets.toml, config/models.toml   as in v4 (docfinqa disabled, officeqa enabled for the published numbers)
  data/pool/  14 pools (officeqa, finqa, tat_qa, tab_fact, financebench, fetaqa, wikitablequestions: 120 rows/40 real; hitab, abt_buy, amazon_google, dblp_scholar,
              walmart_amazon, wdc_products, tpcdi_cells: 150 rows/150 real); _excluded/docfinqa.jsonl
  data/predictions/  4 models covering the 7 original datasets; _excluded/ three small models
  src/metrics/library.py   Ctx + make_ctx (final answer, normalised tokens, gold aliases, numbers); 100 metric functions registered by family via @metric;
                           METRIC_NAMES (order), FAMILIES, SEMANTIC; compute_all(pred, gold, aliases, atype, gold_list, program, semantic=False) -> np.array(100)
  src/metrics/{normalize,answer_types,components,composite}.py   shared library
  src/anchors/ladder.py    UTILITY (operator -> utility), OPS_BY_TYPE, apply(op, item, rng, pool), paraphrase, generate(items, seed) -> rows {uid, dataset, atype, op, utility, prediction}
  src/calibration/select.py  dedupe(X, names, thresh, prefer) -> representatives + clusters; anchor_agreement(A, u, groups) -> rho/auc/gap per metric;
                           fit_nnls; lodo_rho(A, u, groups, cols); forward_select(A, u, groups, candidates, k_max, min_gain)
  src/calibration/grid.py  LAMBDAS; with_gate(W); gated_scores(X, hedge_free, Wg) = (X·w)·(1−λ·hedged); simplex_grid(K, step); anchor_terms(S, u, groups, ops) -> rho, auc, js, bad;
                           native_fidelity(S_models, native, model_idx, ds_idx, ...) -> mean τ; objective(terms, alpha)
  src/pooling/rank_aggregation.py, src/adapters/, src/inference/   as in v4
  scripts/00a_build_item_pool.py, scripts/00_run_models.py   as in v4 (ROOT one level up)
  scripts/01_compute_matrix.py … 06_report.py, run_all.sh     steps below
  tests/test_v3.py (library, anchors, grid, selection), tests/test_metrics.py
  paper/main.tex, refs.bib, numbers.tex, tables/, figures/, main.pdf
  notes/ 00_PLAIN_ENGLISH_GUIDE, 01_GOAL_AND_CONSTRAINTS, 02_DESIGN_SPACE, 03_PIPELINE_FLOW, 04_RESULTS (auto), 05_CONFERENCE_READINESS, 06_USER_TODO, 07_MODEL_CATALOGUE, 08_CODE_FLOW (this), background/
  output/  matrix_models.npz, index_models.csv, matrix_anchors.npz, index_anchors.csv, metric_table.csv, clusters.json, selected.json, grid_all.csv, ensemble.json,
           baselines_grid.csv, item_scores.csv, leaderboard.md/json, fig_leaderboard, validation.json, probes.csv, lodo.csv
```

## Steps (exact reads / writes)
1. `01_compute_matrix.py [--semantic]`: enabled datasets with pool files; predictions; models. For datasets where every model covers ≥ 90 % of the real
   subset: `compute_all` per (model, item) → `matrix_models.npz` (M 1,120 × 100) + `index_models.csv` (model, dataset, uid, answer_type, native_metric,
   native_value = the column named by NATIVE_COL {num_tol→num_tol_1, em→em_norm, rouge_l→rouge_l}). For ALL enabled pools: `anchors.ladder.generate`
   (one row per applicable operator per item: numeric 15, text 11, boolean 7, free-form 10 operators) → `compute_all` → `matrix_anchors.npz`
   (A 12,813 × 100) + `index_anchors.csv` (dataset, uid, atype, op, utility). Semantic family is zeros unless --semantic.
2. `02_select_metrics.py [--labels file.csv] [--k-max 10] [--thresh 0.95]`: anchor = (A, utility, dataset) or human labels merged on (uid, dataset, model).
   `dedupe` (constant columns dropped; |Spearman| ≥ 0.95 clusters; PREFER order picks the representative) → `anchor_agreement` → candidates =
   representatives with rho > 0.05, auc > 0.55, family ∉ {structure, commit, length} → `forward_select` (LODO Spearman of the NNLS fit, stop when gain
   < 0.002 or k = 10) → writes `metric_table.csv` (metric, rho, auc, gap, family, representative, cluster), `clusters.json`, `selected.json`
   (selected names/idx, nnls_weights, trace, lodo_rho_selected/native_only/em_only).
3. `03_grid_weights.py [--top 100] [--step]`: K = len(selected); step 0.02 (K ≤ 3) / 0.05 (K ≤ 6) / 0.1; `with_gate(simplex_grid(K, step))` (×5 λ);
   per batch of 256: S = `gated_scores(A[:, sel], A[:, hedge_free], Wb)` → `anchor_terms` (rho per dataset mean, AUC of u ≥ .95 vs u ≤ .3, JS between datasets'
   10-bin histograms at the same operator, bad = mean S over u ≤ 0); `native_fidelity` on the model matrix; `objective` with ALPHA {rho .30, auc .15,
   consistency .20, native .15, bad .20}; sort; top-100 → `ensemble.json` (selected, hedge_col, alpha, grid_step, n_grid, mean_weights, mean_lambda,
   weight_spread, top_weightings (100 × K+1), J_top1/J_top100/J_median_grid, terms); `grid_all.csv` (every candidate + terms + w_* + lambda);
   `baselines_grid.csv` (native_style_metric, em_norm, tok_f1, rouge_l, num_tol_1, uniform_over_selected_no_gate, ensemble_top100).
4. `04_leaderboard.py`: S_all = `gated_scores(M[:, sel], M[:, hedge], Wtop)` (1,120 × 100); score = row mean, score_lo/hi = min/max → `item_scores.csv`;
   piv (4 × 7) of means; z-mean common score; `consensus_ranking` for all RULES; native Borda; `bootstrap_consensus` (1,000); rank under each of the 100
   weightings; `dataset_agreement`, `pairwise_dataset_tau`, rule agreement → `leaderboard.json`, `leaderboard.md`, `fig_leaderboard.png/pdf`.
5. `05_validate.py`: (a) LODO: `calibrate()` (dedupe → agreement → candidates → forward_select → gated grid → top-100) without dataset d, then held-out
   Spearman of the LODO ensemble vs the full ensemble on d's anchors, JS of the LODO ensemble over all anchors → `lodo.csv`; (b) 5 draws of utility ± 0.15
   (identity fixed 1, wrong 0) → re-calibrate → L1 shift of mean weights, selection changed; (c) per-operator mean of ensemble / em / native / f1 vs utility
   → `probes.csv`; summary → `validation.json`.
6. `06_report.py`: figures `paper/figures/fig_selection.pdf` (anchor rho by family + top-100 weight spread), `fig_probes.pdf`, `fig_leaderboard.pdf`; LaTeX
   tables `tab_selected, tab_baselines, tab_probes, tab_lodo, tab_leaderboard`; `paper/numbers.tex` (macros); `notes/04_RESULTS.md`. Then `tectonic paper/main.tex`.

## Diagram
```
datasets.toml ─00a─► data/pool/*.jsonl ────────────────────────────┐
models.toml   ─00──► data/predictions/*.jsonl (cached) ─┐          │
                                                        ▼          ▼
                          01_compute_matrix: compute_all(model answers) ; ladder.generate + compute_all(anchors)
                          matrix_models.npz + index_models.csv          matrix_anchors.npz + index_anchors.csv
                                                        │                  │
                                                        └───────┬──────────┘
                                                                ▼ 02_select_metrics: dedupe → agreement → forward_select (LODO)
                                                     metric_table.csv  clusters.json  selected.json
                                                                ▼ 03_grid_weights: simplex × λ → anchor_terms + native_fidelity → objective → top-100
                                                     grid_all.csv  ensemble.json  baselines_grid.csv
                                                                ▼ 04_leaderboard: gated_scores → means → z → Borda/Kemeny → bootstrap
                                                     item_scores.csv  leaderboard.md/json  fig_leaderboard
                                                                ▼ 05_validate: LODO, severity perturbation, probes
                                                     lodo.csv  validation.json  probes.csv
                                                                ▼ 06_report: figures, tables, numbers.tex, notes/04_RESULTS.md → paper/main.pdf
```

## Results as run
100 metrics → 10 constant → 42 representatives → 24 candidates → selected tok_f1, num_decay_2p5, bigram_rec (LODO ρ 0.882; native 0.811; EM 0.822).
Grid 6,630; ensemble mean weights decay .81, F1 .16, bigram_rec .03, λ .63; anchor ρ .906, AUC .997, JS .053, wrong→ .022, τ_native .678; J_ensemble .903
vs native typed metric .913 (wins τ_native by construction). LODO held-out ρ .895 vs .900 full; severity L1 shift .17; probe MAE .095 (native .145, EM .196).
Leaderboard: gpt-5.5 and claude-sonnet-5 tie on Borda (Kemeny: sonnet first); CIs [1,3], [1,4], [1,4], [2,4].

## What still needs to be run
* `scripts/00_run_models.py --sequential`: predictions for the 7 new datasets (≈ USD 22); then set officeqa `enabled = false`; `scripts/run_all.sh` (~6 min).
* Optional: `--semantic` in step 1 after `uv add sentence-transformers`; `02_select_metrics.py --labels labels.csv` once human labels exist;
  Gemini billing / free keys for more models (notes/06_USER_TODO.md).
