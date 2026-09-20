from operations.airflow_client import AirflowClient
from operations.diagnosis import build_diagnosis
from operations.report_formatter import format_operation_email
from operations.notifier import EmailNotifier
from operations.rag_helper import search_troubleshooting


DAG_ID = "olist_incremental_pipeline"


def extract_log_tail(log_content, lines=40):

    text_lines = []

    for item in log_content:

        if isinstance(item, dict):
            message = (
                item.get("message")
                or item.get("event")
                or ""
            )

            if message:
                text_lines.append(str(message))

        else:
            text_lines.append(str(item))

    return "\n".join(
        text_lines[-lines:]
    )


def main():

    client = AirflowClient()

    run = client.get_latest_dag_run(
        DAG_ID
    )

    if not run:
        raise RuntimeError(
            "No Airflow runs found."
        )

    data = client.get_task_instances(
        DAG_ID,
        run["dag_run_id"],
    )

    tasks = data.get(
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

    report = {
        "run": run,
        "tasks": tasks,
        "failed_tasks": failed_tasks,
        "diagnosis": diagnosis,
    }

    subject, body = format_operation_email(
        report
    )

    if failed_tasks:

        failed_task = failed_tasks[0]

        task_id = failed_task.get(
            "task_id"
        )

        try_number = failed_task.get(
            "try_number",
            1,
        )

        log = client.get_task_log(
            DAG_ID,
            run["dag_run_id"],
            task_id,
            try_number,
        )

        log_tail = extract_log_tail(
            log.get("content", []),
            lines=40,
        )

        body += f"""

Recent Airflow Log
==================

Task:
{task_id}

{log_tail}
"""

        # Search the existing project RAG knowledge base.
        rag_query = (
            f"Olist pipeline failure troubleshooting. "
            f"Failed Airflow task: {task_id}. "
            f"Recent error information: {log_tail[-2000:]}"
        )

        rag_result = search_troubleshooting(
            rag_query,
            top_k=3,
        )

        body += """

Project Knowledge / Troubleshooting Guidance
============================================
"""

        if rag_result.get("success"):

            results = (
                rag_result.get("results")
                or rag_result.get("documents")
                or []
            )

            if results:

                for result in results:

                    if isinstance(result, dict):

                        content = (
                            result.get("content")
                            or result.get("text")
                            or result.get("snippet")
                            or ""
                        )

                        if content:
                            body += (
                                f"\n- {content}\n"
                            )

            else:
                body += (
                    "\nNo relevant project "
                    "troubleshooting guidance found.\n"
                )

        else:

            body += (
                "\nRAG troubleshooting lookup "
                "was unavailable.\n"
            )

    print("\n=== EMAIL SUBJECT ===")
    print(subject)

    print("\n=== EMAIL BODY ===")
    print(body)

    notifier = EmailNotifier()

    notifier.send(
        subject,
        body,
    )

    print("\nEmail sent successfully.")


if __name__ == "__main__":
    main()