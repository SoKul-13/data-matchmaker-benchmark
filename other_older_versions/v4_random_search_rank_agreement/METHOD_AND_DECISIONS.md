# What was done, and why every choice was made

This is the single place that records the full story of the v2 calibration: the goal, what was
found in v1, every design decision with the reason behind it, the alternatives that were tried or
rejected, the exact results, and what they do and do not show. Numbers come from `output/rs/`
(regenerate with `scripts/rs/run_all.sh`).

---

## 1. The goal

Produce **one common score** for LLMs across the benchmark's data-matching datasets, so that
per-dataset results can be pooled into a single leaderboard. Concretely:

1. use the datasets already in the original (v1) catalogue, which are diverse and widely used;
2. keep the idea of a composite answer metric (a weighted sum of component metrics) but **choose the
   weights by a random search over 100 combinations on a grid**, not by hand;
3. define "calibrated" as: under these weights, the datasets rank the models consistently, so that
   **pooling the per-dataset rankings** (Borda and other ensemble rules) is meaningful;
4. keep Kullback–Leibler / Jensen–Shannon divergence as a documented **extension**, not part of the
   pipeline.

---

## 2. What was found in v1 before anything was built

Reading the original folder showed three things that shaped every later decision.

| Finding | Consequence |
|---|---|
| The v1 leaderboard was produced by `scripts/benchmark_harness.py`, which **simulated** model answers (`random.random() < base_accuracy` and a noisy copy of the gold). No API was called. | All model results in v2 come from real API calls, with the raw outputs cached in `data/predictions/` so they can be audited and reused. |
| The v1 rubric `R_custom = 0.35·F1 + 0.35·exp(−2.5·MRE) + 0.15·P + 0.15·R` had hand-set weights with an after-the-fact "Lipschitz bound" justification. | Weights are treated as unknowns and selected by an explicit, reproducible search against an explicit objective. The v1 rubric is kept as a baseline. |
| Two adapters produced wrong gold answers: TAT-QA golds were `str(list)` (e.g. `"['$1,496.5']"`) and FinQA used only the program result (`0.14464`) although the human answer is `14%`. TabFact statements were sent without the table. | Adapters were fixed (aliases, scale-aware numbers, list golds, per-item table fetch) before any scoring. Without this, every metric would have been scored against broken references. |

---

## 3. Datasets: which and why

Seven, all from the v1 catalogue. They were kept because each is a standard, heavily cited
benchmark and together they cover the modalities and answer types a data-matching judge meets.

| Dataset | Modality | Answer types | Why it is in |
|---|---|---|---|
| OfficeQA (Databricks) | document QA, Treasury bulletins | numeric, some lists | the benchmark's own headline task; closed-book here because the corpus is gated on Hugging Face |
| FinQA | SEC 10-K table + text | numeric | canonical financial numeric reasoning |
| TAT-QA | financial table + paragraphs | numeric, span, multi-span, count | hybrid reasoning with mixed answer types |
| FinanceBench | 10-K/10-Q with evidence | numeric, text, free-form | long-document financial QA |
| TabFact | Wikipedia tables | boolean | fact verification, the only boolean task |
| FeTaQA | Wikipedia tables | free-form sentences | generative answers, the hardest case for lexical metrics |
| WikiTableQuestions | open-domain tables | short text, numbers, lists | the standard table-QA benchmark |

Sampling: 40 items per dataset, stratified by answer type / difficulty where the dataset has it,
fixed seed. 40 was the budget compromise for running eleven models; it is the main limitation
(Section 9).

Rejected: adding GSM8K, TabMWP and BoolQ (they were used in the earlier ladder version as numeric
and boolean anchors). They are not data-matching tasks, and the instruction was to use the original
catalogue.

---

## 4. Models: which and why

Policy: **industry-standard models only, the flagship and the standard tier of each major provider**.
No small or deliberately weak models.

| Provider | In results now | In catalogue, waiting on a key |
|---|---|---|
| OpenAI | GPT-5.5, GPT-5.4-mini | |
| Anthropic | Claude Opus 5, Claude Sonnet 5 | |
| Google | | Gemini 3.1 Pro, Gemini 3.8 Flash (key present, free-tier quota exhausted) |
| xAI | | Grok-4 (key present, no credits) |
| Meta / DeepSeek / Alibaba / Mistral | | Llama-3.3-70B, DeepSeek-V3, DeepSeek-R1, Qwen-2.5-72B, Mistral Large |

