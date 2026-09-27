#!/usr/bin/env python
"""
v2 step 3 - Is the "best weighting" real?  Nested selection, plateau, transfer and sensitivity.

A. Nested item bootstrap (B resamples, items resampled within each dataset):
   in each resample choose the best weighting on the IN-BAG items (over the whole exhaustive grid) and score it on the OUT-OF-BAG
   items.  Reports: in-bag J of the selected weighting (optimistic), out-of-bag J of the same weighting (honest), out-of-bag J of v1
   and of the full-data best, the paired difference best-vs-v1 with a bootstrap p-value, how often v1 is inside the plateau, and the
   distribution of the selected weights.  (Cawley & Talbot 2010; Varma & Simon 2006.)
B. Plateau: every candidate gets a bootstrap distribution of J (same resamples); a candidate is "in the plateau" if its paired
   difference to the full-data best is not significantly negative (paired bootstrap p > 0.05).  Size of the plateau, is v1 inside.
C. Leave-one-dataset-out and leave-one-family-out: choose the best weighting without the held-out part, then report the held-out
   dataset's tau to the pooled ranking of the rest under (i) the LODO weights, (ii) the full-data best, (iii) v1.
D. Per-family best weightings (families with >= 2 datasets) versus the global best.
E. Sensitivity: J over the lattice neighbourhood (L1 <= 0.10, i.e. one 0.05 unit moved) of v1 and of the best; flatness = max - min.
Outputs: output/selection/nested.json, nested_draws.npz, plateau.csv, lodo.csv, lofo.csv, per_family.json, sensitivity.json,
         fig_nested.png/pdf, fig_plateau.png/pdf
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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
from search.fast_rank import J_many, ranks_many, tau_b, borda_many  # noqa: E402
from stats.significance import paired_objective_test  # noqa: E402

COMP = ["f1", "decay", "precision", "recall"]; WC = [f"w_{c}" for c in COMP]
V1 = np.array([0.35, 0.35, 0.15, 0.15])
BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#3a9d5d"


def load():
    T = np.load(OUT / "tensors.npz", allow_pickle=True); idx = json.load(open(OUT / "tensors_index.json"))
    datasets, models = idx["datasets"], idx["models"]
    X = {d: T[f"X_{d}"] for d in datasets}
    grid = pd.read_csv(OUT / "grid_exhaustive.csv"); W = grid[WC].to_numpy(float)
    return datasets, models, X, grid, W, idx["families"]


def J_from_means(means, W):
    """means: M x 4 x D  -> J for all candidates"""
    return J_many(np.einsum("ck,mkd->cmd", W, means))["J"]


def means_of(X, datasets, idx_sets):
    return np.stack([np.nanmean(X[d][idx_sets[d]], 0) for d in datasets], -1)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--boot", type=int, default=1000); ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    sel = OUT / "selection"; sel.mkdir(exist_ok=True)
    datasets, models, X, grid, W, fam = load()
    C = len(W); i_v1 = int(np.where(np.all(np.isclose(W, V1), 1))[0][0]); i_best = 0   # grid is sorted by J
    rng = np.random.default_rng(args.seed)
    # ---------- A + B: nested bootstrap
    J_in = np.empty((args.boot, C), np.float32); J_out_sel = np.empty(args.boot); J_in_sel = np.empty(args.boot)
    J_out_v1 = np.empty(args.boot); J_out_best = np.empty(args.boot); chosen = np.empty(args.boot, int); J_out_all = np.empty((args.boot, C), np.float32)
    for b in range(args.boot):
        ib, ob = {}, {}
        for d in datasets:
            n = X[d].shape[0]; draw = rng.integers(0, n, n); ib[d] = draw; mask = np.ones(n, bool); mask[np.unique(draw)] = False
            ob[d] = np.where(mask)[0] if mask.any() else np.array([rng.integers(0, n)])
        Jb = J_from_means(means_of(X, datasets, ib), W); J_in[b] = Jb
        c = int(np.argmax(Jb)); chosen[b] = c; J_in_sel[b] = Jb[c]
        Jo = J_from_means(means_of(X, datasets, ob), W); J_out_all[b] = Jo
        J_out_sel[b] = Jo[c]; J_out_v1[b] = Jo[i_v1]; J_out_best[b] = Jo[i_best]
    np.savez_compressed(sel / "nested_draws.npz", J_in=J_in, J_out=J_out_all, chosen=chosen, J_out_sel=J_out_sel, J_out_v1=J_out_v1, J_out_best=J_out_best)
    # plateau from in-bag draws (every candidate has the same resamples)
    Jm = J_in.mean(0); d_best = J_in[:, i_best][:, None] - J_in                       # B x C, positive = best ahead
    p_vs_best = (d_best <= 0).mean(0)                                                  # share of resamples where candidate >= best
    in_plateau = p_vs_best > 0.05
    practical = Jm >= Jm.max() - 0.02                                                  # within 0.02 of the best bootstrap-mean J
    plateau = pd.DataFrame({"rank_full": grid["rank"], **{c: grid[c] for c in WC}, "label": grid.label, "J_full": grid.J, "J_boot_mean": Jm,
                            "J_boot_sd": J_in.std(0), "J_boot_lo": np.percentile(J_in, 2.5, 0), "J_boot_hi": np.percentile(J_in, 97.5, 0),
                            "p_vs_best": p_vs_best, "in_plateau": in_plateau, "in_practical_plateau": practical, "times_selected": np.bincount(chosen, minlength=C),
                            "J_oob_mean": J_out_all.mean(0)})
    plateau.to_csv(sel / "plateau.csv", index=False)
    sel_counts = Counter(chosen.tolist()); top_sel = [{"weights": dict(zip(COMP, W[c].round(2).tolist())), "times": n, "share": n / args.boot} for c, n in sel_counts.most_common(10)]
    nested = {"B": args.boot, "n_candidates": C,
              "in_bag_J_of_selected_mean": float(J_in_sel.mean()), "out_of_bag_J_of_selected_mean": float(J_out_sel.mean()),
              "optimism_gap": float(J_in_sel.mean() - J_out_sel.mean()),
              "out_of_bag_J_v1_mean": float(J_out_v1.mean()), "out_of_bag_J_full_best_mean": float(J_out_best.mean()),
              "selected_vs_v1_out_of_bag": paired_objective_test(J_out_sel, J_out_v1),
              "full_best_vs_v1_out_of_bag": paired_objective_test(J_out_best, J_out_v1),
              "full_best_vs_v1_in_bag": paired_objective_test(J_in[:, i_best], J_in[:, i_v1]),
              "share_resamples_v1_in_top_5pct": float((np.argsort(np.argsort(-J_in, 1), 1)[:, i_v1] < 0.05 * C).mean()),
              "selected_weights_mean": dict(zip(COMP, W[chosen].mean(0).round(3).tolist())), "selected_weights_sd": dict(zip(COMP, W[chosen].std(0).round(3).tolist())),
              "n_distinct_selected": int(len(sel_counts)), "most_selected": top_sel,
              "plateau_size": int(in_plateau.sum()), "plateau_share": float(in_plateau.mean()), "v1_in_plateau": bool(in_plateau[i_v1]),
              "v1_p_vs_best": float(p_vs_best[i_v1]),
              "practical_plateau_size_within_0.02": int(practical.sum()), "v1_in_practical_plateau": bool(practical[i_v1]),
              "practical_plateau_weight_ranges": {c: [float(W[practical, k].min()), float(W[practical, k].max())] for k, c in enumerate(COMP)}, "plateau_weight_ranges": {c: [float(W[in_plateau, k].min()), float(W[in_plateau, k].max())] for k, c in enumerate(COMP)}}
    # ---------- C: LODO / LOFO
    allidx = {d: np.arange(X[d].shape[0]) for d in datasets}
    full_means = means_of(X, datasets, allidx)                                       # M x 4 x D

    def heldout_rows(groups, kind):
        rows = []
        for g, held in groups.items():
            rest = [d for d in datasets if d not in held]
            if len(rest) < 2: continue
            ri = [datasets.index(d) for d in rest]; hi = [datasets.index(d) for d in held]
            Jr = J_from_means(full_means[:, :, ri], W); c_lodo = int(np.argmax(Jr))
            for c_name, c in [("lodo_weights", c_lodo), ("full_best", i_best), ("v1", i_v1)]:
                S_rest = np.einsum("k,mkd->md", W[c], full_means[:, :, ri]); S_held = np.einsum("k,mkd->md", W[c], full_means[:, :, hi])
                Rc = borda_many(ranks_many(S_rest[None]))[0]; Rh = ranks_many(S_held[None])[0]          # M ; M x |held|
                taus = tau_b(np.moveaxis(Rh, 0, 1), Rc[None]).ravel()
                rows.append({"kind": kind, "held_out": g, "weights_from": c_name, **dict(zip(WC, W[c].round(2))), "J_rest": float(Jr[c]),
                             "tau_heldout_mean": float(taus.mean()), "n_heldout": len(held)})
        return pd.DataFrame(rows)
    lodo = heldout_rows({d: [d] for d in datasets}, "dataset"); lodo.to_csv(sel / "lodo.csv", index=False)
    fams = {}
    for d in datasets: fams.setdefault(fam.get(d, "OTHER"), []).append(d)
    lofo = heldout_rows(fams, "family") if len(fams) >= 2 else pd.DataFrame(); lofo.to_csv(sel / "lofo.csv", index=False)
    # ---------- D: per-family best
    per_family = {}
    for f, ds in fams.items():
        if len(ds) < 2: per_family[f] = {"datasets": ds, "note": "one dataset: J is trivially 1"}; continue
        fi = [datasets.index(d) for d in ds]; Jf = J_from_means(full_means[:, :, fi], W); c = int(np.argmax(Jf))
        per_family[f] = {"datasets": ds, "best_weights": dict(zip(COMP, W[c].round(2).tolist())), "J_family_best": float(Jf[c]),
                         "J_family_under_global_best": float(Jf[i_best]), "J_family_under_v1": float(Jf[i_v1]),
                         "L1_distance_to_global_best": float(np.abs(W[c] - W[i_best]).sum())}
    json.dump(per_family, open(sel / "per_family.json", "w"), indent=2)
    # ---------- E: sensitivity
    def neighbourhood(c):
        nb = np.where(np.abs(W - W[c]).sum(1) <= 0.10 + 1e-9)[0]; Jn = grid.J.to_numpy()[nb]
        return {"n_neighbours": int(len(nb) - 1), "J_centre": float(grid.J[c]), "J_min": float(Jn.min()), "J_max": float(Jn.max()), "J_mean": float(Jn.mean()),
                "flatness_range": float(Jn.max() - Jn.min()), "share_neighbours_better": float((Jn > grid.J[c]).mean())}
    sens = {"v1": neighbourhood(i_v1), "best": neighbourhood(i_best)}
    json.dump(sens, open(sel / "sensitivity.json", "w"), indent=2); json.dump(nested, open(sel / "nested.json", "w"), indent=2)
    # ---------- figures
    fig, ax = plt.subplots(figsize=(5.5, 3))
    ax.hist(J_in_sel, bins=30, alpha=0.6, color=BLUE, label="in-bag J of selected (optimistic)")
    ax.hist(J_out_sel, bins=30, alpha=0.6, color=GREEN, label="out-of-bag J of selected (honest)")
    ax.hist(J_out_v1, bins=30, alpha=0.6, color=ORANGE, label="out-of-bag J of v1")
    ax.set_xlabel("J"); ax.set_ylabel("resamples"); ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(sel / "fig_nested.png", dpi=200); fig.savefig(sel / "fig_nested.pdf"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.5, 3))
    order = np.argsort(-Jm); ax.fill_between(np.arange(C), plateau.J_boot_lo.to_numpy()[order], plateau.J_boot_hi.to_numpy()[order], color=GRAY, alpha=0.4, label="95 % bootstrap band")
    ax.plot(np.arange(C), Jm[order], color=BLUE, lw=1, label="bootstrap mean J"); ax.axvline(in_plateau.sum(), color=GREEN, ls=":", label=f"plateau ({int(in_plateau.sum())} weightings)")
    pos_v1 = int(np.where(order == i_v1)[0][0]); ax.scatter([pos_v1], [Jm[i_v1]], color=ORANGE, zorder=5, label="v1")
    ax.set_xlabel("weighting (sorted by bootstrap mean J)"); ax.set_ylabel("J"); ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(sel / "fig_plateau.png", dpi=200); fig.savefig(sel / "fig_plateau.pdf"); plt.close(fig)
    print(json.dumps({k: nested[k] for k in ["in_bag_J_of_selected_mean", "out_of_bag_J_of_selected_mean", "optimism_gap", "out_of_bag_J_v1_mean", "plateau_size", "v1_in_plateau", "v1_p_vs_best", "practical_plateau_size_within_0.02", "v1_in_practical_plateau"]}, indent=1))
    print(nested["selected_vs_v1_out_of_bag"]); print(lodo[lodo.weights_from == "lodo_weights"][["held_out", "tau_heldout_mean"]].to_string(index=False))


if __name__ == "__main__":
    main()
