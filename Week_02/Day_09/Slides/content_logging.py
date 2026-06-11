"""Section 2 — Logging & Error Handling (teacher-friendly).

Story arc per concept:
  intro -> analogy -> visual/example -> recap-before-quiz -> quiz -> answer
"""
from __future__ import annotations
import theme as T


def specs(images, accent):
    src_log = "12factor.net/logs"
    src_dlq = "kafka.apache.org/documentation/streams/developer-guide/config-streams.html"

    return [
        # ============================================================
        # DIVIDER
        # ============================================================
        dict(
            kind="divider",
            number=2,
            title="Logging & Error Handling",
            summary="When something breaks, logs are the only thing that "
                    "tells you WHY. Let's make them useful.",
            accent=accent,
        ),

        # ============================================================
        # CONCEPT 1 — What is a log, really?
        # ============================================================

        dict(
            kind="content",
            title="What IS a log?",
            section="Logging · Intro",
            accent=accent,
            bullets=[
                "A log is a TIME-STAMPED RECORD of something that happened",
                "Programs write logs to remember what they did",
                "When things break, logs are how we look back in time",
                "Without logs, debugging in production is GUESSING",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "A log is like a diary:\n\n"
                "  10:01 — got out of bed\n"
                "  10:15 — drank coffee\n"
                "  10:23 — fell down stairs ← BUG\n"
                "  10:24 — phone broke\n\n"
                "You can read backwards and find\n"
                "out why the phone broke."),
            notes=(
                "Start ridiculously simple. A log is a list of timestamped "
                "things that happened. The diary analogy gives the "
                "intuition for why ORDER and TIME matter."
            ),
        ),

        # ============================================================
        # CONCEPT 2 — Plain text vs structured
        # ============================================================

        dict(
            kind="content",
            title="Two kinds of logs — pick the right one",
            section="Logging · Structure",
            accent=accent,
            bullets=[
                "PLAIN-TEXT logs: easy to write — humans read them with their eyes",
                "  -> impossible to query when you have millions per minute",
                "STRUCTURED logs: written as JSON — each field is searchable",
                "  -> tools like Loki / Splunk can answer 'find me all errors for "
                "user X'",
                "Always use STRUCTURED logs in production. No exceptions.",
            ],
            right_panel=("text",
                "PLAIN TEXT (bad):\n"
                "  got trip abc-123 in 47ms\n\n"
                "STRUCTURED JSON (good):\n"
                "  {\n"
                "    'time': '2026-06-11T10:23',\n"
                "    'level': 'INFO',\n"
                "    'event': 'trip_processed',\n"
                "    'trip_id': 'abc-123',\n"
                "    'latency_ms': 47\n"
                "  }"),
            source=src_log,
            notes=(
                "Structured logs are the single highest-leverage change "
                "in any codebase. Plain-text logs force grep, regex, tears."
            ),
        ),

        dict(
            kind="code",
            title="Same line — bad vs good way to write it",
            section="Logging · Structure",
            accent=accent,
            language="python",
            code=(
                "# BAD - humans only, impossible to query later\n"
                "print(f\"got trip {trip_id} took {ms}ms\")\n\n\n"
                "# GOOD - structured, every field searchable\n"
                "log.info(\n"
                "    \"trip_processed\",\n"
                "    extra={\n"
                "        'trip_id':   trip_id,\n"
                "        'latency_ms': ms,\n"
                "        'partition':  p,\n"
                "        'offset':     o,\n"
                "    },\n"
                ")"
            ),
            caption="Six extra lines today saves you six hours of grep at 3 a.m.",
            source=src_log,
            notes=(
                "Make the trade-off concrete: six lines now vs six hours "
                "later. The choice is obvious when phrased that way."
            ),
        ),

        # ============================================================
        # CONCEPT 3 — Log levels
        # ============================================================

        dict(
            kind="content",
            title="Log levels — when do I use each one?",
            section="Logging · Levels",
            accent=accent,
            bullets=[
                "Levels let us FILTER noise — turn DEBUG off in production",
                "Five levels you'll use: DEBUG · INFO · WARNING · ERROR · CRITICAL",
                "Discipline matters: if everything is INFO, nothing is INFO",
                "Rule of thumb: WARNING = 'we self-healed', ERROR = 'a thing did "
                "not happen'",
            ],
            right_panel=("text",
                "HOSPITAL ANALOGY\n\n"
                "DEBUG    = nurse's notes (off in prod)\n"
                "INFO     = vital signs every hour\n"
                "WARNING  = patient coughed\n"
                "ERROR    = patient fell out of bed\n"
                "CRITICAL = patient's heart stopped\n"
                "           (wake up the doctor!)"),
            notes=(
                "Most teams log everything at INFO and drown during "
                "incidents. Spend 30 seconds on the discipline rule."
            ),
        ),

        dict(
            kind="table",
            title="Log levels — quick reference",
            section="Logging · Levels",
            accent=accent,
            headers=["Level", "Use when…", "Example", "Where it goes"],
            rows=[
                ["DEBUG", "Deep diagnostic detail",
                 "Connection pool stats", "Local dev only"],
                ["INFO", "Normal state changes",
                 "'consumer joined group'", "Loki, kept 7-30 days"],
                ["WARNING", "Recoverable problem (don't wake anyone)",
                 "'retrying broker-2'", "Loki + weekly review"],
                ["ERROR", "Operation failed; service continues",
                 "'message dropped after 5 retries'", "Loki + alert"],
                ["CRITICAL", "Service degraded or down",
                 "'broker has no leader'", "PagerDuty (3 a.m. call)"],
            ],
            source="docs.python.org/3/library/logging.html#logging-levels",
            notes=(
                "Reference slide they will photograph. Reinforces the "
                "discipline rule from the previous slide."
            ),
        ),

        # ============================================================
        # CONCEPT 4 — Correlation / trace IDs
        # ============================================================

        dict(
            kind="content",
            title="How do I trace ONE request across many services?",
            section="Logging · Tracing",
            accent=accent,
            bullets=[
                "Problem: one user click hits 5 services — 5 different log files",
                "Solution: stamp every request with a unique ID at the edge",
                "Pass that ID through Kafka headers, HTTP headers, function args",
                "Every log line includes it — now `trace_id=abc-123` finds them all",
                "This is the simplest version of 'distributed tracing'",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "Airline luggage tags.\n\n"
                "Your bag goes through:\n"
                "  check-in -> conveyor ->\n"
                "  plane -> carousel\n\n"
                "Every system stamps the SAME\n"
                "barcode. If your bag is lost,\n"
                "the airline scans for that ONE\n"
                "barcode everywhere."),
            source="opentelemetry.io/docs/concepts/context-propagation/",
            notes=(
                "The luggage-tag analogy is golden. Make sure they SEE "
                "the connection: same ID propagated everywhere -> instant "
                "search."
            ),
        ),

        dict(
            kind="code",
            title="Trace IDs — produce, propagate, search",
            section="Logging · Tracing",
            accent=accent,
            language="python",
            code=(
                "# PRODUCER: stamp a fresh trace ID on every record\n"
                "import uuid\n"
                "trace_id = str(uuid.uuid4())\n"
                "producer.send(\n"
                "    'trips',\n"
                "    value=trip,\n"
                "    headers=[('trace_id', trace_id.encode())],\n"
                ")\n"
                "log.info('trip_published', extra={'trace_id': trace_id})\n\n\n"
                "# CONSUMER: extract it and put it in every log line\n"
                "trace_id = dict(msg.headers).get('trace_id', b'').decode()\n"
                "with logging_context(trace_id=trace_id):\n"
                "    process(msg.value)\n"
                "    log.info('trip_consumed')\n\n\n"
                "# IN LOKI / GRAFANA you can now search:\n"
                "#   {job=\"app\"} |= \"trace_id=abc-123\""
            ),
            caption="Free distributed tracing for 10 minutes of work.",
            source="opentelemetry.io/docs/concepts/context-propagation/",
            notes=(
                "Show the chain end-to-end. The last comment is the "
                "punchline — one query returns every log line."
            ),
        ),

        # ============================================================
        # CONCEPT 5 — Categorise errors
        # ============================================================

        dict(
            kind="content",
            title="Not all errors are the same — categorise them",
            section="Logging · Error categories",
            accent=accent,
            bullets=[
                "TRANSIENT — network blip -> RETRY (it'll work next time)",
                "POISON-PILL — bad message that will NEVER parse -> DLQ",
                "QUOTA / THROTTLE — rate limit hit -> SLOW DOWN",
                "SCHEMA MISMATCH — producer changed -> DLQ + alert humans",
                "PROGRAMMER BUG — NullPointer, IndexError -> PAGE NOW, fix code",
                "Treating them all the same = the #1 source of stream-processing bugs",
            ],
            right_panel=("text",
                "FOOD-AT-A-RESTAURANT ANALOGY\n\n"
                "TRANSIENT — chef dropped a plate\n"
                "            -> cook a new one (retry)\n\n"
                "POISON-PILL — customer ordered\n"
                "  something not on the menu\n"
                "  -> set it aside, serve next order\n\n"
                "QUOTA — kitchen is overwhelmed\n"
                "  -> tell waiters to slow down\n\n"
                "PROGRAMMER BUG — the stove caught fire\n"
                "  -> CALL THE FIRE BRIGADE (page humans)"),
            source=src_dlq,
            notes=(
                "Each category needs a DIFFERENT action. Generic "
                "'except Exception' treats them all the same and that's "
                "why pipelines silently rot."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Pre-quiz warm-up — categorise these 4 errors",
            section="Logging · Pre-quiz",
            accent=accent,
            bullets=[
                "Ask of each: 'Will retrying THIS exact message help?'",
                "  YES -> transient, RETRY with backoff",
                "  NO  -> poison-pill or schema problem -> DLQ",
                "Ask: 'Is this a programmer bug?' (NullPointer, IndexError)",
                "  YES -> DLQ to keep moving, BUT also page humans",
                "Now grade these 4 cases on the next slide →",
            ],
            right_panel=("text",
                "PREVIEW:\n\n"
                "A) JSON parse error\n"
                "   -> retry won't help -> DLQ ✓\n\n"
                "B) Kafka broker timeout\n"
                "   -> temporary -> RETRY (not DLQ)\n\n"
                "C) Schema field missing\n"
                "   -> won't fix itself -> DLQ ✓\n\n"
                "D) NullPointerException\n"
                "   -> DLQ + page humans ✓"),
            notes=(
                "Walk through the four cases one at a time. By the time "
                "they see the quiz, they have already done the work."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — which goes to the DLQ?",
            section="Logging · Quiz",
            qtype="MULTI",
            question="Which of these errors should send the message to the DLQ? "
                     "(Pick all that apply.)",
            options=[
                "JSON parse error on a record",
                "Kafka broker timeout on send",
                "Schema validation fails: missing required field",
                "NullPointerException inside the parser",
            ],
            notes="A, C, and D. B is transient -> retry.",
        ),
        dict(
            kind="answer",
            title="Answer — A, C, and D (page on D)",
            section="Logging · Quiz",
            answer="A · C · D — and PAGE humans on D",
            explanation=(
                "A (bad JSON) and C (schema violation) are classic "
                "poison-pills — retrying won't help.\n"
                "B (broker timeout) is TRANSIENT — retry with backoff.\n"
                "D (NullPointerException) is a programmer bug. Send to DLQ "
                "to keep the consumer moving, but PAGE humans because the "
                "same code will explode on every similar message."
            ),
        ),

        # ============================================================
        # CONCEPT 6 — The DLQ pattern
        # ============================================================

        dict(
            kind="content",
            title="What is a Dead-Letter Queue (DLQ)?",
            section="Logging · DLQ",
            accent=accent,
            bullets=[
                "A DLQ is just another Kafka topic — usually named like 'trips-dlq'",
                "When a message fails, you DON'T retry forever — you send it here",
                "A separate tool can inspect, fix, and REPLAY messages from the DLQ",
                "The pipeline keeps moving. The bad message is preserved for "
                "debugging.",
                "Without a DLQ, one poison-pill stalls your whole consumer.",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "Mailroom 'return to sender' box.\n\n"
                "The mail keeps flowing.\n"
                "Bad letters land in the box.\n"
                "A human sorts the box later.\n\n"
                "Without the box, the mailroom\n"
                "shuts down for every misaddressed\n"
                "letter."),
            source=src_dlq,
            notes=(
                "DLQ is the simplest, most powerful pattern in stream "
                "processing. The mailroom analogy makes it click."
            ),
        ),

        dict(
            kind="chart",
            title="The DLQ pattern — happy path and sad path",
            section="Logging · DLQ",
            accent=accent,
            chart_path=images["dlq_flow"],
            caption="Success goes to the warehouse. Failure branches to the DLQ. "
                    "Same plumbing, isolated impact.",
            source=src_dlq,
            notes=(
                "Point at the green and red arrows. Two paths, one "
                "consumer. The DLQ is just a topic — no new infrastructure."
            ),
        ),

        dict(
            kind="code",
            title="What to PUT on every DLQ message",
            section="Logging · DLQ",
            accent=accent,
            language="python",
            code=(
                "dlq_record = {\n"
                "    # WHERE the message came from\n"
                "    'original_topic':     msg.topic,\n"
                "    'original_partition': msg.partition,\n"
                "    'original_offset':    msg.offset,\n"
                "    'original_key':       msg.key,\n"
                "    'original_value':     base64.b64encode(msg.value).decode(),\n\n"
                "    # WHY it failed\n"
                "    'error_class':   type(exc).__name__,\n"
                "    'error_message': str(exc)[:500],\n"
                "    'attempts':      attempt_count,\n\n"
                "    # HOW to find related events\n"
                "    'trace_id':    trace_id,\n"
                "    'failed_at':   datetime.utcnow().isoformat(),\n"
                "    'consumer_id': socket.gethostname(),\n"
                "}\n"
                "producer.send('trips-dlq', value=dlq_record, key=msg.key)"
            ),
            caption="Storing original_offset is how you replay surgically.",
            source="Lab_Files/dlq_tool.py",
            notes=(
                "Without WHERE and WHY, the DLQ message is useless. Walk "
                "through the three sections: where, why, how-to-find."
            ),
        ),

        # ============================================================
        # CONCEPT 7 — Retries done right
        # ============================================================

        dict(
            kind="content",
            title="Retries — how NOT to make things worse",
            section="Logging · Retries",
            accent=accent,
            bullets=[
                "DON'T retry instantly — you hammer the same broken thing",
                "DON'T retry forever — you fill up memory and never give up",
                "DO use EXPONENTIAL backoff — wait 1 s, 2 s, 4 s, 8 s, 16 s…",
                "DO add JITTER — a random ± fraction so 1000 clients don't "
                "retry at the same instant",
                "DO cap the attempts — after N tries, give up and DLQ",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "Calling a friend's phone:\n\n"
                "BAD: call, call, call, call\n"
                "  (in 4 seconds — annoying)\n\n"
                "GOOD: wait 1s, then 2s, then 4s,\n"
                "  then 8s. They might be in\n"
                "  a meeting. Give up after 5 tries.\n\n"
                "GREAT: add a random 0-1s jitter so\n"
                "  100 friends don't all call at\n"
                "  exactly the same instant."),
            source="aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/",
            notes=(
                "Thundering-herd is the #1 retry mistake. The friend-on-"
                "phone analogy makes the maths obvious."
            ),
        ),

        dict(
            kind="chart",
            title="Retry strategies — exponential + jitter wins",
            section="Logging · Retries",
            accent=accent,
            chart_path=images["retry_backoff"],
            caption="Notice the y-axis is log-scale. Exponential grows fast — "
                    "that's the point.",
            source="aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/",
            notes=(
                "Quick comparison of the four shapes. Red line (with "
                "jitter) is the production-quality choice."
            ),
        ),

        # ============================================================
        # CONCEPT 8 — Idempotent producer
        # ============================================================

        dict(
            kind="content",
            title="Retries create DUPLICATES — unless you turn on idempotency",
            section="Logging · Idempotency",
            accent=accent,
            bullets=[
                "Problem: producer sends batch, broker writes it, but the ACK "
                "is lost -> producer retries -> duplicate in the topic",
                "Solution: each batch gets a producer ID + sequence number",
                "Broker remembers what it already wrote and rejects duplicates",
                "All you do: enable_idempotence=True. That's it. Free.",
                "Default ON in Apache Kafka since 3.0",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "Posting a parcel:\n\n"
                "WITHOUT tracking number:\n"
                "  resend if unsure ->\n"
                "  customer gets 2 parcels.\n\n"
                "WITH tracking number:\n"
                "  resend if unsure ->\n"
                "  postman sees 'already delivered'\n"
                "  -> 1 parcel, every time."),
            source="kafka.apache.org/documentation/#design_idempotentproducer",
            notes=(
                "The parcel analogy nails it. Producer ID + sequence = "
                "tracking number on every batch."
            ),
        ),

        dict(
            kind="chart",
            title="With vs without idempotency — side by side",
            section="Logging · Idempotency",
            accent=accent,
            chart_path=images["idempotent_producer"],
            caption="Same retry. Two very different outcomes.",
            source="kafka.apache.org/documentation/#design_idempotentproducer",
            notes=(
                "Compare red panel and green panel. One produces "
                "duplicates, one produces exactly-once. The fix is one "
                "config line."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Pre-quiz — recall the magic setting",
            section="Logging · Pre-quiz",
            accent=accent,
            bullets=[
                "We just saw: idempotent producer = exactly-once on a partition",
                "The Python kafka client setting is: enable_idempotence",
                "Set it to True and Kafka attaches producer_id + sequence numbers",
                "Brokers then dedupe retries automatically",
                "Now fill in the blank on the next slide →",
            ],
            right_panel=("text",
                "REMEMBER:\n\n"
                "producer = KafkaProducer(\n"
                "    bootstrap_servers='...',\n"
                "    enable_idempotence=True,   ← here\n"
                "    acks='all',\n"
                ")\n\n"
                "(In Java / librdkafka it's\n"
                " 'enable.idempotence' — with a dot)"),
            notes=(
                "Set them up so the fill-in-blank is trivial. The point "
                "isn't to trick — it's to anchor the setting in memory."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — fill in the blank",
            section="Logging · Quiz",
            qtype="FILL",
            question="To enable exactly-once delivery per partition in a Python "
                     "Kafka producer, you set ____________________ = True.",
            options=None,
            notes="Answer: enable_idempotence (kafka-python) or "
                  "enable.idempotence (Java / librdkafka).",
        ),
        dict(
            kind="answer",
            title="Answer — enable_idempotence",
            section="Logging · Quiz",
            answer="enable_idempotence = True",
            explanation=(
                "In kafka-python / confluent-kafka-python: "
                "enable_idempotence=True.\n"
                "In Java / librdkafka: 'enable.idempotence' = 'true' "
                "(with a dot, not an underscore).\n\n"
                "Default-on in Apache Kafka since 3.0 — but always set it "
                "explicitly so it's obvious from your config."
            ),
        ),

        # ============================================================
        # CONCEPT 9 — Loki + LogQL
        # ============================================================

        dict(
            kind="content",
            title="Where do all the logs GO? Meet Loki.",
            section="Logging · Loki",
            accent=accent,
            bullets=[
                "Loki is 'Prometheus for logs' — same labels-based design",
                "It is CHEAP because it indexes by LABEL, not by content",
                "promtail = the agent that ships logs from each container to Loki",
                "You query Loki with LogQL inside Grafana — same UI as metrics",
                "Rule: keep labels SHORT and LOW-cardinality (level, service, "
                "host) — never user_id or trace_id",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "A library catalogue:\n\n"
                "INDEXED labels = title, author\n"
                "  (cheap to search)\n\n"
                "NOT INDEXED = the entire book text\n"
                "  (still searchable but slower)\n\n"
                "Loki indexes the spine, not\n"
                "the contents. Pick your spine\n"
                "labels carefully."),
            source="grafana.com/docs/loki/latest/clients/promtail/",
            notes=(
                "Label cardinality is THE rule of Loki. Putting trace_id "
                "in labels kills performance and bankrupts the cluster."
            ),
        ),

        dict(
            kind="code",
            title="The LogQL queries you'll run during an incident",
            section="Logging · LogQL",
            accent=accent,
            language="logql",
            code=(
                "# 1. All errors from the consumer in the last 15 min\n"
                "{service=\"taxi_consumer\", level=\"ERROR\"}\n\n"
                "# 2. Find a single trip across ALL services\n"
                "{job=\"containerlogs\"} |= \"trace_id=abc-123\"\n\n"
                "# 3. Error rate per service per minute\n"
                "sum by (service) (rate({level=\"ERROR\"}[1m]))\n\n"
                "# 4. Parse JSON, then filter by a field\n"
                "{service=\"taxi_consumer\"}\n"
                "  | json\n"
                "  | latency_ms > 500"
            ),
            caption="{labels} pick streams. Pipes filter and parse.",
            source="grafana.com/docs/loki/latest/logql/",
            notes=(
                "Just like PromQL — selector first, then pipes. The first "
                "query is what you run when an alert fires. The second is "
                "what you run when a customer complains."
            ),
        ),

        # ============================================================
        # LAB CALLOUT
        # ============================================================

        dict(
            kind="lab",
            title="Hands-on: trace a trip & drain a DLQ",
            section="Logging · Lab",
            lab_name="Labs 8 + 9 · tracing & DLQ recovery",
            summary="Inject a poison-pill trip. Watch it land in the DLQ. "
                    "Trace it across services in Loki. Then replay it.",
            bullets=[
                "Lab_Files/taxi_simulator.py — produce one malformed trip",
                "Lab_Files/taxi_consumer.py — observe the DLQ branch",
                "Loki query: {service=\"taxi_consumer\"} |= \"trace_id=...\"",
                "Lab_Files/dlq_tool.py — inspect -> fix -> replay",
                "Verify: warehouse row count matches expected count",
            ],
            notes=(
                "Most realistic drill of the day. Produce the failure, "
                "see it in logs, fix it, replay it. By the end they will "
                "TRUST the DLQ rather than fear it."
            ),
        ),
    ]
