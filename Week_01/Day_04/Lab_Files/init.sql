CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    balance NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_total NUMERIC(10, 2) NOT NULL,
    order_status VARCHAR(30) NOT NULL DEFAULT 'created',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS debezium_signal (
    id VARCHAR(42) PRIMARY KEY,
    type VARCHAR(32) NOT NULL,
    data VARCHAR(2048)
);

ALTER TABLE customers REPLICA IDENTITY FULL;
ALTER TABLE orders REPLICA IDENTITY FULL;

INSERT INTO customers (name, email, balance, status) VALUES
    ('Alice', 'alice@example.com', 100.00, 'active'),
    ('Bob', 'bob@example.com', 200.00, 'active'),
    ('Carol', 'carol@example.com', 150.00, 'review');

INSERT INTO orders (customer_id, order_total, order_status) VALUES
    (1, 49.90, 'created'),
    (2, 129.50, 'paid'),
    (3, 18.25, 'created');
