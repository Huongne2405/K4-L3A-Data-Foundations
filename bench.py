"""G35 retrieval benchmark. Run with ``python bench.py`` in an active venv.

Everyone uses the same corpus, questions, metadata and embedding model. To
compare chunking strategies, change only the CHUNKER assignment below. Install
``requirements-local.txt`` before first use of the local MiniLM embedder.
"""

from __future__ import annotations

from pathlib import Path

from src import Document, EmbeddingStore, HeadingSectionChunker, LocalEmbedder, RecursiveChunker


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "quy-dinh-dao-tao"

# Change only this line when testing another chunking strategy.
CHUNKER = RecursiveChunker(separators=["\n## ", "\n\n", "\n", ". ", " ", ""], chunk_size=600)

BENCHMARKS = [
    (
        "Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong học kỳ hè?",
        "8 TC (Điều 10 khoản 2a)",
        None,
    ),
    (
        "Khi nào sinh viên bị buộc thôi học?",
        "Cảnh báo mức 3 lần thứ hai liên tiếp, hoặc chậm tiến độ quá thời gian cho phép/không còn khả năng tốt nghiệp đúng hạn (Điều 19 khoản 3)",
        None,
    ),
    (
        "Nghỉ học tạm thời vì lý do cá nhân thì được nghỉ tối đa bao lâu?",
        "04 học kỳ chính, tính vào thời gian học chậm tiến độ (Điều 16 khoản 2d)",
        None,
    ),
    (
        "Điều kiện để được xét công nhận tốt nghiệp là gì?",
        "Hoàn thành học phần CTĐT gồm GDTC và GDQP-AN; đạt chuẩn ngoại ngữ; điểm trung bình tích lũy toàn khóa từ 2,0; tại thời điểm xét tốt nghiệp không bị truy cứu trách nhiệm hình sự hoặc không đang bị đình chỉ học tập (Điều 14 khoản 3a–d)",
        None,
    ),
    (
        "Điểm ĐATN được tính từ điểm quá trình và điểm cuối kỳ theo trọng số nào?",
        "0,5 cho điểm quá trình và 0,5 cho điểm cuối kỳ (Điều 13 khoản 2a)",
        {"audience": "student"},
    ),
]


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    """Return frontmatter metadata and body without passing YAML to the chunker."""
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError(f"Missing YAML frontmatter: {path}")
    frontmatter = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"')
    if frontmatter.get("doc_id") != path.stem:
        raise ValueError(f"doc_id must match the file name: {path}")
    if not frontmatter.get("audience"):
        raise ValueError(f"Missing audience: {path}")
    return frontmatter, parts[2].strip()


def main() -> None:
    paths = sorted(DATA_DIR.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No Markdown documents in {DATA_DIR}")

    documents = []
    for path in paths:
        frontmatter, body = read_markdown(path)
        for index, chunk in enumerate(CHUNKER.chunk(body)):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={**frontmatter, "doc_id": path.stem, "file_path": str(path.relative_to(ROOT))},
                )
            )

    embedder = LocalEmbedder()
    store = EmbeddingStore(embedding_fn=embedder)
    store.add_documents(documents)
    print(f"model: {embedder._backend_name}")
    print(f"sources: {len(paths)} | chunks loaded: {store.get_collection_size()}")
    print(f"chunker: {CHUNKER.__class__.__name__} | settings: {vars(CHUNKER)}")

    for number, (question, gold, metadata_filter) in enumerate(BENCHMARKS, start=1):
        results = store.search_with_filter(question, top_k=3, metadata_filter=metadata_filter)
        print(f"\nQ{number}: {question}")
        print(f"gold: {gold}")
        print(f"metadata_filter: {metadata_filter}")
        for rank, result in enumerate(results, start=1):
            print(
                f"  {rank}. id={result['id']} | doc_id={result['metadata']['doc_id']} "
                f"| score={result['score']:.4f}"
            )
            print(f"     {result['content'][:120].replace(chr(10), ' ')}")


if __name__ == "__main__":
    main()
