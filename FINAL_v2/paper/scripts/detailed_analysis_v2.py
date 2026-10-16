"""Detailed analysis of every v2 output file -> paper/v2/DETAILED_ANALYSIS.md (figures referenced from paper/v2/figures/).
Run from FINAL_v2:  uv run python paper/scripts/detailed_analysis_v2.py
"""
from __future__ import annotations
import json, glob, os
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import kendalltau, spearmanr

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "v2_gridsearch" / "output"; PRED = ROOT / "data" / "predictions"; POOL = ROOT / "data" / "pool"
DOC = ROOT / "paper" / "v2" / "DETAILED_ANALYSIS.md"; FIG = "figures"
PRETTY = {"gemini-3.1-pro": "Gemini 3.1 Pro", "claude-opus-5": "Claude Opus 5", "claude-sonnet-5": "Claude Sonnet 5", "gpt-5.5": "GPT-5.5", "gpt-5.4-mini": "GPT-5.4-mini", "gemini-3.8-flash": "Gemini 3.8 Flash",
          "grok-4": "Grok 4", "deepseek-chat": "DeepSeek-chat", "deepseek-r1": "DeepSeek-R1", "gpt-oss-120b": "gpt-oss-120b", "llama-3.3-70b": "Llama 3.3 70B"}
FAM = {"EM": "entity matching", "SM": "schema matching", "TQA": "table QA", "FIN": "finance"}
RULES = ["em_only", "v1_original", "top1", "top2", "top3", "top4", "top5", "best_anchor", "pareto_knee"]
RP = {"em_only": "exact match", "v1_original": "v1 (deployed)", "top1": "top1 (best J)", "top2": "top2", "top3": "top3", "top4": "top4", "top5": "top5", "best_anchor": "best-rho", "pareto_knee": "Pareto knee"}
W = ["w_f1", "w_decay", "w_precision", "w_recall"]; WN = ["F1", "decay", "precision", "recall"]
L = []


def h(t, n=2): L.append("\n" + "#" * n + " " + t + "\n")
def p(t): L.append(t + "\n")
def fig(name, cap): L.append(f"\n![{cap}]({FIG}/{name}.png)\n\n*{cap}*\n")


def md(df, fmt="{:.3f}", index=False, maxrows=None):
    df = df.copy()
    if index: df = df.reset_index()
    if maxrows: df = df.head(maxrows)
    cols = list(df.columns)
    def c(x):
        if isinstance(x, (float, np.floating)): return "–" if pd.isna(x) else fmt.format(x)
        if isinstance(x, (bool, np.bool_)): return "yes" if x else "no"
        return str(x)
    L.append("| " + " | ".join(str(k) for k in cols) + " |\n|" + "---|" * len(cols) + "\n" + "".join("| " + " | ".join(c(v) for v in row) + " |\n" for row in df.itertuples(index=False)) + "\n")


def wstr(r): return f"F1 {r['w_f1']:.2f} / decay {r['w_decay']:.2f} / P {r['w_precision']:.2f} / R {r['w_recall']:.2f}"


# ------------------------------------------------------------------ load
grid = pd.read_csv(OUT / "grid_exhaustive.csv"); comp = pd.read_csv(OUT / "components_v1.csv"); anch = pd.read_csv(OUT / "anchors" / "anchor_components.csv")
corr = pd.read_csv(OUT / "anchors" / "correctness.csv"); cj = json.load(open(OUT / "anchors" / "correctness.json")); best = json.load(open(OUT / "best.json"))
nested = json.load(open(OUT / "selection" / "nested.json")); draws = np.load(OUT / "selection" / "nested_draws.npz"); plateau = pd.read_csv(OUT / "selection" / "plateau.csv")
lodo = pd.read_csv(OUT / "selection" / "lodo.csv"); lofo = pd.read_csv(OUT / "selection" / "lofo.csv"); pfam = json.load(open(OUT / "selection" / "per_family.json")); sens = json.load(open(OUT / "selection" / "sensitivity.json"))
designs = pd.read_csv(OUT / "designs.csv"); ds = json.load(open(OUT / "designs_summary.json")); diag = pd.read_csv(OUT / "diagnostics" / "dataset_diagnostics.csv"); dj = json.load(open(OUT / "diagnostics" / "diagnostics.json"))
ra = pd.read_csv(OUT / "leaderboards" / "rule_agreement.csv", index_col=0); cov = json.load(open(OUT / "coverage.json")); man = json.load(open(OUT / "run_manifest.json"))
LB = {r: pd.read_csv(OUT / "leaderboards" / r / "leaderboard.csv") for r in RULES}; PAR = {r: json.load(open(OUT / "leaderboards" / r / "params.json")) for r in RULES}
SIG = {r: json.load(open(OUT / "leaderboards" / r / "significance.json")) for r in RULES}; BOOT = {r: np.load(OUT / "leaderboards" / r / "bootstrap.npz") for r in RULES}
PDM = {r: pd.read_csv(OUT / "leaderboards" / r / "per_dataset_mean.csv", index_col=0) for r in RULES}; PDS = pd.read_csv(OUT / "leaderboards" / "v1_original" / "per_dataset_se.csv", index_col=0)
OFF = pd.read_csv(OUT / "leaderboards" / "v1_original" / "official_split_estimates.csv"); PW = pd.read_csv(OUT / "leaderboards" / "v1_original" / "pairwise_item_tests.csv")
models = PAR["v1_original"]["models"]; datasets = PAR["v1_original"]["datasets"]; fam_of = dict(zip(diag.dataset, diag.family))
order = LB["v1_original"].sort_values("rank_bt").model.tolist()
v1 = grid[grid.label == "v1_original"].iloc[0]; b = grid.sort_values("J", ascending=False).iloc[0]
comp["v1"] = .35 * comp.f1 + .35 * comp.decay + .15 * comp.precision + .15 * comp.recall
anch["v1"] = .35 * anch.f1 + .35 * anch.decay + .15 * anch.precision + .15 * anch.recall

