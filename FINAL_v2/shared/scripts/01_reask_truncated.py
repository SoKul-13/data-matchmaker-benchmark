#!/usr/bin/env python
"""Truncation protocol, one stage at a time: re-ask the answers a model did not finish.

An answer is "unfinished" when the provider reported finish == length at the stage's budget AND the reply has no
`FINAL ANSWER:` line.  The decision is mechanical (never about correctness).  Stages: 700 -> 2,500 -> 8,000 -> 16,000 -> 32,000.

    uv run python shared/scripts/01_reask_truncated.py --model deepseek-r1 --from 700 --to 2500
    uv run python shared/scripts/01_reask_truncated.py --model deepseek-r1 --from 2500 --to 8000
    uv run python shared/scripts/01_reask_truncated.py --model claude-opus-5 --from 8000 --to 16000

What it does: (1) moves the unfinished rows from data/predictions/<model>.jsonl to data/predictions/_replaced/<model>.jsonl with
replaced_reason = truncated_<from> and replaced_on = today; (2) runs 00_run_models.py --max-tokens <to> for that model, which fills the
now-missing items; (3) tags the new rows with attempt (2500 -> 2, 8000 -> 3, 16000 -> 4) and reason = truncated_<from>.
--dry-run lists what would be re-asked and the worst-case cost.
"""
from __future__ import annotations
import argparse, datetime, json, re, subprocess, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRED = ROOT / "data" / "predictions"; REPL = PRED / "_replaced"
ATTEMPT = {700: 1, 2500: 2, 8000: 3, 16000: 4, 32000: 5}
FINAL = re.compile(r"final answer\s*:", re.I)


def load(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []


def dump(p, rows):
    with open(p, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")


def unfinished(rows, stage):
    att = ATTEMPT[stage]
    return [r for r in rows if not r.get("error") and ("length" in str(r.get("finish")).lower() or "max_tokens" in str(r.get("finish")).lower()) and (r.get("attempt") or 1) == att and not FINAL.search(r.get("prediction") or "")]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", required=True); ap.add_argument("--from", dest="frm", type=int, required=True); ap.add_argument("--to", type=int, required=True); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); assert a.frm in ATTEMPT and a.to in ATTEMPT and a.to > a.frm
    main_p = PRED / f"{a.model}.jsonl"; rows = load(main_p); sel = unfinished(rows, a.frm)
    cfg = tomllib.load(open(ROOT / "config" / "models.toml", "rb")); spec = next(m for m in cfg["model"] if m["name"] == a.model)
    worst = len(sel) * (a.to * spec["price_out"] + 1500 * spec["price_in"]) / 1e6
    print(f"[{a.model}] unfinished at {a.frm}: {len(sel)} answers; re-ask at {a.to}; worst-case cost USD {worst:.2f}")
    for d in sorted({r["dataset"] for r in sel}): print(f"   {d}: {sum(1 for r in sel if r['dataset'] == d)}")
    if a.dry_run or not sel: return
    today = datetime.date.today().isoformat(); keys = {(r["dataset"], r["uid"]) for r in sel}
    REPL.mkdir(exist_ok=True)
    with open(REPL / f"{a.model}.jsonl", "a", encoding="utf-8") as f:
        for r in sel: f.write(json.dumps({**r, "replaced_reason": f"truncated_{a.frm}", "replaced_on": today}, ensure_ascii=False) + "\n")
    dump(main_p, [r for r in rows if (r["dataset"], r["uid"]) not in keys])
    print(f"archived {len(sel)} rows to _replaced/{a.model}.jsonl; running the model at max_tokens={a.to} ...")
    subprocess.run([sys.executable, str(ROOT / "shared" / "scripts" / "00_run_models.py"), "--sequential", "--models", a.model, "--max-tokens", str(a.to)], cwd=ROOT, check=True)
    rows = load(main_p); n = 0
    for r in rows:
        if (r["dataset"], r["uid"]) in keys and "attempt" not in r:
            r["attempt"] = ATTEMPT[a.to]; r["reason"] = f"truncated_{a.frm}"; n += 1
    dump(main_p, rows)
    still = [r for r in rows if (r["dataset"], r["uid"]) in keys and ("length" in str(r.get("finish")).lower() or "max_tokens" in str(r.get("finish")).lower()) and not FINAL.search(r.get("prediction") or "")]
    missing = keys - {(r["dataset"], r["uid"]) for r in rows if not r.get("error")}
    print(f"tagged {n} replacement rows (attempt {ATTEMPT[a.to]}); still unfinished at {a.to}: {len(still)}; missing / errored: {len(missing)}")


if __name__ == "__main__":
    main()
