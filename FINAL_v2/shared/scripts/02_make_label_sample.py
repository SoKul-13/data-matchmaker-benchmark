#!/usr/bin/env python
"""Draw the human-labelling sample and write the labellers' sheets.

    uv run python shared/scripts/02_make_label_sample.py            # 50 questions per dataset (1,550 rows) + 30-row pilot, 5 graders who all grade every row
    uv run python shared/scripts/02_make_label_sample.py --stratify type --n 400          # the first small design
    uv run python shared/scripts/02_make_label_sample.py --per-dataset 50 --pilot 30 --seed 20260923 --block-size 50

Sample design (FINAL_v2/notes/HUMAN_LABELLING_PROTOCOL.md section 2).  Default --stratify dataset, for every dataset:
  * --per-dataset DISTINCT questions (50 -> 1,550 rows); no question appears twice, so every sampled question carries the same weight;
  * stratified random sampling by question sub-type (the pool's sub-task / difficulty label combined with the answer type): within a
    sub-type the questions are drawn at random; --allocation proportional (default) gives each sub-type the share of the sample that it
    has of the dataset (largest-remainder rounding, so a sub-type with very few questions can receive none); --allocation equal gives
    every sub-type the same number, a sub-type with fewer questions than its share contributing all of them;
  * models balanced: each question is paired with ONE model's answer so that every model has the same number of rows (within one);
  * up to --disagree-share of the rows (default a quarter) use an answer on which exact match and the deployed composite disagree by
    >= 0.5 (the informative cases), chosen only through which model's answer is shown, never through which question is sampled.
--stratify type: --n rows split equally over the four answer types with a --per-dataset floor (the original 400-row design).
Rows come from the real answered items only.  The pilot is drawn from questions that are not in the main sample.

Outputs in data/labels/ :
  sample_master.csv     researcher copy: row_id + dataset, uid, model, answer_type, the judge's scores (never given to labellers)
  labeller_sheet.csv    blind sheet: row_id, task family, dataset description, question, context, table, gold answer, accepted
                        alternatives, the model's final answer and its full reply, plus empty rating / hedged / note columns
                        There is no assignment of rows to people: any number of graders can take part, each identified by a
                        email address (stored as a code).  The sheet has a `block` column that cuts the (shuffled) rows into work
                        units of --block-size rows (one online form = one block); a grader does whole blocks.
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


def clip_final(t, n=1200):
    """A reply that never reached a final-answer line is returned whole by the extractor (up to 100,000 characters of reasoning).
    Show its end, marked, so the grader sees that no final answer was given (guide: grade what is there, 0.00 if nothing)."""
    return t if len(t) <= n else f"[no final-answer line was found in this reply; its last {n} characters are shown]\n" + t[-n:]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=400, help="rows when --stratify type"); ap.add_argument("--pilot", type=int, default=30); ap.add_argument("--seed", type=int, default=20260923)
    ap.add_argument("--stratify", choices=["dataset", "type"], default="dataset"); ap.add_argument("--per-dataset", type=int, default=50, help="distinct questions per dataset (dataset mode) or floor per dataset (type mode)")
    ap.add_argument("--allocation", choices=["proportional", "equal"], default="proportional", help="dataset mode: questions per sub-type in proportion to the dataset's mix, or the same number for every sub-type")
    ap.add_argument("--disagree-share", type=float, default=0.25, help="dataset mode: share of rows shown with a judge-vs-exact-match disagreement answer")
    ap.add_argument("--block-size", type=int, default=50, help="rows per block (work unit; one online form)"); a = ap.parse_args()
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
    comp["stratum"] = [f"{pools[(d, u)].get('difficulty') or '-'} / {t}" for d, u, t in zip(comp.dataset, comp.uid, comp.atype)]

    def draw_dataset(frame, n, share):
        """n distinct questions of one dataset, stratified by sub-type (proportional or equal), one model's answer per question, models balanced."""
        q = frame.drop_duplicates("uid")[["uid", "stratum"]]
        by = {st: list(g.uid.sample(frac=1, random_state=int(rng.integers(1 << 31)))) for st, g in sorted(q.groupby("stratum"))}
        total = min(n, len(q))
        if a.allocation == "proportional":  # each sub-type's share of the sample = its share of the dataset (largest-remainder rounding)
            exact = {st: total * len(by[st]) / len(q) for st in by}; quota = {st: int(exact[st]) for st in by}
            for st in sorted(by, key=lambda st: (-(exact[st] - quota[st]), rng.random()))[:total - sum(quota.values())]: quota[st] += 1
        else:  # equal allocation (water-filling): one more question to every sub-type that still has one, smallest quota first
            quota = {st: 0 for st in by}; left = total
            while left > 0:
                for st in sorted([st for st in by if quota[st] < len(by[st])], key=lambda st: (quota[st], rng.random())):
                    if left == 0: break
                    quota[st] += 1; left -= 1
        chosen = [u for st in by for u in by[st][:quota[st]]]
        idx = {(r.uid, r.model): r.Index for r in frame.itertuples()}; dis = {(r.uid, r.model): bool(r.disagree) for r in frame.itertuples()}
        cap = -(-len(chosen) // len(models)); load = {m: 0 for m in models}; picks = []; n_dis = int(round(len(chosen) * share)); rest = []
        for u in rng.permutation(chosen):
            ms = [m for m in models if dis.get((u, m)) and load[m] < cap] if n_dis > 0 else []
            if ms:
                m = min(ms, key=lambda m: (load[m], rng.random())); load[m] += 1; picks.append(idx[(u, m)]); n_dis -= 1
            else: rest.append(u)
        for u in rest:
            ms = [m for m in models if (u, m) in idx and load[m] < cap] or [m for m in models if (u, m) in idx]
            m = min(ms, key=lambda m: (load[m], rng.random())); load[m] += 1; picks.append(idx[(u, m)])
        return frame.loc[picks]

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
        main_df = pd.concat([draw_dataset(comp[comp.dataset == d], a.per_dataset, a.disagree_share) for d in sorted(comp.dataset.unique())])
    else:
        main_df = pd.concat([draw(comp[comp.atype == t], per_type, set()) for t in types])
        for d in sorted(comp.dataset.unique()):  # dataset floor
            have = (main_df.dataset == d).sum()
            if have < a.per_dataset:
                extra = comp[(comp.dataset == d) & ~comp.index.isin(main_df.index)].sample(a.per_dataset - have, random_state=int(rng.integers(1 << 31)))
                main_df = pd.concat([main_df, extra])
    used_q = set(zip(main_df.dataset, main_df.uid)); fresh = comp[[(d, u) not in used_q for d, u in zip(comp.dataset, comp.uid)]]  # pilot: questions not in the main sample
    pilot = pd.concat([draw(fresh[fresh.atype == t], a.pilot // 4 + (1 if i < a.pilot % 4 else 0), set()) for i, t in enumerate(types)])

    def rows_for(df, prefix):
        out = []
        for i, (_, r) in enumerate(df.sample(frac=1, random_state=int(rng.integers(1 << 31))).iterrows()):
            it = pools[(r.dataset, r.uid)]; pr = preds[(r.model, r.dataset, r.uid)]
            aliases = it.get("gold_aliases") or "[]"; gl = it.get("gold_list")
            out.append({"row_id": f"{prefix}{i+1:03d}", "task_family": FAMILY[r.family], "dataset_description": DATASET_DESC.get(r.dataset, r.dataset), "answer_type": r.atype,
                        "question": it["question"], "context": it.get("context") or "", "table": it.get("table_data") or "", "choices": "" if str(it.get("choices")) in ("None", "") else str(it.get("choices")),
                        "gold_answer": it["ground_truth"], "accepted_alternatives": "" if aliases in ("[]", "") else aliases, "gold_is_a_list": "" if str(gl) in ("None", "") else "yes: every item required",
                        "model_final_answer": clip_final(extract_final_answer(pr.get("prediction") or "")), "model_full_reply": clip_reply(pr.get("prediction") or ""),
                        "rating": "", "hedged": "", "note": "",
                        "_dataset": r.dataset, "_uid": r.uid, "_model": r.model, "_em": r.em, "_v1": round(r.v1, 3), "_disagree_case": bool(r.disagree), "_stratum": r.stratum})
        return out

    for stale in ["assignments.csv"]:
        if (LAB / stale).exists(): (LAB / stale).unlink()
    for df, prefix, name in [(main_df, "R", "main"), (pilot, "P", "pilot")]:
        rows = rows_for(df, prefix)
        master = pd.DataFrame(rows)
        master.insert(1, "block", [i // a.block_size + 1 for i in range(len(master))] if name == "main" else 1)
        master.to_csv(LAB / ("sample_master.csv" if name == "main" else "pilot_master.csv"), index=False)
        blind = master[[c for c in master.columns if not c.startswith("_")]]
        blind.to_csv(LAB / ("labeller_sheet.csv" if name == "main" else f"pilot_{a.pilot}.csv"), index=False)
        print(f"{name}: {len(master)} rows | by type {master.answer_type.value_counts().to_dict()} | disagreement cases {int(master._disagree_case.sum())} | datasets {master._dataset.nunique()} (rows per dataset {master._dataset.value_counts().min()}-{master._dataset.value_counts().max()}) | models {master._model.nunique()} (rows per model {master._model.value_counts().min()}-{master._model.value_counts().max()}) | distinct questions {master[["_dataset", "_uid"]].drop_duplicates().shape[0]} | question sub-types {master.groupby("_dataset")._stratum.nunique().sum()}")
    (LAB / "README.md").write_text(f"""# Human labels

Generated by `shared/scripts/02_make_label_sample.py --stratify {a.stratify} --per-dataset {a.per_dataset} --allocation {a.allocation} --disagree-share {a.disagree_share} --n {a.n} --pilot {a.pilot} --seed {a.seed} --block-size {a.block_size}`.
Design: {a.per_dataset} distinct questions per dataset, random within question sub-types with {a.allocation} allocation, one model's answer per question with models balanced; graders record a rating from 1 to 7, converted afterwards to a utility on the 0-1 line, (rating - 1) / 6 (`shared/scripts/label_scale.py`).

* `labeller_sheet.csv` - the one blind main sheet every grader receives: {len(main_df)} rows in {-(-len(main_df) // a.block_size)} blocks of {a.block_size} (`block` column; one online form per block). No rows are assigned to anyone: any number of graders take part, each identified by their email address (stored only as a code), and each does whole blocks. Graders fill `rating` (1 to 7), `hedged`, `note`.
* `pilot_{a.pilot}.csv` - the calibration pilot, done first by every grader and discussed before the main sheet.
* `handoff/grader_kit.zip` (from `04_make_labeller_handoff.py`) - the one zip to give every grader: walkthrough, guide, pilot and main sheets (xlsx + csv).
* Never share `sample_master.csv` / `pilot_master.csv`: they name the model and carry the judge's scores.
* After labelling: `uv run python shared/scripts/03_label_agreement.py` reports agreement, writes the adjudication queue, and (once `adjudicated.csv` exists) merges everything into `human_labels.csv` for the pipelines.

* `forms_images/` (not in git; `uv run python shared/scripts/06_render_row_images.py`) - one card per row and the scale table as PNG, for the Google Forms route.

Documents: `notes/LABELLING_GUIDE_FOR_LABELLERS.md` (the rules given to graders), `notes/WALKTHROUGH_LABELLERS.md` (their procedure), `notes/WALKTHROUGH_COORDINATOR.md` (yours), `notes/GOOGLE_FORMS_OPTION.md` (the online-form route), `notes/HUMAN_LABELLING_PROTOCOL.md` (design and reporting).
""")


if __name__ == "__main__":
    main()
