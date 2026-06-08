from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


LABS = {
    "01": "labs/lab_01_spark_dataframe_basics.py",
    "02": "labs/lab_02_spark_sql_exploration.py",
    "03": "labs/lab_03_storage_formats_and_partitions.py",
    "04": "labs/lab_04_bronze_raw_ingestion.py",
    "05": "labs/lab_05_bronze_schema_drift.py",
    "06": "labs/lab_06_silver_cleaning_and_standardization.py",
    "07": "labs/lab_07_silver_quality_quarantine.py",
    "08": "labs/lab_08_cdc_latest_order_state.py",
    "09": "labs/lab_09_dimension_enrichment.py",
    "10": "labs/lab_10_gold_kpis_and_aggregations.py",
    "11": "labs/lab_11_incremental_batch_processing.py",
    "12": "labs/lab_12_full_medallion_pipeline.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Day 7 Spark lab through Docker Compose.")
    parser.add_argument("lab", choices=LABS.keys(), help="Lab number, for example 01 or 12.")
    args = parser.parse_args()

    script = LABS[args.lab]
    command = [
        "docker",
        "compose",
        "run",
        "--rm",
        "spark-client",
        "/opt/spark/bin/spark-submit",
        "--master",
        "spark://spark-master:7077",
        f"/workspace/{script}",
    ]
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=Path(__file__).resolve().parent)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
