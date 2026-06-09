"""
DAG 03 – Medallion Pipeline (Bronze → Silver → Gold)
=====================================================
Lab 3: Full medallion architecture in Airflow with FileSensor,
PythonOperator, XCom data passing, and PostgreSQL writes.

Concepts:
  - FileSensor (reschedule mode)
  - PythonOperator with **context
  - XCom push/pull for metadata tracking
  - SQL DDL/DML from Python
  - Pipeline execution logging
"""

import csv
import os
from datetime import datetime, timedelta
from decimal import Decimal

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago
from sqlalchemy import create_engine, text

PG_CONN = os.environ.get(
    "WAREHOUSE_CONN",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)


# ── Task functions ────────────────────────────────────────────

def load_bronze_orders(**context):
    """Read raw CSV and INSERT into bronze_orders (append-only)."""
    file_path = "/opt/airflow/data/new_orders.csv"
    engine = create_engine(PG_CONN)

    with open(file_path, newline="", encoding="utf-8") as fh:
        rows = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(fh)]

    with engine.begin() as conn:
        for row in rows:
            conn.execute(
                text("""
                    INSERT INTO bronze_orders
                        (order_id, customer_id, product_id, product_name,
                         category, quantity, unit_price, total_amount,
                         order_date, status, source)
                    VALUES
                        (:order_id, :customer_id, :product_id, :product_name,
                         :category, :quantity, :unit_price, :total_amount,
                         :order_date, :status, 'csv')
                """),
                {
                    "order_id": int(row["order_id"]),
                    "customer_id": int(row["customer_id"]),
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "category": row["category"],
                    "quantity": int(row["quantity"]),
                    "unit_price": Decimal(row["unit_price"]),
                    "total_amount": Decimal(row["total_amount"]),
                    "order_date": row["order_date"],
                    "status": row["status"],
                },
            )
    context["ti"].xcom_push(key="bronze_count", value=len(rows))
    return f"Loaded {len(rows)} rows into bronze_orders"


def load_bronze_customers(**context):
    """Read customers CSV into bronze_customers."""
    file_path = "/opt/airflow/data/customers.csv"
    engine = create_engine(PG_CONN)

    with open(file_path, newline="", encoding="utf-8") as fh:
        rows = [{k.lower(): v for k, v in row.items()} for row in csv.DictReader(fh)]

    with engine.begin() as conn:
        for row in rows:
            conn.execute(
                text("""
                    INSERT INTO bronze_customers
                        (customer_id, customer_name, email, city, country, signup_date)
                    VALUES
                        (:customer_id, :customer_name, :email, :city, :country, :signup_date)
                """),
                {
                    "customer_id": int(row["customer_id"]),
                    "customer_name": row["customer_name"],
                    "email": row.get("email", ""),
                    "city": row["city"],
                    "country": row["country"],
                    "signup_date": row["signup_date"],
                },
            )
    context["ti"].xcom_push(key="customers_count", value=len(rows))
    return f"Loaded {len(rows)} rows into bronze_customers"


def transform_silver_orders(**context):
    """Cleanse and deduplicate bronze → silver_orders."""
    engine = create_engine(PG_CONN)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM silver_orders"))
        conn.execute(text("""
            INSERT INTO silver_orders
                (order_id, customer_id, product_id, product_name,
                 category, quantity, unit_price, total_amount, order_date, status)
            SELECT DISTINCT ON (order_id)
                order_id, customer_id, product_id, product_name,
                category, quantity, unit_price, total_amount,
                TO_DATE(order_date, 'YYYY-MM-DD'), status
            FROM bronze_orders
            WHERE quantity > 0
              AND status != 'CANCELLED'
            ORDER BY order_id, _loaded_at DESC
        """))
        count = conn.execute(text("SELECT COUNT(*) FROM silver_orders")).scalar_one()
    context["ti"].xcom_push(key="silver_count", value=count)
    return f"Silver orders: {count} rows"


def transform_silver_customers(**context):
    """Cleanse bronze → silver_customers."""
    engine = create_engine(PG_CONN)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM silver_customers"))
        conn.execute(text("""
            INSERT INTO silver_customers
                (customer_id, customer_name, email, city, country, signup_date)
            SELECT DISTINCT ON (customer_id)
                customer_id,
                INITCAP(TRIM(customer_name)),
                LOWER(TRIM(email)),
                TRIM(city),
                UPPER(TRIM(country)),
                TO_DATE(signup_date, 'YYYY-MM-DD')
            FROM bronze_customers
            WHERE customer_name IS NOT NULL AND customer_name != ''
            ORDER BY customer_id, _loaded_at DESC
        """))
        count = conn.execute(text("SELECT COUNT(*) FROM silver_customers")).scalar_one()
    context["ti"].xcom_push(key="silver_customers", value=count)


