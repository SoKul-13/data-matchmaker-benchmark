#!/usr/bin/env python
"""
Step 3 - Common score and pooled leaderboard under the calibrated weights.

For every model: per-dataset composite score, the COMMON SCORE (mean over datasets, and the
difficulty-adjusted z-mean), and the pooled rank under several ensemble rules (mean score,
mean-z, mean rank, Borda, Copeland, Kemeny-Young, RRF) with bootstrap intervals over items.

Outputs (output/rs/): leaderboard.md, pooled_ranking.json, fig_leaderboard.png/pdf,
                      paper/tables/*.tex, paper/numbers.tex
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
from pooling.rank_aggregation import (RULES, bootstrap_consensus, consensus_ranking, dataset_agreement,  # noqa: E402
                                      kendall_tau, pairwise_dataset_tau, ranks_from_scores)

BLUE, ORANGE, GRAY, INK = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b"
DS = {"officeqa": "OfficeQA", "finqa": "FinQA", "tat_qa": "TAT-QA", "tab_fact": "TabFact", "financebench": "FinanceBench",
      "fetaqa": "FeTaQA", "wikitablequestions": "WTQ"}
TAB = ROOT / "paper" / "tables"
TAB.mkdir(parents=True, exist_ok=True)


def tex_table(name, header, rows, caption, label, align=None, wide=False, size="\\small", resize=False):
    align = align or "l" + "r" * (len(header) - 1)
    env = "table*" if wide else "table"
    L = [f"\\begin{{{env}}}[t]", "\\centering", size, f"\\caption{{{caption}}}", f"\\label{{{label}}}",
         "\\resizebox{\\textwidth}{!}{%" if resize else "", f"\\begin{{tabular}}{{{align}}}", "\\toprule",
         " & ".join(header) + " \\\\", "\\midrule"] + [" & ".join(str(x) for x in r) + " \\\\" for r in rows] + \
        ["\\bottomrule", "\\end{tabular}", "}" if resize else "", f"\\end{{{env}}}"]
    (TAB / f"{name}.tex").write_text("\n".join(L), encoding="utf-8")


def esc(s):
    return str(s).replace("_", "\\_").replace("%", "\\%")


def main():
    out = ROOT / "output" / "rs"
    z = np.load(out / "components.npz")
    M = z["M"][:, :K]
    idx = pd.read_csv(out / "index.csv")
    best = json.load(open(out / "best_weights.json"))
    w = np.array([best["weights"][n] for n in COMPONENT_NAMES])
    rs = pd.read_csv(out / "weights_random_search.csv")
    base = pd.read_csv(out / "baselines.csv")
    lodo = pd.read_csv(out / "lodo.csv")
    datasets = sorted(idx.dataset.unique())
    df = idx.assign(S=M @ w)
    piv = df.pivot_table(index="model", columns="dataset", values="S", aggfunc="mean")[datasets]
    models = list(piv.index)
    S = piv.to_numpy()
    items = [df[df.dataset == d].pivot_table(index="uid", columns="model", values="S").reindex(columns=models).to_numpy() for d in datasets]
    # common scores
    common = piv.mean(1)
    zmean = ((piv - piv.mean(0)) / (piv.std(0) + 1e-9)).mean(1)
    ranks = {rule: consensus_ranking(S, rule) for rule in RULES}
    bs = bootstrap_consensus(items, "borda", n_boot=1000, seed=0)
    agree = {rule: dataset_agreement(S, ranks[rule]) for rule in RULES}
    T = pairwise_dataset_tau(S)
    # native reference
    nat_piv = idx.assign(N=[z["M"][i, list(z["columns"]).index(m)] if m in list(z["columns"]) else z["M"][i, 0]
                            for i, m in enumerate(idx.native_metric)]).pivot_table(index="model", columns="dataset", values="N")[datasets]
    nat_rank = consensus_ranking(nat_piv.to_numpy(), "borda")
    em_piv = idx.assign(E=M @ PRESET_WEIGHTS["em_only"].get("numeric")).pivot_table(index="model", columns="dataset", values="E")[datasets]
    em_rank = consensus_ranking(em_piv.to_numpy(), "borda")

    order = sorted(models, key=lambda m: ranks["borda"][models.index(m)])
    res = {"weights": best["weights"], "datasets": datasets, "models": models,
           "per_dataset_scores": piv.round(4).to_dict(orient="index"),
           "common_score_mean": common.round(4).to_dict(), "common_score_zmean": zmean.round(4).to_dict(),
           "pooled_ranks": {rule: {m: float(r) for m, r in zip(models, ranks[rule])} for rule in RULES},
           "bootstrap_borda": {"rank_mean": {m: float(x) for m, x in zip(models, bs["rank_mean"])},
                               "rank_ci95": {m: [float(bs["rank_ci"][0, i]), float(bs["rank_ci"][1, i])] for i, m in enumerate(models)},
                               "p_rank": {m: bs["p_rank"][i].round(3).tolist() for i, m in enumerate(models)}},
           "dataset_agreement_with_pooled": {rule: {d: float(a) for d, a in zip(datasets, agree[rule])} for rule in RULES},
           "pairwise_dataset_tau": pd.DataFrame(T, index=datasets, columns=datasets).round(3).to_dict(),
           "rule_agreement_tau": {a: {b: kendall_tau(-ranks[a], -ranks[b]) for b in RULES} for a in RULES},
           "tau_vs_native_borda": kendall_tau(-ranks["borda"], -nat_rank), "tau_vs_em_borda": kendall_tau(-ranks["borda"], -em_rank)}
    json.dump(res, open(out / "pooled_ranking.json", "w"), indent=2)

    # ---- markdown leaderboard
    L = ["# Common score and pooled leaderboard (calibrated weights, 7 datasets x 40 items)\n",
         "Weights: " + ", ".join(f"{n} {v:.2f}" for n, v in best["weights"].items() if v > 0) + f" (J = {best['objective']:.3f})\n",
         "| Model | " + " | ".join(DS[d] for d in datasets) + " | Common (mean) | Common (z-mean) | Borda | Kemeny | RRF | 95% CI (Borda rank) | Native-metric Borda |",
         "|---|" + "---|" * (len(datasets) + 7)]
    for m in order:
        i = models.index(m)
        ci = res["bootstrap_borda"]["rank_ci95"][m]
        L.append(f"| {m} | " + " | ".join(f"{piv.loc[m, d]:.2f}" for d in datasets) + f" | {common[m]:.3f} | {zmean[m]:+.2f} | "
                 f"{ranks['borda'][i]:.0f} | {ranks['kemeny'][i]:.0f} | {ranks['rrf'][i]:.0f} | [{ci[0]:.0f}, {ci[1]:.0f}] | {nat_rank[i]:.0f} |")
    L += ["", "## Agreement of each dataset's ranking with the pooled (Borda) ranking (Kendall tau)", "",
          "| " + " | ".join(DS[d] for d in datasets) + " |", "|" + "---|" * len(datasets),
          "| " + " | ".join(f"{agree['borda'][j]:.2f}" for j in range(len(datasets))) + " |", "",
          "## Agreement between pooling rules (Kendall tau of consensus rankings)", "",
          pd.DataFrame(res["rule_agreement_tau"]).round(2).to_markdown(), "",
          f"Pooled (Borda) ranking vs. native-metric Borda ranking: tau = {res['tau_vs_native_borda']:.2f}; vs. EM-only Borda: tau = {res['tau_vs_em_borda']:.2f}."]
    (out / "leaderboard.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- figure
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.2, 1]}, constrained_layout=True)
    ax = axes[0]
    yp = np.arange(len(order))[::-1]
    rk = piv.rank(ascending=False)
    for k, m in enumerate(order):
        i = models.index(m)
        ax.scatter(rk.loc[m].to_numpy(), np.full(len(datasets), yp[k]) + np.random.default_rng(k).uniform(-0.18, 0.18, len(datasets)), s=10, color=GRAY, lw=0, zorder=2)
        lo, hi = res["bootstrap_borda"]["rank_ci95"][m]
        ax.plot([lo, hi], [yp[k], yp[k]], color=BLUE, lw=2.2, solid_capstyle="round", zorder=3)
        ax.scatter([bs["rank_mean"][i]], [yp[k]], s=36, color=BLUE, zorder=4, edgecolor="white", lw=0.6)
        ax.scatter([em_rank[i]], [yp[k]], s=28, marker="D", color=ORANGE, zorder=4, edgecolor="white", lw=0.5)
    ax.set_yticks(yp); ax.set_yticklabels(order); ax.set_xlabel("rank (1 = best)"); ax.set_xlim(0.5, len(order) + 0.5)
    ax.set_title("Pooled Borda rank, 95% bootstrap CI (blue); EM-only pooled rank (orange);\nper-dataset ranks (grey)", fontsize=7.5, loc="left")
    ax = axes[1]
    im = ax.imshow(piv.loc[order].to_numpy(), cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#fcfcfb", "#6da7ec", "#2a78d6", "#0d366b"]), vmin=0, vmax=1, aspect="auto")
    ax.set_yticks(range(len(order))); ax.set_yticklabels([]); ax.set_xticks(range(len(datasets))); ax.set_xticklabels([DS[d] for d in datasets], rotation=60, ha="right")
    for i in range(len(order)):
        for j in range(len(datasets)):
            v = piv.loc[order[i], datasets[j]]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6, color="white" if v > 0.55 else INK)
    ax.grid(False); ax.set_title("Calibrated composite per dataset", fontsize=7.5, loc="left")
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    fig.savefig(out / "fig_leaderboard.png", dpi=200); fig.savefig(out / "fig_leaderboard.pdf")

    # ---- LaTeX tables
    tex_table("tab_leaderboard", ["Model"] + [DS[d] for d in datasets] + ["Common", "$z$-mean", "Borda", "Kemeny", "RRF", "95\\% CI", "Native"],
              [[esc(m)] + [f"{piv.loc[m, d]:.2f}" for d in datasets] + [f"{common[m]:.3f}", f"{zmean[m]:+.2f}", f"{ranks['borda'][models.index(m)]:.0f}",
               f"{ranks['kemeny'][models.index(m)]:.0f}", f"{ranks['rrf'][models.index(m)]:.0f}",
               f"[{res['bootstrap_borda']['rank_ci95'][m][0]:.0f}, {res['bootstrap_borda']['rank_ci95'][m][1]:.0f}]", f"{nat_rank[models.index(m)]:.0f}"] for m in order],
              "Per-dataset calibrated composite, common score (mean and difficulty-adjusted $z$-mean) and pooled ranks; CI from 1{,}000 item bootstraps.",
              "tab:leaderboard", wide=True, resize=True)
    top = rs.head(10)
    tex_table("tab_rs_top10", ["\\#", "$J$", "boot 95\\% CI", "pairwise $\\tau$", "disp."] + [esc(n) for n in COMPONENT_NAMES],
              [[int(r["rank"]), f"{r.J_tau_to_pooled:.3f}", (f"[{r.J_boot_lo:.2f}, {r.J_boot_hi:.2f}]" if not np.isnan(r.J_boot_lo) else "--"),
                f"{r.mean_pairwise_tau:.3f}", f"{r.scale_dispersion:.2f}"] + [f"{r[f'w_{n}']:.2f}" if r[f"w_{n}"] > 0 else "--" for n in COMPONENT_NAMES] for _, r in top.iterrows()],
              "Top-10 of the 100 random weight combinations (grid step 0.05). $J$ = mean Kendall $\\tau$ between each dataset's model ranking and the pooled Borda ranking.",
              "tab:rs", wide=True, size="\\footnotesize", resize=True)
    tex_table("tab_baselines", ["Weights", "$J$", "pairwise $\\tau$", "dispersion"],
              [[esc(r.baseline), f"{r.J_tau_to_pooled:.3f}", f"{r.mean_pairwise_tau:.3f}", f"{r.scale_dispersion:.2f}"] for _, r in base.iterrows()],
              "Fixed baselines vs.\\ the random-search optimum under the same objective.", "tab:baselines")
    tex_table("tab_lodo", ["Held-out", "$J$ w/o", "$\\tau$ held-out (LODO w)", "$\\tau$ held-out (full w)", "$L_1$ shift"],
              [[DS[r.held_out], f"{r.J_without:.3f}", f"{r.tau_heldout_lodo_weights:.2f}", f"{r.tau_heldout_full_weights:.2f}", f"{r.l1_shift:.1f}"] for _, r in lodo.iterrows()],
              "Leave-one-dataset-out: best combination chosen without the held-out dataset, then agreement of the held-out dataset's ranking with the pooled ranking of the rest.",
              "tab:lodo", size="\\footnotesize", wide=True)
    tex_table("tab_rules", ["Rule"] + [esc(r) for r in RULES], [[esc(a)] + [f"{res['rule_agreement_tau'][a][b]:.2f}" for b in RULES] for a in RULES],
              "Kendall $\\tau$ between the consensus rankings produced by different pooling rules.", "tab:rules", size="\\footnotesize")
    tex_table("tab_dsagree", [DS[d] for d in datasets], [[f"{agree['borda'][j]:.2f}" for j in range(len(datasets))]],
              "Kendall $\\tau$ between each dataset's ranking and the pooled Borda ranking under the calibrated weights.", "tab:dsagree")
    # numbers.tex
    b = {r.baseline: r for _, r in base.iterrows()}
    mac = {"nModels": len(models), "nDatasets": len(datasets), "Jbest": f"{best['objective']:.3f}", "JbootLo": f"{best['bootstrap_J'][0]:.2f}",
           "JbootHi": f"{best['bootstrap_J'][1]:.2f}", "JEm": f"{b['em_only'].J_tau_to_pooled:.3f}", "JRc": f"{b['original_rcustom'].J_tau_to_pooled:.3f}",
           "JUni": f"{b['uniform'].J_tau_to_pooled:.3f}", "JFone": f"{b['f1_only'].J_tau_to_pooled:.3f}", "pairTauBest": f"{b['random_search_best'].mean_pairwise_tau:.3f}",
           "pairTauEm": f"{b['em_only'].mean_pairwise_tau:.3f}", "dispBest": f"{b['random_search_best'].scale_dispersion:.2f}", "dispEm": f"{b['em_only'].scale_dispersion:.2f}",
           "tauNative": f"{res['tau_vs_native_borda']:.2f}", "tauEmPool": f"{res['tau_vs_em_borda']:.2f}", "topOne": esc(order[0]), "topTwo": esc(order[1]), "topThree": esc(order[2]),
           "medianJ": f"{rs.J_tau_to_pooled.median():.3f}", "minJ": f"{rs.J_tau_to_pooled.min():.3f}",
           "nAboveEm": int((rs.J_tau_to_pooled > b['em_only'].J_tau_to_pooled).sum()),
           "lodoMean": f"{lodo.tau_heldout_lodo_weights.mean():.2f}", "lodoFullMean": f"{lodo.tau_heldout_full_weights.mean():.2f}",
           "weightsStr": ", ".join(f"{esc(n)} {v:.2f}" for n, v in best["weights"].items() if v > 0)}
    (ROOT / "paper" / "numbers.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in mac.items()) + "\n")
    print("\n".join(L[:12]))
    print("tables:", sorted(p.name for p in TAB.glob("*.tex")))


if __name__ == "__main__":
    main()
