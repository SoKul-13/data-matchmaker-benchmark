"""GDC-SM: the GDC schema-matching benchmark used by Magneto (Liu et al., VLDB 2025;
https://github.com/VIDA-NYU/magneto-matcher; data: Zenodo record 14963588 / DOI 10.5281/zenodo.14963587,
CC BY 4.0).  Ten CPTAC tumour-study clinical tables (supplementary spreadsheets of the papers) must be
mapped onto the Genomic Data Commons (GDC) model (736 target columns with value vocabularies).
The mapping is many-to-one (several study columns -> one GDC column) and occasionally one-to-many
(e.g. age -> age_at_diagnosis / age_at_index / days_to_birth); all acceptable targets go to gold_aliases.

Raw files (data/raw/magneto_gdc/): gdc-sm-data.zip (ground truth + target table) and <Study>.xlsx (the
papers' supplementary tables listed in papers_info.json, downloaded from ars.els-cdn.com).
Item = one source column with up to 5 sample values + a candidate list of GDC columns (all gold targets +
hard negatives by name-token overlap + random fill, 40 shown; 2 sample values each); answer = GDC column.
"""
import csv
import io
import json
import logging
import random
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import clip, ensure_file, jaccard, raw_dir, tokens

logger = logging.getLogger(__name__)
ZENODO = "https://zenodo.org/api/records/14963588/files/{f}/content"
QUESTION = ("Which GDC (Genomic Data Commons) column does this study column map to? "
            "Answer with the exact target column name from the candidate list.")


def _camel_tokens(name: str) -> set:
    return tokens(re.sub(r"([a-z])([A-Z])", r"\1 \2", str(name)).replace("_", " "))


class MagnetoGDCAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        import pandas as pd
        root = raw_dir("magneto_gdc")
        zp = ensure_file(root / "gdc-sm-data.zip", ZENODO.format(f="gdc-sm-data.zip"), hint="Download gdc-sm-data.zip from https://zenodo.org/records/14963588")
        info_p = ensure_file(root / "papers_info.json", ZENODO.format(f="papers_info.json"), hint="Download papers_info.json from https://zenodo.org/records/14963588")
        papers = json.loads(info_p.read_text())
        z = zipfile.ZipFile(zp)
        tgt_member = [n for n in z.namelist() if n.endswith("gdc_unique_columns_concat_values.csv")][0]
        tgt = pd.read_csv(io.BytesIO(z.read(tgt_member)), low_memory=False, dtype=str)
        t_cols = list(tgt.columns)
        t_vals: Dict[str, List[str]] = {}
        for c in t_cols:
            vs = [str(v).strip() for v in tgt[c].dropna().tolist() if str(v).strip() and str(v).strip().lower() != "nan"]
            t_vals[c] = list(dict.fromkeys(vs))[:6]
        t_tok = {c: _camel_tokens(c) for c in t_cols}
        seed = config.get("seed", 0)
        n_cand = int(config.get("gdc_candidates", 40))
        out = []
        for study, meta in papers.items():
            gt_member = [n for n in z.namelist() if n.endswith(f"ground-truth/{study}")]
            if not gt_member:
                continue
            gt = list(csv.DictReader(io.StringIO(z.read(gt_member[0]).decode("utf-8"))))
            xlsx = ensure_file(root / study.replace(".csv", ".xlsx"), meta["Dataset URL"],
                               hint=f"Supplementary table of {meta['First Author']} ({meta['Paper URL']}), sheet '{meta['Sheet Name']}'")
            try:
                df = pd.read_excel(xlsx, sheet_name=meta["Sheet Name"], dtype=str)
            except Exception as e:
                raise FileNotFoundError(f"Could not read sheet {meta['Sheet Name']} from {xlsx}: {e}")
            df.columns = [str(c).strip() for c in df.columns]
            golds: Dict[str, List[str]] = defaultdict(list)
            for r in gt:
                s, t = str(r["original_paper_variable_names"]).strip(), str(r["GDC_format_variable_names"]).strip()
                if t in t_vals and t not in golds[s]:
                    golds[s].append(t)
            for s, tg in golds.items():
                if s not in df.columns:
                    continue
                vals = [str(v).strip() for v in df[s].dropna().tolist() if str(v).strip() and str(v).strip().lower() != "nan"]
                distinct = list(dict.fromkeys(vals))
                rng = random.Random(f"{seed}-{study}-{s}")
                sample = distinct[:5] if len(distinct) <= 5 else rng.sample(distinct, 5)
                stoks = _camel_tokens(s) | set().union(*(tokens(v) for v in sample[:3]))
                # candidates: golds + hard negatives by token overlap with source name / gold names + random fill
                gtoks = set().union(*(t_tok[g] for g in tg))
                scored = sorted(((jaccard(t_tok[c], stoks) + jaccard(t_tok[c], gtoks), c) for c in t_cols if c not in tg), reverse=True)
                hard = [c for _, c in scored[: n_cand // 2]]
                rest = [c for c in t_cols if c not in tg and c not in hard]
                cands = list(tg) + hard + rng.sample(rest, max(0, n_cand - len(tg) - len(hard)))
                rng.shuffle(cands)
                lines = [f"- {c}" + (f"  (e.g. {' | '.join(clip(v, 30) for v in t_vals[c][:2])})" if t_vals[c] else "") for c in cands]
                ctx = (f"Source table: {study.replace('.csv', '')} study clinical table ({df.shape[1]} columns)\n"
                       f"Source column: {s}\nSample values: {' | '.join(clip(v, 60) for v in sample) if sample else '(none)'}\n\n"
                       f"Candidate GDC target columns ({len(cands)} of {len(t_cols)}), with example vocabulary values:\n" + "\n".join(lines))
                out.append(QuestionItem(
                    uid=f"magneto_gdc_{study.replace('.csv', '')}_{s}".replace(" ", "_")[:200], question=QUESTION,
                    ground_truth=tg[0], gold_aliases=tg[1:], difficulty=study.replace(".csv", ""), context=clip(ctx, 2500),
                    dataset_name="magneto_gdc", data_type="table", answer_type="text", native_metric="em",
                    extra={"study": study.replace(".csv", ""), "source_column": s, "all_gold_targets": tg,
                           "gold_matches_source_table": [[a, b] for a, bs in golds.items() for b in bs],
                           "n_target_columns_total": len(t_cols), "n_candidates_shown": len(cands),
                           "source": "https://zenodo.org/records/14963588", "licence": "CC BY 4.0"}))
        rng = random.Random(seed)
        rng.shuffle(out)
        num_q = int(config.get("num_questions") or 0)
        return out[:num_q] if num_q else out
