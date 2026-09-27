# How each version searches its weights: candidate generation, step by step

Scope: the exact mechanics of candidate generation and evaluation in v2, v3, v4 and v5, read from the code on 2026-09-23
(`other_older_versions/v2_gridsearch_v1_rubric/scripts/02_gridsearch.py`, `other_older_versions/v3_literature_aggregation/scripts/02_gridsearch_views.py`,
`other_older_versions/v4_random_search_rank_agreement/scripts/rs/02_random_search.py`, `other_older_versions/v5_metric_library_anchor_ensemble/scripts/03_grid_weights.py` and
`src/calibration/grid.py`). Short answer: v2, v3 and v4 draw random points from a fixed lattice on the simplex; only v5 sweeps its lattice
exhaustively. None of the four refines around a winner or runs a second stage.

## 1. The shared lattice

Every version restricts a weight vector w to the simplex (w_k ≥ 0, Σ w_k = 1) and to a lattice with a fixed step s: every vector whose entries
are multiples of s and sum to 1. The code enumerates the lattice by stars-and-bars: choose K − 1 cut positions among 1/s + K − 1 slots
(`simplex_grid(K, step)`), which lists all compositions of 1/s into K non-negative parts.

| K | step | lattice size |
|---|---|---|
| 4 (v2) | 0.05 | 1,771 |
| 8 (v3) | 0.05 | 888,030 |
| 9 (v4) | 0.05 | 3,108,105 |
| 3 (v5) | 0.02 | 1,326 (× 5 hedge values = 6,630) |

## 2. v2: four v1 rubric weights, 105 candidates

1. Enumerate the full 1,771-point lattice (K = 4, s = 0.05).
2. Draw 100 of them uniformly at random **without replacement**, seed 20260909 (`rng.choice(len(G), 100, replace=False)`).
3. Prepend the v1 point (0.35, 0.35, 0.15, 0.15) and the four corners (`np.eye(4)`): 105 candidates, labelled `v1_original`, `only_<metric>`,
   `random_000…099`.
4. For each candidate: S = w · [F1, decay, precision, recall] per answer; mean per (model, dataset); Borda-pool the per-dataset rankings;
   J = mean over datasets of Kendall τ between the dataset's ranking and the pooled ranking; also τ to the native metric, minimum agreement,
   mean pairwise τ, scale dispersion.
5. Sort by (J, τ_native) descending. Bootstrap (200 item resamples per dataset, Borda recomputed) only for ranks 1–5, the v1 row and the worst row.
6. No refinement, no local search, no second stage.

## 3. v3: eight aggregation views, 109 candidates

1. Same lattice construction at K = 8, s = 0.05 (888,030 points).
2. 100 random draws without replacement, same seed, plus the eight corners (`np.eye(8)`) and the uniform mix (all 1/8): 109 candidates.
3. Weights apply to the z-scored view table Z (models × 8 views), not to metrics: mixed score = Z · w, ranking = ranks of that score.
4. J = 0.5 · stability + 0.25 · transitivity + 0.25 · reference, where stability = mean τ between the mixed ranking on 100 item-bootstrap
   resamples and on the full data; transitivity = τ to the Copeland ranking of the per-dataset score table; reference = τ to the Kemeny consensus
   of the eight single-view rankings.
5. Coverage: 100 of 888,030 lattice points (0.01 %). The winner is a corner (pure Bradley–Terry) because corners are in the candidate set by
   construction and random draws almost never land near them.

## 4. v4: nine metric weights, 100 candidates (Dirichlet snapped to the lattice)

1. The lattice is **not** enumerated (3.1 million points). Instead `sample_grid_weights(100, 9, 0.05, rng)`:
   * draw p ~ Dirichlet(1, …, 1), which is uniform on the continuous simplex;
   * c = floor(20 · p) per entry; then hand the leftover units (20 − Σ c) one at a time to the entries with the largest residual 20·p − c,
     so the total is exactly 20;
   * reject duplicates until 100 distinct lattice points exist; w = c / 20.
2. Objective as in v2 with nine components (EM, numeric tolerance, numeric decay, precision, recall, F1, edit similarity, ROUGE-L, Jaccard):
   J = mean τ to the Borda-pooled ranking; also τ to Kemeny, mean pairwise τ, minimum agreement, scale dispersion, Borda-vs-Kemeny agreement.
3. Sort by (J, mean pairwise τ). Bootstrap (200) for the top 5, the median and the worst.
4. Five fixed baselines evaluated with the same J: EM only, F1 only, numeric tolerance only, the v1 rubric, uniform.
5. Leave-one-dataset-out: for each dataset d, re-pick the best w without d, then report τ of d's ranking to the pooled ranking of the rest,
   under the LODO weights and under the full-data weights.

## 5. v5: three selected metrics plus a hedge penalty, 6,630 candidates, exhaustive

1. Metric selection first reduces the 100-metric library to three (token F1, numeric decay 2.5, bigram recall).
2. Step chosen by K: 0.02 if K ≤ 3, 0.05 if K ≤ 6, else 0.1. With K = 3 the full lattice at 0.02 has 1,326 points.
3. `with_gate` crosses every lattice point with five hedge-penalty values λ ∈ {0, 0.25, 0.5, 0.75, 1}: 6,630 candidates. Score per answer =
   (w · metrics) · (1 − λ · hedged).
4. Every candidate is evaluated on the synthetic anchors (12,813 answers of known utility): Spearman ρ to utility; AUC correct vs wrong;
   1 − JS/ln 2 between datasets at matched operator; τ to the native model ranking; wrong-answer score. Objective
   J = 0.30 ρ + 0.15 AUC + 0.20 (1 − JS/ln 2) + 0.15 τ_native + 0.20 (1 − wrong).
5. The 100 best by J are averaged into the ensemble (decay 0.81, F1 0.16, bigram recall 0.03, λ 0.63); `grid_all.csv` keeps all 6,630 with
   every term; `baselines_grid.csv` scores single metrics, uniform and the ensemble with the same objective.

## 6. Consequences for the v6 revision

* v2 and v3 are uniform draws from a lattice; v4 is Dirichlet snapped to it. None is stratified, so candidates can cluster while regions go
  unvisited. The Latin hypercube design (k stratified uniforms through the exponential inverse CDF, normalised to sum to 1, snapped to the same
  lattice) covers every marginal evenly at the same budget of 100; both designs will be run and compared (centred discrepancy, minimum pairwise
  distance, best J).
* v3's coverage (100 of 888,030) is the weakest; enumerating all 255 equal-weight view subsets adds every corner, edge and face of that simplex,
  which random draws essentially never reach.
* v2 and v4 bootstrap only 7 candidates; the significance module extends the bootstrap and a paired test to the whole top 10, so a "top five tie"
  claim has a p-value behind it.
* v5's search is already exhaustive; the LHS run there is a coverage check, not a replacement.
* Every version fixes its seed and saves every candidate with its objective terms; the per-combination parameter dump extends those files
  rather than replacing them.
