# Pipeline Recovery SLA

## Purpose

This document defines the intended recovery targets for the example Olist
pipeline operations process.

These values are project policy examples and are not external organizational
SLAs.

## Critical Pipeline Failure

For a critical production-impacting pipeline failure:

- Acknowledge the failure within 15 minutes.
- Begin investigation within 30 minutes.
- Establish an initial root-cause hypothesis within 60 minutes.
- Target recovery within 4 hours.

## Non-Critical Failure

For a non-critical failure:

- Acknowledge within 1 business hour.
- Begin investigation within 2 business hours.
- Target recovery within 1 business day.

## Escalation

Escalate when the failure cannot be resolved within the applicable target
or when the root cause indicates a broader data-quality or infrastructure
problem.

## Important Note

These SLA values are example project policies created for the RAG knowledge
base.