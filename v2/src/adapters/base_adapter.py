from abc import ABC, abstractmethod
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    uid: str
    question: str
    ground_truth: str
    difficulty: str = "all"
    context: Optional[str] = None
    table_data: Optional[str] = None
    metric_type: str = "fuzzy_numeric"  # fuzzy_numeric, binary, exact_match, freeform
    dataset_name: str = "generic"
    data_type: str = "text"  # text, table, document, conversational


class DatasetAdapter(ABC):
    """
    Abstract Base Class for Dataset Adapters in the Green Agent Judge.
    Adapters convert raw benchmark formats (CSV, JSON, HuggingFace) into QuestionItems.
    """

    @abstractmethod
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        """
        Load and parse dataset into a list of QuestionItem instances.
        """
        pass
