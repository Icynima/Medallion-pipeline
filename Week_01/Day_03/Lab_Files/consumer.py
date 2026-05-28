#!/usr/bin/env python3
"""
Simple Kafka consumer for Day 3 lab.

This script consumes messages from a specified topic as part of
experiments with offset management.  It disables auto commits and
commits offsets manually after processing each message.  Usage:

    python consumer.py [topic]

The consumer runs until interrupted (Ctrl+C).
"""

from confluent_kafka import Consumer
import sys


def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else 'logs'
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'cg_lab3',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }
    consumer = Consumer(conf)
    consumer.subscribe([topic])
    print(f'Started consuming from topic "{topic}"... Press Ctrl+C to stop.')
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f'Error: {msg.error()}')
                continue
            key = msg.key().decode() if msg.key() else None
            value = msg.value().decode() if msg.value() else None
            print(f'Received record key={key} value={value} partition={msg.partition()} offset={msg.offset()}')
            # Simulate processing then commit the message synchronously
            consumer.commit(msg)
    except KeyboardInterrupt:
        print('Stopping consumer...')
    finally:
        consumer.close()


if __name__ == '__main__':
    main()