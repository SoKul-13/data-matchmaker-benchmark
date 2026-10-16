"""Build the Overleaf package for the v2 evaluation paper.

Reads FINAL_v2/v2_gridsearch/output/ (and the prediction cache for run facts), generates every figure that can be drawn
from those files, exports every table to LaTeX, copies all raw data, writes overleaf/main.tex (Setup + Results from
eval_paper.tex, followed by an appendix that includes every figure and table) and zips the folder.

Run from FINAL_v2:  uv run python paper/scripts/make_overleaf_package.py
"""
from __future__ import annotations
import json, re, shutil, zipfile, itertools
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kendalltau

ROOT = Path(__file__).resolve().parents[2]          # FINAL_v2
OUT = ROOT / "v2_gridsearch" / "output"
PAPER = ROOT / "paper"
PKG = PAPER / "v2"
FIG = PKG / "figures"; TAB = PKG / "tables"; DAT = PKG / "data"
for d in (FIG, TAB, DAT): d.mkdir(parents=True, exist_ok=True)

PRETTY = {"claude-opus-5": "Claude Opus 5", "claude-sonnet-5": "Claude Sonnet 5", "gpt-5.5": "GPT-5.5", "gpt-5.4-mini": "GPT-5.4-mini",
          "gemini-3.8-flash": "Gemini 3.8 Flash", "grok-4": "Grok 4", "deepseek-chat": "DeepSeek-chat", "deepseek-r1": "DeepSeek-R1",
          "gpt-oss-120b": "gpt-oss-120b", "llama-3.3-70b": "Llama 3.3 70B", "gemini-3.1-pro": "Gemini 3.1 Pro"}
RULES = ["em_only", "v1_original", "top1", "top2", "top3", "top4", "top5", "best_anchor", "pareto_knee"]
RULE_PRETTY = {"em_only": "exact match", "v1_original": "v1", "top1": "top1", "top2": "top2", "top3": "top3", "top4": "top4", "top5": "top5",
               "best_anchor": "best-rho", "pareto_knee": "knee"}
FAM = {"EM": "entity matching", "SM": "schema matching", "TQA": "table QA", "FIN": "finance"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 110})
captions: dict[str, str] = {}
table_caps: dict[str, str] = {}


def save(fig, name, cap):
    fig.tight_layout(); fig.savefig(FIG / f"{name}.png", dpi=200); fig.savefig(FIG / f"{name}.pdf"); plt.close(fig)
    captions[name] = cap


def tex_escape(s):
    return str(s).replace("_", r"\_\allowbreak{}").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")


def to_tex(df: pd.DataFrame, name: str, cap: str, fmt="%.3f", index=False, small=True, longtable=False, col_format=None):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object: df[c] = df[c].map(tex_escape)
    df.columns = [tex_escape(c) for c in df.columns]
    if index: df = df.reset_index()
    def cell(x):
        if isinstance(x, (float, np.floating)): return "--" if pd.isna(x) else fmt % x
        if isinstance(x, (bool, np.bool_)): return "yes" if x else "no"
        return tex_escape(x) if not isinstance(x, str) else x
    ncol = len(df.columns)
    lens = [max([len(str(x)) for x in df[c]] + [len(str(c))]) for c in df.columns]
    longcols = [i for i, L in enumerate(lens) if L > 10]
    if not longtable and ncol > 8:
        cf = "l" + "r" * (ncol - 1); longcols = []
    elif longtable and ncol > 8:
        share = (0.985 - 0.0095 * ncol) / (ncol + 1); cf = f"p{{{2 * share:.3f}\\linewidth}}" + "".join(f"p{{{share:.3f}\\linewidth}}" for _ in range(ncol - 1)); longcols = []
    elif longcols:
        tot = sum(lens[i] for i in longcols); avail = 0.97 - 0.014 * ncol - 0.05 * (ncol - len(longcols))
        cf = "".join((f"p{{{max(0.06, avail * lens[i] / tot):.3f}\\linewidth}}" if i in longcols else ("l" if i == 0 else "r")) for i in range(ncol))
    else:
        cf = "l" + "r" * (ncol - 1)
    head = " & ".join(str(c) for c in df.columns) + r" \\"
    lines = [" & ".join(cell(x) for x in row) + r" \\" for row in df.itertuples(index=False)]
    env = "longtable" if longtable else "tabular"
    body = f"\\begin{{{env}}}{{{cf}}}\n\\toprule\n{head}\n\\midrule\n" + "\n".join(lines) + f"\n\\bottomrule\n\\end{{{env}}}\n"
    wide = len(df.columns) > 8
    if wide and not longtable and "p{" not in cf: body = "\\resizebox{\\linewidth}{!}{%\n" + body + "}\n"
    size = r"\tiny" if (wide or len(df.columns) > 6) else (r"\scriptsize" if small else r"\small")
    L0, L1 = ("\\begin{landscape}\n", "\\end{landscape}\n") if wide else ("", "")
    if not longtable:
        body = L0 + f"\\begin{{table}}[htbp]\n\\centering{size}\n\\caption{{{cap}}}\n\\label{{tab:{name}}}\n\\setlength{{\\tabcolsep}}{{3pt}}\n{body}\\end{{table}}\n" + L1
    else:
        body = L0 + body.replace(f"\\begin{{longtable}}{{{cf}}}\n", f"{size}\n\\setlength{{\\tabcolsep}}{{3pt}}\n\\begin{{longtable}}{{{cf}}}\n\\caption{{{cap}}}\\label{{tab:{name}}}\\\\\n", 1) + "\\normalsize\n" + L1
    (TAB / f"{name}.tex").write_text(body)
    table_caps[name] = cap


# ------------------------------------------------------------------ load
grid = pd.read_csv(OUT / "grid_exhaustive.csv")
comp = pd.read_csv(OUT / "components_v1.csv")
anch = pd.read_csv(OUT / "anchors" / "anchor_components.csv")
corr = pd.read_csv(OUT / "anchors" / "correctness.csv")
corr_json = json.load(open(OUT / "anchors" / "correctness.json"))
best = json.load(open(OUT / "best.json"))
nested = json.load(open(OUT / "selection" / "nested.json"))
draws = np.load(OUT / "selection" / "nested_draws.npz")
plateau = pd.read_csv(OUT / "selection" / "plateau.csv")
lodo = pd.read_csv(OUT / "selection" / "lodo.csv")
lofo = pd.read_csv(OUT / "selection" / "lofo.csv")
per_family = json.load(open(OUT / "selection" / "per_family.json"))
sens = json.load(open(OUT / "selection" / "sensitivity.json"))
designs = pd.read_csv(OUT / "designs.csv")
diag = pd.read_csv(OUT / "diagnostics" / "dataset_diagnostics.csv")
rule_agree = pd.read_csv(OUT / "leaderboards" / "rule_agreement.csv", index_col=0)
summary = json.load(open(OUT / "leaderboards" / "summary.json"))
LB = {r: pd.read_csv(OUT / "leaderboards" / r / "leaderboard.csv") for r in RULES}
PARAMS = {r: json.load(open(OUT / "leaderboards" / r / "params.json")) for r in RULES}
SIG = {r: json.load(open(OUT / "leaderboards" / r / "significance.json")) for r in RULES}
BOOT = {r: np.load(OUT / "leaderboards" / r / "bootstrap.npz") for r in RULES}
PDM = {r: pd.read_csv(OUT / "leaderboards" / r / "per_dataset_mean.csv", index_col=0) for r in RULES}
PDS = {r: pd.read_csv(OUT / "leaderboards" / r / "per_dataset_se.csv", index_col=0) for r in RULES}
OFF = {r: pd.read_csv(OUT / "leaderboards" / r / "official_split_estimates.csv") for r in RULES}
PW = {r: pd.read_csv(OUT / "leaderboards" / r / "pairwise_item_tests.csv") for r in RULES}
models = list(PARAMS["v1_original"]["models"]); datasets = list(PARAMS["v1_original"]["datasets"])
fam_of = dict(zip(diag["dataset"], diag["family"]))
W = ["w_f1", "w_decay", "w_precision", "w_recall"]; WN = ["F1", "decay", "precision", "recall"]
v1_row = grid[grid["label"] == "v1"].iloc[0] if "v1" in set(grid["label"]) else grid[(grid.w_f1 == .35) & (grid.w_decay == .35)].iloc[0]
best_row = grid.sort_values("J", ascending=False).iloc[0]
order_v1 = LB["v1_original"].sort_values("rank_bt")["model"].tolist()

