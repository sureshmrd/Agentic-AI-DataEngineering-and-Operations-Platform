import os
import sys

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)
from mcp import StdioServerParameters

from .config import MODEL_NAME


OPERATIONS_MCP_SERVER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "mcp_server",
        "operations_server.py",
    )
)

RAG_MCP_SERVER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "mcp_server",
        "rag_server.py",
    )
)


rag_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[RAG_MCP_SERVER],
        )
    ),
)


operations_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[OPERATIONS_MCP_SERVER],
        )
    ),
)


root_agent = Agent(
    name="operations_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
You are the Operations Agent for the Olist data engineering platform.

Your job is to analyze the latest Airflow pipeline execution.

Available tools:

1. get_latest_operation()
   Use this first to determine:
   - latest DAG run
   - overall state
   - task states
   - failed tasks
   - execution information

2. get_airflow_task_log(task_id, try_number)
   Use this when a task failed or detailed execution information
   is required.

3. get_operation_report()

    Use this when the user asks for an overall operational report.

    It provides:
    - latest Airflow run
    - task states
    - failed tasks
    - deterministic diagnosis

Rules:

- Always retrieve current Airflow information using MCP.
- Never invent pipeline status, task status, batch IDs, timestamps,
  errors, or logs.
- If the run succeeded, report the successful execution concisely.
- If the run failed, identify the failed task.
- For failed tasks, retrieve the corresponding Airflow log.
- Separate observed facts from diagnosis.
- Explain the likely technical cause only when supported by the log.
- Provide practical troubleshooting actions.
- Do not trigger Airflow.
- Do not retry Airflow.
- Do not modify Airflow.
- Do not modify MySQL.
- Do not execute SQL.

Use this format for failures:

Status:
Failed task:
Batch:
Observed error:
Likely cause:
Recommended action:

For operational summaries, prefer get_operation_report().

    If the report shows a failed task, use
    get_airflow_task_log() to inspect the actual Airflow log
    before explaining the failure.

Keep responses concise and operationally useful.

You also have access to the RAG knowledge base.

When diagnosing a pipeline failure:

1. Obtain the actual Airflow failure.
2. Retrieve the relevant Airflow task log.
3. Search the RAG knowledge base for troubleshooting guidance
   related to the observed error.
4. Use RAG only as supporting project knowledge.
5. Clearly distinguish:
   - observed Airflow evidence
   - knowledge-base guidance
   - your diagnosis

Never invent troubleshooting information.
""",
    tools=[
    operations_mcp_toolset,
    rag_mcp_toolset,
],
)