# v3 pipeline, stage by stage

## 0. Items and predictions (inputs)
* `data/pool/<dataset>.jsonl`: one row per item with question, context/table, gold, aliases, list gold, answer type, native metric.
  Built by `scripts/00a_build_item_pool.py` from `config/datasets.toml` (14 datasets; OfficeQA and DocFinQA disabled).
* `data/predictions/<model>.jsonl`: raw model outputs, cached, from `scripts/00_run_models.py` (only models with keys run).

## 1. `01_compute_matrix.py` — the 100-metric matrices
* Models: for every (model, item) where predictions cover ≥ 90 % of a dataset's real subset, `compute_all` → 100 numbers.
  Also stores the item's native metric value (typed: num_tol_1 / em_norm / rouge_l).
* Anchors: for every item of every enabled dataset (predictions not needed), `anchors.ladder.generate` produces one answer
  per applicable operator (numeric 15, text 11, boolean 7, free-form 10 operators) with a known utility; each is scored with
  the 100 metrics. ~12.8k anchor answers.

## 2. `02_select_metrics.py` — which metrics carry information
1. Drop constant metrics; cluster the rest by |Spearman| ≥ 0.95 over anchors; keep one representative per cluster (preferring
   the familiar metric: native_style_metric, em_norm, num_tol_1, tok_f1, rouge_l, …).
2. Per metric: mean-per-dataset Spearman with utility, AUC(correct vs wrong), score gap. Written to `output/metric_table.csv`.
3. Candidates = representatives with ρ > 0.05, AUC > 0.55, not in the indicator families (structure, commitment, length; those
   are 1 for most wrong answers and would act as constant offsets — the hedge indicator is used as a multiplicative gate instead).
4. Forward selection: add the candidate that most raises the leave-one-dataset-out Spearman of a non-negative least-squares
   combination; stop when the gain < 0.002 or k = 10. Output `output/selected.json`.
* `--labels file.csv` replaces the anchors with human labels on real answers (uid, dataset, model, label).

## 3. `03_grid_weights.py` — weights and the 100-best ensemble
* Grid: every weight vector on the simplex with step 0.02 (k ≤ 3), 0.05 (k ≤ 6) or 0.1, × hedge penalty λ ∈ {0, .25, .5, .75, 1}.
* Score of an answer under (w, λ): (Σ w_k m_k) · (1 − λ · hedged).
* Objective per candidate: J = .30 ρ_anchor + .15 AUC + .20 (1 − JS_×/ln 2) + .15 τ_native + .20 (1 − mean score of wrong anchors),
  where JS_× is the Jensen–Shannon divergence between datasets' score histograms at the same operator and τ_native the Kendall
  agreement between composite and native model rankings per dataset.
* Keep the 100 best; ensemble = their mean; `output/ensemble.json`, all candidates in `output/grid_all.csv`, baselines in
  `output/baselines_grid.csv`.

## 4. `04_leaderboard.py`
* Score real answers with the ensemble (mean over the 100 weightings; min/max kept as spread).
* Per-dataset means → z-normalise → equal dataset weights → common score; Borda headline, Kemeny/Copeland/RRF/mean-score checks;
  1,000 item bootstraps; rank range across the 100 weightings; native-metric pooled rank beside. `output/leaderboard.md/.json`.

## 5. `05_validate.py`
* LODO: re-run selection + grid without dataset d; anchor Spearman on d under LODO vs full weights; selection stability.
* Severity perturbation: utilities ± 0.15 (identity fixed at 1, wrong at 0), 5 draws; L1 shift of ensemble weights, selection changes.
* Probes: mean ensemble / native / EM / F1 score per operator vs utility. `output/validation.json`, `probes.csv`, `lodo.csv`.

## 6. `06_report.py`
Figures (`paper/figures`), LaTeX tables (`paper/tables`), `paper/numbers.tex`, `notes/04_RESULTS.md`; then `tectonic paper/main.tex`.

## Design decisions embedded above
* Anchors, not models, are the calibration target → no circularity with the leaderboard.
* Indicator metrics are gates, not addends → no constant-offset degeneracy.
* Percent equivalence only with a % sign or a fraction → a 100× error is never free.
* "100 best weights" = an ensemble, not one winner → weighting uncertainty is reported, not hidden.
* Native metrics are kept as baseline and fidelity term, not as the scoring rule.
