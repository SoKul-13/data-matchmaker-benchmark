"""Publication figures for the v2 audit -> paper/v2/figures_paper/ (PDF + PNG) with FIGURES.md and figures_paper.tex.
Design: one accent for the thing to look at, greys for context, the four task families in a validated categorical palette,
thin marks, hairline grid, direct labels only where they carry the point.  Run from FINAL_v2:  uv run python paper/scripts/make_paper_figures.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import gaussian_kde

ROOT = Path(__file__).resolve().parents[2]; OUT = ROOT / "v2_gridsearch" / "output"; PRED = ROOT / "data" / "predictions"
DST = ROOT / "paper" / "v2" / "figures_paper"; DST.mkdir(parents=True, exist_ok=True)

# ---- tokens (reference palette, validated: node validate_palette.js "#2a78d6,#eb6834,#1baf7a,#eda100" -> all checks pass)
ACC = "#2a78d6"; ACC2 = "#eb6834"; INK = "#0b0b0b"; INK2 = "#52514e"; MUTE = "#9b9a94"; GRID = "#e4e3de"; SURF = "#ffffff"; LIGHT = "#c3c2b7"
FAMC = {"EM": "#2a78d6", "SM": "#eb6834", "TQA": "#1baf7a", "FIN": "#eda100"}; FAMN = {"EM": "entity matching", "SM": "schema matching", "TQA": "table QA", "FIN": "finance"}
SEQ = LinearSegmentedColormap.from_list("seq", ["#eef3fb", "#2a78d6", "#0c3a78"]); DIV = LinearSegmentedColormap.from_list("div", ["#eb6834", "#f3f2ee", "#2a78d6"])
PRETTY = {"gemini-3.1-pro": "Gemini 3.1 Pro", "claude-opus-5": "Claude Opus 5", "claude-sonnet-5": "Claude Sonnet 5", "gpt-5.5": "GPT-5.5", "gpt-5.4-mini": "GPT-5.4-mini", "gemini-3.8-flash": "Gemini 3.8 Flash", "grok-4": "Grok 4",
          "deepseek-chat": "DeepSeek-chat", "deepseek-r1": "DeepSeek-R1", "gpt-oss-120b": "gpt-oss-120b", "llama-3.3-70b": "Llama 3.3 70B"}
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"], "font.size": 7.5, "axes.labelsize": 7.5, "axes.titlesize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
                     "axes.edgecolor": LIGHT, "axes.linewidth": 0.6, "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2, "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "grid.color": GRID, "grid.linewidth": 0.5, "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
                     "legend.frameon": False, "pdf.fonttype": 42, "ps.fonttype": 42, "figure.dpi": 110, "savefig.dpi": 300, "figure.facecolor": SURF, "axes.facecolor": SURF})
SINGLE, DOUBLE = 3.4, 7.0
W = ["w_f1", "w_decay", "w_precision", "w_recall"]; WN = ["F1", "decay", "precision", "recall"]
CAP = []


def save(fig, name, cap, place):
    fig.savefig(DST / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02); fig.savefig(DST / f"{name}.png", bbox_inches="tight", pad_inches=0.02); plt.close(fig); CAP.append((name, cap, place))


def wstr(r): return f"F1 {r['w_f1']:.2f}, decay {r['w_decay']:.2f}, P {r['w_precision']:.2f}, R {r['w_recall']:.2f}"


# ---- data
grid = pd.read_csv(OUT / "grid_exhaustive.csv"); plateau = pd.read_csv(OUT / "selection" / "plateau.csv"); nested = json.load(open(OUT / "selection" / "nested.json")); draws = np.load(OUT / "selection" / "nested_draws.npz")
corr = pd.read_csv(OUT / "anchors" / "correctness.csv"); cj = json.load(open(OUT / "anchors" / "correctness.json")); anch = pd.read_csv(OUT / "anchors" / "anchor_components.csv"); comp = pd.read_csv(OUT / "components_v1.csv")
lodo = pd.read_csv(OUT / "selection" / "lodo.csv"); pfam = json.load(open(OUT / "selection" / "per_family.json")); diag = pd.read_csv(OUT / "diagnostics" / "dataset_diagnostics.csv"); dj = json.load(open(OUT / "diagnostics" / "diagnostics.json"))
RULES = ["em_only", "v1_original", "top1", "top2", "top3", "top4", "top5", "best_anchor", "pareto_knee"]; RP = {"em_only": "exact match", "v1_original": "v1 (deployed)", "top1": "best J", "top2": "2nd J", "top3": "3rd J", "top4": "4th J", "top5": "5th J", "best_anchor": "best ρ", "pareto_knee": "knee"}
LB = {r: pd.read_csv(OUT / "leaderboards" / r / "leaderboard.csv") for r in RULES}; SIG = json.load(open(OUT / "leaderboards" / "v1_original" / "significance.json")); OFF = pd.read_csv(OUT / "leaderboards" / "v1_original" / "official_split_estimates.csv")
PDM = pd.read_csv(OUT / "leaderboards" / "v1_original" / "per_dataset_mean.csv", index_col=0)
models = list(LB["v1_original"].model); order = LB["v1_original"].sort_values("rank_bt").model.tolist(); datasets = list(PDM.columns); fam_of = dict(zip(diag.dataset, diag.family))
v1 = grid[grid.label == "v1_original"].iloc[0]; best = grid.sort_values("J", ascending=False).iloc[0]
comp["v1"] = .35 * comp.f1 + .35 * comp.decay + .15 * comp.precision + .15 * comp.recall; anch["v1"] = .35 * anch.f1 + .35 * anch.decay + .15 * anch.precision + .15 * anch.recall

# ================================================================ F1 landscape
pl = plateau.sort_values("J_full", ascending=False).reset_index(drop=True); x = np.arange(len(pl)) + 1
fig, (a, b_) = plt.subplots(1, 2, figsize=(DOUBLE, 2.3), gridspec_kw={"width_ratios": [2.2, 1]})
a.fill_between(x, pl.J_boot_lo, pl.J_boot_hi, color=ACC, alpha=.12, lw=0, label="95 % item-bootstrap band")
a.plot(x, pl.J_full, color=ACC, lw=1.2, label="J (full data)")
a.plot(x, pl.J_oob_mean, color=MUTE, lw=1, label="mean out-of-bag J")
rk_v1 = int(v1["rank"]); a.scatter([rk_v1], [v1.J], s=28, color=ACC2, zorder=5); a.annotate("v1 (deployed)\nrank 1,483 of 1,771", (rk_v1, v1.J), xytext=(-10, -128), textcoords="offset points", fontsize=7, color=ACC2, arrowprops={"arrowstyle": "-", "color": ACC2, "lw": .6})
for lab, txt, off in [("only_f1", "F1 only", (-4, 7)), ("only_decay", "decay only", (-22, -11)), ("only_precision", "precision only", (-30, -24)), ("only_recall", "recall only", (4, -13)), ("uniform", "uniform", (-8, -11))]:
    r = grid[grid.label == lab].iloc[0]; a.scatter([int(r["rank"])], [r.J], s=12, facecolor=SURF, edgecolor=INK2, lw=.7, zorder=5); a.annotate(txt, (int(r["rank"]), r.J), xytext=off, textcoords="offset points", fontsize=6, color=INK2)
a.axhspan(pl.J_full.max() - .02, pl.J_full.max(), color=GRID, alpha=.5, lw=0); a.text(20, pl.J_full.max() + .004, "shaded: within 0.02 of the best (1,720 of 1,771 weightings)", ha="left", va="bottom", fontsize=6.5, color=INK2); a.set_ylim(a.get_ylim()[0], pl.J_full.max() + .018)
a.set_xlabel("weighting, sorted by J (1 = best)"); a.set_ylabel("agreement objective J"); a.set_xlim(0, 1790); a.legend(loc="lower left", fontsize=6.5)
b_.hist(grid.J, bins=40, color=ACC, alpha=.85, lw=0); b_.axvline(v1.J, color=ACC2, lw=1.2); b_.text(v1.J - .001, b_.get_ylim()[1] * .95, "v1", color=ACC2, ha="right", va="top", fontsize=7); b_.axvline(best.J, color=INK, lw=.8); b_.text(best.J - .0005, b_.get_ylim()[1] * .95, "best", ha="right", va="top", fontsize=7)
b_.set_xlabel("J"); b_.set_ylabel("weightings"); b_.set_xlim(grid.J.min() - .003, grid.J.max() + .003)
for ax, t in [(a, "a"), (b_, "b")]: ax.text(-0.02, 1.04, t, transform=ax.transAxes, fontweight="bold", fontsize=9)
save(fig, "fig01_landscape", "The agreement objective over every weighting of the four ingredients. (a) All 1,771 step-0.05 weightings sorted by J, with the 95 % item-bootstrap band and the mean out-of-bag J; the deployed weights (v1) and the single-ingredient corners are marked. (b) The distribution of J: the whole lattice spans 0.39–0.42, less than the bootstrap width of any single point.", "Fig. 1, Results §1 (double column)")

# ================================================================ F2 marginals
fig, axes = plt.subplots(1, 4, figsize=(DOUBLE, 1.9), sharey=True)
for ax, w, n in zip(axes, W, WN):
    ax.scatter(grid[w] + np.random.default_rng(0).uniform(-.008, .008, len(grid)), grid.J, s=2.5, color=LIGHT, lw=0, rasterized=True)
    m = grid.groupby(w).J.mean(); ax.plot(m.index, m.values, color=ACC, lw=1.4); ax.scatter([v1[w]], [v1.J], s=22, color=ACC2, zorder=5)
    ax.set_xlabel(f"weight on {n}"); ax.set_xticks([0, .5, 1]); ax.set_xlim(-.04, 1.04)
axes[0].set_ylabel("J"); axes[0].annotate("v1", (v1[W[0]], v1.J), xytext=(6, 6), textcoords="offset points", color=ACC2, fontsize=7)
axes[1].text(.98, .04, "mean J at each weight level", transform=axes[1].transAxes, ha="right", fontsize=6.5, color=ACC)
save(fig, "fig02_marginals", "J against each ingredient's weight over the full lattice (grey) with the mean at each weight level (blue). No weight has a slope worth acting on: the largest whole-range swing of the mean is 0.018 (precision).", "Fig. 2 or appendix (double column)")

# ================================================================ F3 honest selection
sel_in = draws["J_in"].max(1); sel_out = draws["J_out_sel"]; v1_out = draws["J_out_v1"]; d = sel_out - v1_out
fig, (a, b_) = plt.subplots(1, 2, figsize=(DOUBLE, 2.2), gridspec_kw={"width_ratios": [1.4, 1]})
xs = np.linspace(.22, .48, 400)
for arr, col, lab, ls in [(sel_in, ACC, "selected weighting, in-bag J", "-"), (sel_out, ACC, "selected weighting, out-of-bag J", "--"), (v1_out, ACC2, "v1, out-of-bag J", "-")]:
    k = gaussian_kde(arr)(xs); a.plot(xs, k, color=col, lw=1.3, ls=ls, label=lab); a.fill_between(xs, 0, k, color=col, alpha=.08, lw=0)
a.annotate("", xy=(sel_out.mean(), 6.5), xytext=(sel_in.mean(), 6.5), arrowprops={"arrowstyle": "<->", "color": INK2, "lw": .7}); a.text((sel_in.mean() + sel_out.mean()) / 2, 7.0, f"optimism gap {nested['optimism_gap']:.3f}", ha="center", fontsize=6.5, color=INK2)
a.set_xlabel("J"); a.set_ylabel("density over 1,000 resamples"); a.legend(loc="upper left", fontsize=6.3); a.set_ylim(0, a.get_ylim()[1] * 1.15)
b_.hist(d, bins=40, color=ACC, alpha=.85, lw=0); b_.axvline(0, color=INK, lw=.8); lo, hi = np.percentile(d, [2.5, 97.5]); b_.axvspan(lo, hi, color=ACC2, alpha=.12, lw=0)
b_.text(.03, .95, f"mean {d.mean():+.3f}\n95 % [{lo:+.3f}, {hi:+.3f}]\nselected ahead in {100*(d > 0).mean():.0f} %", transform=b_.transAxes, va="top", fontsize=6.8, color=INK2)
b_.set_xlabel("out-of-bag J: selected − v1"); b_.set_ylabel("resamples")
for ax, t in [(a, "a"), (b_, "b")]: ax.text(-0.02, 1.04, t, transform=ax.transAxes, fontweight="bold", fontsize=9)
save(fig, "fig03_honest_selection", "Honest selection with a nested item bootstrap (B = 1,000). (a) The weighting chosen on in-bag items looks better than it is: its out-of-bag J falls below v1's. (b) The paired out-of-bag difference to v1 is centred near zero, with 95 % interval through zero.", "Fig. 3, Results §2 (double column)")

# ================================================================ F4 selected weights
chosen = draws["chosen"]; wsel = grid.iloc[chosen][W].values
fig, axes = plt.subplots(1, 4, figsize=(DOUBLE, 1.7), sharey=True)
for ax, j, n in zip(axes, range(4), WN):
    ax.hist(wsel[:, j], bins=np.arange(-.025, 1.05, .05), color=ACC, alpha=.85, lw=0); ax.axvline(v1[W[j]], color=ACC2, lw=1.2); ax.set_xlabel(f"selected weight on {n}"); ax.set_xticks([0, .5, 1])
    ax.text(.97, .93, f"mean {wsel[:, j].mean():.2f}\nsd {wsel[:, j].std():.2f}", transform=ax.transAxes, ha="right", va="top", fontsize=6.5, color=INK2)
axes[0].set_ylabel("resamples"); axes[0].text(v1[W[0]] + .03, axes[0].get_ylim()[1] * .6, "v1", color=ACC2, fontsize=7)
save(fig, "fig04_selected_weights", "Which weighting wins depends on which items are drawn: the in-bag best over 1,000 resamples spreads over the whole simplex (608 distinct winners); orange = the deployed value.", "Fig. 3 companion or appendix (double column)")

# ================================================================ F5 pareto
fig, ax = plt.subplots(figsize=(SINGLE, 2.9))
ax.scatter(corr.J, corr.rho, s=5, color=LIGHT, lw=0, rasterized=True, label="all 1,771 weightings")
pf = corr[corr.pareto == True].sort_values("J"); ax.plot(pf.J, pf.rho, color=INK2, lw=.8, zorder=3); ax.scatter(pf.J, pf.rho, s=14, facecolor=SURF, edgecolor=INK2, lw=.8, zorder=4, label="Pareto front")
pts = [("v1 (deployed)", cj["v1"], ACC2, (-55, -14)), ("best J", cj["best_J"], ACC, (6, -12)), ("best ρ", cj["best_rho"], ACC, (-40, 6)), ("Pareto knee", cj["pareto_knee"], INK, (6, 6))]
for lab, v, col, off in pts:
    ax.scatter([v["J"]], [v["rho"]], s=34, color=col, zorder=6); ax.annotate(lab, (v["J"], v["rho"]), xytext=off, textcoords="offset points", fontsize=7, color=col, arrowprops={"arrowstyle": "-", "lw": .5, "color": col})
for lab, txt in [("only_f1", "F1 only"), ("only_decay", "decay only"), ("only_precision", "precision only"), ("only_recall", "recall only")]:
    r = corr[corr.label == lab].iloc[0]; ax.scatter([r.J], [r.rho], s=12, facecolor=SURF, edgecolor=INK2, lw=.7, zorder=5); ax.annotate(txt, (r.J, r.rho), xytext=(4, -3), textcoords="offset points", fontsize=6, color=INK2)
ax.set_xlabel("agreement among datasets, J"); ax.set_ylabel("correctness on 31,380 anchors, Spearman ρ"); ax.grid(True, axis="both")
ax.text(.03, .30, f"Spearman(J, ρ) over the grid = {cj['spearman_J_vs_rho_across_grid']:+.2f}", transform=ax.transAxes, fontsize=6.5, color=INK2); ax.legend(loc="lower right", fontsize=6.3)
save(fig, "fig05_agreement_vs_correctness", "Agreement is not correctness. Every weighting placed by its agreement objective J and its Spearman ρ against the known utility of 31,380 synthetic answers; the two criteria anti-correlate, the best-J weighting is among the worst by ρ, and the deployed v1 sits near the ρ optimum.", "Fig. 4, Results §3 (single column)")

# ================================================================ F6 operators dumbbell
op = anch.groupby("op").agg(utility=("utility", "mean"), v1=("v1", "mean"), em=("em", "mean"), n=("v1", "size")).sort_values("utility")
fig, ax = plt.subplots(figsize=(SINGLE, 3.4)); y = np.arange(len(op))
for yi, r in zip(y, op.itertuples()): ax.plot([r.utility, r.v1], [yi, yi], color=GRID, lw=2.2, zorder=1, solid_capstyle="round")
ax.scatter(op.utility, y, s=22, color=INK2, zorder=3, label="known utility"); ax.scatter(op.v1, y, s=22, color=ACC, zorder=4, label="mean v1 score"); ax.scatter(op.em, y, s=16, facecolor=SURF, edgecolor=ACC2, lw=.9, zorder=5, label="exact match")
ax.set_yticks(y); ax.set_yticklabels([f"{o.replace('_', ' ')}  (n={n:,})" for o, n in zip(op.index, op.n)], fontsize=6.5); ax.set_xlabel("score / utility"); ax.set_xlim(-.03, 1.03); ax.grid(True, axis="x"); ax.grid(False, axis="y"); ax.legend(loc="lower right", fontsize=6.3)
save(fig, "fig06_anchor_operators", "What the judge rewards. Each row is one perturbation operator applied to the gold answers (n anchors); the grey point is its known utility, blue the mean score under the deployed rule, orange exact match. The lexical rule is generous to superset and shuffled lists and severe on typos and medium near misses; these are the cases human labels must settle.", "Fig. 5, Results §3 (single column)")

# ================================================================ F7 leaderboard small multiples
show = ["em_only", "v1_original", "top1", "best_anchor"]
fig, axes = plt.subplots(1, 4, figsize=(DOUBLE, 2.6), sharey=True)
yy = np.arange(len(order))[::-1]
for ax, r in zip(axes, show):
    d_ = LB[r].set_index("model").loc[order]; first = d_.rank_bt.idxmin()
    ax.hlines(yy, 0, d_.bt_strength, color=GRID, lw=1.2); ax.errorbar(d_.bt_strength, yy, xerr=d_.bt_se_vs_ref, fmt="none", ecolor=INK2, elinewidth=.7, capsize=0)
    ax.scatter(d_.bt_strength, yy, s=[34 if m == first else 18 for m in order], color=[ACC2 if m == first else ACC for m in order], zorder=4)
    for yi, m in zip(yy, order): ax.text(ax.get_xlim()[1] if False else d_.bt_strength.max() + .03, yi, f"{int(d_.loc[m, 'rank_bt'])} [{int(d_.loc[m, 'bt_rank_lo95'])}–{int(d_.loc[m, 'bt_rank_hi95'])}]", va="center", fontsize=6, color=INK2)
    ax.axvline(0, color=LIGHT, lw=.6); ax.set_title(RP[r], fontsize=8); ax.set_xlabel("Bradley–Terry strength"); ax.grid(True, axis="x"); ax.grid(False, axis="y"); ax.set_xlim(d_.bt_strength.min() - .03, d_.bt_strength.max() + .12)
axes[0].set_yticks(yy); axes[0].set_yticklabels([PRETTY[m] for m in order], fontsize=7)
save(fig, "fig07_leaderboard_rules", "The leaderboard under four scoring rules, pooled by Bradley–Terry over item-level wins (± SE vs reference); orange = first place; the text gives the rank with its 95 % bootstrap interval. The ends are fixed under every rule; the order of the top three depends on the rule.", "Fig. 6, Results §4 (double column)")

# ================================================================ F8 rank matrix
R = pd.DataFrame({RP[r]: LB[r].set_index("model").loc[order, "rank_bt"].astype(int) for r in RULES}); B = pd.DataFrame({RP[r]: LB[r].set_index("model").loc[order, "rank_borda"].astype(int) for r in RULES})
fig, ax = plt.subplots(figsize=(SINGLE, 2.9)); ax.imshow(R.values, cmap=SEQ.reversed(), vmin=1, vmax=10, aspect="auto"); ax.grid(False)
for i in range(R.shape[0]):
    for j in range(R.shape[1]): v = R.values[i, j]; ax.text(j, i, f"{v}" + (f" ({B.values[i, j]})" if B.values[i, j] != v else ""), ha="center", va="center", fontsize=6.3, color=SURF if v <= 4 else INK)
ax.set_xticks(range(R.shape[1])); ax.set_xticklabels(R.columns, rotation=45, ha="right", fontsize=6.5); ax.set_yticks(range(len(order))); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=7); ax.tick_params(length=0)
for s in ax.spines.values(): s.set_visible(False)
save(fig, "fig08_rank_matrix", "Bradley–Terry rank of every model under every reported rule (Borda rank in brackets where it differs). Dark = better. Rows 4–10 barely move; rows 1–3 swap with the rule.", "Fig. 6 companion or appendix (single column)")

# ================================================================ F9 dataset agreement heatmap
names = dj.get("datasets", datasets); T = pd.DataFrame(dj["pairwise_tau"], index=names, columns=names)
fam_order = ["EM", "SM", "TQA", "FIN"]; ordn = [d_ for f in fam_order for d_ in names if fam_of[d_] == f]; T = T.loc[ordn, ordn]
fig, ax = plt.subplots(figsize=(SINGLE, 3.3)); im = ax.imshow(T.values, cmap=DIV, vmin=-1, vmax=1, aspect="equal"); ax.grid(False)
ax.set_xticks(range(len(ordn))); ax.set_xticklabels(ordn, rotation=90, fontsize=4.8); ax.set_yticks(range(len(ordn))); ax.set_yticklabels(ordn, fontsize=4.8); ax.tick_params(length=0)
for lab in ax.get_xticklabels() + ax.get_yticklabels(): lab.set_color(FAMC[fam_of[lab.get_text()]])
start = 0
for f in fam_order:
    n = sum(1 for d_ in ordn if fam_of[d_] == f); ax.add_patch(plt.Rectangle((start - .5, start - .5), n, n, fill=False, edgecolor=INK, lw=.7)); ax.text(start + n / 2 - .5, -1.3 if f in ("EM", "TQA") else -3.0, FAMN[f], ha="center", fontsize=6, color=FAMC[f]); start += n
for s in ax.spines.values(): s.set_visible(False)
cb = fig.colorbar(im, ax=ax, shrink=.6, pad=.02); cb.set_label("Kendall τ between dataset rankings", fontsize=6.5); cb.ax.tick_params(labelsize=6); cb.outline.set_visible(False)
save(fig, "fig09_dataset_agreement", "How much the 31 datasets agree about the model ranking under v1: Kendall τ between every pair, grouped by family (boxes). Agreement is moderate inside families and weak across them (Kendall's W = 0.26).", "Fig. 7, Results §4 (single column)")

# ================================================================ F10 LODO dot plot
L_ = lodo[lodo.kind == "dataset"]; piv = L_.pivot(index="held_out", columns="weights_from", values="tau_heldout_mean").sort_values("v1")
fig, ax = plt.subplots(figsize=(SINGLE, 3.6)); y = np.arange(len(piv))
for yi, (dname, r) in zip(y, piv.iterrows()): ax.plot([min(r.lodo_weights, r.v1), max(r.lodo_weights, r.v1)], [yi, yi], color=GRID, lw=2, zorder=1)
ax.scatter(piv.lodo_weights, y, s=18, facecolor=SURF, edgecolor=INK2, lw=.8, zorder=3, label="weights re-fitted without the dataset"); ax.scatter(piv.v1, y, s=18, color=ACC, zorder=4, label="v1 (deployed)")
ax.axvline(0, color=LIGHT, lw=.6); ax.set_yticks(y); ax.set_yticklabels(piv.index, fontsize=6)
for lab in ax.get_yticklabels(): lab.set_color(FAMC[fam_of[lab.get_text()]])
ax.set_xlabel("τ of the held-out dataset to the pooled ranking of the other 30"); ax.grid(True, axis="x"); ax.grid(False, axis="y"); ax.legend(loc="lower right", fontsize=6.2)
ax.text(.02, .98, f"mean: re-fitted {piv.lodo_weights.mean():+.2f}, v1 {piv.v1.mean():+.2f}", transform=ax.transAxes, va="top", fontsize=6.5, color=INK2)
save(fig, "fig10_leave_one_dataset_out", "Transfer. For each dataset held out, how well the other 30 predict its ranking under weights re-fitted without it (hollow) and under the deployed weights (blue); label colour = family. Re-fitting does not help, and the same handful of sets resist prediction under any weights.", "Fig. 8, Results §5 (single column)")

# ================================================================ F11 family weights stacked
rows_ = [("v1 (deployed)", [v1[w] for w in W]), ("global best", [best[w] for w in W])] + [(FAMN[f], [pfam[f]["best_weights"][k] for k in ["f1", "decay", "precision", "recall"]]) for f in fam_order]
fig, ax = plt.subplots(figsize=(SINGLE, 2.0)); y = np.arange(len(rows_))[::-1]; cols = [ACC, "#0c3a78", "#9dbfea", LIGHT]
for yi, (lab, ws) in zip(y, rows_):
    left = 0
    for wv, c, n in zip(ws, cols, WN):
        if wv > 0:
            ax.barh(yi, wv - .006, left=left + .003, height=.62, color=c, lw=0)
            if wv >= .25: ax.text(left + wv / 2, yi, f"{n} {wv:.2f}", ha="center", va="center", fontsize=6, color=SURF if c in (ACC, "#0c3a78") else INK)
            elif wv >= .1: ax.text(left + wv / 2, yi, f"{n[0].upper()} {wv:.2f}", ha="center", va="center", fontsize=5.5, color=SURF if c in (ACC, "#0c3a78") else INK)
            left += wv
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows_], fontsize=7); ax.set_xlim(0, 1); ax.set_xlabel("weight (sums to 1)"); ax.grid(False)
for s in ["left", "bottom"]: ax.spines[s].set_visible(False)
ax.tick_params(length=0)
save(fig, "fig11_family_weights", "Where the weight goes: the deployed rule, the global optimum, and the optimum fitted inside each task family. Families pull in different directions (decay for schema matching, recall for table QA, precision for finance), which is part of why the suite-level objective is flat.", "Fig. 9, Results §5 (single column)")

# ================================================================ F12 official F1 slope
em = OFF[OFF.official_f1_pos.notna()].groupby("dataset").agg(pool=("suite_f1_pos", "mean"), off=("official_f1_pos", "mean"), share=("official_positive_share", "mean")).sort_values("off")
fig, ax = plt.subplots(figsize=(SINGLE, 3.2))
ly = em.off.values.copy()
for _ in range(200):
    for i in range(1, len(ly)):
        if ly[i] - ly[i - 1] < .016: ly[i] = ly[i - 1] + .016
for i, (dname, r) in enumerate(em.iterrows()):
    col = ACC2 if r.pool - r.off > .1 else INK2; ax.plot([0, 1], [r.pool, r.off], color=col, lw=1.1 if col == ACC2 else .8, marker="o", ms=3.2, mec=col, mfc=SURF if col == INK2 else col)
    ax.plot([1.0, 1.06], [r.off, ly[i]], color=LIGHT, lw=.5); ax.text(1.08, ly[i], f"{dname}  (match share {r.share:.2f})", va="center", fontsize=6, color=col)
ax.set_xticks([0, 1]); ax.set_xticklabels(["balanced pool\n(50 / 50)", "official split\n(post-stratified)"]); ax.set_ylabel("positive-class F1, mean over ten models"); ax.set_xlim(-.1, 2.3); ax.grid(True, axis="y"); ax.grid(False, axis="x")
save(fig, "fig12_official_split_f1", "Comparability. Positive-class F1 on the balanced 50/50 pools against the same answers re-weighted to each matching dataset's official match ratio. Where matches are rare the balanced number overstates F1, mainly through precision (orange: drop > 0.10).", "Fig. 10, Results §6 (single column)")

# ================================================================ F13 CD diagram
s = SIG["friedman"]; mr = pd.Series(s["mean_rank"]).sort_values(); cd = s["nemenyi_cd_05"]
fig, ax = plt.subplots(figsize=(DOUBLE, 2.0)); lo, hi = 1, 10
ax.plot([lo, hi], [0, 0], color=INK, lw=.8); ax.set_xlim(lo - 2.3, hi + 2.3); ax.set_ylim(-1.7, 1.1); ax.axis("off")
for t in range(lo, hi + 1): ax.plot([t, t], [0, .08], color=INK, lw=.6); ax.text(t, .14, str(t), ha="center", fontsize=6.5, color=INK2)
ax.text((lo + hi) / 2, .45, "mean rank across 31 datasets (1 = best)", ha="center", fontsize=7, color=INK2)
n = len(mr); half = (n + 1) // 2
for i, (m, v) in enumerate(mr.items()):
    left = i < half; yl = -.35 - (i if left else i - half) * .22; xt = lo - .3 if left else hi + .3
    ax.plot([v, v], [0, yl], color=INK2, lw=.6); ax.plot([v, xt], [yl, yl], color=INK2, lw=.6); ax.text(xt - .08 if left else xt + .08, yl, PRETTY[m], ha="right" if left else "left", va="center", fontsize=6.8)
# cliques: groups not separated by CD (consecutive runs)
vals = mr.values; cliques = []; i = 0
while i < n:
    j = i
    while j + 1 < n and vals[j + 1] - vals[i] <= cd: j += 1
    if j > i: cliques.append((i, j))
    i = j + 1 if j > i else i + 1
cl = [(a_, b2) for a_, b2 in cliques if not any((c <= a_ and b2 <= d2) and (c, d2) != (a_, b2) for c, d2 in cliques)]
for k, (a_, b2) in enumerate(cl): ax.plot([vals[a_] - .05, vals[b2] + .05], [-.12 - .06 * k, -.12 - .06 * k], color=ACC, lw=2.2, solid_capstyle="round")
ax.plot([lo, lo + cd], [.85, .85], color=ACC2, lw=1.4); ax.text(lo + cd / 2, .93, f"critical difference {cd:.2f} (Nemenyi, α = .05)", ha="center", fontsize=6.5, color=ACC2)
save(fig, "fig13_critical_difference", "Friedman test under v1 (p < 0.001) with the Nemenyi critical difference: models joined by a blue bar are not separated at α = .05. The top group is separated from the bottom two; nothing inside the top group is.", "Fig. 6 companion or appendix (double column)")

# ================================================================ F14 why flat: ingredient agreement
C = comp[["em", "f1", "decay", "precision", "recall"]].corr(method="spearman"); lab = ["exact match", "F1", "decay", "precision", "recall"]
same = comp.assign(allsame=lambda d_: (d_.f1 == d_.em) & (d_.decay == d_.em) & (d_.precision == d_.em) & (d_.recall == d_.em)).groupby("family").allsame.mean().loc[fam_order]
fig, (a, b_) = plt.subplots(1, 2, figsize=(DOUBLE, 2.2), gridspec_kw={"width_ratios": [1, 1.15]})
a.imshow(C.values, cmap=SEQ, vmin=.5, vmax=1, aspect="equal"); a.grid(False)
for i in range(5):
    for j in range(5): a.text(j, i, f"{C.values[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color=SURF if C.values[i, j] > .85 else INK)
a.set_xticks(range(5)); a.set_xticklabels(lab, rotation=45, ha="right", fontsize=6.5); a.set_yticks(range(5)); a.set_yticklabels(lab, fontsize=6.5); a.tick_params(length=0)
for s_ in a.spines.values(): s_.set_visible(False)
b_.barh(range(4)[::-1], same.values, color=[FAMC[f] for f in fam_order], height=.6, lw=0)
for i, (f, v) in enumerate(zip(fam_order, same.values)): b_.text(v + .01, 3 - i, f"{100*v:.0f} %", va="center", fontsize=7, color=INK2)
b_.set_yticks(range(4)[::-1]); b_.set_yticklabels([FAMN[f] for f in fam_order], fontsize=7); b_.set_xlim(0, 1.08); b_.set_xlabel("share of answers where all four ingredients equal exact match"); b_.grid(True, axis="x"); b_.grid(False, axis="y")
a.set_title("Spearman ρ between ingredients", fontsize=7, pad=8, loc="left")
for ax, t in [(a, "a"), (b_, "b")]: ax.text(-0.28 if ax is a else -0.34, 1.12, t, transform=ax.transAxes, fontweight="bold", fontsize=9)
save(fig, "fig14_why_flat", "Why the weights barely matter. (a) The four ingredients agree with each other almost everywhere. (b) In most answers all four equal exact match, so every weighting gives the same score; only the table-QA and finance answers leave room for the weights to act.", "Fig. 2 alternative, Results §1 (double column)")

# ================================================================ F15 cost vs score
rows = []
for f in sorted(PRED.glob("*.jsonl")):
    m = f.stem
    if m not in models: continue
    for l in open(f):
        r = json.loads(l)
        if not r.get("error") and r["dataset"] in datasets: rows.append({"model": m, "cost": r.get("cost_usd", 0.0), "out": r.get("out_tokens", 0)})
run = pd.DataFrame(rows).groupby("model").agg(cost=("cost", "sum"), out=("out", "mean"))
run["score"] = PDM.mean(1).loc[run.index]; run["bt"] = LB["v1_original"].set_index("model").loc[run.index, "bt_strength"]
fig, ax = plt.subplots(figsize=(SINGLE, 2.8)); ax.set_xscale("log")
ax.scatter(run.cost, run.bt, s=np.clip(run.out / 6, 12, 160), color=ACC, alpha=.75, lw=0, zorder=3)
OFFS = {"gemini-3.1-pro": (-62, 7), "gemini-3.8-flash": (7, 3), "claude-opus-5": (-6, 7), "gpt-5.5": (7, 3), "claude-sonnet-5": (7, -4), "grok-4": (-30, 6), "gpt-5.4-mini": (-52, 4), "deepseek-r1": (8, -3), "deepseek-chat": (7, -8), "gpt-oss-120b": (7, -8), "llama-3.3-70b": (7, -3)}
for m, r in run.iterrows():
    ax.annotate(PRETTY[m], (r.cost, r.bt), xytext=OFFS[m], textcoords="offset points", fontsize=6.3, color=INK2)
ax.set_xlabel("API cost for the 3,083 answers (USD, log scale)"); ax.set_ylabel("Bradley–Terry strength under v1"); ax.grid(True, axis="both"); ax.axhline(0, color=LIGHT, lw=.6)
ax.text(.98, .04, "marker area scales with mean reply length", transform=ax.transAxes, ha="right", fontsize=6.3, color=INK2)
save(fig, "fig15_cost_vs_strength", "What the ranking costs. Bradley–Terry strength under the deployed rule against the API cost of answering the suite; marker size is mean reply length. The top three span a 30× price range.", "Discussion or appendix (single column)")

# ================================================================ F16 power per dataset
nsp = pd.Series(SIG["n_significant_pairs_per_dataset"]).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(DOUBLE, 2.0)); x = np.arange(len(nsp))
ax.bar(x, nsp.values, color=[FAMC[fam_of[d_]] for d_ in nsp.index], width=.72, lw=0)
ax.set_xticks(x); ax.set_xticklabels(nsp.index, rotation=60, ha="right", fontsize=6)
for lab_ in ax.get_xticklabels(): lab_.set_color(FAMC[fam_of[lab_.get_text()]])
ax.set_ylabel("model pairs separated (of 45)"); ax.axhline(0, color=LIGHT, lw=.6)
ax.text(.99, .95, f"{int((nsp == 0).sum())} datasets separate no pair; {int((nsp >= 20).sum())} separate ≥ 20", transform=ax.transAxes, ha="right", va="top", fontsize=6.8, color=INK2)
hs = [plt.Rectangle((0, 0), 1, 1, color=FAMC[f]) for f in fam_order]; ax.legend(hs, [FAMN[f] for f in fam_order], loc="upper right", bbox_to_anchor=(1, .85), ncol=4, fontsize=6.3)
save(fig, "fig16_power_per_dataset", "Where the leaderboard's power comes from: the number of model pairs each dataset separates with a Holm-corrected per-item paired test under v1. The entity-matching sets at ceiling separate none; a dozen table and document sets carry the result.", "Fig. 7 companion or appendix (double column)")

# ---- index files
md = ["# Paper figures (v2)\n\nGenerated by `paper/scripts/make_paper_figures.py` from `v2_gridsearch/output/`. Each figure exists as PDF (vector, for LaTeX) and PNG (300 dpi). Widths: single column 3.4 in, double column 7.0 in.\n\nPalette: one accent (blue) for the thing to look at, orange for the deployed rule or the highlighted point, greys for context; the four task families use a colour-blind-validated categorical set (blue, orange, aqua, yellow) only where family is the encoding.\n"]
tex = ["% \\input this file, or copy the blocks you need. Requires \\usepackage{graphicx,subcaption} and \\graphicspath{{figures_paper/}}.\n"]
for name, cap, place in CAP:
    md.append(f"\n## {name}\n\n![{name}]({name}.png)\n\n**Caption.** {cap}\n\n**Suggested placement.** {place}\n")
    width = r"\textwidth" if "double" in place else r"\columnwidth"
    tex.append(f"\\begin{{figure{'*' if 'double' in place else ''}}}[t]\\centering\\includegraphics[width={width}]{{{name}.pdf}}\\caption{{{cap.replace('%', chr(92) + '%')}}}\\label{{fig:{name}}}\\end{{figure{'*' if 'double' in place else ''}}}\n\n")
(DST / "FIGURES.md").write_text("".join(md)); (DST / "figures_paper.tex").write_text("".join(tex))
print(f"wrote {len(CAP)} figures to {DST}")
