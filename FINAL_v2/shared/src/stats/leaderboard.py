"""
Version-independent leaderboard + significance + parameter dump for ONE scoring rule.

  report_rule(name, items, datasets, models, fam, out_dir, weights=None, majority=None, n_boot=1000)
      items: list over datasets of (n_items x M) per-item scores under the rule (NaN allowed)
      writes leaderboard.md/csv, params.json (Bradley-Terry strengths + SE, Kemeny order + cost, Copeland, Borda, pairwise wins,
      family-balanced z), bootstrap.npz (Borda ranks, BT strengths and ranks per draw, per-dataset means), significance.json
      (Friedman / Iman-Davenport / Nemenyi / Holm-Wilcoxon, Kendall's W), pairwise_item_tests.csv, per_dataset_mean/se.csv, table.tex
      returns dict(rank_bt, rank_borda, S, items, sig, lb)
  rule_agreement(results)      Kendall tau between the BT rankings of every pair of rules
  dataset_diagnostics(res, datasets, models, fam, out_dir)   pairwise dataset tau heat-map, floor / ceiling / self-stability flags
  majority_baselines(pool_dir, datasets)   majority-class accuracy for boolean datasets
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pooling.rank_aggregation import consensus_ranking, kendall_tau, pairwise_dataset_tau, ranks_from_scores
from stats.params import bt_fit, borda_scores, copeland_scores, kemeny, pairwise_wins
from stats.significance import bootstrap_ranking, friedman_nemenyi, kendall_w, pairwise_item_tests

INK = "#0b0b0b"


def family_balanced_z(S, datasets, fam):
    Z = (S - S.mean(0)) / (S.std(0) + 1e-9); fams = sorted({fam.get(d, "OTHER") for d in datasets})
    return np.stack([Z[:, [i for i, d in enumerate(datasets) if fam.get(d, "OTHER") == f]].mean(1) for f in fams], 1).mean(1), fams


def majority_baselines(pool_dir: Path, datasets: Sequence[str]) -> Dict[str, dict]:
    out = {}
    for d in datasets:
        p = pool_dir / f"{d}.jsonl"
        if not p.exists():
            continue
        pool = [json.loads(l) for l in open(p, encoding="utf-8")]
        real = [r for r in pool if r.get("in_real_subset")]
        if real and np.mean([r.get("answer_type") == "boolean" for r in real]) > 0.5:
            golds = [str(r["ground_truth"]).strip().lower() for r in real]
            out[d] = {"majority_class_accuracy": max(golds.count(v) for v in set(golds)) / len(golds), "n": len(golds)}
    return out


def _j(x):
    return x.tolist() if isinstance(x, np.ndarray) else x


def report_rule(name: str, items: List[np.ndarray], datasets: Sequence[str], models: Sequence[str], fam: Dict[str, str], out_dir: Path,
                weights: Optional[dict] = None, majority: Optional[dict] = None, n_boot: int = 1000, n_perm: int = 5000, poststrat: Optional[dict] = None) -> dict:
    """poststrat: {"weights": [w_d], "labels": [gold labels or None], "infos": [dict]} aligned with `items` (see stats.poststrat)"""
    out_dir.mkdir(parents=True, exist_ok=True); M = len(models)
    S = np.stack([np.nanmean(I, 0) for I in items], 1); SE = np.stack([np.nanstd(I, 0) / np.sqrt(np.sum(~np.isnan(I[:, 0]))) for I in items], 1)
    wins = pairwise_wins(items); bt = bt_fit(wins)
    rank_bt = ranks_from_scores(bt["beta"]); rank_borda = consensus_ranking(S, "borda"); rank_z = consensus_ranking(S, "mean_z")
    kem = kemeny(S); rank_kem = kem["position"] + 1; cop = copeland_scores(S); rank_cop = ranks_from_scores(cop); rank_rrf = consensus_ranking(S, "rrf")
    fbz, fams = family_balanced_z(S, datasets, fam); rank_fb = ranks_from_scores(fbz)
    boot_b = bootstrap_ranking(items, "borda", n_boot, seed=1)
    rng = np.random.default_rng(2); bt_draws = np.empty((n_boot, M)); bt_rank_draws = np.empty((n_boot, M))
    for b in range(n_boot):
        res = [I[rng.integers(0, I.shape[0], I.shape[0])] for I in items]; beta = bt_fit(pairwise_wins(res))["beta"]
        bt_draws[b] = beta; bt_rank_draws[b] = ranks_from_scores(beta)
    np.savez_compressed(out_dir / "bootstrap.npz", borda_ranks=boot_b["ranks"], per_dataset_means=boot_b["means"], bt_beta=bt_draws, bt_ranks=bt_rank_draws, models=np.array(models))
    sig = {"friedman": friedman_nemenyi(S, list(models)), "kendall_W_datasets": kendall_w(S)}
    pit = pd.DataFrame(pairwise_item_tests(items, list(datasets), list(models), n_perm=n_perm)); pit.to_csv(out_dir / "pairwise_item_tests.csv", index=False)
    sig["n_significant_pairs_per_dataset"] = pit.groupby("dataset").significant_05.sum().to_dict() if len(pit) else {}
    json.dump(sig, open(out_dir / "significance.json", "w"), indent=2)
    pd.DataFrame(S, index=list(models), columns=list(datasets)).to_csv(out_dir / "per_dataset_mean.csv")
    pd.DataFrame(SE, index=list(models), columns=list(datasets)).to_csv(out_dir / "per_dataset_se.csv")
    lb = pd.DataFrame({"model": list(models), "bt_strength": bt["beta"].round(3), "bt_se_vs_ref": bt["se_vs_reference"].round(3), "rank_bt": rank_bt,
                       "bt_rank_lo95": np.percentile(bt_rank_draws, 2.5, 0), "bt_rank_hi95": np.percentile(bt_rank_draws, 97.5, 0), "p_first_bt": (bt_rank_draws == 1).mean(0).round(3),
                       "rank_borda": rank_borda, "borda_rank_lo95": boot_b["rank_lo"], "borda_rank_hi95": boot_b["rank_hi"], "p_first_borda": boot_b["p_first"].round(3),
                       "rank_mean_z": rank_z, "rank_kemeny": rank_kem, "rank_copeland": rank_cop, "rank_rrf": rank_rrf, "rank_family_balanced_z": rank_fb,
                       "mean_score": S.mean(1).round(4), "mean_z": ((S - S.mean(0)) / (S.std(0) + 1e-9)).mean(1).round(3), "family_balanced_z": fbz.round(3)}).sort_values("rank_bt")
    lb.to_csv(out_dir / "leaderboard.csv", index=False)
    params = {"rule": name, "weights": weights, "bradley_terry": {k: _j(v) for k, v in bt.items()}, "pairwise_wins": wins.tolist(), "kemeny": {k: _j(v) for k, v in kem.items()},
              "copeland": cop.tolist(), "borda": borda_scores(S).tolist(), "families": fams, "family_balanced_z": fbz.tolist(), "models": list(models), "datasets": list(datasets),
              "majority_baselines": majority or {}}
    json.dump(params, open(out_dir / "params.json", "w"), indent=2)
    fr = sig["friedman"]
    wtxt = "" if not weights else " (weights " + ", ".join(f"{k} {v:.2f}" for k, v in weights.items()) + ")"
    L = [f"# Leaderboard under rule `{name}`{wtxt}\n",
         "| # (BT) | Model | BT strength ± SE | BT rank 95 % | P(first) | Borda rank [95 %] | mean-z rank | Kemeny | Copeland | family-balanced rank | mean score |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in lb.iterrows():
        L.append(f"| {int(r.rank_bt)} | {r.model} | {r.bt_strength:+.2f} ± {r.bt_se_vs_ref:.2f} | [{int(r.bt_rank_lo95)}, {int(r.bt_rank_hi95)}] | {r.p_first_bt:.2f} | {int(r.rank_borda)} [{int(r.borda_rank_lo95)}, {int(r.borda_rank_hi95)}] | {int(r.rank_mean_z)} | {int(r.rank_kemeny)} | {int(r.rank_copeland)} | {int(r.rank_family_balanced_z)} | {r.mean_score:.3f} |")
    L += ["", f"Friedman χ² = {fr.get('friedman_chi2', float('nan')):.2f}, p = {fr.get('friedman_p', float('nan')):.3f}; Iman–Davenport p = {fr.get('iman_davenport_p', float('nan')):.3f}; Nemenyi CD (α = .05) = {fr.get('nemenyi_cd_05', float('nan')):.2f} mean-rank units; "
          f"Kendall's W among datasets = {sig['kendall_W_datasets']['kendall_W']:.2f} (p = {sig['kendall_W_datasets']['p']:.3f}). Attainable τ values with {M} models: {fr.get('tau_granularity')}.", "",
          "Pairwise (Holm-corrected Wilcoxon across datasets): " + "; ".join(f"{p['a']} vs {p['b']}: p = {p['wilcoxon_p_holm']:.3f}{' *' if p['wilcoxon_significant_05'] else ''}" for p in fr.get("pairwise", [])) + ".", "",
          "Per-dataset means (SE in `per_dataset_se.csv`):", "", "| Model | " + " | ".join(datasets) + " |", "|---|" + "---|" * len(datasets)]
    for m_i, m in enumerate(models):
        L.append(f"| {m} | " + " | ".join(f"{S[m_i, j]:.3f}" for j in range(len(datasets))) + " |")
    if majority:
        L += ["", "Majority-class accuracy for boolean datasets: " + ", ".join(f"{d} {v['majority_class_accuracy']:.2f}" for d, v in majority.items()) + "."]
    official = None
    if poststrat is not None:
        from stats.poststrat import weighted_estimates
        official = weighted_estimates(items, poststrat["weights"], poststrat["labels"], list(datasets), list(models), poststrat["infos"], n_boot=n_boot)
        official.to_csv(out_dir / "official_split_estimates.csv", index=False)
        L += ["", "## Official-split estimates (post-stratified to the official stratum / class proportions; 95 % weighted item bootstrap)", "",
              "| Model | " + " | ".join(datasets) + " |", "|---|" + "---|" * len(datasets)]
        for m in models:
            cells = []
            for d in datasets:
                r = official[(official.model == m) & (official.dataset == d)].iloc[0]
                cells.append((f"{r.official_estimate:.3f} [{r.official_lo95:.2f}, {r.official_hi95:.2f}]" + (f" F1 {r.official_f1_pos:.2f}" if "official_f1_pos" in r and not np.isnan(r.get("official_f1_pos", np.nan)) else "")) if r.weighted else f"{r.suite_mean:.3f} (n/c)")
            L.append(f"| {m} | " + " | ".join(cells) + " |")
        L += ["", "n/c = not comparable to the published split (constructed pairs, closed-book, or no census); suite scores above remain the calibration numbers. "
              "Boolean matching sets show positive-class F1 at the official class ratio. Effective n per dataset: " + ", ".join(f"{d} {poststrat['infos'][j].get('effective_n', float('nan')):.0f}" for j, d in enumerate(datasets)) + "."]
    open(out_dir / "leaderboard.md", "w").write("\n".join(L) + "\n")
    tex = ["\\begin{tabular}{llccc}", "\\toprule", "Rank & Model & BT strength & Borda rank [95\\%] & mean score \\\\", "\\midrule"]
    for _, r in lb.iterrows():
        tex.append(f"{int(r.rank_bt)} & {r.model} & ${r.bt_strength:+.2f} \\pm {r.bt_se_vs_ref:.2f}$ & {int(r.rank_borda)} [{int(r.borda_rank_lo95)}, {int(r.borda_rank_hi95)}] & {r.mean_score:.3f} \\\\")
    tex += ["\\bottomrule", "\\end{tabular}"]; open(out_dir / "table.tex", "w").write("\n".join(tex) + "\n")
    return {"rule": name, "rank_bt": rank_bt, "rank_borda": rank_borda, "S": S, "items": items, "sig": sig, "lb": lb, "official": official}


def rule_agreement(results: Dict[str, dict]) -> pd.DataFrame:
    names = list(results); A = pd.DataFrame(index=names, columns=names, dtype=float)
    for a in names:
        for b in names:
            A.loc[a, b] = kendall_tau(-results[a]["rank_bt"], -results[b]["rank_bt"])
    return A


def summary_of(results: Dict[str, dict], models: Sequence[str], weights: Dict[str, Optional[dict]]) -> dict:
    return {n: {"weights": weights.get(n), "bt_ranking": {m: int(r) for m, r in zip(models, res["rank_bt"])}, "borda_ranking": {m: int(r) for m, r in zip(models, res["rank_borda"])},
                "friedman_p": res["sig"]["friedman"].get("friedman_p"), "kendall_W": res["sig"]["kendall_W_datasets"]["kendall_W"],
                "significant_pairs_holm": [f"{p['a']} > {p['b']}" if p["mean_rank_diff"] < 0 else f"{p['b']} > {p['a']}" for p in res["sig"]["friedman"].get("pairwise", []) if p["wilcoxon_significant_05"]]}
            for n, res in results.items()}


def dataset_diagnostics(res: dict, datasets: Sequence[str], models: Sequence[str], fam: Dict[str, str], out_dir: Path, label: str = "reference rule") -> pd.DataFrame:
    out_dir.mkdir(exist_ok=True); S, items = res["S"], res["items"]; T = pairwise_dataset_tau(S); n = len(datasets)
    fig, ax = plt.subplots(figsize=(max(4.8, 0.3 * n + 2), max(4, 0.3 * n + 1.5))); im = ax.imshow(T, vmin=-1, vmax=1, cmap="RdBu")
    ax.set_xticks(range(n)); ax.set_xticklabels(datasets, rotation=60, ha="right", fontsize=6); ax.set_yticks(range(n)); ax.set_yticklabels(datasets, fontsize=6)
    if n <= 16:
        for i in range(n):
            for j in range(n):
                ax.text(j, i, f"{T[i, j]:.1f}", ha="center", va="center", fontsize=5, color=INK)
    fig.colorbar(im, ax=ax, shrink=0.8, label=f"Kendall τ between dataset rankings ({label})"); fig.tight_layout(); fig.savefig(out_dir / "fig_dataset_tau.png", dpi=200); fig.savefig(out_dir / "fig_dataset_tau.pdf"); plt.close(fig)
    rng = np.random.default_rng(3); rows = []
    for j, d in enumerate(datasets):
        I = items[j]; consts = 0; ranks = []
        for _ in range(500):
            m = np.nanmean(I[rng.integers(0, I.shape[0], I.shape[0])], 0); consts += int(np.allclose(m, m[0])); ranks.append(ranks_from_scores(m))
        ranks = np.array(ranks); stab = np.mean([kendall_tau(-ranks[b], -ranks_from_scores(S[:, j])) for b in range(len(ranks))])
        rows.append({"dataset": d, "family": fam.get(d, "OTHER"), "mean_score": float(S[:, j].mean()), "spread_across_models": float(S[:, j].max() - S[:, j].min()),
                     "floor": bool(S[:, j].max() < 0.05), "ceiling": bool(S[:, j].min() > 0.95), "share_constant_bootstrap_rankings": consts / 500,
                     "ranking_self_stability_tau": float(stab), "tau_to_others_mean": float(np.mean([T[j, k] for k in range(n) if k != j])), "n_items": int(I.shape[0])})
    diag = pd.DataFrame(rows); diag["exclude_from_objective"] = diag.floor | diag.ceiling | (diag.ranking_self_stability_tau < 0.2)
    diag.to_csv(out_dir / "dataset_diagnostics.csv", index=False)
    json.dump({"pairwise_tau": T.tolist(), "datasets": list(datasets), "excluded": diag[diag.exclude_from_objective].dataset.tolist()}, open(out_dir / "diagnostics.json", "w"), indent=2)
    return diag


def poststrat_for(pool_dir: Path, datasets: Sequence[str], uid_order: Dict[str, Sequence[str]]) -> Optional[dict]:
    """Build the post-stratification input for report_rule: weights and gold labels aligned with each dataset's uid order."""
    import json as _json
    from stats.poststrat import load_strata, weights_for
    strata = load_strata(pool_dir / "_official_strata.json")
    if not strata:
        return None
    W, Lb, I = [], [], []
    for d in datasets:
        items = {r["uid"]: r for r in (_json.loads(l) for l in open(pool_dir / f"{d}.jsonl", encoding="utf-8"))}
        w, lab, info = weights_for(d, items, list(uid_order[d]), strata)
        if strata.get(d, {}).get("official_positive_share") is not None:
            info["official_positive_share"] = strata[d]["official_positive_share"]
        W.append(w); Lb.append(lab); I.append(info)
    return {"weights": W, "labels": Lb, "infos": I}


