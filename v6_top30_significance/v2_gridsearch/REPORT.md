# v2 report: an audit of the deployed judge's weights, done exhaustively

Generated 2026-09-27 13:46. Data: 31 datasets × 10 models, 3083 answered items in total (abt_buy 100, alaska_camera 100, alaska_schema 93, amazon_google 100, bird 100, dblp_acm 100, dblp_scholar 100, fetaqa 100, fintagging 100, hitab 100, machamp 100, magneto_gdc 100, mmtu 100, officeqa 100, officeqa_pro_v2 90, opensanctions_pairs 100, papadakis_dn 100, realhitbench 100, smat 100, suc 100, tab_fact 100, tabis 100, tablebench 100, tableeval 100, tat_qa 100, tpcdi_cells 100, valentine 100, walmart_amazon 100, wdc_lspc 100, wdc_products 100, wikitablequestions 100). Models: claude-opus-5, claude-sonnet-5, deepseek-chat, deepseek-r1, gemini-3.8-flash, gpt-5.4-mini, gpt-5.5, gpt-oss-120b, grok-4, llama-3.3-70b. Every number below is read from `output/`; `scripts/run_all.sh` regenerates everything from the cached answers in a few minutes.

## 1. Question and design

v1 scores an answer as 0.35·F1 + 0.35·numeric-decay + 0.15·precision + 0.15·recall. Are those weights defensible? We evaluate **every** weighting on the step-0.05 simplex lattice (1,771 points; v1, the four corners and the uniform mix are lattice points), not a sample. The objective J is the mean Kendall τ between each dataset's model ranking and the Borda-pooled ranking: it measures **consistency between datasets, not correctness**. Correctness is checked separately in section 5 with known-quality anchors. Selection honesty (section 3), transfer (section 4), sensitivity (section 6), leaderboards under the naive, deployed and calibrated rules with significance tests (section 7) and dataset diagnostics (section 8) follow.

## 2. Exhaustive grid

* Best weighting: f1 0.00, decay 0.70, precision 0.00, recall 0.30 with J = 0.421 (τ to native metrics 0.91).
* v1: J = 0.404, rank 1483 of 1,771; 1482 weightings are better (84 %), 5 tie.
* Corners and uniform: only f1 0.411, only decay 0.404, only precision 0.398, only recall 0.400, uniform 0.410.
* J quantiles over the lattice: median 0.409, 90 % 0.415, 99 % 0.418.
* Objective robustness: the best under Kemeny pooling is f1 0.20, decay 0.00, precision 0.50, recall 0.30 (J 0.425, v1 rank 1506); under Copeland f1 0.20, decay 0.00, precision 0.50, recall 0.30 (v1 rank 1489); under Bradley–Terry f1 0.00, decay 0.60, precision 0.00, recall 0.40 (v1 rank 393). v1's J under the four rules: Borda 0.404, Kemeny 0.408, Copeland 0.409, BT 0.390.
* Top 5 by J: #1 f1 0.00, decay 0.70, precision 0.00, recall 0.30 (J 0.421); #2 f1 0.35, decay 0.10, precision 0.10, recall 0.45 (J 0.419); #3 f1 0.40, decay 0.10, precision 0.05, recall 0.45 (J 0.419); #4 f1 0.05, decay 0.60, precision 0.25, recall 0.10 (J 0.419); #5 f1 0.00, decay 0.60, precision 0.00, recall 0.40 (J 0.419).

Figures: `fig_landscape` (sorted J with v1 and corners), `fig_marginals` (J against each weight), `fig_designs`.

### 2b. Sampled designs at a budget of 100 (20 seeds each)

| design | best J found (mean ± sd) | regret vs exhaustive (mean / max) | rank of found best in the grid (median / worst) | min pairwise L1 | centred L2 discrepancy | share with a zero weight |
|---|---|---|---|---|---|---|
| dirichlet_lattice | 0.418 ± 0.001 | 0.004 / 0.005 | 14 / 49 | 0.10 | 0.538 | 0.27 |
| lhs_simplex | 0.418 ± 0.001 | 0.003 / 0.005 | 10 / 49 | 0.10 | 0.531 | 0.28 |
| uniform_lattice | 0.418 ± 0.001 | 0.003 / 0.005 | 6 / 42 | 0.10 | 0.526 | 0.45 |

Reading: with four weights the exhaustive grid is cheap, so the sampled designs only matter as a rehearsal for v3/v4; their regret and discrepancy are reported for that comparison.

## 3. Is the best weighting real? Nested selection and plateau

* Nested item bootstrap (B = 1000): the weighting selected on in-bag items has mean in-bag J 0.380 but out-of-bag J 0.331 (**optimism gap 0.049**). v1's out-of-bag J is 0.339; the full-data best's is 0.332.
* Selected vs v1 out of bag: mean difference -0.008, 95 % CI [-0.039, +0.013], one-sided bootstrap p = 0.721 (share of resamples where the selected weighting is ahead: 0.28).
* Full-data best vs v1: in-bag p = 0.664; out-of-bag p = 0.715.
* Selection instability: 608 distinct weightings were selected across resamples; mean selected weights f1 0.33, decay 0.26, precision 0.16, recall 0.25 (sd f1 0.28, decay 0.23, precision 0.15, recall 0.25). Most often: f1 0.00, decay 0.30, precision 0.00, recall 0.70 (1 %); f1 0.80, decay 0.00, precision 0.20, recall 0.00 (1 %); f1 0.90, decay 0.00, precision 0.10, recall 0.00 (1 %).
* **Plateau** (weightings not significantly below the best, paired bootstrap p > .05): 1765 of 1771 (100 %); v1 inside: True (p vs best 0.66). Practical plateau (bootstrap-mean J within 0.02 of the best): 1720 weightings, v1 inside: True; weight ranges inside it: f1 [0.00, 1.00], decay [0.00, 1.00], precision [0.00, 0.85], recall [0.00, 0.95].
* v1 is in the top 5 % of in-bag J in 5 % of resamples.

Figures: `selection/fig_nested`, `selection/fig_plateau`.

## 4. Transfer: leave-one-dataset-out and leave-one-family-out

