# v2 report: an audit of the deployed judge's weights, done exhaustively

Generated 2026-10-16 14:32. Data: 31 datasets × 11 models, 3083 answered items in total (abt_buy 100, alaska_camera 100, alaska_schema 93, amazon_google 100, bird 100, dblp_acm 100, dblp_scholar 100, fetaqa 100, fintagging 100, hitab 100, machamp 100, magneto_gdc 100, mmtu 100, officeqa 100, officeqa_pro_v2 90, opensanctions_pairs 100, papadakis_dn 100, realhitbench 100, smat 100, suc 100, tab_fact 100, tabis 100, tablebench 100, tableeval 100, tat_qa 100, tpcdi_cells 100, valentine 100, walmart_amazon 100, wdc_lspc 100, wdc_products 100, wikitablequestions 100). Models: claude-opus-5, claude-sonnet-5, deepseek-chat, deepseek-r1, gemini-3.1-pro, gemini-3.8-flash, gpt-5.4-mini, gpt-5.5, gpt-oss-120b, grok-4, llama-3.3-70b. Every number below is read from `output/`; `scripts/run_all.sh` regenerates everything from the cached answers in a few minutes.

## 1. Question and design

v1 scores an answer as 0.35·F1 + 0.35·numeric-decay + 0.15·precision + 0.15·recall. Are those weights defensible? We evaluate **every** weighting on the step-0.05 simplex lattice (1,771 points; v1, the four corners and the uniform mix are lattice points), not a sample. The objective J is the mean Kendall τ between each dataset's model ranking and the Borda-pooled ranking: it measures **consistency between datasets, not correctness**. Correctness is checked separately in section 5 with known-quality anchors. Selection honesty (section 3), transfer (section 4), sensitivity (section 6), leaderboards under the naive, deployed and calibrated rules with significance tests (section 7) and dataset diagnostics (section 8) follow.

## 2. Exhaustive grid

* Best weighting: f1 0.35, decay 0.60, precision 0.05, recall 0.00 with J = 0.414 (τ to native metrics 0.92).
* v1: J = 0.392, rank 1602 of 1,771; 1601 weightings are better (90 %), 4 tie.
* Corners and uniform: only f1 0.409, only decay 0.394, only precision 0.386, only recall 0.389, uniform 0.401.
* J quantiles over the lattice: median 0.401, 90 % 0.407, 99 % 0.412.
* Objective robustness: the best under Kemeny pooling is f1 0.35, decay 0.20, precision 0.05, recall 0.40 (J 0.418, v1 rank 1404); under Copeland f1 0.05, decay 0.60, precision 0.25, recall 0.10 (v1 rank 1542); under Bradley–Terry f1 0.25, decay 0.60, precision 0.10, recall 0.05 (v1 rank 615). v1's J under the four rules: Borda 0.392, Kemeny 0.402, Copeland 0.402, BT 0.390.
* Top 5 by J: #1 f1 0.35, decay 0.60, precision 0.05, recall 0.00 (J 0.414); #2 f1 0.80, decay 0.00, precision 0.20, recall 0.00 (J 0.414); #3 f1 0.85, decay 0.00, precision 0.15, recall 0.00 (J 0.414); #4 f1 0.20, decay 0.00, precision 0.50, recall 0.30 (J 0.414); #5 f1 0.00, decay 0.15, precision 0.15, recall 0.70 (J 0.413).

Figures: `fig_landscape` (sorted J with v1 and corners), `fig_marginals` (J against each weight), `fig_designs`.

### 2b. Sampled designs at a budget of 100 (20 seeds each)

| design | best J found (mean ± sd) | regret vs exhaustive (mean / max) | rank of found best in the grid (median / worst) | min pairwise L1 | centred L2 discrepancy | share with a zero weight |
|---|---|---|---|---|---|---|
| dirichlet_lattice | 0.412 ± 0.001 | 0.002 / 0.004 | 12 / 58 | 0.10 | 0.538 | 0.27 |
| lhs_simplex | 0.413 ± 0.001 | 0.002 / 0.004 | 14 / 49 | 0.10 | 0.531 | 0.28 |
| uniform_lattice | 0.412 ± 0.001 | 0.002 / 0.004 | 14 / 60 | 0.10 | 0.526 | 0.45 |

Reading: with four weights the exhaustive grid is cheap, so the sampled designs only matter as a rehearsal for v3/v4; their regret and discrepancy are reported for that comparison.

## 3. Is the best weighting real? Nested selection and plateau

* Nested item bootstrap (B = 1000): the weighting selected on in-bag items has mean in-bag J 0.370 but out-of-bag J 0.323 (**optimism gap 0.047**). v1's out-of-bag J is 0.330; the full-data best's is 0.328.
* Selected vs v1 out of bag: mean difference -0.007, 95 % CI [-0.033, +0.011], one-sided bootstrap p = 0.721 (share of resamples where the selected weighting is ahead: 0.28).
* Full-data best vs v1: in-bag p = 0.634; out-of-bag p = 0.644.
* Selection instability: 624 distinct weightings were selected across resamples; mean selected weights f1 0.30, decay 0.28, precision 0.16, recall 0.27 (sd f1 0.26, decay 0.22, precision 0.16, recall 0.25). Most often: f1 0.00, decay 0.70, precision 0.00, recall 0.30 (1 %); f1 0.00, decay 0.35, precision 0.00, recall 0.65 (1 %); f1 0.00, decay 0.40, precision 0.00, recall 0.60 (1 %).
* **Plateau** (weightings not significantly below the best, paired bootstrap p > .05): 1749 of 1771 (99 %); v1 inside: True (p vs best 0.63). Practical plateau (bootstrap-mean J within 0.02 of the best): 1731 weightings, v1 inside: True; weight ranges inside it: f1 [0.00, 1.00], decay [0.00, 1.00], precision [0.00, 0.85], recall [0.00, 0.95].
* v1 is in the top 5 % of in-bag J in 6 % of resamples.

Figures: `selection/fig_nested`, `selection/fig_plateau`.

## 4. Transfer: leave-one-dataset-out and leave-one-family-out

