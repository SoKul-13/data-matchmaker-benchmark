#!/usr/bin/env python
"""
v3 step 2 - the eight aggregation views, their fitted parameters WITH standard errors, every combination of views, sampled designs,
and a split-half honesty check.

Views (native metric per dataset): mean_raw, baseline_norm_mean, z_mean, mean_win_rate, borda, kemeny_score, bradley_terry, irt_ability.
Candidates (weights over the z-scored views, sum 1):
  * all 255 non-empty subsets with equal weights (includes the 8 corners and the uniform mix)     labels subset_<bitmask>
  * 100 uniform-lattice and 100 Latin-hypercube points at step 0.05                                 labels lattice_i / lhs_i
Objective (unchanged): J = 0.5 stability + 0.25 transitivity + 0.25 reference, where stability = mean tau between the mixed ranking on
B item-bootstrap resamples and on full data; transitivity = tau to the Copeland ranking of per-dataset scores; reference = tau to the
Kemeny consensus of the eight single-view rankings.
Parameters saved (output/params/): Bradley-Terry strengths + SE, Rasch abilities + SE and item difficulties + SE, Kemeny order + cost,
Copeland, Borda, win matrix; per bootstrap draw the BT strengths and Rasch abilities (npz).
Combos (output/combos/): combos.csv with weights, terms, J, mixed scores, ranks, bootstrap rank CIs; combo_<label>.json per subset.
Honesty: 50 random half-splits of items; select the best candidate on half A (J with 20 inner resamples), evaluate it on half B,
compare with pure BT, uniform and the full-data best on half B (output/selection/split_half.json).
Also the same views on EXACT-MATCH item scores (output/views_em.csv) for the EM-only leaderboard.
Outputs: views.csv, views_em.csv, Zb.npz, combos/, params/, designs.json, selection/split_half.json, best.json, fig_views.png/pdf, fig_combos.png/pdf
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from pooling.rank_aggregation import consensus_ranking, kendall_tau, kemeny_order, ranks_from_scores  # noqa: E402
from search.sampling import coverage, sample_lhs_simplex, sample_uniform_lattice  # noqa: E402
from stats.params import bt_fit, copeland_scores, kemeny, pairwise_wins, rasch_fit  # noqa: E402
from views import VIEWS, all_views, per_dataset_table, standardise  # noqa: E402

K = len(VIEWS); STEP = 0.05
BLUE, ORANGE, GRAY, INK, GREEN = "#2a78d6", "#eb6834", "#c3c2b7", "#0b0b0b", "#3a9d5d"


def item_matrices(items, models, datasets, col="score"):
    return [items[items.dataset == d].pivot_table(index="uid", columns="model", values=col).reindex(columns=models).to_numpy(float) for d in datasets]


def resample(items, rng, frac_split=None):
    parts = []
    for d, g in items.groupby("dataset"):
        uids = g.uid.unique(); pick = rng.choice(uids, len(uids), replace=True)
        parts.append(pd.concat([g[g.uid == u] for u in pick]))
    return pd.concat(parts)


def split_half(items, rng):
    A, B = [], []
    for d, g in items.groupby("dataset"):
        uids = rng.permutation(g.uid.unique()); h = len(uids) // 2
        A.append(g[g.uid.isin(uids[:h])]); B.append(g[g.uid.isin(uids[h:])])
    return pd.concat(A), pd.concat(B)


def objective_terms(Z, Zb, W, copeland_r, kemeny_ref):
    """Z (M x K), Zb (B x M x K), W (C x K) -> stability, transitivity, reference, J, mixed scores, ranks, bootstrap ranks"""
    s = Z.to_numpy() @ W.T                                              # M x C
    R = np.stack([ranks_from_scores(s[:, c]) for c in range(W.shape[0])], 1)      # M x C
    sb = np.einsum("bmk,ck->bcm", Zb, W)                                # B x C x M
    Rb = np.empty_like(sb)
    for b in range(sb.shape[0]):
        for c in range(sb.shape[1]):
            Rb[b, c] = ranks_from_scores(sb[b, c])
    stab = np.array([np.mean([kendall_tau(-Rb[b, c], -R[:, c]) for b in range(sb.shape[0])]) for c in range(W.shape[0])])
    trans = np.array([kendall_tau(-R[:, c], -copeland_r) for c in range(W.shape[0])]); ref = np.array([kendall_tau(-R[:, c], -kemeny_ref) for c in range(W.shape[0])])
    return {"stability": stab, "transitivity": trans, "reference": ref, "J": 0.5 * stab + 0.25 * trans + 0.25 * ref, "scores": s, "ranks": R, "boot_ranks": Rb}


def fit_views_with_params(items, baseline, models, datasets):
    V = all_views(items, baseline); T = per_dataset_table(items).reindex(index=models)
    mats = item_matrices(items, models, datasets); wins = pairwise_wins(mats); bt = bt_fit(wins)
    piv = items.pivot_table(index=["dataset", "uid"], columns="model", values="score").reindex(columns=models).to_numpy(float)
    rasch = rasch_fit((piv >= 0.5).astype(float)); kem = kemeny(T.to_numpy()); cop = copeland_scores(T.to_numpy())
    return V.reindex(index=models), {"bradley_terry": bt, "rasch": rasch, "kemeny": kem, "copeland": cop, "wins": wins, "per_dataset_table": T}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--boot", type=int, default=100); ap.add_argument("--splits", type=int, default=50); ap.add_argument("--inner", type=int, default=20)
    ap.add_argument("--n-design", type=int, default=100); ap.add_argument("--seed", type=int, default=20260909); args = ap.parse_args()
    items = pd.read_csv(OUT / "native_item_scores.csv"); baseline = json.load(open(OUT / "random_baseline.json"))
    models = sorted(items.model.unique()); datasets = sorted(items.dataset.unique()); M = len(models)
    for sub in ["combos", "params", "selection"]:
        (OUT / sub).mkdir(exist_ok=True)
    # ---------- full-data views + parameters with SE
    V, P = fit_views_with_params(items, baseline, models, datasets); V.round(4).to_csv(OUT / "views.csv"); Z = standardise(V)
    Vem, Pem = fit_views_with_params(items.assign(score=items.em), baseline, models, datasets); Vem.round(4).to_csv(OUT / "views_em.csv")
    def jsonable(P):
        return {"bradley_terry": {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in P["bradley_terry"].items()},
                "rasch": {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in P["rasch"].items() if k not in ("b", "se_b")},
                "rasch_item_difficulty_summary": {"mean": float(P["rasch"]["b"].mean()), "sd": float(P["rasch"]["b"].std()), "se_mean": float(P["rasch"]["se_b"].mean())},
                "kemeny": {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in P["kemeny"].items()}, "copeland": P["copeland"].tolist(), "wins": P["wins"].tolist(), "models": models}
    json.dump({"native": jsonable(P), "exact_match": jsonable(Pem)}, open(OUT / "params" / "view_params_full.json", "w"), indent=2)
    pd.DataFrame({"item": [f"{d}/{u}" for d, u in items.drop_duplicates(["dataset", "uid"]).sort_values(["dataset", "uid"])[["dataset", "uid"]].to_numpy()][: len(P["rasch"]["b"])],
                  "difficulty": P["rasch"]["b"], "se": P["rasch"]["se_b"]}).to_csv(OUT / "params" / "rasch_item_difficulties.csv", index=False)
    # ---------- bootstrap views (+ per-draw BT and Rasch parameters)
    rng = np.random.default_rng(args.seed); Zb = np.empty((args.boot, M, K)); bt_draws = np.empty((args.boot, M)); th_draws = np.empty((args.boot, M))
    for b in range(args.boot):
        it_b = resample(items, rng); Vb, Pb = fit_views_with_params(it_b, baseline, models, datasets)
        Zb[b] = standardise(Vb).to_numpy(); bt_draws[b] = Pb["bradley_terry"]["beta"]; th_draws[b] = Pb["rasch"]["theta"]
    np.savez_compressed(OUT / "Zb.npz", Zb=Zb, bt_beta=bt_draws, rasch_theta=th_draws, models=np.array(models), views=np.array(VIEWS))
    json.dump({"bt_beta_mean": bt_draws.mean(0).tolist(), "bt_beta_sd_bootstrap": bt_draws.std(0).tolist(), "rasch_theta_mean": th_draws.mean(0).tolist(), "rasch_theta_sd_bootstrap": th_draws.std(0).tolist(),
               "bt_se_analytic_vs_ref": P["bradley_terry"]["se_vs_reference"].tolist(), "rasch_se_analytic": P["rasch"]["se_theta"].tolist(), "models": models, "B": args.boot},
              open(OUT / "params" / "view_params_bootstrap.json", "w"), indent=2)
    # ---------- reference rankings
    T = P["per_dataset_table"].to_numpy(); copeland_r = consensus_ranking(T, "copeland")
    single_ranks = np.stack([ranks_from_scores(Z[v].to_numpy()) for v in VIEWS], 1); kem_ref = kemeny_order(-single_ranks); kemeny_ref = np.empty(M); kemeny_ref[kem_ref] = np.arange(1, M + 1)
    # ---------- candidates
    subsets = [s for r in range(1, K + 1) for s in itertools.combinations(range(K), r)]
    W_sub = np.array([[1 / len(s) if k in s else 0.0 for k in range(K)] for s in subsets]); lab_sub = ["subset_" + "".join("1" if k in s else "0" for k in range(K)) for s in subsets]
    W_lat = sample_uniform_lattice(args.n_design, K, STEP, args.seed); W_lhs = sample_lhs_simplex(args.n_design, K, STEP, args.seed)
    W = np.vstack([W_sub, W_lat, W_lhs]); labels = lab_sub + [f"lattice_{i:03d}" for i in range(len(W_lat))] + [f"lhs_{i:03d}" for i in range(len(W_lhs))]
    src = ["subset"] * len(W_sub) + ["lattice"] * len(W_lat) + ["lhs"] * len(W_lhs)
    res = objective_terms(Z, Zb, W, copeland_r, kemeny_ref)
    df = pd.DataFrame({"label": labels, "design": src, "n_views": (W > 0).sum(1), **{f"w_{v}": W[:, k] for k, v in enumerate(VIEWS)}, "stability": res["stability"], "transitivity": res["transitivity"],
                       "reference": res["reference"], "J": res["J"], **{f"score_{m}": res["scores"][i] for i, m in enumerate(models)}, **{f"rank_{m}": res["ranks"][i] for i, m in enumerate(models)},
                       **{f"rank_lo_{m}": np.percentile(res["boot_ranks"][:, :, i], 2.5, 0) for i, m in enumerate(models)}, **{f"rank_hi_{m}": np.percentile(res["boot_ranks"][:, :, i], 97.5, 0) for i, m in enumerate(models)}})
    df = df.sort_values(["J", "stability"], ascending=False).reset_index(drop=True); df.insert(0, "rank", range(1, len(df) + 1)); df.to_csv(OUT / "combos" / "combos.csv", index=False)
    for _, r in df[df.design == "subset"].iterrows():
        members = [v for v in VIEWS if r[f"w_{v}"] > 0]
        json.dump({"label": r.label, "views": members, "weights": {v: float(r[f"w_{v}"]) for v in members}, "J": float(r.J), "stability": float(r.stability), "transitivity": float(r.transitivity),
                   "reference": float(r.reference), "rank_among_candidates": int(r["rank"]), "mixed_scores": {m: float(r[f"score_{m}"]) for m in models}, "ranks": {m: int(r[f"rank_{m}"]) for m in models},
                   "rank_ci95": {m: [float(r[f"rank_lo_{m}"]), float(r[f"rank_hi_{m}"])] for m in models},
                   "member_parameters": {v: ({"beta": P["bradley_terry"]["beta"].tolist(), "se_vs_reference": P["bradley_terry"]["se_vs_reference"].tolist()} if v == "bradley_terry" else
                                             {"theta": P["rasch"]["theta"].tolist(), "se_theta": P["rasch"]["se_theta"].tolist()} if v == "irt_ability" else
                                             {"order": P["kemeny"]["order"].tolist(), "kendall_cost": P["kemeny"]["kendall_cost"]} if v == "kemeny_score" else
                                             {"values": V[v].tolist()}) for v in members}}, open(OUT / "combos" / f"combo_{r.label}.json", "w"), indent=2)
    # ---------- designs (coverage only; both are 100-point samples of the same lattice)
    designs = {"lattice": coverage(W_lat), "lhs": coverage(W_lhs), "best_J": {"subset": float(df[df.design == "subset"].J.max()), "lattice": float(df[df.design == "lattice"].J.max()), "lhs": float(df[df.design == "lhs"].J.max())}}
    json.dump(designs, open(OUT / "designs.json", "w"), indent=2)
    # ---------- split-half honesty
    rng2 = np.random.default_rng(args.seed + 1); rows = []; i_bt = labels.index("subset_" + "".join("1" if v == "bradley_terry" else "0" for v in VIEWS)); i_uni = labels.index("subset_" + "1" * K); i_best = int(df.index[0])
    W_best_full = df.iloc[0][[f"w_{v}" for v in VIEWS]].to_numpy(float)
    for s in range(args.splits):
        A, B = split_half(items, rng2)
        def half(part):
            Vh, Ph = fit_views_with_params(part, baseline, models, datasets); Zh = standardise(Vh)
            Zhb = np.stack([standardise(fit_views_with_params(resample(part, rng2), baseline, models, datasets)[0]).to_numpy() for _ in range(args.inner)])
            Th = Ph["per_dataset_table"].to_numpy(); cr = consensus_ranking(Th, "copeland"); sr = np.stack([ranks_from_scores(Zh[v].to_numpy()) for v in VIEWS], 1)
            ko = kemeny_order(-sr); kr = np.empty(M); kr[ko] = np.arange(1, M + 1); return Zh, Zhb, cr, kr
        ZA, ZAb, cA, kA = half(A); ZB, ZBb, cB, kB = half(B)
        JA = objective_terms(ZA, ZAb, W, cA, kA)["J"]; sel = int(np.argmax(JA)); JB = objective_terms(ZB, ZBb, W, cB, kB)["J"]
        rows.append({"split": s, "selected": labels[sel], "J_A_selected": float(JA[sel]), "J_B_selected": float(JB[sel]), "J_B_pure_bt": float(JB[i_bt]), "J_B_uniform": float(JB[i_uni]),
                     "J_B_full_best": float(objective_terms(ZB, ZBb, W_best_full[None], cB, kB)["J"][0])})
    sh = pd.DataFrame(rows); sh.to_csv(OUT / "selection" / "split_half.csv", index=False)
    d_sel_bt = sh.J_B_selected - sh.J_B_pure_bt
    json.dump({"splits": args.splits, "inner_resamples": args.inner, "J_A_selected_mean": float(sh.J_A_selected.mean()), "J_B_selected_mean": float(sh.J_B_selected.mean()), "optimism_gap": float((sh.J_A_selected - sh.J_B_selected).mean()),
               "J_B_pure_bt_mean": float(sh.J_B_pure_bt.mean()), "J_B_uniform_mean": float(sh.J_B_uniform.mean()), "J_B_full_best_mean": float(sh.J_B_full_best.mean()),
               "selected_minus_pure_bt": {"mean": float(d_sel_bt.mean()), "ci95": [float(d_sel_bt.quantile(0.025)), float(d_sel_bt.quantile(0.975))], "share_selected_ahead": float((d_sel_bt > 0).mean())},
               "selection_counts": sh.selected.value_counts().head(10).to_dict()}, open(OUT / "selection" / "split_half.json", "w"), indent=2)
    # ---------- best.json
    top = df.head(5); best = df.iloc[0]
    json.dump({"views": VIEWS, "models": models, "datasets": datasets, "n_candidates": int(len(df)), "n_subsets": len(W_sub), "n_lattice": len(W_lat), "n_lhs": len(W_lhs), "B": args.boot,
               "best": {"label": best.label, "weights": {v: float(best[f"w_{v}"]) for v in VIEWS}, "J": float(best.J), "stability": float(best.stability), "transitivity": float(best.transitivity), "reference": float(best.reference)},
               "top5": [{"label": r.label, "weights": {v: float(r[f"w_{v}"]) for v in VIEWS if r[f"w_{v}"] > 0}, "J": float(r.J)} for _, r in top.iterrows()],
               "single_views": {v: {"J": float(df[df.label == "subset_" + "".join("1" if u == v else "0" for u in VIEWS)].J.iloc[0]), "ranks": {m: int(ranks_from_scores(Z[v].to_numpy())[i]) for i, m in enumerate(models)}} for v in VIEWS},
               "uniform_J": float(df[df.label == "subset_" + "1" * K].J.iloc[0]), "best_by_size": {int(n): {"label": g.iloc[0].label, "J": float(g.iloc[0].J)} for n, g in df[df.design == "subset"].groupby("n_views")},
               "designs": designs, "kemeny_reference_rank": dict(zip(models, kemeny_ref.tolist())), "copeland_rank": dict(zip(models, copeland_r.tolist()))}, open(OUT / "best.json", "w"), indent=2)
    # ---------- figures
    fig, ax = plt.subplots(figsize=(6.5, 3))
    for dname, col in [("subset", BLUE), ("lattice", GRAY), ("lhs", GREEN)]:
        sub = df[df.design == dname]; ax.scatter(sub["rank"], sub.J, s=8, color=col, label=f"{dname} ({len(sub)})")
    ax.axhline(df[df.label == "subset_" + "1" * K].J.iloc[0], color=ORANGE, ls="--", lw=1); ax.text(len(df), df[df.label == "subset_" + "1" * K].J.iloc[0], "uniform", ha="right", va="bottom", fontsize=7, color=ORANGE)
    ax.set_xlabel("candidate (sorted by J)"); ax.set_ylabel("J = .5 stability + .25 transitivity + .25 reference"); ax.legend(fontsize=7, frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "fig_combos.png", dpi=200); fig.savefig(OUT / "fig_combos.pdf"); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 3)); order = list(V.index)
    im = ax.imshow(np.stack([ranks_from_scores(Z[v].to_numpy()) for v in VIEWS], 1), cmap="viridis_r", aspect="auto"); ax.set_yticks(range(M)); ax.set_yticklabels(order); ax.set_xticks(range(K)); ax.set_xticklabels(VIEWS, rotation=60, ha="right", fontsize=7)
    fig.colorbar(im, ax=ax, label="rank under the view"); fig.tight_layout(); fig.savefig(OUT / "fig_views.png", dpi=200); fig.savefig(OUT / "fig_views.pdf"); plt.close(fig)
    print(df.head(8)[["rank", "label", "n_views", "stability", "transitivity", "reference", "J"]].round(3).to_string(index=False))
    print("split-half:", json.load(open(OUT / "selection" / "split_half.json"))["selected_minus_pure_bt"])


if __name__ == "__main__":
    main()
