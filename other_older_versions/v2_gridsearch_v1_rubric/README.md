# v2 — grid search over the v1 rubric's own weights

**Question.** v1 scored every answer as

    R(answer) = 0.35·F1 + 0.35·exp(−2.5·MRE) + 0.15·Precision + 0.15·Recall

with the four weights chosen by hand. If we keep exactly those four ingredients and only let a grid search
choose the weights, does anything change, and does v1's choice look good or bad?

**Method.** `scripts/01_v1_components.py` computes the four ingredients (token F1, numeric decay, token precision,
token recall) for every cached model answer (4 models × 7 datasets × 40 items), using the fixed gold handling
(aliases, unit-aware numbers, list golds). `scripts/02_gridsearch.py` evaluates 105 weightings: v1's point, the four
single-metric corners and 100 random points on the step-0.05 simplex. For each weighting `w`:

    R_w(answer) = w₁·F1 + w₂·decay + w₃·P + w₄·R          (w ≥ 0, Σw = 1)
    mean per (model, dataset)  →  rank models inside each dataset  →  Borda-pool the rankings
    J(w) = mean over datasets of Kendall τ( dataset ranking , pooled ranking )

with, alongside, τ to each dataset's native metric, the spread of a model's centred score across datasets, and an
item bootstrap of J for the top 5, v1's point and the worst.

**Result** (`output/leaderboard.md`, `output/best.json`, `output/fig_grid.png`): v1's weights rank 35th of 105
(J = 0.429); 27 candidates beat them; the best (F1 0.85, P 0.05, R 0.10, decay 0) reaches 0.507, a gain of +0.078 that
sits inside the bootstrap interval [0.22, 0.55]. Numeric decay gets no weight in the best mixes because on these 7
datasets its ranking signal is already carried by F1 on numeric answers and it inflates wrong answers elsewhere.

**Reading.** The four v1 ingredients are reasonable, the hand-set proportions are not special, and with 4 models × 40
items no weighting is statistically better than another. This folder is deliberately minimal: same objective as
v4, no new metrics, no anchors.

**Run.** `uv sync && scripts/run_all.sh` (seconds).
