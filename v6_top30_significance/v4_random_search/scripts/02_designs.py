#!/usr/bin/env python
"""
v4 step 2 - Search over the nine component weights with three sampled designs at the same budget, plus fixed baselines.

Nine weights on the step-0.05 lattice = 3,108,105 points: too many to enumerate, so the candidate set is
  * Dirichlet-snapped random design (the original v4 design), N points
  * Latin-hypercube-on-the-simplex design, N points
  * uniform-lattice design, N points
  * baselines: exact match, F1 only, numeric tolerance only, uniform, the v1 rubric embedded in 9 dimensions (F1 .35, decay .35, P .15, R .15)
All candidates are evaluated with the same objective as v2 (J = mean tau to the Borda pool; also Kemeny / Copeland / BT pooling,
tau to native metrics).  Design comparison: 20 seeds per design, coverage diagnostics, best J found; regret is relative to the best over
all seeds and designs (no exhaustive optimum exists here).
Outputs: output/grid_candidates.csv (the N x 3 + baselines set, sorted by J), output/best.json, output/designs.csv, designs_summary.json,
         output/tensors.npz, tensors_index.json, fig_landscape, fig_designs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from metrics import COMPONENT_NAMES  # noqa: E402
from search.audit import design_comparison, design_summary, evaluate_all, load_tensors  # noqa: E402
from search.sampling import sample_dirichlet_lattice, sample_lhs_simplex, sample_uniform_lattice, n_lattice_points  # noqa: E402

COMP = list(COMPONENT_NAMES); K = len(COMP); STEP = 0.05
BASE = {"em_only": {"em": 1}, "f1_only": {"tok_f1": 1}, "num_tol_only": {"num_tol": 1}, "uniform": {c: 1 / K for c in COMP},
        "v1_rubric": {"tok_f1": .35, "num_decay": .35, "tok_prec": .15, "tok_rec": .15}}
BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#3a9d5d"


def vec(d):
    return np.array([d.get(c, 0.0) for c in COMP])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=100); ap.add_argument("--seeds", type=int, default=20); ap.add_argument("--seed", type=int, default=20260909)
    args = ap.parse_args()
    models, datasets, X, EM, NAT, uids, fam = load_tensors(OUT / "components.csv", COMP)
    np.savez_compressed(OUT / "tensors.npz", **{f"X_{d}": X[d] for d in datasets}, **{f"EM_{d}": EM[d] for d in datasets}, **{f"NAT_{d}": NAT[d] for d in datasets})
    json.dump({"models": models, "datasets": datasets, "families": fam, "uids": uids, "components": COMP}, open(OUT / "tensors_index.json", "w"))
    print(f"{len(models)} models x {len(datasets)} datasets; lattice has {n_lattice_points(K, STEP):,} points; sampling {args.n} per design")
    designs = {"dirichlet": sample_dirichlet_lattice(args.n, K, STEP, args.seed), "lhs": sample_lhs_simplex(args.n, K, STEP, args.seed), "uniform_lattice": sample_uniform_lattice(args.n, K, STEP, args.seed)}
    W = np.vstack([vec(v) for v in BASE.values()] + list(designs.values()))
    labels = {i: n for i, n in enumerate(BASE)}; src = list(BASE) + sum([[k] * args.n for k in designs], [])
    grid, S = evaluate_all(W, X, EM, NAT, datasets, models, COMP, labels, with_bt=True); grid["design"] = src
    grid = grid.sort_values(["J", "tau_native"], ascending=False).reset_index(drop=True); grid.insert(0, "rank", range(1, len(grid) + 1))
    grid.to_csv(OUT / "grid_candidates.csv", index=False)
    WC = [f"w_{c}" for c in COMP]; best = grid.iloc[0]; v1 = grid[grid.label == "v1_rubric"].iloc[0]; em = grid[grid.label == "em_only"].iloc[0]
    # design comparison across seeds (no exhaustive optimum: regret vs the best found over all seeds and designs)
    def ev(Wd):
        return evaluate_all(Wd, X, EM, NAT, datasets, models, COMP, with_bt=False)[0].J.to_numpy()
    des = design_comparison(K, STEP, args.n, args.seeds, ev); des["regret"] = des.best_J_found.max() - des.best_J_found; des.to_csv(OUT / "designs.csv", index=False)
    dsum = design_summary(des); json.dump(dsum, open(OUT / "designs_summary.json", "w"), indent=2)
    out = {"n_candidates": int(len(grid)), "n_per_design": args.n, "step": STEP, "lattice_points": n_lattice_points(K, STEP), "components": COMP, "models": models, "datasets": datasets,
           "best": {"weights": dict(zip(COMP, best[WC].astype(float).round(2).tolist())), "design": best.design, "J": float(best.J), "tau_native": float(best.tau_native), "J_kemeny": float(best.J_kemeny), "J_copeland": float(best.J_copeland), "J_bt": float(best.J_bt)},
           "best_per_design": {k: {"J": float(grid[grid.design == k].J.max()), "weights": dict(zip(COMP, grid[grid.design == k].iloc[0][WC].astype(float).round(2).tolist()))} for k in designs},
           "baselines": {n: {"J": float(grid[grid.label == n].J.iloc[0]), "rank": int(grid[grid.label == n]["rank"].iloc[0]), "tau_native": float(grid[grid.label == n].tau_native.iloc[0])} for n in BASE},
           "v1_rubric": {"J": float(v1.J), "rank": int(v1["rank"]), "n_better": int((grid.J > v1.J).sum()), "n_tied": int((grid.J == v1.J).sum()) - 1},
           "em_only": {"J": float(em.J), "rank": int(em["rank"])},
           "top5": [{"rank": int(r["rank"]), "design": r.design, "weights": dict(zip(COMP, r[WC].astype(float).round(2).tolist())), "J": float(r.J), "tau_native": float(r.tau_native)} for _, r in grid.head(5).iterrows()],
           "designs_over_seeds": dsum, "j_quantiles": {q: float(grid.J.quantile(q)) for q in [0.5, 0.9, 0.95, 0.99]}}
    json.dump(out, open(OUT / "best.json", "w"), indent=2)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for k, col in zip(designs, [BLUE, GREEN, GRAY]):
        sub = grid[grid.design == k].sort_values("J", ascending=False); ax.plot(np.arange(len(sub)), sub.J, color=col, lw=1.2, label=f"{k} (best {sub.J.max():.3f})")
    for n, col, mk in [("v1_rubric", ORANGE, "o"), ("em_only", INK, "s"), ("f1_only", INK, "^"), ("uniform", INK, "v")]:
        ax.axhline(grid[grid.label == n].J.iloc[0], color=col, ls=":", lw=0.8); ax.text(args.n, grid[grid.label == n].J.iloc[0], n, fontsize=6, ha="right", va="bottom", color=col)
    ax.set_xlabel("candidate (sorted by J within design)"); ax.set_ylabel("J = mean τ to Borda pool"); ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "fig_landscape.png", dpi=200); fig.savefig(OUT / "fig_landscape.pdf"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5, 3))
    for name, col in zip(["uniform_lattice", "dirichlet_lattice", "lhs_simplex"], [GRAY, BLUE, GREEN]):
        sub = des[des.design == name]; ax.scatter(sub.centred_L2_discrepancy, sub.best_J_found, color=col, s=16, label=name)
    ax.set_xlabel("centred L2 discrepancy (lower = more even)"); ax.set_ylabel(f"best J found ({args.n} points)"); ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "fig_designs.png", dpi=200); fig.savefig(OUT / "fig_designs.pdf"); plt.close(fig)
    print(f"best J {best.J:.3f} ({best.design}) {out['best']['weights']}; v1 rubric J {v1.J:.3f} rank {int(v1['rank'])}; EM J {em.J:.3f} rank {int(em['rank'])}")
    print(pd.DataFrame(dsum).T.to_string())


if __name__ == "__main__":
    main()
