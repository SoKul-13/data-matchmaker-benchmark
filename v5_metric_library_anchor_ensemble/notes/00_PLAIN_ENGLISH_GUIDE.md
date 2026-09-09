# Plain-English guide: what this project does, term by term, version by version

Read this first if you are new to the project. No prior knowledge assumed.

---

## 1. The overall goal, in one paragraph

We have several AI language models (GPT, Claude, Gemini, …). We want to say which one is best at
**data-matching work**: deciding whether two records describe the same thing, reading numbers out of
financial tables and documents, combining tables, answering questions about them. There are many
public test sets for these tasks, but each one grades answers its own way, so you cannot add their
scores up or compare them. The project builds a **judge** that grades every answer the same way on
every test set, so that one number per model means the same thing everywhere, and then turns those
numbers into one ranked list with honest error bars.

---

## 2. Glossary: every non-everyday term, with what it means and where it is used here

**Green agent / purple agent / A2A.** In the AgentBeats platform a *green agent* is the judge program;
a *purple agent* is the AI system being tested. They talk over *A2A* (Agent-to-Agent), a standard
message format, so any purple agent can be plugged into our judge. Used: the judge is the product; the
paper is about its grading rule.

**Benchmark / dataset.** A benchmark is a test: questions plus correct answers. A dataset is the file
holding them. Used: FinQA, TAT-QA, TabFact, WikiTableQuestions, FeTaQA, FinanceBench, OfficeQA, HiTab,
and the record-matching sets (Abt-Buy, Amazon-Google, DBLP-Scholar, Walmart-Amazon, WDC Products) and
the benchmark's own TPC-DI task.

**Item.** One question with its correct answer and any context (table, document, two records).

**Gold answer (ground truth).** The correct answer the dataset authors wrote. Everything is graded
against it. **Alias**: an equally correct spelling of it (`14%` and `0.14464`). **List gold**: a correct
answer that is a set of things (`$7,870 | $12,129`), where order does not matter.

**Prediction.** The model's answer text. **Final-answer extraction**: pulling the actual answer out of
the model's reasoning text (we ask models to end with `FINAL ANSWER: …`).

**Answer type.** Numeric (a number), boolean (yes/no), text (a short phrase or list), free-form
(a sentence). Detected automatically from the gold; decides which grading rules make sense.

**Metric.** A formula that compares a prediction with the gold and returns a number from 0 (wrong) to 1
(perfect). Examples below. **Native metric**: the metric the dataset's own authors use.

**Exact match (EM).** 1 if the cleaned-up prediction is identical to the cleaned-up gold, else 0.
Strict; `1,577` vs `1577.0` must be normalised first or EM fails.

**Numeric tolerance.** 1 if the predicted number is within 1 % of the gold number. Used for money and
percentages where rounding differs.

**Relative error (RE).** |prediction − gold| ÷ |gold|. **Graded numeric error / decay**: a score that
falls smoothly as RE grows, e.g. e^(−2.5·RE): a 2 % miss still earns 0.95, a 50 % miss earns 0.29.

**Token.** A word after splitting on spaces. **Precision**: of the words the model said, what fraction
are in the gold. **Recall**: of the gold's words, what fraction the model said. **F1**: the balance of
the two (harmonic mean). Used for short text answers.

**n-gram.** A run of n consecutive words; bigram = 2 words. Bigram recall = fraction of the gold's word
pairs the model reproduced, in order.

**Edit distance (Levenshtein).** Number of single-character changes to turn one string into another;
turned into a similarity from 0 to 1. Catches typos.

**ROUGE-L.** Longest common subsequence of words between prediction and gold, expressed as a score;
standard for sentence-length answers.

**Jaccard.** Overlap of two word sets: shared ÷ total distinct. Order-blind.

**Composite / weighted sum.** Final score = w₁·metric₁ + w₂·metric₂ + …, where the **weights** w add
to 1. Choosing the weights is the whole calibration problem.

