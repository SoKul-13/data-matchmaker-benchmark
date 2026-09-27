"""SMAT - healthcare schema matching (Zhang et al., ADBIS 2021; https://github.com/JZCS2018/SMAT):
MIMIC-III -> OMOP, Synthea -> OMOP, CMS DE-SynPUF -> OMOP.  Each raw row = (omop target attribute with
description, source attribute with description, label 0/1); the files are full cross products.

Item = one source attribute that has at least one positive target: source attribute + description and a
candidate list of 10 OMOP attributes (the true one(s) plus hard negatives drawn from the same OMOP target
table, filled from other tables if needed); answer = target attribute as `table-attribute`.  Sources with
several positives get the extra targets as gold_aliases.  answer_type text, native_metric em.
Raw files: data/raw/smat/omop_{mimic,cms,synthea}_data.xlsx (from the repo's datasets/omap folder).
"""
import logging
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import clip, ensure_file, raw_dir

logger = logging.getLogger(__name__)
GH = "https://raw.githubusercontent.com/JZCS2018/SMAT/main/datasets/omap/"
SOURCES = {"mimic": "MIMIC-III", "cms": "CMS DE-SynPUF", "synthea": "Synthea"}
QUESTION = ("Which OMOP CDM attribute does this source attribute map to? "
            "Answer with the exact target attribute name (table-attribute) from the candidate list.")


class SMATAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        import pandas as pd
        root = raw_dir("smat")
        seed = config.get("seed", 0)
        n_cand = int(config.get("smat_candidates", 10))
        out = []
        for key, label in SOURCES.items():
            p = ensure_file(root / f"omop_{key}_data.xlsx", GH + f"omop_{key}_data.xlsx",
                            hint=f"Download datasets/omap/omop_{key}_data.xlsx from https://github.com/JZCS2018/SMAT")
            df = pd.read_excel(p, dtype=str).fillna("")
            df["label"] = df["label"].astype(str).str.strip()
            t_desc: Dict[str, str] = {}
            for t, d in zip(df["omop"], df["des1"]):
                t_desc.setdefault(t.strip(), d.strip())
            s_desc: Dict[str, str] = {}
            for s, d in zip(df["table"], df["des2"]):
                s_desc.setdefault(s.strip(), d.strip())
            by_table: Dict[str, List[str]] = defaultdict(list)
            for t in t_desc:
                by_table[t.split("-")[0]].append(t)
            golds: Dict[str, List[str]] = defaultdict(list)
            for s, t, l in zip(df["table"], df["omop"], df["label"]):
                if l in ("1", "1.0") and t.strip() not in golds[s.strip()]:
                    golds[s.strip()].append(t.strip())
            all_targets = sorted(t_desc)
            for s, tg in sorted(golds.items()):
                rng = random.Random(f"{seed}-{key}-{s}")
                same = [t for t in by_table[tg[0].split("-")[0]] if t not in tg]
                rng.shuffle(same)
                cands = list(tg) + same[: max(0, n_cand - len(tg))]
                if len(cands) < n_cand:
                    rest = [t for t in all_targets if t not in cands]
                    cands += rng.sample(rest, n_cand - len(cands))
                rng.shuffle(cands)
                src_table, src_attr = (s.split("-", 1) + [""])[:2]
                lines = [f"- {t}: {clip(t_desc.get(t, '').split(';')[-1].strip() or t_desc.get(t, ''), 150)}" for t in cands]
                ctx = (f"Source database: {label}\nSource attribute: {s}  (table `{src_table}`, column `{src_attr}`)\n"
                       f"Source description: {clip(s_desc.get(s, ''), 400)}\n\n"
                       f"Candidate OMOP target attributes (table-attribute: attribute description):\n" + "\n".join(lines))
                out.append(QuestionItem(
                    uid=f"smat_{key}_{s}".replace(" ", "_")[:200], question=QUESTION, ground_truth=tg[0], gold_aliases=tg[1:],
                    difficulty=key, context=clip(ctx, 2500), dataset_name="smat", data_type="table", answer_type="text",
                    native_metric="em",
                    extra={"source_db": label, "source_attribute": s, "all_gold_targets": tg, "n_candidates": len(cands),
                           "candidate_policy": "true target(s) + hard negatives from the same OMOP table",
                           "n_target_attributes_total": len(all_targets),
                           "source": "https://github.com/JZCS2018/SMAT", "licence": "repository has no licence file; OMOP CDM docs Apache 2.0"}))
        rng = random.Random(seed)
        rng.shuffle(out)
        num_q = int(config.get("num_questions") or 0)
        return out[:num_q] if num_q else out
