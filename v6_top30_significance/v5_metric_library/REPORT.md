# v5 report: metric library, anchor-calibrated ensemble, exhaustive grid, designs, leaderboards with significance

Generated 2026-10-16 14:53. Model answers: 31 datasets × 11 models (33,913 rows). Anchors: 31,380 synthetic answers over 31 datasets (every pool, including the new ones without model answers).

## 1. Selection and calibration

* Selected metrics: tok_f1, num_decay_2p5, prefix_ratio (from the 100-metric library; selection details in `selected.json`, `clusters.json`, `metric_table.csv`).
* Exhaustive grid: 6,630 weightings (step 0.02 × 5 hedge penalties); ensemble = mean of the top 100: tok_f1 0.18, num_decay_2p5 0.75, prefix_ratio 0.07, λ = 0.66; J top-1 0.934, top-100 0.933, grid median 0.924.
* Ensemble terms (mean over the top 100): rho 0.904, auc 0.997, js 0.054, tau_native 0.897, bad 0.032.

| baseline | ρ | AUC | 1 − JS/ln2 | τ native | wrong-score | J |
|---|---|---|---|---|---|---|
| native_style_metric | 0.826 | 0.935 | 0.955 | 0.99 | 0.014 | 0.925 |
| em_norm | 0.849 | 0.963 | 0.966 | 0.92 | 0.012 | 0.928 |
| tok_f1 | 0.859 | 0.965 | 0.886 | 0.88 | 0.032 | 0.906 |
| rouge_l | 0.862 | 0.965 | 0.882 | 0.88 | 0.032 | 0.906 |
| num_tol_1 | 0.806 | 0.919 | 0.955 | 0.94 | 0.016 | 0.908 |
| uniform_over_selected_no_gate | 0.882 | 0.970 | 0.859 | 0.91 | 0.028 | 0.912 |
| ensemble_top100 | 0.904 | 0.997 | 0.922 | 0.90 | 0.032 | 0.933 |

## 2. Sampled designs versus the exhaustive grid (20 seeds × 100 weightings × 5 λ)

| design | best J found (mean ± sd) | regret vs exhaustive (mean / max) | min pairwise L1 | centred L2 discrepancy | share with a zero weight |
|---|---|---|---|---|---|
| uniform_lattice | 0.9339 ± 0.0003 | 0.0006 / 0.0013 | 0.04 | 0.264 | 0.11 |
| dirichlet_lattice | 0.9339 ± 0.0003 | 0.0006 / 0.0011 | 0.04 | 0.273 | 0.06 |
| lhs_simplex | 0.9338 ± 0.0003 | 0.0006 / 0.0013 | 0.04 | 0.270 | 0.06 |

Exhaustive best J = 0.9344 over 6,630 points; with three weights every design gets within a few thousandths of it, which is why v5 keeps the exhaustive grid and the sampled designs are a check only.

## 3. Validation (from step 5)

* lodo_mean_rho_lodo: 0.8937564710831764
* lodo_mean_rho_full: 0.8945883733091227
* lodo_same_selection_share: 0.9032258064516129
* severity_l1_shift_mean: 0.03064000000000001
* severity_l1_shift_max: 0.03199999999999993
* severity_selection_changed_share: 0.0
* probe_mae_ensemble: 0.11370895241138705
* probe_mae_em: 0.19909387481166047
* probe_mae_native: 0.15454948486236392
* probe_mae_tok_f1: 0.1439566986518912

## 4. Leaderboards (Bradley–Terry rank, Borda in brackets) with significance

