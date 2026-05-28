import sys, json
from kafka import KafkaConsumer
consumer=KafkaConsumer(*sys.argv[1:], bootstrap_servers="localhost:9092", auto_offset_reset="earliest", value_deserializer=lambda m: json.loads(m.decode()))
for msg in consumer: print(msg.topic, msg.key, msg.value)
