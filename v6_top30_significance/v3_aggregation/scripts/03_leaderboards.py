#!/usr/bin/env python
"""
v3 step 3 - leaderboards with parameters, bootstrap draws and significance under the two item-level rules the aggregation study uses:
  native   each dataset's own metric (the v3 rule)
  em_only  exact match everywhere
plus the top-5 view mixes and the best subset (their model scores, ranks and bootstrap rank CIs come from combos.csv).
Outputs: output/leaderboards/{native,em_only}/*, output/leaderboards/mixes_top5.md, rule_agreement.csv, summary.json, output/diagnostics/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V6 = ROOT.parent
sys.path.insert(0, str(V6 / "shared" / "src"))
DATA, CONFIG, OUT = V6 / "data", V6 / "config", ROOT / "output"
from stats.leaderboard import dataset_diagnostics, majority_baselines, poststrat_for, report_rule, rule_agreement, summary_of  # noqa: E402
from views import VIEWS  # noqa: E402


def main():
    items = pd.read_csv(OUT / "native_item_scores.csv"); models = sorted(items.model.unique()); datasets = sorted(items.dataset.unique())
    fam = items.drop_duplicates("dataset").set_index("dataset").family.to_dict(); maj = majority_baselines(DATA / "pool", datasets)
    def mats(col):
        return [items[items.dataset == d].pivot_table(index="uid", columns="model", values=col).reindex(columns=models).to_numpy(float) for d in datasets]
    uid_order = {d: sorted(items[items.dataset == d].uid.unique()) for d in datasets}; ps = poststrat_for(DATA / "pool", datasets, uid_order)
    results = {"native": report_rule("native", mats("score"), datasets, models, fam, OUT / "leaderboards" / "native", weights=None, majority=maj, poststrat=ps),
               "em_only": report_rule("em_only", mats("em"), datasets, models, fam, OUT / "leaderboards" / "em_only", weights=None, majority=maj, poststrat=ps)}
    for n, r in results.items():
        print(f"[{n}] BT ranking: " + ", ".join(f"{m}={int(x)}" for m, x in zip(models, r["rank_bt"])))
    rule_agreement(results).to_csv(OUT / "leaderboards" / "rule_agreement.csv"); json.dump(summary_of(results, models, {"native": None, "em_only": None}), open(OUT / "leaderboards" / "summary.json", "w"), indent=2)
    dataset_diagnostics(results["native"], datasets, models, fam, OUT / "diagnostics", label="native metric")
    combos = pd.read_csv(OUT / "combos" / "combos.csv"); top = combos.head(5)
    L = ["# Top-5 view mixes and the best equal-weight subset (from combos.csv)\n", "| rank | label | views (weight) | J | stability | transitivity | reference | " + " | ".join(f"{m} rank [95 %]" for m in models) + " |", "|---|---|---|---|---|---|---|" + "---|" * len(models)]
    rows = list(top.iterrows()) + [next(iter(combos[combos.design == "subset"].iterrows()))]
    for _, r in rows:
        L.append(f"| {int(r['rank'])} | {r.label} | " + ", ".join(f"{v} ({r[f'w_{v}']:.2f})" for v in VIEWS if r[f"w_{v}"] > 0) + f" | {r.J:.3f} | {r.stability:.3f} | {r.transitivity:.2f} | {r.reference:.2f} | "
                 + " | ".join(f"{int(r[f'rank_{m}'])} [{int(r[f'rank_lo_{m}'])}, {int(r[f'rank_hi_{m}'])}]" for m in models) + " |")
    (OUT / "leaderboards" / "mixes_top5.md").write_text("\n".join(L) + "\n"); print("\n".join(L[:4]))


if __name__ == "__main__":
    main()