# ------------------------------------------------------------------ figures: grid
fig, ax = plt.subplots(figsize=(6, 3.2))
for col, lab in [("J", "Borda"), ("J_kemeny", "Kemeny"), ("J_copeland", "Copeland"), ("J_bt", "Bradley-Terry")]:
    ax.plot(np.sort(grid[col].values)[::-1], lw=1, label=lab)
ax.axhline(v1_row["J"], ls=":", c="k", lw=.8); ax.text(1700, v1_row["J"], "v1 (Borda)", ha="right", va="bottom", fontsize=7)
ax.set_xlabel("weighting, sorted by J under each rule"); ax.set_ylabel("J"); ax.legend(frameon=False)
save(fig, "fig_j_pooling_rules", "Agreement objective $J$ over all 1,771 weightings under four pooling rules (each curve sorted separately). The landscape is flat under every rule.")

fig, ax = plt.subplots(figsize=(4.2, 3.4))
ax.scatter(grid["tau_native"], grid["J"], s=4, alpha=.4, c="grey")
ax.scatter(v1_row["tau_native"], v1_row["J"], c="C3", s=30, label="v1", zorder=3); ax.scatter(best_row["tau_native"], best_row["J"], c="C0", s=30, marker="s", label="best J", zorder=3)
ax.set_xlabel("tau to native metrics"); ax.set_ylabel("J"); ax.legend(frameon=False)
save(fig, "fig_tau_native_vs_j", "Agreement $J$ against Kendall $\\tau$ between each weighting's ranking and the native-metric ranking.")

fig, axes = plt.subplots(2, 3, figsize=(8, 5))
for ax, (a, b) in zip(axes.flat, itertools.combinations(range(4), 2)):
    piv = grid.groupby([W[a], W[b]])["J"].max().unstack()
    im = ax.imshow(piv.values, origin="lower", aspect="auto", cmap="viridis", extent=[piv.columns.min(), piv.columns.max(), piv.index.min(), piv.index.max()], vmin=grid.J.quantile(.02), vmax=grid.J.max())
    ax.set_xlabel(WN[b]); ax.set_ylabel(WN[a]); ax.plot(v1_row[W[b]], v1_row[W[a]], "r*", ms=8)
fig.colorbar(im, ax=axes, shrink=.6, label="max J over the other two weights")
fig.tight_layout(rect=(0, 0, .9, 1)); fig.savefig(FIG / "fig_weight_pairs.png", dpi=200); fig.savefig(FIG / "fig_weight_pairs.pdf"); plt.close(fig)
captions["fig_weight_pairs"] = "Best $J$ attainable for each pair of weight values (maximised over the remaining two weights); red star = v1."

tau_cols = [c for c in grid.columns if c.startswith("tau_") and c != "tau_native"]
labels_rows = {"v1": v1_row, "best J": best_row, "F1 only": grid[grid.w_f1 == 1].iloc[0], "decay only": grid[grid.w_decay == 1].iloc[0],
               "precision only": grid[grid.w_precision == 1].iloc[0], "recall only": grid[grid.w_recall == 1].iloc[0], "uniform": grid[(grid.w_f1 == .25) & (grid.w_decay == .25) & (grid.w_precision == .25)].iloc[0]}
M = pd.DataFrame({k: [r[c] for c in tau_cols] for k, r in labels_rows.items()}, index=[c[4:] for c in tau_cols])
fig, ax = plt.subplots(figsize=(5.5, 7))
im = ax.imshow(M.values, cmap="RdBu", vmin=-1, vmax=1, aspect="auto"); ax.set_xticks(range(M.shape[1])); ax.set_xticklabels(M.columns, rotation=45, ha="right"); ax.set_yticks(range(M.shape[0])); ax.set_yticklabels(M.index)
for i in range(M.shape[0]):
    for j in range(M.shape[1]): ax.text(j, i, f"{M.values[i, j]:+.2f}", ha="center", va="center", fontsize=5.5)
fig.colorbar(im, ax=ax, shrink=.5, label="tau(dataset ranking, Borda pool)")
save(fig, "fig_per_dataset_tau_rules", "Per-dataset Kendall $\\tau$ to the Borda pool under v1, the best weighting, the four single-ingredient corners and the uniform mix.")

# ------------------------------------------------------------------ figures: components / scores
pdm = PDM["v1_original"].loc[order_v1, datasets]
fig, ax = plt.subplots(figsize=(9, 3.6))
im = ax.imshow(pdm.values, cmap="viridis", aspect="auto", vmin=0, vmax=1); ax.set_xticks(range(len(datasets))); ax.set_xticklabels(datasets, rotation=60, ha="right", fontsize=6); ax.set_yticks(range(len(order_v1))); ax.set_yticklabels([PRETTY[m] for m in order_v1], fontsize=7)
for i in range(pdm.shape[0]):
    for j in range(pdm.shape[1]): ax.text(j, i, f"{pdm.values[i, j]:.2f}", ha="center", va="center", fontsize=4.5, color="w" if pdm.values[i, j] < .6 else "k")
fig.colorbar(im, ax=ax, shrink=.7, label="mean v1 composite")
save(fig, "fig_model_dataset_heatmap", "Mean v1 composite score per model and dataset (models in Bradley--Terry order under v1).")

rk = pdm.rank(ascending=False, axis=0)
fig, ax = plt.subplots(figsize=(9, 3.6))
im = ax.imshow(rk.values, cmap="viridis_r", aspect="auto", vmin=1, vmax=10); ax.set_xticks(range(len(datasets))); ax.set_xticklabels(datasets, rotation=60, ha="right", fontsize=6); ax.set_yticks(range(len(order_v1))); ax.set_yticklabels([PRETTY[m] for m in order_v1], fontsize=7)
for i in range(rk.shape[0]):
    for j in range(rk.shape[1]): ax.text(j, i, f"{rk.values[i, j]:.0f}", ha="center", va="center", fontsize=5, color="w" if rk.values[i, j] > 5 else "k")
fig.colorbar(im, ax=ax, shrink=.7, label="rank within dataset (1 = best)")
save(fig, "fig_model_dataset_ranks", "Rank of each model inside each dataset under v1 (ties by average rank).")

fam_mean = comp.assign(v1=lambda d: .35 * d.f1 + .35 * d.decay + .15 * d.precision + .15 * d.recall).groupby(["family", "model"])["v1"].mean().unstack(0).loc[order_v1]
fig, ax = plt.subplots(figsize=(7, 3))
x = np.arange(len(order_v1)); wdt = .2
for i, f in enumerate(["EM", "SM", "TQA", "FIN"]): ax.bar(x + (i - 1.5) * wdt, fam_mean[f], wdt, label=FAM[f])
ax.set_xticks(x); ax.set_xticklabels([PRETTY[m] for m in order_v1], rotation=30, ha="right"); ax.set_ylabel("mean v1 composite"); ax.legend(frameon=False, ncol=4, fontsize=7)
save(fig, "fig_family_scores", "Mean v1 composite per model within each task family.")

fig, axes = plt.subplots(1, 4, figsize=(9, 2.6), sharey=True)
for ax, f in zip(axes, ["EM", "SM", "TQA", "FIN"]):
    d = comp[comp.family == f]; v1s = .35 * d.f1 + .35 * d.decay + .15 * d.precision + .15 * d.recall
    ax.hexbin(d.native_value, v1s, gridsize=20, cmap="Blues", mincnt=1, bins="log"); ax.set_title(FAM[f]); ax.set_xlabel("native metric")
