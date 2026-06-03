#!/usr/bin/env python3
"""
Day 4 — Lab 3: Schema Evolution Demo.

Demonstrates how Debezium handles schema changes (ALTER TABLE)
by making changes to the PostgreSQL schema and observing the CDC events.
"""

from __future__ import annotations

import argparse
import json
import time

import psycopg2
import requests
from confluent_kafka import Consumer, KafkaException


BOOTSTRAP = "localhost:9092"
CONNECT_URL = "http://localhost:8083"
PG_DSN = "host=localhost port=5432 dbname=inventory user=postgres password=postgres"
TOPIC = "inventory.public.customers"


def wait_for_connect():
    """Wait until Kafka Connect is ready."""
    for _ in range(30):
        try:
            r = requests.get(f"{CONNECT_URL}/connectors", timeout=5)
            if r.status_code == 200:
                print("[OK] Kafka Connect is ready")
                return
        except requests.ConnectionError:
            pass
        time.sleep(2)
    raise RuntimeError("Kafka Connect did not become ready in time")


def get_connector_status(name: str) -> dict:
    r = requests.get(f"{CONNECT_URL}/connectors/{name}/status", timeout=5)
    return r.json()


def execute_sql(sql: str, fetch: bool = False):
    """Execute SQL against the Day 4 PostgreSQL instance."""
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall() if fetch else None
    cur.close()
    conn.close()
    return result


def consume_latest(topic: str, group: str, max_msgs: int = 3, timeout: float = 10.0) -> list:
    """Consume the latest messages from a topic."""
    consumer = Consumer(
        {
            "bootstrap.servers": BOOTSTRAP,
            "group.id": group,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topic])
    events = []
    idle = 0.0
    try:
        while len(events) < max_msgs and idle < timeout:
            msg = consumer.poll(1.0)
            if msg is None:
                idle += 1.0
                continue
            if msg.error():
                raise KafkaException(msg.error())
            idle = 0.0
            val = msg.value()
            if val:
                val = json.loads(val.decode("utf-8"))
            events.append(val)
    finally:
        consumer.close()
    return events


