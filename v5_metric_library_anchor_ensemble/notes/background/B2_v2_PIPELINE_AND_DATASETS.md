# Gold answers, the full pipeline, dataset selection, weight selection, rank pooling

Companion to `METHOD_AND_DECISIONS.md` (which records what was done and why). This file explains the
machinery end to end, recommends the dataset suite for the next run, and fixes the protocol for
choosing weights and pooling ranks.

---

## 1. What a "gold answer" is

The **gold answer** (also "ground truth", "reference") is the correct answer supplied by the
dataset's authors for a question. Every score in this project is a comparison between a model's
**prediction** and the item's **gold**. Nothing is judged by an LLM; the gold is the only reference.

Where the golds come from, per dataset:

| Dataset | Gold field(s) in the source | What we store |
|---|---|---|
| FinQA | `qa.answer` (human-written, e.g. `13.2%`) and `qa.exe_ans` (program result, `0.13202`) | gold = `13.2%`, alias = `0.13202` |
| TAT-QA | `answer` (a list), `answer_type` (arithmetic / span / multi-span / count), `scale` (`million`, `percent`, …) | arithmetic: value + scale, alias without scale; spans: the list → list gold `A | B` with `;`/`,` aliases |
| TabFact | statement label 1 / 0 | `yes` / `no`, aliases `1`/`0`, `entailed`/`refuted` |
| FinanceBench | `answer` (free text written by analysts, e.g. `$1577.00` or a sentence) | as is |
| FeTaQA | `answer` (a full sentence) | as is |
| WikiTableQuestions | `targetValue`, multi-answers joined by `\|` | list gold when `\|` present |
| OfficeQA | `answer` (number, or `[a, b]` list) | number, or list gold |

Three things make a gold usable across datasets:

- **Aliases**: equivalent forms the authors would accept (`14%` ≡ `0.14464`; `-12.6 million` ≡ `-12.6`).
  Every component metric is the maximum over aliases.
- **List golds**: multi-span answers are a *set*; exact match means the same set, in any order.
- **Answer type**: each gold is labelled numeric / boolean / text / free-form by a deterministic
  detector (word booleans only; "exactly one number plus at most one non-unit token" ⇒ numeric;
  ≥ 9 tokens ⇒ free-form). The type decides which fallbacks apply (numeric components fall back to
  EM for non-numeric golds) and how items are stratified.

Two real traces (best weights: NumTol .25, ROUGE-L .25, Recall .15, Edit .15, EM .05, NumDecay .05, P .05, Jaccard .05):

```
TAT-QA  Q: What was the Accruals and reserves in 2019 and 2018 respectively?
GOLD    '$7,870 | $12,129'   list=['$7,870','$12,129']   aliases: '; ' and ', ' joins, '... thousand'
gpt-5.5          FINAL ANSWER: $7,870 | $12,129                 -> every component 1.0   composite 1.000
claude-sonnet-5  FINAL ANSWER: $7,870 thousand | $12,129 thousand
                 EM 0 (set differs because of the unit word), NumTol 0 (falls back to EM for list golds),
                 P .75 R 1.0 F1 .86 Edit .68 ROUGE-L .86 Jaccard 1.0        composite 0.554
```
The second answer is correct; it loses because list-gold exact match compares elements as strings
and the `thousand` alias is attached to the whole list, not to each element. This is a metric
defect to fix before the next run (per-element aliases with and without the unit).

```
TAT-QA  Q: What was the revenues weight in Distribution in 2019?
GOLD    'Our revenues weight in Distribution registered a decrease of 5 percentage point compared to
         2018, reaching a 30% share of total revenues in 2019.'   type=freeform (a "span" gold that is a sentence)
gpt-5.5          FINAL ANSWER: 30%          -> P 1.0 R .05 F1 .10 ROUGE-L .10   composite 0.087
claude-sonnet-5  FINAL ANSWER: The revenues weight in Distribution in 2019 was 30% of total net revenues.
                                             -> P .83 R .50 F1 .62 ROUGE-L .50   composite 0.332
```
Here the gold is a sentence, so a terse correct number scores low under recall/ROUGE-L weights.
Whether that is right is a benchmark policy question (TAT-QA's own metric would give both 0 on EM
and a partial F1); it is the kind of item the answer-format instruction in the prompt exists for.

---

## 2. The full pipeline, stage by stage

