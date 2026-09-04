import httpx
from mcp.server.fastmcp import FastMCP
from urllib.parse import quote

mcp = FastMCP("Employee Server")

def call_api(url: str, not_found_message: str, api_error_message: str):
    try:
        response = httpx.get(url, timeout=5.0)

        if response.status_code == 404:
            return {
                "error": not_found_message
            }

        response.raise_for_status()
        return response.json()

    except httpx.ConnectError:
        return {
            "error": api_error_message
        }

    except httpx.TimeoutException:
        return {
            "error": "Request to Employee API timed out"
        }

    except httpx.HTTPError as e:
        return {
            "error": f"Employee API request failed: {str(e)}"
        }


@mcp.tool()
def get_employee(employee_id: str) -> dict:
    """Get employee information using an employee ID."""

    url = (
        "http://127.0.0.1:8001/"
        f"employees/{quote(employee_id, safe='')}"
    )

    return call_api(
        url,
        f"No employee found with ID {employee_id}",
        "Employee API is unavailable"
    )


@mcp.tool()
def search_employee_by_name(name: str) -> dict:
    """Search for employee information using an employee name."""

    url = (
        "http://127.0.0.1:8001/"
        f"employees/search/{quote(name, safe='')}"
    )

    return call_api(
        url,
        f"No employee found with name {name}",
        "Employee search API is unavailable"
    )


@mcp.tool()
def get_all_employees() -> dict:
    """Get information about all employees."""

    url = "http://127.0.0.1:8001/employees"

    return call_api(
        url,
        "No employees found",
        "Employee API is unavailable"
    )


@mcp.tool()
def get_department(department_name: str) -> dict:
    """Get information about a specific department."""

    url = (
        "http://127.0.0.1:8001/"
        f"departments/{quote(department_name, safe='')}"
    )

    return call_api(
        url,
        f"No department found with name {department_name}",
        "Department API is unavailable"
    )


@mcp.tool()
def get_all_departments() -> dict:
    """Get information about all departments."""

    url = "http://127.0.0.1:8001/departments"

    return call_api(
        url,
        "No departments found",
        "Department API is unavailable"
    )


@mcp.tool()
def get_department_employees(department_name: str) -> dict:
    """Get all employees belonging to a specific department."""

    url = (
        "http://127.0.0.1:8001/"
        f"departments/{quote(department_name, safe='')}/employees"
    )

    return call_api(
        url,
        f"No employees found in department {department_name}",
        "Department employees API is unavailable"
    )


if __name__ == "__main__":
    mcp.run()