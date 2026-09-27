# Is v3 NeurIPS-ready? Assessment and gap list (2026-09-08)

**Short answer: no, not yet.** Solid workshop paper / internal report; a main-track or Datasets & Benchmarks
submission would be rejected on evidence, not on ideas. Ordered by how much each gap matters.

## Blocking
1. **Four models, 40 items per dataset.** All ranking claims have overlapping intervals; Kendall τ on four
   systems takes only six values. Target: 8–12 models across providers and open weights, 100–150 items per
   dataset. Cost: the ≈ USD 22 prediction run + Gemini billing + free keys (see `06_USER_TODO.md`); wired.
2. **The anchor is synthetic and hand-scaled.** The central claim ("calibrated to answer quality") rests on a
   utility scale written by us. Needed: 300–500 real answers labelled correct / partial / wrong by two
   annotators, agreement reported; used as the anchor (`02_select_metrics.py --labels`) or as the held-out
   test of the synthetic anchor.
3. **Only 7 of 14 datasets have model results**, and none of the data-matching half. Run the suite end to end.

## Serious
4. **The headline metric comparison is a tie** with the typed native metric on the mixed objective. The case
   must be made with anchor/probe results and, ideally, human-label correlation where the ensemble wins;
   otherwise reviewers ask "why not just use each dataset's metric?"
5. **No LLM-judge baseline.** A 2026 metrics paper must place a cheap calibrated lexical metric against
   GPT-class judging (agreement with humans, cost, gaming resistance). One extra run.
6. **No significance testing across datasets** (Friedman–Nemenyi) and no prompt/seed variation (one prompt,
   one sample per item).
7. **Related work is thin** for a metrics paper: learned metrics (COMET, BLEURT, BERTScore variants),
   LLM-judge calibration, IRT-based benchmark aggregation.

## Presentation
8. Six pages is short for main track; needs an appendix: the 100 metric definitions, the operator table,
   per-dataset examples, the full grid.
9. Author line is a placeholder; venue-format limitations/ethics sections; final figure polish.

## Already at conference level
Method coherence (anchors not models as target; gate instead of additive indicators; ensemble of the 100
best weightings; LODO + severity perturbation), full reproducibility in minutes, complete documentation,
honest reporting of the tie and the two fixed metric bugs.

## Realistic path
Items 1, 3, 5: one–two days of compute/API once keys exist. Item 2: about a week of annotation. Items 6–8:
about a week of writing. With all of them: credible D&B-track or metrics-workshop submission. Without item 2
it stays a workshop paper.
