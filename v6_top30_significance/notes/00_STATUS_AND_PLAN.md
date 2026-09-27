# v6 status and plan (2026-09-23)

## What v6 is
One folder, one suite, four methods. v2, v3, v4 and v5 were copied here, pointed at a shared `data/` and `shared/src/`, and each received
the same additions. v6 is therefore *not* "v2 with extras": the additions are applied to all four, and the paper can lead with whichever
version fits its claim (v2 for an audit of the deployed judge, v5 for a validated scoring rule, v3 for the aggregation choice, v4 as the ablation).

## Additions, and where each lives

| addition | v2 | v3 | v4 | v5 |
|---|---|---|---|---|
| exhaustive grid | 1,771 points (`02_exhaustive_grid.py`) | 255 view subsets (`02_views_combos.py`) | not feasible (3.1 M points) | already exhaustive (6,630) |
| Latin hypercube + other designs, coverage, regret | 3 designs × 20 seeds | LHS + lattice mixes (100 each) | 3 designs × 20 seeds, 100 each | 3 designs × 20 seeds looked up in the grid (`07_…`) |
| nested (in-bag / out-of-bag) selection, optimism gap, plateau | `03_selection_validity.py` | split-half selection (`02_…`) | `03_selection_validity.py` | n/a (objective is anchor-based; top-100 averaging + LODO in `05_validate.py`) |
| leave-one-dataset-out and leave-one-family-out | yes | – | yes | LODO in `05_validate.py` |
| per-family best weights, sensitivity | yes | – | yes | – |
| correctness on known-quality anchors (ρ, AUC, wrong-score, hedge gap, Pareto with J) | `04_correctness_anchors.py` | – (no weights over metrics) | `04_correctness_anchors.py` | the objective itself |
| leaderboards under exact match / deployed / top-5 / anchor-best / Pareto knee | `05_leaderboards.py` | native + exact match + top-5 mixes | `05_leaderboards.py` | em / native / ensemble / top-5 (`07_…`) |
| parameters with standard errors (BT, Rasch, Kemeny cost, Copeland, Borda, win matrix) | per rule (`params.json`) | per view + per bootstrap draw (`params/`, `Zb.npz`) | per rule | per rule |
| bootstrap draws saved (ranks, BT strengths, per-dataset means) | `bootstrap.npz` per rule | `Zb.npz` | `bootstrap.npz` per rule | `bootstrap.npz` per rule |
| Friedman / Iman–Davenport / Nemenyi / Holm-Wilcoxon / paired permutation / Kendall's W | `significance.json`, `pairwise_item_tests.csv` per rule | same | same | same |
| dataset diagnostics (floor / ceiling / self-stability / pairwise τ) | `diagnostics/` | `diagnostics/` | `diagnostics/` | `diagnostics/` |
| official-split estimates (post-stratification, positive-class F1 at official ratio) | `leaderboards/<rule>/official_split_estimates.csv` | same | same | same |
| report assembled from outputs | `06_report.py` | `04_report.py` | `06_report.py` | `08_report.py` |

## Suite
31 datasets: the evidence top 30 (`datasets_survey/05_RANKED_100_evidence.md`) plus OfficeQA closed-book (already answered). finqa and
financebench are present but disabled. 150 items per pool, 100 flagged for answering (OfficeQA Pro V2: all 90; Alaska schema GT: 93, the
camera half of that gold could not be obtained). Entity-matching pools are balanced except Papadakis–Christen (15 % positive by design).

## Decisions taken (see the repo-root `DECISIONS_AND_RATIONALE.md`)
100 items per dataset; temperature 0 with per-row decoding record; all 13 catalogued models on every dataset; Bradley–Terry headline with
Borda / z-mean / family-balanced checks; nested selection everywhere it applies; every candidate, parameter and bootstrap draw saved.

