"""
DAG 05 – XCom & TaskFlow API
==============================
Lab 5: Data passing between tasks using XCom and the modern TaskFlow API.

Concepts covered:
  - XCom push / pull (traditional)
  - @task decorator (TaskFlow API)
  - Automatic XCom with return values
  - Passing complex data (dicts, lists)
  - XCom limitations and best practices
  - Mixing traditional operators with TaskFlow
"""

import json
import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from sqlalchemy import create_engine, text

PG_CONN = os.environ.get(
    "WAREHOUSE_CONN",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)


# ── Traditional XCom approach ─────────────────────────────────

def extract_stats_traditional(**context):
    """Traditional approach: manually push/pull XCom values."""
    engine = create_engine(PG_CONN)
    stats = {}
    with engine.connect() as conn:
        for table in ["bronze_orders", "silver_orders", "gold_customer_360"]:
            try:
                count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar_one()
                stats[table] = count
            except Exception:
                stats[table] = 0

    # Push individual values
    ti = context["ti"]
    ti.xcom_push(key="table_stats", value=stats)
    ti.xcom_push(key="extraction_time", value=datetime.utcnow().isoformat())
    print(f"Extracted stats: {json.dumps(stats, indent=2)}")
    return stats


def report_traditional(**context):
    """Traditional approach: pull XCom values from upstream task."""
    ti = context["ti"]
    stats = ti.xcom_pull(task_ids="extract_stats_traditional", key="table_stats")
    extraction_time = ti.xcom_pull(task_ids="extract_stats_traditional", key="extraction_time")

    print(f"=== Pipeline Status Report (Traditional XCom) ===")
    print(f"Extraction time: {extraction_time}")
    if stats:
        for table, count in stats.items():
            layer = table.split("_")[0]
            print(f"  [{layer.upper():6s}] {table}: {count} rows")
    else:
        print("  No stats available – run the medallion pipeline first!")


# ── TaskFlow API (modern approach) ────────────────────────────

@dag(
    dag_id="05_xcom_and_taskflow",
    description="XCom and TaskFlow API – data passing between tasks",
    schedule_interval=None,
    start_date=datetime(2026, 6, 1),
    catchup=False,
    default_args={
        "owner": "data-engineer",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["lab", "xcom", "taskflow"],
    doc_md=__doc__,
)
def xcom_and_taskflow():

    # ── Section 1: Traditional XCom ───────────────────────────

    start = EmptyOperator(task_id="start")

    extract_trad = PythonOperator(
        task_id="extract_stats_traditional",
        python_callable=extract_stats_traditional,
    )

    report_trad = PythonOperator(
        task_id="report_traditional",
        python_callable=report_traditional,
    )

    # ── Section 2: TaskFlow API ───────────────────────────────

    @task()
    def extract_order_data() -> dict:
        """TaskFlow: return value is automatically pushed to XCom."""
        engine = create_engine(PG_CONN)
        with engine.connect() as conn:
            try:
                result = conn.execute(text("""
                    SELECT
                        COUNT(*)                    AS total_orders,
                        COUNT(DISTINCT customer_id) AS unique_customers,
                        SUM(total_amount)           AS total_revenue,
                        AVG(total_amount)           AS avg_order_value
                    FROM silver_orders
                """)).fetchone()
                return {
                    "total_orders": result[0],
                    "unique_customers": result[1],
                    "total_revenue": float(result[2]) if result[2] else 0,
                    "avg_order_value": float(result[3]) if result[3] else 0,
                }
            except Exception:
                return {"total_orders": 0, "unique_customers": 0,
                        "total_revenue": 0, "avg_order_value": 0}

    @task()
    def extract_customer_segments() -> dict:
        """Extract customer segment distribution."""
        engine = create_engine(PG_CONN)
        with engine.connect() as conn:
            try:
                rows = conn.execute(text("""
                    SELECT customer_segment, COUNT(*) as cnt
                    FROM gold_customer_360
                    GROUP BY customer_segment
                    ORDER BY cnt DESC
                """)).fetchall()
                return {row[0]: row[1] for row in rows}
            except Exception:
                return {"no_data": 0}

    @task()
    def calculate_kpis(order_data: dict, segments: dict) -> dict:
        """Combine data from multiple upstream tasks.
        TaskFlow automatically resolves XCom dependencies."""
        kpis = {
            "total_orders": order_data["total_orders"],
            "total_revenue": order_data["total_revenue"],
            "avg_order_value": order_data["avg_order_value"],
            "unique_customers": order_data["unique_customers"],
            "segments": segments,
            "revenue_per_customer": (
                order_data["total_revenue"] / order_data["unique_customers"]
                if order_data["unique_customers"] > 0
                else 0
            ),
        }
        print(f"=== Calculated KPIs ===")
        print(json.dumps(kpis, indent=2, default=str))
        return kpis

    @task()
    def generate_report(kpis: dict) -> str:
        """Generate a text report from KPIs."""
        report = [
            "╔══════════════════════════════════════════╗",
            "║     DAILY BUSINESS INTELLIGENCE REPORT   ║",
            "╠══════════════════════════════════════════╣",
            f"║ Total Orders:        {kpis['total_orders']:>18} ║",
            f"║ Total Revenue:     ${kpis['total_revenue']:>17,.2f} ║",
            f"║ Avg Order Value:   ${kpis['avg_order_value']:>17,.2f} ║",
            f"║ Unique Customers:    {kpis['unique_customers']:>18} ║",
            f"║ Revenue/Customer:  ${kpis['revenue_per_customer']:>17,.2f} ║",
            "╠══════════════════════════════════════════╣",
            "║ Customer Segments:                       ║",
        ]
        for segment, count in kpis.get("segments", {}).items():
            report.append(f"║   {segment:.<30} {count:>5} ║")
        report.append("╚══════════════════════════════════════════╝")

        report_text = "\n".join(report)
        print(report_text)
        return report_text

    @task()
    def save_report(report_text: str, kpis: dict):
        """Save the report to the pipeline_execution_log table."""
        engine = create_engine(PG_CONN)
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO pipeline_execution_log
                        (dag_id, task_id, layer, table_name,
                         records_processed, status, started_at)
                    VALUES
                        ('05_xcom_and_taskflow', 'save_report', 'gold',
                         'business_report', :records, 'success', :ts)
                """),
                {
                    "records": kpis.get("total_orders", 0),
                    "ts": datetime.utcnow(),
                },
            )
        print("Report saved to pipeline_execution_log")

    # ── Wire up the DAG ───────────────────────────────────────

    # Section 1: Traditional approach
    start >> extract_trad >> report_trad

    # Section 2: TaskFlow approach (dependencies inferred from function args)
    orders = extract_order_data()
    segments = extract_customer_segments()
    kpis = calculate_kpis(orders, segments)
    report = generate_report(kpis)
    save = save_report(report, kpis)

    start >> orders
    start >> segments

    # Sync point
    end = EmptyOperator(
        task_id="end",
        trigger_rule="none_failed_min_one_success",
    )
    [report_trad, save] >> end


# Instantiate the DAG
xcom_and_taskflow()
