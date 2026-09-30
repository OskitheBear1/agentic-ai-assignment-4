"""chat mode: the personal assistant. Persona + conversation context, and
retrieval only when the turn actually needs a recorded fact.

The retrieval decision is made in two stages, cheapest first:

1. A rule pass catches the cases that must never trigger a lookup -- questions
   about the assistant's own capabilities, greetings, and follow-up edits like
   "make that shorter" that refer to the conversation rather than the wiki.
2. Anything still ambiguous goes to a one-word Gemma classifier.

This is the mechanism behind the mode boundary the assignment asks about: chat
answering "what can you help me with?" does no search at all, so it cannot
produce unrelated citations or an insufficient-evidence refusal.
"""

from __future__ import annotations

import re
import time

from .. import citations, config, evidence, model, prompts, retrieval

CHAT_TOP_K = 4

# Turns that are about the assistant itself, or about the conversation, never
# about a syllabus fact.
_NEVER_RETRIEVE = re.compile(
    r"\b("
    r"what can (you|we) (help|do)|what can you help me with|what do you do|"
    r"who are you|what are you|your capabilities|how do you work|what modes|"
    r"help me understand what you|"
    r"make (that|it) (shorter|longer|tighter|punchier|simpler)|shorten (that|it)|"
    r"rewrite (that|it)|try again|cut (that|it) down|expand (that|it)|"
    r"thanks|thank you|hello|hi there|hey|good morning|nice work|got it|"
    r"never mind|forget it"
    r")\b",
    re.I,
)

# The user telling the assistant something is not a request to search the wiki.
# Without this the router searched, retrieved an unrelated passage, and the model
# reported the user's own sentence as though a source had stated it.
_ASSERTION = re.compile(
    r"^\s*(remember (that|this)|note that|for the record|fyi|just so you know|"
    r"keep in mind that|i (just )?(told|want) you)\b", re.I
)

# Turns that clearly want a recorded fact.
_ALWAYS_RETRIEVE = re.compile(
    r"\b("
    r"how many points|what percent|percentage|weight(ed|ing)?|grade breakdown|"
    r"when is|what time|which room|where is|what room|due date|deadline|"
    r"required reading|textbook|office hours|instructor|professor|gsi|"
    r"how many absences|attendance policy|syllabus says|according to"
    r")\b",
    re.I,
)

BANNER = """\033[1mArchivist\033[0m — local study assistant for your Fall 2026 Haas courses
model: {model} ({execution})   wiki: {notes} notes, {passages} indexed passages

This is chat mode: conversational, uses the current conversation, and looks up
your notes only when a turn needs a recorded fact.
  For a checked factual answer   ->  \033[1m/ask <question>\033[0m   (or exit and run `./wiki ask "..."`)
  To see raw source passages     ->  \033[1m/search <terms>\033[0m
  Commands                       ->  \033[1m/help\033[0m   \033[1m/save\033[0m   \033[1m/reset\033[0m   \033[1m/exit\033[0m
"""

SESSION_HELP = """\033[1mChat commands\033[0m
  /ask <question>    run one standalone ask-mode query (fresh context, citations)
  /search <terms>    show original passages, no generated answer
  /save              write this transcript to evidence/modes/
  /reset             clear the conversation context
  /help              this list
  /exit  /quit       leave chat

\033[1mWhat chat will and will not do\033[0m
  It will brainstorm, draft, plan, and revise its own drafts using this conversation.
  It will look up your syllabi when a turn needs a recorded fact, and cite them.
  It will not invent a fact about your courses, and it will not treat something it
  said earlier as source evidence. Ask mode ignores this conversation entirely.
"""


def should_retrieve(message: str, history: list[dict], execution_mode: str) -> tuple[bool, str]:
    """Return (decision, why) so the transcript records the harness's reasoning."""
    text = message.strip()
    if len(text) < 3:
        return False, "rule: too short to be a factual lookup"
    if _ASSERTION.match(text):
        return False, "rule: user is asserting a fact, not asking for one"
    if _NEVER_RETRIEVE.search(text):
        return False, "rule: capability/meta/follow-up turn, answered from persona and conversation"
    if _ALWAYS_RETRIEVE.search(text):
        return True, "rule: asks for a recorded syllabus fact"
    if not text.endswith("?") and len(text.split()) < 6:
        return False, "rule: short conversational turn"
    try:
        system, user = prompts.build_router_prompt(message, history)
        completion = model.generate(system, user, config.ROUTER_OPTIONS, mode=execution_mode)
        verdict = completion.text.strip().upper()
        if verdict.startswith("SEARCH"):
            return True, f"model router: SEARCH ({completion.seconds:.2f}s)"
        return False, f"model router: CHAT ({completion.seconds:.2f}s)"
    except model.ModelUnavailable:
        return False, "router unavailable; defaulted to no retrieval"


