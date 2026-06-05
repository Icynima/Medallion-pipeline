#!/usr/bin/env python3
"""Seed the Day 5 lab input files into Kafka topics once.

This script turns the static lab fixtures into Kafka events so the bronze
layer can be loaded by consuming topics instead of reading input files directly.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from uuid import uuid4

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
MANIFEST = ROOT / "kafka_topic_manifest.json"


def read_json_records(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def create_topics(bootstrap_servers: str) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    topics = [
        NewTopic(
            name=item["topic"],
            num_partitions=int(item["partitions"]),
            replication_factor=int(item["replication_factor"]),
        )
        for item in manifest
    ]
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="day5-topic-admin")
    try:
        admin.create_topics(topics, validate_only=False)
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--run-id", default=None, help="Optional run id for filtering this lab load")
    parser.add_argument("--skip-create-topics", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or str(uuid4())
    if not args.skip_create_topics:
        create_topics(args.bootstrap_servers)

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap_servers,
        key_serializer=lambda k: str(k).encode("utf-8") if k is not None else None,
        value_serializer=lambda v: json.dumps(v, sort_keys=True).encode("utf-8"),
    )

    counts = {
        "northstar.orders.public.orders": 0,
        "northstar.clickstream.events": 0,
        "northstar.logistics.csv": 0,
    }

    for row in read_json_records(INPUT / "orders_cdc.json"):
        event = {**row, "_lab_run_id": run_id}
        producer.send("northstar.orders.public.orders", key=row["order_id"], value=event)
        counts["northstar.orders.public.orders"] += 1

    for row in read_json_records(INPUT / "clickstream_events.json"):
        event = {**row, "_lab_run_id": run_id}
        producer.send("northstar.clickstream.events", key=row["user_id"], value=event)
        counts["northstar.clickstream.events"] += 1

    with (INPUT / "logistics_batch.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            event = {**row, "_lab_run_id": run_id}
            producer.send("northstar.logistics.csv", key=row.get("shipment_id") or None, value=event)
            counts["northstar.logistics.csv"] += 1

    producer.flush()
    producer.close()

    print(json.dumps({"run_id": run_id, "produced": counts}, indent=2, sort_keys=True))
    print(f"Next: python medallion_pipeline.py all-kafka --run-id {run_id}")


if __name__ == "__main__":
    main()