axes[0].set_ylabel("v1 composite")
save(fig, "fig_native_vs_composite", "Per-answer native metric against the v1 composite, by family (log-count hexbins).")

fig, axes = plt.subplots(1, 5, figsize=(10, 2.4))
for ax, c in zip(axes, ["em", "f1", "decay", "precision", "recall"]):
    for t in ["numeric", "boolean", "text", "free_form"]:
        d = comp[comp.answer_type == t][c].dropna()
        if len(d): ax.hist(d, bins=20, histtype="step", label=t, density=True)
    ax.set_title(c); ax.set_yticks([])
axes[0].legend(frameon=False, fontsize=6)
save(fig, "fig_component_distributions", "Distribution of each v1 ingredient over all answers, by answer type.")

# ------------------------------------------------------------------ figures: anchors
anch["v1"] = .35 * anch.f1 + .35 * anch.decay + .15 * anch.precision + .15 * anch.recall
op = anch.groupby("op").agg(utility=("utility", "mean"), v1=("v1", "mean"), em=("em", "mean"), n=("v1", "size")).sort_values("utility")
fig, ax = plt.subplots(figsize=(7, 3))
x = np.arange(len(op)); ax.bar(x - .2, op.utility, .4, label="known utility"); ax.bar(x + .2, op.v1, .4, label="mean v1 score"); ax.plot(x, op.em, "k.", label="exact match")
ax.set_xticks(x); ax.set_xticklabels(op.index, rotation=45, ha="right"); ax.legend(frameon=False, fontsize=7)
save(fig, "fig_anchor_operators", "Synthetic anchors: known utility of each perturbation operator against the mean v1 score and exact match it receives.")

rho_ds = {}
for lab, w in [("v1", (.35, .35, .15, .15)), ("best J", tuple(best_row[W])), ("best rho", tuple(corr[corr.label == "best_rho"].iloc[0][W]) if "best_rho" in set(corr.label) else None)]:
    if w is None: continue
    s = w[0] * anch.f1 + w[1] * anch.decay + w[2] * anch.precision + w[3] * anch.recall
    rho_ds[lab] = anch.assign(s=s).groupby("dataset").apply(lambda d: d[["s", "utility"]].corr(method="spearman").iloc[0, 1])
rho_ds = pd.DataFrame(rho_ds)
fig, ax = plt.subplots(figsize=(8, 2.8))
x = np.arange(len(rho_ds)); k = len(rho_ds.columns)
for i, c in enumerate(rho_ds.columns): ax.bar(x + (i - (k - 1) / 2) * .8 / k, rho_ds[c], .8 / k, label=c)
ax.set_xticks(x); ax.set_xticklabels(rho_ds.index, rotation=60, ha="right", fontsize=6); ax.set_ylabel("Spearman rho to utility"); ax.legend(frameon=False, fontsize=7)
save(fig, "fig_rho_per_dataset", "Anchor correctness (Spearman $\\rho$ between composite and known utility) per dataset under v1, the best-$J$ and the best-$\\rho$ weightings.")

fig, axes = plt.subplots(1, 3, figsize=(9, 2.8))
for ax, c, lab in zip(axes, ["auc", "wrong_mean", "hedge_gap"], ["AUC correct vs wrong", "mean score of wrong answers", "hedge gap"]):
    ax.scatter(corr.J, corr[c], s=4, alpha=.4, c="grey"); r = corr[corr.label == "v1"]
    if len(r): ax.scatter(r.J, r[c], c="C3", s=30, zorder=3, label="v1")
    ax.set_xlabel("J"); ax.set_ylabel(lab)
axes[0].legend(frameon=False)
save(fig, "fig_anchor_metrics_vs_j", "Three further anchor diagnostics against $J$ for every weighting.")

# ------------------------------------------------------------------ figures: leaderboards
fig, axes = plt.subplots(3, 3, figsize=(9, 7), sharex=True)
for ax, r in zip(axes.flat, RULES):
    d = LB[r].set_index("model").loc[order_v1]
    ax.barh(range(len(d)), d.bt_strength, xerr=d.bt_se_vs_ref, color=["C3" if m == order_v1[0] else "C0" for m in order_v1], height=.7)
    ax.set_yticks(range(len(d))); ax.set_yticklabels([PRETTY[m] for m in order_v1], fontsize=6); ax.invert_yaxis(); ax.set_title(RULE_PRETTY[r], fontsize=8); ax.axvline(0, c="k", lw=.5)
for ax in axes[-1]: ax.set_xlabel("Bradley-Terry strength")
save(fig, "fig_bt_all_rules", "Bradley--Terry strengths ($\\pm$ SE vs reference) under every reported rule; models fixed in v1 order.")

b = BOOT["v1_original"]; bm = list(b["models"])
fig, axes = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
for ax, key, lab in zip(axes, ["bt_ranks", "borda_ranks"], ["Bradley-Terry rank", "Borda rank"]):
    idx = [bm.index(m) for m in order_v1]
    ax.boxplot([b[key][:, i] for i in idx], vert=False, widths=.6, showfliers=False, medianprops={"color": "C3"})
    ax.set_yticks(range(1, len(order_v1) + 1)); ax.set_yticklabels([PRETTY[m] for m in order_v1], fontsize=7); ax.invert_yaxis(); ax.set_xlabel(lab + " (1,000 item bootstraps)")
save(fig, "fig_rank_bootstrap_v1", "Bootstrap distribution of each model's rank under v1 (1,000 item resamples).")

pf = pd.DataFrame({RULE_PRETTY[r]: LB[r].set_index("model").loc[order_v1, "p_first_bt"] for r in RULES})
pb = pd.DataFrame({RULE_PRETTY[r]: LB[r].set_index("model").loc[order_v1, "p_first_borda"] for r in RULES})
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
for ax, P, lab in zip(axes, [pf, pb], ["P(first) Bradley-Terry", "P(first) Borda"]):
    im = ax.imshow(P.values, cmap="Blues", vmin=0, vmax=1, aspect="auto"); ax.set_xticks(range(P.shape[1])); ax.set_xticklabels(P.columns, rotation=45, ha="right", fontsize=7); ax.set_yticks(range(P.shape[0])); ax.set_yticklabels([PRETTY[m] for m in P.index], fontsize=7); ax.set_title(lab)
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            if P.values[i, j] > .005: ax.text(j, i, f"{P.values[i, j]:.2f}", ha="center", va="center", fontsize=6, color="w" if P.values[i, j] > .5 else "k")
save(fig, "fig_p_first", "Bootstrap probability of first place for every model under every rule, by pooling method.")

fig, ax = plt.subplots(figsize=(4.5, 4))
im = ax.imshow(rule_agree.values, cmap="Blues", vmin=.7, vmax=1); ax.set_xticks(range(len(RULES))); ax.set_xticklabels([RULE_PRETTY[r] for r in rule_agree.columns], rotation=45, ha="right"); ax.set_yticks(range(len(RULES))); ax.set_yticklabels([RULE_PRETTY[r] for r in rule_agree.index])
for i in range(len(RULES)):
    for j in range(len(RULES)): ax.text(j, i, f"{rule_agree.values[i, j]:.2f}", ha="center", va="center", fontsize=6, color="w" if rule_agree.values[i, j] > .9 else "k")
save(fig, "fig_rule_agreement", "Kendall $\\tau$ between the Bradley--Terry rankings produced by each pair of rules.")

s = SIG["v1_original"]["friedman"]; mr = pd.Series(s["mean_rank"]).sort_values(); cd = s["nemenyi_cd_05"]
fig, ax = plt.subplots(figsize=(7, 2.6))
ax.scatter(mr.values, np.zeros(len(mr)), c="k", s=15)
for i, (m, v) in enumerate(mr.items()): ax.annotate(PRETTY[m], (v, 0), xytext=(v, .35 + .25 * (i % 2)), ha="center", fontsize=6, arrowprops={"arrowstyle": "-", "lw": .5})
ax.plot([mr.values[0], mr.values[0] + cd], [-.3, -.3], lw=3, c="C3"); ax.text(mr.values[0] + cd / 2, -.5, f"Nemenyi CD = {cd:.2f}", ha="center", fontsize=7, color="C3")
ax.set_ylim(-.8, 1); ax.set_yticks([]); ax.set_xlabel("mean rank across 31 datasets (Friedman, v1)"); ax.spines["left"].set_visible(False)
save(fig, "fig_cd_diagram_v1", "Critical-difference view of the Friedman test under v1: mean rank per model and the Nemenyi critical difference at $\\alpha = .05$.")

