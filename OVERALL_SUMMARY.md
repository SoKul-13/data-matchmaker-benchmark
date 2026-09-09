# Overall summary — every version, from the ground up, with what exists and what still has to run

Per-version, line-by-line code flows (every script, function, input file, output file):
`v1/notes/CODE_FLOW.md`, `v2_gridsearch_v1_rubric/notes/CODE_FLOW.md`, `v3_literature_aggregation/notes/CODE_FLOW.md`,
`v4_random_search_rank_agreement/notes/CODE_FLOW.md`, `v5_metric_library_anchor_ensemble/notes/08_CODE_FLOW.md`.
Formula-level explanation of all versions: `GUIDE_UNDER_THE_HOOD.md`. Plain-language glossary: `v5_…/notes/00_PLAIN_ENGLISH_GUIDE.md`.

---

## 1. What the whole thing is, from zero

1. **The job.** A "green agent" is a judge program on the AgentBeats platform. Another program (a "purple agent", usually an LLM) is given
   data-matching tasks: decide whether two records are the same thing, read numbers from financial tables and documents, join tables and
   aggregate. The judge must return a score, and across several LLMs it must return a ranking.
2. **The data.** Public test sets ("datasets"), each a list of items = question + context (table, document, or two records) + the correct answer
   ("gold"). We use 7 with model answers cached (FinQA, TAT-QA, TabFact, WikiTableQuestions, FeTaQA, FinanceBench, OfficeQA) and 7 more prepared
   but not yet answered by models (HiTab, Abt-Buy, Amazon-Google, DBLP-Scholar, Walmart-Amazon, WDC Products, TPC-DI cells). Items live in
   `data/pool/<dataset>.jsonl`; model answers in `data/predictions/<model>.jsonl`. The 4 answered models: gpt-5.5, gpt-5.4-mini, claude-opus-5,
   claude-sonnet-5 (40 items per dataset each, one answer per item, one fixed prompt).
3. **The core problem.** Each dataset grades its own way (accuracy, exact match, 1 % numeric tolerance, ROUGE-L), so scores cannot be added
   across datasets, and a rule that combines several ways of grading needs weights. Every version is a different answer to "how do we grade
   one answer, and how do we turn per-dataset results into one comparable score/ranking with error bars".
4. **The shared machinery** (in every version's `src/`): `metrics/normalize.py` (pull the final answer out of the model text, clean it,
   parse numbers with signs/percent/scale), `metrics/answer_types.py` (numeric / boolean / text / free-form), `metrics/components.py`
   (9 grading metrics + hedge flag), `pooling/rank_aggregation.py` (Borda, Kemeny, Copeland, RRF, mean-z, Kendall τ, item bootstrap).
5. **How a number becomes a rank.** score per answer → mean per (model, dataset) → either ranks per dataset pooled by Borda/Kemeny, or z-scores
   averaged → one number per model → bootstrap over items for an interval.

---

## 2. Version by version

### v1 — original judge (`v1/`)
* **Grading rule:** TPC-DI 100-point rubric for the join task; for QA, `0.35·F1 + 0.35·e^(−2.5·MRE) + 0.15·P + 0.15·R` with hand-set weights.
* **Inputs:** `jan15_tasks/*.csv`, `data/officeqa.csv`, adapters for 4 datasets. **Outputs:** `output/results.json`, `eval_results.csv` (real, mock purple),
  four leaderboard files (SIMULATED answers; not evidence).
* **Status:** runs; the QA leaderboard must not be cited. **Nothing to run** unless you want the TPC-DI demo (`scripts/run_local_test.py`).

### v2 — grid search over v1's four weights (`v2_gridsearch_v1_rubric/`)
* **Grading rule:** same four ingredients, weights on the simplex. **Search:** 105 weightings (v1 + 4 corners + 100 random step-0.05 grid points).
* **Objective:** J = mean over datasets of Kendall τ between the dataset's model ranking and the Borda-pooled ranking; plus τ to native metrics.
* **Outputs:** `output/components_v1.csv`, `grid.csv`, `best.json`, `leaderboard.md`, `fig_grid.png`.
* **Result:** v1's weights rank 35/105 (J 0.429); best 0.507 (F1 .85, P .05, R .10, decay 0); gain inside the bootstrap interval.
* **Status:** complete. **To run:** nothing; re-run `scripts/run_all.sh` if predictions grow.

