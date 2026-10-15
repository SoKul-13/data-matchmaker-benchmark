# Decisions for the v6 run and the workshop paper: options, trade-offs, the call, and the literature behind it

Goal of the paper: one credible score and ranking for LLMs across data-matching tasks, produced by a judge whose scoring rule was
calibrated rather than hand-set, with uncertainty and significance reported the way the evaluation literature asks for.
Each section gives the options, pros and cons, the decision, and why. "Cost" figures are for the four cached models unless stated.

---

## 1. Items per dataset

| Option | Pros | Cons |
|---|---|---|
| 40 (current old pools) | cheapest (≈ USD 45–50); matches the published v2–v5 numbers | a 70 % score has a 95 % interval of roughly 55–85 %; pairwise item tests have almost no power; Card et al. (2020) show most NLP test sets of this size cannot detect the differences papers claim |
| **100** | interval shrinks to ≈ 61–79 %; Friedman/Nemenyi over 30 datasets and item-level paired tests become informative; ≈ USD 110 | old five datasets must be re-answered to 100 for consistency |
| 150 (current new pools) | best power; ≈ USD 170 | diminishing returns beyond 100 for a proportion; 3× the Opus bill |

**Decision: 100 items per dataset, every dataset, every model.** The paper's core claim is a ranking with error bars; error bars are set by item
count, and 100 is the point where the intervals stop overlapping for models that differ by 10 points. Card, Henderson, Khandelwal, Jia &
Liang, "With Little Power Comes Great Responsibility" (EMNLP 2020); Bouthillier et al., "Accounting for Variance in Machine Learning
Benchmarks" (MLSys 2021) on data-sampling variance dominating other sources.

## 2. Decoding: temperature and repeats

| Option | Pros | Cons |
|---|---|---|
| provider defaults (temperature 1.0), one sample | what was done so far | answers change between runs; a re-run can reorder the leaderboard; not reproducible |
| **temperature 0, one sample, plus a 100-item subset answered 3×** | reproducible; the repeat subset gives an answer-agreement number to report; reasoning models that ignore temperature are measured rather than assumed | temperature 0 is not bit-exact on batched servers (hence the repeat subset); ≈ USD 4 extra |
| defaults, 3 samples per item, majority vote | robust to sampling noise | 3× cost; changes what is measured (a voting system, not the model) |

**Decision: temperature 0 everywhere it is accepted, record every decoding parameter per row, 3× on a 100-item subset.** Renze & Guven
(2024) find no significant accuracy change for temperature in 0–1 on problem-solving tasks, so temperature 0 costs nothing in fidelity and buys
reproducibility. Reimers & Gurevych (2017) and Bouthillier et al. (2021): report variance, do not hide it.

## 3. Which models, and how to pay for them

| Option | Pros | Cons |
|---|---|---|
| the 4 cached models only | no new accounts; ≈ USD 110 at 100 items | Kendall τ over 4 models has 7 possible values; BT and IRT are degenerate; every rank claim below first is unsupported |
| **8 live now + 4 blocked (13 with Grok)** | two flagships and two standard tiers per closed provider, four open-weight flagships; τ becomes fine-grained; BT/IRT identifiable | four need account actions (Gemini prepaid, xAI credits, Mistral plan or pay-as-you-go, Together third-party toggle for Qwen) |
| Opus on the top-10 datasets only | halves the largest bill | breaks "every model on every dataset", which the pooling rules assume; creates missing cells |

**Decision: run all 12 (Grok optional), every model on every dataset, and pay the two free tiers (Groq ≈ USD 0.40, Mistral ≈ USD 1) to remove
daily caps.** Missing cells would force imputation in Borda/Kemeny and break the paired tests; the budget difference (≈ USD 15) is not worth it.
Chatbot Arena (Chiang et al. 2024) and Perlitz et al. (2024) both show ranking reliability is governed by the number of systems compared.
Keep the rule "flagship + standard tier per provider, no small models" so the ranking is about models people actually choose.

## 4. The dataset suite

| Option | Pros | Cons |
|---|---|---|
| the original 7 QA sets | already answered | none of them is data matching; the benchmark's name is unsupported |
| **evidence top 30 + OfficeQA closed-book as continuity** | 17 matching sets (11 entity, 6 schema), 11 table sets covering hierarchy/structure/free-form/boolean/SQL/multilingual, 2 financial; adoption is measured from 220 papers, not judged | 15 new adapters; three NC/restrictive licences; schema sets must be reframed as per-column questions for v2/v4/v5 |
| top 50 | more coverage | 20 more adapters for datasets ranked 31–50, which are second representatives of families already covered |

