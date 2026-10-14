# Experiment procedure, setup, methods and logic, and the work it draws on

Companion to `draft.md` and `PAPER_PLAN.md`. Part I is what we did and why; Part II is the literature, one mini-section per idea we borrowed,
each stating what the source did, what we took, and what we changed. Citations in APA form are in `../../notes/REFERENCES.md`.

---

# Part I. Experiment

## 1. Setup

**Task family.** Data matching in the broad sense: is this pair of records the same entity; which target column does this source column map
to; what value does this table or document give for this question. All tasks have a gold answer, so a judge can be a formula.

**The judge under audit.** v1 scores an answer as R = 0.35·F1 + 0.35·D + 0.15·P + 0.15·Rc, where F1, P and Rc are token-overlap F1, precision
and recall against the gold (maximum over gold aliases), and D = exp(−2.5·|relative numeric error|) for numeric golds. Gold handling is shared by
every rule we compare: aliases, unit and percent equivalence, scale words, list golds scored as sets.

**Suite.** 31 datasets. Selection: a survey of 231 candidates, a seven-criterion rubric (relevance, adoption, generalisation, discriminative
power, gold clarity, inclusivity, licence), adoption re-measured as usage counts in roughly 220 top-cited papers per area, top 30 kept plus the
benchmark's original document set. Families: entity matching 11, schema matching 6, table QA 11, financial documents 3. Pools of 150 items per
dataset by seeded stratified sampling from the official split (strata: question type, sub-task, database, product category, or match label);
100 answered per dataset (90 and 93 for the two smaller sets); the remaining 50 feed calibration. Matching pools are balanced 50/50 except
Papadakis–Christen, which keeps its real ratio. The official population of every dataset is censused by the same strata for post-stratification.

**Models.** Claude Opus 5, Claude Sonnet 5, GPT-5.5, GPT-5.4-mini, Gemini 3.8 Flash, Grok 4, DeepSeek-chat, DeepSeek-R1, gpt-oss-120b, Llama 3.3
70B (ten; Gemini 3.1 Pro collected at 240 items a day and included once it reaches 90 % coverage). Rule: flagship plus standard tier per
provider, no small models.

**Prompting and decoding.** One system prompt and one item template: context (table, document pages or record pair), the question, and a line
asking for `FINAL ANSWER: <answer>`. Temperature 0 where the API accepts it (refused by Claude 5 and GPT-5.5; recorded per answer). Output budget
700 tokens; answers cut off before a final line re-asked at 2,500 then 8,000 tokens; 184 non-terminating answers scored as failures. Replacement is
triggered only mechanically, originals archived, replacements tagged.

**Infrastructure and cost.** Python, `uv`-locked environment, one cache file per model, every row carrying tokens, latency, cost, finish reason
and decoding. USD 161 for the ten models (Opus 99). The analysis reruns from cache in minutes; the paid step is never triggered by the analysis.

## 2. Procedure (the six scripts of `FINAL_v2/v2_gridsearch/scripts/`)
1. `01_v1_components.py`: the four ingredients, exact match, numeric tolerance, hedge flag and the native metric for every (model, item);
   suite-wide coverage rule (a model must cover ≥ 90 % of the suite; items count only when every model answered).
2. `02_exhaustive_grid.py`: every step-0.05 weighting (1,771); J under Borda, Kemeny, Copeland and Bradley–Terry pooling; τ to native metrics;
   three sampled designs × 20 seeds with coverage diagnostics.
3. `03_selection_validity.py`: 1,000 nested item bootstraps (in-bag selection, out-of-bag scoring); plateau; leave-one-dataset-out;
   leave-one-family-out; per-family optima; one-step sensitivity.
4. `04_correctness_anchors.py`: 31,380 synthetic answers of known utility scored under every weighting; ρ, AUC, wrong-answer score, hedge gap;
   (J, ρ) Pareto front and knee.
