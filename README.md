# Agentic AI Data Engineering & Operations Platform

End-to-end Agentic AI + Data Engineering platform combining PySpark,
Apache Airflow, MySQL, Google ADK, MCP, RAG and Groq LLMs around the
Olist Brazilian E-Commerce dataset.

## Architecture

``` mermaid
flowchart TB
    U[User] --> O[Root Orchestrator]
    O --> B[Business Query Agent]
    O --> P[Pipeline Monitor Agent]
    O --> R[RAG Agent]
    O --> X[Operations Agent]
    B --> BMCP[Business MCP]
    P --> PMCP[Pipeline MCP]
    R --> RMCP[RAG MCP]
    X --> XMCP[Operations MCP]
    BMCP --> DB[(MySQL)]
    PMCP --> DB
    RMCP --> KB[(Knowledge Base)]
    XMCP --> AF[Airflow]
    XMCP --> LOG[Airflow Logs]
    OL[Olist] --> BG[Batch Simulation]
    BG --> AF
    AF --> SP[PySpark]
    SP --> DB
    AF --> EM[Email Notification]
```

### Components & Flow

<img width="5187" height="6168" alt="architecture-diagram-2" src="https://github.com/user-attachments/assets/ea3bac74-0555-47c3-aac5-ad0bae564823" />

## Stack

-   Python 3.14.7
-   Google ADK 2.8.0
-   MCP 1.29.1
-   PySpark 4.0.1
-   Apache Airflow 3.3.1
-   MySQL 8.0.42
-   Java 17
-   FastAPI
-   Groq LLM
-   RAG

## Project Structure

``` text
api_server/
mcp_server/
my_agent/
spark_pipeline/
airflow/dags/
operations/
data/raw/
data/batches/
config/
docs/
```

## Data Pipeline

``` text
Olist
  -> Monthly Batch Simulation
  -> Airflow
  -> PySpark
  -> Validate / Transform
  -> MySQL
  -> Analytics + Metadata + Watermarks
```

The Airflow DAG is manually triggered because the project uses a finite
historical batch set.

## Agents

### Business Query Agent

Answers business analytics questions using controlled read-only SQL
against: - monthly_sales_summary - category_performance -
seller_performance

### Pipeline Monitor Agent

Reports actual pipeline state, batches and watermarks through MCP.

### RAG Agent

Retrieves project, schema, metric and troubleshooting knowledge.

### Operations Agent

Investigates Airflow failures using execution data and logs, with RAG as
supporting knowledge.

### Root Orchestrator

Routes by intent: 1. Definitions/documentation -\> RAG 2.
Failure/troubleshooting -\> Operations 3. Pipeline status -\> Pipeline
Monitor 4. Business analytics -\> Business Query

## Incremental Pipeline

``` bash
python -m spark_pipeline.pipeline --batch-id batch_201609
```

Processing:

``` text
Batch -> PySpark -> Validation -> Transformation -> MySQL
      -> Analytics Refresh -> Batch Metadata -> Watermark
```

## Airflow DAG

``` text
find_next_batch
      |
run_pipeline
      |
verify_batch
      |
send_notification
```

Operational notification is deterministic and does not depend on an LLM.

## FastAPI / ADK

``` bash
uvicorn api_server.business_server:app --host 0.0.0.0 --port 8003
adk web --port 8002
```

## Testing

Validated integration boundaries include: - Airflow -\> PySpark -\>
MySQL - FastAPI -\> MCP - MCP -\> Agents - Business Agent -\> MySQL -
Pipeline Monitor -\> MySQL - Operations Agent -\> Airflow/logs - RAG
Agent -\> Knowledge Base - Airflow -\> Email

Representative E2E tests: - revenue query - latest pipeline status -
latest processed batch - metric definition - pipeline failure
investigation - multi-domain business + pipeline request - SQL safety
and agent boundary tests

## Security / Design Principles

-   `.env` contains secrets and must not be committed.
-   Business SQL is read-only.
-   Large raw datasets are not sent to the LLM.
-   Pipeline state comes from authoritative tools.
-   MCP provides controlled tool boundaries.
-   RAG is used for knowledge, not transactional analytics.
-   Specialist agents do not bypass their responsibilities.

## Summary

Built an end-to-end Agentic AI + Data Engineering platform using
PySpark, Apache Airflow, MySQL, Google ADK, MCP, RAG and Groq LLMs.
Implemented incremental Olist e-commerce processing, analytical models,
pipeline monitoring, operational diagnostics, deterministic
notifications and multi-agent orchestration.
