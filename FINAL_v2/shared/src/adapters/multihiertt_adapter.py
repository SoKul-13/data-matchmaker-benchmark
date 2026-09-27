"""MultiHiertt (multi-hierarchical financial tables + text).  The data is distributed via Google
Drive (github.com/psunlpgroup/MultiHiertt); download test.json / dev.json and pass its path as
dataset_url (default: data/raw/multihiertt/dev.json)."""
import json
import logging
import re
from pathlib import Path
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import render_table

logger = logging.getLogger(__name__)


def _html_table_to_rows(html: str):
    rows = []
    for tr in re.findall(r"<tr.*?</tr>", html, flags=re.S | re.I):
        cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh].*?</t[dh]>", tr, flags=re.S | re.I)]
        if cells:
            rows.append(cells)
    return rows


class MultiHierttAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        path = Path(config.get("dataset_url") or Path(__file__).resolve().parents[2] / "data" / "raw" / "multihiertt" / "dev.json")
        if not path.exists():
            logger.warning(f"MultiHiertt file not found at {path}; download from the project's Google Drive link")
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        out = []
        for i, d in enumerate(self._select(data, config)):
            qa = d.get("qa", {})
            gold = str(qa.get("answer", "")).strip()
            if not gold:
                continue
            tables = d.get("tables", [])
            rendered = "\n\n".join(render_table(_html_table_to_rows(t) if isinstance(t, str) else t, max_rows=30, max_chars=1800) for t in tables[:4])
            out.append(QuestionItem(uid=str(d.get("uid") or f"mh_{i}"), question=qa.get("question", "").strip(), ground_truth=gold,
                                    context="\n".join(d.get("paragraphs", []))[:2500], table_data=rendered[:6000],
                                    dataset_name="multihiertt", data_type="table", native_metric="auto"))
        return out
