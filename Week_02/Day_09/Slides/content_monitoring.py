"""Section 1 — Pipeline Monitoring (teacher-friendly).

Story arc per concept:
  intro → analogy → visual → real example → recap-before-quiz → quiz → answer
"""
from __future__ import annotations
import theme as T


def specs(images, accent):
    src_sre = "sre.google/sre-book/monitoring-distributed-systems/"
    src_prom = "prometheus.io/docs/practices/instrumentation/"
    src_kafka = "kafka.apache.org/documentation/#monitoring"

    return [
        # ============================================================
        # SECTION DIVIDER
        # ============================================================
        dict(
            kind="divider",
            number=1,
            title="Pipeline Monitoring",
            summary="How do we know our pipeline is healthy? "
                    "We watch four simple numbers.",
            accent=accent,
        ),

        # ============================================================
        # CONCEPT 1 — Why monitor at all?
        # ============================================================

        dict(
            kind="content",
            title="What does 'monitoring' even mean?",
            section="Monitoring · Intro",
            accent=accent,
            bullets=[
                "Monitoring = watching your pipeline 24/7 so a computer "
                "tells you when something breaks",
                "Without it, you only find out when a customer complains",
                "With it, you fix problems BEFORE customers notice",
                "Think of it like a smoke alarm in your house — you don't "
                "watch it, but it screams when needed",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "Driving a car:\n\n"
                "Speedometer = how fast you go\n"
                "Fuel gauge  = how much is left\n"
                "Warning light = something broke\n"
                "Dashboard  = all of it in one glance\n\n"
                "Monitoring a pipeline =\n"
                "a dashboard for your data."),
            notes=(
                "Start at the simplest level. Monitoring is just watching "
                "the pipeline with software so a human does not have to. "
                "Use the car analogy — everyone has seen a dashboard."
            ),
        ),

        dict(
            kind="content",
            title="Monitoring does three jobs (not just one)",
            section="Monitoring · Three jobs",
            accent=accent,
            bullets=[
                "1) DETECT — wake someone up: 'Something is wrong RIGHT NOW'",
                "2) DIAGNOSE — help them find WHERE and WHY",
                "3) PLAN — show trends over weeks: 'we'll need more servers next month'",
                "Same data, three uses. Most teams only do #1 and wonder "
                "why incidents are confusing",
            ],
            right_panel=("text",
                "EXAMPLE\n\n"
                "3:00 AM — phone rings (DETECT)\n"
                "        'Consumer lag too high!'\n\n"
                "3:02 AM — open dashboard (DIAGNOSE)\n"
                "        'Broker 2 fell out of ISR'\n\n"
                "3:10 AM — incident done\n"
                "Next month — review (PLAN)\n"
                "        'add a 4th broker'"),
            source=src_sre,
            notes=(
                "Three different time-scales: seconds for detection, "
                "minutes for diagnosis, weeks for planning. Same data "
                "feeds all three."
            ),
        ),

        # ============================================================
        # CONCEPT 2 — Four Golden Signals
        # ============================================================

        dict(
            kind="chart",
            title="The Four Golden Signals — your cheat sheet",
            section="Monitoring · Golden Signals",
            accent=accent,
            chart_path=images["four_golden_signals"],
            caption="Four questions you should always be able to answer "
                    "about any service.",
            source=src_sre,
            notes=(
                "Walk through each quadrant slowly. These four words are "
                "the single most useful thing they'll learn today."
            ),
        ),

        dict(
            kind="content",
            title="The Four Golden Signals — in plain English",
            section="Monitoring · Golden Signals",
            accent=accent,
            bullets=[
                "LATENCY: 'How LONG does each request take?' (slow = bad)",
                "TRAFFIC: 'How MUCH work is the system doing?' (req/s, MB/s)",
                "ERRORS: 'How OFTEN does something fail?' (errors/total)",
                "SATURATION: 'How FULL is the system?' (CPU, disk, queue)",
                "Memorise these four words. Every dashboard ever, ever, ever.",
            ],
            right_panel=("text",
                "RESTAURANT ANALOGY\n\n"
                "LATENCY → how long until food arrives?\n"
                "TRAFFIC → how many customers tonight?\n"
                "ERRORS → how many orders are wrong?\n"
                "SATURATION → how full is the kitchen?\n\n"
                "If you can answer all four, the\n"
                "restaurant is OBSERVABLE."),
            source=src_sre,
            notes=(
                "Use the restaurant analogy. It works for every audience. "
                "Make them repeat the four words back to you."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Let's get ready for a quiz — match these examples",
            section="Monitoring · Pre-quiz",
            accent=accent,
            bullets=[
                "'The site is slow today' → which signal? (LATENCY)",
                "'We had 10× more users today' → which signal? (TRAFFIC)",
                "'1% of orders returned a 500 error' → which signal? (ERRORS)",
                "'Our database disk is 95% full' → which signal? (SATURATION)",
                "Now try the same exercise for a Kafka producer →",
            ],
            right_panel=("text",
                "NEXT SLIDE\n\n"
                "Producer reports 0.3% of sends fail with\n"
                "NotEnoughReplicasException.\n\n"
                "Which Golden Signal best describes this?\n\n"
                "Think:\n"
                "  Is it slow? (Latency)\n"
                "  Is it busy? (Traffic)\n"
                "  Did it fail? (Errors) ←\n"
                "  Is it full? (Saturation)"),
            notes=(
                "Walk through the four examples slowly. By the time they "
                "see the quiz, the answer should be obvious."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — which Golden Signal?",
            section="Monitoring · Quiz",
            qtype="MCQ",
            question="A producer reports 0.3% of sends fail with "
                     "NotEnoughReplicasException. Which Golden Signal is this?",
            options=[
                "Latency",
                "Traffic",
                "Errors",
                "Saturation",
            ],
            notes="Walk through each option. 'Fail' = Errors.",
        ),
        dict(
            kind="answer",
            title="Answer — Errors",
            section="Monitoring · Quiz",
            answer="C. Errors",
            explanation=(
                "The key word is 'fail'. Anything that fails belongs to "
                "the ERRORS signal.\n\n"
                "Bonus insight: this kind of error often happens because "
                "the broker is overloaded (SATURATION). So you'd put both "
                "panels next to each other on a dashboard."
            ),
        ),

        # ============================================================
        # CONCEPT 3 — Pull vs push, and Prometheus
        # ============================================================

        dict(
            kind="content",
            title="How does a monitoring tool collect data?",
            section="Monitoring · Prometheus",
            accent=accent,
            bullets=[
                "PUSH model: each service sends its numbers to a central place",
                "PULL model: the central place asks each service for its numbers",
                "Prometheus uses PULL — it visits every service every 15 seconds "
                "and asks 'how are you?'",
                "Each service answers by exposing a simple text page at /metrics",
                "That's it. No magic. Just HTTP requests on a timer.",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "PUSH = each kid yells\n"
                "      'I'm here!' constantly\n\n"
                "PULL = the teacher takes\n"
                "      attendance every morning\n\n"
                "Prometheus is the teacher.\n"
                "Your services are the kids."),
            source="prometheus.io/docs/introduction/overview/",
            notes=(
                "Pull model is unusual for new students. The classroom "
                "attendance analogy makes it click. Show the URL "
                "/metrics — it's just text they can curl."
            ),
        ),

        dict(
            kind="chart",
            title="The full Prometheus stack — who talks to who",
            section="Monitoring · Architecture",
            accent=accent,
            chart_path=images["prometheus_architecture"],
            caption="Targets expose /metrics. Prometheus scrapes them. "
                    "Alertmanager notifies humans. Grafana draws pictures.",
            source="prometheus.io/docs/introduction/overview/",
            notes=(
                "Three boxes to remember: Prometheus (collects), "
                "Alertmanager (sends alerts), Grafana (draws pretty)."
            ),
        ),

        dict(
            kind="content",
            title="Four flavours of numbers — meet the metric types",
            section="Monitoring · Metric types",
            accent=accent,
            bullets=[
                "COUNTER — a number that ONLY goes UP (total messages sent)",
                "GAUGE — a number that goes UP and DOWN (queue size, CPU)",
                "HISTOGRAM — buckets of values (how many took 0-10ms, 10-100ms…)",
                "SUMMARY — like a histogram but the percentiles are pre-computed",
                "99% of the time you only need COUNTER and GAUGE",
            ],
            right_panel=("text",
                "EXAMPLES FROM REAL LIFE\n\n"
                "Counter = car's odometer\n"
                "          (only goes up)\n\n"
                "Gauge   = speedometer\n"
                "          (goes up and down)\n\n"
                "Histogram = a survey result\n"
                "  '23 people slept 0-4 hrs,\n"
                "   89 people slept 4-8 hrs…'"),
            source=src_prom,
            notes=(
                "Odometer vs speedometer is the analogy that always "
                "clicks. Counters never decrease — they reset to zero on "
                "restart but otherwise climb forever."
            ),
        ),

        dict(
            kind="chart",
            title="See the four metric types in action",
            section="Monitoring · Metric types",
            accent=accent,
            chart_path=images["metric_types"],
            caption="From left to right: ever-rising counter, "
                    "up-and-down gauge, distribution histogram, percentile summary.",
            source=src_prom,
            notes=(
                "Just point at the shapes. The visual makes the "
                "difference obvious in a way words can't."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Before the next quiz — pick the right metric",
            section="Monitoring · Pre-quiz",
            accent=accent,
            bullets=[
                "Question to ask yourself: does this number ONLY go UP?",
                "  → YES → it's a COUNTER (e.g. total bytes sent)",
                "  → NO, goes up and down → it's a GAUGE (e.g. memory used)",
                "Question to ask: do I need to see a distribution / percentile?",
                "  → YES → it's a HISTOGRAM (e.g. request latency)",
                "Now match these four real metrics to their type →",
            ],
            right_panel=("text",
                "MATCH THESE:\n\n"
                "1. Total bytes received since start\n"
                "   (only goes up)\n\n"
                "2. Current consumer lag\n"
                "   (rises and falls)\n\n"
                "3. Distribution of latency\n"
                "   (need p95, p99)\n\n"
                "4. JVM heap usage right now\n"
                "   (snapshot)"),
            notes=(
                "Walk through each example. Make them say the type out loud "
                "before flipping to the quiz."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — pick the metric type",
            section="Monitoring · Quiz",
            qtype="MATCH",
            question="Match each metric to its Prometheus type "
                     "(Counter, Gauge, Histogram, Gauge).",
            options=[
                "Total bytes received since broker startup",
                "Current consumer lag",
                "Distribution of message processing latency",
                "Current JVM heap usage",
            ],
            notes="Counter · Gauge · Histogram · Gauge.",
        ),
        dict(
            kind="answer",
            title="Answer — Counter, Gauge, Histogram, Gauge",
            section="Monitoring · Quiz",
            answer="1·Counter   2·Gauge   3·Histogram   4·Gauge",
            explanation=(
                "1. Total bytes only goes up → COUNTER.\n"
                "2. Lag rises and falls as consumers catch up → GAUGE.\n"
                "3. We need percentiles (p95, p99) → HISTOGRAM.\n"
                "4. Heap right now is a snapshot → GAUGE.\n\n"
                "Common mistake: people use a Counter for lag, then "
                "wonder why rate() returns negative numbers."
            ),
        ),

        # ============================================================
        # CONCEPT 4 — Kafka-specific metrics
        # ============================================================

        dict(
            kind="chart",
            title="How does Kafka expose its metrics?",
            section="Monitoring · JMX",
            accent=accent,
            chart_path=images["jmx_exporter"],
            caption="Kafka speaks 'JMX'. A small agent translates JMX into "
                    "the /metrics page Prometheus understands.",
            source=src_kafka,
            notes=(
                "JMX is just Java's built-in way of exposing numbers. The "
                "JMX exporter is the bridge between Java's world and "
                "Prometheus's world."
            ),
        ),

        dict(
            kind="table",
            title="The 7 Kafka metrics you must know",
            section="Monitoring · Kafka",
            accent=accent,
            headers=["Metric", "Plain-English meaning", "Page when"],
            rows=[
                ["UnderReplicatedPartitions",
                 "Partitions missing one or more copies",
                 "> 0 for 5 min"],
                ["OfflinePartitionsCount",
                 "Partitions with no working leader",
                 "> 0 for 1 min"],
                ["ActiveControllerCount",
                 "Should be exactly 1 across whole cluster",
                 "sum != 1 for 1 min"],
                ["consumer_lag",
                 "How many messages your consumer is behind",
                 "> your SLO for 5 min"],
                ["RequestHandlerAvgIdle",
                 "% time broker threads sit doing nothing",
                 "< 20% for 10 min"],
                ["BytesIn / BytesOut per second",
                 "Network throughput per broker",
                 "Trend over weeks (capacity)"],
                ["IsrShrinksPerSec",
                 "Rate at which replicas fall out of sync",
                 "> 0 sustained"],
            ],
            source=src_kafka,
            notes=(
                "These seven cover 90% of real Kafka incidents. Memorise "
                "the first three — those are 'wake-someone-up' alerts."
            ),
        ),

        dict(
            kind="chart",
            title="Consumer lag — the #1 metric in stream processing",
            section="Monitoring · Lag",
            accent=accent,
            chart_path=images["consumer_lag"],
            caption="When the line rises, your consumer is falling behind. "
                    "Lag rises BEFORE everything else breaks.",
            source="github.com/lightbend/kafka-lag-exporter",
            notes=(
                "Lag is the leading indicator. When lag rises, you have "
                "minutes (not hours) to act before SLAs break. Show the "
                "red shaded region — that's the alert firing."
            ),
        ),

        # ============================================================
        # CONCEPT 5 — Good vs bad alerts
        # ============================================================

        dict(
            kind="content",
            title="What makes an alert WORTH waking someone up?",
            section="Monitoring · Alerts",
            accent=accent,
            bullets=[
                "RULE 1: Page on the SYMPTOM (the user feels pain)",
                "RULE 2: Don't page on the CAUSE (CPU high, disk warm)",
                "RULE 3: Every alert should be ACTIONABLE — the on-call can DO something",
                "RULE 4: Include a runbook URL — say what to do in plain words",
                "If you can't write a runbook for an alert, delete the alert",
            ],
            right_panel=("text",
                "GOOD ALERT:\n"
                "  'p99 latency > 2s for 5min'\n"
                "  → user is suffering, act now\n\n"
                "BAD ALERT:\n"
                "  'CPU > 70% for 1min'\n"
                "  → maybe nothing is wrong\n"
                "  → on-call has nothing to do\n"
                "  → false alarms train them\n"
                "    to ignore future pages"),
            source=src_sre,
            notes=(
                "Alert fatigue is the #1 reason on-call rotations burn "
                "out. Make alerting boring and rare."
            ),
        ),

        dict(
            kind="chart",
            title="Symptoms vs causes — page on the LEFT, dashboard the RIGHT",
            section="Monitoring · Alerts",
            accent=accent,
            chart_path=images["symptoms_vs_causes"],
            caption="The on-call wakes on a symptom. Then drills into "
                    "cause panels to find why.",
            source=src_sre,
            notes=(
                "Symptom-based alerting + cause-based dashboards. Two "
                "different tools for two different jobs."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Before the next quiz — score these 4 alerts",
            section="Monitoring · Pre-quiz",
            accent=accent,
            bullets=[
                "Ask of each: 'Is it a SYMPTOM the user feels?'",
                "Ask: 'Does it last long enough to be REAL?' (not 1-min spike)",
                "Ask: 'Can the on-call DO something about it?'",
                "If all three are YES → great alert. If any NO → bad alert.",
                "Now grade these four options on the next slide →",
            ],
            right_panel=("text",
                "PREVIEW THE OPTIONS:\n\n"
                "A) CPU > 70% for 1 minute\n"
                "   → cause, short, often fine. BAD.\n\n"
                "B) JVM heap > 80%\n"
                "   → cause, often normal. BAD.\n\n"
                "C) p99 latency > 5s for 5min\n"
                "   → SYMPTOM, lasts, breaches SLO. GOOD.\n\n"
                "D) Disk > 60%\n"
                "   → cause, way too low threshold. BAD."),
            notes=(
                "Walk through each option BEFORE showing the quiz. By the "
                "time they see it, the answer is obvious — that is the "
                "point: build pattern recognition."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — which alert is best?",
            section="Monitoring · Quiz",
            qtype="BEST",
            question="Which alert is most likely to be ACTIONABLE at 3 a.m.?",
            options=[
                "Broker CPU > 70 % for 1 minute",
                "JVM old-gen heap > 80 %",
                "p99 trip-ingest latency > 5 s for 5 minutes (SLO: 2 s)",
                "Disk usage on broker > 60 %",
            ],
            notes="C is symptom-based and breaches an SLO; the others are cause-side without context.",
        ),
        dict(
            kind="answer",
            title="Answer — option C",
            section="Monitoring · Quiz",
            answer="C. p99 latency breaching SLO",
            explanation=(
                "C ticks all three boxes:\n"
                "  • SYMPTOM (users feel slow ingestion)\n"
                "  • Lasts 5 min (not a flicker)\n"
                "  • Breaches an SLO (action: scale or investigate)\n\n"
                "The others are CAUSE-side. CPU at 70% might mean nothing. "
                "Use those in dashboards while diagnosing — not as pages."
            ),
        ),

        # ============================================================
        # CONCEPT 6 — PromQL + alert syntax
        # ============================================================

        dict(
            kind="content",
            title="A 30-second intro to PromQL (the query language)",
            section="Monitoring · PromQL",
            accent=accent,
            bullets=[
                "Three building blocks cover 80 % of all PromQL you'll write",
                "rate(metric[5m]) — 'how fast is this counter growing?'",
                "sum by (label) (…) — 'group results by something useful'",
                "histogram_quantile(0.99, …) — 'give me the 99th percentile'",
                "That's it. Everything else is variations on these three.",
            ],
            right_panel=("text",
                "WORDS → MATH\n\n"
                "'requests per second'\n"
                "  → rate(http_requests_total[5m])\n\n"
                "'error percentage'\n"
                "  → sum(rate(errors[5m]))\n"
                "  / sum(rate(requests[5m]))\n\n"
                "'p99 latency'\n"
                "  → histogram_quantile(0.99, …)"),
            notes=(
                "Don't drill into syntax. Just show the three idioms and "
                "promise that 99% of dashboards use only these."
            ),
        ),

        dict(
            kind="code",
            title="The 5 PromQL queries you will actually reuse",
            section="Monitoring · PromQL",
            accent=accent,
            language="promql",
            code=(
                "# 1. Requests per second (counter -> rate)\n"
                "rate(http_requests_total[5m])\n\n"
                "# 2. Error percentage (ratio of two rates)\n"
                "sum(rate(http_requests_total{status=~\"5..\"}[5m]))\n"
                "  / sum(rate(http_requests_total[5m]))\n\n"
                "# 3. p99 latency (from histogram buckets)\n"
                "histogram_quantile(0.99,\n"
                "  sum by (le) (rate(http_request_duration_seconds_bucket[5m])))\n\n"
                "# 4. Top 3 lagging consumer groups\n"
                "topk(3, sum by (group) (kafka_consumergroup_lag))\n\n"
                "# 5. JVM heap saturation\n"
                "jvm_memory_used_bytes{area=\"heap\"}\n"
                "  / jvm_memory_max_bytes{area=\"heap\"}"
            ),
            caption="Copy-paste these into Grafana and tweak the metric names.",
            source="prometheus.io/docs/prometheus/latest/querying/basics/",
            notes=(
                "These five queries appear in 90% of real dashboards. "
                "Encourage them to bookmark this slide."
            ),
        ),

        dict(
            kind="code",
            title="Anatomy of an alert rule — read top to bottom",
            section="Monitoring · Alertmanager",
            accent=accent,
            language="yaml",
            code=(
                "- alert: HighConsumerLag       # name shown in PagerDuty\n"
                "  expr: sum by (group) (kafka_consumergroup_lag) > 10000\n"
                "  for: 5m                       # must stay true for 5min\n"
                "  labels:\n"
                "    severity: page              # routes via Alertmanager\n"
                "    team: streaming\n"
                "  annotations:\n"
                "    summary: \"Consumer group {{ $labels.group }} is lagging\"\n"
                "    runbook: \"https://wiki/runbooks/kafka-lag\"\n"
                "    description: |\n"
                "      Group {{ $labels.group }} lag = {{ $value }} msgs\n"
                "      for >5 min. See dashboard panel 'Consumer lag'."
            ),
            caption="`for: 5m` kills false positives. `runbook:` kills 3 a.m. confusion.",
            source="prometheus.io/docs/alerting/latest/configuration/",
            notes=(
                "Highlight the 'for' clause and the runbook URL. Without "
                "these two fields, the alert is half-built."
            ),
        ),

        # ============================================================
        # CONCEPT 7 — SLOs in plain English
        # ============================================================

        dict(
            kind="content",
            title="SLI · SLO · SLA — three letters that confuse everyone",
            section="Monitoring · SLOs",
            accent=accent,
            bullets=[
                "SLI = a NUMBER you measure (e.g. p99 latency in seconds)",
                "SLO = a TARGET for that number (e.g. 'p99 < 2s 99.9% of the time')",
                "SLA = a CONTRACT — break the SLO and you owe money",
                "Error budget = the slack you can spend on risk "
                "(1 − SLO target)",
                "Keep your SLO tighter than your SLA — internal early warning",
            ],
            right_panel=("text",
                "RESTAURANT VERSION\n\n"
                "SLI = average wait time tonight\n"
                "      (measured: 18 minutes)\n\n"
                "SLO = our goal: under 20 minutes\n"
                "      95 % of nights\n\n"
                "SLA = if we go over 30 minutes,\n"
                "      free dessert (signed contract)\n\n"
                "Error budget = the 5% of nights\n"
                "      you can run long."),
            source="sre.google/workbook/implementing-slos/",
            notes=(
                "Three vocabulary words people constantly conflate. "
                "Memory hook: Indicator -> Objective -> Agreement."
            ),
        ),

        dict(
            kind="table",
            title="SLI · SLO · SLA — applied to our trips pipeline",
            section="Monitoring · SLOs",
            accent=accent,
            headers=["Term", "Plain meaning", "Example for trip-ingest"],
            rows=[
                ["SLI", "What we MEASURE",
                 "p99 ingest latency in seconds"],
                ["SLO", "Our internal TARGET",
                 "p99 < 2 s for 99.9 % of 30-day windows"],
                ["SLA", "The customer CONTRACT",
                 "Refund $X if monthly availability < 99.5 %"],
                ["Error budget", "The slack — risk you can afford",
                 "0.1 % of 30 days ~ 43 min/month"],
            ],
            source="sre.google/workbook/implementing-slos/",
            notes=(
                "Same vocabulary, this time grounded in our actual "
                "pipeline. Make it concrete."
            ),
        ),

        # ============================================================
        # CONCEPT 8 — Dashboards & pipeline reference
        # ============================================================

        dict(
            kind="content",
            title="What does a GOOD dashboard look like?",
            section="Monitoring · Dashboards",
            accent=accent,
            bullets=[
                "Top row = SYMPTOMS (the Four Golden Signals)",
                "Rows below = CAUSES (CPU, memory, queue depth)",
                "One screen, one service — don't mix prod and staging",
                "Use COLOUR for state: green ok, yellow warn, red page",
                "Annotate deploys on the time axis — context wins arguments",
                "If a panel doesn't help during an incident, DELETE it",
            ],
            right_panel=("text",
                "GOOD vs BAD\n\n"
                "BAD:\n"
                "  60 random panels\n"
                "  No clear top row\n"
                "  Mixed environments\n\n"
                "GOOD:\n"
                "  4 panels on top:\n"
                "    latency · traffic · errors · sat\n"
                "  Cause panels below the fold\n"
                "  ONE service per dashboard"),
            source="grafana.com/docs/grafana/latest/dashboards/",
            notes=(
                "A dashboard is a tool, not art. The first panel an "
                "on-call sees should answer: 'is the USER ok?'"
            ),
        ),

        dict(
            kind="chart",
            title="The pipeline we'll be monitoring today",
            section="Monitoring · Reference",
            accent=accent,
            chart_path=images["pipeline_arch"],
            caption="Every box exposes /metrics. Every line ships logs. "
                    "All of it flows into Prometheus + Loki.",
            source="Lab_Files/docker-compose.yml",
            notes=(
                "Quick orientation map. Sources left, Kafka middle, "
                "processors and observability right. Reference back to "
                "this throughout the day."
            ),
        ),

        dict(
            kind="lab",
            title="Hands-on: stand up Prometheus + Grafana",
            section="Monitoring · Lab",
            lab_name="Lab 6 · Observability stack",
            summary="Wire the JMX exporter to a broker, scrape it from "
                    "Prometheus, open the trips dashboard in Grafana.",
            bullets=[
                "Open Lab_Files/prometheus.yml — see the kafka scrape job",
                "Open Lab_Files/jmx_exporter/kafka.yml — see MBean rules",
                "Open Grafana on http://localhost:3000 (admin / admin)",
                "Find the 'Under-replicated partitions' panel",
                "Stop a broker container and watch the panel turn red",
            ],
            notes=(
                "First practical of the day. Goal: see a real number "
                "change in real time after they break something on "
                "purpose."
            ),
        ),
    ]
