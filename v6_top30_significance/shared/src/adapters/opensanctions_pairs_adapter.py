"""OpenSanctions Pairs entity-resolution benchmark (Hugging Face `sanctions-er-anon/opensanctions_pairs`,
snapshot 2025-12-09 of https://www.opensanctions.org/docs/opensource/pairs/; licence CC BY-NC 4.0).
Person / organisation record pairs with analyst judgement positive / negative; multilingual names.

Uses the label-stratified `sample_1000.json` (769 positive / 231 negative, seed 42) shipped with the
dataset; set config `opensanctions_full = true` (and download pairs.json.gz, ~390 MB) to sample from
the full 755,540-pair corpus instead.  One item per pair, gold yes / no, balanced.
"""
import gzip
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List

from .base_adapter import DatasetAdapter, QuestionItem
from .raw_cache import balanced_sample, clip, default_pool_n, ensure_file, hf_headers, hf_resolve, raw_dir, render_kv

logger = logging.getLogger(__name__)
REPO = "sanctions-er-anon/opensanctions_pairs"
SHOW = ["name", "alias", "weakAlias", "previousName", "firstName", "middleName", "lastName", "fatherName",
        "birthDate", "birthPlace", "deathDate", "gender", "nationality", "citizenship", "country", "jurisdiction",
        "position", "title", "incorporationDate", "registrationNumber", "idNumber", "passportNumber", "taxNumber",
        "innCode", "ogrnCode", "leiCode", "swiftBic", "address", "email", "phone", "website", "notes", "topics",
        "program", "programId", "sanctionStatus", "legalForm", "sector", "status", "keywords", "classification"]
QUESTION = ("Do these two records (from different sanctions / watch lists) refer to the same real-world "
            "person or organisation? Answer yes or no.")


def _render(e: dict) -> str:
    props = e.get("properties", {}) or {}
    rec: Dict[str, Any] = {"type": e.get("schema"), "caption": e.get("caption"),
                           "listed in": ", ".join(e.get("datasets", [])[:4])}
    for k in SHOW:
        if k in props:
            vals = props[k]
            if isinstance(vals, list):
                vals = list(dict.fromkeys(str(v) for v in vals))[:8]
            rec[k] = vals
    return render_kv(rec, max_val=250, max_total=1150)


class OpenSanctionsPairsAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = raw_dir("opensanctions_pairs")
        num_q, seed = int(config.get("num_questions") or default_pool_n("opensanctions_pairs")), config.get("seed", 0)
        rng = random.Random(seed)
        if config.get("opensanctions_full"):
            p = ensure_file(root / "pairs.json.gz", hf_resolve(REPO, "pairs.json.gz"), headers=hf_headers(),
                            hint="Download pairs.json.gz from https://huggingface.co/datasets/" + REPO)
            pairs = [json.loads(l) for l in gzip.open(p, "rt", encoding="utf-8")]
            src = "pairs.json.gz"
        else:
            p = ensure_file(root / "sample_1000.json", hf_resolve(REPO, "sample_1000.json"), headers=hf_headers(),
                            hint="Download sample_1000.json from https://huggingface.co/datasets/" + REPO)
            d = json.load(open(p, encoding="utf-8"))
            pairs = d["pairs"] if isinstance(d, dict) else d
            src = "sample_1000.json"
        pos = [x for x in pairs if str(x.get("judgement", "")).lower() == "positive"]
        neg = [x for x in pairs if str(x.get("judgement", "")).lower() == "negative"]
        out = []
        for x in (pairs if config.get("census") else balanced_sample(pos, neg, num_q, rng)):
            L, R = x["left"], x["right"]
            label = "yes" if str(x.get("judgement", "")).lower() == "positive" else "no"
            out.append(QuestionItem(
                uid=f"opensanctions_{L.get('id')}__{R.get('id')}".replace("/", "_")[:200], question=QUESTION,
                ground_truth=label, difficulty=str(L.get("schema") or "entity"),
                context=f"### Record A\n{_render(L)}\n\n### Record B\n{_render(R)}",
                dataset_name="opensanctions_pairs", data_type="record_pair", answer_type="boolean", native_metric="em",
                gold_aliases=["match" if label == "yes" else "no match", "1" if label == "yes" else "0"],
                extra={"schema_left": L.get("schema"), "schema_right": R.get("schema"), "left_id": L.get("id"),
                       "right_id": R.get("id"), "file": src, "source": "https://huggingface.co/datasets/" + REPO,
                       "licence": "CC BY-NC 4.0 (non-commercial); data (c) OpenSanctions and upstream list publishers"}))
        return out
