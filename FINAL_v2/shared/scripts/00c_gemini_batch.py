#!/usr/bin/env python
"""Gemini Batch API for the items the daily trickle has not finished (replaces the trickle; 50 % of the normal price).

Batch jobs have their own token quota, so Google's ~250 requests/day cap on the Pro preview does not apply.  A job usually
finishes within hours (at most 24 h).  Rows land in data/predictions/<model>.jsonl in the same schema as 00_run_models.py,
plus `batch` (the job name) and cost_usd at the batch price.

    uv run python shared/scripts/00c_gemini_batch.py submit --dry-run          # what would be asked + cost estimate
    uv run python shared/scripts/00c_gemini_batch.py submit                    # missing items at max_tokens 700 (stage 1)
    uv run python shared/scripts/00c_gemini_batch.py status                    # state of the last job
    uv run python shared/scripts/00c_gemini_batch.py collect                   # download results, append rows
    # truncation protocol (same rule as 01_reask_truncated.py), once stage 1 is collected:
    uv run python shared/scripts/00c_gemini_batch.py submit --truncated-from 700 --max-tokens 2500
    uv run python shared/scripts/00c_gemini_batch.py submit --truncated-from 2500 --max-tokens 8000

Do not run 00_run_models.py for the same model while a job is open: collect skips items that already have an answer.
Job records: data/predictions/_gemini_batch/<job>.json (request file, keys, stage).
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import statistics
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "shared" / "src"))
DATA, CONFIG = ROOT / "data", ROOT / "config"
PRED = DATA / "predictions"; REPL = PRED / "_replaced"; JOBS = PRED / "_gemini_batch"

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

from inference.prompts import SYSTEM_PROMPT, build_prompt  # noqa: E402

sys.path.insert(0, str(ROOT / "shared" / "scripts"))
_run = __import__("00_run_models")  # load_items / load_cache from the normal runner

BATCH_DISCOUNT = 0.5
ATTEMPT = {700: 1, 2500: 2, 8000: 3, 16000: 4}
FINAL = re.compile(r"final answer\s*:", re.I)
TRUNC = ("length", "max_tokens", "FinishReason.MAX_TOKENS", "MAX_TOKENS")


def spec_cfg(name):
    cfg = tomllib.loads((CONFIG / "models.toml").read_text())
    m = next(m for m in cfg["model"] if m["name"] == name)
    return {"temperature": cfg["global"].get("temperature"), **m}, cfg["global"].get("max_tokens", 700)


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []


def unfinished(rows, stage):
    return [r for r in rows if not r.get("error") and r.get("finish") in TRUNC and (r.get("attempt") or 1) == ATTEMPT[stage]
            and not FINAL.search(r.get("prediction") or "")]


def request(it, m, max_tokens):
    gen = {"maxOutputTokens": max_tokens}
    if m.get("temperature") is not None:
        gen["temperature"] = m["temperature"]
    if m.get("thinking") == "off":
        gen["thinkingConfig"] = {"thinkingBudget": 0}
    elif m.get("thinking") == "low":
        gen["thinkingConfig"] = {"thinkingLevel": "low"}
    return {"contents": [{"role": "user", "parts": [{"text": build_prompt(it)}]}],
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}, "generationConfig": gen}


def client():
    from google import genai
    import os
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def submit(a):
    m, default_max = spec_cfg(a.model)
    max_tokens = a.max_tokens or default_max
    main_p = PRED / f"{a.model}.jsonl"; rows = load(main_p)
    items = {(it["dataset_name"], it["uid"]): it for it in _run.load_items(DATA / "pool", None, 0)}
    if a.truncated_from:
        assert a.truncated_from in ATTEMPT and max_tokens in ATTEMPT and max_tokens > a.truncated_from
        keys = [(r["dataset"], r["uid"]) for r in unfinished(rows, a.truncated_from)]
    else:
        done = _run.load_cache(main_p)
        keys = [k for k in items if k not in done]
    if a.limit:
        keys = keys[:a.limit]
    # cost estimate from this model's own finished rows (same prompts, same settings)
    ok = [r for r in rows if not r.get("error")]
    mean_in = statistics.mean(r["in_tokens"] for r in ok) if ok else 1500
    mean_out = statistics.mean(r["out_tokens"] for r in ok) if ok else max_tokens
    if a.truncated_from:
        mean_out = max_tokens  # a re-asked answer ran past the previous budget: assume it uses the whole new one
    full = len(keys) * (mean_in * m["price_in"] + mean_out * m["price_out"]) / 1e6
    worst = len(keys) * (mean_in * m["price_in"] + max_tokens * m["price_out"]) / 1e6
    print(f"[{a.model}] {len(keys)} requests at max_tokens={max_tokens}"
          + (f" (unfinished at {a.truncated_from})" if a.truncated_from else " (no answer yet)"))
    print(f"  estimate: USD {full * BATCH_DISCOUNT:.2f} batch (USD {full:.2f} at the normal price); "
          f"worst case USD {worst * BATCH_DISCOUNT:.2f}")
    if a.dry_run or not keys:
        return
    JOBS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    req_p = JOBS / f"{a.model}_{stamp}_requests.jsonl"
    with open(req_p, "w", encoding="utf-8") as f:
        for k in keys:
            f.write(json.dumps({"key": f"{k[0]}|{k[1]}", "request": request(items[k], m, max_tokens)}, ensure_ascii=False) + "\n")
    c = client()
    up = c.files.upload(file=str(req_p), config={"display_name": req_p.stem, "mime_type": "jsonl"})
    job = c.batches.create(model=m["model_id"], src=up.name, config={"display_name": req_p.stem})
    rec = {"job": job.name, "model": a.model, "model_id": m["model_id"], "max_tokens": max_tokens,
           "truncated_from": a.truncated_from, "n": len(keys), "requests": req_p.name, "input_file": up.name,
           "submitted": datetime.datetime.now().isoformat(timespec="seconds"),
           "decoding": f"temperature={m['temperature']}" if m.get("temperature") is not None else "default", "collected": False}
    (JOBS / f"{job.name.split('/')[-1]}.json").write_text(json.dumps(rec, indent=1))
    print(f"submitted {job.name} ({job.state}); check with: status, then collect")


def job_record(name):
    recs = sorted(JOBS.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if name:
        recs = [p for p in recs if p.stem == name.split("/")[-1]]
    if not recs:
        sys.exit("no batch job recorded in data/predictions/_gemini_batch/")
    return recs[-1], json.loads(recs[-1].read_text())


def status(a):
    p, rec = job_record(a.job)
    c = client(); job = c.batches.get(name=rec["job"])  # keep c alive: a temporary client closes its HTTP session
    print(f"{rec['job']}: {job.state}  ({rec['n']} requests, max_tokens={rec['max_tokens']}, submitted {rec['submitted']}, "
          f"collected={rec['collected']})")
    if getattr(job, "error", None):
        print(f"  error: {job.error}")
    return job


def parse(resp):
    """REST-shaped GenerateContentResponse -> text, in/out tokens (thinking counted as output), finish"""
    cand = (resp.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []) if not p.get("thought"))
    um = resp.get("usageMetadata") or {}
    out_t = (um.get("candidatesTokenCount") or 0) + (um.get("thoughtsTokenCount") or 0)
    fr = cand.get("finishReason")
    return text, um.get("promptTokenCount") or 0, out_t, (f"FinishReason.{fr}" if fr else None)


def collect(a):
    p, rec = job_record(a.job)
    if rec["collected"]:
        sys.exit(f"{rec['job']} already collected")
    c = client(); job = c.batches.get(name=rec["job"])
    if str(job.state) not in ("JobState.JOB_STATE_SUCCEEDED", "JOB_STATE_SUCCEEDED"):
        sys.exit(f"{rec['job']} is {job.state}; nothing to collect yet")
    raw = c.files.download(file=job.dest.file_name)
    (JOBS / f"{p.stem}_results.jsonl").write_bytes(raw)
    m, _ = spec_cfg(rec["model"])
    main_p = PRED / f"{rec['model']}.jsonl"; rows = load(main_p)
    new, n_err = {}, 0
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line); ds, uid = r["key"].split("|", 1)
        if "response" in r:
            text, in_t, out_t, finish = parse(r["response"]); err = None
        else:
            text, in_t, out_t, finish = "", 0, 0, None; err = f"BatchError: {json.dumps(r.get('error'))[:300]}"; n_err += 1
        new[(ds, uid)] = {"model": rec["model"], "model_id": rec["model_id"], "dataset": ds, "uid": uid, "prediction": text,
                          "in_tokens": in_t, "out_tokens": out_t, "latency_s": None, "error": err, "finish": finish,
                          "decoding": rec["decoding"],
                          "cost_usd": round((in_t * m["price_in"] + out_t * m["price_out"]) / 1e6 * BATCH_DISCOUNT, 6),
                          "batch": rec["job"]}
    if rec["truncated_from"]:
        # replace the unfinished answer only when the re-ask came back; archive it like 01_reask_truncated.py
        stage, today = rec["truncated_from"], datetime.date.today().isoformat()
        old = {(r["dataset"], r["uid"]): r for r in unfinished(rows, stage)}
        swap = {k for k, r in new.items() if not r["error"] and k in old}
        REPL.mkdir(exist_ok=True)
        with open(REPL / f"{rec['model']}.jsonl", "a", encoding="utf-8") as f:
            for k in swap:
                f.write(json.dumps({**old[k], "replaced_reason": f"truncated_{stage}", "replaced_on": today}, ensure_ascii=False) + "\n")
        for k in swap:
            new[k].update(attempt=ATTEMPT[rec["max_tokens"]], reason=f"truncated_{stage}")
        rows = [r for r in rows if (r["dataset"], r["uid"]) not in swap] + [new[k] for k in swap]
        added = len(swap)
    else:
        done = _run.load_cache(main_p)
        fresh = [r for k, r in new.items() if k not in done]
        rows += fresh; added = sum(1 for r in fresh if not r["error"])
    tmp = main_p.with_suffix(".jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(main_p)
    rec.update(collected=True, collected_on=datetime.datetime.now().isoformat(timespec="seconds"), answered=added, errors=n_err,
               cost_usd=round(sum(r["cost_usd"] for r in new.values()), 4))
    p.write_text(json.dumps(rec, indent=1))
    ok = {(r["dataset"], r["uid"]) for r in rows if not r.get("error")}
    trunc = sum(1 for r in new.values() if not r["error"] and r["finish"] in TRUNC and not FINAL.search(r["prediction"]))
    print(f"collected {rec['job']}: {added} answers written, {n_err} errors, cost USD {rec['cost_usd']:.2f}; "
          f"{rec['model']} now has {len(ok)} answered; {trunc} new answers unfinished at {rec['max_tokens']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["submit", "status", "collect"])
    ap.add_argument("--model", default="gemini-3.1-pro")
    ap.add_argument("--max-tokens", type=int, default=None, help="default: [global] max_tokens (700)")
    ap.add_argument("--truncated-from", type=int, default=None, help="re-ask answers unfinished at this budget")
    ap.add_argument("--limit", type=int, default=0, help="only the first N requests (smoke test)")
    ap.add_argument("--job", default=None, help="job name (default: the last one submitted)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    {"submit": submit, "status": status, "collect": collect}[a.cmd](a)


if __name__ == "__main__":
    main()
