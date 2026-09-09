# 📊 Master Benchmark Evaluation Results

Comprehensive benchmark performance matrix across 8 datasets, 8 active implemented LLM models, and 3 hyperparameter configurations.

## 1. Implemented Active Models Performance Summary

| provider   | model             | model_type               | exact_match_pct   | precision_pct   | recall_pct   | f1_score_pct   | mean_relative_error_pct   |   original_rubric_score |   custom_rubric_score | latency_sec   |
|:-----------|:------------------|:-------------------------|:------------------|:----------------|:-------------|:---------------|:--------------------------|------------------------:|----------------------:|:--------------|
| Anthropic  | claude-3-5-haiku  | Speed/Flash              | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 61.27%                    |                   45.52 |                 14.71 | 0.342s        |
| Google     | gemini-2.5-flash  | Speed/Flash              | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 61.33%                    |                   45.52 |                 14.7  | 0.154s        |
| OpenAI     | o3-mini           | Deep Reasoning           | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 80.42%                    |                   37.83 |                  8.81 | 0.208s        |
| OpenAI     | gpt-4o            | Flagship                 | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 80.84%                    |                   37.76 |                  8.77 | 0.376s        |
| Google     | gemini-2.5-pro    | Long Context / Reasoning | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 100.16%                   |                   30    |                  2.86 | 0.146s        |
| Anthropic  | claude-3-7-sonnet | Flagship                 | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 100.19%                   |                   30    |                  2.86 | 0.227s        |
| Google     | gemini-3.6-flash  | Speed/Flash              | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 100.22%                   |                   30    |                  2.86 | 0.344s        |
| OpenAI     | gpt-4o-mini       | Speed/Flash              | 0.00%             | 0.00%           | 0.00%        | 0.00%          | 100.25%                   |                   30    |                  2.85 | 0.313s        |

## 2. Dataset-by-Dataset Performance Matrix

