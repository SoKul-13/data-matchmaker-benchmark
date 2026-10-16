# FINAL_v2 review: results, decisions, how they were reached, and what was rejected along the way

Date: 2026-09-27. Scope: the final v2 evaluation in `FINAL_v2/` (self-contained copy of `v6_top30_significance/v2_gridsearch`), the road that
led to it, and the reasoning behind every material choice. Numbers are from `FINAL_v2/v2_gridsearch/REPORT.md` generated 13:12 on 2026-09-27
on the final answer cache.

---

## 1. The question and the one-paragraph answer

v1, the deployed judge, scores an answer as 0.35·token-F1 + 0.35·numeric-decay + 0.15·precision + 0.15·recall with weights set by hand.
The audit asks whether those weights are defensible. Answer: **yes, and no weighting of those four ingredients is defensibly better.** Over
every one of the 1,771 step-0.05 weightings, the agreement objective ranges only from 0.38 to 0.41; the whole lattice is one statistical plateau
(1,749 of 1,771 weightings are not distinguishable from the best), v1 sits inside it, and when selection is done honestly (choose on in-bag items,
score on out-of-bag items) the "best" weighting is 0.008 *below* v1 with a confidence interval that spans zero. On correctness against 31,380
answers of known quality, v1's correlation (0.878) is within 0.005 of the best achievable (0.883). The deployed weights are as good as any.

## 2. The final result in numbers

Data: 31 datasets × 11 models × 100 items = 3,083 answers per model (Gemini 3.1 Pro completed on 2026-10-16; numbers below are from the 2026-10-16 14:32 run).

| Quantity | Value |
|---|---|
| Exhaustive grid | 1,771 weightings (step 0.05); best F1 .35 / decay .60 / precision .05, J = 0.414; v1 J = 0.392 (rank 1,602) |
| J over the lattice | median 0.409, 99th percentile 0.418: a flat landscape |
| Plateau (paired bootstrap p > .05 vs best) | 1,749 of 1,771 (v1 inside, p = 0.63); practical plateau within 0.02: 1,731 |
| Nested selection (B = 1,000) | in-bag J of selected 0.380, out-of-bag 0.331 (optimism gap 0.049); v1 out-of-bag 0.339 |
| Selected vs v1, out of bag | −0.007, 95 % CI [−0.033, +0.011], p = 0.72; 624 distinct weightings selected across resamples (optimism gap 0.047) |
| Sampled designs (100 points, 20 seeds) | Dirichlet / LHS / uniform all reach 0.418 ± 0.001, regret ≤ 0.005: sampling would have sufficed |
| Objective under other pooling rules | Kemeny, Copeland, Bradley–Terry each pick a different "best"; v1's rank swings from 393 to 1,506: rank is noise |
| Transfer (leave-one-dataset-out) | held-out τ: LODO weights +0.33, full best +0.35, v1 +0.32 |
| Leave-one-family-out | v1 within 0.02 of the held-out-fitted weights on EM, SM, TQA; FIN favours precision-heavy weights (0.51 vs 0.43) |
| Anchors (31,380 synthetic answers) | v1 ρ 0.878, best-ρ weighting 0.883, best-J weighting 0.876, exact match 0.828; AUC correct-vs-wrong 0.994 everywhere; Spearman(J, ρ) −0.23 |
| J vs ρ across the lattice | −0.34 on this cache; +0.38 on the previous cache: unstable because J is flat |
| Leaderboard | Friedman p < 0.001 under every rule; Kendall's W among datasets 0.26–0.27; Gemini 3.1 Pro enters fifth by Bradley–Terry under v1 |
| Significant pairs (Holm) | 15 of 55: nine models > Llama 3.3 70B; Opus, gpt-5.5, Gemini 3.1 Pro, Gemini Flash, DeepSeek R1 and Grok 4 > gpt-oss-120b |
| First place | Bradley–Terry: Gemini 3.8 Flash under v1 and the calibrated rules, Opus under exact match; Borda: gpt-5.5 under v1, Opus under exact match and the top-5 |
| Datasets at ceiling | Valentine, WDC LSPC, WDC Products (means 0.98): flagged; still inside the objective (see §6) |
| Cost | USD 174 for the final cache (Opus 107, Gemini 3.1 Pro 12); USD 224 over the project including archived truncated originals |

