"""
DAG 01 – Hello Airflow
======================
Lab 1: Your first DAG! Learn the fundamental building blocks.

Concepts covered:
  - DAG definition & default_args
  - BashOperator – run shell commands
  - PythonOperator – run Python functions
  - Task dependencies (>> operator)
  - Viewing logs in the Airflow UI
  - Manual triggering
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

# ── Default arguments applied to every task ──────────────────

default_args = {
    "owner": "data-engineer",          # shows in the Airflow UI
    "depends_on_past": False,          # each run is independent
    "email_on_failure": False,
    "retries": 1,                      # retry once on failure
    "retry_delay": timedelta(minutes=1),
}


# ── Python callables ─────────────────────────────────────────

def greet(**context):
    """A simple function that prints a greeting with execution context."""
    execution_date = context["logical_date"]
    dag_id = context["dag"].dag_id
    task_id = context["task"].task_id
    print(f"Hello from Airflow!")
    print(f"  DAG:            {dag_id}")
    print(f"  Task:           {task_id}")
    print(f"  Execution date: {execution_date}")
    print(f"  Run ID:         {context['run_id']}")
    return "Greeting complete"


def show_environment(**context):
    """Print key environment info to demonstrate PythonOperator."""
    import os
    import platform

    print(f"Python version:  {platform.python_version()}")
    print(f"Hostname:        {platform.node()}")
    print(f"Airflow home:    {os.environ.get('AIRFLOW_HOME', 'not set')}")
    print(f"DAGs folder:     {os.environ.get('AIRFLOW__CORE__DAGS_FOLDER', 'default')}")
    print(f"Executor:        {os.environ.get('AIRFLOW__CORE__EXECUTOR', 'not set')}")


# ── DAG definition ───────────────────────────────────────────

with DAG(
    dag_id="01_hello_airflow",
    description="Your first Airflow DAG – BashOperator & PythonOperator basics",
    schedule_interval=None,            # manual trigger only
    start_date=datetime(2026, 6, 1),
    catchup=False,                     # don't backfill past runs
    default_args=default_args,
    tags=["lab", "basics"],
    doc_md=__doc__,
) as dag:

    # Task 1: EmptyOperator marks the start of the DAG
    start = EmptyOperator(task_id="start")

    # Task 2: BashOperator runs a shell command
    print_date = BashOperator(
        task_id="print_date",
        bash_command="echo 'Current date:' && date && echo 'Hostname:' && hostname",
    )

    # Task 3: BashOperator lists files in the data directory
    list_data_files = BashOperator(
        task_id="list_data_files",
        bash_command="echo '=== Data Directory ===' && ls -la /opt/airflow/data/ || echo 'No data directory'",
    )

    # Task 4: PythonOperator runs a Python function
    greet_task = PythonOperator(
        task_id="greet",
        python_callable=greet,
    )

    # Task 5: PythonOperator shows environment
    env_task = PythonOperator(
        task_id="show_environment",
        python_callable=show_environment,
    )

    # Task 6: EmptyOperator marks the end
    end = EmptyOperator(task_id="end")

    # ── Task dependencies (the >> operator) ──────────────────
    # This creates a diamond pattern:
    #
    #              ┌─ print_date ──────┐
    #   start ─────┤                   ├──── end
    #              └─ list_data_files ─┘
    #                       │
    #                    greet
    #                       │
    #                  show_environment
    #                       │
    #                      end

    start >> [print_date, list_data_files]
    start >> greet_task >> env_task
    [print_date, list_data_files, env_task] >> end
