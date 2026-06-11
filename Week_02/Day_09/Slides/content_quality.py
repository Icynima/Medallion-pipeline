"""Section 3 — Data Quality Checks (teacher-friendly)."""
from __future__ import annotations
import theme as T


def specs(images, accent):
    src_dama = "dama.org/cpages/body-of-knowledge"
    src_ge = "greatexpectations.io"
    src_sr = "docs.confluent.io/platform/current/schema-registry/"

    return [
        # ============================================================
        # DIVIDER
        # ============================================================
        dict(
            kind="divider",
            number=3,
            title="Data Quality Checks",
            summary="A pipeline can be UP and still serve garbage. "
                    "Today we make 'good data' a measurable thing.",
            accent=accent,
        ),

        # ============================================================
        # CONCEPT 1 — Why data quality matters
        # ============================================================

        dict(
            kind="content",
            title="Why do we even talk about data quality?",
            section="Quality · Why",
            accent=accent,
            bullets=[
                "The pipeline can be 100% UP and still deliver WRONG data",
                "A green dashboard with bad data is WORSE than a red one",
                "Bad data is silent — you find out weeks later in a meeting",
                "We need to MEASURE quality and ALERT on it, just like we do "
                "for latency or errors",
            ],
            right_panel=("text",
                "REAL EXAMPLE\n\n"
                "A bank shipped a release that\n"
                "rounded all amounts to the\n"
                "nearest dollar by accident.\n\n"
                "Uptime: 100%.\n"
                "Latency: perfect.\n"
                "Dashboards: all green.\n\n"
                "Three weeks later: $4M in\n"
                "incorrect statements. CFO\n"
                "called from holiday."),
            notes=(
                "Open with the scariest property of bad data: it's "
                "silent. Use the bank story to make it visceral."
            ),
        ),

        dict(
            kind="content",
            title="Two pipelines — which one would you trust?",
            section="Quality · Why",
            accent=accent,
            bullets=[
                "Pipeline A — 99.99 % UPTIME but 5 % of rows are WRONG",
                "Pipeline B — 99.5 % uptime, 0 % wrong rows",
                "Business chooses B. Every time.",
                "Lesson: quality is a first-class SLI — not 'something the "
                "data team handles'",
            ],
            right_panel=("text",
                "QUESTION\n\n"
                "If your dashboard showed:\n"
                "  Sales today: $1.2M\n\n"
                "Would you rather it BLINK 'no data'\n"
                "for 30 seconds…\n\n"
                "…or silently show $1.5M\n"
                "(20% too high)?\n\n"
                "Most people prefer the blink."),
            source=src_dama,
            notes=(
                "Make them choose. Outages get forgiven. Wrong numbers "
                "destroy trust forever."
            ),
        ),

        # ============================================================
        # CONCEPT 2 — DAMA's six dimensions
        # ============================================================

        dict(
            kind="content",
            title="Six WAYS data can be 'good' or 'bad'",
            section="Quality · Dimensions",
            accent=accent,
            bullets=[
                "ACCURACY — does the value match REAL truth?",
                "COMPLETENESS — are any required fields MISSING?",
                "CONSISTENCY — does the same value match across systems?",
                "TIMELINESS — does it arrive IN TIME to be useful?",
                "UNIQUENESS — any duplicates?",
                "VALIDITY — does it match the schema / format?",
            ],
            right_panel=("text",
                "FOR A TRIP RECORD\n\n"
                "Accuracy -> fare is correct\n"
                "Completeness -> trip_id not null\n"
                "Consistency -> driver_id matches\n"
                "  drivers table\n"
                "Timeliness -> arrived within 5 min\n"
                "  of event time\n"
                "Uniqueness -> no duplicate trip_id\n"
                "Validity -> zone code = ABC-1234"),
            source=src_dama,
            notes=(
                "Six is a manageable number. Make sure each one is "
                "anchored to a CONCRETE example from our trips data."
            ),
        ),

        dict(
            kind="chart",
            title="Six dimensions in one chart",
            section="Quality · Dimensions",
            accent=accent,
            chart_path=images["dq_dimensions"],
            caption="Each dimension gets its own score. A red bar tells you "
                    "exactly where to look.",
            source=src_dama,
            notes=(
                "Once they see this chart on a real Grafana panel, "
                "incidents will be 10× faster to diagnose."
            ),
        ),

        # ============================================================
        # CONCEPT 3 — Quality contracts in code
        # ============================================================

        dict(
            kind="content",
            title="How do we ENFORCE quality? Write 'expectations'.",
            section="Quality · Contracts",
            accent=accent,
            bullets=[
                "An 'expectation' is a rule the data MUST satisfy",
                "Example: 'fare_amount must be between 0 and 500'",
                "Tools like Great Expectations let you write these as code",
                "Run them on every batch / every message -> branch failures to DLQ",
                "Each rule emits a metric -> see exactly WHICH rule is breaking",
            ],
            right_panel=("text",
                "WHAT A RULE LOOKS LIKE\n\n"
                "expect_column_values_to_not_be_null(\n"
                "    'trip_id')\n\n"
                "expect_column_values_to_be_between(\n"
                "    'fare_amount',\n"
                "    min_value=0,\n"
                "    max_value=500)\n\n"
                "Reads like English. That's the\n"
                "whole pitch."),
            source=src_ge,
            notes=(
                "Rules-as-code is the key idea. The library name doesn't "
                "matter — the pattern does."
            ),
        ),

        dict(
            kind="code",
            title="Six dimensions, one block of code (Great Expectations)",
            section="Quality · Contracts",
            accent=accent,
            language="python",
            code=(
                "import great_expectations as gx\n"
                "df = pd.read_sql('SELECT * FROM trips_silver', conn)\n"
                "v = gx.from_pandas(df)\n\n"
                "# VALIDITY — must match a pattern\n"
                "v.expect_column_values_to_match_regex(\n"
                "    'pickup_zone', r'^[A-Z]{3}-\\d{4}$')\n\n"
                "# COMPLETENESS — required fields\n"
                "v.expect_column_values_to_not_be_null('trip_id')\n\n"
                "# UNIQUENESS — no duplicate trips\n"
                "v.expect_column_values_to_be_unique('trip_id')\n\n"
                "# ACCURACY — reasonable range\n"
                "v.expect_column_values_to_be_between(\n"
                "    'fare_amount', min_value=0, max_value=500)\n\n"
                "# CONSISTENCY — referential\n"
                "v.expect_column_values_to_be_in_set(\n"
                "    'driver_id', valid_driver_ids)\n\n"
                "result = v.validate()\n"
                "if not result['success']:\n"
                "    publish_to_dlq(...)"
            ),
            caption="One library, six DAMA dimensions covered.",
            source=src_ge,
            notes=(
                "Walk down the comments. The library is incidental — "
                "the pattern (rules-as-code -> branch on failure) is the "
                "takeaway."
            ),
        ),

        dict(
            kind="table",
            title="Where in the pipeline should checks live?",
            section="Quality · Placement",
            accent=accent,
            headers=["Where", "Cost", "When to use it"],
            rows=[
                ["At producer (BEFORE Kafka)", "Cheapest",
                 "Validity + basic completeness"],
                ["At consumer (in-stream)", "Medium",
                 "Most expectations + lookups"],
                ["In Bronze (raw landing)", "Cheap",
                 "Schema check + dedup"],
                ["In Silver (cleaned)", "Medium",
                 "Business rules + joins"],
                ["In Gold (aggregated)", "Expensive",
                 "KPIs + reconciliation with source-of-truth"],
            ],
            source="medallion architecture — Databricks blog",
            notes=(
                "You don't pick one — you pick all of them, with the "
                "right check at each layer. Cheapest checks earliest."
            ),
        ),

        # ============================================================
        # CONCEPT 4 — Schema Registry
        # ============================================================

        dict(
            kind="content",
            title="Schema Registry — stop bad data BEFORE it enters Kafka",
            section="Quality · Schema Registry",
            accent=accent,
            bullets=[
                "Producers tell the registry: 'here's the shape of my messages'",
                "Registry checks if changes are SAFE for existing consumers",
                "If unsafe, the producer is REJECTED — bad data never enters Kafka",
                "Every message stores the schema ID — consumers fetch + cache it",
                "Without a registry, producers drift silently and consumers break",
            ],
            right_panel=("text",
                "REAL INCIDENT\n\n"
                "A producer team renamed\n"
                "  'amount'  ->  'fare_amount'.\n\n"
                "No registry -> 7 downstream\n"
                "  consumers silently got NULL\n"
                "  in their amount column.\n\n"
                "Nobody noticed for 3 days.\n"
                "Reports were wrong."),
            source=src_sr,
            notes=(
                "Schema Registry is the kind of tool that looks like "
                "overhead until you've seen the incident it prevents."
            ),
        ),

        # ============================================================
        # CONCEPT 5 — Compatibility modes
        # ============================================================

        dict(
            kind="content",
            title="The mode names are confusing — let's decode them",
            section="Quality · Compatibility",
            accent=accent,
            bullets=[
                "Compatibility modes ask: 'whose perspective are we protecting?'",
                "BACKWARD = new CONSUMERS can read OLD data -> upgrade consumers FIRST",
                "FORWARD = old consumers can read NEW data -> upgrade producers FIRST",
                "FULL = both directions safe -> only additive changes allowed",
                "NONE = anything goes -> only for greenfield topics",
                "Memory trick: the mode name describes the CONSUMER's POV",
            ],
            right_panel=("text",
                "WHICH ROLLOUT ORDER?\n\n"
                "BACKWARD -> roll out CONSUMERS first\n"
                "  (old producers, new consumers ok)\n\n"
                "FORWARD -> roll out PRODUCERS first\n"
                "  (new producers, old consumers ok)\n\n"
                "The names trip up everyone.\n"
                "Read them as 'what the\n"
                "consumer can do'."),
            source=src_sr,
            notes=(
                "Compatibility mode naming is famously confusing. Spend "
                "an extra 30 seconds making the consumer-POV memory hook "
                "stick."
            ),
        ),

        dict(
            kind="chart",
            title="Compatibility modes — pick BACKWARD by default",
            section="Quality · Compatibility",
            accent=accent,
            chart_path=images["schema_compat"],
            caption="BACKWARD is the safe default for rolling deploys.",
            source=src_sr,
            notes=(
                "Default BACKWARD. Only consider FORWARD if you can't "
                "deploy consumers first. NONE = throwing away the seatbelt."
            ),
        ),

        dict(
            kind="table",
            title="What can I change under BACKWARD?",
            section="Quality · Compatibility",
            accent=accent,
            headers=["Change", "Allowed?", "Why"],
            rows=[
                ["Add optional field WITH default", "yes",
                 "Old data has no value -> default fills in"],
                ["Add field WITHOUT default", "no",
                 "Old data would fail validation"],
                ["Remove an OPTIONAL field", "yes",
                 "Consumers can simply ignore missing"],
                ["Remove a REQUIRED field", "no",
                 "Old consumers still expect it"],
                ["RENAME a field", "no",
                 "Use alias or two-step migration"],
                ["int -> long (numeric promotion)", "yes (Avro)",
                 "Wider type is safe"],
                ["string -> int", "no",
                 "Type changes aren't allowed"],
            ],
            source=src_sr,
            notes=(
                "The most-asked schema question in interviews. Pattern: "
                "additive + default = safe. Subtractive + rename = unsafe."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Pre-quiz — the scenario",
            section="Quality · Pre-quiz",
            accent=accent,
            bullets=[
                "Recall: under BACKWARD, you can ADD fields with defaults",
                "Recall: under BACKWARD, you CANNOT rename a field",
                "But what if the team WANTS to rename 'amount' -> 'fare_amount'?",
                "Right answer: two-step migration. Add new, deprecate old, "
                "remove later",
                "Wrong answer: switch to NONE compatibility. That's giving up "
                "the safety net.",
            ],
            right_panel=("text",
                "TWO-STEP MIGRATION\n\n"
                "Step 1:  Producer writes BOTH\n"
                "         'amount' AND 'fare_amount'\n"
                "         Consumers migrate to read\n"
                "         the new name.\n\n"
                "Step 2:  Producer stops writing\n"
                "         'amount'. Registry approves\n"
                "         the field removal.\n\n"
                "Boring, safe, ships."),
            notes=(
                "Make the safe migration pattern obvious BEFORE asking. "
                "We want to teach the right behaviour, not catch them out."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — schema rename",
            section="Quality · Quiz",
            qtype="MCQ",
            question="Your registry is set to BACKWARD. The producer team wants "
                     "to RENAME 'amount' to 'fare_amount'. What's the safest path?",
            options=[
                "Just rename it — BACKWARD lets you do anything",
                "Add 'fare_amount' with default, deprecate 'amount', "
                "remove it in a later release",
                "Switch to NONE compatibility first, then rename",
                "Use FORWARD compatibility instead",
            ],
            notes="B — two-step migration. The others are unsafe.",
        ),
        dict(
            kind="answer",
            title="Answer — B (two-step migration)",
            section="Quality · Quiz",
            answer="B. Add new field, deprecate old, remove later",
            explanation=(
                "Renaming is forbidden under BACKWARD because old consumers "
                "still look for 'amount' after the producer changed.\n\n"
                "Safe pattern (two steps):\n"
                "  1. Producer writes BOTH names. Consumers migrate to read "
                "     'fare_amount'.\n"
                "  2. In a later release, remove 'amount'.\n\n"
                "Switching to NONE just disables the safety net — bad data "
                "will land in production within days."
            ),
        ),

        # ============================================================
        # CONCEPT 6 — Anomaly detection
        # ============================================================

        dict(
            kind="content",
            title="Static rules miss the SUBTLE problems",
            section="Quality · Anomalies",
            accent=accent,
            bullets=[
                "Static rule: 'fare must be 0-500' -> catches the OBVIOUS bugs",
                "Subtle bugs need STATISTICAL checks (compare to history)",
                "VOLUME DRIFT — today's row count is way off the 7-day avg",
                "DISTRIBUTION DRIFT — p99 fare doubled overnight",
                "NULL-RATE SPIKE — a column suddenly has 10× more nulls",
                "Use BOTH: static rules for hard limits, anomaly checks for drift",
            ],
            right_panel=("text",
                "EXAMPLE\n\n"
                "Static rule passes:\n"
                "  every fare is 0-500\n\n"
                "But this morning someone\n"
                "shipped a 'surge multiplier' bug.\n"
                "Fares are now 3× normal.\n\n"
                "Static check: silent.\n"
                "Anomaly check: 'today's p99\n"
                "  fare = 240, 7-day avg = 80,\n"
                "  that's 5σ above normal' -> ALERT."),
            source="evidentlyai.com",
            notes=(
                "Two layers: hard limits in-stream, statistical checks "
                "per batch. Show how they complement each other."
            ),
        ),

        # ============================================================
        # CONCEPT 7 — Quality SLOs
        # ============================================================

        dict(
            kind="content",
            title="Turn quality into SLOs — same discipline as latency",
            section="Quality · SLOs",
            accent=accent,
            bullets=[
                "Quality SLO = a measurable target for 'good data'",
                "Example: '99.5 % of trips pass all expectations every hour'",
                "Below target -> alert someone -> triage like any incident",
                "Some SLOs are real-time, some are batch (daily reconciliation)",
                "Treat quality regressions as urgently as a service outage",
            ],
            right_panel=("text",
                "WHY THIS WORKS\n\n"
                "Latency SLO trains the team to\n"
                "care about user experience.\n\n"
                "Quality SLO trains the team to\n"
                "care about whether the data\n"
                "is actually correct.\n\n"
                "Same dashboards, same alerts,\n"
                "same on-call rotation."),
            source="Lab_Files/quality_validator.py",
            notes=(
                "SLOs are the cultural glue. If quality has the same "
                "respect as latency, the team will protect it the same "
                "way."
            ),
        ),

        dict(
            kind="table",
            title="Sample quality SLOs for the trips pipeline",
            section="Quality · SLOs",
            accent=accent,
            headers=["SLI (what we measure)", "Target", "Alert window"],
            rows=[
                ["% of trips passing all expectations", "> 99.5 %", "5 min"],
                ["DLQ msgs / total ingested", "< 0.5 %", "1 hour"],
                ["Trips with null driver_id", "0", "real-time"],
                ["Daily trip count vs 7-day avg", "within ± 3 σ", "next day"],
                ["Late-arriving rows (event_ts > 30 min late)",
                 "< 1 %", "1 hour"],
            ],
            source="Lab_Files/quality_validator.py",
            notes=(
                "Concrete examples make SLOs feel achievable. Top three "
                "can be measured in real time; bottom two are batch."
            ),
        ),

        # ============================================================
        # CONCEPT 8 — The actual validator code
        # ============================================================

        dict(
            kind="code",
            title="Our validator — read top to bottom",
            section="Quality · Validator",
            accent=accent,
            language="python",
            code=(
                "EXPECTATIONS = [\n"
                "    ('trip_id_present', lambda t: t.get('trip_id') is not None),\n"
                "    ('fare_positive',   lambda t: t.get('fare_amount', -1) >= 0),\n"
                "    ('fare_reasonable', lambda t: t.get('fare_amount', 0) <= 500),\n"
                "    ('valid_zone_code', lambda t: zone_re.match(t.get('zone',''))),\n"
                "    ('known_driver',    lambda t: t.get('driver_id') in driver_set),\n"
                "    ('event_ts_recent', lambda t: now() - t['event_ts'] < timedelta(hours=1)),\n"
                "]\n\n"
                "def validate(trip):\n"
                "    failures = [name for name, fn in EXPECTATIONS if not fn(trip)]\n"
                "    if failures:\n"
                "        metric_dq_failure.labels(\n"
                "            rules=','.join(failures)).inc()\n"
                "        send_to_dlq(trip, reason=failures)\n"
                "        return False\n"
                "    metric_dq_pass.inc()\n"
                "    return True"
            ),
            caption="Each rule has a NAME and emits a Prometheus metric — "
                    "you'll see WHICH rule is breaking.",
            source="Lab_Files/quality_validator.py",
            notes=(
                "Two design choices to point out: named rules and "
                "labelled metrics. Together they make incidents actionable."
            ),
        ),

        # ============================================================
        # CONCEPT 9 — Reinforce BACKWARD direction
        # ============================================================

        dict(
            kind="content",
            title="Pre-quiz — recall the BACKWARD direction",
            section="Quality · Pre-quiz",
            accent=accent,
            bullets=[
                "BACKWARD = NEW CONSUMER can read OLD producer data",
                "So when you upgrade, you upgrade CONSUMERS FIRST",
                "Producers go LAST (they keep speaking the old shape until "
                "consumers are ready)",
                "FORWARD is the opposite: producers first, consumers later",
                "Now answer the true/false on the next slide →",
            ],
            right_panel=("text",
                "MEMORY HOOK\n\n"
                "Backward = look 'back' at old data.\n"
                "  -> new code can READ old data.\n"
                "  -> upgrade the READERS first.\n\n"
                "Forward = old code looks 'forward'\n"
                "  at new data.\n"
                "  -> upgrade the WRITERS first."),
            notes=(
                "Set them up so the True/False is genuinely easy. We want "
                "to reinforce the memory hook, not surprise them."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — true or false",
            section="Quality · Quiz",
            qtype="TF",
            question="Under BACKWARD compatibility, the PRODUCER can be "
                     "deployed first, BEFORE consumers upgrade.",
            options=None,
            notes="False. BACKWARD = upgrade CONSUMERS first.",
        ),
        dict(
            kind="answer",
            title="Answer — FALSE",
            section="Quality · Quiz",
            answer="False",
            explanation=(
                "BACKWARD means NEW CONSUMERS can read OLD data — so "
                "CONSUMERS go first. Then producers can roll out the new "
                "schema knowing all consumers can already handle it.\n\n"
                "FORWARD is the reverse: producers first, consumers later.\n\n"
                "The names refer to the CONSUMER'S perspective and trip up "
                "everyone."
            ),
        ),

        # ============================================================
        # LAB CALLOUT
        # ============================================================

        dict(
            kind="lab",
            title="Hands-on: enforce a quality SLO end-to-end",
            section="Quality · Lab",
            lab_name="Labs 10-11 · DQ + Schema Registry",
            summary="Wire 8 expectations into the consumer, register an Avro "
                    "schema, evolve it under BACKWARD and watch rejection happen.",
            bullets=[
                "Lab_Files/quality_validator.py — review the 8 rules",
                "Inject a trip with fare_amount = -50 -> watch it land in DLQ",
                "Register schema v1 in Schema Registry",
                "Push v2 with an additive change -> accepted",
                "Push v3 with a rename -> rejected with reason",
                "Add a Grafana panel: DQ failure rate per rule",
            ],
            notes=(
                "By the end they have a pipeline that rejects bad data "
                "at TWO layers (producer schema + consumer rules) and can "
                "articulate BACKWARD/FORWARD in an interview."
            ),
        ),
    ]