### v3 — aggregation views from the literature (`v3_literature_aggregation/`)
* **Grading rule:** each dataset's own metric. **Views (8):** raw mean, baseline-normalised mean (Open LLM Leaderboard v2), z-mean, mean win rate (HELM),
  Borda and Kemeny score (Colombo et al.), Bradley–Terry strength (Chatbot Arena), IRT ability (tinyBenchmarks).
* **Search:** 109 mixes of the 8 standardised views. **Objective:** 0.5·bootstrap stability + 0.25·transitivity (τ to Copeland) + 0.25·τ to the Kemeny
  consensus of the views (Perlitz DIoR, Elo Uncovered, BenchBench).
* **Outputs:** `output/native_item_scores.csv`, `random_baseline.json`, `views.csv`, `grid_views.csv`, `best.json`, `leaderboard.md`, `fig_views.png`;
  `notes/01_LITERATURE_REVIEW.md` (10 papers: summary, findings, math, sources), `notes/02_MATH.md`.
* **Result:** pure Bradley–Terry most reliable (J 0.867), then Kemeny 0.818, IRT 0.815; raw mean 0.547. Views agree on the winner (gpt-5.5) and
  disagree on the middle (raw mean puts claude-sonnet-5 last, rank-based views second).
* **Status:** complete. **To run:** nothing; more models/items make BT and IRT better determined.

### v4 — random search, rank-agreement objective (`v4_random_search_rank_agreement/`, was v2)
* **Grading rule:** 9-metric composite (EM, numeric tolerance, numeric decay, P, R, F1, edit similarity, ROUGE-L, Jaccard) with aliases / units / list golds.
* **Search:** 100 random step-0.05 weightings; J as in v2; bootstrap; LODO; baselines (EM, F1, NumTol, uniform, v1 rubric). **Pooling:** 7 rules; 1,000 bootstraps.
* **Extras:** 14 dataset adapters and pools; model runner with spend cap; KL/JS/W1 divergence as a standalone extension; 5-page paper; design notes.
* **Outputs:** `output/rs/*` (components.npz, index.csv, weights_random_search.csv, best_weights.json, baselines.csv, lodo.csv, pooled_ranking.json,
  leaderboard.md, figures), `paper/main.pdf`.
* **Result:** best J 0.476 [0.16, 0.50] (top five tie) vs EM 0.362; pooled gpt-5.5, claude-opus-5, claude-sonnet-5, gpt-5.4-mini.
* **Status:** complete for 7 datasets. **To run:** `scripts/rs/00_run_models.py --sequential` for the 7 new datasets (≈ USD 22), set officeqa
  `enabled = false`, `scripts/rs/run_all.sh`.

### v5 — 100-metric library calibrated on known-quality anchors (`v5_metric_library_anchor_ensemble/`, was v3)
* **Grading rule:** 100 metrics (`src/metrics/library.py`); after selection, 3 (token F1, numeric decay, bigram recall) with a multiplicative hedge penalty.
* **Calibration target:** 12,813 synthetic answers of known utility from 20 typed operators on 14 datasets (`src/anchors/ladder.py`); human labels accepted instead.
* **Selection:** drop constants → cluster |Spearman| ≥ 0.95 (100 → 42) → agreement floor and no indicator families (→ 24) → forward selection with
  leave-one-dataset-out stop (→ 3). **Search:** 6,630 (weights × λ) candidates; objective .30 ρ + .15 AUC + .20 (1 − JS/ln2) + .15 τ_native + .20 (1 − wrong-score);
  100 best averaged. **Leaderboard:** z-mean, Borda/Kemeny, 1,000 bootstraps, rank range across the 100 weightings. **Validation:** LODO, ±0.15 severity
  perturbation, per-operator probes.
* **Outputs:** `output/*` (18 files, listed in notes/08_CODE_FLOW.md), `paper/main.pdf`, `notes/00–08`.
* **Result:** ensemble decay .81 / F1 .16 / λ .63; anchor ρ .906, AUC .997, wrong answers .02; LODO .895 vs .900; probe MAE .095 (EM .196);
  leaderboard top gpt-5.5 / claude-sonnet-5 (tie), CIs overlap below.
* **Status:** complete for 7 datasets. **To run:** same model run as v4 (≈ USD 22), then `scripts/run_all.sh` (~6 min); optional `--semantic`, `--labels`.