**Decision: top 30 + OfficeQA.** On the licences: CC BY-NC (RealHiTBench, OpenSanctions) and the TPC-DI spec permit research use; state them in
the data section and ship download scripts, never the files. On reframing: every dataset gets a *native* score (set-level F1 / MRR for schema
matching, positive-class F1 for entity matching, execution result for BIRD) used by v3, and a *QA-form* score used by v2/v4/v5; report both and say
which is comparable to published numbers. Papadakis et al. (ICDE 2024) on why balanced EM samples inflate accuracy; Peeters & Bizer (2024)
on hard negatives; Koutras et al. (Valentine, ICDE 2021) for schema-matching scoring.

## 5. What the scoring rule is optimised against (the logic of the paper)

| Objective | Pros | Cons | Version |
|---|---|---|---|
| rank agreement between datasets (J = mean τ to the pooled ranking) | needs no labels; simple | measures **consistency**, not correctness: a rule that makes every dataset agree is rewarded even if all are wrong; circular with the ranked models | v2, v4 |
| reliability of aggregation views (stability + transitivity + reference) | grounded in the benchmark-reliability literature | selects an aggregation rule, not a scoring rule | v3 |
| **known-quality anchors (ρ, AUC, JS consistency, τ-native, wrong-answer penalty)** | measures correctness against answers of known utility; not circular with the ranked models | anchors are synthetic (lexical perturbations judged by lexical metrics); utility scale hand-set | v5 |

**Decision: v5's anchor objective is the headline scoring rule; v2/v4's rank agreement is reported as a consistency diagnostic, never as
accuracy; v3 is the aggregation study.** This is the structure metric meta-evaluation uses: a metric is validated against a quality signal
external to the systems being ranked (Mathur et al., "Tangled up in BLEU", ACL 2020; Kocmi et al., "To Ship or Not to Ship", WMT 2021).
State plainly that human labels on 300–500 answers would replace the synthetic anchors, and that the pipeline accepts them (`--labels`).

## 6. Selecting the best weighting honestly

| Option | Pros | Cons |
|---|---|---|
| pick the best of 100 on all data, CI on the same data (current) | simple | winner's curse: the reported optimum is optimistically biased (Cawley & Talbot 2010; Varma & Simon 2006) |
| **nested bootstrap: select on in-bag items, score out-of-bag; paired tests vs baselines; ensemble of the top 100 (v5)** | honest estimate; a p-value for "best beats EM"; the ensemble spreads selection risk | more compute (minutes, not hours) |
| leave-one-dataset-out only (v4) | tests transfer across datasets | does not address selection on items within datasets |

**Decision: nested bootstrap + LODO + Holm-corrected paired permutation tests, for every version.** Report the in-bag and out-of-bag objective
side by side; the gap is itself a result.

## 7. Search design

| Option | Pros | Cons |
|---|---|---|
| 100 uniform draws from the lattice (v2, v3) | unbiased | unstratified; 100 of 888,030 points in v3 |
| 100 Dirichlet draws snapped to the lattice (v4) | unbiased on the continuous simplex | same clustering problem |
| exhaustive grid (v5, 6,630) | complete | only feasible for ≤ 3 weights |
| **Latin hypercube on the simplex (McKay, Beckman & Conover 1979), 100 points, plus the existing designs; all 255 equal-weight view subsets in v3** | every marginal covered evenly at the same budget; subsets add the corners/edges random draws never reach | snapping to the 0.05 lattice erodes some stratification in 9 dimensions; report coverage on snapped points |

**Decision: run random and LHS designs side by side at 100 points each, report best J and coverage (centred discrepancy, minimum pairwise
distance) for both, and keep v5 exhaustive.** Bergstra & Bengio (2012) on why random/stratified designs beat grids when few dimensions matter,
which is the case here (v5 ends with one dominant weight).

## 8. Pooling rule and the headline leaderboard

| Option | Pros | Cons |
|---|---|---|
| mean of z-scores | continuous; simple | one outlier dataset moves everything (Mathur et al. 2020) |
| Borda | robust; per-dataset ranks | discards score magnitude; equal dataset weight |
| Kemeny | optimal consensus | expensive above ~10 models; equal dataset weight |
| **Bradley–Terry with item-level bootstrap CIs** | the Chatbot Arena standard; v3 found it most reliable (J 0.867); gives strengths with intervals | needs enough pairwise item comparisons (fine at 100 items × 30 datasets) |
| family-balanced (mean within family, then across) | stops the largest family (entity matching, 11 sets) deciding the ranking | a modelling choice reviewers may question |

