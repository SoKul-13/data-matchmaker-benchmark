# Data Matchmaker Benchmark

Green-agent evaluator for the AgentBeats A2A platform, in two versions:

| Folder | What it is |
|---|---|
| [`v1/`](v1/) | The original benchmark: TPC-DI data-integration judge, dataset adapters, hand-set rubric. |
| [`v2/`](v2/) | Calibrated cross-dataset scoring: one common score over the 7 original datasets, composite-metric weights chosen by a random search over 100 grid combinations, rankings pooled with Borda / Kemeny / RRF and bootstrap intervals, KL/JS divergence as a documented extension, and a short paper (`v2/paper/main.pdf`). See `v2/README.md`, `v2/MODELS.md` and `v2/COMPARISON_with_ladder_version.md`. |

Each folder is a self-contained `uv` project (`cd v1 && uv sync`, `cd v2 && uv sync`). API keys go in a
`.env` inside the folder you run (see each `sample.env`); `.env` files are git-ignored.
