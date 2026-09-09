#!/usr/bin/env python
"""
EXTENSION (not wired into the pipeline): KL and Jensen-Shannon divergence as calibration
objectives for cross-dataset score consistency.

Idea
----
The main pipeline (scripts/rs/) calibrates weights so that model RANKINGS agree across
datasets.  Rankings ignore the score scale: a metric can rank models identically on two
datasets while giving the same model 0.9 on one and 0.4 on the other.  Divergence measures
compare the whole DISTRIBUTION of item-level scores, so they can ask a stronger question:

    "Under weights w, does the score distribution a model produces on dataset A look like the
     score distribution it produces on dataset B (after accounting for difficulty)?"

Two ways to use divergences as an objective term:

  (1) Model-conditional matching.  For each model m and each pair of datasets (A, B), compute
      the histogram of item scores P_m,A and P_m,B and measure JS(P_m,A || P_m,B).  Average
      over models and pairs.  Low = the metric produces comparable score profiles across
      datasets for the same system.  Caveat: datasets genuinely differ in difficulty, so this
      term must be combined with a difficulty adjustment (histograms of dataset-centred scores)
      or it will just measure difficulty.

  (2) Anchor matching (what v2 does).  Instead of real models, use synthetic systems of KNOWN
      quality on every dataset (e.g. "answers 70% of items correctly, errors are near misses").
      Under a consistent metric the score distribution of such a system is the same on every
      dataset, so JS between datasets at matched quality is a clean consistency target with no
      difficulty confound.

KL vs JS
--------
  KL(P||Q) = sum_i P_i log(P_i / Q_i)  is asymmetric and infinite when Q has an empty bin
              that P fills; needs smoothing (add eps to every bin).  Good for "how surprising
              is A's distribution if I expected B's".
  JS(P,Q)  = 0.5 KL(P||M) + 0.5 KL(Q||M), M = (P+Q)/2.  Symmetric, bounded in [0, ln 2],
              always finite.  This is the natural choice for an objective term because it is
              bounded (so it can be mixed with tau terms) and symmetric (dataset order does not
              matter).  1-Wasserstein distance is a useful complement because it is sensitive
              to *location* shifts even when histograms do not overlap.

How it would enter the objective
--------------------------------
    J(w) = a1 * mean_d tau(ranking_d, pooled ranking)         (what scripts/rs uses)
         + a2 * (1 - mean_{m,(A,B)} JS(P_m,A, P_m,B) / ln 2)   (this file, variant 1)
  with the JS term computed on dataset-centred scores.  Because a binary metric (EM) gives a
  Bernoulli(p) histogram on every dataset, JS alone is minimised by binary indicators; the
  ranking term and (in v2) severity / native-fidelity terms are what prevent that collapse.

Running this file
-----------------
    uv run python extensions/divergence_extension.py
prints, for the calibrated weights found by the random search and for the EM-only baseline,
the dataset x dataset JS matrix (averaged over models), the per-model mean JS to other datasets,
and the symmetric KL and 1-Wasserstein equivalents.  It reads output/rs/components.npz and
output/rs/best_weights.json and writes nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from metrics import COMPONENT_NAMES, K, PRESET_WEIGHTS  # noqa: E402

NBINS, EPS = 10, 1e-3


def histogram(x: np.ndarray) -> np.ndarray:
    h, _ = np.histogram(np.clip(x, 0, 1), bins=NBINS, range=(0, 1))
    p = h.astype(float) + EPS
    return p / p.sum()


def kl(p, q):
    return float(np.sum(p * np.log(p / q)))


def js(p, q):
    m = 0.5 * (p + q)
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def sym_kl(p, q):
    return 0.5 * (kl(p, q) + kl(q, p))


def divergence_report(scores: pd.DataFrame, centre: bool = True):
    """scores: columns model, dataset, S (item level).  Returns dataset x dataset matrices
    (mean over models) for JS, symmetric KL and W1, plus per-model mean JS."""
    df = scores.copy()
    if centre:  # remove dataset difficulty: subtract the dataset's mean over all models
        df["S"] = df["S"] - df.groupby("dataset")["S"].transform("mean") + df["S"].mean()
    models, datasets = sorted(df.model.unique()), sorted(df.dataset.unique())
    D = len(datasets)
    JS, KLm, W1 = (np.zeros((D, D)) for _ in range(3))
    per_model = {}
    for m in models:
        sub = df[df.model == m]
        hists = {d: histogram(sub[sub.dataset == d].S.to_numpy()) for d in datasets}
        raw = {d: sub[sub.dataset == d].S.to_numpy() for d in datasets}
        vals = []
        for i, a in enumerate(datasets):
            for j, b in enumerate(datasets):
                if i < j:
                    v = js(hists[a], hists[b])
                    JS[i, j] += v / len(models); JS[j, i] = JS[i, j]
                    KLm[i, j] += sym_kl(hists[a], hists[b]) / len(models); KLm[j, i] = KLm[i, j]
                    W1[i, j] += wasserstein_distance(raw[a], raw[b]) / len(models); W1[j, i] = W1[i, j]
                    vals.append(v)
        per_model[m] = float(np.mean(vals))
    return (pd.DataFrame(JS, datasets, datasets), pd.DataFrame(KLm, datasets, datasets),
            pd.DataFrame(W1, datasets, datasets), pd.Series(per_model))


def main():
    z = np.load(ROOT / "output" / "rs" / "components.npz")
    M = z["M"][:, :K]
    idx = pd.read_csv(ROOT / "output" / "rs" / "index.csv")
    best = json.load(open(ROOT / "output" / "rs" / "best_weights.json"))
    w_best = np.array([best["weights"][n] for n in COMPONENT_NAMES])
    for name, w in [("random-search calibrated", w_best), ("EM only", PRESET_WEIGHTS["em_only"].get("numeric")),
                    ("v1 R_custom", PRESET_WEIGHTS["original_rcustom"].get("numeric"))]:
        JS, KLm, W1, pm = divergence_report(idx.assign(S=M @ w))
        iu = np.triu_indices(len(JS), 1)
        print(f"\n=== {name} ===  mean JS/ln2 = {JS.to_numpy()[iu].mean() / np.log(2):.3f} | mean symKL = {KLm.to_numpy()[iu].mean():.3f} | mean W1 = {W1.to_numpy()[iu].mean():.3f}")
        print("dataset x dataset JS (mean over models, difficulty-centred):")
        print(JS.round(3).to_string())
        print("per-model mean JS to other datasets:", pm.round(3).to_dict())
    print("\nNote: a binary metric (EM) can obtain LOW divergence for the wrong reason (uniform failure). "
          "Use divergences together with a ranking or known-quality anchor term (see docstring).")


if __name__ == "__main__":
    main()
