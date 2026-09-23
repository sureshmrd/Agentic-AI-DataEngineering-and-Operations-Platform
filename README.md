# Agentic AI Data Engineering & Operations Platform

End-to-end Agentic AI + Data Engineering platform combining PySpark,
Apache Airflow, MySQL, Google ADK, MCP, RAG and Groq LLMs around the
Olist Brazilian E-Commerce dataset.

<img width="2172" height="724" alt="project-banner" src="https://github.com/user-attachments/assets/aa8d6a21-c658-4d91-800b-287d99d1d963" />


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
###### ===================================================================================================================================

# Agents

The platform is composed of specialized agents, with each agent responsible for a specific type of business or technical task.

```text
                         ┌──────────────────────┐
                         │   Root Orchestrator  │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐       ┌───────────────┐      ┌──────────────┐
      │ RAG Agent   │       │ Business Query│      │ Pipeline     │
      │             │       │ Agent         │      │ Monitor Agent│
      └─────────────┘       └───────────────┘      └──────────────┘
             ▲
             │
      ┌──────┴───────┐
      │ Operations   │
      │ Agent        │
      └──────────────┘
```

---

## 1. RAG Agent

### Problem Statement

Business users and technical personnel often need to understand different aspects of an application, but the required information is typically distributed across multiple documents such as architecture documents, pipeline documentation, incident reports, troubleshooting guides, policies, data documentation, and solution guides.

The objective was to build an internal **Knowledge Retrieval Agent** that can understand this heterogeneous knowledge base and provide accurate answers to both technical and non-technical users using natural language. The agent should also assist technical users by retrieving relevant troubleshooting information and documented solutions whenever an application or pipeline issue occurs.

### Result

The **RAG Agent** provides a grounded knowledge-retrieval interface for both technical and non-technical users.

It supports project knowledge across:

- Application Architecture
- Data
- Pipelines
- Incidents
- Solutions
- Policies
- Runbooks
- Troubleshooting

The knowledge base supports `.md`, `.pdf`, and other configured document types.

The ingestion pipeline uses **SHA-256 content hashing** to detect new, modified, and unchanged documents. Unchanged documents are skipped, while modified documents are reprocessed.

Documents are split into meaningful chunks using `RecursiveCharacterTextSplitter`, with metadata maintained for source traceability.

Chunks are converted into vector embeddings using **Sentence Transformers** with:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embeddings are stored in a persistent **ChromaDB** vector database and retrieved using semantic similarity with cosine distance.

The vector index is synchronized with the document repository by removing obsolete chunks and documents deleted from the filesystem.

### Architecture

```text
documents/
     │
     ▼
┌──────────────────┐
│    Ingestion     │
│                  │
│ Discover         │
│ Extract          │
│ Hash             │
│ Chunk            │
│ Embed            │
│ Synchronize      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     ChromaDB     │
│ Vectors + Text   │
│ + Metadata       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    RAG Agent     │
│ Query Embedding  │
│ Semantic Search  │
│ Context Retrieval│
└────────┬─────────┘
         │
         ▼
   Relevant Context
         │
         ▼
        LLM
         │
         ▼
   Grounded Answer
```

### Key Features

- Incremental document ingestion
- SHA-256 change detection
- Markdown and PDF ingestion
- Recursive document chunking
- Sentence Transformer embeddings
- Persistent ChromaDB storage
- Cosine-distance semantic search
- Configurable `top_k` retrieval
- Relevance threshold filtering
- Source metadata and traceability
- Obsolete chunk cleanup
- Deleted-document cleanup
- Full-document retrieval by `doc_id`

### Core Retrieval Flow

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
ChromaDB Similarity Search
      │
      ▼
Candidate Chunks
      │
      ▼
Distance Filtering
      │
      ▼
Relevant Context
      │
      ▼
LLM
      │
      ▼
