import json, time
from datetime import datetime
from kafka import KafkaProducer
producer=KafkaProducer(bootstrap_servers="localhost:9092", value_serializer=lambda v: json.dumps(v).encode(), key_serializer=lambda k: str(k).encode())
for e in [{"order_id":1,"customer_id":101,"product_id":"P1","status":"NEW","amount":100},{"order_id":2,"customer_id":102,"product_id":"P2","status":"NEW","amount":50},{"order_id":1,"customer_id":101,"product_id":"P1","status":"UPDATED","amount":120}]:
    e["event_time"]=datetime.utcnow().isoformat()+"Z"
    producer.send("orders.cdc", key=e["order_id"], value=e); print("sent", e); time.sleep(1)
producer.flush()
