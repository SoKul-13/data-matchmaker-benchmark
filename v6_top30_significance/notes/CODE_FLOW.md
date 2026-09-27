# v6 code flow: every script, what it reads and writes

Paths are relative to `v6_top30_significance/`. `V6/data` and `V6/shared/src` are shared; each version writes only to its own `output/` and `REPORT.md`.

## shared/src (new modules)

* `search/sampling.py`: `simplex_grid`, `sample_uniform_lattice`, `sample_dirichlet_lattice`, `sample_lhs_simplex` (Latin hypercube → exponential inverse CDF → normalise → snap to lattice), `coverage` (min pairwise L1, nearest-neighbour L1, centred L2 discrepancy, zero-weight share), `design_table`.
* `search/fast_rank.py`: vectorised average ranks, tie-aware Kendall τ-b, Borda pooling and `J_many` for thousands of candidates at once.
* `search/nested.py`: `nested_selection` (in-bag select / out-of-bag score, optimism gap, plateau, selection instability, figures), `transfer` (LODO, LOFO, per-family best), `sensitivity`.
* `search/audit.py`: `load_tensors`, `evaluate_all` (J under Borda / Kemeny / Copeland / BT + τ-native + diagnostics), `design_comparison`, `anchor_components`, `correctness` (ρ, AUC, wrong-mean, hedge gap, Pareto), `neighbours`.
* `stats/significance.py`: `friedman_nemenyi` (+ Iman–Davenport, Holm-Wilcoxon), `pairwise_item_tests` (paired permutation + Wilcoxon, Holm), `kendall_w`, `bootstrap_ranking`, `paired_objective_test`, `tau_granularity`, `holm`.
* `stats/params.py`: `bt_fit` (strengths + SE from the observed information), `rasch_fit` (abilities + item difficulties + SE), `pairwise_wins`, `kemeny` (order + cost), `copeland_scores`, `borda_scores`.
* `stats/leaderboard.py`: `report_rule` (everything one rule's folder contains), `rule_agreement`, `summary_of`, `dataset_diagnostics`, `majority_baselines`.
* `families.py`: dataset → family (EM / SM / TQA / FIN). `views.py`: the eight aggregation views (from v3).
* `adapters/`: 34 adapters; new in v6: dblp_acm (in magellan), wdc_lspc, machamp, papadakis_dn, alaska_camera, alaska_schema, valentine, magneto_gdc, smat, opensanctions_pairs, fintagging, mmtu, realhitbench, suc, tabis, tableeval, tablebench, bird, officeqa_pro_v2; `raw_cache.py` helpers.
* `inference/providers.py`: `ModelSpec` gained `rpm`, `rpd`, `temperature`; `_create_with_temperature` retries without the parameter when an API rejects it and records the outcome in `DECODING_USED`.

## v2_gridsearch

* `01_v1_components.py`: v2 step 1 - the FOUR v1 rubric ingredients (token F1, numeric decay, token precision, token recall) plus exact match, numeric
  Output: output/components_v1.csv  (model, dataset, family, uid, answer_type, native_metric, native_value, em, num_tol, f1, decay,
* `02_exhaustive_grid.py`: v2 step 2 - EXHAUSTIVE grid over the four v1 weights, plus the sampled designs for comparison.
  Outputs: output/grid_exhaustive.csv, output/grid_fine.csv (--fine), output/best.json, output/designs.csv, output/designs_summary.json,
* `03_selection_validity.py`: v2 step 3 - Is the "best weighting" real?  Nested selection, plateau, transfer and sensitivity.
  Outputs: output/selection/nested.json, nested_draws.npz, plateau.csv, lodo.csv, lofo.csv, per_family.json, sensitivity.json,
* `04_correctness_anchors.py`: v2 step 4 - Correctness check borrowed from v5, WITHOUT changing v2's objective.
  Outputs: output/anchors/anchor_components.csv (cached), correctness.csv (per weighting), correctness.json (v1, best-J, best-rho,
* `05_leaderboards.py`: v2 step 5 - Leaderboards under several scoring rules, with parameters, bootstrap draws and significance tests saved for each.
* `06_report.py`: v2 step 6 - Assemble REPORT.md from every output of steps 1-5, plus a run manifest.
* `run_all.sh`: runs the steps above in order.

## v3_aggregation

* `01_native_scores.py`: v3 step 1 - each dataset's OWN metric per (model, item) (num_tol for numeric, exact match for text/boolean, ROUGE-L for free-form),
  Outputs: output/native_item_scores.csv (model, dataset, family, uid, answer_type, metric, score, em), output/random_baseline.json, output/coverage.json
* `02_views_combos.py`: v3 step 2 - the eight aggregation views, their fitted parameters WITH standard errors, every combination of views, sampled designs,
  Outputs: views.csv, views_em.csv, Zb.npz, combos/, params/, designs.json, selection/split_half.json, best.json, fig_views.png/pdf, fig_combos.png/pdf
* `03_leaderboards.py`: v3 step 3 - leaderboards with parameters, bootstrap draws and significance under the two item-level rules the aggregation study uses:
  Outputs: output/leaderboards/{native,em_only}/*, output/leaderboards/mixes_top5.md, rule_agreement.csv, summary.json, output/diagnostics/
* `04_report.py`: v3 step 4 - REPORT.md from output/.
* `run_all.sh`: runs the steps above in order.

## v4_random_search

* `01_components.py`: v4 step 1 - the nine composite components (em, num_tol, num_decay, tok_prec, tok_rec, tok_f1, edit_sim, rouge_l, jaccard) + hedge flag +
  Output: output/components.csv, output/coverage.json
* `02_designs.py`: v4 step 2 - Search over the nine component weights with three sampled designs at the same budget, plus fixed baselines.
  Outputs: output/grid_candidates.csv (the N x 3 + baselines set, sorted by J), output/best.json, output/designs.csv, designs_summary.json,
* `03_selection_validity.py`: v4 step 3 - Nested selection / plateau / transfer / sensitivity over the candidate set of step 2 (reference = the v1 rubric).
  Outputs: output/selection/*
* `04_correctness_anchors.py`: v4 step 4 - correctness of every candidate on v5's known-utility anchors (nine components).  Outputs: output/anchors/*
* `05_leaderboards.py`: v4 step 5 - leaderboards + params + bootstrap + significance under: em_only, v1_rubric, top1..top5, best_anchor, pareto_knee; rule agreement; diagnostics.
* `06_report.py`: v4 step 6 - REPORT.md assembled from output/ (nothing computed here).
* `run_all.sh`: runs the steps above in order.

## v5_metric_library

* `01_compute_matrix.py`: v3 step 1 - Compute the 100-metric matrix for (a) every real (model, item) pair and (b) every synthetic anchor.
  Outputs (output/):
* `02_select_metrics.py`: v3 step 2 - Deduplicate the 100 metrics and select the k that carry information about answer quality.
  Outputs: output/metric_table.csv, output/clusters.json, output/selected.json
* `03_grid_weights.py`: v3 step 3 - Grid search over the selected metrics' weights; keep the 100 best weightings as an ensemble.
  Outputs: output/grid_all.csv (every weighting + terms), output/ensemble.json (top-100 weightings, mean weights),
* `04_leaderboard.py`: v3 step 4 - Score real answers with the ensemble metric and pool across datasets.
  Outputs: output/leaderboard.md, output/leaderboard.json, output/item_scores.csv, output/fig_leaderboard.png/pdf
* `05_validate.py`: v3 step 5 - Validation of the selection + weights.
  Outputs: output/validation.json, output/probes.csv, output/lodo.csv
* `06_report.py`: v3 step 6 - Figures, LaTeX tables, numbers.tex and notes/04_RESULTS.md from output/.
* `07_designs_leaderboards.py`: v5 step 7 - (a) sampled designs versus the exhaustive grid, (b) leaderboards with parameters, bootstrap draws and significance under
  Outputs: output/designs.csv, designs_summary.json, output/leaderboards/<rule>/*, rule_agreement.csv, summary.json, output/diagnostics/
* `08_report.py`: v5 step 8 - REPORT.md from output/ (the v5 notes/04_RESULTS.md from step 6 stays as the detailed results note).
* `run_all.sh`: runs the steps above in order.

## shared/scripts

* `00a_build_item_pool.py`: adapters → stratified pool of 150 → answer types → 100 flagged `in_real_subset` (global `real_size`, per-dataset override) → `data/pool/<name>.jsonl`.
* `00_run_models.py`: models with keys → prompts → cached answers in `data/predictions/<model>.jsonl` with cost, tokens, latency, finish reason and decoding record; `--dry-run`, `--sequential`, `--limit`, `--datasets`, `--models`; per-model rpm / rpd throttle.

## Post-stratification (official-split estimates), added 2026-09-26
* `shared/scripts/00b_official_strata.py`: census of each dataset's official population (adapter loaded with `census: True`, no cap) → stratum counts with the same rule the pool uses (gold label for boolean matching sets, the `stratify` key otherwise, else answer type) + comparability notes → `data/pool/_official_strata.json`.
* `shared/src/stats/poststrat.py`: `stratum_of`, `weights_for` (w = official share / sample share, mean 1), `weighted_estimates` (weighted mean + weighted item bootstrap; positive-class precision / recall / F1 at the official class ratio for boolean sets).
* `stats/leaderboard.report_rule(..., poststrat=...)` writes `official_split_estimates.csv` and an "Official-split estimates" section in every rule's `leaderboard.md`; `poststrat_for` builds the input from the pools; `official_table_md` renders the section used by every version's report.
* Wired in: v2 `05_leaderboards.py`, v3 `03_leaderboards.py`, v4 `05_leaderboards.py`, v5 `07_designs_leaderboards.py`; reports show the table for the version's reference rule (v1 weights / native / v1 rubric / ensemble).
* Adapters with a census mode (return every labelled pair): magellan (5 sets), wdc_products, wdc_lspc, machamp, papadakis_dn, opensanctions_pairs. Not comparable by construction: alaska_camera, officeqa closed-book.
