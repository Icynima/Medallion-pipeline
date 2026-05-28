"""A tiny durable event-notification channel and independent consumer."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from common import OUT, ensure_dir, read_jsonl, write_jsonl


INBOX = OUT / "events" / "order_notifications.jsonl"
CHECKPOINT = OUT / "events" / "notification_checkpoint.json"
OPERATIONS_LOG = OUT / "events" / "operations_notifications.txt"


def new_event() -> dict:
    return {
        "specversion": "1.0",
        "id": "ev-live-001",
        "source": "/lab/order-api",
        "type": "training.order.submitted.v1",
        "time": datetime.now(timezone.utc).isoformat(),
        "subject": "order/O-LIVE-002",
        "data": {"order_id": "O-LIVE-002", "customer_id": "C-041", "amount": 149.90},
    }


def produce() -> None:
    event = new_event()
    write_jsonl(INBOX, [event], append=True)
    print(f"PRODUCED {event['id']}: source work is durably recorded in {INBOX}.")
    print("The producer does not need a notification consumer to be online.")


def load_completed() -> set[str]:
    if CHECKPOINT.exists():
        return set(json.loads(CHECKPOINT.read_text(encoding="utf-8"))["completed_ids"])
    return set()


def store_completed(completed: set[str]) -> None:
    ensure_dir(CHECKPOINT.parent)
    CHECKPOINT.write_text(
        json.dumps({"completed_ids": sorted(completed)}, indent=2) + "\n",
        encoding="utf-8",
    )


def consume(unavailable: bool) -> int:
    completed = load_completed()
    pending = [event for event in read_jsonl(INBOX) if event["id"] not in completed]
    if not pending:
        print("No pending notifications. Existing event IDs are already checkpointed.")
        return 0
    for event in pending:
        print(f"CONSUMING {event['id']} for {event['subject']}")
        if unavailable:
            print("CONSUMER FAILED: operations notification endpoint is unavailable.")
            print("Event remains in the durable inbox; rerun consume after recovery.")
            return 1
        ensure_dir(OPERATIONS_LOG.parent)
        with OPERATIONS_LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"{event['time']} Notify operations about {event['subject']}\n")
        completed.add(event["id"])
        store_completed(completed)
        print(f"ACKNOWLEDGED {event['id']}; checkpoint written after successful action.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("produce")
    consume_parser = subparsers.add_parser("consume")
    consume_parser.add_argument("--fail-notification", action="store_true")
    args = parser.parse_args()
    if args.command == "produce":
        produce()
    else:
        raise SystemExit(consume(args.fail_notification))
