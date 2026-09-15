import chromadb

from rag.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DEFAULT_TOP_K,
    MAX_DISTANCE,
)
from rag.embeddings import embed_query
from rag.vector_store import collection


# client = chromadb.PersistentClient(
#     path=str(CHROMA_DIR)
# )

# collection = client.get_or_create_collection(
#     name=COLLECTION_NAME,
#     metadata={
#         "description": "Olist project knowledge base",
#         "hnsw:space": "cosine",
#     },
# )


def search_knowledge_base(
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> dict:

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    top_k = max(
        1,
        min(top_k, 20),
    )

    query_embedding = embed_query(query)

    # Retrieve a few extra candidates so that
    # low-quality results can be filtered.
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k * 2, 20),
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = result.get(
        "documents", [[]]
    )[0]

    metadatas = result.get(
        "metadatas", [[]]
    )[0]

    distances = result.get(
        "distances", [[]]
    )[0]

    ids = result.get(
        "ids", [[]]
    )[0]

    results = []

    for index in range(len(documents)):

        distance = distances[index]

        # Lower Chroma cosine distance = better match.
        if distance > MAX_DISTANCE:
            continue

        results.append(
            {
                "chunk_id": ids[index],
                "doc_id": metadatas[index]["doc_id"],
                "text": documents[index],
                "distance": distance,
                "metadata": metadatas[index],
            }
        )

        if len(results) >= top_k:
            break

    low_confidence = len(results) == 0

    return {
        "success": True,
        "query": query,
        "result_count": len(results),
        "low_confidence": low_confidence,
        "results": results,
    }

def get_document(doc_id: str) -> dict:

    result = collection.get(
        where={"doc_id": doc_id},
        include=[
            "documents",
            "metadatas",
        ],
    )

    documents = result.get(
        "documents",
        [],
    )

    metadatas = result.get(
        "metadatas",
        [],
    )

    if not documents:
        return {
            "success": False,
            "error": (
                f"Document not found: {doc_id}"
            ),
        }

    chunks = []

    combined = []

    for document, metadata in zip(
        documents,
        metadatas,
    ):
        chunks.append(
            {
                "chunk_id": metadata["chunk_id"],
                "text": document,
                "metadata": metadata,
            }
        )

    chunks.sort(
        key=lambda item:
        item["metadata"]["chunk_index"]
    )

    for chunk in chunks:
        combined.append(
            chunk["text"]
        )

    return {
        "success": True,
        "doc_id": doc_id,
        "source": chunks[0]["metadata"]["source"],
        "title": chunks[0]["metadata"]["title"],
        "category": chunks[0]["metadata"]["category"],
        "content_hash": chunks[0]["metadata"]["content_hash"],
        "ingested_at": chunks[0]["metadata"]["ingested_at"],
        "text": "\n\n".join(combined),
        "chunks": chunks,
    }