**Simplex.** The set of all weight lists that are non-negative and sum to 1. **Grid**: the simplex
sampled at fixed steps (0, 0.05, 0.10, …). **Grid search**: try every point on the grid, score each,
pick by a rule. **Random search**: try a random subset of grid points.

**Objective.** The number a search maximises; it encodes what "good weights" means.

**Ranking.** Sorting models from best to worst. **Kendall τ (tau).** Agreement between two rankings,
from −1 (reversed) through 0 (unrelated) to +1 (identical); counts pairs of models ordered the same way
minus pairs ordered differently. **Spearman ρ (rho).** Agreement between two lists of numbers by their
ranks; used to ask "does the metric rise when true quality rises".

**AUC.** Probability that a random correct answer scores higher than a random wrong one; 1 is perfect
separation, 0.5 is coin-flip.

**z-score / normalisation.** Re-expressing a dataset's scores as "how many standard deviations above
that dataset's average", so hard and easy datasets become comparable.

**Pooling / rank aggregation.** Combining per-dataset rankings into one. **Borda**: each model gets
points by position in every dataset (first = most), sum the points. **Kemeny–Young**: the single
ordering that disagrees least with all the per-dataset orderings. **Copeland**: count the head-to-head
wins. **RRF (reciprocal rank fusion)**: sum of 1/(60 + rank). **Bradley–Terry**: a statistical model
that turns pairwise wins into a strength score with an error bar.

**Bootstrap.** Re-draw the test items at random (with replacement) many times, recompute the result
each time, and see how much it moves. Gives a **confidence interval** (CI): the range the result would
fall in 95 % of the time if the test had been drawn differently.

**Leave-one-dataset-out (LODO).** Fit everything without one dataset, then test on it. Shows whether
the result transfers to data it never saw.

**Anchor.** A synthetic answer whose quality we *know* because we made it: the gold copied exactly
(quality 1), the gold with a small numeric error (0.75), the gold plus a wrong extra (0.6), a refusal
(0), a random wrong answer (0). **Utility / severity scale**: the assigned quality numbers.

**Hedging.** Giving several candidate answers ("12 or 15", "A, B, C, D") to catch credit. **Gate**:
multiplying the score by (1 − λ) when hedging is detected; λ is the penalty strength.

**Ensemble.** Instead of one winning weight list, keep the 100 best and average the scores they give;
the disagreement among them is an error bar for the weights themselves.

**KL / JS divergence, Wasserstein distance.** Ways to measure how different two distributions of
scores are. Used to ask "does the metric produce the same spread of scores on dataset A as on
dataset B for answers of the same quality". JS is symmetric and bounded, so it is the one used.

**Overfitting.** Choosing settings that fit the data you have but would not hold on new data.
**Circularity.** Judging the models with weights that were tuned by looking at those same models.

**Saturated (ceiling / floor).** A dataset where all models score near 100 % (ceiling) or near 0 %
(floor); it cannot tell models apart.

**Stratified sampling.** Picking test items so that each answer type / label is represented in
proportion; **balanced**: equal yes and no in matching sets.

**Deduplication by correlation.** Two metrics that always move together carry the same information;
keep one.

**NNLS (non-negative least squares).** Fitting weights that must be ≥ 0 so a combination best
predicts a target. **Forward selection**: add one metric at a time, keep the one that helps most, stop
when nothing helps.

**Entity matching.** Deciding whether two records (product listings, paper citations) describe the same
real thing. **TPC-DI**: a standard data-integration task: join customers, accounts and trades and
compute per-customer totals; the benchmark's original job.

**Closed-book.** Asking a question without giving the source document; only fair if the model can be
expected to know the answer. OfficeQA is closed-book here because its documents are access-restricted.

**IRT (item response theory).** The statistics behind standardised tests: every question has a
difficulty, every test-taker an ability; a score on the ability scale is comparable across different
test forms. Proposed as the next step for "rank capability on any new dataset".

---

## 3. What the data flow does, tests and proves (all versions share this skeleton)

```
items (question + gold)  ->  model answers  ->  metric(s) per answer  ->  one score per (model, dataset)
     ->  make datasets comparable  ->  one score / rank per model  ->  error bars
```
* The **item → answer** stage tests the *models*.
* The **answer → metric** stage is the judge's grading rule; the paper is about making it fair.
* The **dataset → comparable** stage removes "this dataset is just harder".
* The **rank + error bars** stage is what we can actually claim; the error bars are what stops us
  over-claiming.

What a version can *prove* depends on what its weights are checked against: nothing (v1), the models'
own agreement (v2), or answers of known quality (v3).

---

## 4. v1: the original judge

**What it was.** A judge for the TPC-DI join-and-aggregate task with a 100-point rubric (points for the
right columns, row count, coverage, numbers within 1 %, strings matching), plus, for question-answer
datasets, a composite score `0.35·F1 + 0.35·e^(−2.5·RE) + 0.15·precision + 0.15·recall` with weights
chosen by hand and justified after the fact.

**Steps.** Load dataset → send question to the model → compare answer with the gold using the composite
→ average per dataset → print a leaderboard.

**Motive.** Have *some* number per model per dataset.

**Why it does not work as a paper.** The weights are guesses; nothing checks that they are fair across
datasets. Two of the dataset loaders produced wrong golds (TAT-QA lists stored as Python text, FinQA using
the program number instead of the human answer, TabFact statements sent without the table). And the
leaderboard it shipped was produced by a script that *simulated* model answers with random numbers, so
it measured nothing.

**Pros.** Simple; the TPC-DI rubric itself is fine and is kept.
**Cons.** Unjustified weights; broken golds; no real model runs; no error bars.
**Proves.** Nothing about models.

---

## 5. v2: weights chosen so that datasets agree about the models

**What it is.** The same idea of a composite, now over 9 metrics (EM, numeric tolerance, numeric decay,
precision, recall, F1, edit similarity, ROUGE-L, Jaccard), with the weights chosen by a search.

**Steps.**
1. Fix the golds (aliases, unit-aware numbers, list golds) and fetch tables into the prompts.
2. Run real models (GPT-5.5, GPT-5.4-mini, Claude Opus 5, Claude Sonnet 5) once per item; cache the answers.
3. Compute the 9 metrics for every answer.
4. Draw 100 random weight lists from the grid. For each: score every answer → average per model per
   dataset → rank the models inside each dataset → pool the rankings with Borda → measure with Kendall τ
   how well each dataset's ranking agrees with the pooled one. Objective = the average agreement.
5. Take the best weight list. Report the leaderboard with bootstrap intervals and a leave-one-dataset-out check.

**Motive.** If the grading rule is fair, different datasets should tell the same story about which model
is better; so pick the rule that makes them agree.

**Why it works.** It removes the hand-set weights and gives a reproducible recipe; the pooling and
error bars are standard and sound.

**Why it is worse than it looks (the cons).** The objective is *circular*: it tunes the judge by looking
at the very models it will rank, and a grading rule that blurs all differences would also make datasets
"agree". With 4 close models and 40 items, τ takes only seven possible values, five weight lists tied at
the top, and the improvement over plain exact match (0.36 → 0.48) sat inside the bootstrap interval.

**Proves.** That a search can replace hand-set weights and that the leaderboard machinery works; not that
the metric measures answer quality.

---

## 6. v3: weights checked against answers of known quality

**What it is.** A library of 100 metrics, a set of synthetic answers whose quality we know, a procedure
that keeps only the metrics that predict that quality, and a grid search whose 100 best weight lists are
averaged.

**Steps.**
1. **Library.** 100 metrics in families: exact-match variants, a ladder of numeric tolerances (0.1 % … 20 %),
   graded numeric error at five steepnesses, word overlap (P/R/F1, bigrams, stems), character similarity,
   ROUGE/BLEU-style sequence scores, set overlap, structure (right type? right units?), length, commitment
   (did it hedge?), and task-specific rules. All computed identically for every answer on every dataset.