# prediction cache
rows = []
for f in sorted(PRED.glob("*.jsonl")):
    m = f.stem
    if m not in models: continue
    for l in open(f):
        r = json.loads(l)
        if r.get("error"): continue
        rows.append({"model": m, "dataset": r["dataset"], "out_tokens": r.get("out_tokens", 0), "in_tokens": r.get("in_tokens", 0), "latency": r.get("latency_s", np.nan), "cost": r.get("cost_usd", 0.0),
                     "attempt": r.get("attempt") or 1, "cut": ("length" in str(r.get("finish")).lower() or "max_tokens" in str(r.get("finish")).lower()), "decoding": r.get("decoding", ""), "has_final": bool(__import__("re").search(r"final answer\s*:", r.get("prediction") or "", __import__("re").I))})
run = pd.DataFrame(rows); run = run[run.dataset.isin(datasets)].copy(); run["cut_final"] = run.cut & (run.attempt == 4) & ~run.has_final; run["cut_700_unreasked"] = run.cut & (run.attempt < 4) & ~run.has_final

# ================================================================== 0. header
L.append(f"# v2 detailed analysis: every output, read end to end\n\nGenerated {pd.Timestamp.now():%Y-%m-%d} from `v2_gridsearch/output/` (run {man['generated']}, commit {man['git_commit']}) and the prediction cache. Figures are in `{FIG}/`; every table is computed directly from the files named in each section.\n")
h("Contents")
p("1. Run facts (cache, coverage, cost, truncation)\n2. The answers as scored (component distributions, hedging, answer types)\n3. Model × dataset scores under v1\n4. The exhaustive grid\n5. Honest selection and the plateau\n6. Transfer: leave-one-dataset-out, leave-one-family-out, families\n7. Sampled designs\n8. Correctness on known-quality anchors\n9. Leaderboards under every rule\n10. Significance\n11. Official-split comparability\n12. Dataset diagnostics\n13. What the data support, in one page")

# ================================================================== 1. run facts
h("1. Run facts")
p(f"Files: `data/predictions/*.jsonl`, `coverage.json`, `run_manifest.json`.")
n_items = sum(c["items_kept"] for d, c in cov.items() if not d.startswith("_"))
p(f"* {len(models)} models × {len(datasets)} datasets; {n_items:,} items kept per model (every model answered every kept item); models left out of the study: {cov.get('_models_left_out') or 'none'}.")
facts = run.groupby("model").agg(answers=("dataset", "size"), cost_usd=("cost", "sum"), in_tokens=("in_tokens", "mean"), out_tokens=("out_tokens", "mean"), out_p90=("out_tokens", lambda s: s.quantile(.9)), latency_med=("latency", "median"), latency_p90=("latency", lambda s: s.quantile(.9)),
                                 reask_2500=("attempt", lambda a: (a == 2).sum()), reask_8000=("attempt", lambda a: (a == 3).sum()), reask_16000=("attempt", lambda a: (a == 4).sum()), cut_at_16000=("cut_final", "sum"), cut_below_16000_pending=("cut_700_unreasked", "sum"), no_final_line=("has_final", lambda s: (~s).sum()), decoding=("decoding", lambda s: s.mode().iloc[0] if len(s.mode()) else "")).loc[order]
facts.index = [PRETTY[m] for m in facts.index]
md(facts.reset_index().rename(columns={"index": "model"}), fmt="{:.2f}")
p(f"* Total cost USD {run.cost.sum():.0f} on the 31 study datasets; the most expensive model is {facts.cost_usd.idxmax()} (USD {facts.cost_usd.max():.0f}, {100*facts.cost_usd.max()/run.cost.sum():.0f} % of the bill); the cheapest is {facts.cost_usd.idxmin()} (USD {facts.cost_usd.min():.1f}).")
p(f"* Output length varies {facts.out_tokens.max()/facts.out_tokens.min():.0f}× between models: {facts.out_tokens.idxmax()} averages {facts.out_tokens.max():.0f} output tokens, {facts.out_tokens.idxmin()} {facts.out_tokens.min():.0f}. Reasoning models carry their thinking in the output budget, which is why they dominate the re-asks.")
p(f"* Re-asks: {int(facts.reask_2500.sum())} answers were re-asked at 2,500 tokens, {int(facts.reask_8000.sum())} at 8,000 and {int(facts.reask_16000.sum())} at 16,000; {int(facts.cut_at_16000.sum())} were still cut off at 16,000 ({facts.cut_at_16000.idxmax()} accounts for {int(facts.cut_at_16000.max())}) and {int(facts.cut_below_16000_pending.sum())} unfinished answers below 16,000 are awaiting their next stage ({facts.cut_below_16000_pending.idxmax()} accounts for {int(facts.cut_below_16000_pending.max())}: the 16,000-token re-ask failed on provider balance and their 8,000-token replies were kept). {int(facts.no_final_line.sum())} replies carry no literal `FINAL ANSWER` line; those are scored from a boxed expression or the last short line, which is why the extraction hand-check is still open.")
tok = run.groupby("dataset").agg(out_tokens=("out_tokens", "mean"), in_tokens=("in_tokens", "mean"), cut=("cut", "sum"), reasked=("attempt", lambda a: (a > 1).sum())).sort_values("out_tokens", ascending=False)
p("Per dataset, the longest replies and most re-asks come from the document and SQL tasks:")
md(tok.head(10).reset_index(), fmt="{:.0f}")
fig("fig_run_facts", "Cost, output length, latency and residual cut-offs per model.")
fig("fig_truncation", "Re-asks per model under the 700 → 2,500 → 8,000 protocol.")
fig("fig_tokens_heatmap", "Mean output tokens per model and dataset.")

