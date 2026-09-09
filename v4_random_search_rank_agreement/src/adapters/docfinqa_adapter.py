"""DocFinQA (Kensho): FinQA questions with the FULL filing as context.  Filings are ~1M
characters, far beyond a 700-token judge budget, so a small lexical retriever selects the
`n_windows` passages that share the most tokens with the question (retrieval-augmented setting)."""
import json
import logging
import re
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import fetch_text

logger = logging.getLogger(__name__)
ROWS = "https://datasets-server.huggingface.co/rows?dataset=kensho/DocFinQA&config=default&split=test&offset={off}&length={n}"
_STOP = set("the of in and to a an for is are was were what by on at from as with that this which how much many percentage percent total".split())


def select_windows(context: str, question: str, n_windows: int = 3, size: int = 3000) -> str:
    q = {w for w in re.findall(r"[a-z0-9]+", question.lower()) if w not in _STOP and len(w) > 2}
    wins = [context[i:i + size] for i in range(0, len(context), size)]
    scored = sorted(((sum(1 for w in q if w in win.lower()), i) for i, win in enumerate(wins)), reverse=True)
    keep = sorted(i for _, i in scored[:n_windows])
    return "\n...\n".join(wins[i] for i in keep)


class DocFinQAAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        max_rows = int(config.get("max_rows", 300))
        page = 10
        rows = []
        for off in range(0, max_rows, page):
            try:
                payload = json.loads(fetch_text(ROWS.format(off=off, n=page), timeout=180))
            except Exception as e:  # pragma: no cover
                logger.warning(f"DocFinQA offset {off}: {e}")
                break
            batch = [r["row"] for r in payload.get("rows", [])]
            if not batch:
                break
            rows.extend(batch)
        rows = self._select(rows, config)
        out = []
        for i, r in enumerate(rows):
            gold = str(r.get("Answer", "")).strip()
            if not gold or not r.get("Question"):
                continue
            out.append(QuestionItem(
                uid=f"docfinqa_{i}", question=r["Question"].strip(), ground_truth=gold,
                context=select_windows(r.get("Context", ""), r["Question"], int(config.get("n_windows", 3)), int(config.get("window_chars", 3000))),
                dataset_name="docfinqa", data_type="document", native_metric="auto", extra={"program": r.get("Program", "")[:300]}))
        return out
