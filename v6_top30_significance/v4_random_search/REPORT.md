# v4 report: nine-component composite, three sampled designs, honest selection

Generated 2026-10-16 13:04. 31 datasets × 11 models (abt_buy 100, alaska_camera 100, alaska_schema 93, amazon_google 100, bird 100, dblp_acm 100, dblp_scholar 100, fetaqa 100, fintagging 100, hitab 100, machamp 100, magneto_gdc 100, mmtu 100, officeqa 100, officeqa_pro_v2 90, opensanctions_pairs 100, papadakis_dn 100, realhitbench 100, smat 100, suc 100, tab_fact 100, tabis 100, tablebench 100, tableeval 100, tat_qa 100, tpcdi_cells 100, valentine 100, walmart_amazon 100, wdc_lspc 100, wdc_products 100, wikitablequestions 100). Candidates: 100 per design × 3 designs (Dirichlet-snapped, Latin hypercube, uniform lattice) + 5 baselines = 305 on a lattice of 3,108,105 points. Components: em, num_tol, num_decay, tok_prec, tok_rec, tok_f1, edit_sim, rouge_l, jaccard.

## 1. Search and designs

* Best: em 1.00 (design em_only), J = 0.439, τ_native 0.92; under Kemeny 0.439, Copeland 0.452, BT 0.420.
* Best per design: dirichlet 0.432 (em 0.10, num_tol 0.30, num_decay 0.10, tok_prec 0.20, tok_rec 0.05, tok_f1 0.05, rouge_l 0.10, jaccard 0.10); lhs 0.433 (num_tol 0.35, tok_prec 0.25, tok_rec 0.20, tok_f1 0.05, edit_sim 0.05, rouge_l 0.05, jaccard 0.05); uniform_lattice 0.432 (em 0.55, num_tol 0.05, num_decay 0.15, tok_prec 0.05, rouge_l 0.05, jaccard 0.15).
* Baselines: em_only J 0.439 (rank 1); f1_only J 0.414 (rank 164); num_tol_only J 0.428 (rank 16); uniform J 0.420 (rank 92); v1_rubric J 0.399 (rank 298). The v1 rubric is beaten by 297 candidates and tied by 0.
* Top 5: #1 em 1.00 (em_only, J 0.439); #2 num_tol 0.35, tok_prec 0.25, tok_rec 0.20, tok_f1 0.05, edit_sim 0.05, rouge_l 0.05, jaccard 0.05 (lhs, J 0.433); #3 em 0.10, num_tol 0.30, num_decay 0.10, tok_prec 0.20, tok_rec 0.05, tok_f1 0.05, rouge_l 0.10, jaccard 0.10 (dirichlet, J 0.432); #4 em 0.55, num_tol 0.05, num_decay 0.15, tok_prec 0.05, rouge_l 0.05, jaccard 0.15 (uniform_lattice, J 0.432); #5 em 0.65, num_tol 0.15, num_decay 0.10, edit_sim 0.10 (uniform_lattice, J 0.432).

| design (20 seeds) | best J (mean ± sd) | best J (max) | mean J of design | regret vs best over all (mean / max) | min pairwise L1 | mean nearest L1 | centred L2 discrepancy | share with a zero weight |
|---|---|---|---|---|---|---|---|---|
| dirichlet_lattice | 0.432 ± 0.002 | 0.438 | 0.415 | 0.007 / 0.011 | 0.20 | 0.40 | 2.674 | 0.88 |
| lhs_simplex | 0.432 ± 0.002 | 0.437 | 0.415 | 0.007 / 0.012 | 0.21 | 0.41 | 2.672 | 0.88 |
| uniform_lattice | 0.434 ± 0.003 | 0.439 | 0.415 | 0.005 / 0.009 | 0.23 | 0.47 | 2.590 | 0.97 |

## 2. Honest selection

* Nested bootstrap (B = 1000): in-bag J of the selected candidate 0.380, out-of-bag 0.330 (optimism gap 0.050); v1 rubric out-of-bag 0.333.
* Selected vs v1 rubric out of bag: -0.003 [-0.029, +0.020], one-sided p = 0.555.
* Plateau (paired p > .05): 305 of 305; practical plateau (within 0.02): 305, v1 rubric inside: True. 211 distinct candidates selected; mean selected weights em 0.22, num_tol 0.25, num_decay 0.08, tok_prec 0.07, tok_rec 0.11, tok_f1 0.07, edit_sim 0.04, rouge_l 0.08, jaccard 0.07.

## 3. Transfer

