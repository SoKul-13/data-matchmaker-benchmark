# 🏆 Model Leaderboard Rankings & Hyperparameter Grid Search Analysis

## 1. Active Implemented Models Leaderboard

|   rank | model             | provider   | model_type               |   custom_rubric_score |   original_rubric_score | f1_score_pct   | latency_sec   |
|-------:|:------------------|:-----------|:-------------------------|----------------------:|------------------------:|:---------------|:--------------|
|      1 | claude-3-5-haiku  | Anthropic  | Speed/Flash              |                 14.71 |                   45.52 | 0.00%          | 0.342s        |
|      2 | gemini-2.5-flash  | Google     | Speed/Flash              |                 14.7  |                   45.52 | 0.00%          | 0.154s        |
|      3 | o3-mini           | OpenAI     | Deep Reasoning           |                  8.81 |                   37.83 | 0.00%          | 0.208s        |
|      4 | gpt-4o            | OpenAI     | Flagship                 |                  8.77 |                   37.76 | 0.00%          | 0.376s        |
|      5 | gemini-2.5-pro    | Google     | Long Context / Reasoning |                  2.86 |                   30    | 0.00%          | 0.146s        |
|      6 | claude-3-7-sonnet | Anthropic  | Flagship                 |                  2.86 |                   30    | 0.00%          | 0.227s        |
|      7 | gemini-3.6-flash  | Google     | Speed/Flash              |                  2.86 |                   30    | 0.00%          | 0.344s        |
|      8 | gpt-4o-mini       | OpenAI     | Speed/Flash              |                  2.85 |                   30    | 0.00%          | 0.313s        |

## 2. Hyperparameter Grid Search Analysis (Implemented Models)

| model             |   temperature |   top_p |   custom_rubric_score | f1_score_pct   | exact_match_pct   |
|:------------------|--------------:|--------:|----------------------:|:---------------|:------------------|
| claude-3-5-haiku  |           0   |     1   |                 14.71 | 0.00%          | 0.00%             |
| claude-3-5-haiku  |           0.3 |     0.9 |                  8.79 | 0.00%          | 0.00%             |
| claude-3-5-haiku  |           0.7 |     0.9 |                  2.86 | 0.00%          | 0.00%             |
| claude-3-7-sonnet |           0   |     1   |                  2.86 | 0.00%          | 0.00%             |
| claude-3-7-sonnet |           0.3 |     0.9 |                  8.79 | 0.00%          | 0.00%             |
| claude-3-7-sonnet |           0.7 |     0.9 |                  8.78 | 0.00%          | 0.00%             |
| gemini-2.5-flash  |           0   |     1   |                 14.7  | 0.00%          | 0.00%             |
| gemini-2.5-flash  |           0.3 |     0.9 |                  2.86 | 0.00%          | 0.00%             |
| gemini-2.5-flash  |           0.7 |     0.9 |                 15.22 | 0.00%          | 0.00%             |
| gemini-2.5-pro    |           0   |     1   |                  2.86 | 0.00%          | 0.00%             |
| gemini-2.5-pro    |           0.3 |     0.9 |                  2.86 | 0.00%          | 0.00%             |
| gemini-2.5-pro    |           0.7 |     0.9 |                  8.78 | 0.00%          | 0.00%             |
| gemini-3.6-flash  |           0   |     1   |                  2.86 | 0.00%          | 0.00%             |
| gemini-3.6-flash  |           0.3 |     0.9 |                  8.78 | 0.00%          | 0.00%             |
| gemini-3.6-flash  |           0.7 |     0.9 |                  2.86 | 0.00%          | 0.00%             |
| gpt-4o            |           0   |     1   |                  8.77 | 0.00%          | 0.00%             |
| gpt-4o            |           0.3 |     0.9 |                  2.85 | 0.00%          | 0.00%             |
| gpt-4o            |           0.7 |     0.9 |                 15.21 | 0.00%          | 0.00%             |
| gpt-4o-mini       |           0   |     1   |                  2.85 | 0.00%          | 0.00%             |
| gpt-4o-mini       |           0.3 |     0.9 |                  8.78 | 0.00%          | 0.00%             |
| gpt-4o-mini       |           0.7 |     0.9 |                  8.78 | 0.00%          | 0.00%             |
| o3-mini           |           0   |     1   |                  8.81 | 0.00%          | 0.00%             |
| o3-mini           |           0.3 |     0.9 |                  8.81 | 0.00%          | 0.00%             |
| o3-mini           |           0.7 |     0.9 |                  8.81 | 0.00%          | 0.00%             |

## 3. Best Overall Implemented Model Recommendation

**Best Overall Active Model**: `claude-3-5-haiku` by **Anthropic** with a Custom Rubric Score of **14.71 / 100**.

- **Optimal Temperature**: `0.0` (Deterministic mode maximizes numerical accuracy).
- **Optimal Top_P**: `1.0`.
