# Under the hood: what every version computes, with the formulas, in plain words

The aim is that every version can be explained the way v1's formula can: "the score is this sum of these things".
Notation used throughout: model m, dataset d, item i, prediction p, gold answer g, M models, D datasets, n_d items.

---

## 0. The shared skeleton and what each stage proves

```
items (question, gold)  ->  model answer p  ->  per-answer score s(m,d,i)  ->  per-dataset score S_md
   ->  comparable across datasets  ->  one number / rank per model  ->  error bars
```
* s(m,d,i) is the grading rule; this is what the versions differ on.
* S_md = (1/n_d) Σ_i s(m,d,i) is a plain mean; every version uses it.
* "Comparable across datasets" is either ranks (order only) or z-scores z_md = (S_md − μ_d)/σ_d, where μ_d, σ_d are
  the mean and standard deviation of S_·d over models; a z of +1 means "one standard deviation above the average
  model on this dataset", so a hard and an easy dataset become comparable.
* Error bars come from the item bootstrap: resample the n_d items of each dataset with replacement, recompute
  everything, repeat B times, report the 2.5th and 97.5th percentiles.

Two recurring agreement measures:
* **Kendall τ** between two rankings of the M models: τ = (C − Dc)/√((n₀−n₁)(n₀−n₂)), C concordant pairs (ordered the
  same way in both), Dc discordant pairs, n₀ = M(M−1)/2 total pairs, n₁, n₂ pairs tied in each ranking. With M = 4,
  n₀ = 6, so τ moves in steps of 1/6: coarse.
* **Spearman ρ** between two lists of numbers: Pearson correlation of their ranks; used to ask "does the score go up
  when the true quality goes up".

Pooling per-dataset rankings σ_d into one:
* **Borda**: b(m) = Σ_d (M − σ_d(m)); rank by b. Equivalent to mean rank.
* **Kemeny–Young**: the ordering π minimising Σ_d d_K(π, σ_d), d_K = number of discordant pairs; found by trying all
  M! orderings (24 for M = 4). The "least disagreeing" consensus.
* **Copeland**: for every pair (m, k), m wins if S_md > S_kd on more than half the datasets; score = wins − losses.

---

## 1. v1 — the original judge (`other_older_versions/v1/`)

**Grading rule.** For each answer, four ingredients in [0,1]:
* token precision P = |tokens(p) ∩ tokens(g)| / |tokens(p)|; recall R = same / |tokens(g)|; F1 = 2PR/(P+R)
* MRE = |p_num − g_num| / |g_num| on the first number found; decay = exp(−2.5·MRE)

then  **R_v1 = 0.35·F1 + 0.35·decay + 0.15·P + 0.15·R**.

**What it tests.** Nothing beyond the formula: the four weights were chosen by hand and no data checks them.
**What went wrong.** The number extractor took the *first* number in a sentence, gold handling ignored aliases and
units, two dataset loaders produced wrong golds, and the shipped leaderboard came from a script that drew random
numbers instead of calling models. **Keep from v1:** the four ingredients are sensible, and the TPC-DI rubric
(points for columns, rows, coverage, 1 % numeric matches, string matches) is fine.

---

## 2. v2 — grid search over v1's own weights (`other_older_versions/v2_gridsearch_v1_rubric/`)

**Same ingredients, searched weights.** R_w = w₁·F1 + w₂·decay + w₃·P + w₄·R with w on the simplex Δ³ (w ≥ 0,
Σw = 1). Candidates: v1's (0.35, 0.35, 0.15, 0.15), the four corners (one ingredient only), and 100 random points on
the step-0.05 grid.

**Objective.** For each w: S_md → per-dataset ranking σ_d → Borda pool σ* → J(w) = (1/D) Σ_d τ(σ_d, σ*).
In words: "how much do the datasets agree on the model order under these weights". Also reported:
τ_native = (1/D) Σ_d τ(σ_d, σ_d^native), agreement with each dataset's own metric.