| rule | weights | claude-opus-5 | claude-sonnet-5 | deepseek-chat | deepseek-r1 | gemini-3.1-pro | gemini-3.8-flash | gpt-5.4-mini | gpt-5.5 | gpt-oss-120b | grok-4 | llama-3.3-70b | Friedman p | Kendall's W | significant pairs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| em_only | – | 1 (1) | 7 (4) | 9 (8) | 6 (5) | 4 (7) | 2 (3) | 8 (9) | 3 (2) | 10 (10) | 5 (6) | 11 (11) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| native | – | 3 (2) | 7 (4) | 8 (9) | 6 (6) | 4 (5) | 1 (3) | 9 (8) | 2 (1) | 10 (10) | 5 (7) | 11 (11) | 0.000 | 0.27 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, gpt-5.5 > deepseek-chat, deepseek-chat > llama-3.3-70b, deepseek-r1 > gpt-oss-120b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| ensemble | tok_f1 0.18, num_decay_2p5 0.75, prefix_ratio 0.07, lambda 0.66 | 2 (1) | 4 (4) | 9 (9) | 8 (5) | 5 (6) | 1 (3) | 7 (8) | 3 (2) | 10 (10) | 6 (7) | 11 (11) | 0.000 | 0.25 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top1 | tok_f1 0.06, num_decay_2p5 0.90, prefix_ratio 0.04, lambda 0.75 | 2 (1) | 4 (4) | 9 (9) | 8 (5) | 5 (7) | 1 (3) | 7 (8) | 3 (2) | 10 (10) | 6 (6) | 11 (11) | 0.000 | 0.24 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top2 | tok_f1 0.08, num_decay_2p5 0.90, prefix_ratio 0.02, lambda 0.75 | 2 (1) | 4 (4) | 9 (9) | 8 (5) | 5 (7) | 1 (3) | 7 (8) | 3 (2) | 10 (10) | 6 (6) | 11 (11) | 0.000 | 0.24 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top3 | tok_f1 0.02, num_decay_2p5 0.90, prefix_ratio 0.08, lambda 0.75 | 2 (1) | 4 (4) | 9 (9) | 8 (5) | 5 (6) | 1 (3) | 7 (8) | 3 (2) | 10 (10) | 6 (7) | 11 (11) | 0.000 | 0.24 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top4 | tok_f1 0.04, num_decay_2p5 0.90, prefix_ratio 0.06, lambda 0.75 | 2 (1) | 4 (4) | 9 (9) | 8 (5) | 5 (7) | 1 (3) | 7 (8) | 3 (2) | 10 (10) | 6 (6) | 11 (11) | 0.000 | 0.24 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |
| top5 | tok_f1 0.22, num_decay_2p5 0.70, prefix_ratio 0.08, lambda 0.75 | 2 (1) | 4 (4) | 9 (9) | 8 (5) | 5 (6) | 1 (3) | 7 (8) | 3 (2) | 10 (10) | 6 (7) | 11 (11) | 0.000 | 0.25 | claude-opus-5 > gpt-oss-120b, claude-opus-5 > llama-3.3-70b, claude-sonnet-5 > llama-3.3-70b, deepseek-chat > llama-3.3-70b, deepseek-r1 > llama-3.3-70b, gpt-5.5 > gemini-3.1-pro, gemini-3.1-pro > gpt-oss-120b, gemini-3.1-pro > llama-3.3-70b, gemini-3.8-flash > gpt-oss-120b, gemini-3.8-flash > llama-3.3-70b, gpt-5.4-mini > llama-3.3-70b, gpt-5.5 > gpt-oss-120b, gpt-5.5 > llama-3.3-70b, grok-4 > gpt-oss-120b, grok-4 > llama-3.3-70b |

τ between BT rankings of the rules:

| | em_only | native | ensemble | top1 | top2 | top3 | top4 | top5 |
|---|---|---|---|---|---|---|---|---|
| em_only | +1.00 | +0.89 | +0.82 | +0.82 | +0.82 | +0.82 | +0.82 | +0.82 |
| native | +0.89 | +1.00 | +0.78 | +0.78 | +0.78 | +0.78 | +0.78 | +0.78 |
| ensemble | +0.82 | +0.78 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 |
| top1 | +0.82 | +0.78 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 |
| top2 | +0.82 | +0.78 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 |
| top3 | +0.82 | +0.78 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 |
| top4 | +0.82 | +0.78 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 |
| top5 | +0.82 | +0.78 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 |

