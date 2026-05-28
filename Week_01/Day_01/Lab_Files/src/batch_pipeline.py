"""Run a bounded batch aggregation over the supplied order file."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from common import DATA, OUT, ensure_dir


def run_batch() -> None:
    source = DATA / "orders_batch.csv"
    output = ensure_dir(OUT / "batch") / "product_summary.csv"
    totals: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {"submitted_orders": 0, "cancelled_orders": 0, "net_value": Decimal("0.00")}
    )

    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            value = Decimal(row["quantity"]) * Decimal(row["unit_price"])
            bucket = totals[row["product"]]
            if row["status"] == "CANCELLED":
                bucket["cancelled_orders"] += 1
                bucket["net_value"] -= value
            else:
                bucket["submitted_orders"] += 1
                bucket["net_value"] += value

    with output.open("w", newline="", encoding="utf-8") as handle:
        fields = ["product", "submitted_orders", "cancelled_orders", "net_value", "batch_processed_at"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        processed_at = datetime.now(timezone.utc).isoformat()
        for product in sorted(totals):
            values = totals[product]
            writer.writerow(
                {
                    "product": product,
                    "submitted_orders": values["submitted_orders"],
                    "cancelled_orders": values["cancelled_orders"],
                    "net_value": f"{values['net_value']:.2f}",
                    "batch_processed_at": processed_at,
                }
            )

    print(f"BATCH COMPLETE: read a closed input set and wrote {output}")
    print("Ask: how stale could this output be if the schedule runs nightly?")


if __name__ == "__main__":
    run_batch()
