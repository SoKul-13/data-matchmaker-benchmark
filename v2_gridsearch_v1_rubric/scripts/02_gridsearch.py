#!/usr/bin/env python
"""
v2 step 2 - Grid search over the four v1 weights.

Candidate weightings: 100 points drawn (fixed seed) from the step-0.05 simplex grid over (F1, decay, precision, recall),
plus the original v1 point (0.35, 0.35, 0.15, 0.15) and the four single-metric corners, so 105 in total.
For each weighting w:   R_w(answer) = w1*F1 + w2*decay + w3*precision + w4*recall
   -> mean per (model, dataset) -> rank models inside each dataset -> Borda-pool the rankings
   objective J(w) = mean over datasets of Kendall tau(dataset ranking, pooled ranking)     [agreement among datasets]
   also reported: tau_native = mean over datasets of tau(R_w ranking, native-metric ranking)  [fidelity to the datasets' own metrics]
                  scale dispersion, and a 200-resample item bootstrap of J for the top 5, v1's point and the worst.
Outputs: output/grid.csv, output/best.json, output/leaderboard.md, output/fig_grid.png/pdf
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
from pooling.rank_aggregation import RULES, bootstrap_consensus, consensus_ranking, dataset_agreement, kendall_tau, pairwise_dataset_tau, ranks_from_scores  # noqa: E402

COMP = ["f1", "decay", "precision", "recall"]
V1 = np.array([0.35, 0.35, 0.15, 0.15])
SEED, N_RANDOM, STEP = 20260909, 100, 0.05
BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b"


def simplex_grid(K, step):
    u = int(round(1 / step)); out = []
    for cuts in itertools.combinations(range(u + K - 1), K - 1):
        prev, comp = -1, []
        for c in cuts:
            comp.append(c - prev - 1); prev = c
        comp.append(u + K - 2 - prev); out.append(comp)
    return np.asarray(out, float) / u


def tables(df, w):
    s = df[COMP].to_numpy() @ w
    d = df.assign(S=s)
    piv = d.pivot_table(index="model", columns="dataset", values="S", aggfunc="mean")
    items = [d[d.dataset == c].pivot_table(index="uid", columns="model", values="S").reindex(columns=piv.index).to_numpy() for c in piv.columns]
    return piv, items


def evaluate(piv, nat):
    S = piv.to_numpy(); R = consensus_ranking(S, "borda")
    agree = dataset_agreement(S, R)
    tau_nat = np.mean([kendall_tau(-ranks_from_scores(S[:, j]), -ranks_from_scores(nat.to_numpy()[:, j])) for j in range(S.shape[1])])
    C = S - S.mean(0, keepdims=True)
    return {"J": float(np.mean(agree)), "tau_native": float(tau_nat), "min_agree": float(agree.min()),
            "pairwise_tau": float(np.mean(pairwise_dataset_tau(S)[np.triu_indices(S.shape[1], 1)])), "dispersion": float(np.mean(C.std(1)) / (C.mean(1).std() + 1e-9))}


def boot_J(items, n=200, seed=0):
    rng = np.random.default_rng(seed); vals = []
    for _ in range(n):
        S = np.stack([X[rng.integers(0, X.shape[0], X.shape[0])].mean(0) for X in items], 1)
        vals.append(float(np.mean(dataset_agreement(S, consensus_ranking(S, "borda")))))
    return float(np.mean(vals)), float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def main():
    out = ROOT / "output"
    df = pd.read_csv(out / "components_v1.csv")
    nat = df.pivot_table(index="model", columns="dataset", values="native_value", aggfunc="mean")
    rng = np.random.default_rng(SEED)
    G = simplex_grid(4, STEP)
    W = np.vstack([V1, np.eye(4), G[rng.choice(len(G), N_RANDOM, replace=False)]])
    labels = ["v1_original"] + [f"only_{c}" for c in COMP] + [f"random_{i:03d}" for i in range(N_RANDOM)]
    rows = []
    for lab, w in zip(labels, W):
        piv, _ = tables(df, w); rows.append({"label": lab, **{f"w_{c}": float(x) for c, x in zip(COMP, w)}, **evaluate(piv, nat)})
    g = pd.DataFrame(rows).sort_values(["J", "tau_native"], ascending=False).reset_index(drop=True); g.insert(0, "rank", range(1, len(g) + 1))
    for r in list(range(5)) + [int(g.index[g.label == "v1_original"][0]), len(g) - 1]:
        w = g.loc[r, [f"w_{c}" for c in COMP]].to_numpy(float); _, items = tables(df, w)
        g.loc[r, ["J_boot", "J_lo", "J_hi"]] = boot_J(items)
    g.to_csv(out / "grid.csv", index=False)
    best = g.iloc[0]; wb = best[[f"w_{c}" for c in COMP]].to_numpy(float)
    v1row = g[g.label == "v1_original"].iloc[0]
    piv, items = tables(df, wb); S = piv.to_numpy(); models, datasets = list(piv.index), list(piv.columns)
    ranks = {r: consensus_ranking(S, r) for r in RULES}; bs = bootstrap_consensus(items, "borda", 1000)
    piv1, _ = tables(df, V1); r1 = consensus_ranking(piv1.to_numpy(), "borda"); rn = consensus_ranking(nat[datasets].to_numpy(), "borda")
    json.dump({"components": COMP, "n_candidates": int(len(W)), "best": {"label": best.label, "weights": dict(zip(COMP, wb.round(3).tolist())), "J": float(best.J), "J_ci95": [float(best.J_lo), float(best.J_hi)], "tau_native": float(best.tau_native)},
               "v1_original": {"weights": dict(zip(COMP, V1.tolist())), "J": float(v1row.J), "J_ci95": [float(v1row.J_lo), float(v1row.J_hi)], "tau_native": float(v1row.tau_native), "rank_among_candidates": int(v1row["rank"])},
               "n_beating_v1": int((g.J > v1row.J).sum()), "pooled_ranks_best": {m: float(x) for m, x in zip(models, ranks["borda"])}, "pooled_ranks_v1": {m: float(x) for m, x in zip(models, r1)},
               "pooled_ranks_native": {m: float(x) for m, x in zip(models, rn)}, "tau_best_vs_v1": kendall_tau(-ranks["borda"], -r1), "tau_best_vs_native": kendall_tau(-ranks["borda"], -rn),
               "bootstrap_rank_ci": {m: [float(bs["rank_ci"][0, i]), float(bs["rank_ci"][1, i])] for i, m in enumerate(models)}}, open(out / "best.json", "w"), indent=2)
    order = sorted(models, key=lambda m: ranks["borda"][models.index(m)])
    L = [f"# v2: grid search over the v1 rubric weights ({len(W)} candidates: v1 point + 4 corners + {N_RANDOM} random grid points, step {STEP})\n",
         "| rank | label | F1 | decay | precision | recall | J (mean tau to pooled) | tau to native | J 95% CI |", "|---|---|---|---|---|---|---|---|---|"]
    for _, r in g.head(10).iterrows():
        L.append(f"| {r['rank']} | {r.label} | {r.w_f1:.2f} | {r.w_decay:.2f} | {r.w_precision:.2f} | {r.w_recall:.2f} | {r.J:.3f} | {r.tau_native:.3f} | " + (f"[{r.J_lo:.2f}, {r.J_hi:.2f}]" if not np.isnan(r.J_lo) else "") + " |")
    L += [f"| {v1row['rank']} | **v1_original** | 0.35 | 0.35 | 0.15 | 0.15 | {v1row.J:.3f} | {v1row.tau_native:.3f} | [{v1row.J_lo:.2f}, {v1row.J_hi:.2f}] |", "",
          f"{int((g.J > v1row.J).sum())} of {len(W) - 1} other candidates beat the v1 weights on J; the best beats v1 by {best.J - v1row.J:+.3f}, inside the bootstrap interval.", "",
          "## Leaderboard under the best weights\n", "| Model | " + " | ".join(datasets) + " | Borda | Kemeny | 95% CI (items) | v1-weights Borda | native Borda |", "|---|" + "---|" * (len(datasets) + 5)]
    for m in order:
        i = models.index(m); L.append(f"| {m} | " + " | ".join(f"{piv.loc[m, d]:.2f}" for d in datasets) + f" | {ranks['borda'][i]:.0f} | {ranks['kemeny'][i]:.0f} | [{bs['rank_ci'][0, i]:.0f}, {bs['rank_ci'][1, i]:.0f}] | {r1[i]:.0f} | {rn[i]:.0f} |")
    (out / "leaderboard.md").write_text("\n".join(L) + "\n")
    fig, ax = plt.subplots(figsize=(4.2, 2.6), constrained_layout=True)
    ax.bar(g["rank"], g.J, color=GRAY, width=1, lw=0); ax.bar(g["rank"][:10], g.J[:10], color=BLUE, width=1, lw=0)
    ax.axhline(v1row.J, color=ORANGE, ls="--", lw=1); ax.text(len(g), v1row.J, "v1 weights", ha="right", va="bottom", fontsize=7, color=ORANGE)
    ax.set_xlabel("candidate weighting (sorted)"); ax.set_ylabel("J"); ax.set_title("Grid search over v1's four weights", fontsize=8, loc="left")
    fig.savefig(out / "fig_grid.png", dpi=200); fig.savefig(out / "fig_grid.pdf")
    print("\n".join(L[:16]))


if __name__ == "__main__":
    main()
