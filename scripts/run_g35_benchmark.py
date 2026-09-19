"""Reproduce G35's five-query retrieval run with the local MiniLM embedder.

Run from the repository root with the optional local requirements installed:
    python scripts/run_g35_benchmark.py

The agent uses the repository's demo_llm, which only previews its prompt. Its
output is recorded for transparency and must not be scored as a real answer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import demo_llm
from src import Document, EmbeddingStore, KnowledgeBaseAgent, LocalEmbedder, RecursiveChunker


DATA_DIR = Path("data/quy-dinh-dao-tao")
SEPARATORS = ["\n## ", "\n\n", "\n", ". ", " ", ""]
QUERIES = [
    ("Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong học kỳ hè?", None),
    ("Khi nào sinh viên bị buộc thôi học?", None),
    ("Nghỉ học tạm thời vì lý do cá nhân thì được nghỉ tối đa bao lâu?", None),
    ("Điều kiện để được xét công nhận tốt nghiệp là gì?", None),
    (
        "Điểm ĐATN được tính từ điểm quá trình và điểm cuối kỳ theo trọng số nào?",
        {"audience": "student"},
    ),
]


def read_source(path: Path) -> tuple[dict[str, str], str]:
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"Invalid front matter: {path}")
    metadata = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    if not metadata.get("doc_id") or not metadata.get("audience"):
        raise ValueError(f"Missing doc_id or audience: {path}")
    return metadata, parts[2].strip()


class FilteredStore:
    """Expose a filtered search to KnowledgeBaseAgent without re-embedding."""

    def __init__(self, store: EmbeddingStore, metadata_filter: dict[str, str]):
        self.store = store
        self.metadata_filter = metadata_filter

    def get_collection_size(self) -> int:
        return self.store.get_collection_size()

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        return self.store.search_with_filter(query, top_k, self.metadata_filter)


def main() -> None:
    chunker = RecursiveChunker(separators=SEPARATORS, chunk_size=600)
    documents = []
    paths = sorted(DATA_DIR.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No Markdown sources in {DATA_DIR}")
    for path in paths:
        metadata, content = read_source(path)
        for index, chunk in enumerate(chunker.chunk(content), start=1):
            documents.append(
                Document(
                    id=f"{metadata['doc_id']}::chunk_{index:03d}",
                    content=chunk,
                    metadata=metadata,
                )
            )

    embedder = LocalEmbedder()
    store = EmbeddingStore(embedding_fn=embedder)
    store.add_documents(documents)
    print(f"Model: {embedder._backend_name}")
    print(f"Corpus: {len(paths)} files, {len(documents)} chunks")
    print(f"Strategy: RecursiveChunker(separators={SEPARATORS!r}, chunk_size=600)")

    for number, (question, metadata_filter) in enumerate(QUERIES, start=1):
        search_store = FilteredStore(store, metadata_filter) if metadata_filter else store
        hits = search_store.search(question, top_k=3)
        answer = KnowledgeBaseAgent(search_store, demo_llm).answer(question, top_k=3)
        print(f"\nQ{number}: {question}")
        print(f"metadata_filter={metadata_filter}")
        for rank, hit in enumerate(hits, start=1):
            print(f"  {rank}. {hit['id']} | score={hit['score']:.4f}")
        print(f"Agent (demo_llm): {answer}")


if __name__ == "__main__":
    main()
