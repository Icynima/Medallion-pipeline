"""Section 'Tools in the Wild' — real product screenshots from official docs.

Inserts a visual tour between the intro and the monitoring deep-dive so
students see what Prometheus/Grafana/Kafka UI/Loki/etc. actually look like
BEFORE the theory dives in.

All images live in Slides/images/web/ and are downloaded by
fetch_web_images.py (idempotent).
"""
from __future__ import annotations
from pathlib import Path
import theme as T

WEB = Path(__file__).parent / "images" / "web"


def _img(name: str) -> str:
    """Return absolute path for a file in images/web/."""
    return str(WEB / name)


def specs(images, accent):
    """images: dict from chart_helpers.generate_all() (used for promql_anatomy)."""
    return [
        # ── Section divider ───────────────────────────────────────────
        dict(
            kind="divider",
            number=0,  # pre-section: visual tour comes BEFORE Topic 01
            title="Tools in the Wild",
            summary=(
                "Real screenshots from the official docs of every tool "
                "you'll touch today. Skim these now — every one of them "
                "will be in front of you during the labs."
            ),
            accent=accent,
        ),

        # ── 1. PromQL — what is it really ─────────────────────────────
        dict(
            kind="chart",
            title="What is PromQL? (the Prometheus query language)",
            section="Tools · PromQL",
            accent=accent,
            chart_path=images["promql_anatomy"],
            caption=(
                "PromQL is to Prometheus what SQL is to a database. "
                "Every query has three pieces: WHAT metric · "
                "label FILTER · what to DO with it."
            ),
            source="prometheus.io/docs/prometheus/latest/querying/basics/",
            notes=(
                "If you only remember one thing about PromQL: it's a language for "
                "asking Prometheus a question about time-series numbers. The query "
                "shown reads as: 'For HTTP requests that returned status 500, "
                "what is the rate per second over the last 5 minutes?' Every PromQL "
                "query you will ever write is some variation on this same shape. "
                "Use this slide as the reading guide when you see PromQL in the next "
                "section of the deck."
            ),
        ),

        # ── 2. Prometheus architecture (custom clean redraw) ──────────
        dict(
            kind="chart",
            title="Prometheus — architecture at a glance",
            section="Tools · Prometheus",
            accent=accent,
            chart_path=images["prometheus_official"],
            caption=(
                "Prometheus PULLS metrics from /metrics endpoints on a "
                "schedule (default every 15s), stores them in its own "
                "TSDB, then serves them to Grafana and Alertmanager."
            ),
            source="prometheus.io/docs/introduction/overview/",
            notes=(
                "This is the most important picture in the monitoring section. "
                "Note the PULL direction — Prometheus reaches out to your services, "
                "not the other way around. That single design choice is why "
                "Prometheus scales to thousands of services without any agent "
                "infrastructure on each host."
            ),
        ),

        # ── 3. Grafana — show the logo + real dashboard description ──
        dict(
            kind="content",
            title="Grafana — the visualisation layer",
            section="Tools · Grafana",
            accent=accent,
            bullets=[
                "What it is: a web UI that draws graphs from time-series data",
                "Inputs: Prometheus, Loki, InfluxDB, Postgres, 100+ data sources",
                "URL in our lab: http://localhost:3000  (login admin / admin)",
                "You DRAG metrics into PANELS, save panels into DASHBOARDS",
                "Use 'Explore' tab for ad-hoc PromQL / LogQL queries",
                "Use 'Dashboards' tab for the saved live overviews",
            ],
            right_panel=("image", _img("grafana_logo.png")),
            source="grafana.com/docs",
            notes=(
                "Grafana is the dashboard layer most teams use. Today it will be at "
                "localhost:3000 with the 'Taxi Pipeline Overview' dashboard already "
                "provisioned for you. Skim it now so the visual is familiar by Lab 5."
            ),
        ),

        # ── 4. Loki overview (official) ───────────────────────────────
        dict(
            kind="chart",
            title="Loki — the 'logs database' from Grafana Labs",
            section="Tools · Loki",
            accent=accent,
            chart_path=_img("loki_overview.png"),
            caption=(
                "Loki indexes log METADATA (labels) rather than content. "
                "Promtail tails every container's stdout and ships lines "
                "into Loki. You query them in Grafana's Explore tab using "
                "LogQL (same shape as PromQL)."
            ),
            source="github.com/grafana/loki (AGPL-3.0)",
            notes=(
                "Why Loki and not Elasticsearch? Loki is dramatically cheaper to run "
                "because it doesn't full-text-index every word. The trade-off: "
                "label-based filtering is fast, free-text search is slower. For "
                "container logs, label filtering is what you want 95 percent of the "
                "time."
            ),
        ),

        # ── 5. Kafka — log anatomy (official) ─────────────────────────
        dict(
            kind="chart",
            title="Kafka — partition log anatomy",
            section="Tools · Kafka",
            accent=accent,
            chart_path=_img("kafka_log_anatomy.png"),
            caption=(
                "A topic is sliced into PARTITIONS. Each partition is an "
                "append-only LOG. Every record gets a monotonically "
                "increasing OFFSET. Consumers track 'where am I up to' "
                "by storing the offset of the next record to read."
            ),
            source="kafka.apache.org / Apache 2.0",
            notes=(
                "This single diagram explains 80 percent of Kafka semantics. "
                "Append-only log + per-partition offset = ordered, replayable, "
                "and naturally parallelisable across partitions."
            ),
        ),

        # ── 6. Kafka — consumer groups (official) ─────────────────────
        dict(
            kind="chart",
            title="Kafka — consumer groups and partition assignment",
            section="Tools · Kafka",
            accent=accent,
            chart_path=_img("kafka_consumer_groups.png"),
            caption=(
                "One partition → AT MOST ONE consumer per group. "
                "Adding consumers helps scale only up to the partition "
                "count. Adding more after that = idle consumers. "
                "You'll prove this in Lab 13."
            ),
            source="kafka.apache.org / Apache 2.0",
            notes=(
                "This is the rule that governs scaling consumer groups. Number of "
                "consumers in a group is bounded by partition count. If you need "
                "more parallelism, you must add partitions, which we do live in Lab 13."
            ),
        ),

        # ── 7. Kafka Streams architecture (official) ──────────────────
        dict(
            kind="chart",
            title="Kafka Streams — architecture overview",
            section="Tools · Kafka Streams",
            accent=accent,
            chart_path=_img("kafka_streams_arch.jpg"),
            caption=(
                "Kafka Streams is a JAVA library that turns Kafka topics "
                "into stream-processing topologies (filter · map · join · "
                "aggregate). Our taxi_consumer.py and driver_enricher.py "
                "implement the SAME idea in Python so the logic is "
                "readable line-by-line."
            ),
            source="kafka.apache.org / Apache 2.0",
            notes=(
                "We avoid Java in the labs, but the conceptual diagram is the same: "
                "stream processors read input topics, write output topics, optionally "
                "maintain state in RocksDB. Our Python scripts mirror this design."
            ),
        ),

        # ── 8. Debezium architecture (official) ───────────────────────
        dict(
            kind="chart",
            title="Debezium — Change Data Capture for Postgres",
            section="Tools · Debezium",
            accent=accent,
            chart_path=_img("debezium_architecture.png"),
            caption=(
                "Debezium is a Kafka Connect SOURCE connector. It reads "
                "Postgres' write-ahead log (WAL) and publishes every "
                "INSERT/UPDATE/DELETE as a Kafka message. That's how the "
                "drivers table becomes a streaming topic in Lab 3."
            ),
            source="debezium.io / Apache 2.0",
            notes=(
                "CDC turns a normal database table into a stream of change events "
                "with near-zero latency, without any application changes. This is the "
                "standard way to bring transactional data into a streaming pipeline."
            ),
        ),

        # ── 9. ksqlDB architecture (official) ─────────────────────────
        dict(
            kind="chart",
            title="ksqlDB — streaming SQL on top of Kafka",
            section="Tools · ksqlDB",
            accent=accent,
            chart_path=_img("ksqldb_architecture.png"),
            caption=(
                "ksqlDB lets you write CREATE STREAM / CREATE TABLE / "
                "SELECT EMIT CHANGES statements that compile into Kafka "
                "Streams topologies running 24/7. Same things you can do "
                "in Python, but spelled as SQL. You'll try it in Lab 12."
            ),
            source="github.com/confluentinc/ksql",
            notes=(
                "ksqlDB is great when your transformation is expressible in SQL — "
                "joins, windows, aggregations. Reach for Python or Java only when "
                "the logic genuinely needs procedural code."
            ),
        ),

        # ── 10. Kafka UI (animated GIF — first frame at minimum) ─────
        dict(
            kind="chart",
            title="Kafka UI (provectus/kafka-ui) — the operator's GUI",
            section="Tools · Kafka UI",
            accent=accent,
            chart_path=_img("kafka_ui_interface.gif"),
            caption=(
                "Open-source web GUI for Kafka — same role as Confluent "
                "Control Center or Redpanda Console. Browse topics, peek "
                "at messages, manage consumer groups, view schemas. "
                "Lives at http://localhost:8080 in our lab."
            ),
            source="github.com/provectus/kafka-ui / Apache 2.0",
            notes=(
                "Animated GIF from the project README — shows the live cluster "
                "navigation. In PowerPoint it shows the first frame; preview animates "
                "the whole flow."
            ),
        ),

        # ── 11. Tools-strip slide (logos at a glance) ─────────────────
        dict(
            kind="content",
            title="Today's toolbox — at a glance",
            section="Tools · Recap",
            accent=accent,
            bullets=[
                "Kafka — the streaming log (broker · topic · partition)",
                "Debezium — CDC from Postgres → Kafka",
                "ksqlDB — streaming SQL on top of Kafka",
                "Prometheus — metrics database (pulls /metrics)",
                "Grafana — dashboards + Explore tab (PromQL + LogQL)",
                "Loki — logs database (label-indexed, cheap)",
                "Alertmanager — routes Prometheus alerts to notifications",
                "Kafka UI — the operator's web console",
                "Postgres — the upstream OLTP database",
                "Docker Compose — orchestrates all 15 containers locally",
            ],
            right_panel=("image", _img("kafka_logo_wide.png")),
            source="See each tool's official site for license details.",
            notes=(
                "Keep this slide as the table of contents for the tools. Each one "
                "got its own previous slide. By the end of Day 9 you will have "
                "interacted with every one of them at least once."
            ),
        ),
    ]
