#!/usr/bin/env python3
"""Register Day 5 Debezium connectors with Kafka Connect."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def request_json(method: str, url: str, payload: dict | None = None) -> dict | list | str:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else ""


def register(connect_url: str, connector_file: Path) -> dict | str:
    spec = json.loads(connector_file.read_text(encoding="utf-8"))
    name = spec["name"]
    try:
        return request_json("POST", f"{connect_url}/connectors", spec)
    except urllib.error.HTTPError as exc:
        if exc.code != 409:
            raise
        return request_json("PUT", f"{connect_url}/connectors/{name}/config", spec["config"])


def connector_status(connect_url: str, name: str) -> dict | str:
    for _ in range(10):
        try:
            return request_json("GET", f"{connect_url}/connectors/{name}/status")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            time.sleep(1)
    return "status endpoint was not ready after registration"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--connect-url", default="http://localhost:8083")
    parser.add_argument(
        "connectors",
        nargs="*",
        default=["orders-connector.json"],
        help="Connector JSON files to register",
    )
    args = parser.parse_args()

    results = {}
    for connector in args.connectors:
        path = ROOT / connector
        result = register(args.connect_url.rstrip("/"), path)
        name = json.loads(path.read_text(encoding="utf-8"))["name"]
        status = connector_status(args.connect_url.rstrip("/"), name)
        results[name] = {"registration": result, "status": status}

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