Earlier runs also covered GPT-4.1-mini, GPT-5-mini and Claude Haiku 4.5; their predictions are
parked in `data/predictions/_excluded/` after the policy decision. Every model was queried once per
item with the same prompt (context, rendered table, question, a one-line answer-format instruction,
and a required `FINAL ANSWER:` line); reasoning effort was set to low where the API exposes it.
`config/models.toml` auto-skips any model whose key is missing, so adding a provider is one line in
`.env`.

---

## 5. The metric: nine components, and why these

The composite is `S(prediction, gold) = Σ_k w_k · m_k(prediction, gold)` with `w` on the simplex.

| Component | What it rewards | Why it is included |
|---|---|---|
| EM | exact match after normalisation | the strictest signal; what WTQ and TAT-QA spans officially use |
| NumTol | number within 1 % of the gold | what FinQA / TAT-QA arithmetic effectively use |
| NumDecay | `exp(−2.5·relative error)` | graded credit for near misses; the one non-linear piece of the v1 rubric worth keeping |
| P, R, F1 | token overlap | the v1 rubric's components; standard for spans |
| Edit | normalised Levenshtein similarity | tolerates typos and formatting differences that token metrics miss |
| ROUGE-L | longest-common-subsequence F | order-aware overlap, the standard for FeTaQA free-form answers |
| Jaccard | token-set overlap | order-free overlap; cheap complement to ROUGE-L |

Details that matter for fairness across datasets, all applied before any weighting:
- **Gold aliases**: FinQA `14%` and `0.14464`, TAT-QA values with and without their scale, WTQ
  `A|B` lists. Each component is the maximum over aliases.
- **Unit / percent equivalence** when comparing numbers (`0.145` ≡ `14.5%`, `1.2 billion` ≡ `1200000000`).
- **List golds** use set equality for EM.
- **Final-answer extraction** strips reasoning and scaffolding such as "the answer is …".
- For non-numeric golds the two numeric components fall back to EM, so every component is defined
  for every item and one global weight vector is well posed.

Decision: **one global weight vector**, not one per answer type. Reason: a single vector is the
transparent object the paper asks for and can be shown in one line; per-type vectors (used in the
ladder version) quadruple the parameters and need a type detector in the loop. Cost: numeric and
free-form items are scored by the same weights; this is visible in the selected weights (Section 7).

Rejected: a multiplicative hedge penalty (a factor `1 − λ` when the answer lists several candidates).
It was implemented in the ladder version and found to conflict with native-metric fidelity; it was
dropped here to keep the composite a plain weighted sum.

---

## 6. The calibration objective, and why rankings

For a candidate `w`:
1. score every (model, item) pair;
2. average per model per dataset → a 4 × 7 table;
3. rank the models within each dataset;
4. pool the seven rankings with a **Borda count** (each model receives `n − rank` points per dataset);
5. `J(w)` = mean over datasets of Kendall τ between the dataset's ranking and the pooled ranking.

Why this objective:
- It is literally "the datasets agree on who is better", which is the precondition for pooling
  rankings; the pooled ranking is then defensible as an ensemble.
- It is scale-free: a dataset at ceiling (TabFact) and one at floor (OfficeQA) contribute through
  their orderings, not their score levels.
- It uses real models only; nothing synthetic is defined.

Why Borda for the pooling inside the objective: it is the simplest positional rule, has no ties to
resolve by search, and (Section 8) agrees with Kemeny, Copeland, RRF, mean-rank and mean-z on this data.

What it does **not** do, deliberately, and what was added to compensate:
- It ignores score levels → a *scale-dispersion* statistic is reported (after removing each
  dataset's mean, how much a model's standing moves between datasets relative to the spread between
  models; lower is better).
- It could be satisfied by a metric that blurs real differences → *native-metric agreement* and
  *mean pairwise τ between datasets* are reported alongside.
