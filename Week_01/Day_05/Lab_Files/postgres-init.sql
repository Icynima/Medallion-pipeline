-- SQL script to initialize the orders database for Day 5 lab
-- It creates an orders table and inserts a few seed records.

CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  status VARCHAR(32) NOT NULL,
  order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO orders (customer_id, status, order_date) VALUES
  (1, 'NEW', NOW()),
  (2, 'PAID', NOW() - INTERVAL '1 day'),
  (3, 'SHIPPED', NOW() - INTERVAL '2 days');