# ================================================================== 2. answers as scored
h("2. The answers as scored")
p("File: `components_v1.csv` (one row per model × item: native metric, exact match, numeric tolerance, F1, decay, precision, recall, hedge flag).")
at = comp.groupby("answer_type").agg(items=("uid", "nunique"), answers=("uid", "size"), em=("em", "mean"), f1=("f1", "mean"), decay=("decay", "mean"), precision=("precision", "mean"), recall=("recall", "mean"), v1=("v1", "mean"), hedged=("hedge_free", lambda s: 1 - s.mean()))
p("Mean of every ingredient by answer type (over all 30,830 scored answers):")
md(at.reset_index())
p("Reading: boolean and text golds are scored almost identically by every ingredient (F1 ≈ exact match), so the weights only matter on numeric and free-form golds. Numeric decay sits above exact match on numeric golds because near misses get partial credit; on free-form golds (FeTaQA) exact match and decay are ~0 while token overlap is ~0.6, so the composite is capped by the 0.65 of weight on F1 / precision / recall: any weight moved onto decay lowers every free-form score uniformly.")
fm = comp.groupby("family").agg(answers=("uid", "size"), em=("em", "mean"), f1=("f1", "mean"), decay=("decay", "mean"), precision=("precision", "mean"), recall=("recall", "mean"), v1=("v1", "mean"), native=("native_value", "mean"), hedged=("hedge_free", lambda s: 1 - s.mean()))
p("By family:")
md(fm.reset_index())
C = comp[["em", "num_tol", "f1", "decay", "precision", "recall", "native_value"]].corr(method="spearman")
p("Spearman correlation between ingredients across all answers:")
md(C.round(3), index=True)
p(f"F1 and recall correlate {C.loc['f1','recall']:.2f}, F1 and precision {C.loc['f1','precision']:.2f}, decay and exact match {C.loc['decay','em']:.2f}: the four ingredients are far from independent, which is the first reason the weights barely matter.")
ident = (comp.f1 == comp.em).mean(); dec = (comp.decay == comp.em).mean(); allsame = ((comp.f1 == comp.em) & (comp.decay == comp.em) & (comp.precision == comp.em) & (comp.recall == comp.em)).mean()
p(f"* In {100*allsame:.1f} % of answers all four ingredients equal exact match (the answer is either exactly right or shares no token with the gold); any weighting gives the same score there. F1 equals exact match in {100*ident:.1f} % of answers and decay equals it in {100*dec:.1f} %.")
hz = comp.groupby("model").hedge_free.apply(lambda s: 1 - s.mean()).loc[order]; hz.index = [PRETTY[m] for m in hz.index]
p("Hedge rate per model (answers flagged as offering several candidates):")
md(hz.round(3).to_frame("hedge rate").reset_index().rename(columns={"index": "model"}))
nat = comp.groupby(["dataset"]).agg(native_metric=("native_metric", lambda s: s.mode().iloc[0]), answer_type=("answer_type", lambda s: s.mode().iloc[0]), native=("native_value", "mean"), v1=("v1", "mean"), em=("em", "mean"), gap=("v1", "mean"))
nat["v1 − native"] = nat.v1 - nat.native; nat = nat.drop(columns="gap").sort_values("v1 − native")
p("Per dataset, the composite against the dataset's own metric (the largest gaps are where the weights can matter):")
md(nat.reset_index())
fig("fig_component_distributions", "Distribution of each ingredient by answer type.")
fig("fig_native_vs_composite", "Native metric vs v1 composite per answer, by family.")

# ================================================================== 3. model x dataset
h("3. Model × dataset scores under v1")
p("Files: `leaderboards/v1_original/per_dataset_mean.csv`, `per_dataset_se.csv`.")
pdm = PDM["v1_original"].loc[order, datasets]; se = PDS.loc[order, datasets]
tbl = pdm.copy(); tbl.index = [PRETTY[m] for m in tbl.index]
md(tbl.T.reset_index().rename(columns={"index": "dataset"}), fmt="{:.2f}")
p("Standard error of each cell is the item-level SE of the mean (100 items):")
md(se.T.describe().loc[["mean", "min", "max"]].T.describe().loc[["mean", "min", "max"]].reset_index().rename(columns={"index": "SE across cells"}), fmt="{:.3f}")
famm = comp.groupby(["model", "family"]).v1.mean().unstack().loc[order]; famm.index = [PRETTY[m] for m in famm.index]
p("Per-family mean composite per model:")
md(famm.reset_index().rename(columns={"index": "model"}))
rk = pdm.rank(ascending=False, axis=0)
summ = pd.DataFrame({"model": [PRETTY[m] for m in order], "mean score": pdm.mean(1).values, "mean rank": rk.mean(1).values, "datasets ranked 1st": (rk == 1).sum(1).values, "datasets in top 3": (rk <= 3).sum(1).values, "datasets ranked last": (rk == 10).sum(1).values,
                     "best dataset": [pdm.loc[m].idxmax() for m in order], "worst dataset": [pdm.loc[m].idxmin() for m in order]})
p("How each model's rank moves across datasets:")
md(summ)
p(f"No model is first on more than {int((rk == 1).sum(1).max())} of 31 datasets, and even {PRETTY[order[-1]]} is not last everywhere ({int((rk == len(order)).sum(1).loc[order[-1]])} datasets). The leaderboard is an average over disagreeing datasets, which is what Kendall's W ≈ 0.27 says in section 10.")
spread = (pdm.max() - pdm.min()).sort_values(ascending=False)
p("Datasets that separate the models most and least (max − min of the ten model means):")
md(pd.concat([spread.head(6).rename("spread").reset_index().rename(columns={"index": "most separating"}), spread.tail(6).rename("spread").reset_index().rename(columns={"index": "least separating"})], axis=1))
fig("fig_model_dataset_heatmap", "Mean v1 score per model and dataset.")
fig("fig_model_dataset_ranks", "Rank per model within each dataset.")
fig("fig_family_scores", "Per-family means.")

