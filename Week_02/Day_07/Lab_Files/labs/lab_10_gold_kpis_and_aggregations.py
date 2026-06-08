from __future__ import annotations

from day7_common import LAKE_DIR, gold_frames, ensure_output_dirs, require_source_data, spark_session, write_csv_dir


def main() -> None:
    require_source_data()
    ensure_output_dirs()
    spark = spark_session("Day7Lab10GoldKpis")

    enriched = spark.read.parquet(str(LAKE_DIR / "silver" / "orders_enriched"))
    frames = gold_frames(enriched)
    gold_path = LAKE_DIR / "gold"

    for name, frame in frames.items():
        frame.write.mode("overwrite").parquet(str(gold_path / name))
        write_csv_dir(frame, gold_path / f"{name}_csv")

    print("LAB 10 COMPLETE")
    print(f"Gold tables written: {', '.join(frames.keys())}")
    print("Concepts: business aggregates, revenue rules, Gold-layer tables.")
    spark.stop()


if __name__ == "__main__":
    main()
