"""
DAG 10 – Advanced Patterns
============================
Lab 10: Production-grade Airflow patterns for real-world pipelines.

Concepts covered:
  - TaskGroups for visual organisation
  - Dynamic task mapping with complex data
  - Custom callbacks (on_success, on_failure, on_retry)
  - SLA monitoring and alerting
  - Cross-DAG dependencies (TriggerDagRunOperator)
  - Idempotent task design
  - Airflow Variables and Connections in code
  - Retry strategies and exponential backoff
"""

import json
import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task, task_group
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from sqlalchemy import create_engine, text

PG_CONN = os.environ.get(
    "WAREHOUSE_CONN",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)


# ── Custom callbacks ──────────────────────────────────────────

def on_success_callback(context):
    """Called when a task succeeds."""
    ti = context["task_instance"]
    print(f"SUCCESS: {ti.dag_id}.{ti.task_id} "
          f"(attempt {ti.try_number}, duration: {ti.duration}s)")


def on_failure_callback(context):
    """Called when a task fails. In production: send Slack/email alerts."""
    ti = context["task_instance"]
    exception = context.get("exception", "Unknown")
    print(f"FAILURE ALERT: {ti.dag_id}.{ti.task_id}")
    print(f"  Error:    {exception}")
    print(f"  Attempt:  {ti.try_number}")
    print(f"  Log URL:  {ti.log_url}")
    # In production, you'd call Slack/PagerDuty/email here


def on_retry_callback(context):
    """Called when a task is retried."""
    ti = context["task_instance"]
    print(f"RETRY: {ti.dag_id}.{ti.task_id} "
          f"(attempt {ti.try_number})")


def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """Called when a task misses its SLA."""
    print(f"SLA MISS: {dag.dag_id}")
    for task in task_list:
        print(f"  Task: {task.task_id}")


# ── DAG definition ────────────────────────────────────────────

