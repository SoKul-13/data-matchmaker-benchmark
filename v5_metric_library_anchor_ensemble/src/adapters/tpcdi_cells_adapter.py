"""TPC-DI cell-level items from the benchmark's own data-integration task (v1/jan15_tasks).
For one customer, the prompt gives the customer record, the customer's accounts and ALL trades on
those accounts (any status); the question asks for one aggregate field.  Gold = the value in
gold_ground_truth_tpcdi_lite_v3.csv.  Only completed (CMPT) trades count, as in the v1 task."""
import csv
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, List

from .base_adapter import DatasetAdapter, QuestionItem
from .table_utils import render_record, render_table

logger = logging.getLogger(__name__)
FIELDS = {
    "num_accounts": ("How many accounts does this customer own?", "numeric", "num_tol"),
    "total_balance": ("What is the sum of the balances of all the customer's accounts?", "numeric", "num_tol"),
    "num_trades": ("How many COMPLETED trades (trade_status = CMPT) were made on the customer's accounts?", "numeric", "num_tol"),
    "total_trade_volume": ("What is the total quantity across the customer's COMPLETED trades?", "numeric", "num_tol"),
    "total_trade_value": ("What is the total value (sum of quantity x trade_price) of the customer's COMPLETED trades?", "numeric", "num_tol"),
    "symbols_traded": ("Which stock symbols were traded in the customer's COMPLETED trades? List them separated by ' | '.", "text", "em"),
}


class TPCDICellsAdapter(DatasetAdapter):
    def load_questions(self, config: dict[str, Any]) -> List[QuestionItem]:
        root = Path(config.get("dataset_url") or Path(__file__).resolve().parents[2] / "jan15_tasks")
        def read(name):
            return list(csv.DictReader(open(root / name, encoding="utf-8")))
        customers = {c["customer_id"]: c for c in read("customers_tpcdi_lite_v3.csv")}
        accounts = defaultdict(list)
        for a in read("accounts_tpcdi_lite_v3.csv"):
            accounts[a["customer_id"]].append(a)
        trades = defaultdict(list)
        for t in read("trades_tpcdi_lite_v3.csv"):
            trades[t["account_id"]].append(t)
        gold = {g["customer_id"]: g for g in read("gold_ground_truth_tpcdi_lite_v3.csv")}
        items = []
        for cid, g in gold.items():
            c = customers.get(cid)
            if not c:
                continue
            accs = accounts.get(cid, [])
            trs = [t for a in accs for t in trades.get(a["account_id"], [])]
            acc_tbl = render_table([list(accs[0].keys())] + [list(a.values()) for a in accs], max_rows=20) if accs else "(no accounts)"
            tr_cols = ["trade_id", "trade_status", "symbol", "quantity", "trade_price", "account_id"]
            tr_tbl = render_table([tr_cols] + [[t[k] for k in tr_cols] for t in trs], max_rows=60, max_chars=5000) if trs else "(no trades)"
            ctx = f"### Customer\n{render_record({k: c[k] for k in ['customer_id', 'first_name', 'last_name', 'country', 'status']})}\n\n### Accounts\n{acc_tbl}\n\n### Trades on these accounts (all statuses)\n{tr_tbl}"
            for field, (q, atype, native) in FIELDS.items():
                val = g[field].strip()
                gold_list = None
                aliases = []
                if field == "symbols_traded":
                    parts = [p.strip() for p in val.split(",") if p.strip()]
                    gold_list = parts if len(parts) > 1 else None
                    val = " | ".join(parts) if parts else "none"
                    aliases = [", ".join(parts)] if parts else ["", "no symbols"]
                items.append(QuestionItem(uid=f"tpcdi_{cid}_{field}", question=q, ground_truth=val, difficulty=field, context=ctx,
                                          dataset_name="tpcdi_cells", data_type="table", answer_type=atype, native_metric=native,
                                          gold_list=gold_list, gold_aliases=aliases))
        return self._select(items, config)
