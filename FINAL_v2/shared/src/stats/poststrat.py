"""
Post-stratification: estimate what a model would score on a dataset's OFFICIAL split from the answers it gave on our stratified pool.

The pool draws strata equally (so calibration sees every kind of item); the official split has its own stratum proportions.
Weight every answered item by  w_i = official share of its stratum / share of its stratum among the answered items,  normalised
to mean 1.  The weighted mean of a per-item score is an unbiased estimate of the official-split mean (Horvitz–Thompson); the
interval comes from a weighted item bootstrap.  For boolean matching datasets the stratum is the gold label, so the same weights
also give precision / recall / F1 on the positive class at the official class ratio (what the matching literature reports).

  stratum_of(name, item, key)                 the stratum label used both in the census and here
  load_strata(path)                           data/pool/_official_strata.json
  weights_for(name, items_by_uid, uids, strata)  weight per uid (in the given uid order) and the gold labels
  weighted_estimates(items, weights, labels, datasets, models, n_boot)  per-dataset weighted mean + CI (+ P/R/F1 for boolean sets)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd


def stratum_of(name: str, item: dict, key: Optional[str]) -> str:
    """boolean matching sets: gold label (crossed with the stratify key when there is one, e.g. task|yes); keyed sets: the key; else answer type"""
    g = str(item.get("ground_truth", "")).strip().lower(); is_bool = item.get("answer_type") == "boolean" and g in ("yes", "no", "true", "false", "1", "0")
    label = ("yes" if g in ("yes", "true", "1") else "no") if is_bool else None
    kv = str(item.get(key)) if key and item.get(key) not in (None, "", "all") else None
    if is_bool and item.get("data_type") == "record_pair":
        return f"{kv}|{label}" if kv else label
    if kv:
        return kv
    return label if is_bool else str(item.get("answer_type", "text"))


def load_strata(path: Path) -> dict:
    return json.load(open(path)) if path.exists() else {}


def weights_for(name: str, items_by_uid: Dict[str, dict], uids: Sequence[str], strata: dict):
    """returns (weights aligned to uids, gold labels aligned to uids or None, info dict)"""
    info = strata.get(name); n = len(uids)
    labels = None
    if uids and all(items_by_uid[u].get("answer_type") == "boolean" for u in uids):
        labels = np.array([1.0 if stratum_of(name, items_by_uid[u], None) == "yes" else 0.0 for u in uids])
    if not info or not info.get("counts") or not info.get("comparable", True):
        return np.ones(n), labels, {"weighted": False, "reason": (info or {}).get("note", "no official census")}
    key = info.get("key"); off = info["counts"]; tot = sum(off.values())
    strat = [stratum_of(name, items_by_uid[u], key) for u in uids]
    samp = pd.Series(strat).value_counts().to_dict()
    w = np.array([(off.get(s, 0) / tot) / (samp[s] / n) if samp.get(s) and off.get(s) else 0.0 for s in strat], float)
    if w.sum() == 0:
        return np.ones(n), labels, {"weighted": False, "reason": "no stratum overlap with the census"}
    w = w * n / w.sum()
    missing = [s for s in off if s not in samp]
    return w, labels, {"weighted": True, "key": key, "official_n": tot, "strata_in_sample": len(samp), "strata_official": len(off),
                       "official_strata_absent_from_sample": missing, "max_weight": float(w.max()), "effective_n": float(w.sum() ** 2 / (w ** 2).sum())}


def _prf(correct: np.ndarray, labels: np.ndarray, w: np.ndarray):
    """boolean matching: correct (n,) 0/1 per item, labels (n,) gold 1 = match.  Predicted match = correct if gold match else incorrect."""
    pred_pos = np.where(labels == 1, correct, 1 - correct)
    tp = float((w * pred_pos * labels).sum()); fp = float((w * pred_pos * (1 - labels)).sum()); fn = float((w * (1 - pred_pos) * labels).sum())
    p = tp / (tp + fp) if tp + fp > 0 else 0.0; r = tp / (tp + fn) if tp + fn > 0 else 0.0
    return p, r, (2 * p * r / (p + r) if p + r > 0 else 0.0)


def weighted_estimates(items: List[np.ndarray], weights: List[np.ndarray], labels: List[Optional[np.ndarray]], datasets: Sequence[str], models: Sequence[str],
                       infos: List[dict], n_boot: int = 1000, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed); rows = []
    for j, d in enumerate(datasets):
        X, w, lab = items[j], weights[j], labels[j]; n = X.shape[0]
        for i, m in enumerate(models):
            x = X[:, i]; ok = ~np.isnan(x); xx, ww = x[ok], w[ok]
            est = float((ww * xx).sum() / ww.sum()); plain = float(xx.mean())
            boots = np.empty(n_boot)
            for b in range(n_boot):
                idx = rng.integers(0, len(xx), len(xx)); boots[b] = (ww[idx] * xx[idx]).sum() / ww[idx].sum()
            row = {"dataset": d, "model": m, "suite_mean": plain, "official_estimate": est, "official_lo95": float(np.percentile(boots, 2.5)), "official_hi95": float(np.percentile(boots, 97.5)),
                   "n_items": int(ok.sum()), "weighted": infos[j].get("weighted", False), "effective_n": infos[j].get("effective_n", float(ok.sum()))}
            if lab is not None:
                ll = lab[ok]; p, r, f = _prf(xx, ll, ww); p0, r0, f0 = _prf(xx, ll, np.ones_like(ww))
                fb = np.empty(n_boot)
                for b in range(n_boot):
                    idx = rng.integers(0, len(xx), len(xx)); fb[b] = _prf(xx[idx], ll[idx], ww[idx])[2]
                row.update({"suite_f1_pos": f0, "official_precision_pos": p, "official_recall_pos": r, "official_f1_pos": f, "official_f1_lo95": float(np.percentile(fb, 2.5)), "official_f1_hi95": float(np.percentile(fb, 97.5)),
                            "official_positive_share": float(infos[j].get("official_positive_share", np.nan))})
            rows.append(row)
    return pd.DataFrame(rows)
