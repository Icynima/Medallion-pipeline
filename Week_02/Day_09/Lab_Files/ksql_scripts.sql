-- Day 9 lab: ksqlDB statements to create streams, tables and queries.

-- Create a stream over the raw orders topic. The topic name is 'orders'
CREATE STREAM orders_raw (
  order_id STRING KEY,
  customer_id STRING,
  amount DOUBLE,
  created_at BIGINT
) WITH (
  KAFKA_TOPIC='orders',
  VALUE_FORMAT='JSON'
);

-- Filter out small orders and write the results to a new stream/topic
CREATE STREAM high_value_orders WITH (KAFKA_TOPIC='orders_high_value', PARTITIONS=1) AS
  SELECT *
  FROM orders_raw
  WHERE amount > 100
  EMIT CHANGES;

-- Aggregate orders into tumbling windows per customer
CREATE TABLE order_aggregates WITH (KAFKA_TOPIC='orders_agg', PARTITIONS=1) AS
  SELECT customer_id,
         WINDOWSTART AS window_start,
         WINDOWEND   AS window_end,
         COUNT(*)    AS order_count,
         SUM(amount) AS total_amount
  FROM orders_raw
  WINDOW TUMBLING (SIZE 1 MINUTE)
  GROUP BY customer_id
  EMIT CHANGES;

-- Inspect the contents of the aggregate table (pull query example)
-- SELECT * FROM order_aggregates WHERE customer_id='C001' LIMIT 5;