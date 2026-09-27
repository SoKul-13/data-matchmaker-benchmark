#!/usr/bin/env python
"""v5 step 8 - REPORT.md from output/ (the v5 notes/04_RESULTS.md from step 6 stays as the detailed results note)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from stats.leaderboard import official_table_md  # noqa: E402


def main():
    ens = json.load(open(OUT / "ensemble.json")); sel = json.load(open(OUT / "selected.json")); val = json.load(open(OUT / "validation.json")) if (OUT / "validation.json").exists() else {}
    des = json.load(open(OUT / "designs_summary.json")); lbsum = json.load(open(OUT / "leaderboards" / "summary.json")); agree = pd.read_csv(OUT / "leaderboards" / "rule_agreement.csv", index_col=0)
    diag = pd.read_csv(OUT / "diagnostics" / "dataset_diagnostics.csv"); base = pd.read_csv(OUT / "baselines_grid.csv"); ia = pd.read_csv(OUT / "index_anchors.csv"); im = pd.read_csv(OUT / "index_models.csv")
    models = sorted(im.model.unique()); datasets = sorted(im.dataset.unique()); M = len(models)
    names = ens["selected"]; wt = lambda w: ", ".join(f"{k} {v:.2f}" for k, v in w.items()) if w else "–"
    L = [f"# v5 report: metric library, anchor-calibrated ensemble, exhaustive grid, designs, leaderboards with significance\n",
         f"Generated {time.strftime('%Y-%m-%d %H:%M')}. Model answers: {len(datasets)} datasets × {M} models ({len(im):,} rows). Anchors: {len(ia):,} synthetic answers over {ia.dataset.nunique()} datasets (every pool, including the new ones without model answers).\n",
         "## 1. Selection and calibration\n",
         f"* Selected metrics: {', '.join(names)} (from the {len(pd.read_csv(OUT / 'metric_table.csv'))}-metric library; selection details in `selected.json`, `clusters.json`, `metric_table.csv`).",
         f"* Exhaustive grid: {ens['n_grid']:,} weightings (step {ens['grid_step']} × {len(ens.get('top_weightings', [])) and 5} hedge penalties); ensemble = mean of the top {ens['top_k']}: {wt(ens['mean_weights'])}, λ = {ens['mean_lambda']:.2f}; J top-1 {ens['J_top1']:.3f}, top-100 {ens['J_top100']:.3f}, grid median {ens['J_median_grid']:.3f}.",
         "* Ensemble terms (mean over the top 100): " + ", ".join(f"{k} {v:.3f}" for k, v in ens["terms_ensemble_mean"].items()) + ".",
         "", "| baseline | ρ | AUC | 1 − JS/ln2 | τ native | wrong-score | J |", "|---|---|---|---|---|---|---|"]
    for _, r in base.iterrows():
        L.append(f"| {r.baseline} | {r.rho:.3f} | {r.auc:.3f} | {1 - r.js / 0.6931:.3f} | {r.tau_native:.2f} | {r.bad:.3f} | {r.J:.3f} |")
    L += ["", "## 2. Sampled designs versus the exhaustive grid (20 seeds × 100 weightings × 5 λ)\n", "| design | best J found (mean ± sd) | regret vs exhaustive (mean / max) | min pairwise L1 | centred L2 discrepancy | share with a zero weight |", "|---|---|---|---|---|---|"]
    for d in ["uniform_lattice", "dirichlet_lattice", "lhs_simplex"]:
        r = des[d]; L.append(f"| {d} | {r['best_J_mean']:.4f} ± {r['best_J_sd']:.4f} | {r['regret_mean']:.4f} / {r['regret_max']:.4f} | {r['min_pairwise_L1']:.2f} | {r['discrepancy']:.3f} | {r['zero_share']:.2f} |")
    L += ["", f"Exhaustive best J = {des['exhaustive_best_J']:.4f} over {des['n_grid']:,} points; with three weights every design gets within a few thousandths of it, which is why v5 keeps the exhaustive grid and the sampled designs are a check only.",
          "", "## 3. Validation (from step 5)\n"]
    if val:
        for k, v in val.items():
            if isinstance(v, dict):
                L.append(f"* {k}: " + ", ".join(f"{kk} {vv:.3f}" if isinstance(vv, (int, float)) else f"{kk} {vv}" for kk, vv in list(v.items())[:8]))
            else:
                L.append(f"* {k}: {v}")
    L += ["", "## 4. Leaderboards (Bradley–Terry rank, Borda in brackets) with significance\n", "| rule | weights | " + " | ".join(models) + " | Friedman p | Kendall's W | significant pairs |", "|---|---|" + "---|" * M + "---|---|---|"]
    for name, r in lbsum.items():
        L.append(f"| {name} | {wt(r['weights'])} | " + " | ".join(f"{r['bt_ranking'][m]} ({r['borda_ranking'][m]})" for m in models) + f" | {r['friedman_p']:.3f} | {r['kendall_W']:.2f} | {', '.join(r['significant_pairs_holm']) or 'none'} |")
    L += ["", "τ between BT rankings of the rules:", "", "| | " + " | ".join(agree.columns) + " |", "|---|" + "---|" * len(agree.columns)] + [f"| {i} | " + " | ".join(f"{x:+.2f}" for x in row) + " |" for i, row in agree.iterrows()]
    L += official_table_md(OUT / "leaderboards" / "ensemble", models, datasets, "Official-split estimates under the ensemble")
    L += ["", "## 5. Dataset diagnostics (under the ensemble)\n", "| dataset | family | mean | spread | self-stability τ | τ to others | exclude |", "|---|---|---|---|---|---|---|"] + \
         [f"| {r.dataset} | {r.family} | {r.mean_score:.3f} | {r.spread_across_models:.3f} | {r.ranking_self_stability_tau:.2f} | {r.tau_to_others_mean:+.2f} | {r.exclude_from_objective} |" for _, r in diag.iterrows()]
    L += ["", "## 6. Reading\n",
          "* v5 is the only version whose objective measures correctness (against anchors of known utility) rather than agreement; its ensemble is the headline scoring rule and the other rules here are the comparison points the paper needs (naive exact match, the dataset's own metric, the five best single weightings).",
          "* Selection honesty is built into v5 differently from v2–v4: the top-100 average spreads selection risk and step 5 re-runs the selection leave-one-dataset-out and under utility perturbation; the nested item bootstrap of v2/v4 does not apply because the objective is not a function of the ranked models.",
          "* Files: matrix_models.npz / matrix_anchors.npz, index_*.csv, metric_table.csv, clusters.json, selected.json, grid_all.csv (every weighting with every term), ensemble.json, baselines_grid.csv, validation.json, probes.csv, lodo.csv, designs.csv, leaderboards/<rule>/ (params with BT SE, Kemeny cost, bootstrap draws, significance), diagnostics/, notes/04_RESULTS.md."]
    open(ROOT / "REPORT.md", "w").write("\n".join(L) + "\n"); print("wrote", ROOT / "REPORT.md")


if __name__ == "__main__":
    main()
