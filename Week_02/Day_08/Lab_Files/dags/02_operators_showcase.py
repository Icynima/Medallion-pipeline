"""
DAG 02 – Operators Showcase
============================
Lab 2: Deep dive into Airflow's built-in operators.

Concepts covered:
  - BashOperator (templating with Jinja)
  - PythonOperator (passing op_args / op_kwargs)
  - PostgresOperator (SQL execution)
  - BranchPythonOperator (conditional branching)
  - ShortCircuitOperator (conditional skipping)
  - TriggerDagRunOperator (cross-DAG triggering)
  - Trigger rules (all_success, one_success, none_failed)
"""

import random
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator, ShortCircuitOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


# ── Callable functions ────────────────────────────────────────

def generate_random_number(**context):
    """Generate a random number and push it to XCom."""
    number = random.randint(1, 100)
    print(f"Generated number: {number}")
    context["ti"].xcom_push(key="random_number", value=number)
    return number


def decide_branch(**context):
    """Branch based on the random number: high (>50), medium (25-50), low (<25)."""
    number = context["ti"].xcom_pull(task_ids="generate_random_number", key="random_number")
    print(f"Evaluating number: {number}")
    if number > 50:
        return "high_value_path"
    elif number > 25:
        return "medium_value_path"
    else:
        return "low_value_path"


def check_is_weekday(**context):
    """Return True on weekdays (Mon-Fri), False on weekends.
    ShortCircuitOperator skips downstream tasks when False."""
    day = context["logical_date"].weekday()
    is_weekday = day < 5
    print(f"Day of week: {day} ({'weekday' if is_weekday else 'weekend'})")
    return is_weekday


def process_high_value(**context):
    number = context["ti"].xcom_pull(task_ids="generate_random_number", key="random_number")
    print(f"HIGH VALUE processing for number {number}")
    print("  → Sending priority notification")
    print("  → Flagging for review")


def process_medium_value(**context):
    number = context["ti"].xcom_pull(task_ids="generate_random_number", key="random_number")
    print(f"MEDIUM VALUE processing for number {number}")
    print("  → Standard processing")


def process_low_value(**context):
    number = context["ti"].xcom_pull(task_ids="generate_random_number", key="random_number")
    print(f"LOW VALUE processing for number {number}")
    print("  → Logging only")


# ── DAG definition ────────────────────────────────────────────

default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="02_operators_showcase",
    description="Showcase of Airflow operators: Bash, Python, Postgres, Branch, ShortCircuit",
    schedule_interval=None,
    start_date=datetime(2026, 6, 1),
    catchup=False,
    default_args=default_args,
    tags=["lab", "operators"],
    doc_md=__doc__,
) as dag:

    start = EmptyOperator(task_id="start")

    # ── BashOperator with Jinja templating ────────────────────
    bash_template = BashOperator(
        task_id="bash_with_template",
        bash_command="""
            echo "=== Jinja Templating Demo ==="
            echo "Logical date:    {{ ds }}"
            echo "Next run:        {{ next_ds }}"
            echo "DAG ID:          {{ dag.dag_id }}"
            echo "Task ID:         {{ task.task_id }}"
            echo "Run ID:          {{ run_id }}"
            echo "Execution date:  {{ execution_date }}"
        """,
    )

    # ── PostgresOperator – run SQL directly ───────────────────
    create_audit_table = PostgresOperator(
        task_id="create_audit_table",
        postgres_conn_id="warehouse_postgres",
        sql="""
            CREATE TABLE IF NOT EXISTS dag_audit_log (
                audit_id   SERIAL PRIMARY KEY,
                dag_id     VARCHAR(255),
                run_id     VARCHAR(255),
                message    TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
    )

    insert_audit = PostgresOperator(
        task_id="insert_audit_record",
        postgres_conn_id="warehouse_postgres",
        sql="""
            INSERT INTO dag_audit_log (dag_id, run_id, message)
            VALUES ('{{ dag.dag_id }}', '{{ run_id }}', 'Operators showcase executed');
        """,
    )

    # ── ShortCircuitOperator – skip downstream on weekends ────
    weekday_check = ShortCircuitOperator(
        task_id="weekday_only_gate",
        python_callable=check_is_weekday,
    )

    weekday_task = BashOperator(
        task_id="weekday_processing",
        bash_command="echo 'This only runs on weekdays!'",
    )

    # ── BranchPythonOperator – conditional paths ──────────────
    gen_number = PythonOperator(
        task_id="generate_random_number",
        python_callable=generate_random_number,
    )

    branch = BranchPythonOperator(
        task_id="decide_branch",
        python_callable=decide_branch,
    )

    high_path = PythonOperator(
        task_id="high_value_path",
        python_callable=process_high_value,
    )

    medium_path = PythonOperator(
        task_id="medium_value_path",
        python_callable=process_medium_value,
    )

    low_path = PythonOperator(
        task_id="low_value_path",
        python_callable=process_low_value,
    )

    # Join after branching – uses trigger_rule='none_failed_min_one_success'
    # because only one branch will execute
    join = EmptyOperator(
        task_id="join_after_branch",
        trigger_rule="none_failed_min_one_success",
    )

    end = EmptyOperator(
        task_id="end",
        trigger_rule="none_failed_min_one_success",
    )

    # ── Dependencies ──────────────────────────────────────────
    start >> bash_template
    start >> create_audit_table >> insert_audit

    start >> weekday_check >> weekday_task

    start >> gen_number >> branch
    branch >> [high_path, medium_path, low_path] >> join

    [bash_template, insert_audit, weekday_task, join] >> end
