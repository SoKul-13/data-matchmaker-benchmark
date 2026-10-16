"""Build Overleaf packages for v3, v4 and v5 (from v6_top30_significance/) and a cross-version comparison paper.

Each package: paper/<version>/{main.tex, figures/, tables/, data/, README.md} + paper/<version>_overleaf.zip.
main.tex = Setup + Results (one figure or table per result) + appendix with every figure and table.
Run from FINAL_v2:  uv run python paper/scripts/make_version_packages.py
"""
from __future__ import annotations
import json, re, shutil, zipfile, itertools
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FINAL = Path(__file__).resolve().parents[2]
REPO = FINAL.parent
V6 = REPO / "v6_top30_significance"
PAPER = FINAL / "paper"
PRETTY = {"gemini-3.1-pro": "Gemini 3.1 Pro", "claude-opus-5": "Claude Opus 5", "claude-sonnet-5": "Claude Sonnet 5", "gpt-5.5": "GPT-5.5", "gpt-5.4-mini": "GPT-5.4-mini",
          "gemini-3.8-flash": "Gemini 3.8 Flash", "grok-4": "Grok 4", "deepseek-chat": "DeepSeek-chat", "deepseek-r1": "DeepSeek-R1",
          "gpt-oss-120b": "gpt-oss-120b", "llama-3.3-70b": "Llama 3.3 70B"}
