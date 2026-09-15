# Pipeline Failure Guide

## First Check

When a pipeline batch fails, first identify:

- DAG
- Run ID
- Failed task
- Batch ID
- Failure timestamp
- Error message

The actual Airflow execution and task log should be inspected for the
underlying failure.

## Duplicate Records

A possible pipeline failure can occur when duplicate upstream records violate
the expected uniqueness constraint.

One known example involved duplicate records for the combination:

study_code_alias
country_code
study_subject_eid
visit_name

The duplicate records contained different site identifiers.

## Investigation

Pipeline failures should be investigated using the available Airflow logs,
DBeaver job logs, and Databricks execution information when applicable.

## Resolution

When duplicate upstream records cause an integrity error, the upstream
team should review the key used to identify records.

In the known incident, the super-key was changed by adding an updated-date
column to the key basis.

## Important Principle

Do not assume that every pipeline failure has the same root cause.

The observed error and underlying logs should determine the investigation.