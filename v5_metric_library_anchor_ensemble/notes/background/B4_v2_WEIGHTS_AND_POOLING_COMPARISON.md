# Choosing weights and pooling ranks: v1 vs current v2 vs recommended

Side-by-side of how the composite-metric weights are chosen and how per-dataset results are
combined into one leaderboard, in the original benchmark (v1), in this folder as it stands (v2),
and in the protocol recommended for the next run (documented in `PIPELINE_AND_DATASETS.md` §4–5).

## A. Choosing the weights

| Aspect | v1 (original) | v2 (current) | Recommended next |
|---|---|---|---|
| Components | F1, exp(−2.5·MRE), P, R (4) | EM, NumTol, NumDecay, P, R, F1, Edit, ROUGE-L, Jaccard (9) | same 9; optional embedding-similarity column if free-form answers matter |
| Weight vector | one, hand-set: .35/.35/.15/.15 | one global vector on the 0.05 simplex grid | same |
| How chosen | by the author, with an after-the-fact "Lipschitz bound" argument | random search: 100 grid combinations, best by objective J | random search: 100 grid combinations **+ the 5 baselines**, objective computed as a bootstrap mean |
| Objective | none | J = mean over datasets of Kendall τ(dataset ranking, Borda-pooled ranking) | same J, averaged over 50 item-bootstraps so ties disappear; τ-AP (top-weighted) if the claims are about the top ranks |
| Tie-break | — | mean pairwise τ between datasets | (1) native-metric agreement, (2) fewest non-zero weights, (3) selection stability across bootstraps |
| Uncertainty | none | bootstrap CI of J for top-5 / median / worst | bootstrap CI for all 100; "statistical tie set" = within one SE of the best |
| Transfer check | none | leave-one-dataset-out | same, and it must not reverse the choice |
| Data it is fitted to | none (no fitting) | 4 real models × 7 datasets × 40 items (1,120 pairs) | ≥ 8 models × 13 datasets × 100–150 items |
| Result | the weights were never tested; v1's leaderboard came from a simulated harness | NumTol .25, ROUGE-L .25, R .15, Edit .15, EM/NumDecay/P/Jaccard .05; J .476 vs .362 (EM), .429 (v1 rubric); bootstrap [.16, .50] | expected: a graded profile like v2's but with a narrow interval; the point is to make the interval, not the weights, publishable |
| What each does better | nothing to compute; instantly explainable | transparent, reproducible in a minute, honest about noise | statistically defensible; separates "which weights" from "does it matter" |

## B. Pooling per-dataset results into one leaderboard

| Aspect | v1 (original) | v2 (current) | Recommended next |
|---|---|---|---|
| Per-dataset score | mean of the rubric per dataset | mean calibrated composite per dataset | same |
| Common score | none across datasets (per-dataset tables only; TPC-DI has its own 100-point rubric) | mean over datasets, and difficulty-adjusted z-mean | z-mean as the headline number; plain mean beside it |
| Pooled rank | none | Borda (headline); mean-score, mean-z, mean-rank, Copeland, Kemeny–Young, RRF reported | Borda headline; Kemeny + Copeland as robustness; drop RRF and raw mean from the paper body |
| Dataset weights | — | equal (informativeness weights implemented, unused) | equal, plus informativeness-weighted Borda if saturated datasets stay in |
| Uncertainty | none | 1,000-resample item bootstrap → rank intervals and rank-probability matrix | keep; add Friedman test + Nemenyi critical-difference diagram |
| Strength score | — | — | Bradley–Terry fitted to item-level pairwise wins across datasets (score + standard error) |
| Agreement diagnostics | — | τ of each dataset with the pooled ranking; τ between rules; τ with native-metric and EM-only pooled rankings | same |
| Current result | — | gpt-5.5 > claude-opus-5 > claude-sonnet-5 > gpt-5.4-mini under every rank rule; only rank 1 separable | — |

## C. What changes materially if you follow the recommendation

1. **Noise stops deciding the winner.** With bootstrap-averaged J and a tie set, five combinations
   that currently share J = 0.476 would be reported as one equivalence class, and the choice inside
   it would be by the pre-registered secondary criteria rather than by a tie-break nobody planned.
2. **The leaderboard gets a significance statement.** A Nemenyi diagram says which adjacent ranks
   are indistinguishable at α = 0.05 across datasets; today the bootstrap interval says it only
   informally.
3. **A strength score with error bars.** Bradley–Terry gives "gpt-5.5 is stronger than opus with
   probability p" style statements, which reviewers accept more readily than rank tables.
4. **Nothing else moves.** The metric, the pools, the cache and the scripts stay; the changes are a
   few dozen lines in `02_random_search.py` (bootstrap-mean J, tie set) and `03_pool_report.py`
   (Friedman/Nemenyi, Bradley–Terry).
