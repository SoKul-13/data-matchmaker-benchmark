#!/usr/bin/env python
"""v4 step 6 - REPORT.md assembled from output/ (nothing computed here)."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from stats.leaderboard import official_table_md  # noqa: E402


def wstr(w):
    return ", ".join(f"{k} {v:.2f}" for k, v in w.items() if v > 0)


def main():
    best = json.load(open(OUT / "best.json")); nested = json.load(open(OUT / "selection" / "nested.json")); sens = json.load(open(OUT / "selection" / "sensitivity.json"))
    perfam = json.load(open(OUT / "selection" / "per_family.json")); corr = json.load(open(OUT / "anchors" / "correctness.json")); lodo = pd.read_csv(OUT / "selection" / "lodo.csv")
    lofo = pd.read_csv(OUT / "selection" / "lofo.csv") if (OUT / "selection" / "lofo.csv").stat().st_size > 5 else pd.DataFrame()
    lbsum = json.load(open(OUT / "leaderboards" / "summary.json")); agree = pd.read_csv(OUT / "leaderboards" / "rule_agreement.csv", index_col=0); diag = pd.read_csv(OUT / "diagnostics" / "dataset_diagnostics.csv")
    cov = json.load(open(OUT / "coverage.json")); models, datasets, COMP = best["models"], best["datasets"], best["components"]; M, D = len(models), len(datasets)
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=V6).stdout.strip()
    except Exception:
        commit = "n/a"
    json.dump({"generated": time.strftime("%Y-%m-%d %H:%M"), "git_commit": commit, "coverage": cov, "candidates": best["n_candidates"], "n_per_design": best["n_per_design"]}, open(OUT / "run_manifest.json", "w"), indent=2)
    b, v1, em = best["best"], best["v1_rubric"], best["em_only"]; sv = nested["selected_vs_ref_out_of_bag"]
    L = [f"# v4 report: nine-component composite, three sampled designs, honest selection\n",
         f"Generated {time.strftime('%Y-%m-%d %H:%M')}. {D} datasets × {M} models ({', '.join(d + ' ' + str(c['items_kept']) for d, c in cov.items() if isinstance(c, dict) and c.get('items_kept'))}). "
         f"Candidates: {best['n_per_design']} per design × 3 designs (Dirichlet-snapped, Latin hypercube, uniform lattice) + 5 baselines = {best['n_candidates']} on a lattice of {best['lattice_points']:,} points. Components: {', '.join(COMP)}.\n",
         "## 1. Search and designs\n",
         f"* Best: {wstr(b['weights'])} (design {b['design']}), J = {b['J']:.3f}, τ_native {b['tau_native']:.2f}; under Kemeny {b['J_kemeny']:.3f}, Copeland {b['J_copeland']:.3f}, BT {b['J_bt']:.3f}.",
         "* Best per design: " + "; ".join(f"{k} {v['J']:.3f} ({wstr(v['weights'])})" for k, v in best["best_per_design"].items()) + ".",
         "* Baselines: " + "; ".join(f"{n} J {v['J']:.3f} (rank {v['rank']})" for n, v in best["baselines"].items()) + f". The v1 rubric is beaten by {v1['n_better']} candidates and tied by {v1['n_tied']}.",
         "* Top 5: " + "; ".join(f"#{t['rank']} {wstr(t['weights'])} ({t['design']}, J {t['J']:.3f})" for t in best["top5"]) + ".",
         "", "| design (20 seeds) | best J (mean ± sd) | best J (max) | mean J of design | regret vs best over all (mean / max) | min pairwise L1 | mean nearest L1 | centred L2 discrepancy | share with a zero weight |", "|---|---|---|---|---|---|---|---|---|"]
    for k, r in best["designs_over_seeds"].items():
        L.append(f"| {k} | {r['best_J_mean']:.3f} ± {r['best_J_sd']:.3f} | {r['best_J_max']:.3f} | {r['mean_J']:.3f} | {r['regret_mean']:.3f} / {r['regret_max']:.3f} | {r['min_pairwise_L1']:.2f} | {r['mean_nearest_L1']:.2f} | {r['discrepancy']:.3f} | {r['zero_share']:.2f} |")
    L += ["", "## 2. Honest selection\n",
          f"* Nested bootstrap (B = {nested['B']}): in-bag J of the selected candidate {nested['in_bag_J_of_selected_mean']:.3f}, out-of-bag {nested['out_of_bag_J_of_selected_mean']:.3f} (optimism gap {nested['optimism_gap']:.3f}); v1 rubric out-of-bag {nested['out_of_bag_J_ref_mean']:.3f}.",
          f"* Selected vs v1 rubric out of bag: {sv['mean_diff']:+.3f} [{sv['ci95_lo']:+.3f}, {sv['ci95_hi']:+.3f}], one-sided p = {sv['p_boot_one_sided']:.3f}.",
          f"* Plateau (paired p > .05): {nested['plateau_size']} of {nested['n_candidates']}; practical plateau (within {nested['practical_margin']}): {nested['practical_plateau_size']}, v1 rubric inside: {nested['ref_in_practical_plateau']}. "
          f"{nested['n_distinct_selected']} distinct candidates selected; mean selected weights {wstr(nested['selected_weights_mean'])}.",
          "", "## 3. Transfer\n", "| held out | J on rest | held-out weights | τ held-out: held-out weights | full best | v1 rubric |", "|---|---|---|---|---|---|"]
    for d, g in lodo.groupby("held_out", sort=False):
        r = {row.weights_from: row for _, row in g.iterrows()}; hw = {c: float(r["heldout_weights"][f"w_{c}"]) for c in COMP}
        L.append(f"| {d} | {r['heldout_weights'].J_rest:.3f} | {wstr(hw)} | {r['heldout_weights'].tau_heldout_mean:+.2f} | {r['full_best'].tau_heldout_mean:+.2f} | {r['v1_rubric'].tau_heldout_mean:+.2f} |")
    ml = lodo.groupby("weights_from").tau_heldout_mean.mean(); L.append(f"\nMean held-out τ: held-out weights {ml.get('heldout_weights', float('nan')):+.2f}, full best {ml.get('full_best', float('nan')):+.2f}, v1 rubric {ml.get('v1_rubric', float('nan')):+.2f}.")
    if len(lofo):
        L += ["", "| held-out family | J on rest | held-out weights | τ: held-out weights | full best | v1 rubric |", "|---|---|---|---|---|---|"]
        for f, g in lofo.groupby("held_out", sort=False):
            r = {row.weights_from: row for _, row in g.iterrows()}; hw = {c: float(r["heldout_weights"][f"w_{c}"]) for c in COMP}
            L.append(f"| {f} | {r['heldout_weights'].J_rest:.3f} | {wstr(hw)} | {r['heldout_weights'].tau_heldout_mean:+.2f} | {r['full_best'].tau_heldout_mean:+.2f} | {r['v1_rubric'].tau_heldout_mean:+.2f} |")
    L += ["", "Per-family best: " + "; ".join(f"{f}: {wstr(v['best_weights'])} (J {v['J_family_best']:.3f}; global best {v['J_family_under_global_best']:.3f})" if "best_weights" in v else f"{f}: {v['note']}" for f, v in perfam.items()) + ".",
          "", "## 4. Correctness on anchors\n", f"{corr['n_anchors']:,} anchors ({corr['n_correct']:,} correct, {corr['n_wrong']:,} wrong).", "",
          "| rule | weights | J | ρ | per-dataset ρ | AUC | wrong mean | hedge gap | rank by J | rank by ρ |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name in ["reference", "best_J", "best_rho", "pareto_knee"]:
        r = corr[name]; hg = "–" if r["hedge_gap"] is None else f"{r['hedge_gap']:+.2f}"
        L.append(f"| {'v1_rubric' if name == 'reference' else name} | {wstr(r['weights'])} | {r['J']:.3f} | {r['rho']:.3f} | {r['rho_ds']:.3f} | {r['auc']:.3f} | {r['wrong_mean']:.3f} | {hg} | {r['rank_by_J']} | {r['rank_by_rho']} |")
    for nm, t in corr["extra_rules"].items():
        L.append(f"| {nm} | – | – | {t['rho']:.3f} | {t['rho_ds']:.3f} | {t['auc']:.3f} | {t['wrong_mean']:.3f} | {t['hedge_gap']:+.2f} | – | – |")
    L += ["", f"Spearman(J, ρ) across candidates: **{corr['spearman_J_vs_rho_across_candidates']:+.2f}**; Pareto front size {corr['pareto_size']}.",
          "", "## 5. Sensitivity\n"] + [f"* {k}: {v['n_neighbours']} one-step neighbours; J centre {v['J_centre']:.3f}, min {v['J_min']:.3f} / mean {v['J_mean']:.3f} / max {v['J_max']:.3f}; {100 * v['share_neighbours_better']:.0f} % better." for k, v in sens.items()]
    L += ["", "## 6. Leaderboards (Bradley–Terry rank, Borda in brackets)\n", "| rule | weights | " + " | ".join(models) + " | Friedman p | Kendall's W | significant pairs |", "|---|---|" + "---|" * M + "---|---|---|"]
    for name, r in lbsum.items():
        L.append(f"| {name} | {wstr(r['weights'])} | " + " | ".join(f"{r['bt_ranking'][m]} ({r['borda_ranking'][m]})" for m in models) + f" | {r['friedman_p']:.3f} | {r['kendall_W']:.2f} | {', '.join(r['significant_pairs_holm']) or 'none'} |")
    L += ["", "τ between BT rankings of the rules:", "", "| | " + " | ".join(agree.columns) + " |", "|---|" + "---|" * len(agree.columns)] + [f"| {i} | " + " | ".join(f"{x:+.2f}" for x in row) + " |" for i, row in agree.iterrows()]
    L += official_table_md(OUT / "leaderboards" / "v1_rubric", models, datasets, "Official-split estimates under the v1 rubric")
    L += ["", "## 7. Dataset diagnostics\n", "| dataset | family | mean | spread | self-stability τ | τ to others | exclude |", "|---|---|---|---|---|---|---|"] + \
         [f"| {r.dataset} | {r.family} | {r.mean_score:.3f} | {r.spread_across_models:.3f} | {r.ranking_self_stability_tau:.2f} | {r.tau_to_others_mean:+.2f} | {r.exclude_from_objective} |" for _, r in diag.iterrows()]
    L += ["", "## 8. Reading\n",
          f"* The three designs reach the same best J within noise (see the design table); the Latin hypercube design has the lowest discrepancy and the fewest zero weights, so it is the one to keep when a design is sampled.",
          f"* The honest advantage of the selected weighting over the v1 rubric is {sv['mean_diff']:+.3f} with a CI that {'excludes' if sv['ci95_lo'] > 0 else 'includes'} zero; the optimism gap {nested['optimism_gap']:.3f} is the size of the winner's curse on this data.",
          f"* J and ρ correlate {corr['spearman_J_vs_rho_across_candidates']:+.2f} across candidates: the agreement objective {'is' if corr['spearman_J_vs_rho_across_candidates'] > 0.3 else 'is not'} a proxy for correctness here; the anchor-optimal and Pareto-knee weightings are reported next to the J-optimal one.",
          "* Files: grid_candidates.csv, best.json, designs.csv, selection/, anchors/, leaderboards/<rule>/ (params with BT SE, Kemeny cost, bootstrap draws, significance), diagnostics/, run_manifest.json."]
    open(ROOT / "REPORT.md", "w").write("\n".join(L) + "\n"); print("wrote", ROOT / "REPORT.md")


if __name__ == "__main__":
    main()
