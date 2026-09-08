"""Tests for the v2 random-search calibration and pooling helpers."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
spec = importlib.util.spec_from_file_location("rs02", ROOT / "scripts" / "rs" / "02_random_search.py")
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)
from metrics import K  # noqa: E402
from pooling.rank_aggregation import RULES, consensus_ranking  # noqa: E402


def test_grid_sampling_is_on_simplex_grid_and_distinct():
    W = rs.sample_grid_weights(100, K, 0.05, np.random.default_rng(0))
    assert W.shape == (100, K)
    assert np.allclose(W.sum(1), 1.0)
    assert np.allclose(W * 20, np.round(W * 20))
    assert len({tuple(np.round(w, 6)) for w in W}) == 100


def test_objective_perfect_agreement():
    rng = np.random.default_rng(1)
    models, datasets = [f"m{i}" for i in range(5)], [f"d{j}" for j in range(4)]
    rows = []
    for m_i, m in enumerate(models):
        for d in datasets:
            for u in range(20):
                rows.append({"model": m, "dataset": d, "uid": f"{d}_{u}", "S": 0.1 * m_i + rng.normal(0, 0.001)})
    piv = pd.DataFrame(rows).pivot_table(index="model", columns="dataset", values="S")
    ev = rs.evaluate(piv)
    assert ev["J_tau_to_pooled"] > 0.99 and ev["mean_pairwise_tau"] > 0.99


def test_rules_consistent_on_clear_order():
    S = np.array([[0.9, 0.85, 0.95], [0.6, 0.65, 0.55], [0.3, 0.2, 0.35]])
    for rule in RULES:
        assert list(consensus_ranking(S, rule)) == [1, 2, 3]
