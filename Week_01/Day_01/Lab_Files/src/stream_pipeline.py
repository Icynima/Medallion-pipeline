"""Handle a sequence of arriving event notifications and write rolling state."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from decimal import Decimal

from common import DATA, OUT, ensure_dir, read_jsonl


STATE = OUT / "stream" / "rolling_state.json"
ALERTS = OUT / "stream" / "alerts.txt"


def handle_events(delay_seconds: float) -> None:
    totals: dict[str, Decimal] = {}
    count = 0
    ensure_dir(STATE.parent)
    if ALERTS.exists():
        ALERTS.unlink()
    for event in read_jsonl(DATA / "order_events.jsonl"):
        time.sleep(delay_seconds)
        data = event["data"]
        value = Decimal(str(data["quantity"])) * Decimal(str(data["unit_price"]))
        sign = -1 if data["status"] == "CANCELLED" else 1
        totals[data["product"]] = totals.get(data["product"], Decimal("0.00")) + sign * value
        count += 1
        observed = datetime.now(timezone.utc).isoformat()
        state = {
            "last_event_id": event["id"],
            "events_processed": count,
            "state_updated_at": observed,
            "net_value_by_product": {key: f"{value:.2f}" for key, value in sorted(totals.items())},
        }
        STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(f"HANDLED {event['id']} {event['type']} -> rolling state updated")
        if data["status"] == "CANCELLED":
            with ALERTS.open("a", encoding="utf-8") as handle:
                handle.write(f"{observed} REVIEW cancellation for {data['order_id']}\n")
    print(f"STREAM COMPLETE: {count} event notifications handled; inspect {STATE} and {ALERTS}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay-seconds", type=float, default=0.05)
    args = parser.parse_args()
    handle_events(args.delay_seconds)
