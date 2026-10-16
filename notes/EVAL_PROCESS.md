# The evaluation process, end to end

How an answer becomes a number, and how a number becomes a claim. Written 2026-10-14 against `FINAL_v2/`.

## 1. Inputs
* **Datasets (31).** Each adapter reads the official test or dev split and emits items with a question, context (table, document or record
  pair), a gold answer with aliases, list golds where the answer is a set, an answer type (numeric / boolean / text / free-form) and the dataset's
  native metric. Entity-matching pairs are sampled half match / half non-match (Papadakis–Christen keeps its real 1.8 % ratio); schema matching
  is framed as one question per source column with a candidate list; BIRD is graded on the executed result value.
* **Pools.** 150 items per dataset by seeded stratified sampling (strata: question type, sub-task, database, product category, match label);
  100 flagged for answering (`in_real_subset`); the other 50 are a seeded reserve, stored in the pool file but not used by any step of the current pipeline (every script filters on the flag). OfficeQA Pro V2 has all 90; Alaska schema 93.
* **Official census.** For post-stratification, every dataset's official population is counted by the same strata (`_official_strata.json`).

## 2. Collecting answers
* One prompt per item: context, the question, and an answer-format line asking for `FINAL ANSWER: <answer>`.
* Eleven models (Claude Opus 5 / Sonnet 5, GPT-5.5 / 5.4-mini, Gemini 3.1 Pro, Gemini 3.8 Flash, Grok 4, DeepSeek chat / R1, gpt-oss-120b, Llama 3.3 70B); Gemini
  3.1 Pro was collected over three weeks under Google's daily quota (GitHub Actions trickle plus a final local run on 2026-10-16) and entered the study at full coverage.
* Decoding: temperature 0 where the API accepts it; Claude 5 and GPT-5.5 refuse it and ran at their defaults; every row records which applied.
* Output budget 700 tokens. Answers cut off before a final line were re-asked at 2,500, then 8,000, then 16,000 tokens (32,000 for two Claude Sonnet 5 answers); 41 DeepSeek-R1 answers never terminated at 16,000 and are scored as failures to answer, and 123 DeepSeek-R1 answers await their 16,000-token re-ask (provider balance) at their 8,000-token replies. The budget is counted in each provider's own tokens and, for reasoning models, includes the chain of thought, so it is a termination test rather than an equal text allowance. Replacement is triggered only by the mechanical condition, never by correctness; originals are archived with a reason and
  replacement rows carry `attempt = 2` to `5`.
* Every answer is cached (`data/predictions/<model>.jsonl`) with tokens, latency, cost, finish reason and decoding; reruns skip cached items.

## 3. Scoring an answer
* Extraction: the `FINAL ANSWER:` line, else a boxed expression, else the last short line.
* Normalisation: Unicode, case, punctuation, articles, and number parsing with sign, percent, unit words and scale (million / billion).
* The four v1 ingredients per answer: token F1, numeric decay e^{−2.5·relative error}, token precision, token recall, each taken as the maximum
  over the gold's aliases; plus exact match, numeric tolerance (1 %) and a hedge flag. Native metric per dataset: numeric tolerance for
  numeric golds, exact match for text / boolean, ROUGE-L for free-form.
* Composite under weighting w: R = Σ_k w_k m_k. Dataset score for a model = mean of R over the items every model answered (a model is in the
  study only if it covered ≥ 90 % of the suite; items count only when all models answered them).

## 4. Evaluating a weighting (the audit)
1. **Agreement J(w).** Rank the models inside each dataset under w; pool the 31 rankings by Borda; J = mean Kendall τ-b between each
   dataset's ranking and the pooled one. Computed for all 1,771 step-0.05 weightings (also under Kemeny, Copeland and Bradley–Terry pooling).
2. **Correctness ρ(w).** 31,380 synthetic answers of known utility, generated from the golds by typed operators (alias, unit change, rounding,
   magnitude error, wrong value, partial list, hedge, paraphrase …). Spearman between R and utility; AUC correct vs wrong; mean score of wrong
   answers; hedge gap.
3. **Honest selection.** 1,000 item bootstraps: choose the best w on in-bag items, score it out of bag. Report the optimism gap, the paired
   out-of-bag difference to v1, and the plateau of weightings not significantly below the best.
4. **Transfer.** Leave-one-dataset-out and leave-one-family-out (entity matching, schema, table QA, finance); per-family optima; sensitivity
   to one-step weight moves.
5. **Designs.** Uniform, Dirichlet-snapped and Latin-hypercube samples of 100 weightings, 20 seeds, compared with the exhaustive optimum.

## 5. From scores to a leaderboard
* Rules reported: exact match, v1, the five best by J, the best by ρ, the (J, ρ) Pareto knee.
* Pooling: Bradley–Terry strengths (item-level pairwise wins, MLE, standard errors) as the headline; Borda, mean-z, Kemeny (with cost),
  Copeland, reciprocal-rank fusion and family-balanced z as checks.
* Uncertainty: 1,000 item bootstraps of the Borda and Bradley–Terry rankings (rank intervals, probability of first place), saved in full.
* Significance: Friedman with Iman–Davenport across datasets, Nemenyi critical difference, Holm-corrected pairwise Wilcoxon; paired permutation
  and Wilcoxon per dataset and model pair (Holm within dataset); Kendall's W among datasets; majority-class baselines for boolean sets.
* Official-split estimates: the same answers re-weighted by official stratum share / sample share (post-stratification), with a weighted
  bootstrap; positive-class precision / recall / F1 at the official match ratio for the matching sets.
* Diagnostics: pairwise τ between dataset rankings, floor / ceiling / self-stability flags per dataset.

## 6. Reporting
`v2_gridsearch/scripts/run_all.sh` runs steps 1–6 from the cache in minutes and writes `REPORT.md` from the output files, so the text can never
disagree with the numbers. Per rule, `output/leaderboards/<rule>/` holds the leaderboard, parameters with SE, bootstrap draws, significance,
pairwise tests, per-dataset means and SEs, official-split estimates and a LaTeX table.

## 7. What the process cannot do
Lexical scoring only (no semantic judge); synthetic rather than human quality labels; one prompt; defaults rather than greedy decoding on two
providers; 41 non-terminating answers (DeepSeek-R1) scored as wrong and 123 R1 answers awaiting the 16,000-token stage; three datasets at ceiling still inside the objective; exact
match (not F1) as the native metric for boolean sets inside the objective.
