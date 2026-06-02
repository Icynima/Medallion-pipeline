#!/usr/bin/env python3
"""
Kafka consumer for Day 3 lab.

Consumes messages with manual offset commits and CLI arguments.

Usage:
    python consumer.py --topic orders-replicated --bootstrap localhost:9092 --group cg-day3-python --max-messages 12 --reset earliest
"""

from confluent_kafka import Consumer
import argparse


def main():
    parser = argparse.ArgumentParser(description='Day 3 Kafka Consumer')
    parser.add_argument('--topic', default='logs', help='Topic to consume')
    parser.add_argument('--bootstrap', default='localhost:9092', help='Bootstrap servers')
    parser.add_argument('--group', default='cg_lab3', help='Consumer group ID')
    parser.add_argument('--max-messages', type=int, default=0, help='Max messages to consume (0=unlimited)')
    parser.add_argument('--reset', default='earliest', help='Auto offset reset policy')
    args = parser.parse_args()

    conf = {
        'bootstrap.servers': args.bootstrap,
        'group.id': args.group,
        'auto.offset.reset': args.reset,
        'enable.auto.commit': False
    }
    consumer = Consumer(conf)
    consumer.subscribe([args.topic])
    print(f'Started consuming from topic "{args.topic}" group "{args.group}"... Press Ctrl+C to stop.')
    count = 0
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                if args.max_messages > 0 and count >= args.max_messages:
                    break
                continue
            if msg.error():
                print(f"Error: {msg.error()}")
                continue
            key = msg.key().decode() if msg.key() else None
            value = msg.value().decode() if msg.value() else None
            print(f"key={key} value={value} partition={msg.partition()} offset={msg.offset()}")
            consumer.commit(msg)
            print(f"commit=ok partition={msg.partition()} offset={msg.offset()}")
            count += 1
            if args.max_messages > 0 and count >= args.max_messages:
                break
    except KeyboardInterrupt:
        print('Stopping consumer...')
    finally:
        consumer.close()
    print(f'Consumed {count} messages total.')


if __name__ == '__main__':
    main()
