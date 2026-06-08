from __future__ import annotations

from pyspark.sql import functions as F

from day7_common import LAKE_DIR, OUTPUT_DIR, STATE_DIR, cleaned_orders, enriched_orders, ensure_output_dirs, gold_frames, latest_order_state, quality_checked_orders, read_order_events, require_source_data, reset_dir, spark_session, with_bronze_metadata, write_csv_dir, write_json_report


def main() -> None:
    require_source_data()
    ensure_output_dirs()
    spark = spark_session("Day7Lab12FullMedallionPipeline")

    reset_dir(LAKE_DIR / "bronze")
    reset_dir(LAKE_DIR / "silver")
    reset_dir(LAKE_DIR / "gold")
    reset_dir(LAKE_DIR / "quarantine")

    bronze = with_bronze_metadata(read_order_events(spark), "orchestrated-run-001")
    bronze_path = LAKE_DIR / "bronze" / "orders_raw"
    bronze.write.mode("overwrite").parquet(str(bronze_path))

    checked = quality_checked_orders(cleaned_orders(spark.read.parquet(str(bronze_path))))
    valid = checked.filter(F.col("is_valid"))
    invalid = checked.filter(~F.col("is_valid"))
    valid.write.mode("overwrite").parquet(str(LAKE_DIR / "silver" / "orders_valid"))
    invalid.write.mode("overwrite").parquet(str(LAKE_DIR / "quarantine" / "orders_invalid"))

    current = latest_order_state(valid)
    current.write.mode("overwrite").parquet(str(LAKE_DIR / "silver" / "orders_current"))

    enriched = enriched_orders(spark, current)
    enriched.write.mode("overwrite").parquet(str(LAKE_DIR / "silver" / "orders_enriched"))

    frames = gold_frames(enriched)
    for name, frame in frames.items():
        frame.write.mode("overwrite").parquet(str(LAKE_DIR / "gold" / name))
        write_csv_dir(frame, OUTPUT_DIR / f"lab_12_{name}")

    manifest = {
        "bronze_rows": bronze.count(),
        "silver_valid_rows": valid.count(),
        "quarantine_rows": invalid.count(),
        "current_order_rows": current.count(),
        "enriched_rows": enriched.count(),
        "gold_tables": sorted(frames.keys()),
        "expected_learning_path": "Spark basics -> Bronze raw -> Silver quality/current/enriched -> Gold KPIs",
    }
    write_json_report(STATE_DIR / "lab_12_run_manifest.json", manifest)

    assert manifest["bronze_rows"] == 12, manifest
    assert manifest["silver_valid_rows"] == 10, manifest
    assert manifest["quarantine_rows"] == 2, manifest
    assert manifest["current_order_rows"] == 7, manifest

    print("LAB 12 COMPLETE")
    print(manifest)
    print("Concepts: orchestration, layer contracts, validation gates, production-style manifest.")
    spark.stop()


if __name__ == "__main__":
    main()
