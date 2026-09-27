#!/usr/bin/env python
"""
v5 step 7 - (a) sampled designs versus the exhaustive grid, (b) leaderboards with parameters, bootstrap draws and significance under
exact match, the native metric, the ensemble, and the five best single weightings, (c) rule agreement and dataset diagnostics.

(a) v5's grid is exhaustive (every step-0.02 point of the K-simplex x 5 hedge penalties), so a sampled design at the same step is a
    subset of it: uniform-lattice, Dirichlet-snapped and Latin-hypercube samples of 100 weightings (x 5 lambdas) are drawn for 20 seeds
    and their J is looked up in grid_all.csv; regret = exhaustive best J - best J found.
(b) item-level scores under each rule from matrix_models.npz (selected metric columns, hedge gate); report_rule() as in v2-v4.
Outputs: output/designs.csv, designs_summary.json, output/leaderboards/<rule>/*, rule_agreement.csv, summary.json, output/diagnostics/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from calibration.grid import LAMBDAS, gated_scores  # noqa: E402
from families import family_of  # noqa: E402
from metrics.library import METRIC_NAMES  # noqa: E402
from search.sampling import coverage, sample_dirichlet_lattice, sample_lhs_simplex, sample_uniform_lattice  # noqa: E402
from stats.leaderboard import dataset_diagnostics, majority_baselines, poststrat_for, report_rule, rule_agreement, summary_of  # noqa: E402


def main():
    ens = json.load(open(OUT / "ensemble.json")); names = ens["selected"]; cols = ens["selected_idx"]; hcol = ens["hedge_col"]; K = len(names); step = ens["grid_step"]
    grid = pd.read_csv(OUT / "grid_all.csv"); WC = [f"w_{n}" for n in names]
    # ---- (a) designs looked up in the exhaustive grid
    key = {tuple(np.round(np.r_[r[WC].to_numpy(float), r["lambda"]], 4)): float(r.J) for _, r in grid.iterrows()}
    best_J = float(grid.J.max()); rows = []
    for seed in range(20):
        for dname, fn in [("uniform_lattice", sample_uniform_lattice), ("dirichlet_lattice", sample_dirichlet_lattice), ("lhs_simplex", sample_lhs_simplex)]:
            W = fn(100, K, step, seed + 1000); Js = [key.get(tuple(np.round(np.r_[w, l], 4)), np.nan) for w in W for l in LAMBDAS]; Js = np.array(Js, float)
            rows.append({"design": dname, "seed": seed, **coverage(W), "best_J_found": float(np.nanmax(Js)), "regret": best_J - float(np.nanmax(Js)), "share_of_grid_max": float(np.nanmax(Js) / best_J), "n_lookup_miss": int(np.isnan(Js).sum())})
    des = pd.DataFrame(rows); des.to_csv(OUT / "designs.csv", index=False)
    dsum = des.groupby("design").agg(best_J_mean=("best_J_found", "mean"), best_J_sd=("best_J_found", "std"), regret_mean=("regret", "mean"), regret_max=("regret", "max"),
                                     min_pairwise_L1=("min_pairwise_L1", "mean"), discrepancy=("centred_L2_discrepancy", "mean"), zero_share=("share_with_a_zero_weight", "mean")).round(4)
    json.dump({"exhaustive_best_J": best_J, "n_grid": int(len(grid)), **{d: r.to_dict() for d, r in dsum.iterrows()}}, open(OUT / "designs_summary.json", "w"), indent=2)
    # ---- (b) leaderboards
    M = np.load(OUT / "matrix_models.npz")["M"]; im = pd.read_csv(OUT / "index_models.csv"); models = sorted(im.model.unique()); datasets = sorted(im.dataset.unique())
    fam = {d: family_of(d) for d in datasets}; X = M[:, cols]; h = M[:, hcol]
    em_col = next(i for i, n in enumerate(METRIC_NAMES) if n in ("em", "em_norm", "exact_match"))
    def to_items(score_vec):
        df = im.assign(s=score_vec)
        return [df[df.dataset == d].pivot_table(index="uid", columns="model", values="s").reindex(columns=models).to_numpy(float) for d in datasets]
    top = grid.sort_values("J", ascending=False).head(5)
    rules = {"em_only": (M[:, em_col], None), "native": (im.native_value.to_numpy(float), None),
             "ensemble": (gated_scores(X, h, np.array([[ens["mean_weights"][n] for n in names] + [ens["mean_lambda"]]]))[:, 0], {**{n: round(ens["mean_weights"][n], 3) for n in names}, "lambda": round(ens["mean_lambda"], 3)})}
    for i, (_, r) in enumerate(top.iterrows()):
        w = np.array([r[c] for c in WC] + [r["lambda"]]); rules[f"top{i + 1}"] = (gated_scores(X, h, w[None])[:, 0], {**{n: float(r[f"w_{n}"]) for n in names}, "lambda": float(r["lambda"])})
    maj = majority_baselines(DATA / "pool", datasets); results, weights = {}, {}
    ps = poststrat_for(DATA / "pool", datasets, {d: sorted(im[im.dataset == d].uid.unique()) for d in datasets})
    for name, (vec, w) in rules.items():
        weights[name] = w; results[name] = report_rule(name, to_items(vec), datasets, models, fam, OUT / "leaderboards" / name, weights=w, majority=maj, poststrat=ps)
        print(f"[{name}] BT ranking: " + ", ".join(f"{m}={int(x)}" for m, x in zip(models, results[name]["rank_bt"])))
    rule_agreement(results).to_csv(OUT / "leaderboards" / "rule_agreement.csv"); json.dump(summary_of(results, models, weights), open(OUT / "leaderboards" / "summary.json", "w"), indent=2)
    dataset_diagnostics(results["ensemble"], datasets, models, fam, OUT / "diagnostics", label="v5 ensemble")
    print(dsum.to_string())


if __name__ == "__main__":
    main()
