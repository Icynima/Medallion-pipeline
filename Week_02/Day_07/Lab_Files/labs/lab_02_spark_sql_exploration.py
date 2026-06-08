from __future__ import annotations

from day7_common import OUTPUT_DIR, ORDER_SOURCE_FILES, ensure_output_dirs, read_order_events, require_source_data, spark_session, write_csv_dir


def main() -> None:
    require_source_data()
    ensure_output_dirs()
    spark = spark_session("Day7Lab02SparkSQL")

    orders = read_order_events(spark, [ORDER_SOURCE_FILES[0]])
    orders.createOrReplaceTempView("raw_orders")

    status_counts = spark.sql(
        """
        SELECT
          status,
          COUNT(*) AS event_count,
          ROUND(SUM(amount), 2) AS raw_amount_total
        FROM raw_orders
        GROUP BY status
        ORDER BY event_count DESC, status
        """
    )

    write_csv_dir(status_counts, OUTPUT_DIR / "lab_02_status_counts")
    print("LAB 02 COMPLETE")
    print(f"Raw events analyzed from batch 1: {orders.count()}")
    print("Concepts: temp views, Spark SQL, group by, aggregations.")
    spark.stop()


if __name__ == "__main__":
    main()
