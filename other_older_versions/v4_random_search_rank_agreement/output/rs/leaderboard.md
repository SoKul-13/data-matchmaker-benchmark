# Common score and pooled leaderboard (calibrated weights, 7 datasets x 40 items)

Weights: em 0.05, num_tol 0.25, num_decay 0.05, tok_prec 0.05, tok_rec 0.15, edit_sim 0.15, rouge_l 0.25, jaccard 0.05 (J = 0.476)

| Model | FeTaQA | FinanceBench | FinQA | OfficeQA | TabFact | TAT-QA | WTQ | Common (mean) | Common (z-mean) | Borda | Kemeny | RRF | 95% CI (Borda rank) | Native-metric Borda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.5 | 0.39 | 0.49 | 0.66 | 0.04 | 0.75 | 0.74 | 0.88 | 0.564 | +0.57 | 1 | 1 | 1 | [1, 2] | 1 |
| claude-opus-5 | 0.35 | 0.46 | 0.67 | 0.00 | 0.57 | 0.79 | 0.89 | 0.534 | +0.15 | 2 | 2 | 2 | [1, 4] | 3 |
| claude-sonnet-5 | 0.31 | 0.45 | 0.57 | 0.03 | 0.57 | 0.78 | 0.88 | 0.513 | -0.20 | 3 | 3 | 3 | [2, 4] | 2 |
| gpt-5.4-mini | 0.24 | 0.43 | 0.61 | 0.02 | 0.75 | 0.77 | 0.83 | 0.521 | -0.52 | 4 | 4 | 4 | [2, 4] | 4 |

## Agreement of each dataset's ranking with the pooled (Borda) ranking (Kendall tau)

| FeTaQA | FinanceBench | FinQA | OfficeQA | TabFact | TAT-QA | WTQ |
|---|---|---|---|---|---|---|
| 1.00 | 1.00 | 0.33 | 0.33 | 0.00 | 0.00 | 0.67 |

## Agreement between pooling rules (Kendall tau of consensus rankings)

|            |   mean_score |   mean_z |   mean_rank |   borda |   copeland |   rrf |   kemeny |
|:-----------|-------------:|---------:|------------:|--------:|-----------:|------:|---------:|
| mean_score |         1    |     0.67 |        0.67 |    0.67 |       0.67 |  0.67 |     0.67 |
| mean_z     |         0.67 |     1    |        1    |    1    |       1    |  1    |     1    |
| mean_rank  |         0.67 |     1    |        1    |    1    |       1    |  1    |     1    |
| borda      |         0.67 |     1    |        1    |    1    |       1    |  1    |     1    |
| copeland   |         0.67 |     1    |        1    |    1    |       1    |  1    |     1    |
| rrf        |         0.67 |     1    |        1    |    1    |       1    |  1    |     1    |
| kemeny     |         0.67 |     1    |        1    |    1    |       1    |  1    |     1    |

Pooled (Borda) ranking vs. native-metric Borda ranking: tau = 0.67; vs. EM-only Borda: tau = 0.33.
