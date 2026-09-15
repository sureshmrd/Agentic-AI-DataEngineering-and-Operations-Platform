import hashlib
from datetime import datetime, timezone
from pathlib import Path

import chromadb

from rag.chunking import split_document
from rag.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DOCUMENTS_DIR,
    SUPPORTED_EXTENSIONS,
)
from rag.embeddings import embed_documents
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


def calculate_hash(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def load_markdown(path: Path) -> str:
    return path.read_text(
        encoding="utf-8"
    )


def load_pdf(path: Path) -> str:
    import pymupdf

    pages = []

    with pymupdf.open(path) as document:
        for page in document:
            text = page.get_text()
            if text.strip():
                pages.append(text)

    return "\n\n".join(pages)


def load_document(path: Path) -> str:
    if path.suffix.lower() == ".md":
        return load_markdown(path)

    if path.suffix.lower() == ".pdf":
        return load_pdf(path)

    raise ValueError(
        f"Unsupported document type: {path.suffix}"
    )


def make_doc_id(path: Path) -> str:
    relative = path.relative_to(DOCUMENTS_DIR)

    return str(
        relative.with_suffix("")
    ).replace("\\", "/").replace("/", "__")


def get_category(path: Path) -> str:
    relative = path.relative_to(DOCUMENTS_DIR)

    if len(relative.parts) > 1:
        return relative.parts[0]

    return "general"


def get_existing_hash(doc_id: str) -> str | None:
    result = collection.get(
        where={"doc_id": doc_id},
        include=["metadatas"],
    )

    metadatas = result.get("metadatas") or []

    if not metadatas:
        return None

    return metadatas[0].get("content_hash")


def get_existing_chunk_ids(doc_id: str) -> list[str]:
    result = collection.get(
        where={"doc_id": doc_id},
        include=[],
    )

    return result.get("ids", [])


def ingest_document(path: Path) -> str:
    text = load_document(path)

    if not text.strip():
        return "EMPTY"

    doc_id = make_doc_id(path)
    content_hash = calculate_hash(text)

    existing_hash = get_existing_hash(doc_id)

    if existing_hash == content_hash:
        return "UNCHANGED"

    chunks = split_document(text)

    if not chunks:
        return "EMPTY"

    embeddings = embed_documents(chunks)

    now = datetime.now(
        timezone.utc
    ).isoformat()

    ids = [
        f"{doc_id}::chunk_{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "doc_id": doc_id,
            "chunk_id": ids[index],
            "source": str(
                path.relative_to(DOCUMENTS_DIR)
            ).replace("\\", "/"),
            "title": path.stem,
            "category": get_category(path),
            "chunk_index": index,
            "content_hash": content_hash,
            "ingested_at": now,
        }
        for index in range(len(chunks))
    ]

    existing_ids = set(
        get_existing_chunk_ids(doc_id)
    )

    new_ids = set(ids)

    obsolete_ids = list(
        existing_ids - new_ids
    )

    if obsolete_ids:
        collection.delete(
            ids=obsolete_ids
        )

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return "UPDATED"


def ingest_all() -> None:
    DOCUMENTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = [
        path
        for path in DOCUMENTS_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower()
        in SUPPORTED_EXTENSIONS
    ]

    current_doc_ids = {
        make_doc_id(path)
        for path in paths
    }

    remove_deleted_documents(
        current_doc_ids
    )

    if not paths:
        print("No documents found.")
        return

    for path in sorted(paths):
        try:
            result = ingest_document(path)

            print(
                f"{result:10} | "
                f"{path.relative_to(DOCUMENTS_DIR)}"
            )

        except Exception as exc:
            print(
                f"FAILED     | "
                f"{path.relative_to(DOCUMENTS_DIR)} | "
                f"{exc}"
            )


def get_indexed_doc_ids() -> set[str]:
    result = collection.get(
        include=["metadatas"],
    )

    metadatas = result.get("metadatas") or []

    return {
        metadata["doc_id"]
        for metadata in metadatas
        if metadata and "doc_id" in metadata
    }


def remove_deleted_documents(current_doc_ids: set[str]) -> None:
    indexed_doc_ids = get_indexed_doc_ids()

    deleted_doc_ids = (
        indexed_doc_ids - current_doc_ids
    )

    for doc_id in deleted_doc_ids:
        collection.delete(
            where={"doc_id": doc_id}
        )

        print(
            f"DELETED    | {doc_id}"
        )


if __name__ == "__main__":
    ingest_all()