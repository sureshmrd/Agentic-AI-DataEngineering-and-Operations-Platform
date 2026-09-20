import requests


RAG_API_URL = "http://127.0.0.1:8003"


def search_troubleshooting(
    query: str,
    top_k: int = 3,
) -> dict:

    try:
        response = requests.post(
            f"{RAG_API_URL}/rag/search",
            json={
                "query": query,
                "top_k": top_k,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }