"""Real-time clickstream producer for the Day 5 lab."""

from __future__ import annotations

import argparse
import json
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from kafka import KafkaProducer


ROOT = Path(__file__).resolve().parent
TOPIC = "northstar.clickstream.events"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_fixture_events(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def random_event(users: list[dict]) -> dict:
    event_types = ["product_view", "cart_add", "checkout_start", "payment_submit"]
    user = random.choice(users)
    return {
        "event_id": f"clk-live-{uuid.uuid4().hex[:12]}",
        "event_ts": now_utc(),
        "event_type": random.choice(event_types),
        "order_id": random.choice([1001, 1002, 1003, None]),
        "session_id": user["session_id"],
        "user_id": user["user_id"],
    }


def send_event(producer: KafkaProducer, event: dict, run_id: str | None) -> None:
    message = dict(event)
    if run_id:
        message["_lab_run_id"] = run_id
    producer.send(TOPIC, key=message["user_id"], value=message)
    producer.flush()
    print(f"Produced clickstream event to {TOPIC}: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between events")
    parser.add_argument("--run-id", default=None, help="Optional run id for filtering a lab load")
    parser.add_argument(
        "--fixture",
        default=str(ROOT / "input" / "clickstream_events.json"),
        help="JSON fixture to replay before switching to live random events",
    )
    parser.add_argument("--fixture-only", action="store_true", help="Send the fixture once and exit")
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap_servers,
        key_serializer=lambda k: k.encode("utf-8"),
        value_serializer=lambda v: json.dumps(v, sort_keys=True).encode("utf-8"),
    )

    fixture_events = read_fixture_events(Path(args.fixture))
    users = [
        {"user_id": "u-501", "session_id": "s-live-501"},
        {"user_id": "u-502", "session_id": "s-live-502"},
        {"user_id": "u-777", "session_id": "s-live-777"},
    ]

    try:
        for event in fixture_events:
            send_event(producer, event, args.run_id)
            time.sleep(args.interval)

        if args.fixture_only:
            return

        while True:
            send_event(producer, random_event(users), args.run_id)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
