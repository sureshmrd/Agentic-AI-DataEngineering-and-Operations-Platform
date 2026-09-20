import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Business Server")

API_BASE_URL = "http://127.0.0.1:8003"


@mcp.tool()
def get_business_schema() -> dict:
    """Return the current business analytics database schema."""

    try:
        response = httpx.get(
            f"{API_BASE_URL}/business/schema",
            timeout=10.0,
        )

        if response.status_code >= 400:
            return {
                "success": False,
                "error": response.text,
            }

        return response.json()

    except httpx.HTTPError as exc:
        return {
            "success": False,
            "error": f"Business API error: {exc}",
        }

@mcp.tool()
def execute_read_only_sql(sql: str) -> dict:
    """Execute a validated read-only SQL query against business analytics data."""

    try:
        response = httpx.post(
            f"{API_BASE_URL}/business/query",
            json={"sql": sql},
            timeout=10.0,
        )

        if response.status_code >= 400:
            return {
                "success": False,
                "error": response.json().get("detail", response.text),
            }

        return response.json()

    except httpx.ConnectError:
        return {
            "success": False,
            "error": "Business API is unavailable.",
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Business API request timed out.",
        }
    except httpx.HTTPError as exc:
        return {
            "success": False,
            "error": f"Business API error: {exc}",
        }


if __name__ == "__main__":
    mcp.run()