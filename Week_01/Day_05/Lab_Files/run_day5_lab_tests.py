#!/usr/bin/env python3
"""One-command proof runner for the Day 5 client-ready lab."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import medallion_pipeline


ROOT = Path(__file__).resolve().parent


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def assert_equal(actual, expected, label: str, lines: list[str]) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")
    lines.append(f"PASS {label}: {actual!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qa-dir", default=None, help="Optional folder for proof logs")
    args = parser.parse_args()

    lines: list[str] = []
    metrics = medallion_pipeline.run_all()
    lines.append("Day 5 client-ready lab proof run")
    lines.append(json.dumps(metrics, indent=2, sort_keys=True))

    assert_equal(metrics["orders_bronze"], 7, "Bronze order CDC events", lines)
    assert_equal(metrics["duplicate_events"], 1, "Duplicate CDC event quarantined", lines)
    assert_equal(metrics["valid_current_orders"], 2, "Silver current orders", lines)
    assert_equal(metrics["valid_shipments"], 2, "Silver valid shipments", lines)
    assert_equal(metrics["dlq_records"], 2, "DLQ logistics rejects", lines)

    kpis = read_csv(ROOT / "outputs" / "gold" / "daily_order_kpis.csv")
    assert_equal(kpis[0]["recognized_revenue"], "195.50", "Gold recognized revenue", lines)
    assert_equal(kpis[0]["paid_or_shipped_count"], "2", "Gold paid/shipped order count", lines)

    decisions = json.loads((ROOT / "outputs" / "silver" / "schema_change_decisions.json").read_text(encoding="utf-8"))
    assert_equal([d["decision"] for d in decisions], ["ACCEPT", "REJECT", "ACCEPT"], "Schema decision sequence", lines)

    compose_file = ROOT / "docker-compose.yml"
    if compose_file.exists():
        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "config"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode == 0:
            lines.append("PASS docker compose config")
        else:
            raise AssertionError("docker compose config failed:\n" + result.stderr)

    log_text = "\n".join(lines) + "\n"
    print(log_text)
    if args.qa_dir:
        qa_dir = Path(args.qa_dir)
        qa_dir.mkdir(parents=True, exist_ok=True)
        (qa_dir / "day5_lab_test_run.log").write_text(log_text, encoding="utf-8")
        (qa_dir / "day5_lab_run_summary.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        sys.exit(1)
