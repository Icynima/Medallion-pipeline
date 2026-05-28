"""Demonstrate how a synchronous dependency can block valid source work."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone

from common import OUT, ensure_dir


def save_order(order: dict[str, str]) -> None:
    path = ensure_dir(OUT / "tight") / "committed_orders.csv"
    new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(order))
        if new_file:
            writer.writeheader()
        writer.writerow(order)


def send_notification(order: dict[str, str], unavailable: bool) -> None:
    if unavailable:
        raise ConnectionError("notification service is unavailable")
    path = ensure_dir(OUT / "tight") / "notifications.txt"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"Notify operations: {order['order_id']} accepted\n")


def submit_order(unavailable: bool) -> int:
    order = {
        "order_id": "O-LIVE-001",
        "customer_id": "C-041",
        "amount": "149.90",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    print("Order API received a valid order.")
    try:
        send_notification(order, unavailable)
        save_order(order)
    except ConnectionError as error:
        print(f"FAILED: {error}; the order was not committed.")
        print("Observation: a secondary dependency blocked primary work.")
        return 1
    print("SUCCESS: notification sent and order committed.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fail-notification", action="store_true")
    args = parser.parse_args()
    raise SystemExit(submit_order(args.fail_notification))
