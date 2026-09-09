# The pipeline in full detail

Every stage of `scripts/rs/`, what goes in, what comes out, the exact computations, and the edge
cases. Read `PIPELINE_AND_DATASETS.md` first for the overview and the dataset choices; read
`METHOD_AND_DECISIONS.md` for why each design decision was made.

```
config/datasets.toml ──► 00a_build_item_pool.py ──► data/pool/<dataset>.jsonl
config/models.toml   ──► 00_run_models.py      ──► data/predictions/<model>.jsonl
                         01_prepare.py         ──► output/rs/components.npz + index.csv + datasets.md
                         02_random_search.py   ──► weights_random_search.csv, best_weights.json, baselines.csv, lodo.csv, fig_random_search
                         03_pool_report.py     ──► leaderboard.md, pooled_ranking.json, fig_leaderboard, paper/tables/*.tex, paper/numbers.tex
extensions/divergence_extension.py (standalone) ──► printed JS / KL / W1 matrices
```

---

## Stage 0a — items: `00a_build_item_pool.py`

**Input.** `config/datasets.toml`: one block per dataset with `name`, `tier` (1 = data matching
proper, 2 = reasoning over tables/documents), optional `pool_size` (default 150), `stratify`
(field to balance on), `hint` (force an answer type), `enabled`, `optional`.