| held out | J on the rest (LODO weights) | LODO weights | τ held-out → pooled rest: LODO weights | full best | v1 |
|---|---|---|---|---|---|
| abt_buy | 0.413 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.76 | +0.76 | +0.81 |
| alaska_camera | 0.450 | f1 0.15, decay 0.25, precision 0.35, recall 0.25 | -0.42 | -0.49 | -0.44 |
| alaska_schema | 0.437 | f1 0.00, decay 0.25, precision 0.40, recall 0.35 | -0.20 | -0.07 | -0.20 |
| amazon_google | 0.435 | f1 0.30, decay 0.20, precision 0.10, recall 0.40 | +0.00 | -0.07 | -0.02 |
| bird | 0.418 | f1 0.35, decay 0.60, precision 0.05, recall 0.00 | +0.31 | +0.42 | +0.54 |
| dblp_acm | 0.416 | f1 0.00, decay 0.15, precision 0.10, recall 0.75 | +0.66 | +0.64 | +0.64 |
| dblp_scholar | 0.433 | f1 0.05, decay 0.60, precision 0.25, recall 0.10 | +0.00 | -0.05 | +0.00 |
| fetaqa | 0.421 | f1 0.30, decay 0.25, precision 0.10, recall 0.35 | +0.49 | +0.47 | +0.42 |
| fintagging | 0.419 | f1 0.00, decay 0.15, precision 0.25, recall 0.60 | +0.37 | +0.67 | +0.47 |
| hitab | 0.442 | f1 0.00, decay 0.25, precision 0.40, recall 0.35 | -0.31 | -0.29 | -0.31 |
| machamp | 0.416 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.69 | +0.69 | +0.74 |
| magneto_gdc | 0.421 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.51 | +0.47 | +0.54 |
| mmtu | 0.419 | f1 0.35, decay 0.05, precision 0.10, recall 0.50 | +0.49 | +0.69 | +0.56 |
| officeqa | 0.413 | f1 0.20, decay 0.00, precision 0.50, recall 0.30 | +0.58 | +0.69 | +0.56 |
| officeqa_pro_v2 | 0.416 | f1 0.00, decay 0.60, precision 0.00, recall 0.40 | +0.58 | +0.51 | +0.56 |
| opensanctions_pairs | 0.431 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.00 | +0.09 | +0.04 |
| papadakis_dn | 0.437 | f1 0.00, decay 0.15, precision 0.10, recall 0.75 | +0.03 | +0.13 | +0.08 |
| realhitbench | 0.409 | f1 0.00, decay 0.25, precision 0.40, recall 0.35 | +0.67 | +0.73 | +0.60 |
| smat | 0.429 | f1 0.05, decay 0.10, precision 0.10, recall 0.75 | +0.28 | +0.33 | +0.38 |
| suc | 0.419 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.58 | +0.67 | +0.58 |
| tab_fact | 0.437 | f1 0.00, decay 0.65, precision 0.00, recall 0.35 | -0.07 | -0.04 | -0.04 |
| tabis | 0.426 | f1 0.20, decay 0.00, precision 0.50, recall 0.30 | +0.39 | +0.48 | +0.43 |
| tablebench | 0.420 | f1 0.00, decay 0.10, precision 0.30, recall 0.60 | +0.51 | +0.42 | +0.51 |
| tableeval | 0.429 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.29 | +0.33 | +0.33 |
| tat_qa | 0.413 | f1 0.00, decay 1.00, precision 0.00, recall 0.00 | +0.16 | +0.60 | +0.54 |
| tpcdi_cells | 0.416 | f1 0.25, decay 0.15, precision 0.20, recall 0.40 | +0.57 | +0.49 | +0.54 |
| valentine | 0.425 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.39 | +0.52 | +0.48 |
| walmart_amazon | 0.414 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.72 | +0.77 | +0.72 |
| wdc_lspc | 0.426 | f1 0.20, decay 0.00, precision 0.50, recall 0.30 | +0.39 | +0.48 | +0.44 |
| wdc_products | 0.428 | f1 0.70, decay 0.00, precision 0.25, recall 0.05 | +0.32 | +0.37 | +0.37 |
| wikitablequestions | 0.411 | f1 0.05, decay 0.20, precision 0.00, recall 0.75 | +0.74 | +0.78 | +0.78 |

Mean held-out τ: LODO weights +0.34, full best +0.39, v1 +0.37.

| held-out family | J on the rest | LOFO weights | τ held-out: LOFO weights | full best | v1 |
|---|---|---|---|---|---|
| EM | 0.481 | f1 0.20, decay 0.00, precision 0.50, recall 0.30 | +0.32 | +0.29 | +0.30 |
| SM | 0.431 | f1 0.00, decay 0.10, precision 0.00, recall 0.90 | +0.35 | +0.37 | +0.25 |
| TQA | 0.423 | f1 0.45, decay 0.00, precision 0.40, recall 0.15 | +0.38 | +0.40 | +0.38 |
| FIN | 0.406 | f1 0.00, decay 0.95, precision 0.05, recall 0.00 | +0.43 | +0.51 | +0.51 |

Per-family best weightings:
* EM: f1 0.00, decay 0.70, precision 0.00, recall 0.30 (J 0.361; under the global best 0.361; under v1 0.361; L1 distance to global best 0.00) — datasets: abt_buy, alaska_camera, amazon_google, dblp_acm, dblp_scholar, machamp, opensanctions_pairs, papadakis_dn, walmart_amazon, wdc_lspc, wdc_products
* SM: f1 0.00, decay 1.00, precision 0.00, recall 0.00 (J 0.580; under the global best 0.524; under v1 0.503; L1 distance to global best 0.60) — datasets: alaska_schema, fintagging, magneto_gdc, smat, tpcdi_cells, valentine
* TQA: f1 0.00, decay 0.00, precision 0.20, recall 0.80 (J 0.497; under the global best 0.464; under v1 0.480; L1 distance to global best 1.40) — datasets: bird, fetaqa, hitab, mmtu, realhitbench, suc, tab_fact, tabis, tablebench, tableeval, wikitablequestions
* FIN: f1 0.05, decay 0.05, precision 0.50, recall 0.40 (J 0.822; under the global best 0.735; under v1 0.689; L1 distance to global best 1.30) — datasets: officeqa, officeqa_pro_v2, tat_qa

## 5. Correctness on known-quality anchors (borrowed from v5; does not change the objective)

31,380 synthetic answers of known utility over the 31 datasets (9,881 correct, 7,430 wrong; operators: digit_typo, flip, hedge, identity, list_dump, magnitude, near_miss_large, near_miss_medium, near_miss_small, no_answer, paraphrase, partial, shuffled, sign_flip, superset, tagged, typo, unit_variant, verbose, wrong_random).

| rule | weights | J (agreement) | ρ to utility | mean per-dataset ρ | AUC correct vs wrong | mean score of wrong answers | hedge gap | rank by J | rank by ρ |
|---|---|---|---|---|---|---|---|---|---|
| v1 | f1 0.35, decay 0.35, precision 0.15, recall 0.15 | 0.404 | 0.878 | 0.868 | 0.994 | 0.034 | -0.51 | 1483 | 370 |
| best_J | f1 0.00, decay 0.70, precision 0.00, recall 0.30 | 0.421 | 0.845 | 0.840 | 0.994 | 0.037 | -0.49 | 1 | 1755 |
| best_rho | f1 0.00, decay 0.35, precision 0.60, recall 0.05 | 0.398 | 0.883 | 0.871 | 0.994 | 0.034 | -0.57 | 1709 | 1 |
| pareto_knee | f1 0.05, decay 0.60, precision 0.25, recall 0.10 | 0.419 | 0.877 | 0.866 | 0.994 | 0.036 | -0.55 | 4 | 671 |
| exact match | – | – | 0.828 | 0.830 | 0.989 | 0.011 | -0.81 | – | – |

Spearman correlation between J and ρ across all 1,771 weightings: **-0.34**. Pareto front size 10. rho and auc are correctness against known-utility anchors; J is agreement among datasets. If the best-J weighting also has high rho, agreement and correctness pull the same way; if not, the Pareto knee is the defensible compromise.

Figure: `anchors/fig_pareto`.

## 6. Sensitivity

* v1: 12 lattice neighbours within one 0.05 move; J centre 0.404, neighbours min 0.402 / mean 0.405 / max 0.409 (range 0.007); 62 % of neighbours are better.
* best: 6 lattice neighbours within one 0.05 move; J centre 0.421, neighbours min 0.416 / mean 0.418 / max 0.421 (range 0.005); 0 % of neighbours are better.

## 7. Leaderboards under the naive, deployed and calibrated rules

Bradley–Terry (headline) rankings, with Borda in brackets; full tables, strengths with standard errors, 1,000 bootstrap draws, Friedman/Nemenyi, Holm-corrected pairwise tests and LaTeX under `leaderboards/<rule>/`.