pw = PW["v1_original"]; sig_pairs = pw[pw.significant_05].groupby(["a", "b"]).size()
Mp = pd.DataFrame(0, index=order_v1, columns=order_v1, dtype=int)
for (a, bb), n in sig_pairs.items():
    if a in Mp.index and bb in Mp.columns: Mp.loc[a, bb] += n; Mp.loc[bb, a] += n
fig, ax = plt.subplots(figsize=(5, 4.3))
im = ax.imshow(Mp.values, cmap="Oranges", aspect="auto"); ax.set_xticks(range(len(order_v1))); ax.set_xticklabels([PRETTY[m] for m in order_v1], rotation=45, ha="right", fontsize=7); ax.set_yticks(range(len(order_v1))); ax.set_yticklabels([PRETTY[m] for m in order_v1], fontsize=7)
for i in range(len(order_v1)):
    for j in range(len(order_v1)): ax.text(j, i, Mp.values[i, j], ha="center", va="center", fontsize=6)
fig.colorbar(im, ax=ax, shrink=.6, label="datasets with a Holm-significant item-level difference")
save(fig, "fig_pairwise_significance_v1", "Number of datasets (of 31) in which the per-item paired test separates each pair of models under v1 (Holm within dataset).")

nsp = pd.Series(SIG["v1_original"]["n_significant_pairs_per_dataset"]).sort_values()
fig, ax = plt.subplots(figsize=(7, 2.6)); ax.bar(range(len(nsp)), nsp.values, color=[{"EM": "C0", "SM": "C1", "TQA": "C2", "FIN": "C3"}[fam_of[d]] for d in nsp.index])
ax.set_xticks(range(len(nsp))); ax.set_xticklabels(nsp.index, rotation=60, ha="right", fontsize=6); ax.set_ylabel("significant model pairs (of 45)")
save(fig, "fig_significant_pairs_per_dataset", "How many of the 45 model pairs each dataset separates at the item level under v1 (colour = family).")

mb = PARAMS["v1_original"]["majority_baselines"]; bsets = list(mb.keys())
fig, ax = plt.subplots(figsize=(7, 2.8))
x = np.arange(len(bsets))
for i, m in enumerate(order_v1): ax.scatter(x + (i - (len(order_v1) - 1) / 2) * .07, [PDM["em_only"].loc[m, d] for d in bsets], s=8, label=PRETTY[m])
ax.plot(x, [mb[d]["majority_class_accuracy"] for d in bsets], "k_", ms=14, label="majority class")
ax.set_xticks(x); ax.set_xticklabels(bsets, rotation=45, ha="right", fontsize=7); ax.set_ylabel("exact-match accuracy"); ax.legend(frameon=False, fontsize=5, ncol=4)
save(fig, "fig_majority_baselines", "Exact-match accuracy of every model on the boolean datasets against the majority-class baseline of each pool.")

# official-split figures
off = OFF["v1_original"]
fig, ax = plt.subplots(figsize=(4.2, 4))
ax.scatter(off.suite_mean, off.official_estimate, s=8, alpha=.6); ax.plot([0, 1], [0, 1], "k:", lw=.8); ax.set_xlabel("suite score (balanced pool)"); ax.set_ylabel("official-split estimate")
save(fig, "fig_official_scatter", "Suite score against post-stratified official-split estimate for every (dataset, model) pair under v1.")
em = off[off.official_f1_pos.notna()]
fig, ax = plt.subplots(figsize=(7, 3))
ds = em.groupby("dataset").official_f1_pos.mean().sort_values().index; x = np.arange(len(ds))
for i, m in enumerate(order_v1):
    d = em[em.model == m].set_index("dataset").reindex(ds)
    ax.scatter(x + (i - (len(order_v1) - 1) / 2) * .07, d.official_f1_pos, s=8, label=PRETTY[m]); ax.scatter(x + (i - (len(order_v1) - 1) / 2) * .07, d.suite_f1_pos, s=8, marker="_", c="grey")
ax.set_xticks(x); ax.set_xticklabels(ds, rotation=45, ha="right", fontsize=7); ax.set_ylabel("positive-class F1 (dots: official ratio; grey: pool)"); ax.legend(frameon=False, fontsize=5, ncol=5)
save(fig, "fig_official_f1_models", "Positive-class F1 on the balanced pool (grey) and at the official match ratio (coloured) per model and matching dataset.")

# ------------------------------------------------------------------ figures: selection
fig, ax = plt.subplots(figsize=(8, 3))
L = lodo[lodo.kind == "dataset"] if "dataset" in set(lodo.kind) else lodo
piv = L.pivot(index="held_out", columns="weights_from", values="tau_heldout_mean")
cols = [c for c in ["lodo_weights", "full_best", "v1"] if c in piv.columns]; x = np.arange(len(piv))
for i, c in enumerate(cols): ax.bar(x + (i - 1) * .27, piv[c], .27, label=c.replace("_", " "))
ax.set_xticks(x); ax.set_xticklabels(piv.index, rotation=60, ha="right", fontsize=6); ax.set_ylabel("tau held-out -> pooled rest"); ax.legend(frameon=False, fontsize=7); ax.axhline(0, c="k", lw=.5)
save(fig, "fig_lodo_tau", "Leave-one-dataset-out: agreement of the held-out dataset with the pooled ranking of the rest, under weights fitted without it, the full-data best and v1.")

fig, axes = plt.subplots(1, 4, figsize=(9, 2.4), sharey=True)
chosen = draws["chosen"]; wsel = grid.set_index("rank").loc[chosen + 1, W].values if grid["rank"].min() == 1 else grid.iloc[chosen][W].values
for ax, j in enumerate(range(4)):
    axes[j].hist(wsel[:, j], bins=np.arange(-.025, 1.05, .05), color="C0"); axes[j].axvline([.35, .35, .15, .15][j], c="C3", ls=":", label="v1"); axes[j].set_title(WN[j]); axes[j].set_xlabel("selected weight")
axes[0].legend(frameon=False, fontsize=7)
save(fig, "fig_selected_weights", "Weights selected as best on the in-bag items across 1,000 bootstrap resamples; dotted line = v1.")

d_oob = draws["J_out_sel"] - draws["J_out_v1"]
fig, ax = plt.subplots(figsize=(4.5, 3)); ax.hist(d_oob, bins=40, color="C0"); ax.axvline(0, c="k", lw=.8); ax.axvline(d_oob.mean(), c="C3", ls=":", label=f"mean {d_oob.mean():+.3f}")
ax.set_xlabel("out-of-bag J(selected) - J(v1)"); ax.set_ylabel("resamples"); ax.legend(frameon=False)
save(fig, "fig_oob_difference", "Paired out-of-bag difference between the selected weighting and v1 over 1,000 resamples.")

fig, ax = plt.subplots(figsize=(4.5, 3)); ax.hist(draws["J_in"].max(1), bins=40, alpha=.6, label="in-bag J of selected"); ax.hist(draws["J_out_sel"], bins=40, alpha=.6, label="out-of-bag J of selected"); ax.hist(draws["J_out_v1"], bins=40, alpha=.6, label="out-of-bag J of v1")
ax.set_xlabel("J"); ax.legend(frameon=False, fontsize=7)
save(fig, "fig_optimism_distributions", "Distributions behind the optimism gap: in-bag $J$ of the selected weighting, its out-of-bag $J$, and v1's out-of-bag $J$.")

