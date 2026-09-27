# Design space: every way each part of this project can be done

Purpose: before deciding what a v3 should be, see all the choices per stage, what each one buys
and costs, and what is already built. Read top to bottom; §12 turns it into a decision flow and
§13 into three concrete bundles.

Legend for the "status" column: **v2** = implemented and used in `v4_random_search_rank_agreement/`; **v2-opt** = implemented in
`v4_random_search_rank_agreement/` but not used by default; **ladder** = was implemented in the archived ladder version (design
retained in docs, code deleted); **sketch** = designed, not built; **—** = not built.

The original goal, split into its parts:

```
[A] datasets  ->  [B] score one answer  ->  [C] aggregate within a dataset  ->  [D] normalise across datasets
      ->  [E] what "same scoring across datasets" means (the calibration target)
      ->  [F] which weights are being calibrated  ->  [G] how they are searched
      ->  [H] pool rankings / ensemble across datasets  ->  [I] dataset weights inside the pool
      ->  [J] uncertainty and validation  ->  [K] distance / KL / JS  ->  [L] gaming resistance
      ->  [M] deployment in the green agent  ->  [N] the paper's claim
```

---

## 0. What "weights" can mean (the choice that shapes everything else)

| # | Weights over… | One weight per… | What calibrating them achieves | Status |
|---|---|---|---|---|
| W1 | **component metrics** (EM, NumTol, F1, ROUGE-L, …) | metric | one answer-level score that behaves alike across datasets | v2 |
| W2 | **component metrics per answer type** (numeric / boolean / text / free-form) | metric × type | same as W1 but numeric and free-form answers get different mixes | ladder |
| W3 | **datasets** | dataset | how much each dataset counts in the common score / pooled rank | v2-opt (informativeness weights), sketch (grid) |
| W4 | **items** | item | difficulty / discriminativeness weighting (IRT); hard items count more | — |
| W5 | **normalisation parameters** | dataset | offset/scale per dataset so that scores are comparable (z, min-max, quantile) | v2 (z-mean reported), sketch (grid over choices) |
| W6 | **penalty parameters** | behaviour | hedge penalty λ, verbosity penalty, abstention value | ladder |
| W7 | **model strengths** (latent) | model | not weights of the metric but parameters of a Bradley–Terry / IRT model fitted to outcomes | — |
| W8 | **objective mixing coefficients** α | objective term | which calibration targets matter how much | v2 (single term), ladder (nine terms) |
| W9 | **W1 + W3 jointly** | metric and dataset | answer-level comparability and dataset importance at once; risk of over-fitting | — |

Rule of thumb: W1/W2 make *answers* comparable; W3–W5 make *datasets* comparable; W7 replaces
"score then rank" with a statistical model; W8 is a meta-choice. A paper can defend at most two
of these being *searched*; the rest must be fixed by convention and stated.

---

## A. Datasets

| Option | Description | Pros | Cons | Status |
|---|---|---|---|---|
| A1 original catalogue | the 7 v1 datasets | continuity, all standard | OfficeQA is closed-book (floor); TabFact/TAT-QA at ceiling; no matching task | v2 |
| A2 add data-matching proper | Magellan EM (4), WDC Products, TPC-DI cells | matches the benchmark's name; boolean anchors; cheap prompts | boolean tasks only test one skill | v2 (pools built, run pending) |
| A3 add hierarchical / long-doc | HiTab, MultiHiertt, DocFinQA | harder, closer to real reports | DocFinQA expensive and overlaps FinQA; MultiHiertt on Google Drive | v2 (HiTab built; DocFinQA disabled; MultiHiertt optional) |
| A4 add general anchors | GSM8K, BoolQ, TabMWP | pure numeric / boolean anchors for calibration | not data-matching; dilutes the paper's scope | ladder |
| A5 add analysis / SQL | DataBench, BIRD, Spider 2.0 | agentic data work | needs code execution in the judge | — |
| A6 item count | 40 / 100 / 150 per dataset | 150 halves bootstrap interval width vs 40 | cost ∝ items × models | v2: 40 old, 150 new |
| A7 stratification | by answer type / difficulty / label balance | avoids type imbalance driving W1 | needs the labels | v2 |

