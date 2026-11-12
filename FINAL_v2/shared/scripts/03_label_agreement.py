#!/usr/bin/env python
"""Agreement, coverage, adjudication queue and aggregation for the human labels.  Any number of graders, any number of ratings per answer.

    uv run python shared/scripts/03_label_agreement.py --check all      # validate every returned file (or --check <grader code>)
    uv run python shared/scripts/03_label_agreement.py --pilot          # the calibration round (everyone rates the same 30 answers)
    uv run python shared/scripts/03_label_agreement.py                  # main sheet: agreement, coverage, queue, human labels
    uv run python shared/scripts/03_label_agreement.py --aggregate median --min-labels 3 --on-disagreement aggregate --exclude g03

Graders are not assigned letters or rows.  A grader is identified by their email address, which 05_forms_to_returned.py replaces by a
code (g01, g02, ...); the returned files are data/labels/returned/03_main_<code>.xlsx or .csv (pilot: 02_pilot_<code>), and the
graders are whoever has a file there.  Only `row_id`, `rating`, `hedged`, `note` are read.
`rating` is the grader's 1-7 point and is converted here to a utility on the 0-1 line, (rating - 1) / 6.

Reports: ratings per answer and per grader; Krippendorff's alpha (ordinal, any number of coders, missing values allowed) on the rating
and alpha (nominal) on `hedged`, each with a bootstrap interval, overall and per answer type / task family / dataset
(agreement_by_stratum.csv); pairwise exact and within-one-rating agreement; per grader the mean gap to the others (drift check);
coverage.csv: per block, how many ratings its answers have and how many more graders it needs to reach the target.

Aggregation (config/labelling.toml, overridable by flags): method mean | median | mode | trimmed; min_labels; queue_span;
on_disagreement adjudicate | aggregate; hedged majority | any; exclude.  Wide disagreements (ratings more than queue_span points apart,
or a tie on hedged) are written to adjudication_queue.csv; under "adjudicate" they wait for data/labels/adjudicated.csv
(row_id, rating, hedged).  Every run writes data/labels/human_labels.csv with the answers resolved so far (dataset, uid, model, utility,
rating, hedged, label, n_ratings, graders, adjudicated, aggregation, utility_mean / _median / _mode, ...) and
human_correctness.{csv,json}: every v2 leaderboard rule scored on those answers against the human utility.
"""
from __future__ import annotations
import argparse, itertools, json, re, tomllib
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))
from label_scale import LEVELS, STEP, to_utility, to_rating  # graders record a rating 1..7; utility = (rating - 1) / 6

ROOT = Path(__file__).resolve().parents[2]; LAB = ROOT / "data" / "labels"; RET = LAB / "returned"; OUT_V2 = ROOT / "v2_gridsearch" / "output"
CONFIG = ROOT / "config" / "labelling.toml"  # aggregation settings; command-line flags override it
EPS = 1e-9
CORRECT, WRONG = 0.8, 0.2  # final (mean) utility counted as human-correct / human-wrong for AUC and the wrong-answer mean


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


def auc2(scores, human):
    """AUC of the score for human-correct (>= CORRECT) against human-wrong (<= WRONG) answers; answers in between are left out."""
    h = np.asarray(human, float); keep = (h >= CORRECT) | (h <= WRONG)
    return auc(np.asarray(scores, float)[keep], h[keep] >= CORRECT)


def auc(scores, correct):
    s, c = np.asarray(scores, float), np.asarray(correct, bool)
    if c.sum() == 0 or (~c).sum() == 0: return float("nan")
    pos, neg = s[c], s[~c]
    return (np.sum(pos[:, None] > neg[None, :]) + 0.5 * np.sum(pos[:, None] == neg[None, :])) / (len(pos) * len(neg))


# ---------------------------------------------------------------- input
def norm_id(x) -> str:
    """A grader code as used in file names and tables (g01, ...): lower case, letters and digits only."""
    return re.sub(r"[^a-z0-9]+", "", str(x).strip().lower())