- It treats every dataset and every model pair equally. Top-weighted τ and informativeness-weighted
  Borda exist in `src/pooling/rank_aggregation.py` but were not used, to keep the objective plain.

Rejected alternative (the ladder version): calibrate against synthetic systems of *known* quality
with an explicit error-severity scale and put JS divergence in the objective. It validates the metric
more rigorously but requires a hand-set severity scale and nine mixing coefficients, and its headline
numbers are about synthetic systems. It is kept as the documented extension.

---

## 7. The search: random search over 100 grid combinations

- Grid: every weight a multiple of 0.05; nine components → about 900,000 valid vectors, too many to
  inspect, so 100 are drawn.
- Draw: sample a uniform point on the simplex (Dirichlet(1)), snap to the grid preserving the sum,
  keep if new, until 100 distinct vectors exist. Seed 20260907, so the same 100 always come out.
- Score all 100 with `J`, sort by `J` and, for ties, by mean pairwise τ between datasets.
- Bootstrap `J` (200 item resamples) for the top five, the median and the worst combination.
- Baselines under the same objective: EM only, F1 only, NumTol only, uniform, v1 rubric.

### Result

| Weights | J |
|---|---|
| EM only | 0.362 |
| NumTol only | 0.359 |
| v1 rubric | 0.429 |
| Uniform | 0.429 |
| Token-F1 only | 0.459 |
| **Random-search best** | **0.476**, bootstrap 95 % CI [0.16, 0.50] |
| median of the 100 | 0.381 |
| worst of the 100 | 0.180 |

Selected weights: **NumTol 0.25, ROUGE-L 0.25, Recall 0.15, Edit 0.15, EM 0.05, NumDecay 0.05,
Precision 0.05, Jaccard 0.05** (F1 0).

Reading: a firm numeric check (NumTol) for the numeric-heavy datasets, order-aware overlap
(ROUGE-L) plus recall and edit similarity for spans and sentences, and almost no strict exact match.
That is the profile one would expect from a metric that has to serve FinQA and FeTaQA with the same
weights.

Important honesty point: **the top five combinations tie at J = 0.476.** With four models, τ per
dataset takes only seven distinct values, so many weightings produce identical rankings. The best
was chosen by the tie-break (highest pairwise τ, 0.136 vs 0.12–0.13 for the others). The five share
the pattern above (NumTol or F1 plus ROUGE-L / edit / recall, little EM), so the interpretation does
not depend on which of them is called "best".

---

## 8. Pooling and the leaderboard

Under the selected weights:

| Model | Common score (mean over datasets) | Pooled rank (Borda = Kemeny = RRF) | 95 % CI of rank |
|---|---|---|---|
| gpt-5.5 | 0.564 | 1 | [1, 2] |
| claude-opus-5 | 0.534 | 2 | [1, 4] |
| gpt-5.4-mini | 0.521 | 4 | [2, 4] |
| claude-sonnet-5 | 0.513 | 3 | [2, 4] |

- All pooling rules except raw mean score give the same ranking (τ = 1 between Borda, Kemeny,
  Copeland, RRF, mean-rank, mean-z; 0.67 with mean score, which is pulled by dataset difficulty).
- Agreement of each dataset with the pooled ranking: FeTaQA 1.0, FinanceBench 1.0, WTQ 0.67,
  FinQA 0.33, OfficeQA 0.33, TabFact 0.0, TAT-QA 0.0. TabFact and TAT-QA are at ceiling for all four
  models, OfficeQA at floor; those three carry almost no ranking information at 40 items.
- Pooled ranking vs the native-metric pooled ranking: τ = 0.67; vs EM-only pooled ranking: 0.33.
- Bootstrap: only the top rank is separable; positions 2–4 overlap.

---

## 9. Validation, and what it says

- **Bootstrap of J**: [0.16, 0.50] for the best weights. EM-only (0.36) and all of the top ten lie
  inside it. The improvement over EM is real in direction but not statistically separable at this
  sample size.
