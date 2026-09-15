import requests

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("pipeline-monitor-server")

API_BASE_URL = "http://127.0.0.1:8003"


@mcp.tool()
def get_latest_pipeline_run() -> dict:
    """Get the most recent pipeline execution details."""

    response = requests.get(
        f"{API_BASE_URL}/pipeline/latest",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def get_pipeline_status() -> dict:
    """Get the current/latest pipeline status."""

    response = requests.get(
        f"{API_BASE_URL}/pipeline/status",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def get_failed_batches() -> list:
    """Get pipeline batches that did not complete successfully."""

    response = requests.get(
        f"{API_BASE_URL}/pipeline/failed",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


@mcp.tool()
def get_watermark() -> list:
    """Get the current pipeline watermarks."""

    response = requests.get(
        f"{API_BASE_URL}/pipeline/watermark",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    mcp.run(transport="stdio")