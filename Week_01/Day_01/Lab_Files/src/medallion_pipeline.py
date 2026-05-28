"""Build a tiny replayable Bronze/Silver/Gold data product from events."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from common import DATA, OUT, ensure_dir, read_jsonl, write_jsonl


BRONZE = OUT / "lake" / "bronze" / "order_events"
SILVER = OUT / "lake" / "silver" / "orders"
GOLD = OUT / "lake" / "gold" / "daily_product_sales"


def ingest_bronze(events: list[dict]) -> None:
    ingested_at = datetime.now(timezone.utc).isoformat()
    records = []
    for event in events:
        raw = json.dumps(event, sort_keys=True, separators=(",", ":"))
        records.append(
            {
                "ingested_at": ingested_at,
                "source_file": "order_events.jsonl",
                "raw_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                "raw_event": event,
            }
        )
    write_jsonl(BRONZE / "events.jsonl", records)


def conform_silver(events: list[dict]) -> list[dict]:
    current: dict[str, dict] = {}
    for event in events:
        data = event["data"]
        current[data["order_id"]] = {
            "order_id": data["order_id"],
            "customer_id": data["customer_id"],
            "product": data["product"].strip().lower(),
            "quantity": int(data["quantity"]),
            "unit_price": Decimal(str(data["unit_price"])),
            "status": data["status"],
            "event_time": event["time"],
            "source_event_id": event["id"],
        }
    rows = list(current.values())
    ensure_dir(SILVER)
    with (SILVER / "orders_current.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = list(rows[0])
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            rendered = dict(row)
            rendered["unit_price"] = f"{row['unit_price']:.2f}"
            writer.writerow(rendered)
    return rows


def publish_gold(rows: list[dict]) -> None:
    totals: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {"order_count": 0, "net_sales": Decimal("0.00")}
    )
    for row in rows:
        if row["status"] != "CANCELLED":
            totals[row["product"]]["order_count"] += 1
            totals[row["product"]]["net_sales"] += row["unit_price"] * row["quantity"]
    ensure_dir(GOLD)
    with (GOLD / "product_kpis.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["product", "order_count", "net_sales"])
        writer.writeheader()
        for product in sorted(totals):
            writer.writerow(
                {
                    "product": product,
                    "order_count": totals[product]["order_count"],
                    "net_sales": f"{totals[product]['net_sales']:.2f}",
                }
            )


def run() -> None:
    events = read_jsonl(DATA / "order_events.jsonl")
    ingest_bronze(events)
    silver_rows = conform_silver(events)
    publish_gold(silver_rows)
    print(f"BRONZE: raw evidence with ingestion metadata -> {BRONZE / 'events.jsonl'}")
    print(f"SILVER: typed current order view -> {SILVER / 'orders_current.csv'}")
    print(f"GOLD: product KPI output -> {GOLD / 'product_kpis.csv'}")


if __name__ == "__main__":
    run()