The Bradley–Terry and Borda rankings agree on the bottom half and on the set {Opus, gpt-5.5, Gemini Flash, Grok} at the top, and disagree on
the order inside that set. That disagreement, not any single first place, is the paper's leaderboard result.

## 3. How we got here: the history, and why each turn was taken

1. **v1 → the survey question (early September).** v1 scored the join task with a 100-point rubric and QA with the hand-set composite. The
   first request was to calibrate the weights across many datasets and produce one comparable score. Five methods were built in succession:
   v2 (grid over v1's weights), v3 (aggregation rules from ten papers), v4 (nine-metric composite, random search, rank agreement), v5 (100-metric
   library calibrated on synthetic anchors). Each answered a different question; none had a defensible dataset suite, and all had four models
   and 40 items per dataset.
2. **Dataset survey (2026-09-14).** 231 candidates surveyed, 111 scored on a written rubric. The user rejected judgement-only adoption
   ("not just what you think"), so adoption was re-measured from a citation-ranked corpus of about 220 papers per area. The evidence ranking put the
   Magellan matching sets and schema matching at the top and dropped FinQA and FinanceBench out of the top 30. Suite = top 30 + OfficeQA.
3. **Pre-run review (2026-09-23).** Before spending money, the code was audited: no decoding settings, 40 vs 150 items inconsistency,
   balanced entity-matching pools vs 10–20 % official ratios, winner's curse in the selection, floor datasets counting as zero agreement.
   Each became a fix or a stated limitation.
4. **Decision document.** Twelve decisions with options, trade-offs and literature (`DECISIONS_AND_RATIONALE.md`); the user asked what makes
   a workshop paper defensible, and the answer shaped v6: validate the scoring rule against something outside the ranked models, carry honest
   uncertainty, and be reproducible.
5. **v6 build (2026-09-23).** All four versions copied onto one shared suite with the same additions: exhaustive or Latin-hypercube designs,
   nested selection, transfer tests, anchors, leaderboards with parameters and significance, post-stratified official-split estimates.
6. **FINAL_v2 (2026-09-26).** The user chose v2 as the paper's lead and asked for a self-contained copy; the originals moved to
   `other_older_versions/`.
7. **Model run (2026-09-26/27, completed 2026-10-16).** Eleven models, USD 174 in the final cache, four truncation stages (five for two answers), a quota wall for Gemini Pro, an OpenAI project limit, and a
   coverage-rule bug found by the first full pipeline run. All resolved; see §5.
8. **Final reports (2026-09-27).** All five pipelines regenerated on the final cache.

## 4. The decisions, with the alternatives that were rejected

**Suite: evidence top 30 + OfficeQA, not the original 7 and not the top 50.** The original 7 had no data-matching dataset at all, so the
benchmark's name was unsupported. The top 50 adds only second representatives of families already covered, at the cost of 20 more adapters.
Rejected: judgement-only ranking (not auditable); full official test sets (20× the cost for precision the pooled claim does not need).

**100 items per dataset, not 40 or 150.** At 40 a 70 % score means "55–85 %"; at 100 it means "61–79 %", which is where intervals stop
overlapping for models 10 points apart (Card et al. 2020). 150 gave diminishing returns for 3× the Opus bill. The pools hold 150 so the reserve
feeds the anchors for free and can extend later without changing the first 150.

**Exhaustive grid for v2, not random or Latin hypercube.** With four weights the lattice has 1,771 points and costs seconds; enumerating it
makes the claim exact ("over every weighting…"). The sampled designs were still run for comparison and reached the same optimum within 0.005,
which is itself worth a sentence: for this objective any design would have done. Random and LHS stay in v3 and v4, whose lattices have
888,030 and 3.1 million points.

