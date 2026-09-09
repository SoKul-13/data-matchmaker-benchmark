#!/usr/bin/env python
"""
v3 step 2 - Eight aggregation views from the literature, and a grid search over how to mix them.

score_mix(model) = sum_v w_v * z(view_v)(model),   w on the simplex over the 8 views
Candidates: the 8 single-view corners + uniform + 100 random step-0.05 grid points (109).
Objective (papers 6, 7, 10 of the review):
   stability   = mean Kendall tau between the mixed ranking on 100 item-bootstrap resamples and on the full data
   transitivity= tau between the mixed ranking and the pairwise-majority (Copeland) ranking of per-dataset scores
   reference   = tau between the mixed ranking and the Kemeny consensus of the 8 single-view rankings
   J = 0.5 stability + 0.25 transitivity + 0.25 reference
Outputs: output/views.csv, output/grid_views.csv, output/best.json, output/leaderboard.md, output/fig_views.png/pdf
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pooling.rank_aggregation import consensus_ranking, kendall_tau, ranks_from_scores  # noqa: E402
from views import VIEWS, all_views, per_dataset_table, standardise  # noqa: E402

SEED, N_RANDOM, STEP, N_BOOT = 20260909, 100, 0.05, 100
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b"


def simplex_grid(K, step):
    u = int(round(1 / step)); out = []
    for cuts in itertools.combinations(range(u + K - 1), K - 1):
        prev, comp = -1, []
        for c in cuts:
            comp.append(c - prev - 1); prev = c
        comp.append(u + K - 2 - prev); out.append(comp)
    return np.asarray(out, float) / u


def main():
    out = ROOT / "output"
    items = pd.read_csv(out / "native_item_scores.csv"); baseline = json.load(open(out / "random_baseline.json"))
    V = all_views(items, baseline); Z = standardise(V); models = list(V.index)
    V.round(4).to_csv(out / "views.csv")
    print("views (raw):\n", V.round(3).to_string())
    # bootstrap views once
    rng = np.random.default_rng(SEED); Zb = []
    groups = {d: g for d, g in items.groupby("dataset")}
    for b in range(N_BOOT):
        parts = []
        for d, g in groups.items():
            uids = g.uid.unique(); pick = rng.choice(uids, len(uids), replace=True)
            parts.append(pd.concat([g[g.uid == u] for u in pick]))
        Zb.append(standardise(all_views(pd.concat(parts), baseline)).reindex(index=models).to_numpy())
        if b % 25 == 0:
            print(f"  bootstrap {b}/{N_BOOT}", flush=True)
    Zb = np.stack(Zb)                                        # (B, M, K)
    T = per_datasettable = per_dataset_table(items).reindex(index=models)
    copeland = consensus_ranking(T.to_numpy(), "copeland")
    view_ranks = np.stack([ranks_from_scores(Z[v].to_numpy()) for v in VIEWS], 1)   # (M, K)
    ref = consensus_ranking(-view_ranks, "kemeny")           # Kemeny consensus of the single-view rankings (higher score = better -> negate ranks)
    K = len(VIEWS); G = simplex_grid(K, STEP)
    W = np.vstack([np.eye(K), np.ones((1, K)) / K, G[rng.choice(len(G), N_RANDOM, replace=False)]])
    labels = [f"only_{v}" for v in VIEWS] + ["uniform"] + [f"random_{i:03d}" for i in range(N_RANDOM)]
    rows = []
    for lab, w in zip(labels, W):
        s = Z.to_numpy() @ w; r = ranks_from_scores(s)
        stab = np.mean([kendall_tau(-ranks_from_scores(Zb[b] @ w), -r) for b in range(N_BOOT)])
        rows.append({"label": lab, **{f"w_{v}": float(x) for v, x in zip(VIEWS, w)}, "stability": float(stab), "transitivity": kendall_tau(-r, -copeland), "reference": kendall_tau(-r, -ref),
                     "J": 0.5 * stab + 0.25 * kendall_tau(-r, -copeland) + 0.25 * kendall_tau(-r, -ref), **{f"rank_{m}": float(x) for m, x in zip(models, r)}})
    g = pd.DataFrame(rows).sort_values("J", ascending=False).reset_index(drop=True); g.insert(0, "rank", range(1, len(g) + 1)); g.to_csv(out / "grid_views.csv", index=False)
    best = g.iloc[0]; wb = best[[f"w_{v}" for v in VIEWS]].to_numpy(float); s = Z.to_numpy() @ wb; r = ranks_from_scores(s)
    boot_ranks = np.stack([ranks_from_scores(Zb[b] @ wb) for b in range(N_BOOT)])
    json.dump({"views": VIEWS, "n_candidates": int(len(W)), "best": {"label": best.label, "weights": dict(zip(VIEWS, wb.round(3).tolist())), "J": float(best.J), "stability": float(best.stability),
               "transitivity": float(best.transitivity), "reference": float(best.reference)}, "uniform_J": float(g[g.label == "uniform"].J.iloc[0]),
               "single_view_J": {v: float(g[g.label == f"only_{v}"].J.iloc[0]) for v in VIEWS}, "mixed_score": dict(zip(models, s.round(4).tolist())), "mixed_rank": dict(zip(models, r.tolist())),
               "rank_ci95_items": {m: [float(np.percentile(boot_ranks[:, i], 2.5)), float(np.percentile(boot_ranks[:, i], 97.5))] for i, m in enumerate(models)},
               "single_view_ranks": {v: dict(zip(models, ranks_from_scores(Z[v].to_numpy()).tolist())) for v in VIEWS}, "kemeny_reference_rank": dict(zip(models, ref.tolist()))},
              open(out / "best.json", "w"), indent=2)
    order = sorted(models, key=lambda m: r[models.index(m)])
    L = [f"# v3: literature aggregation views mixed by grid search ({len(W)} candidates; {N_BOOT} item bootstraps)\n", "## Views per model (raw values)\n", V.round(3).to_markdown(), "",
         "## Rank under each single view\n", pd.DataFrame({v: ranks_from_scores(Z[v].to_numpy()).astype(int) for v in VIEWS}, index=models).to_markdown(), "",
         "## Top candidates\n", "| rank | label | " + " | ".join(VIEWS) + " | stability | transitivity | reference | J |", "|---|---|" + "---|" * (K + 4)]
    for _, row in g.head(12).iterrows():
        L.append(f"| {row['rank']} | {row.label} | " + " | ".join(f"{row[f'w_{v}']:.2f}" for v in VIEWS) + f" | {row.stability:.3f} | {row.transitivity:.2f} | {row.reference:.2f} | {row.J:.3f} |")
    L += ["", "## Final leaderboard (best mix)\n", "| Model | mixed score | rank | 95% CI (items) | " + " | ".join(f"{v} rank" for v in VIEWS) + " |", "|---|---|---|---|" + "---|" * K]
    for m in order:
        i = models.index(m); L.append(f"| {m} | {s[i]:+.2f} | {r[i]:.0f} | [{np.percentile(boot_ranks[:, i], 2.5):.0f}, {np.percentile(boot_ranks[:, i], 97.5):.0f}] | " + " | ".join(f"{ranks_from_scores(Z[v].to_numpy())[i]:.0f}" for v in VIEWS) + " |")
    (out / "leaderboard.md").write_text("\n".join(L) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8), gridspec_kw={"width_ratios": [1, 1.2]}, constrained_layout=True)
    ax = axes[0]; ax.bar(g["rank"], g.J, color=GRAY, width=1, lw=0); ax.bar(g["rank"][:10], g.J[:10], color=BLUE, width=1, lw=0)
    ax.axhline(g[g.label == "uniform"].J.iloc[0], color=ORANGE, ls="--", lw=1); ax.text(len(g), g[g.label == "uniform"].J.iloc[0], "uniform mix", ha="right", va="bottom", fontsize=7, color=ORANGE)
    ax.set_xlabel("candidate mix (sorted)"); ax.set_ylabel("J"); ax.set_title("Grid search over view weights", fontsize=8, loc="left")
    ax = axes[1]; R = pd.DataFrame({v: ranks_from_scores(Z[v].to_numpy()) for v in VIEWS}, index=models).loc[order]
    im = ax.imshow(R.to_numpy(), cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#0d366b", "#2a78d6", "#cde2fb", "#fcfcfb"]), vmin=1, vmax=len(models), aspect="auto")
    ax.set_yticks(range(len(order))); ax.set_yticklabels(order); ax.set_xticks(range(K)); ax.set_xticklabels(VIEWS, rotation=60, ha="right", fontsize=7)
    for i in range(len(order)):
        for j in range(K):
            ax.text(j, i, f"{R.iloc[i, j]:.0f}", ha="center", va="center", fontsize=7, color="white" if R.iloc[i, j] <= 2 else INK)
    ax.grid(False); ax.set_title("Rank of each model under each view", fontsize=8, loc="left")
    fig.savefig(out / "fig_views.png", dpi=200); fig.savefig(out / "fig_views.pdf")
    print("\n".join(L[-8:]))


if __name__ == "__main__":
    main()
