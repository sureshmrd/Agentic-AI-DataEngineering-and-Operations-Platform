# Duplicate Record Incident

## Incident Summary

An intermittent pipeline failure was caused by duplicate upstream records.

The affected uniqueness combination was:

study_code_alias
country_code
study_subject_eid
visit_name

Two records with different site identifiers were present for the same
combination.

## Investigation

The issue was investigated using Airflow execution information, DBeaver job
logs, and Databricks processing information.

## Resolution

The upstream team changed the super-key basis by adding an updated-date
column.

After the upstream correction, the integrity error was resolved.

## Lesson

When an integrity error occurs, verify the upstream uniqueness assumptions
before repeatedly retrying the same failed processing logic.