**Decision: Bradley–Terry with bootstrap CIs as the headline, Borda and z-mean as agreement checks, and the family-balanced version as the
second table with the disagreement between them reported.** Colombo et al. (NeurIPS 2022) on Kemeny/Borda for NLP benchmarks; HELM (Liang et
al. 2022) on mean win rate; Boubdir et al., "Elo Uncovered" (2023) on transitivity and reliability of pairwise ratings.

## 9. Significance testing

| Test | Use | Reference |
|---|---|---|
| Friedman across datasets + Nemenyi critical difference (or Holm-corrected pairwise Wilcoxon, which has more power with few datasets) | "do the models differ overall, and which pairs?" | Demšar (JMLR 2006); García & Herrera (JMLR 2008) |
| paired permutation / bootstrap on per-item scores within a dataset, Holm-corrected | "does A beat B on this dataset?" | Koehn (2004); Dror et al., "Hitchhiker's Guide" (ACL 2018) |
| item bootstrap on the pooled ranking (1,000 draws, saved) | rank intervals | Chatbot Arena (2024) |
| Kendall's W among datasets; τ granularity stated | how much the datasets agree; what τ can resolve | Perlitz et al. (2024), BenchBench |

**Decision: all four, saved in full (`output/significance/`), with the bootstrap draws kept as arrays so any interval can be recomputed.**

## 10. What to report for the paper's tables
* Per version: leaderboard under exact match only, under each of the five best weightings, and under the ensemble, so a reader sees how much the
  calibrated rule changes the ranking relative to the naive one.
* Per dataset: native score and QA-form score per model with intervals; majority-class baseline for boolean sets.
* The fitted parameters of every aggregation view (BT strengths, Rasch abilities and item difficulties, Kemeny cost) with standard errors.
* A run manifest: models, decoding settings, items, seeds, costs, tokens, commit, dataset versions and licences.

