import csv
import io
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import load_text_or_url

DEFAULT_OFFICEQA_URL = "https://raw.githubusercontent.com/databricks/officeqa/main/officeqa.csv"


class OfficeQAAdapter(DatasetAdapter):
    """OfficeQA Full (closed-book: the corpus is gated). List golds '[a, b]' are parsed."""

    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        reader = csv.DictReader(io.StringIO(load_text_or_url(config.get("dataset_url") or DEFAULT_OFFICEQA_URL)))
        rows = [(r.get("uid") or str(i), r.get("question", ""), r.get("answer") or r.get("ground_truth") or "", (r.get("difficulty") or "all").lower())
                for i, r in enumerate(reader)]
        rows = [r for r in rows if r[1] and r[2]]
        d = (config.get("difficulty") or "all").lower()
        if d != "all":
            rows = [r for r in rows if r[3] == d]
        out = []
        for uid, q, gt, diff in self._select(rows, config):
            gt = gt.strip(); gold_list, aliases, native = None, [], "num_tol"
            if gt.startswith("[") and gt.endswith("]"):
                parts = [p.strip() for p in gt[1:-1].split(", ") if p.strip()]
                if len(parts) > 1:
                    gold_list, native, aliases, gt = parts, "em", [gt, ", ".join(parts)], " | ".join(parts)
                elif parts:
                    gt = parts[0]
            out.append(QuestionItem(uid=str(uid), question=q.strip(), ground_truth=gt, difficulty=diff, dataset_name="officeqa",
                                    data_type="document", native_metric=native, gold_list=gold_list, gold_aliases=aliases))
        return out
