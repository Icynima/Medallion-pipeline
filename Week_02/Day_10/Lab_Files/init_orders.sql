-- Create sample orders table for Debezium CDC
-- Enable pgcrypto extension for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS orders (
  id UUID PRIMARY KEY,
  customer_id UUID NOT NULL,
  product_id UUID NOT NULL,
  amount DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed some initial data
INSERT INTO orders (id, customer_id, product_id, amount, created_at) VALUES
  (gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), 59.99, NOW()),
  (gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), 29.99, NOW()),
  (gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), 109.99, NOW());