5. `05_leaderboards.py`: for nine rules (exact match, v1, top-5 by J, best-ρ, Pareto knee): Bradley–Terry with SE and bootstrap rank intervals,
   Borda / mean-z / Kemeny / Copeland / RRF / family-balanced ranks, Friedman + Nemenyi + Holm-Wilcoxon, paired per-item tests, Kendall's W,
   majority baselines, post-stratified official-split estimates; rule-agreement matrix; dataset diagnostics.
6. `06_report.py`: `REPORT.md` assembled from the outputs; run manifest.

## 3. Methods and the logic behind each

**Agreement objective.** J(w) = (1/D) Σ_d τ_b(r_d(w), r*(w)), where r_d is the model ranking on dataset d under w and r* is the Borda pool of
the D rankings. Logic: a composite that makes the datasets tell the same story is self-consistent. Caveat stated throughout: consistency is not
correctness; a rule that makes every dataset agree can still be wrong. We therefore never claim accuracy from J.

**Why exhaustive.** With four weights and step 0.05 the lattice has 1,771 points, evaluated in seconds; enumerating it makes the claim "over
every weighting" literal. Sampled designs are run only to show that a 100-point design would have found the same plateau (regret ≤ 0.005).

**Correctness objective (borrowed from v5, not swapped in).** Synthetic answers are generated from each gold by typed operators with fixed
utilities (identity 1.0; alias / unit variant 1.0; rounding and small near-misses 0.75–0.9; partial list 0.5; magnitude error, sign flip, wrong
value, no answer 0; hedged answer penalised). Under weighting w each anchor gets R; ρ = Spearman(R, utility), AUC = separation of utility 1 vs
≤ 0.1. Logic: a scoring rule must be validated against a quality signal that does not come from the systems being ranked.

**Nested bootstrap.** For b = 1…1,000: draw items with replacement within each dataset; choose w_b = argmax J on the in-bag items; score w_b and
v1 on the out-of-bag items. Report mean in-bag J(w_b) minus mean out-of-bag J(w_b) (the optimism gap) and the paired out-of-bag difference to v1
with a percentile interval. Logic: selecting a maximum on the data used to evaluate it inflates the winner; the gap measures the inflation.

**Plateau.** Candidate w is in the plateau if, over the same resamples, J_b(w) ≥ J_b(best) in more than 5 % of resamples; a practical plateau
also reports weightings within 0.02 of the best bootstrap-mean J. Logic: when the objective is flat, "the best" is a set, not a point, and the
rank of any member inside it is noise.

**Transfer.** Leave-one-dataset-out: choose w on the other 30, report τ of the held-out dataset's ranking to the pooled ranking of the 30
under the held-out weights, the full-data best and v1. Leave-one-family-out: the same with whole families held out. Per-family optima: the
best w on each family alone, compared with the global best and v1.

**Pooling rules.** Borda (sum of per-dataset ranks), Kemeny (consensus minimising pairwise disagreements, exact for ≤ 9 models), Copeland
(pairwise majority wins), reciprocal-rank fusion, mean-z (z-score within dataset, mean across), family-balanced mean-z, and Bradley–Terry
(strengths β maximising Π σ(β_i − β_j)^{w_ij} over item-level pairwise wins, ridge 0.01, SE from the observed information). Logic: no single
rule is canonical; reporting several and the τ between their rankings is the honest description.

**Significance.** Friedman across datasets with the Iman–Davenport F correction; Nemenyi critical difference; Holm-corrected pairwise Wilcoxon on
per-dataset scores; paired permutation (10,000 sign flips) and Wilcoxon on per-item scores within each dataset, Holm within dataset; Kendall's W
among datasets; 1,000 item bootstraps of the Borda and Bradley–Terry rankings. Logic: the standard battery for comparing systems over many
datasets, with per-item tests where the data allow them.

**Post-stratification.** With official stratum shares π_s and sample shares p_s, each item's weight is π_s / p_s (mean 1); the weighted mean of a
per-item score estimates the official-split mean; a weighted item bootstrap gives the interval; for matching sets the same weights give
positive-class precision, recall and F1 at the official match ratio. Logic: keep equal strata for calibration, report comparable numbers for the
reader.

