import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "judge", "src")))


from adapters import AdapterRegistry
from evaluator import EvaluatorStrategy, SeparationFunction
from agent import score_answer

datasets_to_test = [
    {"name": "officeqa", "path": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "officeqa.csv"))},
    {"name": "finqa", "url": "https://raw.githubusercontent.com/czyssrs/FinQA/master/dataset/test.json"},
    {"name": "tat_qa", "url": "https://raw.githubusercontent.com/NExTplusplus/TAT-QA/master/dataset_raw/tatqa_dataset_dev.json"},
    {"name": "tab_fact", "url": "https://raw.githubusercontent.com/wenhuchen/Table-Fact-Checking/master/tokenized_data/test_examples.json"},
    {"name": "financebench", "url": "https://raw.githubusercontent.com/patronus-ai/financebench/main/data/financebench_open_source.jsonl", "q_key": "question", "a_key": "answer", "id_key": "financebench_id"},
    {"name": "fetaqa", "url": "https://raw.githubusercontent.com/Yale-LILY/FeTaQA/main/data/fetaQA-v1_test.jsonl", "q_key": "question", "a_key": "answer", "id_key": "feta_id", "metric": "freeform"},
    {"name": "wikitablequestions", "url": "https://raw.githubusercontent.com/ppasupat/WikiTableQuestions/master/data/pristine-unseen-tables.tsv", "q_key": "utterance", "a_key": "targetValue", "id_key": "id", "metric": "exact_match"},

]

results_summary = []

for d in datasets_to_test:
    name = d["name"]
    print(f"Testing dataset adapter: '{name}'...")
    adapter = AdapterRegistry.get_adapter(name)
    config = {
        "dataset_name": name,
        "dataset_url": d.get("path") or d.get("url"),
        "num_questions": 5,
        "question_key": d.get("q_key", "question"),
        "answer_key": d.get("a_key", "answer"),
        "id_key": d.get("id_key", "id"),
        "metric_type": d.get("metric", "fuzzy_numeric"),
    }
    try:
        items = adapter.load_questions(config)
        print(f"Loaded {len(items)} items for '{name}'")
        
        correct_count = 0
        scores = []
        
        for q in items:
            pred_sample = f"<REASONING>Derivation for {q.uid}</REASONING><FINAL_ANSWER>{q.ground_truth}</FINAL_ANSWER>"
            is_corr, rationale = score_answer(q.ground_truth, pred_sample, tolerance=0.01, metric_type=q.metric_type)
            if is_corr:
                correct_count += 1
            
            sep_fn = SeparationFunction()
            weighted_score = sep_fn.evaluate(q.ground_truth, q.ground_truth, cd=1.0, metric_type=q.metric_type)
            scores.append(weighted_score)
        
        acc = (correct_count / len(items)) * 100 if items else 0
        avg_score = sum(scores) / len(scores) if scores else 0
        
        results_summary.append({
            "dataset": name,
            "metric_type": items[0].metric_type if items else "unknown",
            "data_type": items[0].data_type if items else "unknown",
            "items_loaded": len(items),
            "eval_accuracy_pct": acc,
            "avg_weighted_score": round(avg_score, 2),
            "status": "PASS"
        })
    except Exception as e:
        print(f"Error testing dataset '{name}': {e}")
        results_summary.append({
            "dataset": name,
            "status": f"FAIL ({e})"
        })

df_res = pd.DataFrame(results_summary)
print("\n================ MASTER DATASET CATALOG PERFORMANCE SUMMARY ================")
print(df_res.to_string(index=False))

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
os.makedirs(output_dir, exist_ok=True)
with open(os.path.join(output_dir, "master_catalog_eval_summary.json"), "w", encoding="utf-8") as f:
    json.dump(results_summary, f, indent=2)
