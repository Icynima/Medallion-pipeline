import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from kafka import KafkaConsumer, KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, to_timestamp, when


BOOTSTRAP = "localhost:9092"
TOPIC = "day7.orders.raw"
GROUP_ID = "day7-bronze-loader"
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "day7_lakehouse" / RUN_ID
BRONZE_DIR = DATA_DIR / "bronze" / "orders_raw"
SILVER_DIR = DATA_DIR / "silver" / "orders_silver"


ORDERS = [
    {
        "event_id": "evt-1001",
        "order_id": 1001,
        "customer_id": 501,
        "product_id": "P-LAP-01",
        "product_name": "Laptop",
        "category": "electronics",
        "status": "NEW",
        "amount": 1299.99,
        "currency": "USD",
        "event_time": "2026-05-29T02:00:01Z",
    },
    {
        "event_id": "evt-1002",
        "order_id": 1002,
        "customer_id": 502,
        "product_id": "P-PHN-02",
        "product_name": "Smartphone",
        "category": "electronics",
        "status": "NEW",
        "amount": 799.00,
        "currency": "USD",
        "event_time": "2026-05-29T02:00:05Z",
    },
    {
        "event_id": "evt-1003",
        "order_id": 1003,
        "customer_id": 503,
        "product_id": "P-HDP-03",
        "product_name": "Headphones",
        "category": "accessories",
        "status": "NEW",
        "amount": 149.50,
        "currency": "USD",
        "event_time": "2026-05-29T02:00:08Z",
    },
    {
        "event_id": "evt-1004",
        "order_id": 1002,
        "customer_id": 502,
        "product_id": "P-PHN-02",
        "product_name": "Smartphone",
        "category": "electronics",
        "status": "NEW",
        "amount": 799.00,
        "currency": "USD",
        "event_time": "2026-05-29T02:00:05Z",
    },
    {
        "event_id": "evt-1005",
        "order_id": 1004,
        "customer_id": 504,
        "product_id": "P-CAM-04",
        "product_name": "Camera",
        "category": "electronics",
        "status": "CANCELLED",
        "amount": 450.00,
        "currency": "USD",
        "event_time": "2026-05-29T02:00:20Z",
    },
    {
        "event_id": "evt-1006",
        "order_id": 1005,
        "customer_id": 505,
        "product_id": "P-BAG-05",
        "product_name": "Travel Bag",
        "category": "travel",
        "status": "NEW",
        "amount": -10.00,
        "currency": "USD",
        "event_time": "2026-05-29T02:00:30Z",
    },
]


def reset_dirs() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    SILVER_DIR.mkdir(parents=True, exist_ok=True)


def produce_orders() -> None:
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        key_serializer=lambda value: str(value).encode("utf-8"),
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
    for order in ORDERS:
        producer.send(TOPIC, key=order["order_id"], value=order)
    producer.flush()
    producer.close()
    print(f"Produced {len(ORDERS)} source events to Kafka topic {TOPIC}")


def land_bronze() -> Path:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        group_id=f"{GROUP_ID}-{RUN_ID}",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=8000,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )
    records = []
    for message in consumer:
        event = message.value
        event["_bronze_ingest_time"] = datetime.now(timezone.utc).isoformat()
        event["_kafka_topic"] = message.topic
        event["_kafka_partition"] = message.partition
        event["_kafka_offset"] = message.offset
        records.append(event)
        if len(records) >= len(ORDERS):
            break
    consumer.close()

    bronze_file = BRONZE_DIR / "orders.jsonl"
    with bronze_file.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    print(f"Landed {len(records)} raw events to Bronze JSON: {bronze_file}")
    return bronze_file


def transform_to_silver() -> None:
    spark = (
        SparkSession.builder.appName("Day7FullBronzeToSilver")
        .master("local[*]")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    bronze_df = spark.read.json(str(BRONZE_DIR))
    silver_df = (
        bronze_df.withColumn("event_time_ts", to_timestamp(col("event_time")))
        .withColumn("category", when(col("category").isNotNull(), col("category")).otherwise("unknown"))
        .withColumn("category", col("category").cast("string"))
        .filter((col("status") == "NEW") & (col("amount") > 0))
        .dropDuplicates(["order_id"])
        .withColumn("silver_processed_at", current_timestamp())
        .select(
            "order_id",
            "event_id",
            "customer_id",
            "product_id",
            "product_name",
            "category",
            "status",
            "amount",
            "currency",
            "event_time",
            "event_time_ts",
            "silver_processed_at",
        )
        .orderBy("order_id")
    )

    parquet_path = SILVER_DIR / "parquet"
    csv_path = SILVER_DIR / "csv"
    silver_df.write.mode("overwrite").parquet(str(parquet_path))
    silver_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(str(csv_path))

    print(f"Wrote Silver Parquet to {parquet_path}")
    print(f"Wrote Silver CSV to {csv_path}")
    print(f"Silver row count: {silver_df.count()}")
    spark.stop()


def main() -> None:
    reset_dirs()
    produce_orders()
    time.sleep(2)
    land_bronze()
    transform_to_silver()
    print(f"Run ID: {RUN_ID}")


if __name__ == "__main__":
    main()