Selection criteria to state in the paper: standard and cited; public and reproducible; covers the
modalities (record pairs, tables, table+text, documents) and answer types; not saturated for the
models tested; ≥ 100 items.

## B. Scoring one answer

| Option | Description | Pros | Cons | Status |
|---|---|---|---|---|
| B1 native metric only | each dataset's official metric (accuracy, EM, numeric tolerance, ROUGE-L) | no W1 at all; authors' intent; simplest story | scores mean different things per dataset; needs D/E to compare | v2-opt (native_value stored) |
| B2 lexical composite | weighted sum of 9 lexical components | graded credit; one scale; gold aliases / units / lists | weights must be chosen (W1); paraphrase-blind | v2 |
| B3 composite + semantic | add embedding cosine (e.g. sentence embeddings) as a 10th component | catches paraphrase on free-form | needs an embedding model; still not "correctness" | — |
| B4 composite + LLM judge | add a judge-model correctness probability as a component | closest to human judgement | cost; judge bias; must be calibrated itself | — |
| B5 execution-based | run the model's program/SQL and compare outputs | exact for numeric/SQL | only where programs exist (FinQA programs, BIRD) | — |
| B6 human labels | annotate a sample of answers as correct / partial / wrong | the true reference for calibration | cost; agreement study needed | — |
| B7 multiplicative gates | hedge penalty (1 − λ·hedged), length/verbosity penalty | gaming resistance | one more parameter; conflicts with native fidelity | ladder |

## C. Aggregate within a dataset (items → one number per model)

| Option | Pros | Cons | Status |
|---|---|---|---|
| C1 mean | standard | sensitive to a few hard items | v2 |
| C2 trimmed mean / median | robust | discards information | — |
| C3 IRT ability | accounts for item difficulty; comparable across item subsets | needs many models/items to fit | — |
| C4 pairwise win rate vs other models | scale-free | loses absolute level | — |

## D. Normalise across datasets (make dataset columns comparable)

| Option | Effect | When | Status |
|---|---|---|---|
| D1 none (raw) | dataset difficulty dominates the mean | never as headline | v2 (reported) |
| D2 z-score per dataset | removes level and spread | default for a common score | v2 (z-mean) |
| D3 min-max per dataset | 0 = worst model, 1 = best | intuitive; unstable with few models | sketch |
| D4 rank per dataset | fully scale-free | throws away margins | v2 (via pooling) |
| D5 quantile / distribution matching | equalise the whole score distribution | needs many items; this is where JS/W1 belong | ladder (JS in objective) |
| D6 difficulty-adjusted (IRT) | principled, item-level | heavy | — |
| D7 relative to a reference model | "vs GPT-x" scale | depends on one model | — |

## E. The calibration target: what "same scoring across datasets" means

| Option | Measured by | Needs | Blind spot | Status |
|---|---|---|---|---|
| E1 rank agreement among datasets | mean Kendall τ to pooled rank | real models only | satisfied by a metric that blurs differences | v2 (the objective) |
| E2 score-scale agreement | dispersion of a model's centred score across datasets | real models | conflates with genuine strengths | v2 (reported) |
| E3 distribution matching | JS / KL / W1 between datasets' item-score histograms | real models or anchors | binary metrics win trivially (uniform failure) | ladder (objective), v2 (extension) |
| E4 known-quality anchors | τ / ρ / MAE of scores vs synthetic systems of known quality and severity | a severity scale | scale is hand-set | ladder |
| E5 human-judgement fidelity | correlation with human correctness labels | annotation | cost | — |
| E6 native-metric fidelity | τ between composite and native rankings | nothing extra | anchors to possibly flawed native metrics | v2 (reported), ladder (objective) |
| E7 gaming resistance | scores of probe answers (hedge, dump, abstain) | probes | needs B7 to act on | ladder |
| E8 stability under resampling | bootstrap variance of pooled rank | nothing extra | prefers coarse metrics | v2-opt |
| E9 multi-objective | weighted sum of several of E1–E8 with α (W8) | choices of α | more knobs | ladder |