# ================================================================== 4. grid
h("4. The exhaustive grid")
p("File: `grid_exhaustive.csv` (1,771 rows: the four weights, J under Borda / Kemeny / Copeland / Bradley–Terry pooling, τ to native metrics, min agreement, dispersion, per-dataset τ).")
q = grid.J.quantile([0, .01, .05, .1, .25, .5, .75, .9, .95, .99, 1]).rename("J")
md(q.to_frame().T.reset_index(drop=True), fmt="{:.4f}")
p(f"* Range {grid.J.min():.4f}–{grid.J.max():.4f}; interquartile range {grid.J.quantile(.75)-grid.J.quantile(.25):.4f}; standard deviation {grid.J.std():.4f}. The bootstrap SD of J for a single weighting (section 5) is about {plateau.J_boot_sd.mean():.3f}, i.e. larger than the spread of the whole grid.")
spec = pd.concat([grid[grid.label.notna()], grid.sort_values("J", ascending=False).head(10)]).drop_duplicates(subset=W)
spec = spec.assign(weights=[wstr(r) for _, r in spec.iterrows()])[["rank", "label", "weights", "J", "J_kemeny", "J_copeland", "J_bt", "tau_native", "min_agree", "dispersion"]].sort_values("rank")
p("Named points and the ten best:")
md(spec.fillna(""), fmt="{:.3f}")
p("Rank of v1 under each pooling rule (of 1,771):")
rk_rules = {c: int((grid[c] > v1[c]).sum() + 1) for c in ["J", "J_kemeny", "J_copeland", "J_bt"]}
md(pd.DataFrame([{"pooling": k, "v1 J": v1[c], "best J": grid[c].max(), "v1 rank": rk_rules[c], "best weighting": wstr(grid.loc[grid[c].idxmax()])} for k, c in [("Borda", "J"), ("Kemeny", "J_kemeny"), ("Copeland", "J_copeland"), ("Bradley–Terry", "J_bt")]]))
p("Marginal effect of each weight (mean and max J at each weight level, step 0.05):")
for w, n in zip(W, WN):
    g = grid.groupby(w).J.agg(["mean", "max", "count"]).reset_index(); g[w] = g[w].round(2)
    L.append(f"**{n}**: mean J over weightings with this weight fixed is lowest at weight {g.loc[g['mean'].idxmin(), w]:.2f} ({g['mean'].min():.4f}) and highest at weight {g.loc[g['mean'].idxmax(), w]:.2f} ({g['mean'].max():.4f}); at weight 0 it is {g['mean'].iloc[0]:.4f} and at weight 1 it is {g['mean'].iloc[-1]:.4f}; whole-range swing {(g['mean'].max()-g['mean'].min()):.4f}.\n\n")
rs = {n: spearmanr(grid[w], grid.J).correlation for w, n in zip(W, WN)}
p(f"Spearman correlation of J with each weight across the grid: " + ", ".join(f"{k} {v:+.2f}" for k, v in rs.items()) + ". Recall and decay help a little, precision and F1 hurt a little; none of the effects exceeds 0.02 of J.")
p(f"τ to native metrics: v1 {v1.tau_native:.3f}, best {b.tau_native:.3f}, grid range {grid.tau_native.min():.3f}–{grid.tau_native.max():.3f}; correlation between J and τ-native across the grid {spearmanr(grid.tau_native, grid.J).correlation:+.2f}.")
tau_cols = [c for c in grid.columns if c.startswith("tau_") and c != "tau_native"]
pt = pd.DataFrame({"dataset": [c[4:] for c in tau_cols], "family": [fam_of[c[4:]] for c in tau_cols], "τ under v1": [v1[c] for c in tau_cols], "τ under best": [b[c] for c in tau_cols], "max τ over grid": [grid[c].max() for c in tau_cols], "min τ over grid": [grid[c].min() for c in tau_cols]}).sort_values("τ under v1")
p("Per-dataset agreement with the pooled ranking (the objective is the mean of the first τ column):")
md(pt)
p(f"{len(pt[pt['τ under v1'] < 0])} datasets have negative τ under v1 ({', '.join(pt[pt['τ under v1'] < 0].dataset)}): their model ranking runs against the consensus whatever the weights, and no weighting flips them (their maximum over the grid is {pt[pt['τ under v1'] < 0]['max τ over grid'].max():+.2f}). Alaska Camera is stably against the consensus (self-stability {diag.set_index('dataset').loc['alaska_camera','ranking_self_stability_tau']:.2f}: Claude Opus 5 scores {pdm.loc['claude-opus-5','alaska_camera']:.2f} there while every other model is above {pdm['alaska_camera'].drop('claude-opus-5').min():.2f}), while HiTab and Alaska schema are among the least self-stable sets ({diag.set_index('dataset').loc['hitab','ranking_self_stability_tau']:.2f} and {diag.set_index('dataset').loc['alaska_schema','ranking_self_stability_tau']:.2f}), so their disagreement is partly noise.")
fig("fig_j_histogram", "Distribution of J over the grid.")
fig("fig_landscape", "Sorted J with v1 and corners.")
fig("fig_marginals", "J against each weight.")
fig("fig_weight_pairs", "Best J for each pair of weights.")
fig("fig_j_pooling_rules", "J under four pooling rules.")
fig("fig_per_dataset_tau_rules", "Per-dataset τ under named weightings.")

# ================================================================== 5. selection
h("5. Honest selection and the plateau")
p("Files: `selection/nested.json`, `nested_draws.npz` (1,000 × 1,771 in-bag and out-of-bag J), `plateau.csv`, `sensitivity.json`.")
Jin, Jout, chosen = draws["J_in"], draws["J_out"], draws["chosen"]
sel_in = Jin.max(1); sel_out = draws["J_out_sel"]; v1_out = draws["J_out_v1"]; best_out = draws["J_out_best"]; d_sel = sel_out - v1_out
tb = pd.DataFrame({"quantity": ["in-bag J of selected", "out-of-bag J of selected", "out-of-bag J of v1", "out-of-bag J of full-data best", "selected − v1 (out of bag)", "full-data best − v1 (out of bag)"],
                   "mean": [sel_in.mean(), sel_out.mean(), v1_out.mean(), best_out.mean(), d_sel.mean(), (best_out - v1_out).mean()],
                   "sd": [sel_in.std(), sel_out.std(), v1_out.std(), best_out.std(), d_sel.std(), (best_out - v1_out).std()],
                   "2.5 %": [np.percentile(x, 2.5) for x in [sel_in, sel_out, v1_out, best_out, d_sel, best_out - v1_out]], "97.5 %": [np.percentile(x, 97.5) for x in [sel_in, sel_out, v1_out, best_out, d_sel, best_out - v1_out]]})
