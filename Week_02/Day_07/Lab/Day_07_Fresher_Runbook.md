# Day 7 Fresher Runbook

## Objective

Day 7 teaches a retail order lakehouse in Spark:

- Spark fundamentals: read CSV/JSON, use DataFrames and SQL, write Parquet partitions.
- Bronze: keep raw order events with source metadata.
- Silver: clean types, apply quality rules, quarantine bad rows, calculate latest order state, enrich with dimensions.
- Gold: build business KPIs that a stakeholder can read.
- Object store: mirror the final lakehouse folders into MinIO.

## Clean Start

Run from `Week_02/Day_07/Lab_Files`:

```bash
docker compose -p day7_lab down -v --remove-orphans
rm -rf data lake output state run_logs
python3 generate_data.py
docker compose -p day7_lab up -d spark-master spark-worker
```

Open Spark:

- Master UI: `http://localhost:8081`
- Worker UI: `http://localhost:8083`

If Docker needs sudo on your machine, prefix the Docker commands with `sudo`.

## See The Lab Sequence

```bash
python3 run_lab.py --list
```

## Manual Lab Run

Run one lab, inspect its output, then continue:

```bash
python3 run_lab.py 01
python3 run_lab.py 02
python3 run_lab.py 03
python3 run_lab.py 04
python3 run_lab.py 05
python3 run_lab.py 06
python3 run_lab.py 07
python3 run_lab.py 08
python3 run_lab.py 09
python3 run_lab.py 10
python3 run_lab.py 11
python3 run_lab.py 12
```

## Expected Results

Lab 12 writes `state/lab_12_run_manifest.json` with:

```json
{
  "bronze_rows": 12,
  "silver_valid_rows": 10,
  "quarantine_rows": 2,
  "current_order_rows": 7,
  "enriched_rows": 7
}
```

Key learner checkpoints:

- Lab 04: Bronze has 12 raw rows.
- Lab 07: Silver quality split is 10 valid rows and 2 quarantined rows.
- Lab 08: Current order table has 7 latest order states.
- Lab 10 and Lab 12: Gold creates daily, category, and segment revenue tables.

## MinIO Object Store

Start MinIO and mirror the lakehouse:

```bash
docker compose -p day7_lab up -d minio
docker compose -p day7_lab --profile object-store run --rm mc
```

Open MinIO Console:

- URL: `http://localhost:9001`
- User: `minioadmin`
- Password: `minioadmin`

The bucket should be `day7-lakehouse`. It should contain `bronze/`, `silver/`, `gold/`, `quarantine/`, and `incremental/` paths. The copy excludes local Spark `.crc` side files so the bucket is easier to inspect.

## Windows PowerShell Notes

Use the same Docker commands from `Week_02\Day_07\Lab_Files`. Replace the cleanup command with:

```powershell
Remove-Item -Recurse -Force data, lake, output, state, run_logs -ErrorAction SilentlyContinue
```

Then run:

```powershell
python generate_data.py
python run_lab.py --list
python run_lab.py 01
```