## 11. Paper structure that follows from the above (workshop length, 4–8 pages)
1. Problem: one score across matching tasks needs a calibrated rule and a reliable aggregation.
2. Suite: 30 datasets chosen by measured adoption plus coverage; licences stated.
3. Scoring rule: metric library → selection → anchor-calibrated ensemble (v5); exact match and the consistency objective as baselines.
4. Aggregation: BT headline, Borda/z-mean/family-balanced checks (v3's reliability study justifies the choice).
5. Results: leaderboard with CIs; Friedman/Nemenyi; per-family tables; in-bag vs out-of-bag objective; random vs LHS design.
6. Limitations: synthetic anchors, one prompt, 100 items, NC licences, models blocked at submission time.
Appendix: v2 and v4 as ablations of the objective; all 255 view combinations; full parameter dumps.

## 12. The decisive calls, in one list
1. 100 items per dataset. 2. Temperature 0 + 3× on 100 items. 3. All 12 models, every dataset; pay Groq and Mistral (≈ USD 1.50 total).
4. Top 30 + OfficeQA; native and QA-form scores both reported. 5. v5 anchors are the headline objective; v2/v4 consistency is a diagnostic.
6. Nested bootstrap + LODO + Holm-corrected tests everywhere. 7. Random and LHS designs both run; v5 stays exhaustive; 255 view subsets in v3.
8. Bradley–Terry with CIs as the headline pooling; family-balanced as the second table. 9. Full significance and parameter dumps saved.
Budget at these settings: ≈ USD 110 (four cached models) + ≈ USD 25 (eight others) + ≈ USD 4 (repeat subset) ≈ USD 140, Grok optional (+ USD 10).

## References
Bergstra & Bengio 2012, JMLR · Boubdir et al. 2023, arXiv 2311.17295 · Bouthillier et al. 2021, MLSys · Card et al. 2020, EMNLP ·
Cawley & Talbot 2010, JMLR · Chiang et al. 2024 (Chatbot Arena), ICML · Colombo et al. 2022, NeurIPS · Demšar 2006, JMLR ·
Dror et al. 2018, ACL · García & Herrera 2008, JMLR · Koehn 2004, EMNLP · Kocmi et al. 2021, WMT · Koutras et al. 2021, ICDE ·
Liang et al. 2022 (HELM) · Mathur et al. 2020, ACL · McKay, Beckman & Conover 1979, Technometrics · Papadakis et al. 2024, ICDE ·
Peeters & Bizer 2024 (WDC Products) · Perlitz et al. 2024 (Efficient Benchmarking; BenchBench) · Polo et al. 2024 (tinyBenchmarks), ICML ·
Reimers & Gurevych 2017, EMNLP · Renze & Guven 2024, arXiv 2402.05201 · Varma & Simon 2006, BMC Bioinformatics.

---

## 13. If v2 leads the paper: what to add to make it rigorous (in order of value per hour)

v2 today: 105 candidates (v1 point, 4 corners, 100 random lattice points), J = mean Kendall τ of each dataset's ranking to the Borda pool,
bootstrap on 7 candidates, no held-out check, no significance test, 7 datasets, 4 models.

| # | Addition | What it changes | Why it matters | Cost |
|---|---|---|---|---|
| 1 | **Exhaustive grid**: all 1,771 step-0.05 weightings (optionally all 23,426 at step 0.02) instead of 100 random ones | the claim becomes exact: "over every weighting, v1 ranks k-th" | removes sampling from the story entirely; only v2 is small enough for this | seconds |
| 2 | **Nested selection**: 1,000 item bootstraps; in each, choose the best weighting on the in-bag items and score it on the out-of-bag items; report in-bag vs out-of-bag J and how often v1 is inside the plateau | honest optimum; a p-value for "best beats v1" from the paired distribution of J(best) − J(v1) | the winner's curse is the first objection to any "we searched and found better weights" result (Cawley & Talbot 2010) | minutes |
| 3 | **Leave-one-dataset-out** (as in v4) and **leave-one-family-out** (entity matching / schema / tables / finance) | shows whether weights chosen on some tasks transfer to unseen tasks and unseen task *types* | with 30 datasets in four families this is the generalisation evidence a reviewer wants | minutes |
| 4 | **Bootstrap every candidate**, not 7, and report the **plateau**: the set of weightings statistically indistinguishable from the best | v2's real finding is likely "a large flat region, v1 inside or just outside it", which is more defensible than a single winner | turns a weak "best" into a strong "region" claim | minutes |
| 5 | **Significance on the leaderboard**: Friedman across datasets, Holm-corrected pairwise Wilcoxon or Nemenyi; paired permutation per dataset; Kendall's W among datasets | which model differences are real under v1's weights and under the best | Demšar 2006 is the standard; currently absent | minutes |
| 6 | **Objective robustness**: recompute J with Kemeny, Copeland and Bradley–Terry in place of Borda; show the optimum and v1's rank under each; report the Pareto front of (J, τ to native metrics) | proves the result is not an artefact of Borda | one paragraph that pre-empts "why Borda?" | minutes |
| 7 | **Correctness check borrowed from v5, without changing v2's objective**: score v5's 12,813 known-quality anchor answers under v1's weights and under the best weights; report Spearman to utility and AUC correct-vs-wrong | gives v2 evidence about *correctness*, which its own objective cannot provide | closes the "consistency is not accuracy" gap with no API cost | minutes (anchors already exist) |
| 8 | **Per-family weights**: fit the best weighting separately per family and compare with the global one | shows whether one rule fits all task types, or whether numeric-heavy and boolean-heavy families pull different ways | direct evidence for or against a single composite | minutes |
| 9 | **Sensitivity**: J on the ±0.05 neighbourhood of the optimum and of v1; flatness statistic | how fragile the ranking is to small weight changes | cheap, reviewers like it | seconds |
| 10 | **Dataset diagnostics**: pairwise τ heat-map between datasets, outlier datasets (Mathur et al. 2020), floor/ceiling datasets excluded from J with a note | explains *why* datasets disagree | needed anyway to justify dropping floor sets | minutes |
| 11 | **Exact-match and top-5 leaderboards** (already planned) plus the leaderboard under v1's original weights | the reader sees the naive rule, the deployed rule and the calibrated rule side by side | this is the figure the workshop paper is built around | none |
| 12 | Reproducibility: temperature 0, run manifest, no seed needed for an exhaustive grid | re-runnable by anyone | required | none |
| 13 | Optional: 300 human-labelled answers scored under both weightings | replaces the synthetic check in row 7 with the real thing | strongest possible validity evidence; the only item that needs people | hours of labelling |

Rows 1–7 turn v2 from "we tried 100 weightings" into "we evaluated every weighting, selected honestly, tested significance, checked transfer
across tasks and task types, and validated correctness on known-quality answers". That is a complete workshop paper on auditing a deployed judge.