def print_section(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def print_event_schema(event: dict, label: str):
    """Print the schema/fields of a CDC event."""
    if event and isinstance(event, dict):
        payload = event.get("payload", event)
        after = payload.get("after", {})
        if after:
            print(f"\n  [{label}] Fields in 'after':")
            for k, v in after.items():
                print(f"    • {k}: {type(v).__name__} = {v}")
        else:
            print(f"\n  [{label}] No 'after' field (tombstone/delete)")


def main():
    parser = argparse.ArgumentParser(description="Schema evolution CDC demo.")
    parser.add_argument("--auto", action="store_true", help="Run all steps automatically.")
    args = parser.parse_args()

    print_section("Schema Evolution Demo — Day 4, Lab 3")
    print("  This demo shows how Debezium handles ALTER TABLE operations.")
    print("  We will add a column, rename a column, and change a type.")

    wait_for_connect()

    # Step 1: Show current schema
    print_section("Step 1: Current Table Schema")
    columns = execute_sql("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'customers' AND table_schema = 'public'
        ORDER BY ordinal_position;
    """, fetch=True)
    print("  Current 'customers' columns:")
    for col_name, data_type, nullable in columns:
        print(f"    • {col_name:20s} {data_type:20s} nullable={nullable}")

    if not args.auto:
        input("\n  Press Enter to proceed to Step 2 (ADD COLUMN)...")

    # Step 2: Add a column
    print_section("Step 2: ALTER TABLE — Add 'phone' Column")
    execute_sql("ALTER TABLE customers ADD COLUMN IF NOT EXISTS phone VARCHAR(20);")
    print("  [SQL] ALTER TABLE customers ADD COLUMN phone VARCHAR(20);")

    # Insert a row with the new column
    execute_sql("""
        INSERT INTO customers (name, email, balance, status, phone)
        VALUES ('Dave', 'dave@example.com', 300.00, 'active', '+1-555-0199');
    """)
    print("  [SQL] INSERT INTO customers ... (with phone='+1-555-0199')")

    time.sleep(3)  # Wait for CDC to propagate

    # Consume and show the event
    events = consume_latest(TOPIC, "schema-evo-step2")
    if events:
        # Find the event for Dave
        for evt in events:
            payload = evt.get("payload", evt) if evt else {}
            after = payload.get("after", {})
            if after and after.get("name") == "Dave":
                print_event_schema(evt, "New row with 'phone' column")
                break
        else:
            print_event_schema(events[-1], "Latest event")

    print("\n  ✓ Debezium automatically picks up the new column!")
    print("  The 'phone' field appears in the 'after' object of the CDC event.")

    if not args.auto:
        input("\n  Press Enter to proceed to Step 3 (UPDATE with new column)...")

    # Step 3: Update existing row to add phone
    print_section("Step 3: Update Existing Row with New Column")
    execute_sql("UPDATE customers SET phone = '+1-555-0100' WHERE name = 'Alice';")
    print("  [SQL] UPDATE customers SET phone = '+1-555-0100' WHERE name = 'Alice';")

    time.sleep(3)

    events = consume_latest(TOPIC, "schema-evo-step3")
    if events:
        for evt in events:
            payload = evt.get("payload", evt) if evt else {}
            if payload.get("op") == "u":
                after = payload.get("after", {})
                before = payload.get("before", {})
                if after and after.get("name") == "Alice":
                    print(f"\n  [UPDATE event]")
                    print(f"    before.phone = {before.get('phone', 'N/A') if before else 'N/A'}")
                    print(f"    after.phone  = {after.get('phone', 'N/A')}")
                    break

    if not args.auto:
        input("\n  Press Enter to proceed to Step 4 (ADD COLUMN with DEFAULT)...")

    # Step 4: Add column with default value
    print_section("Step 4: ALTER TABLE — Add Column with DEFAULT")
    execute_sql("""
        ALTER TABLE customers
        ADD COLUMN IF NOT EXISTS loyalty_tier VARCHAR(20) NOT NULL DEFAULT 'bronze';
    """)
    print("  [SQL] ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(20) DEFAULT 'bronze';")
    print()
    print("  ⚠️  Important: Adding a column with DEFAULT does NOT generate CDC events")
    print("     for existing rows.  Only NEW changes to existing rows will include")
    print("     the new column.  This is because PostgreSQL doesn't write to the WAL")
    print("     when adding a column with a default value (it's a metadata-only change).")

    # Trigger an update so we can see the column
    execute_sql("UPDATE customers SET loyalty_tier = 'gold' WHERE name = 'Bob';")
    print("  [SQL] UPDATE customers SET loyalty_tier = 'gold' WHERE name = 'Bob';")

    time.sleep(3)

    events = consume_latest(TOPIC, "schema-evo-step4")
    if events:
        for evt in events:
            payload = evt.get("payload", evt) if evt else {}
            after = payload.get("after", {})
            if after and after.get("name") == "Bob":
                print_event_schema(evt, "Bob with loyalty_tier")
                break

    if not args.auto:
        input("\n  Press Enter to proceed to Step 5 (DROP COLUMN)...")

    # Step 5: Drop a column
    print_section("Step 5: ALTER TABLE — Drop Column")
    execute_sql("ALTER TABLE customers DROP COLUMN IF EXISTS phone;")
    print("  [SQL] ALTER TABLE customers DROP COLUMN phone;")

    # Trigger an event
    execute_sql("UPDATE customers SET balance = balance + 10 WHERE name = 'Carol';")
    print("  [SQL] UPDATE customers SET balance = balance + 10 WHERE name = 'Carol';")

    time.sleep(3)

    events = consume_latest(TOPIC, "schema-evo-step5")
    if events:
        for evt in events:
            payload = evt.get("payload", evt) if evt else {}
            after = payload.get("after", {})
            if after and after.get("name") == "Carol":
                print_event_schema(evt, "Carol after DROP COLUMN phone")
                break

    print("\n  ✓ The 'phone' field no longer appears in CDC events.")
    print("  Debezium tracks schema changes and adjusts automatically.")

    # Summary
    print_section("Summary — Schema Evolution Behavior")
    print("""
  ┌─────────────────────────┬──────────────────────────────────────┐
  │ Schema Change           │ Debezium Behavior                    │
  ├─────────────────────────┼──────────────────────────────────────┤
  │ ADD COLUMN              │ New field appears in future events   │
  │ ADD COLUMN + DEFAULT    │ No events for existing rows;         │
  │                         │ field appears on next change         │
  │ DROP COLUMN             │ Field disappears from future events  │
  │ ALTER TYPE (compatible) │ Field type changes in future events  │
  │ RENAME COLUMN           │ Old name disappears, new name added  │
  └─────────────────────────┴──────────────────────────────────────┘

  Best practices:
  • Use compatible schema changes (add nullable columns, widen types)
  • Avoid renaming columns — consumers see it as drop + add
  • Test schema changes in non-prod first
  • Consider using Avro + Schema Registry for strict compatibility
    """)


if __name__ == "__main__":
    main()
