# Agentic AI + Data Engineering Project — RAG Agent Context

We are continuing an existing project at:

```text
D:\agentic-ai-adk
```

The project combines:

- Python
- PySpark
- MySQL
- Apache Airflow
- Google ADK
- MCP
- FastAPI
- Groq LLM
- RAG
- Agentic orchestration

The goal is to build a realistic end-to-end Agentic AI + Data Engineering platform around the Olist Brazilian E-Commerce dataset.

---

# 1. Existing Architecture

We have already completed two specialist agents.

## Business Query Agent

Flow:

```text
User
 ↓
Business Query Agent
 ↓
MCP
 ↓
FastAPI
 ↓
MySQL Analytics Tables
 ↓
Business Answer
```

Business Agent is used for questions such as:

```text
What was the revenue in September 2016?
Which category generated the highest revenue?
Who are the top sellers?
What is the average order value?
```

It uses only analytical MySQL tables:

```text
monthly_sales_summary
category_performance
seller_performance
```

Business Agent is already working and tested.

Do NOT redesign or modify it unnecessarily.

---

# 2. Pipeline Monitor Agent

This is also already implemented and working.

Its purpose is interactive monitoring of pipeline execution state.

Flow:

```text
User
 ↓
Pipeline Monitor Agent
 ↓
MCP
 ↓
FastAPI
 ↓
MySQL pipeline metadata
 ↓
Answer
```

Current FastAPI port:

```text
8003
```

ADK Web:

```text
8002
```

The Pipeline Monitor API exposes:

```text
GET /pipeline/latest
GET /pipeline/status
GET /pipeline/failed
GET /pipeline/watermark
```

The Pipeline Monitor MCP server calls FastAPI using `httpx`.

The agent uses the same ADK/MCP architecture and launch pattern as the Business Agent.

The Pipeline Monitor Agent is read-only.

It observes:

```text
pipeline_batches
pipeline_watermarks
```

It does NOT:

- trigger Airflow
- retry Airflow
- modify pipeline metadata
- execute Spark
- modify Airflow state

It answers questions such as:

```text
Did the latest pipeline run succeed?
What was the latest batch?
How many records were processed?
Were there failed batches?
What is the current watermark?
```

Again, do NOT redesign this agent.

---

# 3. Actual Data Engineering Pipeline

The project contains a real incremental PySpark + Airflow pipeline.

Flow:

```text
Olist Dataset
 ↓
One-time batch generation
 ↓
Monthly batch files
 ↓
Airflow
 ↓
PySpark Pipeline
 ↓
Validation / Transformation
 ↓
MySQL
 ↓
Analytics + Pipeline Metadata
```

Airflow runs in WSL.

Environment:

```text
Ubuntu 22.04
Python 3.10.6
Airflow 3.3.1
Java 17
PySpark 4.0.1
```

Windows environment contains:

```text
Python 3.14.7
Google ADK 2.8.0
MCP 1.29.1
PySpark 4.0.1
MySQL 8.0.42
```

The Airflow environment is separate from the Windows Agent environment.

Airflow does NOT use ADK or MCP.

---

# 4. Airflow DAG

DAG:

```text
airflow/dags/olist_incremental_pipeline.py
```

Current flow:

```text
find_next_batch
      ↓
run_pipeline
      ↓
verify_batch
```

The PySpark pipeline records execution information into:

```text
pipeline_batches
pipeline_watermarks
```

Current Airflow setup is manually triggerable.

The pipeline has already been successfully tested.

---

# 5. MySQL Tables

Core:

```text
customers
orders
order_items
products
sellers
order_payments
product_category_translation
```

Pipeline metadata:

```text
pipeline_batches
pipeline_watermarks
```

Analytics:

```text
monthly_sales_summary
category_performance
seller_performance
```

Important pipeline metadata:

```text
pipeline_batches (
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
)
```

```text
pipeline_watermarks (
    pipeline_name,
    source_name,
    watermark_column,
    last_processed_value,
    updated_at
)
```

---

# 6. Fixed Agent/File Architecture

We follow this naming convention and should continue it.

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

Do NOT invent a completely different architecture for RAG.

The RAG Agent should follow the same conceptual pattern:

```text
Agent
 ↓
MCP Toolset
 ↓
MCP Server
 ↓
FastAPI
 ↓
RAG / Knowledge Layer
```

---

# 7. RAG Agent Objective

Now we are starting:

```text
M7 — RAG Agent
```

The RAG Agent should handle unstructured/project knowledge rather than business numerical analytics.

Examples:

```text
What does the orders table represent?
What does gross_revenue mean?
How does the incremental pipeline work?
What happens when a batch fails?
What is the purpose of pipeline_watermarks?
How is the Olist pipeline structured?
What should an operator check when the pipeline fails?
```

The RAG layer should eventually contain knowledge such as:

- project documentation
- architecture documentation
- data dictionary
- schema documentation
- metric definitions
- pipeline documentation
- Airflow documentation
- troubleshooting guides
- runbooks
- incident documentation
- operational procedures

---

# 8. Important RAG Design Principle

Do NOT send the entire knowledge base to the LLM.

The intended flow is:

```text
User Question
      ↓
RAG Agent
      ↓
MCP Tool
      ↓
FastAPI
      ↓
Retriever
      ↓
Relevant Documents / Chunks
      ↓
RAG Agent / LLM
      ↓
Grounded Answer
```

The LLM should receive only the relevant retrieved context.

Answers should be grounded in retrieved project knowledge.

If the required information is not present in the knowledge base, the agent should explicitly say that the available knowledge does not contain enough information rather than inventing an answer.

---

# 9. RAG Technology Decision

Before implementing code, first inspect the existing project and determine the simplest appropriate local RAG architecture.

We need to decide:

- document storage
- chunking
- embeddings
- vector store
- retrieval
- metadata
- indexing/update process
- FastAPI endpoints
- MCP tools
- ADK Agent behavior

Do not introduce unnecessary infrastructure.

Prefer a lightweight local solution appropriate for this project.

Do not assume a vector database such as Pinecone/Weaviate/etc. is required.

We should evaluate whether a local vector store is sufficient.

---

# 10. RAG Architecture Should Remain Independent

The RAG Agent should not directly access MySQL.

It should use its MCP/FastAPI layer.

Preferred structure:

```text
my_agent/rag_agent.py
        ↓
mcp_server/rag_server.py
        ↓
api_server/rag_server.py
        ↓
RAG retrieval layer
        ↓
Knowledge Base
```

The RAG layer can later contain separate modules if required, for example:

```text
rag/
├── documents/
├── ingestion.py
├── chunking.py
├── embeddings.py
├── retrieval.py
└── config.py
```

But do not create unnecessary files until the design requires them.

---

# 11. Existing MCP/ADK Versions

Windows Agent environment:

```text
Google ADK 2.8.0
MCP 1.29.1
```

Correct FastMCP import:

```python
from mcp.server.fastmcp import FastMCP
```

The working Business Agent currently uses:

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)
from mcp import StdioServerParameters
```

Follow the working project pattern rather than unnecessarily migrating import paths.

---

# 12. Important Existing API Ports

Current setup:

```text
FastAPI Business/Pipeline Monitor app → port 8003
ADK Web → port 8002
```

The Pipeline Monitor MCP server points to:

```text
http://127.0.0.1:8003
```

Keep this architecture consistent for RAG unless there is a concrete reason to separate services.

---

# 13. RAG Agent Expected Behavior

The RAG Agent should:

- use the RAG MCP tools
- retrieve relevant context before answering knowledge questions
- answer only from retrieved/project knowledge
- avoid hallucinating missing information
- mention when retrieved context is insufficient
- provide concise grounded explanations
- not execute arbitrary SQL
- not modify pipeline state
- not trigger Airflow
- not directly control other agents

---

# 14. Testing Requirements

Before declaring M7 complete, test:

### Retrieval

```text
Can it retrieve relevant project documentation?
```

### Grounding

```text
Does the answer actually reflect retrieved content?
```

### Unknown information

```text
What happens when the answer is not in the knowledge base?
```

### Irrelevant questions

```text
Does it avoid forcing irrelevant retrieved documents into answers?
```

### Multiple documents

```text
Can it combine relevant information from multiple documents?
```

### Business vs RAG boundary

For example:

```text
"What was revenue in September 2016?"
```

This belongs to Business Query Agent.

Whereas:

```text
"What does gross_revenue represent?"
```

belongs to RAG.

The eventual Root Orchestrator will make this routing decision, but M7 should focus only on the standalone RAG Agent.

---

# 15. Future Operations Feature

There is also a planned operational capability separate from the current Pipeline Monitor Agent.

The current Pipeline Monitor Agent provides interactive information from MySQL.

We additionally want:

```text
Airflow
 ↓
Detect success/failure
 ↓
Operational Alerting
 ↓
Email
 ↓
Operations Person
```

The email should use actual Airflow execution/log information rather than only MySQL metadata.

For failures it should eventually include:

- DAG
- run ID
- failed task
- batch
- timestamps
- relevant error
- relevant Airflow log/traceback

The deterministic alerting itself should preferably be implemented in Airflow rather than as an LLM agent.

Later, an Operations/Incident Agent may use:

```text
Airflow Logs
+
Pipeline Metadata
+
RAG Runbooks
```

to diagnose failures and recommend corrective actions.

This feature should not disturb Business Agent or Pipeline Monitor Agent.

---

# 16. Development Order

Current status:

```text
M1 DB Foundation             COMPLETE
M2 Semantic Layer            COMPLETE
M3 MCP Capability            COMPLETE
M4 Business Query Agent      COMPLETE
M5 Business Evaluation       COMPLETE
M6 Pipeline Monitor Agent    COMPLETE
M7 RAG Agent                 CURRENT
M8 Root Orchestrator         AFTER RAG
M9 Final Integration         AFTER Orchestrator
M10 End-to-End Evaluation    FINAL
```

Start M7 by inspecting the existing project structure and deciding the RAG knowledge/retrieval architecture.

Do not restart completed components.

Do not redesign Business Agent or Pipeline Monitor Agent.

Do not jump to Root Orchestrator yet.

Keep responses concise and implementation-focused because the project is being developed incrementally.