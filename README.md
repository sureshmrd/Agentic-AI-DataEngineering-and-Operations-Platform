# Agentic AI Data Engineering & Operations Platform

End-to-end Agentic AI + Data Engineering platform combining PySpark,
Apache Airflow, MySQL, Google ADK, MCP, RAG and Groq LLMs around the
Olist Brazilian E-Commerce dataset.

<img width="2172" height="724" alt="project-banner" src="https://github.com/user-attachments/assets/aa8d6a21-c658-4d91-800b-287d99d1d963" />

### Intro 



https://github.com/user-attachments/assets/bca7653b-901e-4240-a984-3b3494eb490c


## Problem Statement
This project addresses a common enterprise data and operations problem: business users, application users, and technical/data-engineering teams need information from different enterprise systems, but accessing and interpreting that information typically requires SQL knowledge, application documentation, or direct access to technical monitoring systems.

Business users may need answers about sales, orders, revenue, freight, category performance, and seller performance, but may not have the technical expertise to write SQL queries. Application and business users may also need explanations of application concepts, metrics, schemas, or business terminology that are distributed across internal documentation.

At the same time, data-engineering teams need visibility into Airflow pipeline executions, failed tasks, logs, errors, and possible resolutions. Business users generally should not need access to detailed Airflow logs, while technical operators need deeper diagnostic information when a pipeline fails.

The project therefore aims to build a modular Agentic AI platform that provides a single Natural Language interface while routing each request to a specialized agent capable of interacting with the appropriate enterprise data or knowledge source.

The system addresses four major requirements:

- Business Data Access : Allow non-technical users to query available business data using Natural Language instead of writing SQL.
- Application Knowledge Retrieval : Provide grounded answers about application concepts, metrics, schemas, and internal documentation using RAG.
- Pipeline Visibility : Provide business-friendly information about pipeline execution without requiring users to access Airflow logs.
- Technical Pipeline Operations : Allow technical operations workflows to inspect Airflow execution details, analyze failures, consult technical knowledge, and provide troubleshooting guidance.



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
### Technical Components Flow

<img width="5187" height="6168" alt="architecture-diagram-2" src="https://github.com/user-attachments/assets/1b026835-e7d9-42e1-bbec-75e1dc4d33de" />


## Data Source & Data Model : 
#### => Hybrid Data Model: Normalized Operational/Core Model + Analytical Aggregate Model + Pipeline Metadata Model

### Dataset Overview

This project uses the **Brazilian E-Commerce Public Dataset by Olist**,
a real-world e-commerce dataset containing approximately **100,000
orders** placed between **2016 and 2018**.

The dataset provides a realistic foundation for building an incremental
data engineering and analytics platform because it contains multiple
related business entities such as customers, orders, products, sellers,
order items, and payments.

**Dataset characteristics:**

| Attribute    | Details                                      |
|--------------|----------------------------------------------|
| Dataset      | Brazilian E-Commerce Public Dataset by Olist |
| Source       | Kaggle                                       |
| Approx. Size | 45 MB                                        |
| Orders       | ~100,000                                     |
| Time Period  | 2016 – 2018                                  |
| Format       | CSV                                          |
| Domain       | E-Commerce                                   |
| Primary Use  | Data Engineering, Analytics & Agentic AI     |

### Dataset Scope in This Project

The original Olist dataset contains several related datasets. For this
project, the initial data pipeline focuses on the datasets required for
transactional processing and business analytics.

**Source datasets used:**

``` text
olist_customers_dataset.csv
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```
Reviews and geolocation data are intentionally outside the initial
project scope.

The selected datasets are transformed into three logical layers:

``` text
                    Olist Raw Dataset
                           │
                           ▼
                  ┌─────────────────┐
                  │   Core Tables   │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Analytics    Pipeline      Watermarks
           Tables      Metadata
```
### Raw Dataset → Project Tables

The raw CSV datasets are processed through the PySpark pipeline before
being loaded into MySQL.

``` text
Raw CSV Files
     │
     ▼
Schema Application
     │
     ▼
Data Preparation
     │
     ├── Type conversions
     ├── NULL handling
     ├── Data validation
     └── Transformation
     │
     ▼
Core MySQL Tables
     │
     ├── customers
     ├── orders
     ├── order_items
     ├── order_payments
     ├── products
     ├── sellers
     └── product_category_translation
     │
     ▼
Analytics Transformation
     │
     ├── monthly_sales_summary
     ├── category_performance
     └── seller_performance
```

