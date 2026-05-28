#!/usr/bin/env python3
"""
Simple Kafka producer for Day 3 lab.

This script publishes a fixed number of messages to a specified topic.
It uses the Confluent Kafka Python client and requires that a local
broker is running on localhost:9092.  By default it sends to the
`logs` topic and configures acks=all to ensure durability.  Usage:

    python producer.py [topic]

The script will send ten messages with incrementing keys and flush
before exiting.
"""

from confluent_kafka import Producer
import sys


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered message to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else 'logs'
    producer_conf = {
        'bootstrap.servers': 'localhost:9092',
        'acks': 'all',
        'enable.idempotence': True
    }
    p = Producer(producer_conf)
    for i in range(10):
        key = str(i)
        value = f'message {i}'
        p.produce(topic, key=key, value=value, callback=delivery_report)
    p.flush()
    print(f'Produced 10 messages to topic "{topic}"')


if __name__ == '__main__':
    main()