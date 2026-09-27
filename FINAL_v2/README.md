# FINAL_v2: the final v2 (audit of the deployed judge's weights), self-contained

This folder is a copy of `v6_top30_significance/v2_gridsearch` together with everything it needs (`shared/`, `config/`, `data/`), so it runs
on its own. v6 keeps the same v2 next to v3, v4 and v5; the older stand-alone folders are under `other_older_versions/`.

```
FINAL_v2/
  shared/src/      scorer (metrics/), pooling, adapters (34 datasets), inference, search/ (sampling, fast rank agreement, nested selection, audit),
                   stats/ (significance, parameters with SE, leaderboard writer, post-stratification), families.py, views.py
  shared/scripts/  00a_build_item_pool.py (pools), 00b_official_strata.py (official-split census), 00_run_models.py (model answers, temperature 0, rate caps)
  config/          datasets.toml (31-dataset suite; finqa / financebench disabled), models.toml (13 models, temperature 0)
  data/            pool/ (150 items per dataset, 100 flagged for answering, + _official_strata.json), predictions/ (cached model answers), raw -> ../../data_raw
  v2_gridsearch/   scripts 01-06 + run_all.sh, output/, REPORT.md
  notes/           RUN_MODELS.md (the paid step), HUMAN_LABELLING_PROTOCOL.md, CODE_FLOW.md (v6-wide; the v2 section applies here)
```

What v2 does: evaluates **every** weighting of v1's four ingredients (token F1, numeric decay, precision, recall) on the step-0.05 lattice
(1,771 points), scores each by agreement among datasets (J = mean Kendall τ to the Borda-pooled ranking, also under Kemeny / Copeland /
Bradley–Terry pooling), then checks whether the best is real: nested in-bag / out-of-bag selection with the optimism gap and plateau,
leave-one-dataset-out and leave-one-family-out, per-family weights, sensitivity, correctness on 30 k known-quality anchors with the (J, ρ)
Pareto front, leaderboards under exact match / v1 / the five best / anchor-best / Pareto-knee with Bradley–Terry strengths ± SE, Borda,
mean-z, Kemeny, Copeland, RRF, family-balanced ranks, 1,000 saved bootstrap draws, Friedman / Nemenyi / Holm tests, Kendall's W,
majority-class baselines, official-split (post-stratified) estimates, dataset diagnostics, and a report assembled from the outputs.

Run (minutes, from cached answers): `uv sync` once, then `bash v2_gridsearch/scripts/run_all.sh`; add `--fine` to also evaluate the
step-0.02 lattice (23,426 points). The paid model run is `notes/RUN_MODELS.md`; nothing here calls an API otherwise.

Current state (2026-09-27): the model run is complete — 31 datasets × 10 models × 100 items (Gemini 3.1 Pro left out by quota); `REPORT.md` is the full-data result. Findings summary in `../v6_top30_significance/notes/00_STATUS_AND_PLAN.md`.
