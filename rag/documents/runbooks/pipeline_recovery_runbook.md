# Pipeline Recovery Runbook

## Purpose

This runbook describes the general procedure for investigating and
recovering from a failed pipeline batch.

## Step 1 - Identify the Failure

Identify:

- DAG
- Run ID
- Failed task
- Batch ID
- Failure timestamp
- Error message

## Step 2 - Inspect Logs

Review the relevant Airflow task logs and execution information.

Where applicable, inspect PySpark and downstream processing logs.

## Step 3 - Determine Root Cause

Classify the failure before taking corrective action.

Potential causes include:

- Invalid source data
- Duplicate records
- Transformation errors
- Database errors
- Infrastructure or runtime failures

## Step 4 - Correct the Root Cause

Apply the appropriate correction through the responsible system or team.

Do not modify pipeline state simply to hide a failure.

## Step 5 - Validate Recovery

After correction, verify that the affected batch completes successfully and
that the resulting pipeline metadata is consistent.

## Operational Safety

The RAG Agent can explain this runbook but does not directly retry Airflow
or modify pipeline state.