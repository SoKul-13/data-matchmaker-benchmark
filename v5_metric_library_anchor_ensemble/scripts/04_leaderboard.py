#!/usr/bin/env python
"""
v3 step 4 - Score real answers with the ensemble metric and pool across datasets.

Per (model, item): score = mean over the 100 best weightings of  sum_k w_k * metric_k  (spread = ensemble uncertainty).
Per (model, dataset): mean score.  Common score = mean of per-dataset z-scores (equal dataset weights); Borda pooled
rank (headline), Kemeny / Copeland / RRF / mean-score as checks; 1,000 item bootstraps; native-metric ranking beside.
Outputs: output/leaderboard.md, output/leaderboard.json, output/item_scores.csv, output/fig_leaderboard.png/pdf
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pooling.rank_aggregation import RULES, bootstrap_consensus, consensus_ranking, dataset_agreement, kendall_tau, pairwise_dataset_tau  # noqa: E402

BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b"
DS = {"officeqa": "OfficeQA", "finqa": "FinQA", "tat_qa": "TAT-QA", "tab_fact": "TabFact", "financebench": "FinanceBench", "fetaqa": "FeTaQA",
      "wikitablequestions": "WTQ", "hitab": "HiTab", "abt_buy": "Abt-Buy", "amazon_google": "Amazon-Google", "dblp_scholar": "DBLP-Scholar",
      "walmart_amazon": "Walmart-Amazon", "wdc_products": "WDC", "tpcdi_cells": "TPC-DI"}


def main():
    out = ROOT / "output"
    ens = json.load(open(out / "ensemble.json")); cols = ens["selected_idx"]; Wtop = np.array(ens["top_weightings"])
    M = np.load(out / "matrix_models.npz")["M"]; im = pd.read_csv(out / "index_models.csv")
    from calibration.grid import gated_scores
    S_all = gated_scores(M[:, cols], M[:, ens["hedge_col"]], Wtop)   # (pairs, 100)
    im["score"] = S_all.mean(1); im["score_lo"] = S_all.min(1); im["score_hi"] = S_all.max(1)
    im.to_csv(out / "item_scores.csv", index=False)
    models, datasets = sorted(im.model.unique()), sorted(im.dataset.unique())
    piv = im.pivot_table(index="model", columns="dataset", values="score").reindex(index=models, columns=datasets)
    nat = im.pivot_table(index="model", columns="dataset", values="native_value").reindex(index=models, columns=datasets)
    S = piv.to_numpy()
    z = (piv - piv.mean(0)) / (piv.std(0) + 1e-9)
    common = z.mean(1); common_raw = piv.mean(1)
    ranks = {r: consensus_ranking(S, r) for r in RULES}
    nat_rank = consensus_ranking(nat.to_numpy(), "borda")
    items = [im[im.dataset == d].pivot_table(index="uid", columns="model", values="score").reindex(columns=models).to_numpy() for d in datasets]
    bs = bootstrap_consensus(items, "borda", n_boot=1000, seed=0)
    # ensemble-weighting uncertainty of the pooled rank: rank under each of the 100 weightings
    rank_by_w = np.stack([consensus_ranking(im.assign(s=S_all[:, b]).pivot_table(index="model", columns="dataset", values="s").reindex(index=models, columns=datasets).to_numpy(), "borda") for b in range(Wtop.shape[0])])
    agree = dataset_agreement(S, ranks["borda"]); T = pairwise_dataset_tau(S)
    order = sorted(models, key=lambda m: ranks["borda"][models.index(m)])
    res = {"models": models, "datasets": datasets, "per_dataset": piv.round(4).to_dict(orient="index"), "native_per_dataset": nat.round(4).to_dict(orient="index"),
           "common_score_z": common.round(4).to_dict(), "common_score_raw": common_raw.round(4).to_dict(),
           "pooled_ranks": {r: {m: float(x) for m, x in zip(models, ranks[r])} for r in RULES},
           "native_borda": {m: float(x) for m, x in zip(models, nat_rank)},
           "bootstrap_items": {m: {"mean": float(bs["rank_mean"][i]), "ci95": [float(bs["rank_ci"][0, i]), float(bs["rank_ci"][1, i])]} for i, m in enumerate(models)},
           "rank_over_weightings": {m: {"min": float(rank_by_w[:, i].min()), "max": float(rank_by_w[:, i].max()), "mode_share": float((rank_by_w[:, i] == ranks['borda'][i]).mean())} for i, m in enumerate(models)},
           "dataset_agreement": {d: float(a) for d, a in zip(datasets, agree)}, "mean_pairwise_dataset_tau": float(np.mean(T[np.triu_indices(len(datasets), 1)])),
           "rule_agreement": {a: {b: kendall_tau(-ranks[a], -ranks[b]) for b in RULES} for a in RULES}, "tau_vs_native": kendall_tau(-ranks["borda"], -nat_rank)}
    json.dump(res, open(out / "leaderboard.json", "w"), indent=2)
    L = [f"# v3 leaderboard: ensemble metric ({len(cols)} selected metrics x {Wtop.shape[0]} best weightings), {len(models)} models, {len(datasets)} datasets\n",
         "| Model | " + " | ".join(DS.get(d, d) for d in datasets) + " | Common (z-mean) | Borda | Kemeny | 95% CI (items) | Rank range over 100 weightings | Native Borda |",
         "|---|" + "---|" * (len(datasets) + 6)]
    for m in order:
        i = models.index(m); ci = res["bootstrap_items"][m]["ci95"]; rw = res["rank_over_weightings"][m]
        L.append(f"| {m} | " + " | ".join(f"{piv.loc[m, d]:.2f}" for d in datasets) + f" | {common[m]:+.2f} | {ranks['borda'][i]:.0f} | {ranks['kemeny'][i]:.0f} | [{ci[0]:.0f}, {ci[1]:.0f}] | {rw['min']:.0f}–{rw['max']:.0f} | {nat_rank[i]:.0f} |")
    L += ["", "Dataset agreement with pooled rank (tau): " + ", ".join(f"{DS.get(d, d)} {a:.2f}" for d, a in zip(datasets, agree)),
          f"Mean pairwise dataset tau: {res['mean_pairwise_dataset_tau']:.2f}; pooled vs native-metric pooled rank: tau {res['tau_vs_native']:.2f}", "",
          "Rule agreement (tau):", pd.DataFrame(res["rule_agreement"]).round(2).to_markdown()]
    (out / "leaderboard.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw={"width_ratios": [1.1, 1.4]}, constrained_layout=True)
    ax = axes[0]; yp = np.arange(len(order))[::-1]; rk = piv.rank(ascending=False)
    for k, m in enumerate(order):
        i = models.index(m)
        ax.scatter(rk.loc[m].to_numpy(), np.full(len(datasets), yp[k]) + np.random.default_rng(k).uniform(-0.18, 0.18, len(datasets)), s=10, color=GRAY, lw=0, zorder=2)
        lo, hi = res["bootstrap_items"][m]["ci95"]; ax.plot([lo, hi], [yp[k], yp[k]], color=BLUE, lw=2.2, solid_capstyle="round", zorder=3)
        ax.scatter([bs["rank_mean"][i]], [yp[k]], s=36, color=BLUE, zorder=4, edgecolor="white", lw=0.6)
        ax.scatter([nat_rank[i]], [yp[k]], s=28, marker="D", color=ORANGE, zorder=4, edgecolor="white", lw=0.5)
    ax.set_yticks(yp); ax.set_yticklabels(order); ax.set_xlabel("rank (1 = best)"); ax.set_xlim(0.5, len(order) + 0.5)
    ax.set_title("Pooled Borda rank, 95% item-bootstrap CI (blue);\nnative-metric pooled rank (orange); per-dataset ranks (grey)", fontsize=7.5, loc="left")
    ax = axes[1]; cmap = matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#fcfcfb", "#6da7ec", "#2a78d6", "#0d366b"])
    imh = ax.imshow(piv.loc[order].to_numpy(), cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_yticks(range(len(order))); ax.set_yticklabels([]); ax.set_xticks(range(len(datasets))); ax.set_xticklabels([DS.get(d, d) for d in datasets], rotation=60, ha="right", fontsize=7)
    for i in range(len(order)):
        for j in range(len(datasets)):
            v = piv.loc[order[i], datasets[j]]; ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6, color="white" if v > 0.55 else INK)
    ax.grid(False); ax.set_title("Ensemble metric per dataset", fontsize=7.5, loc="left"); fig.colorbar(imh, ax=ax, fraction=0.04, pad=0.02)
    fig.savefig(out / "fig_leaderboard.png", dpi=200); fig.savefig(out / "fig_leaderboard.pdf")
    print("\n".join(L[:8]))


if __name__ == "__main__":
    main()