| dataset            | model             | exact_match_pct   | f1_score_pct   |   original_rubric_score |   custom_rubric_score |
|:-------------------|:------------------|:------------------|:---------------|------------------------:|----------------------:|
| fetaqa             | claude-3-5-haiku  | 0.00%             | 83.54%         |                   88.61 |                 83.68 |
| fetaqa             | claude-3-7-sonnet | 0.00%             | 82.13%         |                   87.64 |                 82.28 |
| fetaqa             | gemini-2.5-flash  | 0.00%             | 82.13%         |                   87.64 |                 82.28 |
| fetaqa             | gemini-2.5-pro    | 0.00%             | 82.13%         |                   87.64 |                 82.28 |
| fetaqa             | gemini-3.6-flash  | 0.00%             | 83.54%         |                   88.61 |                 83.68 |
| fetaqa             | gpt-4o            | 0.00%             | 86.22%         |                   90.45 |                 86.31 |
| fetaqa             | gpt-4o-mini       | 0.00%             | 82.13%         |                   87.64 |                 82.28 |
| fetaqa             | o3-mini           | 0.00%             | 82.13%         |                   87.64 |                 82.28 |
| financebench       | claude-3-5-haiku  | 0.00%             | 48.80%         |                   60.53 |                 45.72 |
| financebench       | claude-3-7-sonnet | 0.00%             | 47.86%         |                   44.49 |                 32.23 |
| financebench       | gemini-2.5-flash  | 0.00%             | 47.86%         |                   44.49 |                 32.33 |
| financebench       | gemini-2.5-pro    | 0.00%             | 47.86%         |                   44.49 |                 32.33 |
| financebench       | gemini-3.6-flash  | 0.00%             | 52.09%         |                   53.67 |                 41.8  |
| financebench       | gpt-4o            | 0.00%             | 47.86%         |                   44.49 |                 32.09 |
| financebench       | gpt-4o-mini       | 0.00%             | 49.09%         |                   52.85 |                 39.81 |
| financebench       | o3-mini           | 0.00%             | 47.86%         |                   59.97 |                 42.7  |
| finqa              | claude-3-5-haiku  | 0.00%             | 0.00%          |                   45.61 |                 13.71 |
| finqa              | claude-3-7-sonnet | 0.00%             | 0.00%          |                   30    |                  0.53 |
| finqa              | gemini-2.5-flash  | 0.00%             | 0.00%          |                   30    |                  0.54 |
| finqa              | gemini-2.5-pro    | 0.00%             | 0.00%          |                   45.61 |                 13.72 |
| finqa              | gemini-3.6-flash  | 0.00%             | 0.00%          |                   30    |                  0.52 |
| finqa              | gpt-4o            | 0.00%             | 0.00%          |                   37.76 |                  6.49 |
| finqa              | gpt-4o-mini       | 0.00%             | 0.00%          |                   37.79 |                  7.07 |
| finqa              | o3-mini           | 0.00%             | 0.00%          |                   45.79 |                 13.63 |
| officeqa           | claude-3-5-haiku  | 0.00%             | 0.00%          |                   45.52 |                 14.71 |
| officeqa           | claude-3-7-sonnet | 0.00%             | 0.00%          |                   30    |                  2.86 |
| officeqa           | gemini-2.5-flash  | 0.00%             | 0.00%          |                   45.52 |                 14.7  |
| officeqa           | gemini-2.5-pro    | 0.00%             | 0.00%          |                   30    |                  2.86 |
| officeqa           | gemini-3.6-flash  | 0.00%             | 0.00%          |                   30    |                  2.86 |
| officeqa           | gpt-4o            | 0.00%             | 0.00%          |                   37.76 |                  8.77 |
| officeqa           | gpt-4o-mini       | 0.00%             | 0.00%          |                   30    |                  2.85 |
| officeqa           | o3-mini           | 0.00%             | 0.00%          |                   37.83 |                  8.81 |
| tab_fact           | claude-3-5-haiku  | 0.00%             | 0.00%          |                   30    |                  0    |
| tab_fact           | claude-3-7-sonnet | 0.00%             | 0.00%          |                   30    |                  0    |
| tab_fact           | gemini-2.5-flash  | 0.00%             | 0.00%          |                   30    |                  0    |
| tab_fact           | gemini-2.5-pro    | 0.00%             | 0.00%          |                   30    |                  0    |
| tab_fact           | gemini-3.6-flash  | 0.00%             | 0.00%          |                   30    |                  0    |
| tab_fact           | gpt-4o            | 0.00%             | 0.00%          |                   30    |                  0    |
| tab_fact           | gpt-4o-mini       | 0.00%             | 0.00%          |                   30    |                  0    |
| tab_fact           | o3-mini           | 0.00%             | 0.00%          |                   30    |                  0    |
| tat_qa             | claude-3-5-haiku  | 0.00%             | 28.29%         |                   40.54 |                 21.87 |
| tat_qa             | claude-3-7-sonnet | 0.00%             | 28.29%         |                   40.54 |                 21.87 |
| tat_qa             | gemini-2.5-flash  | 0.00%             | 28.29%         |                   56.22 |                 34.63 |
| tat_qa             | gemini-2.5-pro    | 0.00%             | 29.61%         |                   40.61 |                 22.62 |
| tat_qa             | gemini-3.6-flash  | 0.00%             | 28.29%         |                   40.92 |                 22.01 |
| tat_qa             | gpt-4o            | 0.00%             | 28.29%         |                   41.18 |                 22.1  |
| tat_qa             | gpt-4o-mini       | 0.00%             | 28.29%         |                   46.39 |                 27.32 |
| tat_qa             | o3-mini           | 0.00%             | 28.29%         |                   38.66 |                 21.16 |
| wikitablequestions | claude-3-5-haiku  | 0.00%             | 12.44%         |                   38.98 |                 23.43 |
| wikitablequestions | claude-3-7-sonnet | 0.00%             | 4.44%          |                   33.28 |                  5.37 |
| wikitablequestions | gemini-2.5-flash  | 0.00%             | 4.44%          |                   33.28 |                 11.37 |
| wikitablequestions | gemini-2.5-pro    | 0.00%             | 4.44%          |                   33.28 |                  5.45 |
| wikitablequestions | gemini-3.6-flash  | 0.00%             | 4.44%          |                   33.28 |                  5.29 |
| wikitablequestions | gpt-4o            | 0.00%             | 11.43%         |                   38.07 |                 22.21 |
| wikitablequestions | gpt-4o-mini       | 0.00%             | 4.44%          |                   33.28 |                 11.41 |
| wikitablequestions | o3-mini           | 0.00%             | 4.44%          |                   33.28 |                  6.76 |