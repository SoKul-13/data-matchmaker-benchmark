# v3 report: aggregation views, all their combinations, parameters with standard errors

Generated 2026-09-27 14:29. 31 datasets × 10 models (abt_buy 100, alaska_camera 100, alaska_schema 93, amazon_google 100, bird 100, dblp_acm 100, dblp_scholar 100, fetaqa 100, fintagging 100, hitab 100, machamp 100, magneto_gdc 100, mmtu 100, officeqa 100, officeqa_pro_v2 90, opensanctions_pairs 100, papadakis_dn 100, realhitbench 100, smat 100, suc 100, tab_fact 100, tabis 100, tablebench 100, tableeval 100, tat_qa 100, tpcdi_cells 100, valentine 100, walmart_amazon 100, wdc_lspc 100, wdc_products 100, wikitablequestions 100). Candidates: 255 equal-weight subsets of the 8 views + 100 uniform-lattice + 100 Latin-hypercube mixes = 455; 100 item-bootstrap resamples for stability.

## 1. Single views and the best mixes

| view | J alone | claude-opus-5 | claude-sonnet-5 | deepseek-chat | deepseek-r1 | gemini-3.8-flash | gpt-5.4-mini | gpt-5.5 | gpt-oss-120b | grok-4 | llama-3.3-70b |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mean_raw | 0.930 | 2 | 5 | 8 | 6 | 3 | 7 | 1 | 9 | 4 | 10 |
| baseline_norm_mean | 0.886 | 3 | 6 | 8 | 5 | 2 | 7 | 1 | 9 | 4 | 10 |
| z_mean | 0.928 | 2 | 4 | 8 | 6 | 3 | 7 | 1 | 9 | 5 | 10 |
| mean_win_rate | 0.931 | 2 | 4 | 8 | 6 | 3 | 7 | 1 | 9 | 5 | 10 |
| borda | 0.932 | 2 | 4 | 8 | 6 | 3 | 7 | 1 | 9 | 5 | 10 |
| kemeny_score | 0.926 | 1 | 4 | 8 | 6 | 3 | 7 | 2 | 9 | 5 | 10 |
| bradley_terry | 0.891 | 3 | 5 | 7 | 6 | 1 | 8 | 2 | 9 | 4 | 10 |
| irt_ability | 0.904 | 3 | 5 | 8 | 6 | 1 | 7 | 2 | 9 | 4 | 10 |

Uniform mix J = 0.941. Best candidate: `subset_10011001` with J = 0.948 (stability 0.923, transitivity 0.94, reference 1.00); weights mean_raw 0.25, mean_win_rate 0.25, borda 0.25, irt_ability 0.25.
Best subset per size: 1 views: subset_00001000 (J 0.932); 2 views: subset_00010001 (J 0.944); 3 views: subset_10010010 (J 0.945); 4 views: subset_10011001 (J 0.948); 5 views: subset_01111001 (J 0.946); 6 views: subset_11111010 (J 0.946); 7 views: subset_11111011 (J 0.944); 8 views: subset_11111111 (J 0.941).
Designs: best J among subsets 0.948, lattice sample 0.946, LHS sample 0.946; coverage (centred L2 discrepancy) lattice 1.993 vs LHS 2.071.

### Top-5 mixes and the best subset

