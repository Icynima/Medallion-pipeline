-- ─────────────────────────────────────────────────────────
-- Day 8 – Data Warehouse Schema Initialization
-- Runs automatically when PostgreSQL container starts
-- ─────────────────────────────────────────────────────────

-- ============================================================
-- BRONZE LAYER – raw ingested data (append-only)
-- ============================================================
CREATE TABLE IF NOT EXISTS bronze_orders (
    _load_id       SERIAL PRIMARY KEY,
    order_id       INTEGER,
    customer_id    INTEGER,
    product_id     VARCHAR(32),
    product_name   VARCHAR(255),
    category       VARCHAR(64),
    quantity       INTEGER,
    unit_price     NUMERIC(12, 2),
    total_amount   NUMERIC(12, 2),
    order_date     TEXT,
    status         VARCHAR(32),
    source         VARCHAR(32) DEFAULT 'csv',
    _loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze_customers (
    _load_id       SERIAL PRIMARY KEY,
    customer_id    INTEGER,
    customer_name  VARCHAR(255),
    email          VARCHAR(255),
    city           VARCHAR(128),
    country        VARCHAR(64),
    signup_date    TEXT,
    _loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bronze_kafka_events (
    _load_id       SERIAL PRIMARY KEY,
    topic          VARCHAR(128),
    partition_id   INTEGER,
    offset_id      BIGINT,
    key            TEXT,
    payload        JSONB,
    event_time     TIMESTAMP,
    _loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- SILVER LAYER – cleansed, typed, deduplicated
-- ============================================================
CREATE TABLE IF NOT EXISTS silver_orders (
    order_id       INTEGER PRIMARY KEY,
    customer_id    INTEGER NOT NULL,
    product_id     VARCHAR(32),
    product_name   VARCHAR(255),
    category       VARCHAR(64),
    quantity       INTEGER CHECK (quantity > 0),
    unit_price     NUMERIC(12, 2),
    total_amount   NUMERIC(12, 2),
    order_date     DATE,
    status         VARCHAR(32),
    _processed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver_customers (
    customer_id    INTEGER PRIMARY KEY,
    customer_name  VARCHAR(255) NOT NULL,
    email          VARCHAR(255),
    city           VARCHAR(128),
    country        VARCHAR(64),
    signup_date    DATE,
    _processed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- GOLD LAYER – aggregated business metrics
-- ============================================================
CREATE TABLE IF NOT EXISTS gold_customer_360 (
    customer_id        INTEGER PRIMARY KEY,
    customer_name      VARCHAR(255),
    email              VARCHAR(255),
    city               VARCHAR(128),
    country            VARCHAR(64),
    total_orders       INTEGER,
    total_revenue      NUMERIC(14, 2),
    avg_order_value    NUMERIC(12, 2),
    first_order_date   DATE,
    last_order_date    DATE,
    top_category       VARCHAR(64),
    customer_segment   VARCHAR(32),
    _computed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold_daily_sales (
    order_date         DATE PRIMARY KEY,
    total_orders       INTEGER,
    total_revenue      NUMERIC(14, 2),
    unique_customers   INTEGER,
    avg_order_value    NUMERIC(12, 2),
    top_product        VARCHAR(255),
    _computed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold_product_performance (
    product_id         VARCHAR(32),
    product_name       VARCHAR(255),
    category           VARCHAR(64),
    total_sold         INTEGER,
    total_revenue      NUMERIC(14, 2),
    avg_unit_price     NUMERIC(12, 2),
    order_count        INTEGER,
    _computed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id)
);

-- ============================================================
-- PIPELINE METADATA – execution tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS pipeline_execution_log (
    log_id             SERIAL PRIMARY KEY,
    dag_id             VARCHAR(255),
    run_id             VARCHAR(255),
    task_id            VARCHAR(255),
    layer              VARCHAR(32),
    table_name         VARCHAR(255),
    records_processed  INTEGER,
    records_rejected   INTEGER,
    status             VARCHAR(32),
    error_message      TEXT,
    started_at         TIMESTAMP,
    finished_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- DATA QUALITY – validation results
-- ============================================================
CREATE TABLE IF NOT EXISTS data_quality_results (
    check_id           SERIAL PRIMARY KEY,
    dag_id             VARCHAR(255),
    check_name         VARCHAR(255),
    table_name         VARCHAR(255),
    check_sql          TEXT,
    expected_result    VARCHAR(64),
    actual_result      VARCHAR(64),
    passed             BOOLEAN,
    checked_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
