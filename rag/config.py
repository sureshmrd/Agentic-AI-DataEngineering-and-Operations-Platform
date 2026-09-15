from pathlib import Path


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_DIR = PROJECT_ROOT / "rag" / "documents"
CHROMA_DIR = PROJECT_ROOT / "rag" / "chroma"

COLLECTION_NAME = "project_knowledge"


# ---------------------------------------------------------
# Chunking
# ---------------------------------------------------------

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


# ---------------------------------------------------------
# Retrieval
# ---------------------------------------------------------

DEFAULT_TOP_K = 5

# Chroma returns distances. Lower = more similar.
# This is an initial V1 threshold and should be tuned after testing.
MAX_DISTANCE = 0.70


# ---------------------------------------------------------
# Embedding model
# ---------------------------------------------------------

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------
# Supported documents
# ---------------------------------------------------------

SUPPORTED_EXTENSIONS = {
    ".md",
    ".pdf",
}