Grounded Response
```

---

## 2. Business Query Agent

### Problem Statement

Business-end users often need business information such as sales, orders, revenue, freight, category performance, and seller performance, but may not have the technical knowledge to write complex SQL queries. The goal is to provide them with a simple Natural Language interface to query available business data without requiring SQL expertise.

### Result

The `business_query_agent` enables business users to query the available business analytics data using Natural Language. The agent dynamically fetches the current database schema, uses the schema and defined business metrics to generate appropriate SQL, validates and parses the SQL using SQLGlot, and executes it through secured MCP tools and the FastAPI/database layer.

The agent provides grounded responses based only on the returned database results and handles ambiguity and SQL failures safely. The execution layer enforces read-only SQL, allowed-table validation, query timeout, row limits, and audit logging.

Thus, the Business Query Agent provides an end-to-end Agentic AI interface that allows non-technical business users to understand and query business data using simple Natural Language while maintaining controlled SQL execution and security safeguards.

### Architecture

```text
┌──────────────────────────────┐
│       User Question          │
│   Natural Language Query     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Business Query Agent     │
│   Schema + Metrics + SQL     │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          MCP Layer           │
│       Controlled Tools       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         FastAPI              │
│     Service Endpoints        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Database Service Layer   │
│ SQL Validation / Execution   │
│ Limits / Timeouts / Audit    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          MySQL               │
│ Business & Analytical Data   │
└──────────────────────────────┘
```

### Working Flow

```text
Natural Language Question
          │
          ▼
Business Query Agent
          │
          ▼
Retrieve Current Schema
          │
          ▼
Apply Business Metrics / Rules
          │
          ▼
Generate Read-Only SQL
          │
          ▼
Validate SQL
          │
          ▼
Execute Through MCP / FastAPI
          │
          ▼
Retrieve Database Results
          │
          ▼
Grounded Business Response
```

### Dynamic Schema Discovery

```text
MySQL INFORMATION_SCHEMA
          │
          ▼
Business Database Service
          │
          ▼
FastAPI /business/schema
          │
          ▼
MCP Tool
          │
          ▼
Business Query Agent
          │
          ▼
SQL Generation
```

### Business Metrics

Business-specific definitions and rules are maintained in:

```text
config/metrics.yaml
```

### Security and Reliability

- Read-only SQL execution
- SQL parsing and validation using **SQLGlot**
- Allowed-table validation
- Destructive SQL blocking
- Query timeouts
- Row limits
- Audit logging
- Read-only database access
- Bounded retries
- Ambiguity handling
- Safety and edge-case evaluation

The agent provides:

```text
Natural Language
      ↓
Controlled SQL
      ↓
Database Results
      ↓
Grounded Response
```

---

## 3. Pipeline Monitor Agent

### Problem Statement

Business end users often need visibility into data pipeline execution to understand whether data processing is progressing successfully. However, due to access restrictions and organizational policies, they may not have direct access to technical monitoring systems such as Airflow logs.

The objective is therefore to provide a business-friendly interface that allows users to understand the **overall pipeline status** without exposing unnecessary technical details. The agent should answer questions such as:

* Which pipeline failed?
* When did the pipeline last fail or succeed?
* What is the status of the latest batch?
* Were any batches unsuccessful?
* What was the batch ID and how many records were processed?
* What is the next expected batch or watermark?

The intention is **not to replace technical troubleshooting or expose detailed application logs**, but to provide sufficient operational visibility so that business users can participate effectively in pipeline-related communication.

### Result

The **Pipeline Monitor Agent** provides a natural-language interface for obtaining a business-oriented overview of pipeline execution.

Instead of directly depending on Airflow logs, the agent retrieves the latest pipeline execution information from dedicated **MySQL metadata tables**, which are updated whenever the data pipeline executes. The primary metadata sources are:

* `pipeline_batches` — stores batch-level execution information such as batch ID, processing statistics, status, and error information.
* `pipeline_watermarks` — maintains watermark information used to track the progress and upcoming data-processing boundaries.

The agent exposes these capabilities through **MCP tools** and converts the retrieved metadata into a concise, business-friendly status summary.

For business users, it provides visibility into **what happened and the current status** without requiring access to technical monitoring systems. For technical users, it can also serve as a quick **pipeline status checker** before deeper investigation through Airflow logs and application-level monitoring.

Primary metadata sources:

```text
pipeline_batches
    ├── batch_id
    ├── status
    ├── processing statistics
    └── error information

pipeline_watermarks
    ├── processing progress
    └── next data boundary
```

The agent exposes these capabilities through MCP tools and converts the retrieved metadata into concise, business-friendly responses.

### Architecture

```text
┌──────────────────────────────┐
│ Business / Technical User    │
│     Natural Language         │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│    Pipeline Monitor Agent    │
│ Business-Friendly Interpreter│
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          MCP Tools           │
│   Pipeline Metadata Access   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      MySQL Metadata DB       │
│ pipeline_batches             │
│ pipeline_watermarks          │
└──────────────┬───────────────┘
               ▲
               │
┌──────────────┴───────────────┐
│      Data Pipeline / Airflow │
│   Populates execution data   │
└──────────────────────────────┘
```

### Typical Information Returned

- Pipeline status
- Last successful run
- Last failed run
- Batch ID
- Records processed
- Records ingested
- Records failed
- Error summary
- Failed batch details
- Next batch information
- Watermark information

### Core Flow

```text
Natural Language Pipeline Question
              │
              ▼
      Pipeline Metadata
              │
              ▼
    Business-Friendly Summary
```

---

## 4. Operations Agent

### Problem Statement
The Operations Agent is designed to behave like a **Junior Technical Associate** within the data engineering team. Its responsibility is not limited to reporting pipeline status; it should retrieve and understand the complete execution details of an Airflow pipeline, investigate failures, diagnose issues based on available evidence, and provide practical resolution guidance.

Whenever a pipeline execution completes, the agent should be able to understand whether the run succeeded or failed, identify the affected task when applicable, retrieve the corresponding Airflow logs, analyze the error, and structure the findings into a clear operational report.

For recurring or known issues, the agent can additionally use the **RAG Agent** to search relevant technical documentation and previously indexed knowledge to identify potential solutions or troubleshooting steps.

The agent also automates operational communication by preparing the execution report using a predefined email format and sending it to the operator configured for the respective DAG.

### Result

The **Operations Agent** acts as a technical operations assistant for Airflow pipeline executions.

Whenever an Airflow DAG completes, the configured DAG task invokes the Operations Agent through a **FastAPI endpoint**. The agent retrieves the pipeline execution details and relevant Airflow logs through **MCP tools**, analyzes the execution, and generates a structured report.

For successful executions, it provides a concise execution summary. For failed executions, it identifies the failed task, retrieves the corresponding Airflow log, separates observed facts from diagnosis, and determines the likely technical cause only when supported by the available evidence.

For troubleshooting, the agent can delegate to the **RAG Agent**, which searches the relevant technical documentation and embedded knowledge to identify applicable resolution steps. The Operations Agent then structures the findings and suggested actions into an operational report and sends the formatted report to the DAG-configured operator.

Unlike the **Pipeline Monitor Agent**, which is primarily designed to provide business-friendly pipeline visibility, the Operations Agent is designed to perform **technical investigation and resolution assistance**.

### Architecture

```text
┌──────────────────────────────┐
│         Airflow DAG          │
│     Manual / Scheduled Run   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        DAG Task / Hook       │
│     Calls FastAPI Endpoint   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Operations Agent        │
│         Google ADK           │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────────┐
│  MCP Tools   │  │    RAG Agent     │
│ DAG / Task   │  │ Technical Docs   │
│ Run / Logs   │  │ & Knowledge      │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   │
┌──────────────┐           │
│ Airflow Logs │           │
│ Errors       │           │
│ Task Details │           │
└──────┬───────┘           │
       │                   │
       └─────────┬─────────┘
                 ▼
┌──────────────────────────────┐
│      Analysis & Diagnosis    │
│                              │
│ Success / Failure            │
│ Failed Task                  │
│ Observed Evidence            │
│ Technical Diagnosis          │
│ Possible Resolution          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Structured Report       │
│                              │
│ Status / Failed Task         │
│ Error / Diagnosis            │
│ Suggested Actions            │
│ Next Steps                   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Formatted Email        │
│    DAG-configured Operator   │
└──────────────────────────────┘
```

### Investigation Flow

```text
Airflow DAG Completion
          │
          ▼
Operations Agent Trigger
          │
          ▼
Retrieve Execution Details
          │
          ▼
       Success?
      /             YES          NO
     │            │
     ▼            ▼
  Summary    Identify Failed Task
                  │
                  ▼
           Retrieve Airflow Logs
                  │
                  ▼
            Analyze Evidence
                  │
                  ▼
          Evidence-Based Diagnosis
                  │
                  ▼
             Query RAG Agent
                  │
                  ▼
        Troubleshooting Guidance
                  │
                  ▼
           Structured Report
                  │
                  ▼
                 Email
```

### Key Features

- Retrieves Airflow DAG, task, run, and log information through MCP tools.
- Does not invent pipeline status, task status, batch IDs, timestamps, errors, or log information.
- Provides concise summaries for successful executions.
- Identifies failed tasks for unsuccessful runs.
- Retrieves and analyzes relevant Airflow logs.
- Separates **observed facts** from **diagnosis**.
- Produces technical diagnosis only when supported by available evidence.
- Uses the **RAG Agent** for documented troubleshooting and resolution guidance.
- Provides practical next steps.
- Generates a predefined operational report.
- Sends the report to the operator configured in the Airflow DAG.


###### ===================================================================================================================================

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
