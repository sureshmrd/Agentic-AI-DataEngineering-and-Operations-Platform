import chromadb

from rag.config import CHROMA_DIR, COLLECTION_NAME


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": "Olist project knowledge base",
        "hnsw:space": "cosine",
    },
)