---

## 3. What still needs to be run, in one list
1. Model predictions for the 7 new datasets in v4 or v5 (`scripts/00_run_models.py --sequential`, ≈ USD 22 on the 4 cached models); copy the resulting
   `data/predictions/*.jsonl` into v2 and v3 as well; re-run each folder's `run_all.sh`.
2. More models: Gemini billing; free keys for Groq (Llama-3.3-70B), Mistral, OpenRouter (Qwen); DeepSeek (cheap); xAI credits. Catalogue and
   auto-skip logic in `config/models.toml`; instructions in `v5_…/notes/06_USER_TODO.md` and `07_MODEL_CATALOGUE.md`.
3. Optional data: MultiHiertt `dev.json` (Google Drive) → `data/raw/multihiertt/`; OfficeQA corpus access for retrieval instead of closed-book.
4. Human quality labels (300–500 answers) for v5's `02_select_metrics.py --labels`.
5. Paper regeneration is automatic (`06_report.py` / `03_pool_report.py` + tectonic).

---

## 4. Pros and cons against industry practice

Industry reference points: HELM (mean win rate over scenarios, per-scenario native metrics), Open LLM Leaderboard (fixed task set, baseline-normalised
average, lm-evaluation-harness for reproducibility), Chatbot Arena (Bradley–Terry on human pairwise votes with bootstrap CIs), and MT metric
meta-evaluation (metrics validated against human judgements, WMT/MQM).

| Aspect | Industry standard | This project | Pro | Con |
|---|---|---|---|---|
| Per-answer grading | native metric per task; lm-eval fixed scoring rules; LLM judges for open answers | v3/v4/v5 use native metrics as baseline; v4/v5 add a composite with alias/unit/list handling; v5 selects from 100 metrics | gold handling is stricter than most harnesses (aliases, unit equivalence, list sets); v5's selection is data-driven | lexical only; no LLM-judge or embedding component in the shipped results; v1's composite was arbitrary |
| Choosing weights | not done: leaderboards avoid composites, or set them by convention | v2/v4 search weights for rank agreement; v5 searches against known-quality anchors | v5's target is not the ranked models (no circularity); ensemble of 100 best gives a weighting error bar | v2/v4 objective is circular; v5's utility scale is hand-set (perturbed, not human-validated) |
| Cross-dataset aggregation | HELM mean win rate; OLL baseline-normalised mean; Colombo Kemeny; Arena BT | v3 implements all of these and picks by reliability; v4/v5 use z-mean + Borda with Kemeny/Copeland/RRF checks | matches the literature rule-for-rule; reliability-based choice is what Perlitz/BenchBench recommend | 4 models make BT/IRT/Kemeny coarse; no informativeness weighting in the headline |
| Uncertainty | Arena bootstrap CIs; lm-eval standard errors; Perlitz DIoR | item bootstrap everywhere; LODO; v5 severity perturbation; v3 stability objective | more uncertainty reporting than most leaderboards | no Friedman–Nemenyi significance test; no prompt/seed variation |
| Reproducibility | lm-eval: fixed prompts, versioned tasks, published configs | one prompt, seeded sampling, cached raw answers, one-command re-runs, published item ids in pools | fully reproducible from cache in minutes | prompts are ours, not the datasets' official ones; 40 items per dataset on the answered set |
| Validation of the metric itself | MT: correlation with human judgements; Arena: agreement with expert raters | v5: synthetic anchors + probes + LODO; no human labels yet | anchors are cheap, controllable and dataset-independent | reviewers will ask for human labels; the native typed metric ties v5's ensemble on the mixed objective |
| Scale | HELM/OLL: dozens of models, thousands of items | 4 models, 40 items per answered dataset; 7 datasets pending | pipeline scales without code changes | every rank claim below the top is currently unsupported |
| Data-matching coverage | no established LLM benchmark for entity matching + table integration in one suite | Magellan/WDC entity matching + TPC-DI cells + financial table QA in one adapter registry | genuinely new coverage for the benchmark's stated purpose | those datasets have no model results yet |

**Bottom line.** The machinery is at or above industry practice on gold handling, aggregation choices and uncertainty reporting; it is below
on evidence (models, items, human validation). The next USD 22 run and two free API keys move it most; human labels are the remaining gap
to a conference-grade claim.
