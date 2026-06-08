from __future__ import annotations

from day7_common import OUTPUT_DIR, ensure_output_dirs, read_bronze_orders, require_source_data, spark_session, write_csv_dir


def main() -> None:
    require_source_data()
    ensure_output_dirs()
    spark = spark_session("Day7Lab05BronzeSchemaDrift")

    bronze = read_bronze_orders(spark)
    total_rows = bronze.count()
    profile_rows = []
    for field in bronze.schema.fields:
        column = field.name
        non_null = bronze.filter(bronze[column].isNotNull()).count()
        profile_rows.append((column, field.dataType.simpleString(), non_null, total_rows - non_null))

    profile = spark.createDataFrame(profile_rows, ["column_name", "data_type", "non_null_rows", "null_rows"])
    write_csv_dir(profile.orderBy("column_name"), OUTPUT_DIR / "lab_05_bronze_schema_profile")

    print("LAB 05 COMPLETE")
    print(f"Profiled {len(profile_rows)} Bronze columns across {total_rows} rows.")
    print("Concepts: schema drift, sparse optional fields, data profiling before cleaning.")
    spark.stop()


if __name__ == "__main__":
    main()
