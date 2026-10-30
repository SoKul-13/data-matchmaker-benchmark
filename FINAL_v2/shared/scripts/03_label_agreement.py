#!/usr/bin/env python
"""Agreement, adjudication queue and merge for the human labels (any number of labellers, any number of labels per row).

    uv run python shared/scripts/03_label_agreement.py                 # main sheets
    uv run python shared/scripts/03_label_agreement.py --pilot         # the calibration round (every labeller grades the same rows)
    uv run python shared/scripts/03_label_agreement.py --check C       # validate one returned file (add --pilot for the pilot file)

Input: the labellers' returned files, looked up per letter in this order: data/labels/returned/03_main_<L>.xlsx, .csv (pilot: 02_pilot_<L>);
Letters come from data/labels/assignments.csv.  Only `row_id`, `utility`, `hedged`, `note` are read from the returned files.  A grader
must label the rows assigned to them (`assigned_to` contains their letter); labels on other rows are accepted as extra labels.

Reports: Krippendorff's alpha (ordinal, any number of coders, missing values allowed) on `utility`, alpha (nominal) on `hedged`, exact and
within-one-level agreement over all pairs of labels on the same row, agreement by answer type, and per labeller the mean absolute gap to the
other labellers on shared rows (to spot an outlier).  Writes data/labels/adjudication_queue.csv: rows whose labels span more than one level,
whose `hedged` votes tie, or that are missing a label.  If data/labels/adjudicated.csv exists (columns row_id, utility, hedged), merges the
final label per row into data/labels/human_labels.csv (dataset, uid, model, utility, hedged, label, n_labels, adjudicated, ...) and writes
data/labels/human_correctness.{csv,json}: every v2 leaderboard rule scored on the labelled rows against the human utility.
"""
from __future__ import annotations
import argparse, itertools, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; RET = LAB / "returned"; OUT_V2 = ROOT / "v2_gridsearch" / "output"
LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]


# ---------------------------------------------------------------- statistics
def krippendorff_alpha(units: list[list[float]], metric: str = "ordinal") -> float:
    """Krippendorff's alpha for any number of coders with missing data.  `units` = one list of values per row (only values present).
    Rows with fewer than two values are ignored.  Ordinal metric uses the cumulative-marginal distance; nominal is 0/1."""
    units = [u for u in units if len(u) >= 2]
    if not units: return float("nan")
    vals = sorted(set(v for u in units for v in u)); idx = {v: i for i, v in enumerate(vals)}
    n_c = np.zeros(len(vals))
    for u in units:
        for v in u: n_c[idx[v]] += 1
    n = n_c.sum()
    def d2(c, k):
        if c == k: return 0.0
        if metric == "nominal": return 1.0
        lo, hi = min(c, k), max(c, k)
        return (n_c[lo:hi + 1].sum() - (n_c[lo] + n_c[hi]) / 2) ** 2
    Do = 0.0
    for u in units:
        m = len(u)
        Do += sum(d2(idx[a], idx[b]) for a, b in itertools.permutations(u, 2)) / (m - 1)
    Do /= n
    De = sum(n_c[c] * n_c[k] * d2(c, k) for c in range(len(vals)) for k in range(len(vals)) if c != k) / (n * (n - 1))
    return 1 - Do / De if De > 0 else 1.0


def alpha_ci(units, metric="ordinal", B=300, seed=0):
    """95% percentile bootstrap interval for alpha, resampling rows."""
    units = [u for u in units if len(u) >= 2]
    if len(units) < 5: return float("nan"), float("nan")
    rng = np.random.default_rng(seed); vals = []
    for _ in range(B):
        idx = rng.integers(0, len(units), len(units)); vals.append(krippendorff_alpha([units[i] for i in idx], metric))
    return float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))


def auc(scores, correct):
    s, c = np.asarray(scores, float), np.asarray(correct, bool)
    if c.sum() == 0 or (~c).sum() == 0: return float("nan")
    pos, neg = s[c], s[~c]
    return (np.sum(pos[:, None] > neg[None, :]) + 0.5 * np.sum(pos[:, None] == neg[None, :])) / (len(pos) * len(neg))


