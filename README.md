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

```
flowchart TD

subgraph group_agents["Agent Orchestration"]
  node_root_orchestrator["Root Orchestrator"]
  node_business_agent["Business Agent<br/>[business_agent.py]"]
  node_monitor_agent["Monitor Agent"]
  node_rag_agent["RAG Agent<br/>[rag_agent.py]"]
  node_operations_agent["Operations Agent"]
end

subgraph group_interfaces["Service Interfaces"]
  node_business_mcp["Business MCP<br/>[business_server.py]"]
  node_monitor_mcp["Monitor MCP"]
  node_rag_mcp["RAG MCP<br/>[rag_server.py]"]
  node_operations_mcp["Operations MCP"]
  node_business_api["Business API<br/>[business_server.py]"]
  node_monitor_api["Monitor API"]
  node_rag_api["RAG API<br/>[rag_server.py]"]
  node_operations_api["Operations API"]
end

subgraph group_pipeline["Data Pipeline"]
  node_batch_simulation["Batch Simulation<br/>[batch_generator.py]"]
  node_airflow_dag["Incremental DAG"]
  node_spark_pipeline["Spark Pipeline<br/>[pipeline.py]"]
  node_validation["Batch Validation<br/>[validate.py]"]
  node_transformation["Data Transformation<br/>[transform.py]"]
  node_mysql_loader["MySQL Loader<br/>[load.py]"]
end

subgraph group_knowledge["Knowledge Operations"]
  node_retrieval["Knowledge Retrieval<br/>[retrieval.py]"]
  node_ingestion["Knowledge Ingestion<br/>[ingestion.py]"]
  node_chunking["Document Chunking<br/>[chunking.py]"]
  node_embeddings["Embeddings<br/>[embeddings.py]"]
  node_airflow_client["Airflow Client<br/>[airflow_client.py]"]
  node_diagnosis["Failure Diagnosis<br/>[diagnosis.py]"]
  node_notifier["Operational Notifier<br/>[notifier.py]"]
end

subgraph group_state["Persistent State"]
  node_mysql[("MySQL<br/>[database.py]")]
  node_vector_store[("Vector Store<br/>[vector_store.py]")]
end

node_user(("User"))
node_olist["Olist Dataset"]
node_airflow["Airflow"]
node_airflow_logs["Airflow Logs"]
node_email["Email Service"]

node_user -->|"submits request"| node_root_orchestrator
node_root_orchestrator -->|"delegates analytics"| node_business_agent
node_root_orchestrator -->|"delegates status"| node_monitor_agent
node_root_orchestrator -->|"delegates knowledge"| node_rag_agent
node_root_orchestrator -->|"delegates failures"| node_operations_agent
node_business_agent -->|"uses tools"| node_business_mcp
node_monitor_agent -->|"uses tools"| node_monitor_mcp
node_rag_agent -->|"uses tools"| node_rag_mcp
node_operations_agent -->|"uses tools"| node_operations_mcp
node_business_mcp -->|"calls API"| node_business_api
node_monitor_mcp -->|"calls API"| node_monitor_api
node_rag_mcp -->|"calls API"| node_rag_api
node_operations_mcp -->|"calls API"| node_operations_api
node_business_api -->|"reads analytics"| node_mysql
node_monitor_api -->|"reads state"| node_mysql
node_rag_api -->|"runs retrieval"| node_retrieval
node_batch_simulation -->|"provides batches"| node_airflow_dag
node_olist -->|"generates batches"| node_batch_simulation
node_airflow_dag -->|"runs pipeline"| node_spark_pipeline
node_spark_pipeline -->|"validates data"| node_validation
node_spark_pipeline -->|"transforms data"| node_transformation
node_spark_pipeline -->|"loads data"| node_mysql_loader
node_mysql_loader -->|"writes state"| node_mysql
node_airflow_dag -->|"requests notification"| node_operations_api
node_operations_api -->|"dispatches notice"| node_notifier
node_notifier -->|"sends email"| node_email
node_operations_api -->|"runs diagnosis"| node_diagnosis
node_diagnosis -->|"queries execution"| node_airflow_client
node_airflow_client -->|"reads REST API"| node_airflow
node_airflow_client -->|"reads logs"| node_airflow_logs
node_ingestion -->|"splits documents"| node_chunking
node_ingestion -->|"embeds chunks"| node_embeddings
node_ingestion -->|"upserts chunks"| node_vector_store
node_retrieval -->|"embeds query"| node_embeddings
node_retrieval -->|"queries vectors"| node_vector_store

click node_root_orchestrator "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/my_agent/orchestrator_agent.py"
click node_business_agent "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/my_agent/business_agent.py"
click node_monitor_agent "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/my_agent/pipeline_monitor_agent.py"
click node_rag_agent "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/my_agent/rag_agent.py"
click node_operations_agent "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/my_agent/operations_agent.py"
click node_business_mcp "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/mcp_server/business_server.py"
click node_monitor_mcp "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/mcp_server/pipeline_monitor_server.py"
click node_rag_mcp "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/mcp_server/rag_server.py"
click node_operations_mcp "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/mcp_server/operations_server.py"
click node_business_api "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/api_server/business_server.py"
click node_monitor_api "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/api_server/pipeline_monitor_server.py"
click node_rag_api "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/api_server/rag_server.py"
click node_operations_api "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/api_server/operations_server.py"
click node_batch_simulation "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/spark_pipeline/batch_generator.py"
click node_airflow_dag "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/airflow/dags/olist_incremental_pipeline.py"
click node_spark_pipeline "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/spark_pipeline/pipeline.py"
click node_validation "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/spark_pipeline/validate.py"
click node_transformation "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/spark_pipeline/transform.py"
click node_mysql_loader "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/spark_pipeline/load.py"
click node_mysql "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/api_server/database.py"
click node_retrieval "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/rag/retrieval.py"
click node_ingestion "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/rag/ingestion.py"
click node_chunking "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/rag/chunking.py"
click node_embeddings "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/rag/embeddings.py"
click node_vector_store "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/rag/vector_store.py"
click node_airflow_client "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/operations/airflow_client.py"
click node_diagnosis "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/operations/diagnosis.py"
click node_notifier "https://github.com/sureshmrd/agentic-ai-dataengineering-and-operations-platform/blob/main/operations/notifier.py"

classDef toneNeutral fill:#f8fafc,stroke:#334155,stroke-width:1.5px,color:#0f172a
classDef toneBlue fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#172554
classDef toneAmber fill:#fef3c7,stroke:#d97706,stroke-width:1.5px,color:#78350f
classDef toneMint fill:#dcfce7,stroke:#16a34a,stroke-width:1.5px,color:#14532d
classDef toneRose fill:#ffe4e6,stroke:#e11d48,stroke-width:1.5px,color:#881337
classDef toneIndigo fill:#e0e7ff,stroke:#4f46e5,stroke-width:1.5px,color:#312e81
classDef toneTeal fill:#ccfbf1,stroke:#0f766e,stroke-width:1.5px,color:#134e4a
class node_root_orchestrator,node_business_agent,node_monitor_agent,node_rag_agent,node_operations_agent,node_user toneBlue
class node_business_mcp,node_monitor_mcp,node_rag_mcp,node_operations_mcp,node_business_api,node_monitor_api,node_rag_api,node_operations_api toneAmber
class node_batch_simulation,node_airflow_dag,node_spark_pipeline,node_validation,node_transformation,node_mysql_loader toneMint
class node_retrieval,node_ingestion,node_chunking,node_embeddings,node_airflow_client,node_diagnosis,node_notifier toneRose
class node_mysql,node_vector_store,node_olist,node_airflow,node_airflow_logs,node_email toneIndigo
```


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
