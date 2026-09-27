import csv
import io
import logging
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import fetch_text, load_text_or_url, render_table

logger = logging.getLogger(__name__)
DEFAULT_WTQ_URL = "https://raw.githubusercontent.com/ppasupat/WikiTableQuestions/master/data/pristine-unseen-tables.tsv"
TABLE_BASE = "https://raw.githubusercontent.com/ppasupat/WikiTableQuestions/master/"


class WikiTableQuestionsAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        reader = csv.DictReader(io.StringIO(load_text_or_url(config.get("dataset_url") or DEFAULT_WTQ_URL)), delimiter="\t", quoting=csv.QUOTE_NONE)
        rows = self._select([r for r in reader if r.get("utterance") and r.get("targetValue")], config)
        questions: List[QuestionItem] = []
        for r in rows:
            try:
                table_str = render_table(list(csv.reader(io.StringIO(fetch_text(TABLE_BASE + r["context"])))), max_rows=40, max_chars=3500)
            except Exception as e:  # pragma: no cover
                logger.warning(f"WTQ table {r['context']}: {e}")
                continue
            parts = [p.strip() for p in r["targetValue"].split("|") if p.strip()]
            gold_list = parts if len(parts) > 1 else None
            questions.append(QuestionItem(
                uid=str(r["id"]), question=r["utterance"].strip(), ground_truth=" | ".join(parts) if gold_list else r["targetValue"].strip(),
                table_data=table_str, dataset_name="wikitablequestions", data_type="table",
                gold_aliases=[", ".join(parts), "; ".join(parts)] if gold_list else [], gold_list=gold_list, native_metric="em"))
        return questions
