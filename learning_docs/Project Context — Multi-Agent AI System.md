I am building a production-oriented multi-agent AI system using **Google ADK + MCP + FastAPI + MySQL + Groq LLM**.

IMPORTANT: Keep responses concise. Do not unnecessarily elaborate because chat/token limits matter. Give implementation steps/code directly.

## PROJECT GOAL

Build specialist agents independently, evaluate each one, then create a Root Orchestrator that routes user requests to the correct specialist.

## FIXED PROJECT STRUCTURE / NAMING

Use this naming convention for ALL agents:

```text
api_server/
├── server.py
├── business_server.py
├── pipeline_monitor_server.py
└── rag_server.py

mcp_server/
├── server.py
├── business_server.py
├── pipeline_monitor_server.py
└── rag_server.py

my_agent/
├── mcp_agent.py
├── business_agent.py
├── pipeline_monitor_agent.py
├── rag_agent.py
└── agent.py
```

`my_agent/agent.py` will eventually be the Root Orchestrator.

DO NOT change this naming convention.

## CURRENT ARCHITECTURE

Business Agent example:

```text
User
 ↓
Google ADK Business Agent
 ↓ MCP / stdio
mcp_server/business_server.py
 ↓ HTTP
api_server/business_server.py
 ↓
api_server/business_database.py
 ↓
MySQL
```

MCP is launched by ADK using `McpToolset` + `StdioServerParameters`.

FastAPI runs separately:

```cmd
python -m uvicorn api_server.server:app --reload --port 8001
```

ADK Web runs separately:

```cmd
adk web
```

FastAPI uses port 8001.

## VERSIONS / IMPORTANT FIX

Google ADK = 2.8.0

MCP must use:

```text
mcp==1.29.1
```

Correct MCP FastMCP import:

```python
from mcp.server.fastmcp import FastMCP
```

NOT:

```python
from fastmcp import FastMCP
```

Correct ADK MCP imports:

```python
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
)
from mcp import StdioServerParameters
```

## BUSINESS QUERY AGENT — COMPLETED

Business Agent is complete through M1–M5.

### M1 — DB + SQL Foundation

Implemented in:

```text
api_server/business_database.py
```

Implemented:

- MySQL DB connection
- SQLGlot parsing
- single SQL statement validation
- SELECT / WITH SELECT validation
- allowed-table validation
- destructive SQL blocking
- automatic LIMIT
- MAX_EXECUTION_TIME
- fetchmany row limit
- audit logging

SQLGlot is used to parse and inspect the SQL AST:

```python
sqlglot.parse(sql, read="mysql")
```

and:

```python
statement.find_all(exp.Table)
statement.find_all(exp.Select)
statement.find_all(exp.Limit)
```

Read-only DB user is intentionally postponed for later hardening.

Audit logs are written to:

```text
logs/business_queries.log
```

### M2 — Semantic Layer

Dynamic schema discovery is implemented.

Schema should NOT be hardcoded because DB columns can change.

Flow:

```text
MySQL INFORMATION_SCHEMA
 ↓
business_database.py
 ↓
FastAPI /business/schema
 ↓
MCP get_business_schema()
 ↓
Business Agent
```

Business metric definitions are maintained separately in:

```text
config/metrics.yaml
```

Examples:

```yaml
metrics:
  gross_revenue:
    definition: "Sum of order item prices"
    source: "monthly_sales_summary.gross_revenue"

  total_freight:
    definition: "Sum of freight charges"
    source: "monthly_sales_summary.total_freight"

  average_order_value:
    definition: "Gross revenue divided by distinct orders"
    source: "monthly_sales_summary.average_order_value"
```

Schema metadata is dynamic; metric definitions are controlled configuration.

### M3 — MCP

Business MCP exposes:

```text
get_business_schema()
execute_read_only_sql(sql)
```

`execute_read_only_sql()` calls FastAPI:

```text
POST /business/query
```

### M4 — Business Agent

`my_agent/business_agent.py` uses Google ADK Agent + MCP toolset.

NL → SQL is performed by the LLM based on the schema and instructions.

Tool invocation is handled by ADK/MCP.

Flow:

```text
User question
 ↓
LLM
 ↓
get_business_schema()
 ↓
LLM generates SQL
 ↓
execute_read_only_sql(sql)
 ↓
FastAPI
 ↓
MySQL
 ↓
result
 ↓
LLM grounded final answer
```

Business Agent instruction includes:

- call schema first
- generate SQL from current schema
- execute only through MCP
- maximum 2 SQL execution attempts
- do not retry identical SQL
- only SELECT/WITH SELECT
- no destructive operations
- answer only from returned data
- don't invent values/trends/rankings
- ask clarification for ambiguous questions
- report empty results explicitly

### M5 — Evaluation

Tested successfully:

- monthly revenue
- monthly freight
- average order value
- category performance
- seller performance
- ranking/comparison
- ambiguous questions
- INSERT/UPDATE/DELETE/DROP safety
- out-of-scope questions
- grounded responses

Business Query Agent is considered COMPLETE.

## DEVELOPMENT PLAN

We work specialist-by-specialist.

Current status:

```text
M1 DB Foundation             COMPLETE
M2 Semantic Layer            COMPLETE
M3 MCP Capability            COMPLETE
M4 Business Query Agent      COMPLETE
M5 Business Evaluation       COMPLETE

M6 Pipeline Monitor Agent    NEXT
M7 RAG Agent                 AFTER M6
M8 Root Orchestrator         AFTER M6 + M7
M9 Final Integration         AFTER M8
M10 End-to-End Evaluation    FINAL
```

DO NOT jump to Root Orchestrator now.

## NEXT AGENT — PIPELINE MONITOR

Build independently using the same pattern:

```text
api_server/pipeline_monitor_server.py
mcp_server/pipeline_monitor_server.py
my_agent/pipeline_monitor_agent.py
```

Use the same development philosophy:

1. Data/API foundation
2. Deterministic monitoring tools
3. MCP capability
4. ADK Pipeline Monitor Agent
5. Evaluation
6. Only after successful evaluation move to RAG

Potential deterministic tools:

```text
get_latest_pipeline_run()
get_failed_batches()
get_pipeline_status()
get_watermark()
```

The exact tools can be finalized based on the available pipeline-monitoring data.

## RAG AGENT

After Pipeline Monitor is complete:

```text
api_server/rag_server.py
mcp_server/rag_server.py
my_agent/rag_agent.py
```

RAG should retrieve relevant knowledge and generate grounded answers from retrieved context.

Potential knowledge:

- incident documentation
- runbooks
- project documentation
- sample Confluence-like pages
- GitHub repository information

## ROOT ORCHESTRATOR

Only after all specialist agents pass their own evaluation:

```python
root_agent = Agent(
    name="main_agent",
    model=...,
    instruction="Route each request to the appropriate specialist agent.",
    sub_agents=[
        employee_agent,
        business_query_agent,
        pipeline_monitor_agent,
        rag_agent,
    ],
)
```

Root Agent should delegate to specialists and should NOT directly access MySQL.

## IMPORTANT WORKING RULE

Do not assume a feature is implemented merely because it is in the plan. Always distinguish:

- implemented
- partially implemented
- missing
- tested

When giving implementation instructions, be concise and focus only on the next necessary steps.