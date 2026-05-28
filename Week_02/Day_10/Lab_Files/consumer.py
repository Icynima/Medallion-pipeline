#!/usr/bin/env python3
"""
Simple Kafka consumer for the final project.

This script consumes messages from a specified topic and prints them to the
console. Use it to inspect the aggregated results produced by your ksqlDB
queries (e.g. the `product_performance` topic) or any other topic in your
pipeline. The consumer reads Avro-encoded values and decodes them using the
Confluent Schema Registry, so you must have the `confluent_kafka` and
`fastavro` packages installed (see the installation script). Adjust the
bootstrap servers, schema registry URL and topic names as needed.
"""

import argparse
import sys
from confluent_kafka import Consumer, KafkaException, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer


def create_consumer(bootstrap_servers: str, schema_registry_url: str, group_id: str) -> Consumer:
    # Create a schema registry client for Avro deserialization
    schema_registry_conf = {'url': schema_registry_url}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    value_deserializer = AvroDeserializer(schema_registry_client)

    consumer_conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'value.deserializer': value_deserializer
    }
    return Consumer(consumer_conf)


def consume_loop(consumer: Consumer, topics: list[str]):
    consumer.subscribe(topics)
    print(f"Consuming from topics: {topics}")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    continue
            try:
                value = msg.value()
            except Exception as e:
                print(f"Failed to deserialize message: {e}")
                value = None
            print(f"\nKey: {msg.key()}\nValue: {value}\nPartition: {msg.partition()} Offset: {msg.offset()}")
    except KeyboardInterrupt:
        print("Stopping consumer…")
    finally:
        consumer.close()


def main():
    parser = argparse.ArgumentParser(description="Consume Avro messages from Kafka topics")
    parser.add_argument('--bootstrap-servers', default='localhost:9092', help='Kafka bootstrap servers (host:port)')
    parser.add_argument('--schema-registry', default='http://localhost:8081', help='Schema Registry URL')
    parser.add_argument('--group-id', default='final-project-consumer', help='Consumer group id')
    parser.add_argument('--topic', action='append', required=True, help='Topic(s) to consume (can specify multiple)')
    args = parser.parse_args()

    consumer = create_consumer(args.bootstrap_servers, args.schema_registry, args.group_id)
    consume_loop(consumer, args.topic)


if __name__ == '__main__':
    main()