| rank | label | views (weight) | J | stability | transitivity | reference | claude-opus-5 rank [95 %] | claude-sonnet-5 rank [95 %] | deepseek-chat rank [95 %] | deepseek-r1 rank [95 %] | gemini-3.8-flash rank [95 %] | gpt-5.4-mini rank [95 %] | gpt-5.5 rank [95 %] | gpt-oss-120b rank [95 %] | grok-4 rank [95 %] | llama-3.3-70b rank [95 %] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | subset_10011001 | mean_raw (0.25), mean_win_rate (0.25), borda (0.25), irt_ability (0.25) | 0.948 | 0.923 | 0.94 | 1.00 | 2 [1, 3] | 5 [4, 6] | 8 [7, 8] | 6 [5, 8] | 3 [1, 3] | 7 [5, 8] | 1 [1, 3] | 9 [9, 9] | 4 [4, 5] | 10 [10, 10] |
| 2 | subset_10011010 | mean_raw (0.25), mean_win_rate (0.25), borda (0.25), bradley_terry (0.25) | 0.947 | 0.923 | 0.94 | 1.00 | 2 [1, 3] | 5 [4, 6] | 8 [6, 8] | 6 [4, 8] | 3 [1, 3] | 7 [6, 8] | 1 [1, 3] | 9 [9, 9] | 4 [4, 6] | 10 [10, 10] |
| 3 | lhs_038 | baseline_norm_mean (0.20), z_mean (0.10), mean_win_rate (0.35), borda (0.10), irt_ability (0.25) | 0.946 | 0.920 | 0.94 | 1.00 | 2 [1, 3] | 5 [4, 6] | 8 [7, 8] | 6 [4, 8] | 3 [1, 3] | 7 [5, 8] | 1 [1, 3] | 9 [9, 9] | 4 [4, 5] | 10 [10, 10] |
| 4 | subset_11111010 | mean_raw (0.17), baseline_norm_mean (0.17), z_mean (0.17), mean_win_rate (0.17), borda (0.17), bradley_terry (0.17) | 0.946 | 0.920 | 0.94 | 1.00 | 2 [1, 3] | 5 [4, 6] | 8 [7, 8] | 6 [4, 8] | 3 [1, 3] | 7 [5, 8] | 1 [1, 3] | 9 [9, 9] | 4 [4, 6] | 10 [10, 10] |
| 5 | lattice_076 | mean_raw (0.25), baseline_norm_mean (0.05), z_mean (0.15), mean_win_rate (0.15), borda (0.20), bradley_terry (0.10), irt_ability (0.10) | 0.946 | 0.920 | 0.94 | 1.00 | 2 [1, 3] | 5 [4, 6] | 8 [7, 8] | 6 [4, 8] | 3 [1, 3] | 7 [5, 8] | 1 [1, 3] | 9 [9, 9] | 4 [4, 6] | 10 [10, 10] |
| 1 | subset_10011001 | mean_raw (0.25), mean_win_rate (0.25), borda (0.25), irt_ability (0.25) | 0.948 | 0.923 | 0.94 | 1.00 | 2 [1, 3] | 5 [4, 6] | 8 [7, 8] | 6 [5, 8] | 3 [1, 3] | 7 [5, 8] | 1 [1, 3] | 9 [9, 9] | 4 [4, 5] | 10 [10, 10] |

## 2. Parameters with standard errors (native metric)

| model | BT strength (centred) | BT SE vs reference | BT bootstrap SD | Rasch ability | Rasch SE | Rasch bootstrap SD | Copeland | Kemeny position |
|---|---|---|---|---|---|---|---|---|
| claude-opus-5 | +0.045 | 0.000 | 0.005 | +0.651 | 0.103 | 0.086 | 8.5 | 1 |
| claude-sonnet-5 | +0.012 | 0.016 | 0.005 | +0.125 | 0.097 | 0.067 | 4.5 | 4 |
| deepseek-chat | +0.002 | 0.016 | 0.005 | -0.155 | 0.094 | 0.067 | 1.5 | 8 |
| deepseek-r1 | +0.012 | 0.016 | 0.005 | +0.070 | 0.096 | 0.070 | 3.5 | 6 |
| gemini-3.8-flash | +0.063 | 0.016 | 0.005 | +0.736 | 0.104 | 0.078 | 6.5 | 3 |
| gpt-5.4-mini | -0.011 | 0.016 | 0.005 | -0.084 | 0.094 | 0.066 | 2.5 | 7 |
| gpt-5.5 | +0.060 | 0.016 | 0.005 | +0.693 | 0.103 | 0.075 | 7.5 | 2 |
| gpt-oss-120b | -0.053 | 0.016 | 0.006 | -0.608 | 0.090 | 0.069 | 0.5 | 9 |
| grok-4 | +0.031 | 0.016 | 0.005 | +0.345 | 0.099 | 0.067 | 4.5 | 5 |
| llama-3.3-70b | -0.161 | 0.016 | 0.007 | -1.775 | 0.085 | 0.083 | -0.5 | 10 |

Kemeny cost 329 of 1395 possible pairwise disagreements; Rasch item difficulties: mean -0.12, sd 5.10, mean SE 7.40 (per item in `params/rasch_item_difficulties.csv`). The analytic SEs assume the model is right; the bootstrap SDs do not, and with 10 models they are the ones to quote.