def build_gold_customer_360(**context):
    """Join orders + customers to build a customer 360 gold table."""
    engine = create_engine(PG_CONN)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM gold_customer_360"))
        conn.execute(text("""
            INSERT INTO gold_customer_360
                (customer_id, customer_name, email, city, country,
                 total_orders, total_revenue, avg_order_value,
                 first_order_date, last_order_date, top_category, customer_segment)
            SELECT
                c.customer_id,
                c.customer_name,
                c.email,
                c.city,
                c.country,
                COUNT(o.order_id)                         AS total_orders,
                COALESCE(SUM(o.total_amount), 0)          AS total_revenue,
                COALESCE(AVG(o.total_amount), 0)          AS avg_order_value,
                MIN(o.order_date)                         AS first_order_date,
                MAX(o.order_date)                         AS last_order_date,
                MODE() WITHIN GROUP (ORDER BY o.category) AS top_category,
                CASE
                    WHEN SUM(o.total_amount) >= 200 THEN 'Premium'
                    WHEN SUM(o.total_amount) >= 50  THEN 'Regular'
                    ELSE 'New'
                END                                       AS customer_segment
            FROM silver_customers c
            LEFT JOIN silver_orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.customer_name, c.email, c.city, c.country
        """))
        count = conn.execute(
            text("SELECT COUNT(*) FROM gold_customer_360")
        ).scalar_one()
    context["ti"].xcom_push(key="gold_360_count", value=count)


def build_gold_daily_sales(**context):
    """Aggregate daily sales from silver_orders."""
    engine = create_engine(PG_CONN)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM gold_daily_sales"))
        conn.execute(text("""
            INSERT INTO gold_daily_sales
                (order_date, total_orders, total_revenue,
                 unique_customers, avg_order_value, top_product)
            SELECT
                order_date,
                COUNT(*)                                            AS total_orders,
                SUM(total_amount)                                   AS total_revenue,
                COUNT(DISTINCT customer_id)                         AS unique_customers,
                AVG(total_amount)                                   AS avg_order_value,
                MODE() WITHIN GROUP (ORDER BY product_name)         AS top_product
            FROM silver_orders
            GROUP BY order_date
            ORDER BY order_date
        """))
        count = conn.execute(
            text("SELECT COUNT(*) FROM gold_daily_sales")
        ).scalar_one()
    context["ti"].xcom_push(key="gold_daily_count", value=count)


def log_pipeline_result(**context):
    """Write a summary record to pipeline_execution_log."""
    engine = create_engine(PG_CONN)
    ti = context["ti"]
    bronze = ti.xcom_pull(task_ids="load_bronze_orders", key="bronze_count") or 0
    silver = ti.xcom_pull(task_ids="transform_silver_orders", key="silver_count") or 0
    gold = ti.xcom_pull(task_ids="build_gold_customer_360", key="gold_360_count") or 0

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO pipeline_execution_log
                    (dag_id, run_id, task_id, layer, table_name,
                     records_processed, status, started_at)
                VALUES
                    (:dag_id, :run_id, 'summary', 'all', 'medallion',
                     :total, 'success', :ts)
            """),
            {
                "dag_id": context["dag"].dag_id,
                "run_id": context["run_id"],
                "total": bronze + silver + gold,
                "ts": datetime.utcnow(),
            },
        )
    print(f"Pipeline complete: bronze={bronze}, silver={silver}, gold={gold}")


# ── DAG definition ────────────────────────────────────────────

default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="03_medallion_pipeline",
    description="Full Bronze → Silver → Gold medallion pipeline",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    default_args=default_args,
    tags=["lab", "medallion", "core"],
    doc_md=__doc__,
) as dag:

    # ── Sensors ───────────────────────────────────────────────
    wait_orders = FileSensor(
        task_id="wait_for_orders_csv",
        filepath="/opt/airflow/data/new_orders.csv",
        poke_interval=10,
        timeout=600,
        mode="reschedule",
    )

    wait_customers = FileSensor(
        task_id="wait_for_customers_csv",
        filepath="/opt/airflow/data/customers.csv",
        poke_interval=10,
        timeout=600,
        mode="reschedule",
    )

    # ── Bronze layer ──────────────────────────────────────────
    bronze_orders = PythonOperator(
        task_id="load_bronze_orders",
        python_callable=load_bronze_orders,
    )

    bronze_customers = PythonOperator(
        task_id="load_bronze_customers",
        python_callable=load_bronze_customers,
    )

    # ── Silver layer ──────────────────────────────────────────
    silver_orders = PythonOperator(
        task_id="transform_silver_orders",
        python_callable=transform_silver_orders,
    )

    silver_customers = PythonOperator(
        task_id="transform_silver_customers",
        python_callable=transform_silver_customers,
    )

    # ── Gold layer ────────────────────────────────────────────
    gold_360 = PythonOperator(
        task_id="build_gold_customer_360",
        python_callable=build_gold_customer_360,
    )

    gold_daily = PythonOperator(
        task_id="build_gold_daily_sales",
        python_callable=build_gold_daily_sales,
    )

    # ── Logging ───────────────────────────────────────────────
    log_result = PythonOperator(
        task_id="log_pipeline_result",
        python_callable=log_pipeline_result,
        trigger_rule="all_success",
    )

    # ── Dependencies ──────────────────────────────────────────
    # Parallel bronze loads → parallel silver transforms → parallel gold builds → log
    wait_orders >> bronze_orders >> silver_orders
    wait_customers >> bronze_customers >> silver_customers
    [silver_orders, silver_customers] >> gold_360
    silver_orders >> gold_daily
    [gold_360, gold_daily] >> log_result
