"""
DAG 04 – Sensor Patterns & Scheduling
======================================
Lab 4: Master Airflow sensors and scheduling strategies.

Concepts covered:
  - FileSensor (poke vs reschedule mode)
  - SqlSensor (wait for data conditions)
  - ExternalTaskSensor (cross-DAG dependencies)
  - TimeDeltaSensor (time-based delays)
  - Schedule intervals (cron expressions, presets)
  - Trigger rules
  - SLA management
"""

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.time_delta import TimeDeltaSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator

from sqlalchemy import create_engine, text

PG_CONN = os.environ.get(
    "WAREHOUSE_CONN",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)


# ── Callable functions ────────────────────────────────────────

def check_data_freshness(**context):
    """Verify that bronze_orders has recent data."""
    engine = create_engine(PG_CONN)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) as cnt,
                   MAX(_loaded_at) as latest
            FROM bronze_orders
        """)).fetchone()

    count = result[0] if result else 0
    latest = result[1] if result else None

    print(f"Bronze orders count: {count}")
    print(f"Latest load time:    {latest}")

    if count == 0:
        raise ValueError("No data in bronze_orders – run the medallion pipeline first!")

    context["ti"].xcom_push(key="bronze_count", value=count)
    context["ti"].xcom_push(key="latest_load", value=str(latest))
    return count


def process_after_sensors(**context):
    """Process data after all sensors pass."""
    ti = context["ti"]
    bronze_count = ti.xcom_pull(task_ids="check_data_freshness", key="bronze_count")
    print(f"All sensors passed! Bronze data available: {bronze_count} rows")
    print("Proceeding with scheduled processing...")


def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Called when a task misses its SLA."""
    print(f"SLA MISS ALERT!")
    print(f"  DAG:            {dag.dag_id}")
    print(f"  Tasks affected: {[t.task_id for t in task_list]}")
    print(f"  Blocking tasks: {[t.task_id for t in blocking_tis]}")


# ── DAG definition ────────────────────────────────────────────

default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="04_sensor_patterns",
    description="Sensor patterns: File, SQL, TimeDelta, and scheduling strategies",
    # Cron expression: every 30 minutes during business hours (9-17) on weekdays
    schedule_interval="*/30 9-17 * * 1-5",
    start_date=datetime(2026, 6, 1),
    catchup=False,
    default_args=default_args,
    tags=["lab", "sensors", "scheduling"],
    doc_md=__doc__,
    sla_miss_callback=sla_miss_callback,
) as dag:

    start = EmptyOperator(task_id="start")

    # ── FileSensor ────────────────────────────────────────────
    # MODE: poke → keeps the worker slot while waiting
    #   - Good for short waits, uses less overhead
    #   - Blocks the worker slot
    wait_orders_poke = FileSensor(
        task_id="wait_orders_poke_mode",
        filepath="/opt/airflow/data/new_orders.csv",
        poke_interval=15,          # check every 15 seconds
        timeout=300,               # give up after 5 minutes
        mode="poke",               # hold the worker slot
        soft_fail=True,            # mark as SKIPPED instead of FAILED on timeout
    )

    # MODE: reschedule → frees the worker slot between pokes
    #   - Good for long waits, more resource efficient
    #   - Each poke is a separate task attempt
    wait_products_reschedule = FileSensor(
        task_id="wait_products_reschedule_mode",
        filepath="/opt/airflow/data/products.csv",
        poke_interval=30,
        timeout=600,
        mode="reschedule",         # release worker slot between checks
    )

    # ── SqlSensor ─────────────────────────────────────────────
    # Waits until a SQL query returns a truthy value
    wait_for_bronze_data = PostgresOperator(
        task_id="ensure_tables_exist",
        postgres_conn_id="warehouse_postgres",
        sql="""
            -- Create a flag table for sensor demo
            CREATE TABLE IF NOT EXISTS sensor_flags (
                flag_name VARCHAR(64) PRIMARY KEY,
                flag_value BOOLEAN DEFAULT FALSE,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            INSERT INTO sensor_flags (flag_name, flag_value)
            VALUES ('data_ready', TRUE)
            ON CONFLICT (flag_name) DO UPDATE SET flag_value = TRUE, updated_at = CURRENT_TIMESTAMP;
        """,
    )

    # ── TimeDeltaSensor ───────────────────────────────────────
    # Waits for a specified duration after the DAG's schedule time
    wait_5_seconds = TimeDeltaSensor(
        task_id="wait_5_seconds",
        delta=timedelta(seconds=5),
        mode="poke",
        poke_interval=2,
    )

    # ── Data freshness check ──────────────────────────────────
    freshness_check = PythonOperator(
        task_id="check_data_freshness",
        python_callable=check_data_freshness,
    )

    # ── Processing after sensors ──────────────────────────────
    process = PythonOperator(
        task_id="process_after_sensors",
        python_callable=process_after_sensors,
        # SLA: this task should complete within 2 minutes of the DAG start
        sla=timedelta(minutes=2),
    )

    # ── Show schedule info ────────────────────────────────────
    show_schedule = BashOperator(
        task_id="show_schedule_info",
        bash_command="""
            echo "=== Scheduling Concepts ==="
            echo ""
            echo "Common schedule_interval presets:"
            echo "  @once       – run exactly once"
            echo "  @hourly     – 0 * * * *"
            echo "  @daily      – 0 0 * * *"
            echo "  @weekly     – 0 0 * * 0"
            echo "  @monthly    – 0 0 1 * *"
            echo "  @yearly     – 0 0 1 1 *"
            echo "  None        – manual trigger only"
            echo ""
            echo "This DAG uses: */30 9-17 * * 1-5"
            echo "  (every 30 min, 9am-5pm, Mon-Fri)"
            echo ""
            echo "Current time: $(date)"
            echo "Logical date: {{ ds }}"
        """,
    )

    # ── Trigger rules demo ────────────────────────────────────
    always_runs = EmptyOperator(
        task_id="always_runs",
        trigger_rule="all_done",   # runs regardless of upstream success/failure
    )

    end = EmptyOperator(
        task_id="end",
        trigger_rule="none_failed_min_one_success",
    )

    # ── Dependencies ──────────────────────────────────────────
    start >> [wait_orders_poke, wait_products_reschedule]
    start >> wait_for_bronze_data
    start >> wait_5_seconds >> show_schedule

    [wait_orders_poke, wait_products_reschedule] >> freshness_check
    [freshness_check, wait_for_bronze_data] >> process

    [process, show_schedule] >> always_runs >> end
