# v2: grid search over the v1 rubric weights (105 candidates: v1 point + 4 corners + 100 random grid points, step 0.05)

| rank | label | F1 | decay | precision | recall | J (mean tau to pooled) | tau to native | J 95% CI |
|---|---|---|---|---|---|---|---|---|
| 1 | random_059 | 0.85 | 0.00 | 0.05 | 0.10 | 0.507 | 0.496 | [0.22, 0.55] |
| 2 | only_recall | 0.00 | 0.00 | 0.00 | 1.00 | 0.494 | 0.332 | [0.22, 0.59] |
| 3 | random_010 | 0.25 | 0.15 | 0.05 | 0.55 | 0.490 | 0.439 | [0.17, 0.55] |
| 4 | random_006 | 0.80 | 0.05 | 0.00 | 0.15 | 0.476 | 0.487 | [0.17, 0.50] |
| 5 | random_007 | 0.65 | 0.20 | 0.05 | 0.10 | 0.476 | 0.487 | [0.13, 0.50] |
| 6 | random_015 | 0.15 | 0.20 | 0.10 | 0.55 | 0.476 | 0.487 |  |
| 7 | random_019 | 0.50 | 0.10 | 0.20 | 0.20 | 0.476 | 0.487 |  |
| 8 | random_029 | 0.00 | 0.20 | 0.25 | 0.55 | 0.476 | 0.487 |  |
| 9 | random_042 | 0.60 | 0.15 | 0.00 | 0.25 | 0.476 | 0.487 |  |
| 10 | random_044 | 0.30 | 0.15 | 0.10 | 0.45 | 0.476 | 0.487 |  |
| 35 | **v1_original** | 0.35 | 0.35 | 0.15 | 0.15 | 0.429 | 0.419 | [0.12, 0.49] |

27 of 104 other candidates beat the v1 weights on J; the best beats v1 by +0.078, inside the bootstrap interval.

## Leaderboard under the best weights

| Model | fetaqa | financebench | finqa | officeqa | tab_fact | tat_qa | wikitablequestions | Borda | Kemeny | 95% CI (items) | v1-weights Borda | native Borda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5.5 | 0.67 | 0.57 | 0.53 | 0.04 | 0.75 | 0.79 | 0.88 | 1 | 1 | [1, 2] | 1 | 1 |
| claude-opus-5 | 0.58 | 0.52 | 0.55 | 0.00 | 0.57 | 0.86 | 0.89 | 2 | 2 | [1, 3] | 2 | 3 |
| claude-sonnet-5 | 0.54 | 0.52 | 0.39 | 0.01 | 0.57 | 0.86 | 0.88 | 3 | 3 | [2, 4] | 3 | 2 |
| gpt-5.4-mini | 0.43 | 0.48 | 0.49 | 0.00 | 0.75 | 0.81 | 0.82 | 4 | 4 | [3, 4] | 4 | 4 |
