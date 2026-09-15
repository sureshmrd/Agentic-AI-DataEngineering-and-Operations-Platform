# Olist Agentic Data Platform

## Overview

The project is an Agentic AI and Data Engineering platform built around the
Olist Brazilian E-Commerce dataset.

The platform combines Python, PySpark, MySQL, Apache Airflow, Google ADK,
MCP, FastAPI, Groq LLM, RAG, and agentic orchestration.

The system separates analytical questions, pipeline monitoring, and project
knowledge retrieval into different capabilities.

## Business Query Agent

The Business Query Agent answers numerical and analytical questions.

Examples include:

- Revenue for a period
- Highest revenue category
- Top sellers
- Average order value

The Business Query Agent accesses analytical MySQL tables through MCP and
FastAPI.

## Pipeline Monitor Agent

The Pipeline Monitor Agent provides read-only information about pipeline
execution.

It can retrieve:

- Latest pipeline run
- Pipeline status
- Failed batches
- Pipeline watermarks

It does not trigger or modify Airflow.

## RAG Agent

The RAG Agent handles project and operational knowledge.

Examples include:

- What does the orders table represent?
- What does gross_revenue mean?
- How does the incremental pipeline work?
- What happens when a batch fails?
- What is the purpose of pipeline_watermarks?

The RAG Agent retrieves relevant documentation before generating an answer.

## Service Boundary

The RAG Agent must not directly access MySQL.

The intended flow is:

Agent
    -> MCP
    -> FastAPI
    -> RAG Retrieval
    -> Knowledge Base

The existing Business Query Agent and Pipeline Monitor Agent should remain
independent.