"""
Metric library for Data Matchmaker Benchmark v2.

- normalize.py     : text / number normalisation, final-answer extraction
- answer_types.py  : gold-answer typing (numeric / boolean / text / freeform)
- components.py    : the K component metrics, each bounded in [0, 1]
- composite.py     : weighted composite with per-type weight vectors
"""
from .normalize import (
    normalize_text,
    extract_final_answer,
    extract_numbers,
    canonical_number_string,
)
from .answer_types import AnswerType, detect_answer_type, normalize_boolean
from .components import COMPONENT_NAMES, ALL_COLUMNS, HEDGE_COL, K, component_vector, component_dict
from .composite import WeightSet, CompositeScorer, PRESET_WEIGHTS, composite_from_vector

__all__ = [
    "normalize_text", "extract_final_answer", "extract_numbers", "canonical_number_string",
    "AnswerType", "detect_answer_type", "normalize_boolean",
    "COMPONENT_NAMES", "ALL_COLUMNS", "HEDGE_COL", "K", "component_vector", "component_dict",
    "WeightSet", "CompositeScorer", "PRESET_WEIGHTS", "composite_from_vector",
]
