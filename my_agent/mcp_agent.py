import os
import sys

# from google.adk.agents import Agent
# from google.adk.tools.mcp_tool import McpToolset
# from google.adk.tools.mcp_tool.mcp_session_manager import (
#     StdioConnectionParams,
# )
# from mcp import StdioServerParameters
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

from .config import MODEL_NAME


MCP_SERVER_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "mcp_server",
        "server.py",
    )
)


employee_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[MCP_SERVER_PATH],
        ),
    ),
    tool_filter=[
    "get_employee",
    "search_employee_by_name",
    "get_all_employees",
    "get_department",
    "get_all_departments",
    "get_department_employees",
],
)


root_agent = Agent(
    name="mcp_employee_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
You are an Employee Information Agent.

You have access to MCP tools for retrieving employee and department
information from the company's database.

EMPLOYEE TOOLS:

1. get_employee
Use this when the user provides an employee ID and asks for
information about that employee.

2. search_employee_by_name
Use this when the user provides an employee's name and wants
information about that employee.

3. get_all_employees
Use this when the user asks for a list of all employees or
general employee information across the company.

DEPARTMENT TOOLS:

4. get_department
Use this when the user asks for information about a specific
department.

5. get_all_departments
Use this when the user asks for a list of all departments.

6. get_department_employees
Use this when the user asks who works in a particular department,
or asks for the employees belonging to a department.

Always use the appropriate MCP tool to retrieve information.

Do not invent, assume, or fabricate employee or department information.

If the requested information cannot be found, clearly tell the user.

Return the information obtained from the MCP tool clearly and
concisely.
""",
    tools=[employee_mcp_toolset],
)

