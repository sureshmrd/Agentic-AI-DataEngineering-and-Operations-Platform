from operations.airflow_client import AirflowClient


DAG_ID = "olist_incremental_pipeline"


def main():
    client = AirflowClient()

    print("\n=== DAG ===")
    dag = client.get_dag(DAG_ID)
    print(f"ID: {dag['dag_id']}")
    print(f"Display name: {dag.get('dag_display_name')}")

    print("\n=== Latest DAG Run ===")
    run = client.get_latest_dag_run(DAG_ID)

    if not run:
        print("No DAG runs found.")
        return

    print(f"Run ID: {run['dag_run_id']}")
    print(f"State: {run['state']}")
    print(f"Start: {run.get('start_date')}")
    print(f"End: {run.get('end_date')}")
    print(f"Duration: {run.get('duration')}")

    print("\n=== Task Instances ===")
    tasks = client.get_task_instances(
        DAG_ID,
        run["dag_run_id"],
    )

    for task in tasks.get("task_instances", []):
        print(
            f"{task['task_id']}: "
            f"{task['state']} "
            f"(try={task['try_number']})"
        )

    print("\n=== Failed Tasks ===")
    failed_tasks = client.get_failed_tasks(
        DAG_ID,
        run["dag_run_id"],
    )

    if not failed_tasks:
        print("No failed tasks.")
    else:
        for task in failed_tasks:
            print(task["task_id"])

    print("\n=== run_pipeline Log ===")
    log = client.get_task_log(
        DAG_ID,
        run["dag_run_id"],
        "run_pipeline",
        1,
    )

    events = log.get("content", [])

    for event in events:
        message = event.get("event")

        if message:
            print(message)


if __name__ == "__main__":
    main()