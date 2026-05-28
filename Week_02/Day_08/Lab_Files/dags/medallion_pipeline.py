"""
Medallion pipeline DAG for Day 8 lab
-----------------------------------

This DAG demonstrates how to orchestrate a simple medallion pipeline in
Apache Airflow.  It contains three Python tasks that progressively
upgrade data from a Bronze table to Silver and then Gold.  A file
sensor waits for a CSV input file to arrive in the container's data
directory.  Once the file is present, the DAG loads the raw data into
the Bronze table, transforms and aggregates it, then writes the
results to Silver and Gold tables.  The transformation and loading
logic are deliberately simple so learners can focus on orchestration
concepts (scheduling, sensors, XComs, etc.).

Before running this DAG, ensure you have a CSV file at
``/opt/airflow/data/new_orders.csv`` containing columns ``order_id``,
``customer_id``, ``order_date``, ``quantity`` and ``total_amount``.
Airflow will automatically create the tables ``bronze_orders``,
``silver_orders`` and ``gold_order_summary`` in the PostgreSQL
database if they do not already exist.
"""

import csv
from datetime import datetime
from decimal import Decimal

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago
from sqlalchemy import create_engine, text

# Define a connection string to the Postgres database used by Airflow.
# In docker-compose.yml, the metadata database is available at
# postgres:5432 with user/password airflow.  We reuse the same
# database for storing our Bronze/Silver/Gold tables for the purposes
# of this lab.  In production you would typically separate your
# metadata and data storage.
PG_CONN = 'postgresql+psycopg2://airflow:airflow@postgres:5432/airflow'

def load_bronze(**context):
    """Read the raw CSV file and append it to the bronze_orders table."""
    file_path = '/opt/airflow/data/new_orders.csv'
    engine = create_engine(PG_CONN)
    with open(file_path, newline='', encoding='utf-8') as handle:
        rows = [
            {key.lower(): value for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS bronze_orders (
                order_id INTEGER,
                customer_id INTEGER,
                order_date TEXT,
                quantity INTEGER,
                total_amount NUMERIC
            )
        """))
        for row in rows:
            conn.execute(
                text("""
                    INSERT INTO bronze_orders
                    (order_id, customer_id, order_date, quantity, total_amount)
                    VALUES (:order_id, :customer_id, :order_date, :quantity, :total_amount)
                """),
                {
                    'order_id': int(row['order_id']),
                    'customer_id': int(row['customer_id']),
                    'order_date': row['order_date'],
                    'quantity': int(row['quantity']),
                    'total_amount': Decimal(row['total_amount']),
                },
            )
    context['ti'].xcom_push(key='records_loaded', value=len(rows))

def transform_silver(**context):
    """Transform bronze_orders into a cleansed silver_orders table."""
    engine = create_engine(PG_CONN)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS silver_orders"))
        conn.execute(text("""
            CREATE TABLE silver_orders AS
            SELECT
                order_id,
                customer_id,
                TO_DATE(order_date, 'YYYY-MM-DD') AS order_date,
                quantity,
                total_amount
            FROM bronze_orders
            WHERE quantity > 0
        """))
        silver_rows = conn.execute(text("SELECT COUNT(*) FROM silver_orders")).scalar_one()
    context['ti'].xcom_push(key='silver_rows', value=silver_rows)

def aggregate_gold(**context):
    """Aggregate silver_orders to create a gold summary table."""
    engine = create_engine(PG_CONN)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS gold_order_summary"))
        conn.execute(text("""
            CREATE TABLE gold_order_summary AS
            SELECT
                customer_id,
                SUM(total_amount) AS total_spent,
                COUNT(*) AS order_count,
                MAX(:processed_at) AS processed_at
            FROM silver_orders
            GROUP BY customer_id
        """), {'processed_at': datetime.utcnow()})
        gold_rows = conn.execute(text("SELECT COUNT(*) FROM gold_order_summary")).scalar_one()
    context['ti'].xcom_push(key='gold_rows', value=gold_rows)

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

with DAG(
    dag_id='medallion_pipeline',
    description='Orchestrate Bronze->Silver->Gold pipeline using Airflow',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    default_args=default_args,
    tags=['lab', 'medallion']
) as dag:
    # Wait for the file to arrive.  We set ``poke_interval`` low to
    # reduce latency in this lab; in production adjust this based on
    # expected arrival frequency.  The sensor times out after 1 hour.
    wait_for_csv = FileSensor(
        task_id='wait_for_csv',
        filepath='/opt/airflow/data/new_orders.csv',
        poke_interval=10,
        timeout=60 * 60,
        mode='reschedule'
    )

    load_bronze_task = PythonOperator(
        task_id='load_bronze',
        python_callable=load_bronze
    )

    transform_silver_task = PythonOperator(
        task_id='transform_silver',
        python_callable=transform_silver
    )

    aggregate_gold_task = PythonOperator(
        task_id='aggregate_gold',
        python_callable=aggregate_gold
    )

    wait_for_csv >> load_bronze_task >> transform_silver_task >> aggregate_gold_task
