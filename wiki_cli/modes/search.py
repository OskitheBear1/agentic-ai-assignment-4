"""search mode: show original passages and paths. No model-generated answer.

Deliberately able to run with the language model stopped -- that is how you tell
a retrieval failure apart from a generation failure. If the embedding model is
unavailable the search degrades to keyword-only and says so, rather than dying.
"""

from __future__ import annotations

import time

from .. import config, evidence, index, model, retrieval


def run(
    query: str,
    top_k: int = config.SEARCH_K,
    scope: str = "all",
    use_vectors: bool = True,
    save: bool = False,
    full: bool = False,
) -> dict:
    started = time.perf_counter()
    vectors_available = bool(index.load_vectors()) and use_vectors
    if vectors_available:
        status = model.local_runtime_status()
        if not status["reachable"]:
            print(
                "\033[33mnote:\033[0m local runtime unreachable — "
                "searching with keyword (BM25) scoring only.\n"
            )
            vectors_available = False

    hits = retrieval.retrieve(query, top_k=top_k, scope=scope, use_vectors=vectors_available)
    elapsed = time.perf_counter() - started

    print(f"\033[1mSEARCH\033[0m \"{query}\"   scope={scope}   "
          f"{'hybrid BM25+vector' if vectors_available else 'BM25 keyword only'}")
    if hits and hits[0].scope_note:
        print(f"scope: {hits[0].scope_note}")
    print(f"{len(hits)} passage(s) in {elapsed:.3f}s. No answer is generated in this mode.\n")
    for hit in hits:
        print(f"\033[1m[{hit.label}]\033[0m {hit.passage.source_path}")
        page = f"page {hit.passage.page}" if hit.passage.page else "section"
        print(f"      {page} | section: {hit.passage.section} | "
              f"{hit.passage.source_type} | {hit.why()}")
        body = hit.passage.text.strip()
        if not full and len(body) > 600:
            body = body[:600].rstrip() + " …"
        for line in body.splitlines():
            print(f"      {line}")
        print()
    if not hits:
        print("No passages matched. Try fewer or more specific words, or "
              "`./wiki reindex` if you have added sources.\n")

    record = {
        "mode": "search",
        "query": query,
        "scope": scope,
        "scope_note": hits[0].scope_note if hits else None,
        "retrieval": "hybrid BM25 + embeddinggemma vectors (RRF)"
        if vectors_available else "BM25 keyword only",
        "generated_answer": None,
        "seconds": round(elapsed, 3),
        "results": [
            {
                "label": hit.label,
                "source_path": hit.passage.source_path,
                "page": hit.passage.page,
                "section": hit.passage.section,
                "source_type": hit.passage.source_type,
                "why_retrieved": hit.why(),
                "text": hit.passage.text,
            }
            for hit in hits
        ],
    }
    if save:
        record["evidence_card"] = evidence.save_json("modes", "search", record)
    return record
