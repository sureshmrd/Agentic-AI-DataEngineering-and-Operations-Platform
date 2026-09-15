# Data Access Policy

## Purpose

This policy defines the intended access boundaries of the Olist Agentic Data
Platform.

## Business Data

Business analytical data is accessed through the Business Query Agent.

The Business Query Agent uses approved analytical MySQL tables through its
FastAPI and MCP interfaces.

## Pipeline Metadata

Pipeline metadata is accessed through the Pipeline Monitor Agent.

The Pipeline Monitor Agent is read-only.

## Project Knowledge

Project documentation is accessed through the RAG Agent.

The RAG Agent retrieves information from the project knowledge base.

## Access Restrictions

The RAG Agent must not directly query MySQL.

The RAG Agent must not execute arbitrary SQL.

The RAG Agent must not trigger Airflow.

The RAG Agent must not modify pipeline metadata.

The Pipeline Monitor Agent must not modify Airflow state.

## Principle

Each agent should access only the capability required for its responsibility.