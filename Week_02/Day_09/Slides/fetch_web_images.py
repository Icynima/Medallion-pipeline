"""Download official-docs screenshots and logos into images/web/ (idempotent).

Run once:
    .\.venv\Scripts\python.exe fetch_web_images.py

If a file is already on disk, the URL is skipped. SVGs are rasterised to PNG
with svglib + reportlab so python-pptx can embed them.
"""
from __future__ import annotations
from pathlib import Path
import urllib.request as u
import io

HERE = Path(__file__).parent
OUT = HERE / "images" / "web"
OUT.mkdir(parents=True, exist_ok=True)


# (filename, url, attribution)
ASSETS = [
    # ── Kafka official ────────────────────────────────────────────────
    ("kafka_log_anatomy.png",
     "https://kafka.apache.org/images/log_anatomy.png",
     "kafka.apache.org / Apache 2.0"),
    ("kafka_consumer_groups.png",
     "https://kafka.apache.org/images/consumer-groups.png",
     "kafka.apache.org / Apache 2.0"),
    ("kafka_log_consumer.png",
     "https://kafka.apache.org/images/log_consumer.png",
     "kafka.apache.org / Apache 2.0"),
    ("kafka_streams_arch.jpg",
     "https://kafka.apache.org/40/images/streams-architecture-overview.jpg",
     "kafka.apache.org / Apache 2.0"),
    ("kafka_streams_stateful.png",
     "https://kafka.apache.org/40/images/streams-stateful_operations.png",
     "kafka.apache.org / Apache 2.0"),
    ("kafka_logo_wide.png",
     "https://kafka.apache.org/logos/kafka-logo-wide.png",
     "kafka.apache.org / Apache 2.0"),
    # ── Debezium ──────────────────────────────────────────────────────
    ("debezium_architecture.png",
     "https://debezium.io/documentation/reference/stable/_images/debezium-architecture.png",
     "debezium.io / Apache 2.0"),
    # ── ksqlDB ────────────────────────────────────────────────────────
    ("ksqldb_architecture.png",
     "https://raw.githubusercontent.com/confluentinc/ksql/master/docs/img/ksqldb-architecture.png",
     "github.com/confluentinc/ksql / Confluent Community License"),
    # ── Loki ──────────────────────────────────────────────────────────
    ("loki_overview.png",
     "https://raw.githubusercontent.com/grafana/loki/main/docs/sources/get-started/loki-overview-2.png",
     "github.com/grafana/loki / AGPL-3.0"),
    # ── Kafka UI (Interface demo) ─────────────────────────────────────
    ("kafka_ui_interface.gif",
     "https://raw.githubusercontent.com/provectus/kafka-ui/master/documentation/images/Interface.gif",
     "github.com/provectus/kafka-ui / Apache 2.0"),
    # ── Grafana logo (raster) ─────────────────────────────────────────
    ("grafana_logo.png",
     "https://github.com/grafana/grafana/raw/main/docs/logo-horizontal.png",
     "github.com/grafana/grafana / AGPL-3.0"),
]

# SVGs that get converted to PNG on disk
SVG_ASSETS = [
    ("prometheus_architecture.png",
     "https://raw.githubusercontent.com/prometheus/prometheus/main/documentation/images/architecture.svg",
     "github.com/prometheus/prometheus / Apache 2.0"),
    ("logo_prometheus.png",
     "https://upload.wikimedia.org/wikipedia/commons/3/38/Prometheus_software_logo.svg",
     "Wikimedia Commons / Apache 2.0"),
    ("logo_docker.png",
     "https://upload.wikimedia.org/wikipedia/commons/4/4e/Docker_%28container_engine%29_logo.svg",
     "Wikimedia Commons / Apache 2.0"),
    ("logo_postgres.png",
     "https://upload.wikimedia.org/wikipedia/commons/2/29/Postgresql_elephant.svg",
     "Wikimedia Commons / Public Domain"),
    ("logo_python.png",
     "https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg",
     "Wikimedia Commons / PSF Trademark"),
    ("logo_grafana.png",
     "https://upload.wikimedia.org/wikipedia/commons/a/a1/Grafana_logo.svg",
     "Wikimedia Commons / AGPL-3.0"),
]


def _fetch(url: str) -> bytes:
    req = u.Request(url, headers={"User-Agent": "Mozilla/5.0 (LabsBuilder)"})
    with u.urlopen(req, timeout=20) as r:
        return r.read()


def _svg_to_png(svg_bytes: bytes, out_path: Path, target_w: int = 800) -> None:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    drawing = svg2rlg(io.BytesIO(svg_bytes))
    if drawing is None:
        raise RuntimeError("svg2rlg returned None")
    scale = target_w / max(drawing.width, 1)
    drawing.width = drawing.width * scale
    drawing.height = drawing.height * scale
    drawing.scale(scale, scale)
    renderPM.drawToFile(drawing, str(out_path), fmt="PNG")


def main() -> None:
    ok, fail, skip = 0, 0, 0
    for name, url, attr in ASSETS:
        path = OUT / name
        if path.exists() and path.stat().st_size > 1024:
            skip += 1
            continue
        try:
            data = _fetch(url)
            path.write_bytes(data)
            print(f"  + {name:35s} {len(data)//1024:5d} KB  ({attr})")
            ok += 1
        except Exception as e:
            print(f"  ! {name:35s} FAIL: {e}")
            fail += 1

    for name, url, attr in SVG_ASSETS:
        path = OUT / name
        if path.exists() and path.stat().st_size > 1024:
            skip += 1
            continue
        try:
            data = _fetch(url)
            _svg_to_png(data, path, target_w=900)
            print(f"  + {name:35s} {path.stat().st_size//1024:5d} KB  (svg → png, {attr})")
            ok += 1
        except Exception as e:
            print(f"  ! {name:35s} FAIL: {e}")
            fail += 1

    print(f"\ndone · {ok} downloaded · {skip} cached · {fail} failed · in {OUT}")


if __name__ == "__main__":
    main()
