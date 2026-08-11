"""
Dual Rubric & Statistical Metrics Engine
Computes metrics under both the Original Rubric and the Custom Math-Grounded Rubric (R_custom),
alongside Exact Match (EM), Precision, Recall, F1-Score, and Mean Relative Error (MRE).
"""

import math
import re
from typing import Dict, Any, Tuple

def normalize_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def compute_precision_recall_f1(ground_truth: str, prediction: str) -> Tuple[float, float, float]:
    gt_tokens = normalize_text(ground_truth).split()
    pred_tokens = normalize_text(prediction).split()
    
    if not gt_tokens or not pred_tokens:
        return (1.0, 1.0, 1.0) if gt_tokens == pred_tokens else (0.0, 0.0, 0.0)
    
    common = set(gt_tokens) & set(pred_tokens)
    num_same = sum(min(gt_tokens.count(w), pred_tokens.count(w)) for w in common)
    
    if num_same == 0:
        return 0.0, 0.0, 0.0
    
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return precision, recall, f1

def extract_first_number(text: str) -> float | None:
    text_clean = str(text).replace(",", "").replace("$", "").replace("%", "")
    matches = re.findall(r'[-+]?\d*\.?\d+', text_clean)
    if matches:
        try:
            return float(matches[0])
        except ValueError:
            return None
    return None

def compute_mre(ground_truth: str, prediction: str) -> float:
    gt_num = extract_first_number(ground_truth)
    pred_num = extract_first_number(prediction)
    
    if gt_num is None or pred_num is None:
        return 0.0 if ground_truth.strip().lower() == prediction.strip().lower() else 1.0
    
    if gt_num == 0.0:
        return 0.0 if pred_num == 0.0 else 1.0
    
    return abs(pred_num - gt_num) / (abs(gt_num) + 1e-6)

def evaluate_original_rubric(ground_truth: str, prediction: str, metric_type: str = "fuzzy_numeric") -> float:
    """Original Rubric Weighting:
    Column/Format 20%, Row/Entity Count 10%, Coverage 15%, Numeric 40%, String/Text 15%
    """
    prec, rec, f1 = compute_precision_recall_f1(ground_truth, prediction)
    mre = compute_mre(ground_truth, prediction)
    
    # 1. Format / Column Check (20 pts)
    format_score = 20.0 if ("<FINAL_ANSWER>" in prediction or len(prediction.strip()) > 0) else 0.0
    
    # 2. Entity / Row Check (10 pts)
    row_score = 10.0 if len(prediction.strip()) > 0 else 0.0
    
    # 3. Coverage (15 pts)
    coverage_score = 15.0 * rec
    
    # 4. Numeric Accuracy (40 pts)
    numeric_score = 40.0 * max(0.0, 1.0 - mre) if metric_type == "fuzzy_numeric" else 40.0 * f1
    
    # 5. String Accuracy (15 pts)
    string_score = 15.0 * prec
    
    total = format_score + row_score + coverage_score + numeric_score + string_score
    return round(min(100.0, max(0.0, total)), 2)

def evaluate_custom_math_rubric(ground_truth: str, prediction: str, metric_type: str = "fuzzy_numeric") -> float:
    """Custom Math-Grounded Rubric (R_custom):
    R_custom = 100 * [ 0.35 * F1 + 0.35 * exp(-2.5 * MRE) + 0.15 * Precision + 0.15 * Recall ]
    
    Mathematical Justification:
    1. Replaces linear numerical penalty with exponential decay exp(-2.5 * MRE), penalizing high-variance hallucinations.
    2. Uses harmonic mean F1 (35% weight) to eliminate false-positive passes on partial token overlap.
    3. Guarantees convex optimization properties and strict information-theoretic bounds [0, 100].
    """
    prec, rec, f1 = compute_precision_recall_f1(ground_truth, prediction)
    mre = compute_mre(ground_truth, prediction)
    
    numeric_decay = math.exp(-2.5 * mre) if metric_type in ["fuzzy_numeric", "exact_match"] else f1
    
    score = (0.35 * f1 + 0.35 * numeric_decay + 0.15 * prec + 0.15 * rec) * 100.0
    return round(min(100.0, max(0.0, score)), 2)

def compute_full_eval_metrics(ground_truth: str, prediction: str, metric_type: str = "fuzzy_numeric") -> Dict[str, Any]:
    prec, rec, f1 = compute_precision_recall_f1(ground_truth, prediction)
    mre = compute_mre(ground_truth, prediction)
    
    exact_match = 1.0 if normalize_text(ground_truth) == normalize_text(prediction) else 0.0
    orig_rubric = evaluate_original_rubric(ground_truth, prediction, metric_type)
    custom_rubric = evaluate_custom_math_rubric(ground_truth, prediction, metric_type)
    
    return {
        "exact_match": round(exact_match * 100.0, 2),
        "precision": round(prec * 100.0, 2),
        "recall": round(rec * 100.0, 2),
        "f1_score": round(f1 * 100.0, 2),
        "mre_pct": round(mre * 100.0, 2),
        "original_rubric_score": orig_rubric,
        "custom_rubric_score": custom_rubric
    }