def official_table_md(rule_dir: Path, models: Sequence[str], datasets: Sequence[str], title: str) -> List[str]:
    """Markdown section comparing suite scores with post-stratified official-split estimates for one rule (reads official_split_estimates.csv)."""
    p = rule_dir / "official_split_estimates.csv"
    if not p.exists():
        return ["", f"## {title}\n", "No official-split census available (`data/pool/_official_strata.json` missing); run `shared/scripts/00b_official_strata.py`."]
    o = pd.read_csv(p); L = ["", f"## {title}\n",
                             "Suite score = mean over the stratified pool (equal strata; the calibration number). Official estimate = the same answers re-weighted to the official split's "
                             "stratum or class proportions (post-stratification), with a 95 % weighted item bootstrap; F1 = positive-class F1 at the official match ratio for boolean matching sets. "
                             "n/c = not comparable (constructed pairs, closed-book, or no census).", "",
                             "| dataset | model | suite score | official estimate [95 %] | positive-class F1 (suite → official) | effective n |", "|---|---|---|---|---|---|"]
    for d in datasets:
        for m in models:
            r = o[(o.dataset == d) & (o.model == m)]
            if not len(r):
                continue
            r = r.iloc[0]
            if not r.weighted:
                L.append(f"| {d} | {m} | {r.suite_mean:.3f} | n/c | – | {r.n_items} |"); continue
            f1 = f"{r.suite_f1_pos:.2f} → {r.official_f1_pos:.2f} [{r.official_f1_lo95:.2f}, {r.official_f1_hi95:.2f}]" if "official_f1_pos" in r and pd.notna(r.get("official_f1_pos")) else "–"
            L.append(f"| {d} | {m} | {r.suite_mean:.3f} | {r.official_estimate:.3f} [{r.official_lo95:.2f}, {r.official_hi95:.2f}] | {f1} | {r.effective_n:.0f} |")
    return L