## Official-split estimates under the ensemble

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
| alaska_schema | claude-opus-5 | 0.933 | 0.933 [0.88, 0.97] | – | 93 |
| alaska_schema | claude-sonnet-5 | 0.920 | 0.920 [0.87, 0.97] | – | 93 |
| alaska_schema | deepseek-chat | 0.935 | 0.935 [0.88, 0.98] | – | 93 |
| alaska_schema | deepseek-r1 | 0.944 | 0.944 [0.90, 0.98] | – | 93 |
| alaska_schema | gemini-3.1-pro | 0.912 | 0.912 [0.85, 0.96] | – | 93 |
| alaska_schema | gemini-3.8-flash | 0.903 | 0.903 [0.84, 0.95] | – | 93 |
| alaska_schema | gpt-5.4-mini | 0.951 | 0.951 [0.91, 0.99] | – | 93 |
| alaska_schema | gpt-5.5 | 0.912 | 0.912 [0.85, 0.96] | – | 93 |
| alaska_schema | gpt-oss-120b | 0.915 | 0.915 [0.86, 0.96] | – | 93 |
| alaska_schema | grok-4 | 0.912 | 0.912 [0.85, 0.96] | – | 93 |
| alaska_schema | llama-3.3-70b | 0.783 | 0.783 [0.70, 0.86] | – | 93 |
| amazon_google | claude-opus-5 | 0.940 | 0.916 [0.84, 0.98] | 0.94 → 0.70 [0.53, 0.92] | 67 |
| amazon_google | claude-sonnet-5 | 0.960 | 0.935 [0.87, 0.98] | 0.96 → 0.76 [0.59, 0.94] | 67 |
| amazon_google | deepseek-chat | 0.960 | 0.949 [0.89, 1.00] | 0.96 → 0.80 [0.61, 0.99] | 67 |
| amazon_google | deepseek-r1 | 0.943 | 0.931 [0.86, 0.98] | 0.94 → 0.74 [0.57, 0.93] | 67 |
| amazon_google | gemini-3.1-pro | 0.930 | 0.928 [0.86, 0.98] | 0.92 → 0.73 [0.55, 0.91] | 67 |
| amazon_google | gemini-3.8-flash | 0.930 | 0.928 [0.86, 0.98] | 0.92 → 0.73 [0.55, 0.91] | 67 |
| amazon_google | gpt-5.4-mini | 0.930 | 0.942 [0.88, 0.99] | 0.92 → 0.76 [0.58, 0.96] | 67 |
| amazon_google | gpt-5.5 | 0.940 | 0.916 [0.84, 0.98] | 0.94 → 0.70 [0.54, 0.91] | 67 |
| amazon_google | gpt-oss-120b | 0.860 | 0.926 [0.86, 0.97] | 0.83 → 0.68 [0.51, 0.87] | 67 |
| amazon_google | grok-4 | 0.940 | 0.944 [0.87, 0.99] | 0.93 → 0.77 [0.61, 0.97] | 67 |
| amazon_google | llama-3.3-70b | 0.950 | 0.932 [0.86, 0.98] | 0.95 → 0.75 [0.56, 0.94] | 67 |
| bird | claude-opus-5 | 0.388 | 0.407 [0.31, 0.51] | – | 74 |
| bird | claude-sonnet-5 | 0.328 | 0.335 [0.25, 0.43] | – | 74 |
| bird | deepseek-chat | 0.269 | 0.271 [0.19, 0.35] | – | 74 |
| bird | deepseek-r1 | 0.279 | 0.317 [0.23, 0.41] | – | 74 |
| bird | gemini-3.1-pro | 0.212 | 0.250 [0.17, 0.34] | – | 74 |
| bird | gemini-3.8-flash | 0.402 | 0.420 [0.33, 0.51] | – | 74 |
| bird | gpt-5.4-mini | 0.231 | 0.266 [0.18, 0.36] | – | 74 |
| bird | gpt-5.5 | 0.213 | 0.220 [0.13, 0.32] | – | 74 |
| bird | gpt-oss-120b | 0.121 | 0.139 [0.07, 0.21] | – | 74 |
| bird | grok-4 | 0.151 | 0.172 [0.10, 0.26] | – | 74 |
| bird | llama-3.3-70b | 0.196 | 0.208 [0.14, 0.28] | – | 74 |
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
| fetaqa | claude-opus-5 | 0.627 | 0.627 [0.56, 0.69] | – | 100 |
| fetaqa | claude-sonnet-5 | 0.557 | 0.557 [0.49, 0.63] | – | 100 |
| fetaqa | deepseek-chat | 0.619 | 0.619 [0.55, 0.68] | – | 100 |
| fetaqa | deepseek-r1 | 0.593 | 0.593 [0.52, 0.66] | – | 100 |
| fetaqa | gemini-3.1-pro | 0.608 | 0.608 [0.54, 0.67] | – | 100 |
| fetaqa | gemini-3.8-flash | 0.658 | 0.658 [0.59, 0.72] | – | 100 |
| fetaqa | gpt-5.4-mini | 0.341 | 0.341 [0.28, 0.41] | – | 100 |
| fetaqa | gpt-5.5 | 0.618 | 0.618 [0.55, 0.68] | – | 100 |
| fetaqa | gpt-oss-120b | 0.611 | 0.611 [0.54, 0.68] | – | 100 |
| fetaqa | grok-4 | 0.645 | 0.645 [0.58, 0.71] | – | 100 |
| fetaqa | llama-3.3-70b | 0.246 | 0.246 [0.19, 0.31] | – | 100 |
| fintagging | claude-opus-5 | 0.865 | 0.899 [0.82, 0.97] | – | 52 |
| fintagging | claude-sonnet-5 | 0.850 | 0.848 [0.75, 0.93] | – | 52 |
| fintagging | deepseek-chat | 0.790 | 0.775 [0.67, 0.87] | – | 52 |
| fintagging | deepseek-r1 | 0.821 | 0.842 [0.74, 0.92] | – | 52 |
| fintagging | gemini-3.1-pro | 0.832 | 0.862 [0.77, 0.94] | – | 52 |
| fintagging | gemini-3.8-flash | 0.849 | 0.865 [0.77, 0.94] | – | 52 |
| fintagging | gpt-5.4-mini | 0.841 | 0.799 [0.70, 0.89] | – | 52 |
| fintagging | gpt-5.5 | 0.848 | 0.862 [0.78, 0.94] | – | 52 |
| fintagging | gpt-oss-120b | 0.806 | 0.791 [0.68, 0.88] | – | 52 |
| fintagging | grok-4 | 0.839 | 0.828 [0.74, 0.92] | – | 52 |
| fintagging | llama-3.3-70b | 0.790 | 0.758 [0.65, 0.87] | – | 52 |
| hitab | claude-opus-5 | 0.785 | 0.804 [0.72, 0.87] | – | 95 |
| hitab | claude-sonnet-5 | 0.776 | 0.779 [0.69, 0.85] | – | 95 |
| hitab | deepseek-chat | 0.815 | 0.834 [0.76, 0.90] | – | 95 |
| hitab | deepseek-r1 | 0.787 | 0.791 [0.72, 0.86] | – | 95 |
| hitab | gemini-3.1-pro | 0.777 | 0.793 [0.72, 0.87] | – | 95 |
| hitab | gemini-3.8-flash | 0.757 | 0.775 [0.70, 0.85] | – | 95 |
| hitab | gpt-5.4-mini | 0.792 | 0.802 [0.72, 0.87] | – | 95 |
| hitab | gpt-5.5 | 0.759 | 0.777 [0.70, 0.85] | – | 95 |
| hitab | gpt-oss-120b | 0.751 | 0.762 [0.68, 0.84] | – | 95 |
| hitab | grok-4 | 0.744 | 0.759 [0.68, 0.83] | – | 95 |
| hitab | llama-3.3-70b | 0.795 | 0.804 [0.73, 0.87] | – | 95 |
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
| magneto_gdc | claude-opus-5 | 0.964 | 0.966 [0.93, 0.99] | – | 93 |
| magneto_gdc | claude-sonnet-5 | 0.945 | 0.945 [0.90, 0.98] | – | 93 |
| magneto_gdc | deepseek-chat | 0.937 | 0.941 [0.89, 0.98] | – | 93 |
| magneto_gdc | deepseek-r1 | 0.973 | 0.976 [0.95, 1.00] | – | 93 |
| magneto_gdc | gemini-3.1-pro | 0.939 | 0.939 [0.89, 0.98] | – | 93 |
| magneto_gdc | gemini-3.8-flash | 0.954 | 0.958 [0.92, 0.99] | – | 93 |
| magneto_gdc | gpt-5.4-mini | 0.897 | 0.900 [0.84, 0.96] | – | 93 |
| magneto_gdc | gpt-5.5 | 0.962 | 0.968 [0.93, 0.99] | – | 93 |
| magneto_gdc | gpt-oss-120b | 0.953 | 0.957 [0.92, 0.99] | – | 93 |
| magneto_gdc | grok-4 | 0.926 | 0.931 [0.88, 0.97] | – | 93 |
| magneto_gdc | llama-3.3-70b | 0.657 | 0.663 [0.57, 0.75] | – | 93 |
| mmtu | claude-opus-5 | 0.883 | 0.833 [0.75, 0.92] | – | 87 |
| mmtu | claude-sonnet-5 | 0.883 | 0.833 [0.75, 0.92] | – | 87 |
| mmtu | deepseek-chat | 0.857 | 0.803 [0.71, 0.88] | – | 87 |
| mmtu | deepseek-r1 | 0.825 | 0.766 [0.67, 0.85] | – | 87 |
| mmtu | gemini-3.1-pro | 0.896 | 0.852 [0.76, 0.93] | – | 87 |
| mmtu | gemini-3.8-flash | 0.891 | 0.845 [0.76, 0.92] | – | 87 |
| mmtu | gpt-5.4-mini | 0.879 | 0.834 [0.75, 0.92] | – | 87 |
| mmtu | gpt-5.5 | 0.896 | 0.844 [0.76, 0.92] | – | 87 |
| mmtu | gpt-oss-120b | 0.821 | 0.753 [0.66, 0.85] | – | 87 |
| mmtu | grok-4 | 0.884 | 0.834 [0.75, 0.92] | – | 87 |
| mmtu | llama-3.3-70b | 0.809 | 0.764 [0.67, 0.85] | – | 87 |
| officeqa | claude-opus-5 | 0.405 | n/c | – | 100 |
| officeqa | claude-sonnet-5 | 0.337 | n/c | – | 100 |
| officeqa | deepseek-chat | 0.123 | n/c | – | 100 |
| officeqa | deepseek-r1 | 0.174 | n/c | – | 100 |
| officeqa | gemini-3.1-pro | 0.268 | n/c | – | 100 |
| officeqa | gemini-3.8-flash | 0.432 | n/c | – | 100 |
| officeqa | gpt-5.4-mini | 0.253 | n/c | – | 100 |
| officeqa | gpt-5.5 | 0.356 | n/c | – | 100 |
| officeqa | gpt-oss-120b | 0.175 | n/c | – | 100 |
| officeqa | grok-4 | 0.271 | n/c | – | 100 |
| officeqa | llama-3.3-70b | 0.224 | n/c | – | 100 |
| officeqa_pro_v2 | claude-opus-5 | 0.500 | 0.500 [0.43, 0.57] | – | 90 |
| officeqa_pro_v2 | claude-sonnet-5 | 0.319 | 0.319 [0.25, 0.38] | – | 90 |
| officeqa_pro_v2 | deepseek-chat | 0.279 | 0.279 [0.22, 0.33] | – | 90 |
| officeqa_pro_v2 | deepseek-r1 | 0.072 | 0.072 [0.04, 0.11] | – | 90 |
| officeqa_pro_v2 | gemini-3.1-pro | 0.266 | 0.266 [0.21, 0.33] | – | 90 |
| officeqa_pro_v2 | gemini-3.8-flash | 0.411 | 0.411 [0.35, 0.48] | – | 90 |
| officeqa_pro_v2 | gpt-5.4-mini | 0.320 | 0.320 [0.26, 0.38] | – | 90 |
| officeqa_pro_v2 | gpt-5.5 | 0.310 | 0.310 [0.23, 0.39] | – | 90 |
| officeqa_pro_v2 | gpt-oss-120b | 0.217 | 0.217 [0.16, 0.28] | – | 90 |
| officeqa_pro_v2 | grok-4 | 0.261 | 0.261 [0.20, 0.33] | – | 90 |
| officeqa_pro_v2 | llama-3.3-70b | 0.275 | 0.275 [0.22, 0.33] | – | 90 |
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
| realhitbench | claude-opus-5 | 0.777 | 0.778 [0.70, 0.84] | – | 98 |
| realhitbench | claude-sonnet-5 | 0.714 | 0.714 [0.64, 0.80] | – | 98 |
| realhitbench | deepseek-chat | 0.705 | 0.699 [0.62, 0.79] | – | 98 |
| realhitbench | deepseek-r1 | 0.708 | 0.709 [0.63, 0.79] | – | 98 |
| realhitbench | gemini-3.1-pro | 0.753 | 0.751 [0.67, 0.83] | – | 98 |
| realhitbench | gemini-3.8-flash | 0.789 | 0.788 [0.72, 0.86] | – | 98 |
| realhitbench | gpt-5.4-mini | 0.715 | 0.709 [0.62, 0.79] | – | 98 |
| realhitbench | gpt-5.5 | 0.767 | 0.764 [0.69, 0.84] | – | 98 |
| realhitbench | gpt-oss-120b | 0.652 | 0.653 [0.57, 0.74] | – | 98 |
| realhitbench | grok-4 | 0.686 | 0.684 [0.60, 0.77] | – | 98 |
| realhitbench | llama-3.3-70b | 0.640 | 0.647 [0.56, 0.73] | – | 98 |
| smat | claude-opus-5 | 0.913 | 0.911 [0.85, 0.96] | – | 98 |
| smat | claude-sonnet-5 | 0.920 | 0.918 [0.86, 0.96] | – | 98 |
| smat | deepseek-chat | 0.895 | 0.892 [0.83, 0.95] | – | 98 |
| smat | deepseek-r1 | 0.902 | 0.899 [0.84, 0.95] | – | 98 |
| smat | gemini-3.1-pro | 0.848 | 0.846 [0.77, 0.91] | – | 98 |
| smat | gemini-3.8-flash | 0.895 | 0.892 [0.83, 0.94] | – | 98 |
| smat | gpt-5.4-mini | 0.940 | 0.943 [0.90, 0.98] | – | 98 |
| smat | gpt-5.5 | 0.921 | 0.919 [0.87, 0.97] | – | 98 |
| smat | gpt-oss-120b | 0.893 | 0.888 [0.83, 0.94] | – | 98 |
| smat | grok-4 | 0.919 | 0.916 [0.86, 0.96] | – | 98 |
| smat | llama-3.3-70b | 0.728 | 0.724 [0.64, 0.80] | – | 98 |
| suc | claude-opus-5 | 0.998 | 0.998 [0.99, 1.00] | – | 99 |
| suc | claude-sonnet-5 | 0.950 | 0.948 [0.91, 0.98] | – | 99 |
| suc | deepseek-chat | 0.907 | 0.909 [0.86, 0.95] | – | 99 |
| suc | deepseek-r1 | 0.974 | 0.972 [0.95, 0.99] | – | 99 |
| suc | gemini-3.1-pro | 0.969 | 0.965 [0.94, 0.99] | – | 99 |
| suc | gemini-3.8-flash | 0.988 | 0.988 [0.97, 1.00] | – | 99 |
| suc | gpt-5.4-mini | 0.957 | 0.956 [0.92, 0.98] | – | 99 |
| suc | gpt-5.5 | 0.973 | 0.972 [0.95, 0.99] | – | 99 |
| suc | gpt-oss-120b | 0.957 | 0.956 [0.92, 0.98] | – | 99 |
| suc | grok-4 | 0.968 | 0.965 [0.94, 0.99] | – | 99 |
| suc | llama-3.3-70b | 0.833 | 0.836 [0.77, 0.89] | – | 99 |
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
| tabis | claude-opus-5 | 0.920 | 0.925 [0.88, 0.96] | – | 77 |
| tabis | claude-sonnet-5 | 0.881 | 0.879 [0.81, 0.93] | – | 77 |
| tabis | deepseek-chat | 0.744 | 0.690 [0.58, 0.78] | – | 77 |
| tabis | deepseek-r1 | 0.929 | 0.941 [0.92, 0.96] | – | 77 |
| tabis | gemini-3.1-pro | 0.910 | 0.930 [0.90, 0.96] | – | 77 |
| tabis | gemini-3.8-flash | 0.910 | 0.930 [0.90, 0.95] | – | 77 |
| tabis | gpt-5.4-mini | 0.864 | 0.868 [0.80, 0.92] | – | 77 |
| tabis | gpt-5.5 | 0.920 | 0.936 [0.91, 0.96] | – | 77 |
| tabis | gpt-oss-120b | 0.882 | 0.913 [0.88, 0.95] | – | 77 |
| tabis | grok-4 | 0.940 | 0.948 [0.93, 0.96] | – | 77 |
| tabis | llama-3.3-70b | 0.786 | 0.788 [0.70, 0.86] | – | 77 |
| tablebench | claude-opus-5 | 0.882 | 0.887 [0.83, 0.94] | – | 89 |
| tablebench | claude-sonnet-5 | 0.901 | 0.906 [0.86, 0.95] | – | 89 |
| tablebench | deepseek-chat | 0.868 | 0.884 [0.83, 0.93] | – | 89 |
| tablebench | deepseek-r1 | 0.826 | 0.838 [0.76, 0.90] | – | 89 |
| tablebench | gemini-3.1-pro | 0.884 | 0.886 [0.83, 0.94] | – | 89 |
| tablebench | gemini-3.8-flash | 0.871 | 0.876 [0.81, 0.93] | – | 89 |
| tablebench | gpt-5.4-mini | 0.873 | 0.876 [0.82, 0.93] | – | 89 |
| tablebench | gpt-5.5 | 0.882 | 0.886 [0.82, 0.94] | – | 89 |
| tablebench | gpt-oss-120b | 0.854 | 0.859 [0.80, 0.92] | – | 89 |
| tablebench | grok-4 | 0.853 | 0.858 [0.79, 0.92] | – | 89 |
| tablebench | llama-3.3-70b | 0.728 | 0.727 [0.65, 0.80] | – | 89 |
| tableeval | claude-opus-5 | 0.781 | 0.798 [0.70, 0.88] | – | 70 |
| tableeval | claude-sonnet-5 | 0.759 | 0.789 [0.69, 0.88] | – | 70 |
| tableeval | deepseek-chat | 0.741 | 0.737 [0.64, 0.83] | – | 70 |
| tableeval | deepseek-r1 | 0.788 | 0.772 [0.67, 0.87] | – | 70 |
| tableeval | gemini-3.1-pro | 0.796 | 0.806 [0.71, 0.90] | – | 70 |
| tableeval | gemini-3.8-flash | 0.788 | 0.808 [0.71, 0.89] | – | 70 |
| tableeval | gpt-5.4-mini | 0.775 | 0.783 [0.68, 0.87] | – | 70 |
| tableeval | gpt-5.5 | 0.800 | 0.805 [0.71, 0.89] | – | 70 |
| tableeval | gpt-oss-120b | 0.795 | 0.793 [0.70, 0.88] | – | 70 |
| tableeval | grok-4 | 0.806 | 0.794 [0.69, 0.89] | – | 70 |
| tableeval | llama-3.3-70b | 0.693 | 0.677 [0.57, 0.77] | – | 70 |
| tat_qa | claude-opus-5 | 0.833 | 0.801 [0.71, 0.89] | – | 61 |
| tat_qa | claude-sonnet-5 | 0.829 | 0.808 [0.73, 0.89] | – | 61 |
| tat_qa | deepseek-chat | 0.792 | 0.750 [0.65, 0.84] | – | 61 |
| tat_qa | deepseek-r1 | 0.791 | 0.757 [0.66, 0.85] | – | 61 |
| tat_qa | gemini-3.1-pro | 0.795 | 0.750 [0.65, 0.83] | – | 61 |
| tat_qa | gemini-3.8-flash | 0.807 | 0.777 [0.68, 0.86] | – | 61 |
| tat_qa | gpt-5.4-mini | 0.795 | 0.748 [0.66, 0.83] | – | 61 |
| tat_qa | gpt-5.5 | 0.803 | 0.768 [0.68, 0.85] | – | 61 |
| tat_qa | gpt-oss-120b | 0.780 | 0.722 [0.62, 0.81] | – | 61 |
| tat_qa | grok-4 | 0.793 | 0.733 [0.64, 0.82] | – | 61 |
| tat_qa | llama-3.3-70b | 0.757 | 0.699 [0.59, 0.80] | – | 61 |
| tpcdi_cells | claude-opus-5 | 0.423 | 0.452 [0.36, 0.54] | – | 95 |
| tpcdi_cells | claude-sonnet-5 | 0.423 | 0.452 [0.37, 0.54] | – | 95 |
| tpcdi_cells | deepseek-chat | 0.423 | 0.452 [0.37, 0.54] | – | 95 |
| tpcdi_cells | deepseek-r1 | 0.424 | 0.454 [0.36, 0.54] | – | 95 |
| tpcdi_cells | gemini-3.1-pro | 0.423 | 0.452 [0.36, 0.53] | – | 95 |
| tpcdi_cells | gemini-3.8-flash | 0.423 | 0.452 [0.36, 0.54] | – | 95 |
| tpcdi_cells | gpt-5.4-mini | 0.420 | 0.449 [0.36, 0.53] | – | 95 |
| tpcdi_cells | gpt-5.5 | 0.424 | 0.454 [0.37, 0.54] | – | 95 |
| tpcdi_cells | gpt-oss-120b | 0.404 | 0.440 [0.35, 0.52] | – | 95 |
| tpcdi_cells | grok-4 | 0.405 | 0.441 [0.36, 0.52] | – | 95 |
| tpcdi_cells | llama-3.3-70b | 0.404 | 0.440 [0.35, 0.53] | – | 95 |
| valentine | claude-opus-5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | claude-sonnet-5 | 0.991 | 0.985 [0.95, 1.00] | – | 82 |
| valentine | deepseek-chat | 0.974 | 0.958 [0.91, 1.00] | – | 82 |
| valentine | deepseek-r1 | 0.991 | 0.987 [0.96, 1.00] | – | 82 |
| valentine | gemini-3.1-pro | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | gemini-3.8-flash | 0.970 | 0.988 [0.97, 1.00] | – | 82 |
| valentine | gpt-5.4-mini | 0.982 | 0.972 [0.93, 1.00] | – | 82 |
| valentine | gpt-5.5 | 1.000 | 1.000 [1.00, 1.00] | – | 82 |
| valentine | gpt-oss-120b | 0.973 | 0.961 [0.91, 1.00] | – | 82 |
| valentine | grok-4 | 0.966 | 0.944 [0.88, 1.00] | – | 82 |
| valentine | llama-3.3-70b | 0.965 | 0.949 [0.90, 0.99] | – | 82 |
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
| wdc_products | grok-4 | 0.983 | 0.992 [0.98, 1.00] | 0.98 → 0.99 [0.96, 1.00] | 77 |
| wdc_products | llama-3.3-70b | 0.970 | 0.977 [0.94, 1.00] | 0.97 → 0.96 [0.90, 1.00] | 77 |
| wikitablequestions | claude-opus-5 | 0.883 | 0.882 [0.82, 0.94] | – | 98 |
| wikitablequestions | claude-sonnet-5 | 0.866 | 0.866 [0.80, 0.93] | – | 98 |
| wikitablequestions | deepseek-chat | 0.848 | 0.847 [0.78, 0.91] | – | 98 |
| wikitablequestions | deepseek-r1 | 0.850 | 0.848 [0.78, 0.91] | – | 98 |
| wikitablequestions | gemini-3.1-pro | 0.855 | 0.855 [0.79, 0.91] | – | 98 |
| wikitablequestions | gemini-3.8-flash | 0.882 | 0.883 [0.82, 0.94] | – | 98 |
| wikitablequestions | gpt-5.4-mini | 0.853 | 0.851 [0.78, 0.91] | – | 98 |
| wikitablequestions | gpt-5.5 | 0.864 | 0.862 [0.80, 0.92] | – | 98 |
| wikitablequestions | gpt-oss-120b | 0.826 | 0.823 [0.75, 0.89] | – | 98 |
| wikitablequestions | grok-4 | 0.867 | 0.865 [0.80, 0.93] | – | 98 |
| wikitablequestions | llama-3.3-70b | 0.758 | 0.758 [0.68, 0.83] | – | 98 |

