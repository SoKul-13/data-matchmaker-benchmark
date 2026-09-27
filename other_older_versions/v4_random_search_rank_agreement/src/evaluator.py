"""
Evaluator Module with Multi-Metric Evaluation Strategies, Separation Function, & Scoring Helpers

Implements scoring, evaluation metrics, CSV report generation, and metric strategies:
- Fuzzy Numerical Error Tolerance
- Binary Classification Verification (TabFact)
- Exact Match & Normalization
- Rationale & Free-Form Text Similarity
"""

import csv
import math
import os
import re
from typing import Dict, List, Any, Tuple


def normalize_text(text: str) -> str:
    if not text:
        raise ValueError("Cannot normalize empty or None text")
    normalized = text.replace('\u2212', '-')
    normalized = normalized.replace('−', '-')
    return normalized


def extract_numbers_with_context(text: str) -> list[tuple[float, str, bool, bool]]:
    if not text:
        raise ValueError("Cannot extract numbers from empty text")
    text = normalize_text(text)
    text_no_commas = text.replace(',', '')
    numbers_with_context = []
    pattern = r'-?\d+\.?\d*%?'
    for match in re.finditer(pattern, text_no_commas):
        matched_text = match.group()
        if not matched_text or matched_text == '-':
            continue
        has_percent = matched_text.endswith('%')
        num_text = matched_text.rstrip('%')
        is_negative = num_text.startswith('-')
        try:
            num = float(num_text)
        except ValueError as e:
            raise ValueError(f"Failed to parse number from '{matched_text}': {e}") from e
        start = max(0, match.start() - 20)
        end = min(len(text_no_commas), match.end() + 20)
        context = text_no_commas[start:end].lower()
        numbers_with_context.append((num, context, has_percent, is_negative))
    return numbers_with_context


def detect_unit_in_context(context: str) -> tuple[str | None, float]:
    context_lower = context.lower()
    if re.search(r'\btrillions?\b', context_lower):
        return ('trillion', 1e12)
    if re.search(r'\bbillions?\b', context_lower) or re.search(r'\bb\b', context_lower):
        return ('billion', 1e9)
    if re.search(r'\bmillions?\b', context_lower) or re.search(r'\bm\b', context_lower):
        return ('million', 1e6)
    if re.search(r'\bthousands?\b', context_lower) or re.search(r'\bk\b', context_lower):
        return ('thousand', 1e3)
    return (None, 1.0)


def normalize_number_with_units(number: float, context: str) -> tuple[float, str | None]:
    try:
        unit_name, _ = detect_unit_in_context(context)
        return (number, unit_name)
    except Exception as e:
        raise ValueError(f"Failed to normalize number {number} with context '{context}': {e}") from e


def is_likely_year(num: float) -> bool:
    return 1900 <= num <= 2100 and num == int(num)


def has_significant_text(text: str) -> tuple[bool, str]:
    if not text:
        return False, ""
    cleaned = re.sub(r'[\d,.$%−\u2212-]', ' ', text.lower()).strip()
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'of', 'to', 'and', 'for', 'or', 'total', 'million', 'billion', 'trillion', 'dollars', 'dollar'}
    words = [w for w in cleaned.split() if w and w not in stopwords]
    return len(words) > 0, " ".join(words)


def check_text_overlap(ground_truth: str, predicted: str) -> tuple[bool, str]:
    has_gt_text, gt_words = has_significant_text(ground_truth)
    if not has_gt_text:
        return True, "No significant non-numeric text in ground truth"
    has_pred_text, pred_words = has_significant_text(predicted)
    if not has_pred_text:
        return False, f"Ground truth requires text '{gt_words}' but prediction contains no significant text"
    gt_tokens = set(gt_words.split())
    pred_tokens = set(pred_words.split())
    common = gt_tokens.intersection(pred_tokens)
    if common:
        return True, f"Text overlap found: {common}"
    return False, f"Text mismatch: GT='{gt_words}', Pred='{pred_words}'"


