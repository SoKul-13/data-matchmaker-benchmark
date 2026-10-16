# Paper plan: "Auditing a deployed LLM judge: is any weighting of its ingredients better than the one it ships with?"

Target: an evaluation / benchmarking workshop (e.g. the NLP evaluation workshops at ACL/EMNLP, the data-management "DEEM"/"GUIDE-AI"-style
workshops, or an LLM-evaluation track). 4–8 pages plus appendix. Lead contribution: the *audit procedure* and its negative result, on a
31-dataset data-matching suite with 10 models. Everything below maps to files in `FINAL_v2/`.

## 1. What to do, in order
1. Freeze the numbers: `v2_gridsearch/REPORT.md` (2026-09-27 13:12) is the source of every figure and table; do not re-run before submission
   unless Gemini Pro completes, in which case re-run and update every number together.
2. Fix the two small objective-side gaps or state them as limitations (ceiling datasets inside the objective; exact match as the native metric for
   boolean sets). Stating is acceptable for a workshop paper; fixing is half a day.
3. Run the two optional checks if time allows: the 3× repeat subset (answer variance for the models that refuse temperature 0, ≈ USD 4) and the
   50-answer hand check of the extraction fallback. Both become one sentence each in Limitations.
4. Write the draft from `paper/draft.md` (below), replacing the bracketed notes; typeset in the venue template; figures are in `paper/figures/`,
   LaTeX tables in `v2_gridsearch/output/leaderboards/<rule>/table.tex`.
5. Release: the repository with `FINAL_v2/` (pools, cached answers, scripts), which makes the paper reproducible from cache in minutes.

## 2. Figures (all exist in `paper/figures/`)

| File | What it shows | Where it goes | Caption gist |
|---|---|---|---|
| `fig_j_histogram.png` | distribution of J over all 1,771 weightings, v1, the best, the plateau band | Fig. 1 (results) | the whole lattice spans 0.39–0.42; v1 is inside the plateau |
| `fig_landscape.png` | sorted J with v1 and the four corners | appendix or Fig. 1 alternative | same message as a curve |
| `fig_marginals.png` | J against each of the four weights | appendix | no weight has a slope worth acting on |
| `fig_nested.png` | in-bag vs out-of-bag J of the selected weighting vs v1 | Fig. 2 (honesty) | the optimism gap (0.049) and the overlap with v1 |
| `fig_plateau.png` | bootstrap band over sorted weightings with the plateau boundary | Fig. 2 companion or appendix | 1,765 of 1,771 are equivalent |
| `fig_pareto.png` | agreement J vs anchor correctness ρ for every weighting | Fig. 3 (correctness) | the two criteria are not aligned; v1 is near the ρ optimum |
| `fig_leaderboard_rules.png` | Bradley–Terry strengths ± SE with rank intervals under exact match / v1 / best | Fig. 4 (leaderboard) | ends are stable, the top order is rule-dependent |
| `fig_official_split.png` | suite score vs post-stratified official estimate; EM F1 at the official match ratio | Fig. 5 (comparability) | balanced pools inflate matching F1 by up to 0.6 |
| `fig_family_weights.png` | deployed vs global optimum vs per-family optima | Fig. 6 (transfer) | families pull in different directions; none is far from the plateau |
| `fig_dataset_tau.png` | Kendall τ between dataset rankings | appendix | datasets agree only moderately (W ≈ 0.27) |
| `fig_designs.png` | sampled designs vs the exhaustive optimum | appendix | any 100-point design finds the plateau |

## 3. Tables
* T1 Suite: 31 datasets by family with item counts, licence, official population size (from `TOP30_DATASETS_AND_PRE_RUN_NOTES.md` and `data/pool/_official_strata.json`).
* T2 Models and run facts: 11 models, decoding (temperature accepted or refused), truncation re-asks per model, cost (`data/predictions/`).
* T3 Audit summary: J of v1 / best / corners; plateau size; nested in-bag vs out-of-bag; LODO / LOFO τ; anchor ρ and AUC (`best.json`, `selection/nested.json`, `selection/lodo.csv`, `anchors/correctness.json`).
* T4 Leaderboard under three rules with BT rank intervals, Friedman and Holm results (`leaderboards/<rule>/leaderboard.csv`, `significance.json`, `table.tex`).
* T5 Official-split estimates for the matching sets: suite accuracy, official F1 with interval (`leaderboards/v1_original/official_split_estimates.csv`).