The pipeline uses explicit Spark schemas rather than relying entirely on
automatic type inference. This provides predictable data types during
processing and loading.

### Data Transformation & Preparation

The PySpark pipeline performs the required preparation and
transformation before data reaches the analytical layer.

Key processing areas include:

- Applying explicit schemas to raw datasets
- Converting source fields into appropriate Spark data types
- Handling nullable fields during processing
- Validating incoming batch data
- Transforming transactional data into analytics-ready structures
- Joining related business entities where required for analytical
  calculations
- Calculating business metrics
- Refreshing analytical tables after successful core-table loading
- Maintaining pipeline execution metadata
- Maintaining processing watermarks

The pipeline processes data incrementally rather than loading the
complete historical dataset on every execution.

``` text
Historical Olist Data
        │
        ▼
Monthly Batch Simulation
        │
        ▼
Airflow
        │
        ▼
PySpark
        │
        ├── Extract
        ├── Transform
        ├── Validate
        └── Load
        │
        ▼
      MySQL
```
### Schema Design

The final MySQL model is organized into three logical layers.

#### Core / Operational Tables

These tables preserve the primary business entities and transactional
relationships.

``` text
customers
orders
order_items
order_payments
products
sellers
product_category_translation
```

Key relationships include:

``` text
customers
    │
    └── 1 : N ── orders
                    │
                    ├── 1 : N ── order_items
                    │                 │
                    │                 ├── N : 1 ── products
                    │                 │
                    │                 └── N : 1 ── sellers
                    │
                    └── 1 : N ── order_payments

products
    │
    └── N : 1 ── product_category_translation
```

#### Pipeline Metadata Tables

These tables track the state of incremental processing.

``` text
pipeline_batches
pipeline_watermarks
```

`pipeline_batches` stores batch execution history, including status,
record counts, timestamps, and errors.

`pipeline_watermarks` stores the latest successfully processed position
for the pipeline.

#### Analytics Tables

These tables provide pre-aggregated, business-ready data for efficient
analytical queries.

``` text
monthly_sales_summary
category_performance
seller_performance
```

This prevents the Business Query Agent from having to repeatedly process
large transactional datasets for common business questions.

### Transformations & Business Metrics

The analytical layer derives business metrics from the transactional
data.

For example:

``` text
gross_revenue
    = SUM(order_items.price)

total_freight
    = SUM(order_items.freight_value)

average_order_value
    = gross_revenue / distinct_orders
```

The analytical tables are refreshed after successful incremental loading
so that they represent the accumulated successfully processed data.

### Data Model Pattern

The project follows a **Hybrid Data Model** consisting of:

``` text
┌──────────────────────────────────────────┐
│        NORMALIZED CORE MODEL             │
│                                          │
│ customers                                │
│ orders                                   │
│ order_items                              │
│ order_payments                           │
│ products                                 │
│ sellers                                  │
│ category translation                     │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│       ANALYTICAL AGGREGATE MODEL         │
│                                          │
│ monthly_sales_summary                    │
│ category_performance                     │
│ seller_performance                       │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│          PIPELINE METADATA               │
│                                          │
│ pipeline_batches                         │
│ pipeline_watermarks                      │
└──────────────────────────────────────────┘
```

This design combines:

- **Normalized operational data** for transactional integrity
- **Aggregated analytical data** for efficient business querying
- **Pipeline metadata** for incremental processing and observability

The Business Query Agent primarily interacts with the analytical layer,
while the Pipeline Monitor Agent uses the pipeline metadata layer.

### Data Model Pattern and Diagram 
The diagram represents the relationship between the operational/core
entities, pipeline metadata, and analytical aggregate tables used
throughout the platform.

