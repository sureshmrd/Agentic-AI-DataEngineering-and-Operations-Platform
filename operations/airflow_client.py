import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


class AirflowClient:
    """Read-only client for the Airflow 3 REST API."""

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.base_url = (
            base_url
            or os.getenv("AIRFLOW_API_URL")
            or "http://127.0.0.1:8080"
        ).rstrip("/")

        self.username = username or os.getenv("AIRFLOW_USERNAME")
        self.password = password or os.getenv("AIRFLOW_PASSWORD")

        if not self.username or not self.password:
            raise ValueError(
                "AIRFLOW_USERNAME and AIRFLOW_PASSWORD must be configured."
            )

        self._token: str | None = None

    def _get_token(self) -> str:
        response = httpx.post(
            f"{self.base_url}/auth/token",
            json={
                "username": self.username,
                "password": self.password,
            },
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()
        token = data.get("access_token")

        if not token:
            raise RuntimeError("Airflow authentication returned no access token.")

        self._token = token
        return token

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict:
        token = self._token or self._get_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        response = httpx.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            timeout=20.0,
            **kwargs,
        )

        # Token may have expired.
        if response.status_code == 401:
            self._token = self._get_token()

            headers["Authorization"] = f"Bearer {self._token}"

            response = httpx.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                timeout=20.0,
                **kwargs,
            )

        response.raise_for_status()
        return response.json()

    def get_dag(self, dag_id: str) -> dict:
        return self._request(
            "GET",
            f"/api/v2/dags/{dag_id}",
        )

    def get_dag_runs(
        self,
        dag_id: str,
        limit: int = 100,
    ) -> dict:
        return self._request(
            "GET",
            f"/api/v2/dags/{dag_id}/dagRuns",
            params={"limit": limit},
        )

    def get_dag_run(
        self,
        dag_id: str,
        dag_run_id: str,
    ) -> dict:
        return self._request(
            "GET",
            f"/api/v2/dags/{dag_id}/dagRuns/{dag_run_id}",
        )

    def get_task_instances(
        self,
        dag_id: str,
        dag_run_id: str,
    ) -> dict:
        return self._request(
            "GET",
            f"/api/v2/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
        )

    def get_task_log(
        self,
        dag_id: str,
        dag_run_id: str,
        task_id: str,
        try_number: int = 1,
    ) -> dict:
        return self._request(
            "GET",
            (
                f"/api/v2/dags/{dag_id}/dagRuns/"
                f"{dag_run_id}/taskInstances/"
                f"{task_id}/logs/{try_number}"
            ),
        )

    def get_latest_dag_run(self, dag_id: str) -> dict | None:
        data = self.get_dag_runs(dag_id, limit=100)

        runs = data.get("dag_runs", [])

        if not runs:
            return None

        # Airflow already returns recent runs, but explicitly sort
        # by start_date/run_after for deterministic behavior.
        runs.sort(
            key=lambda run: (
                run.get("start_date")
                or run.get("run_after")
                or ""
            ),
            reverse=True,
        )

        return runs[0]

    def get_failed_tasks(
        self,
        dag_id: str,
        dag_run_id: str,
    ) -> list[dict]:
        data = self.get_task_instances(
            dag_id,
            dag_run_id,
        )

        return [
            task
            for task in data.get("task_instances", [])
            if task.get("state") == "failed"
        ]