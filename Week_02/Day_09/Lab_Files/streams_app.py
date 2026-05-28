#!/usr/bin/env python3
"""
Simple stream processing application for Day 9 lab.

This script consumes order events from the `orders` topic, aggregates
the number of orders and total amount per customer in a sliding
time-based window, and produces the aggregated results to the
`order_counts` topic.  It uses the kafka-python client library and
maintains state in memory (not durable).  While this is not a true
Kafka Streams implementation, it illustrates the core concepts of
stream-table duality and real-time aggregation in Python.

Usage:
    python streams_app.py

Make sure the Kafka cluster is running and the `orders` topic exists.
"""
import json
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaProducer


WINDOW_SIZE_SECONDS = 60  # 1-minute tumbling window


def main():
    consumer = KafkaConsumer(
        'orders',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        key_deserializer=lambda m: m.decode('utf-8') if m is not None else None,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='orders-aggregator'
    )
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: str(k).encode('utf-8') if k is not None else None
    )

    # Maintain a deque of events per customer per window
    windows = defaultdict(lambda: deque())

    def emit_aggregates():
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=WINDOW_SIZE_SECONDS)
        # Iterate through customers
        for cust, events in list(windows.items()):
            # Remove events older than window
            while events and events[0]['timestamp'] < window_start.timestamp():
                events.popleft()
            if events:
                count = len(events)
                total = sum(e['amount'] for e in events)
                agg = {'customer_id': cust, 'order_count': count, 'total_amount': total, 'window_start': window_start.isoformat(), 'window_end': now.isoformat()}
                producer.send('order_counts', key=cust, value=agg)
                producer.flush()

    last_emit = time.time()
    try:
        for msg in consumer:
            record = msg.value
            cust_id = record.get('customer_id')
            ts = record.get('created_at') or record.get('timestamp') or time.time()
            if cust_id is not None:
                windows[cust_id].append({'timestamp': ts, 'amount': record.get('amount', 0.0)})
            # emit aggregates every few seconds
            if time.time() - last_emit > 10:
                emit_aggregates()
                last_emit = time.time()
    except KeyboardInterrupt:
        print("Stopping stream processor...")
    finally:
        emit_aggregates()
        consumer.close()
        producer.close()


if __name__ == '__main__':
    main()