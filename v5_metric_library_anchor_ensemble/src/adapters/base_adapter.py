from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    uid: str
    question: str
    ground_truth: str
    difficulty: str = "all"
    context: Optional[str] = None
    table_data: Optional[str] = None
    metric_type: str = "fuzzy_numeric"  # v1 field kept for compatibility
    dataset_name: str = "generic"
    data_type: str = "text"  # text, table, document, record_pair
    # ---- v2 fields -------------------------------------------------------
    gold_aliases: List[str] = Field(default_factory=list)   # alternative acceptable gold strings
    gold_list: Optional[List[str]] = None                    # list-valued golds (multi-span / WTQ)
    answer_type: Optional[str] = None                        # numeric | boolean | text | freeform (None = auto)
    native_metric: str = "em"                                # metric the dataset's authors use
    choices: Optional[List[str]] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class DatasetAdapter(ABC):
    """Adapters convert a public benchmark into QuestionItems with gold + aliases + type.

    Config keys understood by all adapters: dataset_url (path or URL; adapter default if omitted),
    num_questions (cap), seed (with num_questions -> random sample), difficulty.
    """

    @abstractmethod
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        pass

    @staticmethod
    def _select(items: list, config: dict[str, Any]) -> list:
        import random
        num_q = config.get("num_questions")
        seed = config.get("seed")
        if num_q and isinstance(num_q, int) and num_q > 0 and len(items) > num_q:
            if seed is not None:
                items = random.Random(seed).sample(items, num_q)
            else:
                items = items[:num_q]
        return items
