def format_operation_email(report: dict) -> tuple[str, str]:

    run = report.get("run", {})
    diagnosis = report.get("diagnosis", {})

    status = diagnosis.get(
        "status",
        "UNKNOWN",
    )

    run_id = run.get(
        "dag_run_id",
        "unknown",
    )

    if status == "SUCCESS":

        subject = "Olist Pipeline - SUCCESS"

        body = f"""
Olist Data Pipeline Daily Report

DAG:
olist_incremental_pipeline

Status:
SUCCESS

Run:
{run_id}

The latest Airflow pipeline execution completed successfully.

No failed tasks were detected.
"""

        return subject, body

    failed_tasks = diagnosis.get(
        "failed_tasks",
        [],
    )

    failed_task_names = ", ".join(
        task.get("task_id", "unknown")
        for task in failed_tasks
    )

    subject = "Olist Pipeline - FAILED"

    body = f"""
Olist Data Pipeline Daily Report

DAG:
olist_incremental_pipeline

Status:
FAILED

Run:
{run_id}

Failed Tasks:
{failed_task_names}

Summary:
{diagnosis.get("summary", "No diagnosis available.")}

The recent Airflow log is included below for troubleshooting.
"""

    return subject, body