2. **Anchors.** For every gold, make answers of known quality: exact copy, reworded copy, unit variant (1.0);
   small numeric miss (0.75); partial list (0.5); gold plus a wrong extra (0.6); hedge (0.3); typo (0.6);
   sign or magnitude error (0.05); refusal or random wrong answer (0). 12,813 such answers over 14 datasets.
   This gives a target that does not depend on any model.
3. **Deduplicate.** Metrics that move together (correlation ≥ 0.95) collapse to one; 100 → 42.
4. **Select.** Add metrics one at a time to a non-negative fit that predicts anchor quality; keep a metric
   only if it improves prediction on datasets it was not fitted on. Result: three (token F1, graded numeric
   error, bigram recall). Indicator-style metrics (hedge, length) are excluded from the sum because they are
   1 for most wrong answers and would just add a constant; hedging becomes a multiplicative penalty instead.
5. **Grid search.** Every weight list over the 3 metrics at step 0.02, times five hedge-penalty strengths:
   6,630 candidates. Each is scored by: agreement with anchor quality (Spearman), separation of correct
   from wrong (AUC), same score spread across datasets for the same error type (JS divergence), agreement
   with each dataset's native metric (Kendall τ), and how close to 0 wrong answers score.
6. **Ensemble.** Keep the 100 best; the final score of an answer is their average; their disagreement is
   the weights' error bar.
7. **Leaderboard.** Average per model per dataset → z-normalise → equal dataset weights → Borda rank with
   Kemeny check → item bootstrap → also the rank range across the 100 weight lists → native-metric rank beside.
8. **Validation.** Leave-one-dataset-out (agreement 0.895 vs 0.900), perturb the quality scale by ±0.15
   (weights move by 0.17 on a 0–2 scale), and a table of what each error type actually scores.

**Motive.** Judge the judge against something whose quality is *known*, so the leaderboard cannot be
accused of grading the models by the models.

**Why it works.** Wrong answers now score 0.02 on average (v2's rule gave them up to 0.3); the metric
tracks known quality with Spearman 0.91 and AUC 0.997; it transfers to unseen datasets; it never looks
at model rankings while being calibrated.

**Cons.** The quality scale is written by us (we perturb it, and human labels can replace it); the
library is lexical, so a synonym-only paraphrase is invisible; only 4 models × 40 items have predictions,
so the leaderboard's lower ranks are not separable; the typed native metric ties the ensemble on the
combined objective because it wins the "agrees with native metrics" term by definition.

**Proves.** That a data-driven selection from a large metric library yields a small, interpretable rule
that is calibrated to a stated quality scale and consistent across datasets; and it produces a
leaderboard with two kinds of uncertainty. It does *not yet* prove the leaderboard order beyond the top,
and it does not prove the quality scale matches human judgement.

---

## 7. Side by side

| | v1 | v2 | v3 |
|---|---|---|---|
| Grading rule | 4 metrics, hand weights | 9 metrics, searched weights | 3 of 100 metrics, searched weights, 100-way ensemble, hedge penalty |
| Weights checked against | nothing | agreement among the models being ranked | synthetic answers of known quality + native metrics |
| Model answers | simulated | real (4 models) | real (4 models; 7 more datasets ready) |
| Datasets | 7 | 7 (14 wired) | 7 with results, 14 with anchors |
| Error bars | none | item bootstrap, LODO | item bootstrap, weighting range, LODO, scale perturbation |
| Main risk | meaningless | circular | hand-set quality scale |
| What it can claim | nothing | a recipe and a leaderboard | a calibrated, transferable grading rule and a leaderboard |

## 8. What is still needed to claim more
More models (8+), more items (100–150 per dataset), the 7 pending datasets run, and human quality labels
on a few hundred answers to confirm the synthetic scale. See `05_CONFERENCE_READINESS.md` and `06_USER_TODO.md`.
