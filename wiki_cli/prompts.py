"""Prompt assembly. Each mode loads its own instruction file and builds its own
prompt shape -- this is where the mode boundary is actually enforced.

The model reads nothing from disk by itself. Everything it sees was put in front
of it here, on purpose.
"""

from __future__ import annotations

from functools import lru_cache

from . import config
from .retrieval import Hit, format_evidence_block

_TOPIC_ENUM = (
    "Grading and Assessment",
    "Attendance and Absences",
    "Fall 2026 Schedule",
    "Required Readings",
    "Assignments and Deadlines",
    "Course Policies",
)


@lru_cache(maxsize=8)
def load_instructions(name: str) -> str:
    path = config.INSTRUCTIONS_DIR / name
    if not path.exists():
        raise RuntimeError(
            f"Missing instruction file {path}.\n"
            "The harness will not guess a persona or research rules."
        )
    return path.read_text(encoding="utf-8").strip()


# --- ask ------------------------------------------------------------------

def build_ask_prompt(question: str, hits: list[Hit]) -> tuple[str, str]:
    """ask gets research rules + evidence ONLY. No persona, no chat history."""
    system = load_instructions("wiki-instructions.md")
    if hits:
        evidence = format_evidence_block(hits)
    else:
        evidence = "(no passages matched this question)"
    user = (
        "PASSAGES\n"
        "========\n"
        f"{evidence}\n\n"
        "QUESTION\n"
        "========\n"
        f"{question}\n\n"
        "Answer from the passages above only, citing markers like [S1]."
    )
    return system, user


# --- chat -----------------------------------------------------------------

def build_chat_prompt(
    message: str, history: list[dict], hits: list[Hit] | None
) -> tuple[str, str]:
    """chat gets persona + recent conversation, and evidence only when the
    harness decided the turn needed it."""
    system = load_instructions("persona.md")
    parts: list[str] = []
    recent = history[-2 * config.CHAT_HISTORY_TURNS :]
    if recent:
        parts.append("CONVERSATION SO FAR (for follow-ups; not source evidence)")
        parts.append("=========================================================")
        for turn in recent:
            speaker = "Jonathan" if turn["role"] == "user" else "Archivist"
            parts.append(f"{speaker}: {turn['content']}")
        parts.append("")
    if hits:
        parts.append("RETRIEVED WIKI EVIDENCE (cite these as [S1], [S2] ...)")
        parts.append("======================================================")
        parts.append(format_evidence_block(hits, max_chars=3000))
        parts.append("")
    else:
        parts.append(
            "NOTE: no notes were retrieved for this turn. Answer conversationally "
            "from the persona and the conversation above. Do not claim wiki facts, "
            "and do not say the evidence is insufficient. Write no [S1]-style "
            "citation markers at all -- there are no passages for them to point at, "
            "so any marker you write would be fabricated."
        )
        parts.append("")
    parts.append(f"Jonathan: {message}")
    parts.append("Archivist:")
    return system, "\n".join(parts)


ROUTER_SYSTEM = (
    "You decide whether a chat turn needs a lookup in a personal course wiki.\n"
    "The wiki holds four Fall 2026 Berkeley Haas syllabi: Agentic AI (MBA 290T), "
    "Asset Management (MBA 233), Data Mining (MBA 247), Negotiations (MBA 252).\n"
    "Answer with exactly one word: SEARCH or CHAT.\n"
    "SEARCH when the turn asks for a specific fact recorded in a syllabus -- a "
    "grade weight, a date, a deadline, a room, a reading, a policy, an instructor.\n"
    "CHAT when the turn is small talk, a question about your own capabilities, a "
    "request to brainstorm, draft, plan, shorten, rewrite or continue previous "
    "work, or anything answerable from the conversation itself.\n"
    "CHAT also when the turn is the user telling you something rather than asking "
    "you something -- 'remember that ...', 'note that ...', 'for the record ...'. "
    "A statement is not a lookup.\n"
    "One word only."
)


def build_router_prompt(message: str, history: list[dict]) -> tuple[str, str]:
    tail = history[-2:]
    context = "\n".join(f"{t['role']}: {t['content'][:200]}" for t in tail)
    user = (
        (f"Recent turns:\n{context}\n\n" if context else "")
        + f"New turn: {message}\n\nSEARCH or CHAT?"
    )
    return ROUTER_SYSTEM, user


# --- ingest ---------------------------------------------------------------

# The fixed section vocabulary. Constraining these in the schema is what stopped
# the model transcribing a 22-row reading table into 22 one-line sections while
# omitting the grading breakdown entirely.
SECTION_HEADINGS = (
    "Logistics",
    "Grading",
    "Attendance and Lateness",
    "Assignments and Deadlines",
    "Readings and Materials",
    "Schedule Highlights",
)

# The ingestion note contract, expressed as a schema so the runtime enforces it
# instead of the prompt merely requesting it. Kept next to the prose rules in
# instructions/ingest-instructions.md, which explains each field.
NOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "folder": {"type": "string", "enum": list(config.WIKI_FOLDERS)},
        "summary": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string", "enum": list(SECTION_HEADINGS)},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["heading", "bullets"],
            },
        },
        "topics": {
            "type": "array",
            "items": {"type": "string", "enum": list(_TOPIC_ENUM)},
        },
        "people": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "role": {"type": "string"}},
                "required": ["name", "role"],
            },
        },
    },
    "required": ["title", "folder", "summary", "sections", "topics", "people"],
}


def build_ingest_prompt(source_title: str, source_text: str, budget: int) -> tuple[str, str]:
    system = load_instructions("ingest-instructions.md")
    excerpt = source_text[:budget]
    truncated = len(source_text) > budget
    user = (
        f"SOURCE DOCUMENT: {source_title}\n"
        f"{'(first ' + str(budget) + ' characters; the document continues)' if truncated else '(complete document)'}\n"
        "==================================================================\n"
        f"{excerpt}\n"
        "==================================================================\n\n"
        "Produce the JSON note object described in your instructions."
    )
    return system, user
