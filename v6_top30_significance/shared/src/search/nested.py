"""
Version-independent selection validity for a set of candidate weightings over per-item component tensors.

  nested_selection(X, W, datasets, i_ref, out_dir, comp, boot, seed, ref_name)
      X: dict dataset -> (n_items x M x K) component tensor; W: (C x K) candidates (row i_ref = the reference weighting, e.g. v1
      or exact match); grid order is assumed sorted best-first on the full data (row 0 = full-data best).
      Nested item bootstrap (select in-bag, score out-of-bag), plateau (statistical and practical), selection instability.
  transfer(X, W, datasets, fam, i_ref, out_dir, comp)     leave-one-dataset-out and leave-one-family-out + per-family best weightings
  sensitivity(W, J, i_ref, out_dir, comp, step)            J over the one-step lattice neighbourhood of the reference and of the best
All J values are "mean Kendall tau-b of each dataset's ranking to the Borda pool" computed with search.fast_rank.J_many.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from search.fast_rank import J_many, borda_many, ranks_many, tau_b
from stats.significance import paired_objective_test

BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#3a9d5d"


def J_from_means(means: np.ndarray, W: np.ndarray) -> np.ndarray:
    return J_many(np.einsum("ck,mkd->cmd", W, means))["J"]


def means_of(X: Dict[str, np.ndarray], datasets: Sequence[str], idx_sets: Dict[str, np.ndarray]) -> np.ndarray:
    return np.stack([np.nanmean(X[d][idx_sets[d]], 0) for d in datasets], -1)


def nested_selection(X, W, datasets, i_ref, out_dir: Path, comp: Sequence[str], boot: int = 1000, seed: int = 0, ref_name: str = "reference",
                     practical_margin: float = 0.02) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True); C = len(W); i_best = 0; rng = np.random.default_rng(seed)
    J_in = np.empty((boot, C), np.float32); J_out_all = np.empty((boot, C), np.float32); chosen = np.empty(boot, int)
    for b in range(boot):
        ib, ob = {}, {}
        for d in datasets:
            n = X[d].shape[0]; draw = rng.integers(0, n, n); ib[d] = draw; mask = np.ones(n, bool); mask[np.unique(draw)] = False
            ob[d] = np.where(mask)[0] if mask.any() else np.array([rng.integers(0, n)])
        Jb = J_from_means(means_of(X, datasets, ib), W); J_in[b] = Jb; chosen[b] = int(np.argmax(Jb))
        J_out_all[b] = J_from_means(means_of(X, datasets, ob), W)
    J_in_sel = J_in[np.arange(boot), chosen]; J_out_sel = J_out_all[np.arange(boot), chosen]
    J_out_ref, J_out_best = J_out_all[:, i_ref], J_out_all[:, i_best]
    np.savez_compressed(out_dir / "nested_draws.npz", J_in=J_in, J_out=J_out_all, chosen=chosen, J_out_sel=J_out_sel, J_out_ref=J_out_ref, J_out_best=J_out_best)
    Jm = J_in.mean(0); p_vs_best = ((J_in[:, i_best][:, None] - J_in) <= 0).mean(0); in_plateau = p_vs_best > 0.05; practical = Jm >= Jm.max() - practical_margin
    plateau = pd.DataFrame({"rank_full": np.arange(1, C + 1), **{f"w_{c}": W[:, k] for k, c in enumerate(comp)}, "J_boot_mean": Jm, "J_boot_sd": J_in.std(0),
                            "J_boot_lo": np.percentile(J_in, 2.5, 0), "J_boot_hi": np.percentile(J_in, 97.5, 0), "p_vs_best": p_vs_best, "in_plateau": in_plateau,
                            "in_practical_plateau": practical, "times_selected": np.bincount(chosen, minlength=C), "J_oob_mean": J_out_all.mean(0)})
    plateau.to_csv(out_dir / "plateau.csv", index=False)
    sel_counts = Counter(chosen.tolist())
    nested = {"B": boot, "n_candidates": C, "reference": ref_name,
              "in_bag_J_of_selected_mean": float(J_in_sel.mean()), "out_of_bag_J_of_selected_mean": float(J_out_sel.mean()), "optimism_gap": float(J_in_sel.mean() - J_out_sel.mean()),
              "out_of_bag_J_ref_mean": float(J_out_ref.mean()), "out_of_bag_J_full_best_mean": float(J_out_best.mean()),
              "selected_vs_ref_out_of_bag": paired_objective_test(J_out_sel, J_out_ref), "full_best_vs_ref_out_of_bag": paired_objective_test(J_out_best, J_out_ref),
              "full_best_vs_ref_in_bag": paired_objective_test(J_in[:, i_best], J_in[:, i_ref]),
              "share_resamples_ref_in_top_5pct": float((np.argsort(np.argsort(-J_in, 1), 1)[:, i_ref] < 0.05 * C).mean()),
              "selected_weights_mean": dict(zip(comp, W[chosen].mean(0).round(3).tolist())), "selected_weights_sd": dict(zip(comp, W[chosen].std(0).round(3).tolist())),
              "n_distinct_selected": int(len(sel_counts)),
              "most_selected": [{"weights": dict(zip(comp, W[c].round(2).tolist())), "times": n, "share": n / boot} for c, n in sel_counts.most_common(10)],
              "plateau_size": int(in_plateau.sum()), "plateau_share": float(in_plateau.mean()), "ref_in_plateau": bool(in_plateau[i_ref]), "ref_p_vs_best": float(p_vs_best[i_ref]),
              "practical_plateau_size": int(practical.sum()), "practical_margin": practical_margin, "ref_in_practical_plateau": bool(practical[i_ref]),
              "practical_plateau_weight_ranges": {c: [float(W[practical, k].min()), float(W[practical, k].max())] for k, c in enumerate(comp)}}
    json.dump(nested, open(out_dir / "nested.json", "w"), indent=2)
    fig, ax = plt.subplots(figsize=(5.5, 3))
    ax.hist(J_in_sel, bins=30, alpha=0.6, color=BLUE, label="in-bag J of selected (optimistic)"); ax.hist(J_out_sel, bins=30, alpha=0.6, color=GREEN, label="out-of-bag J of selected (honest)")
    ax.hist(J_out_ref, bins=30, alpha=0.6, color=ORANGE, label=f"out-of-bag J of {ref_name}"); ax.set_xlabel("J"); ax.set_ylabel("resamples"); ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out_dir / "fig_nested.png", dpi=200); fig.savefig(out_dir / "fig_nested.pdf"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.5, 3)); order = np.argsort(-Jm)
    ax.fill_between(np.arange(C), plateau.J_boot_lo.to_numpy()[order], plateau.J_boot_hi.to_numpy()[order], color=GRAY, alpha=0.4, label="95 % bootstrap band")
    ax.plot(np.arange(C), Jm[order], color=BLUE, lw=1, label="bootstrap mean J"); ax.axvline(practical.sum(), color=GREEN, ls=":", label=f"practical plateau ({int(practical.sum())})")
    ax.scatter([int(np.where(order == i_ref)[0][0])], [Jm[i_ref]], color=ORANGE, zorder=5, label=ref_name); ax.set_xlabel("weighting (sorted by bootstrap mean J)"); ax.set_ylabel("J")
    ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False); fig.tight_layout(); fig.savefig(out_dir / "fig_plateau.png", dpi=200); fig.savefig(out_dir / "fig_plateau.pdf"); plt.close(fig)
    return nested


def transfer(X, W, datasets, fam, i_ref, out_dir: Path, comp: Sequence[str], ref_name: str = "reference") -> dict:
    out_dir.mkdir(parents=True, exist_ok=True); i_best = 0
    full_means = means_of(X, datasets, {d: np.arange(X[d].shape[0]) for d in datasets})
    WC = [f"w_{c}" for c in comp]

    def heldout_rows(groups, kind):
        rows = []
        for g, held in groups.items():
            rest = [d for d in datasets if d not in held]
            if len(rest) < 2:
                continue
            ri = [datasets.index(d) for d in rest]; hi = [datasets.index(d) for d in held]
            Jr = J_from_means(full_means[:, :, ri], W); c_h = int(np.argmax(Jr))
            for c_name, c in [("heldout_weights", c_h), ("full_best", i_best), (ref_name, i_ref)]:
                S_rest = np.einsum("k,mkd->md", W[c], full_means[:, :, ri]); S_held = np.einsum("k,mkd->md", W[c], full_means[:, :, hi])
                Rc = borda_many(ranks_many(S_rest[None]))[0]; Rh = ranks_many(S_held[None])[0]
                taus = tau_b(np.moveaxis(Rh, 0, 1), Rc[None]).ravel()
                rows.append({"kind": kind, "held_out": g, "weights_from": c_name, **dict(zip(WC, W[c].round(2))), "J_rest": float(Jr[c]), "tau_heldout_mean": float(taus.mean()), "n_heldout": len(held)})
        return pd.DataFrame(rows)
    lodo = heldout_rows({d: [d] for d in datasets}, "dataset"); lodo.to_csv(out_dir / "lodo.csv", index=False)
    fams: Dict[str, List[str]] = {}
    for d in datasets:
        fams.setdefault(fam.get(d, "OTHER"), []).append(d)
    lofo = heldout_rows(fams, "family") if len(fams) >= 2 else pd.DataFrame(); lofo.to_csv(out_dir / "lofo.csv", index=False)
    per_family = {}
    for f, ds in fams.items():
        if len(ds) < 2:
            per_family[f] = {"datasets": ds, "note": "one dataset: J is trivially 1"}; continue
        fi = [datasets.index(d) for d in ds]; Jf = J_from_means(full_means[:, :, fi], W); c = int(np.argmax(Jf))
        per_family[f] = {"datasets": ds, "best_weights": dict(zip(comp, W[c].round(2).tolist())), "J_family_best": float(Jf[c]), "J_family_under_global_best": float(Jf[i_best]),
                         f"J_family_under_{ref_name}": float(Jf[i_ref]), "L1_distance_to_global_best": float(np.abs(W[c] - W[i_best]).sum())}
    json.dump(per_family, open(out_dir / "per_family.json", "w"), indent=2)
    return {"lodo": lodo, "lofo": lofo, "per_family": per_family}


def sensitivity(W, J, i_ref, out_dir: Path, step: float = 0.05, ref_name: str = "reference") -> dict:
    def nb(c):
        idx = np.where(np.abs(W - W[c]).sum(1) <= 2 * step + 1e-9)[0]; Jn = J[idx]
        return {"n_neighbours": int(len(idx) - 1), "J_centre": float(J[c]), "J_min": float(Jn.min()), "J_max": float(Jn.max()), "J_mean": float(Jn.mean()),
                "flatness_range": float(Jn.max() - Jn.min()), "share_neighbours_better": float((Jn > J[c]).mean())}
    out = {ref_name: nb(i_ref), "best": nb(0)}; json.dump(out, open(out_dir / "sensitivity.json", "w"), indent=2); return out