## 3. Honest selection (split-half)

* 20 random half-splits: the mix selected on half A has J 0.935 there and 0.903 on half B (optimism gap 0.032); on half B pure Bradley–Terry scores 0.879, the uniform mix 0.917, the full-data best 0.913.
* Selected minus pure BT on the held-out half: +0.024 [-0.034, +0.111]; selected ahead in 70 % of splits. Most selected: subset_00010001 (1), subset_00011010 (1), lattice_041 (1), subset_10010101 (1), subset_00010010 (1), subset_00001000 (1), subset_00100000 (1), subset_00000101 (1), lattice_075 (1), subset_10110111 (1).

## 4. Leaderboards (Bradley–Terry rank, Borda in brackets) with significance

| rule | claude-opus-5 | claude-sonnet-5 | deepseek-chat | deepseek-r1 | gemini-3.8-flash | gpt-5.4-mini | gpt-5.5 | gpt-oss-120b | grok-4 | llama-3.3-70b | Friedman p | Kendall's W | significant pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| native | 3 (2) | 5 (4) | 7 (8) | 6 (6) | 1 (3) | 8 (7) | 2 (1) | 9 (9) | 4 (5) | 10 (10) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, gpt-5.5 > deepseek-chat, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| em_only | 1 (1) | 5 (4) | 8 (7) | 7 (6) | 3 (3) | 6 (8) | 2 (2) | 9 (9) | 4 (5) | 10 (10) | 0.000 | 0.28 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |

## Official-split estimates under the native metric

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
| alaska_schema | claude-opus-5 | 0.925 | 0.925 [0.87, 0.97] | – | 93 |
| alaska_schema | claude-sonnet-5 | 0.914 | 0.914 [0.86, 0.97] | – | 93 |
| alaska_schema | deepseek-chat | 0.925 | 0.925 [0.86, 0.98] | – | 93 |
| alaska_schema | deepseek-r1 | 0.925 | 0.925 [0.87, 0.98] | – | 93 |
| alaska_schema | gemini-3.8-flash | 0.892 | 0.892 [0.83, 0.95] | – | 93 |
| alaska_schema | gpt-5.4-mini | 0.946 | 0.946 [0.89, 0.98] | – | 93 |
| alaska_schema | gpt-5.5 | 0.903 | 0.903 [0.84, 0.96] | – | 93 |
| alaska_schema | gpt-oss-120b | 0.903 | 0.903 [0.84, 0.97] | – | 93 |
| alaska_schema | grok-4 | 0.903 | 0.903 [0.84, 0.96] | – | 93 |
| alaska_schema | llama-3.3-70b | 0.731 | 0.731 [0.65, 0.82] | – | 93 |
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
| bird | claude-opus-5 | 0.190 | 0.226 [0.13, 0.32] | – | 74 |
| bird | claude-sonnet-5 | 0.160 | 0.194 [0.11, 0.30] | – | 74 |
| bird | deepseek-chat | 0.120 | 0.147 [0.07, 0.23] | – | 74 |
| bird | deepseek-r1 | 0.130 | 0.170 [0.08, 0.26] | – | 74 |
| bird | gemini-3.8-flash | 0.210 | 0.226 [0.13, 0.33] | – | 74 |
| bird | gpt-5.4-mini | 0.130 | 0.173 [0.09, 0.26] | – | 74 |
| bird | gpt-5.5 | 0.140 | 0.164 [0.09, 0.26] | – | 74 |
| bird | gpt-oss-120b | 0.050 | 0.079 [0.02, 0.15] | – | 74 |
| bird | grok-4 | 0.080 | 0.109 [0.04, 0.19] | – | 74 |
| bird | llama-3.3-70b | 0.050 | 0.079 [0.02, 0.16] | – | 74 |
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
| fetaqa | claude-opus-5 | 0.483 | 0.483 [0.44, 0.52] | – | 100 |
| fetaqa | claude-sonnet-5 | 0.451 | 0.451 [0.41, 0.49] | – | 100 |
| fetaqa | deepseek-chat | 0.540 | 0.540 [0.50, 0.58] | – | 100 |
| fetaqa | deepseek-r1 | 0.504 | 0.504 [0.46, 0.55] | – | 100 |
| fetaqa | gemini-3.8-flash | 0.557 | 0.557 [0.52, 0.60] | – | 100 |
| fetaqa | gpt-5.4-mini | 0.368 | 0.368 [0.33, 0.41] | – | 100 |
| fetaqa | gpt-5.5 | 0.552 | 0.552 [0.51, 0.59] | – | 100 |
| fetaqa | gpt-oss-120b | 0.406 | 0.406 [0.38, 0.44] | – | 100 |
| fetaqa | grok-4 | 0.536 | 0.536 [0.50, 0.58] | – | 100 |
| fetaqa | llama-3.3-70b | 0.287 | 0.287 [0.25, 0.32] | – | 100 |
| fintagging | claude-opus-5 | 0.840 | 0.880 [0.79, 0.96] | – | 52 |
| fintagging | claude-sonnet-5 | 0.820 | 0.818 [0.71, 0.92] | – | 52 |
| fintagging | deepseek-chat | 0.750 | 0.731 [0.61, 0.85] | – | 52 |
| fintagging | deepseek-r1 | 0.760 | 0.790 [0.68, 0.89] | – | 52 |
| fintagging | gemini-3.8-flash | 0.820 | 0.838 [0.73, 0.93] | – | 52 |
| fintagging | gpt-5.4-mini | 0.810 | 0.759 [0.63, 0.87] | – | 52 |
| fintagging | gpt-5.5 | 0.820 | 0.838 [0.73, 0.93] | – | 52 |
| fintagging | gpt-oss-120b | 0.760 | 0.732 [0.61, 0.85] | – | 52 |
| fintagging | grok-4 | 0.810 | 0.798 [0.68, 0.90] | – | 52 |
| fintagging | llama-3.3-70b | 0.750 | 0.711 [0.59, 0.83] | – | 52 |
| hitab | claude-opus-5 | 0.760 | 0.782 [0.70, 0.86] | – | 95 |
| hitab | claude-sonnet-5 | 0.740 | 0.743 [0.65, 0.83] | – | 95 |
| hitab | deepseek-chat | 0.790 | 0.812 [0.74, 0.88] | – | 95 |
| hitab | deepseek-r1 | 0.750 | 0.760 [0.67, 0.84] | – | 95 |
| hitab | gemini-3.8-flash | 0.720 | 0.745 [0.66, 0.83] | – | 95 |
| hitab | gpt-5.4-mini | 0.760 | 0.772 [0.69, 0.86] | – | 95 |
| hitab | gpt-5.5 | 0.730 | 0.751 [0.66, 0.83] | – | 95 |
| hitab | gpt-oss-120b | 0.710 | 0.728 [0.64, 0.82] | – | 95 |
| hitab | grok-4 | 0.710 | 0.723 [0.63, 0.81] | – | 95 |
| hitab | llama-3.3-70b | 0.760 | 0.777 [0.69, 0.85] | – | 95 |
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
| magneto_gdc | claude-opus-5 | 0.960 | 0.962 [0.92, 0.99] | – | 93 |
| magneto_gdc | claude-sonnet-5 | 0.940 | 0.939 [0.89, 0.98] | – | 93 |
| magneto_gdc | deepseek-chat | 0.930 | 0.933 [0.88, 0.98] | – | 93 |
| magneto_gdc | deepseek-r1 | 0.960 | 0.963 [0.92, 0.99] | – | 93 |
| magneto_gdc | gemini-3.8-flash | 0.950 | 0.954 [0.91, 0.99] | – | 93 |
| magneto_gdc | gpt-5.4-mini | 0.890 | 0.894 [0.83, 0.95] | – | 93 |
| magneto_gdc | gpt-5.5 | 0.960 | 0.966 [0.93, 0.99] | – | 93 |
| magneto_gdc | gpt-oss-120b | 0.950 | 0.954 [0.91, 0.99] | – | 93 |
| magneto_gdc | grok-4 | 0.920 | 0.924 [0.87, 0.97] | – | 93 |
| magneto_gdc | llama-3.3-70b | 0.620 | 0.624 [0.52, 0.71] | – | 93 |
| mmtu | claude-opus-5 | 0.900 | 0.858 [0.77, 0.94] | – | 87 |
| mmtu | claude-sonnet-5 | 0.900 | 0.858 [0.77, 0.94] | – | 87 |
| mmtu | deepseek-chat | 0.890 | 0.849 [0.77, 0.93] | – | 87 |
| mmtu | deepseek-r1 | 0.830 | 0.772 [0.67, 0.87] | – | 87 |
| mmtu | gemini-3.8-flash | 0.900 | 0.856 [0.76, 0.94] | – | 87 |
| mmtu | gpt-5.4-mini | 0.890 | 0.855 [0.77, 0.93] | – | 87 |
| mmtu | gpt-5.5 | 0.930 | 0.892 [0.80, 0.97] | – | 87 |
| mmtu | gpt-oss-120b | 0.830 | 0.771 [0.67, 0.86] | – | 87 |
| mmtu | grok-4 | 0.910 | 0.875 [0.79, 0.95] | – | 87 |
| mmtu | llama-3.3-70b | 0.810 | 0.757 [0.66, 0.86] | – | 87 |
| officeqa | claude-opus-5 | 0.150 | n/c | – | 100 |
| officeqa | claude-sonnet-5 | 0.080 | n/c | – | 100 |
| officeqa | deepseek-chat | 0.050 | n/c | – | 100 |
| officeqa | deepseek-r1 | 0.040 | n/c | – | 100 |
| officeqa | gemini-3.8-flash | 0.160 | n/c | – | 100 |
| officeqa | gpt-5.4-mini | 0.020 | n/c | – | 100 |
| officeqa | gpt-5.5 | 0.110 | n/c | – | 100 |
| officeqa | gpt-oss-120b | 0.050 | n/c | – | 100 |
| officeqa | grok-4 | 0.090 | n/c | – | 100 |
| officeqa | llama-3.3-70b | 0.020 | n/c | – | 100 |
| officeqa_pro_v2 | claude-opus-5 | 0.167 | 0.167 [0.09, 0.24] | – | 90 |
| officeqa_pro_v2 | claude-sonnet-5 | 0.100 | 0.100 [0.04, 0.17] | – | 90 |
| officeqa_pro_v2 | deepseek-chat | 0.067 | 0.067 [0.02, 0.12] | – | 90 |
| officeqa_pro_v2 | deepseek-r1 | 0.022 | 0.022 [0.00, 0.06] | – | 90 |
| officeqa_pro_v2 | gemini-3.8-flash | 0.089 | 0.089 [0.03, 0.14] | – | 90 |
| officeqa_pro_v2 | gpt-5.4-mini | 0.067 | 0.067 [0.02, 0.12] | – | 90 |
| officeqa_pro_v2 | gpt-5.5 | 0.144 | 0.144 [0.08, 0.22] | – | 90 |
| officeqa_pro_v2 | gpt-oss-120b | 0.056 | 0.056 [0.01, 0.10] | – | 90 |
| officeqa_pro_v2 | grok-4 | 0.056 | 0.056 [0.01, 0.10] | – | 90 |
| officeqa_pro_v2 | llama-3.3-70b | 0.056 | 0.056 [0.01, 0.10] | – | 90 |
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
| realhitbench | claude-opus-5 | 0.700 | 0.700 [0.61, 0.79] | – | 98 |
| realhitbench | claude-sonnet-5 | 0.640 | 0.640 [0.55, 0.73] | – | 98 |
| realhitbench | deepseek-chat | 0.620 | 0.609 [0.51, 0.70] | – | 98 |
| realhitbench | deepseek-r1 | 0.630 | 0.632 [0.53, 0.72] | – | 98 |
| realhitbench | gemini-3.8-flash | 0.710 | 0.708 [0.62, 0.80] | – | 98 |
| realhitbench | gpt-5.4-mini | 0.610 | 0.606 [0.51, 0.70] | – | 98 |
| realhitbench | gpt-5.5 | 0.690 | 0.686 [0.60, 0.78] | – | 98 |
| realhitbench | gpt-oss-120b | 0.560 | 0.558 [0.46, 0.65] | – | 98 |
| realhitbench | grok-4 | 0.610 | 0.606 [0.51, 0.70] | – | 98 |
| realhitbench | llama-3.3-70b | 0.530 | 0.535 [0.44, 0.63] | – | 98 |
| smat | claude-opus-5 | 0.900 | 0.898 [0.83, 0.95] | – | 98 |
| smat | claude-sonnet-5 | 0.910 | 0.907 [0.85, 0.96] | – | 98 |
| smat | deepseek-chat | 0.880 | 0.876 [0.81, 0.94] | – | 98 |
| smat | deepseek-r1 | 0.880 | 0.875 [0.81, 0.94] | – | 98 |
| smat | gemini-3.8-flash | 0.880 | 0.876 [0.81, 0.94] | – | 98 |
| smat | gpt-5.4-mini | 0.930 | 0.934 [0.88, 0.98] | – | 98 |
| smat | gpt-5.5 | 0.910 | 0.908 [0.84, 0.96] | – | 98 |
| smat | gpt-oss-120b | 0.880 | 0.874 [0.81, 0.94] | – | 98 |
| smat | grok-4 | 0.910 | 0.906 [0.85, 0.96] | – | 98 |
| smat | llama-3.3-70b | 0.680 | 0.675 [0.58, 0.77] | – | 98 |
| suc | claude-opus-5 | 0.980 | 0.981 [0.95, 1.00] | – | 99 |
| suc | claude-sonnet-5 | 0.880 | 0.874 [0.80, 0.94] | – | 99 |
| suc | deepseek-chat | 0.820 | 0.817 [0.74, 0.89] | – | 99 |
| suc | deepseek-r1 | 0.910 | 0.906 [0.84, 0.96] | – | 99 |
| suc | gemini-3.8-flash | 0.970 | 0.971 [0.93, 1.00] | – | 99 |
| suc | gpt-5.4-mini | 0.880 | 0.873 [0.80, 0.94] | – | 99 |
| suc | gpt-5.5 | 0.920 | 0.913 [0.85, 0.97] | – | 99 |
| suc | gpt-oss-120b | 0.910 | 0.906 [0.84, 0.96] | – | 99 |
| suc | grok-4 | 0.920 | 0.912 [0.85, 0.97] | – | 99 |
| suc | llama-3.3-70b | 0.670 | 0.663 [0.57, 0.76] | – | 99 |
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
| tablebench | claude-opus-5 | 0.830 | 0.831 [0.75, 0.91] | – | 89 |
| tablebench | claude-sonnet-5 | 0.870 | 0.867 [0.80, 0.93] | – | 89 |
| tablebench | deepseek-chat | 0.810 | 0.820 [0.74, 0.89] | – | 89 |
| tablebench | deepseek-r1 | 0.760 | 0.773 [0.69, 0.85] | – | 89 |
| tablebench | gemini-3.8-flash | 0.830 | 0.829 [0.75, 0.91] | – | 89 |
| tablebench | gpt-5.4-mini | 0.830 | 0.821 [0.74, 0.90] | – | 89 |
| tablebench | gpt-5.5 | 0.850 | 0.849 [0.77, 0.92] | – | 89 |
| tablebench | gpt-oss-120b | 0.800 | 0.788 [0.70, 0.87] | – | 89 |
| tablebench | grok-4 | 0.820 | 0.815 [0.73, 0.90] | – | 89 |
| tablebench | llama-3.3-70b | 0.620 | 0.610 [0.51, 0.71] | – | 89 |
| tableeval | claude-opus-5 | 0.740 | 0.760 [0.66, 0.86] | – | 70 |
| tableeval | claude-sonnet-5 | 0.705 | 0.745 [0.64, 0.84] | – | 70 |
| tableeval | deepseek-chat | 0.655 | 0.668 [0.55, 0.77] | – | 70 |
| tableeval | deepseek-r1 | 0.730 | 0.732 [0.63, 0.84] | – | 70 |
| tableeval | gemini-3.8-flash | 0.775 | 0.791 [0.69, 0.88] | – | 70 |
| tableeval | gpt-5.4-mini | 0.730 | 0.744 [0.63, 0.84] | – | 70 |
| tableeval | gpt-5.5 | 0.760 | 0.777 [0.67, 0.87] | – | 70 |
| tableeval | gpt-oss-120b | 0.760 | 0.762 [0.66, 0.86] | – | 70 |
| tableeval | grok-4 | 0.780 | 0.769 [0.65, 0.87] | – | 70 |
| tableeval | llama-3.3-70b | 0.570 | 0.561 [0.44, 0.68] | – | 70 |
| tat_qa | claude-opus-5 | 0.810 | 0.771 [0.67, 0.87] | – | 61 |
| tat_qa | claude-sonnet-5 | 0.750 | 0.733 [0.62, 0.84] | – | 61 |
| tat_qa | deepseek-chat | 0.740 | 0.692 [0.58, 0.81] | – | 61 |
| tat_qa | deepseek-r1 | 0.750 | 0.700 [0.59, 0.81] | – | 61 |
| tat_qa | gemini-3.8-flash | 0.740 | 0.709 [0.59, 0.81] | – | 61 |
| tat_qa | gpt-5.4-mini | 0.770 | 0.718 [0.59, 0.82] | – | 61 |
| tat_qa | gpt-5.5 | 0.730 | 0.708 [0.60, 0.81] | – | 61 |
| tat_qa | gpt-oss-120b | 0.730 | 0.663 [0.54, 0.78] | – | 61 |
| tat_qa | grok-4 | 0.770 | 0.705 [0.58, 0.82] | – | 61 |
| tat_qa | llama-3.3-70b | 0.720 | 0.662 [0.53, 0.78] | – | 61 |
| tpcdi_cells | claude-opus-5 | 0.350 | 0.380 [0.29, 0.48] | – | 95 |
| tpcdi_cells | claude-sonnet-5 | 0.350 | 0.380 [0.28, 0.49] | – | 95 |
| tpcdi_cells | deepseek-chat | 0.350 | 0.380 [0.28, 0.48] | – | 95 |
| tpcdi_cells | deepseek-r1 | 0.350 | 0.380 [0.28, 0.48] | – | 95 |
| tpcdi_cells | gemini-3.8-flash | 0.350 | 0.380 [0.28, 0.48] | – | 95 |
| tpcdi_cells | gpt-5.4-mini | 0.340 | 0.368 [0.26, 0.46] | – | 95 |
| tpcdi_cells | gpt-5.5 | 0.350 | 0.380 [0.28, 0.47] | – | 95 |
| tpcdi_cells | gpt-oss-120b | 0.330 | 0.367 [0.26, 0.47] | – | 95 |
| tpcdi_cells | grok-4 | 0.330 | 0.367 [0.27, 0.47] | – | 95 |
| tpcdi_cells | llama-3.3-70b | 0.330 | 0.367 [0.27, 0.46] | – | 95 |
| valentine | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | claude-sonnet-5 | 0.990 | 0.983 [0.94, 1.00] | – | 82 |
| valentine | deepseek-chat | 0.970 | 0.951 [0.90, 1.00] | – | 82 |
| valentine | deepseek-r1 | 0.990 | 0.986 [0.96, 1.00] | – | 82 |
| valentine | gemini-3.8-flash | 0.970 | 0.988 [0.97, 1.00] | – | 82 |
| valentine | gpt-5.4-mini | 0.980 | 0.969 [0.92, 1.00] | – | 82 |
| valentine | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | gpt-oss-120b | 0.970 | 0.955 [0.89, 1.00] | – | 82 |
| valentine | grok-4 | 0.960 | 0.934 [0.87, 0.99] | – | 82 |
| valentine | llama-3.3-70b | 0.960 | 0.941 [0.87, 0.99] | – | 82 |
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
| wikitablequestions | claude-opus-5 | 0.840 | 0.838 [0.76, 0.91] | – | 98 |
| wikitablequestions | claude-sonnet-5 | 0.830 | 0.829 [0.75, 0.90] | – | 98 |
| wikitablequestions | deepseek-chat | 0.800 | 0.798 [0.71, 0.87] | – | 98 |
| wikitablequestions | deepseek-r1 | 0.800 | 0.797 [0.72, 0.88] | – | 98 |
| wikitablequestions | gemini-3.8-flash | 0.840 | 0.839 [0.76, 0.91] | – | 98 |
| wikitablequestions | gpt-5.4-mini | 0.810 | 0.807 [0.73, 0.88] | – | 98 |
| wikitablequestions | gpt-5.5 | 0.820 | 0.816 [0.74, 0.89] | – | 98 |
| wikitablequestions | gpt-oss-120b | 0.770 | 0.766 [0.68, 0.85] | – | 98 |
| wikitablequestions | grok-4 | 0.810 | 0.806 [0.73, 0.88] | – | 98 |
| wikitablequestions | llama-3.3-70b | 0.670 | 0.667 [0.58, 0.76] | – | 98 |

