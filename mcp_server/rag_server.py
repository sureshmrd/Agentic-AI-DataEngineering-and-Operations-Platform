import requests

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("rag-server")

API_BASE_URL = "http://127.0.0.1:8003"


@mcp.tool()
def search_knowledge_base(
    query: str,
    top_k: int = 5,
) -> dict:
    """Search the project knowledge base for relevant project information."""

    try:
        response = requests.post(
            f"{API_BASE_URL}/rag/search",
            json={
                "query": query,
                "top_k": top_k,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "RAG API is unavailable.",
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "RAG API request timed out.",
        }

    except requests.exceptions.HTTPError as exc:
        return {
            "success": False,
            "error": f"RAG API error: {exc}",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": f"RAG request failed: {exc}",
        }


@mcp.tool()
def get_document(doc_id: str) -> dict:
    """Retrieve the complete content of a project knowledge document."""

    try:
        response = requests.get(
            f"{API_BASE_URL}/rag/document/{doc_id}",
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "RAG API is unavailable.",
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "RAG API request timed out.",
        }

    except requests.exceptions.HTTPError as exc:
        return {
            "success": False,
            "error": f"RAG API error: {exc}",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "error": f"RAG request failed: {exc}",
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")