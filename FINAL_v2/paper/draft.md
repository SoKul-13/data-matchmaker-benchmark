# Auditing a Deployed LLM Judge: Is Any Weighting of Its Ingredients Better Than the One It Ships With?

*Sample workshop draft, 2026-10-13. Every number is from `FINAL_v2/v2_gridsearch/REPORT.md` (31 datasets × 10 models × 100 items). Bracketed
notes mark what to adjust before submission. Figures are in `paper/figures/`.*

## Abstract

Judges that grade LLM answers on structured-data tasks often combine several lexical metrics with hand-set weights. We audit one such judge,
deployed on a data-matching benchmark, whose rule is 0.35·F1 + 0.35·numeric-decay + 0.15·precision + 0.15·recall. Rather than searching for better
weights and reporting the winner, we evaluate every weighting on a step-0.05 simplex lattice (1,771 points) against two criteria: agreement among
datasets about the model ranking, and correctness against 31,380 synthetic answers of known quality. We then test whether any winner survives
honest selection (nested item bootstrap), transfers across datasets and task families, and changes the leaderboard. On a suite of 31 datasets
chosen by measured literature adoption (11 entity matching, 6 schema matching, 11 table QA, 3 financial documents) and 10 models, the agreement
objective spans only 0.39–0.42; 1,765 of 1,771 weightings are statistically indistinguishable from the best; the out-of-bag advantage of the
selected weighting over the deployed one is −0.008 (95 % CI −0.039 to +0.013); and the deployed weights are within 0.005 of the best achievable
correctness. The leaderboard separates the ends of the model field at p < 0.001 but its top order depends on the pooling rule. We release the
suite, cached answers and audit code; the audit reruns from cache in minutes.

## 1. Introduction

[One paragraph: why LLM judges on data-matching tasks use composites of lexical metrics (aliases, units, lists, free-form answers), why their
weights are usually set by hand, and why an unvalidated judge undermines any leaderboard built on it. Cite MT-Bench / LLM-as-a-judge for the
judge-validation framing, Mathur et al. 2020 and Kocmi et al. 2021 for metric meta-evaluation.]

Our question is narrow and the answer is negative in the useful sense: for the deployed judge's four ingredients, no weighting is defensibly
better than the deployed one. The contribution is the audit procedure that establishes this, which applies to any composite judge:

1. an exhaustive evaluation of the weight simplex rather than a search that reports a winner;
2. two separated criteria, consistency among datasets and correctness against known-quality answers, never conflated;
3. honest selection with a nested bootstrap, and transfer tests across datasets and task families;
4. the leaderboard consequences under several pooling rules, with significance tests and official-split estimates.

## 2. The judge and the suite

**Judge.** For an answer *a* to an item with gold *g* (with aliases, unit-aware numbers, list golds), the deployed rule is R(a) = Σ_k w_k m_k(a, g)
with m = (token F1, numeric decay e^{−2.5·relative error}, token precision, token recall) and w = (0.35, 0.35, 0.15, 0.15). A dataset's score for a
model is the mean of R over its items.

**Suite.** 31 datasets (Table 1): the top 30 of a 100-dataset ranking whose adoption criterion was measured from ~220 top-cited papers in
entity matching, table QA and financial QA [cite the survey document], plus the benchmark's original document set. Families: entity matching (11:
Abt-Buy, Amazon-Google, Walmart-Amazon, DBLP-Scholar, DBLP-ACM, WDC Products 2024, WDC LSPC, Machamp, Papadakis–Christen, Alaska Camera,
OpenSanctions), schema matching (6: Valentine, Magneto GDC, SMAT, Alaska schema, FinTagging, TPC-DI cells), table QA (11: HiTab, MMTU, WTQ,
RealHiTBench, SUC, TabIS, TableEval, BIRD, TabFact, FeTaQA, TableBench), financial documents (3: OfficeQA Pro V2, TAT-QA, OfficeQA). Each pool
holds 150 items drawn by seeded stratified sampling from the official split; 100 are answered. Schema-matching sets are framed as one question
per source column with a candidate list; BIRD is graded on the executed result value. [State licences: CC BY-NC for RealHiTBench and
OpenSanctions; TPC-DI spec terms.]

**Models.** Ten: Claude Opus 5, Claude Sonnet 5, GPT-5.5, GPT-5.4-mini, Gemini 3.8 Flash, Grok 4, DeepSeek-chat, DeepSeek-R1, gpt-oss-120b,
Llama 3.3 70B. One prompt, greedy decoding where the API accepts it (Claude 5 and GPT-5.5 refuse the parameter; recorded per answer). Output
budget 700 tokens, re-asked at 2,500, 8,000 and then 16,000 when cut off before a final line; 41 answers (all DeepSeek-R1) never terminated and
are scored as failures to answer. Gemini 3.1 Pro was excluded by a 250-request daily quota [update if the trickle completes]. Total cost USD 161.

## 3. Audit procedure

**Candidates.** All 1,771 points of the step-0.05 lattice on the 4-simplex; v1, the four corners and the uniform mix are lattice points. For
comparison, three 100-point sampled designs (uniform lattice, Dirichlet-snapped, Latin hypercube) with 20 seeds each.

**Agreement objective.** J(w) = mean over datasets of Kendall τ-b between the dataset's model ranking under w and the Borda-pooled ranking.
Also computed with Kemeny, Copeland and Bradley–Terry pooling. J measures whether the datasets tell the same story; it is not accuracy.

**Correctness.** 31,380 synthetic answers of known utility generated from the golds by typed operators (identity, alias, unit change,
rounding, magnitude error, wrong value, partial list, hedge, paraphrase, …) [cite the anchor generator]. For every w: Spearman ρ between R and
utility, AUC for correct (utility 1) vs wrong (≤ 0.1), the mean score given to wrong answers, and the hedge gap.

**Honest selection.** 1,000 item bootstraps within datasets; in each, the best w is chosen on in-bag items and scored on out-of-bag items.
We report the optimism gap, the paired out-of-bag difference to v1, and the plateau: the set of weightings whose paired bootstrap difference to
the full-data best is not significantly negative (p > 0.05), plus a practical plateau (bootstrap-mean J within 0.02 of the best).

**Transfer.** Leave-one-dataset-out and leave-one-family-out: choose w without the held-out part, report the held-out τ to the pooled ranking
of the rest under the held-out weights, the full-data best and v1; per-family optima.

**Leaderboards and tests.** Under exact match, v1, the five best weightings by J, the best-ρ weighting and the (J, ρ) Pareto knee:
Bradley–Terry strengths with standard errors and 1,000 bootstrap rank intervals; Borda, mean-z, Kemeny, Copeland, RRF and family-balanced ranks;
Friedman with Iman–Davenport, Nemenyi, Holm-corrected pairwise Wilcoxon across datasets (Demšar 2006; García & Herrera 2008); paired permutation
tests per dataset (Koehn 2004; Dror et al. 2018); Kendall's W among datasets.

**Official-split estimates.** A census of each dataset's official population gives stratum proportions (match ratio for matching sets,
question type for table sets); the same answers re-weighted by official share / sample share give an unbiased official-split estimate with a
weighted bootstrap, and positive-class F1 at the official match ratio.

## 4. Results

**The objective is flat (Fig. 1).** Over all 1,771 weightings J ranges from 0.386 (recall only) to 0.421 (decay 0.70, recall 0.30); median 0.409,
99th percentile 0.418. v1 scores 0.404. Every corner and the uniform mix lie within 0.02 of the best. The sampled designs reach 0.418 ± 0