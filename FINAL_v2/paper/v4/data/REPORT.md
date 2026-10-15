# v4 report: nine-component composite, three sampled designs, honest selection

Generated 2026-09-27 14:00. 31 datasets × 10 models (abt_buy 100, alaska_camera 100, alaska_schema 93, amazon_google 100, bird 100, dblp_acm 100, dblp_scholar 100, fetaqa 100, fintagging 100, hitab 100, machamp 100, magneto_gdc 100, mmtu 100, officeqa 100, officeqa_pro_v2 90, opensanctions_pairs 100, papadakis_dn 100, realhitbench 100, smat 100, suc 100, tab_fact 100, tabis 100, tablebench 100, tableeval 100, tat_qa 100, tpcdi_cells 100, valentine 100, walmart_amazon 100, wdc_lspc 100, wdc_products 100, wikitablequestions 100). Candidates: 100 per design × 3 designs (Dirichlet-snapped, Latin hypercube, uniform lattice) + 5 baselines = 305 on a lattice of 3,108,105 points. Components: em, num_tol, num_decay, tok_prec, tok_rec, tok_f1, edit_sim, rouge_l, jaccard.

## 1. Search and designs

* Best: num_tol 1.00 (design num_tol_only), J = 0.442, τ_native 0.97; under Kemeny 0.442, Copeland 0.444, BT 0.426.
* Best per design: dirichlet 0.427 (em 0.10, num_tol 0.30, num_decay 0.10, tok_prec 0.20, tok_rec 0.05, tok_f1 0.05, rouge_l 0.10, jaccard 0.10); lhs 0.431 (num_tol 0.35, tok_prec 0.25, tok_rec 0.20, tok_f1 0.05, edit_sim 0.05, rouge_l 0.05, jaccard 0.05); uniform_lattice 0.434 (em 0.65, num_tol 0.15, num_decay 0.10, edit_sim 0.10).
* Baselines: em_only J 0.439 (rank 2); f1_only J 0.411 (rank 217); num_tol_only J 0.442 (rank 1); uniform J 0.412 (rank 189); v1_rubric J 0.404 (rank 295). The v1 rubric is beaten by 294 candidates and tied by 0.
* Top 5: #1 num_tol 1.00 (num_tol_only, J 0.442); #2 em 1.00 (em_only, J 0.439); #3 em 0.65, num_tol 0.15, num_decay 0.10, edit_sim 0.10 (uniform_lattice, J 0.434); #4 em 0.20, num_tol 0.30, tok_prec 0.10, tok_rec 0.25, edit_sim 0.05, rouge_l 0.05, jaccard 0.05 (uniform_lattice, J 0.433); #5 em 0.40, num_tol 0.10, num_decay 0.15, tok_prec 0.10, edit_sim 0.10, rouge_l 0.15 (uniform_lattice, J 0.432).

| design (20 seeds) | best J (mean ± sd) | best J (max) | mean J of design | regret vs best over all (mean / max) | min pairwise L1 | mean nearest L1 | centred L2 discrepancy | share with a zero weight |
|---|---|---|---|---|---|---|---|---|
| dirichlet_lattice | 0.432 ± 0.003 | 0.439 | 0.415 | 0.010 / 0.014 | 0.20 | 0.40 | 2.674 | 0.88 |
| lhs_simplex | 0.431 ± 0.002 | 0.437 | 0.415 | 0.011 / 0.014 | 0.21 | 0.41 | 2.672 | 0.88 |
| uniform_lattice | 0.434 ± 0.003 | 0.442 | 0.415 | 0.008 / 0.013 | 0.23 | 0.47 | 2.590 | 0.97 |

## 2. Honest selection

* Nested bootstrap (B = 1000): in-bag J of the selected candidate 0.387, out-of-bag 0.337 (optimism gap 0.050); v1 rubric out-of-bag 0.339.
* Selected vs v1 rubric out of bag: -0.002 [-0.033, +0.024], one-sided p = 0.544.
* Plateau (paired p > .05): 305 of 305; practical plateau (within 0.02): 303, v1 rubric inside: True. 204 distinct candidates selected; mean selected weights em 0.18, num_tol 0.23, num_decay 0.06, tok_prec 0.08, tok_rec 0.10, tok_f1 0.08, edit_sim 0.05, rouge_l 0.13, jaccard 0.08.

## 3. Transfer