**Per dataset.**
1. The adapter (`src/adapters/<name>_adapter.py`) downloads the public split (cached under
   `data/cache/`, keyed by URL hash) and converts each record into a `QuestionItem`:
   `uid`, `question`, `context` (evidence text, record pair, filing windows), `table_data`
   (rendered as pipe-separated rows, header underlined, capped at ~40 rows / 4,000 chars),
   `ground_truth`, `gold_aliases`, `gold_list`, `answer_type` (if the dataset defines it),
   `native_metric` (what the dataset's authors score with), `difficulty` (used for stratification).
2. Fetch-heavy adapters (per-item table or record downloads) sample *before* fetching:
   `num_questions = 2–3 × pool_size` random ids with the global seed, so the download is bounded.
3. Entity-matching adapters sample **balanced**: `pool_size/2` matching pairs and `pool_size/2`
   non-matching pairs from the official test split, then shuffle. Without this the natural 10–20 %
   match rate would let "always no" score 85 %.
4. Stratified sample of `pool_size` items: round-robin over the strata (TAT-QA answer type, WDC
   category, TPC-DI field, FinanceBench question type) so small strata are represented.
5. Answer type: `detect_answer_type(gold, aliases, hint, gold_list)`:
   - hint `boolean` is honoured only if the gold really is a yes/no word;
   - a word boolean (`yes`, `no`, `true`, `false`, `entailed`, `refuted`) ⇒ boolean; digits never are;
   - a list gold ⇒ text;
   - exactly one number and at most one token that is not a unit/currency/filler word ⇒ numeric
     (`$1,577.00`, `-12.6 million`, `2 years`, `1499.39%` all qualify);
   - ≥ 9 normalised tokens ⇒ free-form; otherwise text.
   `native_metric = "auto"` resolves to NumTol / EM / EM / ROUGE-L by type.
6. `in_real_subset` marks the items that will be sent to models (all of them for new datasets;
   the first 40 for the six original datasets whose predictions were already cached).
7. Output: `data/pool/<name>.jsonl`, one JSON object per item, real-subset items first. Existing
   files are never overwritten unless `--force`, so cached predictions stay aligned with their items.

**Current pool** (real items): FinQA 40, TAT-QA 40, TabFact 40, FinanceBench 40, FeTaQA 40, WTQ 40,
HiTab 150, DocFinQA 100, Abt-Buy 150, Amazon-Google 150, DBLP-Scholar 150, Walmart-Amazon 150,
WDC Products 150, TPC-DI cells 150 = 1,390 items. OfficeQA is parked in `data/pool/_excluded/`;
MultiHiertt loads when `data/raw/multihiertt/dev.json` is present.

---

## Stage 00 — predictions: `00_run_models.py`

**Input.** `config/models.toml` (provider, `model_id`, prices, tier, concurrency, optional
`base_url` / `api_key_env` for any OpenAI-compatible endpoint), `.env` keys, the real-subset items.

**Prompt** (`src/inference/prompts.py`), identical for every model:
```
[system]  You are a precise question-answering system for financial documents, tables and
          quantitative reasoning. Use ONLY the provided context when context is given; ...
          Reason briefly and then finish with one line of the exact form: FINAL ANSWER: <answer>
[user]    ### Context   <evidence / record pair / retrieval windows>      (if any)
          ### Table     <rendered table>                                   (if any)
          ### Question  <question>
          ### Answer format  <one sentence by answer type: number / yes or no / shortest exact answer with ' | ' between items / one sentence>
```
**Call.** One request per (model, item); `max_tokens` 700; reasoning effort "low" for OpenAI
reasoning models, `thinking_level` "low" for Gemini; no temperature is set (several APIs reject
it). Retries with exponential back-off on rate limits; after the retry budget the row is stored
with `error` set and an empty prediction.

**Cache.** `data/predictions/<model>.jsonl`, one row per item: `model, model_id, dataset, uid,
prediction (raw text), in_tokens, out_tokens, latency_s, error, finish, cost_usd`. Re-running
skips rows that already exist without error. `--dry-run` prints which models are active/skipped
and the prompt-token total; `--sequential` runs models one at a time (recommended when free-tier
endpoints are active); the spend cap sums `cost_usd` from the price table and stops paid models.

**Cost reference.** Prompt tokens per model for the current pool ≈ 604k (DocFinQA 233k of that).
Completing the 1,150 new items on the four cached models ≈ USD 35 at list prices, three quarters
of it Claude Opus 5.

---

## Stage 01 — component matrix: `01_prepare.py`

**Input.** Enabled datasets from `config/datasets.toml` that have a pool file; every
`data/predictions/*.jsonl` (files starting with `_` are ignored).

**Per (model, item):**
1. **Final-answer extraction** (`metrics/normalize.py`): `<FINAL_ANSWER>…</FINAL_ANSWER>` tag →
   last `FINAL ANSWER:` / `Answer:` line → `\boxed{}` → last short line; then generic scaffolding
   is stripped (`the answer is …`, `… is the correct answer`). A missing prediction (API error)
   becomes the empty string and scores 0 on every component.
2. **Normalisation**: Unicode NFKC, lower-case, numbers rewritten canonically (`1,577.00` → `1577`,
   `(12.6)` → `-12.6`, `14.5%` keeps the value, scale words kept), currency symbols and punctuation
   removed, articles dropped, whitespace collapsed. Booleans map to `yes` / `no` before comparison.
3. **Nine components**, each the maximum over gold aliases:

   | Component | Definition |
   |---|---|
   | EM | 1 if normalised strings are equal; for list golds, 1 if the sets of normalised elements are equal |
   | NumTol | 1 if the primary predicted number matches the gold number within 1 % relative error under any unit interpretation (`v`, `v·scale`, `v/100`, `100v`), else 0; non-numeric gold → EM |
   | NumDecay | `exp(−2.5 · min(relative error, 2))` for the same pair; non-numeric gold → EM |
   | P, R, F1 | token-multiset precision / recall / F1 (SQuAD style) |
   | Edit | `1 − Levenshtein(pred, gold) / max(len)` on normalised strings |
   | ROUGE-L | LCS length `L`; `2PR/(P+R)` with `P = L/len(pred)`, `R = L/len(gold)` |
   | Jaccard | `|tokens_pred ∩ tokens_gold| / |tokens_pred ∪ tokens_gold|` |

   plus a tenth column, `hedge_free` (0 if the prediction offers several distinct numeric
   candidates, says "A or B", or enumerates ≥ 3 short candidates for a single-valued gold), stored
   but **not** used by the composite in v2.
4. **Native metric value** is looked up for the item's `native_metric` name.

**Output.** `components.npz` (`M`: rows × 10 floats, plus the column names), `index.csv`
(model, dataset, uid, answer_type, native_metric, missing), `datasets.md` (tier, source, task type,
item count, answer-type mix per dataset).

---

## Stage 02 — random search: `02_random_search.py`

**Candidates.** 100 distinct vectors `w ∈ R^9`, `w ≥ 0`, `Σw = 1`, each entry a multiple of 0.05.
Generation: draw `p ~ Dirichlet(1,…,1)` (uniform on the simplex), set `c = floor(20·p)`, add the
remaining units to the entries with the largest residual `20·p − c`, `w = c/20`; keep if not seen.
Seed 20260907.

**For each `w`:**
1. `S = M[:, :9] · w` → one composite per (model, item).
2. `S̄[m, d]` = mean of `S` over the items of dataset `d` for model `m` (a models × datasets table).
3. `r_d` = ranks of the models within column `d` (rank 1 = highest mean; ties get the average rank).
4. Pooled ranking `R` = Borda: points `n − r_d[m]` summed over datasets, ranked.
5. `J(w) = (1/|D|) Σ_d τ(r_d, R)` with Kendall τ-b (ties handled). Also:
   `mean_pairwise_tau` = mean τ over all dataset pairs `(d, d′)`; `scale_dispersion` = after
   subtracting each column's mean, mean over models of the row std divided by the std of row means
   (how much a model's relative standing moves between datasets); `tau_to_kemeny`; `min_dataset_agreement`.
6. Rows are sorted by `J`, then `mean_pairwise_tau`; rank 1 is the calibrated vector.

**Bootstrap of J** (top 5, median, worst): 200 times, resample the items of every dataset with
replacement, recompute `S̄`, `r_d`, `R`, `J`; report the mean and the 2.5 / 97.5 percentiles.

**Baselines** under the same `J`: EM only, F1 only, NumTol only, uniform (1/9 each), v1 rubric
(`F1 .35, NumDecay .35, P .15, R .15`).

**LODO.** For each dataset `d`: recompute `J` on the other datasets for all 100 candidates, take the
best `w_{−d}`, then measure τ between `d`'s ranking under `w_{−d}` and the Borda ranking of the
other datasets under `w_{−d}`; compare with the same quantity under the full-data `w`.

**Outputs.** `weights_random_search.csv` (100 rows: rank, J, the secondary statistics, nine
weights, bootstrap interval where computed), `best_weights.json`, `baselines.csv`, `lodo.csv`,
`fig_random_search.pdf/png` (sorted J with baseline lines; heat-map of the top-10 vectors).

---

## Stage 03 — pooling and report: `03_pool_report.py`

Under `best_weights.json`:
1. `S̄` table and per-dataset ranks as above.
2. **Common score** per model: `mean_d S̄[m, d]` and the difficulty-adjusted
   `mean_d (S̄[m, d] − mean_m S̄[·, d]) / std_m S̄[·, d]` (z-mean).
3. **Pooled ranks** under seven rules (`src/pooling/rank_aggregation.py`):
   mean score; mean z; mean rank; Borda; Copeland (pairwise wins − losses, a win = beating the
   other model in more than half the datasets, ties ½); Kemeny–Young (the ordering minimising the
   sum of Kendall distances to the dataset rankings; exact enumeration for ≤ 9 models, pairwise-swap
   local search above); RRF (`Σ_d 1/(60 + r_d)`).
4. **Bootstrap** (1,000 resamples of items within every dataset) of the Borda rank: mean rank,
   95 % interval, and the probability of each rank position per model.
5. **Agreements**: τ between each dataset's ranking and the pooled ranking; τ between rules; τ of
   the pooled ranking with the pooled rankings under the native metrics and under EM-only.
6. **Outputs.** `leaderboard.md`, `pooled_ranking.json`, `fig_leaderboard.pdf/png` (rank
   intervals + per-dataset heat-map), LaTeX tables and `numbers.tex` macros for the paper.

---

## Standalone: `extensions/divergence_extension.py`

Reads the same matrix and weights; for a weight vector builds, per model, the 10-bin histogram of
its item scores on each dataset (after subtracting each dataset's mean over models, so difficulty
is removed), then computes Jensen–Shannon divergence, symmetric KL (ε-smoothed) and 1-Wasserstein
distance between every pair of datasets, averaged over models. Nothing in `scripts/rs/` imports
it; the write-up in `extensions/DIVERGENCE_EXTENSION.md` explains how it would join the objective
and why it needs the ranking term as an anchor.

---

## Where things can go wrong (and what guards them)

| Risk | Guard |
|---|---|
| A dataset's golds are wrong or in the wrong form | adapters carry aliases and list golds; `datasets.md` shows the type mix; two real traces are in `PIPELINE_AND_DATASETS.md` §1 |
| A model answers with the right value in a different unit | unit / percent equivalence classes in NumTol / NumDecay; aliases |
| A model failed on some items (API error) | stored as empty predictions (score 0) and counted; a model covering < 90 % of items is excluded by the coverage rule in the ladder version's prepare step — v2 keeps all rows and reports `missing` |
| Ties in ranks (few models) | average ranks, τ-b; bootstrap intervals show what is separable |
| Weight choice fitted to one dataset | LODO |
| Objective satisfied by a metric that blurs differences | dispersion, native-metric agreement and pairwise τ reported alongside |
| Boolean tasks solvable by a constant answer | entity-matching pools are balanced 50/50 |