Full tables, strengths with SE, 1,000 bootstrap draws and Holm-corrected pairwise tests under `leaderboards/native/` and `leaderboards/em_only/`.

## 5. Dataset diagnostics

| dataset | family | mean | spread | self-stability τ | τ to others | exclude |
|---|---|---|---|---|---|---|
| abt_buy | EM | 0.970 | 0.060 | 0.73 | +0.37 | False |
| alaska_camera | EM | 0.958 | 0.180 | 0.92 | -0.22 | False |
| alaska_schema | SM | 0.897 | 0.215 | 0.71 | +0.05 | False |
| amazon_google | EM | 0.936 | 0.100 | 0.68 | -0.02 | False |
| bird | TQA | 0.126 | 0.160 | 0.84 | +0.36 | False |
| dblp_acm | EM | 0.986 | 0.090 | 0.88 | +0.36 | False |
| dblp_scholar | EM | 0.949 | 0.060 | 0.73 | -0.03 | False |
| fetaqa | TQA | 0.468 | 0.270 | 0.94 | +0.28 | False |
| fintagging | SM | 0.794 | 0.090 | 0.71 | +0.38 | False |
| hitab | TQA | 0.743 | 0.080 | 0.65 | -0.09 | False |
| machamp | EM | 0.887 | 0.070 | 0.60 | +0.40 | False |
| magneto_gdc | SM | 0.908 | 0.340 | 0.74 | +0.27 | False |
| mmtu | TQA | 0.879 | 0.120 | 0.74 | +0.36 | False |
| officeqa | FIN | 0.077 | 0.140 | 0.87 | +0.33 | False |
| officeqa_pro_v2 | FIN | 0.082 | 0.144 | 0.80 | +0.30 | False |
| opensanctions_pairs | EM | 0.821 | 0.210 | 0.89 | +0.03 | False |
| papadakis_dn | EM | 0.941 | 0.030 | 0.74 | +0.07 | False |
| realhitbench | TQA | 0.630 | 0.180 | 0.80 | +0.39 | False |
| smat | SM | 0.876 | 0.250 | 0.71 | +0.20 | False |
| suc | TQA | 0.886 | 0.310 | 0.88 | +0.32 | False |
| tab_fact | TQA | 0.798 | 0.200 | 0.84 | -0.00 | False |
| tabis | TQA | 0.915 | 0.210 | 0.85 | +0.24 | False |
| tablebench | TQA | 0.802 | 0.250 | 0.77 | +0.32 | False |
| tableeval | TQA | 0.721 | 0.210 | 0.80 | +0.19 | False |
| tat_qa | FIN | 0.751 | 0.090 | 0.63 | +0.19 | False |
| tpcdi_cells | SM | 0.343 | 0.020 | 0.82 | +0.33 | False |
| valentine | SM | 0.979 | 0.040 | 0.73 | +0.30 | True |
| walmart_amazon | EM | 0.958 | 0.060 | 0.76 | +0.39 | False |
| wdc_lspc | EM | 0.982 | 0.040 | 0.80 | +0.27 | True |
| wdc_products | EM | 0.978 | 0.020 | 0.64 | +0.19 | True |
| wikitablequestions | TQA | 0.799 | 0.170 | 0.75 | +0.39 | False |

## 6. Reading

* Every combination of the eight views is now on file (`combos/`, 255 subsets with member parameters), so the choice of aggregation rule is an enumerated, reproducible decision rather than a sample.
* The split-half check is the honesty test for that choice: if the selected mix beats pure Bradley–Terry on held-out halves in most splits, mixing views is worth it; otherwise pure BT is the defensible headline (Chatbot Arena's rule).
* With 10 models every parameter table is coarse; the bootstrap SDs say how coarse. The 12-model run is what makes section 2 informative.
* Files: views.csv, views_em.csv, Zb.npz (bootstrap view tables + per-draw BT/Rasch parameters), combos/, params/, designs.json, selection/split_half.{csv,json}, best.json, leaderboards/, diagnostics/.
