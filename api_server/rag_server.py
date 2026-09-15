from fastapi import HTTPException

from rag.retrieval import (
    search_knowledge_base,
    get_document,
)


def search_rag(
    query: str,
    top_k: int = 5,
) -> dict:
    """
    Search the project knowledge base.
    """
    try:
        return search_knowledge_base(
            query=query,
            top_k=top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG retrieval failed: {exc}",
        ) from exc


def fetch_rag_document(
    doc_id: str,
) -> dict:
    """
    Retrieve a complete project knowledge document.
    """
    try:
        result = get_document(doc_id)

        if not result["success"]:
            raise HTTPException(
                status_code=404,
                detail=result["error"],
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document retrieval failed: {exc}",
        ) from exc