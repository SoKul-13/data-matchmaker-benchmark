#!/usr/bin/env python
"""
v2 step 2 - EXHAUSTIVE grid over the four v1 weights, plus the sampled designs for comparison.

Candidates: every point of the step-0.05 simplex lattice over (F1, decay, precision, recall) = 1,771 weightings; v1's point
(0.35, 0.35, 0.15, 0.15), the four corners and the uniform mix are lattice points and are labelled.  With --fine the step-0.02
lattice (23,426) is evaluated as well and saved separately.
Per weighting w:  R_w = w . [F1, decay, precision, recall] per answer -> mean per (model, dataset) -> ranks per dataset ->
  J        = mean over datasets of Kendall tau-b(dataset ranking, Borda-pooled ranking)           [agreement among datasets]
  J_kemeny / J_copeland / J_bt = the same with Kemeny, Copeland and Bradley-Terry pooling          [robustness of the objective]
  tau_native = mean over datasets of tau(R_w ranking, native-metric ranking)                       [fidelity to the datasets' own metrics]
  min_agree, pairwise_tau, dispersion
Designs: uniform-lattice, Dirichlet-snapped and Latin-hypercube samples of 100 points, 20 seeds each: coverage diagnostics, best J found,
  and the rank of that best inside the exhaustive grid.
Outputs: output/grid_exhaustive.csv, output/grid_fine.csv (--fine), output/best.json, output/designs.csv, output/designs_summary.json,
         output/fig_landscape.png/pdf, output/fig_marginals.png/pdf, output/fig_designs.png/pdf, output/tensors.npz (per-dataset item tensors)
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
from pooling.rank_aggregation import consensus_ranking, kendall_tau, ranks_from_scores  # noqa: E402
from search.fast_rank import J_many, ranks_many, tau_b  # noqa: E402
from search.sampling import coverage, n_lattice_points, sample_dirichlet_lattice, sample_lhs_simplex, sample_uniform_lattice, simplex_grid  # noqa: E402
from stats.params import bt_fit  # noqa: E402

COMP = ["f1", "decay", "precision", "recall"]
V1 = np.array([0.35, 0.35, 0.15, 0.15])
STEP, N_DESIGN, N_SEEDS = 0.05, 100, 20
BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#3a9d5d"


def load_tensors():
    df = pd.read_csv(OUT / "components_v1.csv")
    models = sorted(df.model.unique()); datasets = sorted(df.dataset.unique())
    X, EM, NAT, uids = {}, {}, {}, {}
    for d in datasets:
        g = df[df.dataset == d]
        piv = {c: g.pivot_table(index="uid", columns="model", values=c).reindex(columns=models) for c in COMP + ["em", "native_value"]}
        X[d] = np.stack([piv[c].to_numpy(float) for c in COMP], -1)          # n_d x M x 4
        EM[d] = piv["em"].to_numpy(float); NAT[d] = piv["native_value"].to_numpy(float); uids[d] = list(piv["f1"].index)
    fam = df.drop_duplicates("dataset").set_index("dataset").family.to_dict()
    return models, datasets, X, EM, NAT, uids, fam


def score_tensor(X, W, datasets):
    """S (C x M x D) = per-dataset mean of the composite under every candidate"""
    means = np.stack([np.nanmean(X[d], 0) for d in datasets], -1)            # M x 4 x D
    return np.einsum("ck,mkd->cmd", W, means)


def label_of(w):
    if np.allclose(w, V1): return "v1_original"
    if np.allclose(w, np.ones(4) / 4): return "uniform"
    for k, c in enumerate(COMP):
        if w[k] == 1.0: return f"only_{c}"
    return ""


def pooled_J(S, rule):
    """J under a non-Borda pooling rule (loops; used for the robustness columns)"""
    out = np.empty(S.shape[0])
    for c in range(S.shape[0]):
        R = consensus_ranking(S[c], rule)
        out[c] = np.mean([kendall_tau(-ranks_from_scores(S[c][:, j]), -R) for j in range(S.shape[2])])
    return out


def bt_J(X, W, datasets, models):
    """J with Bradley-Terry pooling: item-level pairwise wins under each candidate -> BT strengths -> ranking -> mean tau"""
    M = len(models); C = len(W); out = np.empty(C); Rc_all = np.empty((C, M))
    per_item = [np.einsum("ck,nmk->cnm", W, X[d]) for d in datasets]          # list of C x n_d x M
    for c in range(C):
        wins = np.zeros((M, M))
        for s in per_item:
            sc = s[c]                                                          # n_d x M
            gt = (sc[:, :, None] > sc[:, None, :]).sum(0); eq = (sc[:, :, None] == sc[:, None, :]).sum(0)
            wins += gt + 0.5 * (eq - np.eye(M) * sc.shape[0])
        beta = bt_fit(wins)["beta"]; Rc = ranks_from_scores(beta); Rc_all[c] = Rc
        S = np.stack([s[c].mean(0) for s in per_item], 1)
        out[c] = np.mean([kendall_tau(-ranks_from_scores(S[:, j]), -Rc) for j in range(S.shape[1])])
    return out, Rc_all


def evaluate_all(W, X, EM, NAT, datasets, models, with_bt=True):
    S = score_tensor(X, W, datasets)
    res = J_many(S)
    natS = np.stack([np.nanmean(NAT[d], 0) for d in datasets], 1)                        # M x D
    Rn = ranks_many(natS[None])[0]                                                        # M x D
    R = ranks_many(S)                                                                     # C x M x D
    tau_nat = tau_b(np.moveaxis(R, 1, 2), np.moveaxis(Rn, 0, 1)[None]).mean(1)
    Cc = S - S.mean(1, keepdims=True)
    disp = Cc.std(2).mean(1) / (Cc.mean(2).std(1) + 1e-9)
    df = pd.DataFrame({f"w_{c}": W[:, k] for k, c in enumerate(COMP)})
    df["label"] = [label_of(w) for w in W]
    df["J"] = res["J"]; df["min_agree"] = res["min_agree"]; df["pairwise_tau"] = res["pairwise_tau"]; df["tau_native"] = tau_nat; df["dispersion"] = disp
    df["J_kemeny"] = pooled_J(S, "kemeny"); df["J_copeland"] = pooled_J(S, "copeland")
    if with_bt:
        df["J_bt"], _ = bt_J(X, W, datasets, models)
    for j, d in enumerate(datasets):
        df[f"tau_{d}"] = res["tau_per_dataset"][:, j]
    for m_i, m in enumerate(models):
        df[f"rank_{m}"] = res["consensus_ranks"][:, m_i]
    return df, S


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--fine", action="store_true", help="also evaluate the step-0.02 lattice (23,426 points)")
    args = ap.parse_args()
    models, datasets, X, EM, NAT, uids, fam = load_tensors()
    np.savez_compressed(OUT / "tensors.npz", **{f"X_{d}": X[d] for d in datasets}, **{f"EM_{d}": EM[d] for d in datasets},
                        **{f"NAT_{d}": NAT[d] for d in datasets}, models=np.array(models), datasets=np.array(datasets))
    json.dump({"models": models, "datasets": datasets, "families": fam, "uids": uids}, open(OUT / "tensors_index.json", "w"))
    G = simplex_grid(4, STEP)
    print(f"exhaustive lattice: {len(G)} weightings at step {STEP}; {len(models)} models x {len(datasets)} datasets")
    grid, S = evaluate_all(G, X, EM, NAT, datasets, models)
    grid = grid.sort_values(["J", "tau_native"], ascending=False).reset_index(drop=True); grid.insert(0, "rank", range(1, len(grid) + 1))
    grid.to_csv(OUT / "grid_exhaustive.csv", index=False)
    best = grid.iloc[0]; v1 = grid[grid.label == "v1_original"].iloc[0]
    n_better = int((grid.J > v1.J).sum()); n_tie = int((grid.J == v1.J).sum()) - 1
    # ---- sampled designs at the same budget
    drows = []
    for seed in range(N_SEEDS):
        for name, fn in [("uniform_lattice", sample_uniform_lattice), ("dirichlet_lattice", sample_dirichlet_lattice), ("lhs_simplex", sample_lhs_simplex)]:
            W = fn(N_DESIGN, 4, STEP, seed + 1000)
            cov = coverage(W); sub, _ = evaluate_all(W, X, EM, NAT, datasets, models, with_bt=False)
            bj = sub.J.max(); w_best = sub.loc[sub.J.idxmax(), [f"w_{c}" for c in COMP]].to_numpy()
            rank_in_grid = int(grid[(np.abs(grid[[f"w_{c}" for c in COMP]].to_numpy() - w_best).sum(1) < 1e-9)]["rank"].iloc[0])
            drows.append({"design": name, "seed": seed, **cov, "best_J_found": float(bj), "best_rank_in_exhaustive": rank_in_grid,
                          "regret": float(best.J - bj), "share_of_grid_max": float(bj / best.J) if best.J else np.nan})
    designs = pd.DataFrame(drows); designs.to_csv(OUT / "designs.csv", index=False)
    dsum = designs.groupby("design").agg(best_J_mean=("best_J_found", "mean"), best_J_sd=("best_J_found", "std"), regret_mean=("regret", "mean"),
                                         regret_max=("regret", "max"), rank_median=("best_rank_in_exhaustive", "median"), rank_worst=("best_rank_in_exhaustive", "max"),
                                         min_pairwise_L1=("min_pairwise_L1", "mean"), mean_nearest_L1=("mean_nearest_L1", "mean"),
                                         discrepancy=("centred_L2_discrepancy", "mean"), zero_share=("share_with_a_zero_weight", "mean")).round(4)
    dsum.to_json(OUT / "designs_summary.json", indent=2)
    # ---- fine lattice
    fine_info = None
    if args.fine:
        Gf = simplex_grid(4, 0.02); print(f"fine lattice: {len(Gf)} weightings")
        gf, _ = evaluate_all(Gf, X, EM, NAT, datasets, models, with_bt=False)
        gf = gf.sort_values(["J", "tau_native"], ascending=False).reset_index(drop=True); gf.insert(0, "rank", range(1, len(gf) + 1))
        gf.to_csv(OUT / "grid_fine.csv", index=False)
        fine_info = {"n": int(len(gf)), "best_J": float(gf.J.iloc[0]), "best_weights": dict(zip(COMP, gf.iloc[0][[f"w_{c}" for c in COMP]].astype(float).round(2).tolist())),
                     "v1_rank": int(gf[gf.label == "v1_original"]["rank"].iloc[0]), "n_better_than_v1": int((gf.J > gf[gf.label == "v1_original"].J.iloc[0]).sum())}
    # ---- best.json
    wcols = [f"w_{c}" for c in COMP]
    out = {"n_candidates": int(len(grid)), "step": STEP, "n_lattice_points": n_lattice_points(4, STEP), "models": models, "datasets": datasets,
           "best": {"weights": dict(zip(COMP, best[wcols].astype(float).round(2).tolist())), "J": float(best.J), "tau_native": float(best.tau_native),
                    "J_kemeny": float(best.J_kemeny), "J_copeland": float(best.J_copeland), "J_bt": float(best.J_bt)},
           "v1_original": {"weights": dict(zip(COMP, V1.tolist())), "J": float(v1.J), "tau_native": float(v1.tau_native), "rank": int(v1["rank"]),
                           "n_better": n_better, "n_tied": n_tie, "share_better": n_better / (len(grid) - 1), "J_kemeny": float(v1.J_kemeny),
                           "J_copeland": float(v1.J_copeland), "J_bt": float(v1.J_bt)},
           "best_under_other_pooling": {r: {"weights": dict(zip(COMP, grid.loc[grid[f"J_{r}"].idxmax(), wcols].astype(float).round(2).tolist())), "J": float(grid[f"J_{r}"].max()),
                                            "v1_rank": int((grid[f"J_{r}"] > v1[f"J_{r}"]).sum() + 1)} for r in ["kemeny", "copeland", "bt"]},
           "top5": [{"rank": int(r["rank"]), "weights": dict(zip(COMP, r[wcols].astype(float).round(2).tolist())), "J": float(r.J), "tau_native": float(r.tau_native)} for _, r in grid.head(5).iterrows()],
           "corners": {lab: float(grid[grid.label == lab].J.iloc[0]) for lab in [f"only_{c}" for c in COMP] + ["uniform"]},
           "designs": json.loads(dsum.to_json()), "fine_lattice": fine_info,
           "j_quantiles": {q: float(grid.J.quantile(q)) for q in [0.5, 0.9, 0.95, 0.99]}}
    json.dump(out, open(OUT / "best.json", "w"), indent=2)
    # ---- figures
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(grid["rank"], grid.J, color=BLUE, lw=1.2, label="all %d weightings (sorted)" % len(grid))
    ax.axhline(v1.J, color=ORANGE, ls="--", lw=1); ax.scatter([v1["rank"]], [v1.J], color=ORANGE, zorder=5, label=f"v1 weights (rank {int(v1['rank'])})")
    for lab, col in zip([f"only_{c}" for c in COMP], ["#777", "#999", "#aaa", "#bbb"]):
        r = grid[grid.label == lab].iloc[0]; ax.scatter([r["rank"]], [r.J], color=GRAY, marker="s", s=18, zorder=4)
        ax.annotate(lab.replace("only_", ""), (r["rank"], r.J), fontsize=6, color=INK, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("weighting (sorted by J)"); ax.set_ylabel("J = mean τ to Borda pool"); ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(OUT / "fig_landscape.png", dpi=200); fig.savefig(OUT / "fig_landscape.pdf"); plt.close(fig)
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.6), sharey=True)
    for k, (c, ax) in enumerate(zip(COMP, axes)):
        ax.scatter(grid[f"w_{c}"] + np.random.default_rng(k).uniform(-0.008, 0.008, len(grid)), grid.J, s=3, alpha=0.25, color=BLUE)
        mx = grid.groupby(f"w_{c}").J.max(); ax.plot(mx.index, mx.values, color=INK, lw=1, label="max J at this weight")
        ax.axvline(V1[k], color=ORANGE, ls="--", lw=1); ax.set_xlabel(f"w_{c}"); ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("J"); axes[0].legend(fontsize=6, frameon=False); fig.tight_layout(); fig.savefig(OUT / "fig_marginals.png", dpi=200); fig.savefig(OUT / "fig_marginals.pdf"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(5, 3))
    for name, col in zip(["uniform_lattice", "dirichlet_lattice", "lhs_simplex"], [GRAY, BLUE, GREEN]):
        sub = designs[designs.design == name]; ax.scatter(sub.centred_L2_discrepancy, sub.best_J_found, color=col, s=16, label=name)
    ax.axhline(best.J, color=INK, lw=0.8, ls=":"); ax.set_xlabel("centred L2 discrepancy (lower = more even)"); ax.set_ylabel("best J found (100 points)")
    ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(OUT / "fig_designs.png", dpi=200); fig.savefig(OUT / "fig_designs.pdf"); plt.close(fig)
    print(f"\nbest J {best.J:.3f} {dict(zip(COMP, best[wcols].astype(float).round(2)))}; v1 J {v1.J:.3f} rank {int(v1['rank'])}/{len(grid)}; {n_better} better, {n_tie} tied")
    print(dsum.to_string())


if __name__ == "__main__":
    main()
