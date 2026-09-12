from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api_server.business_database import execute_read_only_sql,get_business_schema


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