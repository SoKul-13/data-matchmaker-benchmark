# v3 — aggregation methods from the literature, mixed by grid search

**Question.** Ten published papers each propose a way to turn many datasets into one model score. Which of their
rules should a data-matching leaderboard use, and can a grid search choose the mix instead of us?

**Step 1: the papers.** `notes/01_LITERATURE_REVIEW.md` summarises ten industry/workshop papers (HELM mean win rate;
Colombo et al. Kemeny consensus; tinyBenchmarks IRT; Chatbot Arena Bradley–Terry; Open LLM Leaderboard v2 baseline
normalisation; Perlitz's DIoR reliability; Elo Uncovered; Lessons from the Trenches; the Emergent-Abilities mirage paper;
BenchBench agreement testing), with each one's findings and math.

**Step 2: eight views.** `src/views.py` implements the aggregation rules the papers use. Every view maps the per-item
scores of each dataset's **own metric** (no composite) to one number per model:

| view | paper | formula (per model m) |
|---|---|---|
| mean_raw | baseline | mean over datasets of the dataset mean |
| baseline_norm_mean | Open LLM LB v2 | mean over d of (S_md − b_d)/(1 − b_d), clipped at 0, b_d = random-guess score |
| z_mean | standardisation | mean over d of (S_md − mean_d)/sd_d |
| mean_win_rate | HELM | mean over d of the fraction of other models beaten on d |
| borda | Colombo (positional) | mean over d of (M − rank_d(m)) |
| kemeny_score | Colombo (consensus) | M − position in the Kemeny consensus of the per-dataset rankings |
| bradley_terry | Chatbot Arena | strength β_m from per-item pairwise wins, P(m beats k) = σ(β_m − β_k), MLE |
| irt_ability | tinyBenchmarks | ability θ_m in the Rasch model P(correct) = σ(θ_m − b_item), joint MLE |

**Step 3: grid search over the mix.** Each view is standardised across models; a candidate is a weight vector `w` on the
simplex over the 8 views and the mixed score is `Σ_v w_v · z(view_v)`. Candidates: 8 single-view corners, the uniform mix,
and 100 random step-0.05 grid points (109). The objective follows papers 6, 7 and 10:

    J(w) = 0.5·stability + 0.25·transitivity + 0.25·reference
    stability   = mean τ between the mixed ranking on 100 item-bootstrap resamples and on the full data   (Perlitz)
    transitivity= τ between the mixed ranking and the pairwise-majority (Copeland) ranking                (Elo Uncovered)
    reference   = τ between the mixed ranking and the Kemeny consensus of the 8 single-view rankings      (BenchBench)

**Result** (`output/leaderboard.md`, `best.json`, `fig_views.png`). The eight views agree on the top model (gpt-5.5) and
disagree on the middle: raw means put claude-sonnet-5 last, every rank-based or pairwise view puts it second, which is
exactly Colombo et al.'s point about the arithmetic mean. The best candidate is the pure **Bradley–Terry** view (J = 0.867: stability 0.90, transitivity 1.0, reference 0.67), ahead of Kemeny (0.818), IRT ability (0.815), z-mean (0.788) and the uniform mix (0.798); raw mean (0.547) and baseline-normalised mean (0.458) are least stable. Final ranking gpt-5.5 > claude-sonnet-5 > claude-opus-5 > gpt-5.4-mini;
the item-bootstrap intervals show the top rank is certain and ranks 2–4 overlap, as with 4 models they must.

**Run.** `uv sync && scripts/run_all.sh` (about one minute; the bootstrap refits BT and IRT 100 times).
