#!/usr/bin/env python3
"""Finite Debezium CDC topic inspector for Day 4 labs."""

from __future__ import annotations

import argparse
import json
from typing import Any

from confluent_kafka import Consumer, KafkaException


OP_CODES = {
    "c": "create",
    "u": "update",
    "d": "delete",
    "r": "read/snapshot",
    "t": "truncate",
    "m": "message",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect Debezium records from a Kafka topic.")
    parser.add_argument("--topic", required=True, help="Topic to consume.")
    parser.add_argument("--bootstrap", default="localhost:9092", help="Kafka bootstrap server.")
    parser.add_argument("--group", default="day4-python-inspector", help="Consumer group id.")
    parser.add_argument("--max-messages", type=int, default=5, help="Stop after this many records.")
    parser.add_argument("--timeout", type=float, default=20.0, help="Total idle timeout in seconds.")
    return parser.parse_args()


def decode(payload: bytes | None) -> Any:
    if payload is None:
        return None
    text = payload.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def describe_value(value: Any) -> dict[str, Any]:
    if value is None:
        return {
            "format": "tombstone",
            "value": None,
        }
    if isinstance(value, dict) and "payload" in value:
        value = value["payload"]
    if isinstance(value, dict) and {"before", "after", "op"}.issubset(value.keys()):
        before = value.get("before")
        after = value.get("after")
        op = value.get("op")
        op_label = OP_CODES.get(op, "unknown")
        table = (value.get("source") or {}).get("table")
        return {
            "format": "debezium_envelope",
            "op_code": op,
            "op_meaning": op_label,
            "table": table,
            "before": before,
            "after": after,
        }
    if isinstance(value, dict):
        op = value.get("__op")
        op_label = OP_CODES.get(op, "unknown")
        table = value.get("__table")
        deleted = value.get("__deleted")
        return {
            "format": "flat",
            "op_code": op,
            "op_meaning": op_label,
            "table": table,
            "deleted": deleted,
            "value": value,
        }
    return {
        "format": "raw",
        "value": value,
    }


def main() -> None:
    args = parse_args()
    consumer = Consumer(
        {
            "bootstrap.servers": args.bootstrap,
            "group.id": args.group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "client.id": "day4-cdc-inspector",
        }
    )
    consumer.subscribe([args.topic])
    print(f"inspector topic={args.topic} bootstrap={args.bootstrap} group={args.group}")
    idle = 0.0
    consumed = 0
    try:
        while consumed < args.max_messages and idle < args.timeout:
            msg = consumer.poll(1.0)
            if msg is None:
                idle += 1.0
                continue
            if msg.error():
                raise KafkaException(msg.error())
            idle = 0.0
            key = decode(msg.key())
            value = decode(msg.value())
            record = {
                "partition": msg.partition(),
                "offset": msg.offset(),
                "key": key,
                "event": describe_value(value),
            }
            print(json.dumps(record, indent=2, default=str))
            consumed += 1
    finally:
        consumer.close()
    print(f"consumed={consumed}")


if __name__ == "__main__":
    main()