md(tb)
p(f"* Optimism gap {nested['optimism_gap']:.3f}: the in-bag winner looks {nested['optimism_gap']:.3f} better than it is. Out of bag it is {d_sel.mean():+.3f} from v1 and ahead of v1 in {100*(d_sel > 0).mean():.0f} % of resamples; the full-data best is ahead of v1 in {100*((best_out - v1_out) > 0).mean():.0f} %.")
p(f"* {nested['n_distinct_selected']} distinct weightings were selected across 1,000 resamples. Mean selected weights {', '.join(f'{k} {v:.2f}' for k, v in nested['selected_weights_mean'].items())} with SDs {', '.join(f'{k} {v:.2f}' for k, v in nested['selected_weights_sd'].items())}: the selection is essentially uniform over the simplex.")
ts = plateau.sort_values("times_selected", ascending=False).head(12)
p("Most often selected weightings (times selected of 1,000):")
md(ts.assign(weights=[wstr(r) for _, r in ts.iterrows()])[["weights", "J_full", "J_boot_mean", "J_boot_sd", "J_oob_mean", "times_selected", "p_vs_best"]], fmt="{:.3f}")
p(f"* Plateau: {nested['plateau_size']} of 1,771 weightings are not significantly below the best (paired bootstrap p > .05); v1 is inside with p = {nested['v1_p_vs_best']:.2f}. The {1771 - nested['plateau_size']} outside are: " + "; ".join(wstr(r) for _, r in plateau[~plateau.in_plateau].iterrows()) + ".")
p(f"* Practical plateau (bootstrap mean within 0.02 of the best): {nested['practical_plateau_size_within_0.02']}; weight ranges inside it: " + ", ".join(f"{k} [{v[0]:.2f}, {v[1]:.2f}]" for k, v in nested["practical_plateau_weight_ranges"].items()) + ". Every weight can take almost any value and stay within 0.02 of the best.")
p(f"* v1 is in the top 5 % of in-bag J in {100*nested['share_resamples_v1_in_top_5pct']:.0f} % of resamples.")
p("Sensitivity to one lattice step (0.05):")
md(pd.DataFrame(sens).T.reset_index().rename(columns={"index": "point"}), fmt="{:.4f}")
fig("fig_nested", "In-bag vs out-of-bag J.")
fig("fig_optimism_distributions", "Distributions behind the optimism gap.")
fig("fig_oob_difference", "Out-of-bag difference to v1.")
fig("fig_selected_weights", "Selected weights across resamples.")
fig("fig_plateau", "Bootstrap band and plateau boundary.")
fig("fig_plateau_oob", "Full-data, bootstrap and out-of-bag J in rank order.")
fig("fig_times_selected", "Most selected weightings.")
fig("fig_sensitivity", "One-step sensitivity.")

# ================================================================== 6. transfer
h("6. Transfer")
p("Files: `selection/lodo.csv`, `lofo.csv`, `per_family.json`.")
L_ = lodo[lodo.kind == "dataset"]; piv = L_.pivot(index="held_out", columns="weights_from", values="tau_heldout_mean")[["lodo_weights", "full_best", "v1"]]
piv["family"] = [fam_of[d] for d in piv.index]; piv["refitted weights"] = [wstr(r) for _, r in L_[L_.weights_from == "lodo_weights"].set_index("held_out").loc[piv.index].iterrows()]
p("Leave-one-dataset-out: τ of the held-out dataset's ranking to the pooled ranking of the other 30, under weights re-fitted without it, the full-data best and v1:")
md(piv.sort_values("v1").reset_index())
p(f"* Means: re-fitted {piv.lodo_weights.mean():+.3f}, full best {piv.full_best.mean():+.3f}, v1 {piv.v1.mean():+.3f}. Re-fitting beats v1 on {(piv.lodo_weights > piv.v1).sum()} datasets and loses on {(piv.lodo_weights < piv.v1).sum()}; the re-fitted weights are different for almost every held-out set, which is the plateau seen from another side.")
p(f"* Hardest to predict (τ ≤ 0 under every rule): {', '.join(piv[(piv[['lodo_weights','full_best','v1']] <= 0).all(1)].index)}. Easiest (τ ≥ 0.7): {', '.join(piv[(piv[['lodo_weights','full_best','v1']] >= 0.7).all(1)].index)}.")
p("Leave-one-family-out:")
lf = lofo.assign(weights=[wstr(r) for _, r in lofo.iterrows()])[["held_out", "weights_from", "weights", "J_rest", "tau_heldout_mean", "n_heldout"]]
md(lf)
p("Per-family optimum and the family's J under its own optimum, the global best and v1:")
md(pd.DataFrame([{"family": f, "datasets": len(v["datasets"]), "best weights": f"F1 {v['best_weights']['f1']:.2f} / decay {v['best_weights']['decay']:.2f} / P {v['best_weights']['precision']:.2f} / R {v['best_weights']['recall']:.2f}", "J own": v["J_family_best"], "J global best": v["J_family_under_global_best"], "J v1": v["J_family_under_v1"], "L1 to global": v["L1_distance_to_global_best"]} for f, v in pfam.items()]))
p("Within a family the datasets agree more than across the suite (FIN 0.82, SM 0.58, TQA 0.50, EM 0.36 under their own optima) and the optima differ: decay-only for schema matching, recall-heavy for table QA, precision-heavy for finance. The suite-level flatness is partly the families cancelling each other.")
fig("fig_lodo_tau", "Leave-one-dataset-out τ.")
fig("fig_family_weights", "Per-family weights.")
fig("fig_family_j", "Within-family J.")

# ================================================================== 7. designs
h("7. Sampled designs")
p("Files: `designs.csv`, `designs_summary.json` (three designs × 20 seeds × 100 weightings).")
md(designs.groupby("design").agg(best_J_mean=("best_J_found", "mean"), best_J_sd=("best_J_found", "std"), best_J_min=("best_J_found", "min"), regret_mean=("regret", "mean"), regret_max=("regret", "max"), rank_median=("best_rank_in_exhaustive", "median"), rank_worst=("best_rank_in_exhaustive", "max"), discrepancy=("centred_L2_discrepancy", "mean"), min_L1=("min_pairwise_L1", "mean"), zero_share=("share_with_a_zero_weight", "mean")).reset_index(), fmt="{:.4f}")
p("All three designs find a weighting within 0.005 of the exhaustive optimum in every seed; the worst seed of any design still lands in the top 49 of 1,771. With four weights the exhaustive grid costs nothing, so the designs are reported only to show that sampling would have sufficed.")
fig("fig_designs", "Designs vs the exhaustive optimum.")
fig("fig_design_metrics", "Design metrics over seeds.")