top = plateau.sort_values("times_selected", ascending=False).head(20)
fig, ax = plt.subplots(figsize=(7, 3)); ax.bar(range(len(top)), top.times_selected); ax.set_xticks(range(len(top))); ax.set_xticklabels([f"{r.w_f1:.2f}/{r.w_decay:.2f}/{r.w_precision:.2f}/{r.w_recall:.2f}" for r in top.itertuples()], rotation=60, ha="right", fontsize=6); ax.set_ylabel("times selected (of 1,000)")
save(fig, "fig_times_selected", "The twenty weightings most often selected as in-bag best (F1 / decay / precision / recall).")

fig, ax = plt.subplots(figsize=(6, 3)); pl = plateau.sort_values("J_full", ascending=False).reset_index(drop=True)
ax.fill_between(pl.index, pl.J_boot_lo, pl.J_boot_hi, alpha=.3, label="bootstrap 95% band"); ax.plot(pl.index, pl.J_full, lw=1, label="J (full data)"); ax.plot(pl.index, pl.J_oob_mean, lw=1, label="mean out-of-bag J")
ax.set_xlabel("weighting, sorted by full-data J"); ax.set_ylabel("J"); ax.legend(frameon=False, fontsize=7)
save(fig, "fig_plateau_oob", "Full-data $J$, bootstrap band and mean out-of-bag $J$ for every weighting in rank order.")

fig, ax = plt.subplots(figsize=(4.5, 2.8))
for i, k in enumerate(["v1", "best"]):
    s_ = sens[k]; ax.errorbar(i, s_["J_centre"], yerr=[[s_["J_centre"] - s_["J_min"]], [s_["J_max"] - s_["J_centre"]]], fmt="o", capsize=4, label=f"{k}: {s_['n_neighbours']} neighbours")
ax.set_xticks([0, 1]); ax.set_xticklabels(["v1", "best"]); ax.set_ylabel("J (centre; bar = neighbour min/max)"); ax.legend(frameon=False, fontsize=7)
save(fig, "fig_sensitivity", "One-step sensitivity: $J$ at v1 and at the best weighting with the range over all lattice neighbours one 0.05 move away.")

fig, axes = plt.subplots(1, 3, figsize=(9, 2.8))
for ax, c in zip(axes, ["regret", "centred_L2_discrepancy", "best_rank_in_exhaustive"]):
    ax.boxplot([designs[designs.design == d][c] for d in designs.design.unique()], tick_labels=[d.replace("_", "\n") for d in designs.design.unique()]); ax.set_title(c.replace("_", " "), fontsize=8)
save(fig, "fig_design_metrics", "Sampled designs over 20 seeds: regret against the exhaustive optimum, centred $L_2$ discrepancy and rank of the found best.")

# families: J of each family under each per-family optimum
fams = ["EM", "SM", "TQA", "FIN"]
fig, ax = plt.subplots(figsize=(5, 3)); x = np.arange(4)
ax.bar(x - .27, [per_family[f]["J_family_best"] for f in fams], .27, label="own optimum"); ax.bar(x, [per_family[f]["J_family_under_global_best"] for f in fams], .27, label="global best"); ax.bar(x + .27, [per_family[f]["J_family_under_v1"] for f in fams], .27, label="v1")
ax.set_xticks(x); ax.set_xticklabels([FAM[f] for f in fams]); ax.set_ylabel("within-family J"); ax.legend(frameon=False, fontsize=7)
save(fig, "fig_family_j", "Within-family agreement $J$ under each family's own optimum, the global best and v1.")

# diagnostics
fig, ax = plt.subplots(figsize=(5, 3.6))
cols_ = [{"EM": "C0", "SM": "C1", "TQA": "C2", "FIN": "C3"}[f] for f in diag.family]
ax.scatter(diag.mean_score, diag.spread_across_models, c=cols_, s=18)
for r in diag.itertuples(): ax.annotate(r.dataset, (r.mean_score, r.spread_across_models), fontsize=5, xytext=(2, 2), textcoords="offset points")
ax.axvline(.95, c="k", ls=":", lw=.6); ax.set_xlabel("mean v1 score across models"); ax.set_ylabel("spread (max - min) across models")
save(fig, "fig_diagnostics_scatter", "Dataset diagnostics: mean score against spread across models; dotted line marks the ceiling flag.")

fig, ax = plt.subplots(figsize=(7, 2.6)); dd = diag.sort_values("ranking_self_stability_tau")
ax.bar(range(len(dd)), dd.ranking_self_stability_tau, color=[{"EM": "C0", "SM": "C1", "TQA": "C2", "FIN": "C3"}[f] for f in dd.family]); ax.set_xticks(range(len(dd))); ax.set_xticklabels(dd.dataset, rotation=60, ha="right", fontsize=6); ax.set_ylabel("self-stability tau")
save(fig, "fig_self_stability", "Self-stability of each dataset's model ranking (Kendall $\\tau$ between bootstrap halves) under v1.")

# ------------------------------------------------------------------ figures: run facts from the prediction cache
rows = []
for f in sorted((ROOT / "data" / "predictions").glob("*.jsonl")):
    m = f.stem
    for l in open(f):
        r = json.loads(l)
        if r.get("error"): continue
        rows.append({"model": m, "dataset": r["dataset"], "out_tokens": r.get("out_tokens", 0), "in_tokens": r.get("in_tokens", 0), "latency": r.get("latency_s", np.nan), "cost": r.get("cost_usd", 0.0),
                     "attempt": r.get("attempt") or 1, "cut": ("length" in str(r.get("finish")).lower() or "max_tokens" in str(r.get("finish")).lower())})
run = pd.DataFrame(rows); run = run[run.model.isin(models)]
facts = run.groupby("model").agg(answers=("dataset", "size"), cost_usd=("cost", "sum"), mean_out_tokens=("out_tokens", "mean"), median_latency_s=("latency", "median"),
                                 reasked_2500=("attempt", lambda a: (a == 2).sum()), reasked_8000=("attempt", lambda a: (a == 3).sum()), reasked_16000=("attempt", lambda a: (a == 4).sum()), still_cut=("cut", "sum")).loc[order_v1]
fig, axes = plt.subplots(1, 4, figsize=(10, 2.8))
for ax, c, lab in zip(axes, ["cost_usd", "mean_out_tokens", "median_latency_s", "still_cut"], ["cost (USD)", "mean output tokens", "median latency (s)", "answers cut at final budget"]):
    ax.barh(range(len(order_v1)), facts[c]); ax.set_yticks(range(len(order_v1))); ax.set_yticklabels([PRETTY[m] for m in order_v1], fontsize=6); ax.invert_yaxis(); ax.set_xlabel(lab)
save(fig, "fig_run_facts", "Run facts per model from the prediction cache: cost, output length, latency and answers still cut off at the final budget.")

fig, ax = plt.subplots(figsize=(6, 2.8)); x = np.arange(len(order_v1))
ax.bar(x, facts.reasked_2500, label="re-asked at 2,500"); ax.bar(x, facts.reasked_8000, bottom=facts.reasked_2500, label="re-asked at 8,000"); ax.bar(x, facts.reasked_16000, bottom=facts.reasked_2500 + facts.reasked_8000, label="re-asked at 16,000")
ax.set_xticks(x); ax.set_xticklabels([PRETTY[m] for m in order_v1], rotation=30, ha="right", fontsize=7); ax.set_ylabel("answers"); ax.legend(frameon=False, fontsize=7)
save(fig, "fig_truncation", "Truncation protocol: answers re-asked at 2,500, 8,000 and 16,000 output tokens per model.")

tok = run.groupby(["dataset", "model"]).out_tokens.mean().unstack().loc[datasets, order_v1]
fig, ax = plt.subplots(figsize=(9, 3.6)); im = ax.imshow(tok.T.values, cmap="magma", aspect="auto"); ax.set_xticks(range(len(datasets))); ax.set_xticklabels(datasets, rotation=60, ha="right", fontsize=6); ax.set_yticks(range(len(order_v1))); ax.set_yticklabels([PRETTY[m] for m in order_v1], fontsize=7)
fig.colorbar(im, ax=ax, shrink=.7, label="mean output tokens")
save(fig, "fig_tokens_heatmap", "Mean output tokens per model and dataset.")

