"""Run Hưởng's five-question benchmark with a real LLM answer step.

    LLM_STRATEGY='huong_recursive(600)' python scripts/compare_strategies.py --llm

Retrieval uses the same local MiniLM embeddings and RecursiveChunker as
bench.py. Only the answer step calls the OpenAI Responses API. The API key is
read from .env and never written to the report.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
import certifi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bench import BENCHMARKS, DATA_DIR
from scripts.evaluate_cp6 import ANSWER_CUES, GOLD_DOC_IDS, STRATEGIES, assess, build_store
from src import KnowledgeBaseAgent, LocalEmbedder

STRATEGY_NAME = "huong_recursive(600)"
REPORT_PATH = ROOT / "report" / "ket_qua_llm_huong.txt"


class FilteredStore:
    """Give KnowledgeBaseAgent the same filtered candidates as the benchmark."""

    def __init__(self, store: object, metadata_filter: dict[str, str] | None) -> None:
        self.store = store
        self.metadata_filter = metadata_filter

    def get_collection_size(self) -> int:
        return self.store.get_collection_size()

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        return self.store.search_with_filter(query, top_k=top_k, metadata_filter=self.metadata_filter)


def extract_text(response: dict) -> str:
    """Read text from a completed Responses API JSON object."""
    if response.get("status") != "completed":
        raise RuntimeError(f"LLM response status: {response.get('status', 'unknown')}")
    parts = [
        content.get("text", "")
        for item in response.get("output", [])
        if item.get("type") == "message"
        for content in item.get("content", [])
        if content.get("type") == "output_text"
    ]
    answer = "\n".join(part for part in parts if part).strip()
    if not answer:
        raise RuntimeError("LLM returned no output text")
    return answer


def make_openai_llm(model: str):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is missing from the environment or .env")

    def call(prompt: str) -> str:
        payload = json.dumps(
            {
                "model": model,
                "input": prompt,
                "max_output_tokens": 500,
                "temperature": 0,
                "store": False,
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            "https://api.openai.com/v1/responses",
            data=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            with urlopen(request, timeout=90, context=context) as connection:
                response = json.load(connection)
        except HTTPError as error:
            try:
                detail = json.load(error)
                code = detail.get("error", {}).get("code") or detail.get("error", {}).get("type")
            except (ValueError, OSError):
                code = "unknown"
            raise RuntimeError(f"OpenAI API HTTP {error.code} ({code})") from error
        except URLError as error:
            raise RuntimeError(f"OpenAI API network error: {error.reason}") from error
        return extract_text(response)

    return call


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm", action="store_true", help="Call the LLM for the five answers")
    args = parser.parse_args()
    strategy = os.getenv("LLM_STRATEGY")
    if strategy != STRATEGY_NAME:
        parser.error(f"Set LLM_STRATEGY='{STRATEGY_NAME}'")
    load_dotenv(ROOT / ".env", override=False)
    model = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    llm = make_openai_llm(model) if args.llm else None

    paths = sorted(DATA_DIR.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No Markdown documents in {DATA_DIR}")
    embedder = LocalEmbedder()
    store = build_store(paths, STRATEGIES["recursive_600"], embedder)
    lines = [
        f"strategy: {strategy}",
        f"embedding: {embedder._backend_name}",
        f"llm_model: {model if args.llm else 'not called'}",
        f"files: {len(paths)} | chunks: {store.get_collection_size()} | top_k: 3",
    ]

    for index, (question, gold, metadata_filter) in enumerate(BENCHMARKS):
        search_store = FilteredStore(store, metadata_filter)
        hits = search_store.search(question, top_k=3)
        retrieval = assess(hits, GOLD_DOC_IDS[index], ANSWER_CUES[index])
        block = [
            "",
            f"Q{index + 1}: {question}",
            f"gold: {gold}",
            f"metadata_filter: {metadata_filter}",
            f"source_answer_rank: {retrieval['source_answer_rank']}",
        ]
        for rank, hit in enumerate(hits, 1):
            block.append(
                f"  {rank}. {hit['id']} | score={hit['score']:.4f} "
                f"| doc_id={hit['metadata']['doc_id']}"
            )
        if llm is not None:
            answer = KnowledgeBaseAgent(search_store, llm).answer(question, top_k=3)
            block.append(f"agent_answer: {answer}")
        lines.extend(block)
        # Save each completed paid call, so a later API error does not erase
        # the answers. A run without --llm cannot replace this evidence.
        if llm is not None:
            REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(block), flush=True)
    if llm is not None:
        print(f"\nSaved: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