# ================================================================== 8. anchors
h("8. Correctness on known-quality anchors")
p("Files: `anchors/anchor_components.csv` (31,380 rows), `correctness.csv` (every weighting), `correctness.json`.")
p(f"* {cj['n_anchors']:,} synthetic answers: {cj['n_correct']:,} with utility 1, {cj['n_wrong']:,} with utility 0, the rest partial; {len(cj['operators'])} operators.")
op = anch.groupby("op").agg(n=("v1", "size"), utility=("utility", "mean"), em=("em", "mean"), f1=("f1", "mean"), decay=("decay", "mean"), precision=("precision", "mean"), recall=("recall", "mean"), v1=("v1", "mean")).sort_values("utility", ascending=False)
op["v1 − utility"] = op.v1 - op.utility
p("Per operator: utility, mean of each ingredient and of the v1 composite:")
md(op.reset_index())
p("Reading: the composite tracks utility well at the ends (identity, verbose, tagged at 1; flip, no answer at 0) and is most generous on `shuffled`, `superset` and `list_dump` (token overlap rewards extra correct tokens) and most severe on `typo`, `digit_typo` and `near_miss_medium` (a changed character or digit destroys both token overlap and numeric closeness). These are the cases a human labeller would score differently from any lexical rule.")
cr = corr[corr.label.notna()].assign(weights=[wstr(r) for _, r in corr[corr.label.notna()].iterrows()])[["label", "weights", "J", "rho", "rho_ds", "auc", "wrong_mean", "hedge_gap", "rank"]]
cr = pd.concat([cr, pd.DataFrame([{"label": k, "weights": f"F1 {v['weights']['f1']:.2f} / decay {v['weights']['decay']:.2f} / P {v['weights']['precision']:.2f} / R {v['weights']['recall']:.2f}", "J": v["J"], "rho": v["rho"], "rho_ds": v["rho_ds"], "auc": v["auc"], "wrong_mean": v["wrong_mean"], "hedge_gap": v["hedge_gap"], "rank": v["rank_by_J"]} for k, v in cj.items() if k in ("best_J", "best_rho", "pareto_knee")] + [{"label": "exact match", "weights": "–", "J": np.nan, "rho": cj["exact_match"]["rho"], "rho_ds": cj["exact_match"]["rho_ds"], "auc": cj["exact_match"]["auc"], "wrong_mean": cj["exact_match"]["wrong_mean"], "hedge_gap": cj["exact_match"]["hedge_gap"], "rank": np.nan}])]).sort_values("rho", ascending=False)
p("Named weightings on the anchors (rank = rank by J):")
md(cr)
q2 = corr.rho.quantile([0, .1, .5, .9, 1]).rename("rho")
p("Distribution of ρ over the 1,771 weightings:"); md(q2.to_frame().T.reset_index(drop=True), fmt="{:.4f}")
p(f"* ρ ranges {corr.rho.min():.3f}–{corr.rho.max():.3f} (wider than J's range); v1 is at rank {cj['v1']['rank_by_J']} by J but rank {cj['v1']['rank_by_rho']} by ρ; the best-by-J weighting is rank {cj['best_J']['rank_by_rho']} by ρ. Spearman(J, ρ) across the grid = {cj['spearman_J_vs_rho_across_grid']:+.2f}. AUC is {corr.auc.min():.3f}–{corr.auc.max():.3f} everywhere: every weighting separates right from wrong; they differ only in partial credit.")
rho_ds = anch.groupby("dataset").apply(lambda d: pd.Series({"rho v1": spearmanr(d.v1, d.utility).correlation, "rho em": spearmanr(d.em, d.utility).correlation, "n": len(d)})).sort_values("rho v1")
p("Per-dataset ρ under v1 and under exact match:")
md(rho_ds.reset_index())
pf = corr[corr.pareto == True].assign(weights=[wstr(r) for _, r in corr[corr.pareto == True].iterrows()])[["weights", "J", "rho", "auc"]]
p(f"Pareto front over (J, ρ): {len(pf)} weightings."); md(pf)
fig("fig_pareto", "J vs ρ.")
fig("fig_anchor_operators", "Operators: utility vs score.")
fig("fig_rho_per_dataset", "ρ per dataset.")
fig("fig_anchor_metrics_vs_j", "AUC, wrong-mean and hedge gap vs J.")

# ================================================================== 9. leaderboards
h("9. Leaderboards under every rule")
p("Files: `leaderboards/<rule>/leaderboard.csv`, `params.json`, `bootstrap.npz`, `rule_agreement.csv`.")
for r in RULES:
    d = LB[r].set_index("model").loc[order]; pr = PAR[r]
    L.append(f"\n**{RP[r]}** — weights: {('F1 %.2f / decay %.2f / P %.2f / R %.2f' % tuple(pr['weights'][k] for k in ['f1','decay','precision','recall'])) if pr['weights'] else 'exact match only'}; Kemeny cost {pr['kemeny']['kendall_cost']:.0f} of {pr['kemeny']['max_cost']:.0f}; BT converged: {pr['bradley_terry']['converged']}, comparisons {int(pr['bradley_terry']['n_comparisons']):,}.\n\n")
    md(pd.DataFrame({"model": [PRETTY[m] for m in order], "BT strength": d.bt_strength, "SE": d.bt_se_vs_ref, "BT rank": d.rank_bt.astype(int), "BT 95 %": [f"[{int(a)}, {int(b_)}]" for a, b_ in zip(d.bt_rank_lo95, d.bt_rank_hi95)], "P(first) BT": d.p_first_bt, "Borda": d.rank_borda.astype(int), "Borda 95 %": [f"[{int(a)}, {int(b_)}]" for a, b_ in zip(d.borda_rank_lo95, d.borda_rank_hi95)], "P(first) Borda": d.p_first_borda, "Kemeny": d.rank_kemeny.astype(int), "Copeland": d.rank_copeland, "mean-z": d.rank_mean_z.astype(int), "RRF": d.rank_rrf.astype(int), "fam-bal z": d.rank_family_balanced_z.astype(int), "mean score": d.mean_score}))