# ------------------------------------------------------------------ copy existing paper figures
for p in (PAPER / "figures").glob("*.png"):
    shutil.copy(p, FIG / p.name)
for p in list(OUT.rglob("fig_*.pdf")):
    shutil.copy(p, FIG / p.name)
EXISTING = {"fig_j_histogram": "Distribution of $J$ over the 1,771 weightings with v1, the best and the plateau band.",
            "fig_landscape": "Sorted $J$ with v1 and the four single-ingredient corners.", "fig_marginals": "$J$ against each of the four weights.",
            "fig_nested": "In-bag vs out-of-bag $J$ of the selected weighting against v1.", "fig_plateau": "Bootstrap band over sorted weightings and the plateau boundary.",
            "fig_pareto": "Agreement $J$ against anchor correctness $\\rho$ for every weighting.", "fig_leaderboard_rules": "Bradley--Terry strengths with rank intervals under exact match, v1 and the best-$J$ weighting.",
            "fig_official_split": "Suite score vs post-stratified official estimate; matching F1 at the official ratio.", "fig_family_weights": "Deployed, global-optimum and per-family weights.",
            "fig_dataset_tau": "Kendall $\\tau$ between dataset rankings under v1.", "fig_designs": "Sampled designs against the exhaustive optimum."}
captions.update(EXISTING)

# ------------------------------------------------------------------ tables
def wfmt(r): return f"{r.w_f1:.2f} / {r.w_decay:.2f} / {r.w_precision:.2f} / {r.w_recall:.2f}"
g = grid.sort_values("J", ascending=False).head(25)
to_tex(pd.DataFrame({"rank": g["rank"], "F1 / decay / prec / rec": [wfmt(r) for r in g.itertuples()], "J": g.J, "J Kemeny": g.J_kemeny, "J Copeland": g.J_copeland, "J BT": g.J_bt, "tau native": g.tau_native, "min agree": g.min_agree}),
       "grid_top25", "The 25 best weightings by $J$ with the objective under the other pooling rules.")
spec = pd.concat([grid[grid.label.isin(["v1", "uniform"])], grid[(grid[W] == 1).any(axis=1)]]).drop_duplicates()
to_tex(pd.DataFrame({"label": spec.label.fillna(""), "F1 / decay / prec / rec": [wfmt(r) for r in spec.itertuples()], "rank": spec["rank"], "J": spec.J, "J Kemeny": spec.J_kemeny, "J Copeland": spec.J_copeland, "J BT": spec.J_bt, "tau native": spec.tau_native}),
       "grid_special_points", "v1, the uniform mix and the four single-ingredient corners on the lattice.")
to_tex(grid.J.describe(percentiles=[.01, .05, .1, .25, .5, .75, .9, .95, .99]).to_frame("J").T.reset_index(drop=True), "grid_quantiles", "Quantiles of $J$ over the lattice.", fmt="%.4f")
to_tex(pd.read_csv(OUT / "designs.csv").groupby("design").agg(["mean", "std"])[["best_J_found", "regret", "centred_L2_discrepancy", "min_pairwise_L1", "share_with_a_zero_weight", "best_rank_in_exhaustive"]].round(4).pipe(lambda d: d.set_axis([f"{a} {b}" for a, b in d.columns], axis=1)).reset_index(),
       "designs_full", "Sampled designs: mean and sd over 20 seeds of every coverage and performance measure.", fmt="%.4f")
nest = pd.DataFrame([{"quantity": k, "value": json.dumps(v) if isinstance(v, (dict, list)) else v} for k, v in nested.items() if k not in ("most_selected",)])
to_tex(nest, "nested_selection", "Every quantity saved by the nested item bootstrap.", longtable=True)
to_tex(plateau.sort_values("J_full", ascending=False).head(30)[["rank_full", "w_f1", "w_decay", "w_precision", "w_recall", "J_full", "J_boot_mean", "J_boot_sd", "J_boot_lo", "J_boot_hi", "p_vs_best", "J_oob_mean", "times_selected"]],
       "plateau_top30", "The 30 best weightings with their bootstrap statistics (full plateau table in data/selection/plateau.csv).")
to_tex(lodo.round(3), "lodo_full", "Leave-one-dataset-out: fitted weights and held-out $\\tau$ for every dataset and weight source.", longtable=True)
to_tex(lofo.round(3), "lofo_full", "Leave-one-family-out: fitted weights and held-out $\\tau$.")
to_tex(pd.DataFrame([{"family": f, "datasets": len(v["datasets"]), "best F1 / decay / prec / rec": f'{v["best_weights"]["f1"]:.2f} / {v["best_weights"]["decay"]:.2f} / {v["best_weights"]["precision"]:.2f} / {v["best_weights"]["recall"]:.2f}', "J own best": v["J_family_best"], "J global best": v["J_family_under_global_best"], "J v1": v["J_family_under_v1"], "L1 to global best": v["L1_distance_to_global_best"]} for f, v in per_family.items()]),
       "per_family", "Per-family optimum and the family's $J$ under its own optimum, the global best and v1.")
to_tex(pd.DataFrame(sens).T.reset_index().rename(columns={"index": "point"}).round(4), "sensitivity", "One-step sensitivity around v1 and the best weighting.", fmt="%.4f")
to_tex(corr[corr.label.notna()][["label", "rank", "w_f1", "w_decay", "w_precision", "w_recall", "J", "tau_native", "rho", "rho_ds", "auc", "wrong_mean", "hedge_gap"]].round(3), "anchors_rules", "Anchor correctness for the labelled rules.")
to_tex(corr[corr.pareto == True][["rank", "w_f1", "w_decay", "w_precision", "w_recall", "J", "rho", "auc", "wrong_mean", "hedge_gap"]].round(3), "pareto_front", "The $(J,\\rho)$ Pareto front.")
to_tex(op.reset_index().round(3), "anchor_operators", "Anchor operators: known utility, mean v1 score, exact-match rate and count.")
to_tex(rho_ds.round(3).reset_index().rename(columns={"index": "dataset"}), "rho_per_dataset", "Anchor correctness per dataset under three weightings.")
for r in RULES:
    d = LB[r].copy(); d["model"] = d.model.map(PRETTY)
    to_tex(d[["model", "bt_strength", "bt_se_vs_ref", "rank_bt", "bt_rank_lo95", "bt_rank_hi95", "p_first_bt", "rank_borda", "borda_rank_lo95", "borda_rank_hi95", "p_first_borda", "rank_kemeny", "rank_copeland", "rank_mean_z", "rank_rrf", "rank_family_balanced_z", "mean_score"]].round(3),
           f"leaderboard_{r}", f"Full leaderboard under rule {tex_escape(RULE_PRETTY[r])} (weights {PARAMS[r]['weights']}).".replace("{", "\\{").replace("}", "\\}") if False else f"Full leaderboard under rule {tex_escape(RULE_PRETTY[r])}; weights F1/decay/prec/rec = " + ("--" if PARAMS[r]["weights"] is None else " / ".join(f"{PARAMS[r]['weights'][k]:.2f}" for k in ["f1", "decay", "precision", "recall"])) + ".")
    fr = SIG[r]["friedman"]
    to_tex(pd.DataFrame([{"a": PRETTY[p["a"]], "b": PRETTY[p["b"]], "mean rank diff": p["mean_rank_diff"], "wins a": p["wins_a"], "wins b": p["wins_b"], "ties": p["ties"], "Wilcoxon p": p["wilcoxon_p"], "Holm p": p["wilcoxon_p_holm"], "Nemenyi": p["nemenyi_significant"], "sig .05": p["wilcoxon_significant_05"]} for p in fr["pairwise"]]).round(4),
           f"pairwise_{r}", f"Cross-dataset pairwise tests under rule {tex_escape(RULE_PRETTY[r])}: Friedman $\\chi^2$ = {fr['friedman_chi2']:.1f} ($p$ = {fr['friedman_p']:.1e}), Iman--Davenport $F$ = {fr['iman_davenport_F']:.1f}, Nemenyi CD = {fr['nemenyi_cd_05']:.2f}, Kendall's $W$ = {SIG[r]['kendall_W_datasets']['kendall_W']:.3f}.", fmt="%.4f", longtable=True)
    to_tex(PDM[r].loc[order_v1].rename(index=PRETTY).T.round(3).reset_index().rename(columns={"index": "dataset"}), f"per_dataset_mean_{r}", f"Mean score per dataset and model under rule {tex_escape(RULE_PRETTY[r])}.", longtable=True)
