# v3: constraints stated before building, and the choice taken per section

Written before the build (2026-09-08). Everything marked "alternative taken" is what v3 does.

## What is not possible now, or costs money / time

| Item | Constraint | Alternative taken | Pros / cons |
|---|---|---|---|
| Predictions on the 7 new datasets (HiTab, Abt-Buy, Amazon-Google, DBLP-Scholar, Walmart-Amazon, WDC, TPC-DI cells) | ≈ USD 22 of API spend on the 4 cached models; the user's call | v3 is built and validated on the cached 4 models × 7 original datasets; the new pools are wired in and `01_compute_matrix.py` picks them up as soon as `data/predictions/` covers them | free now; statistics stay weak until run (`uv run python scripts/00_run_models.py --sequential`) |
| More models (Gemini billing, Groq / Mistral free keys, xAI credits) | account actions by the user | 4 models | coarse ranks; every claim carries a bootstrap interval |
| Human correctness labels as the calibration anchor | ≈ 300 answers, 2–3 h of annotation | synthetic known-quality anchors (`src/anchors/ladder.py`, 20 operators with a stated utility scale) + native-metric fidelity | free, controllable, dataset-independent; the severity scale is a stated choice and is perturbed in validation; `02_select_metrics.py --labels file.csv` accepts human labels when they exist |
| Semantic metrics (sentence embeddings, NLI, BERTScore) | ~1 GB torch + model download; minutes of CPU | implemented as an optional family (8 slots: 2 embedding cosines + thresholds, NLI/BERTScore reserved), off by default (`--semantic` flag) | library is dependency-free by default; free-form gains deferred |
| METEOR / TER / BERTScore packages | extra dependencies | in-house equivalents (meteor_lite, ter_score, chrF-style) | reproducible, slightly non-standard |
| Execution-based metrics | need programs; only FinQA has them | placeholder that falls back to numeric tolerance | small coverage |
| Grid over 100 metrics | infeasible (simplex in 100-D) | deduplicate (Spearman ≥ 0.95 clusters) → select 6–10 against the anchor (non-negative forward selection, leave-one-dataset-out stop) → grid over survivors (step 0.05/0.1) → keep the 100 best weightings → ensemble | the only workable route; selection quality depends on the anchor |
| IRT capability model (design-space §15) | unreliable with 4 models | documented; `scripts/90_irt_experimental.py` fits a Rasch model but is not in the headline | ready when ≥ 8 models exist |
| Paper numbers | change when new predictions land | generated from `output/` by script | one command to refresh |
| KG embeddings (node2vec / TransE) as semantic metrics | wrong tool for free text (they embed graph nodes, not sentences); need entity linking + a KG | not used | see design-space §16 |
| Datasets' own scoring guides | not needed for scoring | kept as a baseline column and as the fidelity term | drops nothing the authors would report |

## Choice per section (the "best" pick given the constraints)

| Section | Choice | Why |
|---|---|---|
| Datasets | 7 original (cached) + 7 new (pools built; predictions pending); OfficeQA parked | matching proper + reasoning over tables; ≥ 100 items where new |
| Answer scoring | 100-metric library (`src/metrics/library.py`), computed identically for every answer of every dataset | one structure; no dataset-specific rule |
| Calibration anchor | synthetic known-quality anchors (utility scale) + native fidelity; human labels accepted if provided | the only free anchor that is not the models themselves |
| Metric selection | dedupe → non-negative forward selection on anchor agreement with LODO stop | avoids collinearity and overfitting |
| Weight search | full grid over the k survivors (step 0.05 if k ≤ 6 else 0.1); objective = anchor Spearman + anchor AUC + cross-dataset consistency of anchor scores (JS at matched utility) + native fidelity; keep the 100 best weightings | grid is exhaustive where it is feasible; "100 best" = the ensemble |
| Final metric | mean over the 100 best weightings; spread = uncertainty | removes the arbitrariness of one winner |
| Leaderboard | per-dataset means → z-normalise → equal dataset weights; Borda headline, Kemeny check; item bootstrap; native ranking beside | difficulty removed, no tuned dataset weights |
| Validation | LODO on selection and weights; severity-scale perturbation; gaming probes; grid sensitivity | shows what transfers |
| Green agent | ships the k metrics + 100 weightings; QA mode returns ensemble score + spread per item | dataset-agnostic judge |
