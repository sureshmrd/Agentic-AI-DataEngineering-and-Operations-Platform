from typing import Any


def build_diagnosis(
    run: dict[str, Any],
    tasks: list[dict[str, Any]],
    failed_tasks: list[dict[str, Any]],
) -> dict[str, Any]:

    state = run.get("state", "unknown")

    if state == "success":
        return {
            "status": "SUCCESS",
            "summary": "The latest Airflow pipeline run completed successfully.",
            "failed_tasks": [],
        }

    if state == "failed":
        failures = []

        for task in failed_tasks:
            failures.append(
                {
                    "task_id": task.get("task_id"),
                    "state": task.get("state"),
                    "try_number": task.get("try_number"),
                }
            )

        return {
            "status": "FAILED",
            "summary": "The latest Airflow pipeline run failed.",
            "failed_tasks": failures,
        }

    return {
        "status": state.upper(),
        "summary": (
            f"The latest Airflow pipeline run is currently "
            f"in state: {state}."
        ),
        "failed_tasks": [],
    }