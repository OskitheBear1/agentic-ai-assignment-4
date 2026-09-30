"""Citation checking.

A citation is only worth something if it points at a passage that was actually
retrieved. The harness verifies that mechanically after every generated answer:
markers the model invented are reported as unsupported, and an answer with no
marker at all is reported as uncited. It does NOT claim to verify that the
passage semantically supports the sentence -- that judgement stays with the
human reading the evidence card, which is why the card prints the passages.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .retrieval import Hit

_MARKER = re.compile(r"\[S(\d+)\]")
_PROPER_NOUN = re.compile(r"\b[A-Z][a-z]{3,}\b")
INSUFFICIENT = "INSUFFICIENT EVIDENCE"
CLOSEST = "CLOSEST AVAILABLE"


@dataclass
class CitationReport:
    cited: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    unused: list[str] = field(default_factory=list)
    declared_insufficient: bool = False
    uncited_answer: bool = False
    contract_violations: list[str] = field(default_factory=list)
    spelling_flags: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        if self.contract_violations:
            return False
        if self.declared_insufficient:
            return not self.unsupported
        return not self.unsupported and not self.uncited_answer

    def summary(self) -> str:
        if self.contract_violations:
            return "FAIL: " + "; ".join(self.contract_violations)
        if self.declared_insufficient:
            base = "declared insufficient evidence (no citation required)"
        elif self.uncited_answer:
            base = "FAIL: answer makes claims with no citation marker"
        else:
            base = f"cited {', '.join(self.cited)}"
        if self.unsupported:
            base += f" | FAIL: invented markers {', '.join(self.unsupported)}"
        if self.unused and not self.declared_insufficient:
            base += f" | unused retrieved passages: {', '.join(self.unused)}"
        if self.spelling_flags:
            base += (" | spelling flags (in the answer, absent from every cited "
                     f"passage): {', '.join(self.spelling_flags)}")
        return base


def check(answer: str, hits: list[Hit]) -> CitationReport:
    """Mechanical checks only. Whether a passage *supports* a sentence stays a
    human judgement, which is why the evidence card prints the passages."""
    available = {hit.label for hit in hits}
    found = [f"S{n}" for n in dict.fromkeys(_MARKER.findall(answer))]
    upper = answer.upper()
    declared = INSUFFICIENT in upper
    report = CitationReport(declared_insufficient=declared)
    report.cited = [m for m in found if m in available]
    report.unsupported = [m for m in found if m not in available]
    report.unused = sorted(available - set(found), key=lambda s: int(s[1:]))
    report.uncited_answer = not found and not declared

    # The research rules define exactly two reply forms. A reply that mixes them
    # is a mode-contract violation, not a merely imperfect answer: it asserts a
    # fact and disclaims it in the same breath.
    answered = "ANSWER:" in re.sub(r"[*_`]", "", upper)
    if answered and declared:
        report.contract_violations.append(
            "reply uses both ANSWER: and INSUFFICIENT EVIDENCE:")
    elif answered and CLOSEST in upper:
        report.contract_violations.append(
            "reply follows ANSWER: with a 'Closest available:' line, which belongs "
            "only to an insufficient-evidence reply")
    elif not answered and not declared:
        report.contract_violations.append(
            "reply begins with neither ANSWER: nor INSUFFICIENT EVIDENCE:")

    # Proper nouns the model produced that appear in no cited passage. Reported,
    # never rewritten: the saved answer must stay exactly what the model said.
    passage_words = {
        w.lower() for hit in hits for w in _PROPER_NOUN.findall(hit.passage.text)
    }
    body = _MARKER.sub(" ", answer)
    flagged = [
        w for w in dict.fromkeys(_PROPER_NOUN.findall(body))
        if w.lower() not in passage_words
        and w.upper() not in {"ANSWER", "INSUFFICIENT", "EVIDENCE", "CLOSEST",
                              "AVAILABLE", "ANSWER:"}
    ]
    report.spelling_flags = flagged[:8]
    return report


def resolve(markers: list[str], hits: list[Hit]) -> list[Hit]:
    by_label = {hit.label: hit for hit in hits}
    return [by_label[m] for m in markers if m in by_label]
