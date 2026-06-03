#!/usr/bin/env python3
"""
Day 4 — Lab 2: Compare envelope vs flat CDC event formats.

This script consumes events from both envelope and flat topics side-by-side,
printing a formatted comparison so students can visually see the difference.
"""

from __future__ import annotations

import argparse
import json
import textwrap

from confluent_kafka import Consumer, KafkaException


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare envelope vs flat Debezium events side-by-side."
    )
    parser.add_argument(
        "--envelope-topic",
        default="inventory.public.customers",
        help="Envelope-format topic name.",
    )
    parser.add_argument(
        "--flat-topic",
        default="inventory_flat.public.customers-flat",
        help="Flat-format topic name.",
    )
    parser.add_argument(
        "--bootstrap",
        default="localhost:9092",
        help="Kafka bootstrap server.",
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=5,
        help="Max messages to consume per topic.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Total idle timeout in seconds.",
    )
    return parser.parse_args()


def decode(payload: bytes | None):
    if payload is None:
        return None
    text = payload.decode("utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def pretty(obj, indent: int = 2) -> str:
    if obj is None:
        return "null"
    return json.dumps(obj, indent=indent, default=str)


def consume_topic(bootstrap: str, topic: str, max_msgs: int, timeout: float) -> list:
    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap,
            "group.id": f"day4-compare-{topic}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topic])
    events = []
    idle = 0.0
    try:
        while len(events) < max_msgs and idle < timeout:
            msg = consumer.poll(1.0)
            if msg is None:
                idle += 1.0
                continue
            if msg.error():
                raise KafkaException(msg.error())
            idle = 0.0
            events.append(
                {
                    "key": decode(msg.key()),
                    "value": decode(msg.value()),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                }
            )
    finally:
        consumer.close()
    return events


def main() -> None:
    args = parse_args()

    print("=" * 80)
    print("  ENVELOPE FORMAT vs FLAT FORMAT — Side-by-Side Comparison")
    print("=" * 80)

    # Consume envelope events
    print(f"\n{'─' * 80}")
    print(f"  Consuming ENVELOPE events from: {args.envelope_topic}")
    print(f"{'─' * 80}")
    envelope_events = consume_topic(
        args.bootstrap, args.envelope_topic, args.max_messages, args.timeout
    )
    for i, evt in enumerate(envelope_events, 1):
        val = evt["value"]
        if val and isinstance(val, dict) and "payload" in val:
            val = val["payload"]
        print(f"\n  Event {i} (partition={evt['partition']}, offset={evt['offset']}):")
        if val and isinstance(val, dict):
            print(f"    op     = {val.get('op', 'N/A')}")
            print(f"    before = {json.dumps(val.get('before'), default=str)}")
            print(f"    after  = {json.dumps(val.get('after'), default=str)}")
            source = val.get("source", {})
            if source:
                print(f"    table  = {source.get('table', 'N/A')}")
                print(f"    lsn    = {source.get('lsn', 'N/A')}")
        else:
            print(f"    value  = {val}")

    # Consume flat events
    print(f"\n{'─' * 80}")
    print(f"  Consuming FLAT events from: {args.flat_topic}")
    print(f"{'─' * 80}")
    flat_events = consume_topic(
        args.bootstrap, args.flat_topic, args.max_messages, args.timeout
    )
    for i, evt in enumerate(flat_events, 1):
        val = evt["value"]
        print(f"\n  Event {i} (partition={evt['partition']}, offset={evt['offset']}):")
        if val and isinstance(val, dict):
            # Show all fields — flat format has everything at top level
            for k, v in val.items():
                label = f"    {k:20s}"
                print(f"{label} = {v}")
        else:
            print(f"    value  = {val}")

    # Summary
    print(f"\n{'=' * 80}")
    print("  SUMMARY")
    print(f"{'=' * 80}")
    print(f"  Envelope events consumed: {len(envelope_events)}")
    print(f"  Flat events consumed:     {len(flat_events)}")
    print()
    print("  Key differences:")
    print("  • Envelope: nested structure with before/after/source/op")
    print("  • Flat:     top-level fields with __op, __table, __deleted metadata")
    print("  • Envelope events are larger but contain full audit information")
    print("  • Flat events are simpler and easier for downstream sinks")


if __name__ == "__main__":
    main()
