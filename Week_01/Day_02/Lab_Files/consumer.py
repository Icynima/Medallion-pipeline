#!/usr/bin/env python3
"""
Kafka Consumer Example (Day 2 Lab)

This script demonstrates how to consume messages from an Apache Kafka
topic using the `kafka-python` library.  It reads events from the
beginning of the specified topic and prints the key, value and offset
information.  You can run multiple instances of this consumer with the
same `group_id` to see how Kafka partitions are assigned across
consumers.

Prerequisites:
  - Kafka cluster running locally at `localhost:9092` (use the provided
    Docker Compose file to start a broker).
  - The `kafka-python` library installed:  `pip install kafka-python`

Example usage:
  python consumer.py

During the lab, try changing the `group_id` to spawn separate consumer
groups and observe how they each receive all messages independently.
You can also toggle `auto_offset_reset` between `earliest` and `latest`
to control where new consumers start reading.
"""

from __future__ import annotations

from kafka import KafkaConsumer


def main() -> None:
    topic_name = "demo-topic"

    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=["localhost:9092"],
        group_id="demo-group",
        enable_auto_commit=True,
        auto_offset_reset="earliest",  # start from beginning if no committed offset
        value_deserializer=lambda x: x.decode("utf-8"),
        key_deserializer=lambda x: x.decode("utf-8") if x is not None else None,
    )

    print(f"Subscribed to topic {topic_name}, waiting for messages...\n")
    try:
        for message in consumer:
            key = message.key
            value = message.value
            partition = message.partition
            offset = message.offset
            print(f"Partition {partition}, offset {offset}, key={key}, value={value}")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()