| held out | J on rest | held-out weights | τ held-out: held-out weights | full best | v1 rubric |
|---|---|---|---|---|---|
| abt_buy | 0.425 | num_tol 0.40, tok_prec 0.05, tok_rec 0.15, tok_f1 0.10, edit_sim 0.10, rouge_l 0.20 | +0.68 | +0.68 | +0.68 |
| alaska_camera | 0.460 | em 1.00 | -0.25 | -0.25 | -0.28 |
| alaska_schema | 0.449 | em 1.00 | +0.15 | +0.15 | -0.09 |
| amazon_google | 0.447 | em 1.00 | +0.14 | +0.14 | +0.10 |
| bird | 0.432 | em 1.00 | +0.66 | +0.66 | +0.62 |
| dblp_acm | 0.431 | num_tol 1.00 | +0.45 | +0.54 | +0.47 |
| dblp_scholar | 0.450 | em 1.00 | +0.13 | +0.13 | +0.04 |
| fetaqa | 0.433 | num_tol 0.40, tok_prec 0.05, tok_rec 0.15, tok_f1 0.10, edit_sim 0.10, rouge_l 0.20 | +0.35 | +0.63 | +0.31 |
| fintagging | 0.430 | em 1.00 | +0.71 | +0.71 | +0.49 |
| hitab | 0.454 | em 1.00 | +0.00 | +0.00 | -0.35 |
| machamp | 0.428 | em 1.00 | +0.80 | +0.80 | +0.76 |
| magneto_gdc | 0.434 | em 1.00 | +0.60 | +0.60 | +0.45 |
| mmtu | 0.437 | em 1.00 | +0.51 | +0.51 | +0.51 |
| officeqa | 0.434 | em 1.00 | +0.53 | +0.53 | +0.51 |
| officeqa_pro_v2 | 0.431 | num_tol 1.00 | +0.47 | +0.52 | +0.45 |
| opensanctions_pairs | 0.455 | em 1.00 | -0.02 | -0.02 | -0.07 |
| papadakis_dn | 0.451 | em 1.00 | +0.08 | +0.08 | +0.08 |
| realhitbench | 0.429 | em 0.30, num_tol 0.20, tok_prec 0.05, tok_rec 0.05, tok_f1 0.25, edit_sim 0.10, rouge_l 0.05 | +0.72 | +0.79 | +0.64 |
| smat | 0.444 | num_tol 1.00 | +0.31 | +0.33 | +0.42 |
| suc | 0.429 | em 1.00 | +0.54 | +0.54 | +0.40 |
| tab_fact | 0.454 | em 1.00 | +0.02 | +0.02 | -0.06 |
| tabis | 0.441 | em 1.00 | +0.42 | +0.42 | +0.39 |
| tablebench | 0.439 | em 1.00 | +0.46 | +0.46 | +0.48 |
| tableeval | 0.442 | em 1.00 | +0.36 | +0.36 | +0.24 |
| tat_qa | 0.437 | num_tol 1.00 | +0.22 | +0.60 | +0.53 |
| tpcdi_cells | 0.429 | em 0.65, num_tol 0.15, num_decay 0.10, edit_sim 0.10 | +0.52 | +0.56 | +0.55 |
| valentine | 0.437 | em 0.40, num_tol 0.20, num_decay 0.10, tok_f1 0.05, rouge_l 0.20, jaccard 0.05 | +0.40 | +0.41 | +0.34 |
| walmart_amazon | 0.427 | em 1.00 | +0.61 | +0.61 | +0.57 |
| wdc_lspc | 0.433 | em 1.00 | +0.42 | +0.42 | +0.42 |
| wdc_products | 0.442 | em 1.00 | +0.35 | +0.35 | +0.35 |
| wikitablequestions | 0.430 | em 1.00 | +0.72 | +0.72 | +0.67 |

Mean held-out τ: held-out weights +0.39, full best +0.42, v1 rubric +0.34.

| held-out family | J on rest | held-out weights | τ: held-out weights | full best | v1 rubric |
|---|---|---|---|---|---|
| EM | 0.494 | em 1.00 | +0.33 | +0.33 | +0.33 |
| SM | 0.428 | em 1.00 | +0.43 | +0.43 | +0.30 |
| TQA | 0.437 | em 0.05, num_tol 0.45, num_decay 0.05, tok_prec 0.20, rouge_l 0.05, jaccard 0.20 | +0.38 | +0.44 | +0.35 |
| FIN | 0.429 | num_tol 1.00 | +0.45 | +0.46 | +0.48 |

