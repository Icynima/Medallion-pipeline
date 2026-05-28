"""Check expected evidence from Day 1 labs for trainer/student confidence."""

from __future__ import annotations

import csv
import json
import sys

from common import OUT


checks: list[tuple[str, bool]] = []
checks.append(("event inbox exists", (OUT / "events" / "order_notifications.jsonl").exists()))
checks.append(("event consumer checkpoint exists", (OUT / "events" / "notification_checkpoint.json").exists()))
checks.append(("batch summary exists", (OUT / "batch" / "product_summary.csv").exists()))
checks.append(("stream state exists", (OUT / "stream" / "rolling_state.json").exists()))
checks.append(("bronze raw events exist", (OUT / "lake" / "bronze" / "order_events" / "events.jsonl").exists()))
checks.append(("silver view exists", (OUT / "lake" / "silver" / "orders" / "orders_current.csv").exists()))
gold = OUT / "lake" / "gold" / "daily_product_sales" / "product_kpis.csv"
checks.append(("gold KPIs exist", gold.exists()))

if gold.exists():
    with gold.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    checks.append(("gold excludes cancelled-only adjustment", all(row["product"] != "monitor" or row["net_sales"] == "420.00" for row in rows)))

if (OUT / "stream" / "rolling_state.json").exists():
    state = json.loads((OUT / "stream" / "rolling_state.json").read_text(encoding="utf-8"))
    checks.append(("six streaming events handled", state["events_processed"] == 6))

print("Day 1 Lab Validation")
for label, passed in checks:
    print(f"{'PASS' if passed else 'FAIL'} - {label}")
if not all(passed for _, passed in checks):
    sys.exit(1)
print("PASS - generated evidence is ready for debrief.")
