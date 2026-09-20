import httpx

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Operations Server")

API_BASE_URL = "http://127.0.0.1:8003"


@mcp.tool()
def get_latest_operation() -> dict:
    """Get the latest Airflow pipeline execution and task status."""

    try:
        response = httpx.get(
            f"{API_BASE_URL}/operations/latest",
            timeout=20.0,
        )

        response.raise_for_status()

        return response.json()

    except Exception as exc:
        return {
            "success": False,
            "error": f"Operations API error: {exc}",
        }


@mcp.tool()
def get_airflow_task_log(
    task_id: str,
    try_number: int = 1,
) -> dict:
    """Get Airflow logs for a task from the latest pipeline run."""

    try:
        response = httpx.get(
            f"{API_BASE_URL}/operations/log/{task_id}",
            params={"try_number": try_number},
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()

    except Exception as exc:
        return {
            "success": False,
            "error": f"Operations API error: {exc}",
        }

@mcp.tool()
def get_operation_report() -> dict:
    """Return the latest Airflow operational report and diagnosis."""

    try:
        response = httpx.get(
            f"{API_BASE_URL}/operations/report",
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()

    except Exception as exc:
        return {
            "success": False,
            "error": f"Operations API error: {exc}",
        }


if __name__ == "__main__":
    mcp.run()