p("Agreement between the Bradley–Terry rankings of the rules (Kendall τ):")
md(ra.rename(index=RP, columns=RP).round(2), index=True, fmt="{:.2f}")
first = pd.DataFrame([{"rule": RP[r], "first (BT)": PRETTY[LB[r].sort_values("rank_bt").model.iloc[0]], "P(first)": LB[r].sort_values("rank_bt").p_first_bt.iloc[0], "first (Borda)": PRETTY[LB[r].sort_values("rank_borda").model.iloc[0]], "first (Kemeny)": PRETTY[LB[r].sort_values("rank_kemeny").model.iloc[0]], "first (mean-z)": PRETTY[LB[r].sort_values("rank_mean_z").model.iloc[0]], "last (BT)": PRETTY[LB[r].sort_values("rank_bt").model.iloc[-1]]} for r in RULES])
p("Who is first under each rule and pooling method:"); md(first)
p(f"* Under v1, Bradley–Terry gives Gemini 3.8 Flash P(first) = {LB['v1_original'].set_index('model').loc['gemini-3.8-flash','p_first_bt']:.2f} while Borda gives it {LB['v1_original'].set_index('model').loc['gemini-3.8-flash','p_first_borda']:.2f} and splits first place three ways (Opus {LB['v1_original'].set_index('model').loc['claude-opus-5','p_first_borda']:.2f}, GPT-5.5 {LB['v1_original'].set_index('model').loc['gpt-5.5','p_first_borda']:.2f}). The two pooling methods answer different questions: BT counts item-level wins (Flash wins many items by small margins), Borda counts dataset-level ranks (GPT-5.5 and Opus top more datasets).")
# bootstrap rank distribution v1
bb = BOOT["v1_original"]; bm = list(bb["models"])
rd = pd.DataFrame({PRETTY[m]: np.bincount(bb["bt_ranks"][:, bm.index(m)].astype(int), minlength=len(order) + 1)[1:len(order) + 1] / 1000 for m in order}).T; rd.columns = [f"rank {i}" for i in range(1, len(order) + 1)]
p("Bootstrap distribution of the Bradley–Terry rank under v1 (share of 1,000 resamples):"); md(rd.round(2).reset_index().rename(columns={"index": "model"}), fmt="{:.2f}")
fig("fig_leaderboard_rules", "BT strengths and rank intervals under three rules.")
fig("fig_bt_all_rules", "BT strengths under all nine rules.")
fig("fig_rank_bootstrap_v1", "Bootstrap rank distributions under v1.")
fig("fig_p_first", "P(first) by rule and pooling method.")
fig("fig_rule_agreement", "τ between rules.")

# ================================================================== 10. significance
h("10. Significance")
p("Files: `leaderboards/<rule>/significance.json`, `pairwise_item_tests.csv`.")
md(pd.DataFrame([{"rule": RP[r], "Friedman χ²": SIG[r]["friedman"]["friedman_chi2"], "p": SIG[r]["friedman"]["friedman_p"], "Iman–Davenport F": SIG[r]["friedman"]["iman_davenport_F"], "Nemenyi CD": SIG[r]["friedman"]["nemenyi_cd_05"], "Kendall W": SIG[r]["kendall_W_datasets"]["kendall_W"], "Holm-sig pairs": sum(x["wilcoxon_significant_05"] for x in SIG[r]["friedman"]["pairwise"]), "Nemenyi-sig pairs": sum(x["nemenyi_significant"] for x in SIG[r]["friedman"]["pairwise"])} for r in RULES]), fmt="{:.3g}")
s = SIG["v1_original"]["friedman"]
mr = pd.Series(s["mean_rank"]).loc[order]
p(f"Mean Friedman rank under v1 (lower is better): " + ", ".join(f"{PRETTY[m]} {v:.2f}" for m, v in mr.items()) + f". Nemenyi CD = {s['nemenyi_cd_05']:.2f}: two models differ at α = .05 only if their mean ranks differ by more than that, which separates the top group from the bottom two and nothing inside the top group.")
pw_ = pd.DataFrame(s["pairwise"]); pw_["a"] = pw_.a.map(PRETTY); pw_["b"] = pw_.b.map(PRETTY)
p("All 45 cross-dataset pairwise tests under v1 (wins = datasets where a scores higher than b):")
md(pw_[["a", "b", "mean_rank_diff", "wins_a", "wins_b", "ties", "wilcoxon_p", "wilcoxon_p_holm", "nemenyi_significant", "wilcoxon_significant_05"]].sort_values("wilcoxon_p"), fmt="{:.3g}")
sp = PW[PW.significant_05].groupby(["a", "b"]).size().sort_values(ascending=False)
p("Per-item paired tests (within datasets, Holm within dataset): number of datasets in which each pair is separated:")
md(sp.rename("datasets").reset_index().assign(a=lambda d: d.a.map(PRETTY), b=lambda d: d.b.map(PRETTY)).head(20), fmt="{:.0f}")
nsp = pd.Series(SIG["v1_original"]["n_significant_pairs_per_dataset"]).sort_values(ascending=False)
p("Significant pairs per dataset (of 45):"); md(nsp.rename("pairs").reset_index().rename(columns={"index": "dataset"}).assign(family=lambda d: d.dataset.map(fam_of)), fmt="{:.0f}")
p(f"{(nsp == 0).sum()} datasets separate no pair at all at the item level ({', '.join(nsp[nsp == 0].index)}); {(nsp >= 20).sum()} separate 20 or more. Power lives in a dozen datasets.")
mb = PAR["v1_original"]["majority_baselines"]
em_pdm = PDM["em_only"]
p("Boolean datasets: exact-match accuracy of the best and worst model against the majority-class baseline of the pool:")
md(pd.DataFrame([{"dataset": d_, "majority class": v["majority_class_accuracy"], "best model": em_pdm[d_].max(), "worst model": em_pdm[d_].min(), "models above baseline": int((em_pdm[d_] > v["majority_class_accuracy"]).sum())} for d_, v in mb.items()]))
fig("fig_cd_diagram_v1", "Critical-difference view under v1.")
fig("fig_pairwise_significance_v1", "Item-level significant pairs.")
fig("fig_significant_pairs_per_dataset", "Significant pairs per dataset.")
fig("fig_majority_baselines", "Boolean sets vs majority baseline.")

