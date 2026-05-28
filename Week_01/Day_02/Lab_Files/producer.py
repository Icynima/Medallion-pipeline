#!/usr/bin/env python3
"""
Kafka Producer Example (Day 2 Lab)

This script demonstrates how to produce messages to an Apache Kafka topic
from Python using the `kafka-python` library.  It sends a series of
simple text events with a key so you can observe how messages are
distributed across partitions.  You can modify the `topic_name`,
`num_messages` and key logic to experiment with different patterns.

Prerequisites:
  - Kafka cluster running locally at `localhost:9092` (use the provided
    Docker Compose file to start a broker).
  - The `kafka-python` library installed:  `pip install kafka-python`

Example usage:
  python producer.py

During the lab, try changing the key from a fixed value to a computed
value (e.g., based on the loop index) and observe how the records
distribute across partitions.  You can also adjust `acks` in the
producer configuration to experiment with different delivery guarantees.
"""

from __future__ import annotations

import json
import time
from typing import Any

from kafka import KafkaProducer


def json_serializer(data: Any) -> bytes:
    """Serialize Python objects to JSON encoded bytes."""
    return json.dumps(data).encode("utf-8")


def main() -> None:
    topic_name = "demo-topic"
    num_messages = 10

    # Configure the producer.  `acks` controls delivery semantics:
    # 0 = fire and forget, 1 = leader acknowledgment, -1/all = leader + replicas.
    producer = KafkaProducer(
        bootstrap_servers=["localhost:9092"],
        value_serializer=json_serializer,
        key_serializer=lambda k: k.encode("utf-8"),
        acks="all",
        linger_ms=5,
        batch_size=16384,
    )

    try:
        for i in range(num_messages):
            # Use a key to demonstrate partitioning.  Messages with the same key
            # will land in the same partition.  Try changing `key` to a
            # different value or derive from `i` to see the effect.
            key = "partition-key"
            value = {"id": i, "message": f"hello event {i}"}
            producer.send(topic_name, key=key, value=value)
            print(f"Sent message {i} to {topic_name}")
            time.sleep(0.1)
    finally:
        # Wait for all messages to be delivered before exiting
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()