## F. Which weights are calibrated (pick from §0)

| Bundle | Searched | Fixed by convention | Status |
|---|---|---|---|
| F1 | W1 (9 metric weights) | equal dataset weights, z-mean | v2 |
| F2 | W2 (per-type metric weights) + W6 (λ) | equal dataset weights | ladder |
| F3 | W3 (dataset weights) | native metric per dataset (B1) | sketch (the interrupted v3) |
| F4 | nothing; report the whole grid of W3 as a sensitivity analysis | native metric, equal weights headline | sketch |
| F5 | W1 then W3 sequentially | — | — |
| F6 | W7 (Bradley–Terry strengths) | native metric per dataset | — |

## G. Search method

| Option | Pros | Cons | Status |
|---|---|---|---|
| G1 hand-set | none | the v1 problem | v1 |
| G2 random search, N points on a grid | stated budget; cheap | may miss optimum; N is arbitrary | v2 (N = 100) |
| G3 exhaustive grid | finds the grid optimum | 10^5–10^6 evaluations (still seconds–minutes here) | ladder |
| G4 coarse-to-fine (grid then local moves) | near-continuous optimum | more code | ladder |
| G5 Bayesian optimisation | sample-efficient for expensive objectives | overkill; objective is cheap | — |
| G6 gradient / convex (if objective smooth) | exact | τ is not smooth; needs a surrogate | — |
| G7 constrained search (e.g. EM ≥ 0.1, native fidelity ≥ 0.8) | encodes policy | policy must be argued | — |
| G8 no search: full-grid sensitivity report | nothing to defend; shows robustness | no "best" weights to publish | sketch |

Selection inside a tie set (needed with G2–G4 when τ is coarse): native fidelity → sparsity →
bootstrap selection frequency (v2 protocol, PIPELINE_AND_DATASETS.md §4).

## H. Pooling rankings across datasets (ensemble)

| Option | Type | Pros | Cons | Status |
|---|---|---|---|---|
| H1 mean score | positional | simplest | difficulty-dominated | v2 |
| H2 mean-z | positional | difficulty-adjusted | — | v2 |
| H3 mean rank / Borda | positional | standard; = each other | ignores margins | v2 (headline) |
| H4 Copeland | pairwise | Condorcet-consistent | coarse | v2 |
| H5 Kemeny–Young | pairwise | optimal consensus (min Kendall distance) | NP-hard beyond ~10 systems | v2 |
| H6 RRF | positional | robust to outlier datasets | arbitrary constant | v2 |
| H7 Schulze / ranked pairs / minimax | pairwise | strong Condorcet rules | — | — |
| H8 MC4 (Markov chain) | pairwise | robust to partial lists | — | — |
| H9 Bradley–Terry / Plackett–Luce | probabilistic | strength + standard error | needs pairwise/listwise outcomes | — |
| H10 mean win rate (HELM) | pairwise | scale-free, simple | — | — |
| H11 IRT / Bayesian hierarchical | probabilistic | item difficulty + model ability jointly | heavy | — |

## I. Dataset weights inside the pool (W3)

| Option | Pros | Cons | Status |
|---|---|---|---|
| I1 equal | no argument needed | saturated datasets count fully | v2 |
| I2 informativeness (inverse bootstrap rank variance) | down-weights noisy/saturated datasets | data-driven, may look self-serving | v2-opt |
| I3 size-proportional | more items = more weight | conflates size with importance | — |
| I4 tier / expert importance | reflects the paper's priorities | subjective | — |
| I5 medoid weighting (most central on the grid) | untuned, defensible | unfamiliar to readers | sketch |
| I6 full-grid sensitivity (P(rank) over all weightings, adversarial best/worst weights) | shows how much weighting matters | no single answer | sketch |
| I7 searched to an objective (E1/E8) | optimises something stated | the pooled rank is tuned to itself | — |

## J. Uncertainty and validation

