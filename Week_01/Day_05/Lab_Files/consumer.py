"""
Generic Kafka Consumer
----------------------
This script consumes messages from one or more topics and prints
them to the console.  Use this to observe events produced by
Debezium connectors, clickstream and CSV producers during the Day 5 lab.

Prerequisites:
  pip install kafka-python

Usage:
  python consumer.py topic1 topic2 ...
"""

import json
import sys
from kafka import KafkaConsumer


def main(topics):
    if not topics:
        print("Please specify at least one topic to consume from.")
        return
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="day5-consumer",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        key_deserializer=lambda m: m.decode("utf-8") if m else None,
    )
    print(f"Subscribed to topics: {topics}")
    try:
        for message in consumer:
            print(f"\nTopic: {message.topic}\nKey: {message.key}\nValue: {message.value}\nOffset: {message.offset}")
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main(sys.argv[1:])