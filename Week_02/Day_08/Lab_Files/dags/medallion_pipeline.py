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

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago
import pandas as pd
from sqlalchemy import create_engine

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
    df = pd.read_csv(file_path)
    # Normalize column names (lowercase) for consistency
    df.columns = [c.lower() for c in df.columns]
    engine = create_engine(PG_CONN)
    # Create table if it does not exist; append data otherwise
    df.to_sql('bronze_orders', engine, if_exists='append', index=False)
    context['ti'].xcom_push(key='records_loaded', value=len(df))

def transform_silver(**context):
    """Transform bronze_orders into a cleansed silver_orders table."""
    engine = create_engine(PG_CONN)
    bronze_df = pd.read_sql('SELECT * FROM bronze_orders', engine)
    # Example transformation: filter out orders with zero quantity
    silver_df = bronze_df[bronze_df['quantity'] > 0].copy()
    # Standardise date format
    silver_df['order_date'] = pd.to_datetime(silver_df['order_date']).dt.date
    # Write to silver table (replace existing contents)
    silver_df.to_sql('silver_orders', engine, if_exists='replace', index=False)
    context['ti'].xcom_push(key='silver_rows', value=len(silver_df))

def aggregate_gold(**context):
    """Aggregate silver_orders to create a gold summary table."""
    engine = create_engine(PG_CONN)
    silver_df = pd.read_sql('SELECT * FROM silver_orders', engine)
    # Aggregate total amount by customer
    summary = silver_df.groupby('customer_id')['total_amount'].sum().reset_index()
    summary.rename(columns={'total_amount': 'total_spent'}, inplace=True)
    summary.to_sql('gold_order_summary', engine, if_exists='replace', index=False)
    context['ti'].xcom_push(key='gold_rows', value=len(summary))

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