| Option | Answers | Status |
|---|---|---|
| J1 item bootstrap | how much do ranks / J move if items were resampled | v2 |
| J2 dataset bootstrap | how much does the pooled rank depend on which datasets are in | — |
| J3 leave-one-dataset-out | do weights transfer to an unseen dataset | v2 |
| J4 Friedman + Nemenyi critical difference | are models statistically separable across datasets | — |
| J5 permutation test on J | is the calibrated J better than chance | — |
| J6 prompt / seed / temperature variation | is the leaderboard robust to the prompt | — |
| J7 α-sensitivity, severity-scale perturbation | are the calibrated weights robust to the objective's knobs | ladder |
| J8 selection-frequency across resamples | how often the same weights win | sketch |

## K. Distance / KL / JS: where they can sit

| Placement | Role | Status |
|---|---|---|
| K1 in the objective (E3) | forces score distributions to match across datasets at matched quality | ladder |
| K2 diagnostic after calibration | reports how comparable score profiles are | v2 (extension file) |
| K3 as a normalisation (D5) | quantile-map each dataset's scores onto a reference | — |
| K4 not used | — | — |

Measures: JS (bounded, symmetric: objective-safe), symmetric KL (unbounded, needs smoothing),
Wasserstein-1 (location-sensitive), plus plain distances between score vectors (L1/L2 of the model
× dataset table after centring). All need an anchor (E1/E4/E5) or they are minimised by uniform failure.

## L. Gaming resistance

| Option | Status |
|---|---|
| L1 answer-format instruction + final-answer extraction | v2 |
| L2 hedge detection + multiplicative penalty λ | ladder |
| L3 probe systems (tagged / dump / unit variant / hedge / abstain / random) in the objective | ladder |
| L4 length or verbosity penalty | — |
| L5 LLM-judge for commitment | — |

## M. Deployment in the green agent

| Option | Status |
|---|---|
| M1 composite score with calibrated weights inside the judge (QA mode) | ladder |
| M2 native metric per dataset, calibration offline only | v2 |
| M3 both reported per item | — |

## N. What the paper claims (pick one; it determines A–M)

| Claim | Needs | Bundle |
|---|---|---|
| N1 "a metric that scores the same quality the same way across datasets" | E4 or E5 anchors, W1/W2, K1 | the ladder design |
| N2 "one common score / leaderboard across data-matching datasets, with weights chosen by grid search" | E1 (+E2/E6 reported), W1 or W3, G2/G3, H3+H5, J1+J3 | v2 (W1) or v3-sketch (W3) |
| N3 "how much does the leaderboard depend on weighting" (robustness paper) | B1, F4/I6, J1/J2/J4 | v3-sketch |
| N4 "a validated composite metric for financial/table QA" (metric paper) | B3/B4, E5 human labels, J6 | new work |

---

## 12. Decision flow (text flowchart)

```
Q1  What is the headline claim?  (§N)
    ├─ N3 robustness  ──────────────────────────────►  B1 native metrics, D2 z, F4 no search,
    │                                                   I6 full-grid sensitivity, H3+H5, J1+J2+J4
    ├─ N2 common score by grid search
    │     Q2  Are answers comparable across datasets already?
    │         ├─ yes, accept native metrics (B1) ───►  calibrate W3 (F3): G3 exhaustive over dataset weights,
    │         │                                         objective E8 stability or I5 medoid; report I6; J1+J3
    │         └─ no, need one answer scale (B2) ────►  calibrate W1 (F1) = v2; add tie-set selection (G2 + fidelity),
    │                                                   J1+J3+J5; keep K2 as diagnostic
    ├─ N1 metric invariance ───────────────────────►  need anchors: E4 synthetic ladder (cheap) or E5 human labels (best);
    │                                                   W2 + W6, G3/G4, K1 in objective, L2+L3
    └─ N4 metric paper ─────────────────────────────►  B3/B4 components, E5 labels, agreement study, J6
Q3  Models: ≥ 8 industry-standard systems?  if no → any weight claim needs J1 intervals and a stated sample-size limit
Q4  Datasets: does the suite contain data-matching proper (A2)?  if no → rename the claim or add A2
Q5  Money: DocFinQA-type long contexts?  only if N4 or long-doc is the claim
```

