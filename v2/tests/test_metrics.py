"""Unit tests for the v2 metric library (component metrics, typing, composite)."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from metrics import (ALL_COLUMNS, COMPONENT_NAMES, HEDGE_COL, K, AnswerType, CompositeScorer,  # noqa: E402
                     PRESET_WEIGHTS, WeightSet, component_dict, component_vector, detect_answer_type,
                     extract_final_answer, extract_numbers, normalize_boolean, normalize_text)


class TestNormalize:
    def test_numbers_canonical(self):
        assert normalize_text("$1,577.00 million") == "1577 million"
        assert normalize_text("(12.6)") == "-12.6"
        assert normalize_text("14.5%", keep_percent=True) == "14.5%"

    def test_articles_and_punct(self):
        assert normalize_text("The Answer, is: Italy!") == "answer is italy"

    def test_extract_numbers_scale_percent(self):
        nums = extract_numbers("revenue rose 14.5% to $1.2 billion in 2019")
        vals = [(n.value, n.is_percent, n.scale, n.is_year_like) for n in nums]
        assert vals[0] == (14.5, True, 1.0, False)
        assert vals[1] == (1.2, False, 1e9, False)
        assert vals[2] == (2019.0, False, 1.0, True)

    def test_final_answer_extraction(self):
        assert extract_final_answer("blah\n<FINAL_ANSWER> 42 </FINAL_ANSWER>") == "42"
        assert extract_final_answer("reasoning...\nFINAL ANSWER: 3 | 4") == "3 | 4"
        assert extract_final_answer("Based on the table, the answer is Italy.") == "Italy"
        assert extract_final_answer("") == ""


class TestTyping:
    @pytest.mark.parametrize("gold,expected", [
        ("2,602", AnswerType.NUMERIC), ("$1577.00", AnswerType.NUMERIC), ("-12.6 million", AnswerType.NUMERIC),
        ("1499.39%", AnswerType.NUMERIC), ("yes", AnswerType.BOOLEAN), ("Refuted", AnswerType.BOOLEAN),
        ("0", AnswerType.NUMERIC), ("Italy", AnswerType.TEXT), ("2 years", AnswerType.NUMERIC),
        ("In 2019, Shagun Sharma played in the roles as Pernia in Laal Ishq and Aarti", AnswerType.FREEFORM),
    ])
    def test_detect(self, gold, expected):
        assert detect_answer_type(gold) == expected

    def test_list_gold_is_text(self):
        assert detect_answer_type("a very long first item of the list | second", gold_list=["a very long first item of the list", "second"]) == AnswerType.TEXT

    def test_boolean_words(self):
        assert normalize_boolean("Yes, the statement is entailed.") == "yes"
        assert normalize_boolean("The claim is refuted") == "no"
        assert normalize_boolean("the correct row") is None


class TestComponents:
    def test_shape_and_names(self):
        v = component_vector("42", "42")
        assert v.shape == (K + 1,)
        assert ALL_COLUMNS[HEDGE_COL] == "hedge_free"
        assert len(COMPONENT_NAMES) == K == 9

    def test_exact(self):
        d = component_dict("<FINAL_ANSWER>2,602</FINAL_ANSWER>", "2,602")
        assert all(d[k] == 1.0 for k in ALL_COLUMNS)

    def test_percent_fraction_equivalence(self):
        d = component_dict("14.5%", "0.145")
        assert d["num_tol"] == 1.0 and d["num_decay"] > 0.99

    def test_alias_max(self):
        d = component_dict("14%", "0.14464", aliases=["14%"])
        assert d["em"] == 1.0

    def test_near_miss_decay(self):
        d = component_dict("about 1,600", "1577")
        assert d["num_tol"] == 0.0 and 0.9 < d["num_decay"] < 1.0

    def test_hedge_detected(self):
        assert component_dict("12 or 15", "12")["hedge_free"] == 0.0
        assert component_dict("Italy, France, Spain, Germany", "Italy")["hedge_free"] == 0.0
        assert component_dict("Italy", "Italy")["hedge_free"] == 1.0

    def test_list_gold_em(self):
        assert component_dict("France | Italy", "Italy | France", gold_list=["Italy", "France"])["em"] == 1.0
        assert component_dict("Italy", "Italy | France", gold_list=["Italy", "France"])["em"] == 0.0

    def test_boolean(self):
        d = component_dict("Yes, the statement is entailed.", "1", atype=AnswerType.BOOLEAN)
        assert d["em"] == 1.0
        assert component_dict("no", "yes", atype=AnswerType.BOOLEAN)["em"] == 0.0

    def test_empty_prediction(self):
        d = component_dict("", "18")
        assert all(d[k] == 0.0 for k in COMPONENT_NAMES)

    def test_bounds(self):
        rng = np.random.default_rng(0)
        for _ in range(50):
            a = " ".join(rng.choice(["alpha", "12", "beta", "3.5%", "or", "gamma"], size=rng.integers(1, 6)))
            b = " ".join(rng.choice(["alpha", "12", "beta", "3.5%", "gamma"], size=rng.integers(1, 4)))
            v = component_vector(a, b)
            assert np.all(v >= 0) and np.all(v <= 1)


class TestComposite:
    def test_presets_sum_to_one(self):
        for name, ws in PRESET_WEIGHTS.items():
            for t in ws.weights:
                assert abs(ws.weights[t].sum() - 1) < 1e-9, name

    def test_hedge_gate(self):
        ws = WeightSet.uniform_all({"num_tol": 1.0}, "t", lam=0.5)
        sc = CompositeScorer(ws)
        assert sc.score("12", "12") == pytest.approx(1.0)
        assert sc.score("12 or 15", "12") == pytest.approx(0.5)

    def test_roundtrip(self, tmp_path):
        ws = WeightSet.uniform_all({"em": 0.5, "tok_f1": 0.5}, "rt", lam=0.25)
        ws.save(tmp_path / "w.json")
        ws2 = WeightSet.load(tmp_path / "w.json")
        assert np.allclose(ws2.get("numeric"), ws.get("numeric")) and ws2.lam("text") == 0.25

    def test_score_matrix_matches_scalar(self):
        ws = PRESET_WEIGHTS["original_rcustom"]
        sc = CompositeScorer(ws)
        pairs = [("12", "12"), ("about 1,600", "1577"), ("Italy and France", "Italy")]
        M = np.stack([component_vector(p, g) for p, g in pairs])
        types = np.array([0, 0, 2])
        vec = CompositeScorer.score_matrix(M, types, ws.param_matrix())
        for i, (p, g) in enumerate(pairs):
            assert vec[i] == pytest.approx(sc.score(p, g, atype=AnswerType(["numeric", "boolean", "text", "freeform"][types[i]])))