| held out | J on the rest (LODO weights) | LODO weights | τ held-out → pooled rest: LODO weights | full best | v1 |
|---|---|---|---|---|---|
| abt_buy | 0.406 | f1 0.20, decay 0.00, precision 0.50, recall 0.30 | +0.86 | +0.72 | +0.72 |
| alaska_camera | 0.449 | f1 0.00, decay 0.55, precision 0.10, recall 0.35 | -0.38 | -0.40 | -0.40 |
| alaska_schema | 0.435 | f1 0.45, decay 0.25, precision 0.20, recall 0.10 | -0.18 | -0.09 | -0.16 |
| amazon_google | 0.430 | f1 0.55, decay 0.00, precision 0.30, recall 0.15 | +0.00 | -0.06 | -0.06 |
| bird | 0.412 | f1 0.35, decay 0.60, precision 0.05, recall 0.00 | +0.37 | +0.37 | +0.56 |
| dblp_acm | 0.409 | f1 0.00, decay 0.15, precision 0.15, recall 0.70 | +0.56 | +0.54 | +0.54 |
| dblp_scholar | 0.431 | f1 0.05, decay 0.55, precision 0.30, recall 0.10 | -0.02 | +0.00 | -0.04 |
| fetaqa | 0.418 | f1 0.00, decay 0.15, precision 0.00, recall 0.85 | +0.41 | +0.38 | +0.33 |
| fintagging | 0.408 | f1 0.20, decay 0.25, precision 0.30, recall 0.25 | +0.44 | +0.60 | +0.49 |
| hitab | 0.440 | f1 0.45, decay 0.20, precision 0.20, recall 0.15 | -0.34 | -0.35 | -0.38 |
| machamp | 0.406 | f1 0.80, decay 0.00, precision 0.20, recall 0.00 | +0.67 | +0.72 | +0.71 |
| magneto_gdc | 0.414 | f1 0.00, decay 0.25, precision 0.20, recall 0.55 | +0.49 | +0.45 | +0.45 |
| mmtu | 0.409 | f1 0.25, decay 0.10, precision 0.15, recall 0.50 | +0.40 | +0.53 | +0.48 |
| officeqa | 0.412 | f1 0.50, decay 0.00, precision 0.35, recall 0.15 | +0.51 | +0.60 | +0.53 |
| officeqa_pro_v2 | 0.410 | f1 0.00, decay 0.60, precision 0.00, recall 0.40 | +0.45 | +0.45 | +0.44 |
| opensanctions_pairs | 0.422 | f1 0.35, decay 0.60, precision 0.05, recall 0.00 | +0.04 | +0.04 | +0.00 |
| papadakis_dn | 0.433 | f1 0.50, decay 0.00, precision 0.35, recall 0.15 | -0.10 | -0.02 | -0.08 |
| realhitbench | 0.409 | f1 0.60, decay 0.20, precision 0.20, recall 0.00 | +0.64 | +0.64 | +0.60 |
| smat | 0.419 | f1 0.25, decay 0.15, precision 0.05, recall 0.55 | +0.16 | +0.37 | +0.27 |
| suc | 0.410 | f1 0.10, decay 0.75, precision 0.00, recall 0.15 | +0.60 | +0.55 | +0.48 |
| tab_fact | 0.427 | f1 0.30, decay 0.00, precision 0.45, recall 0.25 | -0.04 | -0.09 | -0.06 |
| tabis | 0.420 | f1 0.00, decay 0.05, precision 0.50, recall 0.45 | +0.44 | +0.41 | +0.37 |
| tablebench | 0.415 | f1 0.80, decay 0.00, precision 0.20, recall 0.00 | +0.44 | +0.38 | +0.38 |
| tableeval | 0.416 | f1 0.20, decay 0.00, precision 0.50, recall 0.30 | +0.29 | +0.24 | +0.20 |
| tat_qa | 0.411 | f1 0.20, decay 0.75, precision 0.05, recall 0.00 | +0.37 | +0.56 | +0.51 |
| tpcdi_cells | 0.412 | f1 0.50, decay 0.10, precision 0.00, recall 0.40 | +0.54 | +0.51 | +0.51 |
| valentine | 0.412 | f1 0.00, decay 0.05, precision 0.50, recall 0.45 | +0.42 | +0.47 | +0.40 |
| walmart_amazon | 0.404 | f1 0.25, decay 0.15, precision 0.05, recall 0.55 | +0.73 | +0.65 | +0.65 |
| wdc_lspc | 0.418 | f1 0.05, decay 0.15, precision 0.35, recall 0.45 | +0.48 | +0.50 | +0.46 |
| wdc_products | 0.414 | f1 0.80, decay 0.00, precision 0.20, recall 0.00 | +0.31 | +0.31 | +0.31 |
| wikitablequestions | 0.403 | f1 0.80, decay 0.00, precision 0.20, recall 0.00 | +0.71 | +0.75 | +0.71 |

Mean held-out τ: LODO weights +0.33, full best +0.35, v1 +0.32.

| held-out family | J on the rest | LOFO weights | τ held-out: LOFO weights | full best | v1 |
|---|---|---|---|---|---|
| EM | 0.471 | f1 0.70, decay 0.15, precision 0.05, recall 0.10 | +0.32 | +0.31 | +0.32 |
| SM | 0.420 | f1 0.05, decay 0.25, precision 0.00, recall 0.70 | +0.33 | +0.30 | +0.28 |
| TQA | 0.421 | f1 0.05, decay 0.00, precision 0.60, recall 0.35 | +0.33 | +0.37 | +0.33 |
| FIN | 0.400 | f1 0.05, decay 0.75, precision 0.05, recall 0.15 | +0.45 | +0.49 | +0.44 |

Per-family best weightings:
* EM: f1 0.35, decay 0.60, precision 0.05, recall 0.00 (J 0.358; under the global best 0.358; under v1 0.358; L1 distance to global best 0.00) — datasets: abt_buy, alaska_camera, amazon_google, dblp_acm, dblp_scholar, machamp, opensanctions_pairs, papadakis_dn, walmart_amazon, wdc_lspc, wdc_products
* SM: f1 0.00, decay 1.00, precision 0.00, recall 0.00 (J 0.556; under the global best 0.535; under v1 0.512; L1 distance to global best 0.80) — datasets: alaska_schema, fintagging, magneto_gdc, smat, tpcdi_cells, valentine
* TQA: f1 0.05, decay 0.05, precision 0.25, recall 0.65 (J 0.484; under the global best 0.470; under v1 0.463; L1 distance to global best 1.70) — datasets: bird, fetaqa, hitab, mmtu, realhitbench, suc, tab_fact, tabis, tablebench, tableeval, wikitablequestions
* FIN: f1 0.00, decay 0.05, precision 0.00, recall 0.95 (J 0.842; under the global best 0.697; under v1 0.685; L1 distance to global best 1.90) — datasets: officeqa, officeqa_pro_v2, tat_qa

## 5. Correctness on known-quality anchors (borrowed from v5; does not change the objective)

31,380 synthetic answers of known utility over the 31 datasets (9,881 correct, 7,430 wrong; operators: digit_typo, flip, hedge, identity, list_dump, magnitude, near_miss_large, near_miss_medium, near_miss_small, no_answer, paraphrase, partial, shuffled, sign_flip, superset, tagged, typo, unit_variant, verbose, wrong_random).

| rule | weights | J (agreement) | ρ to utility | mean per-dataset ρ | AUC correct vs wrong | mean score of wrong answers | hedge gap | rank by J | rank by ρ |
|---|---|---|---|---|---|---|---|---|---|
| v1 | f1 0.35, decay 0.35, precision 0.15, recall 0.15 | 0.392 | 0.878 | 0.868 | 0.994 | 0.034 | -0.51 | 1602 | 370 |
| best_J | f1 0.35, decay 0.60, precision 0.05, recall 0.00 | 0.414 | 0.876 | 0.866 | 0.994 | 0.036 | -0.56 | 1 | 722 |
| best_rho | f1 0.00, decay 0.35, precision 0.60, recall 0.05 | 0.391 | 0.883 | 0.871 | 0.994 | 0.034 | -0.57 | 1667 | 1 |
| pareto_knee | f1 0.35, decay 0.60, precision 0.05, recall 0.00 | 0.414 | 0.876 | 0.866 | 0.994 | 0.036 | -0.56 | 1 | 722 |
| exact match | – | – | 0.828 | 0.830 | 0.989 | 0.011 | -0.81 | – | – |

Spearman correlation between J and ρ across all 1,771 weightings: **-0.23**. Pareto front size 17. rho and auc are correctness against known-utility anchors; J is agreement among datasets. If the best-J weighting also has high rho, agreement and correctness pull the same way; if not, the Pareto knee is the defensible compromise.

Figure: `anchors/fig_pareto`.

## 6. Sensitivity

* v1: 12 lattice neighbours within one 0.05 move; J centre 0.392, neighbours min 0.388 / mean 0.394 / max 0.400 (range 0.012); 77 % of neighbours are better.
* best: 9 lattice neighbours within one 0.05 move; J centre 0.414, neighbours min 0.398 / mean 0.406 / max 0.414 (range 0.017); 0 % of neighbours are better.

## 7. Leaderboards under the naive, deployed and calibrated rules

Bradley–Terry (headline) rankings, with Borda in brackets; full tables, strengths with standard errors, 1,000 bootstrap draws, Friedman/Nemenyi, Holm-corrected pairwise tests and LaTeX under `leaderboards/<rule>/`.

| rule | weights | claude-opus-5 | claude-sonnet-5 | deepseek-chat | deepseek-r1 | gemini-3.1-pro | gemini-3.8-flash | gpt-5.4-mini | gpt-5.5 | gpt-oss-120b | grok-4 | llama-3.3-70b | Friedman p | Kendall's W | significant pairs (Holm) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| em_only | – | 1 (1) | 7 (4) | 9 (8) | 6 (5) | 4 (7) | 3 (3) | 8 (9) | 2 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| v1_original | f1 0.35, decay 0.35, precision 0.15, recall 0.15 | 2 (2) | 4 (4) | 9 (8) | 7 (5) | 5 (6) | 1 (3) | 8 (9) | 3 (1) | 10 (10) | 6 (7) | 11 (11) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top1 | f1 0.35, decay 0.60, precision 0.05, recall 0.00 | 2 (2) | 4 (4) | 9 (9) | 7 (7) | 5 (5) | 1 (3) | 8 (8) | 3 (1) | 10 (10) | 6 (5) | 11 (11) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top2 | f1 0.80, decay 0.00, precision 0.20, recall 0.00 | 3 (1) | 7 (5) | 8 (8) | 6 (7) | 4 (4) | 1 (3) | 9 (9) | 2 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top3 | f1 0.85, decay 0.00, precision 0.15, recall 0.00 | 3 (1) | 7 (5) | 8 (8) | 6 (7) | 4 (4) | 1 (3) | 9 (9) | 2 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top4 | f1 0.20, decay 0.00, precision 0.50, recall 0.30 | 3 (1) | 7 (5) | 8 (8) | 5 (5) | 4 (4) | 1 (3) | 9 (9) | 2 (2) | 10 (10) | 6 (7) | 11 (11) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top5 | f1 0.00, decay 0.15, precision 0.15, recall 0.70 | 2 (1) | 4 (6) | 8 (8) | 7 (4) | 5 (6) | 1 (3) | 9 (9) | 3 (2) | 10 (10) | 6 (5) | 11 (11) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| best_anchor | f1 0.00, decay 0.35, precision 0.60, recall 0.05 | 2 (2) | 4 (4) | 9 (9) | 8 (6) | 5 (5) | 1 (3) | 6 (8) | 3 (1) | 10 (10) | 7 (7) | 11 (11) | 0.000 | 0.25 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| pareto_knee | f1 0.35, decay 0.60, precision 0.05, recall 0.00 | 2 (2) | 4 (4) | 9 (9) | 7 (7) | 5 (5) | 1 (3) | 8 (8) | 3 (1) | 10 (10) | 6 (5) | 11 (11) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |

Agreement between the BT rankings of the rules (Kendall τ):

| | em_only | v1_original | top1 | top2 | top3 | top4 | top5 | best_anchor | pareto_knee |
|---|---|---|---|---|---|---|---|---|---|
| em_only | +1.00 | +0.82 | +0.82 | +0.85 | +0.85 | +0.82 | +0.78 | +0.75 | +0.82 |
| v1_original | +0.82 | +1.00 | +1.00 | +0.82 | +0.82 | +0.78 | +0.96 | +0.93 | +1.00 |
| top1 | +0.82 | +1.00 | +1.00 | +0.82 | +0.82 | +0.78 | +0.96 | +0.93 | +1.00 |
| top2 | +0.85 | +0.82 | +0.82 | +1.00 | +1.00 | +0.96 | +0.85 | +0.75 | +0.82 |
| top3 | +0.85 | +0.82 | +0.82 | +1.00 | +1.00 | +0.96 | +0.85 | +0.75 | +0.82 |
| top4 | +0.82 | +0.78 | +0.78 | +0.96 | +0.96 | +1.00 | +0.82 | +0.71 | +0.78 |
| top5 | +0.78 | +0.96 | +0.96 | +0.85 | +0.85 | +0.82 | +1.00 | +0.89 | +0.96 |
| best_anchor | +0.75 | +0.93 | +0.93 | +0.75 | +0.75 | +0.71 | +0.89 | +1.00 | +0.93 |
| pareto_knee | +0.82 | +1.00 | +1.00 | +0.82 | +0.82 | +0.78 | +0.96 | +0.93 | +1.00 |

## Official-split estimates under the deployed rule (v1 weights)

Suite score = mean over the stratified pool (equal strata; the calibration number). Official estimate = the same answers re-weighted to the official split's stratum or class proportions (post-stratification), with a 95 % weighted item bootstrap; F1 = positive-class F1 at the official match ratio for boolean matching sets. n/c = not comparable (constructed pairs, closed-book, or no census).

