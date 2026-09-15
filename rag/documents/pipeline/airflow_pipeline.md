# Airflow Pipeline Operations

## DAG

The incremental pipeline DAG is:

airflow/dags/olist_incremental_pipeline.py

## Task Flow

The current task flow is:

find_next_batch
    ->
run_pipeline
    ->
verify_batch

## Execution

The DAG is manually triggerable in the current implementation.

Airflow runs in a separate WSL environment.

The current Airflow environment uses:

- Ubuntu 22.04
- Python 3.10.6
- Airflow 3.3.1
- Java 17
- PySpark 4.0.1

The Windows agent environment is separate from the Airflow environment.

Airflow does not use ADK or MCP.