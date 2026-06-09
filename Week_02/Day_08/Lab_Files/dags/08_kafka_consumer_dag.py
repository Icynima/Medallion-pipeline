"""
DAG 08 – Kafka Consumer Pipeline
==================================
Lab 8: Consume events from Kafka and process them through the medallion layers.

Concepts covered:
  - Consuming Kafka messages in Airflow
  - Event-driven batch processing (micro-batch)
  - Kafka → Bronze → Silver pipeline
  - Kafka offset management
  - Error handling for streaming data
  - Bridging streaming and batch worlds
"""

import json
import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task, task_group
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from sqlalchemy import create_engine, text

PG_CONN = os.environ.get(
    "WAREHOUSE_CONN",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:29092")
KAFKA_TOPIC = os.environ.get("KAFKA_ORDERS_TOPIC", "orders.raw")


@dag(
    dag_id="08_kafka_consumer_pipeline",
    description="Consume Kafka events → Bronze → Silver medallion layers",
    schedule_interval="*/5 * * * *",  # every 5 minutes (micro-batch)
    start_date=datetime(2026, 6, 1),
    catchup=False,
    max_active_runs=1,  # prevent overlapping runs
    default_args={
        "owner": "data-engineer",
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["lab", "kafka", "streaming"],
    doc_md=__doc__,
)
def kafka_consumer_pipeline():

    start = EmptyOperator(task_id="start")

    # ── Step 1: Check Kafka connectivity ──────────────────────

    @task()
    def check_kafka_health() -> dict:
        """Verify Kafka broker is reachable and topic exists."""
        try:
            from kafka import KafkaConsumer
            from kafka.admin import KafkaAdminClient

            admin = KafkaAdminClient(
                bootstrap_servers=KAFKA_BROKER,
                client_id="airflow-health-check",
            )
            topics = admin.list_topics()
            admin.close()

            status = {
                "broker": KAFKA_BROKER,
                "reachable": True,
                "topics": topics,
                "target_topic_exists": KAFKA_TOPIC in topics,
            }
        except Exception as e:
            status = {
                "broker": KAFKA_BROKER,
                "reachable": False,
                "error": str(e),
                "target_topic_exists": False,
            }

        print(f"Kafka health: {json.dumps(status, indent=2)}")
        return status

    # ── Step 2: Consume messages from Kafka ───────────────────

    @task()
    def consume_kafka_batch(health: dict) -> dict:
        """Consume a batch of messages from the Kafka topic."""
        if not health.get("reachable", False):
            print("Kafka not reachable – skipping consumption")
            return {"records": [], "count": 0}

        try:
            from helpers.kafka_utils import consume_batch

            records = consume_batch(
                topic=KAFKA_TOPIC,
                group_id="airflow-medallion-consumer",
                max_records=100,
                timeout_ms=10000,
            )
            print(f"Consumed {len(records)} records from '{KAFKA_TOPIC}'")
            for i, rec in enumerate(records[:5]):
                print(f"  [{i}] key={rec['key']}, offset={rec['offset']}")
            if len(records) > 5:
                print(f"  ... and {len(records) - 5} more")

            return {"records": records, "count": len(records)}

        except Exception as e:
            print(f"Kafka consumption error: {e}")
            return {"records": [], "count": 0, "error": str(e)}

    # ── Step 3: Write to Bronze (raw events) ──────────────────

    @task()
    def write_to_bronze(batch: dict) -> dict:
        """Write consumed Kafka events to bronze_kafka_events table."""
        records = batch.get("records", [])
        if not records:
            print("No records to write – skipping bronze load")
            return {"loaded": 0}

        engine = create_engine(PG_CONN)
        loaded = 0

        with engine.begin() as conn:
            for rec in records:
                conn.execute(
                    text("""
                        INSERT INTO bronze_kafka_events
                            (topic, partition_id, offset_id, key, payload, event_time)
                        VALUES
                            (:topic, :partition, :offset, :key,
                             :payload::jsonb, :event_time::timestamp)
                    """),
                    {
                        "topic": rec["topic"],
                        "partition": rec["partition"],
                        "offset": rec["offset"],
                        "key": rec["key"],
                        "payload": json.dumps(rec["value"]),
                        "event_time": rec["timestamp"],
                    },
                )
                loaded += 1

        print(f"Bronze: loaded {loaded} Kafka events")
        return {"loaded": loaded}

    # ── Step 4: Transform to Silver ───────────────────────────

    @task()
    def transform_kafka_to_silver(bronze_result: dict) -> dict:
        """Transform bronze Kafka events into silver_orders (structured)."""
        if bronze_result.get("loaded", 0) == 0:
            print("No new bronze data – skipping silver transform")
            return {"processed": 0}

        engine = create_engine(PG_CONN)
        with engine.begin() as conn:
            # Extract structured order data from JSONB payloads
            result = conn.execute(text("""
                INSERT INTO silver_orders
                    (order_id, customer_id, product_id, status, total_amount, order_date)
                SELECT
                    (payload->>'order_id')::INTEGER,
                    (payload->>'customer_id')::INTEGER,
                    payload->>'product_id',
                    payload->>'status',
                    (payload->>'amount')::NUMERIC,
                    CURRENT_DATE
                FROM bronze_kafka_events
                WHERE payload->>'order_id' IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM silver_orders s
                      WHERE s.order_id = (payload->>'order_id')::INTEGER
                  )
                ON CONFLICT (order_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    total_amount = EXCLUDED.total_amount,
                    _processed_at = CURRENT_TIMESTAMP
            """))

            count = conn.execute(text(
                "SELECT COUNT(*) FROM silver_orders"
            )).scalar_one()

        print(f"Silver orders total: {count}")
        return {"processed": count}

    # ── Step 5: Log execution ─────────────────────────────────

    @task()
    def log_kafka_run(bronze_result: dict, silver_result: dict):
        """Log the Kafka pipeline execution."""
        engine = create_engine(PG_CONN)
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO pipeline_execution_log
                        (dag_id, task_id, layer, table_name,
                         records_processed, status, started_at)
                    VALUES
                        ('08_kafka_consumer', 'summary', 'kafka',
                         'kafka_events', :records, 'success', :ts)
                """),
                {
                    "records": bronze_result.get("loaded", 0),
                    "ts": datetime.utcnow(),
                },
            )

        print(f"\n=== Kafka Pipeline Summary ===")
        print(f"  Kafka events consumed:  {bronze_result.get('loaded', 0)}")
        print(f"  Silver orders updated:  {silver_result.get('processed', 0)}")

    # ── Wire the pipeline ─────────────────────────────────────

    health = check_kafka_health()
    batch = consume_kafka_batch(health)
    bronze = write_to_bronze(batch)
    silver = transform_kafka_to_silver(bronze)

    start >> health
    log_kafka_run(bronze, silver)


kafka_consumer_pipeline()
