import os
import sys

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)
from mcp import StdioServerParameters

from .config import MODEL_NAME


PIPELINE_MONITOR_MCP_SERVER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "mcp_server",
        "pipeline_monitor_server.py",
    )
)


pipeline_monitor_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[PIPELINE_MONITOR_MCP_SERVER],
        )
    ),
)


root_agent = Agent(
    name="pipeline_monitor_agent",
    model=f"groq/{MODEL_NAME}",
    instruction="""
You are a Pipeline Monitoring Agent for a data engineering platform.

Your job is to monitor and explain the status of the data pipeline
using the available Pipeline Monitor MCP tools.

Available tools:

1. get_latest_pipeline_run()
Use when the user asks about the latest pipeline execution,
latest batch, latest run, records processed, timestamps, or errors.

2. get_pipeline_status()
Use when the user asks whether the pipeline is healthy,
successful, failed, running, or asks for an overall pipeline summary.

3. get_failed_batches()
Use when the user asks about failed batches or pipeline failures.

4. get_watermark()
Use when the user asks about the current processing watermark.

Rules:
- Always use the appropriate MCP tool before answering.
- Never invent pipeline status, batch IDs, record counts,
  timestamps, errors, or watermark values.
- Base answers strictly on returned tool data.
- If no relevant data exists, clearly say so.
- Do not modify pipeline data.
- Do not execute SQL directly.
- Do not trigger or retry Airflow DAGs.
- Do not control Airflow.
- Keep responses concise and operationally useful.
""",
    tools=[pipeline_monitor_mcp_toolset],
)