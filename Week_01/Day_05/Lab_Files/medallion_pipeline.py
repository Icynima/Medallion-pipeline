#!/usr/bin/env python3
"""Local proof pipeline for Day 5 ingestion contracts and medallion layers."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
OUTPUT = ROOT / "outputs"
BRONZE = OUTPUT / "bronze"
SILVER = OUTPUT / "silver"
GOLD = OUTPUT / "gold"
QUARANTINE = OUTPUT / "quarantine"


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def write_json_records(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")


def read_json_records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array of records")
    return data


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stable_hash(row: dict) -> str:
    payload = json.dumps(row, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def reset_outputs() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    for path in (BRONZE, SILVER, GOLD, QUARANTINE):
        path.mkdir(parents=True, exist_ok=True)


def bronze_load() -> dict:
    reset_outputs()
    loaded_at = datetime.now(timezone.utc).isoformat()

    orders = []
    for row in read_json_records(INPUT / "orders_cdc.json"):
        row["_bronze_loaded_at"] = loaded_at
        row["_record_hash"] = stable_hash(row)
        orders.append(row)
    write_json_records(BRONZE / "orders_cdc.json", orders)

    clicks = []
    for row in read_json_records(INPUT / "clickstream_events.json"):
        row["_bronze_loaded_at"] = loaded_at
        row["_record_hash"] = stable_hash(row)
        clicks.append(row)
    write_json_records(BRONZE / "clickstream_events.json", clicks)

    shipments = []
    with (INPUT / "logistics_batch.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            row["_bronze_loaded_at"] = loaded_at
            row["_record_hash"] = stable_hash(row)
            shipments.append(row)
    write_json_records(BRONZE / "logistics_batch.json", shipments)

    return {
        "orders_bronze": len(orders),
        "clickstream_bronze": len(clicks),
        "logistics_bronze": len(shipments),
    }


def build_silver() -> dict:
    orders = read_json_records(BRONZE / "orders_cdc.json")
    seen_event_ids = set()
    duplicate_events = []
    current_orders = {}

    for event in sorted(orders, key=lambda r: (r["source_lsn"], r["event_id"])):
        if event["event_id"] in seen_event_ids:
            duplicate_events.append(event)
            continue
        seen_event_ids.add(event["event_id"])
        order_id = str(event["order_id"])
        if event["op"] == "d":
            current_orders.pop(order_id, None)
        else:
            current_orders[order_id] = {
                "order_id": order_id,
                "customer_id": str(event["customer_id"]),
                "order_date": event["order_ts"][:10],
                "status": event["status"],
                "amount": f"{float(event['amount']):.2f}",
                "last_source_lsn": str(event["source_lsn"]),
            }

    customers = {}
    with (INPUT / "customers.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            customers[row["customer_id"]] = row

    order_rows = sorted(current_orders.values(), key=lambda r: int(r["order_id"]))
    write_csv(
        SILVER / "orders_current.csv",
        order_rows,
        ["order_id", "customer_id", "order_date", "status", "amount", "last_source_lsn"],
    )
    write_json_records(QUARANTINE / "duplicate_events.json", duplicate_events)

    shipments_valid = []
    dlq = []
    known_orders = set(current_orders)
    for row in read_json_records(BRONZE / "logistics_batch.json"):
        errors = []
        if not row.get("shipment_id"):
            errors.append("missing shipment_id")
        if row.get("status") not in {"CREATED", "IN_TRANSIT", "DELIVERED"}:
            errors.append("invalid shipment status")
        if row.get("order_id") not in known_orders:
            errors.append("unknown order_id")
        if errors:
            dlq.append({"source": "logistics_batch", "errors": errors, "record": row})
        else:
            shipments_valid.append(
                {
                    "shipment_id": row["shipment_id"],
                    "order_id": row["order_id"],
                    "carrier": row["carrier"],
                    "status": row["status"],
                    "event_ts": row["event_ts"],
                }
            )
    write_csv(
        SILVER / "shipments_valid.csv",
        shipments_valid,
        ["shipment_id", "order_id", "carrier", "status", "event_ts"],
    )
    write_json_records(QUARANTINE / "dlq_logistics.json", dlq)

    dim_rows = []
    for customer in customers.values():
        dim_rows.append(
            {
                "customer_key": customer["customer_id"],
                "customer_id": customer["customer_id"],
                "customer_name": customer["customer_name"],
                "customer_tier": customer["customer_tier"],
                "region": customer["region"],
            }
        )
    write_csv(
        SILVER / "dim_customer.csv",
        sorted(dim_rows, key=lambda r: r["customer_id"]),
        ["customer_key", "customer_id", "customer_name", "customer_tier", "region"],
    )

    fact_rows = []
    for order in order_rows:
        cust = customers.get(order["customer_id"], {})
        fact_rows.append(
            {
                "order_id": order["order_id"],
                "order_date": order["order_date"],
                "customer_key": order["customer_id"],
                "region": cust.get("region", "UNKNOWN"),
                "status": order["status"],
                "amount": order["amount"],
            }
        )
    write_csv(
        SILVER / "fact_orders.csv",
        fact_rows,
        ["order_id", "order_date", "customer_key", "region", "status", "amount"],
    )

    quality_report = {
        "duplicate_events": len(duplicate_events),
        "valid_current_orders": len(order_rows),
        "valid_shipments": len(shipments_valid),
        "dlq_records": len(dlq),
        "latest_order_lsn": max(int(r["last_source_lsn"]) for r in order_rows),
    }
    (SILVER / "data_quality_report.json").write_text(
        json.dumps(quality_report, indent=2, sort_keys=True), encoding="utf-8"
    )
    return quality_report


def build_gold() -> dict:
    fact_path = SILVER / "fact_orders.csv"
    with fact_path.open(encoding="utf-8", newline="") as f:
        facts = list(csv.DictReader(f))

    daily = defaultdict(lambda: {"order_count": 0, "paid_or_shipped_count": 0, "revenue": 0.0})
    region = defaultdict(lambda: {"order_count": 0, "revenue": 0.0})
    for row in facts:
        daily_row = daily[row["order_date"]]
        daily_row["order_count"] += 1
        if row["status"] in {"PAID", "SHIPPED", "DELIVERED"}:
            daily_row["paid_or_shipped_count"] += 1
            daily_row["revenue"] += float(row["amount"])
        region_row = region[row["region"]]
        region_row["order_count"] += 1
        region_row["revenue"] += float(row["amount"])

    daily_rows = [
        {
            "order_date": date,
            "order_count": vals["order_count"],
            "paid_or_shipped_count": vals["paid_or_shipped_count"],
            "recognized_revenue": f"{vals['revenue']:.2f}",
        }
        for date, vals in sorted(daily.items())
    ]
    region_rows = [
        {
            "region": name,
            "order_count": vals["order_count"],
            "gross_order_amount": f"{vals['revenue']:.2f}",
        }
        for name, vals in sorted(region.items())
    ]
    write_csv(
        GOLD / "daily_order_kpis.csv",
        daily_rows,
        ["order_date", "order_count", "paid_or_shipped_count", "recognized_revenue"],
    )
    write_csv(
        GOLD / "region_order_summary.csv",
        region_rows,
        ["region", "order_count", "gross_order_amount"],
    )

    click_counts = Counter(row["event_type"] for row in read_json_records(BRONZE / "clickstream_events.json"))
    write_csv(
        GOLD / "clickstream_event_summary.csv",
        [{"event_type": k, "event_count": v} for k, v in sorted(click_counts.items())],
        ["event_type", "event_count"],
    )

    return {
        "daily_kpi_rows": len(daily_rows),
        "region_summary_rows": len(region_rows),
        "clickstream_summary_rows": len(click_counts),
    }


def validate_schema_proposals() -> list[dict]:
    proposals = json.loads((INPUT / "schema_change_proposals.json").read_text(encoding="utf-8"))
    out = []
    for item in proposals:
        status = "ACCEPT" if item["recommended_policy"] != "reject" else "REJECT"
        out.append({**item, "decision": status})
    (SILVER / "schema_change_decisions.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    return out


def run_all() -> dict:
    metrics = {}
    metrics.update(bronze_load())
    metrics.update(build_silver())
    metrics.update(build_gold())
    metrics["schema_change_proposals"] = len(validate_schema_proposals())
    metrics["generated_at"] = datetime.now(timezone.utc).isoformat()
    (OUTPUT / "run_summary.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8"
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["bronze", "silver", "gold", "all"])
    args = parser.parse_args()
    if args.command == "bronze":
        print(json.dumps(bronze_load(), indent=2, sort_keys=True))
    elif args.command == "silver":
        print(json.dumps(build_silver(), indent=2, sort_keys=True))
    elif args.command == "gold":
        print(json.dumps(build_gold(), indent=2, sort_keys=True))
    else:
        print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
