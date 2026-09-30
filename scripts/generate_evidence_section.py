"""Generate the README's inline ask-mode evidence section from the saved cards.

The assignment requires the README itself to *show* the retrieved passages and
source paths, the actual answers with citations, and the unsupported question's
retrieved context and refusal -- not merely link to them. Generating that section
from the evidence JSON keeps it honest: nothing here is retyped by hand, so it
cannot drift from what the harness actually produced.
"""

from __future__ import annotations

import glob
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The single passage that decides each test, and how far into it the key line is.
# Named explicitly so the excerpt shown is the evidence, not the first 400 chars.
KEY_PHRASES = {
    "test-1": "Global participation",
    "test-2": "More than three absences",
    "test-3": "Day: Wednesdays",
    "test-4": None,
}

SUPPORT_NOTES = {
    "test-1": (
        "**Do the cited passages support the claim?** Yes. `[S4]` is the generated note's "
        "Grading section and `[S5]` the note header, both tracing to page 2 of the original, "
        "which reads `Global participation (attendance, punctuality, engagement, quality of "
        "discussion) | Weekly | 40` and then `Participation (40 points)`. The figure and all "
        "four listed components are in the cited text. The model misspells the course as "
        "\"Negotiaions\" in its own prose; the harness flags that (`spelling flags`) and does "
        "**not** rewrite it, because a saved answer must be exactly what the model said."
    ),
    "test-2": (
        "**Do the cited passages support the claim?** The number and the citation are correct: "
        "`[S1]`/`[S5]` contain `More than three absences will adversely affect the class "
        "contribution grade`. **But I mark this PARTIAL by hand even though it passes the "
        "machine check.** The sentence inverts the rule — it reads as permission to miss more "
        "than three, when more than three is exactly what costs you. A mechanical citation "
        "check cannot evaluate the direction of a threshold, which is precisely why the "
        "passage is printed here."
    ),
    "test-3": (
        "**Do the cited passages support the claim?** Yes, and both sources were used. `[S1]` "
        "is the Negotiations syllabus page 1; `[S4]`–`[S6]` are the Data Mining syllabus page 1. "
        "It correctly **excluded** the two Tuesday courses, whose passages were retrieved as "
        "deliberate distractors and left uncited. PARTIAL only because my written expectation "
        "asked for the courses to be named, and it identifies Negotiations solely by its course "
        "code, dropping the rooms that were present in the passages."
    ),
    "test-4": (
        "**Is the refusal correct?** Yes. The Asset Management syllabus names only "
        "`Instructor: Sam Olesky`; searching its extracted text for GSI, GSR, assistant, reader "
        "and TA returns only an unrelated `gsi.berkeley.edu` plagiarism URL. Note the retrieved "
        "context above: **every passage is from Asset Management**. That is the course filter "
        "working — before it existed, the Negotiations syllabus was retrieved here and the "
        "model reported its GSI, Oranda Hou, as Asset Management's."
    ),
}


def excerpt(text: str, phrase: str | None, width: int = 420) -> str:
    body = text.strip()
    if phrase and phrase in body:
        start = max(0, body.index(phrase) - 120)
        body = ("…" if start else "") + body[start : start + width]
        return body.rstrip() + " …"
    return body[:width].rstrip() + (" …" if len(text) > width else "")


def card(test_id: str) -> dict:
    matches = sorted(glob.glob(str(ROOT / f"evidence/ask/{test_id}-*.json")))
    if not matches:
        raise SystemExit(f"no evidence card for {test_id}")
    return json.loads(Path(matches[0]).read_text())


def card_link(test_id: str) -> str:
    md = sorted(glob.glob(str(ROOT / f"evidence/ask/{test_id}-*.md")))[0]
    return Path(md).relative_to(ROOT).as_posix()


def render(test_id: str, kind: str, machine: str, human: str) -> str:
    d = card(test_id)
    link = card_link(test_id)
    lines = [
        f"#### {test_id} — {kind}",
        "",
        f"> **{d['question']}**",
        "",
        f"`{d['model']}` · execution **{d['execution']}** · {d['runtime']} · "
        f"embeddings `{d['embed_model']}` · temperature "
        f"{d['model_options'].get('temperature')} · top_k {d['top_k']}  ",
        f"Machine verdict **{machine}** · my verdict **{human}** · "
        f"retrieval {d['timing_seconds']['retrieval']} s, generation "
        f"{d['timing_seconds']['generation']} s",
        "",
    ]
    if d.get("retrieval_scope_note"):
        lines += [f"*Retrieval scope:* {d['retrieval_scope_note']}", ""]

    lines += ["**Retrieved passages and source paths**", "",
              "| | Source path | Where | Layer | Matched by |", "|---|---|---|---|---|"]
    for item in d["retrieved"]:
        where = f"page {item['page']}" if item["page"] else "section"
        lines.append(
            f"| `{item['label']}` | `{item['source_path']}` | {where} — "
            f"*{item['section']}* | {item['source_type']} | {item['why_retrieved']} |"
        )
    lines.append("")

    phrase = KEY_PHRASES.get(test_id)
    if phrase:
        hit = next((i for i in d["retrieved"] if phrase in i["text"]), None)
        if hit:
            where = f"page {hit['page']}" if hit["page"] else "section"
            lines += [
                f"The decisive passage, `{hit['label']}` — `{hit['source_path']}`, {where}:",
                "", "```text", excerpt(hit["text"], phrase), "```", "",
            ]

    lines += ["**Actual answer from local Gemma**", "", "```text", d["answer"].strip(), "```", ""]
    check = d["citations"]
    lines += [
        f"**Citation check:** {'PASS' if check['passes_machine_check'] else 'REVIEW'} — "
        f"{check['machine_check']}",
        "",
        textwrap.fill(SUPPORT_NOTES[test_id], 88),
        "",
        f"Full card, with every passage in full: [`{link}`]({link.replace(' ', '%20')})",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    meta = [
        ("test-1", "a direct question answered by one source", "PASS", "PASS"),
        ("test-2", "answerable, deliberately reworded away from the source", "PASS", "**PARTIAL**"),
        ("test-3", "answerable, spans two sources", "PARTIAL", "PARTIAL"),
        ("test-4", "a plausible question the wiki cannot answer", "PASS", "PASS"),
    ]
    out = "\n".join(render(*m) for m in meta)
    target = ROOT / "evidence" / "ask" / "INLINE-README-SECTION.md"
    target.write_text(out, encoding="utf-8")
    print(f"generated {len(out.splitlines())} lines -> {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
