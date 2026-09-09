import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from anchors.ladder import OPS_BY_TYPE, UTILITY, Item, apply, generate  # noqa: E402
from calibration.grid import anchor_terms, objective, simplex_grid  # noqa: E402
from calibration.select import dedupe, fit_nnls, forward_select  # noqa: E402
from metrics.answer_types import AnswerType  # noqa: E402
from metrics.library import FAMILIES, METRIC_NAMES, compute_all  # noqa: E402


def test_library_has_100_named_metrics():
    assert len(METRIC_NAMES) == 100 and len(set(METRIC_NAMES)) == 100
    assert sum(len(v) for v in FAMILIES.values()) == 100


def test_all_metrics_bounded_and_correct_answer_scores_high():
    v = compute_all("FINAL ANSWER: 13.2%", "13.2%", ["0.13202"])
    assert v.shape == (100,) and v.min() >= 0 and v.max() <= 1
    for n in ["em_norm", "num_tol_1", "num_decay_2p5", "tok_f1", "rouge_l", "hedge_free", "native_style_metric"]:
        assert v[METRIC_NAMES.index(n)] == 1.0, n


def test_wrong_answer_scores_low_on_core_metrics():
    v = compute_all("FINAL ANSWER: 42", "13.2%", ["0.13202"])
    for n in ["em_norm", "num_tol_1", "tok_f1"]:
        assert v[METRIC_NAMES.index(n)] == 0.0, n


def test_list_gold_with_unit_alias():
    v = compute_all("$7,870 thousand | $12,129 thousand", "$7,870 | $12,129", ["$7,870 thousand | $12,129 thousand"], gold_list=["$7,870", "$12,129"])
    assert v[METRIC_NAMES.index("em_list_set")] == 1.0


def test_hedge_detected():
    assert compute_all("12 or 15", "12")[METRIC_NAMES.index("hedge_free")] == 0.0


def test_anchor_operators_have_utilities():
    for ops in OPS_BY_TYPE.values():
        assert all(o in UTILITY for o in ops)
    pool = [Item(f"n{i}", "d", str(100 + 7 * i), AnswerType.NUMERIC, []) for i in range(6)]
    rows = generate(pool, seed=1)
    assert len(rows) == 6 * len(OPS_BY_TYPE[AnswerType.NUMERIC])
    assert all(r["prediction"] for r in rows)


def test_identity_anchor_scores_one_on_native():
    it = Item("x", "d", "Italy", AnswerType.TEXT, [])
    assert compute_all(apply("identity", it, np.random.default_rng and __import__("random").Random(0), [it]), "Italy")[METRIC_NAMES.index("native_style_metric")] == 1.0


def test_simplex_grid_and_objective_shapes():
    W = simplex_grid(3, 0.25)
    assert np.allclose(W.sum(1), 1) and len(W) == 15
    rng = np.random.default_rng(0)
    u = rng.choice([0, 0.5, 1.0], 200); A = np.clip(u[:, None] + rng.normal(0, 0.1, (200, 3)), 0, 1)
    t = anchor_terms(A @ W.T, u, np.array(["a"] * 100 + ["b"] * 100), np.array(["op1", "op2"] * 100))
    t["tau_native"] = np.zeros(len(W))
    J = objective(t, {"rho": 0.35, "auc": 0.2, "consistency": 0.25, "native": 0.2})
    assert J.shape == (len(W),) and t["rho"].max() > 0.8 and t["auc"].max() > 0.9


def test_dedupe_and_selection():
    rng = np.random.default_rng(1)
    u = rng.random(300); X = np.stack([u, u * 0.99 + 0.001, rng.random(300), 1 - u], 1)
    keep, clusters = dedupe(X, ["a", "b", "noise", "neg"], 0.95)
    assert 0 in keep and 1 not in keep
    sel, trace = forward_select(X, u, np.array(["d1"] * 150 + ["d2"] * 150), keep, k_max=3)
    assert 0 in sel
    w = fit_nnls(X[:, sel], u)
    assert np.all(w >= 0) and abs(w.sum() - 1) < 1e-9
