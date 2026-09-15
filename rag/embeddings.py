from sentence_transformers import SentenceTransformer

from rag.config import EMBEDDING_MODEL


_model = SentenceTransformer(EMBEDDING_MODEL)


def embed_documents(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = _model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    embedding = _model.encode(
        query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embedding.tolist()