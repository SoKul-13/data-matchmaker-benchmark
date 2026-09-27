#!/usr/bin/env python
"""v3 step 4 - REPORT.md from output/."""
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
from views import VIEWS  # noqa: E402


def main():
    best = json.load(open(OUT / "best.json")); sh = json.load(open(OUT / "selection" / "split_half.json")); params = json.load(open(OUT / "params" / "view_params_full.json"))
    pb = json.load(open(OUT / "params" / "view_params_bootstrap.json")); lbsum = json.load(open(OUT / "leaderboards" / "summary.json")); cov = json.load(open(OUT / "coverage.json"))
    combos = pd.read_csv(OUT / "combos" / "combos.csv"); diag = pd.read_csv(OUT / "diagnostics" / "dataset_diagnostics.csv"); mixes = (OUT / "leaderboards" / "mixes_top5.md").read_text().split("\n", 2)[2]
    models, datasets = best["models"], best["datasets"]; M, D = len(models), len(datasets); b = best["best"]
    L = [f"# v3 report: aggregation views, all their combinations, parameters with standard errors\n",
         f"Generated {time.strftime('%Y-%m-%d %H:%M')}. {D} datasets × {M} models ({', '.join(d + ' ' + str(c['items_kept']) for d, c in cov.items() if isinstance(c, dict) and c.get('items_kept'))}). "
         f"Candidates: {best['n_subsets']} equal-weight subsets of the {len(VIEWS)} views + {best['n_lattice']} uniform-lattice + {best['n_lhs']} Latin-hypercube mixes = {best['n_candidates']}; {best['B']} item-bootstrap resamples for stability.\n",
         "## 1. Single views and the best mixes\n", "| view | J alone | " + " | ".join(models) + " |", "|---|---|" + "---|" * M]
    for v, r in best["single_views"].items():
        L.append(f"| {v} | {r['J']:.3f} | " + " | ".join(str(r["ranks"][m]) for m in models) + " |")
    L += ["", f"Uniform mix J = {best['uniform_J']:.3f}. Best candidate: `{b['label']}` with J = {b['J']:.3f} (stability {b['stability']:.3f}, transitivity {b['transitivity']:.2f}, reference {b['reference']:.2f}); weights " + ", ".join(f"{v} {w:.2f}" for v, w in b["weights"].items() if w > 0) + ".",
          "Best subset per size: " + "; ".join(f"{n} views: {r['label']} (J {r['J']:.3f})" for n, r in best["best_by_size"].items()) + ".",
          f"Designs: best J among subsets {best['designs']['best_J']['subset']:.3f}, lattice sample {best['designs']['best_J']['lattice']:.3f}, LHS sample {best['designs']['best_J']['lhs']:.3f}; "
          f"coverage (centred L2 discrepancy) lattice {best['designs']['lattice']['centred_L2_discrepancy']:.3f} vs LHS {best['designs']['lhs']['centred_L2_discrepancy']:.3f}.", "",
          "### Top-5 mixes and the best subset\n", mixes,
          "## 2. Parameters with standard errors (native metric)\n", "| model | BT strength (centred) | BT SE vs reference | BT bootstrap SD | Rasch ability | Rasch SE | Rasch bootstrap SD | Copeland | Kemeny position |", "|---|---|---|---|---|---|---|---|---|"]
    P = params["native"]
    for i, m in enumerate(models):
        L.append(f"| {m} | {P['bradley_terry']['beta'][i]:+.3f} | {P['bradley_terry']['se_vs_reference'][i]:.3f} | {pb['bt_beta_sd_bootstrap'][i]:.3f} | {P['rasch']['theta'][i]:+.3f} | {P['rasch']['se_theta'][i]:.3f} | {pb['rasch_theta_sd_bootstrap'][i]:.3f} | {P['copeland'][i]:.1f} | {int(P['kemeny']['position'][i]) + 1} |")
    L += ["", f"Kemeny cost {P['kemeny']['kendall_cost']:.0f} of {P['kemeny']['max_cost']:.0f} possible pairwise disagreements; Rasch item difficulties: mean {P['rasch_item_difficulty_summary']['mean']:+.2f}, sd {P['rasch_item_difficulty_summary']['sd']:.2f}, mean SE {P['rasch_item_difficulty_summary']['se_mean']:.2f} "
          f"(per item in `params/rasch_item_difficulties.csv`). The analytic SEs assume the model is right; the bootstrap SDs do not, and with {M} models they are the ones to quote.",
          "", "## 3. Honest selection (split-half)\n",
          f"* {sh['splits']} random half-splits: the mix selected on half A has J {sh['J_A_selected_mean']:.3f} there and {sh['J_B_selected_mean']:.3f} on half B (optimism gap {sh['optimism_gap']:.3f}); on half B pure Bradley–Terry scores {sh['J_B_pure_bt_mean']:.3f}, the uniform mix {sh['J_B_uniform_mean']:.3f}, the full-data best {sh['J_B_full_best_mean']:.3f}.",
          f"* Selected minus pure BT on the held-out half: {sh['selected_minus_pure_bt']['mean']:+.3f} [{sh['selected_minus_pure_bt']['ci95'][0]:+.3f}, {sh['selected_minus_pure_bt']['ci95'][1]:+.3f}]; selected ahead in {100 * sh['selected_minus_pure_bt']['share_selected_ahead']:.0f} % of splits. Most selected: " + ", ".join(f"{k} ({v})" for k, v in sh["selection_counts"].items()) + ".",
          "", "## 4. Leaderboards (Bradley–Terry rank, Borda in brackets) with significance\n", "| rule | " + " | ".join(models) + " | Friedman p | Kendall's W | significant pairs |", "|---|" + "---|" * M + "---|---|---|"]
    for name, r in lbsum.items():
        L.append(f"| {name} | " + " | ".join(f"{r['bt_ranking'][m]} ({r['borda_ranking'][m]})" for m in models) + f" | {r['friedman_p']:.3f} | {r['kendall_W']:.2f} | {', '.join(r['significant_pairs_holm']) or 'none'} |")
    L += official_table_md(OUT / "leaderboards" / "native", models, datasets, "Official-split estimates under the native metric")
    L += ["", "Full tables, strengths with SE, 1,000 bootstrap draws and Holm-corrected pairwise tests under `leaderboards/native/` and `leaderboards/em_only/`.",
          "", "## 5. Dataset diagnostics\n", "| dataset | family | mean | spread | self-stability τ | τ to others | exclude |", "|---|---|---|---|---|---|---|"] + \
         [f"| {r.dataset} | {r.family} | {r.mean_score:.3f} | {r.spread_across_models:.3f} | {r.ranking_self_stability_tau:.2f} | {r.tau_to_others_mean:+.2f} | {r.exclude_from_objective} |" for _, r in diag.iterrows()]
    L += ["", "## 6. Reading\n",
          f"* Every combination of the eight views is now on file (`combos/`, {best['n_subsets']} subsets with member parameters), so the choice of aggregation rule is an enumerated, reproducible decision rather than a sample.",
          f"* The split-half check is the honesty test for that choice: if the selected mix beats pure Bradley–Terry on held-out halves in most splits, mixing views is worth it; otherwise pure BT is the defensible headline (Chatbot Arena's rule).",
          f"* With {M} models every parameter table is coarse; the bootstrap SDs say how coarse. The 12-model run is what makes section 2 informative.",
          "* Files: views.csv, views_em.csv, Zb.npz (bootstrap view tables + per-draw BT/Rasch parameters), combos/, params/, designs.json, selection/split_half.{csv,json}, best.json, leaderboards/, diagnostics/."]
    open(ROOT / "REPORT.md", "w").write("\n".join(L) + "\n"); print("wrote", ROOT / "REPORT.md")


if __name__ == "__main__":
    main()