# ---------------------------------------------------------------- input
def letters_for(pilot: bool) -> list[str]:
    return sorted(pd.read_csv(LAB / "assignments.csv").labeller.unique())


def load_sheet(lab: str, pilot: bool, quiet=False) -> pd.DataFrame | None:
    """The grader's returned file (xlsx or csv from data/labels/returned/)."""
    cands = [RET / f"{'02_pilot' if pilot else '03_main'}_{lab}.xlsx", RET / f"{'02_pilot' if pilot else '03_main'}_{lab}.csv"]
    for c in cands:
        if c.exists():
            df = pd.read_excel(c, dtype=str) if c.suffix == ".xlsx" else pd.read_csv(c, dtype=str)
            if not quiet: print(f"labeller {lab}: {c.relative_to(ROOT)}")
            return df.set_index("row_id")
    return None


def expected_rows(lab: str, pilot: bool, master: pd.DataFrame) -> pd.Index:
    if pilot: return master.index
    return master.index[master.assigned_to.str.split().apply(lambda v: lab in v)]


def num(series):
    return pd.to_numeric(series.astype(str).str.strip().replace({"": np.nan, "nan": np.nan, "None": np.nan}), errors="coerce")


def check_one(S: pd.DataFrame, master: pd.DataFrame, lab: str, rows: pd.Index) -> int:
    """Validate one returned sheet: all assigned row ids, no blanks, values on the scale, columns unchanged.  Returns the number of problems."""
    probs = []
    unknown = [r for r in S.index if r not in master.index]
    if unknown: probs.append(f"{len(unknown)} unknown row ids: {unknown[:10]}")
    if len(S) != len(master): probs.append(f"row count changed: sheet has {len(S)} rows, expected {len(master)} (rows deleted or added?)")
    expected = [c for c in master.columns if not c.startswith("_")]
    if list(S.columns) != expected: probs.append(f"columns changed: expected {expected}, got {list(S.columns)}")
    full = S.reindex(master.index)
    extra = [r for r in master.index if r not in rows and str(full.loc[r, "utility"]).strip() not in ("", "nan", "None")]
    if extra: print(f"  note: {len(extra)} labelled rows beyond this grader's assignment; kept as extra labels")
    S = full.reindex(rows)
    u = S.utility.astype(str).str.strip().replace({"nan": "", "None": ""}); h = S.hedged.astype(str).str.strip().replace({"nan": "", "None": ""})
    bu = [r for r, v in u.items() if v == ""]; bh = [r for r, v in h.items() if v == ""]
    if bu: probs.append(f"utility blank on {len(bu)} rows: {bu[:15]}")
    if bh: probs.append(f"hedged blank on {len(bh)} rows: {bh[:15]}")
    def ok(v, allowed):
        try: return float(v) in allowed
        except ValueError: return False
    wu = [(r, v) for r, v in u.items() if v and not ok(v, LEVELS)]; wh = [(r, v) for r, v in h.items() if v and not ok(v, (0.0, 1.0))]
    if wu: probs.append(f"utility outside {{0, 0.25, 0.5, 0.75, 1}} on {len(wu)} rows: {wu[:10]}")
    if wh: probs.append(f"hedged outside {{0, 1}} on {len(wh)} rows: {wh[:10]}")
    ro = [c for c in expected if c not in ("utility", "hedged", "note") and c in full.columns]
    changed = [c for c in ro if not (full[c].fillna("").astype(str).str.strip().values == master[c].fillna("").astype(str).str.strip().values).all()]
    if changed: probs.append(f"read-only columns edited: {changed}")
    print(f"labeller {lab}: {len(rows)} rows checked; " + ("OK, nothing to fix" if not probs else f"{len(probs)} problem(s):"))
    for q in probs: print("  -", q)
    return len(probs)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pilot", action="store_true"); ap.add_argument("--check", metavar="LETTER"); a = ap.parse_args()
    master = pd.read_csv(LAB / ("pilot_master.csv" if a.pilot else "sample_master.csv")).set_index("row_id")
    letters = letters_for(a.pilot)
    if a.check:
        S = load_sheet(a.check, a.pilot)
        if S is None: raise SystemExit(f"no returned file for labeller {a.check} in {RET.relative_to(ROOT)}")
        return check_one(S, master, a.check, expected_rows(a.check, a.pilot, master))

    # long table: one line per (row, labeller) label
    recs = []
    for L in letters:
        S = load_sheet(L, a.pilot)
        if S is None: print(f"labeller {L}: nothing returned yet"); continue
        rows = expected_rows(L, a.pilot, master); S = S.reindex(master.index)
        u, h = num(S.utility), num(S.hedged)
        for rid in master.index:
            if rid in rows or pd.notna(u[rid]):
                recs.append({"row_id": rid, "labeller": L, "utility": u[rid], "hedged": h[rid], "note": S.loc[rid, "note"] if "note" in S.columns else ""})
    if not recs: raise SystemExit("no returned sheets found")
    long = pd.DataFrame(recs)
    bad = long[long.utility.notna() & ~long.utility.isin(LEVELS)]
    if len(bad): print("values outside the scale:", bad[["row_id", "labeller", "utility"]].head(10).to_dict("records"))
    got = long[long.utility.notna()]
    per_row = got.groupby("row_id").utility.apply(list); per_row_h = long[long.hedged.notna()].groupby("row_id").hedged.apply(list)
    n_exp = long.groupby("row_id").size(); n_got = got.groupby("row_id").size().reindex(n_exp.index).fillna(0).astype(int)
    print(f"\nrows: {len(master)} | labels expected {len(long)}, received {len(got)} ({len(long) - len(got)} blank) | labellers returned: {sorted(got.labeller.unique())}")
    print(f"rows with all labels in: {(n_got == n_exp).sum()} | with >= 2 labels: {(n_got >= 2).sum()} | with < 2: {(n_got < 2).sum()}")
    units = [v for v in per_row if len(v) >= 2]
    pairs = [(x, y) for v in units for x, y in itertools.combinations(v, 2)]
    exact = np.mean([x == y for x, y in pairs]) if pairs else float("nan"); within = np.mean([abs(x - y) <= 0.25 for x, y in pairs]) if pairs else float("nan")
    lo, hi = alpha_ci(units); hu_units = [v for v in per_row_h if len(v) >= 2]; hlo, hhi = alpha_ci(hu_units, "nominal")
    print(f"utility: Krippendorff alpha (ordinal) = {krippendorff_alpha(units):.3f} [95% bootstrap {lo:.3f}, {hi:.3f}] | pairwise exact = {exact:.3f} | pairwise within one level = {within:.3f}")
    print(f"hedged:  Krippendorff alpha (nominal) = {krippendorff_alpha(hu_units, 'nominal'):.3f} [{hlo:.3f}, {hhi:.3f}]")
    strata = [("type", t, master.index[master.answer_type == t]) for t in master.answer_type.unique()]
    strata += [("family", f, master.index[master.task_family == f]) for f in master.task_family.unique()]
    if not a.pilot: strata += [("dataset", d, master.index[master._dataset == d]) for d in sorted(master._dataset.unique())]
    summary = []
    for kind, name, ids in strata:
        uu = [per_row[r] for r in ids if r in per_row.index and len(per_row[r]) >= 2]
        pp = [(x, y) for v in uu for x, y in itertools.combinations(v, 2)]
        if uu:
            al = krippendorff_alpha(uu); l2, h2 = alpha_ci(uu, B=200)
            summary.append({"stratum": kind, "name": name if kind != "family" else name.split(" (")[0], "rows": len(uu), "alpha": al, "alpha_lo": l2, "alpha_hi": h2, "exact": np.mean([x == y for x, y in pp])})
    sm = pd.DataFrame(summary)
    print(sm[sm.stratum != "dataset"].round(3).to_string(index=False))
    if (sm.stratum == "dataset").any():
        sm.to_csv(LAB / "agreement_by_stratum.csv", index=False); print(f"per-dataset agreement -> {(LAB / 'agreement_by_stratum.csv').relative_to(ROOT)}")
    # per labeller: mean absolute gap to the other labels on the rows they share (outlier check)
    print("per labeller (rows, mean label, mean |gap| to the others' mean on shared rows; a gap far above the rest flags drift):")
    others_mean = {}
    for L in sorted(got.labeller.unique()):
        mine = got[got.labeller == L]; gaps = []
        for _, r in mine.iterrows():
            oth = got[(got.row_id == r.row_id) & (got.labeller != L)].utility.values
            if len(oth): gaps.append(abs(r.utility - oth.mean()))
        print(f"  {L}: n={len(mine):3d} mean={mine.utility.mean():.3f} gap={np.mean(gaps) if gaps else float('nan'):.3f}")
    print("confusion over all label pairs (rows = first label, cols = second; symmetric):")
    print(pd.crosstab(pd.Series([x for x, _ in pairs] + [y for _, y in pairs], name="a"), pd.Series([y for _, y in pairs] + [x for x, _ in pairs], name="b")))

    # adjudication queue: labels span more than one level, hedged votes tie, or a label is missing
    span = per_row.apply(lambda v: max(v) - min(v)).reindex(master.index)
    hed_tie = per_row_h.apply(lambda v: len(v) >= 2 and sum(v) * 2 == len(v)).reindex(master.index).fillna(False)
    q_ids = [r for r in master.index if (n_got[r] < n_exp[r]) or (pd.notna(span[r]) and span[r] > 0.25) or hed_tie[r]]
    queue = master.loc[q_ids, ["task_family", "dataset_description", "answer_type", "question", "gold_answer", "accepted_alternatives", "gold_is_a_list", "model_final_answer", "model_full_reply"]].copy()
    def lab_str(rid):
        parts = []
        for r in long[long.row_id == rid].itertuples():
            u = "" if pd.isna(r.utility) else f"{r.utility:g}"; h = "" if pd.isna(r.hedged) else str(int(r.hedged))
            parts.append(f"{r.labeller}={u}/{h}" + (f" ({r.note})" if isinstance(r.note, str) and r.note.strip() else ""))
        return "; ".join(parts)
    queue["labels (labeller=utility/hedged (note))"] = [lab_str(r) for r in q_ids]; queue["utility"] = ""; queue["hedged"] = ""
    qp = LAB / ("pilot_adjudication_queue.csv" if a.pilot else "adjudication_queue.csv"); queue.to_csv(qp)
    print(f"\nadjudication queue: {len(queue)} rows -> {qp.relative_to(ROOT)} (fill utility and hedged there, or in adjudicated.csv with columns row_id, utility, hedged)")
    adj_p = LAB / "adjudicated.csv"
    if a.pilot or not adj_p.exists():
        if not a.pilot: print("no adjudicated.csv yet: resolve the queue, then re-run to merge")
        return
    adj = pd.read_csv(adj_p).set_index("row_id")
    rows = []
    for rid, r in master.iterrows():
        v = per_row.get(rid, []); hv = per_row_h.get(rid, [])
        if rid in adj.index: fu, fh, src = float(adj.loc[rid, "utility"]), float(adj.loc[rid, "hedged"]), True
        elif len(v) >= 1 and (len(v) == 1 or max(v) - min(v) <= 0.25) and n_got[rid] >= n_exp[rid]:
            fu, src = float(np.mean(v)), False; fh = float(round(np.mean(hv))) if hv and sum(hv) * 2 != len(hv) else (float(hv[0]) if len(hv) == 1 else np.nan)
        else: continue  # queued but not yet adjudicated
        rows.append({"dataset": r._dataset, "uid": r._uid, "model": r._model, "utility": fu, "hedged": fh, "label": float(np.round(fu * 2) / 2),
                     "n_labels": len(v), "labellers": "".join(got[got.row_id == rid].labeller), "adjudicated": src,
                     "utility_min": min(v) if v else np.nan, "utility_max": max(v) if v else np.nan, "judge_v1": r._v1, "judge_em": r._em, "row_id": rid})
    out = pd.DataFrame(rows); out.to_csv(LAB / "human_labels.csv", index=False)
    print(f"wrote human_labels.csv with {len(out)} rows of {len(master)} (label = utility rounded to the v5 selector's {{0, 0.5, 1}} scale)")
    hu = out.utility.values
    print("judge vs human: Spearman rho v1 = %.3f, exact match = %.3f | AUC(v1) = %.3f, AUC(exact match) = %.3f (correct = human 1.0, wrong = human 0.0)" % (
        spearmanr(out.judge_v1, hu).correlation, spearmanr(out.judge_em, hu).correlation, auc(out.judge_v1, hu == 1.0), auc(out.judge_em, hu == 1.0)))
    human_correctness(out)
    print("next: bash paper/scripts/rebuild_all.sh --paper  (the overleaf package adds the real-label correctness table); optionally, in v6, "
          "v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv")


