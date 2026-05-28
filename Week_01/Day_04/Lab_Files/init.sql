-- Initialization script for Day 4 CDC lab
--
-- This script creates a sample customers table and populates it with
-- initial data.  When the PostgreSQL container starts, Docker
-- Compose mounts this file at /docker-entrypoint-initdb.d/init.sql
-- so the table and data exist before the Debezium connector takes its
-- initial snapshot.

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS debezium_signal (
    id VARCHAR(42) PRIMARY KEY,
    type VARCHAR(32) NOT NULL,
    data VARCHAR(2048)
);

INSERT INTO customers (name, email, balance) VALUES
    ('Alice', 'alice@example.com', 100.00),
    ('Bob', 'bob@example.com', 200.00),
    ('Carol', 'carol@example.com', 150.00);
