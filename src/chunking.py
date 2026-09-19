from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if not 0 <= overlap < chunk_size:
            raise ValueError("overlap must be between 0 and chunk_size - 1")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []

        # Split after the punctuation so ". ", "! ", "? ", and ".\n" stay on the sentence.
        sentences = [
            part.strip()
            for part in re.split(r"(?<=[.!?] )|(?<=\.\n)", text)
            if part.strip()
        ]
        if not sentences:
            return []

        chunks: list[str] = []
        size = self.max_sentences_per_chunk
        for i in range(0, len(sentences), size):
            chunks.append(" ".join(sentences[i : i + size]).strip())
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _hard_split(self, text: str) -> list[str]:
        return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            return self._hard_split(current_text)

        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]
        if separator == "":
            return self._hard_split(current_text)

        pieces = current_text.split(separator)
        if len(pieces) == 1:
            return self._split(current_text, next_separators)

        # A Markdown heading marker belongs to the section that follows it.
        # Other separators remain with the preceding piece. Either way, the
        # original text is preserved without dropping a boundary character.
        if separator == "\n## ":
            units = [pieces[0]] + [separator + piece for piece in pieces[1:]]
        else:
            units = [piece + separator for piece in pieces[:-1]] + [pieces[-1]]
        chunks: list[str] = []
        current = ""
        for unit in units:
            if len(unit) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(self._split(unit, next_separators))
                continue

            candidate = current + unit
            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = unit

        if current:
            chunks.append(current)
        return chunks


class HeadingSectionChunker:
    """Keep each Markdown ``##`` section together when it fits.

    Long sections use recursive splitting, with their heading repeated on every
    piece so retrieved text remains meaningful outside its original document.
    """

    def __init__(self, chunk_size: int = 600) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text.strip():
            return []

        chunks: list[str] = []
        for section in re.split(r"(?=^## )", text, flags=re.MULTILINE):
            section = section.strip()
            if not section:
                continue
            if not section.startswith("## "):
                chunks.extend(RecursiveChunker(chunk_size=self.chunk_size).chunk(section))
                continue

            heading, _, body = section.partition("\n")
            if len(heading) >= self.chunk_size:
                raise ValueError("section heading must be shorter than chunk_size")
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            budget = self.chunk_size - len(heading) - 1
            for piece in RecursiveChunker(chunk_size=budget).chunk(body.strip()):
                chunks.append(f"{heading}\n{piece.strip()}")
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("vectors must have the same number of dimensions")
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    mag_a = math.sqrt(_dot(vec_a, vec_a))
    mag_b = math.sqrt(_dot(vec_b, vec_b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size).chunk(text),
            "by_sentences": SentenceChunker().chunk(text),
            "recursive": RecursiveChunker(chunk_size=chunk_size).chunk(text),
        }
        result: dict = {}
        for name, chunks in strategies.items():
            count = len(chunks)
            avg_length = (sum(len(c) for c in chunks) / count) if count else 0.0
            result[name] = {"count": count, "avg_length": avg_length, "chunks": chunks}
        return result