**Agreement objective kept, correctness added as a separate check, not swapped in.** J (mean Kendall τ of each dataset's ranking to the
Borda pool) is v2's original objective and measures consistency, not correctness; swapping it would have made v2 a different method (that is
v5). Instead v5's anchors are scored under every v2 weighting so each has both numbers. Rejected: making J the paper's accuracy claim (it is
not one), and dropping J (it is the question v2 asks).

**Nested bootstrap plus leave-one-dataset-out plus leave-one-family-out, not the original "best of 105 with a CI on the same items".** Choosing
a maximum of 1,771 candidates on the data used to score it inflates the winner (Cawley & Talbot 2010); the optimism gap of 0.049 is the measured
size of that inflation here. LODO and LOFO test transfer across datasets and task types. Rejected: only LODO (v4's approach), because it does not
address selection on items within datasets.

**Bradley–Terry headline with Borda, mean-z, Kemeny, Copeland, RRF and family-balanced checks.** BT is the Chatbot Arena standard and v3's
reliability study picked it with four models; with ten models v3 now finds mixes of views more stable, so the report shows every rule and the
disagreement between them rather than declaring one winner. Rejected: a single pooled number without the others (hides the disagreement).

**Temperature 0 where accepted, recorded per row where refused.** Claude 5 reports the parameter deprecated and gpt-5.5 rejects any value but
its default, so the closed flagships ran at provider defaults; Gemini, Grok, DeepSeek, Llama and gpt-oss ran greedy. The decoding field on every
row is the record. Rejected: three samples per item with majority vote (3× cost, and it measures a voting system rather than the model); the
3× repeat subset (≈ USD 4) is still the right way to measure the residual variance and is still open.

**Truncation protocol: 700 → 2,500 → 8,000 → 16,000 tokens (32,000 once), then scored as failure.** The 700-token budget cut off 5 % of answers, mostly on
reasoning models; 2,500 left 461; 8,000 left 209; the 16,000-token stage added on 2026-10-16 finished every Claude Opus 5 and gpt-oss-120b answer, 8 of 10 Sonnet answers (the last two at 32,000) and 95 of 218 DeepSeek R1 answers; 41 R1 answers (30 OfficeQA, 8 BIRD) do not terminate at 16,000 and 123 R1 answers await the stage on provider balance.
Replacement is triggered only by a mechanical condition (no final line before the cap), never by whether the answer was right; every original is
archived under `_replaced/` with a reason and every replacement row carries its attempt number. Rejected: leaving 700 as the cap (a budget
artefact would have scored 5 % of answers wrong); an unbounded budget (cost, and R1 shows some never finish).

**Coverage rule: a model is in the study for the whole suite or not at all; items count only when every model answered.** The first full
pipeline run crashed because Gemini Pro's 252 answers created empty cells that turned every pooled ranking into NaN. Per-dataset model
exclusion (the earlier rule) is exactly what produces missing cells. Rejected: imputation (invents answers); per-dataset model sets (no
paired tests).

**Post-stratification, not resampling, for official-split comparability.** The pools draw strata equally so calibration sees every kind of
item, but the official splits are 10–20 % matches for entity matching and have their own question-type mix. Re-weighting the same answers by
official-share / sample-share gives an unbiased official-split estimate (Horvitz–Thompson) with a weighted bootstrap, and positive-class F1 at
the official match ratio, for no new spend. It matters: Amazon-Google accuracy 0.94 becomes F1 0.70 at the official ratio; Papadakis–Christen
0.92 becomes F1 0.32 for Opus. Rejected: re-sampling the pools to official proportions (would starve calibration of rare strata).

**Models: flagship plus standard tier per provider, no small models; direct-route keys, no OpenRouter.** The user's rule from the start,
and the user's choice on the route. Groq's free tier lost Llama in August, so Llama went to Together; gpt-oss moved from Groq's free tier to
Together for USD 0.66 to avoid a four-day trickle; Qwen has no serverless open-weight host left and is disabled; Mistral's free tier returns
rate-limit errors on every call and is excluded. Gemini Pro trickles at 240 items a day through a GitHub Actions workflow with the key as a
repository secret, after the Claude cloud routine turned out to have no place for a secret.

## 5. What went wrong, and what each cost

| Problem | Cause | Resolution |
|---|---|---|
| Estimate too low for Anthropic | Anthropic's tokenizer counts these prompts at ~900 tokens, not 550; output prices 15/75 | Opus USD 99 vs 40 estimated; everything else at or under estimate |
| OpenAI project spend limit | a per-project enforced limit, not the balance | user raised it; 285 items re-asked, USD 6 |
| Gemini Pro quota | ~250 requests/day on Tier 1 for the preview model; no GA Pro model available to new accounts | left out by the coverage rule; daily trickle via GitHub Actions |
| First pipeline crash | partial model created NaN cells | suite-wide coverage rule (§4) |
| Stale anchor cache | the five-dataset anchor file was reused after the suite grew, giving a wrong per-dataset column | caches deleted and rebuilt before any report was cited |
| v3 split-half runtime | 1,050 Rasch fits on 3,083 items × 10 models | 20 splits × 8 inner resamples (still a valid check) |
| Rank instability | J range 0.03–0.04; v1's rank moved 724 → 1,483 → 1,602 and the J–ρ correlation went +.38 → −.34 → −.23 across the 2,500-token, 8,000-token and eleven-model caches | report the plateau and the out-of-bag difference; never the rank |

## 6. What the paper can and cannot say

Can: v1's weights are inside the plateau of equivalent weightings on agreement and within 0.005 of the best on correctness; the audit's
method (exhaustive grid, nested selection, transfer, anchors) is the contribution, and the negative result is the honest outcome. The leaderboard
separates the ends at p < 0.001 and the pooling rule decides the order at the top. Official-split estimates make per-dataset numbers comparable
to published ones where the population is the published split.

Cannot: rank v1 among weightings (the rank is noise inside a flat objective); claim accuracy from J; claim that the four-ingredient composite
is better than a single typed metric (v4 shows numeric tolerance alone ties it); claim anything for Gemini Pro until its trickle completes.

Two known gaps remain in the code, both small: the three ceiling datasets (Valentine, WDC LSPC, WDC Products at 0.98) are flagged by the
diagnostics but still inside the objective, and positive-class F1 is reported for the matching sets but exact match is still their native metric in
the objective. Both are items 4 and 5 of `V2_VARIANTS_PLAN.md`.

## 7. Open items
1. Gemini Pro trickle: push the repo with FINAL_v2 and the workflow, add the `GEMINI_API_KEY` repository secret, allow Actions to open PRs.
2. Format-repair turn on the ~2 % of answers with the value buried in a sentence (cents); the 3× repeat subset for answer variance (≈ USD 4).
3. Fixes 4, 5 and 8 of the variants plan (ceiling datasets out of the objective; F1 as native for boolean sets; extraction-path logging).
4. Human labels on 400 answers (`FINAL_v2/notes/HUMAN_LABELLING_PROTOCOL.md`), the only thing that replaces the synthetic anchors.
5. Commit and push; nothing is committed yet.

## 8. Where everything is
`FINAL_v2/v2_gridsearch/REPORT.md` (the result) and `output/` (every candidate, every bootstrap draw, every parameter, per-rule leaderboards with
significance and official-split estimates); `FINAL_v2/data/predictions/` (answers, `_replaced/` originals); `DECISIONS_AND_RATIONALE.md`,
`PRE_RUN_REVIEW.md`, `SEARCH_DESIGN_REPORT.md`, `TOP30_DATASETS_AND_PRE_RUN_NOTES.md`, `V2_VARIANTS_PLAN.md` (the reasoning trail);
`datasets_survey/` (how the suite was chosen); `v6_top30_significance/` (v3, v4, v5 on the same answers); `.github/workflows/gemini-pro-trickle.yml`.
