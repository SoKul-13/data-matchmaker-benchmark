# v2 — complete code flow (grid search over v1's four rubric weights)

## Purpose
Keep exactly v1's four ingredients (token F1, numeric decay, token precision, token recall) and let a grid search choose the weights;
compare v1's hand-set point with 104 alternatives on the same cached model answers.

## Folder tree
```
v2_gridsearch_v1_rubric/
  data/pool/<dataset>.jsonl        items (copied from v4): one JSON per line with uid, question, ground_truth, difficulty, context, table_data,
                                   dataset_name, data_type, gold_aliases[], gold_list|null, answer_type, native_metric, in_real_subset  (7 datasets, 120 rows each, 40 flagged real)
  data/predictions/<model>.jsonl   cached model answers: model, model_id, dataset, uid, prediction, in_tokens, out_tokens, latency_s, error, finish, cost_usd
                                   (gpt-5.5, gpt-5.4-mini, claude-opus-5, claude-sonnet-5; _excluded/ holds three small models not used)
  src/metrics/normalize.py         strip_templates, extract_final_answer (tag > "FINAL ANSWER:" line > \boxed > last short line), ParsedNumber(.equivalents),
                                   extract_numbers (sign, %, scale words), canonical_number_string, normalize_text (NFKC, lowercase, canonical numbers, no punctuation/articles), tokens
  src/metrics/answer_types.py      AnswerType {numeric, boolean, text, freeform}; normalize_boolean; detect_answer_type; split_list_answer
  src/metrics/components.py        component_vector(pred, gold, aliases, atype, gold_list) -> 10 numbers [em, num_tol, num_decay, tok_prec, tok_rec, tok_f1, edit_sim, rouge_l, jaccard, hedge_free];
                                   component_dict returns them by name. Helpers: _prf, _rouge_l (LCS), _jaccard, _edit_sim (rapidfuzz), _rel_err (min over unit/percent interpretations), _distinct_numbers
  src/metrics/composite.py         WeightSet / CompositeScorer (not used by v2 scripts; kept for parity)
  src/pooling/rank_aggregation.py  ranks_from_scores, kendall_tau (scipy tau-b), agg_* rules, consensus_ranking(S, rule), dataset_agreement, pairwise_dataset_tau, bootstrap_consensus
  scripts/01_v1_components.py      step 1 (below)
  scripts/02_gridsearch.py         step 2 (below)
  scripts/run_all.sh               runs 1 then 2
  output/                          components_v1.csv, grid.csv, best.json, leaderboard.md, fig_grid.png/pdf
  README.md, notes/MATH.md, notes/CODE_FLOW.md (this file)
```

## Step 1 — `scripts/01_v1_components.py`
Reads: every `data/predictions/*.jsonl` (not `_excluded`), every `data/pool/*.jsonl` (rows with in_real_subset = true and a prediction from every model).
For each (model, item): `component_dict(prediction, ground_truth, gold_aliases, AnswerType, gold_list)`; keeps f1 = tok_f1, decay = num_decay,
precision = tok_prec, recall = tok_rec, and native_value = the component named by the item's native_metric (num_tol | em | rouge_l).
Writes: `output/components_v1.csv` with columns model, dataset, uid, answer_type, native_value, f1, decay, precision, recall (1,120 rows = 4 models × 7 datasets × 40 items).
Prints: per-dataset means of the four ingredients and the native metric.

## Step 2 — `scripts/02_gridsearch.py`
Reads: `output/components_v1.csv`.
Candidates W (105 × 4): v1 point (0.35, 0.35, 0.15, 0.15); the four unit vectors; 100 rows sampled without replacement (seed 20260909) from
`simplex_grid(4, 0.05)` = all 1,771 vectors with entries in {0, 0.05, …, 1} summing to 1.
For each w: `tables(df, w)` → S = w·[f1, decay, precision, recall] per row → pivot mean per (model, dataset) (4 × 7) and per-dataset item matrices;
`evaluate(piv, nat)` → Borda consensus `consensus_ranking(S, "borda")`; J = mean over datasets of `dataset_agreement` (Kendall τ between each
dataset's ranking and the Borda ranking); tau_native = mean over datasets of τ(ranking by S, ranking by native_value); min_agree; pairwise_tau
(mean τ between dataset rankings); dispersion = mean over models of std of centred scores across datasets ÷ std of model means.
Sort by (J, tau_native) descending. `boot_J` (200 item resamples per dataset, Borda recomputed) for ranks 1–5, v1's row and the worst row.
Leaderboard under the best w: per-dataset means, Borda and Kemeny ranks, `bootstrap_consensus` (1,000 resamples) 95 % rank intervals, plus
the Borda ranks under v1's weights and under the native metric.
Writes: `output/grid.csv` (rank, label, w_f1, w_decay, w_precision, w_recall, J, tau_native, min_agree, pairwise_tau, dispersion, J_boot, J_lo, J_hi),
`output/best.json` (best + v1 + counts + pooled ranks + τ between them + CI), `output/leaderboard.md`, `output/fig_grid.png/pdf`.

## Diagram
```
pool/*.jsonl + predictions/*.jsonl
        │  01_v1_components.py : component_dict -> f1, decay, precision, recall, native_value
        ▼
components_v1.csv (1,120 rows)
        │  02_gridsearch.py : 105 weightings -> S_md -> per-dataset ranks -> Borda -> J = mean τ ; tau_native ; bootstrap
        ▼
grid.csv  best.json  leaderboard.md  fig_grid.png
```

## Results as run (2026-09-09)
v1 point: rank 35/105, J 0.429 [0.12, 0.49], τ_native 0.42. Best: random_059 (F1 .85, P .05, R .10, decay 0), J 0.507 [0.22, 0.55], τ_native 0.50.
27 candidates beat v1. Leaderboard under best: see output/leaderboard.md (gpt-5.5 first; ranks 2–4 overlap).

## What still needs to be run
Nothing for this folder as specified. To strengthen it: more models / items in `data/predictions` (copy from v5 after its model run) and re-run
`scripts/run_all.sh` (seconds).