| dataset | model | suite score | official estimate [95 %] | positive-class F1 (suite → official) | effective n |
|---|---|---|---|---|---|
| abt_buy | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 63 |
| abt_buy | claude-sonnet-5 | 0.970 | 0.993 [0.98, 1.00] | 0.97 → 0.97 [0.92, 1.00] | 63 |
| abt_buy | deepseek-chat | 0.960 | 0.976 [0.93, 1.00] | 0.96 → 0.89 [0.73, 0.99] | 63 |
| abt_buy | deepseek-r1 | 0.970 | 0.978 [0.93, 1.00] | 0.97 → 0.90 [0.75, 1.00] | 63 |
| abt_buy | gemini-3.1-pro | 0.980 | 0.996 [0.99, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 63 |
| abt_buy | gemini-3.8-flash | 0.980 | 0.996 [0.99, 1.00] | 0.98 → 0.98 [0.94, 1.00] | 63 |
| abt_buy | gpt-5.4-mini | 0.960 | 0.976 [0.94, 1.00] | 0.96 → 0.89 [0.74, 0.99] | 63 |
| abt_buy | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 63 |
| abt_buy | gpt-oss-120b | 0.940 | 0.987 [0.97, 1.00] | 0.93 → 0.93 [0.87, 0.98] | 63 |
| abt_buy | grok-4 | 0.960 | 0.976 [0.93, 1.00] | 0.96 → 0.89 [0.74, 0.99] | 63 |
| abt_buy | llama-3.3-70b | 0.960 | 0.976 [0.94, 1.00] | 0.96 → 0.89 [0.74, 0.99] | 63 |
| alaska_camera | claude-opus-5 | 0.820 | n/c | – | 100 |
| alaska_camera | claude-sonnet-5 | 0.980 | n/c | – | 100 |
| alaska_camera | deepseek-chat | 1.000 | n/c | – | 100 |
| alaska_camera | deepseek-r1 | 0.990 | n/c | – | 100 |
| alaska_camera | gemini-3.1-pro | 0.810 | n/c | – | 100 |
| alaska_camera | gemini-3.8-flash | 0.890 | n/c | – | 100 |
| alaska_camera | gpt-5.4-mini | 0.970 | n/c | – | 100 |
| alaska_camera | gpt-5.5 | 1.000 | n/c | – | 100 |
| alaska_camera | gpt-oss-120b | 1.000 | n/c | – | 100 |
| alaska_camera | grok-4 | 0.940 | n/c | – | 100 |
| alaska_camera | llama-3.3-70b | 0.990 | n/c | – | 100 |
| alaska_schema | claude-opus-5 | 0.945 | 0.945 [0.90, 0.98] | – | 93 |
| alaska_schema | claude-sonnet-5 | 0.929 | 0.929 [0.88, 0.97] | – | 93 |
| alaska_schema | deepseek-chat | 0.951 | 0.951 [0.91, 0.99] | – | 93 |
| alaska_schema | deepseek-r1 | 0.957 | 0.957 [0.92, 0.99] | – | 93 |
| alaska_schema | gemini-3.1-pro | 0.928 | 0.928 [0.87, 0.97] | – | 93 |
| alaska_schema | gemini-3.8-flash | 0.918 | 0.918 [0.86, 0.96] | – | 93 |
| alaska_schema | gpt-5.4-mini | 0.958 | 0.958 [0.92, 0.99] | – | 93 |
| alaska_schema | gpt-5.5 | 0.928 | 0.928 [0.88, 0.97] | – | 93 |
| alaska_schema | gpt-oss-120b | 0.934 | 0.934 [0.89, 0.97] | – | 93 |
| alaska_schema | grok-4 | 0.929 | 0.929 [0.88, 0.97] | – | 93 |
| alaska_schema | llama-3.3-70b | 0.840 | 0.840 [0.78, 0.89] | – | 93 |
| amazon_google | claude-opus-5 | 0.940 | 0.916 [0.84, 0.98] | 0.94 → 0.70 [0.53, 0.92] | 67 |
| amazon_google | claude-sonnet-5 | 0.960 | 0.935 [0.87, 0.98] | 0.96 → 0.76 [0.59, 0.94] | 67 |
| amazon_google | deepseek-chat | 0.960 | 0.949 [0.89, 1.00] | 0.96 → 0.80 [0.61, 0.99] | 67 |
| amazon_google | deepseek-r1 | 0.950 | 0.932 [0.87, 0.98] | 0.95 → 0.75 [0.58, 0.93] | 67 |
| amazon_google | gemini-3.1-pro | 0.930 | 0.928 [0.86, 0.98] | 0.92 → 0.73 [0.55, 0.91] | 67 |
| amazon_google | gemini-3.8-flash | 0.930 | 0.928 [0.86, 0.98] | 0.92 → 0.73 [0.55, 0.91] | 67 |
| amazon_google | gpt-5.4-mini | 0.930 | 0.942 [0.88, 0.99] | 0.92 → 0.76 [0.58, 0.96] | 67 |
| amazon_google | gpt-5.5 | 0.940 | 0.916 [0.84, 0.98] | 0.94 → 0.70 [0.54, 0.91] | 67 |
| amazon_google | gpt-oss-120b | 0.860 | 0.926 [0.86, 0.97] | 0.83 → 0.68 [0.51, 0.87] | 67 |
| amazon_google | grok-4 | 0.940 | 0.944 [0.87, 0.99] | 0.93 → 0.77 [0.61, 0.97] | 67 |
| amazon_google | llama-3.3-70b | 0.950 | 0.932 [0.86, 0.98] | 0.95 → 0.75 [0.56, 0.94] | 67 |
| bird | claude-opus-5 | 0.293 | 0.323 [0.23, 0.42] | – | 74 |
| bird | claude-sonnet-5 | 0.233 | 0.260 [0.17, 0.35] | – | 74 |
| bird | deepseek-chat | 0.187 | 0.203 [0.13, 0.29] | – | 74 |
| bird | deepseek-r1 | 0.214 | 0.254 [0.17, 0.34] | – | 74 |
| bird | gemini-3.1-pro | 0.183 | 0.228 [0.14, 0.32] | – | 74 |
| bird | gemini-3.8-flash | 0.293 | 0.313 [0.23, 0.40] | – | 74 |
| bird | gpt-5.4-mini | 0.178 | 0.218 [0.13, 0.31] | – | 74 |
| bird | gpt-5.5 | 0.185 | 0.204 [0.12, 0.29] | – | 74 |
| bird | gpt-oss-120b | 0.084 | 0.109 [0.05, 0.18] | – | 74 |
| bird | grok-4 | 0.122 | 0.144 [0.07, 0.23] | – | 74 |
| bird | llama-3.3-70b | 0.122 | 0.144 [0.08, 0.22] | – | 74 |
| dblp_acm | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | claude-sonnet-5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | deepseek-chat | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | deepseek-r1 | 0.990 | 0.996 [0.99, 1.00] | 0.99 → 0.99 [0.96, 1.00] | 72 |
| dblp_acm | gemini-3.1-pro | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | gemini-3.8-flash | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | gpt-5.4-mini | 0.990 | 0.996 [0.99, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 72 |
| dblp_acm | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | gpt-oss-120b | 0.910 | 0.967 [0.94, 0.99] | 0.90 → 0.90 [0.83, 0.96] | 72 |
| dblp_acm | grok-4 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 72 |
| dblp_acm | llama-3.3-70b | 0.970 | 0.952 [0.89, 1.00] | 0.97 → 0.88 [0.75, 1.00] | 72 |
| dblp_scholar | claude-opus-5 | 0.950 | 0.956 [0.90, 1.00] | 0.95 → 0.89 [0.75, 0.98] | 70 |
| dblp_scholar | claude-sonnet-5 | 0.970 | 0.976 [0.93, 1.00] | 0.97 → 0.94 [0.83, 1.00] | 70 |
| dblp_scholar | deepseek-chat | 0.960 | 0.959 [0.91, 1.00] | 0.96 → 0.90 [0.78, 0.99] | 70 |
| dblp_scholar | deepseek-r1 | 0.950 | 0.969 [0.93, 1.00] | 0.95 → 0.92 [0.82, 0.99] | 70 |
| dblp_scholar | gemini-3.1-pro | 0.940 | 0.965 [0.93, 0.99] | 0.94 → 0.91 [0.81, 0.98] | 70 |
| dblp_scholar | gemini-3.8-flash | 0.930 | 0.961 [0.91, 0.99] | 0.93 → 0.90 [0.79, 0.97] | 70 |
| dblp_scholar | gpt-5.4-mini | 0.940 | 0.965 [0.92, 0.99] | 0.94 → 0.91 [0.80, 0.98] | 70 |
| dblp_scholar | gpt-5.5 | 0.960 | 0.959 [0.91, 1.00] | 0.96 → 0.90 [0.78, 0.99] | 70 |
| dblp_scholar | gpt-oss-120b | 0.910 | 0.967 [0.94, 0.99] | 0.90 → 0.90 [0.83, 0.96] | 70 |
| dblp_scholar | grok-4 | 0.950 | 0.969 [0.93, 1.00] | 0.95 → 0.92 [0.81, 0.99] | 70 |
| dblp_scholar | llama-3.3-70b | 0.970 | 0.976 [0.94, 1.00] | 0.97 → 0.94 [0.85, 1.00] | 70 |
| fetaqa | claude-opus-5 | 0.401 | 0.401 [0.37, 0.43] | – | 100 |
| fetaqa | claude-sonnet-5 | 0.373 | 0.373 [0.35, 0.40] | – | 100 |
| fetaqa | deepseek-chat | 0.434 | 0.434 [0.41, 0.46] | – | 100 |
| fetaqa | deepseek-r1 | 0.413 | 0.413 [0.38, 0.45] | – | 100 |
| fetaqa | gemini-3.1-pro | 0.433 | 0.433 [0.41, 0.46] | – | 100 |
| fetaqa | gemini-3.8-flash | 0.445 | 0.445 [0.42, 0.47] | – | 100 |
| fetaqa | gpt-5.4-mini | 0.312 | 0.312 [0.29, 0.34] | – | 100 |
| fetaqa | gpt-5.5 | 0.438 | 0.438 [0.41, 0.47] | – | 100 |
| fetaqa | gpt-oss-120b | 0.322 | 0.322 [0.30, 0.34] | – | 100 |
| fetaqa | grok-4 | 0.428 | 0.428 [0.40, 0.45] | – | 100 |
| fetaqa | llama-3.3-70b | 0.253 | 0.253 [0.23, 0.28] | – | 100 |
| fintagging | claude-opus-5 | 0.909 | 0.932 [0.88, 0.98] | – | 52 |
| fintagging | claude-sonnet-5 | 0.898 | 0.897 [0.83, 0.96] | – | 52 |
| fintagging | deepseek-chat | 0.858 | 0.847 [0.77, 0.91] | – | 52 |
| fintagging | deepseek-r1 | 0.873 | 0.885 [0.81, 0.95] | – | 52 |
| fintagging | gemini-3.1-pro | 0.887 | 0.907 [0.84, 0.96] | – | 52 |
| fintagging | gemini-3.8-flash | 0.897 | 0.908 [0.85, 0.96] | – | 52 |
| fintagging | gpt-5.4-mini | 0.892 | 0.863 [0.79, 0.92] | – | 52 |
| fintagging | gpt-5.5 | 0.893 | 0.899 [0.83, 0.96] | – | 52 |
| fintagging | gpt-oss-120b | 0.863 | 0.847 [0.77, 0.92] | – | 52 |
| fintagging | grok-4 | 0.887 | 0.876 [0.81, 0.94] | – | 52 |
| fintagging | llama-3.3-70b | 0.858 | 0.836 [0.76, 0.91] | – | 52 |
| hitab | claude-opus-5 | 0.781 | 0.790 [0.71, 0.86] | – | 95 |
| hitab | claude-sonnet-5 | 0.763 | 0.758 [0.67, 0.84] | – | 95 |
| hitab | deepseek-chat | 0.814 | 0.822 [0.75, 0.89] | – | 95 |
| hitab | deepseek-r1 | 0.783 | 0.781 [0.71, 0.85] | – | 95 |
| hitab | gemini-3.1-pro | 0.778 | 0.786 [0.70, 0.86] | – | 95 |
| hitab | gemini-3.8-flash | 0.748 | 0.757 [0.68, 0.83] | – | 95 |
| hitab | gpt-5.4-mini | 0.784 | 0.783 [0.71, 0.85] | – | 95 |
| hitab | gpt-5.5 | 0.757 | 0.764 [0.68, 0.84] | – | 95 |
| hitab | gpt-oss-120b | 0.750 | 0.752 [0.67, 0.83] | – | 95 |
| hitab | grok-4 | 0.746 | 0.749 [0.67, 0.82] | – | 95 |
| hitab | llama-3.3-70b | 0.784 | 0.783 [0.70, 0.85] | – | 95 |
| machamp | claude-opus-5 | 0.900 | 0.912 [0.83, 0.97] | 0.90 → 0.77 [0.62, 0.91] | 32 |
| machamp | claude-sonnet-5 | 0.900 | 0.923 [0.85, 0.97] | 0.90 → 0.79 [0.64, 0.92] | 32 |
| machamp | deepseek-chat | 0.890 | 0.892 [0.80, 0.96] | 0.90 → 0.74 [0.60, 0.89] | 32 |
| machamp | deepseek-r1 | 0.900 | 0.897 [0.81, 0.96] | 0.91 → 0.75 [0.59, 0.90] | 32 |
| machamp | gemini-3.1-pro | 0.890 | 0.908 [0.83, 0.97] | 0.89 → 0.76 [0.62, 0.90] | 32 |
| machamp | gemini-3.8-flash | 0.900 | 0.912 [0.84, 0.97] | 0.90 → 0.77 [0.61, 0.92] | 32 |
| machamp | gpt-5.4-mini | 0.890 | 0.893 [0.80, 0.96] | 0.90 → 0.74 [0.57, 0.90] | 32 |
| machamp | gpt-5.5 | 0.900 | 0.897 [0.81, 0.96] | 0.91 → 0.75 [0.59, 0.90] | 32 |
| machamp | gpt-oss-120b | 0.830 | 0.794 [0.66, 0.91] | 0.83 → 0.56 [0.36, 0.76] | 32 |
| machamp | grok-4 | 0.890 | 0.896 [0.81, 0.96] | 0.90 → 0.75 [0.59, 0.91] | 32 |
| machamp | llama-3.3-70b | 0.870 | 0.880 [0.79, 0.95] | 0.87 → 0.70 [0.53, 0.85] | 32 |
| magneto_gdc | claude-opus-5 | 0.971 | 0.974 [0.95, 0.99] | – | 93 |
| magneto_gdc | claude-sonnet-5 | 0.955 | 0.955 [0.92, 0.99] | – | 93 |
| magneto_gdc | deepseek-chat | 0.953 | 0.956 [0.92, 0.99] | – | 93 |
| magneto_gdc | deepseek-r1 | 0.978 | 0.981 [0.96, 1.00] | – | 93 |
| magneto_gdc | gemini-3.1-pro | 0.956 | 0.957 [0.92, 0.98] | – | 93 |
| magneto_gdc | gemini-3.8-flash | 0.963 | 0.967 [0.94, 0.99] | – | 93 |
| magneto_gdc | gpt-5.4-mini | 0.912 | 0.914 [0.86, 0.96] | – | 93 |
| magneto_gdc | gpt-5.5 | 0.967 | 0.972 [0.94, 0.99] | – | 93 |
| magneto_gdc | gpt-oss-120b | 0.961 | 0.965 [0.93, 0.99] | – | 93 |
| magneto_gdc | grok-4 | 0.939 | 0.944 [0.90, 0.98] | – | 93 |
| magneto_gdc | llama-3.3-70b | 0.753 | 0.759 [0.69, 0.82] | – | 93 |
| mmtu | claude-opus-5 | 0.882 | 0.846 [0.76, 0.93] | – | 87 |
| mmtu | claude-sonnet-5 | 0.872 | 0.838 [0.75, 0.92] | – | 87 |
| mmtu | deepseek-chat | 0.865 | 0.831 [0.74, 0.91] | – | 87 |
| mmtu | deepseek-r1 | 0.842 | 0.794 [0.70, 0.88] | – | 87 |
| mmtu | gemini-3.1-pro | 0.914 | 0.881 [0.79, 0.95] | – | 87 |
| mmtu | gemini-3.8-flash | 0.894 | 0.856 [0.77, 0.93] | – | 87 |
| mmtu | gpt-5.4-mini | 0.882 | 0.851 [0.77, 0.93] | – | 87 |
| mmtu | gpt-5.5 | 0.917 | 0.882 [0.80, 0.95] | – | 87 |
| mmtu | gpt-oss-120b | 0.830 | 0.774 [0.68, 0.87] | – | 87 |
| mmtu | grok-4 | 0.901 | 0.869 [0.79, 0.95] | – | 87 |
| mmtu | llama-3.3-70b | 0.807 | 0.773 [0.68, 0.85] | – | 87 |
| officeqa | claude-opus-5 | 0.199 | n/c | – | 100 |
| officeqa | claude-sonnet-5 | 0.171 | n/c | – | 100 |
| officeqa | deepseek-chat | 0.075 | n/c | – | 100 |
| officeqa | deepseek-r1 | 0.092 | n/c | – | 100 |
| officeqa | gemini-3.1-pro | 0.119 | n/c | – | 100 |
| officeqa | gemini-3.8-flash | 0.194 | n/c | – | 100 |
| officeqa | gpt-5.4-mini | 0.107 | n/c | – | 100 |
| officeqa | gpt-5.5 | 0.168 | n/c | – | 100 |
| officeqa | gpt-oss-120b | 0.079 | n/c | – | 100 |
| officeqa | grok-4 | 0.129 | n/c | – | 100 |
| officeqa | llama-3.3-70b | 0.097 | n/c | – | 100 |
| officeqa_pro_v2 | claude-opus-5 | 0.270 | 0.270 [0.21, 0.34] | – | 90 |
| officeqa_pro_v2 | claude-sonnet-5 | 0.154 | 0.154 [0.11, 0.21] | – | 90 |
| officeqa_pro_v2 | deepseek-chat | 0.121 | 0.121 [0.08, 0.16] | – | 90 |
| officeqa_pro_v2 | deepseek-r1 | 0.050 | 0.050 [0.03, 0.08] | – | 90 |
| officeqa_pro_v2 | gemini-3.1-pro | 0.120 | 0.120 [0.08, 0.16] | – | 90 |
| officeqa_pro_v2 | gemini-3.8-flash | 0.198 | 0.198 [0.15, 0.25] | – | 90 |
| officeqa_pro_v2 | gpt-5.4-mini | 0.123 | 0.123 [0.10, 0.15] | – | 90 |
| officeqa_pro_v2 | gpt-5.5 | 0.188 | 0.188 [0.13, 0.25] | – | 90 |
| officeqa_pro_v2 | gpt-oss-120b | 0.104 | 0.104 [0.07, 0.15] | – | 90 |
| officeqa_pro_v2 | grok-4 | 0.119 | 0.119 [0.08, 0.16] | – | 90 |
| officeqa_pro_v2 | llama-3.3-70b | 0.115 | 0.115 [0.08, 0.15] | – | 90 |
| opensanctions_pairs | claude-opus-5 | 0.940 | 0.906 [0.83, 0.97] | 0.93 → 0.93 [0.88, 0.98] | 76 |
| opensanctions_pairs | claude-sonnet-5 | 0.730 | 0.587 [0.48, 0.70] | 0.63 → 0.64 [0.50, 0.75] | 76 |
| opensanctions_pairs | deepseek-chat | 0.760 | 0.635 [0.53, 0.74] | 0.68 → 0.69 [0.54, 0.80] | 76 |
| opensanctions_pairs | deepseek-r1 | 0.850 | 0.765 [0.67, 0.86] | 0.82 → 0.82 [0.71, 0.90] | 76 |
| opensanctions_pairs | gemini-3.1-pro | 0.970 | 0.964 [0.92, 1.00] | 0.97 → 0.98 [0.94, 1.00] | 76 |
| opensanctions_pairs | gemini-3.8-flash | 0.860 | 0.780 [0.68, 0.88] | 0.83 → 0.83 [0.73, 0.91] | 76 |
| opensanctions_pairs | gpt-5.4-mini | 0.900 | 0.865 [0.78, 0.94] | 0.89 → 0.91 [0.83, 0.96] | 76 |
| opensanctions_pairs | gpt-5.5 | 0.750 | 0.608 [0.50, 0.72] | 0.66 → 0.66 [0.52, 0.78] | 76 |
| opensanctions_pairs | gpt-oss-120b | 0.780 | 0.666 [0.56, 0.78] | 0.72 → 0.72 [0.59, 0.81] | 76 |
| opensanctions_pairs | grok-4 | 0.850 | 0.776 [0.68, 0.87] | 0.82 → 0.83 [0.73, 0.91] | 76 |
| opensanctions_pairs | llama-3.3-70b | 0.790 | 0.682 [0.57, 0.80] | 0.73 → 0.74 [0.62, 0.84] | 76 |
| papadakis_dn | claude-opus-5 | 0.920 | 0.955 [0.89, 1.00] | 0.79 → 0.32 [0.13, 0.81] | 33 |
| papadakis_dn | claude-sonnet-5 | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.56, 0.94] | 33 |
| papadakis_dn | deepseek-chat | 0.940 | 0.993 [0.99, 1.00] | 0.83 → 0.76 [0.53, 0.92] | 33 |
| papadakis_dn | deepseek-r1 | 0.940 | 0.993 [0.99, 1.00] | 0.83 → 0.76 [0.53, 0.92] | 33 |
| papadakis_dn | gemini-3.1-pro | 0.930 | 0.974 [0.93, 1.00] | 0.81 → 0.45 [0.20, 0.89] | 33 |
| papadakis_dn | gemini-3.8-flash | 0.940 | 0.992 [0.98, 1.00] | 0.82 → 0.70 [0.44, 0.89] | 33 |
| papadakis_dn | gpt-5.4-mini | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.58, 0.95] | 33 |
| papadakis_dn | gpt-5.5 | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.56, 0.94] | 33 |
| papadakis_dn | gpt-oss-120b | 0.930 | 0.992 [0.98, 1.00] | 0.79 → 0.68 [0.43, 0.89] | 33 |
| papadakis_dn | grok-4 | 0.950 | 0.994 [0.99, 1.00] | 0.86 → 0.79 [0.56, 0.95] | 33 |
| papadakis_dn | llama-3.3-70b | 0.940 | 0.975 [0.93, 1.00] | 0.83 → 0.46 [0.19, 0.91] | 33 |
| realhitbench | claude-opus-5 | 0.743 | 0.745 [0.66, 0.81] | – | 98 |
| realhitbench | claude-sonnet-5 | 0.681 | 0.684 [0.61, 0.77] | – | 98 |
| realhitbench | deepseek-chat | 0.662 | 0.656 [0.58, 0.74] | – | 98 |
| realhitbench | deepseek-r1 | 0.655 | 0.655 [0.57, 0.74] | – | 98 |
| realhitbench | gemini-3.1-pro | 0.699 | 0.698 [0.61, 0.78] | – | 98 |
| realhitbench | gemini-3.8-flash | 0.746 | 0.747 [0.67, 0.82] | – | 98 |
| realhitbench | gpt-5.4-mini | 0.661 | 0.658 [0.57, 0.74] | – | 98 |
| realhitbench | gpt-5.5 | 0.724 | 0.721 [0.64, 0.80] | – | 98 |
| realhitbench | gpt-oss-120b | 0.603 | 0.602 [0.51, 0.69] | – | 98 |
| realhitbench | grok-4 | 0.640 | 0.638 [0.55, 0.72] | – | 98 |
| realhitbench | llama-3.3-70b | 0.611 | 0.616 [0.54, 0.69] | – | 98 |
| smat | claude-opus-5 | 0.933 | 0.931 [0.89, 0.97] | – | 98 |
| smat | claude-sonnet-5 | 0.938 | 0.936 [0.89, 0.97] | – | 98 |
| smat | deepseek-chat | 0.918 | 0.916 [0.86, 0.96] | – | 98 |
| smat | deepseek-r1 | 0.921 | 0.919 [0.87, 0.96] | – | 98 |
| smat | gemini-3.1-pro | 0.883 | 0.881 [0.82, 0.93] | – | 98 |
| smat | gemini-3.8-flash | 0.921 | 0.919 [0.87, 0.96] | – | 98 |
| smat | gpt-5.4-mini | 0.956 | 0.958 [0.92, 0.99] | – | 98 |
| smat | gpt-5.5 | 0.940 | 0.939 [0.90, 0.97] | – | 98 |
| smat | gpt-oss-120b | 0.916 | 0.913 [0.86, 0.96] | – | 98 |
| smat | grok-4 | 0.936 | 0.933 [0.89, 0.97] | – | 98 |
| smat | llama-3.3-70b | 0.806 | 0.803 [0.74, 0.86] | – | 98 |
| suc | claude-opus-5 | 0.987 | 0.988 [0.96, 1.00] | – | 99 |
| suc | claude-sonnet-5 | 0.911 | 0.908 [0.86, 0.95] | – | 99 |
| suc | deepseek-chat | 0.858 | 0.858 [0.79, 0.91] | – | 99 |
| suc | deepseek-r1 | 0.942 | 0.939 [0.89, 0.98] | – | 99 |
| suc | gemini-3.1-pro | 0.945 | 0.939 [0.90, 0.98] | – | 99 |
| suc | gemini-3.8-flash | 0.977 | 0.978 [0.95, 1.00] | – | 99 |
| suc | gpt-5.4-mini | 0.914 | 0.910 [0.86, 0.96] | – | 99 |
| suc | gpt-5.5 | 0.943 | 0.938 [0.89, 0.98] | – | 99 |
| suc | gpt-oss-120b | 0.932 | 0.930 [0.88, 0.97] | – | 99 |
| suc | grok-4 | 0.943 | 0.938 [0.90, 0.98] | – | 99 |
| suc | llama-3.3-70b | 0.740 | 0.738 [0.66, 0.81] | – | 99 |
| tab_fact | claude-opus-5 | 0.660 | 0.667 [0.57, 0.76] | 0.67 → 0.70 [0.59, 0.78] | 99 |
| tab_fact | claude-sonnet-5 | 0.740 | 0.733 [0.64, 0.82] | 0.70 → 0.71 [0.59, 0.81] | 99 |
| tab_fact | deepseek-chat | 0.840 | 0.826 [0.74, 0.90] | 0.79 → 0.79 [0.68, 0.88] | 99 |
| tab_fact | deepseek-r1 | 0.770 | 0.763 [0.67, 0.85] | 0.73 → 0.74 [0.62, 0.84] | 99 |
| tab_fact | gemini-3.1-pro | 0.830 | 0.818 [0.75, 0.90] | 0.78 → 0.79 [0.67, 0.88] | 99 |
| tab_fact | gemini-3.8-flash | 0.860 | 0.848 [0.77, 0.91] | 0.82 → 0.82 [0.72, 0.90] | 99 |
| tab_fact | gpt-5.4-mini | 0.820 | 0.808 [0.73, 0.89] | 0.77 → 0.77 [0.65, 0.86] | 99 |
| tab_fact | gpt-5.5 | 0.840 | 0.829 [0.75, 0.90] | 0.80 → 0.80 [0.70, 0.89] | 99 |
| tab_fact | gpt-oss-120b | 0.830 | 0.815 [0.74, 0.89] | 0.77 → 0.77 [0.65, 0.87] | 99 |
| tab_fact | grok-4 | 0.850 | 0.839 [0.76, 0.91] | 0.81 → 0.81 [0.71, 0.90] | 99 |
| tab_fact | llama-3.3-70b | 0.780 | 0.769 [0.68, 0.85] | 0.72 → 0.73 [0.62, 0.83] | 99 |
| tabis | claude-opus-5 | 0.960 | 0.964 [0.92, 0.99] | – | 77 |
| tabis | claude-sonnet-5 | 0.920 | 0.917 [0.85, 0.97] | – | 77 |
| tabis | deepseek-chat | 0.770 | 0.710 [0.60, 0.81] | – | 77 |
| tabis | deepseek-r1 | 0.970 | 0.982 [0.96, 1.00] | – | 77 |
| tabis | gemini-3.1-pro | 0.950 | 0.970 [0.94, 0.99] | – | 77 |
| tabis | gemini-3.8-flash | 0.950 | 0.970 [0.94, 0.99] | – | 77 |
| tabis | gpt-5.4-mini | 0.900 | 0.905 [0.84, 0.96] | – | 77 |
| tabis | gpt-5.5 | 0.960 | 0.976 [0.95, 0.99] | – | 77 |
| tabis | gpt-oss-120b | 0.920 | 0.951 [0.92, 0.98] | – | 77 |
| tabis | grok-4 | 0.980 | 0.988 [0.97, 1.00] | – | 77 |
| tabis | llama-3.3-70b | 0.820 | 0.821 [0.73, 0.90] | – | 77 |
| tablebench | claude-opus-5 | 0.846 | 0.846 [0.78, 0.91] | – | 89 |
| tablebench | claude-sonnet-5 | 0.877 | 0.875 [0.81, 0.93] | – | 89 |
| tablebench | deepseek-chat | 0.833 | 0.844 [0.78, 0.90] | – | 89 |
| tablebench | deepseek-r1 | 0.793 | 0.801 [0.72, 0.87] | – | 89 |
| tablebench | gemini-3.1-pro | 0.858 | 0.853 [0.78, 0.92] | – | 89 |
| tablebench | gemini-3.8-flash | 0.835 | 0.833 [0.76, 0.90] | – | 89 |
| tablebench | gpt-5.4-mini | 0.841 | 0.835 [0.76, 0.90] | – | 89 |
| tablebench | gpt-5.5 | 0.852 | 0.850 [0.78, 0.92] | – | 89 |
| tablebench | gpt-oss-120b | 0.813 | 0.808 [0.74, 0.88] | – | 89 |
| tablebench | grok-4 | 0.839 | 0.837 [0.76, 0.90] | – | 89 |
| tablebench | llama-3.3-70b | 0.660 | 0.641 [0.55, 0.72] | – | 89 |
| tableeval | claude-opus-5 | 0.765 | 0.784 [0.69, 0.87] | – | 70 |
| tableeval | claude-sonnet-5 | 0.733 | 0.764 [0.66, 0.85] | – | 70 |
| tableeval | deepseek-chat | 0.711 | 0.708 [0.61, 0.80] | – | 70 |
| tableeval | deepseek-r1 | 0.773 | 0.760 [0.66, 0.86] | – | 70 |
| tableeval | gemini-3.1-pro | 0.790 | 0.794 [0.70, 0.88] | – | 70 |
| tableeval | gemini-3.8-flash | 0.791 | 0.805 [0.71, 0.89] | – | 70 |
| tableeval | gpt-5.4-mini | 0.742 | 0.751 [0.65, 0.84] | – | 70 |
| tableeval | gpt-5.5 | 0.784 | 0.794 [0.69, 0.88] | – | 70 |
| tableeval | gpt-oss-120b | 0.773 | 0.774 [0.67, 0.86] | – | 70 |
| tableeval | grok-4 | 0.802 | 0.785 [0.69, 0.88] | – | 70 |
| tableeval | llama-3.3-70b | 0.636 | 0.618 [0.51, 0.72] | – | 70 |
| tat_qa | claude-opus-5 | 0.861 | 0.846 [0.77, 0.91] | – | 61 |
| tat_qa | claude-sonnet-5 | 0.845 | 0.845 [0.78, 0.91] | – | 61 |
| tat_qa | deepseek-chat | 0.806 | 0.774 [0.68, 0.86] | – | 61 |
| tat_qa | deepseek-r1 | 0.815 | 0.780 [0.70, 0.86] | – | 61 |
| tat_qa | gemini-3.1-pro | 0.802 | 0.745 [0.65, 0.83] | – | 61 |
| tat_qa | gemini-3.8-flash | 0.829 | 0.815 [0.73, 0.89] | – | 61 |
| tat_qa | gpt-5.4-mini | 0.789 | 0.719 [0.63, 0.81] | – | 61 |
| tat_qa | gpt-5.5 | 0.789 | 0.748 [0.67, 0.83] | – | 61 |
| tat_qa | gpt-oss-120b | 0.765 | 0.684 [0.59, 0.78] | – | 61 |
| tat_qa | grok-4 | 0.791 | 0.710 [0.62, 0.80] | – | 61 |
| tat_qa | llama-3.3-70b | 0.752 | 0.679 [0.57, 0.78] | – | 61 |
| tpcdi_cells | claude-opus-5 | 0.462 | 0.465 [0.38, 0.55] | – | 95 |
| tpcdi_cells | claude-sonnet-5 | 0.462 | 0.465 [0.38, 0.56] | – | 95 |
| tpcdi_cells | deepseek-chat | 0.462 | 0.465 [0.38, 0.56] | – | 95 |
| tpcdi_cells | deepseek-r1 | 0.462 | 0.466 [0.37, 0.55] | – | 95 |
| tpcdi_cells | gemini-3.1-pro | 0.462 | 0.465 [0.37, 0.55] | – | 95 |
| tpcdi_cells | gemini-3.8-flash | 0.462 | 0.465 [0.37, 0.56] | – | 95 |
| tpcdi_cells | gpt-5.4-mini | 0.455 | 0.458 [0.37, 0.54] | – | 95 |
| tpcdi_cells | gpt-5.5 | 0.462 | 0.466 [0.38, 0.56] | – | 95 |
| tpcdi_cells | gpt-oss-120b | 0.442 | 0.453 [0.36, 0.53] | – | 95 |
| tpcdi_cells | grok-4 | 0.447 | 0.456 [0.37, 0.54] | – | 95 |
| tpcdi_cells | llama-3.3-70b | 0.442 | 0.453 [0.37, 0.54] | – | 95 |
| valentine | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | claude-sonnet-5 | 0.994 | 0.989 [0.97, 1.00] | – | 82 |
| valentine | deepseek-chat | 0.979 | 0.967 [0.93, 1.00] | – | 82 |
| valentine | deepseek-r1 | 0.990 | 0.986 [0.96, 1.00] | – | 82 |
| valentine | gemini-3.1-pro | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | gemini-3.8-flash | 0.970 | 0.988 [0.97, 1.00] | – | 82 |
| valentine | gpt-5.4-mini | 0.985 | 0.978 [0.94, 1.00] | – | 82 |
| valentine | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | gpt-oss-120b | 0.979 | 0.971 [0.93, 1.00] | – | 82 |
| valentine | grok-4 | 0.973 | 0.957 [0.91, 1.00] | – | 82 |
| valentine | llama-3.3-70b | 0.970 | 0.958 [0.92, 0.99] | – | 82 |
| walmart_amazon | claude-opus-5 | 0.980 | 0.982 [0.95, 1.00] | 0.98 → 0.91 [0.77, 1.00] | 71 |
| walmart_amazon | claude-sonnet-5 | 0.950 | 0.962 [0.91, 1.00] | 0.94 → 0.82 [0.64, 0.98] | 71 |
| walmart_amazon | deepseek-chat | 0.950 | 0.962 [0.91, 1.00] | 0.94 → 0.82 [0.66, 0.98] | 71 |
| walmart_amazon | deepseek-r1 | 0.960 | 0.978 [0.94, 1.00] | 0.95 → 0.89 [0.73, 0.99] | 71 |
| walmart_amazon | gemini-3.1-pro | 0.970 | 0.967 [0.92, 1.00] | 0.96 → 0.85 [0.67, 1.00] | 71 |
| walmart_amazon | gemini-3.8-flash | 0.990 | 0.998 [0.99, 1.00] | 0.99 → 0.99 [0.95, 1.00] | 71 |
| walmart_amazon | gpt-5.4-mini | 0.950 | 0.975 [0.94, 1.00] | 0.94 → 0.87 [0.71, 0.98] | 71 |
| walmart_amazon | gpt-5.5 | 0.970 | 0.967 [0.92, 1.00] | 0.96 → 0.85 [0.68, 1.00] | 71 |
| walmart_amazon | gpt-oss-120b | 0.940 | 0.973 [0.94, 1.00] | 0.92 → 0.86 [0.69, 0.97] | 71 |
| walmart_amazon | grok-4 | 0.960 | 0.978 [0.94, 1.00] | 0.95 → 0.89 [0.73, 0.99] | 71 |
| walmart_amazon | llama-3.3-70b | 0.930 | 0.971 [0.93, 0.99] | 0.91 → 0.85 [0.70, 0.97] | 71 |
| wdc_lspc | claude-opus-5 | 0.990 | 0.996 [0.99, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 75 |
| wdc_lspc | claude-sonnet-5 | 0.980 | 0.992 [0.98, 1.00] | 0.98 → 0.98 [0.96, 1.00] | 75 |
| wdc_lspc | deepseek-chat | 0.960 | 0.940 [0.88, 0.99] | 0.96 → 0.90 [0.78, 0.99] | 75 |
| wdc_lspc | deepseek-r1 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 75 |
| wdc_lspc | gemini-3.1-pro | 0.980 | 0.992 [0.98, 1.00] | 0.98 → 0.98 [0.96, 1.00] | 75 |
| wdc_lspc | gemini-3.8-flash | 0.980 | 0.992 [0.98, 1.00] | 0.98 → 0.98 [0.96, 1.00] | 75 |
| wdc_lspc | gpt-5.4-mini | 0.970 | 0.986 [0.97, 1.00] | 0.97 → 0.97 [0.94, 1.00] | 75 |
| wdc_lspc | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 75 |
| wdc_lspc | gpt-oss-120b | 0.980 | 0.990 [0.98, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 75 |
| wdc_lspc | grok-4 | 1.000 | 1.000 [1.00, 1.00] | 1.00 → 1.00 [1.00, 1.00] | 75 |
| wdc_lspc | llama-3.3-70b | 0.960 | 0.940 [0.87, 0.99] | 0.96 → 0.90 [0.78, 0.99] | 75 |
| wdc_products | claude-opus-5 | 0.980 | 0.990 [0.98, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 77 |
| wdc_products | claude-sonnet-5 | 0.970 | 0.986 [0.97, 1.00] | 0.97 → 0.97 [0.94, 1.00] | 77 |
| wdc_products | deepseek-chat | 0.970 | 0.977 [0.94, 1.00] | 0.97 → 0.96 [0.90, 1.00] | 77 |
| wdc_products | deepseek-r1 | 0.980 | 0.990 [0.97, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 77 |
| wdc_products | gemini-3.1-pro | 0.980 | 0.990 [0.97, 1.00] | 0.98 → 0.98 [0.95, 1.00] | 77 |
| wdc_products | gemini-3.8-flash | 0.990 | 0.995 [0.98, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 77 |
| wdc_products | gpt-5.4-mini | 0.970 | 0.986 [0.97, 1.00] | 0.97 → 0.97 [0.93, 1.00] | 77 |
| wdc_products | gpt-5.5 | 0.980 | 0.979 [0.94, 1.00] | 0.98 → 0.96 [0.89, 1.00] | 77 |
| wdc_products | gpt-oss-120b | 0.980 | 0.979 [0.94, 1.00] | 0.98 → 0.96 [0.90, 1.00] | 77 |
| wdc_products | grok-4 | 0.990 | 0.995 [0.98, 1.00] | 0.99 → 0.99 [0.97, 1.00] | 77 |
| wdc_products | llama-3.3-70b | 0.970 | 0.977 [0.94, 1.00] | 0.97 → 0.96 [0.90, 1.00] | 77 |
| wikitablequestions | claude-opus-5 | 0.879 | 0.878 [0.81, 0.93] | – | 98 |
| wikitablequestions | claude-sonnet-5 | 0.863 | 0.863 [0.80, 0.93] | – | 98 |
| wikitablequestions | deepseek-chat | 0.843 | 0.842 [0.77, 0.90] | – | 98 |
| wikitablequestions | deepseek-r1 | 0.846 | 0.844 [0.78, 0.91] | – | 98 |
| wikitablequestions | gemini-3.1-pro | 0.855 | 0.855 [0.79, 0.91] | – | 98 |
| wikitablequestions | gemini-3.8-flash | 0.881 | 0.881 [0.82, 0.94] | – | 98 |
| wikitablequestions | gpt-5.4-mini | 0.842 | 0.839 [0.77, 0.90] | – | 98 |
| wikitablequestions | gpt-5.5 | 0.865 | 0.862 [0.80, 0.92] | – | 98 |
| wikitablequestions | gpt-oss-120b | 0.824 | 0.821 [0.75, 0.89] | – | 98 |
| wikitablequestions | grok-4 | 0.867 | 0.864 [0.80, 0.92] | – | 98 |
| wikitablequestions | llama-3.3-70b | 0.749 | 0.747 [0.67, 0.82] | – | 98 |

## 8. Dataset diagnostics

| dataset | family | mean score | spread across models | self-stability τ | mean τ to other datasets | floor | ceiling | exclude from objective |
|---|---|---|---|---|---|---|---|---|
| abt_buy | EM | 0.971 | 0.060 | 0.75 | +0.35 | False | False | False |
| alaska_camera | EM | 0.945 | 0.190 | 0.92 | -0.20 | False | False | False |
| alaska_schema | SM | 0.929 | 0.118 | 0.68 | -0.03 | False | False | False |
| amazon_google | EM | 0.935 | 0.100 | 0.68 | +0.01 | False | False | False |
| bird | TQA | 0.190 | 0.209 | 0.83 | +0.30 | False | False | False |
| dblp_acm | EM | 0.987 | 0.090 | 0.88 | +0.33 | False | False | False |
| dblp_scholar | EM | 0.948 | 0.060 | 0.71 | -0.02 | False | False | False |
| fetaqa | TQA | 0.387 | 0.192 | 0.91 | +0.26 | False | False | False |
| fintagging | SM | 0.883 | 0.051 | 0.65 | +0.29 | False | False | False |
| hitab | TQA | 0.772 | 0.068 | 0.57 | -0.18 | False | False | False |
| machamp | EM | 0.887 | 0.070 | 0.58 | +0.37 | False | False | False |
| magneto_gdc | SM | 0.937 | 0.225 | 0.68 | +0.25 | False | False | False |
| mmtu | TQA | 0.873 | 0.110 | 0.77 | +0.28 | False | False | False |
| officeqa | FIN | 0.130 | 0.124 | 0.86 | +0.29 | False | False | False |
| officeqa_pro_v2 | FIN | 0.142 | 0.220 | 0.78 | +0.27 | False | False | False |
| opensanctions_pairs | EM | 0.835 | 0.240 | 0.90 | +0.04 | False | False | False |
| papadakis_dn | EM | 0.940 | 0.030 | 0.74 | +0.03 | False | False | False |
| realhitbench | TQA | 0.675 | 0.143 | 0.78 | +0.33 | False | False | False |
| smat | SM | 0.915 | 0.150 | 0.71 | +0.18 | False | False | False |
| suc | TQA | 0.917 | 0.246 | 0.82 | +0.29 | False | False | False |
| tab_fact | TQA | 0.802 | 0.200 | 0.83 | +0.02 | False | False | False |
| tabis | TQA | 0.918 | 0.210 | 0.84 | +0.25 | False | False | False |
| tablebench | TQA | 0.822 | 0.218 | 0.66 | +0.22 | False | False | False |
| tableeval | TQA | 0.755 | 0.166 | 0.74 | +0.17 | False | False | False |
| tat_qa | FIN | 0.804 | 0.109 | 0.76 | +0.25 | False | False | False |
| tpcdi_cells | SM | 0.456 | 0.020 | 0.78 | +0.31 | False | False | False |
| valentine | SM | 0.985 | 0.030 | 0.72 | +0.23 | False | True | True |
| walmart_amazon | EM | 0.959 | 0.060 | 0.76 | +0.35 | False | False | False |
| wdc_lspc | EM | 0.982 | 0.040 | 0.79 | +0.26 | False | True | True |
| wdc_products | EM | 0.978 | 0.020 | 0.62 | +0.19 | False | True | True |
| wikitablequestions | TQA | 0.847 | 0.132 | 0.73 | +0.35 | False | False | False |

Figure: `diagnostics/fig_dataset_tau` (pairwise τ between dataset rankings under v1).

## 9. What this supports, and what it does not

* Supported: over every step-0.05 weighting of v1's four ingredients, v1 sits at rank 1602 of 1,771 on the agreement objective, and the honest (out-of-bag) advantage of the best weighting over v1 is -0.007 with a confidence interval that includes zero. The plateau of statistically equivalent weightings covers 99 % of the lattice.
* Correctness (anchors): v1 ρ 0.878 vs best-J ρ 0.876 vs exact match ρ 0.828; J and ρ correlate -0.23 across the lattice, so agreement and correctness do not pull the same way, and the Pareto knee is the defensible compromise.
* Not supported: any rank claim below first place with 11 models (attainable τ values: [-1.0, -0.9636, -0.9273, -0.8909, -0.8545, -0.8182, -0.7818, -0.7455, -0.7091, -0.6727, -0.6364, -0.6, -0.5636, -0.5273, -0.4909, -0.4545, -0.4182, -0.3818, -0.3455, -0.3091, -0.2727, -0.2364, -0.2, -0.1636, -0.1273, -0.0909, -0.0545, -0.0182, 0.0182, 0.0545, 0.0909, 0.1273, 0.1636, 0.2, 0.2364, 0.2727, 0.3091, 0.3455, 0.3818, 0.4182, 0.4545, 0.4909, 0.5273, 0.5636, 0.6, 0.6364, 0.6727, 0.7091, 0.7455, 0.7818, 0.8182, 0.8545, 0.8909, 0.9273, 0.9636, 1.0]); any claim about accuracy from J alone; transfer to unseen task families until the 30-dataset run exists.
* Next: the same pipeline on the 30-dataset, 12-model run; human labels on 300 answers to replace the synthetic anchors in section 5.

## 10. Files

`grid_exhaustive.csv` (all weightings, every term, per-dataset τ, pooled ranks); `best.json`; `designs.csv` / `designs_summary.json`; `selection/` (nested.json, nested_draws.npz, plateau.csv, lodo.csv, lofo.csv, per_family.json, sensitivity.json); `anchors/` (anchor_components.csv, correctness.csv, correctness.json); `leaderboards/<rule>/` (leaderboard.md/csv, params.json with BT strengths + SE, Kemeny cost, Copeland, Borda, pairwise wins; bootstrap.npz; significance.json; pairwise_item_tests.csv; per_dataset_mean/se.csv; table.tex); `leaderboards/rule_agreement.csv`, `summary.json`; `diagnostics/`; `run_manifest.json`; `coverage.json`.
