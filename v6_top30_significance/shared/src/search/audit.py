"""
Shared building blocks for the weight-search audits (v2: 4 ingredients, v4: 9 components).

  load_tensors(csv, comp)                  components CSV -> models, datasets, X{d: n x M x K}, EM{d}, NAT{d}, families
  evaluate_all(W, X, EM, NAT, ds, models, comp, with_bt)   J (Borda) + J under Kemeny / Copeland / (BT) + tau_native + diagnostics, per candidate
  design_comparison(K, step, n, seeds, evaluate, best_J)   uniform-lattice / Dirichlet / LHS designs: coverage + regret per seed
  anchor_components(pool_dir, datasets, comp_fn, cache)    v5's synthetic anchors scored with the given component function (cached CSV)
  correctness(A, comp, W, grid, out_dir, extra_rules)      rho / AUC / wrong-mean / hedge-gap per candidate + Pareto (J, rho) + JSON summary
  neighbours(w, step, K)                                   all one-step lattice moves of w (for sensitivity when the design is sampled)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from pooling.rank_aggregation import consensus_ranking, kendall_tau, ranks_from_scores
from search.fast_rank import J_many, ranks_many, tau_b
from search.sampling import coverage, sample_dirichlet_lattice, sample_lhs_simplex, sample_uniform_lattice
from stats.params import bt_fit

BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#3a9d5d"


def load_tensors(csv_path: Path, comp: Sequence[str]):
    df = pd.read_csv(csv_path); models = sorted(df.model.unique()); datasets = sorted(df.dataset.unique())
    X, EM, NAT, uids = {}, {}, {}, {}
    for d in datasets:
        g = df[df.dataset == d]
        piv = {c: g.pivot_table(index="uid", columns="model", values=c).reindex(columns=models) for c in list(comp) + ["em", "native_value"]}
        X[d] = np.stack([piv[c].to_numpy(float) for c in comp], -1); EM[d] = piv["em"].to_numpy(float); NAT[d] = piv["native_value"].to_numpy(float); uids[d] = list(piv[comp[0]].index)
    fam = df.drop_duplicates("dataset").set_index("dataset").family.to_dict() if "family" in df else {}
    return models, datasets, X, EM, NAT, uids, fam


def score_tensor(X, W, datasets):
    means = np.stack([np.nanmean(X[d], 0) for d in datasets], -1)
    return np.einsum("ck,mkd->cmd", W, means)


def pooled_J(S, rule):
    out = np.empty(S.shape[0])
    for c in range(S.shape[0]):
        R = consensus_ranking(S[c], rule); out[c] = np.mean([kendall_tau(-ranks_from_scores(S[c][:, j]), -R) for j in range(S.shape[2])])
    return out


def bt_J(X, W, datasets):
    M = X[datasets[0]].shape[1]; C = len(W); out = np.empty(C)
    per_item = [np.einsum("ck,nmk->cnm", W, np.nan_to_num(X[d])) for d in datasets]
    for c in range(C):
        wins = np.zeros((M, M))
        for s in per_item:
            sc = s[c]; gt = (sc[:, :, None] > sc[:, None, :]).sum(0); eq = (sc[:, :, None] == sc[:, None, :]).sum(0)
            wins += gt + 0.5 * (eq - np.eye(M) * sc.shape[0])
        Rc = ranks_from_scores(bt_fit(wins)["beta"]); S = np.stack([s[c].mean(0) for s in per_item], 1)
        out[c] = np.mean([kendall_tau(-ranks_from_scores(S[:, j]), -Rc) for j in range(S.shape[1])])
    return out


def evaluate_all(W, X, EM, NAT, datasets, models, comp, labels: Dict[int, str] | None = None, with_bt=True):
    S = score_tensor(X, W, datasets); res = J_many(S)
    natS = np.stack([np.nanmean(NAT[d], 0) for d in datasets], 1); Rn = ranks_many(natS[None])[0]; R = ranks_many(S)
    tau_nat = tau_b(np.moveaxis(R, 1, 2), np.moveaxis(Rn, 0, 1)[None]).mean(1)
    Cc = S - S.mean(1, keepdims=True); disp = Cc.std(2).mean(1) / (Cc.mean(2).std(1) + 1e-9)
    df = pd.DataFrame({f"w_{c}": W[:, k] for k, c in enumerate(comp)}); df["label"] = [(labels or {}).get(i, "") for i in range(len(W))]
    df["J"] = res["J"]; df["min_agree"] = res["min_agree"]; df["pairwise_tau"] = res["pairwise_tau"]; df["tau_native"] = tau_nat; df["dispersion"] = disp
    df["J_kemeny"] = pooled_J(S, "kemeny"); df["J_copeland"] = pooled_J(S, "copeland")
    if with_bt:
        df["J_bt"] = bt_J(X, W, datasets)
    for j, d in enumerate(datasets):
        df[f"tau_{d}"] = res["tau_per_dataset"][:, j]
    for m_i, m in enumerate(models):
        df[f"rank_{m}"] = res["consensus_ranks"][:, m_i]
    return df, S


def design_comparison(K: int, step: float, n: int, seeds: int, evaluate: Callable[[np.ndarray], np.ndarray], best_J: float | None = None) -> pd.DataFrame:
    rows = []
    for seed in range(seeds):
        for name, fn in [("uniform_lattice", sample_uniform_lattice), ("dirichlet_lattice", sample_dirichlet_lattice), ("lhs_simplex", sample_lhs_simplex)]:
            W = fn(n, K, step, seed + 1000); J = evaluate(W); cov = coverage(W)
            rows.append({"design": name, "seed": seed, **cov, "best_J_found": float(J.max()), "mean_J": float(J.mean()),
                         "regret": float(best_J - J.max()) if best_J is not None else np.nan, "best_weights": json.dumps(np.round(W[int(np.argmax(J))], 2).tolist())})
    return pd.DataFrame(rows)


def design_summary(designs: pd.DataFrame) -> dict:
    g = designs.groupby("design").agg(best_J_mean=("best_J_found", "mean"), best_J_sd=("best_J_found", "std"), best_J_max=("best_J_found", "max"), mean_J=("mean_J", "mean"),
                                      regret_mean=("regret", "mean"), regret_max=("regret", "max"), min_pairwise_L1=("min_pairwise_L1", "mean"), mean_nearest_L1=("mean_nearest_L1", "mean"),
                                      discrepancy=("centred_L2_discrepancy", "mean"), zero_share=("share_with_a_zero_weight", "mean")).round(4)
    return {d: r.to_dict() for d, r in g.iterrows()}


def anchor_components(pool_dir: Path, datasets: Sequence[str], comp_fn: Callable[[str, dict], dict], cache: Path, real_only: bool = True) -> pd.DataFrame:
    if cache.exists():
        return pd.read_csv(cache)
    from anchors.ladder import Item, generate
    from metrics import AnswerType
    rows = []
    for d in datasets:
        items = [json.loads(l) for l in open(pool_dir / f"{d}.jsonl", encoding="utf-8")]
        if real_only:
            items = [r for r in items if r.get("in_real_subset")]
        its = [Item(r["uid"], d, r["ground_truth"], AnswerType(r["answer_type"]), r.get("gold_aliases") or [], r.get("gold_list")) for r in items]
        by = {r["uid"]: r for r in items}
        for a in generate(its):
            r = by[a["uid"]]; c = comp_fn(a["prediction"], r)
            rows.append({"dataset": d, "uid": a["uid"], "atype": a["atype"], "op": a["op"], "utility": a["utility"], **c})
    df = pd.DataFrame(rows); cache.parent.mkdir(parents=True, exist_ok=True); df.to_csv(cache, index=False); return df


def _auc_many(S, pos, neg):
    keep = pos | neg; R = stats.rankdata(S[keep], axis=0); p = pos[keep]; n1, n0 = p.sum(), (~p).sum()
    return (R[p].sum(0) - n1 * (n1 + 1) / 2) / (n1 * n0)


def _spearman_many(S, u):
    R = stats.rankdata(S, axis=0); ru = stats.rankdata(u); R = R - R.mean(0); ru = ru - ru.mean()
    return (R * ru[:, None]).sum(0) / (np.sqrt((R ** 2).sum(0) * (ru ** 2).sum()) + 1e-12)


def correctness(A: pd.DataFrame, comp: Sequence[str], W: np.ndarray, grid: pd.DataFrame, out_dir: Path, ref_label: str, extra_rules: Dict[str, np.ndarray] | None = None,
                human: pd.DataFrame | None = None) -> dict:
    """grid: rows aligned with W, with columns rank, label, J, tau_native.  extra_rules: name -> per-anchor score vector (e.g. exact match)."""
    out_dir.mkdir(parents=True, exist_ok=True); WC = [f"w_{c}" for c in comp]
    Xa = A[list(comp)].to_numpy(float); u = A.utility.to_numpy(float); S = Xa @ W.T; pos, neg = u >= 0.999, u <= 0.1
    datasets = sorted(A.dataset.unique()); hedged = A.op.str.contains("hedge").to_numpy(); ident = (A.op == "identity").to_numpy()

    def terms(Sx):
        return {"rho": _spearman_many(Sx, u), "rho_ds": np.mean([_spearman_many(Sx[(A.dataset == d).to_numpy()], u[(A.dataset == d).to_numpy()]) for d in datasets], 0),
                "auc": _auc_many(Sx, pos, neg), "wrong_mean": Sx[neg].mean(0), "hedge_gap": (Sx[hedged].mean(0) - Sx[ident].mean(0)) if hedged.any() else np.full(Sx.shape[1], np.nan)}
    T = terms(S); corr = grid[["rank", "label"] + WC + ["J", "tau_native"]].copy()
    for k, v in T.items():
        corr[k] = v
    Jv, Rv = corr.J.to_numpy(), corr.rho.to_numpy(); pareto = np.ones(len(corr), bool)
    for i in range(len(corr)):
        pareto[i] = not np.any((Jv >= Jv[i]) & (Rv >= Rv[i]) & ((Jv > Jv[i]) | (Rv > Rv[i])))
    corr["pareto"] = pareto; corr.to_csv(out_dir / "correctness.csv", index=False)
    P = corr[pareto]; jz = (P.J - Jv.min()) / (Jv.max() - Jv.min() + 1e-12); rz = (P.rho - Rv.min()) / (Rv.max() - Rv.min() + 1e-12)
    knee = P.iloc[int(np.argmin((1 - jz) ** 2 + (1 - rz) ** 2))]

    def row(r):
        return {"weights": dict(zip(comp, r[WC].astype(float).round(2).tolist())), "J": float(r.J), "rho": float(r.rho), "rho_ds": float(r.rho_ds), "auc": float(r.auc), "wrong_mean": float(r.wrong_mean),
                "hedge_gap": None if pd.isna(r.hedge_gap) else float(r.hedge_gap), "rank_by_J": int(r["rank"]), "rank_by_rho": int((corr.rho > r.rho).sum() + 1)}
    ref = corr[corr.label == ref_label]; summary = {"n_anchors": int(len(A)), "n_correct": int(pos.sum()), "n_wrong": int(neg.sum()), "operators": sorted(A.op.unique().tolist()),
                                                    "reference_label": ref_label, "reference": row(ref.iloc[0]) if len(ref) else None, "best_J": row(corr.iloc[0]), "best_rho": row(corr.loc[corr.rho.idxmax()]),
                                                    "pareto_knee": row(knee), "pareto_size": int(pareto.sum()), "spearman_J_vs_rho_across_candidates": float(stats.spearmanr(Jv, Rv)[0]), "extra_rules": {}}
    for nm, vec in (extra_rules or {}).items():
        t = terms(np.asarray(vec, float)[:, None]); summary["extra_rules"][nm] = {k: (None if np.isnan(v[0]) else float(v[0])) for k, v in t.items()}
    if human is not None and len(human):
        summary["human_labels_note"] = "human utility supplied; see correctness_human.csv"
    json.dump(summary, open(out_dir / "correctness.json", "w"), indent=2)
    fig, ax = plt.subplots(figsize=(5, 3.4))
    ax.scatter(corr.J, corr.rho, s=4, alpha=0.3, color=GRAY, label="all candidates"); ax.scatter(P.J, P.rho, s=10, color=BLUE, label="Pareto front")
    if len(ref):
        ax.scatter([ref.J.iloc[0]], [ref.rho.iloc[0]], color=ORANGE, zorder=5, label=ref_label)
    ax.scatter([corr.J.iloc[0]], [corr.rho.iloc[0]], color=INK, marker="^", zorder=5, label="best J"); ax.scatter([knee.J], [knee.rho], color=GREEN, marker="*", s=80, zorder=6, label="Pareto knee")
    for nm, t in summary["extra_rules"].items():
        ax.axhline(t["rho"], color=ORANGE, ls=":", lw=0.8, label=f"{nm} ρ")
    ax.set_xlabel("J (agreement among datasets)"); ax.set_ylabel("ρ (correctness on anchors)"); ax.legend(fontsize=6, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out_dir / "fig_pareto.png", dpi=200); fig.savefig(out_dir / "fig_pareto.pdf"); plt.close(fig)
    return summary


def neighbours(w: np.ndarray, step: float) -> np.ndarray:
    K = len(w); out = []
    for i in range(K):
        for j in range(K):
            if i != j and w[i] >= step - 1e-9:
                v = w.copy(); v[i] -= step; v[j] += step; out.append(np.round(v, 6))
    return np.unique(np.asarray(out), axis=0) if out else np.empty((0, K))