## 13. Three coherent bundles to choose from

| | **Bundle 1: keep v2** | **Bundle 2: native + dataset-weight grid** (the interrupted v3) | **Bundle 3: anchored metric** (ladder, rebuilt) |
|---|---|---|---|
| Claim | N2 | N2 / N3 | N1 |
| Answer score | B2 lexical composite | B1 native metric per dataset | B2 (+B3 if affordable) |
| Weights searched | W1 metric weights | W3 dataset weights (or none: F4) | W2 per-type + W6 λ |
| Target | E1 rank agreement (+E2, E6 reported) | E8 stability / I5 medoid, or no target | E4 anchors + E3 JS + E6 + E7 |
| Search | G2 100 random + tie-set rule | G3 exhaustive over datasets (thousands) | G3/G4 |
| Pooling | H3 Borda headline, H5 check | H3 + H9 Bradley–Terry | H3 + H5 |
| Dataset weights | I1 equal | I6 full-grid sensitivity, I5 medoid | I1 |
| Validation | J1, J3 | J1, J2, J4 | J1, J3, J7 |
| KL/JS | K2 diagnostic | K2 | K1 in objective |
| Reviewer's likely objection | "weights tuned to make datasets agree" | "you never calibrated the metric" | "synthetic anchors, hand-set severity" |
| Best when | you want a simple, stated recipe and a leaderboard | you distrust composite weights and want a robustness story | you need to claim the metric itself is fair |
| Cost to build from here | 0 | ~1 day | ~3 days (code deleted; design documented) |

A defensible hybrid: Bundle 2 for the headline leaderboard (nothing tuned), Bundle 1's composite
reported as a secondary metric, and Bundle 3's anchors as the validation section. That combination
answers each objection with the other bundle's strength; its cost is length.

---

## 14. Recommended combination (hybrid) and how it compares

```
                    ┌──────────────────────────────────────────────────────────────┐
                    │ A. DATASETS: 6 tier-2 QA sets (FinQA, TAT-QA, WTQ, TabFact,   │
                    │    FeTaQA, FinanceBench) + HiTab + 6 tier-1 matching sets      │
                    │    (Abt-Buy, Amazon-Google, DBLP-Scholar, Walmart-Amazon, WDC,  │
                    │    TPC-DI cells). 150 items each. OfficeQA out (closed-book).  │
                    └──────────────────────────────┬───────────────────────────────┘
                                                   ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │ B. SCORE EACH ANSWER TWO WAYS                                  │
                    │   B1 native metric of the dataset  (accuracy / EM / NumTol /   │
                    │      ROUGE-L)                       -> drives the LEADERBOARD  │
                    │   B2 lexical composite, weights W2 per answer type + hedge λ   │
                    │      -> the SECONDARY metric, must earn its place in Track 2   │
                    └──────────────┬─────────────────────────────────┬─────────────┘
                                   ▼                                 ▼
     TRACK 1  LEADERBOARD (nothing tuned)            TRACK 2  METRIC CALIBRATION (tuned, but not on the models)
     ┌────────────────────────────────────┐          ┌──────────────────────────────────────────────────┐
     │ C1 mean native score per dataset    │          │ E4 anchors: synthetic systems of known quality q  │
     │ D2 z-normalise per dataset          │          │    with an explicit severity scale (+ E7 probes)  │
     │ I1 equal dataset weights = headline │          │ target = τ(q order) + ρ/MAE(severity) + E3 JS     │
     │ I6 full grid over dataset weights:  │          │    across datasets/styles + E6 native fidelity    │
     │    P(rank) per model, best/worst    │          │ G3 exhaustive simplex grid (step 0.1) + G4 refine │
     │    achievable rank, medoid weights  │          │ J3 LODO, J7 α + severity perturbation             │
     │ H3 Borda headline, H5 Kemeny check, │          │ output: W2 weights, λ; report the composite       │
     │ H9 Bradley–Terry strength ± SE      │          │    leaderboard next to Track 1 and their τ         │
     │ J1 item bootstrap, J4 Friedman-     │          └──────────────────────────────────────────────────┘
     │    Nemenyi critical difference      │
     └────────────────────────────────────┘
                                   ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │ K2 DIAGNOSTIC: JS / KL / W1 between datasets' score           │
                    │    distributions under native vs composite (not optimised)     │
                    │ M3 GREEN AGENT reports both scores per item                   │
                    │ N  CLAIM: "one common leaderboard across data-matching         │
                    │    datasets that does not depend on tuned weights, plus a      │
                    │    calibrated composite whose fairness is validated against    │
                    │    known-quality anchors"                                      │
                    └──────────────────────────────────────────────────────────────┘
```