```
data/pool/<dataset>.jsonl        (items: uid, question, context, table, gold, aliases, list, type, native_metric)
        │
        ▼  00_run_models.py       one prompt per item per model  ->  data/predictions/<model>.jsonl (cached)
        │
        ▼  01_prepare.py          9 component metrics (+ hedge flag) for every (model, item)  ->  output/rs/components.npz, index.csv
        │
        ▼  02_random_search.py    100 weight vectors -> composite -> per-dataset ranks -> Borda -> J ; bootstrap ; baselines ; LODO
        │                         ->  weights_random_search.csv, best_weights.json, baselines.csv, lodo.csv
        ▼  03_pool_report.py      common score, pooled ranks under 7 rules, bootstrap CIs, tables  ->  leaderboard.md, pooled_ranking.json, paper/tables
        │
        ▼  extensions/divergence_extension.py   (standalone) JS / KL / W1 between datasets' score distributions
```

### Stage 0 — items (`data/pool/`)
Each dataset adapter downloads the public split, renders the table or evidence into text (capped
length), builds the gold + aliases + list + type, and samples a fixed number of items with a fixed
seed, stratified by answer type / difficulty where the dataset has it. The first N of each pool are
flagged `in_real_subset` and are the items models see. Output: one JSONL per dataset.

### Stage 00 — model predictions (`data/predictions/`)
For every model in `config/models.toml` with a key: build one prompt (system prompt + context +
table + question + a one-line answer-format instruction + "finish with `FINAL ANSWER: <answer>`"),
call the API once, store the raw text, token counts, latency, and any error. Cached by (model,
dataset, uid); re-runs fill gaps only; a spend cap stops paid models. Models without a key are
skipped and listed.

### Stage 01 — component matrix (`output/rs/components.npz`)
For each (model, item): extract the final answer from the raw text (tag, `FINAL ANSWER:` line, or
last short line; scaffolding like "the answer is" stripped), normalise (Unicode, case, canonical
numbers, punctuation, articles), then compute the nine components against the gold and its aliases
(max over aliases): EM, NumTol, NumDecay, P, R, F1, Edit, ROUGE-L, Jaccard, plus a hedge flag
(unused by the composite). Result: a matrix with one row per (model, item) and an index of which
model / dataset / item / type each row is.

### Stage 02 — random search (`output/rs/weights_random_search.csv`)
1. Draw 100 distinct weight vectors on the step-0.05 simplex grid (Dirichlet(1) draws snapped to
   the grid, fixed seed).
2. For each vector `w`: composite `S = M·w` for every row; mean per (model, dataset); rank models in
   each dataset; Borda-pool the rankings; `J = mean over datasets of Kendall τ(dataset ranking,
   pooled ranking)`. Also record mean pairwise τ between datasets and the scale-dispersion statistic.
3. Sort by `J` (tie-break: pairwise τ). Bootstrap `J` (200 item resamples) for the top five, median
   and worst. Evaluate the five fixed baselines under the same `J`.
4. Leave-one-dataset-out: re-select without each dataset, test agreement of the held-out dataset with
   the pooled ranking of the rest.
5. Write `best_weights.json` (the calibrated weights).

### Stage 03 — pooling and report
Under the best weights: per-dataset means (the leaderboard table), the **common score** (mean over
datasets; and the difficulty-adjusted mean of per-dataset z-scores), pooled ranks under mean-score,
mean-z, mean-rank, Borda, Copeland, Kemeny–Young and RRF, agreement of each dataset with the pooled
ranking, agreement between rules, agreement with the native-metric and EM-only pooled rankings, and
1,000 item bootstraps of the Borda rank (interval + rank-probability matrix). Writes the markdown
leaderboard, the JSON, the figure and the LaTeX tables consumed by `paper/main.tex`.

### What travels between stages (one item, one model)
`pool` row → prompt → raw prediction text → final-answer string → 9 numbers in [0,1] → one composite
number → contributes 1/40 of the model's mean on that dataset → that mean's rank in the dataset →
Borda points → pooled rank; and, in the search, the same chain evaluated 100 times with different `w`.

---

## 3. Datasets: the landscape and what to keep, replace, add

The benchmark's name and its native task (TPC-DI: join customers, accounts and trades, aggregate per
customer) are about **data matching and integration**. The v1 catalogue, however, is entirely
**question answering over tables and financial documents**. Both matter, and the most indicative
suite covers both: a model that is good at matching records should also be good at reading the
integrated result. Recommended structure: two tiers plus one optional tier.

### Tier 1 — data matching proper (new; this is what the name promises)

