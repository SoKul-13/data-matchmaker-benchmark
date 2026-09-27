"""Alaska benchmark - camera vertical (SIGMOD 2020 programming contest; Alaska: A Flexible Benchmark for
Data Integration, Crescenzi et al.).  29,787 camera specifications (JSON key-value pages) from 24 web
sources; entity-resolution ground truth = labelled spec pairs whose positives form entity clusters.

Raw files (data/raw/alaska_camera/): `2013_camera_specs/<source>/<n>.json` (extracted from
sigmod_dataset_specs.tar.gz) and `large_labelled_data.csv` (left_spec_id,right_spec_id,label).  Both are
mirrored in https://github.com/transactionalblog/sigmod-contest-2020 (the original bit.ly / SharePoint
links of research.alaska are login-walled).

Pairs: positives = two specs in the same cluster (connected components of labelled matches; the sampled
pairs are labelled positives), negatives = labelled non-matching pairs from different clusters, sampled
from the hardest third by page-title token Jaccard.  gold yes / no, balanced.
"""
import csv
import json
import logging
import random
import tarfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import balanced_sample, clip, default_pool_n, ensure_file, jaccard, raw_dir, render_kv, tokens

logger = logging.getLogger(__name__)
GH = "https://raw.githubusercontent.com/transactionalblog/sigmod-contest-2020/main/dataset/"
QUESTION = ("Do these two camera product specifications, scraped from different web pages, describe the same "
            "camera model (the same real-world product)? Answer yes or no.")


def _spec(root: Path, spec_id: str) -> dict:
    src, n = spec_id.split("//")
    p = root / "2013_camera_specs" / src / f"{n}.json"
    with open(p, encoding="utf-8", errors="replace") as f:
        return json.load(f)


def _render(spec: dict, spec_id: str) -> str:
    rec = {"source": spec_id.split("//")[0], "page title": spec.get("<page title>")}
    for k, v in spec.items():
        if k != "<page title>":
            rec[k] = v
    return render_kv(rec, max_val=200, max_total=1150)


class _UF:
    def __init__(self):
        self.p: Dict[str, str] = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


class AlaskaCameraAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = raw_dir("alaska_camera")
        labels = ensure_file(root / "large_labelled_data.csv", GH + "large_labelled_data",
                             hint="Expected the SIGMOD 2020 contest labelled pairs (left_spec_id,right_spec_id,label).")
        if not (root / "2013_camera_specs").is_dir():
            tgz = ensure_file(root / "sigmod_dataset_specs.tar.gz", GH + "sigmod_dataset_specs",
                              hint="Expected sigmod_dataset_specs.tar.gz containing 2013_camera_specs/<source>/<n>.json")
            with tarfile.open(tgz) as t:
                t.extractall(root)
        with open(labels, encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f)]
        uf = _UF()
        pos, neg = [], []
        for r in rows:
            a, b = r["left_spec_id"], r["right_spec_id"]
            if a == b:
                continue
            (pos if r["label"].strip() == "1" else neg).append((a, b))
            if r["label"].strip() == "1":
                uf.union(a, b)
        num_q, seed = int(config.get("num_questions") or default_pool_n("alaska_camera")), config.get("seed", 0)
        rng = random.Random(seed)
        # pre-sample a manageable candidate set, then rank negatives by title overlap (hard negatives)
        pos_c = rng.sample(pos, min(len(pos), 6 * num_q))
        neg_c = rng.sample(neg, min(len(neg), 30 * num_q))
        neg_c = [(a, b) for a, b in neg_c if uf.find(a) != uf.find(b)]
        cache: Dict[str, dict] = {}

        def spec(sid):
            if sid not in cache:
                cache[sid] = _spec(root, sid)
            return cache[sid]

        def title_tokens(sid):
            return tokens(spec(sid).get("<page title>", ""))

        scored = sorted(((jaccard(title_tokens(a), title_tokens(b)), a, b) for a, b in neg_c), reverse=True)
        hard = scored[: max(num_q, len(scored) // 3)]           # hardest third
        neg_pool = [(a, b, s) for s, a, b in hard]
        pos_pool = [(a, b, jaccard(title_tokens(a), title_tokens(b))) for a, b in pos_c]
        # prefer cross-source positives (same-source duplicates are near-trivial); keep some same-source too
        pos_pool.sort(key=lambda t: (t[0].split("//")[0] == t[1].split("//")[0], rng.random()))
        pos_pool = pos_pool[: max(num_q, len(pos_pool) // 2)]
        chosen = balanced_sample([("yes",) + p for p in pos_pool], [("no",) + n for n in neg_pool], num_q, rng)
        out = []
        for label, a, b, sim in chosen:
            out.append(QuestionItem(
                uid=f"alaska_camera_{a}__{b}".replace("/", "_"), question=QUESTION, ground_truth=label,
                difficulty="cross-source" if a.split("//")[0] != b.split("//")[0] else "same-source",
                context=f"### Specification A\n{_render(spec(a), a)}\n\n### Specification B\n{_render(spec(b), b)}",
                dataset_name="alaska_camera", data_type="record_pair", answer_type="boolean", native_metric="em",
                gold_aliases=["match" if label == "yes" else "no match", "1" if label == "yes" else "0"],
                extra={"left_spec_id": a, "right_spec_id": b, "title_jaccard": round(sim, 3),
                       "cluster_left": uf.find(a), "cluster_right": uf.find(b),
                       "negatives": "labelled non-matches, hardest third by page-title token Jaccard",
                       "source": "https://github.com/merialdo/research.alaska (mirror: transactionalblog/sigmod-contest-2020)",
                       "licence": "MIT (research.alaska repository); specs are scraped public web pages"}))
        return out
