# Extension: KL and Jensen–Shannon divergence as consistency objectives

**Status: proposal + standalone demo. Not used by `scripts/rs/`.** Run the demo with
`uv run python extensions/divergence_extension.py` (reads the cached component matrix and the
calibrated weights, writes nothing).

## What the main pipeline measures, and what it misses
`scripts/rs/02_random_search.py` calibrates the composite weights `w` so that the *ranking* of
models induced by each dataset agrees with the pooled (Borda) ranking. Rankings are blind to the
score *scale*: two datasets can rank seven models identically while one gives gpt-5.5 a 0.9 and the
other a 0.4. If the goal is that "the same model performance looks the same across datasets", the
scale matters too. Divergence measures compare the full distribution of item-level scores and can
express that goal directly.

## The two divergences
For histograms `P` and `Q` of item scores (10 bins on [0, 1], `+ε` smoothing):

| | Formula | Properties | Use |
|---|---|---|---|
| KL | `KL(P‖Q) = Σ P_i log(P_i/Q_i)` | asymmetric; infinite if `Q` has an empty bin that `P` uses; unbounded | "how surprising is A's profile if I expected B's" |
| JS | `JS(P,Q) = ½KL(P‖M) + ½KL(Q‖M)`, `M=(P+Q)/2` | symmetric; bounded in `[0, ln 2]`; always finite | the objective term: bounded so it mixes with τ, symmetric so dataset order is irrelevant |
| W1 | 1-Wasserstein (earth mover's) | sensitive to location shifts even when histograms don't overlap | complement to JS; reported, not optimised |

## How it would enter the objective (variant 1: real models, difficulty-centred)
For each model `m` and dataset pair `(A, B)`, take the histograms of `m`'s item scores on `A` and
`B` **after subtracting each dataset's mean over all models** (otherwise the term measures
difficulty, not metric consistency), and average `JS` over models and pairs:

```
J(w) = a1 · mean_d τ( ranking_d(w), pooled ranking(w) )        # what scripts/rs uses today
     + a2 · ( 1 − mean_{m,(A,B)} JS(P_{m,A}, P_{m,B}) / ln 2 )   # this extension
```

The demo output on the cached data (4 models): mean JS/ln 2 across dataset pairs is 0.86 for
EM-only, 0.77 for the v1 hand-set rubric and 0.78 for the random-search weights. Graded weightings
produce more comparable score profiles than exact match; the ranking objective alone does not reduce
divergence further, which is exactly why adding this term would change the selected weights.

## Why divergence must not be used alone (the collapse)
A binary metric gives every dataset a Bernoulli score distribution; if failure is uniform the
histograms match perfectly and JS ≈ 0 while the metric measures nothing. In the demo, EM-only
reaches JS ≈ 0.005 between TabFact and TAT-QA for exactly this reason. Any divergence term therefore
needs a companion that anchors the score to correctness: the ranking term above, native-metric
fidelity, or (variant 2, used in the earlier ladder version implementation) synthetic systems of *known* quality
on every dataset, for which "same quality ⇒ same score distribution" is a clean target with no
difficulty confound.

## What implementing it would take
1. Add `js_term(w)` to `02_random_search.py` (function body is `divergence_report` in the demo file).
2. Add the mixing coefficient `a2` (start at 0.3) and re-run the 100-combination random search.
3. Report both terms per combination and the Pareto front (rank agreement vs. divergence), because
   the two goals conflict: distribution matching pulls toward binary indicators, rank agreement
   toward graded metrics.