# ================================================================== 11. official split
h("11. Official-split comparability")
p("File: `leaderboards/v1_original/official_split_estimates.csv` (post-stratification to the official stratum / class proportions, weighted bootstrap).")
o = OFF.groupby("dataset").agg(suite=("suite_mean", "mean"), official=("official_estimate", "mean"), lo=("official_lo95", "mean"), hi=("official_hi95", "mean"), eff_n=("effective_n", "mean"), f1_pool=("suite_f1_pos", "mean"), f1_official=("official_f1_pos", "mean"), prec_off=("official_precision_pos", "mean"), rec_off=("official_recall_pos", "mean"), pos_share=("official_positive_share", "mean"))
o["shift"] = o.official - o.suite; o["f1 drop"] = o.f1_pool - o.f1_official
md(o.sort_values("shift").reset_index())
p(f"* Accuracy shifts by at most {o["shift"].abs().max():.3f} ({o["shift"].abs().idxmax()}); for {int((o["shift"].abs() < 0.01).sum())} datasets the shift is under 0.01 because the pool strata already match the official split or there is no census (n/c rows are excluded from the mean).")
p(f"* For the matching sets the balanced pool overstates positive-class F1 wherever the official match share is small: the drop is {o['f1 drop'].max():.2f} on {o['f1 drop'].idxmax()} (official match share {o.loc[o['f1 drop'].idxmax(),'pos_share']:.3f}) and {o.loc['papadakis_dn','f1 drop']:.2f} on Papadakis–Christen (share 0.018), driven by precision: at a 2 % match rate even a 1 % false-positive rate halves precision.")
p(f"* Effective sample size after re-weighting falls to {o.eff_n.min():.0f} on {o.eff_n.idxmin()}: the official-ratio intervals for the sparse matching sets are wide, and the official estimates should be read with their intervals.")
fig("fig_official_split", "Suite vs official estimates.")
fig("fig_official_scatter", "All (dataset, model) pairs.")
fig("fig_official_f1_models", "Matching F1: pool vs official ratio per model.")

# ================================================================== 12. diagnostics
h("12. Dataset diagnostics")
p("Files: `diagnostics/dataset_diagnostics.csv`, `diagnostics.json` (pairwise τ between dataset rankings).")
md(diag.sort_values("mean_score").reset_index(drop=True))
pt_ = np.array(dj["pairwise_tau"]); names = dj.get("datasets", datasets)
iu = np.triu_indices(len(names), 1); vals = pt_[iu]
p(f"* Pairwise τ between dataset rankings: mean {vals.mean():+.2f}, median {np.median(vals):+.2f}, range {vals.min():+.2f} to {vals.max():+.2f}; {100*(vals > 0).mean():.0f} % of pairs agree in sign.")
top_pairs = sorted(((vals[k], names[iu[0][k]], names[iu[1][k]]) for k in range(len(vals))), reverse=True)
p("Most and least agreeing dataset pairs:")
md(pd.DataFrame([{"τ": t, "dataset A": a_, "dataset B": b_} for t, a_, b_ in top_pairs[:6] + top_pairs[-6:]]))
p(f"* Flags: ceiling {', '.join(diag[diag.ceiling].dataset)} (mean ≥ 0.95, spread ≤ 0.04); floor none; lowest self-stability {diag.sort_values('ranking_self_stability_tau').dataset.iloc[0]} ({diag.ranking_self_stability_tau.min():.2f}), highest {diag.sort_values('ranking_self_stability_tau').dataset.iloc[-1]} ({diag.ranking_self_stability_tau.max():.2f}). The three ceiling sets are flagged `exclude_from_objective` but were kept inside J in this run.")
fig("fig_dataset_tau", "τ between dataset rankings.")
fig("fig_diagnostics_scatter", "Mean vs spread.")
fig("fig_self_stability", "Self-stability per dataset.")

# ================================================================== 13. one page
h("13. What the data support, in one page")
p(f"""1. **The weights of the deployed judge cannot be improved on this suite by the agreement criterion.** All 1,771 weightings span J {grid.J.min():.3f}–{grid.J.max():.3f}; {nested['plateau_size']} are statistically equivalent to the best; the in-sample winner loses {nested['optimism_gap']:.3f} out of sample and ends {d_sel.mean():+.3f} from v1 with a 95 % interval [{np.percentile(d_sel, 2.5):+.3f}, {np.percentile(d_sel, 97.5):+.3f}]; {nested['n_distinct_selected']} different weightings win across resamples.
2. **Why it is flat.** The four ingredients agree with each other (F1–recall ρ {C.loc['f1','recall']:.2f}, decay–exact match {C.loc['decay','em']:.2f}); in {100*allsame:.0f} % of answers all four equal exact match; and the families pull in opposite directions (decay for SM, recall for TQA, precision for FIN), cancelling at suite level.
3. **Agreement is not correctness.** On 31,380 anchors v1 scores ρ {cj['v1']['rho']:.3f}, the best-by-J weighting {cj['best_J']['rho']:.3f}, the best-by-ρ {cj['best_rho']['rho']:.3f}, exact match {cj['exact_match']['rho']:.3f}; Spearman(J, ρ) = {cj['spearman_J_vs_rho_across_grid']:+.2f}. Every weighting has AUC ≥ {corr.auc.min():.3f}; they differ only in partial credit, and the operators where lexical rules fail (typos, digit typos, medium near misses, shuffled lists) are the ones human labels must settle.
4. **The leaderboard.** Ends fixed under every rule: {PRETTY[order[-1]]} last, gpt-oss-120b ninth, Holm-significant against the top group; Friedman p < 0.001 everywhere. First place is {PRETTY[LB['v1_original'].sort_values('rank_bt').model.iloc[0]]} by Bradley–Terry (P = {LB['v1_original'].sort_values('rank_bt').p_first_bt.iloc[0]:.2f}) but {PRETTY[LB['v1_original'].sort_values('rank_borda').model.iloc[0]]} by Borda under v1, and {PRETTY[LB['em_only'].sort_values('rank_bt').model.iloc[0]]} under exact match. No model is first on more than {int((rk == 1).sum(1).max())} datasets; Kendall's W = {SIG['v1_original']['kendall_W_datasets']['kendall_W']:.2f}; {(nsp == 0).sum()} datasets separate no pair at the item level.
5. **Comparability.** Post-stratification moves accuracy by ≤ {o["shift"].abs().max():.2f}; balanced matching pools overstate official-ratio F1 by up to {o['f1 drop'].max():.2f}, through precision at low match rates.
6. **Caveats carried by the data.** Lexical scoring only; synthetic anchors; defaults rather than greedy decoding on two providers; {int(facts.cut_at_16000.sum())} answers still cut at 16,000 tokens plus {int(facts.cut_below_16000_pending.sum())} awaiting their 16,000-token re-ask; three ceiling datasets inside the objective; one prompt.""")

DOC.write_text("".join(L))
print(f"wrote {DOC} ({len(''.join(L))//1000} k chars)")
