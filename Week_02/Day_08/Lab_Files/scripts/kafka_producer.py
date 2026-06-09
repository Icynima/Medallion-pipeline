"""
Kafka Order Event Producer
==========================
Generates realistic order events and sends them to the Kafka orders.raw topic.
Run from outside the containers:   python scripts/kafka_producer.py
Run from inside Airflow container: python /opt/airflow/scripts/kafka_producer.py

Usage:
  python kafka_producer.py                    # send 10 events
  python kafka_producer.py --count 50         # send 50 events
  python kafka_producer.py --continuous       # stream continuously
"""
from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BROKER", "localhost:9092")
TOPIC = os.environ.get("KAFKA_ORDERS_TOPIC", "orders.raw")

CUSTOMERS = list(range(101, 111))
PRODUCTS = [
    {"id": "P001", "name": "Wireless Mouse", "category": "Electronics", "price": 15.99},
    {"id": "P002", "name": "USB-C Cable", "category": "Electronics", "price": 9.99},
    {"id": "P003", "name": "Notebook A5", "category": "Stationery", "price": 3.50},
    {"id": "P004", "name": "Mechanical Keyboard", "category": "Electronics", "price": 89.99},
    {"id": "P005", "name": "Standing Desk Pad", "category": "Office", "price": 45.00},
    {"id": "P006", "name": "Monitor Light Bar", "category": "Electronics", "price": 59.99},
    {"id": "P007", "name": "Gel Pen Pack", "category": "Stationery", "price": 1.25},
    {"id": "P008", "name": "Webcam HD", "category": "Electronics", "price": 39.99},
    {"id": "P009", "name": "Ergonomic Chair", "category": "Office", "price": 299.99},
    {"id": "P010", "name": "Desk Organizer", "category": "Office", "price": 24.99},
]
STATUSES = ["NEW", "NEW", "NEW", "UPDATED", "COMPLETED"]


def generate_event(order_id: int) -> dict:
    """Generate a single order event."""
    product = random.choice(PRODUCTS)
    quantity = random.randint(1, 5)
    return {
        "order_id": order_id,
        "customer_id": random.choice(CUSTOMERS),
        "product_id": product["id"],
        "product_name": product["name"],
        "category": product["category"],
        "quantity": quantity,
        "unit_price": product["price"],
        "amount": round(product["price"] * quantity, 2),
        "status": random.choice(STATUSES),
        "event_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main():
    parser = argparse.ArgumentParser(description="Produce order events to Kafka")
    parser.add_argument("--count", type=int, default=10, help="Number of events to send")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between events (seconds)")
    parser.add_argument("--continuous", action="store_true", help="Stream events continuously")
    parser.add_argument("--broker", default=BOOTSTRAP_SERVERS, help="Kafka broker address")
    parser.add_argument("--topic", default=TOPIC, help="Kafka topic")
    args = parser.parse_args()

    print(f"Connecting to Kafka broker: {args.broker}")
    print(f"Target topic: {args.topic}")

    producer = KafkaProducer(
        bootstrap_servers=args.broker,
        key_serializer=lambda v: str(v).encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    order_id = 2001
    sent = 0

    try:
        while True:
            event = generate_event(order_id)
            producer.send(args.topic, key=event["order_id"], value=event)
            print(f"[{sent + 1}] Sent order {event['order_id']}: "
                  f"{event['product_name']} x{event['quantity']} = ${event['amount']:.2f} "
                  f"({event['status']})")

            order_id += 1
            sent += 1

            if not args.continuous and sent >= args.count:
                break

            time.sleep(args.delay)

    except KeyboardInterrupt:
        print(f"\nInterrupted after {sent} events")
    finally:
        producer.flush()
        producer.close()
        print(f"\nTotal events sent: {sent}")


if __name__ == "__main__":
    main()
