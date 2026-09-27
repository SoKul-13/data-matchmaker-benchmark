"""Valentine schema-matching benchmark (Koutras et al., ICDE 2021; https://github.com/delftdata/valentine;
datasets: Zenodo record 5084605, CC BY 4.0).  Five sub-benchmarks (ChEMBL, OpenData, TPC-DI, Wikidata,
Magellan) of table pairs with ground-truth column matches; the fabricated ones come in four pair types
(Joinable, Semantically-Joinable, Unionable, View-Unionable).

Item = one gold column match: source table + source column + up to 5 sample values + the target's column
list (2 sample values each); answer = the matching target column name.  extra carries the sub-benchmark,
pair type, and the full gold match set of the source table (for set-level F1).
Raw file: data/raw/valentine/Valentine-datasets.zip (read in place, never extracted).
"""
import csv
import io
import json
import logging
import random
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import clip, ensure_file, raw_dir

logger = logging.getLogger(__name__)
ZENODO = "https://zenodo.org/records/5084605/files/Valentine-datasets.zip?download=1"
PAIR_TYPES = {"Joinable": "joinable", "Semantically-Joinable": "semantically-joinable", "Unionable": "unionable",
              "View-Unionable": "view-unionable", "View -Unionable": "view-unionable"}
QUESTION = ("Which column of the target table matches this source column (same attribute / semantics)? "
            "Answer with the exact target column name.")


def _csv_columns(z: zipfile.ZipFile, member: str, max_rows: int = 3000) -> Tuple[List[str], Dict[str, List[str]]]:
    csv.field_size_limit(10 ** 9)
    with z.open(member) as fh:
        reader = csv.reader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace", newline=""))
        header = next(reader, [])
        vals: Dict[str, List[str]] = {h: [] for h in header}
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            if row == header:  # some Magellan files repeat the header
                continue
            for h, v in zip(header, row):
                v = v.strip()
                if v and v.lower() not in ("nan", "none", "null") and len(vals[h]) < 60 and v not in vals[h]:
                    vals[h].append(v)
    return header, vals


class ValentineAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = raw_dir("valentine")
        zp = ensure_file(root / "Valentine-datasets.zip", ZENODO, hint="Download Valentine-datasets.zip (600 MB) from https://zenodo.org/record/5084605")
        z = zipfile.ZipFile(zp)
        names = [n for n in z.namelist() if n.startswith("Valentine-datasets/") and not n.endswith("/")]
        maps = [n for n in names if n.endswith("_mapping.json")]
        groups: Dict[Tuple[str, str], List[str]] = defaultdict(list)
        for m in maps:
            parts = m.split("/")
            sub = parts[1]
            ptype = PAIR_TYPES.get(parts[2], "real-world" if sub in ("Magellan", "Wikidata") else parts[2])
            if sub == "Wikidata":
                low = parts[-2].lower()
                ptype = ("view-unionable" if "viewunion" in low else "semantically-joinable" if "semjoin" in low
                         else "unionable" if "union" in low else "joinable" if "join" in low else ptype)
            groups[(sub, ptype)].append(m)
        seed = config.get("seed", 0)
        rng = random.Random(seed)
        pairs_per_group = int(config.get("valentine_pairs_per_group", 4))
        items_per_pair = int(config.get("valentine_items_per_pair", 6))
        chosen_maps = []
        for key in sorted(groups):
            ms = sorted(groups[key])
            k = len(ms) if key[0] in ("Magellan", "Wikidata") else min(pairs_per_group, len(ms))
            chosen_maps += [(key, m) for m in rng.sample(ms, k)]
        out = []
        for (sub, ptype), m in chosen_maps:
            folder = m.rsplit("/", 1)[0]
            matches = json.loads(z.read(m).decode("utf-8"))["matches"]
            if not matches:
                continue
            src_csv = [n for n in names if n.startswith(folder + "/") and n.endswith("_source.csv")]
            tgt_csv = [n for n in names if n.startswith(folder + "/") and n.endswith("_target.csv")]
            if not src_csv or not tgt_csv:
                continue
            try:
                s_cols, s_vals = _csv_columns(z, src_csv[0])
                t_cols, t_vals = _csv_columns(z, tgt_csv[0])
            except Exception as e:  # pragma: no cover
                logger.warning(f"valentine {folder}: {e}")
                continue
            src_table = matches[0]["source_table"]
            tgt_table = matches[0]["target_table"]
            gold_set = [[mt["source_column"], mt["target_column"]] for mt in matches]
            gold_by_src: Dict[str, List[str]] = defaultdict(list)
            for s, t in gold_set:
                gold_by_src[s].append(t)
            srcs = sorted(gold_by_src)
            srcs = rng.sample(srcs, min(items_per_pair, len(srcs)))
            for s in srcs:
                if s not in s_vals:
                    continue
                golds = [g for g in gold_by_src[s] if g in t_cols] or gold_by_src[s]
                sv = s_vals.get(s, [])[:5]
                # target column list with 2 sample values each; keep gold columns if the list must be cut
                lines = {c: f"- {c}" + (f"  (e.g. {' | '.join(clip(v, 40) for v in t_vals.get(c, [])[:2])})" if t_vals.get(c) else "") for c in t_cols}
                header = (f"Source table: {src_table}  ({len(s_cols)} columns)\nSource column: {s}\n"
                          f"Sample values: {' | '.join(clip(v, 60) for v in sv) if sv else '(none)'}\n\n"
                          f"Target table: {tgt_table}  ({len(t_cols)} columns)\nTarget columns:\n")
                budget = 2450 - len(header)
                keep = list(t_cols)
                total = sum(len(lines[c]) + 1 for c in keep)
                others = [c for c in keep if c not in golds]
                rng2 = random.Random(f"{seed}-{folder}-{s}")
                rng2.shuffle(others)
                while total > budget and others:
                    c = others.pop()
                    total -= len(lines[c]) + 1
                    keep.remove(c)
                omitted = len(t_cols) - len(keep)
                ctx = header + "\n".join(lines[c] for c in keep) + (f"\n... ({omitted} more target columns omitted)" if omitted else "")
                out.append(QuestionItem(
                    uid=f"valentine_{sub}_{folder.split('/')[-1]}_{s}".replace(" ", "_")[:200],
                    question=QUESTION, ground_truth=golds[0], gold_aliases=golds[1:], difficulty=sub,
                    context=clip(ctx, 2500), dataset_name="valentine", data_type="table", answer_type="text",
                    native_metric="em",
                    extra={"sub_benchmark": sub, "pair_type": ptype, "pair": folder.split("/")[-1],
                           "source_table": src_table, "target_table": tgt_table, "source_column": s,
                           "all_gold_targets": gold_by_src[s], "gold_matches_source_table": gold_set,
                           "n_source_columns": len(s_cols), "n_target_columns": len(t_cols),
                           "n_target_columns_shown": len(keep),
                           "source": "https://zenodo.org/record/5084605", "licence": "CC BY 4.0"}))
        rng.shuffle(out)
        num_q = int(config.get("num_questions") or 0)
        return out[:num_q] if num_q else out
