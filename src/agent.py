from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy ngữ cảnh trong kho tri thức."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy ngữ cảnh liên quan đến câu hỏi."

        context_parts: list[str] = []
        for index, record in enumerate(results, start=1):
            metadata = record.get("metadata") or {}
            chunk_id = record.get("id") or "unknown"
            doc_id = metadata.get("doc_id") or chunk_id
            source = (
                metadata.get("source_url")
                or metadata.get("source")
                or doc_id
                or "unknown"
            )
            content = str(record.get("content", "")).strip()
            context_parts.append(
                f"[{index}] (doc_id: {doc_id}; chunk_id: {chunk_id}; nguồn: {source})\n{content}"
            )

        context = "\n\n".join(context_parts)
        prompt = (
            "Bạn chỉ được trả lời dựa trên ngữ cảnh bên dưới. "
            "Không bịa thông tin. Nếu ngữ cảnh không đủ, nói rõ là không tìm thấy. "
            "Khi dùng một đoạn, trích dẫn số chunk tương ứng, ví dụ [1] hoặc [2].\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n\n"
            "Câu trả lời:"
        )
        return self.llm_fn(prompt)