def returned(pilot: bool) -> dict[str, Path]:
    """grader code -> returned file.  Codes are read from the file names: 03_main_<code>.xlsx / .csv (pilot: 02_pilot_<code>)."""
    pre = "02_pilot_" if pilot else "03_main_"; out = {}
    for p in sorted(RET.glob(pre + "*")):
        if p.suffix.lower() not in (".xlsx", ".csv") or p.name.startswith("~$"): continue
        gid = norm_id(p.stem[len(pre):])
        if gid and not (gid in out and out[gid].suffix.lower() == ".xlsx"): out[gid] = p
    return out


def load_sheet(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=0, dtype=str) if path.suffix.lower() == ".xlsx" else pd.read_csv(path, dtype=str)
    if "row_id" not in df.columns: raise SystemExit(f"{path.name}: no row_id column (wrong file?)")
    return df.set_index("row_id")


def num(series):
    """hedged: 0 / 1, also accepted as '0 No' / '1 Yes' / 'No' / 'Yes'."""
    t = series.astype(str).str.strip().str.lower().replace({"no": "0", "yes": "1"})
    return pd.to_numeric(t.str.extract(r"^([01])(?:\.0)?(?:\D|$)")[0], errors="coerce")


def util(series):
    """recorded rating ('6', '6 Correct, cosmetic defect', 6.0) -> utility (rating - 1) / 6; blank / not a whole number 1..7 -> nan."""
    return series.map(to_utility).astype(float)


def blank(col):
    return col.astype(str).str.strip().replace({"nan": "", "None": ""})


def check_one(S: pd.DataFrame, master: pd.DataFrame, gid: str, pilot: bool) -> int:
    """Validate one returned sheet.  Nobody is assigned rows, so a grader may have rated any part of the main sheet; what is checked:
    every row of the sheet still present, columns and read-only cells untouched, every rating a whole number 1..7, hedged 0/1, no
    half-filled row (rating without hedged or the reverse); in the pilot, every row rated.  Returns the number of problems."""
    probs = []
    unknown = [r for r in S.index if r not in master.index]
    if unknown: probs.append(f"{len(unknown)} unknown row ids: {unknown[:10]}")
    if len(S) != len(master): probs.append(f"row count changed: sheet has {len(S)} rows, expected {len(master)} (rows deleted or added?)")
    expected = [c for c in master.columns if not c.startswith("_")]
    if list(S.columns) != expected: probs.append(f"columns changed: expected {expected}, got {list(S.columns)}")
    full = S.reindex(master.index); u, h = blank(full.rating), blank(full.hedged); su, sh = util(u), num(h)
    wu = [(r, v) for r, v in u.items() if v and np.isnan(su[r])]; wh = [(r, v) for r, v in h.items() if v and np.isnan(sh[r])]
    if wu: probs.append(f"rating is not a whole number from 1 to 7 on {len(wu)} rows: {wu[:10]}")
    if wh: probs.append(f"hedged is not 0 or 1 on {len(wh)} rows: {wh[:10]}")
    half_u = [r for r in master.index if u[r] == "" and h[r] != ""]; half_h = [r for r in master.index if u[r] != "" and h[r] == ""]
    if half_u: probs.append(f"hedged filled but rating blank on {len(half_u)} rows: {half_u[:15]}")
    if half_h: probs.append(f"rating filled but hedged blank on {len(half_h)} rows: {half_h[:15]}")
    rated = [r for r in master.index if u[r] != ""]
    if pilot and len(rated) < len(master): probs.append(f"pilot: {len(master) - len(rated)} rows not rated (everyone rates the whole pilot)")
    if not rated: probs.append("no rating in this file")
    ro = [c for c in expected if c not in ("rating", "hedged", "note") and c in full.columns]
    norm = lambda col: col.fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip().str[:1500]  # spreadsheets alter line ends and very long cells
    changed = [c for c in ro if not (norm(full[c]).values == norm(master[c]).values).all()]
    if changed: probs.append(f"read-only columns edited: {changed}")
    note = ""
    if not pilot and "block" in master.columns and rated:
        per = pd.Series(1, index=rated).groupby(master.loc[rated, "block"].values).sum(); size = master.groupby("block").size()
        done = [int(b) for b in per.index if per[b] == size[b]]; part = {int(b): f"{int(per[b])}/{int(size[b])}" for b in per.index if per[b] < size[b]}
        note = f" | blocks complete: {done if done else 'none'}" + (f" | blocks partly rated: {part}" if part else "")
    print(f"grader {gid}: {len(rated)} of {len(master)} rows rated{note}; " + ("OK, nothing to fix" if not probs else f"{len(probs)} problem(s):"))
    for q in probs: print("  -", q)
    return len(probs)