## 5. Dataset diagnostics (under the ensemble)

| dataset | family | mean | spread | self-stability τ | τ to others | exclude |
|---|---|---|---|---|---|---|
| abt_buy | EM | 0.971 | 0.060 | 0.75 | +0.35 | False |
| alaska_camera | EM | 0.945 | 0.190 | 0.92 | -0.20 | False |
| alaska_schema | SM | 0.911 | 0.168 | 0.66 | -0.00 | False |
| amazon_google | EM | 0.935 | 0.100 | 0.65 | -0.02 | False |
| bird | TQA | 0.254 | 0.281 | 0.89 | +0.22 | False |
| dblp_acm | EM | 0.987 | 0.090 | 0.88 | +0.31 | False |
| dblp_scholar | EM | 0.948 | 0.060 | 0.71 | -0.03 | False |
| fetaqa | TQA | 0.557 | 0.411 | 0.74 | +0.20 | False |
| fintagging | SM | 0.830 | 0.076 | 0.64 | +0.30 | False |
| hitab | TQA | 0.776 | 0.072 | 0.60 | -0.15 | False |
| machamp | EM | 0.887 | 0.070 | 0.58 | +0.37 | False |
| magneto_gdc | SM | 0.919 | 0.315 | 0.70 | +0.24 | False |
| mmtu | TQA | 0.866 | 0.087 | 0.64 | +0.26 | False |
| officeqa | FIN | 0.274 | 0.309 | 0.91 | +0.28 | False |
| officeqa_pro_v2 | FIN | 0.294 | 0.428 | 0.84 | +0.19 | False |
| opensanctions_pairs | EM | 0.835 | 0.240 | 0.90 | +0.04 | False |
| papadakis_dn | EM | 0.940 | 0.030 | 0.74 | +0.03 | False |
| realhitbench | TQA | 0.719 | 0.150 | 0.78 | +0.34 | False |
| smat | SM | 0.889 | 0.212 | 0.69 | +0.17 | False |
| suc | TQA | 0.952 | 0.165 | 0.80 | +0.30 | False |
| tab_fact | TQA | 0.802 | 0.200 | 0.83 | +0.01 | False |
| tabis | TQA | 0.881 | 0.196 | 0.81 | +0.23 | False |
| tablebench | TQA | 0.857 | 0.173 | 0.67 | +0.21 | False |
| tableeval | TQA | 0.775 | 0.112 | 0.63 | +0.14 | False |
| tat_qa | FIN | 0.798 | 0.076 | 0.62 | +0.34 | False |
| tpcdi_cells | SM | 0.418 | 0.020 | 0.76 | +0.30 | False |
| valentine | SM | 0.983 | 0.035 | 0.70 | +0.24 | True |
| walmart_amazon | EM | 0.959 | 0.060 | 0.76 | +0.34 | False |
| wdc_lspc | EM | 0.982 | 0.040 | 0.79 | +0.25 | True |
| wdc_products | EM | 0.978 | 0.020 | 0.57 | +0.18 | True |
| wikitablequestions | TQA | 0.850 | 0.125 | 0.70 | +0.34 | False |

## 6. Reading

* v5 is the only version whose objective measures correctness (against anchors of known utility) rather than agreement; its ensemble is the headline scoring rule and the other rules here are the comparison points the paper needs (naive exact match, the dataset's own metric, the five best single weightings).
* Selection honesty is built into v5 differently from v2–v4: the top-100 average spreads selection risk and step 5 re-runs the selection leave-one-dataset-out and under utility perturbation; the nested item bootstrap of v2/v4 does not apply because the objective is not a function of the ranked models.
* Files: matrix_models.npz / matrix_anchors.npz, index_*.csv, metric_table.csv, clusters.json, selected.json, grid_all.csv (every weighting with every term), ensemble.json, baselines_grid.csv, validation.json, probes.csv, lodo.csv, designs.csv, leaderboards/<rule>/ (params with BT SE, Kemeny cost, bootstrap draws, significance), diagnostics/, notes/04_RESULTS.md.
