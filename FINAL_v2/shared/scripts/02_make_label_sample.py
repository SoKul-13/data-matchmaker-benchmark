#!/usr/bin/env python
"""Draw the human-labelling sample and write the labellers' sheets.

    uv run python shared/scripts/02_make_label_sample.py            # 100 rows per dataset (3,100) + 30-row pilot, 5 graders who all grade every row
    uv run python shared/scripts/02_make_label_sample.py --stratify type --n 400 --labellers 2 --per-row 2   # the small two-grader layout
    uv run python shared/scripts/02_make_label_sample.py --per-dataset 100 --pilot 30 --seed 20260923 --labellers 5 --per-row 5

Sample design (FINAL_v2/notes/HUMAN_LABELLING_PROTOCOL.md section 2).  Default --stratify dataset: --per-dataset rows from every dataset
(100 -> 3,100 rows), an equal share per model inside each dataset, a quarter of the rows drawn from answers where exact match and the
deployed composite disagree by >= 0.5 (the informative cases).  --stratify type: --n rows split equally over the four answer types with a
--per-dataset floor (the original 400-row design).  Rows come from the real answered items only.

Outputs in data/labels/ :
  sample_master.csv     researcher copy: row_id + dataset, uid, model, answer_type, the judge's scores (never given to labellers)
  labeller_sheet.csv    blind sheet: row_id, task family, dataset description, question, context, table, gold answer, accepted
                        alternatives, the model's final answer and its full reply, plus empty utility / hedged / note columns
                        The sheet has an `assigned_to` column: the letters of the --per-row graders who own that row (loads balanced to
                        within one row).  Every grader gets the same sheet and filters it to their letter.  assignments.csv is the long form.
  pilot_30.csv          the calibration pilot (rows drawn from the same design, disjoint from the main sample); every grader does all of it
"""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "shared" / "src"))
from metrics.normalize import extract_final_answer  # noqa: E402

OUT_V2 = ROOT / "v2_gridsearch" / "output"; LAB = ROOT / "data" / "labels"
FAMILY = {"EM": "entity matching (are these two records the same real-world thing?)", "SM": "schema matching (which target column does this source column map to?)",
          "TQA": "table question answering (answer a question from a table)", "FIN": "financial document reading (answer from a filing or report)"}
DATASET_DESC = {
    "abt_buy": "product records from Abt and Buy.com", "amazon_google": "product records from Amazon and Google", "walmart_amazon": "product records from Walmart and Amazon",
    "dblp_acm": "bibliographic records from DBLP and ACM", "dblp_scholar": "bibliographic records from DBLP and Google Scholar", "wdc_products": "product offers from web shops (WDC Products 2024)",
    "wdc_lspc": "product offers from web shops (WDC LSPC 2017)", "machamp": "records with different schemas (Machamp)", "papadakis_dn": "entity-matching sets Dn1-Dn8 at their real match ratio",
    "alaska_camera": "camera product offers (Alaska)", "opensanctions_pairs": "sanctioned-entity records (OpenSanctions)",
    "valentine": "table-column matching (Valentine)", "magneto_gdc": "clinical column matching to the GDC schema", "smat": "clinical column matching to the OMOP schema",
    "alaska_schema": "monitor product attribute matching (Alaska)", "fintagging": "linking a financial fact to an XBRL concept", "tpcdi_cells": "customer-cell values from a join-and-aggregate task (TPC-DI)",
    "wikitablequestions": "questions over Wikipedia tables", "tab_fact": "is the statement supported by the table? (TabFact)", "fetaqa": "free-form answers over Wikipedia tables (FeTaQA)",
    "hitab": "questions over hierarchical statistical tables (HiTab)", "mmtu": "table understanding tasks (MMTU)", "realhitbench": "fact-checking and numeric questions over real hierarchical tables",
    "suc": "table-structure questions (SUC)", "tabis": "table information seeking, multiple choice (TabIS)", "tableeval": "table evaluation sub-tasks (TableEval)", "tablebench": "numeric and list questions over tables (TableBench)",
    "bird": "database question; the gold is the value the correct SQL returns (BIRD)", "tat_qa": "questions over financial reports with tables and text (TAT-QA)",
    "officeqa_pro_v2": "questions over office documents with the referenced pages shown (OfficeQA Pro V2)", "officeqa": "questions about office documents without the document (closed book)",
}