- **Leave-one-dataset-out**: re-select the best combination without dataset *d*, then measure *d*'s
  agreement with the pooled ranking of the rest. Held-out τ: FeTaQA 1.0, FinanceBench 0.67, WTQ 0.67,
  FinQA 0.33, OfficeQA 0.0, TAT-QA 0.0, TabFact −0.22; identical to the full-data weights on six of
  seven datasets (the selected vector shifts by L1 = 0 in six cases). The weights are not fitted to
  any single dataset, but the three saturated datasets do not transfer under any weights.
- **Divergence extension** (`extensions/divergence_extension.py`, run on the cached scores): mean
  JS/ln 2 between datasets, difficulty-centred, is 0.86 for EM, 0.77 for the v1 rubric and 0.78 for
  the selected weights. Graded metrics give more comparable score profiles than EM; the ranking
  objective alone does not reduce divergence further, which is the argument for adding the term if
  score-scale comparability is a requirement. It is not added because a binary metric can reach low
  divergence by failing uniformly, so the term needs an anchor (the ranking term, or the ladder).

Bottom line: the pipeline does what it should and the selected weights are sensible and
interpretable, but with four closely matched models and 40 items per dataset the datasets barely
agree on the model ordering under *any* weighting (mean pairwise τ 0.14 for the best weights, 0.05
for EM). The remedy is more models across providers (the catalogue is ready; Gemini needs billing,
Llama needs a free Groq key) and more items per dataset; both require no code changes.

---

## 10. Timeline of what happened

1. Read v1; found the simulated harness, the hand-set rubric and the adapter bugs (Section 2).
2. Built the metric library (Section 5) and the real inference layer; ran eleven models on ten
   datasets; Gemini's key hit its quota after 15–25 % of items and xAI had no credits.
3. First calibration design ("ladder version"): synthetic known-quality systems, exhaustive simplex
   grid, JS/KL/Wasserstein in the objective, per-type weights, hedge gate, QA-mode green agent,
   10-page paper. Archived outside the repo (`data-matchmaker-benchmark-v2` sibling folder).
4. Re-specified goal (this document): original seven datasets, one global vector, random search of
   100 grid combinations, ranking-agreement objective, rank pooling; divergence as an extension only.
   Built as `scripts/rs/00–03` reusing the cached predictions.
5. Model policy narrowed to flagship + standard tier per provider; small models parked; all
   numbers, the paper and the docs regenerated for the four remaining models.
6. Repo restructured: `v1/` original, `v4_random_search_rank_agreement/` this work.

---

## 11. Reproduce

```bash
cd v2 && uv sync
scripts/rs/run_all.sh          # 01 prepare -> 02 random search -> 03 pooling/report -> extension demo -> paper
uv run pytest tests/test_metrics.py tests/test_random_search.py -q
```
Add models: put a key in `.env`, run `scripts/rs/00_run_models.py --sequential`, then `run_all.sh`.

---

## 12. How the pooled ranks are calculated (worked on the real numbers)

Everything starts from the 4 × 7 table of mean calibrated scores (model × dataset):

| | FeTaQA | FinanceBench | FinQA | OfficeQA | TabFact | TAT-QA | WTQ |
|---|---|---|---|---|---|---|---|
| claude-opus-5 | 0.35 | 0.46 | 0.67 | 0.00 | 0.57 | 0.79 | 0.89 |
| claude-sonnet-5 | 0.31 | 0.45 | 0.57 | 0.03 | 0.57 | 0.78 | 0.88 |
| gpt-5.4-mini | 0.24 | 0.43 | 0.61 | 0.02 | 0.75 | 0.77 | 0.83 |
| gpt-5.5 | 0.39 | 0.49 | 0.66 | 0.04 | 0.75 | 0.74 | 0.88 |

**Step 1, per-dataset ranks.** In every column, sort descending and assign rank 1..4; exact ties share
the average rank (TabFact: gpt-5.5 and gpt-5.4-mini tie at 0.75 → both 1.5; the two Claudes tie at
0.57 → both 3.5).

| | FeTaQA | FinanceBench | FinQA | OfficeQA | TabFact | TAT-QA | WTQ |
|---|---|---|---|---|---|---|---|
| claude-opus-5 | 2 | 2 | 1 | 4 | 3.5 | 1 | 1 |
| claude-sonnet-5 | 3 | 3 | 4 | 2 | 3.5 | 2 | 3 |
| gpt-5.4-mini | 4 | 4 | 3 | 3 | 1.5 | 3 | 4 |
| gpt-5.5 | 1 | 1 | 2 | 1 | 1.5 | 4 | 2 |