**Truncation protocol.** Mechanical trigger (no final line before the cap), escalating budgets (700 → 2,500 → 8,000), archive + tag, and a final
"failure to answer" verdict for non-termination. Logic: a budget artefact must not be scored as a wrong answer, but a model that never stops
reasoning has failed the item.

---

# Part II. Related work and inspirations (mini-sections)

### Pairwise-comparison leaderboards: Chatbot Arena (Chiang et al., 2024)
Did: Bradley–Terry strengths from millions of human pairwise votes with bootstrap confidence intervals. Took: Bradley–Terry as the headline
pooling rule and item-level bootstrap rank intervals. Changed: the pairwise "votes" are item-level score comparisons from a gold-based judge, so
the judge itself is audited; the leaderboard is reported under several pooling rules rather than one.

### Rank aggregation for benchmarks: Colombo et al. (2022); Kemeny (1959); Borda
Did: argued for Kemeny / Borda consensus over mean scores when aggregating NLP benchmarks, because means are sensitive to scale and outliers.
Took: Borda inside the objective (cheap, robust), Kemeny and Copeland as checks, and the Kemeny cost as a saved parameter. Changed: we quantify
how much the *choice* of rule changes the top order on the same scores.

### Holistic, native-metric evaluation: HELM (Liang et al., 2022)
Did: per-scenario native metrics, mean win rate across scenarios, no composite. Took: the idea that each dataset keeps its own metric as a
baseline column (our "native" rule and τ-to-native). Changed: we study the composite because the deployed judge uses one, and show its weights
do not matter on this suite.

### Few-item evaluation and IRT: tinyBenchmarks (Polo et al., 2024)
Did: showed ~100 well-chosen items reproduce full-benchmark rankings, using item-response theory. Took: 100 items per dataset as the design
target and a Rasch ability view in the sibling v3 pipeline. Changed: our items are stratified by task structure rather than selected by IRT
informativeness; we report the attainable precision directly through item bootstraps.

### Benchmark agreement and reliability: Perlitz et al. (2024, BenchBench); Boubdir et al. (2023, Elo Uncovered)
Did: measured how much benchmarks agree about model rankings and how reliable Elo-style ratings are (transitivity, sensitivity to the order and
set of comparisons). Took: Kendall's W among datasets, τ between pooling rules, and the stability of rankings under resampling as first-class
outputs. Changed: applied to datasets inside one suite rather than to whole benchmarks.

### Comparing systems over many datasets: Demšar (2006); García & Herrera (2008)
Did: established the Friedman test with Nemenyi or Holm post-hoc as the correct way to compare classifiers across datasets. Took: exactly that
battery, plus the Iman–Davenport correction. Changed: added per-item paired tests within datasets (Koehn, 2004; Dror et al., 2018) because we
have item-level scores, which the classic setting does not.

### Selection bias and nested validation: Cawley & Talbot (2010); Varma & Simon (2006)
Did: showed that choosing a model or hyper-parameter on the same data used to report its performance biases the report upward, and that nested
cross-validation removes the bias. Took: the nested item bootstrap (select in-bag, score out-of-bag) and the optimism gap as a reported quantity.
Changed: applied to weight search for a judge, and extended with the plateau, which turns "the best weighting" into a set.

### Metric meta-evaluation: Mathur et al. (2020); Kocmi et al. (2021); SummEval (Fabbri et al., 2021)
Did: validated automatic metrics against human judgements and showed that correlations are driven by outlier systems and that metric choice
changes decisions. Took: the principle that a judge must be validated against a quality signal external to the systems it ranks, the outlier
diagnostics, and the design of the human-labelling protocol (two labellers, adjudication, agreement statistics). Changed: our external signal
is synthetic (controlled perturbations of gold answers) until human labels exist; we keep agreement and correctness as separate axes.

