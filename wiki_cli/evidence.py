"""Saved outputs. Every run can be inspected later without rerunning the model.

Evidence lives OUTSIDE the vault so that generated test records can never be
retrieved as if they were source material -- that is the "answer key" trap the
assignment warns about.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from . import config


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _slug(text: str, limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit] or "untitled"


def save_json(subdir: str, prefix: str, record: dict) -> str:
    directory = config.EVIDENCE_DIR / subdir
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{_stamp()}-{prefix}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path.relative_to(config.ROOT))


def save_ask_card(record: dict) -> str:
    """Write the ask-mode evidence card as both JSON and readable Markdown."""
    directory = config.EVIDENCE_DIR / "ask"
    directory.mkdir(parents=True, exist_ok=True)
    name = f"{record.get('test_id') or _stamp()}-{_slug(record['question'])}"
    (directory / f"{name}.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (directory / f"{name}.md").write_text(render_ask_card(record), encoding="utf-8")
    return str((directory / f"{name}.md").relative_to(config.ROOT))


def render_ask_card(record: dict) -> str:
    citation = record["citations"]
    lines = [
        f"# Ask-mode evidence card — {record.get('test_id') or 'ad hoc'}",
        "",
        f"**Question:** {record['question']}",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Mode | `ask` (standalone; chat history not used) |",
        f"| Execution | **{record['execution']}** |",
        f"| Generation model | `{record['model']}` |",
        f"| Embedding model | `{record['embed_model']}` |",
        f"| Runtime | {record['runtime']} |",
        f"| Retrieval scope | {record['scope']}, top_k={record['top_k']} |",
        f"| Course filter | {record.get('retrieval_scope_note') or 'not applied (no single course named)'} |",
        f"| Retrieval time | {record['timing_seconds']['retrieval']} s |",
        f"| Generation time | {record['timing_seconds']['generation']} s |",
        f"| Tokens | {record['tokens']['prompt']} prompt / {record['tokens']['completion']} completion |",
        f"| Run at | {datetime.now().isoformat(timespec='seconds')} |",
        "",
        "## Retrieved passages",
        "",
    ]
    if not record["retrieved"]:
        lines.append("_No passages matched._")
    for item in record["retrieved"]:
        where = f"page {item['page']}" if item["page"] else "section"
        lines += [
            f"### [{item['label']}] `{item['source_path']}` — {where}",
            f"*section:* {item['section']} · *layer:* {item['source_type']} · "
            f"*matched by:* {item['why_retrieved']} · *chunk:* `{item['chunk_id']}`",
            "",
            "```text",
            item["text"],
            "```",
            "",
        ]
    lines += [
        "## Actual answer from the model",
        "",
        "```text",
        record["answer"] or "(empty response)",
        "```",
        "",
        "## Citation check",
        "",
        f"- Machine check: **{'PASS' if citation['passes_machine_check'] else 'REVIEW'}** — "
        f"{citation['machine_check']}",
        f"- Markers resolving to a retrieved passage: "
        f"{', '.join(citation['cited']) or 'none'}",
        f"- Markers the model invented: {', '.join(citation['unsupported']) or 'none'}",
        f"- Declared insufficient evidence: {citation['declared_insufficient']}",
        f"- Reply-form contract violations: "
        f"{'; '.join(citation.get('contract_violations') or []) or 'none'}",
        f"- Proper nouns in the answer absent from every cited passage: "
        f"{', '.join(citation.get('spelling_flags') or []) or 'none'}",
        "",
        "> The machine check verifies that every citation marker points at a passage that",
        "> was actually retrieved. Whether the passage *supports* the sentence is a human",
        "> judgement — the full passage text is printed above so it can be checked.",
        "",
    ]
    return "\n".join(lines)


def save_chat_transcript(transcript: list[dict], execution_mode: str) -> str:
    directory = config.EVIDENCE_DIR / "modes"
    directory.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    (directory / f"{stamp}-chat-session.json").write_text(
        json.dumps(
            {"execution": execution_mode, "saved_at": datetime.now().isoformat(),
             "turns": transcript},
            indent=2, ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    lines = [
        f"# Chat-mode transcript ({execution_mode})",
        "",
        f"_Saved {datetime.now().isoformat(timespec='seconds')}_",
        "",
    ]
    for turn in transcript:
        kind = turn.get("kind")
        if kind == "chat":
            lines += [
                f"**you>** {turn['message']}",
                "",
                f"`[retrieval {'ON' if turn['retrieved'] else 'OFF'} — {turn['retrieval_reason']}]`",
                "",
            ]
            for hit in turn.get("hits", []):
                lines.append(f"- retrieved `[{hit['label']}]` {hit['locator']}")
            if turn.get("hits"):
                lines.append("")
            lines += [f"**archivist>** {turn['reply']}", "",
                      f"_({turn['seconds']}s, {turn['model']})_", "", "---", ""]
        elif kind == "ask":
            lines += [f"**you>** /ask {turn['question']}", "",
                      "`[ask mode — fresh context, conversation not used]`", "",
                      f"**answer>** {turn['answer']}", "",
                      f"_citation check: {turn['citations']}_", "", "---", ""]
        elif kind == "search":
            lines += [f"**you>** /search {turn['query']}", "",
                      f"`[search mode — {turn['results']} passages, no generated answer]`",
                      "", "---", ""]
    path = directory / f"{stamp}-chat-session.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path.relative_to(config.ROOT))