| Dataset | What it is | Items available | Answer type | Why | Source |
|---|---|---|---|---|---|
| **Abt-Buy** | product entity matching (two retailer catalogues) | ~9.5k labelled pairs | boolean match / no-match | the canonical noisy-text EM benchmark | Magellan / DeepMatcher data release (`anhaidgroup/deepmatcher`) |
| **Amazon-Google** | software product matching | ~11.5k pairs | boolean | canonical, harder than Abt-Buy | same |
| **DBLP-Scholar** (or DBLP-ACM) | bibliographic record matching | ~28.7k (12.4k) pairs | boolean | structured-record matching with dirty variants | same |
| **Walmart-Amazon** | product matching, multi-attribute | ~10.2k pairs | boolean | attribute-level matching | same |
| **WDC Products** | web product offers, multi-domain, hard negatives | 80/20-percent-corner sets, thousands of pairs | boolean | modern, large, has difficulty levels | Web Data Commons (Peeters & Bizer) |
| **TPC-DI cell-level** (already in v1) | per-customer aggregates from joined tables | 120 customers × 8 fields | numeric / text | the benchmark's own task; each cell becomes an item with a gold | `v1/jan15_tasks` |

Sample **150 pairs per EM dataset, balanced 50/50 match vs non-match**, stratified by the source's
difficulty label where present (WDC has it). Prompt: both records rendered as key: value lines,
"Do these refer to the same entity? Answer yes or no." These are boolean tasks, so the metric is
accuracy; their value is that they anchor the *matching* half of the suite and are exactly the
tasks an ETL agent performs.

### Tier 2 — reasoning over tables and financial documents (keep the core, fix the weak spots)

| Dataset | Decision | Reason |
|---|---|---|
| **FinQA** | keep, 150 items | canonical numeric reasoning over 10-K tables; clean golds with aliases |
| **TAT-QA** | keep, 150 items stratified by the four answer types | only dataset with arithmetic + span + multi-span + count in one place; note the sentence-length "span" golds |
| **WikiTableQuestions** | keep, 150 items | the standard open-domain table QA set; short answers and lists |
| **TabFact** | keep, 150 statements balanced entailed/refuted | the boolean table task; at ceiling for frontier models, so it separates little; keep for coverage, weight it down if needed |
| **FeTaQA** | keep, 100 items | the only free-form generation task; it is where lexical metrics are weakest, so it must stay to keep the calibration honest |
| **FinanceBench** | keep, all 150 open items | long-document financial QA with analyst golds; only 150 exist, use them all |
| **OfficeQA** | **replace or make optional** | closed-book here (corpus gated on Hugging Face), so every model is at floor (0.00–0.04) and the dataset carries no ranking information. Either request corpus access and run it with retrieval, or drop it from the calibration and report it separately |
| **MultiHiertt** | **add**, 150 items | multi-hierarchical financial tables + text, numeric reasoning; the closest public proxy to real report tables and much harder than FinQA (`psunlpgroup/MultiHiertt`) |
| **HiTab** | **add**, 150 items | hierarchical statistical tables (government / stats reports) with numeric and text answers; different domain from finance, same skill (`microsoft/HiTab`, `data/test_samples.jsonl` verified reachable) |
| **ConvFinQA** | optional | conversational FinQA; multi-turn is a different interface for an A2A agent; add only if the judge supports multi-turn |
| **DocFinQA** | optional replacement for OfficeQA | FinQA questions with the *full* filing as context (long-context retrieval), open on Hugging Face; gives the "find the number in a long document" skill OfficeQA was meant to test, without the gated corpus |

### Tier 3 — optional, only if the paper's scope widens

DataBench (SemEval 2025; QA over real CSVs by writing code), BIRD / Spider 2.0 (text-to-SQL over
databases), TableBench (886 analytic questions). These test data *analysis* rather than matching or
reading; include only if the agent under test writes code.

### Amounts and mix, and why

- **≥ 100 items per dataset, 150 where the source has them.** The bootstrap interval on a
  dataset's model ranking shrinks roughly with 1/√n; at 40 items the current intervals span three
  rank positions of four. 150 items halves the width.
- **8–10 datasets** in the calibration: enough for the pooled ranking to be an ensemble rather than
  a coin flip, few enough that every dataset is run for every model.
- **Balanced answer types across the suite**: roughly numeric 40 %, boolean 25 % (TabFact + entity
  matching), short text/list 20 %, free-form 15 %. A single global weight vector is only defensible
  if no type dominates.
