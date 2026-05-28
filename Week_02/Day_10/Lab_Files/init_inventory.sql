-- Create inventory table to capture product stock levels
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS inventory (
  product_id UUID PRIMARY KEY,
  product_name TEXT NOT NULL,
  stock INTEGER NOT NULL,
  price DOUBLE PRECISION NOT NULL,
  updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert some initial inventory records
INSERT INTO inventory (product_id, product_name, stock, price) VALUES
  (gen_random_uuid(), 'Widget A', 100, 29.99),
  (gen_random_uuid(), 'Widget B', 75, 49.99),
  (gen_random_uuid(), 'Widget C', 40, 19.99);