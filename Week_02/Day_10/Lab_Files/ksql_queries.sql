-- ksqlDB queries for the final project

-- Register the Debezium CDC topics as streams. Use the AVRO format because
-- the connectors publish Avro-encoded records and the schema is stored in
-- Confluent Schema Registry.
CREATE STREAM orders_raw WITH (
    KAFKA_TOPIC='orders.public.orders',
    VALUE_FORMAT='AVRO',
    KEY_FORMAT='AVRO',
    KEY='id'
);

CREATE STREAM inventory_raw WITH (
    KAFKA_TOPIC='inventory.public.inventory',
    VALUE_FORMAT='AVRO',
    KEY_FORMAT='AVRO',
    KEY='product_id'
);

-- Create cleaned streams that extract the after state from Debezium envelopes
-- and convert timestamps to proper types. This requires the Debezium New
-- Record State Extract SMT to be configured on the connectors or we can
-- unwrap manually using the ksqlDB EXTRACTJSONFIELD function. For
-- simplicity, assume the connectors use the SMT and the value schema
-- contains the actual columns.
CREATE STREAM orders_clean AS
    SELECT
        id AS order_id,
        customer_id,
        product_id,
        amount,
        TIMESTAMPTOSTRING(CAST(created_at AS BIGINT),'yyyy-MM-dd HH:mm:ss','UTC') AS created_at
    FROM orders_raw
    EMIT CHANGES;

CREATE STREAM inventory_clean AS
    SELECT
        product_id,
        product_name,
        stock,
        price,
        TIMESTAMPTOSTRING(CAST(updated_at AS BIGINT),'yyyy-MM-dd HH:mm:ss','UTC') AS updated_at
    FROM inventory_raw
    EMIT CHANGES;

-- Create a table aggregating orders by product and computing total revenue and
-- quantity ordered. This uses a tumbling window of one hour. Adjust the
-- window size based on your business requirements.
CREATE TABLE product_sales_hourly WITH (KAFKA_TOPIC='product_sales_hourly', PARTITIONS=1, REPLICAS=1) AS
    SELECT
        o.product_id AS product_id,
        i.product_name AS product_name,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end,
        SUM(o.amount) AS total_sales,
        COUNT(*) AS orders_count
    FROM orders_clean o
    JOIN inventory_clean i
        ON o.product_id = i.product_id
    WINDOW TUMBLING (SIZE 1 HOUR)
    GROUP BY o.product_id, i.product_name
    EMIT CHANGES;

-- A materialized view for the latest inventory levels. Use a table because
-- we want to keep the latest value for each product.
CREATE TABLE inventory_latest WITH (KAFKA_TOPIC='inventory_latest', VALUE_FORMAT='AVRO', KEY='product_id') AS
    SELECT product_id,
           LATEST_BY_OFFSET(product_name) AS product_name,
           LATEST_BY_OFFSET(stock) AS stock,
           LATEST_BY_OFFSET(price) AS price
    FROM inventory_clean
    GROUP BY product_id
    EMIT CHANGES;

-- Query to join sales and inventory to compute remaining stock and sales
-- revenue per product in near real-time. This table can serve dashboards.
CREATE TABLE product_performance WITH (KAFKA_TOPIC='product_performance') AS
    SELECT
        s.product_id AS product_id,
        s.product_name AS product_name,
        l.stock AS current_stock,
        SUM(s.total_sales) AS total_sales
    FROM product_sales_hourly s
    JOIN inventory_latest l
        ON s.product_id = l.product_id
    GROUP BY s.product_id, s.product_name, l.stock
    EMIT CHANGES;

-- Pull query example: get current performance for a specific product
-- SELECT * FROM product_performance WHERE product_id = '<uuid>';  