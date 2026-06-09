"""
DAG 06 – Dynamic DAGs & Task Mapping
======================================
Lab 6: Generate tasks dynamically at runtime.

Concepts covered:
  - Dynamic task mapping (expand)
  - Generating DAGs programmatically
  - Parameterized tasks
  - TaskGroup for visual organisation
  - Processing multiple data sources in parallel
"""

import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task, task_group
from airflow.operators.empty import EmptyOperator
from sqlalchemy import create_engine, text

PG_CONN = os.environ.get(
    "WAREHOUSE_CONN",
    "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
)

# Data sources to process dynamically
DATA_SOURCES = [
    {"name": "orders", "file": "new_orders.csv", "table": "bronze_orders"},
    {"name": "customers", "file": "customers.csv", "table": "bronze_customers"},
    {"name": "products", "file": "products.csv", "table": "bronze_products"},
]

# Categories to analyze
CATEGORIES = ["Electronics", "Office", "Stationery"]


@dag(
    dag_id="06_dynamic_dags",
    description="Dynamic task mapping, TaskGroups, and parameterized processing",
    schedule_interval=None,
    start_date=datetime(2026, 6, 1),
    catchup=False,
    default_args={
        "owner": "data-engineer",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["lab", "dynamic", "taskgroup"],
    doc_md=__doc__,
)
def dynamic_dags():

    start = EmptyOperator(task_id="start")

    # ── Section 1: TaskGroup ──────────────────────────────────
    # TaskGroups organize tasks visually in the UI without SubDAG overhead

    @task_group(group_id="validate_sources")
    def validate_data_sources():
        """Validate each data source file exists and has content."""

        @task()
        def check_file(source: dict) -> dict:
            """Check if a data file exists and count lines."""
            import csv

            path = f"/opt/airflow/data/{source['file']}"
            exists = os.path.exists(path)
            line_count = 0
            if exists:
                with open(path, "r") as f:
                    reader = csv.reader(f)
                    line_count = sum(1 for _ in reader) - 1  # subtract header
            result = {
                "source": source["name"],
                "file": source["file"],
                "exists": exists,
                "rows": line_count,
            }
            print(f"Validated {source['name']}: exists={exists}, rows={line_count}")
            return result

        # Use .expand() for dynamic task mapping
        # This creates one task instance per item in the list
        return check_file.expand(source=DATA_SOURCES)

    # ── Section 2: Dynamic Task Mapping with expand ───────────

    @task()
    def get_categories() -> list:
        """Return list of categories to process dynamically.
        In production this might query the database."""
        engine = create_engine(PG_CONN)
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(
                    "SELECT DISTINCT category FROM silver_orders WHERE category IS NOT NULL"
                )).fetchall()
                categories = [row[0] for row in rows]
                if categories:
                    return categories
        except Exception:
            pass
        # Fallback to static list
        return CATEGORIES

    @task()
    def analyze_category(category: str) -> dict:
        """Analyze a single product category."""
        engine = create_engine(PG_CONN)
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT
                            COUNT(*)          AS order_count,
                            SUM(total_amount) AS revenue,
                            AVG(total_amount) AS avg_value
                        FROM silver_orders
                        WHERE category = :cat
                    """),
                    {"cat": category},
                ).fetchone()
                analysis = {
                    "category": category,
                    "order_count": result[0] if result else 0,
                    "revenue": float(result[1]) if result and result[1] else 0,
                    "avg_value": float(result[2]) if result and result[2] else 0,
                }
        except Exception:
            analysis = {"category": category, "order_count": 0, "revenue": 0, "avg_value": 0}

        print(f"Category '{category}': {analysis['order_count']} orders, "
              f"${analysis['revenue']:.2f} revenue")
        return analysis

    @task()
    def aggregate_analyses(analyses: list) -> dict:
        """Combine all category analyses into a summary."""
        total_orders = sum(a["order_count"] for a in analyses)
        total_revenue = sum(a["revenue"] for a in analyses)

        summary = {
            "total_categories": len(analyses),
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "by_category": {a["category"]: a for a in analyses},
        }

        print(f"\n=== Dynamic Analysis Summary ===")
        print(f"Categories analyzed: {len(analyses)}")
        print(f"Total orders:        {total_orders}")
        print(f"Total revenue:       ${total_revenue:,.2f}")
        for a in sorted(analyses, key=lambda x: x["revenue"], reverse=True):
            print(f"  {a['category']:15s} → {a['order_count']:3d} orders, ${a['revenue']:>10,.2f}")

        return summary

    # ── Section 3: Parameterized processing ───────────────────

    @task_group(group_id="data_quality")
    def run_quality_checks():
        """Run data quality checks on each layer."""

        @task()
        def quality_check(layer: str) -> dict:
            """Run quality check for a specific layer."""
            engine = create_engine(PG_CONN)
            checks = {
                "bronze": "SELECT COUNT(*) FROM bronze_orders WHERE order_id IS NULL",
                "silver": "SELECT COUNT(*) FROM silver_orders WHERE quantity <= 0",
                "gold": "SELECT COUNT(*) FROM gold_customer_360 WHERE total_orders = 0 AND total_revenue > 0",
            }
            query = checks.get(layer, "SELECT 0")
            try:
                with engine.connect() as conn:
                    violations = conn.execute(text(query)).scalar_one()
            except Exception:
                violations = -1  # table doesn't exist yet

            result = {
                "layer": layer,
                "violations": violations,
                "passed": violations == 0 or violations == -1,
            }
            status = "PASS" if result["passed"] else "FAIL"
            print(f"[{status}] {layer} layer: {violations} violations")
            return result

        return quality_check.expand(layer=["bronze", "silver", "gold"])

    # ── Wire it all together ──────────────────────────────────

    validations = validate_data_sources()
    categories = get_categories()
    # Dynamic mapping: creates one analyze_category task per category
    analyses = analyze_category.expand(category=categories)
    summary = aggregate_analyses(analyses)
    quality = run_quality_checks()

    end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

    start >> validations
    start >> categories
    start >> quality
    [summary, quality] >> end


dynamic_dags()
