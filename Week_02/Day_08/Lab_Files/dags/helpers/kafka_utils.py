"""
Kafka utility functions shared across DAGs.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from kafka import KafkaConsumer, KafkaProducer


KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:29092")


def get_producer() -> KafkaProducer:
    """Return a KafkaProducer with JSON serialisation."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        key_serializer=lambda v: str(v).encode("utf-8"),
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
    )


def get_consumer(topic: str, group_id: str, timeout_ms: int = 5000) -> KafkaConsumer:
    """Return a KafkaConsumer reading from the beginning."""
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        group_id=group_id,
        auto_offset_reset="earliest",
        consumer_timeout_ms=timeout_ms,
        key_deserializer=lambda v: v.decode("utf-8") if v else None,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )


def consume_batch(topic: str, group_id: str, max_records: int = 500,
                  timeout_ms: int = 10000) -> list[dict[str, Any]]:
    """Consume up to *max_records* messages and return them as dicts."""
    consumer = get_consumer(topic, group_id, timeout_ms=timeout_ms)
    records: list[dict[str, Any]] = []
    try:
        for msg in consumer:
            records.append({
                "topic": msg.topic,
                "partition": msg.partition,
                "offset": msg.offset,
                "key": msg.key,
                "value": msg.value,
                "timestamp": datetime.fromtimestamp(
                    msg.timestamp / 1000, tz=timezone.utc
                ).isoformat(),
            })
            if len(records) >= max_records:
                break
    finally:
        consumer.close()
    return records
