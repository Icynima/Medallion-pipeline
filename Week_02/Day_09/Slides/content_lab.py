"""Section 5 — Lab walk-through & wrap-up (teacher-friendly)."""
from __future__ import annotations
import theme as T


def specs(images, accent):
    src_lab = "Lab_Files/LABS_GUIDE.md"

    return [
        # ============================================================
        # DIVIDER
        # ============================================================
        dict(
            kind="divider",
            number=5,
            title="Practical Block",
            summary="Theory was the recipe. Now we cook. "
                    "15 labs, 4 hours, one fault-injection finale.",
            accent=accent,
        ),

        # ---- Logistics ----
        dict(
            kind="content",
            title="How the next 4 hours work",
            section="Lab · Logistics",
            accent=accent,
            bullets=[
                "All code lives in Lab_Files/ — read LABS_GUIDE.md first",
                "Bootstrap ONCE: ./bootstrap.sh (Linux/Mac) or bootstrap.cmd (Win)",
                "Each lab stands alone — you can re-run any single one",
                "Labs 1-5 = warm-up · 6-11 = topic deep dives · 12-15 = scaling & faults",
                "We pause every 4 labs for questions",
            ],
            right_panel=("text",
                "WHAT YOU NEED OPEN\n\n"
                "Browser tabs:\n"
                "  Grafana          → :3000\n"
                "  Prometheus       → :9090\n"
                "  Kafka UI         → :8080\n"
                "  Schema Registry  → :8081\n"
                "  ksqlDB           → :8088\n\n"
                "Terminal:\n"
                "  python venv activated\n"
                "  docker ps shows 8 containers"),
            source=src_lab,
            notes=(
                "Make sure everyone's environment is up BEFORE diving "
                "into labs. The bootstrap script handles 95% of setup."
            ),
        ),

        # ---- Pick your path ----
        dict(
            kind="content",
            title="If you're short on time — the priority order",
            section="Lab · Path",
            accent=accent,
            bullets=[
                "MUST-DO (in order): Lab 6, Lab 9, Lab 11, Lab 14, Lab 15",
                "Lab 6 = observability stack (you'll use it for everything else)",
                "Lab 9 = DLQ + recovery (the most realistic incident drill)",
                "Lab 11 = Schema Registry (interview gold)",
                "Lab 14 = scaling out live",
                "Lab 15 = the fault-injection finale",
            ],
            right_panel=("text",
                "TIME-BOXED PATH\n\n"
                "If you only have 2 hours:\n"
                "  Lab 1  · 15 min  setup\n"
                "  Lab 6  · 30 min  observability\n"
                "  Lab 9  · 30 min  DLQ\n"
                "  Lab 15 · 45 min  finale\n\n"
                "Skip everything else if you must.\n"
                "Those four cover the whole deck."),
            source=src_lab,
            notes=(
                "Give them an explicit priority list. People worry about "
                "falling behind — the priority list is permission to skip."
            ),
        ),

        # ---- All 15 labs ----
        dict(
            kind="table",
            title="The 15 labs — what you do, what you learn",
            section="Lab · Roadmap",
            accent=accent,
            headers=["#", "Lab", "You will…"],
            rows=[
                ["1", "Bootstrap the cluster",
                 "Bring up Kafka + Postgres + Connect"],
                ["2", "Seed topics",
                 "Create topics with correct partition / RF"],
                ["3", "Produce trips",
                 "Run taxi_simulator at 100 msg/s"],
                ["4", "Consume + warehouse",
                 "Land trips in Postgres warehouse"],
                ["5", "CDC the drivers table",
                 "Register Debezium connector"],
                ["6", "Wire observability ★",
                 "Prometheus + Grafana + JMX exporter"],
                ["7", "Write alerts",
                 "alerts.yml + Alertmanager rules"],
                ["8", "Structured logs + trace IDs",
                 "Promtail → Loki, end-to-end trace"],
                ["9", "DLQ + recovery ★",
                 "Inject poison-pills, drain with dlq_tool"],
                ["10", "Data-quality validator",
                 "Eight expectations, fail → DLQ"],
                ["11", "Schema Registry ★",
                 "Evolve under BACKWARD, observe rejection"],
                ["12", "Tune producer batching",
                 "Measure throughput vs linger.ms"],
                ["13", "ksqlDB surge detector",
                 "Windowed aggregation on streams"],
                ["14", "Add a broker live ★",
                 "Reassign partitions under load"],
                ["15", "Fault-injection finale ★",
                 "Break the cluster, diagnose live"],
            ],
            source=src_lab,
            notes=(
                "Walk down the column. Stars mark the must-do labs. "
                "Reinforce that 9, 11, 14, 15 are the keepers."
            ),
        ),

        # ---- Finale ----
        dict(
            kind="content",
            title="The grand finale — Lab 15 runbook",
            section="Lab · Finale",
            accent=accent,
            bullets=[
                "Load: 5 000 trips/s sustained for 10 minutes",
                "We inject FOUR failures, one at a time",
                "1) docker pause kafka-2 (broker freeze)",
                "2) tc qdisc add (300 ms latency on a consumer pod)",
                "3) drop the drivers Postgres replica",
                "4) push a schema rename to Schema Registry",
                "You diagnose each using ONLY dashboards + logs",
            ],
            right_panel=("text",
                "SCORING (per failure)\n\n"
                "Detected the issue:    1 pt\n"
                "Identified root cause: 2 pt\n"
                "Mitigated correctly:   2 pt\n\n"
                "Max 20 pts across 4 actions.\n\n"
                "Format: ONE person at the keyboard\n"
                "(rotates per failure).\n"
                "Everyone else watches dashboards\n"
                "and helps diagnose."),
            source=src_lab,
            notes=(
                "This is the moment the day pays off. Four failures map "
                "to four theory blocks: scaling, logging, quality, schemas."
            ),
        ),

        # ---- Wrap-up ----
        dict(
            kind="content",
            title="Wrap-up — what to take into Day 10",
            section="Lab · Wrap",
            accent=accent,
            bullets=[
                "Tomorrow = capstone — production-readiness review of YOUR pipeline",
                "Bring: notes, favourite Grafana panel, scariest DLQ message",
                "We'll run a mock incident review on your code",
                "Tonight (optional): SRE Workbook chapters 4 (SLOs) and 5 (alerting)",
                "If you remember nothing else: alert on symptoms, dashboard on "
                "causes, structured logs everywhere, schemas always",
            ],
            right_panel=("text",
                "TODAY IN 7 WORDS:\n\n"
                "Latency · Traffic · Errors · Saturation\n"
                "Logs · Schemas · Backpressure\n\n"
                "If these feel natural by 5 p.m.,\n"
                "we succeeded.\n\n"
                "Have fun breaking things\n"
                "in the lab."),
            source=src_lab,
            notes=(
                "Close warmly. Remind them tomorrow reviews THEIR "
                "pipeline. Take questions, then break for labs."
            ),
        ),
    ]
