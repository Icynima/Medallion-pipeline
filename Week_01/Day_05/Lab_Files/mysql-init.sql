-- SQL script to initialize the inventory database for Day 5 lab
-- It creates an inventory table and inserts some seed data.

CREATE TABLE IF NOT EXISTS inventory (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_name VARCHAR(255) NOT NULL,
  quantity INT NOT NULL,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO inventory (product_name, quantity) VALUES
  ('Widget A', 100),
  ('Widget B', 50),
  ('Widget C', 200);