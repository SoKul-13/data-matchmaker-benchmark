# v4 — complete code flow (random search over 9 metric weights, rank-agreement objective; was "v2")

## Purpose
Replace v1's hand-set composite with a 9-metric composite whose weights are chosen by a random search so that the datasets rank the models
consistently; pool rankings; report uncertainty; keep KL/JS divergence as a documented extension; extend the dataset suite to 14 adapters.

## Folder tree (only what the rs pipeline uses; v1 files are also present unchanged)
```
v4_random_search_rank_agreement/
  config/datasets.toml       [global] pool_size 150, seed; [[dataset]] name, tier, hint, stratify, pool_size, enabled (officeqa enabled for the published numbers; docfinqa disabled)
  config/models.toml         [global] budget_usd, max_tokens; [[model]] name, provider (openai|google|anthropic|openai_compat), model_id, price_in/out, tier, reasoning/thinking, base_url, api_key_env, enabled
  src/adapters/              14 adapters (officeqa, finqa, tat_qa, tab_fact, wikitablequestions, fetaqa, financebench, hitab, docfinqa, multihiertt, abt_buy/amazon_google/dblp_scholar/walmart_amazon
                             via MagellanEMAdapter, wdc_products, tpcdi_cells) + table_utils (cached fetch, zip member, table/record rendering) + AdapterRegistry
  src/inference/providers.py ModelSpec (key_available, resolved_base_url), GenResult, generate(spec, prompt, system, max_tokens) with per-provider calls (_openai, _gemini, _anthropic, _openai_compat), retries
  src/inference/prompts.py   SYSTEM_PROMPT, TYPE_INSTRUCTIONS per answer type, build_prompt(item) = context + table + question + format line
  src/metrics/, src/pooling/ same library as v2/v3
  scripts/rs/00a_build_item_pool.py   adapters -> stratified sample -> answer type -> data/pool/<dataset>.jsonl (skips existing pools unless --force)
  scripts/rs/00_run_models.py         for every model with a key: build_prompt -> generate -> data/predictions/<model>.jsonl (cached, resumable, spend cap); --dry-run, --models, --datasets, --limit, --sequential
  scripts/rs/01_prepare.py            9 components + hedge for every (model, item) of enabled datasets with predictions -> output/rs/components.npz (M: n×10), index.csv, datasets.md
  scripts/rs/02_random_search.py      100 random step-0.05 weightings over 9 components -> J = mean τ to Borda-pooled ranking -> weights_random_search.csv, best_weights.json, baselines.csv, lodo.csv, fig_random_search
  scripts/rs/03_pool_report.py        best weights -> per-dataset means, z-mean common score, 7 pooling rules, 1,000 item bootstraps -> leaderboard.md/json, fig_leaderboard, paper/tables/*.tex, paper/numbers.tex
  scripts/rs/run_all.sh               01 → 02 → 03 → extension demo → tectonic paper
  extensions/divergence_extension.py  standalone JS/KL/W1 report (not in the pipeline) + DIVERGENCE_EXTENSION.md
  paper/main.tex, refs.bib, tables/, figures/, main.pdf
  DESIGN_SPACE.md, METHOD_AND_DECISIONS.md, PIPELINE_AND_DATASETS.md, PIPELINE_DETAILED.md, WEIGHTS_AND_POOLING_COMPARISON.md, MODELS.md, COMPARISON_with_ladder_version.md
  data/pool/ (14 pools: 7 with 40 real items, 7 with 150), data/predictions/ (4 models cover the 7 original datasets only)
  output/rs/ (all step outputs), output/ (v1 leftovers)
```

## Steps
0a. `00a_build_item_pool.py`: reads config/datasets.toml; for each enabled dataset without a pool file: adapter.load_questions(seed, num_questions) →
    `stratified_sample` (round-robin over strata) → `detect_answer_type` → in_real_subset flags → writes the pool JSONL and data/pool/_summary_new.json.
0.  `00_run_models.py`: reads config/models.toml, keeps models whose keys exist (`key_available`), sorts by tier, loads real-subset items of enabled
    datasets, skips cached (dataset, uid) pairs, calls `generate` concurrently with per-model semaphores, appends rows to data/predictions/<model>.jsonl,
    logs spend to `_run.log`. STATUS: run for the 7 original datasets (400 items × 4 models); NOT run for the 7 new datasets (1,050 items; ≈ USD 22).
1.  `01_prepare.py`: DATASETS = enabled datasets with a pool file; loads predictions; drops datasets with no predictions ("pending"); for each
    (model, item) `component_vector` → M (1,120 × 10); index.csv (model, dataset, uid, answer_type, native_metric, missing); datasets.md table.
2.  `02_random_search.py`: `sample_grid_weights(100, 9, 0.05)` (Dirichlet draws snapped to the grid, distinct); for each w: `score_table` → 4×7
    means; `evaluate` → J (mean τ to Borda), tau_to_kemeny, mean_pairwise_tau, min_dataset_agreement, scale_dispersion (centred), borda_vs_kemeny;
    sort by (J, mean_pairwise_tau); `bootstrap_J` (200) for top 5, median, worst; baselines em_only, f1_only, num_tol_only, original_rcustom,
    uniform; LODO = best w without dataset d, held-out τ of d to the pooled rank of the rest; writes best_weights.json.
3.  `03_pool_report.py`: composite with best w → piv (4×7), common score mean and z-mean, `consensus_ranking` for mean_score, mean_z, mean_rank, borda,
    copeland, rrf, kemeny; `bootstrap_consensus` (1,000); `dataset_agreement`, `pairwise_dataset_tau`, rule agreement, τ vs native and vs EM-only pooled
    ranks; writes leaderboard.md/json, per-dataset tables (LaTeX), numbers.tex, fig_leaderboard.

## Diagram
```
datasets.toml ─00a─► data/pool/*.jsonl ─┐
models.toml   ─00──► data/predictions/*.jsonl (cached) ─┤
                                                         ▼ 01_prepare: component_vector ×(model,item)
                                              output/rs/components.npz + index.csv
                                                         ▼ 02_random_search: 100 w → J, bootstrap, baselines, LODO
                                              best_weights.json, weights_random_search.csv, baselines.csv, lodo.csv
                                                         ▼ 03_pool_report: 7 pooling rules, 1,000 bootstraps, tables
                                              leaderboard.md/json, fig_leaderboard, paper/tables, numbers.tex ─► tectonic paper/main.tex
extensions/divergence_extension.py (reads components.npz + best_weights.json; writes nothing)
```

## Results as run
Best w: num_tol .25, rouge_l .25, tok_rec .15, edit_sim .15, em .05, num_decay .05, tok_prec .05, jaccard .05; J 0.476 [0.16, 0.50] (top five tie);
EM only 0.362, F1 0.459, v1 rubric 0.429, uniform 0.429. Pooled: gpt-5.5, claude-opus-5, claude-sonnet-5, gpt-5.4-mini; CIs [1,2], [1,4], [2,4], [2,4].

## What still needs to be run
* `scripts/rs/00_run_models.py --sequential` for the 7 new datasets (hitab, abt_buy, amazon_google, dblp_scholar, walmart_amazon, wdc_products, tpcdi_cells): ≈ USD 22 on the 4 models; then set officeqa `enabled = false` in datasets.toml and re-run `scripts/rs/run_all.sh`.
* Gemini (billing), Groq/Mistral/OpenRouter/DeepSeek keys, xAI credits to grow the model set (see MODELS.md).
* MultiHiertt: place data/raw/multihiertt/dev.json then `00a_build_item_pool.py --datasets multihiertt`.