**Step 2, one pooling rule turns the 7 rank columns into one ordering.** All rules are in
`src/pooling/rank_aggregation.py`; `consensus_ranking(S, rule)` returns the final 1..n ranks.

| Rule | How it is computed | On this table |
|---|---|---|
| **mean_score** | average the raw scores across datasets (the "common score"), rank by it | gpt-5.5 0.564, opus 0.534, 5.4-mini 0.521, sonnet 0.513 → 5.4-mini above sonnet, because TabFact's high scores lift it |
| **mean_z** | in each dataset column subtract the column mean and divide by its std (so every dataset has the same scale), then average | gpt-5.5 +0.57, opus +0.15, sonnet −0.20, 5.4-mini −0.52 |
| **mean_rank** | average the rank row | gpt-5.5 1.79, opus 2.07, sonnet 2.93, 5.4-mini 3.21 |
| **Borda** | a model gets `n − rank` points in each dataset (4 models: 3 for 1st, 0 for last), sum the points | gpt-5.5 15.5, opus 13.5, sonnet 7.5, 5.4-mini 5.5 (identical ordering to mean rank, it is the same information) |
| **Copeland** | for every pair of models count in how many datasets A beats B (ties count ½); A "wins" the pair if that is more than half of the datasets; score = pairwise wins − pairwise losses | gpt-5.5 wins all 3 pairs (4:3 vs opus, 6:1 vs sonnet, 5.5:1.5 vs 5.4-mini) → +3; opus wins 2, loses 1 → +1; sonnet → −1; 5.4-mini → −3 |
| **Kemeny–Young** | pick the single ordering that agrees with the largest total number of per-dataset pairwise preferences (for 4 models: try all 24 orderings, score each by summing "datasets that agree" over its 6 pairs, keep the max). This is the ordering with the smallest total Kendall distance to the 7 dataset rankings. | gpt-5.5 > opus > sonnet > 5.4-mini (pairwise-wins table: gpt-5.5 beats opus 4:3, sonnet 6:1, 5.4-mini 5.5:1.5; opus beats sonnet 5.5:1.5, 5.4-mini 5:2; sonnet beats 5.4-mini 5:2) |
| **RRF** (reciprocal rank fusion) | each dataset contributes `1 / (60 + rank)`; sum. The 60 damps the difference between rank 1 and rank 2 so no single dataset dominates | gpt-5.5 0.1133, opus 0.1128, sonnet 0.1113, 5.4-mini 0.1108 |

Result: every rank-based rule (mean_z, mean_rank, Borda, Copeland, Kemeny, RRF) gives
**gpt-5.5 > claude-opus-5 > claude-sonnet-5 > gpt-5.4-mini**; only the raw mean score swaps the last
two, because it is pulled by dataset difficulty. That agreement is what Table "rule agreement" in the
paper reports (τ = 1 among the rank rules, 0.67 for mean score).

Optional dataset weights: `informativeness_weights` gives each dataset a weight equal to
1 / (bootstrap variance of its ranks), so a dataset whose ranking flips when items are resampled
counts less. It is implemented but not used in the reported numbers.

**Step 3, bootstrap (uncertainty of the pooled rank).** `bootstrap_consensus` repeats 1,000 times:
inside every dataset draw 40 items *with replacement* from its 40, recompute the 4 × 7 mean table,
re-run Borda, record each model's rank. From the 1,000 recorded ranks per model it reports the mean
rank, the 2.5th–97.5th percentile interval, and the probability of each rank position. Reading: gpt-5.5
is rank 1 or 2 in 95 % of resamples ([1, 2]); claude-opus-5 spans [1, 4]; the other two [2, 4]. That is
the honest statement that only the top position is established with 40 items.

The same bootstrap is used on the calibration objective `J` (200 resamples) to give the interval
[0.16, 0.50] around the best combination's 0.476.