**Result.** v1's point ranks 35th of 105; the best (F1 0.85, P 0.05, R 0.10, decay 0) gains +0.078 in J, inside
the bootstrap interval. Decay gets no weight: on these datasets F1 already orders numeric answers and decay gives
credit to wrong numbers elsewhere.
**Pros.** Minimal, transparent, directly comparable with v1. **Cons.** The objective rewards "datasets agree", which
a bland metric satisfies too; with 4 models, no weighting is statistically better than another.

---

## 3. v3 — aggregation methods from the literature (`other_older_versions/v3_literature_aggregation/`)

**Different question: keep each dataset's own metric, and ask how to combine datasets.** s(m,d,i) is the native
metric (yes/no accuracy, exact match, 1 % numeric tolerance, ROUGE-L). Eight *views* map the table S_md to one
number per model, each from a published paper (formulas in `other_older_versions/v3_literature_aggregation/notes/02_MATH.md`):
raw mean; baseline-normalised mean (S_md − b_d)/(1 − b_d) with b_d the random-guess score; z-mean; mean win rate
(fraction of other models beaten per dataset); Borda; Kemeny score; Bradley–Terry strength β_m fitted so that
P(m beats k on an item) = σ(β_m − β_k); IRT ability θ_m fitted so that P(m gets item i right) = σ(θ_m − b_i).

**Grid search over the mix.** score_w(m) = Σ_v w_v·z_v(m), w on Δ⁷; 109 candidates. Objective from the reliability
papers: J = 0.5·stability + 0.25·transitivity + 0.25·reference, where stability = mean τ between the ranking on a
bootstrap resample and on the full data (100 resamples, views refitted each time), transitivity = τ to the
Copeland ranking, reference = τ to the Kemeny consensus of the eight single-view rankings.

**Result.** Pure Bradley–Terry is the most reliable mix (J 0.87), then Kemeny and IRT; raw and baseline-normalised
means are least stable (0.55, 0.46). Views agree on the winner and disagree on the middle: raw means put
claude-sonnet-5 last, every rank- or pair-based view puts it second, which is the arithmetic-mean fragility the
Colombo paper describes.
**Pros.** No composite to defend; every rule has a citation; the objective is reliability, not agreement.
**Cons.** Native metrics differ in kind across datasets (a 1 on FeTaQA's ROUGE-L is not a 1 on TabFact's accuracy),
and Bradley–Terry / IRT need many items and models to be well determined.

---

## 4. v4 — random search with a rank-agreement objective (`other_older_versions/v4_random_search_rank_agreement/`, was v2)

