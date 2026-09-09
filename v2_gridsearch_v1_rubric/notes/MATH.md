# v2 math, line by line

**Inputs.** For model m, dataset d, item i: a prediction p and a gold g (with aliases). Four ingredient scores in [0,1]:
* token F1: with C = common tokens of p and g, P = C/|p|, R = C/|g|, F1 = 2PR/(P+R)
* numeric decay: RE = |p_num − g_num| / |g_num| (unit/percent aware), decay = exp(−2.5·min(RE, 2)); for non-numeric golds decay = exact match
* precision P, recall R as above

**Composite.** R_w = w₁·F1 + w₂·decay + w₃·P + w₄·R, weights on the simplex Δ³ = {w ≥ 0, Σw = 1}.
**Grid.** Points of Δ³ with coordinates in {0, 0.05, …, 1}: C(23,3) = 1,771 points; 100 sampled with a fixed seed + v1 + 4 corners.
**Per-dataset score.** S_w(m,d) = mean_i R_w(m,d,i).
**Per-dataset ranking.** σ_d = ranks of models by S_w(·,d) (ties averaged).
**Pooled ranking.** Borda points b(m) = Σ_d (M − σ_d(m)); σ* = ranks by b.
**Objective.** J(w) = (1/D) Σ_d τ(σ_d, σ*), Kendall τ-b.
**Native fidelity.** τ_nat(w) = (1/D) Σ_d τ(σ_d, σ_d^native), where σ_d^native ranks models by the dataset's own metric.
**Bootstrap.** Resample items within each dataset with replacement, recompute S_w, σ_d, σ*, J; 200 times; report the 2.5/97.5 percentiles.
**Why J can only take few values.** With M = 4 models τ has C(4,2) = 6 pairs, so τ ∈ {−1, −⅔, −⅓, 0, ⅓, ⅔, 1} and J is a mean of seven such numbers.
