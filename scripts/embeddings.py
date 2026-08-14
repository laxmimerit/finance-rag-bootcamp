"""Embeddings: text to vectors with nomic-embed-text on local Ollama."""

from ragwire.embeddings.factory import get_embedding


def get_embedder():
    """Return the embedding model the whole pipeline uses."""
    return get_embedding({"provider": "ollama", "model": "nomic-embed-text"})
