from langchain_huggingface import HuggingFaceEmbeddings
from .config import EMBED_MODEL_NAME, EMBED_DEVICE, EMBED_BATCH_SIZE

embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME,
    model_kwargs={"device": EMBED_DEVICE},
    encode_kwargs={"normalize_embeddings": True, "batch_size": EMBED_BATCH_SIZE},
)