## What the reports show on the full run (2026-09-27; 31 datasets × 10 models × 100 items; Gemini 3.1 Pro left out at 252/3,083 by Google's daily quota)

* **v2 (audit of v1's weights).** Exhaustive 1,771-point grid on the final cache (after the 700 → 2,500 → 8,000-token re-asks): best weighting
  decay .70 / recall .30, J .421 vs v1 .404. The J landscape is flat: the plateau of statistically equivalent weightings covers 100 % of the lattice,
  out of bag the selected weighting is −.008 vs v1 (CI [−.039, +.013]), optimism gap ≈ .05. Because the range of J is only .40–.42, v1's *rank* and the
  sign of the J-vs-ρ correlation moved between the 2,500-token cache (rank 724, +.38) and the 8,000-token cache (rank 1,483, −.34) while the
  substantive result did not: report the plateau and the out-of-bag difference, not the rank or that correlation. Anchors: v1 ρ .878 within .005 of
  the best possible (.883). Verdict: v1's hand-set weights are as good as any weighting of the four ingredients, on agreement and on correctness.
* **v4 (nine components).** Best candidate = numeric tolerance alone (J .438), tied with exact match alone (.437); v1 rubric .403 (rank 289);
  out-of-bag difference to v1 .000; J vs ρ +.05. The 9-component composite buys nothing over a single typed metric on this suite.
* **v3 (aggregation).** All 255 subsets + 200 mixes: uniform mix J .946, best LHS mix .951; pure Bradley–Terry .903 is now the *weakest* single view
  (z-mean .933, raw mean .935 strongest). Split-half (20 splits): selected mix beats pure BT on held-out halves in 80 % of splits (+.032). With ten
  models and 3,083 items, mixing views is defensible; with four it was not.
* **v5 (anchor-calibrated ensemble).** Selected metrics token F1 / numeric decay / prefix ratio; ensemble decay .79, F1 .14, prefix .07, λ .54; anchor ρ .903,
  AUC .996. Designs: every sampled design is within .01 of the exhaustive optimum.
* **Leaderboard (all versions agree on the ends, disagree in the middle).** Friedman p < .001 under every rule; Holm-corrected wins for Claude Opus,
  gpt-5.5 and Gemini Flash over gpt-oss-120b and Llama 3.3 70B (last). First place depends on the pooling rule: Bradley–Terry puts Gemini 3.8 Flash
  first under the calibrated rules, Borda puts gpt-5.5 first with Opus second; under exact match Opus is first under both. Kendall's W among
  datasets ≈ .27–.29: the datasets agree only moderately, which is the reason a calibrated rule and a stated pooling rule are needed at all.
* **Run facts for the paper.** 1,544 answers (5 %) hit the 700-token budget and were re-asked at 2,500 tokens; 461 still hit that and were re-asked at 8,000; 184 (mostly DeepSeek R1: 160, 5 % of its items) never finished and are scored as failures to answer (originals archived under `_replaced/`, replacements tagged attempt 2 / 3);
  temperature 0 was refused by Claude 5 and gpt-5.5 (recorded per row); one refusal (Sonnet); ≈ 2 % of gpt-5.5 / R1 answers lack a final-answer line
  and rely on the last-line fallback. Cost ≈ USD 161 (Opus 99). Gemini 3.1 Pro trickles in via the cloud routine `gemini-pro-trickle` (240 items/day, branch + PR).

## Next
1. Done: model run and all four pipelines on the full suite. Open: Gemini 3.1 Pro (quota), the format-repair turn (≈ 2 % of answers), the 3× repeat subset (≈ USD 4), fix 4/5/8 of `V2_VARIANTS_PLAN.md`.
2. Human labels (`notes/HUMAN_LABELLING_PROTOCOL.md`) to replace the synthetic anchors in v2 §5 and v5.
3. Paper: structure in `DECISIONS_AND_RATIONALE.md` §11; tables come from `leaderboards/<rule>/table.tex` and the reports.