### Behavioural testing with controlled perturbations: CheckList (Ribeiro et al., 2020)
Did: tested NLP models with templated, typed perturbations whose expected outcome is known. Took: the operator idea for the anchors: every
synthetic answer has a type (alias, unit change, magnitude error, hedge, …) and a known utility. Changed: the perturbations are applied to gold
answers to test the *judge*, not to inputs to test the model.

### LLM judges and their validation: MT-Bench (Zheng et al., 2023); JudgeBench (Tan et al., 2024); G-Eval (Liu et al., 2023)
Did: used LLMs as judges and measured their agreement with humans; built benchmarks of hard judging cases. Took: the framing that any judge is a
model of quality and needs validation; the refusal and hedge handling. Changed: our judge is a formula over lexical metrics, which is cheaper,
deterministic and auditable but blind to semantics; we state that trade-off rather than mixing in an LLM judge.

### Search designs: McKay, Beckman & Conover (1979); Bergstra & Bengio (2012); Hickernell (1998)
Did: Latin hypercube sampling for even coverage; random search beating grids when few dimensions matter; discrepancy as a coverage measure.
Took: three designs (uniform lattice, Dirichlet-snapped, Latin hypercube on the simplex via exponential spacings) with centred L2 discrepancy
and nearest-neighbour distances. Changed: for four weights the exhaustive grid replaces all of them; the designs remain for the larger sibling
searches and as evidence that sampling would have sufficed.

### Variance in benchmarks: Bouthillier et al. (2021); Card et al. (2020); Renze & Guven (2024)
Did: decomposed benchmark variance into data sampling, initialisation and other sources; showed most NLP test sets lack power; found temperature
in 0–1 does not change problem-solving accuracy. Took: item bootstraps everywhere, 100 items per dataset, temperature 0 as a reproducibility
choice with a planned repeat subset. Changed: documented which providers refuse temperature control and recorded the decoding per answer.

### Class imbalance in matching benchmarks: Papadakis et al. (2024)
Did: re-evaluated entity-matching benchmarks and showed that the usual balanced or easy splits overstate matcher quality; released re-balanced
sets (Dn1–Dn8). Took: the Dn sets in the suite at their real ratios, and the motivation for post-stratification. Changed: balanced pools are kept
for calibration while official-ratio F1 is reported for comparability.

### Survey estimation: Horvitz & Thompson (1952)
Did: unbiased estimation of a population mean from a sample with known inclusion probabilities. Took: post-stratification weights
(official share / sample share) and the weighted bootstrap. Changed: applied to benchmark items as a population, with the official split as the
target.

### Leaderboard integrity: The Leaderboard Illusion (Singh et al., 2025)
Did: documented how private testing and selective reporting distort a public leaderboard. Took: the discipline of reporting every candidate and
every bootstrap draw, archiving replaced answers, and tagging re-asks. Changed: our selection effect is weight search rather than model
submission, and the nested bootstrap is the counter-measure.

### Qualitative model differences: VibeCheck (Dunlap et al., 2024)
Did: extracted and quantified qualitative traits that predict human preference. Took: the reminder that a lexical judge cannot see style,
hedging or formatting quality; the hedge flag is our one concession. Changed: nothing adopted; cited as the complementary axis our evaluation
does not cover.

### The matching and table benchmarks themselves
Mudgal et al. (2018, DeepMatcher / Magellan sets); Li et al. (2020, Ditto); Peeters, Der & Bizer (2024, WDC Products); Wang et al. (2021,
Machamp); Crescenzi et al. (2021, Alaska); Koutras et al. (2021, Valentine); Liu et al. (2025, Magneto); Zhang et al. (2021, SMAT); Cheng et al.
(2022, HiTab); Pasupat & Liang (2015, WTQ); Chen et al. (2020, TabFact); Nan et al. (2022, FeTaQA); Zhu et al. (2021, TAT-QA); Li et al. (2023,
BIRD); Wu et al. (2025, TableBench); Sui et al. (2024, SUC). Took: their official splits, their native metrics as the baseline column, and their
published numbers as the comparison point for the official-split estimates. Changed: per-column framing for schema matching, result-value grading
for BIRD, and stratified 150-item pools; all stated in the data table.
