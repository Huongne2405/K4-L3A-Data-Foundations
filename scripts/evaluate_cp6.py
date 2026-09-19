"""Compare three G35 chunkers with a semantic embedder and answer-level checks.

Run from the project root with the local requirements installed:
    python scripts/evaluate_cp6.py

The personal Recursive run is written to report/ket_qua_benchmark.txt. The
three-strategy comparison is written separately to report/so_sanh_chien_luoc.txt.
Scores measure whether retrieval supplies the answer, not LLM answer quality.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bench import BENCHMARKS, DATA_DIR, read_markdown
from src import (
    Document,
    EmbeddingStore,
    FixedSizeChunker,
    HeadingSectionChunker,
    LocalEmbedder,
    RecursiveChunker,
)


STRATEGIES = {
    "fixed_600_overlap_50": FixedSizeChunker(chunk_size=600, overlap=50),
    "recursive_600": RecursiveChunker(
        separators=["\n## ", "\n\n", "\n", ". ", " ", ""], chunk_size=600
    ),
    "heading_600": HeadingSectionChunker(chunk_size=600),
}

# Every phrase is copied from a source paragraph and required for a complete
# answer. This guards against counting a topical but answer-free chunk.
ANSWER_CUES = [
    ("tối đa 8 TC trong học kỳ hè",),
    (
        "cảnh báo học tập mức 3 lần thứ hai liên tiếp",
        "học chậm tiến độ quá thời gian cho phép",
        "không còn đủ khả năng tốt nghiệp",
    ),
    ("Thời gian nghỉ học tối đa cho phép là 04 học kỳ chính", "tính vào thời gian học chậm tiến độ"),
    (
        "Giáo dục thể chất",
        "Đạt chuẩn ngoại ngữ đầu ra",
        "đạt từ 2,0 trở lên",
        "truy cứu trách nhiệm hình sự",
        "đình chỉ học tập",
    ),
    ("trọng số 0,5 đối với điểm quá trình", "trọng số 0,5 đối với điểm cuối kỳ"),
]
GOLD_DOC_IDS = [
    "dieu-10-dang-ky-hoc-tap",
    "dieu-19-20-canh-bao-hoc-tap-va-buoc-thoi-hoc",
    "dieu-16-nghi-hoc-tam-thoi-va-thoi-hoc",
    "dieu-14-15-dang-ky-tot-nghiep-va-hang-tot-nghiep",
    "dieu-13-dieu-kien-lam-do-an-tot-nghiep",
]


def contains_all(text: str, cues: tuple[str, ...]) -> bool:
    normalized = " ".join(text.casefold().split())
    return all(" ".join(cue.casefold().split()) in normalized for cue in cues)


def assess(hits: list[dict], gold_doc_id: str, cues: tuple[str, ...]) -> dict:
    doc_rank = next(
        (rank for rank, hit in enumerate(hits, 1) if hit["metadata"]["doc_id"] == gold_doc_id),
        None,
    )
    answer_rank = next(
        (rank for rank, hit in enumerate(hits, 1) if contains_all(hit["content"], cues)),
        None,
    )
    source_answer_rank = next(
        (
            rank
            for rank, hit in enumerate(hits, 1)
            if hit["metadata"]["doc_id"] == gold_doc_id and contains_all(hit["content"], cues)
        ),
        None,
    )
    context_answerable = contains_all("\n".join(hit["content"] for hit in hits), cues)
    # Credit requires the answer in the agreed gold source, not merely the
    # same words in another audience's document. The other rank remains in
    # the log to expose that distinction during the filter A/B run.
    score = 2 if source_answer_rank == 1 else 1 if source_answer_rank is not None else 0
    return {
        "doc_rank": doc_rank,
        "answer_rank": answer_rank,
        "source_answer_rank": source_answer_rank,
        "context_answerable": context_answerable,
        "score": score,
    }


def build_store(paths: list[Path], chunker: object, embedder: LocalEmbedder) -> EmbeddingStore:
    documents = []
    for path in paths:
        metadata, body = read_markdown(path)
        for index, chunk in enumerate(chunker.chunk(body)):
            documents.append(
                Document(
                    id=f"{path.stem}#{index}",
                    content=chunk,
                    metadata={**metadata, "doc_id": path.stem, "file_path": str(path.relative_to(ROOT))},
                )
            )
    store = EmbeddingStore(embedding_fn=embedder)
    store.add_documents(documents)
    return store


def run() -> tuple[str, str]:
    paths = sorted(DATA_DIR.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No documents in {DATA_DIR}")
    embedder = LocalEmbedder()
    header = [f"Embedding backend: {embedder._backend_name}", f"Sources: {len(paths)}", "Top-k: 3"]
    lines = header.copy()
    personal_block: list[str] = []

    for strategy_name, chunker in STRATEGIES.items():
        block_start = len(lines)
        store = build_store(paths, chunker, embedder)
        lines.extend(["", f"=== {strategy_name} | chunks={store.get_collection_size()} ==="])
        total = 0
        for index, (question, gold_answer, metadata_filter) in enumerate(BENCHMARKS):
            hits = store.search_with_filter(question, top_k=3, metadata_filter=metadata_filter)
            result = assess(hits, GOLD_DOC_IDS[index], ANSWER_CUES[index])
            total += result["score"]
            lines.extend(
                [
                    f"Q{index + 1}: {question}",
                    f"  gold: {gold_answer}",
                    f"  filter: {metadata_filter}",
                    f"  gold_doc_rank={result['doc_rank']} answer_chunk_rank={result['answer_rank']} "
                    f"source_answer_rank={result['source_answer_rank']} "
                    f"context_answerable={result['context_answerable']} retrieval_score={result['score']}/2",
                ]
            )
            for rank, hit in enumerate(hits, 1):
                has_answer = contains_all(hit["content"], ANSWER_CUES[index])
                lines.append(
                    f"  {rank}. id={hit['id']} doc_id={hit['metadata']['doc_id']} "
                    f"score={hit['score']:.4f} answer_cues={has_answer}"
                )

            if index == 4:
                unfiltered = store.search_with_filter(question, top_k=3, metadata_filter=None)
                ab = assess(unfiltered, GOLD_DOC_IDS[index], ANSWER_CUES[index])
                lines.append(
                    f"  A/B no filter: gold_doc_rank={ab['doc_rank']} "
                    f"answer_chunk_rank={ab['answer_rank']} "
                    f"source_answer_rank={ab['source_answer_rank']} "
                    f"context_answerable={ab['context_answerable']} retrieval_score={ab['score']}/2"
                )
                for rank, hit in enumerate(unfiltered, 1):
                    has_answer = contains_all(hit["content"], ANSWER_CUES[index])
                    lines.append(
                        f"  {rank}. id={hit['id']} doc_id={hit['metadata']['doc_id']} "
                        f"score={hit['score']:.4f} answer_cues={has_answer}"
                    )
        lines.append(f"TOTAL retrieval proxy: {total}/10 (LLM answer not measured)")
        if strategy_name == "recursive_600":
            personal_block = lines[block_start:].copy()
    return "\n".join(lines) + "\n", "\n".join(header + personal_block) + "\n"


if __name__ == "__main__":
    comparison, personal = run()
    personal_path = ROOT / "report" / "ket_qua_benchmark.txt"
    comparison_path = ROOT / "report" / "so_sanh_chien_luoc.txt"
    personal_path.write_text(personal, encoding="utf-8")
    comparison_path.write_text(comparison, encoding="utf-8")
    print(comparison, end="")
    print(f"Saved: {personal_path} and {comparison_path}")
