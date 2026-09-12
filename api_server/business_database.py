import os
import time
import logging

import mysql.connector
import sqlglot
from sqlglot import exp
from dotenv import load_dotenv


load_dotenv()


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MAX_ROWS = 100
QUERY_TIMEOUT_MS = 5000

ALLOWED_TABLES = {
    "monthly_sales_summary",
    "category_performance",
    "seller_performance",
}

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/business_queries.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Database connection
# ---------------------------------------------------------

def get_business_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


# ---------------------------------------------------------
# SQL validation
# ---------------------------------------------------------

def validate_sql(sql: str) -> str:
    """
    Validate and normalize an LLM-generated SQL query.

    Rules:
    - Exactly one SQL statement
    - SELECT / WITH ... SELECT only
    - Only approved tables
    - No destructive SQL
    - LIMIT automatically added when missing
    """

    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    sql = sql.strip()

    try:
        statements = sqlglot.parse(sql, read="mysql")
    except Exception as exc:
        raise ValueError(
            f"Invalid SQL syntax: {exc}"
        ) from exc

    if len(statements) != 1:
        raise ValueError(
            "Only one SQL statement is allowed."
        )

    statement = statements[0]

    # -----------------------------------------------------
    # SELECT-only enforcement
    # -----------------------------------------------------

    forbidden_types = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.TruncateTable,
        exp.Merge,
    )

    if isinstance(statement, forbidden_types):
        raise ValueError(
            "Only read-only SELECT queries are allowed."
        )

    # A normal SELECT
    # A WITH query will contain a SELECT underneath it.
    if not isinstance(statement, exp.Select):
        selects = list(statement.find_all(exp.Select))

        if not selects:
            raise ValueError(
                "Only SELECT queries are allowed."
            )

    # -----------------------------------------------------
    # Table allowlist
    # -----------------------------------------------------

    referenced_tables = {
        table.name.lower()
        for table in statement.find_all(exp.Table)
    }

    disallowed_tables = (
        referenced_tables - ALLOWED_TABLES
    )

    if disallowed_tables:
        raise ValueError(
            "Query references disallowed table(s): "
            + ", ".join(sorted(disallowed_tables))
        )

    # -----------------------------------------------------
    # LIMIT protection
    # -----------------------------------------------------

    if not list(statement.find_all(exp.Limit)):
        sql = f"{sql.rstrip(';')} LIMIT {MAX_ROWS}"

    return sql


# ---------------------------------------------------------
# Query execution
# ---------------------------------------------------------

def execute_read_only_sql(sql: str) -> dict:
    """
    Validate and execute a read-only analytical SQL query.
    """

    validated_sql = validate_sql(sql)

    logger.info(
        "QUERY_SUBMITTED | sql=%s",
        validated_sql,
    )

    connection = None
    cursor = None

    started_at = time.perf_counter()

    try:
        connection = get_business_connection()
        cursor = connection.cursor(dictionary=True)

        # MySQL session-level maximum execution time
        cursor.execute(
            f"SET SESSION MAX_EXECUTION_TIME = {QUERY_TIMEOUT_MS}"
        )

        cursor.execute(validated_sql)

        rows = cursor.fetchmany(MAX_ROWS)

        execution_time_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        logger.info(
            "QUERY_SUCCESS | rows=%s | execution_time_ms=%s",
            len(rows),
            execution_time_ms,
        )

        return {
            "success": True,
            "sql": validated_sql,
            "columns": list(rows[0].keys()) if rows else [],
            "rows": rows,
            "row_count": len(rows),
            "execution_time_ms": execution_time_ms,
        }

    except mysql.connector.Error as exc:

        execution_time_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        logger.error(
            "QUERY_FAILED | error=%s | execution_time_ms=%s",
            str(exc),
            execution_time_ms,
        )

        return {
            "success": False,
            "sql": validated_sql,
            "error": str(exc),
            "row_count": 0,
            "execution_time_ms": execution_time_ms,
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

#----------------------- dynamic get_business_schema() ------------------------

def get_business_schema():
    connection = None
    cursor = None

    try:
        connection = get_business_connection()
        cursor = connection.cursor(dictionary=True)

        placeholders = ", ".join(["%s"] * len(ALLOWED_TABLES))

        query = f"""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME IN ({placeholders})
            ORDER BY TABLE_NAME, ORDINAL_POSITION
        """

        cursor.execute(query, tuple(ALLOWED_TABLES))
        rows = cursor.fetchall()

        tables = {}

        for row in rows:
            tables.setdefault(row["TABLE_NAME"], []).append({
                "name": row["COLUMN_NAME"],
                "type": row["DATA_TYPE"],
            })

        return {
            "success": True,
            "tables": tables,
        }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()