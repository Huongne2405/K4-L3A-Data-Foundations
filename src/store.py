from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    An in-memory vector store for text chunks.

    The embedding_fn parameter allows injection of a real or mock embedder.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._store: list[dict[str, Any]] = []

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = dict(doc.metadata or {})
        if not metadata.get("doc_id"):
            # Chunk IDs such as "file#0" still belong to the source document "file".
            source_id, marker, chunk_number = doc.id.rpartition("#")
            metadata["doc_id"] = source_id if marker and chunk_number.isdigit() else doc.id
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []
        query_vec = self._embedding_fn(query)
        ranked: list[dict[str, Any]] = []
        for record in records:
            result = {
                "id": record.get("id"),
                "content": record.get("content", ""),
                "metadata": dict(record.get("metadata") or {}),
                "score": _dot(query_vec, record["embedding"]),
            }
            ranked.append(result)
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[: max(0, top_k)]

    def add_documents(self, docs: list[Document]) -> None:
        """Embed each document's content and store it in memory."""
        for doc in docs:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            candidates = self._store
        else:
            candidates = [
                record
                for record in self._store
                if all((record.get("metadata") or {}).get(key) == value for key, value in metadata_filter.items())
            ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        remaining = [
            record
            for record in self._store
            if (record.get("metadata") or {}).get("doc_id") != doc_id
        ]
        removed = len(remaining) < len(self._store)
        self._store = remaining
        return removed
