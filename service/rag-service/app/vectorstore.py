from pathlib import Path
from langchain_community.vectorstores import FAISS, DistanceStrategy
from .embeddings import embeddings
from .config import FAISS_DIR

def load_faiss_store(path: Path):
    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
        distance_strategy=DistanceStrategy.COSINE,
    )

def retriever(path: Path, k: int = 5):
    store = load_faiss_store(path)
    return store.as_retriever(search_type="similarity", search_kwargs={"k": k})

def collection_path(name: str) -> Path:
    return FAISS_DIR / name