Per-family best: EM: em 1.00 (J 0.358; global best 0.358); SM: num_tol 0.15, num_decay 0.60, edit_sim 0.25 (J 0.580; global best 0.546); TQA: em 1.00 (J 0.512; global best 0.512); FIN: em 0.15, num_tol 0.05, num_decay 0.05, tok_prec 0.05, tok_rec 0.50, rouge_l 0.05, jaccard 0.15 (J 0.771; global best 0.706).

## 4. Correctness on anchors

31,380 anchors (9,881 correct, 7,430 wrong).

| rule | weights | J | ρ | per-dataset ρ | AUC | wrong mean | hedge gap | rank by J | rank by ρ |
|---|---|---|---|---|---|---|---|---|---|
| v1_rubric | num_decay 0.35, tok_prec 0.15, tok_rec 0.15, tok_f1 0.35 | 0.399 | 0.878 | 0.868 | 0.994 | 0.034 | -0.51 | 298 | 112 |
| best_J | em 1.00 | 0.439 | 0.828 | 0.830 | 0.989 | 0.011 | -0.81 | 1 | 304 |
| best_rho | em 0.20, num_decay 0.25, tok_prec 0.25, tok_rec 0.05, tok_f1 0.05, edit_sim 0.15, rouge_l 0.05 | 0.409 | 0.884 | 0.865 | 0.994 | 0.053 | -0.61 | 234 | 1 |
| pareto_knee | em 0.55, num_tol 0.05, num_decay 0.15, tok_prec 0.05, rouge_l 0.05, jaccard 0.15 | 0.432 | 0.882 | 0.872 | 0.994 | 0.020 | -0.70 | 4 | 21 |
| exact_match | – | – | 0.828 | 0.830 | 0.989 | 0.011 | -0.81 | – | – |

Spearman(J, ρ) across candidates: **-0.21**; Pareto front size 8.

## 5. Sensitivity

* v1_rubric: 32 one-step neighbours; J centre 0.399, min 0.394 / mean 0.403 / max 0.408; 81 % better.
* best: 8 one-step neighbours; J centre 0.439, min 0.422 / mean 0.429 / max 0.441; 12 % better.

## 6. Leaderboards (Bradley–Terry rank, Borda in brackets)

| rule | weights | claude-opus-5 | claude-sonnet-5 | deepseek-chat | deepseek-r1 | gemini-3.1-pro | gemini-3.8-flash | gpt-5.4-mini | gpt-5.5 | gpt-oss-120b | grok-4 | llama-3.3-70b | Friedman p | Kendall's W | significant pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| em_only | em 1.00 | 1 (1) | 6 (4) | 9 (7) | 5 (5) | 8 (8) | 3 (3) | 7 (9) | 2 (2) | 10 (10) | 4 (6) | 11 (11) | 0.000 | 0.28 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| v1_rubric | num_decay 0.35, tok_prec 0.15, tok_rec 0.15, tok_f1 0.35 | 2 (2) | 4 (4) | 9 (7) | 6 (5) | 8 (9) | 1 (3) | 7 (8) | 3 (1) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.26 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top1 | em 1.00 | 1 (1) | 6 (4) | 9 (7) | 5 (5) | 8 (8) | 3 (3) | 7 (9) | 2 (2) | 10 (10) | 4 (6) | 11 (11) | 0.000 | 0.28 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top2 | num_tol 0.35, tok_prec 0.25, tok_rec 0.20, tok_f1 0.05, edit_sim 0.05, rouge_l 0.05, jaccard 0.05 | 2 (1) | 4 (4) | 8 (7) | 6 (5) | 9 (8) | 1 (3) | 7 (9) | 3 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.28 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gemini-3.1-pro, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.5 > gpt-5.4-mini, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top3 | em 0.10, num_tol 0.30, num_decay 0.10, tok_prec 0.20, tok_rec 0.05, tok_f1 0.05, rouge_l 0.10, jaccard 0.10 | 2 (1) | 4 (4) | 9 (7) | 6 (5) | 8 (8) | 1 (3) | 7 (9) | 3 (1) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.28 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, gpt-5.5 > deepseek-chat, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gemini-3.1-pro, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top4 | em 0.55, num_tol 0.05, num_decay 0.15, tok_prec 0.05, rouge_l 0.05, jaccard 0.15 | 2 (1) | 4 (4) | 9 (7) | 6 (5) | 8 (8) | 1 (3) | 7 (9) | 3 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.29 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gemini-3.1-pro, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top5 | em 0.65, num_tol 0.15, num_decay 0.10, edit_sim 0.10 | 1 (1) | 4 (4) | 7 (8) | 8 (5) | 9 (9) | 2 (3) | 6 (7) | 3 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.29 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| best_anchor | em 0.20, num_decay 0.25, tok_prec 0.25, tok_rec 0.05, tok_f1 0.05, edit_sim 0.15, rouge_l 0.05 | 2 (2) | 4 (4) | 9 (9) | 7 (5) | 8 (8) | 1 (3) | 6 (7) | 3 (1) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.27 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| pareto_knee | em 0.55, num_tol 0.05, num_decay 0.15, tok_prec 0.05, rouge_l 0.05, jaccard 0.15 | 2 (1) | 4 (4) | 9 (7) | 6 (5) | 8 (8) | 1 (3) | 7 (9) | 3 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.29 | claude-opus-5 > gemini-3.1-pro, claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gemini-3.1-pro, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |

