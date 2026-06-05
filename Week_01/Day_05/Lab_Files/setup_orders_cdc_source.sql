-- Prepare the Postgres orders source for a Debezium CDC lab run.
-- Run this before registering orders-connector if you want a clean snapshot.

ALTER TABLE public.orders
  ADD COLUMN IF NOT EXISTS amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS order_ts TIMESTAMPTZ NOT NULL DEFAULT NOW();

ALTER TABLE public.orders REPLICA IDENTITY FULL;

TRUNCATE TABLE public.orders RESTART IDENTITY;

INSERT INTO public.orders (id, customer_id, status, amount, order_date, order_ts) VALUES
  (1001, 501, 'CREATED', 120.50, '2026-06-01 09:15:00', '2026-06-01T09:15:00Z'),
  (1002, 502, 'CREATED', 75.00, '2026-06-01 09:30:00', '2026-06-01T09:30:00Z'),
  (1003, 501, 'CREATED', 42.25, '2026-06-01 10:05:00', '2026-06-01T10:05:00Z');

SELECT setval('public.orders_id_seq', 1003, true);