Why this shape: the two things reviewers attack are "weights were tuned to make the datasets agree"
(a Track-1-only or v2-style design) and "you never showed the metric is fair" (a native-only design).
Splitting the tuned part (Track 2) from the ranked part (Track 1) means the leaderboard cannot be
accused of circularity, and the metric's calibration is judged against anchors whose quality is
known, not against the very models being ranked.

### Side by side

| | **current v2** | **interrupted v3 plan** | **recommended hybrid** |
|---|---|---|---|
| Answer score | lexical composite only (W1) | native metric only (B1) | both: native (leaderboard) + composite (secondary) |
| What is searched | 9 metric weights, one global vector, 100 random grid points | dataset weights, exhaustive grid, or nothing (sensitivity only) | Track 2: per-type metric weights + λ, exhaustive grid; Track 1: nothing (full-grid sensitivity reported) |
| Calibration target | rank agreement among real models (E1) | stability / medoid over dataset weightings (E8/I5) or none | known-quality anchors + severity scale + JS + native fidelity (E4+E3+E6+E7) |
| Circularity risk | high: weights chosen so the models' datasets agree | none for weights; leaderboard depends on dataset weighting | none for the leaderboard; Track 2 tuned on anchors, not models |
| Pooling | Borda headline; Kemeny, Copeland, RRF checks | Borda + Bradley–Terry | Borda + Kemeny + Bradley–Terry ± SE |
| Dataset weights | equal | equal headline + full grid P(rank) + adversarial + medoid | same as v3 |
| Uncertainty | item bootstrap, LODO | item bootstrap, dataset bootstrap, Friedman–Nemenyi | all of those + α/severity perturbation for Track 2 |
| KL/JS | diagnostic extension only | diagnostic | in Track 2 objective (anchored) + diagnostic |
| Gaming resistance | format instruction only | same | hedge gate λ + probes (Track 2) |
| Green agent | unchanged v1 | unchanged | reports native + composite per item (QA mode) |
| Paper claim | "weights by random search make datasets agree" | "leaderboard robust to dataset weighting" | both, and "composite validated on anchors" |
| Main weakness | objective gameable by blandness; 4 models × 40 items | metric never validated; native metrics differ in kind | longest paper; severity scale is a stated choice |
| Build cost from now | done | ~1 day | ~3–4 days (anchor code must be rebuilt; design fully documented) |
| Reuses | cached predictions | cached predictions | cached predictions + new-dataset run (~$22) |

### What the hybrid gives up
Simplicity of message. It is two results, not one. If the venue wants a short paper, drop Track 2
to an appendix and lead with Track 1 (this is Bundle 2); if the venue is metrics-focused, lead with
Track 2 and make Track 1 the application (Bundle 3).

---

## 15. If the goal is "rank model capability on ANY new data-matching dataset"

That is a generalisation claim, not a leaderboard claim: the method must work on a dataset it has
never seen, without re-tuning, and its ranking there must be trustworthy. Three ingredients make
that possible; the current v2 has the first, half of the second, none of the third.

### Ingredient 1: a dataset-agnostic scorer (no per-dataset tuning)
The scoring rule may depend on the *answer type* of an item, never on the dataset. So:
- one adapter interface (question, context/records, gold, aliases, answer type, native metric);
- a typed scoring rule fixed in advance: boolean → accuracy, numeric → 1 % tolerance with unit/percent
  equivalence, short text/list → normalised EM (set equality for lists), free-form → ROUGE-L (or the
  anchored composite of §14 Track 2, which is also typed and fixed once calibrated);