| rule | weights | claude-opus-5 | claude-sonnet-5 | deepseek-chat | deepseek-r1 | gemini-3.8-flash | gpt-5.4-mini | gpt-5.5 | gpt-oss-120b | grok-4 | llama-3.3-70b | Friedman p | Kendall's W | significant pairs (Holm) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| em_only | – | 1 (1) | 5 (4) | 8 (7) | 7 (6) | 3 (3) | 6 (8) | 2 (2) | 9 (9) | 4 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| v1_original | f1 0.35, decay 0.35, precision 0.15, recall 0.15 | 2 (2) | 4 (4) | 7 (7) | 8 (6) | 1 (3) | 6 (8) | 3 (1) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top1 | f1 0.00, decay 0.70, precision 0.00, recall 0.30 | 2 (1) | 4 (4) | 7 (8) | 6 (6) | 1 (3) | 8 (7) | 3 (2) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top2 | f1 0.35, decay 0.10, precision 0.10, recall 0.45 | 2 (1) | 4 (4) | 6 (7) | 8 (6) | 1 (3) | 7 (8) | 3 (2) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top3 | f1 0.40, decay 0.10, precision 0.05, recall 0.45 | 2 (1) | 4 (4) | 6 (7) | 8 (6) | 1 (3) | 7 (8) | 3 (2) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top4 | f1 0.05, decay 0.60, precision 0.25, recall 0.10 | 2 (1) | 4 (4) | 7 (8) | 8 (6) | 1 (3) | 6 (7) | 3 (2) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > gpt-oss-120b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top5 | f1 0.00, decay 0.60, precision 0.00, recall 0.40 | 2 (1) | 4 (4) | 7 (8) | 6 (6) | 1 (3) | 8 (7) | 3 (2) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| best_anchor | f1 0.00, decay 0.35, precision 0.60, recall 0.05 | 2 (2) | 4 (4) | 8 (8) | 7 (6) | 1 (3) | 5 (7) | 3 (1) | 9 (9) | 6 (5) | 10 (10) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| pareto_knee | f1 0.05, decay 0.60, precision 0.25, recall 0.10 | 2 (1) | 4 (4) | 7 (8) | 8 (6) | 1 (3) | 6 (7) | 3 (2) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > gpt-oss-120b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |

Agreement between the BT rankings of the rules (Kendall τ):

| | em_only | v1_original | top1 | top2 | top3 | top4 | top5 | best_anchor | pareto_knee |
|---|---|---|---|---|---|---|---|---|---|
| em_only | +1.00 | +0.82 | +0.78 | +0.78 | +0.78 | +0.82 | +0.78 | +0.82 | +0.82 |
| v1_original | +0.82 | +1.00 | +0.87 | +0.96 | +0.96 | +1.00 | +0.87 | +0.91 | +1.00 |
| top1 | +0.78 | +0.87 | +1.00 | +0.91 | +0.91 | +0.87 | +1.00 | +0.87 | +0.87 |
| top2 | +0.78 | +0.96 | +0.91 | +1.00 | +1.00 | +0.96 | +0.91 | +0.87 | +0.96 |
| top3 | +0.78 | +0.96 | +0.91 | +1.00 | +1.00 | +0.96 | +0.91 | +0.87 | +0.96 |
| top4 | +0.82 | +1.00 | +0.87 | +0.96 | +0.96 | +1.00 | +0.87 | +0.91 | +1.00 |
| top5 | +0.78 | +0.87 | +1.00 | +0.91 | +0.91 | +0.87 | +1.00 | +0.87 | +0.87 |
| best_anchor | +0.82 | +0.91 | +0.87 | +0.87 | +0.87 | +0.91 | +0.87 | +1.00 | +0.91 |
| pareto_knee | +0.82 | +1.00 | +0.87 | +0.96 | +0.96 | +1.00 | +0.87 | +0.91 | +1.00 |

## Official-split estimates under the deployed rule (v1 weights)

Suite score = mean over the stratified pool (equal strata; the calibration number). Official estimate = the same answers re-weighted to the official split's stratum or class proportions (post-stratification), with a 95 % weighted item bootstrap; F1 = positive-class F1 at the official match ratio for boolean matching sets. n/c = not comparable (constructed pairs, closed-book, or no census).

