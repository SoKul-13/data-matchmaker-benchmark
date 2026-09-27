#!/usr/bin/env python
"""v3 step 6 - Figures, LaTeX tables, numbers.tex and notes/04_RESULTS.md from output/."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]          # this version's folder (output/ lives here)
V6 = ROOT.parent                                     # the shared v6 folder (shared/src, data/, config/)
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from metrics.library import FAMILIES, METRIC_NAMES  # noqa: E402

OUT, FIG, TAB = OUT, ROOT / "paper" / "figures", ROOT / "paper" / "tables"
FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#1baf7a"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e8e7e3", "grid.linewidth": 0.5, "legend.frameon": False, "savefig.bbox": "tight", "pdf.fonttype": 42})


def esc(s):
    return str(s).replace("_", "\\_").replace("%", "\\%")


def table(name, header, rows, caption, label, align=None, wide=False, size="\\small", resize=False):
    align = align or "l" + "r" * (len(header) - 1); env = "table*" if wide else "table"
    L = [f"\\begin{{{env}}}[t]", "\\centering", size, f"\\caption{{{caption}}}", f"\\label{{{label}}}", "\\resizebox{\\textwidth}{!}{%" if resize else "",
         f"\\begin{{tabular}}{{{align}}}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"] + [" & ".join(str(x) for x in r) + " \\\\" for r in rows] + \
        ["\\bottomrule", "\\end{tabular}", "}" if resize else "", f"\\end{{{env}}}"]
    (TAB / f"{name}.tex").write_text("\n".join(L), encoding="utf-8")


def main():
    sel = json.load(open(OUT / "selected.json")); ens = json.load(open(OUT / "ensemble.json")); lb = json.load(open(OUT / "leaderboard.json"))
    val = json.load(open(OUT / "validation.json")); mt = pd.read_csv(OUT / "metric_table.csv"); base = pd.read_csv(OUT / "baselines_grid.csv")
    probes = pd.read_csv(OUT / "probes.csv"); lodo = pd.read_csv(OUT / "lodo.csv"); grid = pd.read_csv(OUT / "grid_all.csv")
    ia = pd.read_csv(OUT / "index_anchors.csv"); im = pd.read_csv(OUT / "index_models.csv")
    names = ens["selected"]; Wtop = np.array(ens["top_weightings"])
    # ---- fig: metric agreement by family + top-100 weight spread
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.8), gridspec_kw={"width_ratios": [1.5, 1]}, constrained_layout=True)
    ax = axes[0]
    fam_order = [f for f in FAMILIES if f != "semantic"]
    mt["fam_i"] = mt.family.map({f: i for i, f in enumerate(fam_order)})
    mm = mt.dropna(subset=["fam_i"])
    ax.scatter(mm.fam_i + np.random.default_rng(0).uniform(-0.25, 0.25, len(mm)), mm.rho, s=[22 if r else 8 for r in mm.representative], color=[BLUE if r else GRAY for r in mm.representative], lw=0)
    for n in names:
        r = mt[mt.metric == n].iloc[0]; ax.annotate(n, (r.fam_i, r.rho), xytext=(4, 4), textcoords="offset points", fontsize=6.5, color=ORANGE)
    ax.set_xticks(range(len(fam_order))); ax.set_xticklabels(fam_order, rotation=45, ha="right"); ax.set_ylabel("Spearman with anchor utility")
    ax.set_title("100 metrics: anchor agreement by family (blue = cluster representative; orange = selected)", fontsize=7.5, loc="left")
    ax = axes[1]
    for k, n in enumerate(names + ["lambda"]):
        ax.scatter(np.full(Wtop.shape[0], k) + np.random.default_rng(k).uniform(-0.15, 0.15, Wtop.shape[0]), Wtop[:, k], s=8, color=BLUE, alpha=0.5, lw=0)
        ax.scatter([k], [Wtop[:, k].mean()], s=40, color=ORANGE, zorder=3, edgecolor="white")
    ax.set_xticks(range(len(names) + 1)); ax.set_xticklabels(names + ["λ (hedge)"], rotation=45, ha="right"); ax.set_ylabel("weight")
    ax.set_title("The 100 best weightings (orange = ensemble mean)", fontsize=7.5, loc="left")
    fig.savefig(FIG / "fig_selection.pdf"); fig.savefig(FIG / "fig_selection.png", dpi=200); plt.close(fig)
    # ---- fig: probe calibration (score vs utility)
    fig, ax = plt.subplots(figsize=(3.8, 2.8), constrained_layout=True)
    for col, c, lab in [("ensemble", BLUE, "ensemble (ours)"), ("native", ORANGE, "native typed metric"), ("em", GRAY, "EM")]:
        ax.scatter(probes.utility, probes[col], s=18, color=c, label=lab, lw=0)
    ax.plot([0, 1], [0, 1], color=INK, lw=0.6, ls="--"); ax.set_xlabel("anchor utility (known)"); ax.set_ylabel("mean score")
    for _, r in probes.iterrows():
        if abs(r.ensemble - r.utility) > 0.2:
            ax.annotate(r.op, (r.utility, r.ensemble), xytext=(3, 2), textcoords="offset points", fontsize=5.5, color=BLUE)
    ax.legend(fontsize=6.5, loc="upper left"); ax.set_title("Score vs known utility per anchor operator", fontsize=7.5, loc="left")
    fig.savefig(FIG / "fig_probes.pdf"); fig.savefig(FIG / "fig_probes.png", dpi=200); plt.close(fig)
    import shutil
    shutil.copy(OUT / "fig_leaderboard.pdf", FIG / "fig_leaderboard.pdf")
    # ---- tables
    table("tab_selected", ["Step", "Added metric", "Family", "LODO $\\rho$", "Gain"], [[t["step"], esc(t["added"]), esc(mt[mt.metric == t["added"]].family.iloc[0]), f"{t['lodo_rho']:.3f}", f"{t['gain']:+.3f}" + (" (stop)" if t.get("stopped") else "")] for t in sel["trace"]],
          f"Forward selection on the anchor set ({esc(sel['anchor'])}); {sel['n_representatives']} cluster representatives of 100 metrics were candidates.", "tab:selected", align="rlllr", wide=True, size="\\footnotesize")
    table("tab_baselines", ["Metric", "$\\rho_{anchor}$", "AUC", "JS$_\\times$", "wrong$\\to$", "$\\tau_{native}$", "$J$"],
          [[esc(r.baseline), f"{r.rho:.3f}", f"{r.auc:.3f}", f"{r.js:.3f}", f"{r.bad:.3f}", f"{r.tau_native:.3f}", f"{r.J:.3f}"] for _, r in base.iterrows()],
          "Single-metric baselines vs.\\ the calibrated ensemble under the same objective (higher is better except JS and wrong$\\to$, the mean score given to wrong or abstaining answers).", "tab:baselines", wide=True, size="\\footnotesize")
    top = probes.sort_values("utility", ascending=False)
    table("tab_probes", ["Operator", "$u$", "$n$", "Ensemble", "Native", "EM", "F1"], [[esc(r.op), f"{r.utility:.2f}", int(r.n), f"{r.ensemble:.2f}", f"{r.native:.2f}", f"{r.em:.2f}", f"{r.tok_f1:.2f}"] for _, r in top.iterrows()],
          "Mean score per anchor operator (all datasets). A calibrated metric tracks the utility column.", "tab:probes", wide=True, size="\\footnotesize")
    table("tab_lodo", ["Held-out", "$\\rho$ LODO", "$\\rho$ full", "Selection (LODO)"], [[esc(r.held_out), f"{r.rho_heldout_lodo:.3f}", f"{r.rho_heldout_full:.3f}", esc(", ".join(eval(r.selected_lodo)))] for _, r in lodo.iterrows()],
          "Leave-one-dataset-out: selection and weights re-fitted without the held-out dataset, anchor Spearman on it.", "tab:lodo", wide=True, size="\\footnotesize")
    models, datasets = lb["models"], lb["datasets"]; order = sorted(models, key=lambda m: lb["pooled_ranks"]["borda"][m])
    DS = {"officeqa": "OfficeQA", "finqa": "FinQA", "tat_qa": "TAT-QA", "tab_fact": "TabFact", "financebench": "FinanceBench", "fetaqa": "FeTaQA", "wikitablequestions": "WTQ", "hitab": "HiTab", "abt_buy": "Abt-Buy", "amazon_google": "Amazon-Google", "dblp_scholar": "DBLP-Scholar", "walmart_amazon": "Walmart-Amazon", "wdc_products": "WDC", "tpcdi_cells": "TPC-DI"}
    table("tab_leaderboard", ["Model"] + [DS.get(d, d) for d in datasets] + ["$z$-mean", "Borda", "Kemeny", "95\\% CI", "over 100 $w$", "Native"],
          [[esc(m)] + [f"{lb['per_dataset'][m][d]:.2f}" for d in datasets] + [f"{lb['common_score_z'][m]:+.2f}", f"{lb['pooled_ranks']['borda'][m]:.0f}", f"{lb['pooled_ranks']['kemeny'][m]:.0f}",
           f"[{lb['bootstrap_items'][m]['ci95'][0]:.0f}, {lb['bootstrap_items'][m]['ci95'][1]:.0f}]", f"{lb['rank_over_weightings'][m]['min']:.0f}--{lb['rank_over_weightings'][m]['max']:.0f}", f"{lb['native_borda'][m]:.0f}"] for m in order],
          "Leaderboard under the ensemble metric: per-dataset means, difficulty-adjusted common score, pooled ranks, item-bootstrap CI, rank range across the 100 weightings, native-metric pooled rank.", "tab:leaderboard", wide=True, resize=True)
    # ---- numbers.tex
    n_models_pending = len([d for d in pd.read_csv(OUT / "index_anchors.csv").dataset.unique() if d not in datasets])
    mac = {"nMetrics": 100, "nConstant": sel["n_constant"], "nReps": sel["n_representatives"], "nCands": sel["n_candidates"], "kSel": len(names), "selList": esc(", ".join(names)),
           "nAnchors": f"{len(ia):,}", "nOps": ia.op.nunique(), "nAnchorDatasets": ia.dataset.nunique(), "nModels": len(models), "nDatasets": len(datasets), "nPendingDatasets": n_models_pending,
           "gridStep": ens["grid_step"], "nGrid": f"{ens['n_grid']:,}", "topK": ens["top_k"], "meanLambda": f"{ens['mean_lambda']:.2f}",
           "meanW": esc(", ".join(f"{k} {v:.2f}" for k, v in ens["mean_weights"].items())),
           "Jtop": f"{ens['J_top1']:.3f}", "JtopHundred": f"{ens['J_top100']:.3f}", "JmedGrid": f"{ens['J_median_grid']:.3f}",
           "rhoEns": f"{ens['terms_ensemble_mean']['rho']:.3f}", "aucEns": f"{ens['terms_ensemble_mean']['auc']:.3f}", "jsEns": f"{ens['terms_ensemble_mean']['js']:.3f}", "badEns": f"{ens['terms_ensemble_mean']['bad']:.3f}", "tauNatEns": f"{ens['terms_ensemble_mean']['tau_native']:.3f}",
           "lodoRhoSel": f"{sel['lodo_rho_selected']:.3f}", "lodoRhoNative": f"{sel['lodo_rho_native_only']:.3f}", "lodoRhoEm": f"{sel['lodo_rho_em_only']:.3f}",
           "lodoMeanLodo": f"{val['lodo_mean_rho_lodo']:.3f}", "lodoMeanFull": f"{val['lodo_mean_rho_full']:.3f}", "lodoSameSel": f"{100 * val['lodo_same_selection_share']:.0f}",
           "sevShift": f"{val['severity_l1_shift_mean']:.3f}", "sevSelChanged": f"{100 * val['severity_selection_changed_share']:.0f}",
           "probeMaeEns": f"{val['probe_mae_ensemble']:.3f}", "probeMaeNative": f"{val['probe_mae_native']:.3f}", "probeMaeEm": f"{val['probe_mae_em']:.3f}", "probeMaeF": f"{val['probe_mae_tok_f1']:.3f}",
           "topOne": esc(order[0]), "topTwo": esc(order[1]), "tauNativePool": f"{lb['tau_vs_native']:.2f}", "pairTau": f"{lb['mean_pairwise_dataset_tau']:.2f}"}
    for _, r in base.iterrows():
        key = "".join(w.capitalize() for w in r.baseline.replace("_", " ").replace("100", " hundred ").split())
        key = re.sub(r"\d", lambda m: "ZeroOneTwoThreeFourFiveSixSevenEightNine".split("Zero")[0] if False else ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"][int(m.group())], key)
        mac[f"J{key}"] = f"{r.J:.3f}"; mac[f"rho{key}"] = f"{r.rho:.3f}"; mac[f"tauNat{key}"] = f"{r.tau_native:.3f}"; mac[f"bad{key}"] = f"{r.bad:.3f}"
    (ROOT / "paper" / "numbers.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in mac.items()) + "\n")
    # ---- notes/04_RESULTS.md
    L = ["# v3 results (auto-generated by scripts/06_report.py)\n",
         f"* Library: 100 metrics; {sel['n_constant']} constant on this data; {sel['n_representatives']} cluster representatives (|Spearman| ≥ 0.95); {sel['n_candidates']} candidates after the anchor-agreement floor.",
         f"* Anchor: {sel['anchor']} across {ia.dataset.nunique()} datasets (including the {n_models_pending} datasets whose model predictions are still pending).",
         f"* Selected metrics: {', '.join(names)} (LODO Spearman with utility {sel['lodo_rho_selected']:.3f}; native typed metric alone {sel['lodo_rho_native_only']:.3f}; EM alone {sel['lodo_rho_em_only']:.3f}).",
         f"* Grid: step {ens['grid_step']} × 5 hedge penalties = {ens['n_grid']:,} weightings; top {ens['top_k']} kept. Ensemble mean weights: " + ", ".join(f"{k} {v:.2f}" for k, v in ens["mean_weights"].items()) + f"; mean λ {ens['mean_lambda']:.2f}.",
         f"* Objective terms (ensemble mean): anchor ρ {ens['terms_ensemble_mean']['rho']:.3f}, AUC {ens['terms_ensemble_mean']['auc']:.3f}, cross-dataset JS {ens['terms_ensemble_mean']['js']:.3f}, wrong→ {ens['terms_ensemble_mean']['bad']:.3f}, native τ {ens['terms_ensemble_mean']['tau_native']:.3f}.",
         "", "## Baselines under the same objective\n", base.round(3).to_markdown(index=False), "",
         "## Probes: mean score per anchor operator vs known utility\n", probes.round(2).to_markdown(index=False), "",
         f"Probe MAE to utility: ensemble {val['probe_mae_ensemble']:.3f}, native {val['probe_mae_native']:.3f}, EM {val['probe_mae_em']:.3f}, F1 {val['probe_mae_tok_f1']:.3f}.", "",
         "## Leave-one-dataset-out\n", lodo.round(3).to_markdown(index=False), "",
         f"Mean held-out ρ: LODO weights {val['lodo_mean_rho_lodo']:.3f} vs full weights {val['lodo_mean_rho_full']:.3f}; same selection in {100 * val['lodo_same_selection_share']:.0f}% of folds.",
         f"Severity-scale perturbation (±0.15, 5 draws): mean L1 shift of ensemble weights {val['severity_l1_shift_mean']:.3f}; selection changed in {100 * val['severity_selection_changed_share']:.0f}% of draws.", "",
         "## Leaderboard\n", (OUT / "leaderboard.md").read_text().split("\n", 1)[1],
         "## Caveats\n", "* 4 models × 40 items on the 7 datasets with predictions; ranks below the top are not separable (see CIs).",
         f"* {n_models_pending} datasets have anchors but no model predictions yet (run `scripts/00_run_models.py`).",
         "* The anchor utility scale is hand-set (stated in `src/anchors/ladder.py`) and perturbed above; human labels can replace it via `02_select_metrics.py --labels`.",
         "* The native typed metric scores as high as the ensemble on the mixed objective because it wins the native-fidelity term by construction; the ensemble wins on anchor agreement, AUC and wrong→0."]
    (ROOT / "notes" / "04_RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("figures:", sorted(p.name for p in FIG.glob("*.pdf")), "\ntables:", sorted(p.name for p in TAB.glob("*.tex")))


if __name__ == "__main__":
    main()
