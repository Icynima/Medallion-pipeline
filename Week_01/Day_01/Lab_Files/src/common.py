"""Shared helpers for the Week 1 Day 1 dependency-free Python labs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_jsonl(path: Path, records: Iterable[dict[str, Any]], append: bool = False) -> None:
    ensure_dir(path.parent)
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]