τ between BT rankings of the rules:

| | em_only | v1_rubric | top1 | top2 | top3 | top4 | top5 | best_anchor | pareto_knee |
|---|---|---|---|---|---|---|---|---|---|
| em_only | +1.00 | +0.85 | +1.00 | +0.82 | +0.85 | +0.85 | +0.78 | +0.82 | +0.85 |
| v1_rubric | +0.85 | +1.00 | +0.85 | +0.96 | +1.00 | +1.00 | +0.85 | +0.96 | +1.00 |
| top1 | +1.00 | +0.85 | +1.00 | +0.82 | +0.85 | +0.85 | +0.78 | +0.82 | +0.85 |
| top2 | +0.82 | +0.96 | +0.82 | +1.00 | +0.96 | +0.96 | +0.89 | +0.93 | +0.96 |
| top3 | +0.85 | +1.00 | +0.85 | +0.96 | +1.00 | +1.00 | +0.85 | +0.96 | +1.00 |
| top4 | +0.85 | +1.00 | +0.85 | +0.96 | +1.00 | +1.00 | +0.85 | +0.96 | +1.00 |
| top5 | +0.78 | +0.85 | +0.78 | +0.89 | +0.85 | +0.85 | +1.00 | +0.89 | +0.85 |
| best_anchor | +0.82 | +0.96 | +0.82 | +0.93 | +0.96 | +0.96 | +0.89 | +1.00 | +0.96 |
| pareto_knee | +0.85 | +1.00 | +0.85 | +0.96 | +1.00 | +1.00 | +0.85 | +0.96 | +1.00 |

## Official-split estimates under the v1 rubric

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
| alaska_schema | gemini-3.1-pro | 0.920 | 0.920 [0.87, 0.96] | – | 93 |
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
| bird | gemini-3.1-pro | 0.126 | 0.168 [0.09, 0.25] | – | 74 |
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
| fintagging | gemini-3.1-pro | 0.862 | 0.890 [0.81, 0.95] | – | 52 |
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
| hitab | gemini-3.1-pro | 0.772 | 0.779 [0.70, 0.85] | – | 95 |
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
| magneto_gdc | gemini-3.1-pro | 0.946 | 0.949 [0.91, 0.98] | – | 93 |
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
| mmtu | gemini-3.1-pro | 0.879 | 0.822 [0.73, 0.90] | – | 87 |
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
| officeqa | gemini-3.1-pro | 0.098 | n/c | – | 100 |
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
| realhitbench | gemini-3.1-pro | 0.647 | 0.650 [0.56, 0.74] | – | 98 |
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
| smat | gemini-3.1-pro | 0.876 | 0.874 [0.81, 0.93] | – | 98 |
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
| suc | gemini-3.1-pro | 0.943 | 0.938 [0.90, 0.98] | – | 99 |
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
| tabis | gemini-3.1-pro | 0.929 | 0.957 [0.92, 0.98] | – | 77 |
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
| tablebench | gemini-3.1-pro | 0.748 | 0.717 [0.62, 0.80] | – | 89 |
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
| tableeval | gemini-3.1-pro | 0.760 | 0.777 [0.68, 0.87] | – | 70 |
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
| tat_qa | gemini-3.1-pro | 0.799 | 0.740 [0.64, 0.83] | – | 61 |
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
| tpcdi_cells | gemini-3.1-pro | 0.459 | 0.463 [0.37, 0.55] | – | 95 |
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
| wdc_products | gemini-3.1-pro | 0.970 | 0.985 [0.97, 1.00] | 0.97 → 0.97 [0.94, 1.00] | 77 |
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
| wikitablequestions | gemini-3.1-pro | 0.858 | 0.858 [0.79, 0.91] | – | 98 |
| wikitablequestions | gemini-3.8-flash | 0.881 | 0.881 [0.82, 0.94] | – | 98 |
| wikitablequestions | gpt-5.4-mini | 0.842 | 0.839 [0.77, 0.90] | – | 98 |
| wikitablequestions | gpt-5.5 | 0.865 | 0.862 [0.80, 0.92] | – | 98 |
| wikitablequestions | gpt-oss-120b | 0.824 | 0.821 [0.75, 0.89] | – | 98 |
| wikitablequestions | grok-4 | 0.867 | 0.864 [0.80, 0.92] | – | 98 |
| wikitablequestions | llama-3.3-70b | 0.749 | 0.747 [0.67, 0.82] | – | 98 |