**Kendall τ** (used everywhere for "agreement"): for two rankings of the same models, look at every
pair of models; concordant if both rankings order the pair the same way, discordant otherwise;
τ = (concordant − discordant) / number of pairs, so +1 identical, 0 unrelated, −1 reversed. With 4
models there are only 6 pairs, so τ can only take the values ±1, ±0.67, ±0.33, 0 — which is why the
top combinations of the random search tie.

## 13. Other reputable ways to pool rankings across datasets (and which fit the grid search)

Anything that maps the 7 per-dataset results to one ordering can replace Borda inside `J(w)`; the
search code does not care which rule is used.

| Family | Method | What it adds | Fit for the objective |
|---|---|---|---|
| Positional (what we use) | Borda, mean rank, RRF, mean-z | simple, no fitting | already in |
| Condorcet / pairwise | Copeland, Kemeny–Young (in), **Schulze**, **Ranked pairs (Tideman)**, **Minimax** | pick winners from pairwise majorities; Schulze and ranked pairs are the standard "strong" Condorcet rules used in elections and in NLP leaderboard papers (Colombo et al. 2022 argue for Kemeny) | drop-in, deterministic |
| Markov-chain rank aggregation | **MC4** (Dwork, Kumar, Naor, Sivakumar 2001) | random walk on models, moving toward the model that wins pairwise majorities; stationary distribution = ranking; robust to spammy/partial lists | drop-in |
| Probabilistic paired-comparison models | **Bradley–Terry**, **Plackett–Luce**, **Thurstone** | fit a latent "strength" per model from pairwise or listwise outcomes with a likelihood, giving a score *and* a standard error; Chatbot Arena's leaderboard is Bradley–Terry | fits per dataset or pooled; the pooled strength can replace Borda; gives CIs without bootstrap |
| Rating systems | **Elo**, **TrueSkill** | sequential versions of the above; order-dependent, less appropriate for a fixed batch | not recommended for a static benchmark |
| Win-rate aggregation | **mean win rate** (HELM), "head-to-head win probability" | fraction of (dataset, opponent) comparisons a model wins; scale-free like ranks | drop-in, equivalent in spirit to Copeland with graded credit |
| Statistical-significance aware | **Friedman test + Nemenyi critical-difference** (Demšar 2006), **Wilcoxon signed-rank per pair** | tests whether models differ at all across datasets and which pairs are separable; the standard in ML model comparison over many datasets | not an aggregator, but the right way to state "rank k and k+1 are not distinguishable"; could replace the bootstrap |
| Latent-ability / psychometric | **IRT-based aggregation** (item response theory; tinyBenchmarks, Polo et al. 2024), Bayesian hierarchical models | model ability and item difficulty estimated jointly; naturally pools datasets and handles unequal item counts and ceilings | heavier to fit; strongest option if items per dataset grow |
| Objective variants (what to compare with) | **top-weighted τ (τ-AP)**, **rank-biased overlap**, **Spearman footrule**, **Kemeny distance** | replace plain Kendall τ in `J` when agreement at the top of the leaderboard matters more than at the bottom | one-line change in `evaluate()` |
| Distribution matching | KL / JS / Wasserstein between score distributions | scale-aware consistency (see `extensions/`) | must be combined with a ranking term |

Recommendation if the study is extended: keep Borda/Kemeny for the headline (they are the easiest to
explain and agree here), add **Bradley–Terry pooled over datasets** for a strength score with
standard errors, and report a **Friedman–Nemenyi critical-difference** diagram in place of, or next
to, the bootstrap intervals; use **τ-AP** in the objective if the top ranks are what the paper is
about.

---

## 14. What is used at each step (one-page chain)

