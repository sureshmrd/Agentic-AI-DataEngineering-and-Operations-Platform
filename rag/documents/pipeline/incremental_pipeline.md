# Incremental Data Pipeline

## Overview

The Olist pipeline processes data incrementally using monthly batch files.

The pipeline is orchestrated by Apache Airflow and the processing logic is
implemented using PySpark.

The general flow is:

Olist Dataset
    -> Batch Generation
    -> Monthly Batch Files
    -> Airflow
    -> PySpark
    -> Validation and Transformation
    -> MySQL
    -> Analytics and Pipeline Metadata

## Batch Processing

The pipeline identifies the next available batch and processes that batch.

The current Airflow DAG contains:

find_next_batch
    -> run_pipeline
    -> verify_batch

## Pipeline Metadata

Pipeline execution information is recorded in:

pipeline_batches

Pipeline processing progress is recorded in:

pipeline_watermarks

## Incremental Processing

The pipeline uses a watermark to track the latest processed value.

The watermark allows subsequent executions to identify the next portion of
source data that needs to be processed.

## Validation

The PySpark pipeline validates and transforms incoming data before writing
results into MySQL.

Validation failures are recorded through pipeline execution metadata.