def extract_final_answer(text: str) -> str:
    if not text:
        raise ValueError("Cannot extract final answer from empty text")
    match = re.search(r'<FINAL_ANSWER>\s*(.*?)\s*</FINAL_ANSWER>', text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError("No FINAL_ANSWER tags found in response")
    content = match.group(1).strip()
    if not content:
        raise ValueError("FINAL_ANSWER tags are empty")
    if len(content) > 500:
        raise ValueError(f"FINAL_ANSWER too long ({len(content)} chars)")
    return content


def contains_multiple_candidates(ground_truth: str, predicted: str) -> tuple[bool, str]:
    gt_numbers = extract_numbers_with_context(ground_truth)
    pred_numbers = extract_numbers_with_context(predicted)
    if len(gt_numbers) != 1:
        return False, ""
    gt_val, gt_ctx, _, _ = gt_numbers[0]
    gt_is_year = is_likely_year(gt_val)
    candidates = set()
    for pred_val, pred_ctx, _, _ in pred_numbers:
        if gt_is_year:
            if is_likely_year(pred_val):
                candidates.add(int(pred_val))
        else:
            if not is_likely_year(pred_val):
                candidates.add(round(pred_val, 2))
    if len(candidates) > 1:
        return True, f"Hedged answer: GT expects 1 value but prediction contains {len(candidates)} candidates {list(candidates)[:5]}"
    return False, ""


def fuzzy_match_answer(ground_truth: str, predicted: str, tolerance: float = 0.05) -> tuple[bool, str]:
    if not ground_truth:
        raise ValueError("Ground truth cannot be empty")
    if not predicted:
        raise ValueError("Predicted answer cannot be empty")
    if not 0 <= tolerance <= 1:
        raise ValueError(f"Tolerance must be between 0 and 1, got {tolerance}")

    is_hedged, hedge_reason = contains_multiple_candidates(ground_truth, predicted)
    if is_hedged:
        return False, hedge_reason

    try:
        gt_numbers_with_context = extract_numbers_with_context(ground_truth)
    except Exception as e:
        raise ValueError(f"Failed to extract numbers: {e}") from e

    try:
        pred_numbers_with_context = extract_numbers_with_context(predicted)
    except Exception as e:
        raise ValueError(f"Failed to extract numbers: {e}") from e

    gt_numbers = [(num, ctx) for num, ctx, _, _ in gt_numbers_with_context]
    pred_numbers = [(num, ctx) for num, ctx, _, _ in pred_numbers_with_context]

    if gt_numbers and pred_numbers:
        pred_non_years = [(n, c) for n, c in pred_numbers
                         if not is_likely_year(n) or any(is_likely_year(g) for g, _ in gt_numbers)]
        matched_gt_count = 0
        for gt_val, gt_context in gt_numbers:
            gt_base, gt_unit = normalize_number_with_units(gt_val, gt_context)
            found_match = False
            for pred_val, pred_context in pred_non_years:
                pred_base, pred_unit = normalize_number_with_units(pred_val, pred_context)
                if gt_base == 0:
                    if pred_base == 0:
                        found_match = True
                        break
                else:
                    diff_pct = abs(gt_base - pred_base) / abs(gt_base)
                    if diff_pct <= tolerance:
                        found_match = True
                        break
            if found_match:
                matched_gt_count += 1

        if matched_gt_count == len(gt_numbers):
            text_matches, text_rationale = check_text_overlap(ground_truth, predicted)
            if text_matches:
                return True, f"Matched all {len(gt_numbers)} ground truth numbers within tolerance {tolerance*100:.2f}%. {text_rationale}"

            if best_match is not None:
                return False, f"No match: GT={gt_base} ({gt_unit or 'no unit'}), Closest={best_pred_info[0]} ({best_pred_info[1] or 'no unit'}), Diff={best_diff*100:.2f}%"
            else:
                return False, f"No valid numbers found in prediction"

    gt_clean = ground_truth.strip().lower().strip('"').strip("'")
    pred_clean = predicted.strip().lower().strip('"').strip("'")
    gt_clean = re.sub(r'\([^)]*\)', '', gt_clean).strip()
    pred_clean = re.sub(r'\([^)]*\)', '', pred_clean).strip()

    if gt_clean in pred_clean:
        return True, f"Text match: '{ground_truth}' found in prediction"
    if gt_clean == pred_clean:
        return True, "Exact text match"

    return False, f"No match found. GT: '{ground_truth[:100]}', Pred: '{predicted[:100]}'"


def score_answer(ground_truth: str, predicted: str, tolerance: float = 0.00, metric_type: str = "fuzzy_numeric") -> tuple[bool, str]:
    try:
        predicted_answer = extract_final_answer(predicted)
    except ValueError:
        predicted_answer = predicted.strip()

    if predicted_answer.strip().lower() == "no answer found":
        return False, "Agent reported: no answer found"

    if metric_type and metric_type != "fuzzy_numeric":
        score = EvaluatorStrategy.evaluate(predicted_answer, ground_truth, metric_type=metric_type, tolerance=tolerance)
        is_corr = score >= 0.5
        return is_corr, f"Metric '{metric_type}' evaluation score: {score}"

    try:
        return fuzzy_match_answer(ground_truth, predicted_answer, tolerance)
    except ValueError as e:
        return False, str(e)


class EvaluatorStrategy:
    """Base class for metric evaluation strategies."""
    
    @staticmethod
    def evaluate(predicted: str, ground_truth: str, metric_type: str = "fuzzy_numeric", tolerance: float = 0.01) -> float:
        if not predicted or not ground_truth:
            return 0.0

        norm_p = predicted.replace('\u2212', '-').replace('−', '-').replace(',', '').strip().lower()
        norm_gt = ground_truth.replace('\u2212', '-').replace('−', '-').replace(',', '').strip().lower()

        if norm_p == norm_gt:
            return 1.0

        if metric_type == "binary":
            pred_bool = "1" if norm_p in ["1", "true", "yes", "entailed"] else ("0" if norm_p in ["0", "false", "no", "refuted"] else norm_p)
            gt_bool = "1" if norm_gt in ["1", "true", "yes", "entailed"] else ("0" if norm_gt in ["0", "false", "no", "refuted"] else norm_gt)
            return 1.0 if pred_bool == gt_bool else 0.0

        elif metric_type == "exact_match":
            return 1.0 if norm_p == norm_gt else 0.0

        elif metric_type == "freeform":
            tokens_p = set(re.findall(r'\w+', norm_p))
            tokens_gt = set(re.findall(r'\w+', norm_gt))
            if not tokens_gt:
                return 0.0
            overlap = len(tokens_p.intersection(tokens_gt)) / float(len(tokens_gt))
            return round(overlap, 4)

        else:
            nums_p = re.findall(r'-?\d+\.?\d*', norm_p)
            nums_gt = re.findall(r'-?\d+\.?\d*', norm_gt)
            if nums_p and nums_gt:
                try:
                    val_p = float(nums_p[0])
                    val_gt = float(nums_gt[0])
                    if abs(val_p - val_gt) < 1e-4 or (val_gt != 0 and abs(val_p - val_gt) / abs(val_gt) <= tolerance):
                        return 1.0
                except ValueError:
                    pass

        return 0.0


class SeparationFunction:
    r"""
    Implements separation function f(x, y, cd) -> \hat{y} for scoring model predictions
    across synthetic and real-world datasets with domain context weighting.
    """

    def __init__(self, synthetic_weight: float = 0.8, real_weight: float = 1.0):
        self.synthetic_weight = synthetic_weight
        self.real_weight = real_weight

    def evaluate(self, x: str, y: str, cd: float = 1.0, is_synthetic: bool = False, metric_type: str = "fuzzy_numeric", tolerance: float = 0.01) -> float:
        r"""
        Computes score prediction \hat{y} in [0.0, 1.0] given predicted value x,
        ground truth y, context complexity cd, and dataset type indicator.
        """
        base_score = EvaluatorStrategy.evaluate(x, y, metric_type=metric_type, tolerance=tolerance)
        weight = self.synthetic_weight if is_synthetic else self.real_weight
        y_hat = base_score * cd * weight
        return round(y_hat, 4)


def export_eval_results_to_csv(results: List[Dict[str, Any]], output_path: str = "output/eval_results.csv") -> None:
    """Saves evaluation results, score levels, and raw values to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not results:
        return

    headers = list(results[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)