**Grading rule.** Nine metrics (EM, numeric tolerance, numeric decay, P, R, F1, edit similarity, ROUGE-L, Jaccard)
with gold aliases, unit/percent-aware numbers and set-equality for list golds:
s_w(m,d,i) = Σ_k w_k·metric_k(p, g), w on Δ⁸.
**Search.** 100 random points on the step-0.05 grid, scored by the same J as v2 (mean τ to the Borda-pooled
ranking), tie-break by mean pairwise τ between datasets; bootstrap of J; leave-one-dataset-out (choose w without
dataset d, test on d).
**Pooling.** Borda headline; Kemeny, Copeland, RRF (Σ_d 1/(60 + σ_d(m))), mean-z, mean-score as checks; 1,000
item bootstraps for rank intervals.
**Result.** Best w: NumTol 0.25, ROUGE-L 0.25, Recall 0.15, Edit 0.15, small rest; J 0.476 vs 0.362 for EM alone,
with the top five candidates tied and a bootstrap interval [0.16, 0.50].
**Pros.** Reproducible recipe; standard pooling and uncertainty; the divergence extension (JS/KL/Wasserstein
between datasets' score distributions) is documented separately. **Cons.** Circular: the judge is tuned on the
models it ranks; τ is coarse with 4 models.

---

## 5. v5 — 100-metric library calibrated on answers of known quality (`other_older_versions/v5_metric_library_anchor_ensemble/`, was v3)

**Library.** 100 metrics m_k(p, g) ∈ [0,1] in twelve families (exact-match variants, numeric tolerance ladder
0.1–20 %, graded numeric error for five steepness values, token/n-gram overlap, character similarity, ROUGE/BLEU-
style, set overlap, structure, length, commitment, task-specific, optional semantic). Percent equivalence only when a
% sign or a fraction in (0,1) is involved, so a 100× error is never free.

**Anchors.** For every gold g and every applicable operator o, a synthetic answer a_o(g) with a known utility u_o:
identity / verbose / tagged 1.0, paraphrase 0.95, unit variant 1.0, near miss 0.75 / 0.45 / 0.15, digit typo 0.2,
magnitude or sign error 0.05, partial 0.5, superset 0.6, typo 0.6, shuffled 0.4, hedge 0.3, list dump 0.25, flip /
abstain / random wrong 0. 12,813 anchors over 14 datasets, needing no model.

**Selection.** (i) drop constant metrics; (ii) cluster by |Spearman| ≥ 0.95 across anchors, keep one per cluster
(100 → 42); (iii) candidates need ρ(metric, u) > 0.05 and AUC > 0.55 and must not be indicator families (those are
1 for most wrong answers and would act as a constant offset); (iv) forward selection: add the metric that most raises
the leave-one-dataset-out Spearman between a non-negative least-squares fit Σ_k c_k m_k and u; stop when the gain
< 0.002. Kept: token F1, numeric decay exp(−2.5·RE), bigram recall.

**Grid and gate.** s_{w,λ}(p,g) = (Σ_k w_k m_k(p,g)) · (1 − λ·hedged(p)), w on the step-0.02 simplex over the 3
metrics, λ ∈ {0, .25, .5, .75, 1}: 6,630 candidates. Objective on anchors and models:
J = 0.30·ρ(s, u) + 0.15·AUC(correct vs wrong) + 0.20·(1 − JS_×/ln 2) + 0.15·τ_native + 0.20·(1 − mean s over wrong anchors),
where JS_× is the Jensen–Shannon divergence between datasets' score histograms at the same operator (same error
type should get the same score spread everywhere) and τ_native the agreement with each dataset's own metric on the
real models. **Ensemble:** keep the 100 best (w, λ); the answer's score is their mean; their spread is the
weighting's error bar. Ensemble mean: decay 0.81, F1 0.16, bigram recall 0.03, λ 0.63.

**Leaderboard.** S_md of the ensemble score → z → equal dataset weights → Borda with Kemeny check → item
bootstrap → rank range across the 100 weightings → native ranking beside.

**Validation.** Leave-one-dataset-out (held-out ρ 0.895 vs 0.900); utility scale perturbed ±0.15 (weights move
L1 0.17 on a 0–2 scale); per-operator table (wrong answers 0.02, hedges 0.22, near misses 0.78/0.64/0.33).
**Pros.** Calibrated against known quality, never against the ranked models; wrong answers score ≈ 0; transfers
to unseen datasets; selection explains which of 100 metrics matter. **Cons.** The utility scale is ours (human
labels can replace it); lexical only; the native typed metric ties the ensemble on the combined objective because
it wins the native-fidelity term by construction; 4 models × 40 items.

---

## 6. Side by side

| | v1 | v2 | v3 | v4 | v5 |
|---|---|---|---|---|---|
| per-answer rule | 4 metrics, hand weights | 4 metrics, searched | dataset's own metric | 9 metrics, searched | 3 of 100, searched, ensemble, hedge gate |
| what is searched | nothing | 4 weights | mix of 8 aggregation views | 9 weights | 3 weights + λ |
| objective | none | datasets agree (τ to Borda) | stability + transitivity + consensus | datasets agree (τ to Borda) | anchor ρ, AUC, JS consistency, native τ, wrong→0 |
| checked against | nothing | the ranked models | bootstrap resamples | the ranked models | synthetic answers of known quality |
| main risk | unjustified | circular | metrics differ in kind | circular | hand-set utility scale |

All five run on the same cached answers (4 models × 7 datasets × 40 items), so their leaderboards are comparable;
with that little data only the top rank is ever established, which every version's bootstrap shows.
