"""Clear generated learning outputs without modifying supplied input data."""

from __future__ import annotations

import shutil

from common import OUT


if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)
print(f"Reset generated lab outputs: {OUT}")
