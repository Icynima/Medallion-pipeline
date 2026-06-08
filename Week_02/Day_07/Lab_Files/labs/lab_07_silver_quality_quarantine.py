from __future__ import annotations

from pyspark.sql import functions as F

from day7_common import LAKE_DIR, OUTPUT_DIR, cleaned_orders, ensure_output_dirs, quality_checked_orders, read_bronze_orders, require_source_data, spark_session, write_csv_dir


def main() -> None:
    require_source_data()
    ensure_output_dirs()
    spark = spark_session("Day7Lab07QualityQuarantine")

    checked = quality_checked_orders(cleaned_orders(read_bronze_orders(spark)))
    valid = checked.filter(F.col("is_valid"))
    invalid = checked.filter(~F.col("is_valid"))

    valid_path = LAKE_DIR / "silver" / "orders_valid"
    quarantine_path = LAKE_DIR / "quarantine" / "orders_invalid"
    valid.write.mode("overwrite").parquet(str(valid_path))
    invalid.write.mode("overwrite").parquet(str(quarantine_path))

    summary = checked.groupBy("is_valid").count().orderBy("is_valid")
    write_csv_dir(summary, OUTPUT_DIR / "lab_07_quality_summary")
    write_csv_dir(
        invalid.select("event_id", "order_id", "quality_errors").orderBy("event_id"),
        OUTPUT_DIR / "lab_07_quarantine_preview",
    )

    print("LAB 07 COMPLETE")
    print(f"Valid rows: {valid.count()}; quarantined rows: {invalid.count()}")
    print("Concepts: data contracts, quarantine design, quality error arrays.")
    spark.stop()


if __name__ == "__main__":
    main()
