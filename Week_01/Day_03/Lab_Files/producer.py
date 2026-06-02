#!/usr/bin/env python3
"""
Kafka producer for Day 3 lab.

Publishes keyed JSON records with production-style settings.
Supports CLI arguments for topic, bootstrap server, count, and prefix.

Usage:
    python producer.py --topic orders-replicated --bootstrap localhost:9092 --count 12 --prefix day3-lab
"""

from confluent_kafka import Producer
import argparse
import json
import random


def delivery_report(err, msg):
    if err is not None:
        print(f"delivery=FAILED err={err}")
    else:
        print(f"delivery=ok topic={msg.topic()} partition={msg.partition()} offset={msg.offset()} key={msg.key().decode()}")


def main():
    parser = argparse.ArgumentParser(description='Day 3 Kafka Producer')
    parser.add_argument('--topic', default='logs', help='Target topic')
    parser.add_argument('--bootstrap', default='localhost:9092', help='Bootstrap servers')
    parser.add_argument('--count', type=int, default=10, help='Number of messages')
    parser.add_argument('--prefix', default='msg', help='Key prefix')
    args = parser.parse_args()

    producer_conf = {
        'bootstrap.servers': args.bootstrap,
        'acks': 'all',
        'enable.idempotence': True,
        'compression.type': 'snappy'
    }
    p = Producer(producer_conf)

    customers = ['C101', 'C102', 'C103', 'C104', 'C105']
    statuses = ['new', 'processing', 'shipped', 'delivered']

    for i in range(args.count):
        key = f"{args.prefix}-{i:03d}"
        value = json.dumps({
            "order_id": key,
            "customer": random.choice(customers),
            "amount": round(random.uniform(10, 200), 2),
            "status": random.choice(statuses)
        })
        p.produce(args.topic, key=key, value=value, callback=delivery_report)
    p.flush()
    print(f'Produced {args.count} messages to topic "{args.topic}"')


if __name__ == '__main__':
    main()
