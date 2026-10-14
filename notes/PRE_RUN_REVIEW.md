# Pre-run review (2026-09-23): what a reviewer could call wrong, and what v6 changes before the model run

Checked in code, not from memory: `src/inference/providers.py`, `src/pooling/rank_aggregation.py`, `scripts/01_compute_matrix.py`,
`data/pool/*.jsonl`, the four search scripts (see `SEARCH_DESIGN_REPORT.md`).

## A. Must fix before spending money

| # | Finding | Evidence | Fix in v6 |
|---|---|---|---|
| 1 | **No decoding settings are sent.** No `temperature`, `top_p` or `seed` in any provider call, so every model runs at its provider default (1.0). Answers are not reproducible and a re-run can change the leaderboard. | `grep temperature src/inference/providers.py` → nothing | send temperature 0 where the API accepts it (reasoning models ignore it; record that), store every decoding parameter in each prediction row, and answer a 100-item subset 3× to measure answer variance |
| 2 | **Item counts are inconsistent.** The 7 old pools flag 40 items as the real subset; the 7 new pools flag all 150. The runner would send 150 per new dataset, so the cost estimates (which assumed 40) are 3× low for those. | `in_real_subset` counts: 40 vs 150 | decide one size for all 31 datasets (see decision 1 below) and re-flag pools |
| 3 | **Entity-matching pools are balanced (45–51 % positive) by stratified sampling; the official test splits are 10–20 % positive.** Scores are therefore not comparable to published F1, and accuracy (`native_metric = em`) is not the field's metric. | `ground_truth` share per pool | keep the balanced sample (it is what makes accuracy meaningful) but report positive-class F1 as the native metric, add the majority-class baseline, and state the class ratio in every EM table |
| 4 | **Winner's curse.** The best of 100–109 candidates is chosen on all data and its confidence interval is then computed on the same items. Only v4 has leave-one-dataset-out; nothing has a held-out check of the selection itself. | v2/v4 bootstrap 7 candidates, on the same items used for selection | nested bootstrap: select on the in-bag items, score on the out-of-bag items; paired permutation test best vs each baseline; Holm correction |
| 5 | **Floor datasets silently count as zero agreement.** `kendall_tau` returns 0 when a ranking is constant, so a dataset where every model scores 0 (OfficeQA closed-book) drags J down instead of being excluded. | `rank_aggregation.py:33-37` | drop datasets whose per-model scores do not differ beyond bootstrap noise from the objective, and list them in the report; OfficeQA runs with its documents (Pro V2), not closed-book |

## B. Limitations a reviewer will raise (report them; some are fixed by scale)

| # | Finding | Consequence | Mitigation |
|---|---|---|---|
| 6 | Only 4 models. Kendall τ over 4 items takes 7 values (−1, −⅔, −⅓, 0, ⅓, ⅔, 1); J is a mean of 7 such values; Bradley–Terry and Rasch fits on 4 models are near-degenerate; "top five tie" is an artefact of granularity. | every rank claim below first place is unsupported | the 13-model run (8 live now) is the fix; report τ granularity explicitly |
| 7 | The v2/v4 objective rewards **agreement between datasets**, not correctness. A scoring rule that makes every dataset rank models identically maximises J even if it is wrong about all of them. | the paper must call J "consistency", never "accuracy" | v5's anchor objective is the answer; v6 reports both and states the difference |
| 8 | v5's anchors are lexical perturbations judged by lexical metrics, so ρ = 0.906 is partly tautological. | validity rests on the perturbation operators being realistic | human labels (300–500 answers) remain the only real fix; the plan keeps the `--labels` path |
| 9 | Search coverage: v2 100 of 1,771 lattice points, v3 100 of 888,030, v4 100 of 3.1 million; no stratification. | the reported optimum is a sample optimum | Latin hypercube design run alongside; all 255 view subsets in v3 |
| 10 | Bootstrap resamples items only, never models or prompts; one prompt of our own, not the datasets' official prompts. | intervals understate uncertainty | 3-sample variance from fix 1; state the prompt limitation |
| 11 | Datasets are equally weighted in Borda regardless of size, difficulty or family; entity matching (5 sets) and table QA (many sets) would dominate a 31-dataset pool by count. | family with most datasets decides the ranking | report family-balanced pooling (mean within family, then across) next to plain Borda |
| 12 | Extraction heuristics: the final answer is taken from a "FINAL ANSWER:" line, else a boxed expression, else the last short line; the hedge detector has had false positives before. | mis-extraction is scored as a wrong answer | log the extraction path per row and the share of answers with no FINAL ANSWER line; manual check of 50 |
| 13 | 40 items per dataset (if kept) gives ±0.15 on a proportion at 95 %. | per-dataset differences between models are rarely significant | see decision 1 |

## C. Things that are fine
Fixed seeds everywhere; every candidate saved with its objective terms; `uv.lock` pins the environment; cached raw answers; alias, unit and list
handling in the scorer is stricter than most harnesses; the Dirichlet-to-lattice snapping in v4 is unbiased; ties in ranks use average ranks.

## D. Decisions needed before the run
1. **Items per dataset**: 40 (current old pools; USD 45–50 for the four cached models on 26 new datasets), 100 (recommended for the
   significance tests; about USD 110, and the 5 old datasets re-answered to 100 as well), or 150 (about USD 170).
2. **Temperature 0** for all models (recommended), or provider defaults with 3 samples per item (3× cost).
3. Family-balanced pooling as the headline or as a secondary table.

## E. What "very detailed output" will mean in v6 (saved for every run)
* `output/items/`: every (model, item) row with raw answer, extracted answer, extraction path, all metric values, hedge flag, native score, cost, tokens, latency.
* `output/candidates/`: every weighting or view mix with every objective term, in-bag and out-of-bag J, rank, and the per-dataset score table it induces.
* `output/params/`: fitted parameters with standard errors per view (Bradley–Terry, Rasch abilities and item difficulties, Kemeny cost, Copeland, Borda), once on full data and once per bootstrap draw.
* `output/combos/`: all 255 view subsets (v3) and all top-5 weightings and EM-only (v2, v4, v5), each with a full leaderboard, per-dataset tables and LaTeX.
* `output/significance/`: Friedman + Nemenyi, pairwise Wilcoxon and permutation tests (Holm-corrected), Kendall's W, bootstrap distributions as `.npz`, one summary markdown.
* `output/run_manifest.json`: models, decoding settings, item counts, seeds, costs, token totals, git commit, dataset versions and licences.
