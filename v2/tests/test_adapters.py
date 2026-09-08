import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adapters import AdapterRegistry, QuestionItem
from evaluator import EvaluatorStrategy


class TestAdapters(unittest.TestCase):
    def test_adapter_registry(self):
        officeqa_adapter = AdapterRegistry.get_adapter("officeqa")
        self.assertEqual(officeqa_adapter.__class__.__name__, "OfficeQAAdapter")

        finqa_adapter = AdapterRegistry.get_adapter("finqa")
        self.assertEqual(finqa_adapter.__class__.__name__, "FinQAAdapter")

        tatqa_adapter = AdapterRegistry.get_adapter("tat_qa")
        self.assertEqual(tatqa_adapter.__class__.__name__, "TATQAAdapter")

        tabfact_adapter = AdapterRegistry.get_adapter("tab_fact")
        self.assertEqual(tabfact_adapter.__class__.__name__, "TabFactAdapter")

        generic_adapter = AdapterRegistry.get_adapter("unknown_dataset")
        self.assertEqual(generic_adapter.__class__.__name__, "GenericDatasetAdapter")

    def test_evaluator_strategy_binary(self):
        score_true = EvaluatorStrategy.evaluate("1", "1", metric_type="binary")
        self.assertEqual(score_true, 1.0)

        score_entailed = EvaluatorStrategy.evaluate("Entailed", "1", metric_type="binary")
        self.assertEqual(score_entailed, 1.0)

        score_false = EvaluatorStrategy.evaluate("0", "1", metric_type="binary")
        self.assertEqual(score_false, 0.0)

    def test_evaluator_strategy_numeric(self):
        score_exact = EvaluatorStrategy.evaluate("$150.50", "150.5", metric_type="fuzzy_numeric")
        self.assertEqual(score_exact, 1.0)

        score_approx = EvaluatorStrategy.evaluate("The value is 100.5 million", "100.0", metric_type="fuzzy_numeric", tolerance=0.01)
        self.assertEqual(score_approx, 1.0)

    def test_local_officeqa_adapter(self):
        local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "officeqa.csv"))
        if os.path.exists(local_path):
            adapter = AdapterRegistry.get_adapter("officeqa")
            questions = adapter.load_questions({"dataset_url": local_path, "num_questions": 5})
            self.assertEqual(len(questions), 5)
            self.assertEqual(questions[0].dataset_name, "officeqa")
            self.assertNotEqual(questions[0].question, "")
            self.assertNotEqual(questions[0].ground_truth, "")


if __name__ == "__main__":
    unittest.main()
