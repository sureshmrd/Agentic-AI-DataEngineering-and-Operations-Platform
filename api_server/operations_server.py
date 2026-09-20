import os
import sys

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from operations.diagnosis import build_diagnosis

from operations.airflow_client import AirflowClient
from operations.report_formatter import format_operation_email
from operations.notifier import EmailNotifier

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from operations.airflow_client import AirflowClient

DAG_ID = "olist_incremental_pipeline"


def get_client() -> AirflowClient:
    return AirflowClient()


def get_latest_operation():
    try:
        client = get_client()

        run = client.get_latest_dag_run(DAG_ID)

        if not run:
            return {
                "success": False,
                "message": "No Airflow runs found.",
            }

        tasks = client.get_task_instances(
            DAG_ID,
            run["dag_run_id"],
        )

        failed_tasks = [
            task
            for task in tasks.get("task_instances", [])
            if task.get("state") == "failed"
        ]

        return {
            "success": True,
            "dag_id": DAG_ID,
            "run": run,
            "tasks": tasks.get("task_instances", []),
            "failed_tasks": failed_tasks,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Operations API error: {exc}",
        )

def get_task_log(
    task_id: str,
    try_number: int = 1,
):
    try:
        client = get_client()

        run = client.get_latest_dag_run(DAG_ID)

        if not run:
            return {
                "success": False,
                "message": "No Airflow runs found.",
            }

        log = client.get_task_log(
            DAG_ID,
            run["dag_run_id"],
            task_id,
            try_number,
        )

        return {
            "success": True,
            "dag_run_id": run["dag_run_id"],
            "task_id": task_id,
            "try_number": try_number,
            "log": log.get("content", []),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Operations API error: {exc}",
        )

def get_operation_report():

    try:
        client = get_client()

        run = client.get_latest_dag_run(DAG_ID)

        if not run:
            return {
                "success": False,
                "message": "No Airflow runs found.",
            }

        tasks_data = client.get_task_instances(
            DAG_ID,
            run["dag_run_id"],
        )

        tasks = tasks_data.get(
            "task_instances",
            [],
        )

        failed_tasks = [
            task
            for task in tasks
            if task.get("state") == "failed"
        ]

        diagnosis = build_diagnosis(
            run,
            tasks,
            failed_tasks,
        )

        return {
            "success": True,
            "dag_id": DAG_ID,
            "run": run,
            "tasks": tasks,
            "failed_tasks": failed_tasks,
            "diagnosis": diagnosis,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Operations report error: {exc}",
        )

def build_operation_report_for_run(dag_run_id: str) -> dict:
    client = AirflowClient()

    run = client.get_dag_run(
        DAG_ID,
        dag_run_id,
    )

    tasks_data = client.get_task_instances(
        DAG_ID,
        dag_run_id,
    )

    tasks = tasks_data.get(
        "task_instances",
        [],
    )

    failed_tasks = [
        task
        for task in tasks
        if task.get("state") == "failed"
    ]

    # During send_notification, the DAG itself may still be RUNNING.
    # Therefore determine the operational outcome from task states.
    if failed_tasks:
        effective_state = "failed"
    elif all(
        task.get("state") == "success"
        for task in tasks
        if task.get("task_id") != "send_notification"
    ):
        effective_state = "success"
    else:
        effective_state = run.get("state", "unknown")

    diagnosis = build_diagnosis(
        {
            **run,
            "state": effective_state,
        },
        tasks,
        failed_tasks,
    )

    return {
        "success": True,
        "dag_id": DAG_ID,
        "run": run,
        "tasks": tasks,
        "failed_tasks": failed_tasks,
        "diagnosis": diagnosis,
    }

def send_operation_notification(
    dag_run_id: str,
):
    """
    Generate and send the deterministic operational email
    for a specific Airflow DAG run.
    """

    try:
        report = build_operation_report_for_run(
            dag_run_id
        )

        subject, body = format_operation_email(
            report
        )

        notifier = EmailNotifier()

        notifier.send(
            subject=subject,
            body=body,
        )

        return {
            "success": True,
            "dag_run_id": dag_run_id,
            "subject": subject,
            "message": "Operational notification sent successfully.",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Notification failed: {exc}",
        ) from exc