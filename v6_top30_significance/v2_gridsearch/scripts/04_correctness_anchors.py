#!/usr/bin/env python
"""
v2 step 4 - Correctness check borrowed from v5, WITHOUT changing v2's objective.

v5 generates synthetic answers of known utility for every pool item (typed operators: identity, alias, unit change, rounding,
off-by-magnitude, wrong number, partial list, hedged answer, paraphrase, ... each with a fixed utility in [0, 1]).  Here those
anchors are scored with the four v1 ingredients under EVERY lattice weighting, so each weighting gets, next to its agreement J:
  rho        Spearman correlation between the composite score and the known utility (all anchors)
  rho_ds     mean of the per-dataset Spearman correlations
  auc        AUC for separating correct anchors (utility = 1) from wrong ones (utility <= 0.1)
  wrong_mean mean score given to wrong answers (should be near 0)
  hedge_gap  mean score of hedged anchors minus the mean score of their committed counterparts (should be negative)
Also computed for the exact-match rule.  The (J, rho) Pareto front tells whether agreement and correctness pull the same way.
Outputs: output/anchors/anchor_components.csv (cached), correctness.csv (per weighting), correctness.json (v1, best-J, best-rho,
         exact match, Pareto knee), fig_pareto.png/pdf
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
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from anchors.ladder import Item, generate  # noqa: E402
from metrics import AnswerType, component_dict  # noqa: E402

COMP = ["f1", "decay", "precision", "recall"]; WC = [f"w_{c}" for c in COMP]
V1 = np.array([0.35, 0.35, 0.15, 0.15])
BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#3a9d5d"


def build_anchor_components(datasets):
    path = OUT / "anchors" / "anchor_components.csv"
    if path.exists():
        return pd.read_csv(path)
    rows = []
    for d in datasets:
        items = [json.loads(l) for l in open(DATA / "pool" / f"{d}.jsonl", encoding="utf-8")]
        items = [r for r in items if r.get("in_real_subset")]
        its = [Item(r["uid"], d, r["ground_truth"], AnswerType(r["answer_type"]), r.get("gold_aliases") or [], r.get("gold_list")) for r in items]
        by = {r["uid"]: r for r in items}
        for a in generate(its):
            r = by[a["uid"]]
            c = component_dict(a["prediction"], r["ground_truth"], r.get("gold_aliases"), AnswerType(r["answer_type"]), gold_list=r.get("gold_list"))
            rows.append({"dataset": d, "uid": a["uid"], "atype": a["atype"], "op": a["op"], "utility": a["utility"], "em": c["em"],
                         "f1": c["tok_f1"], "decay": c["num_decay"], "precision": c["tok_prec"], "recall": c["tok_rec"], "hedge_free": c["hedge_free"]})
        print(f"[{d}] {sum(1 for x in rows if x['dataset'] == d)} anchors")
    df = pd.DataFrame(rows); df.to_csv(path, index=False); return df


def auc_many(S, pos, neg):
    """S: n x C scores; Mann-Whitney AUC per column computed on the correct ∪ wrong subset only (ties = 0.5)"""
    keep = pos | neg; R = stats.rankdata(S[keep], axis=0); p = pos[keep]; n1, n0 = p.sum(), (~p).sum()
    return (R[p].sum(0) - n1 * (n1 + 1) / 2) / (n1 * n0)


def spearman_many(S, u):
    R = stats.rankdata(S, axis=0); ru = stats.rankdata(u)
    R = R - R.mean(0); ru = ru - ru.mean()
    return (R * ru[:, None]).sum(0) / (np.sqrt((R ** 2).sum(0) * (ru ** 2).sum()) + 1e-12)


def main():
    (OUT / "anchors").mkdir(exist_ok=True)
    idx = json.load(open(OUT / "tensors_index.json")); datasets = idx["datasets"]
    A = build_anchor_components(datasets)
    grid = pd.read_csv(OUT / "grid_exhaustive.csv"); W = grid[WC].to_numpy(float)
    Xa = A[COMP].to_numpy(float); u = A.utility.to_numpy(float)
    S = Xa @ W.T                                                                          # n_anchor x C
    pos, neg = u >= 0.999, u <= 0.1
    rho = spearman_many(S, u); auc = auc_many(S, pos, neg); wrong = S[neg].mean(0)
    rho_ds = np.mean([spearman_many(S[(A.dataset == d).to_numpy()], u[(A.dataset == d).to_numpy()]) for d in datasets], 0)
    hedged = A.op.str.contains("hedge").to_numpy()
    hedge_gap = S[hedged].mean(0) - S[(A.op == "identity").to_numpy()].mean(0) if hedged.any() else np.full(len(W), np.nan)
    # exact match rule
    em = A.em.to_numpy(float)[:, None]
    em_row = {"rho": float(spearman_many(em, u)[0]), "rho_ds": float(np.mean([spearman_many(em[(A.dataset == d).to_numpy()], u[(A.dataset == d).to_numpy()])[0] for d in datasets])),
              "auc": float(auc_many(em, pos, neg)[0]), "wrong_mean": float(em[neg].mean()), "hedge_gap": float(em[hedged].mean() - em[(A.op == 'identity').to_numpy()].mean()) if hedged.any() else None}
    corr = grid[["rank", "label"] + WC + ["J", "tau_native"]].copy()
    corr["rho"] = rho; corr["rho_ds"] = rho_ds; corr["auc"] = auc; corr["wrong_mean"] = wrong; corr["hedge_gap"] = hedge_gap
    # Pareto front on (J, rho): not dominated
    Jv, Rv = corr.J.to_numpy(), corr.rho.to_numpy(); pareto = np.ones(len(corr), bool)
    for i in range(len(corr)):
        pareto[i] = not np.any((Jv >= Jv[i]) & (Rv >= Rv[i]) & ((Jv > Jv[i]) | (Rv > Rv[i])))
    corr["pareto"] = pareto; corr.to_csv(OUT / "anchors" / "correctness.csv", index=False)
    # knee: Pareto point closest to the utopia (max J, max rho) after min-max scaling
    P = corr[pareto]; jz = (P.J - Jv.min()) / (Jv.max() - Jv.min() + 1e-12); rz = (P.rho - Rv.min()) / (Rv.max() - Rv.min() + 1e-12)
    knee = P.iloc[int(np.argmin((1 - jz) ** 2 + (1 - rz) ** 2))]

    def row(r):
        return {"weights": dict(zip(COMP, r[WC].astype(float).round(2).tolist())), "J": float(r.J), "rho": float(r.rho), "rho_ds": float(r.rho_ds), "auc": float(r.auc),
                "wrong_mean": float(r.wrong_mean), "hedge_gap": None if pd.isna(r.hedge_gap) else float(r.hedge_gap), "rank_by_J": int(r["rank"]), "rank_by_rho": int((corr.rho > r.rho).sum() + 1)}
    v1 = corr[corr.label == "v1_original"].iloc[0]; bestJ = corr.iloc[0]; bestR = corr.loc[corr.rho.idxmax()]
    summary = {"n_anchors": int(len(A)), "n_correct": int(pos.sum()), "n_wrong": int(neg.sum()), "operators": sorted(A.op.unique().tolist()),
               "v1": row(v1), "best_J": row(bestJ), "best_rho": row(bestR), "pareto_knee": row(knee), "exact_match": em_row,
               "pareto_size": int(pareto.sum()), "spearman_J_vs_rho_across_grid": float(stats.spearmanr(Jv, Rv)[0]),
               "reading": "rho and auc are correctness against known-utility anchors; J is agreement among datasets. If the best-J weighting also has high rho, agreement and correctness pull the same way; if not, the Pareto knee is the defensible compromise."}
    json.dump(summary, open(OUT / "anchors" / "correctness.json", "w"), indent=2)
    fig, ax = plt.subplots(figsize=(5, 3.4))
    ax.scatter(corr.J, corr.rho, s=4, alpha=0.3, color=GRAY, label="all weightings")
    ax.scatter(P.J, P.rho, s=10, color=BLUE, label="Pareto front")
    ax.scatter([v1.J], [v1.rho], color=ORANGE, zorder=5, label="v1"); ax.scatter([bestJ.J], [bestJ.rho], color=INK, marker="^", zorder=5, label="best J")
    ax.scatter([knee.J], [knee.rho], color=GREEN, marker="*", s=80, zorder=6, label="Pareto knee"); ax.axhline(em_row["rho"], color=ORANGE, ls=":", lw=0.8, label="exact match ρ")
    ax.set_xlabel("J (agreement among datasets)"); ax.set_ylabel("ρ (correctness on anchors)"); ax.legend(fontsize=6, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "anchors" / "fig_pareto.png", dpi=200); fig.savefig(OUT / "anchors" / "fig_pareto.pdf"); plt.close(fig)
    print(json.dumps({k: summary[k] for k in ["v1", "best_J", "best_rho", "pareto_knee", "exact_match", "spearman_J_vs_rho_across_grid"]}, indent=1))


if __name__ == "__main__":
    main()