- **Fixed seed, stratified sampling, published item ids** so anyone can reproduce the exact subset.

### Which datasets are "most indicative" of data matching

In this order: the entity-matching sets (they *are* matching), TPC-DI cell-level (the agent's own
task), TAT-QA and MultiHiertt (reading integrated financial tables with mixed answer types), FinQA,
WTQ, HiTab, FinanceBench, TabFact, FeTaQA. OfficeQA only with corpus access.

---

## 4. How to pick the best weights with the grid search

Protocol for the next run (all supported by the existing scripts with small changes):

1. **Candidates**: 100 weight vectors on the step-0.05 simplex grid. Draw them quasi-uniformly
   (Dirichlet(1) snapped to the grid, as now) and **always add the five fixed baselines** to the
   evaluated set so the paper can say where they fall.
2. **Objective**: keep `J(w)` = mean over datasets of Kendall τ to the Borda-pooled ranking, but
   compute it as the **mean over 50 bootstrap resamples of items** instead of once. This removes
   the ties seen with 4 models and makes `J` a smooth number.
3. **With ≥ 8 models** switch τ to a top-weighted variant (τ-AP) if the paper's claims are about the
   top of the leaderboard; otherwise plain τ.
4. **Statistical tie set**: take every candidate whose `J` is within one bootstrap standard error of
   the best. These are indistinguishable by the objective.
5. **Choose inside the tie set** by fixed secondary criteria, in this order:
   (a) highest agreement with the native-metric pooled ranking (so the composite does not drift
   from what dataset authors intend); (b) fewest non-zero weights (simplicity); (c) highest
   *selection stability*, i.e. how often the vector is in the top five across the bootstrap resamples.
6. **Leave-one-dataset-out** must not reverse the choice: report the held-out agreement under LODO
   weights vs full weights for every dataset.
7. **Report all 100** (`weights_random_search.csv`) with their bootstrap intervals, not just the
   winner, and pre-register the objective and the tie-break before running.

What not to do: rerun the search with a different seed until a nicer vector appears; add objective
terms after seeing the leaderboard; hand-edit a weight "because it looks better".

---

## 5. Which rank-pooling combination to use

Use them in defined roles rather than choosing one:

| Role | Method | Why |
|---|---|---|
| **The number** (common score) | mean of per-dataset **z-scores** under the calibrated weights (report the plain mean beside it) | difficulty-adjusted, one value per model, transparent |
| **The headline rank** | **Borda** count of the per-dataset rankings | simplest positional rule; identical to mean rank; what the objective optimised |
| **Robustness check** | **Kemeny–Young** and **Copeland** | Condorcet-style rules; if they disagree with Borda, say so (here they agree) |
| **Uncertainty** | **item bootstrap** (1,000 resamples) → rank intervals and rank-probability matrix | already implemented; honest about what 150 items can separate |
| **Significance** | **Friedman test + Nemenyi critical-difference diagram** across datasets | the standard for comparing models over many datasets; tells you which adjacent ranks are not separable |
| **Strength with error bars** (recommended addition) | **Bradley–Terry** fitted to (dataset, item)-level pairwise wins between models | one latent score per model with a standard error, as in Chatbot Arena; complements rank-based rules |
| Do not use as headline | raw mean score (dataset difficulty dominates), RRF (its constant 60 is arbitrary), Elo / TrueSkill (order-dependent) | |

Dataset weighting: equal weights by default. If the suite keeps a saturated dataset (TabFact) for
coverage, use `informativeness_weights` (inverse bootstrap rank variance) and report both weighted
and unweighted Borda.

---

## 6. Concrete plan for the next run (status 2026-09-08: steps 1–3 implemented; pools built; model run pending)

1. Fix list-gold aliases (per-element unit variants) and re-score; re-run `01–03` (minutes).
2. Add adapters for Abt-Buy, Amazon-Google, DBLP-Scholar, WDC Products, MultiHiertt, HiTab,
   DocFinQA; TPC-DI cell-level items from `v1/jan15_tasks`. Drop OfficeQA from calibration unless
   corpus access is granted.
3. Pool 150 items per dataset (100 for FeTaQA), balanced types; publish item ids.
4. Models: the catalogue's flagship + standard tier for OpenAI, Anthropic, Google (after billing),
   xAI (after credits), plus Llama-3.3-70B, DeepSeek-V3/R1, Qwen-2.5-72B, Mistral Large → 12–14
   systems.
5. Run the search with the protocol in §4; pool with the roles in §5; regenerate the paper.
