"""
Environment Verification Script
================================
Checks that all Day 8 lab services are running and accessible.

Usage:
  docker compose exec airflow-web python /opt/airflow/scripts/verify_setup.py
  -- or from host --
  python scripts/verify_setup.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request


def check_postgres():
    """Verify PostgreSQL connectivity."""
    try:
        from sqlalchemy import create_engine, text

        conn_str = os.environ.get(
            "WAREHOUSE_CONN",
            "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow",
        )
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar_one()
            tables = conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)).fetchall()

        return {
            "status": "OK",
            "version": version.split(",")[0],
            "tables": [t[0] for t in tables],
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


def check_airflow():
    """Verify Airflow webserver health."""
    try:
        url = "http://localhost:8080/health"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
        return {
            "status": "OK",
            "metadatabase": data.get("metadatabase", {}).get("status"),
            "scheduler": data.get("scheduler", {}).get("status"),
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


def check_kafka():
    """Verify Kafka broker connectivity."""
    try:
        from kafka.admin import KafkaAdminClient

        broker = os.environ.get("KAFKA_BROKER", "localhost:9092")
        admin = KafkaAdminClient(
            bootstrap_servers=broker,
            client_id="verify-setup",
        )
        topics = admin.list_topics()
        admin.close()
        return {"status": "OK", "broker": broker, "topics": topics}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


def check_hop_web():
    """Verify Hop Web UI is accessible."""
    try:
        url = "http://localhost:8082"
        with urllib.request.urlopen(url, timeout=5) as resp:
            return {"status": "OK", "http_code": resp.status}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


def check_kafka_ui():
    """Verify Kafka UI is accessible."""
    try:
        url = "http://localhost:8081"
        with urllib.request.urlopen(url, timeout=5) as resp:
            return {"status": "OK", "http_code": resp.status}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}


def check_data_files():
    """Verify data files exist."""
    data_dir = os.environ.get("DATA_DIR", "./data")
    expected = ["new_orders.csv", "customers.csv", "products.csv"]
    results = {}
    for f in expected:
        path = os.path.join(data_dir, f)
        results[f] = os.path.exists(path)
    return {
        "status": "OK" if all(results.values()) else "PARTIAL",
        "files": results,
    }


def main():
    print("=" * 60)
    print("  Day 8 – Lab Environment Verification")
    print("=" * 60)
    print()

    checks = [
        ("PostgreSQL", check_postgres),
        ("Airflow WebUI", check_airflow),
        ("Apache Kafka", check_kafka),
        ("Hop Web UI", check_hop_web),
        ("Kafka UI", check_kafka_ui),
        ("Data Files", check_data_files),
    ]

    all_ok = True
    for name, check_fn in checks:
        result = check_fn()
        status = result.get("status", "UNKNOWN")
        icon = "OK" if status == "OK" else "FAIL"
        print(f"  [{icon:4s}] {name}")

        if status != "OK":
            all_ok = False
            error = result.get("error", "")
            if error:
                print(f"         Error: {error[:80]}")
        else:
            for k, v in result.items():
                if k != "status":
                    print(f"         {k}: {v}")
        print()

    print("=" * 60)
    if all_ok:
        print("  All checks passed! Lab environment is ready.")
    else:
        print("  Some checks failed. Review errors above.")
        print("  Run: docker compose up -d  (to start services)")
    print("=" * 60)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