to_tex(PDS["v1_original"].loc[order_v1].rename(index=PRETTY).T.round(3).reset_index().rename(columns={"index": "dataset"}), "per_dataset_se_v1", "Standard error of the per-dataset mean under v1.", longtable=True)
to_tex(rule_agree.round(3).rename(index=RULE_PRETTY, columns=RULE_PRETTY).reset_index().rename(columns={"index": "rule"}), "rule_agreement", "Kendall $\\tau$ between the Bradley--Terry rankings of the rules.")
_rows = []
for r in RULES:
    d = LB[r].set_index("model"); _rows.append({"rule": RULE_PRETTY[r], **{PRETTY[m]: f"{int(d.loc[m, 'rank_bt'])} ({int(d.loc[m, 'rank_borda'])})" for m in order_v1}, "Friedman p": f"{SIG[r]['friedman']['friedman_p']:.1e}", "W": f"{SIG[r]['kendall_W_datasets']['kendall_W']:.2f}"})
to_tex(pd.DataFrame(_rows), "ranks_by_rule", "Bradley--Terry rank (Borda rank in brackets) under each reported rule, with the Friedman $p$ and Kendall's $W$ among datasets.")
_d = LB["v1_original"].set_index("model").loc[order_v1]
to_tex(pd.DataFrame({"rank": range(1, len(order_v1) + 1), "model": [PRETTY[m] for m in order_v1], "BT strength": _d.bt_strength.round(3), "SE": _d.bt_se_vs_ref.round(3), "BT 95%": [f"[{int(a)}, {int(b)}]" for a, b in zip(_d.bt_rank_lo95, _d.bt_rank_hi95)], "P(first) BT": _d.p_first_bt.round(2), "Borda rank": _d.rank_borda.astype(int), "Borda 95%": [f"[{int(a)}, {int(b)}]" for a, b in zip(_d.borda_rank_lo95, _d.borda_rank_hi95)], "P(first) Borda": _d.p_first_borda.round(2), "mean score": _d.mean_score.round(3)}), "leaderboard_headline", "Leaderboard under the deployed rule (v1 weights): Bradley--Terry strength $\\pm$ SE vs reference with the 95\\,\\% bootstrap rank interval, Borda rank with its interval, and the mean composite over the suite.")
_dsj = json.load(open(OUT / "designs_summary.json"))
to_tex(pd.DataFrame([{"design": k, "best J (mean)": _dsj["best_J_mean"][k], "sd": _dsj["best_J_sd"][k], "regret mean": _dsj["regret_mean"][k], "regret max": _dsj["regret_max"][k]} for k in _dsj["best_J_mean"]]), "designs_short", "Sampled designs at a budget of 100 weightings, 20 seeds each, against the exhaustive optimum.", fmt="%.4f")
to_tex(pd.DataFrame([{"family": f, "LOFO weights": f"{r.w_f1:.2f} / {r.w_decay:.2f} / {r.w_precision:.2f} / {r.w_recall:.2f}", "tau: LOFO weights": r.tau_heldout_mean} for f, r in ((row.held_out, row) for row in lofo[lofo.weights_from == "lodo_weights"].itertuples())]).merge(pd.DataFrame([{"family": row.held_out, "full best": row.tau_heldout_mean} for row in lofo[lofo.weights_from == "full_best"].itertuples()])).merge(pd.DataFrame([{"family": row.held_out, "v1": row.tau_heldout_mean} for row in lofo[lofo.weights_from == "v1"].itertuples()])), "lofo_short", "Leave-one-family-out: weights re-fitted without the family (F1 / decay / precision / recall) and the held-out family's $\\tau$ to the pooled rest under those weights, the full-data best and v1.")
o = off.copy(); o["model"] = o.model.map(PRETTY)
to_tex(o[["dataset", "model", "suite_mean", "official_estimate", "official_lo95", "official_hi95", "effective_n", "suite_f1_pos", "official_f1_pos", "official_f1_lo95", "official_f1_hi95", "official_positive_share"]].round(3), "official_split_v1", "Official-split estimates under v1 for every dataset and model.", longtable=True)
to_tex(off.groupby("dataset")[["suite_mean", "official_estimate", "suite_f1_pos", "official_precision_pos", "official_recall_pos", "official_f1_pos", "official_positive_share"]].mean().round(3).reset_index(), "official_split_by_dataset", "Official-split estimates under v1 averaged over the ten models.")
to_tex(pd.DataFrame([{"dataset": d, "majority-class accuracy": v["majority_class_accuracy"], "n": v["n"]} for d, v in mb.items()]), "majority_baselines", "Majority-class baselines for the boolean datasets.")
to_tex(diag.round(3), "diagnostics", "Dataset diagnostics under v1.", longtable=True)
cov = json.load(open(OUT / "coverage.json"))
to_tex(pd.DataFrame([{"dataset": d, "answered items": v["answered_items"], "items kept": v["items_kept"], "models used": len(v["models_used"]), "models dropped": ", ".join(v["models_dropped"]) or "--"} for d, v in cov.items() if not d.startswith("_")]), "coverage", "Coverage rule outcome per dataset.", longtable=True)
f2 = facts.copy(); f2.index = [PRETTY[m] for m in f2.index]; f2 = f2.reset_index().rename(columns={"index": "model"})
to_tex(f2.round(2), "run_facts", "Run facts per model from the prediction cache.", fmt="%.2f")
to_tex(fam_mean.round(3).rename(index=PRETTY, columns=FAM).reset_index().rename(columns={"model": "model"}), "family_scores", "Mean v1 composite per model within each family.")
ctab = comp.groupby("dataset").agg(items=("uid", "nunique"), answer_type=("answer_type", lambda s: s.mode().iloc[0]), native_metric=("native_metric", lambda s: s.mode().iloc[0]), family=("family", "first")).reset_index()
to_tex(ctab, "datasets", "Datasets: family, items answered, dominant answer type and native metric.", longtable=True)

# ------------------------------------------------------------------ copy data
for p in OUT.rglob("*"):
    if p.is_file() and p.suffix in {".csv", ".json", ".npz", ".md", ".tex"} and "fig_" not in p.name:
        dst = DAT / p.relative_to(OUT); dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy(p, dst)
shutil.copy(ROOT / "v2_gridsearch" / "REPORT.md", DAT / "REPORT.md")
shutil.copy(ROOT / "data" / "pool" / "_official_strata.json", DAT / "official_strata.json")
shutil.copy(PAPER / "DATASETS_TABLE.md", DAT / "DATASETS_TABLE.md")
facts.to_csv(DAT / "run_facts.csv"); fam_mean.to_csv(DAT / "family_scores.csv"); rho_ds.to_csv(DAT / "rho_per_dataset.csv"); op.to_csv(DAT / "anchor_operators.csv")

