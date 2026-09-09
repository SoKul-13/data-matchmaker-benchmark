"""
Weighted composite metric with per-answer-type weight vectors and a hedge gate.

    S(p, g) = [ sum_k w[type(g)]_k * m_k(p, g) ] * (1 - lambda[type(g)] * hedged(p))

w[t] lies on the probability simplex (K = 9 components); lambda[t] in [0, 1] is the
penalty applied when the prediction hedges between several candidate answers.

`PRESET_WEIGHTS` contains the baselines compared in the paper (lambda = 0).  Calibrated
weights are produced by scripts/05_calibrate_weights.py -> config/calibrated_weights.json.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np

from .answer_types import AnswerType, detect_answer_type
from .components import ALL_COLUMNS, COMPONENT_NAMES, HEDGE_COL, K, component_vector

TYPES = [t.value for t in AnswerType]


def _vec(d: Dict[str, float]) -> np.ndarray:
    v = np.array([float(d.get(n, 0.0)) for n in COMPONENT_NAMES])
    s = v.sum()
    return v / s if s > 0 else v


@dataclass
class WeightSet:
    """Per-type weight vectors (each sums to 1) and per-type hedge penalties."""
    weights: Dict[str, np.ndarray] = field(default_factory=dict)
    hedge_lambda: Dict[str, float] = field(default_factory=dict)
    name: str = "unnamed"
    meta: Dict = field(default_factory=dict)

    @classmethod
    def uniform_all(cls, d: Dict[str, float], name: str, lam: float = 0.0) -> "WeightSet":
        v = _vec(d)
        return cls({t: v.copy() for t in TYPES}, {t: lam for t in TYPES}, name)

    @classmethod
    def from_dict(cls, obj: Dict) -> "WeightSet":
        w = {t: _vec(obj["weights"][t]) for t in obj["weights"]}
        lam = {t: float(obj.get("hedge_lambda", {}).get(t, 0.0)) for t in w}
        return cls(w, lam, obj.get("name", "loaded"), obj.get("meta", {}))

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "components": COMPONENT_NAMES,
            "weights": {t: {n: float(x) for n, x in zip(COMPONENT_NAMES, v)} for t, v in self.weights.items()},
            "hedge_lambda": {t: float(self.hedge_lambda.get(t, 0.0)) for t in self.weights},
            "meta": self.meta,
        }

    @classmethod
    def load(cls, path: str | Path) -> "WeightSet":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def get(self, atype: AnswerType | str) -> np.ndarray:
        t = atype.value if isinstance(atype, AnswerType) else atype
        return self.weights.get(t, np.ones(K) / K)

    def lam(self, atype: AnswerType | str) -> float:
        t = atype.value if isinstance(atype, AnswerType) else atype
        return float(self.hedge_lambda.get(t, 0.0))

    def param_matrix(self) -> np.ndarray:
        """(n_types, K+1) matrix: weights followed by lambda, in TYPES order."""
        return np.stack([np.concatenate([self.get(t), [self.lam(t)]]) for t in TYPES])


# ----------------------------------------------------------------------------
# Baseline presets (same vector for every type, no hedge penalty).  "original_rcustom"
# reproduces the v1 hand-set rubric R_custom = .35 F1 + .35 exp(-2.5 MRE) + .15 P + .15 R.
# ----------------------------------------------------------------------------
PRESET_WEIGHTS: Dict[str, WeightSet] = {
    "em_only": WeightSet.uniform_all({"em": 1.0}, "em_only"),
    "f1_only": WeightSet.uniform_all({"tok_f1": 1.0}, "f1_only"),
    "num_tol_only": WeightSet.uniform_all({"num_tol": 1.0}, "num_tol_only"),
    "original_rcustom": WeightSet.uniform_all(
        {"tok_f1": 0.35, "num_decay": 0.35, "tok_prec": 0.15, "tok_rec": 0.15}, "original_rcustom"),
    "uniform": WeightSet.uniform_all({n: 1.0 for n in COMPONENT_NAMES}, "uniform"),
}


def composite_from_vector(vec: np.ndarray, w: np.ndarray, lam: float) -> float:
    """vec = component_vector() output (K+1), w (K,) simplex weights, lam hedge penalty."""
    hedged = 1.0 - float(vec[HEDGE_COL])
    return float(np.dot(w, vec[:K]) * (1.0 - lam * hedged))


class CompositeScorer:
    """Score (prediction, gold) pairs with a WeightSet."""

    def __init__(self, weights: WeightSet):
        self.ws = weights

    def score(self, pred: Optional[str], gold: str, aliases: Optional[Iterable[str]] = None,
              atype: Optional[AnswerType] = None, *, gold_list: Optional[List[str]] = None,
              return_components: bool = False):
        if atype is None:
            atype = detect_answer_type(gold, aliases, gold_list=gold_list)
        m = component_vector(pred, gold, aliases, atype, gold_list=gold_list)
        s = composite_from_vector(m, self.ws.get(atype), self.ws.lam(atype))
        if return_components:
            return s, {n: float(x) for n, x in zip(ALL_COLUMNS, m)}
        return s

    @staticmethod
    def score_matrix(M: np.ndarray, type_idx: np.ndarray, P: np.ndarray) -> np.ndarray:
        """Vectorised: M (n, K+1) component matrix incl. hedge column, type_idx (n,),
        P (n_types, K+1) parameter matrix (weights + lambda) -> (n,) composite scores."""
        W = P[type_idx, :K]
        lam = P[type_idx, K]
        base = np.einsum("nk,nk->n", M[:, :K], W)
        return base * (1.0 - lam * (1.0 - M[:, HEDGE_COL]))