FAMC = {"EM": "C0", "SM": "C1", "TQA": "C2", "FIN": "C3"}
FAM = {"EM": "entity matching", "SM": "schema matching", "TQA": "table QA", "FIN": "finance"}
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs,graphicx,longtable,tabularx,array,caption,subcaption,amsmath,hyperref,enumitem,xcolor,pdflscape}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\captionsetup{font=small,labelfont=bf}
\setlist{nosep,leftmargin=*}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\graphicspath{{figures/}}
\emergencystretch=1.5em
\hypersetup{colorlinks=true,linkcolor=blue!60!black,citecolor=blue!60!black,urlcolor=blue!60!black}
"""


def esc(s):
    return str(s).replace("\\", "/").replace("_", r"\_\allowbreak{}").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")


class Pkg:
    def __init__(self, name, title):
        self.dir = PAPER / name; self.fig = self.dir / "figures"; self.tab = self.dir / "tables"; self.dat = self.dir / "data"
        for d in (self.fig, self.tab, self.dat):
            if d.exists(): shutil.rmtree(d)
            d.mkdir(parents=True)
        self.name, self.title = name, title; self.captions = {}; self.table_caps = {}; self.wide = set()

    def save(self, fig, name, cap):
        fig.tight_layout(); fig.savefig(self.fig / f"{name}.png", dpi=200); fig.savefig(self.fig / f"{name}.pdf"); plt.close(fig); self.captions[name] = cap

    def copy_fig(self, src, name, cap):
        if Path(src).exists(): shutil.copy(src, self.fig / f"{name}{Path(src).suffix}"); self.captions[name] = cap

    def to_tex(self, df, name, cap, fmt="%.3f", longtable=False):
        df = df.copy()
        if isinstance(df.index, pd.MultiIndex) or df.index.name is not None: df = df.reset_index(drop=(df.index.name in df.columns) if not isinstance(df.index, pd.MultiIndex) else False)
        cols = [esc(c) for c in df.columns]

        def cell(x):
            if isinstance(x, (bool, np.bool_)): return "yes" if x else "no"
            if isinstance(x, (float, np.floating)): return "--" if pd.isna(x) else fmt % x
            if isinstance(x, (int, np.integer)): return str(x)
            return esc(x)
        # column format: long text columns wrap in p{} columns sized by their share of text; numbers right-aligned
        ncol = len(cols)
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
        head = " & ".join(cols) + r" \\"
        lines = [" & ".join(cell(x) for x in row) + r" \\" for row in df.itertuples(index=False)]
        wide = len(cols) > 8
        env = "longtable" if longtable else "tabular"
        size = r"\tiny" if (wide or len(cols) > 6) else r"\scriptsize"
        core = f"\\begin{{{env}}}{{{cf}}}\n" + (f"\\caption{{{cap}}}\\label{{tab:{name}}}\\\\\n" if longtable else "") + f"\\toprule\n{head}\n\\midrule\n" + "\n".join(lines) + f"\n\\bottomrule\n\\end{{{env}}}\n"
        if longtable:
            body = (r"\begin{landscape}" + "\n" if wide else "") + size + "\n\\setlength{\\tabcolsep}{3pt}\n" + core + "\\normalsize\n" + (r"\end{landscape}" + "\n" if wide else "")
        else:
            if wide and "p{" not in cf: core = "\\resizebox{\\linewidth}{!}{%\n" + core + "}\n"
            body = (r"\begin{landscape}" + "\n" if wide else "") + f"\\begin{{table}}[htbp]\n\\centering{size}\n\\caption{{{cap}}}\n\\label{{tab:{name}}}\n\\setlength{{\\tabcolsep}}{{3pt}}\n{core}\\end{{table}}\n" + (r"\end{landscape}" + "\n" if wide else "")
        (self.tab / f"{name}.tex").write_text(body); self.table_caps[name] = cap

    def copy_data(self, out_dir, extra=()):
        for p in out_dir.rglob("*"):
            if p.is_file() and p.suffix in {".csv", ".json", ".npz", ".md", ".tex"} and "fig_" not in p.name and p.name != "_run.log":
                dst = self.dat / p.relative_to(out_dir); dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy(p, dst)
        for p in extra:
            if Path(p).exists(): shutil.copy(p, self.dat / Path(p).name)

    def write(self, setup_tex, results_tex, intro=""):
        app = ["\\clearpage\n\\appendix\n\\section{All figures}\nEvery figure that can be drawn from the saved outputs; source data in \\texttt{data/}.\n"]
        for n in sorted(self.captions):
            ext = "png" if (self.fig / f"{n}.png").exists() else "pdf"
            app.append(f"\\begin{{figure}}[htbp]\\centering\\includegraphics[width=0.9\\textwidth]{{{n}.{ext}}}\\caption{{{self.captions[n]}}}\\label{{figall:{n}}}\\end{{figure}}\n")
        app.append("\\clearpage\n\\section{All tables}\nEvery saved table, one file each under \\texttt{tables/}; include any in the main text with \\texttt{\\textbackslash input}.\n")
        for n in sorted(self.table_caps): app.append(f"\\input{{tables/{n}.tex}}\n\\clearpage\n")
        main = PREAMBLE + f"\\title{{{self.title}}}\n\\author{{}}\n\\date{{2026}}\n\\begin{{document}}\n\\maketitle\n{intro}\n" + setup_tex + "\n" + results_tex + "\n" + "".join(app) + "\\end{document}\n"
        (self.dir / "main.tex").write_text(main)
        (self.dir / "README.md").write_text(f"# Summary report (Overleaf package): {self.title}\n\nUpload the folder or the zip as an Overleaf project and compile `main.tex` with pdfLaTeX.\n\n* `main.tex` - Setup and Results, then an appendix with every figure and table.\n* `figures/` - {len(self.captions)} figures.\n* `tables/` - {len(self.table_caps)} LaTeX tables.\n* `data/` - every output file of the run (CSV / JSON / NPZ) and the generated REPORT.md.\n\nGenerated by `FINAL_v2/paper/scripts/make_version_packages.py`.\n")
        zp = PAPER / f"{self.name}_overleaf.zip"
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for p in self.dir.rglob("*"):
                if p.is_file(): z.write(p, p.relative_to(self.dir))
        print(f"{self.name}: figures {len(self.captions)} tables {len(self.table_caps)} data {sum(1 for p in self.dat.rglob('*') if p.is_file())} zip {zp.stat().st_size/1e6:.1f} MB")


def fig_(name): return f"\\begin{{figure}}[htbp]\\centering\\includegraphics[width=0.85\\textwidth]{{{name}.png}}\\caption{{CAP}}\\label{{fig:{name}}}\\end{{figure}}"


def figure(pk, name, width=0.85):
    ext = "png" if (pk.fig / f"{name}.png").exists() else "pdf"
    return f"\\begin{{figure}}[htbp]\\centering\\includegraphics[width={width}\\textwidth]{{{name}.{ext}}}\\caption{{{pk.captions[name]}}}\\label{{fig:{name}}}\\end{{figure}}\n"


def table(pk, name): return f"\\input{{tables/{name}.tex}}\n"


# ---------------------------------------------------------------- shared leaderboard block
def leaderboard_block(pk, out, rules, headline, rule_pretty, weights_of):
    """Figures and tables from leaderboards/<rule>/ (full outputs), diagnostics/ and official splits. Returns dict of key numbers."""
    LB = {r: pd.read_csv(out / "leaderboards" / r / "leaderboard.csv") for r in rules if (out / "leaderboards" / r / "leaderboard.csv").exists()}
    rules = [r for r in rules if r in LB]
    SIG = {r: json.load(open(out / "leaderboards" / r / "significance.json")) for r in rules if (out / "leaderboards" / r / "significance.json").exists()}
    PARAMS = {r: json.load(open(out / "leaderboards" / r / "params.json")) for r in rules if (out / "leaderboards" / r / "params.json").exists()}
    order = LB[headline].sort_values("rank_bt")["model"].tolist()
    models = order; info = {"order": order, "LB": LB, "SIG": SIG}
    # BT all rules
    n = len(rules); ncol = 3; nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(9, 2.4 * nrow), sharex=True, squeeze=False)
    for ax in axes.flat: ax.axis("off")
    for ax, r in zip(axes.flat, rules):
        ax.axis("on"); d = LB[r].set_index("model").loc[order]
        ax.barh(range(len(d)), d.bt_strength, xerr=d.bt_se_vs_ref, color=["C3" if m == order[0] else "C0" for m in order], height=.7)
        ax.set_yticks(range(len(d))); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=6); ax.invert_yaxis(); ax.set_title(rule_pretty.get(r, r), fontsize=8); ax.axvline(0, c="k", lw=.5)
    pk.save(fig, "fig_bt_all_rules", "Bradley--Terry strengths ($\\pm$ SE vs reference) under every reported rule; models fixed in the headline order.")
    # rank bootstrap headline
    bp = out / "leaderboards" / headline / "bootstrap.npz"
    if bp.exists():
        b = np.load(bp); bm = list(b["models"])
        fig, axes = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
        for ax, key, lab in zip(axes, ["bt_ranks", "borda_ranks"], ["Bradley-Terry rank", "Borda rank"]):
            idx = [bm.index(m) for m in order]
            ax.boxplot([b[key][:, i] for i in idx], vert=False, widths=.6, showfliers=False, medianprops={"color": "C3"})
            ax.set_yticks(range(1, len(order) + 1)); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=7); ax.invert_yaxis(); ax.set_xlabel(lab + " (1,000 item bootstraps)")
        pk.save(fig, "fig_rank_bootstrap", f"Bootstrap distribution of each model's rank under the headline rule ({rule_pretty.get(headline, headline)}).")
    # p first
    pf = pd.DataFrame({rule_pretty.get(r, r): LB[r].set_index("model").loc[order, "p_first_bt"] for r in rules})
    pb = pd.DataFrame({rule_pretty.get(r, r): LB[r].set_index("model").loc[order, "p_first_borda"] for r in rules})
    fig, axes = plt.subplots(1, 2, figsize=(9, 3))
    for ax, P, lab in zip(axes, [pf, pb], ["P(first) Bradley-Terry", "P(first) Borda"]):
        ax.imshow(P.values, cmap="Blues", vmin=0, vmax=1, aspect="auto"); ax.set_xticks(range(P.shape[1])); ax.set_xticklabels(P.columns, rotation=45, ha="right", fontsize=7); ax.set_yticks(range(P.shape[0])); ax.set_yticklabels([PRETTY[m] for m in P.index], fontsize=7); ax.set_title(lab)
        for i in range(P.shape[0]):
            for j in range(P.shape[1]):
                if P.values[i, j] > .005: ax.text(j, i, f"{P.values[i, j]:.2f}", ha="center", va="center", fontsize=6, color="w" if P.values[i, j] > .5 else "k")
    pk.save(fig, "fig_p_first", "Bootstrap probability of first place under every rule, by pooling method.")
    # rule agreement
    ra_p = out / "leaderboards" / "rule_agreement.csv"
    if ra_p.exists():
        ra = pd.read_csv(ra_p, index_col=0)
        fig, ax = plt.subplots(figsize=(4.5, 4)); ax.imshow(ra.values, cmap="Blues", vmin=.7, vmax=1)
        ax.set_xticks(range(len(ra.columns))); ax.set_xticklabels([rule_pretty.get(r, r) for r in ra.columns], rotation=45, ha="right"); ax.set_yticks(range(len(ra.index))); ax.set_yticklabels([rule_pretty.get(r, r) for r in ra.index])
        for i in range(len(ra.index)):
            for j in range(len(ra.columns)): ax.text(j, i, f"{ra.values[i, j]:.2f}", ha="center", va="center", fontsize=6, color="w" if ra.values[i, j] > .9 else "k")
        pk.save(fig, "fig_rule_agreement", "Kendall $\\tau$ between the Bradley--Terry rankings of each pair of rules.")
        pk.to_tex(ra.round(3).rename(index=rule_pretty, columns=rule_pretty).reset_index().rename(columns={"index": "rule"}), "rule_agreement", "Kendall $\\tau$ between the Bradley--Terry rankings of the rules.")
    # CD diagram + pairwise
    if headline in SIG:
        s = SIG[headline]["friedman"]; mr = pd.Series(s["mean_rank"]).sort_values(); cd = s["nemenyi_cd_05"]
        fig, ax = plt.subplots(figsize=(7, 2.6)); ax.scatter(mr.values, np.zeros(len(mr)), c="k", s=15)
        for i, (m, v) in enumerate(mr.items()): ax.annotate(PRETTY[m], (v, 0), xytext=(v, .35 + .25 * (i % 2)), ha="center", fontsize=6, arrowprops={"arrowstyle": "-", "lw": .5})
        ax.plot([mr.values[0], mr.values[0] + cd], [-.3, -.3], lw=3, c="C3"); ax.text(mr.values[0] + cd / 2, -.5, f"Nemenyi CD = {cd:.2f}", ha="center", fontsize=7, color="C3")
        ax.set_ylim(-.8, 1); ax.set_yticks([]); ax.set_xlabel("mean rank across 31 datasets (Friedman)"); ax.spines["left"].set_visible(False)
        pk.save(fig, "fig_cd_diagram", f"Critical-difference view of the Friedman test under the headline rule: mean rank per model and the Nemenyi critical difference at $\\alpha=.05$.")
        info["friedman"] = s
        pw_p = out / "leaderboards" / headline / "pairwise_item_tests.csv"
        if pw_p.exists():
            pw = pd.read_csv(pw_p); sp = pw[pw.significant_05].groupby(["a", "b"]).size()
            Mp = pd.DataFrame(0, index=order, columns=order, dtype=int)
            for (a, bb), k in sp.items():
                if a in Mp.index and bb in Mp.columns: Mp.loc[a, bb] += k; Mp.loc[bb, a] += k
            fig, ax = plt.subplots(figsize=(5, 4.3)); ax.imshow(Mp.values, cmap="Oranges", aspect="auto")
            ax.set_xticks(range(len(order))); ax.set_xticklabels([PRETTY[m] for m in order], rotation=45, ha="right", fontsize=7); ax.set_yticks(range(len(order))); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=7)
            for i in range(len(order)):
                for j in range(len(order)): ax.text(j, i, Mp.values[i, j], ha="center", va="center", fontsize=6)
            pk.save(fig, "fig_pairwise_significance", "Number of datasets (of 31) in which the per-item paired test separates each pair of models under the headline rule (Holm within dataset).")
        nsp = pd.Series(SIG[headline]["n_significant_pairs_per_dataset"]).sort_values()
        diag = pd.read_csv(out / "diagnostics" / "dataset_diagnostics.csv"); fam_of = dict(zip(diag.dataset, diag.family))
        fig, ax = plt.subplots(figsize=(7, 2.6)); ax.bar(range(len(nsp)), nsp.values, color=[FAMC[fam_of[d]] for d in nsp.index]); ax.set_xticks(range(len(nsp))); ax.set_xticklabels(nsp.index, rotation=60, ha="right", fontsize=6); ax.set_ylabel("significant model pairs (of 45)")
        pk.save(fig, "fig_significant_pairs_per_dataset", "How many of the 45 model pairs each dataset separates at the item level under the headline rule (colour = family).")
    # per-dataset heatmaps (headline)
    pdm_p = out / "leaderboards" / headline / "per_dataset_mean.csv"
    if pdm_p.exists():
        pdm = pd.read_csv(pdm_p, index_col=0).loc[order]; datasets = list(pdm.columns)
        for key, M, cmap, lab, fmtc in [("fig_model_dataset_heatmap", pdm, "viridis", "mean score", "{:.2f}"), ("fig_model_dataset_ranks", pdm.rank(ascending=False, axis=0), "viridis_r", "rank within dataset (1 = best)", "{:.0f}")]:
            fig, ax = plt.subplots(figsize=(9, 3.6)); im = ax.imshow(M.values, cmap=cmap, aspect="auto"); ax.set_xticks(range(len(datasets))); ax.set_xticklabels(datasets, rotation=60, ha="right", fontsize=6); ax.set_yticks(range(len(order))); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=7)
            for i in range(M.shape[0]):
                for j in range(M.shape[1]): ax.text(j, i, fmtc.format(M.values[i, j]), ha="center", va="center", fontsize=4.5, color="w" if (M.values[i, j] < .6 if cmap == "viridis" else M.values[i, j] > 5) else "k")
            fig.colorbar(im, ax=ax, shrink=.7, label=lab)
            pk.save(fig, key, f"{'Mean score' if cmap == 'viridis' else 'Rank'} per model and dataset under the headline rule.")
        pk.to_tex(pdm.rename(index=PRETTY).T.round(3).reset_index().rename(columns={"index": "dataset"}), f"per_dataset_mean_{headline}", f"Mean score per dataset and model under the headline rule ({esc(rule_pretty.get(headline, headline))}).", longtable=True)
    # official split
    off_p = out / "leaderboards" / headline / "official_split_estimates.csv"
    if off_p.exists():
        off = pd.read_csv(off_p)
        fig, ax = plt.subplots(figsize=(4.2, 4)); ax.scatter(off.suite_mean, off.official_estimate, s=8, alpha=.6); ax.plot([0, 1], [0, 1], "k:", lw=.8); ax.set_xlabel("suite score (balanced pool)"); ax.set_ylabel("official-split estimate")
        pk.save(fig, "fig_official_scatter", "Suite score against post-stratified official-split estimate for every (dataset, model) pair under the headline rule.")
        em = off[off.official_f1_pos.notna()]
        if len(em):
            fig, ax = plt.subplots(figsize=(7, 3)); ds = em.groupby("dataset").official_f1_pos.mean().sort_values().index; x = np.arange(len(ds))
            for i, m in enumerate(order):
                d = em[em.model == m].set_index("dataset").reindex(ds); ax.scatter(x + (i - (len(order) - 1) / 2) * .07, d.official_f1_pos, s=8, label=PRETTY[m]); ax.scatter(x + (i - (len(order) - 1) / 2) * .07, d.suite_f1_pos, s=8, marker="_", c="grey")
            ax.set_xticks(x); ax.set_xticklabels(ds, rotation=45, ha="right", fontsize=7); ax.set_ylabel("positive-class F1 (dots: official ratio; grey: pool)"); ax.legend(frameon=False, fontsize=5, ncol=5)
            pk.save(fig, "fig_official_f1_models", "Positive-class F1 on the balanced pool (grey) and at the official match ratio (coloured) per model and matching dataset.")
        o = off.copy(); o["model"] = o.model.map(PRETTY)
        pk.to_tex(o[["dataset", "model", "suite_mean", "official_estimate", "official_lo95", "official_hi95", "effective_n", "suite_f1_pos", "official_f1_pos", "official_f1_lo95", "official_f1_hi95", "official_positive_share"]].round(3), "official_split", "Official-split estimates under the headline rule for every dataset and model.", longtable=True)
        pk.to_tex(off.groupby("dataset")[["suite_mean", "official_estimate", "suite_f1_pos", "official_precision_pos", "official_recall_pos", "official_f1_pos", "official_positive_share"]].mean().round(3).reset_index(), "official_split_by_dataset", "Official-split estimates under the headline rule averaged over the ten models.")
        info["official"] = off
    # diagnostics
    dg = out / "diagnostics" / "dataset_diagnostics.csv"
    if dg.exists():
        diag = pd.read_csv(dg)
        fig, ax = plt.subplots(figsize=(5, 3.6)); ax.scatter(diag.mean_score, diag.spread_across_models, c=[FAMC[f] for f in diag.family], s=18)
        for r in diag.itertuples(): ax.annotate(r.dataset, (r.mean_score, r.spread_across_models), fontsize=5, xytext=(2, 2), textcoords="offset points")
        ax.axvline(.95, c="k", ls=":", lw=.6); ax.set_xlabel("mean score across models"); ax.set_ylabel("spread (max - min) across models")
        pk.save(fig, "fig_diagnostics_scatter", "Dataset diagnostics: mean score against spread across models; dotted line marks the ceiling flag.")
        dd = diag.sort_values("ranking_self_stability_tau")
        fig, ax = plt.subplots(figsize=(7, 2.6)); ax.bar(range(len(dd)), dd.ranking_self_stability_tau, color=[FAMC[f] for f in dd.family]); ax.set_xticks(range(len(dd))); ax.set_xticklabels(dd.dataset, rotation=60, ha="right", fontsize=6); ax.set_ylabel("self-stability tau")
        pk.save(fig, "fig_self_stability", "Self-stability of each dataset's model ranking (Kendall $\\tau$ between bootstrap halves).")
        pk.to_tex(diag.round(3), "diagnostics", "Dataset diagnostics under the headline rule.", longtable=True)
        info["diag"] = diag
    pk.copy_fig(out / "diagnostics" / "fig_dataset_tau.png", "fig_dataset_tau", "Kendall $\\tau$ between the model rankings of each pair of datasets under the headline rule.")
    # leaderboard tables
    for r in rules:
        d = LB[r].copy(); d["model"] = d.model.map(PRETTY)
        cols = [c for c in ["model", "bt_strength", "bt_se_vs_ref", "rank_bt", "bt_rank_lo95", "bt_rank_hi95", "p_first_bt", "rank_borda", "borda_rank_lo95", "borda_rank_hi95", "p_first_borda", "rank_kemeny", "rank_copeland", "rank_mean_z", "rank_rrf", "rank_family_balanced_z", "mean_score"] if c in d.columns]
        pk.to_tex(d[cols].round(3), f"leaderboard_{r}", f"Full leaderboard under rule {esc(rule_pretty.get(r, r))}; weights: {esc(weights_of(r))}.")
        if r in SIG:
            fr = SIG[r]["friedman"]
            pk.to_tex(pd.DataFrame([{"a": PRETTY[p["a"]], "b": PRETTY[p["b"]], "mean rank diff": p["mean_rank_diff"], "wins a": p["wins_a"], "wins b": p["wins_b"], "ties": p["ties"], "Wilcoxon p": p["wilcoxon_p"], "Holm p": p["wilcoxon_p_holm"], "Nemenyi": p["nemenyi_significant"], "sig .05": p["wilcoxon_significant_05"]} for p in fr["pairwise"]]).round(4),
                      f"pairwise_{r}", f"Cross-dataset pairwise tests under rule {esc(rule_pretty.get(r, r))}: Friedman $\\chi^2$ = {fr['friedman_chi2']:.1f} ($p$ = {fr['friedman_p']:.1e}), Iman--Davenport $F$ = {fr['iman_davenport_F']:.1f}, Nemenyi CD = {fr['nemenyi_cd_05']:.2f}, Kendall's $W$ = {SIG[r]['kendall_W_datasets']['kendall_W']:.3f}.", fmt="%.4f", longtable=True)
    # compact rank table across rules
    rows = []
    for r in rules:
        d = LB[r].set_index("model"); rows.append({"rule": rule_pretty.get(r, r), **{PRETTY[m]: f"{int(d.loc[m, 'rank_bt'])} ({int(d.loc[m, 'rank_borda'])})" for m in order}, "Friedman p": f"{SIG[r]['friedman']['friedman_p']:.1e}" if r in SIG else "", "W": f"{SIG[r]['kendall_W_datasets']['kendall_W']:.2f}" if r in SIG else ""})
    pk.to_tex(pd.DataFrame(rows), "ranks_by_rule", "Bradley--Terry rank (Borda rank in brackets) under each reported rule, Friedman $p$ and Kendall's $W$ among datasets.")
    # headline leaderboard (short)
    d = LB[headline].set_index("model").loc[order]
    pk.to_tex(pd.DataFrame({"rank": range(1, 11), "model": [PRETTY[m] for m in order], "BT strength": d.bt_strength.round(3), "SE": d.bt_se_vs_ref.round(3), "Borda rank": d.rank_borda.astype(int), "Borda 95%": [f"[{int(a)}, {int(b)}]" for a, b in zip(d.borda_rank_lo95, d.borda_rank_hi95)], "P(first) BT": d.p_first_bt.round(2), "mean score": d.mean_score.round(3)}),
              "leaderboard_headline", f"Leaderboard under the headline rule ({esc(rule_pretty.get(headline, headline))}).")
    info["LB"] = LB; info["rules"] = rules
    return info


SETUP_COMMON = r"""
\subsection{Shared setup (identical across versions)}
\begin{itemize}
\item \textbf{Suite.} 31 datasets: 11 entity matching (EM), 6 schema matching (SM), 11 table question answering and understanding (TQA), 3 financial documents (FIN). Official test or dev splits only; 150 items per dataset by seeded stratified sampling, 100 flagged for answering (OfficeQA Pro V2: 90; Alaska schema: 93); 3,083 answered items per model. Entity-matching pools are 50/50 match / non-match (Papadakis--Christen keeps its real 1.8\,\% ratio); schema matching is one question per source column with a candidate list; BIRD is graded on the executed result of the gold SQL.
\item \textbf{Answers.} Eleven models (Claude Opus 5, Claude Sonnet 5, GPT-5.5, GPT-5.4-mini, Gemini 3.1 Pro, Gemini 3.8 Flash, Grok 4, DeepSeek-chat, DeepSeek-R1, gpt-oss-120b, Llama 3.3 70B); one prompt per item ending in \texttt{FINAL ANSWER: <answer>}; temperature 0 where accepted (Claude 5 and GPT-5.5 ran at provider defaults, recorded per row); output budget 700 tokens with mechanical re-asks at 2,500, 8,000 and 16,000 for replies cut off before a final line (the budget is counted in each provider's own tokens and, for reasoning models, includes the chain of thought, so it is a termination test rather than an equal text allowance); every answer cached with tokens, cost and finish reason. The same cache feeds every version, so leaderboards are directly comparable.
\item \textbf{Scoring primitives.} Extraction of the final line, Unicode / case / punctuation normalisation, number parsing with sign, percent and scale words, alias lists per gold (best alias wins), list golds, a hedge flag. Native metric per dataset: numeric tolerance (1\,\%) for numeric golds, exact match for text and boolean, ROUGE-L for free-form.
\item \textbf{Coverage rule.} A model is in the study only if it covered $\ge 90\,\%$ of the suite; a dataset counts only items every model answered and only with $\ge 20$ such items.
\item \textbf{Leaderboard machinery.} Bradley--Terry strengths from item-level pairwise wins (MLE, ridge 0.01, SE from the observed information) as the headline pooling; Borda, Kemeny (with cost), Copeland, mean-$z$, reciprocal-rank fusion and family-balanced $z$ as checks; 1,000 item bootstraps of the Borda and Bradley--Terry ranks; Friedman with Iman--Davenport, Nemenyi CD, Holm-corrected pairwise Wilcoxon across datasets; paired permutation and Wilcoxon per item within datasets (Holm); Kendall's $W$ among datasets; majority-class baselines for boolean sets; post-stratified official-split estimates with a weighted bootstrap and positive-class F1 at the official match ratio; floor / ceiling / self-stability diagnostics per dataset.
\item \textbf{Sampled designs.} Uniform-lattice, Dirichlet-snapped and Latin-hypercube samples on the weight simplex at step 0.05 (20 seeds each) with centred $L_2$ discrepancy and nearest-neighbour distances, compared with the exhaustive optimum where one exists.
\item \textbf{Reporting.} Each version's \texttt{run\_all.sh} regenerates its \texttt{REPORT.md} from the cached answers; every number in this document is read from those output files.
\end{itemize}
"""


# ================================================================= v3
def build_v3():
    out = V6 / "v3_aggregation" / "output"
    pk = Pkg("v3", "Summary Report, v3: Aggregation Views from the Literature, Every Combination, and Parameters with Standard Errors")
    views = ["mean_raw", "baseline_norm_mean", "z_mean", "mean_win_rate", "borda", "kemeny_score", "bradley_terry", "irt_ability"]
    VP = {"mean_raw": "mean raw", "baseline_norm_mean": "baseline-normalised mean", "z_mean": "mean z", "mean_win_rate": "mean win rate", "borda": "Borda", "kemeny_score": "Kemeny score", "bradley_terry": "Bradley--Terry", "irt_ability": "Rasch ability"}
    V = pd.read_csv(out / "views.csv", index_col=0); Vem = pd.read_csv(out / "views_em.csv", index_col=0)
    combos = pd.read_csv(out / "combos" / "combos.csv"); best = json.load(open(out / "best.json")); designs = json.load(open(out / "designs.json"))
    sh = json.load(open(out / "selection" / "split_half.json")); shc = pd.read_csv(out / "selection" / "split_half.csv")
    pf = json.load(open(out / "params" / "view_params_full.json")); pb = json.load(open(out / "params" / "view_params_bootstrap.json"))
    rasch_items = pd.read_csv(out / "params" / "rasch_item_difficulties.csv")
    models = list(V.index); Z = (V - V.mean()) / V.std(ddof=0)
    RULES = ["native", "em_only"]; RP = {"native": "native metric", "em_only": "exact match"}
    info = leaderboard_block(pk, out, RULES, "native", RP, lambda r: "--")
    order = info["order"]
    # existing figs
    pk.copy_fig(out / "fig_views.png", "fig_views", "The eight single views: z-scored value per model.")
    pk.copy_fig(out / "fig_combos.png", "fig_combos", "All 455 candidate mixes sorted by $J$, coloured by design.")
    # view z heatmap + ranks
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, M, lab, cmap in [(axes[0], Z.loc[order], "z-score", "RdBu"), (axes[1], V.rank(ascending=False).loc[order], "rank (1 = best)", "viridis_r")]:
        ax.imshow(M.values, cmap=cmap, aspect="auto"); ax.set_xticks(range(8)); ax.set_xticklabels([VP[v] for v in views], rotation=45, ha="right", fontsize=7); ax.set_yticks(range(len(order))); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=7); ax.set_title(lab)
        for i in range(len(order)):
            for j in range(8): ax.text(j, i, f"{M.values[i, j]:.0f}" if "rank" in lab else f"{M.values[i, j]:+.1f}", ha="center", va="center", fontsize=6)
    pk.save(fig, "fig_view_matrix", "Each view's z-score (left) and rank (right) per model on native-metric scores.")
    Jv = combos[combos.n_views == 1].set_index("label")
    single = pd.DataFrame({"view": views, "J alone": [combos[(combos.n_views == 1) & (combos[f"w_{v}"] == 1)].J.iloc[0] for v in views]})
    fig, ax = plt.subplots(figsize=(5, 2.8)); ax.bar(range(8), single["J alone"]); ax.set_xticks(range(8)); ax.set_xticklabels([VP[v] for v in views], rotation=45, ha="right", fontsize=7); ax.set_ylabel("J alone"); ax.set_ylim(single["J alone"].min() - .02, single["J alone"].max() + .01)
    pk.save(fig, "fig_single_view_j", "Objective $J$ of each view used alone.")
    sub = combos[combos.design == "subset"] if "subset" in set(combos.design) else combos[combos.label.str.startswith("subset")]
    fig, ax = plt.subplots(figsize=(5, 3)); ax.boxplot([sub[sub.n_views == k].J for k in range(1, 9)], tick_labels=list(range(1, 9))); ax.set_xlabel("number of views in the equal-weight subset"); ax.set_ylabel("J")
    pk.save(fig, "fig_j_by_subset_size", "Objective $J$ of the 255 equal-weight subsets by subset size.")
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.8))
    for ax, c in zip(axes, ["stability", "transitivity", "reference"]):
        for dsg, col in [("subset", "C0"), ("lattice", "C1"), ("lhs", "C2")]:
            d = combos[combos.label.str.startswith(dsg)]; ax.scatter(d[c], d.J, s=5, alpha=.5, c=col, label=dsg)
        ax.set_xlabel(c); ax.set_ylabel("J")
    axes[0].legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_j_terms", "Objective $J$ against each of its three terms (stability, transitivity, reference) for every candidate mix.")
    top = combos.sort_values("J", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(7, 3)); bottom = np.zeros(len(top))
    for v in views: ax.bar(range(len(top)), top[f"w_{v}"], bottom=bottom, label=VP[v]); bottom += top[f"w_{v}"].values
    ax.set_xticks(range(len(top))); ax.set_xticklabels([f"{l} ({j:.3f})" for l, j in zip(top.label, top.J)], rotation=60, ha="right", fontsize=6); ax.set_ylabel("weight"); ax.legend(frameon=False, fontsize=5, ncol=4)
    pk.save(fig, "fig_top_mix_weights", "View weights of the fifteen best candidate mixes (label and $J$ on the axis).")
    # split half
    fig, ax = plt.subplots(figsize=(6, 3)); x = np.arange(len(shc))
    ax.plot(x, shc.J_A_selected, "o-", ms=3, label="selected: J on half A"); ax.plot(x, shc.J_B_selected, "s-", ms=3, label="selected: J on half B"); ax.plot(x, shc.J_B_pure_bt, "^--", ms=3, label="pure BT on half B"); ax.plot(x, shc.J_B_uniform, "v--", ms=3, label="uniform mix on half B"); ax.plot(x, shc.J_B_full_best, "d:", ms=3, label="full-data best on half B")
    ax.set_xlabel("split"); ax.set_ylabel("J"); ax.legend(frameon=False, fontsize=6, ncol=2)
    pk.save(fig, "fig_split_half", "Split-half honesty check: the mix selected on half A scored on both halves, against pure Bradley--Terry, the uniform mix and the full-data best on half B.")
    # parameters
    pn = pf["native"]; mm = pn["models"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3))
    idx = [mm.index(m) for m in order]
    axes[0].barh(range(len(order)), np.array(pn["bradley_terry"]["beta"])[idx], xerr=np.array(pb["bt_beta_sd_bootstrap"])[idx], color="C0"); axes[0].set_title("Bradley-Terry strength (bar = bootstrap SD)")
    axes[1].barh(range(len(order)), np.array(pn["rasch"]["theta"])[idx], xerr=np.array(pn["rasch"]["se_theta"])[idx], color="C1"); axes[1].set_title("Rasch ability (bar = analytic SE)")
    for ax in axes: ax.set_yticks(range(len(order))); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=7); ax.invert_yaxis(); ax.axvline(0, c="k", lw=.5)
    pk.save(fig, "fig_parameters", "Fitted Bradley--Terry strengths and Rasch abilities with their uncertainty.")
    fig, ax = plt.subplots(figsize=(5, 2.8)); ax.hist(rasch_items.difficulty.clip(-15, 15), bins=40); ax.set_xlabel("Rasch item difficulty (clipped at $\\pm$15)"); ax.set_ylabel("items")
    pk.save(fig, "fig_rasch_items", "Distribution of Rasch item difficulties over the 3,083 items.")
    fig, ax = plt.subplots(figsize=(4, 2.8)); ax.bar(["subset", "lattice", "LHS"], [designs["best_J"]["subset"], designs["best_J"]["lattice"], designs["best_J"]["lhs"]]); ax.set_ylim(.93, .95); ax.set_ylabel("best J found")
    pk.save(fig, "fig_designs_v3", "Best $J$ found by the enumerated subsets and the two sampled designs of 100 mixes each.")
    Zb = np.load(out / "Zb.npz")
    fig, axes = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
    for ax, key, lab in zip(axes, ["bt_beta", "rasch_theta"], ["Bradley-Terry strength", "Rasch ability"]):
        ax.boxplot([Zb[key][:, mm.index(m)] for m in order], vert=False, showfliers=False, widths=.6); ax.set_yticks(range(1, len(order) + 1)); ax.set_yticklabels([PRETTY[m] for m in order], fontsize=7); ax.invert_yaxis(); ax.set_xlabel(lab + " over 100 item bootstraps")
    pk.save(fig, "fig_parameter_bootstrap", "Bootstrap distributions of the Bradley--Terry strengths and Rasch abilities (100 item resamples).")
    # tables
    pk.to_tex(single.assign(view=[VP[v] for v in views]).round(3), "single_views", "Objective $J$ of each view alone.")
    pk.to_tex(V.loc[order].rename(index=PRETTY, columns=VP).round(3).reset_index().rename(columns={"model": "model"}), "views_native", "Value of each view per model (native-metric scores).")
    pk.to_tex(Vem.loc[order].rename(index=PRETTY, columns=VP).round(3).reset_index(), "views_em", "Value of each view per model (exact-match scores).")
    pk.to_tex(top[["rank", "label", "n_views"] + [f"w_{v}" for v in views] + ["stability", "transitivity", "reference", "J"]].round(3), "top_mixes", "The fifteen best candidate mixes with their weights and objective terms.")
    bs = combos[combos.label.str.startswith("subset")].sort_values("J", ascending=False).groupby("n_views").head(1).sort_values("n_views")
    pk.to_tex(bs[["n_views", "label", "J", "stability", "transitivity", "reference"]].round(3), "best_subset_per_size", "Best equal-weight subset for each subset size.")
    pk.to_tex(pd.DataFrame({"model": [PRETTY[m] for m in order], "BT strength": np.array(pn["bradley_terry"]["beta"])[idx], "BT SE vs ref": np.array(pn["bradley_terry"]["se_vs_reference"])[idx], "BT bootstrap SD": np.array(pb["bt_beta_sd_bootstrap"])[idx], "Rasch ability": np.array(pn["rasch"]["theta"])[idx], "Rasch SE": np.array(pn["rasch"]["se_theta"])[idx], "Rasch bootstrap SD": np.array(pb["rasch_theta_sd_bootstrap"])[idx], "Copeland": np.array(pn["copeland"])[idx], "Kemeny position": (np.array(pn["kemeny"]["position"])[idx] + 1).astype(int)}).round(3), "parameters", f"Fitted parameters with standard errors (native metric). Kemeny cost {pn['kemeny']['kendall_cost']:.0f} of {pn['kemeny']['max_cost']:.0f}.")
    pk.to_tex(shc.round(3), "split_half", "Split-half honesty check, every split.", longtable=True)
    pk.to_tex(pd.DataFrame([{"quantity": k, "value": json.dumps(v) if isinstance(v, (dict, list)) else v} for k, v in sh.items() if k != "selection_counts"]), "split_half_summary", "Split-half summary.")
    pk.to_tex(pd.DataFrame([{"design": k, **v} for k, v in designs.items() if k != "best_J"]).round(3), "designs", "Sampled designs of 100 mixes: coverage diagnostics.")
    pk.copy_data(out, extra=[V6 / "v3_aggregation" / "REPORT.md"])
    # numbers
    b = combos.sort_values("J", ascending=False).iloc[0]; uni = combos[combos.label == "subset_11111111"].J.iloc[0]
    bw = ", ".join(f"{VP[v]} {b[f'w_{v}']:.2f}" for v in views if b[f"w_{v}"] > 0)
    nat = info["LB"]["native"].set_index("model"); emr = info["LB"]["em_only"].set_index("model")
    setup = r"""\section{Setup}
""" + SETUP_COMMON + r"""
\subsection{What v3 searches}
\begin{itemize}
\item \textbf{Per-answer rule.} None is searched: each dataset keeps its own native metric (numeric tolerance, exact match or ROUGE-L). v3 asks a different question from v2 and v4: not ``how should an answer be scored'' but ``how should per-dataset scores be pooled into one ranking''.
\item \textbf{Eight aggregation views} from the literature, each mapping the models $\times$ datasets $\times$ items score tensor to one number per model: mean raw score; baseline-normalised mean (Open LLM Leaderboard v2: $(\text{raw} - \text{random baseline})/(1 - \text{baseline})$, clipped at 0); mean $z$ across datasets; mean win rate (HELM: fraction of other models beaten per dataset); Borda; Kemeny score; Bradley--Terry strength from item-level pairwise wins (Chatbot Arena); Rasch ability from a one-parameter IRT fit with items as difficulties (tinyBenchmarks). Views are $z$-scored across models before mixing.
\item \textbf{Candidates.} Every non-empty equal-weight subset of the eight views (255, including the eight corners and the uniform mix), plus 100 uniform-lattice and 100 Latin-hypercube mixes at step 0.05: 455 candidates.
\item \textbf{Objective.} $J = 0.5\,\text{stability} + 0.25\,\text{transitivity} + 0.25\,\text{reference}$: stability = mean Kendall $\tau$ between the mixed ranking on item-bootstrap resamples and on the full data; transitivity = $\tau$ to the Copeland ranking of the per-dataset scores; reference = $\tau$ to the Kemeny consensus of the eight single-view rankings. $J$ measures how reproducible and internally consistent a pooled ranking is, not whether it is right.
\item \textbf{Parameters saved.} Bradley--Terry strengths with analytic SE (vs reference) and bootstrap SD, Rasch abilities with SE and item difficulties with SE, Kemeny order and cost, Copeland, Borda, the win matrix, and per-bootstrap-draw parameters (100 item resamples). Every combination's member parameters, mixed scores, ranks and rank intervals are stored under \texttt{data/combos/}.
\item \textbf{Honesty.} Split-half: 20 random half-splits of the items; the best candidate on half A (20 inner resamples) is scored on half B and compared with pure Bradley--Terry, the uniform mix and the full-data best on half B.
\item \textbf{Leaderboards.} Native metric (headline) and exact match, each pooled by Bradley--Terry with the full significance battery; the five best mixes are reported with bootstrap rank intervals.
\end{itemize}
"""
    results = f"""\\section{{Results}}
\\begin{{table}}[htbp]\\centering\\small\\caption{{v3 audit summary.}}\\label{{tab:v3_summary}}
\\begin{{tabularx}}{{\\textwidth}}{{>{{\\bfseries}}p{{0.30\\textwidth}} L}}\\toprule
Single views & $J$ alone from {single['J alone'].min():.3f} ({VP[single.sort_values('J alone').view.iloc[0]]}) to {single['J alone'].max():.3f} ({VP[single.sort_values('J alone').view.iloc[-1]]}); Bradley--Terry alone {single.set_index('view').loc['bradley_terry', 'J alone']:.3f}, Rasch alone {single.set_index('view').loc['irt_ability', 'J alone']:.3f} \\\\
Best mix & {esc(b.label)}: {esc(bw)}; $J = {b.J:.3f}$ (stability {b.stability:.3f}, transitivity {b.transitivity:.2f}, reference {b.reference:.2f}); uniform mix $J = {uni:.3f}$ \\\\
Candidates & 455 (255 subsets + 100 lattice + 100 LHS); $J$ range {combos.J.min():.3f}--{combos.J.max():.3f}; best per design: subset {designs['best_J']['subset']:.3f}, lattice {designs['best_J']['lattice']:.3f}, LHS {designs['best_J']['lhs']:.3f} \\\\
Split-half honesty & selected mix $J$ {sh['J_A_selected_mean']:.3f} on half A, {sh['J_B_selected_mean']:.3f} on half B (optimism gap {sh['optimism_gap']:.3f}); on half B pure BT {sh['J_B_pure_bt_mean']:.3f}, uniform {sh['J_B_uniform_mean']:.3f}, full-data best {sh['J_B_full_best_mean']:.3f} \\\\
Selected minus pure BT (held out) & ${sh['selected_minus_pure_bt']['mean']:+.3f}$, 95\\,\\% CI $[{sh['selected_minus_pure_bt']['ci95'][0]:+.3f}, {sh['selected_minus_pure_bt']['ci95'][1]:+.3f}]$; selected ahead in {100*sh['selected_minus_pure_bt']['share_selected_ahead']:.0f}\\,\\% of splits; {len(sh['selection_counts'])} distinct mixes selected in 20 splits \\\\
Parameters & BT strengths span {min(pn['bradley_terry']['beta']):+.3f} to {max(pn['bradley_terry']['beta']):+.3f} (bootstrap SD $\\approx$ {np.mean(pb['bt_beta_sd_bootstrap']):.3f}); Rasch abilities {min(pn['rasch']['theta']):+.2f} to {max(pn['rasch']['theta']):+.2f} (SE $\\approx$ {np.mean(pn['rasch']['se_theta']):.2f}); Kemeny cost {pn['kemeny']['kendall_cost']:.0f} of {pn['kemeny']['max_cost']:.0f} \\\\
Leaderboard (native, BT) & first {PRETTY[order[0]]}, then {PRETTY[order[1]]}, {PRETTY[order[2]]}; last {PRETTY[order[-1]]}; Friedman $p$ = {info['friedman']['friedman_p']:.1e}; Kendall's $W$ = {info['SIG']['native']['kendall_W_datasets']['kendall_W']:.2f} \\\\
Leaderboard (exact match, BT) & first {PRETTY[emr.sort_values('rank_bt').index[0]]}; $\\tau$ between the native and exact-match BT rankings {pd.read_csv(out / 'leaderboards' / 'rule_agreement.csv', index_col=0).loc['native', 'em_only']:.2f} \\\\
\\bottomrule\\end{{tabularx}}\\end{{table}}

\\subsection{{Single views and their mixes}}
Every view ranks the same model last and nearly the same three models first; the views differ in the middle (Figure~\\ref{{fig:fig_view_matrix}}). Used alone, the rank-based and mean-based views ($J \\approx 0.93$) beat the two fitted-parameter views (Bradley--Terry {single.set_index('view').loc['bradley_terry', 'J alone']:.3f}, Rasch {single.set_index('view').loc['irt_ability', 'J alone']:.3f}) because the fitted views move more under item resampling. Mixing helps a little: the uniform mix reaches {uni:.3f} and the best four-view subset {b.J:.3f} (Figure~\\ref{{fig:fig_j_by_subset_size}}, Table~\\ref{{tab:top_mixes}}). The whole candidate range is {combos.J.min():.3f}--{combos.J.max():.3f}; the sampled designs land within 0.002 of the best subset (Figure~\\ref{{fig:fig_designs_v3}}).
{figure(pk, 'fig_view_matrix')}{figure(pk, 'fig_single_view_j', 0.6)}{figure(pk, 'fig_j_by_subset_size', 0.6)}{figure(pk, 'fig_top_mix_weights')}{table(pk, 'top_mixes')}

\\subsection{{Honest selection}}
The split-half test (Figure~\\ref{{fig:fig_split_half}}) is the honesty check for the choice of mix. The mix selected on half A loses {sh['optimism_gap']:.3f} of $J$ on half B, and 20 splits select {len(sh['selection_counts'])} different mixes. On the held-out half the selected mix beats pure Bradley--Terry by {sh['selected_minus_pure_bt']['mean']:+.3f} with an interval that includes zero, and the plain uniform mix ({sh['J_B_uniform_mean']:.3f}) does as well as the selected one ({sh['J_B_selected_mean']:.3f}). Mixing views is therefore defensible but not demonstrably better than the uniform mix; pure Bradley--Terry is the least reproducible single rule on this suite.
{figure(pk, 'fig_split_half')}{table(pk, 'split_half_summary')}

\\subsection{{Parameters with standard errors}}
Table~\\ref{{tab:parameters}} and Figure~\\ref{{fig:fig_parameters}} give the fitted Bradley--Terry strengths and Rasch abilities. The analytic standard errors assume the model is right; the bootstrap SDs (Figure~\\ref{{fig:fig_parameter_bootstrap}}) do not, and with ten models they are the ones to quote. Rasch item difficulties are poorly determined (mean SE {pn['rasch_item_difficulty_summary']['se_mean']:.1f}, Figure~\\ref{{fig:fig_rasch_items}}): with ten responses per item the one-parameter model cannot pin individual items down, which is why the Rasch view is the least stable.
{table(pk, 'parameters')}{figure(pk, 'fig_parameters')}{figure(pk, 'fig_parameter_bootstrap')}

\\subsection{{Leaderboard}}
Under the native metric pooled by Bradley--Terry, {PRETTY[order[0]]} is first ($P(\\text{{first}}) = {nat.loc[order[0], 'p_first_bt']:.2f}$) with {PRETTY[order[1]]} and {PRETTY[order[2]]} next; Borda puts {PRETTY[nat.sort_values('rank_borda').index[0]]} first. Exact match puts {PRETTY[emr.sort_values('rank_bt').index[0]]} first. The ends are fixed under every rule and pooling method; Friedman rejects equal models ($p$ = {info['friedman']['friedman_p']:.1e}) while datasets agree only moderately ($W$ = {info['SIG']['native']['kendall_W_datasets']['kendall_W']:.2f}).
{table(pk, 'leaderboard_headline')}{table(pk, 'ranks_by_rule')}{figure(pk, 'fig_bt_all_rules')}{figure(pk, 'fig_rank_bootstrap')}{figure(pk, 'fig_cd_diagram')}

\\subsection{{Comparability and diagnostics}}
{table(pk, 'official_split_by_dataset')}{figure(pk, 'fig_official_f1_models')}{figure(pk, 'fig_diagnostics_scatter', 0.6)}
"""
    pk.write(setup, results)
    return {"best_label": b.label, "best_J": b.J, "uniform_J": uni, "sh": sh, "order": order, "LB": info["LB"], "SIG": info["SIG"], "single": single}


# ================================================================= v4
def build_v4():
    out = V6 / "v4_random_search" / "output"
    pk = Pkg("v4", "Summary Report, v4: Nine-Component Composite, Three Sampled Designs, Honest Selection")
    COMP = ["em", "num_tol", "num_decay", "tok_prec", "tok_rec", "tok_f1", "edit_sim", "rouge_l", "jaccard"]
    CP = {"em": "exact match", "num_tol": "numeric tolerance", "num_decay": "numeric decay", "tok_prec": "token precision", "tok_rec": "token recall", "tok_f1": "token F1", "edit_sim": "edit similarity", "rouge_l": "ROUGE-L", "jaccard": "Jaccard"}
    W = [f"w_{c}" for c in COMP]
    grid = pd.read_csv(out / "grid_candidates.csv"); grid["label"] = grid["label"].fillna(grid["design"] + "_" + grid["rank"].astype(str)); best = json.load(open(out / "best.json")); designs = pd.read_csv(out / "designs.csv"); ds = json.load(open(out / "designs_summary.json"))
    nested = json.load(open(out / "selection" / "nested.json")); draws = np.load(out / "selection" / "nested_draws.npz"); plateau = pd.read_csv(out / "selection" / "plateau.csv")
    lodo = pd.read_csv(out / "selection" / "lodo.csv"); lofo = pd.read_csv(out / "selection" / "lofo.csv"); pfam = json.load(open(out / "selection" / "per_family.json")); sens = json.load(open(out / "selection" / "sensitivity.json"))
    corr = pd.read_csv(out / "anchors" / "correctness.csv"); cj = json.load(open(out / "anchors" / "correctness.json")); anch = pd.read_csv(out / "anchors" / "anchor_components.csv"); comp = pd.read_csv(out / "components.csv")
    RULES = ["em_only", "v1_rubric", "top1", "top2", "top3", "top4", "top5", "best_anchor", "pareto_knee"]; RP = {"em_only": "exact match", "v1_rubric": "v1 rubric", "best_anchor": "best-rho", "pareto_knee": "knee", **{f"top{i}": f"top{i}" for i in range(1, 6)}}

    def wstr(row): return ", ".join(f"{CP[c]} {row[f'w_{c}']:.2f}" for c in COMP if row[f"w_{c}"] > 0)
    PARAMS = {r: json.load(open(out / "leaderboards" / r / "params.json")) for r in RULES}
    info = leaderboard_block(pk, out, RULES, "v1_rubric", RP, lambda r: "--" if PARAMS[r]["weights"] is None else ", ".join(f"{k} {v:.2f}" for k, v in PARAMS[r]["weights"].items() if v > 0))
    order = info["order"]
    v1 = grid[grid.label == "v1_rubric"].iloc[0]; b = grid.sort_values("J", ascending=False).iloc[0]
    pk.copy_fig(out / "fig_landscape.png", "fig_landscape", "All 305 candidates sorted by $J$, with the baselines marked.")
    pk.copy_fig(out / "fig_designs.png", "fig_designs", "Sampled designs: best $J$ found per seed.")
    pk.copy_fig(out / "selection" / "fig_nested.png", "fig_nested", "In-bag vs out-of-bag $J$ of the selected candidate against the v1 rubric.")
    pk.copy_fig(out / "selection" / "fig_plateau.png", "fig_plateau", "Bootstrap band over sorted candidates and the plateau boundary.")
    pk.copy_fig(out / "anchors" / "fig_pareto.png", "fig_pareto", "Agreement $J$ against anchor correctness $\\rho$ for every candidate.")
    # J by design
    fig, ax = plt.subplots(figsize=(5, 3))
    for dsg in ["dirichlet", "lhs", "uniform_lattice"]:
        d = grid[grid.design == dsg]; ax.hist(d.J, bins=30, histtype="step", label=f"{dsg} ({len(d)})")
    for lab in ["v1_rubric", "em_only", "num_tol_only", "f1_only", "uniform"]:
        r = grid[grid.label == lab]
        if len(r): ax.axvline(r.J.iloc[0], ls=":", lw=.8, c="k"); ax.text(r.J.iloc[0], ax.get_ylim()[1] * .9, lab, rotation=90, fontsize=6, va="top")
    ax.set_xlabel("J"); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_j_by_design", "Distribution of $J$ over the 100 candidates of each design, with the five baselines marked.")
    top = grid.sort_values("J", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(7, 3)); bottom = np.zeros(len(top))
    for c in COMP: ax.bar(range(len(top)), top[f"w_{c}"], bottom=bottom, label=CP[c]); bottom += top[f"w_{c}"].values
    ax.set_xticks(range(len(top))); ax.set_xticklabels([f"{l} ({j:.3f})" for l, j in zip(top.label, top.J)], rotation=60, ha="right", fontsize=6); ax.set_ylabel("weight"); ax.legend(frameon=False, fontsize=5, ncol=3)
    pk.save(fig, "fig_top_weights", "Component weights of the fifteen best candidates.")
    fig, axes = plt.subplots(3, 3, figsize=(9, 7))
    for ax, c in zip(axes.flat, COMP): ax.scatter(grid[f"w_{c}"], grid.J, s=5, alpha=.5); ax.scatter(v1[f"w_{c}"], v1.J, c="C3", s=25, zorder=3); ax.set_xlabel(CP[c]); ax.set_ylabel("J")
    pk.save(fig, "fig_marginals", "$J$ against each component weight over all candidates; red = v1 rubric.")
    fig, ax = plt.subplots(figsize=(6, 3.2))
    for col, lab in [("J", "Borda"), ("J_kemeny", "Kemeny"), ("J_copeland", "Copeland"), ("J_bt", "Bradley-Terry")]: ax.plot(np.sort(grid[col].values)[::-1], lw=1, label=lab)
    ax.set_xlabel("candidate, sorted by J under each rule"); ax.set_ylabel("J"); ax.legend(frameon=False)
    pk.save(fig, "fig_j_pooling_rules", "Objective over all candidates under four pooling rules.")
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.8))
    for ax, c in zip(axes, ["regret", "centred_L2_discrepancy", "mean_J"]): ax.boxplot([designs[designs.design == d][c] for d in designs.design.unique()], tick_labels=[d.replace("_", "\n") for d in designs.design.unique()]); ax.set_title(c.replace("_", " "), fontsize=8)
    pk.save(fig, "fig_design_metrics", "Sampled designs over 20 seeds: regret against the best over all seeds and designs, centred $L_2$ discrepancy and mean $J$ of the design.")
    # selection
    chosen = draws["chosen"]; wsel = grid.iloc[chosen][W].values
    fig, axes = plt.subplots(3, 3, figsize=(9, 6))
    for ax, j in zip(axes.flat, range(9)): ax.hist(wsel[:, j], bins=np.arange(-.025, 1.05, .05)); ax.axvline(v1[W[j]], c="C3", ls=":"); ax.set_title(CP[COMP[j]], fontsize=8)
    pk.save(fig, "fig_selected_weights", "Weights selected as in-bag best across 1,000 bootstrap resamples; dotted = v1 rubric.")
    d_oob = draws["J_out_sel"] - draws["J_out_v1"] if "J_out_v1" in draws.files else draws["J_out_sel"] - draws["J_out_ref"]
    fig, ax = plt.subplots(figsize=(4.5, 3)); ax.hist(d_oob, bins=40); ax.axvline(0, c="k", lw=.8); ax.axvline(d_oob.mean(), c="C3", ls=":", label=f"mean {d_oob.mean():+.3f}"); ax.set_xlabel("out-of-bag J(selected) - J(v1 rubric)"); ax.legend(frameon=False)
    pk.save(fig, "fig_oob_difference", "Paired out-of-bag difference between the selected candidate and the v1 rubric over 1,000 resamples.")
    L = lodo[lodo.kind == "dataset"] if "dataset" in set(lodo.kind) else lodo
    piv = L.pivot(index="held_out", columns="weights_from", values="tau_heldout_mean"); cols = list(piv.columns); x = np.arange(len(piv))
    fig, ax = plt.subplots(figsize=(8, 3))
    for i, c in enumerate(cols): ax.bar(x + (i - (len(cols) - 1) / 2) * .8 / len(cols), piv[c], .8 / len(cols), label=c.replace("_", " "))
    ax.set_xticks(x); ax.set_xticklabels(piv.index, rotation=60, ha="right", fontsize=6); ax.set_ylabel("tau held-out -> pooled rest"); ax.legend(frameon=False, fontsize=7); ax.axhline(0, c="k", lw=.5)
    pk.save(fig, "fig_lodo_tau", "Leave-one-dataset-out: agreement of the held-out dataset with the pooled rest under re-fitted weights, the full best and the v1 rubric.")
    fams = ["EM", "SM", "TQA", "FIN"]
    FW = pd.DataFrame({FAM[f]: [pfam[f]["best_weights"].get(c, 0) for c in COMP] for f in fams}, index=[CP[c] for c in COMP]); FW["global best"] = [b[f"w_{c}"] for c in COMP]; FW["v1 rubric"] = [v1[f"w_{c}"] for c in COMP]
    fig, ax = plt.subplots(figsize=(6, 3.4)); im = ax.imshow(FW.values, cmap="Blues", vmin=0, vmax=1, aspect="auto"); ax.set_xticks(range(FW.shape[1])); ax.set_xticklabels(FW.columns, rotation=30, ha="right"); ax.set_yticks(range(9)); ax.set_yticklabels(FW.index)
    for i in range(9):
        for j in range(FW.shape[1]):
            if FW.values[i, j] > 0: ax.text(j, i, f"{FW.values[i, j]:.2f}", ha="center", va="center", fontsize=6, color="w" if FW.values[i, j] > .5 else "k")
    pk.save(fig, "fig_family_weights", "Per-family optimum, global optimum and the v1 rubric over the nine components.")
    fig, ax = plt.subplots(figsize=(5, 3)); x = np.arange(4)
    ax.bar(x - .27, [pfam[f]["J_family_best"] for f in fams], .27, label="own optimum"); ax.bar(x, [pfam[f]["J_family_under_global_best"] for f in fams], .27, label="global best"); ax.bar(x + .27, [pfam[f].get("J_family_under_v1", pfam[f].get("J_family_under_reference", np.nan)) for f in fams], .27, label="v1 rubric")
    ax.set_xticks(x); ax.set_xticklabels([FAM[f] for f in fams]); ax.set_ylabel("within-family J"); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_family_j", "Within-family $J$ under each family's own optimum, the global best and the v1 rubric.")
    # anchors
    anch["v1"] = .35 * anch.tok_f1 + .35 * anch.num_decay + .15 * anch.tok_prec + .15 * anch.tok_rec
    bw_ = {c: b[f"w_{c}"] for c in COMP}; anch["bestJ"] = sum(bw_[c] * anch[c] for c in COMP)
    br = corr[corr.label == "best_rho"].iloc[0] if "best_rho" in set(corr.label) else corr.sort_values("rho", ascending=False).iloc[0]; anch["bestrho"] = sum(br[f"w_{c}"] * anch[c] for c in COMP)
    op = anch.groupby("op").agg(utility=("utility", "mean"), v1=("v1", "mean"), bestJ=("bestJ", "mean"), bestrho=("bestrho", "mean"), em=("em", "mean"), n=("v1", "size")).sort_values("utility")
    fig, ax = plt.subplots(figsize=(7, 3)); x = np.arange(len(op)); ax.bar(x - .3, op.utility, .2, label="known utility"); ax.bar(x - .1, op.v1, .2, label="v1 rubric"); ax.bar(x + .1, op.bestJ, .2, label="best J (num tol)"); ax.bar(x + .3, op.bestrho, .2, label="best rho")
    ax.set_xticks(x); ax.set_xticklabels(op.index, rotation=45, ha="right"); ax.legend(frameon=False, fontsize=6)
    pk.save(fig, "fig_anchor_operators", "Anchors: known utility of each operator against the mean score it receives under the v1 rubric, the best-$J$ and the best-$\\rho$ candidates.")
    rho_ds = pd.DataFrame({k: anch.groupby("dataset").apply(lambda d: d[[k, "utility"]].corr(method="spearman").iloc[0, 1]) for k in ["v1", "bestJ", "bestrho"]})
    fig, ax = plt.subplots(figsize=(8, 2.8)); x = np.arange(len(rho_ds))
    for i, c in enumerate(rho_ds.columns): ax.bar(x + (i - 1) * .27, rho_ds[c], .27, label={"v1": "v1 rubric", "bestJ": "best J", "bestrho": "best rho"}[c])
    ax.set_xticks(x); ax.set_xticklabels(rho_ds.index, rotation=60, ha="right", fontsize=6); ax.set_ylabel("Spearman rho to utility"); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_rho_per_dataset", "Anchor correctness per dataset under the v1 rubric, the best-$J$ and the best-$\\rho$ candidates.")
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.8))
    for ax, c, lab in zip(axes, ["auc", "wrong_mean", "hedge_gap"], ["AUC correct vs wrong", "mean score of wrong answers", "hedge gap"]): ax.scatter(corr.J, corr[c], s=6, alpha=.5, c="grey"); r = corr[corr.label == "v1_rubric"]; ax.scatter(r.J, r[c], c="C3", s=30, zorder=3); ax.set_xlabel("J"); ax.set_ylabel(lab)
    pk.save(fig, "fig_anchor_metrics_vs_j", "Three further anchor diagnostics against $J$ for every candidate (red = v1 rubric).")
    fig, ax = plt.subplots(figsize=(4.5, 2.8))
    for i, k in enumerate(["v1_rubric", "best"]): s_ = sens[k]; ax.errorbar(i, s_["J_centre"], yerr=[[s_["J_centre"] - s_["J_min"]], [s_["J_max"] - s_["J_centre"]]], fmt="o", capsize=4, label=f"{k}: {s_['n_neighbours']} neighbours")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["v1 rubric", "best"]); ax.set_ylabel("J (bar = neighbour min/max)"); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_sensitivity", "One-step sensitivity around the v1 rubric and the best candidate.")
    fam_mean = comp.assign(v1=lambda d: .35 * d.tok_f1 + .35 * d.num_decay + .15 * d.tok_prec + .15 * d.tok_rec).groupby(["family", "model"])["v1"].mean().unstack(0).loc[order]
    fig, axes = plt.subplots(1, 5, figsize=(10, 2.2))
    for ax, c in zip(axes, ["num_tol", "edit_sim", "rouge_l", "jaccard", "em"]):
        for t in comp.answer_type.unique(): ax.hist(comp[comp.answer_type == t][c].dropna(), bins=20, histtype="step", density=True, label=t)
        ax.set_title(CP[c], fontsize=8); ax.set_yticks([])
    axes[0].legend(frameon=False, fontsize=5)
    pk.save(fig, "fig_component_distributions", "Distributions of the five components not in v1, by answer type.")
    # tables
    pk.to_tex(grid.sort_values("J", ascending=False).head(25)[["rank", "label"] + W + ["J", "J_kemeny", "J_copeland", "J_bt", "tau_native"]].round(3), "grid_top25", "The 25 best candidates with the objective under the other pooling rules.", longtable=True)
    pk.to_tex(grid[grid.label.isin(["v1_rubric", "em_only", "f1_only", "num_tol_only", "uniform"])][["rank", "label"] + W + ["J", "J_kemeny", "J_copeland", "J_bt", "tau_native"]].round(3), "baselines", "The five fixed baselines on the candidate set.")
    pk.to_tex(pd.DataFrame([{"design": k, **v} for k, v in ds.items()]).round(4), "designs_summary", "Sampled designs: summary over 20 seeds.", fmt="%.4f")
    pk.to_tex(pd.DataFrame([{"quantity": k, "value": json.dumps(v) if isinstance(v, (dict, list)) else v} for k, v in nested.items() if k != "most_selected"]), "nested_selection", "Every quantity saved by the nested item bootstrap.", longtable=True)
    pk.to_tex(plateau.sort_values("J_boot_mean", ascending=False).head(30).round(3), "plateau_top30", "The 30 best candidates with bootstrap statistics.", longtable=True)
    pk.to_tex(lodo.round(3), "lodo_full", "Leave-one-dataset-out, every dataset.", longtable=True); pk.to_tex(lofo.round(3), "lofo_full", "Leave-one-family-out.", longtable=True)
    pk.to_tex(pd.DataFrame([{"family": f, "best weights": wstr({f"w_{c}": pfam[f]["best_weights"].get(c, 0) for c in COMP}), "J own best": pfam[f]["J_family_best"], "J global best": pfam[f]["J_family_under_global_best"]} for f in fams]).round(3), "per_family", "Per-family optimum.")
    pk.to_tex(pd.DataFrame(sens).T.reset_index().rename(columns={"index": "point"}).round(4), "sensitivity", "One-step sensitivity.", fmt="%.4f")
    pk.to_tex(corr[corr.label.notna()][["label"] + W + ["J", "rho", "rho_ds", "auc", "wrong_mean", "hedge_gap"]].round(3), "anchors_rules", "Anchor correctness for the labelled candidates.")
    pk.to_tex(corr[corr.pareto == True][W + ["J", "rho", "auc"]].round(3), "pareto_front", "The $(J,\\rho)$ Pareto front.")
    pk.to_tex(op.reset_index().round(3), "anchor_operators", "Anchor operators: utility and mean score under three rules.")
    pk.to_tex(rho_ds.round(3).reset_index(), "rho_per_dataset", "Anchor correctness per dataset.")
    pk.to_tex(fam_mean.round(3).rename(index=PRETTY, columns=FAM).reset_index(), "family_scores", "Mean v1-rubric score per model within each family.")
    pk.copy_data(out, extra=[V6 / "v4_random_search" / "REPORT.md"])
    cr = {k: cj[k] for k in ["reference", "best_J", "best_rho", "pareto_knee"]}; emj = corr[corr.label == "exact_match"]
    ref_lb = info["LB"]["v1_rubric"].set_index("model"); t1 = info["LB"]["top1"].set_index("model")
    setup = r"""\section{Setup}
""" + SETUP_COMMON + r"""
\subsection{What v4 searches}
\begin{itemize}
\item \textbf{Per-answer rule.} A weighted sum of nine lexical components per answer: exact match, numeric tolerance (1\,\%), numeric decay $e^{-2.5\cdot\text{rel.\ err}}$, token precision, token recall, token F1, edit similarity, ROUGE-L, Jaccard. The v1 rubric is the point (F1 0.35, decay 0.35, precision 0.15, recall 0.15) embedded in nine dimensions.
\item \textbf{Candidates.} The step-0.05 lattice on the nine-weight simplex has 3,108,105 points, too many to enumerate, so three sampled designs of 100 points each (Dirichlet-snapped, Latin hypercube on the simplex, uniform lattice) plus five baselines (exact match only, F1 only, numeric tolerance only, uniform, v1 rubric): 305 candidates. Design comparison over 20 seeds with coverage diagnostics; regret is relative to the best over all seeds and designs since no exhaustive optimum exists.
\item \textbf{Objective.} The same as v2: $J$ = mean Kendall $\tau$ between each dataset's model ranking under the candidate and the Borda pool of the 31 rankings (also under Kemeny, Copeland and Bradley--Terry pooling; $\tau$ to native metrics beside). $J$ measures consistency between datasets, not correctness.
\item \textbf{Correctness.} 31,380 synthetic anchors of known utility (same generator as v2 and v5); Spearman $\rho$, AUC correct vs wrong, mean score of wrong answers, hedge gap; $(J,\rho)$ Pareto front and knee.
\item \textbf{Honesty and transfer.} Nested item bootstrap ($B = 1{,}000$: select in-bag, score out-of-bag; optimism gap; plateau), leave-one-dataset-out and leave-one-family-out, per-family optima, one-step sensitivity (neighbours one lattice step away within the candidate set).
\item \textbf{Leaderboards.} Exact match, v1 rubric (headline for comparability with v2), the five best by $J$, the best by $\rho$ and the Pareto knee, each pooled by Bradley--Terry with the full significance battery.
\end{itemize}
"""
    results = f"""\\section{{Results}}
\\begin{{table}}[htbp]\\centering\\small\\caption{{v4 audit summary.}}\\label{{tab:v4_summary}}
\\begin{{tabularx}}{{\\textwidth}}{{>{{\\bfseries}}p{{0.30\\textwidth}} L}}\\toprule
Candidates & 305 (3 designs $\\times$ 100 + 5 baselines) on a lattice of 3,108,105 points; $J$ range {grid.J.min():.3f}--{grid.J.max():.3f} \\\\
Best & {esc(wstr(b))} ({esc(b.label)}), $J = {b.J:.3f}$, $\\tau$ native {b.tau_native:.2f}; exact match alone $J = {grid[grid.label == 'em_only'].J.iloc[0]:.3f}$ (rank {int(grid[grid.label == 'em_only']['rank'].iloc[0])}); v1 rubric $J = {v1.J:.3f}$ (rank {int(v1['rank'])} of 305) \\\\
Best per design & Dirichlet {ds['dirichlet_lattice']['best_J_max']:.3f}, LHS {ds['lhs_simplex']['best_J_max']:.3f}, uniform lattice {ds['uniform_lattice']['best_J_max']:.3f}; regret over seeds $\\le$ {max(ds[k]['regret_max'] for k in ds):.3f} \\\\
Nested selection ($B$ = 1,000) & in-bag $J$ of selected {nested['in_bag_J_of_selected_mean']:.3f}, out-of-bag {nested['out_of_bag_J_of_selected_mean']:.3f} (optimism gap {nested['optimism_gap']:.3f}); v1 rubric out-of-bag {nested.get('out_of_bag_J_ref_mean', nested.get('out_of_bag_J_v1_mean', float('nan'))):.3f} \\\\
Selected vs v1 rubric, out of bag & ${d_oob.mean():+.3f}$, 95\\,\\% CI $[{np.percentile(d_oob, 2.5):+.3f}, {np.percentile(d_oob, 97.5):+.3f}]$; {nested['n_distinct_selected']} distinct candidates selected \\\\
Plateau & {nested['plateau_size']} of 305 not significantly below the best; practical plateau (within 0.02): {nested.get('practical_plateau_size', nested.get('practical_plateau_size_within_0.02'))}; v1 rubric inside: {'yes' if nested.get('ref_in_plateau', nested.get('v1_in_plateau')) else 'no'} \\\\
Transfer (LODO) & mean held-out $\\tau$: re-fitted weights {piv[cols[0]].mean():+.2f}, full best {piv['full_best'].mean() if 'full_best' in piv else float('nan'):+.2f}, v1 rubric {piv[[c for c in cols if 'v1' in c or 'ref' in c][0]].mean():+.2f} \\\\
Anchors & v1 rubric $\\rho$ {cr['reference']['rho']:.3f}; best-$J$ {cr['best_J']['rho']:.3f}; best-$\\rho$ {cr['best_rho']['rho']:.3f}; knee {cr['pareto_knee']['rho']:.3f}; exact match {emj.rho.iloc[0] if len(emj) else float('nan'):.3f}; Spearman($J$, $\\rho$) across candidates {cj['spearman_J_vs_rho_across_candidates']:+.2f} \\\\
Sensitivity & one step moves $J$ by at most {sens['v1_rubric']['flatness_range']:.3f} around the v1 rubric and {sens['best']['J_max'] - sens['best']['J_min']:.3f} around the best \\\\
Leaderboard (v1 rubric, BT) & first {PRETTY[order[0]]}, then {PRETTY[order[1]]}, {PRETTY[order[2]]}; last {PRETTY[order[-1]]}; Friedman $p$ = {info['friedman']['friedman_p']:.1e}; $W$ = {info['SIG']['v1_rubric']['kendall_W_datasets']['kendall_W']:.2f} \\\\
Leaderboard (best $J$ = numeric tolerance, BT) & first {PRETTY[t1.sort_values('rank_bt').index[0]]}; identical ranking to exact match ($\\tau$ = 1.00) \\\\
\\bottomrule\\end{{tabularx}}\\end{{table}}

\\subsection{{A single typed metric matches the nine-component composite}}
The best candidate is numeric tolerance alone ($J = {b.J:.3f}$), with exact match alone second ({grid[grid.label == 'em_only'].J.iloc[0]:.3f}); every mixed candidate is below both (Figures~\\ref{{fig:fig_landscape}}, \\ref{{fig:fig_j_by_design}}, \\ref{{fig:fig_top_weights}}). The v1 rubric sits at rank {int(v1['rank'])} of 305, but the whole candidate range is {grid.J.max() - grid.J.min():.3f} wide. The three designs find the same region (Table~\\ref{{tab:designs_summary}}); the uniform lattice has the best coverage and the highest best-$J$.
{figure(pk, 'fig_landscape')}{figure(pk, 'fig_j_by_design', 0.6)}{figure(pk, 'fig_top_weights')}{table(pk, 'designs_summary')}{figure(pk, 'fig_marginals')}

\\subsection{{Honest selection}}
As in v2, the in-bag winner loses {nested['optimism_gap']:.3f} out of bag and ends {d_oob.mean():+.3f} from the v1 rubric with an interval that includes zero; {nested['n_distinct_selected']} different candidates are selected across resamples and the plateau covers {nested['plateau_size']} of 305 (Figures~\\ref{{fig:fig_nested}}, \\ref{{fig:fig_oob_difference}}, \\ref{{fig:fig_selected_weights}}).
{figure(pk, 'fig_nested', 0.6)}{figure(pk, 'fig_oob_difference', 0.5)}{figure(pk, 'fig_selected_weights')}

\\subsection{{Transfer}}
Re-fitted weights predict a held-out dataset no better than the v1 rubric (Figure~\\ref{{fig:fig_lodo_tau}}); the per-family optima are numeric tolerance for EM and SM but recall- and precision-heavy mixes for TQA and FIN (Figure~\\ref{{fig:fig_family_weights}}, Table~\\ref{{tab:per_family}}).
{figure(pk, 'fig_lodo_tau')}{figure(pk, 'fig_family_weights', 0.7)}{table(pk, 'per_family')}

\\subsection{{Correctness}}
Numeric tolerance alone is the best by $J$ but the worst labelled rule on the anchors ($\\rho$ = {cr['best_J']['rho']:.3f} vs {cr['reference']['rho']:.3f} for the v1 rubric): it gives no partial credit to near misses, which the anchors reward (Figure~\\ref{{fig:fig_anchor_operators}}). The Pareto knee ({esc(', '.join(f'{k} {v:.2f}' for k, v in cr['pareto_knee']['weights'].items() if v > 0))}) keeps $J$ = {cr['pareto_knee']['J']:.3f} and $\\rho$ = {cr['pareto_knee']['rho']:.3f}. Across candidates $J$ and $\\rho$ correlate {cj['spearman_J_vs_rho_across_candidates']:+.2f}: agreement and correctness pull apart here as in v2.
{table(pk, 'anchors_rules')}{figure(pk, 'fig_pareto', 0.7)}{figure(pk, 'fig_anchor_operators')}

\\subsection{{Leaderboard}}
Under the v1 rubric the ranking is the one v2 reports (same answers, same rule): {PRETTY[order[0]]} first by Bradley--Terry, {PRETTY[ref_lb.sort_values('rank_borda').index[0]]} first by Borda, {PRETTY[order[-1]]} last. Under the best-$J$ rule (numeric tolerance) and under exact match {PRETTY[t1.sort_values('rank_bt').index[0]]} is first. Rule choice moves the top three and nothing else.
{table(pk, 'leaderboard_headline')}{table(pk, 'ranks_by_rule')}{figure(pk, 'fig_bt_all_rules')}{figure(pk, 'fig_rank_bootstrap')}

\\subsection{{Comparability and diagnostics}}
{table(pk, 'official_split_by_dataset')}{figure(pk, 'fig_diagnostics_scatter', 0.6)}
"""
    pk.write(setup, results)
    return {"grid": grid, "nested": nested, "cj": cj, "corr": corr, "order": order, "LB": info["LB"], "SIG": info["SIG"], "lodo_piv": piv, "d_oob": d_oob, "ds": ds}


# ================================================================= v5
def build_v5():
    out = V6 / "v5_metric_library" / "output"
    pk = Pkg("v5", "Summary Report, v5: A 100-Metric Library Calibrated on Answers of Known Quality")
    mt = pd.read_csv(out / "metric_table.csv"); clusters = json.load(open(out / "clusters.json")); sel = json.load(open(out / "selected.json")); ens = json.load(open(out / "ensemble.json"))
    grid = pd.read_csv(out / "grid_all.csv"); base = pd.read_csv(out / "baselines_grid.csv"); val = json.load(open(out / "validation.json")); probes = pd.read_csv(out / "probes.csv"); lodo = pd.read_csv(out / "lodo.csv")
    designs = pd.read_csv(out / "designs.csv"); ds = json.load(open(out / "designs_summary.json")); items = pd.read_csv(out / "item_scores.csv"); lbj = json.load(open(out / "leaderboard.json"))
    SEL = sel["selected"]; SP = {"tok_f1": "token F1", "num_decay_2p5": "numeric decay (2.5)", "prefix_ratio": "prefix ratio"}
    RULES = ["em_only", "native", "ensemble", "top1", "top2", "top3", "top4", "top5"]; RP = {"em_only": "exact match", "native": "native metric", "ensemble": "ensemble", **{f"top{i}": f"top{i}" for i in range(1, 6)}}
    PARAMS = {r: json.load(open(out / "leaderboards" / r / "params.json")) for r in RULES if (out / "leaderboards" / r / "params.json").exists()}
    info = leaderboard_block(pk, out, RULES, "ensemble", RP, lambda r: "--" if PARAMS.get(r, {}).get("weights") is None else ", ".join(f"{k} {v:.2f}" for k, v in PARAMS[r]["weights"].items()))
    order = info["order"]
    pk.copy_fig(V6 / "v5_metric_library" / "paper" / "figures" / "fig_selection.png", "fig_selection", "Metric selection: anchor agreement of every library metric with the selected set marked.")
    pk.copy_fig(V6 / "v5_metric_library" / "paper" / "figures" / "fig_probes.png", "fig_probes", "Probes: mean score per anchor operator against known utility for the ensemble and the single-metric baselines.")
    pk.copy_fig(out / "fig_leaderboard.png", "fig_leaderboard", "Ensemble leaderboard with bootstrap intervals and the native-metric ranking beside.")
    # metric library
    fig, ax = plt.subplots(figsize=(5.5, 4)); fams = sorted(mt.family.unique())
    for f in fams: d = mt[mt.family == f]; ax.scatter(d.auc, d.rho, s=10, label=f, alpha=.7)
    d = mt[mt.metric.isin(SEL)]; ax.scatter(d.auc, d.rho, s=60, facecolors="none", edgecolors="k", lw=1.2, label="selected")
    for r in d.itertuples(): ax.annotate(r.metric, (r.auc, r.rho), fontsize=6, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("AUC correct vs wrong"); ax.set_ylabel("Spearman rho to utility"); ax.legend(frameon=False, fontsize=6, ncol=2)
    pk.save(fig, "fig_metric_library", "The 100-metric library on the anchors: AUC against Spearman $\\rho$, coloured by family; the three selected metrics are circled.")
    cs = pd.Series({k: len(v) for k, v in clusters.items()}).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 2.8)); ax.bar(range(len(cs)), cs.values); ax.set_xticks(range(len(cs))); ax.set_xticklabels(cs.index, rotation=70, ha="right", fontsize=5); ax.set_ylabel("metrics in cluster")
    pk.save(fig, "fig_clusters", "Cluster sizes after merging metrics with $|$Spearman$| \\ge 0.95$ (45 representatives).")
    fb = mt.groupby("family").agg(n=("metric", "size"), rho_max=("rho", "max"), rho_mean=("rho", "mean"), auc_max=("auc", "max")).sort_values("rho_max", ascending=False)
    fig, ax = plt.subplots(figsize=(6, 2.8)); x = np.arange(len(fb)); ax.bar(x - .2, fb.rho_mean, .4, label="mean rho"); ax.bar(x + .2, fb.rho_max, .4, label="best rho"); ax.set_xticks(x); ax.set_xticklabels(fb.index, rotation=45, ha="right"); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_family_rho", "Anchor $\\rho$ per metric family: mean and best member.")
    # grid
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.6))
    for ax, c in zip(axes, ["w_tok_f1", "w_num_decay_2p5", "w_prefix_ratio", "lambda"]): ax.scatter(grid[c], grid.J, s=3, alpha=.3); ax.set_xlabel(c.replace("w_", "weight ").replace("_", " ")); ax.set_ylabel("J")
    pk.save(fig, "fig_grid_marginals", "Objective $J$ against each selected weight and the hedge penalty $\\lambda$ over all 6,630 grid points.")
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.4))
    top100 = grid.sort_values("J", ascending=False).head(100)
    for ax, c in zip(axes, ["w_tok_f1", "w_num_decay_2p5", "w_prefix_ratio", "lambda"]): ax.hist(top100[c], bins=20); ax.set_title(c.replace("w_", "").replace("_", " "), fontsize=8); ax.axvline(top100[c].mean(), c="C3", ls=":")
    pk.save(fig, "fig_top100_weights", "Weights and $\\lambda$ of the 100 best grid points that form the ensemble (dotted = mean).")
    fig, axes = plt.subplots(1, 5, figsize=(11, 2.4))
    for ax, c in zip(axes, ["rho", "auc", "js", "tau_native", "bad"]): ax.scatter(grid[c], grid.J, s=3, alpha=.3); ax.set_xlabel(c); ax.set_ylabel("J")
    pk.save(fig, "fig_objective_terms", "Objective $J$ against each of its five terms over the grid.")
    fig, ax = plt.subplots(figsize=(6, 3)); x = np.arange(len(base)); ax.bar(x - .3, base.rho, .2, label="rho"); ax.bar(x - .1, base.auc, .2, label="AUC"); ax.bar(x + .1, base.tau_native, .2, label="tau native"); ax.bar(x + .3, base.J, .2, label="J")
    ax.set_xticks(x); ax.set_xticklabels(base.baseline, rotation=30, ha="right", fontsize=7); ax.set_ylim(.7, 1.0); ax.legend(frameon=False, fontsize=7, ncol=4)
    pk.save(fig, "fig_baselines", "Single-metric baselines against the ensemble under the same objective terms.")
    fig, ax = plt.subplots(figsize=(7, 3)); pr = probes.sort_values("utility"); x = np.arange(len(pr))
    ax.bar(x - .3, pr.utility, .2, label="known utility"); ax.bar(x - .1, pr.ensemble, .2, label="ensemble"); ax.bar(x + .1, pr.native, .2, label="native"); ax.bar(x + .3, pr.em, .2, label="exact match")
    ax.set_xticks(x); ax.set_xticklabels(pr.op, rotation=45, ha="right"); ax.legend(frameon=False, fontsize=6, ncol=4)
    pk.save(fig, "fig_probe_operators", "Mean score per anchor operator under the ensemble, the native metric and exact match, against known utility.")
    fig, ax = plt.subplots(figsize=(7, 2.8)); x = np.arange(len(lodo)); ax.bar(x - .2, lodo.rho_heldout_lodo, .4, label="selection + grid refitted without the dataset"); ax.bar(x + .2, lodo.rho_heldout_full, .4, label="full-data ensemble")
    ax.set_xticks(x); ax.set_xticklabels(lodo.held_out, rotation=60, ha="right", fontsize=6); ax.set_ylabel("anchor rho on the held-out dataset"); ax.set_ylim(.7, 1); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_lodo", "Leave-one-dataset-out: anchor $\\rho$ on the held-out dataset under the re-fitted and the full-data ensemble.")
    fig, axes = plt.subplots(1, 3, figsize=(9, 2.8))
    for ax, c in zip(axes, ["regret", "centred_L2_discrepancy", "best_J_found"]): ax.boxplot([designs[designs.design == d][c] for d in designs.design.unique()], tick_labels=[d.replace("_", "\n") for d in designs.design.unique()]); ax.set_title(c.replace("_", " "), fontsize=8)
    pk.save(fig, "fig_design_metrics", "Sampled designs over 20 seeds against the exhaustive grid.")
    items["spread"] = items.score_hi - items.score_lo
    sp = items.groupby("dataset").spread.mean().sort_values()
    fig, ax = plt.subplots(figsize=(7, 2.6)); ax.bar(range(len(sp)), sp.values); ax.set_xticks(range(len(sp))); ax.set_xticklabels(sp.index, rotation=60, ha="right", fontsize=6); ax.set_ylabel("mean ensemble spread (hi - lo)")
    pk.save(fig, "fig_ensemble_spread", "Ensemble uncertainty per dataset: mean spread of the per-answer score across the 100 weightings.")
    fig, axes = plt.subplots(1, 4, figsize=(9, 2.4), sharey=True)
    for ax, t in zip(axes, ["numeric", "boolean", "text", "free_form"]):
        d = items[items.answer_type == t]
        if len(d): ax.hexbin(d.native_value, d.score, gridsize=15, cmap="Blues", mincnt=1, bins="log"); ax.set_title(t); ax.set_xlabel("native metric")
    axes[0].set_ylabel("ensemble score")
    pk.save(fig, "fig_native_vs_ensemble", "Per-answer native metric against the ensemble score, by answer type.")
    # tables
    pk.to_tex(mt.sort_values("rho", ascending=False).round(3), "metric_table", "Every library metric: anchor $\\rho$, AUC, gap, family, cluster.", longtable=True)
    pk.to_tex(pd.DataFrame([{"quantity": k, "value": json.dumps(v) if isinstance(v, (dict, list)) else v} for k, v in sel.items() if k != "trace"]), "selected", "Metric selection summary.")
    pk.to_tex(pd.DataFrame(sel["trace"]) if isinstance(sel["trace"], list) and isinstance(sel["trace"][0], dict) else pd.DataFrame({"step": range(len(sel["trace"])), "trace": [json.dumps(t) for t in sel["trace"]]}), "selection_trace", "Forward-selection trace.")
    pk.to_tex(pd.DataFrame([{"quantity": k, "value": json.dumps(v) if isinstance(v, (dict, list)) else v} for k, v in ens.items() if k != "top_weightings"]), "ensemble", "Ensemble summary.", longtable=True)
    pk.to_tex(grid.sort_values("J", ascending=False).head(25).round(3), "grid_top25", "The 25 best weightings with every objective term.")
    pk.to_tex(base.round(3), "baselines", "Baselines under the same objective.")
    pk.to_tex(probes.round(3), "probes", "Probes: mean score per anchor operator.")
    pk.to_tex(lodo.round(3), "lodo", "Leave-one-dataset-out.", longtable=True)
    pk.to_tex(pd.DataFrame([{"quantity": k, "value": v} for k, v in val.items()]).round(4), "validation", "Validation summary.", fmt="%.4f")
    pk.to_tex(pd.DataFrame([{"design": k, **v} for k, v in ds.items() if isinstance(v, dict)]).round(4), "designs_summary", f"Sampled designs vs the exhaustive grid (best $J$ = {ds['exhaustive_best_J']:.4f} over {ds['n_grid']} points).", fmt="%.4f")
    pk.to_tex(sp.round(3).reset_index(), "ensemble_spread", "Mean ensemble spread per dataset.")
    pk.copy_data(out, extra=[V6 / "v5_metric_library" / "REPORT.md", V6 / "v5_metric_library" / "notes" / "04_RESULTS.md"])
    ensr = info["LB"]["ensemble"].set_index("model"); natr = info["LB"]["native"].set_index("model"); emr = info["LB"]["em_only"].set_index("model")
    e_base = base.set_index("baseline")
    setup = r"""\section{Setup}
""" + SETUP_COMMON + r"""
\subsection{What v5 searches}
\begin{itemize}
\item \textbf{Metric library.} 100 per-answer metrics in twelve families (exact-match variants, token overlap, character and sequence similarity, numeric tolerance and graded numeric error, set metrics for list golds, structure and task-specific scores, length, commitment / hedging, semantic placeholders), computed for every (model, item) pair and for every anchor.
\item \textbf{Anchors as the quality signal.} 31,380 synthetic answers generated from the golds by 20 typed operators with a known utility each (identity, verbose, tagged, unit variant = 1; paraphrase 0.95; near misses 0.75 / 0.45 / 0.15; superset 0.6; typo 0.6; partial 0.5; shuffled 0.4; hedge 0.3; list dump 0.25; digit typo 0.2; sign flip and magnitude 0.05; flip, no answer, wrong random = 0). v5 is the only version whose objective is correctness against this signal rather than agreement among the ranked models.
\item \textbf{Selection.} Drop constant metrics; cluster $|$Spearman$| \ge 0.95$ into representatives; keep candidates above an anchor-agreement floor; forward selection maximising leave-one-dataset-out Spearman of a non-negative least-squares fit to utility.
\item \textbf{Weights.} Exhaustive grid at step 0.02 over the selected weights (sum to 1) $\times$ five hedge penalties $\lambda$ (score multiplied by $1 - \lambda$ when the answer hedges): 6,630 points. Objective $J = 0.30\,\rho + 0.15\,\text{AUC} + 0.20\,(1 - \text{JS}/\ln 2) + 0.15\,\tau_{\text{native}} + 0.20\,(1 - \text{wrong mean})$, where JS is the Jensen--Shannon divergence between datasets' score distributions at matched operator (cross-dataset consistency) and $\tau_{\text{native}}$ the agreement of the composite's model ranking with the native-metric ranking. The ensemble is the mean of the 100 best weightings, so each answer carries a score and a spread.
\item \textbf{Validation.} Leave-one-dataset-out re-selection and re-fitting; utility-scale perturbation ($\pm 0.15$, five draws); gaming probes (mean score per operator vs utility against single-metric baselines); sampled designs looked up in the exhaustive grid.
\item \textbf{Leaderboards.} Exact match, the native metric, the ensemble (headline) and the five best single weightings, each pooled by Bradley--Terry with the full significance battery.
\end{itemize}
"""
    results = f"""\\section{{Results}}
\\begin{{table}}[htbp]\\centering\\small\\caption{{v5 audit summary.}}\\label{{tab:v5_summary}}
\\begin{{tabularx}}{{\\textwidth}}{{>{{\\bfseries}}p{{0.30\\textwidth}} L}}\\toprule
Library & 100 metrics, {sel['n_constant']} constant on this data, {sel['n_representatives']} cluster representatives, {sel['n_candidates']} candidates above the floor \\\\
Selected & {esc(', '.join(SEL))}; LODO $\\rho$ of the selected set {sel['lodo_rho_selected']:.3f} vs native typed metric alone {sel['lodo_rho_native_only']:.3f} and exact match alone {sel['lodo_rho_em_only']:.3f} \\\\
Grid & {ens['n_grid']:,} weightings (step {ens['grid_step']} $\\times$ 5 $\\lambda$); $J$ top-1 {ens['J_top1']:.3f}, top-100 mean {ens['J_top100']:.3f}, grid median {ens['J_median_grid']:.3f}; range {grid.J.min():.3f}--{grid.J.max():.3f} \\\\
Ensemble weights & {esc(', '.join(f'{k} {v:.2f}' for k, v in ens['mean_weights'].items()))}, $\\lambda$ = {ens['mean_lambda']:.2f}; decay weight spans {ens['weight_spread']['num_decay_2p5'][0]:.2f}--{ens['weight_spread']['num_decay_2p5'][1]:.2f} across the top 100 \\\\
Ensemble terms & $\\rho$ {ens['terms_ensemble_mean']['rho']:.3f}, AUC {ens['terms_ensemble_mean']['auc']:.3f}, JS {ens['terms_ensemble_mean']['js']:.3f}, $\\tau$ native {ens['terms_ensemble_mean']['tau_native']:.3f}, wrong mean {ens['terms_ensemble_mean']['bad']:.3f} \\\\
Baselines & token F1 $\\rho$ {e_base.loc['tok_f1', 'rho']:.3f} / $J$ {e_base.loc['tok_f1', 'J']:.3f}; numeric tolerance $\\rho$ {e_base.loc['num_tol_1', 'rho']:.3f} / $J$ {e_base.loc['num_tol_1', 'J']:.3f}; ensemble $\\rho$ {e_base.loc['ensemble_top100', 'rho']:.3f} / $J$ {e_base.loc['ensemble_top100', 'J']:.3f} \\\\
Sampled designs & all three within {max(ds[k]['regret_max'] for k in ds if isinstance(ds[k], dict)):.4f} of the exhaustive best ({ds['exhaustive_best_J']:.4f}) \\\\
Leave-one-dataset-out & mean held-out $\\rho$ {val['lodo_mean_rho_lodo']:.3f} (re-fitted) vs {val['lodo_mean_rho_full']:.3f} (full); same metric set selected in {100*val['lodo_same_selection_share']:.0f}\\,\\% of folds \\\\
Utility perturbation & mean $L_1$ shift of the ensemble weights {val['severity_l1_shift_mean']:.3f}; selection changed in {100*val['severity_selection_changed_share']:.0f}\\,\\% of draws \\\\
Probes (MAE to utility) & ensemble {val['probe_mae_ensemble']:.3f}, token F1 {val['probe_mae_tok_f1']:.3f}, native {val['probe_mae_native']:.3f}, exact match {val['probe_mae_em']:.3f} \\\\
Leaderboard (ensemble, BT) & first {PRETTY[order[0]]} ($P$(first) {ensr.loc[order[0], 'p_first_bt']:.2f}), then {PRETTY[order[1]]}, {PRETTY[order[2]]}; last {PRETTY[order[-1]]}; Friedman $p$ = {info['friedman']['friedman_p']:.1e}; $W$ = {info['SIG']['ensemble']['kendall_W_datasets']['kendall_W']:.2f} \\\\
Other rules & native metric: {PRETTY[natr.sort_values('rank_bt').index[0]]} first; exact match: {PRETTY[emr.sort_values('rank_bt').index[0]]} first; $\\tau$ ensemble vs native {pd.read_csv(out / 'leaderboards' / 'rule_agreement.csv', index_col=0).loc['ensemble', 'native']:.2f}, vs exact match {pd.read_csv(out / 'leaderboards' / 'rule_agreement.csv', index_col=0).loc['ensemble', 'em_only']:.2f} \\\\
\\bottomrule\\end{{tabularx}}\\end{{table}}

\\subsection{{Three metrics carry the library's information}}
Of 100 metrics, {sel['n_representatives']} are distinct at $|$Spearman$| \\ge 0.95$ and forward selection stops at three: token F1, numeric decay and prefix ratio (Figures~\\ref{{fig:fig_metric_library}}, \\ref{{fig:fig_clusters}}). Their NNLS fit reaches leave-one-dataset-out $\\rho$ {sel['lodo_rho_selected']:.3f} against {sel['lodo_rho_native_only']:.3f} for the native typed metric and {sel['lodo_rho_em_only']:.3f} for exact match.
{figure(pk, 'fig_metric_library', 0.7)}{figure(pk, 'fig_clusters')}{figure(pk, 'fig_family_rho', 0.7)}

\\subsection{{The calibrated ensemble}}
The grid is decay-dominated (Figures~\\ref{{fig:fig_grid_marginals}}, \\ref{{fig:fig_top100_weights}}): the top 100 put {ens['mean_weights']['num_decay_2p5']:.2f} on numeric decay with a hedge penalty of {ens['mean_lambda']:.2f}. The ensemble reaches $\\rho$ {ens['terms_ensemble_mean']['rho']:.3f} and AUC {ens['terms_ensemble_mean']['auc']:.3f} on the anchors, above every single-metric baseline (Table~\\ref{{tab:baselines}}, Figure~\\ref{{fig:fig_baselines}}); the probes show where the gain comes from: near misses, unit variants and partial answers get graded credit instead of zero (Figure~\\ref{{fig:fig_probe_operators}}, Table~\\ref{{tab:probes}}). The sampled designs land within {max(ds[k]['regret_max'] for k in ds if isinstance(ds[k], dict)):.4f} of the exhaustive best (Table~\\ref{{tab:designs_summary}}).
{figure(pk, 'fig_grid_marginals')}{figure(pk, 'fig_top100_weights')}{table(pk, 'baselines')}{figure(pk, 'fig_baselines', 0.7)}{figure(pk, 'fig_probe_operators')}{table(pk, 'designs_summary')}

\\subsection{{Validation}}
Leaving any dataset out re-selects the same three metrics in {100*val['lodo_same_selection_share']:.0f}\\,\\% of folds and changes held-out $\\rho$ by {abs(val['lodo_mean_rho_lodo'] - val['lodo_mean_rho_full']):.3f} on average (Figure~\\ref{{fig:fig_lodo}}); perturbing the utility scale by $\\pm 0.15$ moves the weights by {val['severity_l1_shift_mean']:.3f} in $L_1$ and never changes the selection. The hand-set utility scale is the main assumption, and these checks say the result is not sensitive to it.
{figure(pk, 'fig_lodo')}{table(pk, 'validation')}

\\subsection{{Leaderboard}}
Under the ensemble pooled by Bradley--Terry, {PRETTY[order[0]]} is first, {PRETTY[order[1]]} and {PRETTY[order[2]]} next, {PRETTY[order[-1]]} last; Borda puts {PRETTY[ensr.sort_values('rank_borda').index[0]]} first. The five best single weightings give the same ranking as the ensemble ($\\tau$ = 1.00); the native metric and exact match move the top three. Dataset agreement stays moderate ($W$ = {info['SIG']['ensemble']['kendall_W_datasets']['kendall_W']:.2f}). The ensemble spread per answer (Figure~\\ref{{fig:fig_ensemble_spread}}) is largest on the free-form and list datasets, which is where the weighting matters.
{table(pk, 'leaderboard_headline')}{table(pk, 'ranks_by_rule')}{figure(pk, 'fig_bt_all_rules')}{figure(pk, 'fig_rank_bootstrap')}{figure(pk, 'fig_ensemble_spread')}

\\subsection{{Comparability and diagnostics}}
{table(pk, 'official_split_by_dataset')}{figure(pk, 'fig_diagnostics_scatter', 0.6)}
"""
    pk.write(setup, results)
    return {"ens": ens, "sel": sel, "val": val, "base": base, "order": order, "LB": info["LB"], "SIG": info["SIG"], "ds": ds, "probes": probes}


# ================================================================= comparison
def build_comparison(v3, v4, v5):
    pk = Pkg("comparison", "Summary Report: Four Audits of One Judge Side by Side, v2, v3, v4 and v5 on the Same 31 Datasets and Eleven Models")
    o2 = FINAL / "v2_gridsearch" / "output"
    g2 = pd.read_csv(o2 / "grid_exhaustive.csv"); n2 = json.load(open(o2 / "selection" / "nested.json")); c2 = json.load(open(o2 / "anchors" / "correctness.json")); cc2 = pd.read_csv(o2 / "anchors" / "correctness.csv")
    LB2 = {r: pd.read_csv(o2 / "leaderboards" / r / "leaderboard.csv") for r in ["em_only", "v1_original", "top1", "best_anchor", "pareto_knee"]}
    SIG2 = {r: json.load(open(o2 / "leaderboards" / r / "significance.json")) for r in LB2}
    lodo2 = pd.read_csv(o2 / "selection" / "lodo.csv"); lodo2 = lodo2[lodo2.kind == "dataset"] if "dataset" in set(lodo2.kind) else lodo2
    piv2 = lodo2.pivot(index="held_out", columns="weights_from", values="tau_heldout_mean"); ds2 = json.load(open(o2 / "designs_summary.json"))
    v1_2 = g2[g2.label == "v1_original"].iloc[0]; b2 = g2.sort_values("J", ascending=False).iloc[0]
    models = list(LB2["v1_original"].model); order = LB2["v1_original"].sort_values("rank_bt").model.tolist()
    # ---- headline rules per version
    HEAD = [("v2", "v1 (deployed)", LB2["v1_original"], SIG2["v1_original"]), ("v2", "best J", LB2["top1"], SIG2["top1"]), ("v2", "best rho", LB2["best_anchor"], SIG2["best_anchor"]),
            ("v3", "native + BT mix", v3["LB"]["native"], v3["SIG"]["native"]), ("v4", "best J (num tol)", v4["LB"]["top1"], v4["SIG"]["top1"]), ("v4", "best rho", v4["LB"]["best_anchor"], v4["SIG"]["best_anchor"]),
            ("v5", "ensemble", v5["LB"]["ensemble"], v5["SIG"]["ensemble"]), ("all", "exact match", LB2["em_only"], SIG2["em_only"]), ("all", "native metric", v5["LB"]["native"], v5["SIG"]["native"])]
    R = pd.DataFrame({f"{v}: {lab}": lb.set_index("model").loc[order, "rank_bt"].astype(int) for v, lab, lb, _ in HEAD}); R.index = [PRETTY[m] for m in order]
    fig, ax = plt.subplots(figsize=(8, 4)); ax.imshow(R.values, cmap="viridis_r", vmin=1, vmax=10, aspect="auto"); ax.set_xticks(range(R.shape[1])); ax.set_xticklabels(R.columns, rotation=40, ha="right", fontsize=7); ax.set_yticks(range(R.shape[0])); ax.set_yticklabels(R.index, fontsize=7)
    for i in range(R.shape[0]):
        for j in range(R.shape[1]): ax.text(j, i, R.values[i, j], ha="center", va="center", fontsize=7, color="w" if R.values[i, j] > 5 else "k")
    pk.save(fig, "fig_cmp_ranks", "Bradley--Terry rank of every model under each version's headline rule(s) and the two common baselines.")
    B = pd.DataFrame({f"{v}: {lab}": lb.set_index("model").loc[order, "bt_strength"] for v, lab, lb, _ in HEAD}); B.index = R.index
    fig, ax = plt.subplots(figsize=(8, 3.4)); x = np.arange(B.shape[0]); k = B.shape[1]
    for i, c in enumerate(B.columns): ax.bar(x + (i - (k - 1) / 2) * .8 / k, B[c], .8 / k, label=c)
    ax.set_xticks(x); ax.set_xticklabels(B.index, rotation=30, ha="right", fontsize=7); ax.set_ylabel("Bradley-Terry strength"); ax.legend(frameon=False, fontsize=5, ncol=3); ax.axhline(0, c="k", lw=.5)
    pk.save(fig, "fig_cmp_bt", "Bradley--Terry strengths per model under each version's headline rule(s).")
    PF = pd.DataFrame({f"{v}: {lab}": lb.set_index("model").loc[order, "p_first_bt"] for v, lab, lb, _ in HEAD}); PF.index = R.index
    fig, ax = plt.subplots(figsize=(8, 3.6)); ax.imshow(PF.values, cmap="Blues", vmin=0, vmax=1, aspect="auto"); ax.set_xticks(range(PF.shape[1])); ax.set_xticklabels(PF.columns, rotation=40, ha="right", fontsize=7); ax.set_yticks(range(PF.shape[0])); ax.set_yticklabels(PF.index, fontsize=7)
    for i in range(PF.shape[0]):
        for j in range(PF.shape[1]):
            if PF.values[i, j] > .005: ax.text(j, i, f"{PF.values[i, j]:.2f}", ha="center", va="center", fontsize=6, color="w" if PF.values[i, j] > .5 else "k")
    pk.save(fig, "fig_cmp_p_first", "Bootstrap probability of first place under each headline rule.")
    # anchors across versions
    A = pd.DataFrame([
        {"version": "v2", "rule": "v1 (deployed)", "rho": c2["v1"]["rho"], "auc": c2["v1"]["auc"], "wrong mean": c2["v1"]["wrong_mean"]},
        {"version": "v2", "rule": "best J (decay .70 / recall .30)", "rho": c2["best_J"]["rho"], "auc": c2["best_J"]["auc"], "wrong mean": c2["best_J"]["wrong_mean"]},
        {"version": "v2", "rule": "best rho", "rho": c2["best_rho"]["rho"], "auc": c2["best_rho"]["auc"], "wrong mean": c2["best_rho"]["wrong_mean"]},
        {"version": "v2", "rule": "Pareto knee", "rho": c2["pareto_knee"]["rho"], "auc": c2["pareto_knee"]["auc"], "wrong mean": c2["pareto_knee"]["wrong_mean"]},
        {"version": "v4", "rule": "best J (numeric tolerance)", "rho": v4["cj"]["best_J"]["rho"], "auc": v4["cj"]["best_J"]["auc"], "wrong mean": v4["cj"]["best_J"]["wrong_mean"]},
        {"version": "v4", "rule": "best rho (7 components)", "rho": v4["cj"]["best_rho"]["rho"], "auc": v4["cj"]["best_rho"]["auc"], "wrong mean": v4["cj"]["best_rho"]["wrong_mean"]},
        {"version": "v4", "rule": "Pareto knee", "rho": v4["cj"]["pareto_knee"]["rho"], "auc": v4["cj"]["pareto_knee"]["auc"], "wrong mean": v4["cj"]["pareto_knee"]["wrong_mean"]},
        {"version": "v5", "rule": "ensemble (F1 / decay / prefix, hedge gate)", "rho": v5["ens"]["terms_ensemble_mean"]["rho"], "auc": v5["ens"]["terms_ensemble_mean"]["auc"], "wrong mean": v5["ens"]["terms_ensemble_mean"]["bad"]},
        {"version": "all", "rule": "exact match", "rho": c2["exact_match"]["rho"], "auc": c2["exact_match"]["auc"], "wrong mean": c2["exact_match"]["wrong_mean"]},
        {"version": "all", "rule": "token F1 alone", "rho": v5["base"].set_index("baseline").loc["tok_f1", "rho"], "auc": v5["base"].set_index("baseline").loc["tok_f1", "auc"], "wrong mean": v5["base"].set_index("baseline").loc["tok_f1", "bad"]},
        {"version": "all", "rule": "numeric tolerance alone", "rho": v5["base"].set_index("baseline").loc["num_tol_1", "rho"], "auc": v5["base"].set_index("baseline").loc["num_tol_1", "auc"], "wrong mean": v5["base"].set_index("baseline").loc["num_tol_1", "bad"]},
    ])
    fig, ax = plt.subplots(figsize=(7, 3.2)); x = np.arange(len(A)); cols = {"v2": "C0", "v4": "C1", "v5": "C2", "all": "grey"}
    ax.bar(x, A.rho, color=[cols[v] for v in A.version]); ax.set_xticks(x); ax.set_xticklabels([f"{v}: {r}" for v, r in zip(A.version, A.rule)], rotation=40, ha="right", fontsize=6); ax.set_ylabel("Spearman rho to known utility (31,380 anchors)"); ax.set_ylim(.75, .92)
    for i, r in enumerate(A.itertuples()): ax.text(i, r.rho + .002, f"{r.rho:.3f}", ha="center", fontsize=6)
    pk.save(fig, "fig_cmp_anchor_rho", "Correctness of each version's scoring rule on the same 31,380 anchors (v3 has no per-answer rule).")
    # honesty
    H = pd.DataFrame([
        {"version": "v2", "test": "nested item bootstrap (B = 1,000)", "optimism gap": n2["optimism_gap"], "selected - reference (held out)": n2["selected_vs_v1_out_of_bag"]["mean_diff"] if isinstance(n2.get("selected_vs_v1_out_of_bag"), dict) and "mean_diff" in n2["selected_vs_v1_out_of_bag"] else n2["out_of_bag_J_of_selected_mean"] - n2["out_of_bag_J_v1_mean"], "reference": "v1 weights", "distinct selections": n2["n_distinct_selected"], "plateau": f"{n2['plateau_size']} of 1,771"},
        {"version": "v3", "test": "split-half (20 splits)", "optimism gap": v3["sh"]["optimism_gap"], "selected - reference (held out)": v3["sh"]["selected_minus_pure_bt"]["mean"], "reference": "pure Bradley-Terry", "distinct selections": len(v3["sh"]["selection_counts"]), "plateau": "--"},
        {"version": "v4", "test": "nested item bootstrap (B = 1,000)", "optimism gap": v4["nested"]["optimism_gap"], "selected - reference (held out)": float(v4["d_oob"].mean()), "reference": "v1 rubric", "distinct selections": v4["nested"]["n_distinct_selected"], "plateau": f"{v4['nested']['plateau_size']} of 305"},
        {"version": "v5", "test": "leave-one-dataset-out re-selection + utility perturbation", "optimism gap": v5["val"]["lodo_mean_rho_full"] - v5["val"]["lodo_mean_rho_lodo"], "selected - reference (held out)": v5["val"]["lodo_mean_rho_lodo"] - v5["sel"]["lodo_rho_native_only"], "reference": "native typed metric", "distinct selections": f"same set in {100*v5['val']['lodo_same_selection_share']:.0f}% of folds", "plateau": "top-100 ensemble"},
    ])
    fig, ax = plt.subplots(figsize=(6, 3)); x = np.arange(4); ax.bar(x - .2, H["optimism gap"], .4, label="optimism gap (in-sample - held-out)"); ax.bar(x + .2, H["selected - reference (held out)"], .4, label="selected - reference, held out")
    ax.set_xticks(x); ax.set_xticklabels(H.version); ax.axhline(0, c="k", lw=.5); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_cmp_honesty", "Honest-selection outcome per version: how much the in-sample winner loses when held out, and whether it still beats the version's reference rule.")
    # transfer
    T = pd.DataFrame([{"version": "v2", "re-fitted weights": piv2["lodo_weights"].mean(), "full-data best": piv2["full_best"].mean(), "reference (v1)": piv2["v1"].mean()},
                      {"version": "v4", "re-fitted weights": v4["lodo_piv"][v4["lodo_piv"].columns[0]].mean(), "full-data best": v4["lodo_piv"]["full_best"].mean() if "full_best" in v4["lodo_piv"] else np.nan, "reference (v1)": v4["lodo_piv"][[c for c in v4["lodo_piv"].columns if "v1" in c or "ref" in c][0]].mean()}])
    fig, ax = plt.subplots(figsize=(5, 2.8)); x = np.arange(2)
    for i, c in enumerate(["re-fitted weights", "full-data best", "reference (v1)"]): ax.bar(x + (i - 1) * .27, T[c], .27, label=c)
    ax.set_xticks(x); ax.set_xticklabels(T.version); ax.set_ylabel("mean held-out tau (LODO)"); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_cmp_transfer", "Leave-one-dataset-out transfer for the two versions that search per-answer weights under the agreement objective.")
    # designs
    D = pd.DataFrame([{"version": "v2 (K = 4, exhaustive 1,771)", "design": d, "regret mean": ds2["regret_mean"][d], "regret max": ds2["regret_max"][d]} for d in ds2["regret_mean"]] +
                     [{"version": "v4 (K = 9, no exhaustive)", "design": d, "regret mean": v4["ds"][d]["regret_mean"], "regret max": v4["ds"][d]["regret_max"]} for d in v4["ds"]] +
                     [{"version": "v5 (K = 3 + lambda, exhaustive 6,630)", "design": d, "regret mean": v5["ds"][d]["regret_mean"], "regret max": v5["ds"][d]["regret_max"]} for d in v5["ds"] if isinstance(v5["ds"][d], dict)])
    fig, ax = plt.subplots(figsize=(6, 3)); piv = D.pivot(index="version", columns="design", values="regret max"); x = np.arange(len(piv))
    for i, c in enumerate(piv.columns): ax.bar(x + (i - 1) * .27, piv[c], .27, label=c)
    ax.set_xticks(x); ax.set_xticklabels(piv.index, fontsize=7); ax.set_ylabel("max regret vs best (20 seeds)"); ax.legend(frameon=False, fontsize=7)
    pk.save(fig, "fig_cmp_designs", "Sampled-design regret per version: with few weights every design finds the optimum; with nine the lattice design is marginally better.")
    # W and significant pairs
    S = pd.DataFrame([{"version": v, "rule": lab, "Kendall W": sg["kendall_W_datasets"]["kendall_W"], "Friedman p": sg["friedman"]["friedman_p"], "Holm-significant pairs": sum(p["wilcoxon_significant_05"] for p in sg["friedman"]["pairwise"]), "first (BT)": PRETTY[lb.sort_values("rank_bt").model.iloc[0]], "first (Borda)": PRETTY[lb.sort_values("rank_borda").model.iloc[0]], "last": PRETTY[lb.sort_values("rank_bt").model.iloc[-1]]} for v, lab, lb, sg in HEAD])
    # tables
    pk.to_tex(R.reset_index().rename(columns={"index": "model"}), "cmp_ranks", "Bradley--Terry rank per model under each headline rule.")
    pk.to_tex(A.round(3), "cmp_anchors", "Anchor correctness of each version's rule on the same 31,380 synthetic answers.")
    pk.to_tex(H.round(3), "cmp_honesty", "Honest-selection outcome per version.")
    pk.to_tex(T.round(3), "cmp_transfer", "Leave-one-dataset-out transfer (mean held-out $\\tau$).")
    pk.to_tex(D.round(4), "cmp_designs", "Sampled-design regret per version.", fmt="%.4f")
    pk.to_tex(S.round(3), "cmp_significance", "Leaderboard significance per headline rule.")
    design_tbl = pd.DataFrame([
        {"": "per-answer rule", "v2": "4 metrics (F1, decay, P, R), weights searched", "v3": "dataset's own metric", "v4": "9 metrics, weights searched", "v5": "3 of 100 metrics, weights searched, top-100 ensemble, hedge gate"},
        {"": "what is searched", "v2": "4 weights, exhaustive (1,771)", "v3": "mix of 8 aggregation views (455 candidates)", "v4": "9 weights, 3 sampled designs (305)", "v5": "3 weights + lambda, exhaustive (6,630)"},
        {"": "objective", "v2": "datasets agree (tau to Borda pool)", "v3": "stability + transitivity + consensus", "v4": "datasets agree (tau to Borda pool)", "v5": "anchor rho, AUC, JS consistency, native tau, wrong -> 0"},
        {"": "checked against", "v2": "the ranked models (+ anchors beside)", "v3": "bootstrap resamples", "v4": "the ranked models (+ anchors beside)", "v5": "31,380 synthetic answers of known quality"},
        {"": "honesty test", "v2": "nested item bootstrap, plateau, LODO/LOFO", "v3": "split-half vs pure BT / uniform", "v4": "nested item bootstrap, plateau, LODO/LOFO", "v5": "LODO re-selection, utility perturbation, probes"},
        {"": "headline leaderboard rule", "v2": "v1 weights (deployed)", "v3": "native metric, Bradley-Terry", "v4": "v1 rubric (comparability)", "v5": "calibrated ensemble"},
        {"": "main risk", "v2": "circular: agreement is not correctness", "v3": "views differ in kind; no per-answer rule", "v4": "circular; 9-D space not enumerable", "v5": "hand-set utility scale; synthetic anchors"},
    ])
    pk.to_tex(design_tbl, "cmp_design", "What each version does.")
    pk.copy_data(PAPER / "v2" / "data" / "leaderboards", extra=[])
    for v in ["v3", "v4", "v5"]:
        src = PAPER / v / "data" / "leaderboards"
        if src.exists():
            for p in src.rglob("*"):
                if p.is_file(): dst = pk.dat / v / p.relative_to(src); dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy(p, dst)
    A.to_csv(pk.dat / "cmp_anchors.csv", index=False); R.to_csv(pk.dat / "cmp_ranks.csv"); H.to_csv(pk.dat / "cmp_honesty.csv", index=False); S.to_csv(pk.dat / "cmp_significance.csv", index=False)
    # verdict numbers
    best_rho = A.sort_values("rho", ascending=False).iloc[0]
    v2_sel = n2["out_of_bag_J_of_selected_mean"] - n2["out_of_bag_J_v1_mean"]
    intro = ""
    setup = r"""\section{Setup}
Four audit pipelines were run on one cache of answers: 31 datasets (11 entity matching, 6 schema matching, 11 table QA, 3 finance), 100 stratified items each from the official splits (90 and 93 for two small sets), eleven models, 3,083 answers per model, USD 161. Each version asks a different question of the deployed judge, whose rule is $R = 0.35\,\mathrm{F1} + 0.35\,e^{-2.5\,|\text{rel.\ err}|} + 0.15\,\mathrm{P} + 0.15\,\mathrm{R}$ (``v1''):
\begin{itemize}
\item \textbf{v2}: are v1's four weights the right ones? Every step-0.05 weighting of the four ingredients (1,771) is scored by how consistently the 31 datasets rank the models (mean Kendall $\tau$ to the Borda pool), with correctness on 31,380 synthetic answers of known quality checked beside it, nested-bootstrap selection, a plateau, leave-one-out transfer and sampled designs.
\item \textbf{v3}: given per-dataset scores, how should they be pooled? Eight aggregation views from the literature (mean, baseline-normalised mean, mean $z$, win rate, Borda, Kemeny, Bradley--Terry, Rasch) and all 255 equal-weight subsets plus 200 sampled mixes, scored by stability under item resampling, transitivity and agreement with the views' consensus; split-half honesty; parameters with standard errors.
\item \textbf{v4}: does a richer per-answer rule help? Nine lexical components, three sampled designs of 100 weightings plus baselines, the same agreement objective and honesty battery as v2.
\item \textbf{v5}: what does the external quality signal say? A 100-metric library reduced to three by anchor-driven selection, an exhaustive grid over their weights and a hedge penalty scored by correctness on the anchors, a top-100 ensemble, leave-one-dataset-out re-selection and utility perturbation.
\end{itemize}
All four share the pools, the answer cache, the scoring primitives, the coverage rule and the leaderboard machinery (Bradley--Terry headline with Borda, Kemeny, Copeland and mean-$z$ checks; 1,000 item bootstraps; Friedman, Nemenyi and Holm across datasets; per-item paired tests; Kendall's $W$; post-stratified official-split estimates). Table~\ref{tab:cmp_design} summarises the design differences. Each version's full Setup, Results, figures, tables and data are in the sibling packages \texttt{v2/}, \texttt{v3/}, \texttt{v4/}, \texttt{v5/}.
\input{tables/cmp_design.tex}
"""
    results = f"""\\section{{Results side by side}}

\\subsection{{Which rule scores answers best}}
On the one quantity all per-answer rules can be compared on, correctness against the same 31,380 anchors, the order is: v5 ensemble $\\rho$ {A.set_index('rule').loc['ensemble (F1 / decay / prefix, hedge gate)', 'rho']:.3f} $>$ v4 best-$\\rho$ {v4['cj']['best_rho']['rho']:.3f} $\\approx$ v2 best-$\\rho$ {c2['best_rho']['rho']:.3f} $>$ v1 as deployed {c2['v1']['rho']:.3f} $>$ token F1 alone {A.set_index('rule').loc['token F1 alone', 'rho']:.3f} $>$ exact match {c2['exact_match']['rho']:.3f} $>$ numeric tolerance alone (v4's best by agreement) {v4['cj']['best_J']['rho']:.3f} (Figure~\\ref{{fig:fig_cmp_anchor_rho}}, Table~\\ref{{tab:cmp_anchors}}). Every rule separates correct from wrong answers with AUC $\\ge$ 0.99; the differences are in graded credit for near misses, unit variants and partial answers. The deployed v1 is within {best_rho.rho - c2['v1']['rho']:.3f} of the best rule found by any version.
{figure(pk, 'fig_cmp_anchor_rho')}{table(pk, 'cmp_anchors')}

\\subsection{{Which search finds something real}}
Under the agreement objective (v2, v4) the in-sample winner loses about 0.05 when held out and ends within noise of v1 ({v2_sel:+.3f} for v2, {float(v4['d_oob'].mean()):+.3f} for v4); the plateau covers almost every candidate in both. v3's split-half test gives the same picture for the choice of pooling rule: the selected mix beats pure Bradley--Terry by {v3['sh']['selected_minus_pure_bt']['mean']:+.3f} with an interval through zero, and the uniform mix does as well. v5 is the only version whose selection survives its honesty test: the same three metrics are chosen in {100*v5['val']['lodo_same_selection_share']:.0f}\\,\\% of leave-one-dataset-out folds, held-out $\\rho$ moves by {abs(v5['val']['lodo_mean_rho_lodo'] - v5['val']['lodo_mean_rho_full']):.3f}, and the result is {v5['val']['lodo_mean_rho_lodo'] - v5['sel']['lodo_rho_native_only']:+.3f} above the native typed metric on the same folds (Figure~\\ref{{fig:fig_cmp_honesty}}, Table~\\ref{{tab:cmp_honesty}}). The reason is the objective, not the search: agreement among the ranked models is flat over the weight space, correctness against an external signal is not.
{figure(pk, 'fig_cmp_honesty', 0.7)}{table(pk, 'cmp_honesty')}

\\subsection{{Transfer and designs}}
Re-fitted weights predict a held-out dataset no better than v1 in v2 or v4 (Figure~\\ref{{fig:fig_cmp_transfer}}). Sampled designs find the optimum whenever it exists (regret $\\le$ {ds2['regret_max'][max(ds2['regret_max'], key=ds2['regret_max'].get)]:.3f} in v2, $\\le$ {max(v5['ds'][k]['regret_max'] for k in v5['ds'] if isinstance(v5['ds'][k], dict)):.4f} in v5); in v4's nine-dimensional space the uniform lattice has the best coverage and the best found value, and the three designs agree to 0.01 (Figure~\\ref{{fig:fig_cmp_designs}}).
{figure(pk, 'fig_cmp_transfer', 0.6)}{figure(pk, 'fig_cmp_designs', 0.7)}

\\subsection{{The leaderboard every version produces}}
The same answers give the same ends under every rule and every version: {PRETTY[order[-1]]} last, gpt-oss-120b ninth, and {{Claude Opus 5, GPT-5.5, Gemini 3.8 Flash}} as the top three, with Friedman $p < 0.001$ and Holm-significant separation of the top group from the bottom two (Table~\\ref{{tab:cmp_significance}}). What changes is the order inside the top three (Figure~\\ref{{fig:fig_cmp_ranks}}): exact match and v4's numeric-tolerance rule put Opus first; the graded rules (v1, v2 best, v4 best-$\\rho$, v5 ensemble) put Gemini 3.8 Flash first by Bradley--Terry and GPT-5.5 or Opus first by Borda; v3's native-metric pooling puts Gemini Flash first by Bradley--Terry and GPT-5.5 by Borda. Kendall's $W$ among datasets is 0.25--0.28 everywhere: the datasets disagree about the middle of the table regardless of rule.
{figure(pk, 'fig_cmp_ranks')}{table(pk, 'cmp_significance')}{figure(pk, 'fig_cmp_bt')}{figure(pk, 'fig_cmp_p_first')}

\\section{{What is better, per version}}
\\begin{{description}}[style=unboxed,leftmargin=0pt]
\\item[] \\textbf{{v2 (exhaustive grid over v1's weights).}} Best at answering the question it was built for: it proves, not samples, that no weighting of v1's ingredients is distinguishable from v1 on this suite (plateau 1,765 of 1,771; out-of-bag difference $-0.008$ with an interval through zero). It is the right headline for ``the deployed weights are fine''. It cannot say the weights are \\emph{{right}}, because agreement is not correctness.
\\item[] \\textbf{{v3 (aggregation views).}} Best at the pooling question and the only version that reports fitted parameters with standard errors (Bradley--Terry, Rasch, Kemeny cost). Its finding is that mixing views buys little over the uniform mix and that pure Bradley--Terry is the least reproducible single rule on 31 datasets $\\times$ 10 models. It has no per-answer rule, so it cannot audit the judge's formula.
\\item[] \\textbf{{v4 (nine components).}} Best as the negative control: adding five components and sampling 305 candidates in a 3-million-point space finds that a single typed metric (numeric tolerance) maximises agreement, and that this metric is the worst on correctness. It shows most clearly that the agreement objective rewards coarseness. Its search cannot be exhaustive, so its optimum is only ``best found''.
\\item[] \\textbf{{v5 (anchor-calibrated ensemble).}} Best scoring rule by the external signal ($\\rho$ {v5['ens']['terms_ensemble_mean']['rho']:.3f}, AUC {v5['ens']['terms_ensemble_mean']['auc']:.3f}) and the only selection that survives leave-one-dataset-out unchanged. It is the version to deploy if the goal is to score answers well; its weakness is that the signal is synthetic (a hand-set utility scale) until human labels exist, and its gain over v1 ({v5['ens']['terms_ensemble_mean']['rho'] - c2['v1']['rho']:+.3f} in $\\rho$) is real but small.
\\item[] \\textbf{{Taken together.}} v2 and v4 establish that the weight question has no answer on this suite; v3 establishes that the pooling question has no strong answer either; v5 establishes that the correctness question does, and that the deployed rule is close to its answer. The paper's claim is therefore: keep v1 (or the v5 ensemble), report the leaderboard under several rules with the ends and the significant pairs, and spend the next effort on human labels rather than on more weight search.
\\end{{description}}
"""
    pk.write(setup, results)


if __name__ == "__main__":
    r3 = build_v3(); r4 = build_v4(); r5 = build_v5(); build_comparison(r3, r4, r5)
