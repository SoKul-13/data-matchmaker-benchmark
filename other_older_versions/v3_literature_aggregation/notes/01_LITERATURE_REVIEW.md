# Ten papers on evaluating models evenly across datasets: summary, findings, math

Selected for direct relevance to "one score / one ranking across many datasets". For each: what it does,
what it found, the math it uses, and what we take from it. Sources listed at the end.

## 1. HELM — Holistic Evaluation of Language Models (Liang et al., 2022; Stanford CRFM)
**Does.** Evaluates many models on many scenarios with many metrics; the top-level number is the **mean win rate**.
**Math.** For metric m and scenario s, model i's win rate is the fraction of other models j it beats:
`WR_i(s) = (1/(M−1)) Σ_{j≠i} 1[score_i(s) > score_j(s)]` (ties ½); `MWR_i = mean over scenarios of WR_i(s)`.
**Findings.** MWR is scale-free (metrics with different units can be combined) but depends on which models are in the
pool and is gameable; HELM Capabilities (2025) moved to a rescaled mean score. **Take.** Win rate as one aggregation view.

## 2. What are the best systems? New perspectives on NLP benchmarking (Colombo, Noiry, Irurozki, Clémençon; NeurIPS 2022)
**Does.** Shows the arithmetic mean over tasks is fragile and proposes **Kemeny consensus ranking** over task-level or
instance-level rankings. **Math.** Kendall distance `d(σ,τ) = number of discordant pairs`; Kemeny consensus
`σ* = argmin_σ Σ_t d(σ, σ_t)` over task rankings σ_t (task level) or over instance-level rankings (σ^2l). Borda is the
positional approximation. **Findings.** Kemeny-based aggregation is more robust to adding/removing tasks or systems and
changes which systems come out best versus the mean. **Take.** Kemeny/Borda views; robustness to task removal as a test.

## 3. tinyBenchmarks: evaluating LLMs with fewer examples (Maia Polo et al., ICML 2024)
**Does.** Fits **item response theory** to benchmark items so a model's ability can be estimated from ~100 items.
**Math.** 2-parameter logistic IRT: `P(correct_{ij}) = σ(a_j (θ_i − b_j))` with model ability θ_i, item difficulty b_j,
discrimination a_j; ability estimated by maximum likelihood with item parameters fixed. **Findings.** IRT-based estimates
recover full-benchmark accuracy within ~2 points with 100 items; item information tells which items matter.
**Take.** A Rasch/IRT ability as an aggregation view; difficulty is estimated, not assumed.

## 4. Chatbot Arena (Chiang et al., ICML 2024; statistical framework at ICLR 2025)
**Does.** Ranks models from crowdsourced pairwise votes with the **Bradley–Terry** model instead of Elo.
**Math.** `P(i beats j) = σ(β_i − β_j)`; strengths β by maximum likelihood (logistic regression on pair indicators);
confidence intervals by bootstrap or sandwich estimator; active sampling of pairs to shrink intervals.
**Findings.** BT with CIs is stable where sequential Elo is order-dependent; crowd votes agree with experts.
**Take.** BT strength from per-item pairwise wins between models as a view; report CIs.

## 5. Open LLM Leaderboard v2 score normalisation (Hugging Face, 2024)
**Does.** Puts benchmarks with different chance levels on one 0–100 scale. **Math.** `norm = 100 · (raw − baseline) /
(max − baseline)` with baseline = random-guess score (e.g. 25 for 4-way MCQ, 50 for yes/no), clipped at 0.
**Findings.** Without it, easy and high-baseline tasks dominate the average; with it, gains on hard tasks count more.
**Take.** Baseline-corrected mean as a view (yes/no tasks: baseline 0.5; open answers: 0).

## 6. Efficient Benchmarking (of Language Models) (Perlitz et al., NAACL 2024)
**Does.** Studies how benchmark design (number of scenarios, examples, prompts) changes the reliability of rankings.
**Math.** **DIoR** (decision impact on reliability): the lower confidence bound of a meta-metric (e.g. Kendall τ of the
ranking under a cheaper setup vs the full benchmark) across resamples. **Findings.** Many examples can be dropped with
little loss if diversity is kept; reliability must be reported, not assumed. **Take.** Rank stability under item
resampling as the objective for choosing an aggregation, not a hand-picked rule.

