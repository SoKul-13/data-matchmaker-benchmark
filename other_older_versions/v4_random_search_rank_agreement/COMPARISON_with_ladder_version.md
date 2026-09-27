# This version (v2) vs the earlier ladder version — two calibration designs for the same green agent

Both folders start from the original `data-matchmaker-benchmark` (v1), replace its hand-set
rubric `R_custom = .35·F1 + .35·exp(-2.5·MRE) + .15·P + .15·R`, and share the same component
metric library (`src/metrics/`: 9 components, gold aliases, unit-aware numbers, list golds) and the
same rank-aggregation code. They differ in **what "calibrated" means, how the weights are searched,
and what the search is scored against**. this version also reuses the ladder version's cached real-model predictions, so it
cost no new API calls.

| | **Ladder version** (earlier ladder build, archived) | **v2** (this folder) |
|---|---|---|
| Goal | Metric behaves the same on every dataset for the *same answer quality* (metric-level invariance), then rank models | One common score such that datasets *rank models the same way* (leaderboard-level agreement) |
| Datasets | 10: the 7 original + TabMWP, GSM8K, BoolQ (added as numeric / boolean anchors) | 7: exactly the original catalogue (diverse and standard) |
| Weights | 4 vectors (numeric / boolean / text / free-form) + a calibrated hedge penalty λ | 1 global vector, no hedge gate |
| Search | Exhaustive simplex grid: 218,790 candidates per type, then hill-climb refinement | Random search: 100 combinations drawn from the step-0.05 grid, as requested |
| Calibration target | Synthetic "controlled-severity ladder": 60 systems of *known* quality per dataset + gaming probes, with an explicit error-severity scale | Real models only: mean Kendall τ between each dataset's model ranking and the pooled Borda ranking |
| Objective terms | 9 terms: order recovery, Spearman/MAE to severity, **JS divergence** across datasets and styles, native-metric fidelity, range, probe terms | 1 term (rank agreement); pairwise τ and score dispersion reported alongside |
| KL / JS divergence | Implemented inside the objective (JS optimised; KL, Wasserstein reported) | Kept **out** of the pipeline: standalone `extensions/divergence_extension.py` + write-up |
| Validation | α-sensitivity, severity-scale perturbation, leave-one-dataset-out, gaming probes | Bootstrap CIs on J, leave-one-dataset-out |
| Green agent | New QA mode scoring any dataset with calibrated weights (A2A end to end) | Unchanged v1 agent; calibration is an offline analysis |
| Runtime | ~35 min calibration + ~15 min API run | ~1 min from cache |
| Paper | 10 pages, 6 figures, 13 tables | 5 pages, 2 figures, 6 tables |

## What each does better

**The ladder version is better at making the metric itself trustworthy.** Because it scores against systems whose
quality is *known by construction*, it can say things a real-model objective cannot: that a 2 %
numeric miss and a partial list get comparable credit on FinQA and WTQ, that verbose or
differently-formatted correct answers are not penalised (probe terms), that hedging is detected,
and that the weights transfer to a held-out dataset. Its distribution-matching (JS) term is a real
consistency measure because "same quality" is observable. It also found and fixed the degenerate
solutions (constant-offset components, binary indicators winning JS trivially) that any
divergence-based objective must guard against. The cost is complexity: an explicit severity scale
and nine mixing coefficients that are choices, per-type weights, and a long paper.

**v2 (this folder) is better at answering the question as posed.** It uses only the original, well-known datasets,
a single transparent weight vector, a search with exactly 100 combinations, and an objective that is
literally "make the datasets agree on the model ranking, then pool the rankings". It is fast,
reproducible from cache, easy to explain in a talk, and its leaderboard is the direct deliverable
(common score + Borda/Kemeny/RRF ranks with bootstrap intervals). Its weakness is statistical: with 4
industry-standard models (7 real models in the ladder version) and 40 items per dataset, per-dataset rankings are noisy under *any*
weighting (mean pairwise τ ≈ 0.04), so the gain from 0.36 (EM) to 0.48 sits inside the bootstrap
interval and LODO transfer is weak. v2 reports this plainly rather than hiding it; the fix is more
items and more models, which the pipeline accepts without code changes.

**Which to use.** For the paper's core claim (one common score across the original datasets, weights
chosen by random search, rankings pooled), use this folder and cite the ladder version as the principled extension
for validating the metric. If the reviewer asks "how do you know the metric is fair across
datasets?", the ladder machinery (synthetic known-quality systems, JS/KL/W1, probes) is the answer, and
the `extensions/` write-up here already points there.
