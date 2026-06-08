from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


LABS = {
    "01": {
        "script": "labs/lab_01_spark_dataframe_basics.py",
        "layer": "Spark fundamentals",
        "title": "DataFrame basics with customer dimension data",
    },
    "02": {
        "script": "labs/lab_02_spark_sql_exploration.py",
        "layer": "Spark fundamentals",
        "title": "SQL exploration over raw order events",
    },
    "03": {
        "script": "labs/lab_03_storage_formats_and_partitions.py",
        "layer": "Spark fundamentals",
        "title": "Parquet storage and partitioned reads",
    },
    "04": {
        "script": "labs/lab_04_bronze_raw_ingestion.py",
        "layer": "Bronze",
        "title": "Raw order-event ingestion with source metadata",
    },
    "05": {
        "script": "labs/lab_05_bronze_schema_drift.py",
        "layer": "Bronze",
        "title": "Schema drift profiling",
    },
    "06": {
        "script": "labs/lab_06_silver_cleaning_and_standardization.py",
        "layer": "Silver",
        "title": "Cleaning and type standardization",
    },
    "07": {
        "script": "labs/lab_07_silver_quality_quarantine.py",
        "layer": "Silver",
        "title": "Quality gates and quarantine",
    },
    "08": {
        "script": "labs/lab_08_cdc_latest_order_state.py",
        "layer": "Silver",
        "title": "Latest order state with a CDC window",
    },
    "09": {
        "script": "labs/lab_09_dimension_enrichment.py",
        "layer": "Silver",
        "title": "Customer, product, and FX enrichment",
    },
    "10": {
        "script": "labs/lab_10_gold_kpis_and_aggregations.py",
        "layer": "Gold",
        "title": "Business KPI aggregations",
    },
    "11": {
        "script": "labs/lab_11_incremental_batch_processing.py",
        "layer": "Cross-layer",
        "title": "Incremental file processing with a manifest",
    },
    "12": {
        "script": "labs/lab_12_full_medallion_pipeline.py",
        "layer": "End to end",
        "title": "Full Bronze to Silver to Gold pipeline",
    },
}


def print_lab_list() -> None:
    for lab, meta in LABS.items():
        print(f"{lab} | {meta['layer']} | {meta['title']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Day 7 Spark lab through Docker Compose.")
    parser.add_argument("lab", nargs="?", choices=LABS.keys(), help="Lab number, for example 01 or 12.")
    parser.add_argument("--list", action="store_true", help="Show the Day 7 lab sequence and learning layer.")
    args = parser.parse_args()

    if args.list:
        print_lab_list()
        return
    if not args.lab:
        parser.error("choose a lab number, or use --list")

    metadata = LABS[args.lab]
    script = metadata["script"]
    command = [
        "docker",
        "compose",
        "-p",
        "day7_lab",
        "run",
        "--rm",
        "spark-client",
        "/opt/spark/bin/spark-submit",
        "--master",
        "spark://spark-master:7077",
        f"/workspace/{script}",
    ]
    print(f"Day 7 Lab {args.lab}: {metadata['title']}")
    print(f"Learning layer: {metadata['layer']}")
    print("Running:", " ".join(command))
    result = subprocess.run(command, cwd=Path(__file__).resolve().parent)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
