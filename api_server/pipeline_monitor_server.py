from fastapi import HTTPException

from api_server.database import execute_query


def get_latest_pipeline_run():
    query = """
        SELECT
            batch_id,
            source_name,
            batch_date,
            min_event_date,
            max_event_date,
            records_received,
            records_processed,
            records_failed,
            status,
            started_at,
            completed_at,
            error_message
        FROM pipeline_batches
        ORDER BY started_at DESC
        LIMIT 1
    """

    result = execute_query(query, fetch_one=True)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No pipeline runs found.",
        )

    return {
        "success": True,
        "run": result,
    }


def get_pipeline_status():
    summary = execute_query(
        """
        SELECT
            COUNT(*) AS total_runs,
            SUM(status = 'SUCCESS') AS successful_runs,
            SUM(status = 'FAILED') AS failed_runs,
            SUM(status = 'RUNNING') AS running_runs
        FROM pipeline_batches
        """,
        fetch_one=True,
    )

    latest = execute_query(
        """
        SELECT
            batch_id,
            status,
            started_at,
            completed_at,
            error_message
        FROM pipeline_batches
        ORDER BY started_at DESC
        LIMIT 1
        """,
        fetch_one=True,
    )

    return {
        "success": True,
        "latest_run": latest,
        "summary": summary,
    }


def get_failed_batches():
    rows = execute_query(
        """
        SELECT
            batch_id,
            source_name,
            batch_date,
            records_received,
            records_processed,
            records_failed,
            status,
            started_at,
            completed_at,
            error_message
        FROM pipeline_batches
        WHERE status = 'FAILED'
        ORDER BY started_at DESC
        LIMIT 100
        """,
        fetch_all=True,
    )

    return {
        "success": True,
        "count": len(rows),
        "batches": rows,
    }


def get_watermark():
    rows = execute_query(
        """
        SELECT
            pipeline_name,
            source_name,
            watermark_column,
            last_processed_value,
            updated_at
        FROM pipeline_watermarks
        ORDER BY updated_at DESC
        LIMIT 100
        """,
        fetch_all=True,
    )

    return {
        "success": True,
        "count": len(rows),
        "watermarks": rows,
    }