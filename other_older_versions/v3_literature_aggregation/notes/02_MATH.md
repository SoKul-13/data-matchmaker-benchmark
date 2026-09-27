# v3 math, line by line

**Per-item scores.** s(m,d,i) ∈ [0,1] from the dataset's native metric (accuracy for yes/no, exact match for spans,
1 % numeric tolerance for numbers, ROUGE-L for sentences). Random baseline b_d = ½·(share of yes/no items in d).
**Per-dataset means.** S_md = mean_i s(m,d,i).

**Views** (one number per model):
1. mean_raw: (1/D) Σ_d S_md
2. baseline_norm_mean: (1/D) Σ_d max(0, (S_md − b_d)/(1 − b_d))
3. z_mean: (1/D) Σ_d (S_md − μ_d)/σ_d, μ_d, σ_d over models
4. mean_win_rate: (1/D) Σ_d (1/(M−1)) Σ_{k≠m} [1(S_md > S_kd) + ½·1(S_md = S_kd)]
5. borda: (1/D) Σ_d (M − rank_d(m))
6. kemeny_score: M − π*(m) where π* = argmin_π Σ_d d_K(π, rank_d), d_K = number of discordant pairs (exact over M! permutations for M ≤ 9)
7. bradley_terry: maximise Σ_{m≠k} W_mk log σ(β_m − β_k) − 0.01‖β‖², W_mk = number of items where s(m,·) > s(k,·) (ties ½); β_1 fixed at 0 then centred
8. irt_ability (Rasch): y_{mi} = 1[s(m,i) ≥ 0.5]; maximise Σ_{m,i} y log σ(θ_m − b_i) + (1−y) log(1 − σ(θ_m − b_i)) − ridge; report centred θ_m

**Standardisation.** z(view)_m = (view_m − mean over models)/sd over models, so a weight of 0.3 means the same thing for every view.
**Mix.** score_w(m) = Σ_v w_v z_v(m), w ∈ Δ⁷ (8 views). Grid: coordinates in {0, 0.05, …}; 100 random points + corners + uniform.
**Objective.** J(w) = 0.5·stab + 0.25·trans + 0.25·ref with
* stab = (1/B) Σ_b τ(rank(score_w on bootstrap b), rank(score_w)), B = 100 resamples of items within each dataset, views recomputed per resample
* trans = τ(rank(score_w), Copeland ranking of the S_md table)
* ref = τ(rank(score_w), Kemeny consensus of the 8 single-view rankings)
**Uncertainty.** Rank of each model under the best w on every bootstrap resample → 2.5/97.5 percentiles.
**Kendall τ-b** throughout: (concordant − discordant)/√((n₀ − n₁)(n₀ − n₂)), which discounts ties.