# ---------------------------------------------------------------- aggregation
def aggregate(v: list[float], method: str) -> float:
    """One utility from several graders' utilities."""
    v = sorted(v)
    if method == "median": return float(np.median(v))
    if method == "trimmed": return float(np.mean(v[1:-1])) if len(v) >= 4 else float(np.mean(v))
    if method == "mode":
        counts = pd.Series(v).round(6).value_counts(); top = sorted(counts[counts == counts.max()].index); med = float(np.median(v))
        return float(min(top, key=lambda x: (abs(x - med), x)))
    return float(np.mean(v))


def settings(a) -> dict:
    cfg = {"method": "mean", "min_labels": 2, "queue_span": 2, "on_disagreement": "adjudicate", "hedged": "majority", "exclude": [], "labels_per_answer": 3}
    if CONFIG.exists():
        t = tomllib.load(open(CONFIG, "rb")); cfg.update(t.get("aggregation", {})); cfg["labels_per_answer"] = t.get("targets", {}).get("labels_per_answer", 3)
    for k, v in [("method", a.aggregate), ("min_labels", a.min_labels), ("queue_span", a.queue_span), ("on_disagreement", a.on_disagreement)]:
        if v is not None: cfg[k] = v
    cfg["exclude"] = sorted({norm_id(x) for x in list(cfg["exclude"]) + (a.exclude or [])})
    if cfg["method"] not in ("mean", "median", "mode", "trimmed"): raise SystemExit(f"unknown aggregation method {cfg['method']!r}")
    return cfg


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pilot", action="store_true"); ap.add_argument("--check", metavar="GRADER", help="validate one returned file; 'all' for every returned file")
    ap.add_argument("--aggregate", choices=["mean", "median", "mode", "trimmed"], help="how several ratings become one label (default: config/labelling.toml)")
    ap.add_argument("--min-labels", type=int, help="ratings an answer needs to get a human label"); ap.add_argument("--queue-span", type=int, help="ratings spread over more than this many points = wide disagreement")
    ap.add_argument("--on-disagreement", choices=["adjudicate", "aggregate"]); ap.add_argument("--exclude", action="append", metavar="GRADER", help="leave this grader out (repeatable)")
    a = ap.parse_args(); cfg = settings(a)
    master = pd.read_csv(LAB / ("pilot_master.csv" if a.pilot else "sample_master.csv")).set_index("row_id")
    files = returned(a.pilot)
    if not files: raise SystemExit(f"no returned files in {RET.relative_to(ROOT)} (expected {'02_pilot' if a.pilot else '03_main'}_<code>.xlsx or .csv; run 05_forms_to_returned.py first)")
    if a.check:
        ids = sorted(files) if a.check == "all" else [norm_id(a.check)]
        missing = [g for g in ids if g not in files]
        if missing: raise SystemExit(f"no returned file for grader {missing[0]}; found: {sorted(files)}")
        return sum(check_one(load_sheet(files[g]), master, g, a.pilot) for g in ids)

    # long table: one line per (row, grader) rating
    recs = []; graders = [g for g in sorted(files) if g not in cfg["exclude"]]
    if cfg["exclude"]: print(f"excluded graders: {cfg['exclude']}")
    for g in graders:
        S = load_sheet(files[g]).reindex(master.index); u, h = util(S.rating), num(S.hedged)
        off = [(rid, v) for rid, v in S.rating.items() if str(v).strip() not in ("", "nan", "None") and np.isnan(u[rid])]
        if off: print(f"  grader {g}: {len(off)} ratings off the scale, treated as blank: {off[:8]}")
        for rid in master.index:
            if pd.notna(u[rid]): recs.append({"row_id": rid, "grader": g, "utility": u[rid], "hedged": h[rid], "note": S.loc[rid, "note"] if "note" in S.columns else ""})
    if not recs: raise SystemExit("no ratings found in the returned files")
    got = pd.DataFrame(recs)
    per_row = got.groupby("row_id").utility.apply(list).reindex(master.index).apply(lambda v: v if isinstance(v, list) else [])
    per_row_h = got[got.hedged.notna()].groupby("row_id").hedged.apply(list).reindex(master.index).apply(lambda v: v if isinstance(v, list) else [])
    n_lab = per_row.apply(len); per_grader = got.groupby("grader").size()
    print(f"\ngraders: {len(per_grader)} " + ", ".join(f"{g} ({int(n)})" for g, n in per_grader.items()))
    print(f"answers: {len(master)} | ratings: {len(got)} | ratings per answer: min {n_lab.min()}, median {int(n_lab.median())}, max {n_lab.max()} | "
          f"answers with 0 / 1 / 2 / 3+ ratings: {(n_lab == 0).sum()} / {(n_lab == 1).sum()} / {(n_lab == 2).sum()} / {(n_lab >= 3).sum()}")
    units = [v for v in per_row if len(v) >= 2]
    if not units: print("no answer has two ratings yet: agreement cannot be computed"); 
    pairs = [(x, y) for v in units for x, y in itertools.combinations(v, 2)]
    if units:
        exact = np.mean([x == y for x, y in pairs]); within = np.mean([abs(x - y) <= STEP + EPS for x, y in pairs])
        lo, hi = alpha_ci(units); hu_units = [v for v in per_row_h if len(v) >= 2]; hlo, hhi = alpha_ci(hu_units, "nominal")
        print(f"rating: Krippendorff alpha (ordinal) = {krippendorff_alpha(units):.3f} [95% bootstrap {lo:.3f}, {hi:.3f}] | pairwise exact = {exact:.3f} | pairwise within one rating = {within:.3f}")
        print(f"hedged:  Krippendorff alpha (nominal) = {krippendorff_alpha(hu_units, 'nominal'):.3f} [{hlo:.3f}, {hhi:.3f}]")
        strata = [("type", t, master.index[master.answer_type == t]) for t in master.answer_type.unique()]
        strata += [("family", f, master.index[master.task_family == f]) for f in master.task_family.unique()]
        if not a.pilot: strata += [("dataset", d, master.index[master._dataset == d]) for d in sorted(master._dataset.unique())]
        summary = []
        for kind, name, ids in strata:
            uu = [per_row[r] for r in ids if len(per_row[r]) >= 2]
            pp = [(x, y) for v in uu for x, y in itertools.combinations(v, 2)]
            if uu:
                al = krippendorff_alpha(uu); l2, h2 = alpha_ci(uu, B=200)
                summary.append({"stratum": kind, "name": name if kind != "family" else name.split(" (")[0], "rows": len(uu), "alpha": al, "alpha_lo": l2, "alpha_hi": h2, "exact": np.mean([x == y for x, y in pp])})
        sm = pd.DataFrame(summary)
        print(sm[sm.stratum != "dataset"].round(3).to_string(index=False))
        if (sm.stratum == "dataset").any():
            sm.to_csv(LAB / "agreement_by_stratum.csv", index=False); print(f"per-dataset agreement -> {(LAB / 'agreement_by_stratum.csv').relative_to(ROOT)}")
        # per grader: mean absolute gap to the other ratings on the rows they share (outlier check)
        print("per grader (answers rated, mean utility, mean |gap| in utility to the others' mean on shared answers; a gap far above the rest flags drift):")
        row_sum = got.groupby("row_id").utility.sum(); row_n = got.groupby("row_id").utility.size()
        for g in sorted(per_grader.index):
            mine = got[got.grader == g].set_index("row_id").utility; n_oth = row_n[mine.index] - 1; shared = n_oth > 0
            gap = (mine[shared] - (row_sum[mine.index][shared] - mine[shared]) / n_oth[shared]).abs().mean() if shared.any() else float("nan")
            print(f"  {g}: n={len(mine):4d} mean={mine.mean():.3f} gap={gap:.3f}")

    # coverage: which blocks still need graders
    target = cfg["labels_per_answer"]
    if not a.pilot and "block" in master.columns:
        cov = pd.DataFrame({"block": master.block, "n": n_lab}).groupby("block").n.agg(answers="size", min_ratings="min", median_ratings="median").reset_index()
        cov["graders"] = [", ".join(sorted(got[got.row_id.isin(master.index[master.block == b])].grader.unique())) for b in cov.block]
        cov["below_min"] = [int((n_lab[master.block == b] < cfg["min_labels"]).sum()) for b in cov.block]; cov["more_graders_for_target"] = (target - cov.min_ratings).clip(lower=0)
        cov.to_csv(LAB / "coverage.csv", index=False); need = cov[cov.more_graders_for_target > 0]
        print(f"\ncoverage -> {(LAB / 'coverage.csv').relative_to(ROOT)}: {len(cov) - len(need)} of {len(cov)} blocks have {target}+ ratings on every answer"
              + (f"; blocks needing graders (block: how many more): {dict(zip(need.block.astype(int), need.more_graders_for_target.astype(int)))}" if len(need) else ""))

    # wide disagreements: ratings spread over more than queue_span points, or a tie on hedged
    span = per_row.apply(lambda v: (max(v) - min(v)) if len(v) >= 2 else 0.0)
    hed_tie = per_row_h.apply(lambda v: len(v) >= 2 and sum(v) * 2 == len(v)) if cfg["hedged"] == "majority" else pd.Series(False, index=master.index)
    wide = (span > cfg["queue_span"] * STEP + EPS) | hed_tie
    q_ids = list(master.index[wide]) if cfg["on_disagreement"] == "adjudicate" or a.pilot else []
    queue = master.loc[q_ids, ["task_family", "dataset_description", "answer_type", "question", "gold_answer", "accepted_alternatives", "gold_is_a_list", "model_final_answer", "model_full_reply"]].copy()
    def lab_str(rid):
        parts = []
        for r in got[got.row_id == rid].itertuples():
            h = "" if pd.isna(r.hedged) else str(int(r.hedged))
            parts.append(f"{r.grader}={to_rating(r.utility)}/{h}" + (f" ({r.note})" if isinstance(r.note, str) and r.note.strip() else ""))
        return "; ".join(parts)
    queue["ratings (grader=rating/hedged (note))"] = [lab_str(r) for r in q_ids]; queue["rating"] = ""; queue["hedged"] = ""
    qp = LAB / ("pilot_adjudication_queue.csv" if a.pilot else "adjudication_queue.csv"); queue.to_csv(qp)
    print(f"\nwide disagreements (ratings more than {cfg['queue_span']} points apart, or a tie on hedged): {int(wide.sum())}"
          + (f" -> {qp.relative_to(ROOT)} (the adjudicator fills rating 1-7 and hedged there, or in adjudicated.csv with columns row_id, rating, hedged)" if q_ids else " (aggregated without adjudication)"))
    if a.pilot: return

    # merge: one human label per answer
    adj_p = LAB / "adjudicated.csv"; adj = pd.read_csv(adj_p, dtype=str).set_index("row_id") if adj_p.exists() else pd.DataFrame(columns=["rating", "hedged"])
    rows = []; waiting = under = 0
    for rid, r in master.iterrows():
        v, hv = per_row[rid], per_row_h[rid]; au = to_utility(adj.loc[rid, "rating"]) if rid in adj.index else float("nan")
        if au == au:
            fu, src = au, True; fh = float(num(pd.Series([adj.loc[rid, "hedged"]]))[0])
        elif len(v) < cfg["min_labels"]: under += 1; continue
        elif rid in q_ids: waiting += 1; continue
        else:
            fu, src = aggregate(v, cfg["method"]), False
            fh = (float(any(hv)) if cfg["hedged"] == "any" else float(sum(hv) * 2 > len(hv))) if hv else np.nan
        rows.append({"dataset": r._dataset, "uid": r._uid, "model": r._model, "utility": fu, "rating": 1 + 6 * fu, "hedged": fh, "label": float(np.round(fu * 2) / 2),
                     "n_ratings": len(v), "graders": "+".join(got[got.row_id == rid].grader), "adjudicated": src, "aggregation": "adjudicated" if src else cfg["method"],
                     "utility_mean": float(np.mean(v)) if v else np.nan, "utility_median": float(np.median(v)) if v else np.nan, "utility_mode": aggregate(v, "mode") if v else np.nan,
                     "utility_min": min(v) if v else np.nan, "utility_max": max(v) if v else np.nan, "judge_v1": r._v1, "judge_em": r._em, "row_id": rid})
    out = pd.DataFrame(rows)
    print(f"\naggregation: {cfg['method']} of the converted ratings, at least {cfg['min_labels']} ratings per answer, hedged by {cfg['hedged']}, wide disagreements: {cfg['on_disagreement']}")
    print(f"human labels: {len(out)} of {len(master)} answers | under-covered (fewer than {cfg['min_labels']} ratings): {under} | waiting for adjudication: {waiting} | adjudicated: {int(out.adjudicated.sum()) if len(out) else 0}")
    if not len(out): print("nothing to merge yet"); return
    out.to_csv(LAB / "human_labels.csv", index=False)
    print("wrote human_labels.csv (utility = aggregated (rating - 1) / 6; rating = the same on the 1-7 scale; label = utility rounded to the v5 selector's {0, 0.5, 1} scale; utility_mean / _median / _mode for comparison)")
    hu = out.utility.values
    if len(out) >= 10:
        print("judge vs human: Spearman rho v1 = %.3f, exact match = %.3f | AUC(v1) = %.3f, AUC(exact match) = %.3f (correct = human >= 0.8, wrong = human <= 0.2, rows in between left out of the AUC)" % (
            spearmanr(out.judge_v1, hu).correlation, spearmanr(out.judge_em, hu).correlation, auc2(out.judge_v1.values, hu), auc2(out.judge_em.values, hu)))
        human_correctness(out, cfg)
    if under or waiting: print("partial result: grade the under-covered blocks (coverage.csv) and resolve the adjudication queue, then re-run")
    else: print("complete. next: bash paper/scripts/rebuild_all.sh --paper  (the overleaf package adds the real-label correctness table); optionally, in v6, "
                "v5_metric_library/scripts/02_select_metrics.py --labels data/labels/human_labels.csv")


