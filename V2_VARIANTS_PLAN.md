# Five v2-style variants: plan for approval (2026-09-26)

Scope: five versions that all stay true to v2 (v1's four ingredients token F1, numeric decay, precision, recall; one linear composite; the
full step-0.05 lattice of 1,771 weightings; Borda pooling inside the loop; Bradley–Terry headline leaderboard) and differ only in the
question they answer and therefore in the objective, the grouping and the honesty check. Each fixes the same list of issues (section 1)
and each is a plausible workshop paper (section 3). Nothing here spends money: all five run in minutes on cached answers, once the
31-dataset model run (`v6_top30_significance/notes/RUN_MODELS.md`, ≈ USD 120) has been approved and run.

## 1. Issues fixed in all five (with where the fix lives)

| # | issue | fix | status |
|---|---|---|---|
| 1 | provider-default decoding, non-reproducible | temperature 0 sent, fallback recorded per row; 100-item subset answered 3× for an agreement number | runner done; repeat subset to add (≈ USD 4) |
| 2 | 40 items per dataset, wide intervals | 100 answered items per dataset (90 / 93 for the two smaller sets) | pools re-flagged |
| 3 | best-of-many on the same data (winner's curse) | nested item bootstrap: select in-bag, score out-of-bag; optimism gap; plateau | shared `search/nested.py`, in every variant |
| 4 | floor / ceiling / unstable datasets silently count as zero agreement | diagnostics flag them; the objective drops them and the report lists them | flags exist; **wiring into the objective is part of this plan** |
| 5 | entity-matching pools balanced, accuracy reported | positive-class F1 as the native metric for boolean pools, majority-class baseline, class ratio stated; Papadakis–Christen keeps the real ratio | baseline done; **F1-as-native to add** |
| 6 | four models: τ takes 7 values | 12-model run; τ granularity printed in every significance file | printed; run pending |
| 7 | equal weighting of datasets in the pool | family-balanced pooling as the second table; per-family variant (D) makes it the object of study | done / variant D |
| 8 | answer extraction is heuristic | log the extraction path per row; report the share of answers with no FINAL ANSWER line; 50-answer manual check | **to add** (small) |
| 9 | agreement objective is not correctness (J vs ρ = −0.33) | every variant reports both; variants B and C make correctness the objective or a constraint | anchors done |
| 10 | synthetic anchors only | human-label file accepted by all variants (`notes/HUMAN_LABELLING_PROTOCOL.md`) | protocol written |
| 11 | one prompt | stated as a limitation; optional paraphrased-prompt subset (≈ USD 30) not in the default plan | decision |
| 12 | OfficeQA closed-book at floor | excluded by fix 4; OfficeQA Pro V2 with documents replaces it | pool built |

## 2. The five variants

| | A. Audit | B. Correctness-calibrated | C. Two-objective (Pareto) | D. Per-family | E. Reliability and efficiency |
|---|---|---|---|---|---|
| question | are v1's hand-set weights defensible? | what should the same four weights be if we optimise for correctness? | how do agreement and correctness trade off, and what does a compromise cost? | does one composite fit all matching task types? | which weights give the most reproducible leaderboard, and how much data does the audit need? |
| objective | J = mean τ to the Borda pool (v2's) | anchor correctness: 0.5 ρ + 0.25 AUC + 0.25 (1 − wrong-score); human labels replace anchors when present | both; selection = Pareto knee, plus the constrained rule "max J subject to ρ ≥ ρ(v1)" | J within each family; global J as comparison | stability: mean τ between the pooled ranking on bootstrap resamples and on full data, subject to ρ ≥ ρ(exact match) |
| candidates | 1,771 lattice | 1,771 lattice (+ λ hedge penalty in {0, .25, .5, .75, 1} as an option, off by default) | 1,771 lattice | 1,771 per family | 1,771 lattice |
| honesty check | nested bootstrap, plateau, LODO, LOFO | anchor-item bootstrap (in-bag / out-of-bag ρ), LODO over anchor datasets | nested bootstrap on both objectives; frontier stability across resamples | leave-one-family-out; per-family plateau; test "global vs per-family" by paired bootstrap on held-out families | split-half; nested bootstrap; subsampling curves |
| new computation | none (built) | objective swap; anchor bootstrap | Pareto set per resample; constrained selection | family loop; hierarchical pooling (within family then across) | stability objective; subsampling curves: J, rank CIs and significant pairs vs items per dataset (10…100) and vs number of datasets (5…31) and models (4…12) |
| headline figure | sorted-J landscape with v1 and the plateau | ρ landscape with v1, best-J and best-ρ; anchor operator profile | the (J, ρ) frontier with v1, knee and constrained choice | four family panels: best weights per family vs global | curves: interval width and number of significant pairs vs items / datasets / models |
| claim it supports | v1 is (not) inside the plateau; honest gain ≤ x | four-ingredient rule calibrated for correctness; how far v1 and the J-optimum are from it | consistency and correctness disagree; here is the priced compromise | one rule vs task-specific rules, with a test | a leaderboard needs N items and D datasets to separate the models at α = .05 |
| literature | Cawley & Talbot 2010; Demšar 2006 | Mathur 2020; Kocmi 2021 | multi-objective selection; Perlitz 2024 | Papadakis 2024 (family effects); HELM per-scenario | Perlitz 2024; Card 2020; Polo 2024 (tinyBenchmarks) |
| risk | result may be "nothing beats v1" (still a paper: an audit) | anchors are synthetic until labels exist | knee choice is a convention; state it | families with ≤ 3 datasets give trivial J | subsampling on 12 models is coarse for the model axis |

Shared by all five: the same five-rule leaderboard set (exact match, v1, best under the variant's objective, best under the other objective,
Pareto knee), Bradley–Terry with SE and bootstrap draws, Borda / z-mean / Kemeny / Copeland checks, family-balanced table, Friedman +
Nemenyi + Holm pairwise, Kendall's W, dataset diagnostics, `REPORT.md` assembled from files.

## 3. How they map to a paper

* One paper, five sections: A is the audit (§4), B the recalibration (§5), C the reconciliation (§6), D the generalisation test (§7), E the
  procedure section (§3 methods + §8 "how much data"). Four to eight pages with the appendix carrying the full tables. This is my recommendation:
  the five together tell one story (the deployed weights are defensible on agreement, wrong on correctness, one rule does or does not fit all
  families, and here is the data budget the audit needs).
* Or two papers: A + C + E as the evaluation-methodology paper; B + D as the judge-calibration paper.

## 4. Implementation plan (no new money)

1. `v6_top30_significance/v2_variants/` with one script set parameterised by `--variant {A,B,C,D,E}`; A reuses the existing v2 outputs.
   Shared additions: objective registry (agreement / correctness / stability), family grouping, Pareto and constrained selectors, subsampling
   module. Estimated build: one day; compute per variant on the 31-dataset run: A 5 min, B 5 min, C 15 min, D 10 min, E 40 min.
2. Fixes 4, 5 and 8 above wired into the shared code first (half a day), so every variant inherits them.
3. Each variant writes `REPORT_<X>.md`; a combined `V2_VARIANTS_SUMMARY.md` lines up the five headline numbers.
4. Order of running after the model run: A → B → C → D → E, each report reviewed before the next.

## 5. What needs your approval
* The five variants as specified (or drop / merge any).
* The paper mapping (one paper with five sections, or two papers).
* Two optional spends: the 3× repeat subset (≈ USD 4, recommended) and the paraphrased-prompt subset (≈ USD 30, not recommended now).
* The model run itself (≈ USD 120), which all five depend on; without it every variant runs on 5 datasets × 4 models.