def respond(
    message: str, history: list[dict], execution_mode: str = "local", verbose: bool = True
) -> dict:
    retrieve, why = should_retrieve(message, history, execution_mode)
    hits = retrieval.retrieve(message, top_k=CHAT_TOP_K) if retrieve else []
    if verbose:
        marker = "retrieval ON" if retrieve else "retrieval OFF"
        print(f"\033[2m[{marker} — {why}]\033[0m")
        for hit in hits:
            print(f"\033[2m  [{hit.label}] {hit.passage.locator()}\033[0m")

    system, user = prompts.build_chat_prompt(message, history, hits)
    completion = model.generate(system, user, config.CHAT_OPTIONS, mode=execution_mode)
    report = citations.check(completion.text, hits)
    return {
        "message": message,
        "retrieved": retrieve,
        "retrieval_reason": why,
        "hits": [
            {"label": h.label, "locator": h.passage.locator(), "text": h.passage.text}
            for h in hits
        ],
        "reply": completion.text,
        "seconds": round(completion.seconds, 3),
        "model": completion.model,
        "execution": completion.mode,
        "invented_citations": report.unsupported,
    }


def run(execution_mode: str = "local", verbose: bool = True) -> None:
    from .. import index
    from . import ask as ask_mode
    from . import search as search_mode

    try:
        passages = index.load_passages()
    except RuntimeError as exc:
        print(f"\033[33mwarning:\033[0m {exc}\n")
        passages = []
    notes = len(list(config.WIKI_DIR.rglob("*.md")))

    model.require_local_model(config.LOCAL_CHAT_MODEL) if execution_mode == "local" else None
    print(BANNER.format(
        model=config.LOCAL_CHAT_MODEL if execution_mode == "local" else config.ONLINE_CHAT_MODEL,
        execution=execution_mode, notes=notes, passages=len(passages),
    ))

    history: list[dict] = []
    transcript: list[dict] = []
    while True:
        try:
            line = input("\033[1myou>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            break
        if not line:
            continue
        lowered = line.lower()
        if lowered in {"/exit", "/quit", "exit", "quit"}:
            print("bye.")
            break
        if lowered == "/help":
            print(SESSION_HELP)
            continue
        if lowered == "/reset":
            history.clear()
            print("\033[2m[conversation context cleared]\033[0m")
            continue
        if lowered == "/save":
            path = evidence.save_chat_transcript(transcript, execution_mode)
            print(f"\033[2m[transcript saved to {path}]\033[0m")
            continue
        if lowered.startswith("/ask "):
            print("\033[2m[ask mode: fresh context, this conversation is not used]\033[0m")
            record = ask_mode.run(line[5:].strip(), execution_mode=execution_mode)
            transcript.append({"kind": "ask", "question": record["question"],
                               "answer": record["answer"],
                               "citations": record["citations"]["machine_check"]})
            continue
        if lowered.startswith("/search "):
            record = search_mode.run(line[8:].strip())
            transcript.append({"kind": "search", "query": record["query"],
                               "results": len(record["results"])})
            continue

        try:
            turn = respond(line, history, execution_mode, verbose=verbose)
        except model.ModelUnavailable as exc:
            print(f"\033[31merror:\033[0m {exc}\n")
            continue
        print()
        print(turn["reply"])
        if turn["invented_citations"]:
            print(f"\033[31m[citation check] invented markers: "
                  f"{', '.join(turn['invented_citations'])}\033[0m")
        print(f"\033[2m({turn['seconds']}s, {turn['model']}, {turn['execution']})\033[0m\n")
        history.append({"role": "user", "content": line})
        history.append({"role": "assistant", "content": turn["reply"]})
        transcript.append({"kind": "chat", **turn})

    if transcript:
        path = evidence.save_chat_transcript(transcript, execution_mode)
        print(f"\033[2m[transcript saved to {path}]\033[0m")
