from datetime import datetime
from pathlib import Path
import os
import subprocess

import mysql.connector
from dotenv import load_dotenv

from airflow.sdk import dag, task


PROJECT_ROOT = Path("/mnt/d/agentic-ai-adk")
BATCH_DIR = PROJECT_ROOT / "data" / "batches"

load_dotenv(PROJECT_ROOT / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "agent_adk_db")


def get_windows_host_ip():
    result = subprocess.run(
        ["ip", "route", "show", "default"],
        capture_output=True,
        text=True,
        check=True,
    )

    parts = result.stdout.split()

    if "via" not in parts:
        raise RuntimeError("Could not determine Windows host IP from WSL.")

    return parts[parts.index("via") + 1]


def get_db_connection():
    return mysql.connector.connect(
        host=get_windows_host_ip(),
        port=3306,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


@dag(
    dag_id="olist_incremental_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["olist", "pyspark", "mysql"],
)
def olist_incremental_pipeline():

    @task
    def find_next_batch():
        batches = sorted(
            p.name
            for p in BATCH_DIR.iterdir()
            if p.is_dir() and p.name.startswith("batch_")
        )

        if not batches:
            raise ValueError("No generated batches found.")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT batch_id
            FROM pipeline_batches
            WHERE status = 'SUCCESS'
        """)

        successful_batches = {
            row[0]
            for row in cursor.fetchall()
        }

        cursor.close()
        connection.close()

        pending_batches = [
            batch
            for batch in batches
            if batch not in successful_batches
        ]

        if not pending_batches:
            raise ValueError("No pending batches available.")

        next_batch = pending_batches[0]

        print(f"Next batch: {next_batch}")

        return next_batch

    @task
    def run_pipeline(batch_id: str):
        command = [
            "python",
            "-m",
            "spark_pipeline.pipeline",
            "--batch-id",
            batch_id,
        ]

        print(f"Running pipeline for {batch_id}")

        env = os.environ.copy()
        env["DB_HOST"] = get_windows_host_ip()

        subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=True,
            env=env,
        )

        return batch_id

    @task
    def verify_batch(batch_id: str):
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT status
            FROM pipeline_batches
            WHERE batch_id = %s
        """, (batch_id,))

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if not result:
            raise ValueError(
                f"No pipeline record found for {batch_id}"
            )

        if result[0] != "SUCCESS":
            raise ValueError(
                f"Batch {batch_id} completed with status: {result[0]}"
            )

        print(f"{batch_id} verified successfully.")

    batch = find_next_batch()
    completed = run_pipeline(batch)
    verify_batch(completed)


olist_incremental_pipeline()