def clip_reply(t, n=6000):
    """Spreadsheet cells cap at ~50k characters; keep the end of long replies (the final answer is there)."""
    return t if len(t) <= n else "[... first " + str(len(t) - n) + " characters of the reply omitted; the final answer is at the end ...]\n" + t[-n:]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=400, help="rows when --stratify type"); ap.add_argument("--pilot", type=int, default=30); ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument("--stratify", choices=["dataset", "type"], default="dataset"); ap.add_argument("--per-dataset", type=int, default=100, help="rows per dataset (dataset mode) or floor per dataset (type mode)")
    ap.add_argument("--labellers", type=int, default=5, help="number of graders (letters A, B, ...)")
    ap.add_argument("--per-row", type=int, default=5, help="how many graders grade each main row (= --labellers: everyone grades everything)"); a = ap.parse_args()
    if not 1 <= a.per_row <= a.labellers <= 26: raise SystemExit("need 1 <= --per-row <= --labellers <= 26")
    rng = np.random.default_rng(a.seed); LAB.mkdir(parents=True, exist_ok=True)
    comp = pd.read_csv(OUT_V2 / "components_v1.csv"); comp["v1"] = .35 * comp.f1 + .35 * comp.decay + .15 * comp.precision + .15 * comp.recall
    comp["disagree"] = (comp.v1 - comp.em).abs() >= 0.5
    pools = {}
    for p in sorted((ROOT / "data" / "pool").glob("*.jsonl")):
        if p.stem.startswith("_"): continue
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            if r.get("in_real_subset"): pools[(r["dataset_name"], r["uid"])] = r
    preds = {}
    for p in sorted((ROOT / "data" / "predictions").glob("*.jsonl")):
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            if not r.get("error"): preds[(r["model"], r["dataset"], r["uid"])] = r
    comp = comp[[(d, u) in pools for d, u in zip(comp.dataset, comp.uid)]].copy()
    types = ["numeric", "boolean", "text", "freeform"]; per_type = a.n // 4; models = sorted(comp.model.unique())
    comp["atype"] = comp.answer_type.replace({"free_form": "freeform"})

    def draw(frame, n, excluded):
        frame = frame[~frame.index.isin(excluded)]
        n_dis = int(round(n * 0.25)); dis = frame[frame.disagree]; reg = frame[~frame.disagree]
        take_dis = dis.sample(min(n_dis, len(dis)), random_state=int(rng.integers(1 << 31))) if len(dis) else dis
        rest = n - len(take_dis)
        # equal share per model, datasets proportional with a floor: sample by model round-robin
        parts = []
        per_model = {m: rest // len(models) + (1 if i < rest % len(models) else 0) for i, m in enumerate(models)}
        for m, k in per_model.items():
            cand = reg[(reg.model == m) & ~reg.index.isin(take_dis.index)]
            parts.append(cand.sample(min(k, len(cand)), random_state=int(rng.integers(1 << 31))))
        return pd.concat([take_dis] + parts)

    if a.stratify == "dataset":
        main_df = pd.concat([draw(comp[comp.dataset == d], a.per_dataset, set()) for d in sorted(comp.dataset.unique())])
    else:
        main_df = pd.concat([draw(comp[comp.atype == t], per_type, set()) for t in types])
        for d in sorted(comp.dataset.unique()):  # dataset floor
            have = (main_df.dataset == d).sum()
            if have < a.per_dataset:
                extra = comp[(comp.dataset == d) & ~comp.index.isin(main_df.index)].sample(a.per_dataset - have, random_state=int(rng.integers(1 << 31)))
                main_df = pd.concat([main_df, extra])
    pilot = pd.concat([draw(comp[comp.atype == t], a.pilot // 4 + (1 if i < a.pilot % 4 else 0), set(main_df.index)) for i, t in enumerate(types)])

    def rows_for(df, prefix):
        out = []
        for i, (_, r) in enumerate(df.sample(frac=1, random_state=int(rng.integers(1 << 31))).iterrows()):
            it = pools[(r.dataset, r.uid)]; pr = preds[(r.model, r.dataset, r.uid)]
            aliases = it.get("gold_aliases") or "[]"; gl = it.get("gold_list")
            out.append({"row_id": f"{prefix}{i+1:03d}", "task_family": FAMILY[r.family], "dataset_description": DATASET_DESC.get(r.dataset, r.dataset), "answer_type": r.atype,
                        "question": it["question"], "context": it.get("context") or "", "table": it.get("table_data") or "", "choices": "" if str(it.get("choices")) in ("None", "") else str(it.get("choices")),
                        "gold_answer": it["ground_truth"], "accepted_alternatives": "" if aliases in ("[]", "") else aliases, "gold_is_a_list": "" if str(gl) in ("None", "") else "yes: every item required",
                        "model_final_answer": extract_final_answer(pr.get("prediction") or ""), "model_full_reply": clip_reply(pr.get("prediction") or ""),
                        "utility": "", "hedged": "", "note": "",
                        "_dataset": r.dataset, "_uid": r.uid, "_model": r.model, "_em": r.em, "_v1": round(r.v1, 3), "_disagree_case": bool(r.disagree)})
        return out

    letters = [chr(65 + i) for i in range(a.labellers)]
    for df, prefix, name in [(main_df, "R", "main"), (pilot, "P", "pilot")]:
        rows = rows_for(df, prefix)
        master = pd.DataFrame(rows)
        if name == "main":  # --per-row distinct graders per row, loads balanced to within one row, ties broken at random
            load = {l: 0 for l in letters}; assign = []
            for rid in master.row_id:
                order = sorted(letters, key=lambda l: (load[l], rng.random())); chosen = sorted(order[:a.per_row])
                for l in chosen: load[l] += 1
                assign.append(" ".join(chosen))
            master.insert(1, "assigned_to", assign)
            pd.DataFrame([{"row_id": r, "labeller": l} for r, v in zip(master.row_id, assign) for l in v.split()]).to_csv(LAB / "assignments.csv", index=False)
            print(f"assignment: {a.labellers} graders ({letters[0]}-{letters[-1]}), {a.per_row} per row, rows per grader {min(load.values())}-{max(load.values())} -> assignments.csv")
        master.to_csv(LAB / ("sample_master.csv" if name == "main" else "pilot_master.csv"), index=False)
        blind = master[[c for c in master.columns if not c.startswith("_")]]
        blind.to_csv(LAB / ("labeller_sheet.csv" if name == "main" else f"pilot_{a.pilot}.csv"), index=False)
        print(f"{name}: {len(master)} rows | by type {master.answer_type.value_counts().to_dict()} | disagreement cases {int(master._disagree_case.sum())} | datasets {master._dataset.nunique()} (rows per dataset {master._dataset.value_counts().min()}-{master._dataset.value_counts().max()}) | models {master._model.nunique()}")
    (LAB / "README.md").write_text(f"""# Human labels

Generated by `shared/scripts/02_make_label_sample.py --stratify {a.stratify} --per-dataset {a.per_dataset} --n {a.n} --pilot {a.pilot} --seed {a.seed} --labellers {a.labellers} --per-row {a.per_row}`.

* `labeller_sheet.csv` - the one blind main sheet every grader receives: {len(main_df)} rows, `assigned_to` = the {a.per_row} grader letters ({letters[0]}-{letters[-1]}) who own each row. Graders fill `utility`, `hedged`, `note` on their rows only. `assignments.csv` is the same assignment in long form.
* `pilot_{a.pilot}.csv` - the calibration pilot, done first by every grader and discussed before the main sheet.
* `handoff/grader_kit.zip` (from `04_make_labeller_handoff.py`) - the one zip to give every grader: walkthrough, guide, pilot and main sheets (xlsx + csv).
* Never share `sample_master.csv` / `pilot_master.csv`: they name the model and carry the judge's scores.
* After labelling: `uv run python shared/scripts/03_label_agreement.py` reports agreement, writes the adjudication queue, and (once `adjudicated.csv` exists) merges everything into `human_labels.csv` for the pipelines.

The guide to give the labellers is `notes/LABELLING_GUIDE_FOR_LABELLERS.md`.
""")


if __name__ == "__main__":
    main()
