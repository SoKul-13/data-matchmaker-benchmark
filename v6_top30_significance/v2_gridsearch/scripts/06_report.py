#!/usr/bin/env python
"""
v2 step 6 - Assemble REPORT.md from every output of steps 1-5, plus a run manifest.
Nothing is computed here; every number is read from output/*.json|csv so the report always matches the files.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from stats.leaderboard import official_table_md  # noqa: E402
COMP = ["f1", "decay", "precision", "recall"]; WC = [f"w_{c}" for c in COMP]


def wstr(w):
    return ", ".join(f"{c} {w[c]:.2f}" for c in COMP) if isinstance(w, dict) else ", ".join(f"{c} {x:.2f}" for c, x in zip(COMP, w))


def manifest():
    pred = {}
    for f in sorted((DATA / "predictions").glob("*.jsonl")):
        rows = [json.loads(l) for l in open(f, encoding="utf-8")]
        pred[f.stem] = {"rows": len(rows), "cost_usd": round(sum(r.get("cost_usd") or 0 for r in rows), 2), "in_tokens": sum(r.get("in_tokens") or 0 for r in rows),
                        "out_tokens": sum(r.get("out_tokens") or 0 for r in rows), "decoding": sorted({str(r.get("decoding")) for r in rows})}
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=V6).stdout.strip()
    except Exception:
        commit = "n/a"
    m = {"generated": time.strftime("%Y-%m-%d %H:%M"), "git_commit": commit, "coverage": json.load(open(OUT / "coverage.json")), "predictions": pred,
         "seeds": {"nested_bootstrap": 0, "designs": "1000 + seed index", "leaderboard_bootstrap": [1, 2]}, "scripts": sorted(p.name for p in (ROOT / "scripts").glob("*.py"))}
    json.dump(m, open(OUT / "run_manifest.json", "w"), indent=2); return m


def main():
    best = json.load(open(OUT / "best.json")); nested = json.load(open(OUT / "selection" / "nested.json")); sens = json.load(open(OUT / "selection" / "sensitivity.json"))
    perfam = json.load(open(OUT / "selection" / "per_family.json")); corr = json.load(open(OUT / "anchors" / "correctness.json"))
    lodo = pd.read_csv(OUT / "selection" / "lodo.csv"); lofo = pd.read_csv(OUT / "selection" / "lofo.csv") if (OUT / "selection" / "lofo.csv").stat().st_size > 5 else pd.DataFrame()
    lbsum = json.load(open(OUT / "leaderboards" / "summary.json")); agree = pd.read_csv(OUT / "leaderboards" / "rule_agreement.csv", index_col=0)
    diag = pd.read_csv(OUT / "diagnostics" / "dataset_diagnostics.csv"); raw = json.load(open(OUT / "designs_summary.json")); designs = {d: {k: v[d] for k, v in raw.items()} for d in next(iter(raw.values()))}
    man = manifest(); models, datasets = best["models"], best["datasets"]; M, D = len(models), len(datasets)
    v1, b = best["v1_original"], best["best"]
    L = ["# v2 report: an audit of the deployed judge's weights, done exhaustively\n",
         f"Generated {man['generated']}. Data: {D} datasets × {M} models, {sum(c['items_kept'] for c in man['coverage'].values() if isinstance(c, dict) and c.get('items_kept'))} answered items in total "
         f"({', '.join(d + ' ' + str(c['items_kept']) for d, c in man['coverage'].items() if isinstance(c, dict) and c.get('items_kept'))}). Models: {', '.join(models)}. "
         "Every number below is read from `output/`; `scripts/run_all.sh` regenerates everything from the cached answers in a few minutes.\n",
         "## 1. Question and design\n",
         "v1 scores an answer as 0.35·F1 + 0.35·numeric-decay + 0.15·precision + 0.15·recall. Are those weights defensible? We evaluate **every** weighting on the "
         f"step-0.05 simplex lattice ({best['n_candidates']:,} points; v1, the four corners and the uniform mix are lattice points), not a sample. The objective J is the "
         "mean Kendall τ between each dataset's model ranking and the Borda-pooled ranking: it measures **consistency between datasets, not correctness**. Correctness is "
         "checked separately in section 5 with known-quality anchors. Selection honesty (section 3), transfer (section 4), sensitivity (section 6), leaderboards under the "
         "naive, deployed and calibrated rules with significance tests (section 7) and dataset diagnostics (section 8) follow.\n",
         "## 2. Exhaustive grid\n",
         f"* Best weighting: {wstr(b['weights'])} with J = {b['J']:.3f} (τ to native metrics {b['tau_native']:.2f}).",
         f"* v1: J = {v1['J']:.3f}, rank {v1['rank']} of {best['n_candidates']:,}; {v1['n_better']} weightings are better ({100 * v1['share_better']:.0f} %), {v1['n_tied']} tie.",
         f"* Corners and uniform: " + ", ".join(f"{k.replace('only_', 'only ')} {v:.3f}" for k, v in best["corners"].items()) + ".",
         f"* J quantiles over the lattice: median {best['j_quantiles']['0.5']:.3f}, 90 % {best['j_quantiles']['0.9']:.3f}, 99 % {best['j_quantiles']['0.99']:.3f}.",
         f"* Objective robustness: the best under Kemeny pooling is {wstr(best['best_under_other_pooling']['kemeny']['weights'])} (J {best['best_under_other_pooling']['kemeny']['J']:.3f}, v1 rank {best['best_under_other_pooling']['kemeny']['v1_rank']}); "
         f"under Copeland {wstr(best['best_under_other_pooling']['copeland']['weights'])} (v1 rank {best['best_under_other_pooling']['copeland']['v1_rank']}); "
         f"under Bradley–Terry {wstr(best['best_under_other_pooling']['bt']['weights'])} (v1 rank {best['best_under_other_pooling']['bt']['v1_rank']}). v1's J under the four rules: Borda {v1['J']:.3f}, Kemeny {v1['J_kemeny']:.3f}, Copeland {v1['J_copeland']:.3f}, BT {v1['J_bt']:.3f}.",
         "* Top 5 by J: " + "; ".join(f"#{t['rank']} {wstr(t['weights'])} (J {t['J']:.3f})" for t in best["top5"]) + ".",
         "", "Figures: `fig_landscape` (sorted J with v1 and corners), `fig_marginals` (J against each weight), `fig_designs`.\n",
         "### 2b. Sampled designs at a budget of 100 (20 seeds each)\n", "| design | best J found (mean ± sd) | regret vs exhaustive (mean / max) | rank of found best in the grid (median / worst) | min pairwise L1 | centred L2 discrepancy | share with a zero weight |", "|---|---|---|---|---|---|---|"]
    for name, r in designs.items():
        L.append(f"| {name} | {r['best_J_mean']:.3f} ± {r['best_J_sd']:.3f} | {r['regret_mean']:.3f} / {r['regret_max']:.3f} | {r['rank_median']:.0f} / {r['rank_worst']:.0f} | {r['min_pairwise_L1']:.2f} | {r['discrepancy']:.3f} | {r['zero_share']:.2f} |")
    L += ["", "Reading: with four weights the exhaustive grid is cheap, so the sampled designs only matter as a rehearsal for v3/v4; their regret and discrepancy are reported for that comparison.\n",
          "## 3. Is the best weighting real? Nested selection and plateau\n",
          f"* Nested item bootstrap (B = {nested['B']}): the weighting selected on in-bag items has mean in-bag J {nested['in_bag_J_of_selected_mean']:.3f} but out-of-bag J {nested['out_of_bag_J_of_selected_mean']:.3f} "
          f"(**optimism gap {nested['optimism_gap']:.3f}**). v1's out-of-bag J is {nested['out_of_bag_J_v1_mean']:.3f}; the full-data best's is {nested['out_of_bag_J_full_best_mean']:.3f}.",
          f"* Selected vs v1 out of bag: mean difference {nested['selected_vs_v1_out_of_bag']['mean_diff']:+.3f}, 95 % CI [{nested['selected_vs_v1_out_of_bag']['ci95_lo']:+.3f}, {nested['selected_vs_v1_out_of_bag']['ci95_hi']:+.3f}], "
          f"one-sided bootstrap p = {nested['selected_vs_v1_out_of_bag']['p_boot_one_sided']:.3f} (share of resamples where the selected weighting is ahead: {nested['selected_vs_v1_out_of_bag']['share_a_ahead']:.2f}).",
          f"* Full-data best vs v1: in-bag p = {nested['full_best_vs_v1_in_bag']['p_boot_one_sided']:.3f}; out-of-bag p = {nested['full_best_vs_v1_out_of_bag']['p_boot_one_sided']:.3f}.",
          f"* Selection instability: {nested['n_distinct_selected']} distinct weightings were selected across resamples; mean selected weights {wstr(nested['selected_weights_mean'])} (sd {wstr(nested['selected_weights_sd'])}). Most often: "
          + "; ".join(f"{wstr(t['weights'])} ({100 * t['share']:.0f} %)" for t in nested["most_selected"][:3]) + ".",
          f"* **Plateau** (weightings not significantly below the best, paired bootstrap p > .05): {nested['plateau_size']} of {nested['n_candidates']} ({100 * nested['plateau_share']:.0f} %); v1 inside: {nested['v1_in_plateau']} (p vs best {nested['v1_p_vs_best']:.2f}). "
          f"Practical plateau (bootstrap-mean J within 0.02 of the best): {nested['practical_plateau_size_within_0.02']} weightings, v1 inside: {nested['v1_in_practical_plateau']}; weight ranges inside it: "
          + ", ".join(f"{c} [{lo:.2f}, {hi:.2f}]" for c, (lo, hi) in nested["practical_plateau_weight_ranges"].items()) + ".",
          f"* v1 is in the top 5 % of in-bag J in {100 * nested['share_resamples_v1_in_top_5pct']:.0f} % of resamples.",
          "", "Figures: `selection/fig_nested`, `selection/fig_plateau`.\n",
          "## 4. Transfer: leave-one-dataset-out and leave-one-family-out\n", "| held out | J on the rest (LODO weights) | LODO weights | τ held-out → pooled rest: LODO weights | full best | v1 |", "|---|---|---|---|---|---|"]
    for d, g in lodo.groupby("held_out", sort=False):
        r = {row.weights_from: row for _, row in g.iterrows()}
        lw = {c: float(r["lodo_weights"][f"w_{c}"]) for c in COMP}
        L.append(f"| {d} | {r['lodo_weights'].J_rest:.3f} | {wstr(lw)} | {r['lodo_weights'].tau_heldout_mean:+.2f} | {r['full_best'].tau_heldout_mean:+.2f} | {r['v1'].tau_heldout_mean:+.2f} |")
    mean_l = lodo.groupby("weights_from").tau_heldout_mean.mean()
    L += ["", f"Mean held-out τ: LODO weights {mean_l.get('lodo_weights', float('nan')):+.2f}, full best {mean_l.get('full_best', float('nan')):+.2f}, v1 {mean_l.get('v1', float('nan')):+.2f}."]
    if len(lofo):
        L += ["", "| held-out family | J on the rest | LOFO weights | τ held-out: LOFO weights | full best | v1 |", "|---|---|---|---|---|---|"]
        for f, g in lofo.groupby("held_out", sort=False):
            r = {row.weights_from: row for _, row in g.iterrows()}
            lw = {c: float(r["lodo_weights"][f"w_{c}"]) for c in COMP}
            L.append(f"| {f} | {r['lodo_weights'].J_rest:.3f} | {wstr(lw)} | {r['lodo_weights'].tau_heldout_mean:+.2f} | {r['full_best'].tau_heldout_mean:+.2f} | {r['v1'].tau_heldout_mean:+.2f} |")
    L += ["", "Per-family best weightings:"] + [f"* {f}: " + (f"{wstr(v['best_weights'])} (J {v['J_family_best']:.3f}; under the global best {v['J_family_under_global_best']:.3f}; under v1 {v['J_family_under_v1']:.3f}; L1 distance to global best {v['L1_distance_to_global_best']:.2f})" if "best_weights" in v else v["note"]) + f" — datasets: {', '.join(v['datasets'])}" for f, v in perfam.items()]
    c = corr
    L += ["", "## 5. Correctness on known-quality anchors (borrowed from v5; does not change the objective)\n",
          f"{c['n_anchors']:,} synthetic answers of known utility over the {D} datasets ({c['n_correct']:,} correct, {c['n_wrong']:,} wrong; operators: {', '.join(c['operators'])}).",
          "", "| rule | weights | J (agreement) | ρ to utility | mean per-dataset ρ | AUC correct vs wrong | mean score of wrong answers | hedge gap | rank by J | rank by ρ |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name in ["v1", "best_J", "best_rho", "pareto_knee"]:
        r = c[name]; hg = "–" if r["hedge_gap"] is None else f"{r['hedge_gap']:+.2f}"
        L.append(f"| {name} | {wstr(r['weights'])} | {r['J']:.3f} | {r['rho']:.3f} | {r['rho_ds']:.3f} | {r['auc']:.3f} | {r['wrong_mean']:.3f} | {hg} | {r['rank_by_J']} | {r['rank_by_rho']} |")
    e = c["exact_match"]; L.append(f"| exact match | – | – | {e['rho']:.3f} | {e['rho_ds']:.3f} | {e['auc']:.3f} | {e['wrong_mean']:.3f} | {e['hedge_gap']:+.2f} | – | – |")
    L += ["", f"Spearman correlation between J and ρ across all {best['n_candidates']:,} weightings: **{c['spearman_J_vs_rho_across_grid']:+.2f}**. Pareto front size {c['pareto_size']}. " + c["reading"], "", "Figure: `anchors/fig_pareto`.\n",
          "## 6. Sensitivity\n"] + [f"* {k}: {v['n_neighbours']} lattice neighbours within one 0.05 move; J centre {v['J_centre']:.3f}, neighbours min {v['J_min']:.3f} / mean {v['J_mean']:.3f} / max {v['J_max']:.3f} (range {v['flatness_range']:.3f}); {100 * v['share_neighbours_better']:.0f} % of neighbours are better." for k, v in sens.items()]
    L += ["", "## 7. Leaderboards under the naive, deployed and calibrated rules\n", "Bradley–Terry (headline) rankings, with Borda in brackets; full tables, strengths with standard errors, 1,000 bootstrap draws, Friedman/Nemenyi, Holm-corrected pairwise tests and LaTeX under `leaderboards/<rule>/`.\n",
          "| rule | weights | " + " | ".join(models) + " | Friedman p | Kendall's W | significant pairs (Holm) |", "|---|---|" + "---|" * M + "---|---|---|"]
    for name, r in lbsum.items():
        L.append(f"| {name} | {'–' if r['weights'] is None else wstr(r['weights'])} | " + " | ".join(f"{r['bt_ranking'][m]} ({r['borda_ranking'][m]})" for m in models) + f" | {r['friedman_p']:.3f} | {r['kendall_W']:.2f} | {', '.join(r['significant_pairs_holm']) or 'none'} |")
    L += ["", "Agreement between the BT rankings of the rules (Kendall τ):", "", "| | " + " | ".join(agree.columns) + " |", "|---|" + "---|" * len(agree.columns)]
    for i, row in agree.iterrows():
        L.append(f"| {i} | " + " | ".join(f"{x:+.2f}" for x in row) + " |")
    L += official_table_md(OUT / "leaderboards" / "v1_original", models, datasets, "Official-split estimates under the deployed rule (v1 weights)")
    L += ["", "## 8. Dataset diagnostics\n", "| dataset | family | mean score | spread across models | self-stability τ | mean τ to other datasets | floor | ceiling | exclude from objective |", "|---|---|---|---|---|---|---|---|---|"]
    for _, r in diag.iterrows():
        L.append(f"| {r.dataset} | {r.family} | {r.mean_score:.3f} | {r.spread_across_models:.3f} | {r.ranking_self_stability_tau:.2f} | {r.tau_to_others_mean:+.2f} | {r.floor} | {r.ceiling} | {r.exclude_from_objective} |")
    L += ["", "Figure: `diagnostics/fig_dataset_tau` (pairwise τ between dataset rankings under v1).\n",
          "## 9. What this supports, and what it does not\n",
          f"* Supported: over every step-0.05 weighting of v1's four ingredients, v1 sits at rank {v1['rank']} of {best['n_candidates']:,} on the agreement objective, and the honest (out-of-bag) advantage of the best weighting over v1 is "
          f"{nested['selected_vs_v1_out_of_bag']['mean_diff']:+.3f} with a confidence interval that {'excludes' if nested['selected_vs_v1_out_of_bag']['ci95_lo'] > 0 else 'includes'} zero. The plateau of statistically equivalent weightings covers {100 * nested['plateau_share']:.0f} % of the lattice.",
          f"* Correctness (anchors): v1 ρ {c['v1']['rho']:.3f} vs best-J ρ {c['best_J']['rho']:.3f} vs exact match ρ {c['exact_match']['rho']:.3f}; J and ρ correlate {c['spearman_J_vs_rho_across_grid']:+.2f} across the lattice, so agreement and correctness {'pull the same way' if c['spearman_J_vs_rho_across_grid'] > 0.3 else 'do not pull the same way, and the Pareto knee is the defensible compromise'}.",
          f"* Not supported: any rank claim below first place with {M} models (attainable τ values: {json.load(open(OUT / 'leaderboards' / 'v1_original' / 'significance.json'))['friedman']['tau_granularity']}); any claim about accuracy from J alone; transfer to unseen task families until the 30-dataset run exists.",
          "* Next: the same pipeline on the 30-dataset, 12-model run; human labels on 300 answers to replace the synthetic anchors in section 5.",
          "", "## 10. Files\n", "`grid_exhaustive.csv` (all weightings, every term, per-dataset τ, pooled ranks); `best.json`; `designs.csv` / `designs_summary.json`; `selection/` (nested.json, nested_draws.npz, plateau.csv, lodo.csv, lofo.csv, per_family.json, sensitivity.json); "
          "`anchors/` (anchor_components.csv, correctness.csv, correctness.json); `leaderboards/<rule>/` (leaderboard.md/csv, params.json with BT strengths + SE, Kemeny cost, Copeland, Borda, pairwise wins; bootstrap.npz; significance.json; pairwise_item_tests.csv; per_dataset_mean/se.csv; table.tex); "
          "`leaderboards/rule_agreement.csv`, `summary.json`; `diagnostics/`; `run_manifest.json`; `coverage.json`."]
    open(ROOT / "REPORT.md", "w").write("\n".join(L) + "\n"); print("wrote", ROOT / "REPORT.md")


if __name__ == "__main__":
    main()
