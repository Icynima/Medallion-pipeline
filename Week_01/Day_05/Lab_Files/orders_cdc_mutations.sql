-- Generate live CDC changes after the Debezium orders connector is running.

UPDATE public.orders
SET status = 'PAID',
    order_ts = '2026-06-01T10:25:00Z'
WHERE id = 1002;

UPDATE public.orders
SET status = 'SHIPPED',
    order_ts = '2026-06-01T10:35:00Z'
WHERE id = 1001;

DELETE FROM public.orders
WHERE id = 1003;

