"""Alaska benchmark - schema matching ground truth (source attribute -> mediated-schema attribute),
monitor vertical (DI2KG 2020 challenge release of the Alaska data).

Raw files (data/raw/alaska_schema/Schema-Alignment/dataset/, a clone of
https://github.com/ValerioMarini/Schema-Alignment which redistributes the DI2KG 2020 monitor package):
  monitor_schema_matching_labelled_data.csv   source_attribute_id,target_attribute_name  (135 rows, 93 sources)
  monitor_mediated_schema.txt                 one target attribute per line (87)
  monitor_specs/<source>/<n>.json             16,662 monitor specifications (for example values)
The camera schema-matching ground truth (687 labelled attributes) is only published behind the
research.alaska SharePoint links (login wall); drop `camera_schema_matching_labelled_data.csv`,
`camera_mediated_schema.txt` and `camera_specs/` into the same folder and it is picked up automatically.

Item = one source attribute (e.g. "www.ebay.com//screen size") with 3 example values and the list of
target attributes; answer = the target attribute name.  Sources mapped to several targets get the extra
targets as gold_aliases.  answer_type text, native_metric em.
"""
import csv
import json
import logging
import os
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import clip, raw_dir

logger = logging.getLogger(__name__)
REPO = "https://github.com/ValerioMarini/Schema-Alignment.git"
VERTICALS = ["monitor", "camera"]


def _values_by_attr(spec_dir: Path, source: str) -> Dict[str, List[str]]:
    vals: Dict[str, List[str]] = defaultdict(list)
    d = spec_dir / source
    if not d.is_dir():
        return vals
    for p in sorted(d.glob("*.json"), key=lambda q: int(q.stem) if q.stem.isdigit() else 0):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                spec = json.load(f)
        except Exception:
            continue
        for k, v in spec.items():
            if k == "<page title>" or v is None:
                continue
            s = str(v).strip()
            if s:
                vals[k.strip().lower()].append(s)
    return vals


class AlaskaSchemaAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = raw_dir("alaska_schema")
        ds = root / "Schema-Alignment" / "dataset"
        if not ds.is_dir():
            try:
                subprocess.run(["git", "clone", "-q", "--depth", "1", REPO, str(root / "Schema-Alignment")], check=True)
            except Exception as e:
                raise FileNotFoundError(f"Missing {ds}; `git clone --depth 1 {REPO}` into {root} failed: {e}")
        out = []
        num_q, seed = int(config.get("num_questions") or 0), config.get("seed", 0)
        for vert in VERTICALS:
            gt = ds / f"{vert}_schema_matching_labelled_data.csv"
            schema = ds / f"{vert}_mediated_schema.txt"
            specs = ds / f"{vert}_specs"
            if not gt.exists():
                if vert == "monitor":
                    raise FileNotFoundError(f"Missing {gt} (expected in the Schema-Alignment clone)")
                logger.info(f"alaska_schema: no {vert} ground truth at {gt}; skipped")
                continue
            targets = [l.strip() for l in open(schema, encoding="utf-8") if l.strip()]
            golds: Dict[str, List[str]] = defaultdict(list)
            with open(gt, encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    sid, tgt = r["source_attribute_id"].strip(), r["target_attribute_name"].strip()
                    if tgt and tgt not in golds[sid]:
                        golds[sid].append(tgt)
            per_source: Dict[str, Dict[str, List[str]]] = {}
            target_list = "\n".join(f"- {t}" for t in targets)
            for sid, tg in sorted(golds.items()):
                source, attr = sid.split("//", 1)
                if source not in per_source:
                    per_source[source] = _values_by_attr(specs, source)
                vals = per_source[source].get(attr.strip().lower(), [])
                rng = random.Random(f"{seed}-{sid}")
                distinct = list(dict.fromkeys(vals))
                sample = rng.sample(distinct, min(3, len(distinct))) if distinct else []
                ex = "\n".join(f"  - {clip(v, 120)}" for v in sample) if sample else "  (no example values found)"
                ctx = (f"Source: {source} ({vert} product specifications)\n"
                       f"Source attribute name: {attr}\n"
                       f"Example values ({len(vals)} occurrences in this source):\n{ex}\n\n"
                       f"Target attributes of the mediated schema ({len(targets)}):\n{target_list}")
                out.append(QuestionItem(
                    uid=f"alaska_schema_{vert}_{sid}".replace("/", "_").replace(" ", "_"),
                    question=("Which attribute of the mediated schema does this source attribute correspond to? "
                              "Answer with the exact target attribute name from the list."),
                    ground_truth=tg[0], gold_aliases=tg[1:], difficulty=vert, context=clip(ctx, 2500),
                    dataset_name="alaska_schema", data_type="table", answer_type="text", native_metric="em",
                    extra={"vertical": vert, "source": source, "source_attribute": attr, "all_gold_targets": tg,
                           "n_targets": len(targets), "n_value_occurrences": len(vals),
                           "download": "https://github.com/merialdo/research.alaska (DI2KG 2020 package via ValerioMarini/Schema-Alignment)",
                           "licence": "MIT (research.alaska repository)"}))
        if num_q and len(out) > num_q:
            out = random.Random(seed).sample(out, num_q)
        return out