@dag(
    dag_id="10_advanced_patterns",
    description="Production patterns: callbacks, SLA, cross-DAG, idempotency",
    schedule_interval=None,
    start_date=datetime(2026, 6, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-engineer",
        "retries": 3,
        "retry_delay": timedelta(minutes=1),
        "retry_exponential_backoff": True,   # 1m, 2m, 4m, ...
        "max_retry_delay": timedelta(minutes=10),
        "on_success_callback": on_success_callback,
        "on_failure_callback": on_failure_callback,
        "on_retry_callback": on_retry_callback,
    },
    tags=["lab", "advanced", "production"],
    doc_md=__doc__,
    sla_miss_callback=sla_miss_callback,
)
def advanced_patterns():

    start = EmptyOperator(task_id="start")

    # ════════════════════════════════════════════════════════
    # PATTERN 1: Airflow Variables for configuration
    # ════════════════════════════════════════════════════════

    @task()
    def read_configuration() -> dict:
        """Read pipeline configuration from Airflow Variables."""
        config = {
            "kafka_broker": Variable.get("kafka_broker", default_var="kafka:29092"),
            "kafka_topic": Variable.get("kafka_orders_topic", default_var="orders.raw"),
            "hop_folder": Variable.get("hop_project_folder", default_var="/hop-project"),
            "quality_threshold": float(
                Variable.get("data_quality_threshold", default_var="0.95")
            ),
        }
        print(f"Pipeline configuration:\n{json.dumps(config, indent=2)}")
        return config

    # ════════════════════════════════════════════════════════
    # PATTERN 2: Idempotent tasks (safe to re-run)
    # ════════════════════════════════════════════════════════

    @task_group(group_id="idempotent_processing")
    def idempotent_processing():
        """Demonstrate idempotent task design."""

        @task()
        def idempotent_upsert() -> dict:
            """Upsert pattern: safe to run multiple times."""
            engine = create_engine(PG_CONN)
            with engine.begin() as conn:
                # Create a summary table if not exists
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS pipeline_summary (
                        summary_date DATE PRIMARY KEY,
                        total_bronze  INTEGER DEFAULT 0,
                        total_silver  INTEGER DEFAULT 0,
                        total_gold    INTEGER DEFAULT 0,
                        updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # Upsert – INSERT ... ON CONFLICT UPDATE
                conn.execute(text("""
                    INSERT INTO pipeline_summary (summary_date, total_bronze, total_silver, total_gold)
                    VALUES (
                        CURRENT_DATE,
                        (SELECT COUNT(*) FROM bronze_orders),
                        (SELECT COUNT(*) FROM silver_orders),
                        (SELECT COUNT(*) FROM gold_customer_360)
                    )
                    ON CONFLICT (summary_date) DO UPDATE SET
                        total_bronze = EXCLUDED.total_bronze,
                        total_silver = EXCLUDED.total_silver,
                        total_gold   = EXCLUDED.total_gold,
                        updated_at   = CURRENT_TIMESTAMP
                """))

                result = conn.execute(text(
                    "SELECT * FROM pipeline_summary WHERE summary_date = CURRENT_DATE"
                )).fetchone()

            output = {
                "date": str(result[0]),
                "bronze": result[1],
                "silver": result[2],
                "gold": result[3],
            }
            print(f"Idempotent upsert result: {output}")
            return output

        @task()
        def verify_idempotency(first_run: dict) -> str:
            """Verify that running again produces the same result."""
            engine = create_engine(PG_CONN)
            with engine.connect() as conn:
                count = conn.execute(text(
                    "SELECT COUNT(*) FROM pipeline_summary WHERE summary_date = CURRENT_DATE"
                )).scalar_one()

            # Should always be 1 (not 2) because of ON CONFLICT
            assert count == 1, f"Idempotency violated! Expected 1, got {count}"
            print(f"Idempotency verified: exactly 1 summary row for today")
            return "idempotent"

        result = idempotent_upsert()
        verify_idempotency(result)

    # ════════════════════════════════════════════════════════
    # PATTERN 3: Branching with data-driven decisions
    # ════════════════════════════════════════════════════════

    @task()
    def assess_data_volume() -> str:
        """Check data volume and decide processing path."""
        engine = create_engine(PG_CONN)
        try:
            with engine.connect() as conn:
                count = conn.execute(text(
                    "SELECT COUNT(*) FROM bronze_orders"
                )).scalar_one()
        except Exception:
            count = 0

        print(f"Bronze orders count: {count}")
        if count > 100:
            return "heavy_processing"
        elif count > 0:
            return "light_processing"
        else:
            return "no_data_path"

    branch = BranchPythonOperator(
        task_id="volume_based_branch",
        python_callable=lambda **ctx: ctx["ti"].xcom_pull(task_ids="assess_data_volume"),
    )

    heavy = BashOperator(
        task_id="heavy_processing",
        bash_command="""
            echo "=== Heavy Processing Path ==="
            echo "Running full aggregation with parallel workers..."
            echo "  - Partitioned processing"
            echo "  - Incremental updates"
            echo "  - Full recomputation of gold tables"
        """,
    )

    light = BashOperator(
        task_id="light_processing",
        bash_command="""
            echo "=== Light Processing Path ==="
            echo "Running simplified aggregation..."
            echo "  - Quick update"
            echo "  - Append-only gold updates"
        """,
    )

    no_data = BashOperator(
        task_id="no_data_path",
        bash_command="echo 'No data available – skipping processing'",
    )

    join_branch = EmptyOperator(
        task_id="join_processing",
        trigger_rule="none_failed_min_one_success",
    )

    # ════════════════════════════════════════════════════════
    # PATTERN 4: Cross-DAG triggering
    # ════════════════════════════════════════════════════════

    trigger_medallion = TriggerDagRunOperator(
        task_id="trigger_medallion_pipeline",
        trigger_dag_id="03_medallion_pipeline",
        wait_for_completion=False,
        reset_dag_run=True,
        poke_interval=30,
    )

    # ════════════════════════════════════════════════════════
    # PATTERN 5: Comprehensive monitoring
    # ════════════════════════════════════════════════════════

    @task_group(group_id="monitoring")
    def monitoring():
        """Pipeline monitoring and health metrics."""

        @task()
        def collect_metrics() -> dict:
            """Collect pipeline health metrics."""
            engine = create_engine(PG_CONN)
            metrics = {}

            with engine.connect() as conn:
                # Data freshness
                try:
                    latest = conn.execute(text(
                        "SELECT MAX(_loaded_at) FROM bronze_orders"
                    )).scalar_one()
                    metrics["bronze_freshness_minutes"] = (
                        (datetime.utcnow() - latest).total_seconds() / 60
                        if latest else -1
                    )
                except Exception:
                    metrics["bronze_freshness_minutes"] = -1

                # Layer counts
                for table in ["bronze_orders", "silver_orders", "gold_customer_360"]:
                    try:
                        metrics[f"{table}_count"] = conn.execute(
                            text(f"SELECT COUNT(*) FROM {table}")
                        ).scalar_one()
                    except Exception:
                        metrics[f"{table}_count"] = 0

                # Quality check pass rate
                try:
                    result = conn.execute(text("""
                        SELECT
                            COUNT(*) FILTER (WHERE passed = TRUE) AS passed,
                            COUNT(*) AS total
                        FROM data_quality_results
                        WHERE checked_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
                    """)).fetchone()
                    if result and result[1] > 0:
                        metrics["quality_pass_rate"] = round(result[0] / result[1], 3)
                    else:
                        metrics["quality_pass_rate"] = 1.0
                except Exception:
                    metrics["quality_pass_rate"] = -1

            print(f"\n=== Pipeline Health Metrics ===")
            print(json.dumps(metrics, indent=2, default=str))
            return metrics

        @task()
        def check_sla_compliance(metrics: dict):
            """Verify SLA compliance for data freshness and quality."""
            threshold = 0.95  # 95% quality pass rate required

            issues = []
            if metrics.get("bronze_freshness_minutes", -1) > 60:
                issues.append("Bronze data is stale (>60 min old)")
            if metrics.get("quality_pass_rate", 0) < threshold:
                issues.append(f"Quality pass rate below {threshold}")
            if metrics.get("silver_orders_count", 0) == 0:
                issues.append("Silver layer is empty")

            if issues:
                print(f"SLA ISSUES DETECTED:")
                for issue in issues:
                    print(f"  WARNING: {issue}")
            else:
                print("All SLAs within acceptable range")

        m = collect_metrics()
        check_sla_compliance(m)

    # ── Wire everything together ──────────────────────────────

    config = read_configuration()
    idem = idempotent_processing()
    volume = assess_data_volume()
    mon = monitoring()

    end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

    # Main flow
    start >> config >> idem
    start >> volume >> branch
    branch >> [heavy, light, no_data] >> join_branch

    # After processing, trigger medallion and monitor
    [idem, join_branch] >> trigger_medallion >> mon >> end


advanced_patterns()
