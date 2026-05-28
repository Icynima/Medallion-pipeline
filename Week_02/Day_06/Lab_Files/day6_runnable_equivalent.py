"""
Runnable equivalent for Day 6 Apache Hop lab tasks.

Apache Hop is a visual pipeline tool. This script reproduces the lab's
batch and streaming transformation logic with Python so the data results can
be validated in environments where Hop GUI/CLI is not installed.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from kafka import KafkaConsumer, KafkaProducer


BASE_DIR = Path(__file__).resolve().parent


def clean_customers() -> None:
    input_path = BASE_DIR / "customers.csv"
    output_path = BASE_DIR / "customers_cleaned.csv"
    seen: set[str] = set()
    rows: list[dict[str, str]] = []

    with input_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row["customer_id"] or not row["name"]:
                continue
            if row["customer_id"] in seen:
                continue
            seen.add(row["customer_id"])
            row["phone_normalized"] = row["phone"].replace("00", "+", 1)
            rows.append(row)

    rows.sort(key=lambda r: int(r["customer_id"]))
    fields = ["customer_id", "name", "phone_normalized", "country", "order_amount"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})

    print(f"Wrote {len(rows)} cleaned customers to {output_path.name}")


def enrich_orders() -> None:
    products_path = BASE_DIR / "products.csv"
    orders_path = BASE_DIR / "orders.csv"
    output_path = BASE_DIR / "enriched_orders.csv"

    with products_path.open(newline="", encoding="utf-8") as f:
        products = {row["product_id"]: row for row in csv.DictReader(f)}

    rows: list[dict[str, str]] = []
    with orders_path.open(newline="", encoding="utf-8") as f:
        for order in csv.DictReader(f):
            product = products.get(order["product_id"])
            if not product:
                continue
            rows.append(
                {
                    "order_id": order["order_id"],
                    "customer_id": order["customer_id"],
                    "product_id": order["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"].upper(),
                    "status": order["status"],
                    "amount": order["amount"],
                }
            )

    rows.sort(key=lambda r: (r["product_id"], int(r["order_id"])))
    fields = ["order_id", "customer_id", "product_id", "product_name", "category", "status", "amount"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} enriched orders to {output_path.name}")


def process_stream_once(expected_messages: int = 3) -> None:
    consumer = KafkaConsumer(
        "orders.cdc",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="day6-runnable-equivalent",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        key_serializer=lambda k: str(k).encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    seen_orders: set[int] = set()
    consumed = 0
    produced = 0
    idle_polls = 0
    try:
        while consumed < expected_messages and idle_polls < 5:
            msg = consumer.poll(timeout_ms=1500, max_records=10)
            if not msg:
                idle_polls += 1
                continue
            idle_polls = 0
            for records in msg.values():
                for record in records:
                    consumed += 1
                    event = record.value
                    order_id = event.get("order_id")
                    if event.get("status") != "NEW" or order_id in seen_orders:
                        continue
                    seen_orders.add(order_id)
                    producer.send("orders.cleaned", key=order_id, value=event)
                    produced += 1
    finally:
        producer.flush()
        producer.close()
        consumer.close()

    print(f"Consumed {consumed} events from orders.cdc")
    print(f"Produced {produced} deduplicated NEW events to orders.cleaned")


def main() -> None:
    clean_customers()
    enrich_orders()
    process_stream_once()


if __name__ == "__main__":
    main()
