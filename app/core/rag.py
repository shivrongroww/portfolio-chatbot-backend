from llama_index.core import VectorStoreIndex, StorageContext, Settings as LlamaSettings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from app.core.config import get_settings

settings = get_settings()

_index: VectorStoreIndex | None = None


def _get_chroma_collection():
    client = chromadb.PersistentClient(path=settings.chroma_db_path)
    return client.get_or_create_collection("portfolio")


def get_index() -> VectorStoreIndex:
    global _index
    if _index is not None:
        return _index

    LlamaSettings.embed_model = HuggingFaceEmbedding(
        model_name=settings.embedding_model,
    )

    collection = _get_chroma_collection()
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    _index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )
    return _index


def reset_index():
    """Force re-initialization of the index (call after ingestion)."""
    global _index
    _index = None
