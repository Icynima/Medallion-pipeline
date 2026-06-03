#!/usr/bin/env python3
"""
Day 4 — Lab 4: CDC Monitoring & Troubleshooting Tool.

Monitors Debezium connectors, Kafka topics, and PostgreSQL replication
slots to help students understand operational aspects of CDC pipelines.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import psycopg2
import requests
from confluent_kafka import Consumer, KafkaException
from confluent_kafka.admin import AdminClient, ConfigResource


CONNECT_URL = "http://localhost:8083"
BOOTSTRAP = "localhost:9092"
PG_DSN = "host=localhost port=5432 dbname=inventory user=postgres password=postgres"


def print_header(title: str):
    print(f"\n{'━' * 70}")
    print(f"  {title}")
    print(f"{'━' * 70}")


def print_ok(msg: str):
    print(f"  ✅ {msg}")


def print_warn(msg: str):
    print(f"  ⚠️  {msg}")


def print_fail(msg: str):
    print(f"  ❌ {msg}")


# ── Kafka Connect checks ─────────────────────────────────────────────

def check_connect_health() -> bool:
    """Check if Kafka Connect is reachable."""
    print_header("Kafka Connect Health")
    try:
        r = requests.get(f"{CONNECT_URL}/", timeout=5)
        info = r.json()
        print_ok(f"Connect version: {info.get('version', 'unknown')}")
        print_ok(f"Commit: {info.get('commit', 'unknown')}")
        print_ok(f"Kafka cluster ID: {info.get('kafka_cluster_id', 'unknown')}")
        return True
    except requests.ConnectionError:
        print_fail("Cannot reach Kafka Connect at " + CONNECT_URL)
        print("    Troubleshooting:")
        print("    • Is the connect container running?  docker ps | grep day4_connect")
        print("    • Check logs:  docker logs day4_connect --tail 50")
        return False


def list_connectors():
    """List all registered connectors and their status."""
    print_header("Registered Connectors")
    try:
        r = requests.get(f"{CONNECT_URL}/connectors?expand=status", timeout=5)
        connectors = r.json()
        if not connectors:
            print_warn("No connectors registered yet.")
            print("    Create one with:")
            print("    curl -X POST http://localhost:8083/connectors \\")
            print('      -H "Content-Type: application/json" \\')
            print("      -d @postgres-envelope-connector.json")
            return

        for name, details in connectors.items():
            status = details.get("status", {})
            conn_status = status.get("connector", {})
            state = conn_status.get("state", "UNKNOWN")
            worker = conn_status.get("worker_id", "unknown")

            icon = "✅" if state == "RUNNING" else "❌"
            print(f"  {icon} {name}")
            print(f"      State:  {state}")
            print(f"      Worker: {worker}")

            tasks = status.get("tasks", [])
            for task in tasks:
                task_state = task.get("state", "UNKNOWN")
                task_icon = "✅" if task_state == "RUNNING" else "❌"
                print(f"      {task_icon} Task {task['id']}: {task_state}")
                if task_state == "FAILED":
                    trace = task.get("trace", "No trace available")
                    # Show first 3 lines of error
                    lines = trace.strip().split("\n")[:3]
                    for line in lines:
                        print(f"         {line.strip()}")

    except requests.ConnectionError:
        print_fail("Cannot reach Kafka Connect")


def check_connector_config(name: str):
    """Show the configuration of a specific connector."""
    print_header(f"Connector Configuration: {name}")
    try:
        r = requests.get(f"{CONNECT_URL}/connectors/{name}/config", timeout=5)
        if r.status_code == 404:
            print_warn(f"Connector '{name}' not found")
            return
        config = r.json()
        # Group by category
        categories = {
            "Connection": ["database.hostname", "database.port", "database.user",
                          "database.dbname", "database.password"],
            "CDC Settings": ["plugin.name", "slot.name", "publication.name",
                            "snapshot.mode", "tombstones.on.delete"],
            "Filtering": ["schema.include.list", "table.include.list",
                         "column.include.list", "column.exclude.list"],
            "Topic": ["topic.prefix"],
            "Transforms": [],
        }
        shown_keys = set()
        for category, keys in categories.items():
            relevant = {k: config[k] for k in keys if k in config}
            if relevant:
                print(f"\n  {category}:")
                for k, v in relevant.items():
                    # Mask password
                    display_v = "********" if "password" in k else v
                    print(f"    {k}: {display_v}")
                    shown_keys.add(k)

        # Show transform configs
        transform_keys = {k: v for k, v in config.items() if k.startswith("transforms")}
        if transform_keys:
            print(f"\n  Transforms:")
            for k, v in sorted(transform_keys.items()):
                print(f"    {k}: {v}")
                shown_keys.add(k)

        # Show remaining
        remaining = {k: v for k, v in config.items()
                     if k not in shown_keys and k not in ("name", "connector.class", "tasks.max")}
        if remaining:
            print(f"\n  Other:")
            for k, v in sorted(remaining.items()):
                print(f"    {k}: {v}")

    except requests.ConnectionError:
        print_fail("Cannot reach Kafka Connect")


# ── Kafka topic checks ────────────────────────────────────────────────

def check_topics():
    """List CDC-related Kafka topics and their message counts."""
    print_header("Kafka Topics (CDC-related)")
    admin = AdminClient({"bootstrap.servers": BOOTSTRAP})
    try:
        metadata = admin.list_topics(timeout=10)
        topics = sorted(metadata.topics.keys())

        cdc_topics = [t for t in topics if not t.startswith("__") and not t.startswith("day4_connect")]
        internal_topics = [t for t in topics if t.startswith("day4_connect") or t.startswith("__")]

        if cdc_topics:
            print("\n  CDC / Data Topics:")
            for topic in cdc_topics:
                partitions = metadata.topics[topic].partitions
                print(f"    📋 {topic}  ({len(partitions)} partition(s))")

                # Get latest offsets
                consumer = Consumer({
                    "bootstrap.servers": BOOTSTRAP,
                    "group.id": "day4-monitor-temp",
                    "auto.offset.reset": "earliest",
                })
                total_msgs = 0
                for pid in partitions:
                    lo, hi = consumer.get_watermark_offsets(
                        consumer.list_topics(topic).topics[topic].partitions[pid],
                    ) if False else (0, 0)
                consumer.close()
        else:
            print_warn("No CDC topics found. Have you registered a connector?")

        if internal_topics:
            print(f"\n  Internal Topics ({len(internal_topics)}):")
            for topic in internal_topics[:5]:
                print(f"    🔧 {topic}")
            if len(internal_topics) > 5:
                print(f"    ... and {len(internal_topics) - 5} more")

    except Exception as e:
        print_fail(f"Cannot connect to Kafka: {e}")


def consume_sample(topic: str, n: int = 3):
    """Show a sample of recent messages from a topic."""
    print_header(f"Sample Messages from: {topic}")
    consumer = Consumer(
        {
            "bootstrap.servers": BOOTSTRAP,
            "group.id": f"day4-monitor-sample-{int(time.time())}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topic])
    consumed = 0
    idle = 0.0
    try:
        while consumed < n and idle < 10.0:
            msg = consumer.poll(1.0)
            if msg is None:
                idle += 1.0
                continue
            if msg.error():
                print_fail(f"Consumer error: {msg.error()}")
                continue
            idle = 0.0
            consumed += 1
            key = json.loads(msg.key().decode()) if msg.key() else None
            value = json.loads(msg.value().decode()) if msg.value() else None

            print(f"\n  Message {consumed} (partition={msg.partition()}, offset={msg.offset()}):")
            print(f"    Key: {json.dumps(key)}")
            if value and "payload" in value:
                payload = value["payload"]
                print(f"    Op:  {payload.get('op', 'N/A')}")
                if payload.get("after"):
                    print(f"    After: {json.dumps(payload['after'], default=str)}")
            elif value:
                print(f"    Value: {json.dumps(value, indent=2, default=str)[:200]}")
    finally:
        consumer.close()

    if consumed == 0:
        print_warn(f"No messages found in topic '{topic}'")


# ── PostgreSQL checks ─────────────────────────────────────────────────

def check_replication_slots():
    """Check PostgreSQL replication slot status."""
    print_header("PostgreSQL Replication Slots")
    try:
        conn = psycopg2.connect(PG_DSN)
        cur = conn.cursor()
        cur.execute("""
            SELECT slot_name, plugin, slot_type, active,
                   restart_lsn, confirmed_flush_lsn,
                   pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
            FROM pg_replication_slots;
        """)
        slots = cur.fetchall()
        cur.close()
        conn.close()

        if not slots:
            print_warn("No replication slots found.")
            print("    This means no Debezium connector has been started yet,")
            print("    or the connector was deleted and the slot was cleaned up.")
            return

        for slot in slots:
            name, plugin, slot_type, active, restart_lsn, flush_lsn, lag_bytes = slot
            status_icon = "✅" if active else "⚠️"
            print(f"\n  {status_icon} Slot: {name}")
            print(f"      Plugin:          {plugin}")
            print(f"      Type:            {slot_type}")
            print(f"      Active:          {active}")
            print(f"      Restart LSN:     {restart_lsn}")
            print(f"      Confirmed Flush: {flush_lsn}")
            if lag_bytes is not None:
                lag_mb = lag_bytes / (1024 * 1024)
                if lag_mb > 100:
                    print_fail(f"      Lag: {lag_mb:.2f} MB — CRITICAL! WAL is accumulating!")
                elif lag_mb > 10:
                    print_warn(f"      Lag: {lag_mb:.2f} MB — Getting behind")
                else:
                    print_ok(f"      Lag: {lag_bytes} bytes ({lag_mb:.4f} MB)")

            if not active:
                print_warn("      Slot is INACTIVE — WAL files will accumulate!")
                print("      Either start the connector or drop the slot:")
                print(f"      SELECT pg_drop_replication_slot('{name}');")

    except psycopg2.Error as e:
        print_fail(f"Cannot connect to PostgreSQL: {e}")


def check_pg_wal_status():
    """Check PostgreSQL WAL configuration and status."""
    print_header("PostgreSQL WAL Status")
    try:
        conn = psycopg2.connect(PG_DSN)
        cur = conn.cursor()

        # Check wal_level
        cur.execute("SHOW wal_level;")
        wal_level = cur.fetchone()[0]
        if wal_level == "logical":
            print_ok(f"wal_level = {wal_level}")
        else:
            print_fail(f"wal_level = {wal_level} (must be 'logical' for CDC!)")

        # Check max_replication_slots
        cur.execute("SHOW max_replication_slots;")
        max_slots = cur.fetchone()[0]
        print(f"  max_replication_slots = {max_slots}")

        # Check max_wal_senders
        cur.execute("SHOW max_wal_senders;")
        max_senders = cur.fetchone()[0]
        print(f"  max_wal_senders      = {max_senders}")

        # Current WAL position
        cur.execute("SELECT pg_current_wal_lsn();")
        current_lsn = cur.fetchone()[0]
        print(f"  Current WAL LSN      = {current_lsn}")

        # Check publications
        cur.execute("""
            SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete
            FROM pg_publication;
        """)
        pubs = cur.fetchall()
        if pubs:
            print(f"\n  Publications:")
            for pub_name, all_tables, ins, upd, dele in pubs:
                print(f"    📰 {pub_name} (all_tables={all_tables}, "
                      f"insert={ins}, update={upd}, delete={dele})")
        else:
            print_warn("No publications found (will be created by Debezium)")

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print_fail(f"Cannot connect to PostgreSQL: {e}")


def check_table_replica_identity():
    """Check REPLICA IDENTITY setting for monitored tables."""
    print_header("Table REPLICA IDENTITY Settings")
    try:
        conn = psycopg2.connect(PG_DSN)
        cur = conn.cursor()
        cur.execute("""
            SELECT c.relname, c.relreplident
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relkind = 'r'
            ORDER BY c.relname;
        """)
        tables = cur.fetchall()
        cur.close()
        conn.close()

        identity_map = {
            "d": "DEFAULT (primary key only)",
            "n": "NOTHING (no before image!)",
            "f": "FULL (all columns)",
            "i": "INDEX",
        }

        for table_name, identity in tables:
            desc = identity_map.get(identity, f"UNKNOWN ({identity})")
            if identity == "f":
                print_ok(f"{table_name:25s} → {desc}")
            elif identity == "d":
                print_warn(f"{table_name:25s} → {desc}")
                print(f"      Fix: ALTER TABLE {table_name} REPLICA IDENTITY FULL;")
            elif identity == "n":
                print_fail(f"{table_name:25s} → {desc}")
                print(f"      Fix: ALTER TABLE {table_name} REPLICA IDENTITY FULL;")

    except psycopg2.Error as e:
        print_fail(f"Cannot connect to PostgreSQL: {e}")


# ── Full diagnostic ───────────────────────────────────────────────────

def run_full_diagnostic():
    """Run all checks."""
    print("\n" + "█" * 70)
    print("  CDC PIPELINE DIAGNOSTIC REPORT")
    print(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("█" * 70)

    # PostgreSQL checks
    check_pg_wal_status()
    check_table_replica_identity()
    check_replication_slots()

    # Kafka Connect checks
    if check_connect_health():
        list_connectors()

    # Kafka topic checks
    check_topics()

    print_header("Diagnostic Complete")
    print("  If all checks show ✅, your CDC pipeline is healthy.")
    print("  If you see ⚠️ or ❌, follow the troubleshooting hints above.")


def main():
    parser = argparse.ArgumentParser(description="Day 4 CDC Monitoring Tool")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("full", help="Run full diagnostic")
    sub.add_parser("connect", help="Check Kafka Connect health")
    sub.add_parser("connectors", help="List all connectors")
    sub.add_parser("slots", help="Check PostgreSQL replication slots")
    sub.add_parser("wal", help="Check PostgreSQL WAL status")
    sub.add_parser("tables", help="Check table REPLICA IDENTITY")
    sub.add_parser("topics", help="List Kafka topics")

    p_config = sub.add_parser("config", help="Show connector configuration")
    p_config.add_argument("name", help="Connector name")

    p_sample = sub.add_parser("sample", help="Show sample messages from a topic")
    p_sample.add_argument("topic", help="Topic name")
    p_sample.add_argument("-n", type=int, default=3, help="Number of messages")

    args = parser.parse_args()

    if args.command == "full" or args.command is None:
        run_full_diagnostic()
    elif args.command == "connect":
        check_connect_health()
    elif args.command == "connectors":
        list_connectors()
    elif args.command == "slots":
        check_replication_slots()
    elif args.command == "wal":
        check_pg_wal_status()
    elif args.command == "tables":
        check_table_replica_identity()
    elif args.command == "topics":
        check_topics()
    elif args.command == "config":
        check_connector_config(args.name)
    elif args.command == "sample":
        consume_sample(args.topic, args.n)


if __name__ == "__main__":
    main()