def human_correctness(lab: pd.DataFrame):
    """Every v2 leaderboard rule scored on the labelled rows, judged against the human utility."""
    rules = json.load(open(OUT_V2 / "leaderboards" / "summary.json"))
    comp = pd.read_csv(OUT_V2 / "components_v1.csv").set_index(["model", "dataset", "uid"])
    comp = comp.loc[list(zip(lab.model, lab.dataset, lab.uid))]
    hu, hh = lab.utility.values, lab.hedged.fillna(0).values.astype(float)
    human_rank = lab.groupby("model").utility.mean().rank(ascending=False)
    rows = []
    for name, r in rules.items():
        w = r.get("weights")
        score = comp.em.values if not w else sum(w[k] * comp[k].values for k in w)
        rk = pd.Series(score, index=lab.model.values).groupby(level=0).mean().rank(ascending=False)
        rows.append({"rule": name, "weights": "exact match" if not w else " ".join(f"{k} {v:.2f}" for k, v in w.items() if v),
                     "n": len(lab), "rho_human": spearmanr(score, hu).correlation, "auc_correct_vs_wrong": auc(score, hu == 1.0),
                     "mean_score_on_wrong": float(np.mean(score[hu == 0.0])) if (hu == 0.0).any() else float("nan"),
                     "mean_score_on_correct": float(np.mean(score[hu == 1.0])) if (hu == 1.0).any() else float("nan"),
                     "hedge_gap": float(np.mean(score[hh == 1]) - np.mean(score[hh == 0])) if (hh == 1).any() and (hh == 0).any() else float("nan"),
                     "model_rank_rho_vs_human": spearmanr(rk.reindex(human_rank.index), human_rank).correlation})
    hc = pd.DataFrame(rows); hc.to_csv(LAB / "human_correctness.csv", index=False)
    json.dump({"n_labelled": int(len(lab)), "n_human_correct": int((hu == 1.0).sum()), "n_human_wrong": int((hu == 0.0).sum()), "n_hedged": int(hh.sum()),
               "labels_per_row_mean": float(lab.n_labels.mean()), "n_adjudicated": int(lab.adjudicated.sum()),
               "human_model_ranking": {m: int(v) for m, v in human_rank.sort_values().items()}, "rules": hc.set_index("rule").to_dict("index")},
              open(LAB / "human_correctness.json", "w"), indent=2)
    print("\njudge rules vs human labels (data/labels/human_correctness.csv):")
    print(hc[["rule", "rho_human", "auc_correct_vs_wrong", "mean_score_on_wrong", "hedge_gap", "model_rank_rho_vs_human"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
