# Data Matchmaker Benchmark v2 — one common score across the original data-matching datasets

**v2 is a copy of `data-matchmaker-benchmark` (v1) that adds an offline calibration study and a
short paper.** Goal: a single *common score* for LLMs across the benchmark's original dataset
catalogue, with the composite-metric weights chosen by a **random search over 100 grid
combinations** so that the datasets rank models consistently, and per-dataset rankings **pooled into
one leaderboard** (Borda / Copeland / Kemeny–Young / reciprocal-rank fusion with bootstrap
intervals). KL/JS divergence is provided as a documented **extension only** (`extensions/`), not
wired into the pipeline. How this differs from the earlier ladder version implementation, and what each does
better, is in [COMPARISON_with_ladder_version.md](COMPARISON_with_ladder_version.md). Paper: [paper/main.pdf](paper/main.pdf).

## Summary

* **Datasets (7, all from the v1 catalogue, chosen for diversity + importance):** OfficeQA
  (Treasury bulletins, closed-book), FinQA and TAT-QA (SEC filings, table + text), FinanceBench
  (10-K/10-Q with evidence), TabFact (table fact verification), FeTaQA (free-form table QA),
  WikiTableQuestions (open-domain tables). 40 stratified items each; numeric, boolean, short-text
  and free-form golds.
* **Models (industry-standard flagship + standard tier per provider; 4 with cached predictions today):** GPT-5.5, GPT-5.4-mini, Claude Opus 5, Claude Sonnet 5. Gemini 3.1 Pro / 3.8 Flash, Grok-4, Llama-3.3-70B, DeepSeek-V3/R1, Qwen-2.5-72B and Mistral Large are in `config/models.toml` and run as soon as their key is in `.env` (see `MODELS.md`).
  GPT-5.5, Claude Haiku 4.5, Sonnet 5, Opus 5.
* **Composite score:** `S = Σ_k w_k m_k` over 9 components (EM, numeric tolerance, numeric decay,
  token P/R/F1, edit similarity, ROUGE-L, Jaccard; unit-aware numbers, gold aliases, list golds).
* **Calibration:** 100 weight vectors sampled from the step-0.05 simplex grid; objective
  `J(w) = mean_d τ(ranking of models on d, pooled Borda ranking)`; bootstrap CIs; fixed baselines
  (EM, F1, numeric tolerance, uniform, v1 rubric); leave-one-dataset-out.
* **Pooling:** common score = mean of per-dataset composites (and difficulty-adjusted z-mean);
  pooled rank under 7 rules; 1,000 item bootstraps.

## Headline numbers (`output/rs/`, 4 models x 7 datasets x 40 items)

| | J (mean τ to pooled ranking) |
|---|---|
| EM only | 0.362 |
| Token-F1 only | 0.459 |
| v1 hand-set rubric | 0.429 |
| Uniform | 0.429 |
| **Random-search best** (em 0.05, num_tol 0.25, num_decay 0.05, tok_prec 0.05, tok_rec 0.15, edit_sim 0.15, rouge_l 0.25, jaccard 0.05) | **0.476**, bootstrap 95 % CI [0.16, 0.50] |

* Pooled leaderboard: gpt-5.5 first under every rule, then claude-opus-5, claude-sonnet-5, gpt-5.4-mini; bootstrap rank intervals overlap below rank 1. Pooled ranking vs native-metric pooled ranking: τ = 0.67; vs EM-only: 0.33.
* **Read the caveat:** with 4 closely matched models and 40 items per dataset, per-dataset rankings are noisy under *any* weighting (mean pairwise τ = 0.14 for the best weights, 0.05 for EM); 65 of the 100 combinations beat EM and the gain sits inside the bootstrap interval. Adding the remaining catalogue models (Gemini, Grok, Llama, DeepSeek, Qwen, Mistral) is the direct remedy and needs only API keys.
* Divergence extension demo (`output/rs/divergence_extension_demo.txt`): mean JS/ln2 between
  datasets is 0.855 (EM), 0.766 (v1 rubric), 0.777 (calibrated) — the graded weightings give more
  comparable score profiles than EM, but a binary metric can reach low divergence by failing uniformly,
  which is why the extension must be paired with a ranking or known-quality anchor.

## Layout (new in v2)

```
scripts/rs/01_prepare.py        component matrix from data/pool + data/predictions (cached)
scripts/rs/02_random_search.py  100 grid combinations, objective, baselines, bootstrap, LODO, fig
scripts/rs/03_pool_report.py    common score, pooled ranks, bootstrap CIs, tables, leaderboard.md
scripts/rs/run_all.sh           all of the above + paper (about 1 minute, no API calls)
extensions/divergence_extension.py + DIVERGENCE_EXTENSION.md   KL / JS / W1 proposal + demo (not in pipeline)
src/metrics/                    component metric library (shared with ladder version)
src/pooling/rank_aggregation.py Borda, Copeland, Kemeny, RRF, mean-z, bootstrap
data/pool/*.jsonl, data/predictions/*.jsonl   sampled items and cached model outputs
output/rs/                      weights_random_search.csv (100 rows), best_weights.json, baselines.csv,
                                lodo.csv, pooled_ranking.json, leaderboard.md, figures
paper/                          main.tex, tables/, numbers.tex, main.pdf
tests/test_metrics.py, tests/test_random_search.py
COMPARISON_with_ladder_version.md          what differs from ladder version and what each version does better
```

## Reproduce

```bash
uv sync
scripts/rs/run_all.sh            # or the three scripts one by one
uv run pytest tests/test_metrics.py tests/test_random_search.py -q
```
To add models or items, drop new `data/predictions/<model>.jsonl` / `data/pool/<dataset>.jsonl`
files in the same format (ladder version's `scripts/02_run_models.py` produces them) and re-run.

Everything from v1 (green agent, TPC-DI task, Docker files, tests) is unchanged.