## 4. Explanations the reader needs (one paragraph each)
* Why a composite needs weights, and why hand-set weights are suspect (v1's rule, the four ingredients).
* Agreement vs correctness: J measures whether datasets rank models consistently; the anchors measure whether the rule scores answers right.
  They answer different questions and the paper keeps them apart.
* Why exhaustive: 1,771 lattice points make the claim exact; the sampled designs are shown only to say sampling would have sufficed.
* The winner's curse and the nested bootstrap: select in-bag, score out-of-bag; the optimism gap is the measured size of the curse.
* The plateau: a set of weightings not distinguishable from the best; a flat objective means rank is noise.
* Post-stratification: the same answers re-weighted to the official stratum proportions, so per-dataset numbers are comparable to published ones.
* The truncation protocol: four budgets (700 / 2,500 / 8,000 / 16,000), mechanical trigger, archived originals, tagged replacements; budgets are provider tokens and include chain of thought; persistent non-termination at 16,000 is a model property (DeepSeek-R1 on OfficeQA and BIRD).

## 5. Comparisons to make
* v1 vs best-J vs best-ρ vs exact match (the four rules), on J, ρ, AUC, and the leaderboard they induce (rule-agreement τ matrix).
* Borda vs Bradley–Terry vs Kemeny / Copeland / mean-z pooling on the same scores (the order at the top changes; the ends do not).
* Suite score vs official-split estimate (accuracy) and balanced-pool F1 vs official-ratio F1 (matching sets).
* Global vs per-family optimum vs v1 (transfer).
* Exhaustive vs sampled designs (regret ≤ 0.005).
* Optional, from the sibling pipelines on the same answers: v4 (nine components, best = numeric tolerance alone) and v3 (view mixes vs pure BT);
  one paragraph each in Discussion, or an appendix.

## 6. Papers to reference (and what for)
* Demšar 2006, JMLR — Friedman / Nemenyi across datasets; García & Herrera 2008, JMLR — Holm post-hoc. (significance)
* Cawley & Talbot 2010, JMLR; Varma & Simon 2006 — selection bias / nested CV. (winner's curse)
* Chiang et al. 2024 (Chatbot Arena), ICML — Bradley–Terry with bootstrap CIs. (headline pooling)
* Colombo et al. 2022, NeurIPS — Kemeny / Borda for NLP benchmarks. (aggregation)
* Liang et al. 2022 (HELM) — mean win rate, per-scenario native metrics. (aggregation; suite design)
* Perlitz et al. 2024 (Efficient Benchmarking; BenchBench) — benchmark agreement testing, reliability. (dataset agreement, W)
* Boubdir et al. 2023, "Elo Uncovered" — transitivity / reliability of pairwise ratings. (pooling caveats)
* Polo et al. 2024 (tinyBenchmarks), ICML — IRT, 100 items suffice. (item count)
* Card et al. 2020, EMNLP — statistical power in NLP evaluation. (item count)
* Bouthillier et al. 2021, MLSys — sources of variance in ML benchmarks. (decoding, repeat subset)
* Mathur et al. 2020, ACL ("Tangled up in BLEU"); Kocmi et al. 2021, WMT — metric meta-evaluation against external quality. (anchors)
* Koehn 2004; Dror et al. 2018, ACL — paired bootstrap / permutation for per-item comparisons.
* McKay, Beckman & Conover 1979; Bergstra & Bengio 2012 — Latin hypercube and random designs. (design comparison)
* Papadakis et al. 2024, ICDE — class imbalance in entity-matching benchmarks. (post-stratification motivation)
* Peeters & Bizer 2024 (WDC Products); Koutras et al. 2021 (Valentine); Mudgal et al. 2018 (DeepMatcher); Li et al. 2020 (Ditto) — the matching suite.
* Zheng et al. 2023 (MT-Bench / LLM-as-a-judge) — judges need validation. (framing)
* Renze & Guven 2024 — temperature and accuracy. (decoding)

## 7. Venue-fit framing
The result is negative in the best sense: a deployed judge's hand-set weights survive an exhaustive, honest audit. Workshop reviewers reward
(a) the procedure being reusable, (b) uncertainty reported properly, (c) reproducibility from cache. Lead with those; do not oversell the
leaderboard.
