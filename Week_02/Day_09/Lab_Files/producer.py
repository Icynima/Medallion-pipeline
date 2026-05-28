#!/usr/bin/env python3
"""
Simple Kafka producer for Day 9 lab.  This script reads a JSON file
containing order events and publishes each record to the `orders` topic
on the local Kafka cluster.  It uses the kafka-python client library.

Usage:
    python3 producer.py
    python3 producer.py orders.json

Ensure that the Kafka cluster defined in the provided docker-compose
configuration is running before executing this script.
"""
import json
import sys
import time
from kafka import KafkaProducer


def main(json_path: str):
    # Configure the producer to serialize values as JSON bytes
    producer = KafkaProducer(
        bootstrap_servers=["localhost:9092"],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: str(k).encode('utf-8') if k is not None else None
    )

    with open(json_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line: {line}")
                continue
            key = record.get('order_id')
            producer.send('orders', key=key, value=record)
            print(f"Sent order {key}")
            # small delay to simulate streaming
            time.sleep(0.1)
    producer.flush()
    producer.close()


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) == 2 else 'orders.json')
