"""Section 4 — Scaling Kafka Pipelines (teacher-friendly)."""
from __future__ import annotations
import theme as T


def specs(images, accent):
    src_kafka = "kafka.apache.org/documentation/"
    src_conf = "docs.confluent.io/platform/current/installation/configuration/"

    return [
        # ============================================================
        # DIVIDER
        # ============================================================
        dict(
            kind="divider",
            number=4,
            title="Scaling Kafka Pipelines",
            summary="When the load grows, which dial do we turn? "
                    "Today we learn the dials and the order.",
            accent=accent,
        ),

        # ============================================================
        # CONCEPT 1 — Three ways to scale
        # ============================================================

        dict(
            kind="content",
            title="Three ways to make a pipeline 'bigger'",
            section="Scaling · Axes",
            accent=accent,
            bullets=[
                "VERTICAL — bigger machine (more CPU, more RAM, faster disk)",
                "HORIZONTAL — more machines (add brokers, add consumers)",
                "TIME — trade latency for throughput (batching, buffers)",
                "Most teams jump to HORIZONTAL first — usually wrong",
                "Cheapest wins: time-axis tweaks often give 10× for free",
            ],
            right_panel=("text",
                "ANALOGY — A KITCHEN\n\n"
                "VERTICAL = a bigger oven\n"
                "  (one chef, faster cooking)\n\n"
                "HORIZONTAL = more chefs\n"
                "  (parallel cooking — needs\n"
                "   more counter space too)\n\n"
                "TIME = batch the orders\n"
                "  (cook 5 pizzas at once,\n"
                "   each waits a bit longer\n"
                "   but the kitchen ships more)"),
            source=src_kafka,
            notes=(
                "Kitchen analogy works for any audience. Stress that "
                "TIME (batching) is the cheapest dial and the most "
                "underused."
            ),
        ),

        dict(
            kind="chart",
            title="The three axes — visual recap",
            section="Scaling · Axes",
            accent=accent,
            chart_path=images["scaling_axes"],
            caption="Try TIME first, then VERTICAL, then HORIZONTAL. "
                    "That's the order of cheap to expensive.",
            source=src_kafka,
            notes=(
                "Try time-axis tweaks first. Then verify the box is full. "
                "Only then add machines. Most teams do this in reverse."
            ),
        ),

        # ============================================================
        # CONCEPT 2 — Partitions
        # ============================================================

        dict(
            kind="content",
            title="What IS a partition? (the only Kafka concept that matters)",
            section="Scaling · Partitions",
            accent=accent,
            bullets=[
                "A topic is split into PARTITIONS — think of them as parallel "
                "lanes on a motorway",
                "Each partition is a SEPARATE ordered log",
                "One partition = ONE consumer (within a group) can read it",
                "More partitions = more consumers can work in parallel",
                "Fewer partitions = a bottleneck you can't widen later",
            ],
            right_panel=("text",
                "MOTORWAY ANALOGY\n\n"
                "1 lane  -> 1 car at a time\n"
                "3 lanes -> 3 cars in parallel\n\n"
                "Partitions are the lanes.\n"
                "Consumers are the cars.\n\n"
                "Can you have 5 cars on 3 lanes?\n"
                "Yes — but 2 cars must WAIT.\n"
                "(That's an idle consumer.)"),
            source=src_kafka,
            notes=(
                "Motorway lanes is the most reliable analogy for "
                "partitions. Make sure they SEE that consumers > "
                "partitions = wasted consumers."
            ),
        ),

        dict(
            kind="chart",
            title="Producer -> partitions -> consumers — visual",
            section="Scaling · Partitions",
            accent=accent,
            chart_path=images["partitions_distribution"],
            caption="One partition -> at most ONE consumer in the group. "
                    "That's the rule.",
            source=src_kafka,
            notes=(
                "Trace one message: producer hashes the key -> picks a "
                "partition -> exactly one consumer reads it. Order is "
                "preserved per key because each key always goes to the "
                "same partition."
            ),
        ),

        dict(
            kind="content",
            title="How many partitions should I pick?",
            section="Scaling · Partition count",
            accent=accent,
            bullets=[
                "Start with: PEAK throughput ÷ ONE-consumer's throughput",
                "Round UP to a multiple of broker count (even spread)",
                "Add 50 % headroom for growth",
                "Hard limit: <= 4000 partitions per broker (Apache Kafka)",
                "You can ALWAYS add more partitions — but you CAN'T remove",
                "So when in doubt, pick HIGHER",
            ],
            right_panel=("text",
                "WORKED EXAMPLE\n\n"
                "Peak load:    200 MB/s\n"
                "One consumer:  20 MB/s\n"
                "-> need 10 consumers\n"
                "-> need 10 partitions minimum\n\n"
                "Round to multiple of 3 brokers\n"
                "-> 12 partitions\n\n"
                "Add 50% headroom\n"
                "-> 18 partitions"),
            source=src_conf,
            notes=(
                "Concrete worked example. Walk the arithmetic out loud — "
                "people remember numbers."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Pre-quiz — count active consumers",
            section="Scaling · Pre-quiz",
            accent=accent,
            bullets=[
                "Rule again: ONE partition = ONE consumer (per group)",
                "If consumers > partitions -> extras sit IDLE",
                "If consumers < partitions -> some consumers handle multiple",
                "If consumers = partitions -> perfect balance",
                "Quick: 6 partitions, 8 consumers in one group -> how many ACTIVE?",
            ],
            right_panel=("text",
                "WORK IT OUT\n\n"
                "Partitions:  [P0][P1][P2][P3][P4][P5]\n"
                "Consumers:   C1 C2 C3 C4 C5 C6 C7 C8\n\n"
                "Assignment:\n"
                "  C1 -> P0\n"
                "  C2 -> P1\n"
                "  ... (six get one each)\n"
                "  C7 -> IDLE\n"
                "  C8 -> IDLE\n\n"
                "Answer: 6 active, 2 idle."),
            notes=(
                "Walk through the assignment slowly. The point isn't to "
                "trick — it's to make the partition rule REAL."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — partition arithmetic",
            section="Scaling · Quiz",
            qtype="MCQ",
            question="A topic has 6 partitions. A consumer group has 8 members. "
                     "How many consumers actively process data?",
            options=[
                "8 — load is balanced",
                "6 — two consumers are idle",
                "All 8 share each partition equally",
                "It depends on partition.assignment.strategy",
            ],
            notes="B. One partition -> one consumer in a group.",
        ),
        dict(
            kind="answer",
            title="Answer — B (6 active, 2 idle)",
            section="Scaling · Quiz",
            answer="B. 6 active, 2 idle",
            explanation=(
                "A partition can be consumed by AT MOST ONE consumer in a "
                "group. With 6 partitions and 8 consumers, 6 get one "
                "partition each and 2 sit idle.\n\n"
                "Why over-provision? An idle consumer can take over "
                "instantly if one of the active ones crashes."
            ),
        ),

        # ============================================================
        # CONCEPT 3 — Replication & ISR
        # ============================================================

        dict(
            kind="content",
            title="Replication — how Kafka survives broker failures",
            section="Scaling · Replication",
            accent=accent,
            bullets=[
                "Replication factor (RF) = how many COPIES of each partition exist",
                "Typical: RF = 3 -> leader + 2 followers, on 3 different brokers",
                "ISR = 'In-Sync Replicas' — the followers currently keeping up",
                "If a follower falls behind, it's KICKED OUT of the ISR",
                "Under-replicated partitions = your single best early warning",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "Three people share notes:\n"
                "  • Leader writes the master copy\n"
                "  • Two followers photocopy it\n\n"
                "If a follower falls behind:\n"
                "  -> temporarily removed from\n"
                "    the 'official' note-takers\n"
                "  -> rejoins when caught up\n\n"
                "If all three have it -> safe.\n"
                "If only one has it -> risky."),
            source=src_kafka,
            notes=(
                "ISR membership is dynamic. Make sure they see the "
                "leader/follower distinction and why ISR shrink is bad."
            ),
        ),

        dict(
            kind="chart",
            title="ISR shrink and recover — watch the red follower fall behind",
            section="Scaling · ISR",
            accent=accent,
            chart_path=images["isr_timeline"],
            caption="Red follower lags during 40-70s. ISR shrinks. "
                    "When it catches up, ISR expands again.",
            source=src_kafka,
            notes=(
                "Real-world view of an ISR event. Show the red region — "
                "that's when broker-3 was out of ISR. The line catches "
                "back up and rejoins."
            ),
        ),

        # ============================================================
        # CONCEPT 4 — Durability config
        # ============================================================

        dict(
            kind="content",
            title="acks + min.insync.replicas — the durability matrix",
            section="Scaling · Durability",
            accent=accent,
            bullets=[
                "acks tells the producer WHEN to consider a message 'safe'",
                "  acks=0  -> 'fire and forget' (no safety)",
                "  acks=1  -> 'leader has it' (loses if leader dies)",
                "  acks=all -> 'every in-sync replica has it'",
                "min.insync.replicas = MINIMUM number of replicas required for "
                "acks=all to succeed",
                "Safe combo: RF=3, acks=all, min.insync.replicas=2",
            ],
            right_panel=("text",
                "WHY THE COMBO MATTERS\n\n"
                "acks=all alone is a TRAP.\n\n"
                "If the ISR shrinks to JUST the leader,\n"
                "acks=all means 'leader acked' ->\n"
                "no actual redundancy!\n\n"
                "min.insync.replicas=2 says\n"
                "'refuse to ack unless at least\n"
                "TWO replicas have the message'.\n\n"
                "Now one broker can die safely."),
            source=src_kafka,
            notes=(
                "The most common misconfig: acks=all without min.insync. "
                "Hammer this point — sounds safe, isn't safe."
            ),
        ),

        dict(
            kind="table",
            title="The durability matrix — pick your row carefully",
            section="Scaling · Durability",
            accent=accent,
            headers=["acks", "min.insync", "Behaviour", "Survives 1 broker fail?"],
            rows=[
                ["0", "n/a", "Don't wait for any ack",
                 "No — any failure loses data"],
                ["1", "n/a", "Only leader has it",
                 "No — leader fails -> loss"],
                ["all", "1", "All ISR — but ISR can shrink to 1",
                 "No — silently broken"],
                ["all", "2", "Need >= 2 in sync",
                 "YES — one broker can die safely"],
                ["all", "RF (=3)", "Need ALL replicas in sync",
                 "Halts on any one failure"],
            ],
            source=src_kafka,
            notes=(
                "Row 4 (acks=all, min.isr=2 with RF=3) is the 'right "
                "answer' for most production systems. Memorise it."
            ),
        ),

        # ---- Setup for quiz ----
        dict(
            kind="content",
            title="Pre-quiz — pick the safe combo",
            section="Scaling · Pre-quiz",
            accent=accent,
            bullets=[
                "Goal: survive ONE broker failure with ZERO data loss",
                "RF must be at least 3 (otherwise 1 failure removes "
                "redundancy)",
                "acks must be 'all' (otherwise the leader might lose data)",
                "min.insync.replicas must be >= 2 (otherwise acks=all is a lie)",
                "Now pick the option on the next slide that matches all three",
            ],
            right_panel=("text",
                "RECAP THE THREE CONDITIONS\n\n"
                "[X] RF = 3            (3 copies)\n"
                "[X] acks = all        (every ISR acks)\n"
                "[X] min.insync = 2    (must have 2 ISR)\n\n"
                "Only ONE option ticks all 3 boxes.\n"
                "Find it on the next slide."),
            notes=(
                "Make the criteria explicit. Then the quiz is a "
                "filtering exercise rather than a memory test."
            ),
        ),

        dict(
            kind="quiz",
            title="Quick check — durability config",
            section="Scaling · Quiz",
            qtype="BEST",
            question="You want ZERO data loss on a single broker failure. "
                     "Which configuration BEST achieves this?",
            options=[
                "RF=3, acks=1, min.insync.replicas=1",
                "RF=3, acks=all, min.insync.replicas=1",
                "RF=3, acks=all, min.insync.replicas=2",
                "RF=2, acks=all, min.insync.replicas=2",
            ],
            notes="C. Three copies, all-ack, requiring 2 in sync.",
        ),
        dict(
            kind="answer",
            title="Answer — C (RF=3, acks=all, min.isr=2)",
            section="Scaling · Quiz",
            answer="C. RF=3 · acks=all · min.insync.replicas=2",
            explanation=(
                "RF=3 means three copies exist.\n"
                "acks=all + min.isr=2 means at least TWO replicas must "
                "have the message before it's acknowledged.\n\n"
                "If one broker dies, writes continue with the remaining "
                "two.\n\n"
                "Option B silently allows acks=all to succeed with only "
                "the leader -> no real durability.\n"
                "Option D has only 2 copies -> after one failure, no "
                "redundancy AND writes halt."
            ),
        ),

        # ============================================================
        # CONCEPT 5 — Producer tuning (compression + batching)
        # ============================================================

        dict(
            kind="content",
            title="The cheapest way to scale — TUNE the producer",
            section="Scaling · Producer tuning",
            accent=accent,
            bullets=[
                "Compression: shrink messages before they hit the network",
                "Batching: send many messages in ONE request, not one-at-a-time",
                "These two cost nothing AND often give 50-100× more throughput",
                "Real-world: turn on compression=zstd + linger.ms=20 -> done",
                "Always try these BEFORE adding hardware",
            ],
            right_panel=("text",
                "ANALOGY\n\n"
                "Post Office:\n\n"
                "Without batching = mailing 100\n"
                "  letters one at a time\n\n"
                "With batching = put 100 letters\n"
                "  in one parcel, ship once\n\n"
                "Without compression = full-size box\n"
                "With compression = vacuum-sealed\n"
                "                   half the size"),
            source=src_conf,
            notes=(
                "Producer tuning is the highest-leverage change in the "
                "whole pipeline. Free 10-100× throughput."
            ),
        ),

        dict(
            kind="chart",
            title="Compression codecs — pick zstd in 2026",
            section="Scaling · Compression",
            accent=accent,
            chart_path=images["compression_compare"],
            caption="zstd: best ratio, modest CPU. snappy: cheapest CPU.",
            source="github.com/edenhill/librdkafka/wiki/Compression",
            notes=(
                "zstd is the modern winner. Never run compression=none "
                "in production."
            ),
        ),

        dict(
            kind="code",
            title="A production-ready producer config",
            section="Scaling · Producer tuning",
            accent=accent,
            language="python",
            code=(
                "producer = KafkaProducer(\n"
                "    bootstrap_servers='kafka:9092',\n\n"
                "    # BATCHING - wait up to 20ms to fill a batch...\n"
                "    linger_ms=20,\n"
                "    # ...or 64 KB worth of records (whichever first)\n"
                "    batch_size=64 * 1024,\n\n"
                "    # COMPRESSION - usually free throughput\n"
                "    compression_type='zstd',\n\n"
                "    # DURABILITY - survive a broker loss\n"
                "    acks='all',\n"
                "    enable_idempotence=True,\n"
                "    max_in_flight_requests_per_connection=5,\n"
                ")\n\n"
                "# linger_ms=0  -> 1 record per request (low throughput)\n"
                "# linger_ms=20 -> many records per request (50-100x more)"
            ),
            caption="Copy this config. Tweak linger_ms based on your "
                    "latency budget.",
            source=src_conf,
            notes=(
                "This is a real-world snippet. Walk through each block: "
                "batching, compression, durability. Notice the comment "
                "at the bottom — that's the magic."
            ),
        ),

        # ============================================================
        # CONCEPT 6 — Rebalances
        # ============================================================

        dict(
            kind="content",
            title="Consumer rebalances — the cost you forgot",
            section="Scaling · Rebalances",
            accent=accent,
            bullets=[
                "When a consumer JOINS or LEAVES a group, partitions get "
                "reassigned",
                "During the reassignment, the group PAUSES processing",
                "Frequent rebalances = frequent processing freezes",
                "Modern protocol (cooperative-sticky) only moves AFFECTED "
                "partitions",
                "The deadly bug: max.poll.interval.ms too SHORT -> broker "
                "thinks you died -> rebalance",
            ],
            right_panel=("text",
                "REAL FAILURE MODE\n\n"
                "Your code:\n"
                "  consumer.poll()\n"
                "  do_big_DB_write()  # takes 6 min\n\n"
                "max.poll.interval.ms = 5 min\n\n"
                "-> broker: 'you missed the deadline,\n"
                "          you must be dead'\n"
                "-> rebalance fires\n"
                "-> your partitions go elsewhere\n"
                "-> when you finally commit,\n"
                "  the offset is WRONG"),
            source=src_kafka,
            notes=(
                "The max.poll.interval gotcha eats teams alive. Make sure "
                "it's longer than your worst-case processing time."
            ),
        ),

        # ============================================================
        # CONCEPT 7 — Adding a broker
        # ============================================================

        dict(
            kind="code",
            title="Adding a broker LIVE — the three-step dance",
            section="Scaling · Reassignment",
            accent=accent,
            language="bash",
            code=(
                "# 1. New broker (id=4) joins the cluster\n"
                "docker compose up -d kafka-4\n\n\n"
                "# 2. Generate a plan that includes broker 4\n"
                "kafka-reassign-partitions.sh \\\n"
                "  --bootstrap-server kafka:9092 \\\n"
                "  --topics-to-move-json-file topics.json \\\n"
                "  --broker-list \"1,2,3,4\" \\\n"
                "  --generate > plan.json\n\n\n"
                "# 3. Execute the plan - THROTTLED to 50 MB/s\n"
                "#    (without throttle, you saturate inter-broker network)\n"
                "kafka-reassign-partitions.sh \\\n"
                "  --bootstrap-server kafka:9092 \\\n"
                "  --reassignment-json-file plan.json \\\n"
                "  --throttle 50000000 \\\n"
                "  --execute\n\n\n"
                "# 4. Verify (then REMOVE the throttle when done)\n"
                "kafka-reassign-partitions.sh ... --verify"
            ),
            caption="ALWAYS throttle. ALWAYS verify. ALWAYS remove the "
                    "throttle afterwards.",
            source=src_kafka,
            notes=(
                "Three steps: add broker, generate plan, execute with "
                "throttle. The throttle is critical — unthrottled "
                "reassignment tanks producer latency."
            ),
        ),

        dict(
            kind="chart",
            title="Why we throttle — the maths",
            section="Scaling · Throttling",
            accent=accent,
            chart_path=images["throttling_curve"],
            caption="Throttle too LOW -> response delays stretch past 1 s -> "
                    "ISR starts to shrink. Sweet spot: above the red line.",
            source="docs.confluent.io/platform/current/kafka/post-deployment.html",
            notes=(
                "The floor exists because under-throttle causes "
                "follower-fetch responses to time out. Stay above it."
            ),
        ),

        # ============================================================
        # CONCEPT 8 — Rack awareness
        # ============================================================

        dict(
            kind="content",
            title="Rack awareness — survive a whole datacentre going down",
            section="Scaling · Topology",
            accent=accent,
            bullets=[
                "Set broker.rack=us-east-1a (etc.) on every broker",
                "Kafka then spreads partition replicas ACROSS racks",
                "An AZ outage means you lose ONE replica per partition, not all",
                "Bonus: consumers can fetch from the SAME-rack replica -> "
                "saves real money on cross-AZ network",
                "One config line. Massive resilience. Always set it.",
            ],
            right_panel=("text",
                "WITHOUT RACK AWARENESS\n\n"
                "Partition 7 replicas -> [B1, B2, B3]\n"
                "  all in us-east-1a.\n\n"
                "us-east-1a fails -> partition\n"
                "  unavailable until brokers return.\n\n"
                "WITH RACK AWARENESS\n\n"
                "Replicas -> [1a-B1, 1b-B4, 1c-B7]\n"
                "  one per AZ.\n\n"
                "us-east-1a fails -> leader fails over\n"
                "  in 30 seconds. Service continues."),
            source=src_kafka,
            notes=(
                "One config option, life-changing impact. People skip it "
                "because it 'works fine' until the AZ outage."
            ),
        ),

        # ============================================================
        # CONCEPT 9 — Tuning checklist
        # ============================================================

        dict(
            kind="table",
            title="The producer/consumer tuning cheat sheet",
            section="Scaling · Tuning",
            accent=accent,
            headers=["Setting", "Default", "High-throughput choice"],
            rows=[
                ["producer linger.ms", "0", "10-50 ms"],
                ["producer batch.size", "16 KB", "64 KB - 1 MB"],
                ["producer compression.type", "none", "zstd or snappy"],
                ["producer acks", "1", "all (with min.isr=2)"],
                ["producer enable.idempotence", "false (pre-3.0)", "true"],
                ["consumer fetch.min.bytes", "1", "1 KB - 1 MB"],
                ["consumer fetch.max.wait.ms", "500", "100-500 ms"],
                ["consumer max.poll.records", "500",
                 "based on processing time"],
            ],
            source=src_conf,
            notes=(
                "These eight knobs handle most practical tuning. None "
                "require code changes — pure config."
            ),
        ),

        # ============================================================
        # CONCEPT 10 — Auto-scaling
        # ============================================================

        dict(
            kind="content",
            title="Auto-scaling consumers — scale on LAG, not CPU",
            section="Scaling · Auto-scaling",
            accent=accent,
            bullets=[
                "Kubernetes HPA on CPU is WRONG for stream consumers",
                "Lag (not CPU) is the right signal: 'are we falling behind?'",
                "KEDA = Kubernetes Event-Driven Autoscaling — has a Kafka trigger",
                "Scale up when lag > threshold for N minutes",
                "Scale down SLOWLY — frequent scale-downs trigger rebalances",
                "HARD CAP at partition count — extra pods are idle anyway",
            ],
            right_panel=("text",
                "KEDA snippet\n\n"
                "triggers:\n"
                "- type: kafka\n"
                "  metadata:\n"
                "    bootstrapServers: kafka:9092\n"
                "    consumerGroup: trip-consumer\n"
                "    topic: trips\n"
                "    lagThreshold: '5000'\n\n"
                "minReplicas: 1\n"
                "maxReplicas: 18   # = partition count"),
            source="keda.sh/docs/scalers/apache-kafka/",
            notes=(
                "Lag-based scaling. Hard cap at partition count. Anything "
                "more is wasted money."
            ),
        ),

        # ============================================================
        # CONCEPT 11 — Capacity planning
        # ============================================================

        dict(
            kind="table",
            title="Capacity planning — six numbers you need to measure",
            section="Scaling · Capacity",
            accent=accent,
            headers=["Dimension", "Measure today", "Plan for"],
            rows=[
                ["Peak ingest (MB/s)", "BytesInPerSec p95", "2 × peak"],
                ["Storage per topic (GB/day)", "log_size_growth",
                 "retention_days × 1.3"],
                ["Network egress (consumer fan-out)",
                 "BytesOutPerSec × consumers", "n + 1 redundancy"],
                ["Partitions per broker", "PartitionCount / brokers",
                 "< 4000"],
                ["JVM heap", "jvm_memory_used p99", "<= 6 GB total"],
                ["Disk queue depth", "iostat avgqu-sz", "< 4 sustained"],
            ],
            source="confluent.io/blog/how-to-survive-a-kafka-outage",
            notes=(
                "Capacity planning is multiplication once you have the "
                "measurements. The trap is planning for AVERAGE rather "
                "than PEAK."
            ),
        ),

        # ============================================================
        # LAB CALLOUT
        # ============================================================

        dict(
            kind="lab",
            title="Hands-on: add a broker live + survive a failure",
            section="Scaling · Lab",
            lab_name="Labs 14-15 · scale-out + fault injection",
            summary="Add a 4th broker UNDER LOAD, throttle the rebalance, "
                    "then kill a broker mid-flight and verify zero loss.",
            bullets=[
                "Lab_Files/load_test.py — sustain 5 000 msg/s",
                "docker compose up kafka-4 -> join the cluster",
                "Generate + execute reassignment, throttled to 50 MB/s",
                "Grafana: watch UnderReplicatedPartitions during reassignment",
                "Kill kafka-2 mid-flight -> producer continues",
                "Check warehouse row count == produced count",
            ],
            notes=(
                "Most ambitious lab of the day. By the end they've added "
                "capacity LIVE and survived a broker failure with the "
                "dashboard as their guide."
            ),
        ),
    ]
