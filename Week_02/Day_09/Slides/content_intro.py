"""Section 0 — Day 9 intro & agenda (5 slides)."""
from __future__ import annotations
import theme as T


def specs(images, accent):
    src_sre = "sre.google/sre-book/monitoring-distributed-systems/"

    return [
        # ---- 1. Title slide ----
        dict(
            kind="title",
            title="Monitoring & Optimization",
            subtitle="Building pipelines that you can see, debug and scale",
        ),

        # ---- 2. Where we are in the bootcamp ----
        dict(
            kind="content",
            title="Where we are in the Medallion pipeline bootcamp",
            section="Day 9 · Intro",
            accent=accent,
            bullets=[
                "Day 1–3: Sources, ingestion patterns, Kafka 101",
                "Day 4–6: Stream processing, schemas, joins",
                "Day 7: Bronze · Silver · Gold layers",
                "Day 8: End-to-end pipeline with CDC and surge detection",
                "Day 9 (today): Make it observable, resilient and scalable",
                "Day 10: Capstone — production readiness review",
            ],
            right_panel=("text",
                "Yesterday we BUILT the pipeline.\n\n"
                "Today we ask the hard question:\n\n"
                "'When (not if) something breaks at 3 a.m., will the on-call\n"
                "engineer be able to (a) detect it, (b) diagnose it and\n"
                "(c) recover from it — without your help?'"),
            notes=(
                "Welcome back. Quick recap of where we are. For the last eight days "
                "we have been building a streaming taxi-trips pipeline — Kafka, "
                "Debezium CDC, a surge detector, a Postgres warehouse. That pipeline "
                "works on a laptop. The question we tackle today is the only "
                "question that matters in production: when this thing fails at "
                "three in the morning, will the on-call engineer be able to find "
                "it, fix it, and go back to sleep — without paging you? That is "
                "what monitoring, logging, data quality and scaling are all about."
            ),
        ),

        # ---- 3. Day 9 agenda ----
        dict(
            kind="content",
            title="Today’s agenda — 8 hours, split into theory and practice",
            section="Day 9 · Agenda",
            accent=accent,
            bullets=[
                "Block 1 (3–4 h) — THEORY: this deck, 100+ slides, 4 topics, "
                "quizzes throughout",
                "Topic 1: Pipeline Monitoring (≈ 50 min)",
                "Topic 2: Logging & Error Handling (≈ 45 min)",
                "Topic 3: Data Quality Checks (≈ 45 min)",
                "Topic 4: Scaling Kafka Pipelines (≈ 50 min)",
                "Block 2 (4 h) — PRACTICALS: 15 labs in Lab_Files/, "
                "fault injection finale",
            ],
            right_panel=("text",
                "Theory goal:\n"
                "you can EXPLAIN every dial you turn.\n\n"
                "Lab goal:\n"
                "you have TURNED every dial at least once.\n\n"
                "Quiz format:\n"
                "MCQ · multi-select · match-the-following ·\n"
                "fill-in-the-blanks · choose the best · true/false"),
            notes=(
                "Today is structured as two clean halves. The first three to four "
                "hours is theory — this deck. We spend roughly 45–50 minutes per "
                "topic with a quiz every five to ten slides so we never lose you. "
                "The second half is hands-on labs in the Lab_Files folder — fifteen "
                "labs ending in a fault-injection finale where we break the cluster "
                "and you diagnose it live. Take notes during theory; you will use "
                "every concept in the lab."
            ),
        ),

        # ---- 4. Learning outcomes ----
        dict(
            kind="table",
            title="Learning outcomes — what you can do by 5 p.m.",
            section="Day 9 · Outcomes",
            accent=accent,
            headers=["Outcome", "Evidence (lab)", "Theory anchor"],
            rows=[
                ["Read a Grafana dashboard during an incident",
                 "Lab 6", "Four Golden Signals · RED · USE"],
                ["Write a Prometheus alert with sane SLOs",
                 "Lab 7", "Symptoms vs causes"],
                ["Trace a single trip through the cluster",
                 "Lab 8", "Structured logs · request IDs"],
                ["Recover poison-pill messages from a DLQ",
                 "Lab 9", "Error categories · DLQ pattern"],
                ["Defend a Schema Registry compatibility mode",
                 "Lab 11", "BACKWARD · FORWARD · FULL"],
                ["Add a Kafka broker without downtime",
                 "Lab 14", "kafka-reassign-partitions · ISR"],
                ["Survive a broker failure during peak load",
                 "Lab 15", "Replication · throttling · rack awareness"],
            ],
            notes=(
                "These are the seven concrete outcomes we will hit by the end of "
                "the day. Every row of the table maps a measurable skill to a lab "
                "and to a slide section in this deck. If you only remember one "
                "thing, remember the rightmost column — those are the seven "
                "vocabulary blocks you need on your résumé."
            ),
        ),

        # ---- 5. Mental model for the day ----
        dict(
            kind="chart",
            title="Mental model — the four-quadrant operator brain",
            section="Day 9 · Mental model",
            accent=accent,
            chart_path=images["four_golden_signals"],
            caption="The Four Golden Signals are the index card. "
                    "Latency, Traffic, Errors, Saturation — "
                    "if you can answer all four for any service in 30 seconds, "
                    "you have built an observable system.",
            source=src_sre,
            notes=(
                "Keep this picture in your head for the rest of the day. The Four "
                "Golden Signals — Latency, Traffic, Errors, Saturation — come from "
                "Google's SRE book. They are the four questions you must be able to "
                "answer about every service you own, in thirty seconds, at three in "
                "the morning, with a hangover. Throughout the day we will hang every "
                "single concept — metrics, logs, schemas, partitions — onto one of "
                "these four quadrants. By 5 p.m. this picture should feel automatic."
            ),
        ),
    ]
