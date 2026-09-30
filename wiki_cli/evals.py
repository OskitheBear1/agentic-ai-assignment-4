"""`wiki test` — run the fixed four-question eval set and report against the
expectations written down before the harness existed.

An eval here is: a fixed question, a written expectation, and the system's
actual result. This module does not score the answer for you; it reports the
mechanical checks (did the expected source get retrieved, did the answer contain
the expected string, did the citations resolve) and writes the full evidence card
so the human judgement is made against the passages, not against a summary.
"""

from __future__ import annotations

import json
from datetime import datetime

from . import config, evidence
from .modes import ask

QUESTIONS_FILE = config.ROOT / "tests" / "eval_questions.json"


def load_tests() -> list[dict]:
    if not QUESTIONS_FILE.exists():
        raise RuntimeError(f"Missing eval set at {QUESTIONS_FILE}")
    return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))["tests"]


def assess(test: dict, record: dict) -> dict:
    retrieved_paths = {item["source_path"] for item in record["retrieved"]}
    expected = set(test["expected_sources"])
    answer_upper = (record["answer"] or "").upper()
    missing_strings = [
        s for s in test["expected_answer_contains"] if s.upper() not in answer_upper
    ]
    return {
        "expected_sources_retrieved": sorted(expected & retrieved_paths),
        "expected_sources_missing": sorted(expected - retrieved_paths),
        "retrieval_ok": expected.issubset(retrieved_paths),
        "answer_contains_expected": not missing_strings,
        "missing_expected_strings": missing_strings,
        "citations_resolve": record["citations"]["passes_machine_check"],
        "declared_insufficient": record["citations"]["declared_insufficient"],
    }


def verdict(test: dict, assessment: dict) -> str:
    if test["id"] == "test-4":
        return "PASS" if assessment["declared_insufficient"] else "FAIL"
    checks = (
        assessment["retrieval_ok"],
        assessment["answer_contains_expected"],
        assessment["citations_resolve"],
    )
    if all(checks):
        return "PASS"
    return "PARTIAL" if any(checks) else "FAIL"


def run(only: str | None = None, execution_mode: str = "local") -> int:
    tests = [t for t in load_tests() if not only or t["id"] == only]
    if not tests:
        print(f"No test matching '{only}'.")
        return 1

    print(f"\033[1mASK-MODE EVAL SET\033[0m  {len(tests)} test(s), execution={execution_mode}")
    print(f"expectations from {QUESTIONS_FILE.relative_to(config.ROOT)} "
          "(outside the vault, not retrievable)\n")

    results = []
    for test in tests:
        print("=" * 78)
        print(f"\033[1m{test['id']}\033[0m — {test['kind']}")
        print(f"expected: {test['expected_behavior']}")
        record = ask.run(
            test["question"], execution_mode=execution_mode, test_id=test["id"]
        )
        assessment = assess(test, record)
        status = verdict(test, assessment)
        colour = {"PASS": "32", "PARTIAL": "33", "FAIL": "31"}[status]
        print(f"\033[1mVerdict\033[0m \033[{colour}m{status}\033[0m")
        print(f"  expected source retrieved: {assessment['retrieval_ok']}"
              + (f"  (missing: {', '.join(assessment['expected_sources_missing'])})"
                 if assessment["expected_sources_missing"] else ""))
        print(f"  answer contains expected text: {assessment['answer_contains_expected']}"
              + (f"  (missing: {assessment['missing_expected_strings']})"
                 if assessment["missing_expected_strings"] else ""))
        print(f"  citations resolve: {assessment['citations_resolve']}")
        print(f"  evidence card: {record.get('evidence_card')}")
        print()
        results.append(
            {"test": test, "assessment": assessment, "verdict": status,
             "record": record}
        )

    summary = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "execution": execution_mode,
        "model": results[0]["record"]["model"] if results else None,
        "embed_model": config.LOCAL_EMBED_MODEL,
        "results": [
            {
                "id": r["test"]["id"],
                "question": r["test"]["question"],
                "verdict": r["verdict"],
                "assessment": r["assessment"],
                "answer": r["record"]["answer"],
                "retrieved": [
                    {"label": i["label"], "source_path": i["source_path"],
                     "page": i["page"], "section": i["section"]}
                    for i in r["record"]["retrieved"]
                ],
                "citation_check": r["record"]["citations"]["machine_check"],
                "timing_seconds": r["record"]["timing_seconds"],
                "evidence_card": r["record"].get("evidence_card"),
            }
            for r in results
        ],
    }
    path = evidence.save_json("ask", "eval-summary", summary)
    print("=" * 78)
    tally = {v: sum(1 for r in results if r["verdict"] == v) for v in ("PASS", "PARTIAL", "FAIL")}
    print(f"\033[1mSUMMARY\033[0m  "
          + "  ".join(f"{k} {v}" for k, v in tally.items() if v))
    for r in results:
        print(f"  {r['test']['id']:<8} {r['verdict']:<8} {r['test']['question']}")
    print(f"\nsummary written to {path}")
    return 0 if tally["FAIL"] == 0 else 1
