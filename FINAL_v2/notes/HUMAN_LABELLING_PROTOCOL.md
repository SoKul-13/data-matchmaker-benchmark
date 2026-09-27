# Human labelling protocol: what to make so the anchors can be replaced by real judgements

Purpose: v5 (and v2's section 5) validate the scoring rule against *synthetic* answers of known utility. Reviewers will ask for human
judgements. This protocol produces a label file the pipeline already accepts (`02_select_metrics.py --labels` in v5; the same file is
read by v2's step 4 when present) and is sized so two people can finish it in one to two days.

## 1. What is labelled
One row = one (dataset, item, model) answer already in `data/predictions/`. The labeller sees the question, the context or table
(as shown to the model), the gold answer with its aliases, and the model's raw answer. They do **not** see the model name or any metric.

## 2. Sample: 400 answers, stratified
| stratum | rows | why |
|---|---|---|
| answer type: numeric / boolean / text / free-form | 100 each | every scorer component is exercised |
| within each type: models | equal share per model | no model dominates |
| within each type: datasets | proportional to the suite, at least 5 per dataset | every dataset represented |
| "disagreement" oversample | 25 % of rows drawn from answers where exact match and the v1 composite disagree by ≥ 0.5 | the informative cases are where lexical rules disagree |
Draw with seed 20260923; the sampling script writes `labels/sample.csv` with a blind `row_id` and the display fields only.

## 3. The label (one main field, two auxiliaries)
* **utility** ∈ {1.0 correct, 0.75 correct with a minor defect (rounding, unit written differently, extra harmless words), 0.5 partially correct (one of several required parts, or right value wrong unit / scale), 0.25 wrong but related (right entity wrong attribute, off by a magnitude, plausible distractor), 0.0 wrong or empty}.
  Five levels, anchored by the same operators the synthetic ladder uses, so human utility and synthetic utility are on one scale.
* **hedged** ∈ {0, 1}: the answer offers more than one final candidate or refuses to commit.
* **note**: free text, optional (used only to audit disagreements).

## 4. Two labellers, adjudication, agreement
* Both label all 400 independently. Report Krippendorff's α (ordinal) and exact agreement on utility; Cohen's κ on hedged.
* Disagreements of more than one level go to a third person or a joint session; the adjudicated value is final.
* Target α ≥ 0.75. Below 0.6, revise the guideline wording and re-label 50 rows before continuing.

## 5. Labelling guide (give this to the labellers)
1. Judge the **final answer**, not the reasoning. If there is a "FINAL ANSWER:" line, judge that line; otherwise judge the last stated answer.
2. Numbers: equal within the dataset's tolerance (1 %) is correct; a different unit or scale word (million vs thousand) is 0.5; a sign error or wrong magnitude is 0.25.
3. Yes/no: correct or wrong only (1.0 or 0.0); "probably yes" counts as yes but sets hedged = 1.
4. Lists: all required items and no wrong ones = 1.0; missing some = 0.5; wrong extra items = 0.25.
5. Free-form sentences: the sentence states the gold fact correctly = 1.0; correct but incomplete = 0.5; contradicts the gold = 0.0.
6. Aliases listed with the gold are all fully correct.
7. An empty answer, a refusal, or "cannot be determined" when the gold exists = 0.0.
8. Never look up the answer yourself; judge only against the gold shown.

## 6. Output file
`data/labels/human_labels.csv` with columns `dataset, uid, model, utility, hedged, labeller, adjudicated` (one adjudicated row per answer plus
the two raw rows). The pipeline uses adjudicated rows only.

## 7. How it is used
* v5: `uv run python v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv` replaces the synthetic utility with the
  human one in metric selection and weight search; the synthetic run stays as the comparison.
* v2: step 4 reports ρ and AUC against human utility next to the synthetic ρ and AUC; the two columns side by side are the validity argument.
* Report the correlation between synthetic and human utility on the 400 rows: if it is high (> 0.8), the synthetic anchors are vindicated for
  the full 12,000; if not, the human column is the one to cite.

## 8. Effort and cost
400 answers × 2 labellers at about 45 seconds each ≈ 5 hours per person. No money if done in-house; about USD 150–250 on a labelling
platform at typical rates. The only step that cannot be automated.