| held out | J on rest | held-out weights | τ held-out: held-out weights | full best | v1 rubric |
|---|---|---|---|---|---|
| abt_buy | 0.430 | num_tol 1.00 | +0.81 | +0.81 | +0.81 |
| alaska_camera | 0.471 | num_tol 1.00 | -0.44 | -0.44 | -0.44 |
| alaska_schema | 0.453 | em 1.00 | +0.02 | +0.02 | -0.20 |
| amazon_google | 0.457 | num_tol 1.00 | -0.02 | -0.02 | -0.02 |
| bird | 0.433 | num_tol 1.00 | +0.70 | +0.70 | +0.54 |
| dblp_acm | 0.433 | num_tol 1.00 | +0.58 | +0.58 | +0.64 |
| dblp_scholar | 0.457 | num_tol 1.00 | +0.00 | +0.00 | +0.00 |
| fetaqa | 0.434 | num_tol 1.00 | +0.51 | +0.51 | +0.42 |
| fintagging | 0.431 | em 0.20, num_tol 0.30, tok_prec 0.10, tok_rec 0.25, edit_sim 0.05, rouge_l 0.05, jaccard 0.05 | +0.51 | +0.79 | +0.47 |
| hitab | 0.458 | num_tol 1.00 | -0.21 | -0.21 | -0.31 |
| machamp | 0.432 | num_tol 1.00 | +0.74 | +0.74 | +0.74 |
| magneto_gdc | 0.439 | num_tol 1.00 | +0.54 | +0.54 | +0.54 |
| mmtu | 0.434 | em 1.00 | +0.56 | +0.61 | +0.56 |
| officeqa | 0.438 | em 1.00 | +0.55 | +0.61 | +0.56 |
| officeqa_pro_v2 | 0.436 | num_tol 1.00 | +0.63 | +0.63 | +0.56 |
| opensanctions_pairs | 0.451 | em 1.00 | +0.09 | +0.04 | +0.04 |
| papadakis_dn | 0.452 | em 1.00 | +0.03 | +0.03 | +0.08 |
| realhitbench | 0.431 | num_tol 1.00 | +0.76 | +0.76 | +0.60 |
| smat | 0.444 | em 1.00 | +0.25 | +0.25 | +0.38 |
| suc | 0.434 | num_tol 1.00 | +0.69 | +0.69 | +0.58 |
| tab_fact | 0.455 | num_tol 1.00 | -0.09 | -0.09 | -0.04 |
| tabis | 0.441 | num_tol 1.00 | +0.48 | +0.48 | +0.43 |
| tablebench | 0.437 | em 1.00 | +0.48 | +0.55 | +0.51 |
| tableeval | 0.447 | num_tol 1.00 | +0.28 | +0.28 | +0.33 |
| tat_qa | 0.439 | num_tol 1.00 | +0.27 | +0.27 | +0.54 |
| tpcdi_cells | 0.438 | num_tol 1.00 | +0.55 | +0.55 | +0.54 |
| valentine | 0.437 | num_tol 1.00 | +0.60 | +0.60 | +0.48 |
| walmart_amazon | 0.431 | num_tol 1.00 | +0.77 | +0.77 | +0.72 |
| wdc_lspc | 0.441 | num_tol 1.00 | +0.48 | +0.48 | +0.44 |
| wdc_products | 0.444 | num_tol 1.00 | +0.37 | +0.37 | +0.37 |
| wikitablequestions | 0.428 | em 1.00 | +0.78 | +0.92 | +0.78 |

Mean held-out τ: held-out weights +0.39, full best +0.41, v1 rubric +0.37.

| held-out family | J on rest | held-out weights | τ: held-out weights | full best | v1 rubric |
|---|---|---|---|---|---|
| EM | 0.505 | num_tol 1.00 | +0.33 | +0.33 | +0.30 |
| SM | 0.430 | em 0.20, num_tol 0.30, tok_prec 0.10, tok_rec 0.25, edit_sim 0.05, rouge_l 0.05, jaccard 0.05 | +0.36 | +0.43 | +0.25 |
| TQA | 0.427 | em 0.10, num_tol 0.30, num_decay 0.10, tok_prec 0.20, tok_rec 0.05, tok_f1 0.05, rouge_l 0.10, jaccard 0.10 | +0.40 | +0.45 | +0.38 |
| FIN | 0.429 | num_tol 1.00 | +0.46 | +0.46 | +0.51 |

Per-family best: EM: num_tol 1.00 (J 0.361; global best 0.361); SM: num_tol 1.00 (J 0.580; global best 0.580); TQA: em 0.50, num_decay 0.05, tok_prec 0.15, tok_rec 0.05, tok_f1 0.10, edit_sim 0.05, rouge_l 0.10 (J 0.513; global best 0.512); FIN: em 0.10, num_tol 0.10, tok_prec 0.20, tok_rec 0.35, tok_f1 0.10, rouge_l 0.15 (J 0.834; global best 0.619).

## 4. Correctness on anchors

31,380 anchors (9,881 correct, 7,430 wrong).