| dataset | model | suite score | official estimate [95 %] | positive-class F1 (suite → official) | effective n |
|---|---|---|---|---|---|
| abt_buy | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 63 |
| abt_buy | claude-sonnet-5 | 0.970 | 0.993 [0.98, 1.00] | 0.97 → 0.97 [0.92, 1.00] | 63 |
| abt_buy | deepseek-chat | 0.960 | 0.976 [0.93, 1.00] | 0.96 → 0.89 [0.73, 0.99] | 63 |
| abt_buy | deepseek-r1 | 0.970 | 0.978 [0.93, 1.00] | 0.97 → 0.90 [0.75, 1.00] | 63 |
| abt_buy | gemini-3.8-flash | 0.980 | 0.996 [0.99, 1.00] | 0.98 → 0.98 [0.94, 1.00] | 63 |
| abt_buy | gpt-5.4-mini | 0.960 | 0.976 [0.94, 1.00] | 0.96 → 0.89 [0.75, 0.99] | 63 |
| abt_buy | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 63 |
| abt_buy | gpt-oss-120b | 0.940 | 0.987 [0.97, 1.00] | 0.93 → 0.93 [0.88, 0.98] | 63 |
| abt_buy | grok-4 | 0.960 | 0.976 [0.93, 1.00] | 0.96 → 0.89 [0.75, 0.99] | 63 |
| abt_buy | llama-3.3-70b | 0.960 | 0.976 [0.94, 1.00] | 0.96 → 0.89 [0.74, 0.99] | 63 |
| alaska_camera | claude-opus-5 | 0.820 | n/c | – | 100 |
| alaska_camera | claude-sonnet-5 | 0.980 | n/c | – | 100 |
| alaska_camera | deepseek-chat | 1.000 | n/c | – | 100 |
| alaska_camera | deepseek-r1 | 0.990 | n/c | – | 100 |
| alaska_camera | gemini-3.8-flash | 0.890 | n/c | – | 100 |
| alaska_camera | gpt-5.4-mini | 0.970 | n/c | – | 100 |
| alaska_camera | gpt-5.5 | 1.000 | n/c | – | 100 |
| alaska_camera | gpt-oss-120b | 1.000 | n/c | – | 100 |
| alaska_camera | grok-4 | 0.940 | n/c | – | 100 |
| alaska_camera | llama-3.3-70b | 0.990 | n/c | – | 100 |
| alaska_schema | claude-opus-5 | 0.945 | 0.945 [0.90, 0.98] | – | 93 |
| alaska_schema | claude-sonnet-5 | 0.929 | 0.929 [0.88, 0.97] | – | 93 |
| alaska_schema | deepseek-chat | 0.951 | 0.951 [0.91, 0.99] | – | 93 |
| alaska_schema | deepseek-r1 | 0.948 | 0.948 [0.91, 0.98] | – | 93 |
| alaska_schema | gemini-3.8-flash | 0.918 | 0.918 [0.87, 0.97] | – | 93 |
| alaska_schema | gpt-5.4-mini | 0.958 | 0.958 [0.92, 0.99] | – | 93 |
| alaska_schema | gpt-5.5 | 0.928 | 0.928 [0.88, 0.97] | – | 93 |
| alaska_schema | gpt-oss-120b | 0.934 | 0.934 [0.89, 0.98] | – | 93 |
| alaska_schema | grok-4 | 0.929 | 0.929 [0.88, 0.97] | – | 93 |
| alaska_schema | llama-3.3-70b | 0.840 | 0.840 [0.79, 0.89] | – | 93 |
| amazon_google | claude-opus-5 | 0.940 | 0.916 [0.84, 0.98] | 0.94 → 0.70 [0.53, 0.91] | 67 |
| amazon_google | claude-sonnet-5 | 0.960 | 0.935 [0.86, 0.99] | 0.96 → 0.76 [0.59, 0.93] | 67 |
| amazon_google | deepseek-chat | 0.960 | 0.949 [0.89, 1.00] | 0.96 → 0.80 [0.63, 0.99] | 67 |
| amazon_google | deepseek-r1 | 0.950 | 0.932 [0.87, 0.98] | 0.95 → 0.75 [0.58, 0.93] | 67 |
| amazon_google | gemini-3.8-flash | 0.930 | 0.928 [0.86, 0.98] | 0.92 → 0.73 [0.56, 0.93] | 67 |
| amazon_google | gpt-5.4-mini | 0.930 | 0.942 [0.88, 0.99] | 0.92 → 0.76 [0.59, 0.96] | 67 |
| amazon_google | gpt-5.5 | 0.940 | 0.916 [0.84, 0.98] | 0.94 → 0.70 [0.53, 0.92] | 67 |
| amazon_google | gpt-oss-120b | 0.860 | 0.926 [0.86, 0.98] | 0.83 → 0.68 [0.50, 0.86] | 67 |
| amazon_google | grok-4 | 0.940 | 0.944 [0.89, 0.99] | 0.93 → 0.77 [0.61, 0.97] | 67 |
| amazon_google | llama-3.3-70b | 0.950 | 0.932 [0.87, 0.98] | 0.95 → 0.75 [0.58, 0.93] | 67 |
| bird | claude-opus-5 | 0.293 | 0.323 [0.23, 0.41] | – | 74 |
| bird | claude-sonnet-5 | 0.232 | 0.258 [0.18, 0.35] | – | 74 |
| bird | deepseek-chat | 0.187 | 0.203 [0.13, 0.28] | – | 74 |
| bird | deepseek-r1 | 0.178 | 0.214 [0.14, 0.30] | – | 74 |
| bird | gemini-3.8-flash | 0.293 | 0.313 [0.22, 0.41] | – | 74 |
| bird | gpt-5.4-mini | 0.178 | 0.218 [0.13, 0.31] | – | 74 |
| bird | gpt-5.5 | 0.185 | 0.204 [0.12, 0.29] | – | 74 |
| bird | gpt-oss-120b | 0.084 | 0.109 [0.05, 0.19] | – | 74 |
| bird | grok-4 | 0.122 | 0.144 [0.08, 0.22] | – | 74 |
| bird | llama-3.3-70b | 0.122 | 0.144 [0.08, 0.22] | – | 74 |
| dblp_acm | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | claude-sonnet-5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | deepseek-chat | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | deepseek-r1 | 0.990 | 0.996 [0.99, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 72 |
| dblp_acm | gemini-3.8-flash | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | gpt-5.4-mini | 0.990 | 0.996 [0.99, 1.00] | 0.99 → 0.99 [0.96, 1.00] | 72 |
| dblp_acm | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | gpt-oss-120b | 0.910 | 0.967 [0.94, 0.99] | 0.90 → 0.90 [0.82, 0.96] | 72 |
| dblp_acm | grok-4 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | llama-3.3-70b | 0.970 | 0.952 [0.89, 1.00] | 0.97 → 0.88 [0.75, 1.00] | 72 |
| dblp_scholar | claude-opus-5 | 0.950 | 0.956 [0.91, 0.99] | 0.95 → 0.89 [0.78, 0.98] | 70 |
| dblp_scholar | claude-sonnet-5 | 0.970 | 0.976 [0.94, 1.00] | 0.97 → 0.94 [0.84, 1.00] | 70 |
| dblp_scholar | deepseek-chat | 0.960 | 0.959 [0.91, 1.00] | 0.96 → 0.90 [0.79, 0.99] | 70 |
| dblp_scholar | deepseek-r1 | 0.950 | 0.969 [0.93, 0.99] | 0.95 → 0.92 [0.81, 0.99] | 70 |
| dblp_scholar | gemini-3.8-flash | 0.930 | 0.961 [0.92, 0.99] | 0.93 → 0.90 [0.79, 0.97] | 70 |
| dblp_scholar | gpt-5.4-mini | 0.940 | 0.965 [0.92, 0.99] | 0.94 → 0.91 [0.79, 0.98] | 70 |
| dblp_scholar | gpt-5.5 | 0.960 | 0.959 [0.91, 1.00] | 0.96 → 0.90 [0.78, 0.99] | 70 |
| dblp_scholar | gpt-oss-120b | 0.910 | 0.967 [0.94, 0.99] | 0.90 → 0.90 [0.84, 0.96] | 70 |
| dblp_scholar | grok-4 | 0.950 | 0.969 [0.93, 1.00] | 0.95 → 0.92 [0.82, 0.99] | 70 |
| dblp_scholar | llama-3.3-70b | 0.970 | 0.976 [0.94, 1.00] | 0.97 → 0.94 [0.85, 1.00] | 70 |
| fetaqa | claude-opus-5 | 0.401 | 0.401 [0.37, 0.43] | – | 100 |
| fetaqa | claude-sonnet-5 | 0.373 | 0.373 [0.34, 0.40] | – | 100 |
| fetaqa | deepseek-chat | 0.434 | 0.434 [0.41, 0.46] | – | 100 |
| fetaqa | deepseek-r1 | 0.413 | 0.413 [0.38, 0.44] | – | 100 |
| fetaqa | gemini-3.8-flash | 0.445 | 0.445 [0.42, 0.47] | – | 100 |
| fetaqa | gpt-5.4-mini | 0.312 | 0.312 [0.29, 0.34] | – | 100 |
| fetaqa | gpt-5.5 | 0.438 | 0.438 [0.41, 0.46] | – | 100 |
| fetaqa | gpt-oss-120b | 0.322 | 0.322 [0.30, 0.34] | – | 100 |
| fetaqa | grok-4 | 0.428 | 0.428 [0.40, 0.45] | – | 100 |
| fetaqa | llama-3.3-70b | 0.253 | 0.253 [0.22, 0.28] | – | 100 |
| fintagging | claude-opus-5 | 0.909 | 0.932 [0.88, 0.98] | – | 52 |
| fintagging | claude-sonnet-5 | 0.898 | 0.897 [0.84, 0.95] | – | 52 |
| fintagging | deepseek-chat | 0.858 | 0.847 [0.78, 0.92] | – | 52 |
| fintagging | deepseek-r1 | 0.840 | 0.855 [0.77, 0.93] | – | 52 |
| fintagging | gemini-3.8-flash | 0.897 | 0.908 [0.85, 0.96] | – | 52 |
| fintagging | gpt-5.4-mini | 0.892 | 0.863 [0.79, 0.93] | – | 52 |
| fintagging | gpt-5.5 | 0.893 | 0.899 [0.83, 0.96] | – | 52 |
| fintagging | gpt-oss-120b | 0.863 | 0.847 [0.78, 0.91] | – | 52 |
| fintagging | grok-4 | 0.887 | 0.876 [0.81, 0.94] | – | 52 |
| fintagging | llama-3.3-70b | 0.858 | 0.836 [0.77, 0.90] | – | 52 |
| hitab | claude-opus-5 | 0.781 | 0.790 [0.72, 0.86] | – | 95 |
| hitab | claude-sonnet-5 | 0.763 | 0.758 [0.68, 0.84] | – | 95 |
| hitab | deepseek-chat | 0.814 | 0.822 [0.75, 0.89] | – | 95 |
| hitab | deepseek-r1 | 0.771 | 0.771 [0.70, 0.85] | – | 95 |
| hitab | gemini-3.8-flash | 0.748 | 0.757 [0.68, 0.83] | – | 95 |
| hitab | gpt-5.4-mini | 0.784 | 0.783 [0.71, 0.86] | – | 95 |
| hitab | gpt-5.5 | 0.757 | 0.764 [0.68, 0.84] | – | 95 |
| hitab | gpt-oss-120b | 0.750 | 0.752 [0.67, 0.83] | – | 95 |
| hitab | grok-4 | 0.746 | 0.749 [0.66, 0.83] | – | 95 |
| hitab | llama-3.3-70b | 0.784 | 0.783 [0.71, 0.85] | – | 95 |
| machamp | claude-opus-5 | 0.900 | 0.912 [0.83, 0.97] | 0.90 → 0.77 [0.62, 0.92] | 32 |
| machamp | claude-sonnet-5 | 0.900 | 0.923 [0.84, 0.97] | 0.90 → 0.79 [0.65, 0.92] | 32 |
| machamp | deepseek-chat | 0.890 | 0.892 [0.80, 0.96] | 0.90 → 0.74 [0.57, 0.90] | 32 |
| machamp | deepseek-r1 | 0.900 | 0.897 [0.81, 0.96] | 0.91 → 0.75 [0.59, 0.90] | 32 |
| machamp | gemini-3.8-flash | 0.900 | 0.912 [0.83, 0.97] | 0.90 → 0.77 [0.61, 0.91] | 32 |
| machamp | gpt-5.4-mini | 0.890 | 0.893 [0.80, 0.96] | 0.90 → 0.74 [0.57, 0.90] | 32 |
| machamp | gpt-5.5 | 0.900 | 0.897 [0.81, 0.96] | 0.91 → 0.75 [0.59, 0.90] | 32 |
| machamp | gpt-oss-120b | 0.830 | 0.794 [0.64, 0.90] | 0.83 → 0.56 [0.37, 0.77] | 32 |
| machamp | grok-4 | 0.890 | 0.896 [0.81, 0.96] | 0.90 → 0.75 [0.59, 0.89] | 32 |
| machamp | llama-3.3-70b | 0.870 | 0.880 [0.78, 0.95] | 0.87 → 0.70 [0.54, 0.85] | 32 |
| magneto_gdc | claude-opus-5 | 0.971 | 0.974 [0.95, 0.99] | – | 93 |
| magneto_gdc | claude-sonnet-5 | 0.955 | 0.955 [0.92, 0.99] | – | 93 |
| magneto_gdc | deepseek-chat | 0.953 | 0.956 [0.92, 0.99] | – | 93 |
| magneto_gdc | deepseek-r1 | 0.970 | 0.972 [0.94, 0.99] | – | 93 |
| magneto_gdc | gemini-3.8-flash | 0.963 | 0.967 [0.94, 0.99] | – | 93 |
| magneto_gdc | gpt-5.4-mini | 0.912 | 0.914 [0.86, 0.96] | – | 93 |
| magneto_gdc | gpt-5.5 | 0.967 | 0.972 [0.94, 0.99] | – | 93 |
| magneto_gdc | gpt-oss-120b | 0.961 | 0.965 [0.93, 0.99] | – | 93 |
| magneto_gdc | grok-4 | 0.939 | 0.944 [0.90, 0.98] | – | 93 |
| magneto_gdc | llama-3.3-70b | 0.753 | 0.759 [0.69, 0.82] | – | 93 |
| mmtu | claude-opus-5 | 0.882 | 0.846 [0.76, 0.93] | – | 87 |
| mmtu | claude-sonnet-5 | 0.872 | 0.838 [0.76, 0.92] | – | 87 |
| mmtu | deepseek-chat | 0.865 | 0.831 [0.75, 0.91] | – | 87 |
| mmtu | deepseek-r1 | 0.822 | 0.770 [0.67, 0.87] | – | 87 |
| mmtu | gemini-3.8-flash | 0.894 | 0.856 [0.76, 0.93] | – | 87 |
| mmtu | gpt-5.4-mini | 0.882 | 0.851 [0.77, 0.92] | – | 87 |
| mmtu | gpt-5.5 | 0.917 | 0.882 [0.80, 0.96] | – | 87 |
| mmtu | gpt-oss-120b | 0.830 | 0.774 [0.68, 0.86] | – | 87 |
| mmtu | grok-4 | 0.901 | 0.869 [0.79, 0.94] | – | 87 |
| mmtu | llama-3.3-70b | 0.807 | 0.773 [0.68, 0.85] | – | 87 |
| officeqa | claude-opus-5 | 0.187 | n/c | – | 100 |
| officeqa | claude-sonnet-5 | 0.170 | n/c | – | 100 |
| officeqa | deepseek-chat | 0.075 | n/c | – | 100 |
| officeqa | deepseek-r1 | 0.083 | n/c | – | 100 |
| officeqa | gemini-3.8-flash | 0.194 | n/c | – | 100 |
| officeqa | gpt-5.4-mini | 0.107 | n/c | – | 100 |
| officeqa | gpt-5.5 | 0.168 | n/c | – | 100 |
| officeqa | gpt-oss-120b | 0.079 | n/c | – | 100 |
| officeqa | grok-4 | 0.129 | n/c | – | 100 |
| officeqa | llama-3.3-70b | 0.097 | n/c | – | 100 |
| officeqa_pro_v2 | claude-opus-5 | 0.250 | 0.250 [0.19, 0.31] | – | 90 |
| officeqa_pro_v2 | claude-sonnet-5 | 0.133 | 0.133 [0.09, 0.18] | – | 90 |
| officeqa_pro_v2 | deepseek-chat | 0.121 | 0.121 [0.09, 0.16] | – | 90 |
| officeqa_pro_v2 | deepseek-r1 | 0.036 | 0.036 [0.02, 0.05] | – | 90 |
| officeqa_pro_v2 | gemini-3.8-flash | 0.198 | 0.198 [0.15, 0.25] | – | 90 |
| officeqa_pro_v2 | gpt-5.4-mini | 0.123 | 0.123 [0.09, 0.16] | – | 90 |
| officeqa_pro_v2 | gpt-5.5 | 0.188 | 0.188 [0.13, 0.25] | – | 90 |
| officeqa_pro_v2 | gpt-oss-120b | 0.104 | 0.104 [0.07, 0.15] | – | 90 |
| officeqa_pro_v2 | grok-4 | 0.119 | 0.119 [0.08, 0.16] | – | 90 |
| officeqa_pro_v2 | llama-3.3-70b | 0.115 | 0.115 [0.08, 0.15] | – | 90 |
| opensanctions_pairs | claude-opus-5 | 0.940 | 0.906 [0.83, 0.97] | 0.93 → 0.93 [0.87, 0.98] | 76 |
| opensanctions_pairs | claude-sonnet-5 | 0.730 | 0.587 [0.48, 0.70] | 0.63 → 0.64 [0.50, 0.76] | 76 |
| opensanctions_pairs | deepseek-chat | 0.760 | 0.635 [0.52, 0.75] | 0.68 → 0.69 [0.56, 0.79] | 76 |
| opensanctions_pairs | deepseek-r1 | 0.850 | 0.765 [0.66, 0.86] | 0.82 → 0.82 [0.72, 0.90] | 76 |
| opensanctions_pairs | gemini-3.8-flash | 0.860 | 0.780 [0.67, 0.88] | 0.83 → 0.83 [0.73, 0.91] | 76 |
| opensanctions_pairs | gpt-5.4-mini | 0.900 | 0.865 [0.78, 0.94] | 0.89 → 0.91 [0.84, 0.96] | 76 |
| opensanctions_pairs | gpt-5.5 | 0.750 | 0.608 [0.50, 0.72] | 0.66 → 0.66 [0.52, 0.78] | 76 |
| opensanctions_pairs | gpt-oss-120b | 0.780 | 0.666 [0.56, 0.77] | 0.72 → 0.72 [0.59, 0.83] | 76 |
| opensanctions_pairs | grok-4 | 0.850 | 0.776 [0.68, 0.87] | 0.82 → 0.83 [0.73, 0.91] | 76 |
| opensanctions_pairs | llama-3.3-70b | 0.790 | 0.682 [0.57, 0.79] | 0.73 → 0.74 [0.62, 0.83] | 76 |
| papadakis_dn | claude-opus-5 | 0.920 | 0.955 [0.89, 1.00] | 0.79 → 0.32 [0.13, 0.84] | 33 |
| papadakis_dn | claude-sonnet-5 | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.57, 0.95] | 33 |
| papadakis_dn | deepseek-chat | 0.940 | 0.993 [0.99, 1.00] | 0.83 → 0.76 [0.52, 0.93] | 33 |
| papadakis_dn | deepseek-r1 | 0.940 | 0.993 [0.99, 1.00] | 0.83 → 0.76 [0.53, 0.93] | 33 |
| papadakis_dn | gemini-3.8-flash | 0.940 | 0.992 [0.98, 1.00] | 0.82 → 0.70 [0.46, 0.89] | 33 |
| papadakis_dn | gpt-5.4-mini | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.53, 0.94] | 33 |
| papadakis_dn | gpt-5.5 | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.57, 0.94] | 33 |
| papadakis_dn | gpt-oss-120b | 0.930 | 0.992 [0.98, 1.00] | 0.79 → 0.68 [0.43, 0.88] | 33 |
| papadakis_dn | grok-4 | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.55, 0.94] | 33 |
| papadakis_dn | llama-3.3-70b | 0.940 | 0.975 [0.93, 1.00] | 0.83 → 0.46 [0.18, 0.92] | 33 |
| realhitbench | claude-opus-5 | 0.743 | 0.745 [0.67, 0.82] | – | 98 |
| realhitbench | claude-sonnet-5 | 0.681 | 0.684 [0.61, 0.77] | – | 98 |
| realhitbench | deepseek-chat | 0.662 | 0.656 [0.57, 0.73] | – | 98 |
| realhitbench | deepseek-r1 | 0.659 | 0.662 [0.58, 0.74] | – | 98 |
| realhitbench | gemini-3.8-flash | 0.746 | 0.747 [0.67, 0.82] | – | 98 |
| realhitbench | gpt-5.4-mini | 0.661 | 0.658 [0.57, 0.75] | – | 98 |
| realhitbench | gpt-5.5 | 0.724 | 0.721 [0.64, 0.80] | – | 98 |
| realhitbench | gpt-oss-120b | 0.603 | 0.602 [0.51, 0.69] | – | 98 |
| realhitbench | grok-4 | 0.640 | 0.638 [0.55, 0.72] | – | 98 |
| realhitbench | llama-3.3-70b | 0.611 | 0.616 [0.54, 0.69] | – | 98 |
| smat | claude-opus-5 | 0.933 | 0.931 [0.88, 0.97] | – | 98 |
| smat | claude-sonnet-5 | 0.938 | 0.936 [0.89, 0.97] | – | 98 |
| smat | deepseek-chat | 0.918 | 0.916 [0.87, 0.96] | – | 98 |
| smat | deepseek-r1 | 0.913 | 0.909 [0.86, 0.95] | – | 98 |
| smat | gemini-3.8-flash | 0.921 | 0.919 [0.87, 0.96] | – | 98 |
| smat | gpt-5.4-mini | 0.956 | 0.958 [0.92, 0.99] | – | 98 |
| smat | gpt-5.5 | 0.940 | 0.939 [0.89, 0.97] | – | 98 |
| smat | gpt-oss-120b | 0.916 | 0.913 [0.86, 0.96] | – | 98 |
| smat | grok-4 | 0.936 | 0.933 [0.89, 0.97] | – | 98 |
| smat | llama-3.3-70b | 0.806 | 0.803 [0.74, 0.86] | – | 98 |
| suc | claude-opus-5 | 0.987 | 0.988 [0.96, 1.00] | – | 99 |
| suc | claude-sonnet-5 | 0.911 | 0.908 [0.85, 0.96] | – | 99 |
| suc | deepseek-chat | 0.858 | 0.858 [0.80, 0.91] | – | 99 |
| suc | deepseek-r1 | 0.935 | 0.932 [0.89, 0.97] | – | 99 |
| suc | gemini-3.8-flash | 0.977 | 0.978 [0.94, 1.00] | – | 99 |
| suc | gpt-5.4-mini | 0.914 | 0.910 [0.86, 0.96] | – | 99 |
| suc | gpt-5.5 | 0.943 | 0.938 [0.89, 0.98] | – | 99 |
| suc | gpt-oss-120b | 0.932 | 0.930 [0.88, 0.97] | – | 99 |
| suc | grok-4 | 0.943 | 0.938 [0.89, 0.98] | – | 99 |
| suc | llama-3.3-70b | 0.740 | 0.738 [0.66, 0.81] | – | 99 |
| tab_fact | claude-opus-5 | 0.660 | 0.667 [0.57, 0.76] | 0.67 → 0.70 [0.59, 0.79] | 99 |
| tab_fact | claude-sonnet-5 | 0.740 | 0.733 [0.65, 0.82] | 0.70 → 0.71 [0.59, 0.81] | 99 |
| tab_fact | deepseek-chat | 0.840 | 0.826 [0.75, 0.90] | 0.79 → 0.79 [0.68, 0.87] | 99 |
| tab_fact | deepseek-r1 | 0.760 | 0.754 [0.67, 0.84] | 0.72 → 0.73 [0.62, 0.82] | 99 |
| tab_fact | gemini-3.8-flash | 0.860 | 0.848 [0.78, 0.92] | 0.82 → 0.82 [0.71, 0.91] | 99 |
| tab_fact | gpt-5.4-mini | 0.820 | 0.808 [0.72, 0.88] | 0.77 → 0.77 [0.65, 0.87] | 99 |
| tab_fact | gpt-5.5 | 0.840 | 0.829 [0.75, 0.90] | 0.80 → 0.80 [0.70, 0.89] | 99 |
| tab_fact | gpt-oss-120b | 0.830 | 0.815 [0.73, 0.89] | 0.77 → 0.77 [0.66, 0.88] | 99 |
| tab_fact | grok-4 | 0.850 | 0.839 [0.76, 0.91] | 0.81 → 0.81 [0.70, 0.90] | 99 |
| tab_fact | llama-3.3-70b | 0.780 | 0.769 [0.69, 0.85] | 0.72 → 0.73 [0.61, 0.84] | 99 |
| tabis | claude-opus-5 | 0.960 | 0.964 [0.92, 0.99] | – | 77 |
| tabis | claude-sonnet-5 | 0.920 | 0.917 [0.85, 0.97] | – | 77 |
| tabis | deepseek-chat | 0.770 | 0.710 [0.61, 0.82] | – | 77 |
| tabis | deepseek-r1 | 0.970 | 0.982 [0.96, 1.00] | – | 77 |
| tabis | gemini-3.8-flash | 0.950 | 0.970 [0.94, 0.99] | – | 77 |
| tabis | gpt-5.4-mini | 0.900 | 0.905 [0.83, 0.96] | – | 77 |
| tabis | gpt-5.5 | 0.960 | 0.976 [0.95, 0.99] | – | 77 |
| tabis | gpt-oss-120b | 0.920 | 0.951 [0.91, 0.98] | – | 77 |
| tabis | grok-4 | 0.980 | 0.988 [0.97, 1.00] | – | 77 |
| tabis | llama-3.3-70b | 0.820 | 0.821 [0.74, 0.91] | – | 77 |
| tablebench | claude-opus-5 | 0.846 | 0.846 [0.78, 0.91] | – | 89 |
| tablebench | claude-sonnet-5 | 0.877 | 0.875 [0.81, 0.93] | – | 89 |
| tablebench | deepseek-chat | 0.833 | 0.844 [0.78, 0.90] | – | 89 |
| tablebench | deepseek-r1 | 0.783 | 0.793 [0.72, 0.86] | – | 89 |
| tablebench | gemini-3.8-flash | 0.835 | 0.833 [0.77, 0.90] | – | 89 |
| tablebench | gpt-5.4-mini | 0.841 | 0.835 [0.77, 0.90] | – | 89 |
| tablebench | gpt-5.5 | 0.852 | 0.850 [0.78, 0.91] | – | 89 |
| tablebench | gpt-oss-120b | 0.813 | 0.808 [0.74, 0.88] | – | 89 |
| tablebench | grok-4 | 0.839 | 0.837 [0.76, 0.91] | – | 89 |
| tablebench | llama-3.3-70b | 0.660 | 0.641 [0.56, 0.72] | – | 89 |
| tableeval | claude-opus-5 | 0.765 | 0.784 [0.68, 0.87] | – | 70 |
| tableeval | claude-sonnet-5 | 0.733 | 0.764 [0.67, 0.85] | – | 70 |
| tableeval | deepseek-chat | 0.711 | 0.708 [0.61, 0.80] | – | 70 |
| tableeval | deepseek-r1 | 0.756 | 0.757 [0.66, 0.85] | – | 70 |
| tableeval | gemini-3.8-flash | 0.791 | 0.805 [0.71, 0.89] | – | 70 |
| tableeval | gpt-5.4-mini | 0.742 | 0.751 [0.65, 0.84] | – | 70 |
| tableeval | gpt-5.5 | 0.784 | 0.794 [0.69, 0.88] | – | 70 |
| tableeval | gpt-oss-120b | 0.773 | 0.774 [0.68, 0.86] | – | 70 |
| tableeval | grok-4 | 0.802 | 0.785 [0.68, 0.88] | – | 70 |
| tableeval | llama-3.3-70b | 0.636 | 0.618 [0.51, 0.72] | – | 70 |
| tat_qa | claude-opus-5 | 0.861 | 0.846 [0.77, 0.91] | – | 61 |
| tat_qa | claude-sonnet-5 | 0.845 | 0.845 [0.77, 0.91] | – | 61 |
| tat_qa | deepseek-chat | 0.806 | 0.774 [0.68, 0.86] | – | 61 |
| tat_qa | deepseek-r1 | 0.806 | 0.763 [0.67, 0.85] | – | 61 |
| tat_qa | gemini-3.8-flash | 0.829 | 0.815 [0.74, 0.89] | – | 61 |
| tat_qa | gpt-5.4-mini | 0.789 | 0.719 [0.63, 0.81] | – | 61 |
| tat_qa | gpt-5.5 | 0.789 | 0.748 [0.67, 0.83] | – | 61 |
| tat_qa | gpt-oss-120b | 0.765 | 0.684 [0.59, 0.77] | – | 61 |
| tat_qa | grok-4 | 0.791 | 0.710 [0.61, 0.80] | – | 61 |
| tat_qa | llama-3.3-70b | 0.752 | 0.679 [0.57, 0.78] | – | 61 |
| tpcdi_cells | claude-opus-5 | 0.462 | 0.465 [0.38, 0.56] | – | 95 |
| tpcdi_cells | claude-sonnet-5 | 0.462 | 0.465 [0.38, 0.56] | – | 95 |
| tpcdi_cells | deepseek-chat | 0.462 | 0.465 [0.38, 0.56] | – | 95 |
| tpcdi_cells | deepseek-r1 | 0.462 | 0.466 [0.38, 0.56] | – | 95 |
| tpcdi_cells | gemini-3.8-flash | 0.462 | 0.465 [0.38, 0.55] | – | 95 |
| tpcdi_cells | gpt-5.4-mini | 0.455 | 0.458 [0.36, 0.54] | – | 95 |
| tpcdi_cells | gpt-5.5 | 0.462 | 0.466 [0.37, 0.55] | – | 95 |
| tpcdi_cells | gpt-oss-120b | 0.442 | 0.453 [0.36, 0.55] | – | 95 |
| tpcdi_cells | grok-4 | 0.447 | 0.456 [0.37, 0.54] | – | 95 |
| tpcdi_cells | llama-3.3-70b | 0.442 | 0.453 [0.37, 0.54] | – | 95 |
| valentine | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | claude-sonnet-5 | 0.994 | 0.989 [0.96, 1.00] | – | 82 |
| valentine | deepseek-chat | 0.979 | 0.967 [0.93, 1.00] | – | 82 |
| valentine | deepseek-r1 | 0.990 | 0.986 [0.96, 1.00] | – | 82 |
| valentine | gemini-3.8-flash | 0.970 | 0.988 [0.97, 1.00] | – | 82 |
| valentine | gpt-5.4-mini | 0.985 | 0.978 [0.94, 1.00] | – | 82 |
| valentine | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | gpt-oss-120b | 0.979 | 0.971 [0.93, 1.00] | – | 82 |
| valentine | grok-4 | 0.973 | 0.957 [0.91, 0.99] | – | 82 |
| valentine | llama-3.3-70b | 0.970 | 0.958 [0.91, 0.99] | – | 82 |
| walmart_amazon | claude-opus-5 | 0.980 | 0.982 [0.95, 1.00] | 0.98 → 0.91 [0.77, 1.00] | 71 |
| walmart_amazon | claude-sonnet-5 | 0.950 | 0.962 [0.91, 1.00] | 0.94 → 0.82 [0.65, 0.98] | 71 |
| walmart_amazon | deepseek-chat | 0.950 | 0.962 [0.91, 1.00] | 0.94 → 0.82 [0.66, 0.98] | 71 |
| walmart_amazon | deepseek-r1 | 0.960 | 0.978 [0.94, 1.00] | 0.95 → 0.89 [0.74, 0.99] | 71 |
| walmart_amazon | gemini-3.8-flash | 0.990 | 0.998 [0.99, 1.00] | 0.99 → 0.99 [0.96, 1.00] | 71 |
| walmart_amazon | gpt-5.4-mini | 0.950 | 0.975 [0.94, 1.00] | 0.94 → 0.87 [0.72, 0.99] | 71 |
| walmart_amazon | gpt-5.5 | 0.970 | 0.967 [0.92, 1.00] | 0.96 → 0.85 [0.67, 1.00] | 71 |
| walmart_amazon | gpt-oss-120b | 0.940 | 0.973 [0.93, 1.00] | 0.92 → 0.86 [0.70, 0.97] | 71 |
| walmart_amazon | grok-4 | 0.960 | 0.978 [0.94, 1.00] | 0.95 → 0.89 [0.72, 0.99] | 71 |
| walmart_amazon | llama-3.3-70b | 0.930 | 0.971 [0.93, 0.99] | 0.91 → 0.85 [0.68, 0.96] | 71 |
| wdc_lspc | claude-opus-5 | 0.990 | 0.996 [0.99, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 75 |
| wdc_lspc | claude-sonnet-5 | 0.980 | 0.992 [0.98, 1.00] | 0.98 → 0.98 [0.96, 1.00] | 75 |
| wdc_lspc | deepseek-chat | 0.960 | 0.940 [0.87, 0.99] | 0.96 → 0.90 [0.78, 0.99] | 75 |
| wdc_lspc | deepseek-r1 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 75 |
| wdc_lspc | gemini-3.8-flash | 0.980 | 0.992 [0.98, 1.00] | 0.98 → 0.98 [0.96, 1.00] | 75 |
| wdc_lspc | gpt-5.4-mini | 0.970 | 0.986 [0.97, 1.00] | 0.97 → 0.97 [0.94, 1.00] | 75 |
| wdc_lspc | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 75 |
| wdc_lspc | gpt-oss-120b | 0.980 | 0.990 [0.97, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 75 |
| wdc_lspc | grok-4 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 75 |
| wdc_lspc | llama-3.3-70b | 0.960 | 0.940 [0.87, 0.99] | 0.96 → 0.90 [0.78, 0.99] | 75 |
| wdc_products | claude-opus-5 | 0.980 | 0.990 [0.97, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 77 |
| wdc_products | claude-sonnet-5 | 0.970 | 0.986 [0.97, 1.00] | 0.97 → 0.97 [0.94, 1.00] | 77 |
| wdc_products | deepseek-chat | 0.970 | 0.977 [0.94, 1.00] | 0.97 → 0.96 [0.89, 1.00] | 77 |
| wdc_products | deepseek-r1 | 0.980 | 0.990 [0.97, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 77 |
| wdc_products | gemini-3.8-flash | 0.990 | 0.995 [0.98, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 77 |
| wdc_products | gpt-5.4-mini | 0.970 | 0.986 [0.97, 1.00] | 0.97 → 0.97 [0.94, 1.00] | 77 |
| wdc_products | gpt-5.5 | 0.980 | 0.979 [0.94, 1.00] | 0.98 → 0.96 [0.90, 1.00] | 77 |
| wdc_products | gpt-oss-120b | 0.980 | 0.979 [0.94, 1.00] | 0.98 → 0.96 [0.90, 1.00] | 77 |
| wdc_products | grok-4 | 0.990 | 0.995 [0.98, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 77 |
| wdc_products | llama-3.3-70b | 0.970 | 0.977 [0.94, 1.00] | 0.97 → 0.96 [0.90, 1.00] | 77 |
| wikitablequestions | claude-opus-5 | 0.879 | 0.878 [0.81, 0.93] | – | 98 |
| wikitablequestions | claude-sonnet-5 | 0.863 | 0.863 [0.79, 0.92] | – | 98 |
| wikitablequestions | deepseek-chat | 0.843 | 0.842 [0.77, 0.91] | – | 98 |
| wikitablequestions | deepseek-r1 | 0.846 | 0.844 [0.78, 0.91] | – | 98 |
| wikitablequestions | gemini-3.8-flash | 0.881 | 0.881 [0.82, 0.93] | – | 98 |
| wikitablequestions | gpt-5.4-mini | 0.842 | 0.839 [0.77, 0.90] | – | 98 |
| wikitablequestions | gpt-5.5 | 0.865 | 0.862 [0.80, 0.92] | – | 98 |
| wikitablequestions | gpt-oss-120b | 0.824 | 0.821 [0.75, 0.89] | – | 98 |
| wikitablequestions | grok-4 | 0.867 | 0.864 [0.80, 0.92] | – | 98 |
| wikitablequestions | llama-3.3-70b | 0.749 | 0.747 [0.67, 0.82] | – | 98 |

## 8. Dataset diagnostics

| dataset | family | mean score | spread across models | self-stability τ | mean τ to other datasets | floor | ceiling | exclude from objective |
|---|---|---|---|---|---|---|---|---|
| abt_buy | EM | 0.970 | 0.060 | 0.73 | +0.36 | False | False | False |
| alaska_camera | EM | 0.958 | 0.180 | 0.92 | -0.22 | False | False | False |
| alaska_schema | SM | 0.928 | 0.118 | 0.67 | -0.04 | False | False | False |
| amazon_google | EM | 0.936 | 0.100 | 0.68 | -0.01 | False | False | False |
| bird | TQA | 0.187 | 0.209 | 0.82 | +0.31 | False | False | False |
| dblp_acm | EM | 0.986 | 0.090 | 0.88 | +0.35 | False | False | False |
| dblp_scholar | EM | 0.949 | 0.060 | 0.73 | -0.02 | False | False | False |
| fetaqa | TQA | 0.382 | 0.192 | 0.93 | +0.27 | False | False | False |
| fintagging | SM | 0.880 | 0.069 | 0.69 | +0.26 | False | False | False |
| hitab | TQA | 0.770 | 0.068 | 0.58 | -0.18 | False | False | False |
| machamp | EM | 0.887 | 0.070 | 0.60 | +0.38 | False | False | False |
| magneto_gdc | SM | 0.934 | 0.218 | 0.68 | +0.25 | False | False | False |
| mmtu | TQA | 0.867 | 0.110 | 0.76 | +0.30 | False | False | False |
| officeqa | FIN | 0.129 | 0.119 | 0.85 | +0.28 | False | False | False |
| officeqa_pro_v2 | FIN | 0.139 | 0.215 | 0.79 | +0.31 | False | False | False |
| opensanctions_pairs | EM | 0.821 | 0.210 | 0.89 | +0.03 | False | False | False |
| papadakis_dn | EM | 0.941 | 0.030 | 0.74 | +0.07 | False | False | False |
| realhitbench | TQA | 0.673 | 0.143 | 0.77 | +0.34 | False | False | False |
| smat | SM | 0.918 | 0.150 | 0.67 | +0.20 | False | False | False |
| suc | TQA | 0.914 | 0.246 | 0.85 | +0.29 | False | False | False |
| tab_fact | TQA | 0.798 | 0.200 | 0.84 | +0.01 | False | False | False |
| tabis | TQA | 0.915 | 0.210 | 0.85 | +0.22 | False | False | False |
| tablebench | TQA | 0.818 | 0.218 | 0.67 | +0.28 | False | False | False |
| tableeval | TQA | 0.749 | 0.166 | 0.78 | +0.20 | False | False | False |
| tat_qa | FIN | 0.803 | 0.109 | 0.76 | +0.26 | False | False | False |
| tpcdi_cells | SM | 0.456 | 0.020 | 0.78 | +0.30 | False | False | False |
| valentine | SM | 0.984 | 0.030 | 0.68 | +0.23 | False | True | True |
| walmart_amazon | EM | 0.958 | 0.060 | 0.76 | +0.36 | False | False | False |
| wdc_lspc | EM | 0.982 | 0.040 | 0.80 | +0.25 | False | True | True |
| wdc_products | EM | 0.978 | 0.020 | 0.64 | +0.18 | False | True | True |
| wikitablequestions | TQA | 0.846 | 0.132 | 0.74 | +0.35 | False | False | False |

Figure: `diagnostics/fig_dataset_tau` (pairwise τ between dataset rankings under v1).

## 9. What this supports, and what it does not

* Supported: over every step-0.05 weighting of v1's four ingredients, v1 sits at rank 1483 of 1,771 on the agreement objective, and the honest (out-of-bag) advantage of the best weighting over v1 is -0.008 with a confidence interval that includes zero. The plateau of statistically equivalent weightings covers 100 % of the lattice.
* Correctness (anchors): v1 ρ 0.878 vs best-J ρ 0.845 vs exact match ρ 0.828; J and ρ correlate -0.34 across the lattice, so agreement and correctness do not pull the same way, and the Pareto knee is the defensible compromise.
* Not supported: any rank claim below first place with 10 models (attainable τ values: [-1.0, -0.9556, -0.9111, -0.8667, -0.8222, -0.7778, -0.7333, -0.6889, -0.6444, -0.6, -0.5556, -0.5111, -0.4667, -0.4222, -0.3778, -0.3333, -0.2889, -0.2444, -0.2, -0.1556, -0.1111, -0.0667, -0.0222, 0.0222, 0.0667, 0.1111, 0.1556, 0.2, 0.2444, 0.2889, 0.3333, 0.3778, 0.4222, 0.4667, 0.5111, 0.5556, 0.6, 0.6444, 0.6889, 0.7333, 0.7778, 0.8222, 0.8667, 0.9111, 0.9556, 1.0]); any claim about accuracy from J alone; transfer to unseen task families until the 30-dataset run exists.
* Next: the same pipeline on the 30-dataset, 12-model run; human labels on 300 answers to replace the synthetic anchors in section 5.

## 10. Files

`grid_exhaustive.csv` (all weightings, every term, per-dataset τ, pooled ranks); `best.json`; `designs.csv` / `designs_summary.json`; `selection/` (nested.json, nested_draws.npz, plateau.csv, lodo.csv, lofo.csv, per_family.json, sensitivity.json); `anchors/` (anchor_components.csv, correctness.csv, correctness.json); `leaderboards/<rule>/` (leaderboard.md/csv, params.json with BT strengths + SE, Kemeny cost, Copeland, Borda, pairwise wins; bootstrap.npz; significance.json; pairwise_item_tests.csv; per_dataset_mean/se.csv; table.tex); `leaderboards/rule_agreement.csv`, `summary.json`; `diagnostics/`; `run_manifest.json`; `coverage.json`.