- no dataset-specific weights, thresholds or prompt tweaks. For entity matching in particular:
  balanced match / non-match sampling and a fixed prompt template, so base rates never enter.
Status: built (adapters + typed native metrics + composite).

### Ingredient 2: a latent capability model (capability is a parameter, not a mean score)
Replace "mean score per dataset, then pool" with a model in which each LLM has one **ability** θ_m
and each dataset (or item) has a **difficulty** b_d (and optionally a discrimination a_d):

    P(model m answers item i of dataset d correctly) = σ( a_d (θ_m − b_d) )          (2-PL IRT; a_d = 1 gives Rasch)

Fit θ, b, a on all existing (model, item) outcomes (correct = native score ≥ 0.5, or use the graded
score with a continuous-response variant). Then:
- the **capability ranking** is the order of θ_m, and it is the same ranking whatever dataset you look at,
  because dataset difficulty is factored out;
- a **new dataset** is handled by running the models on a modest sample (≈ 50–100 items), estimating
  only its b_new (and a_new) with θ held fixed, and checking fit: if the observed scores match
  σ(a_new(θ_m − b_new)), the dataset is "on the scale" and the θ ranking applies to it; if not
  (poor fit, low a_new), the dataset measures something the scale does not, which is itself a finding;
- **which items are most informative** for ranking is known from the item parameters, so a new
  dataset can be evaluated with far fewer items (adaptive testing).
Alternatives at the same level: Bradley–Terry over (model vs model) outcomes per item (pairwise,
scale-free, no difficulty parameter), or a Bayesian hierarchical logistic model (gives posteriors on θ).
Status: not built; needs ≥ 8 models and ≥ 100 items per dataset to fit reliably.

### Ingredient 3: predictive validation on held-out datasets
The evidence that the method generalises:
- **leave-one-dataset-out prediction**: fit θ on k−1 datasets, run the models on the held-out one, compare
  the predicted ranking (θ) with the observed one (mean native score) by Kendall τ and by
  calibration (predicted vs observed accuracy). Report per held-out dataset;
- **learning curve**: how many items of a new dataset are needed before its observed ranking stabilises
  to the θ ranking (bootstrap over item subsets of size 25, 50, 100, 150);
- **out-of-family test**: hold out a whole *family* (all entity-matching sets, or all table-QA sets) to show
  transfer across task types, not just across datasets of one type;
- **domain-shift check**: the estimated a_d / b_d for a new dataset tell you whether it is harder or less
  discriminative than the calibration suite; publish the acceptance criterion (e.g. a_new ≥ 0.5, fit
  deviance within the range seen on the calibration suite).
Status: LODO for weights exists in v2; predictive LODO for capability does not.

### Flow

```
calibration suite (13 datasets, 150 items, ≥ 8 models)
   │  typed dataset-agnostic scorer (Ingredient 1)
   ▼
(model, item) outcomes ──► fit IRT / Rasch: θ_m (ability), b_d, a_d (difficulty, discrimination)
   │                                   │
   │                                   ├──► capability ranking = order of θ_m  (with posterior / bootstrap CI)
   │                                   └──► item information -> which items matter
   ▼
predictive validation: LODO τ(predicted, observed), learning curve, out-of-family, fit criteria
   ▼
NEW DATASET protocol:  write adapter -> sample 50–100 balanced items -> run models -> estimate b_new, a_new
   with θ fixed -> check fit -> if on-scale: θ ranking applies (and refine θ with the new data);
   if off-scale: report as a new dimension, do not merge
```

### What changes relative to §14
Track 1's "z-mean + Borda" becomes the IRT ability θ (Borda kept as a check); the full-grid
dataset-weight sensitivity is replaced by item/dataset difficulty parameters, which answer the same
question ("how much does the dataset matter") in a model-based way; Track 2 (the anchored composite)
is unchanged and still the right way to justify the scorer for free-form answers. The paper's claim
becomes: "a typed, dataset-agnostic scorer plus a latent-ability model that ranks LLM capability on
unseen data-matching datasets, validated by held-out prediction."