## 7. Dataset diagnostics

| dataset | family | mean | spread | self-stability τ | τ to others | exclude |
|---|---|---|---|---|---|---|
| abt_buy | EM | 0.971 | 0.060 | 0.75 | +0.33 | False |
| alaska_camera | EM | 0.945 | 0.190 | 0.92 | -0.16 | False |
| alaska_schema | SM | 0.928 | 0.118 | 0.68 | +0.00 | False |
| amazon_google | EM | 0.935 | 0.100 | 0.68 | +0.03 | False |
| bird | TQA | 0.185 | 0.209 | 0.85 | +0.31 | False |
| dblp_acm | EM | 0.987 | 0.090 | 0.88 | +0.31 | False |
| dblp_scholar | EM | 0.948 | 0.060 | 0.71 | +0.00 | False |
| fetaqa | TQA | 0.387 | 0.192 | 0.91 | +0.24 | False |
| fintagging | SM | 0.881 | 0.051 | 0.65 | +0.29 | False |
| hitab | TQA | 0.771 | 0.068 | 0.57 | -0.18 | False |
| machamp | EM | 0.887 | 0.070 | 0.58 | +0.39 | False |
| magneto_gdc | SM | 0.936 | 0.225 | 0.71 | +0.26 | False |
| mmtu | TQA | 0.870 | 0.110 | 0.72 | +0.29 | False |
| officeqa | FIN | 0.128 | 0.124 | 0.83 | +0.28 | False |
| officeqa_pro_v2 | FIN | 0.142 | 0.220 | 0.78 | +0.29 | False |
| opensanctions_pairs | EM | 0.835 | 0.240 | 0.90 | -0.00 | False |
| papadakis_dn | EM | 0.940 | 0.030 | 0.74 | +0.06 | False |
| realhitbench | TQA | 0.670 | 0.143 | 0.73 | +0.33 | False |
| smat | SM | 0.915 | 0.150 | 0.71 | +0.22 | False |
| suc | TQA | 0.917 | 0.246 | 0.81 | +0.26 | False |
| tab_fact | TQA | 0.802 | 0.200 | 0.83 | +0.01 | False |
| tabis | TQA | 0.916 | 0.210 | 0.84 | +0.26 | False |
| tablebench | TQA | 0.812 | 0.218 | 0.72 | +0.26 | False |
| tableeval | TQA | 0.752 | 0.166 | 0.74 | +0.19 | False |
| tat_qa | FIN | 0.804 | 0.109 | 0.76 | +0.26 | False |
| tpcdi_cells | SM | 0.456 | 0.020 | 0.78 | +0.32 | False |
| valentine | SM | 0.985 | 0.030 | 0.72 | +0.19 | True |
| walmart_amazon | EM | 0.959 | 0.060 | 0.76 | +0.33 | False |
| wdc_lspc | EM | 0.982 | 0.040 | 0.79 | +0.27 | True |
| wdc_products | EM | 0.977 | 0.020 | 0.62 | +0.19 | True |
| wikitablequestions | TQA | 0.847 | 0.132 | 0.73 | +0.34 | False |

## 8. Reading

* The three designs reach the same best J within noise (see the design table); the Latin hypercube design has the lowest discrepancy and the fewest zero weights, so it is the one to keep when a design is sampled.
* The honest advantage of the selected weighting over the v1 rubric is -0.003 with a CI that includes zero; the optimism gap 0.050 is the size of the winner's curse on this data.
* J and ρ correlate -0.21 across candidates: the agreement objective is not a proxy for correctness here; the anchor-optimal and Pareto-knee weightings are reported next to the J-optimal one.
* Files: grid_candidates.csv, best.json, designs.csv, selection/, anchors/, leaderboards/<rule>/ (params with BT SE, Kemeny cost, bootstrap draws, significance), diagnostics/, run_manifest.json.
