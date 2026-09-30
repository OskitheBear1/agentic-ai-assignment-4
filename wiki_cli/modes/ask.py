"""ask mode: standalone, neutral, cited factual answer. No history, no persona.

    question -> retrieve -> build prompt from research rules + passages
             -> local Gemma -> citation check -> print + save evidence card

Nothing from chat mode can reach here: the function takes a question string and
nothing else, and it loads only wiki-instructions.md.
"""

from __future__ import annotations

import time

from .. import citations, config, evidence, model, prompts, retrieval


def run(
    question: str,
    top_k: int = config.TOP_K,
    scope: str = "all",
    execution_mode: str = "local",
    save: bool = True,
    test_id: str | None = None,
    quiet: bool = False,
) -> dict:
    started = time.perf_counter()
    retrieval_started = time.perf_counter()
    hits = retrieval.retrieve(question, top_k=top_k, scope=scope)
    retrieval_seconds = time.perf_counter() - retrieval_started

    system, user = prompts.build_ask_prompt(question, hits)
    completion = model.generate(system, user, config.ASK_OPTIONS, mode=execution_mode)
    report = citations.check(completion.text, hits)

    scope_note = hits[0].scope_note if hits else None
    record = {
        "mode": "ask",
        "retrieval_scope_note": scope_note,
        "execution": completion.mode,
        "model": completion.model,
        "runtime": f"ollama {model.local_runtime_status().get('version') or 'n/a'}",
        "embed_model": config.LOCAL_EMBED_MODEL,
        "question": question,
        "scope": scope,
        "top_k": top_k,
        "retrieved": [
            {
                "label": hit.label,
                "source_path": hit.passage.source_path,
                "page": hit.passage.page,
                "section": hit.passage.section,
                "source_type": hit.passage.source_type,
                "chunk_id": hit.passage.chunk_id,
                "why_retrieved": hit.why(),
                "text": hit.passage.text,
            }
            for hit in hits
        ],
        "answer": completion.text,
        "citations": {
            "cited": report.cited,
            "unsupported": report.unsupported,
            "unused": report.unused,
            "declared_insufficient": report.declared_insufficient,
            "uncited_answer": report.uncited_answer,
            "contract_violations": report.contract_violations,
            "spelling_flags": report.spelling_flags,
            "machine_check": report.summary(),
            "passes_machine_check": report.ok,
        },
        "timing_seconds": {
            "retrieval": round(retrieval_seconds, 3),
            "generation": round(completion.seconds, 3),
            "total": round(time.perf_counter() - started, 3),
        },
        "tokens": {
            "prompt": completion.prompt_tokens,
            "completion": completion.completion_tokens,
        },
        "model_options": completion.options,
        "test_id": test_id,
    }

    if not quiet:
        _print(record, hits, report)
    if save:
        record["evidence_card"] = evidence.save_ask_card(record)
    return record


def _print(record: dict, hits, report) -> None:
    print()
    print(f"\033[1mQ:\033[0m {record['question']}")
    print(f"   mode=ask  execution={record['execution']}  model={record['model']}")
    print()
    if record.get("retrieval_scope_note"):
        print(f"\033[2mscope: {record['retrieval_scope_note']}\033[0m")
    print("\033[1mRetrieved passages\033[0m")
    if not hits:
        print("  (none)")
    for hit in hits:
        print(
            f"  [{hit.label}] {hit.passage.locator()}"
            f"  [{hit.passage.source_type}]  {hit.why()}"
        )
    print()
    print("\033[1mAnswer\033[0m")
    print(record["answer"] or "(empty response)")
    print()
    flag = "\033[32mOK\033[0m" if report.ok else "\033[31mCHECK\033[0m"
    print(f"\033[1mCitation check\033[0m [{flag}] {report.summary()}")
    for hit in citations.resolve(report.cited, hits):
        print(f"  {hit.label} -> {hit.passage.locator()}")
    timing = record["timing_seconds"]
    print(
        f"\033[2mretrieval {timing['retrieval']}s | generation {timing['generation']}s | "
        f"{record['tokens']['prompt']} prompt tok, {record['tokens']['completion']} completion tok\033[0m"
    )
