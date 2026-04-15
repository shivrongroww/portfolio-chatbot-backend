import os
from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings as LlamaSettings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from app.core.config import get_settings
from app.core.rag import reset_index, _get_chroma_collection

settings = get_settings()

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


async def ingest_documents(file_paths: list[Path]) -> int:
    """
    Ingest documents into ChromaDB vector store.
    Returns the number of documents successfully processed.
    """
    LlamaSettings.embed_model = HuggingFaceEmbedding(
        model_name=settings.embedding_model,
    )
    LlamaSettings.chunk_size = settings.chunk_size
    LlamaSettings.chunk_overlap = settings.chunk_overlap

    valid_paths = [p for p in file_paths if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not valid_paths:
        return 0

    documents = SimpleDirectoryReader(
        input_files=[str(p) for p in valid_paths]
    ).load_data()

    collection = _get_chroma_collection()
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    # Reset cached index so next query uses fresh data
    reset_index()

    return len(valid_paths)


def get_retriever(top_k: int | None = None):
    from app.core.rag import get_index
    index = get_index()
    return index.as_retriever(similarity_top_k=top_k or settings.rag_top_k)


def retrieve_context(query: str) -> str:
    """Retrieve relevant chunks from the vector store for a given query."""
    retriever = get_retriever()
    nodes = retriever.retrieve(query)
    if not nodes:
        return ""
    return "\n\n---\n\n".join(node.get_content() for node in nodes)
