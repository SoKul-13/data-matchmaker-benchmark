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
6. Repo restructured: `v1/` original, `v2/` this work.

---

## 11. Reproduce

```bash
cd v2 && uv sync
scripts/rs/run_all.sh          # 01 prepare -> 02 random search -> 03 pooling/report -> extension demo -> paper
uv run pytest tests/test_metrics.py tests/test_random_search.py -q
```
Add models: put a key in `.env`, run `scripts/rs/00_run_models.py --sequential`, then `run_all.sh`.
