# Day 8 – Workflow Orchestration with Apache Airflow

## Lab: Building Production-Grade Data Pipelines with Airflow, Kafka & Apache Hop

---

## Overview

This lab provides **8 hours** of hands-on experience building real-world data pipelines using **Apache Airflow** as the orchestration engine, integrated with **Apache Kafka** for event streaming and **Apache Hop** for visual ETL transformations.

You will progress through 10 labs, each building on the previous one, ultimately creating a complete **Medallion Architecture** pipeline (Bronze → Silver → Gold) orchestrated by Airflow.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    AIRFLOW (Orchestrator)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Webserver │  │ Scheduler│  │ Triggerer│  │  Workers │       │
│  │  :8080    │  │          │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│         │              │              │              │          │
│         ▼              ▼              ▼              ▼          │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                    10 DAGs                          │       │
│  │  01_hello → 02_operators → 03_medallion →          │       │
│  │  04_sensors → 05_taskflow → 06_dynamic →           │       │
│  │  07_hop → 08_kafka → 09_full_e2e → 10_advanced     │       │
│  └─────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Kafka     │    │  Apache Hop  │
│   :5432      │    │   :9092      │    │  Web  :8082  │
│              │    │   KRaft mode │    │  CLI (batch) │
│ ┌──────────┐ │    │              │    │              │
│ │  Bronze  │ │    │ orders.raw   │    │ ┌──────────┐ │
│ │  Silver  │ │    │ orders.proc  │    │ │ .hpl     │ │
│ │  Gold    │ │    │              │    │ │ .hwf     │ │
│ └──────────┘ │    └──────────────┘    │ └──────────┘ │
└──────────────┘                        └──────────────┘
                         │
                         ▼
                ┌──────────────┐
                │   Kafka UI   │
                │    :8081     │
                └──────────────┘
```

---

## Service Endpoints

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow UI** | http://localhost:8080 | admin / admin |
| **Kafka UI** | http://localhost:8081 | – |
| **Hop Web UI** | http://localhost:8082 | – |
| **PostgreSQL** | localhost:5432 | airflow / airflow |

---

## Quick Start

### 1. Start the Environment

```bash
cd Lab_Files

# Build and start all services
docker compose up -d --build

# Wait for services to be healthy (~2-3 minutes)
docker compose ps