# ------------------------------------------------------------------ main.tex
src = (PAPER / "summary_results.tex").read_text()
body = src[src.index(r"\section{Setup}"): src.index(r"\end{document}")]
pre = src[: src.index(r"\begin{document}")]
pre = pre.replace(r"\graphicspath{{figures/}}", r"\graphicspath{{figures/}}")
# ---- reading guide per figure (appendix A), numbers filled from the data
import sys as _sys; _sys.path.insert(0, str(PAPER / "scripts"))
from figure_explanations_v2 import EXPLANATIONS
_dj = json.load(open(OUT / "diagnostics" / "diagnostics.json")); _pt = np.array(_dj["pairwise_tau"]); _iu = np.triu_indices(len(_pt), 1)
_s = SIG["v1_original"]; _lb = LB["v1_original"].sort_values("rank_bt"); _d = draws["J_out_sel"] - draws["J_out_v1"]
_marg = max(grid.groupby(w).J.mean().max() - grid.groupby(w).J.mean().min() for w in W)
_tau_cols = [c for c in grid.columns if c.startswith("tau_") and c != "tau_native"]
_stab = diag.sort_values("ranking_self_stability_tau")
_off = OFF["v1_original"].groupby("dataset").agg(suite=("suite_mean", "mean"), official=("official_estimate", "mean"), f1p=("suite_f1_pos", "mean"), f1o=("official_f1_pos", "mean"))
_nsp = pd.Series(_s["n_significant_pairs_per_dataset"])
N = {"Jmin": f"{grid.J.min():.3f}", "Jmax": f"{grid.J.max():.3f}", "v1J": f"{v1_row.J:.3f}", "bestJ": f"{best_row.J:.3f}", "plateau": f"{nested['plateau_size']:,}", "practical": f"{nested['practical_plateau_size_within_0.02']:,}",
     "v1rank": f"{int(v1_row['rank']):,}", "Jrange": f"{grid.J.max() - grid.J.min():.3f}", "marg_max": f"{_marg:.3f}", "v1rank_bt": f"{int((grid.J_bt > v1_row.J_bt).sum() + 1):,}", "v1rank_kemeny": f"{int((grid.J_kemeny > v1_row.J_kemeny).sum() + 1):,}",
     "rho_tau_native": f"{spearmanr(grid.tau_native, grid.J).correlation:+.2f}" if False else f"{grid[['tau_native', 'J']].corr(method='spearman').iloc[0, 1]:+.2f}", "v1_tau_native": f"{v1_row.tau_native:.3f}", "n_neg": str(int(sum(v1_row[c] < 0 for c in _tau_cols))),
     "max_first": str(int((PDM["v1_original"].loc[all_models if False else list(PDM["v1_original"].index)].rank(ascending=False, axis=0) == 1).sum(1).max())), "W": f"{_s['kendall_W_datasets']['kendall_W']:.2f}",
     "gap": f"{nested['optimism_gap']:.3f}", "oob_diff": f"{_d.mean():+.3f}", "oob_lo": f"{np.percentile(_d, 2.5):+.3f}", "oob_hi": f"{np.percentile(_d, 97.5):+.3f}", "share_ahead": f"{100 * (_d > 0).mean():.0f}\\,\\%",
     "ndistinct": str(nested["n_distinct_selected"]), "sd_weights": ", ".join(f"{k} {v:.2f}" for k, v in nested["selected_weights_sd"].items()), "v1p": f"{nested['v1_p_vs_best']:.2f}", "top_sel": str(int(plateau.times_selected.max())),
     "sens_v1": f"{sens['v1']['J_max'] - sens['v1']['J_min']:.3f}", "sens_best": f"{sens['best']['J_max'] - sens['best']['J_min']:.3f}",
     "lodo_refit": f"{piv['lodo_weights'].mean():+.2f}", "lodo_best": f"{piv['full_best'].mean():+.2f}", "lodo_v1": f"{piv['v1'].mean():+.2f}", "lodo_wins": str(int((piv['lodo_weights'] > piv['v1']).sum())), "lodo_losses": str(int((piv['lodo_weights'] < piv['v1']).sum())),
     "design_regret": f"{designs.regret.max():.3f}", "design_worst_rank": str(int(designs.best_rank_in_exhaustive.max())),
     "rho_bestJ": f"{corr_json['best_J']['rho']:.3f}", "rho_v1": f"{corr_json['v1']['rho']:.3f}", "rho_best": f"{corr_json['best_rho']['rho']:.3f}", "J_rho_corr": f"{corr_json['spearman_J_vs_rho_across_grid']:+.2f}", "auc_min": f"{corr.auc.min():.3f}", "auc_max": f"{corr.auc.max():.3f}",
     "last": PRETTY[_lb.model.iloc[-1]], "p_first_bt": f"{_lb.p_first_bt.iloc[0]:.2f}", "rule_tau_min": f"{rule_agree.values[np.triu_indices(len(rule_agree), 1)].min():.2f}", "cd": f"{_s['friedman']['nemenyi_cd_05']:.2f}",
     "n_zero": str(int((_nsp == 0).sum())), "n_20": str(int((_nsp >= 20).sum())), "off_shift": f"{(_off.official - _off.suite).abs().max():.2f}", "off_f1drop": f"{(_off.f1p - _off.f1o).max():.2f}",
     "mean_pair_tau": f"{_pt[_iu].mean():+.2f}", "n_ceiling": str(int(diag.ceiling.sum())), "stab_min": f"{_stab.ranking_self_stability_tau.iloc[0]:.2f}", "stab_min_ds": _stab.dataset.iloc[0].replace("_", "\\_"), "stab_max": f"{_stab.ranking_self_stability_tau.iloc[-1]:.2f}", "stab_max_ds": _stab.dataset.iloc[-1].replace("_", "\\_")}

def explain(name):
    t = EXPLANATIONS.get(name, "")
    for k, v in N.items(): t = t.replace("«" + k + "»", v)
    return t.replace("\n", " ")

app = ["\\clearpage\n\\appendix\n\\section{All figures, with a reading guide}\n\\label{app:figures}\nEvery figure that can be drawn from the saved outputs, each followed by what it encodes, how to read it and what it shows. Source data for each is in \\texttt{data/}.\n"]
for name in sorted(captions):
    app.append(f"\\begin{{figure}}[htbp]\\centering\\includegraphics[width=0.9\\textwidth]{{{name}.png}}\\caption{{{captions[name]}}}\\label{{figall:{name}}}\\end{{figure}}\n\\noindent{{\\small {explain(name)}}}\n\\clearpage\n")
app.append("\\clearpage\n\\section{All tables}\n\\label{app:tables}\nEvery saved table, exported from \\texttt{data/}. Each is a separate file under \\texttt{tables/}; include any of them in the main text with \\texttt{\\textbackslash input}.\n")
for name in sorted(table_caps):
    app.append(f"\\input{{tables/{name}.tex}}\n\\clearpage\n")
pre = pre.replace(r"\usepackage[T1]{fontenc}", r"\usepackage{pdflscape}" + "\n" + r"\usepackage[T1]{fontenc}")
pre = pre.replace(r"\title{Summary Results}", r"\title{Summary Results, v2}")
main = pre + "\\usepackage{longtable}\n\\begin{document}\n\\maketitle\n\n" + body + "\n".join(app) + "\n\\end{document}\n"
main = main.replace("\\usepackage{longtable}\n\\begin{document}", "\\begin{document}") if "longtable" in pre else main
(PKG / "main.tex").write_text(main)

readme = f"""# Summary report, v2 (Overleaf package): audit of the deployed data-matching judge

Upload this folder (or the zip) as a new Overleaf project; compile `main.tex` with pdfLaTeX.

* `main.tex` - Setup and Results sections, then an appendix that includes every figure and every table.
* `figures/` - {len(list(FIG.glob('*.png')))} PNG figures (plus PDF versions where generated). Captions are in `main.tex`.
* `tables/` - {len(list(TAB.glob('*.tex')))} LaTeX tables, one file each; `\\input{{tables/<name>.tex}}`.
* `data/` - every output file of the final v2 run (CSV / JSON / NPZ), the generated report `REPORT.md`, the official census and the dataset table.

Generated by `FINAL_v2/paper/scripts/make_overleaf_package.py` from the run of {json.load(open(OUT / "run_manifest.json"))["generated"]} (31 datasets x {len(order_v1)} models).
"""
(PKG / "README.md").write_text(readme)
zp = PAPER / "v2_overleaf.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for p in PKG.rglob("*"):
        if p.is_file(): z.write(p, p.relative_to(PKG))
print(f"figures {len(captions)}  tables {len(table_caps)}  data files {sum(1 for p in DAT.rglob('*') if p.is_file())}  zip {zp.stat().st_size/1e6:.1f} MB")