| Step | Input | What is applied | Output |
|---|---|---|---|
| 1. Score an answer | one prediction, one gold (+aliases) | the 9 component metrics: EM, NumTol, NumDecay, P, R, F1, Edit, ROUGE-L, Jaccard | a 9-vector in [0, 1] |
| 2. Composite | that 9-vector, a weight vector w | weighted sum `S = Σ w_k m_k` | one number in [0, 1] |
| 3. Dataset score | all items of one dataset for one model | arithmetic mean of S | one number per (model, dataset): the models × datasets table |
| 4. Dataset ranking | one column of that table | sort, average ranks for ties | rank 1..n per model, per dataset |
| 5. Pooled ranking | the rank columns | **Borda count** (n − rank points, summed) | one consensus ranking |
| 6. Agreement | a dataset's ranking vs the pooled ranking | **Kendall τ-b** | one number per dataset |
| 7. Objective | the per-dataset τ values | arithmetic mean | J(w), one number per weight vector |
| 8. Search | 100 weight vectors on the 0.05 grid (Dirichlet draws snapped to the grid) | evaluate steps 2–7 for each, sort by J, tie-break by mean pairwise τ | the calibrated w |
| 9. Uncertainty of J | items | **bootstrap** (200 resamples of items, recompute steps 3–7) | 95 % interval on J |
| 10. Transfer | datasets | **leave-one-dataset-out** (repeat step 8 without one dataset, test on it) | held-out τ per dataset |
| 11. Common score | the table under the calibrated w | mean over datasets; and mean of per-dataset **z-scores** | one number per model |
| 12. Leaderboard rank | the rank columns under the calibrated w | **Borda** (headline); Kemeny–Young, Copeland, RRF, mean-rank, mean-z, mean-score as checks | pooled rank per model |
| 13. Uncertainty of rank | items | **bootstrap** (1,000 resamples, recompute steps 3–5) | 95 % rank interval and rank-probability matrix per model |
| 14. Diagnostics | rankings | Kendall τ between each dataset and the pooled rank; between rules; against native-metric and EM-only pooled ranks | agreement tables |
| Extension (not in pipeline) | item scores per model per dataset | **Jensen–Shannon** divergence (plus symmetric KL, Wasserstein-1) between datasets' score histograms | consistency of score *distributions* |

Only a handful of named tools appear: the nine component metrics, a weighted sum, means and ranks,
Borda, Kendall τ, bootstrap resampling, and (as checks) the other pooling rules. Everything else
is bookkeeping.

### Kendall τ, defined

For two rankings of the same models, look at every pair of models. A pair is *concordant* if both
rankings put the same model first, *discordant* otherwise.

    τ = (concordant − discordant) / number of pairs

+1 = identical order, 0 = unrelated, −1 = reversed. With ties, the τ-b variant discounts tied pairs.
Worked example on the real numbers: FinQA ranks (opus 1, gpt-5.5 2, 5.4-mini 3, sonnet 4); the
pooled ranking is (gpt-5.5 1, opus 2, sonnet 3, 5.4-mini 4). Of the six pairs, four are concordant
(opus > 5.4-mini, opus > sonnet, gpt-5.5 > 5.4-mini, gpt-5.5 > sonnet) and two discordant (opus vs
gpt-5.5, 5.4-mini vs sonnet): τ = (4 − 2)/6 = 0.33, the FinQA value in the agreement table.

Why τ and not raw scores: it looks only at order, so a dataset whose scores run 0.90–0.95 and one
whose scores run 0.00–0.10 are compared on equal footing. The catch: τ can only take values in
steps of 1/(number of pairs); with 4 models (6 pairs) that is ±1, ±0.67, ±0.33, 0, which is why
several weight combinations tie at J = 0.476. With 8 models (28 pairs) the step is 0.036.

### Is this the best way? (honest assessment)

Defensible and transparent, not best-in-class. Strong points: standard components anyone can
recompute; weights chosen against a stated, reproducible objective with all candidates reported;
pooling and uncertainty done as the benchmark-aggregation literature recommends; gold handling
better than the source datasets'. Known limits, in order of importance: (1) the objective rewards
datasets agreeing on the ranking, which a metric that blurs real differences can also satisfy, so a
*known* target (human-judged correctness on a sample, or synthetic answers of known quality) is the
stronger calibration; (2) lexical components cannot see paraphrase, an embedding or LLM-judge
component is the accepted upgrade; (3) one global weight vector is a compromise vs per-answer-type
weights; (4) 100 random combinations is a stated budget, exhaustive or Bayesian search costs the same
and should be run once as a check; (5) 4 models × 40 items is the binding constraint on every claim.
The pooling rules are not where the risk is (they agree); a Bradley–Terry strength model and a
Friedman–Nemenyi test would raise the standard there.
