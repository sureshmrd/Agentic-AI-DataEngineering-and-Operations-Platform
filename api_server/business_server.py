from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api_server.business_database import execute_read_only_sql,get_business_schema
from api_server.pipeline_monitor_server import (
    get_latest_pipeline_run,
    get_pipeline_status,
    get_failed_batches,
    get_watermark,
)


app = FastAPI(title="Business Analytics API")


class BusinessQueryRequest(BaseModel):
    sql: str


@app.post("/business/query")
def business_query(request: BusinessQueryRequest):
    try:
        result = execute_read_only_sql(request.sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    return result

@app.get("/business/schema")
def business_schema():
    return get_business_schema()


# ---------------------------------------------------------
# Pipeline Monitor endpoints
# ---------------------------------------------------------

@app.get("/pipeline/latest")
def pipeline_latest():
    return get_latest_pipeline_run()


@app.get("/pipeline/status")
def pipeline_status():
    return get_pipeline_status()


@app.get("/pipeline/failed")
def pipeline_failed():
    return get_failed_batches()


@app.get("/pipeline/watermark")
def pipeline_watermark():
    return get_watermark()