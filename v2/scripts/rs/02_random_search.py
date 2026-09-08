#!/usr/bin/env python
"""
Step 2 - Random search over 100 weight combinations (drawn from the simplex grid) to
calibrate the composite score so that model rankings are consistent across datasets.

Composite:  S(pred, gold) = sum_k w_k m_k(pred, gold)      w on the simplex, one global vector
Objective:  J(w) = mean over datasets d of Kendall tau( ranking of models on d , pooled ranking )
            where the pooled ranking is the Borda ensemble of all per-dataset rankings.
Secondary:  mean pairwise tau between datasets; Kemeny-consensus agreement; score-scale
            dispersion (how much a model's score moves between datasets).

Outputs (output/rs/): weights_random_search.csv (100 rows), best_weights.json, baselines.csv,
                      lodo.csv, fig_random_search.png/pdf
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from metrics import COMPONENT_NAMES, K, PRESET_WEIGHTS  # noqa: E402
from pooling.rank_aggregation import (consensus_ranking, dataset_agreement, kendall_tau,  # noqa: E402
                                      pairwise_dataset_tau, ranks_from_scores)

N_COMBOS = 100
GRID_STEP = 0.05
SEED = 20260907
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b"


def load():
    z = np.load(ROOT / "output" / "rs" / "components.npz")
    idx = pd.read_csv(ROOT / "output" / "rs" / "index.csv")
    return z["M"][:, :K], idx


def sample_grid_weights(n, k, step, rng):
    """n distinct weight vectors on the simplex whose entries are multiples of `step`
    (random search over the grid: draw Dirichlet(1) points and snap them to the grid)."""
    seen, out = set(), []
    units = int(round(1 / step))
    while len(out) < n:
        p = rng.dirichlet(np.ones(k))
        c = np.floor(p * units).astype(int)
        for _ in range(units - c.sum()):          # distribute the remainder to largest residuals
            c[np.argmax(p * units - c)] += 1
        key = tuple(c)
        if key in seen:
            continue
        seen.add(key)
        out.append(c / units)
    return np.asarray(out)


def score_table(M, idx, w):
    """(n_models, n_datasets) mean composite; also list of per-dataset (items x models) arrays."""
    s = M @ w
    df = idx.assign(S=s)
    piv = df.pivot_table(index="model", columns="dataset", values="S", aggfunc="mean")
    items = [df[df.dataset == d].pivot_table(index="uid", columns="model", values="S").reindex(columns=piv.index).to_numpy()
             for d in piv.columns]
    return piv, items


def evaluate(piv):
    S = piv.to_numpy()
    R_borda = consensus_ranking(S, "borda")
    R_kem = consensus_ranking(S, "kemeny")
    agree = dataset_agreement(S, R_borda)
    T = pairwise_dataset_tau(S)
    iu = np.triu_indices(S.shape[1], 1)
    # scale dispersion: after removing each dataset's mean (difficulty), how much a model's relative
    # standing moves between datasets, relative to the spread between models (lower = more consistent)
    C = S - S.mean(0, keepdims=True)
    disp = float(np.mean(C.std(1)) / (C.mean(1).std() + 1e-9))
    return {"J_tau_to_pooled": float(np.mean(agree)), "tau_to_kemeny": float(np.mean(dataset_agreement(S, R_kem))),
            "mean_pairwise_tau": float(np.mean(T[iu])), "min_dataset_agreement": float(np.min(agree)),
            "scale_dispersion": disp, "borda_vs_kemeny": kendall_tau(-R_borda, -R_kem)}


def bootstrap_J(items, w_idx_M, idx, w, n_boot=200, seed=0):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        cols = []
        for X in items:
            ii = rng.integers(0, X.shape[0], X.shape[0])
            cols.append(np.nanmean(X[ii], axis=0))
        S = np.stack(cols, axis=1)
        vals.append(float(np.mean(dataset_agreement(S, consensus_ranking(S, "borda")))))
    return float(np.mean(vals)), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def main():
    out = ROOT / "output" / "rs"
    M, idx = load()
    rng = np.random.default_rng(SEED)
    W = sample_grid_weights(N_COMBOS, K, GRID_STEP, rng)
    rows = []
    for i, w in enumerate(W):
        piv, items = score_table(M, idx, w)
        ev = evaluate(piv)
        rows.append({"combo": i, **{f"w_{n}": float(x) for n, x in zip(COMPONENT_NAMES, w)}, **ev})
    df = pd.DataFrame(rows).sort_values(["J_tau_to_pooled", "mean_pairwise_tau"], ascending=False).reset_index(drop=True)
    df.insert(0, "rank", np.arange(1, len(df) + 1))
    # bootstrap the top 5 and the median combo
    for r in list(range(5)) + [len(df) // 2, len(df) - 1]:
        w = df.loc[r, [f"w_{n}" for n in COMPONENT_NAMES]].to_numpy(dtype=float)
        piv, items = score_table(M, idx, w)
        m, lo, hi = bootstrap_J(items, None, idx, w)
        df.loc[r, ["J_boot_mean", "J_boot_lo", "J_boot_hi"]] = [m, lo, hi]
    df.to_csv(out / "weights_random_search.csv", index=False)
    best = df.iloc[0]
    w_best = best[[f"w_{n}" for n in COMPONENT_NAMES]].to_numpy(dtype=float)
    # baselines
    brows = []
    for name, ws in PRESET_WEIGHTS.items():
        w = ws.get("numeric")
        piv, _ = score_table(M, idx, w)
        brows.append({"baseline": name, **{f"w_{n}": float(x) for n, x in zip(COMPONENT_NAMES, w)}, **evaluate(piv)})
    piv, _ = score_table(M, idx, w_best)
    brows.append({"baseline": "random_search_best", **{f"w_{n}": float(x) for n, x in zip(COMPONENT_NAMES, w_best)}, **evaluate(piv)})
    pd.DataFrame(brows).to_csv(out / "baselines.csv", index=False)
    # leave-one-dataset-out: choose best combo without d, test agreement of d with the pooled ranking of the rest
    datasets = sorted(idx.dataset.unique())
    lrows = []
    for d in datasets:
        best_j, best_w = -9, None
        keep = (idx.dataset != d).to_numpy()
        for w in W:
            piv, _ = score_table(M[keep], idx[keep].reset_index(drop=True), w)
            j = evaluate(piv)["J_tau_to_pooled"]
            if j > best_j:
                best_j, best_w = j, w
        piv_all, _ = score_table(M, idx, best_w)
        S_rest = piv_all.drop(columns=[d]).to_numpy()
        R_rest = consensus_ranking(S_rest, "borda")
        tau_held = kendall_tau(-ranks_from_scores(piv_all[d].to_numpy()), -R_rest)
        piv_full, _ = score_table(M, idx, w_best)
        tau_full = kendall_tau(-ranks_from_scores(piv_full[d].to_numpy()), -consensus_ranking(piv_full.drop(columns=[d]).to_numpy(), "borda"))
        lrows.append({"held_out": d, "J_without": best_j, "tau_heldout_lodo_weights": tau_held, "tau_heldout_full_weights": tau_full,
                      "l1_shift": float(np.abs(best_w - w_best).sum())})
    pd.DataFrame(lrows).to_csv(out / "lodo.csv", index=False)
    json.dump({"weights": {n: float(x) for n, x in zip(COMPONENT_NAMES, w_best)}, "objective": float(best.J_tau_to_pooled),
               "bootstrap_J": [float(best.J_boot_lo), float(best.J_boot_hi)], "n_combos": N_COMBOS, "grid_step": GRID_STEP, "seed": SEED,
               "search": "random search over the simplex grid (Dirichlet(1) draws snapped to multiples of grid_step)"},
              open(out / "best_weights.json", "w"), indent=2)
    # figure
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)
    ax = axes[0]
    ax.bar(df["rank"], df["J_tau_to_pooled"], color=GRAY, width=1.0, lw=0)
    ax.bar(df["rank"][:10], df["J_tau_to_pooled"][:10], color=BLUE, width=1.0, lw=0)
    for name, c in [("em_only", ORANGE), ("original_rcustom", "#1baf7a"), ("uniform", "#eda100")]:
        j = [b for b in brows if b["baseline"] == name][0]["J_tau_to_pooled"]
        ax.axhline(j, color=c, lw=1, ls="--")
        ax.text(len(df) - 1, j, name, fontsize=6.5, ha="right", va="bottom", color=c)
    ax.set_xlabel("weight combination (sorted)"); ax.set_ylabel("J = mean tau to pooled ranking")
    ax.set_title("Random search over 100 grid combinations", fontsize=8, loc="left")
    ax = axes[1]
    top = df.head(10)[[f"w_{n}" for n in COMPONENT_NAMES]].to_numpy()
    im = ax.imshow(top, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#fcfcfb", "#2a78d6", "#0d366b"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(K)); ax.set_xticklabels(COMPONENT_NAMES, rotation=60, ha="right", fontsize=7)
    ax.set_yticks(range(10)); ax.set_yticklabels([f"#{i + 1}  J={j:.2f}" for i, j in enumerate(df.head(10).J_tau_to_pooled)], fontsize=7)
    for i in range(10):
        for j in range(K):
            if top[i, j] > 0.001:
                ax.text(j, i, f"{top[i, j]:.2f}", ha="center", va="center", fontsize=5.5, color="white" if top[i, j] > 0.5 else INK)
    ax.set_title("Top-10 weight vectors", fontsize=8, loc="left"); ax.grid(False)
    fig.savefig(out / "fig_random_search.png", dpi=200); fig.savefig(out / "fig_random_search.pdf")
    print(df.head(10)[["rank", "J_tau_to_pooled", "mean_pairwise_tau", "scale_dispersion", "J_boot_lo", "J_boot_hi"] + [f"w_{n}" for n in COMPONENT_NAMES]].round(3).to_string(index=False))
    print("\nbaselines:\n", pd.DataFrame(brows)[["baseline", "J_tau_to_pooled", "mean_pairwise_tau", "scale_dispersion"]].round(3).to_string(index=False))
    print("\nLODO:\n", pd.DataFrame(lrows).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
