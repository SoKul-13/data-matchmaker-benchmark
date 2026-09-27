# v3 leaderboard: ensemble metric (3 selected metrics x 100 best weightings), 4 models, 7 datasets

| Model | FeTaQA | FinanceBench | FinQA | OfficeQA | TabFact | TAT-QA | WTQ | Common (z-mean) | Borda | Kemeny | 95% CI (items) | Rank range over 100 weightings | Native Borda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5 | 0.55 | 0.55 | 0.80 | 0.13 | 0.57 | 0.72 | 0.88 | +0.23 | 2 | 1 | [1, 4] | 1–2 | 2 |
| gpt-5.5 | 0.62 | 0.55 | 0.83 | 0.04 | 0.75 | 0.71 | 0.88 | +0.27 | 2 | 2 | [1, 3] | 1–2 | 1 |
| claude-opus-5 | 0.57 | 0.49 | 0.81 | 0.02 | 0.57 | 0.72 | 0.91 | -0.17 | 4 | 4 | [1, 4] | 3–4 | 3 |
| gpt-5.4-mini | 0.35 | 0.51 | 0.78 | 0.06 | 0.75 | 0.73 | 0.84 | -0.33 | 4 | 3 | [2, 4] | 3–4 | 4 |

Dataset agreement with pooled rank (tau): FeTaQA 0.41, FinanceBench 0.82, FinQA 0.41, OfficeQA 0.41, TabFact 0.00, TAT-QA -0.41, WTQ 0.00
Mean pairwise dataset tau: -0.07; pooled vs native-metric pooled rank: tau 0.82

Rule agreement (tau):
|            |   mean_score |   mean_z |   mean_rank |   borda |   copeland |   rrf |   kemeny |
|:-----------|-------------:|---------:|------------:|--------:|-----------:|------:|---------:|
| mean_score |         1    |     1    |        0.55 |    0.82 |       0.33 |  0.67 |     0.33 |
| mean_z     |         1    |     1    |        0.55 |    0.82 |       0.33 |  0.67 |     0.33 |
| mean_rank  |         0.55 |     0.55 |        1    |    0.89 |       0.91 |  0.55 |     0.91 |
| borda      |         0.82 |     0.82 |        0.89 |    1    |       0.82 |  0.82 |     0.82 |
| copeland   |         0.33 |     0.33 |        0.91 |    0.82 |       1    |  0.67 |     1    |
| rrf        |         0.67 |     0.67 |        0.55 |    0.82 |       0.67 |  1    |     0.67 |
| kemeny     |         0.33 |     0.33 |        0.91 |    0.82 |       1    |  0.67 |     1    |
