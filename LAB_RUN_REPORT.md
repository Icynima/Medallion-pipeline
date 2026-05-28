# Medallion Pipeline Lab Run Report

Run date: 2026-05-28 20:51 IST  
Workspace: `/home/ubuntu/Downloads/Medallion-pipeline`

## Environment Summary

- Python: PASS (`python3 3.10.12`)
- Git/curl: PASS
- Docker CLI: PASS (`Docker 29.5.1`)
- Docker Compose: PASS (`docker compose v5.1.3`)
- Docker daemon access: available via sudo for lab execution
- Spark: PASS (`spark-submit 4.1.1`)
- Java: PASS (`OpenJDK 21.0.10`)
- LibreOffice: PASS
- Apache Hop CLI/GUI: NOT FOUND
- Python module `kafka`: PASS after `python3 -m pip install --user kafka-python`
- Python module `pandas`: NOT FOUND
- Python module `pyspark`: PASS

## Day-by-Day Status

| Day | Status | Evidence / Reason |
| --- | --- | --- |
| Day 01 | SUCCESS | Completed local Python labs 0-4 and final validation. `src/validate_outputs.py` reported all PASS. Generated outputs under `Week_01/Day_01/Lab_Files/out/`. |
| Day 02 | SUCCESS | Completed Kafka broker, topic creation, CLI producer/consumer, Python producer/consumer, partitioning experiment, and consumer group offset check. Report: `Week_01/Day_02/DAY_02_LAB_REPORT.md`. |
| Day 03 | SUCCESS | Completed Kafka broker and Connect worker, consumer groups, offsets/reset, replication/acks, Python manual commit consumer, and FileStream source/sink connectors. Report: `Week_01/Day_03/DAY_03_LAB_REPORT.md`. |
| Day 04 | SUCCESS | Completed PostgreSQL CDC with Debezium: services started, connector RUNNING, initial snapshot records consumed, insert/update CDC observed, and incremental snapshot signal verified. Report: `Week_01/Day_04/DAY_04_LAB_REPORT.md`. |
| Day 05 | SUCCESS WITH DEVIATION | Completed PostgreSQL CDC, MySQL CDC, clickstream, CSV ingestion, DLQ, Kafka UI/service checks, and generic consumer evidence. Deviation: JSON converters used instead of Avro, so Schema Registry has no subjects. Report: `Week_01/Day_05/DAY_05_LAB_REPORT.md`. |
| Day 06 | PARTIAL SUCCESS | Clean Docker re-run completed. Hop Web Docker was verified at `localhost:8082/ui`, Hop Server was verified at `localhost:8181`, Kafka UI opened at `localhost:8080`, and runnable equivalents completed customer cleaning, order enrichment, Kafka `orders.cdc` production, NEW-order filtering/deduplication, and `orders.cleaned` output. The Day 6 Word guide was rebuilt with real Ubuntu `gnome-screenshot` screenshots. Report: `Week_02/Day_06/DAY_06_LAB_REPORT.md`. |
| Day 07 | SUCCESS | Full practical lakehouse use case completed. MinIO, Kafka, and Zookeeper started; `bronze` and `silver` buckets were created; 6 Kafka order events were landed as Bronze JSON; Spark produced 3 cleaned/deduplicated Silver records; Silver CSV and Parquet were uploaded to MinIO. The Day 7 Word guide was rebuilt with Linux/Windows installation steps and real Ubuntu `gnome-screenshot` captures from the MinIO Console. Report: `Week_02/Day_07/DAY_07_LAB_REPORT.md`. |
| Day 08 | SUCCESS | Airflow/Postgres Docker lab completed. Fixed data volume mount, Airflow log permissions, `fs_default` connection, and removed the DAG's pandas dependency. Triggered `medallion_pipeline`; all tasks succeeded. Verified Bronze=5 rows, Silver=4 rows, and Gold customer totals. The Day 8 Word guide was rebuilt with Linux/Windows installation steps and real Airflow UI screenshots. Report: `Week_02/Day_08/DAY_08_LAB_REPORT.md`. |
| Day 09 | SUCCESS | Kafka, Schema Registry, ksqlDB, and Kafka UI started successfully. Produced 20 order events, ran the streaming aggregation, simulated a stopped processor incident, verified `orders` stayed at 20 while `order_counts` recovered from 4 to 8 records, and rebuilt the Day 9 Word guide with real Kafka UI screenshot evidence. Report: `Week_02/Day_09/DAY_09_LAB_REPORT.md`. |
| Day 10 | BLOCKED | Capstone requires PostgreSQL sources, Kafka, Schema Registry, Kafka Connect/Debezium, ksqlDB, Kafka UI, and optional MinIO via Docker Compose. Docker daemon access is denied. |

## Day 01 Commands Run

From `Week_01/Day_01/Lab_Files`:

```bash
bash setup/verify_environment.sh
python3 src/reset_outputs.py
python3 src/tightly_coupled_order.py --fail-notification
python3 src/tightly_coupled_order.py
python3 src/event_bus_pipeline.py produce
python3 src/event_bus_pipeline.py consume --fail-notification
python3 src/event_bus_pipeline.py consume
python3 src/event_bus_pipeline.py consume
python3 src/batch_pipeline.py
python3 src/stream_pipeline.py --delay-seconds 0
python3 src/medallion_pipeline.py
python3 src/validate_outputs.py
```

Expected intentional failures:

- `tightly_coupled_order.py --fail-notification` returned a simulated notification outage.
- `event_bus_pipeline.py consume --fail-notification` returned a simulated consumer outage.

Final Day 01 validator result:

```text
PASS - event inbox exists
PASS - event consumer checkpoint exists
PASS - batch summary exists
PASS - stream state exists
PASS - bronze raw events exist
PASS - silver view exists
PASS - gold KPIs exist
PASS - gold excludes cancelled-only adjustment
PASS - six streaming events handled
PASS - generated evidence is ready for debrief.
```

## Static Checks Completed

```bash
python3 -m py_compile $(find Week_*/Day_*/Lab_Files -name '*.py' | sort)
```

Result: PASS, all Python files compile syntactically.

## Required Next Action

To continue Days 02-10, the current user needs Docker daemon access. The usual fix is one of:

```bash
sudo usermod -aG docker ubuntu
```

Then log out and back in, or restart the shell/session so the new group is active.

Alternatively, run the lab commands with sudo-enabled Docker access.

Additional software/packages needed after Docker is available:

- `python3 -m pip install --user kafka-python pandas`
- Apache Hop for Day 06 visual pipeline exercises

After Docker access is fixed, resume with Day 02 and run each lab guide in order.
