from __future__ import annotations

from day7_common import LAKE_DIR, OUTPUT_DIR, ensure_output_dirs, latest_order_state, require_source_data, spark_session, write_csv_dir


def main() -> None:
    require_source_data()
    ensure_output_dirs()
    spark = spark_session("Day7Lab08CdcLatestState")

    valid = spark.read.parquet(str(LAKE_DIR / "silver" / "orders_valid"))
    current = latest_order_state(valid)
    current_path = LAKE_DIR / "silver" / "orders_current"
    current.write.mode("overwrite").parquet(str(current_path))

    write_csv_dir(
        current.select("order_id", "event_id", "status", "amount", "currency", "event_time_ts").orderBy("order_id"),
        OUTPUT_DIR / "lab_08_orders_current_preview",
    )

    print("LAB 08 COMPLETE")
    print(f"Current order rows: {current.count()}")
    print("Concepts: CDC, window functions, latest-state tables.")
    spark.stop()


if __name__ == "__main__":
    main()