def human_correctness(lab: pd.DataFrame, cfg: dict):
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
                     "n": len(lab), "rho_human": spearmanr(score, hu).correlation, "auc_correct_vs_wrong": auc2(score, hu),
                     "mean_score_on_wrong": float(np.mean(score[hu <= WRONG])) if (hu <= WRONG).any() else float("nan"),
                     "mean_score_on_correct": float(np.mean(score[hu >= CORRECT])) if (hu >= CORRECT).any() else float("nan"),
                     "hedge_gap": float(np.mean(score[hh == 1]) - np.mean(score[hh == 0])) if (hh == 1).any() and (hh == 0).any() else float("nan"),
                     "model_rank_rho_vs_human": spearmanr(rk.reindex(human_rank.index), human_rank).correlation})
    hc = pd.DataFrame(rows); hc.to_csv(LAB / "human_correctness.csv", index=False)
    json.dump({"n_labelled": int(len(lab)), "n_human_correct": int((hu >= CORRECT).sum()), "n_human_wrong": int((hu <= WRONG).sum()), "scale": "rating 1-7, utility = (rating - 1) / 6", "correct_threshold": CORRECT, "wrong_threshold": WRONG, "n_hedged": int(hh.sum()),
               "ratings_per_answer_mean": float(lab.n_ratings.mean()), "n_adjudicated": int(lab.adjudicated.sum()), "aggregation": {k: cfg[k] for k in ("method", "min_labels", "queue_span", "on_disagreement", "hedged", "exclude")},
               "human_model_ranking": {m: int(v) for m, v in human_rank.sort_values().items()}, "rules": hc.set_index("rule").to_dict("index")},
              open(LAB / "human_correctness.json", "w"), indent=2)
    print("\njudge rules vs human labels (data/labels/human_correctness.csv):")
    print(hc[["rule", "rho_human", "auc_correct_vs_wrong", "mean_score_on_wrong", "hedge_gap", "model_rank_rho_vs_human"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
