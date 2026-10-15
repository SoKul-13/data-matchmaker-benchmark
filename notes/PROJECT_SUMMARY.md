# Project summary (2026-10-14)

## What this repository is
A benchmark and an audit for LLM judges on data-matching tasks: entity matching, schema matching, table question answering and financial
document reading. The deployed judge (v1) scores answers with a hand-set composite of four lexical metrics. Over ten days in September 2026 the
judge was audited, the dataset suite rebuilt from literature evidence, ten models run on 31 datasets, and the whole evaluation made
reproducible from cache. The final, self-contained version is `FINAL_v2/`; the sister methods (v3 aggregation, v4 nine-metric search, v5
anchor-calibrated ensemble) live in `v6_top30_significance/` on the same answers; the originals are archived in `other_older_versions/`.

## The headline result
The deployed weights are as good as any weighting of their ingredients. Over all 1,771 weightings the agreement objective spans only
0.39–0.42; 1,765 are statistically indistinguishable from the best; with honest (out-of-bag) selection the best is 0.008 below v1 with a
confidence interval spanning zero; and v1's correctness on 31,380 known-quality answers (ρ 0.878) is within 0.005 of the best achievable.
The sister methods agree: v4 finds a single typed metric (numeric tolerance) matches the nine-component composite; v5's calibrated ensemble
reaches ρ 0.904 with decay-dominated weights.

## The leaderboard
Ten models, 3,083 answers each, Friedman p < 0.001 under every rule. Claude Opus 5, GPT-5.5 and Gemini 3.8 Flash are above the open models
with Holm-corrected significance; Llama 3.3 70B is last; the order inside the top four depends on the pooling rule (Bradley–Terry favours
Gemini Flash under the calibrated rules, Borda favours GPT-5.5, exact match favours Opus). Datasets agree only moderately (Kendall's W ≈ 0.27).
Gemini 3.1 Pro is being collected at 240 answers a day (2,172 of 3,083 on 2026-10-14) and enters the study automatically at 90 % coverage.

## How the suite was chosen
231 candidate datasets surveyed; 111 scored on a seven-criterion rubric; adoption re-measured from ~220 top-cited papers after the user
rejected judgement-only scoring; the evidence top 30 plus the benchmark's original document set form the suite (11 entity matching, 6 schema,
11 table, 3 finance). Pools are stratified samples of the official splits; post-stratification makes per-dataset numbers comparable to
published results (balanced matching pools inflate F1 by up to 0.6 on the hardest sets).

## What it cost and what went wrong
USD 161 in API answers (Claude Opus 99). Problems met and resolved: 700-token truncations (three-attempt protocol), an OpenAI project spend
limit, Google's 250-a-day quota for Gemini Pro (GitHub Actions trickle with the key as a repository secret), a coverage-rule bug that produced
empty cells and NaN rankings (suite-wide model rule), a stale anchor cache (rebuilt), v3's runtime at ten models (shorter split-half loop),
and an unstable rank for v1 inside a flat objective (report the plateau, not the rank).

## Where things are
| Need | File |
|---|---|
| The result | `FINAL_v2/v2_gridsearch/REPORT.md`; every number traceable to `FINAL_v2/v2_gridsearch/output/` |
| How the process works | `notes/EVAL_PROCESS.md` |
| Full review with decision history | `notes/FINAL_V2_REVIEW.md` |
| Every design decision with alternatives and literature | `notes/DECISIONS_AND_RATIONALE.md` |
| Pre-run audit of the code | `notes/PRE_RUN_REVIEW.md` |
| How each version searches | `notes/SEARCH_DESIGN_REPORT.md` |
| The 30 datasets and why | `notes/TOP30_DATASETS_AND_PRE_RUN_NOTES.md`; survey in `datasets_survey/` |
| Planned v2 variants for the paper | `notes/V2_VARIANTS_PLAN.md` |
| Model access and costs | `notes/MODEL_ACCESS_REQUEST.md` |
| Formulas across versions | `notes/GUIDE_UNDER_THE_HOOD.md`; `notes/OVERALL_SUMMARY.md` |
| Paper plan, figures, partial draft | `FINAL_v2/paper/` |
| Summary reports per version (Overleaf packages: Setup + Results + every figure, table and data file) | `FINAL_v2/paper/{v2,v3,v4,v5,comparison}/` and the matching `*_overleaf.zip`; index in `FINAL_v2/paper/README.md` |
| Human-label protocol, model-run instructions, code flow | `FINAL_v2/notes/` |
| Daily Gemini Pro collection | `.github/workflows/gemini-pro-trickle.yml`, branch `gemini-pro-trickle`, PR #1 |

## Open items
1. Merge the Gemini Pro PR once the branch passes 2,775 answers, then re-run `FINAL_v2/v2_gridsearch/scripts/run_all.sh`.
2. Optional checks: 3× repeat subset (≈ USD 4), format-repair turn (cents), 50-answer hand check of the extraction fallback.
3. Code items from the variants plan: ceiling datasets out of the objective; F1 as native metric for boolean sets; extraction-path logging.
4. Human labels on 400 answers (`FINAL_v2/notes/HUMAN_LABELLING_PROTOCOL.md`).
5. Finish the paper draft from `FINAL_v2/paper/PAPER_PLAN.md`.