# Verify everything is running
docker compose exec airflow-web python /opt/airflow/scripts/verify_setup.py
```

### 2. Access Airflow

Open http://localhost:8080 and login with **admin / admin**.

You'll see 10 DAGs ready for exploration.

### 3. Teardown

```bash
docker compose down -v     # remove containers and volumes
```

---

## Lab Schedule (8 Hours)

### Lab 1: Hello Airflow (45 min)
**DAG:** `01_hello_airflow`

**Objectives:**
- Understand the Airflow UI (DAGs list, Graph view, Grid view, Gantt chart)
- Create and trigger your first DAG
- Learn `BashOperator` and `PythonOperator`
- Understand task dependencies with `>>` operator
- Read task logs

**Exercises:**
1. Open the Airflow UI → Navigate to `01_hello_airflow`
2. Explore the Graph view – identify the diamond dependency pattern
3. Trigger the DAG manually (▶ button)
4. Click on each task → View Log → observe the output
5. **Challenge:** Modify the DAG to add a new `BashOperator` that counts files in `/opt/airflow/dags/`

---

### Lab 2: Operators Deep Dive (60 min)
**DAG:** `02_operators_showcase`

**Objectives:**
- Master `BashOperator` with Jinja templating
- Use `PostgresOperator` for SQL execution
- Understand `BranchPythonOperator` for conditional logic
- Learn `ShortCircuitOperator` for conditional skipping
- Understand trigger rules (`all_success`, `none_failed_min_one_success`)

**Exercises:**
1. Trigger `02_operators_showcase` and observe the branching
2. Run it multiple times – notice how the branch changes (random number)
3. Check the `dag_audit_log` table in PostgreSQL:
   ```bash
   docker compose exec postgres psql -U airflow -c "SELECT * FROM dag_audit_log;"
   ```
4. Study the Jinja templates in `bash_with_template` task logs
5. **Challenge:** Add a new branch path for numbers > 75 called `very_high_value_path`

---

### Lab 3: Medallion Pipeline (60 min)
**DAG:** `03_medallion_pipeline` (formerly `medallion_pipeline.py`)

**Objectives:**
- Build a complete Bronze → Silver → Gold pipeline
- Use `FileSensor` in reschedule mode
- Pass metadata between tasks using XCom
- Understand parallel task execution
- Validate data through SQL transformations

**Exercises:**
1. Trigger `03_medallion_pipeline` – observe the parallel bronze loads
2. After completion, check the tables:
   ```bash
   docker compose exec postgres psql -U airflow -c "SELECT COUNT(*) FROM bronze_orders;"
   docker compose exec postgres psql -U airflow -c "SELECT * FROM gold_customer_360;"
   docker compose exec postgres psql -U airflow -c "SELECT * FROM gold_daily_sales;"
   ```
3. Examine XCom values: Airflow UI → Admin → XComs
4. Look at the `pipeline_execution_log` table for lineage
5. **Challenge:** Add a `gold_product_performance` task to the pipeline

---

### Lab 4: Sensors & Scheduling (45 min)
**DAG:** `04_sensor_patterns`

**Objectives:**
- Compare `poke` vs `reschedule` sensor modes
- Understand `SqlSensor` for data-driven waiting
- Learn `TimeDeltaSensor` for time-based delays
- Master cron expressions and schedule presets
- Implement SLA monitoring

**Exercises:**
1. Trigger `04_sensor_patterns` and observe sensor behaviour
2. Check the difference between poke and reschedule modes in the Grid view
3. Study the cron expression: `*/30 9-17 * * 1-5`
4. Review SLA configurations in the DAG
5. **Challenge:** Create a new `SqlSensor` that waits until `silver_orders` has > 10 rows

---

### Lab 5: XCom & TaskFlow API (60 min)
**DAG:** `05_xcom_and_taskflow`

**Objectives:**
- Compare traditional XCom (push/pull) vs TaskFlow API (@task)
- Pass complex data (dicts, lists) between tasks
- Understand automatic dependency inference in TaskFlow
- Build a business intelligence report pipeline
- Learn XCom best practices and limitations

**Exercises:**
1. First run `03_medallion_pipeline` to populate data
2. Then trigger `05_xcom_and_taskflow`
3. Compare the traditional section vs TaskFlow section in the logs
4. Check XCom values in Admin → XComs (note the data sizes)
5. Study how TaskFlow infers dependencies from function arguments
6. **Challenge:** Add a `@task` that calculates month-over-month growth rate

---

### Lab 6: Dynamic DAGs & Task Groups (45 min)
**DAG:** `06_dynamic_dags`

**Objectives:**
- Use `expand()` for dynamic task mapping
- Organize tasks with `@task_group`
- Process multiple data sources in parallel
- Run parameterized quality checks
- Understand mapped task instances in the UI

**Exercises:**
1. Trigger `06_dynamic_dags` and observe the mapped task instances
2. In the Graph view, expand the `validate_sources` and `data_quality` TaskGroups
3. Note how categories are dynamically discovered from the database
4. Study the `analyze_category` mapped task – one instance per category
5. **Challenge:** Add a new TaskGroup that generates a summary email (print) per category

---

### Lab 7: Apache Hop Integration (60 min)
**DAG:** `07_hop_integration`

**Objectives:**
- Trigger Hop pipelines from Airflow (3 methods)
- Use `BashOperator` with `docker exec` for Hop CLI
- Use `PythonOperator` with Hop utility functions
- Build hybrid workflows (Airflow orchestration + Hop transforms)
- Open Hop Web UI and explore pipeline designs

**Exercises:**
1. Open the Hop Web UI at http://localhost:8082
2. Navigate to `pipelines/` and open `bronze_csv_ingest.hpl`
3. Study the pipeline flow: Read CSV → Validate → Write to PostgreSQL
4. Trigger `07_hop_integration` in Airflow
5. Compare the three integration methods in the TaskGroup views
6. Open `silver_transform.hpl` in Hop – trace the Sort → Deduplicate → Cast flow
7. **Challenge:** Create a new Hop pipeline that reads from `products.csv` and writes to a `bronze_products` table

---

### Lab 8: Kafka Integration (60 min)
**DAG:** `08_kafka_consumer_pipeline`

**Objectives:**
- Consume Kafka events in Airflow (micro-batch pattern)
- Bridge streaming and batch processing
- Write Kafka events to Bronze layer
- Transform Kafka events to Silver layer
- Monitor Kafka topics in the Kafka UI

**Exercises:**
1. Open Kafka UI at http://localhost:8081
2. Produce test events:
   ```bash
   docker compose exec airflow-web python /opt/airflow/scripts/kafka_producer.py --count 20
   ```
3. Check Kafka UI → Topics → `orders.raw` to see the messages
4. Trigger `08_kafka_consumer_pipeline`
5. Verify bronze_kafka_events:
   ```bash
   docker compose exec postgres psql -U airflow -c "SELECT COUNT(*) FROM bronze_kafka_events;"
   ```
6. **Challenge:** Modify the producer to send events with a `priority` field, then filter high-priority events in the silver transform

---

### Lab 9: Full End-to-End Orchestration (60 min)
**DAG:** `09_full_orchestration`

**Objectives:**
- Build a complete pipeline: Kafka → CSV → Hop → Bronze → Silver → Gold
- Implement data quality gates between layers
- Handle multiple data sources in parallel
- Track pipeline execution metadata
- Generate executive summary reports

**Exercises:**
1. Ensure you've run the Kafka producer (Lab 8)
2. Trigger `09_full_orchestration`
3. Watch the 5-phase execution in the Graph view
4. Check the data quality results:
   ```bash
   docker compose exec postgres psql -U airflow -c "SELECT * FROM data_quality_results ORDER BY checked_at DESC LIMIT 10;"
   ```
5. Review the executive summary in the `generate_executive_summary` task log
6. Check all gold tables are populated
7. **Challenge:** Add a sixth phase that exports gold tables to CSV files

---

### Lab 10: Advanced Production Patterns (45 min)
**DAG:** `10_advanced_patterns`

**Objectives:**
- Use Airflow Variables for configuration management
- Design idempotent tasks (safe to re-run)
- Implement custom callbacks (on_success, on_failure, on_retry)
- Use `TriggerDagRunOperator` for cross-DAG dependencies
- Build monitoring and SLA compliance dashboards
- Understand exponential backoff retry strategies

**Exercises:**
1. Review Airflow Variables: Admin → Variables
2. Trigger `10_advanced_patterns`
3. Run it twice – verify the `pipeline_summary` table shows exactly 1 row per date (idempotency)
4. Check callbacks in the task logs (look for SUCCESS/FAILURE messages)
5. Observe `trigger_medallion_pipeline` – it triggers DAG 03 automatically
6. Review the monitoring TaskGroup for SLA compliance
7. **Challenge:** Add a custom callback that writes alerts to a `pipeline_alerts` table

---

## File Structure

```
Lab_Files/
├── docker-compose.yml          # Full stack definition
├── Dockerfile.airflow          # Custom Airflow image
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
│
├── dags/                       # Airflow DAGs (10 progressive labs)
│   ├── 01_hello_airflow.py
│   ├── 02_operators_showcase.py
│   ├── medallion_pipeline.py   # 03_medallion_pipeline
│   ├── 04_sensor_patterns.py
│   ├── 05_xcom_and_taskflow.py
│   ├── 06_dynamic_dags.py
│   ├── 07_hop_integration.py
│   ├── 08_kafka_consumer_dag.py
│   ├── 09_full_orchestration.py
│   ├── 10_advanced_patterns.py
│   └── helpers/
│       ├── kafka_utils.py      # Kafka producer/consumer utilities
│       └── hop_utils.py        # Apache Hop CLI wrapper
│
├── hop/                        # Apache Hop project
│   ├── project-config.json
│   ├── pipelines/
│   │   ├── bronze_csv_ingest.hpl
│   │   ├── silver_transform.hpl
│   │   ├── gold_aggregation.hpl
│   │   └── kafka_orders_consumer.hpl
│   └── workflows/
│       └── day8_medallion_batch.hwf
│
├── sql/
│   └── init_warehouse.sql      # Database schema (Bronze/Silver/Gold)
│
├── scripts/
│   ├── kafka_producer.py       # Generate Kafka events
│   └── verify_setup.py         # Environment health check
│
├── data/                       # Sample data files
│   ├── new_orders.csv
│   ├── customers.csv
│   └── products.csv
│
├── plugins/                    # Airflow plugins directory
├── include/                    # Shared templates and configs
└── logs/                       # Airflow logs (auto-created)
```

---

## Key Concepts Covered

### Airflow Architecture
- **Webserver** – UI for monitoring and triggering DAGs
- **Scheduler** – Parses DAGs, creates DagRuns, schedules tasks
- **Triggerer** – Handles deferrable operators (async waiting)
- **Executor** – LocalExecutor (single-node) vs CeleryExecutor (distributed)
- **Metadata DB** – PostgreSQL storing DAG state, XComs, connections

### DAG Concepts
- Default arguments and inheritance
- Schedule intervals (cron, presets, None)
- Catchup and backfilling
- Task dependencies (`>>`, `<<`, lists)
- Trigger rules (all_success, one_success, none_failed, all_done)

### Operators
- `BashOperator` – shell commands with Jinja templates
- `PythonOperator` – Python callables with context
- `PostgresOperator` – SQL execution via connections
- `BranchPythonOperator` – conditional branching
- `ShortCircuitOperator` – conditional skipping
- `EmptyOperator` – sync/join points
- `TriggerDagRunOperator` – cross-DAG triggering
- `FileSensor` – file existence monitoring

### Data Passing
- XCom push/pull (traditional)
- TaskFlow API (@task decorator)
- Automatic dependency inference
- XCom size limits and best practices

### Integration Patterns
- **Airflow + Kafka:** Micro-batch consumption, event-driven triggers
- **Airflow + Hop:** CLI execution, DockerOperator, hybrid workflows
- **Airflow + PostgreSQL:** Direct SQL, connection management

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DAGs not appearing | Wait 30s for scheduler to parse. Check `docker compose logs airflow-sched` |
| FileSensor timeout | Verify CSV files exist in `data/` directory |
| PostgreSQL errors | Run `docker compose exec postgres psql -U airflow -c "\dt"` to check tables |
| Kafka connection errors | Check `docker compose logs kafka` and wait for broker to start |
| Hop pipelines "simulated" | Expected behaviour – Hop CLI runs inside hop-cli container, not Airflow |
| Port conflicts | Change ports in `docker-compose.yml` if 8080/8081/8082/5432 are in use |

---

## Prerequisites

- Docker Desktop with at least **8 GB** RAM allocated
- Docker Compose v2+
- A modern web browser
- (Optional) DBeaver or pgAdmin for PostgreSQL exploration