``` text
                         ┌─────────────────────┐
                         │      customers      │
                         │─────────────────────│
                         │ PK customer_id      │
                         │   customer_unique_id│
                         │   customer_zip_code │
                         │   customer_city     │
                         │   customer_state    │
                         └──────────┬──────────┘
                                    │
                                    │ 1 : N
                                    ▼
                         ┌─────────────────────┐
                         │       orders        │
                         │─────────────────────│
                         │ PK order_id         │
                         │ FK customer_id      │
                         │    order_status     │
                         │    purchase_ts      │
                         │    approved_ts      │
                         │    delivered_carrier│
                         │   delivered_customer│
                         │   estimated_delivery│
                         └───────┬───────┬─────┘
                                 │       │
                       1 : N     │       │ 1 : N
                                 │       │
                  ┌──────────────┘       └───────────────┐
                  ▼                                      ▼
        ┌─────────────────────┐                ┌─────────────────────┐
        │    order_items      │                │   order_payments    │
        │─────────────────────│                │─────────────────────│
        │ PK/FK order_id      │                │ PK/FK order_id      │
        │ PK order_item_id    │                │ PK payment_seq      │
        │ FK product_id       │                │    payment_type     │
        │ FK seller_id        │                │   installments      │
        │    shipping_limit   │                │    payment_value    │
        │    price            │                └─────────────────────┘
        │    freight_value    │
        └──────────┬──────────┘
                   │
            ┌──────┴──────┐
            │             │
          N : 1         N : 1
            │             │
            ▼             ▼
 ┌────────────────┐  ┌─────────────────────┐
 │    products    │  │       sellers       │
 │────────────────│  │─────────────────────│
 │ PK product_id  │  │ PK seller_id        │
 │ FK category    │  │    zip_code         │
 │    name_length │  │    city             │
 │    description │  │    state            │
 │    photos_qty  │  └─────────────────────┘
 │    weight_g    │
 │    length_cm   │
 │    height_cm   │
 │    width_cm    │
 └───────┬────────┘
         │
         │ N : 1
         ▼
┌────────────────────────────┐
│product_category_translation│
│────────────────────────────│
│ PK product_category_name   │
│    category_name_english   │
└────────────────────────────┘
```
#### Final ERD-Level Model

<img width="1204" height="910" alt="Complete-Data-Model-2" src="https://github.com/user-attachments/assets/343ca55b-5182-4a72-8d7f-aad2298b1331" />



# Specialized Agents Involved in this Agentic Workflow

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

### Complete Project — Solution / Result

The project implements an Agentic AI ecosystem using Google ADK, MCP, FastAPI, MySQL, Airflow, and RAG, where specialized agents collaborate with backend services according to the nature of the user's request.

``` text

                         ┌──────────────────────────┐
                         │        End Users         │
                         │                          │
                         │ Business  │ Application  │
                         │ Technical │ Operations   │
                         └────────────┬─────────────┘
                                      │
                                      │ Natural Language
                                      ▼
                         ┌──────────────────────────┐
                         │     Root / Router Agent  │
                         │                          │
                         │ Understands user intent  │
                         │ and delegates requests   │
                         └────────────┬─────────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
   │ Business Query   │    │    RAG Agent     │    │ Pipeline Monitor │
   │     Agent        │    │                  │    │      Agent       │
   └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
            │                       │                       │
            │                       │                       │
            ▼                       ▼                       ▼
     Business Data            Knowledge Base         Pipeline Metadata
            │                       │                       │
            │                       │                       │
            └───────────────┬───────┴───────────────┬───────┘
                            │                       │
                            ▼                       ▼
                     ┌─────────────┐       ┌──────────────────┐
                     │ MCP Tools   │       │ MySQL Metadata   │
                     │             │       │                  │
                     │ Controlled  │       │ pipeline_batches │
                     │ backend     │       │ pipeline_        │
                     │ capabilities│       │ watermarks       │
                     └──────┬──────┘       └──────────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   FastAPI   │
                     │ API Layer   │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │    MySQL    │
                     │ Business DB │
                     └─────────────┘


       ┌──────────────────────────────────────────────────────┐
       │              Data Engineering Layer                  │
       │                                                      │
       │              Airflow Data Pipeline                   │
       │                                                      │
       │   Source → Extract → Transform → Load → Metadata     │
       │                                  │                   │
       │                                  ▼                   │
       │                     Pipeline Metadata Tables         │
       └──────────────────────────────────────────────────────┘


       ┌──────────────────────────────────────────────────────┐
       │                 Technical Operations                 │
       │                                                      │
       │  Airflow DAG → FastAPI → Operations Agent → MCP      │
       │                              │                       │
       │                              ├── Airflow Logs        │
       │                              │                       │
       │                              └── RAG Agent           │
       │                                      │               │
       │                                      ▼               │
       │                             Technical Knowledge      │
       │                             / Documentation          │
       └──────────────────────────────────────────────────────┘

```

## Copyright

© 2026 Rama Durga Suresh Madagala. All Rights Reserved.

This project, including its original source code, architecture, implementation,
agent workflows, and documentation, was independently designed and developed
by the author.

This repository is published for portfolio, demonstration, and educational
purposes. Third-party libraries, frameworks, models, datasets, and other
external components remain subject to their respective licenses.

For permissions regarding reuse of the original materials in this repository,
please contact the author.