## 7. Elo Uncovered (Boubdir et al., GEM 2023)
**Does.** Tests Elo ratings for LLM comparison against two axioms: reliability (same result under reordering /
resampling) and transitivity. **Math.** Elo update `R'_i = R_i + K (S − E)`, `E = 1/(1+10^{(R_j−R_i)/400})`;
tests via permutation of match order and bootstrap. **Findings.** Elo is volatile, depends on K and match order,
and can violate transitivity; recommends many permutations and reporting variance. **Take.** Do not use sequential
Elo; use batch BT; test transitivity of the pooled ranking.

## 8. Lessons from the Trenches on Reproducible Evaluation (Biderman et al., 2024; lm-evaluation-harness)
**Does.** Documents why evaluation results differ across papers (prompt formats, normalisation, scoring choices) and
gives a framework that fixes them. **Math.** Mostly protocol; emphasises reporting standard errors of the mean per
task (`SE = sd/√n`) and exact scoring rules. **Findings.** Small implementation differences change rankings.
**Take.** One prompt, one scoring rule, standard errors per dataset, published item ids.

## 9. Are Emergent Abilities of LLMs a Mirage? (Schaeffer, Miranda, Koyejo; NeurIPS 2023 outstanding paper)
**Does.** Shows that "emergence" often comes from **nonlinear or discontinuous metrics** (exact match) rather than
model behaviour; linear metrics (token edit distance) give smooth curves. **Math.** If per-token error ε is smooth in
scale, exact match on L tokens `(1−ε)^L` is sharply nonlinear while edit distance is linear in ε. **Findings.** Metric
choice alone can create or remove apparent jumps. **Take.** Prefer graded metrics (numeric decay, F1) over pure
exact match when comparing models; report both.

## 10. Do These LLM Benchmarks Agree? Fixing Benchmark Evaluation with BenchBench (Perlitz et al., 2024)
**Does.** Studies **benchmark agreement testing**: validating a benchmark by correlating its ranking with others.
**Math.** Kendall τ / Pearson between rankings; reference = aggregate of mean win rates over several benchmarks;
agreement thresholds set from the distribution of agreements among established benchmarks. **Findings.** Reference
choice, model subset and correlation metric change conclusions arbitrarily; use an aggregate reference, many models,
and report the distribution. **Take.** Report each dataset's agreement with the aggregate; use several models.

## What we take into the v3 pipeline
Aggregation **views** (each turns per-item native scores into one number per model):
`mean_raw` (naive), `baseline_norm_mean` (OLL v2), `z_mean` (standardised), `mean_win_rate` (HELM), `borda` (Colombo,
positional), `kemeny_score` (Colombo, consensus), `bradley_terry` (Arena, from per-item pairwise wins), `irt_ability`
(tinyBenchmarks, Rasch fit on item outcomes). The final score is a **convex combination of views**; its mixing weights
are grid-searched (100 candidates) with an objective from papers 6, 7 and 10: rank **stability** under item bootstrap,
**transitivity** (agreement of the mixed ranking with the pairwise-majority ranking) and **agreement with the
aggregate reference** (Kemeny consensus of all views).

## Sources
- HELM: https://arxiv.org/pdf/2211.09110 ; HELM Lite / Capabilities notes: https://crfm.stanford.edu/2023/12/19/helm-lite.html , https://crfm.stanford.edu/2025/03/20/helm-capabilities.html
- Colombo et al. 2022: https://arxiv.org/abs/2202.03799 ; code https://github.com/PierreColombo/RankingNLPSystems
- tinyBenchmarks: https://proceedings.mlr.press/v235/maia-polo24a.html ; https://github.com/felipemaiapolo/tinyBenchmarks
- Chatbot Arena: https://arxiv.org/abs/2403.04132 ; statistical framework: https://arxiv.org/pdf/2412.18407
- Open LLM Leaderboard normalisation: https://huggingface.co/docs/leaderboards/open_llm_leaderboard/normalization
- Efficient Benchmarking: https://aclanthology.org/2024.naacl-long.139/ ; https://arxiv.org/abs/2308.11696
- Elo Uncovered: https://aclanthology.org/2023.gem-1.28/
- Lessons from the Trenches: https://arxiv.org/abs/2405.14782
- Emergent abilities a mirage: https://arxiv.org/abs/2304.15004
- BenchBench: https://arxiv.org/abs/2407.13696
