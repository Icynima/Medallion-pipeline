from __future__ import annotations

import json
from pathlib import Path

from pyspark.sql import functions as F

from day7_common import LAKE_DIR, ORDER_SOURCE_FILES, OUTPUT_DIR, STATE_DIR, cleaned_orders, enriched_orders, ensure_output_dirs, gold_frames, latest_order_state, quality_checked_orders, read_order_events, require_source_data, reset_dir, spark_session, with_bronze_metadata, write_csv_dir, write_json_report


def load_manifest(path: Path) -> dict[str, object]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"processed_files": [], "batches": []}


def main() -> None:
    require_source_data()
    ensure_output_dirs()
    spark = spark_session("Day7Lab11IncrementalProcessing")

    incremental_lake = LAKE_DIR / "incremental"
    reset_dir(incremental_lake)
    manifest_path = STATE_DIR / "lab_11_incremental_manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()

    manifest = load_manifest(manifest_path)
    bronze_path = incremental_lake / "bronze" / "orders_raw"

    for index, source_file in enumerate(ORDER_SOURCE_FILES, start=1):
        processed_files = set(manifest["processed_files"])
        if source_file.name in processed_files:
            print(f"Skipping already processed file: {source_file.name}")
            continue

        batch_id = f"incremental-batch-{index:02d}"
        batch = with_bronze_metadata(read_order_events(spark, [source_file]), batch_id)
        batch.write.mode("append").parquet(str(bronze_path))
        row_count = batch.count()
        manifest["processed_files"].append(source_file.name)
        manifest["batches"].append({"batch_id": batch_id, "source_file": source_file.name, "rows": row_count})
        write_json_report(manifest_path, manifest)
        print(f"Processed {source_file.name}: {row_count} Bronze rows")

    bronze = spark.read.parquet(str(bronze_path))
    checked = quality_checked_orders(cleaned_orders(bronze))
    valid = checked.filter(F.col("is_valid"))
    current = latest_order_state(valid)
    enriched = enriched_orders(spark, current)

    valid.write.mode("overwrite").parquet(str(incremental_lake / "silver" / "orders_valid"))
    current.write.mode("overwrite").parquet(str(incremental_lake / "silver" / "orders_current"))
    enriched.write.mode("overwrite").parquet(str(incremental_lake / "silver" / "orders_enriched"))

    for name, frame in gold_frames(enriched).items():
        frame.write.mode("overwrite").parquet(str(incremental_lake / "gold" / name))

    summary = spark.createDataFrame(
        [
            ("bronze_rows", bronze.count()),
            ("silver_valid_rows", valid.count()),
            ("current_order_rows", current.count()),
            ("processed_files", len(manifest["processed_files"])),
        ],
        ["metric", "value"],
    )
    write_csv_dir(summary, OUTPUT_DIR / "lab_11_incremental_summary")

    print("LAB 11 COMPLETE")
    print(f"Manifest: {manifest_path}")
    print("Concepts: file checkpoints, idempotent ingestion, incremental medallion updates.")
    spark.stop()


if __name__ == "__main__":
    main()
