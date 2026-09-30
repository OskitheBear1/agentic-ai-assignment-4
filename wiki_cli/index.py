"""The retrieval tool: build a local index, then search it.

Two independent signals are combined:

* **BM25** (implemented here, ~40 lines) is a keyword score. It is excellent at
  exact tokens -- course codes, room numbers, point totals -- which is most of
  what a syllabus question is about.
* **Dense vectors** from the local ``embeddinggemma`` model score meaning
  rather than spelling, so a question phrased differently from the source still
  matches.

They are fused with Reciprocal Rank Fusion, which combines rankings instead of
raw scores and so needs no score normalisation between two incomparable scales.

No part of this touches the network except the call to Ollama on 127.0.0.1.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from . import config, model
from .documents import Passage, chunk_source, file_sha256, human_title, repo_relative

_TOKEN = re.compile(r"[a-z0-9]+(?:\.[a-z0-9]+)*")
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "for", "on",
    "what", "which", "how", "does", "do", "did", "with", "that", "this", "it",
    "be", "as", "at", "by", "from", "my", "i", "you", "we", "can", "will",
}


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOPWORDS]


# --------------------------------------------------------------------------
# BM25
# --------------------------------------------------------------------------

@dataclass
class Bm25:
    """Classic BM25 over the passage collection. k1/b are the standard defaults."""

    documents: list[list[str]]
    k1: float = 1.5
    b: float = 0.75

    def __post_init__(self) -> None:
        self.lengths = [len(d) for d in self.documents]
        self.avg_length = (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0
        self.term_frequencies = [Counter(d) for d in self.documents]
        document_frequency: Counter[str] = Counter()
        for doc in self.documents:
            document_frequency.update(set(doc))
        total = len(self.documents)
        self.idf = {
            term: math.log(1 + (total - count + 0.5) / (count + 0.5))
            for term, count in document_frequency.items()
        }

    def score(self, query_tokens: list[str]) -> list[float]:
        scores = [0.0] * len(self.documents)
        for term in query_tokens:
            idf = self.idf.get(term)
            if idf is None:
                continue
            for i, frequencies in enumerate(self.term_frequencies):
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                denominator = frequency + self.k1 * (
                    1 - self.b + self.b * self.lengths[i] / (self.avg_length or 1)
                )
                scores[i] += idf * frequency * (self.k1 + 1) / denominator
        return scores


# --------------------------------------------------------------------------
# Vector helpers (pure Python -- the corpus is small enough not to need numpy)
# --------------------------------------------------------------------------

def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


# --------------------------------------------------------------------------
# Building and loading
# --------------------------------------------------------------------------

def collect_passages(include_wiki: bool = True) -> list[Passage]:
    """Chunk every original source, and every curated wiki note.

    Both layers are indexed but tagged by ``source_type``, so ask mode can
    prefer the unchanged original as the citation target while still letting a
    curated note surface the topic.
    """
    passages: list[Passage] = []
    for path in sorted(config.RAW_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".pdf", ".md", ".txt", ".markdown"}:
            passages.extend(chunk_source(path, "raw"))
    if include_wiki:
        # Only the course notes are indexed. Topic hubs, People notes and
        # index.md are navigation: their content is links and blurbs, which
        # retrieved well and cited nothing.
        for path in sorted((config.WIKI_DIR / "Courses").rglob("*.md")):
            passages.extend(chunk_source(path, "wiki"))
    return passages


def build(verbose: bool = True, embed: bool = True) -> dict:
    """Rebuild the whole index from the vault. Idempotent by construction:
    the index is derived state, so re-running it can never create duplicates."""
    config.ensure_dirs()
    passages = collect_passages()
    if not passages:
        raise RuntimeError(
            f"No sources found under {config.RAW_DIR}. Put .pdf/.md/.txt files there first."
        )
    with config.CHUNKS_FILE.open("w", encoding="utf-8") as handle:
        for passage in passages:
            handle.write(json.dumps(passage.to_dict(), ensure_ascii=False) + "\n")

    vectors_written = 0
    if embed:
        if verbose:
            print(f"  embedding {len(passages)} passages with {config.LOCAL_EMBED_MODEL} ...")
        batch_size = 16
        with config.VECTORS_FILE.open("w", encoding="utf-8") as handle:
            for start in range(0, len(passages), batch_size):
                batch = passages[start : start + batch_size]
                vectors = model.embed_local([p.text for p in batch])
                for passage, vector in zip(batch, vectors):
                    handle.write(
                        json.dumps({"chunk_id": passage.chunk_id, "v": vector}) + "\n"
                    )
                    vectors_written += 1
    elif config.VECTORS_FILE.exists():
        config.VECTORS_FILE.unlink()

    catalog = build_catalog(passages)
    config.CATALOG_FILE.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return {
        "passages": len(passages),
        "vectors": vectors_written,
        "sources": len(catalog),
        "raw_passages": sum(1 for p in passages if p.source_type == "raw"),
        "wiki_passages": sum(1 for p in passages if p.source_type == "wiki"),
    }


def build_catalog(passages: list[Passage]) -> list[dict]:
    """The source catalog: the machine-id side of the readable-note mapping."""
    by_source: dict[str, dict] = {}
    for passage in passages:
        entry = by_source.setdefault(
            passage.source_id,
            {
                "source_id": passage.source_id,
                "source_path": passage.source_path,
                "source_title": passage.source_title,
                "source_type": passage.source_type,
                "original_filename": Path(passage.source_path).name,
                "passages": 0,
                "pages": 0,
            },
        )
        entry["passages"] += 1
        if passage.page:
            entry["pages"] = max(entry["pages"], passage.page)
    for entry in by_source.values():
        path = config.ROOT / entry["source_path"]
        if path.exists():
            entry["sha256"] = file_sha256(path)
            entry["bytes"] = path.stat().st_size
    return sorted(by_source.values(), key=lambda e: e["source_path"])


def load_passages() -> list[Passage]:
    if not config.CHUNKS_FILE.exists():
        raise RuntimeError(
            "No retrieval index yet. Build it with:\n"
            "  ./wiki ingest ./vault/raw        (generate notes + index)\n"
            "  ./wiki reindex                   (index only, no model needed)"
        )
    passages = []
    with config.CHUNKS_FILE.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                passages.append(Passage(**json.loads(line)))
    return passages


def load_vectors() -> dict[str, list[float]]:
    if not config.VECTORS_FILE.exists():
        return {}
    vectors = {}
    with config.VECTORS_FILE.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                record = json.loads(line)
                vectors[record["chunk_id"]] = record["v"]
    return vectors
