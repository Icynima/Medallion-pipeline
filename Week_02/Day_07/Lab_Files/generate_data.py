from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SOURCE_DIR = DATA_DIR / "source"


CUSTOMERS = [
    {
        "customer_id": 501,
        "customer_name": "Ada Retail",
        "email": "ada@example.com",
        "country": "US",
        "region": "NA",
        "signup_date": "2026-01-15",
        "loyalty_tier": "Gold",
    },
    {
        "customer_id": 502,
        "customer_name": "Ravi Stores",
        "email": "RAVI@EXAMPLE.COM",
        "country": "IN",
        "region": "APAC",
        "signup_date": "2026-02-20",
        "loyalty_tier": "Silver",
    },
    {
        "customer_id": 503,
        "customer_name": "Sofia Market",
        "email": "sofia@example.com",
        "country": "ES",
        "region": "EMEA",
        "signup_date": "2026-03-05",
        "loyalty_tier": "Bronze",
    },
    {
        "customer_id": 504,
        "customer_name": "Mina Travel",
        "email": "mina@example.com",
        "country": "DE",
        "region": "EMEA",
        "signup_date": "2026-01-29",
        "loyalty_tier": "Gold",
    },
    {
        "customer_id": 505,
        "customer_name": "Omar Services",
        "email": "omar@example.com",
        "country": "AE",
        "region": "MEA",
        "signup_date": "2026-04-14",
        "loyalty_tier": "Silver",
    },
    {
        "customer_id": 506,
        "customer_name": "Nia Wholesale",
        "email": "nia@example.com",
        "country": "US",
        "region": "NA",
        "signup_date": "2026-05-01",
        "loyalty_tier": "Bronze",
    },
]


PRODUCTS = [
    {
        "product_id": "P-LAP-01",
        "product_name": "Cloud Laptop",
        "category": "electronics",
        "unit_cost": 820.00,
    },
    {
        "product_id": "P-PHN-02",
        "product_name": "Edge Phone",
        "category": "electronics",
        "unit_cost": 410.00,
    },
    {
        "product_id": "P-HDP-03",
        "product_name": "Noise Cancel Headphones",
        "category": "accessories",
        "unit_cost": 55.00,
    },
    {
        "product_id": "P-CAM-04",
        "product_name": "Action Camera",
        "category": "electronics",
        "unit_cost": 190.00,
    },
    {
        "product_id": "P-BAG-05",
        "product_name": "Travel Bag",
        "category": "travel",
        "unit_cost": 35.00,
    },
    {
        "product_id": "P-SVC-99",
        "product_name": "Installation Service",
        "category": "services",
        "unit_cost": 25.00,
    },
]


FX_RATES = [
    {"currency": "USD", "rate_to_usd": 1.00, "as_of_date": "2026-05-30"},
    {"currency": "EUR", "rate_to_usd": 1.08, "as_of_date": "2026-05-30"},
    {"currency": "INR", "rate_to_usd": 0.012, "as_of_date": "2026-05-30"},
]


ORDER_BATCH_1 = [
    {
        "event_id": "evt-1001",
        "order_id": 1001,
        "customer_id": 501,
        "product_id": "P-LAP-01",
        "status": "NEW",
        "amount": 1299.99,
        "currency": "USD",
        "channel": "web",
        "event_time": "2026-05-29T02:00:01Z",
    },
    {
        "event_id": "evt-1002",
        "order_id": 1002,
        "customer_id": 502,
        "product_id": "P-PHN-02",
        "status": "NEW",
        "amount": 799.00,
        "currency": "USD",
        "channel": "mobile",
        "event_time": "2026-05-29T02:00:05Z",
    },
    {
        "event_id": "evt-1003",
        "order_id": 1003,
        "customer_id": 503,
        "product_id": "P-HDP-03",
        "status": "NEW",
        "amount": 149.50,
        "currency": "USD",
        "channel": "store",
        "event_time": "2026-05-29T02:00:08Z",
    },
    {
        "event_id": "evt-1004",
        "order_id": 1002,
        "customer_id": 502,
        "product_id": "P-PHN-02",
        "status": "NEW",
        "amount": 799.00,
        "currency": "USD",
        "channel": "mobile",
        "event_time": "2026-05-29T02:00:05Z",
    },
    {
        "event_id": "evt-1005",
        "order_id": 1004,
        "customer_id": 504,
        "product_id": "P-CAM-04",
        "status": "CANCELLED",
        "amount": 450.00,
        "currency": "USD",
        "channel": "web",
        "event_time": "2026-05-29T02:00:20Z",
    },
    {
        "event_id": "evt-1006",
        "order_id": 1005,
        "customer_id": 505,
        "product_id": "P-BAG-05",
        "status": "NEW",
        "amount": -10.00,
        "currency": "USD",
        "channel": "web",
        "event_time": "2026-05-29T02:00:30Z",
    },
]


ORDER_BATCH_2 = [
    {
        "event_id": "evt-1007",
        "order_id": 1001,
        "customer_id": 501,
        "product_id": "P-LAP-01",
        "status": "SHIPPED",
        "amount": 1299.99,
        "currency": "USD",
        "channel": "web",
        "event_time": "2026-05-30T09:00:01Z",
        "coupon_code": "SPRING10",
        "delivery_promise": "2-day",
    },
    {
        "event_id": "evt-1008",
        "order_id": 1006,
        "customer_id": 504,
        "product_id": "P-BAG-05",
        "status": "NEW",
        "amount": 89.99,
        "currency": "EUR",
        "channel": "web",
        "event_time": "2026-05-30T09:05:00Z",
        "delivery_promise": "standard",
    },
    {
        "event_id": "evt-1009",
        "order_id": 1007,
        "customer_id": 999,
        "product_id": "P-CAM-04",
        "status": "NEW",
        "amount": 450.00,
        "currency": "USD",
        "channel": "partner",
        "event_time": "2026-05-30T09:07:00Z",
    },
    {
        "event_id": "evt-1010",
        "order_id": 1008,
        "customer_id": 506,
        "product_id": None,
        "status": "NEW",
        "amount": 25.00,
        "currency": "USD",
        "channel": "store",
        "event_time": "2026-05-30T09:10:00Z",
    },
    {
        "event_id": "evt-1011",
        "order_id": 1002,
        "customer_id": 502,
        "product_id": "P-PHN-02",
        "status": "CANCELLED",
        "amount": 799.00,
        "currency": "USD",
        "channel": "mobile",
        "event_time": "2026-05-30T09:12:00Z",
        "coupon_code": "SAVE20",
    },
    {
        "event_id": "evt-1012",
        "order_id": 1009,
        "customer_id": 505,
        "product_id": "P-SVC-99",
        "status": "PAID",
        "amount": 40.00,
        "currency": "USD",
        "channel": "web",
        "event_time": "2026-05-30T09:15:00Z",
    },
]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(SOURCE_DIR / "customers.csv", CUSTOMERS)
    write_csv(SOURCE_DIR / "products.csv", PRODUCTS)
    write_csv(SOURCE_DIR / "fx_rates.csv", FX_RATES)
    write_jsonl(SOURCE_DIR / "order_events_batch_1.jsonl", ORDER_BATCH_1)
    write_jsonl(SOURCE_DIR / "order_events_batch_2.jsonl", ORDER_BATCH_2)
    print(f"Wrote Day 7 source data to {SOURCE_DIR}")


if __name__ == "__main__":
    main()
