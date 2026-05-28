#!/usr/bin/env python3
"""
Simple Kafka consumer for Day 4 CDC lab.

This script connects to a Kafka broker running inside the Docker
Compose stack and consumes messages from a specified topic.  It
requires the `kafka-python` library, which can be installed via
`pip install kafka-python`.  Run the script after starting the
Docker Compose stack and registering the Debezium connector.  For
example:

    python3 consumer.py --topic inventory.public.customers-raw

You should see JSON-formatted change events printed to the console.
"""

import argparse
import json
from kafka import KafkaConsumer


def main():
    parser = argparse.ArgumentParser(description="Consume messages from a Kafka topic")
    parser.add_argument("--bootstrap-server", default="localhost:9092", help="Kafka bootstrap server (default: localhost:9092)")
    parser.add_argument("--topic", required=True, help="Kafka topic to consume from")
    parser.add_argument("--group-id", default="day4-consumer", help="Consumer group identifier")
    args = parser.parse_args()

    consumer = KafkaConsumer(
        args.topic,
        bootstrap_servers=args.bootstrap_server,
        group_id=args.group_id,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    )

    print(f"Consuming from topic {args.topic}. Press Ctrl+C to exit.")
    try:
        for msg in consumer:
            print(json.dumps(msg.value, indent=2))
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()