| rule | weights | J | ρ | per-dataset ρ | AUC | wrong mean | hedge gap | rank by J | rank by ρ |
|---|---|---|---|---|---|---|---|---|---|
| v1_rubric | num_decay 0.35, tok_prec 0.15, tok_rec 0.15, tok_f1 0.35 | 0.404 | 0.878 | 0.868 | 0.994 | 0.034 | -0.51 | 295 | 112 |
| best_J | num_tol 1.00 | 0.442 | 0.796 | 0.808 | 0.989 | 0.022 | -0.59 | 1 | 305 |
| best_rho | em 0.20, num_decay 0.25, tok_prec 0.25, tok_rec 0.05, tok_f1 0.05, edit_sim 0.15, rouge_l 0.05 | 0.415 | 0.884 | 0.865 | 0.994 | 0.053 | -0.61 | 130 | 1 |
| pareto_knee | em 0.40, num_tol 0.10, num_decay 0.15, tok_prec 0.10, edit_sim 0.10, rouge_l 0.15 | 0.432 | 0.884 | 0.865 | 0.994 | 0.039 | -0.66 | 5 | 5 |
| exact_match | – | – | 0.828 | 0.830 | 0.989 | 0.011 | -0.81 | – | – |

Spearman(J, ρ) across candidates: **-0.19**; Pareto front size 5.

## 5. Sensitivity

* v1_rubric: 32 one-step neighbours; J centre 0.404, min 0.401 / mean 0.406 / max 0.409; 72 % better.
* best: 8 one-step neighbours; J centre 0.442, min 0.425 / mean 0.430 / max 0.446; 12 % better.

## 6. Leaderboards (Bradley–Terry rank, Borda in brackets)

| rule | weights | claude-opus-5 | claude-sonnet-5 | deepseek-chat | deepseek-r1 | gemini-3.8-flash | gpt-5.4-mini | gpt-5.5 | gpt-oss-120b | grok-4 | llama-3.3-70b | Friedman p | Kendall's W | significant pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| em_only | em 1.00 | 1 (1) | 5 (4) | 8 (7) | 7 (6) | 3 (3) | 6 (8) | 2 (2) | 9 (9) | 4 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| v1_rubric | num_decay 0.35, tok_prec 0.15, tok_rec 0.15, tok_f1 0.35 | 2 (2) | 4 (4) | 7 (7) | 8 (6) | 1 (3) | 6 (8) | 3 (1) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top1 | num_tol 1.00 | 1 (1) | 5 (4) | 8 (8) | 7 (6) | 3 (3) | 6 (7) | 2 (2) | 9 (9) | 4 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, gpt-5.5 > deepseek-chat, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top2 | em 1.00 | 1 (1) | 5 (4) | 8 (7) | 7 (6) | 3 (3) | 6 (8) | 2 (2) | 9 (9) | 4 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top3 | em 0.65, num_tol 0.15, num_decay 0.10, edit_sim 0.10 | 2 (1) | 4 (4) | 7 (8) | 8 (6) | 1 (3) | 6 (7) | 3 (2) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, gpt-5.5 > deepseek-chat, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top4 | em 0.20, num_tol 0.30, tok_prec 0.10, tok_rec 0.25, edit_sim 0.05, rouge_l 0.05, jaccard 0.05 | 2 (1) | 5 (4) | 6 (7) | 8 (6) | 1 (3) | 7 (8) | 3 (2) | 9 (9) | 4 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top5 | em 0.40, num_tol 0.10, num_decay 0.15, tok_prec 0.10, edit_sim 0.10, rouge_l 0.15 | 2 (1) | 4 (4) | 7 (8) | 8 (6) | 1 (3) | 6 (7) | 3 (1) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| best_anchor | em 0.20, num_decay 0.25, tok_prec 0.25, tok_rec 0.05, tok_f1 0.05, edit_sim 0.15, rouge_l 0.05 | 2 (2) | 4 (4) | 7 (8) | 8 (6) | 1 (3) | 6 (7) | 3 (1) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| pareto_knee | em 0.40, num_tol 0.10, num_decay 0.15, tok_prec 0.10, edit_sim 0.10, rouge_l 0.15 | 2 (1) | 4 (4) | 7 (8) | 8 (6) | 1 (3) | 6 (7) | 3 (1) | 9 (9) | 5 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |

τ between BT rankings of the rules:

| | em_only | v1_rubric | top1 | top2 | top3 | top4 | top5 | best_anchor | pareto_knee |
|---|---|---|---|---|---|---|---|---|---|
| em_only | +1.00 | +0.82 | +1.00 | +1.00 | +0.82 | +0.82 | +0.82 | +0.82 | +0.82 |
| v1_rubric | +0.82 | +1.00 | +0.82 | +0.82 | +1.00 | +0.91 | +1.00 | +1.00 | +1.00 |
| top1 | +1.00 | +0.82 | +1.00 | +1.00 | +0.82 | +0.82 | +0.82 | +0.82 | +0.82 |
| top2 | +1.00 | +0.82 | +1.00 | +1.00 | +0.82 | +0.82 | +0.82 | +0.82 | +0.82 |
| top3 | +0.82 | +1.00 | +0.82 | +0.82 | +1.00 | +0.91 | +1.00 | +1.00 | +1.00 |
| top4 | +0.82 | +0.91 | +0.82 | +0.82 | +0.91 | +1.00 | +0.91 | +0.91 | +0.91 |
| top5 | +0.82 | +1.00 | +0.82 | +0.82 | +1.00 | +0.91 | +1.00 | +1.00 | +1.00 |
| best_anchor | +0.82 | +1.00 | +0.82 | +0.82 | +1.00 | +0.91 | +1.00 | +1.00 | +1.00 |
| pareto_knee | +0.82 | +1.00 | +0.82 | +0.82 | +1.00 | +0.91 | +1.00 | +1.00 | +1.00 |

## Official-split estimates under the v1 rubric

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

## 7. Dataset diagnostics

| dataset | family | mean | spread | self-stability τ | τ to others | exclude |
|---|---|---|---|---|---|---|
| abt_buy | EM | 0.970 | 0.060 | 0.73 | +0.36 | False |
| alaska_camera | EM | 0.958 | 0.180 | 0.92 | -0.22 | False |
| alaska_schema | SM | 0.928 | 0.118 | 0.67 | -0.04 | False |
| amazon_google | EM | 0.936 | 0.100 | 0.68 | -0.01 | False |
| bird | TQA | 0.187 | 0.209 | 0.82 | +0.31 | False |
| dblp_acm | EM | 0.986 | 0.090 | 0.88 | +0.35 | False |
| dblp_scholar | EM | 0.949 | 0.060 | 0.73 | -0.02 | False |
| fetaqa | TQA | 0.382 | 0.192 | 0.93 | +0.27 | False |
| fintagging | SM | 0.880 | 0.069 | 0.69 | +0.26 | False |
| hitab | TQA | 0.770 | 0.068 | 0.58 | -0.18 | False |
| machamp | EM | 0.887 | 0.070 | 0.60 | +0.38 | False |
| magneto_gdc | SM | 0.934 | 0.218 | 0.68 | +0.25 | False |
| mmtu | TQA | 0.867 | 0.110 | 0.76 | +0.30 | False |
| officeqa | FIN | 0.129 | 0.119 | 0.85 | +0.28 | False |
| officeqa_pro_v2 | FIN | 0.139 | 0.215 | 0.79 | +0.31 | False |
| opensanctions_pairs | EM | 0.821 | 0.210 | 0.89 | +0.03 | False |
| papadakis_dn | EM | 0.941 | 0.030 | 0.74 | +0.07 | False |
| realhitbench | TQA | 0.673 | 0.143 | 0.77 | +0.34 | False |
| smat | SM | 0.918 | 0.150 | 0.67 | +0.20 | False |
| suc | TQA | 0.914 | 0.246 | 0.85 | +0.29 | False |
| tab_fact | TQA | 0.798 | 0.200 | 0.84 | +0.01 | False |
| tabis | TQA | 0.915 | 0.210 | 0.85 | +0.22 | False |
| tablebench | TQA | 0.818 | 0.218 | 0.67 | +0.28 | False |
| tableeval | TQA | 0.749 | 0.166 | 0.78 | +0.20 | False |
| tat_qa | FIN | 0.803 | 0.109 | 0.76 | +0.26 | False |
| tpcdi_cells | SM | 0.456 | 0.020 | 0.78 | +0.30 | False |
| valentine | SM | 0.984 | 0.030 | 0.68 | +0.23 | True |
| walmart_amazon | EM | 0.958 | 0.060 | 0.76 | +0.36 | False |
| wdc_lspc | EM | 0.982 | 0.040 | 0.80 | +0.25 | True |
| wdc_products | EM | 0.978 | 0.020 | 0.64 | +0.18 | True |
| wikitablequestions | TQA | 0.846 | 0.132 | 0.74 | +0.35 | False |

## 8. Reading

* The three designs reach the same best J within noise (see the design table); the Latin hypercube design has the lowest discrepancy and the fewest zero weights, so it is the one to keep when a design is sampled.
* The honest advantage of the selected weighting over the v1 rubric is -0.002 with a CI that includes zero; the optimism gap 0.050 is the size of the winner's curse on this data.
* J and ρ correlate -0.19 across candidates: the agreement objective is not a proxy for correctness here; the anchor-optimal and Pareto-knee weightings are reported next to the J-optimal one.
* Files: grid_candidates.csv, best.json, designs.csv, selection/, anchors/, leaderboards/<rule>/ (params with BT SE, Kemeny cost, bootstrap draws, significance), diagnostics/, run_manifest.json.
