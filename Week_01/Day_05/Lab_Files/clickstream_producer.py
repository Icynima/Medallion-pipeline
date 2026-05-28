"""
Clickstream Producer
---------------------
This script simulates a stream of user click events and publishes them
to the `northstar.clickstream.events` topic.  Each message is
serialized as JSON and keyed by the user ID to ensure events from the
same user land in the same partition.

Run this script after your Kafka cluster is running.  It will
continue to produce events until you stop it (Ctrl‑C).

Prerequisites:
  pip install kafka-python
"""

import json
import random
import time
import uuid
from datetime import datetime
from kafka import KafkaProducer


def main():
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        key_serializer=lambda k: k.encode("utf-8"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    pages = ["home", "search", "product", "cart", "checkout"]
    users = [str(uuid.uuid4()) for _ in range(5)]
    try:
        while True:
            user_id = random.choice(users)
            event = {
                "user_id": user_id,
                "page": random.choice(pages),
                "event_time": datetime.utcnow().isoformat() + "Z"
            }
            producer.send("northstar.clickstream.events", key=user_id, value=event)
            producer.flush()
            print(f"Produced event: {event}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.close()


if __name__ == "__main__":
    main()