### Requirements and risks
- Needs breadth: ≥ 8 models spanning ability, ≥ 100 items per dataset, ≥ 10 datasets. With 4 close
  models the ability estimates will be within error of each other (same limitation as now).
- Dichotomising graded scores (free-form ROUGE-L) loses information; use a graded-response IRT variant or
  keep free-form out of the latent model and report it separately.
- Unidimensionality: if matching and numeric reasoning are different abilities, a 1-D θ will misfit;
  the out-of-family test detects this, and a 2-D model (matching ability, reasoning ability) is the remedy.
- Build cost: IRT fit (e.g. py-irt / a small PyTorch or scipy logistic fit) plus the validation scripts,
  about 2–3 days on top of the data run.

---

## 16. Plan for a 100-metric answer-level library with grid-searched weights (v3 candidate)

Goal restated: one scoring structure applied identically to every answer of every dataset, whose
weighted combination is chosen by grid search, so that model scores are comparable across datasets
and the leaderboard reflects model differences rather than dataset differences.

### Can node2vec / TransE-style models replace sentence-embedding / NLI models?
No, not for scoring free-text answers. node2vec, DeepWalk, TransE, RotatE, ComplEx learn vectors for
*nodes and relations of a graph*; they have no encoder for arbitrary text, so a prediction such as
"revenue rose 5 points" cannot be embedded unless it is first linked to graph entities. They are
usable only in a narrow setting: entity-level answers (WTQ names, entity-matching records) linked
to a knowledge graph (Wikidata) so that both prediction and gold become entities, with similarity =
embedding distance. That adds an entity linker, a KG, and an error source, to cover a small fraction
of items. For text similarity the right tools are small local sentence encoders (MiniLM / BGE-small
via sentence-transformers, free, CPU-fast) or none at all. Recommendation: build the library with the
~85 dependency-free metrics first; add 2–3 sentence-embedding cosines as an optional family; leave
KG embeddings out unless an entity-linked task is added.

### Do the datasets' own scoring guides have to be used?
Not for producing scores: the library scores every answer the same way regardless of dataset.
They should still appear in two places: (1) as a *reference baseline* in the leaderboard (what each
dataset's authors would report), and (2) as a *fidelity check* on the calibrated metric (Kendall τ
between the calibrated ranking and the native ranking per dataset). If you drop native metrics
entirely, the calibration needs another correctness anchor (human labels or synthetic known-quality
answers), otherwise "consistent across datasets" can be satisfied by a metric that measures nothing.

### The plan
1. **Library**: implement the 100 metrics of §C in `src/metrics/library.py`, each `f(pred, gold, aliases, type) -> [0,1]`,
   grouped by family, computed once into a (pairs × 100) matrix.
2. **Deduplicate**: Spearman correlation across items; cluster at 0.95; keep one representative per cluster (expect 25–35).
3. **Anchor**: choose the calibration target: (a) human correctness labels on ~300 sampled answers, or (b) synthetic
   known-quality answers (ladder), or (c) native metrics. (a) > (b) > (c) in credibility; (b) is free.
4. **Select**: non-negative sparse regression / forward selection of the deduplicated metrics against the anchor,
   with leave-one-dataset-out to stop; keep k = 6–10 metrics.
5. **Grid search**: enumerate weights over the k survivors (step 0.05 or 0.1), objective = anchor agreement + cross-dataset
   consistency (rank agreement and JS of score distributions at matched anchor quality) + native fidelity; keep the
   **100 best weightings**.
6. **Final metric** = average score over the 100 best weightings (ensemble); uncertainty = spread across them.
7. **Leaderboard**: per-dataset mean of the final metric, z-normalise, equal dataset weights, Borda + Kemeny check,
   item bootstrap, Friedman–Nemenyi; report native-metric ranking beside it.
8. **Validation**: LODO on both selection and weights; selection stability across folds; gaming probes.
9. **Green agent**: ships the k metrics + the 100 weightings; returns the ensemble score and its spread per item.
