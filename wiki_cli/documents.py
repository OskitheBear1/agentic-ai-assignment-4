"""Reading original sources and splitting them into retrievable passages.

Everything here runs locally: PDF text extraction uses ``pypdf`` (pure Python,
no network, no OCR service), and Markdown/plain text is read directly. The
offline demonstration therefore needs no parsing service of any kind.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from . import config

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
PDF_SUFFIXES = {".pdf"}

# A heading-ish line: short, no trailing sentence punctuation, and either
# ALL CAPS, Title Case, or a Markdown heading. Syllabi are heavily sectioned,
# so this recovers useful "section" labels to attach to each passage.
_MD_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*\S)\s*$")
_SENTENCE_END = (".", ",", ";", ":")


@dataclass
class Passage:
    """One retrievable unit of original text, with provenance attached."""

    chunk_id: str
    text: str
    source_path: str     # repo-relative, e.g. vault/raw/Negotiations Syllabus.pdf
    source_id: str       # stable short id from the file's content hash
    source_title: str    # human label, e.g. "Negotiations Syllabus"
    source_type: str     # "raw" or "wiki"
    page: int | None     # 1-based PDF page, or None for Markdown
    section: str         # nearest preceding heading, or "(document start)"
    order: int           # position within the document

    def locator(self) -> str:
        """Short human citation target, shown in output and evidence cards."""
        where = f"p.{self.page}" if self.page else "§"
        return f"{self.source_path} ({where}, {self.section})"

    def to_dict(self) -> dict:
        return asdict(self)


def repo_relative(path: Path) -> str:
    """Repo-relative POSIX path for citations, so evidence cards stay portable."""
    path = path.resolve()
    try:
        return path.relative_to(config.ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def short_hash(data: bytes, length: int = 10) -> str:
    return hashlib.sha256(data).hexdigest()[:length]


def file_source_id(path: Path) -> str:
    """Content-addressed id. Re-ingesting an unchanged file yields the same id,
    which is how the harness recognises a repeat and updates in place."""
    return short_hash(path.read_bytes())


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def human_title(path: Path) -> str:
    """Turn a filename into a readable source label without inventing anything."""
    stem = path.stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", stem)   # AgenticAISyllabus -> Agentic AI Syllabus
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem


# Sections of a generated note that exist for a human browsing Obsidian and
# carry no evidence: link lists and provenance boilerplate. Indexing them let
# "Related Notes" and "Source Reference" chunks outrank the actual syllabus text,
# because they repeat every course name without stating a single fact.
BOILERPLATE_SECTIONS = {
    "source reference",
    "related notes",
    "how to check a claim here",
    "courses covering this",
    "roles",
    "guest speakers",
}

_FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
_ATX = re.compile(r"^\s{0,3}#{1,6}\s+(.*\S)\s*$")


def strip_note_furniture(text: str) -> str:
    """Remove YAML front matter and boilerplate sections from a Markdown note.

    The front matter holds machine ids, hashes and tags. Left in the index it
    produced high-scoring chunks full of course names and no facts.
    """
    text = _FRONT_MATTER.sub("", text)
    kept: list[str] = []
    skipping = False
    for line in text.splitlines():
        heading = _ATX.match(line)
        if heading:
            skipping = heading.group(1).strip().lower() in BOILERPLATE_SECTIONS
            if skipping:
                continue
        if not skipping:
            kept.append(line)
    return "\n".join(kept)


def extract_pages(path: Path) -> list[tuple[int | None, str]]:
    """Return [(page_number_or_None, text)] for a supported source file."""
    suffix = path.suffix.lower()
    if suffix in TEXT_SUFFIXES:
        text = path.read_text(encoding="utf-8", errors="replace")
        if suffix in {".md", ".markdown"}:
            text = strip_note_furniture(text)
        return [(None, text)]
    if suffix in PDF_SUFFIXES:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "PDF support needs pypdf. Install it with:\n"
                "  .venv/bin/pip install -r requirements.txt"
            ) from exc
        reader = PdfReader(str(path))
        pages: list[tuple[int | None, str]] = []
        for number, page in enumerate(reader.pages, start=1):
            pages.append((number, page.extract_text() or ""))
        return pages
    raise ValueError(
        f"Unsupported source type '{suffix}' for {path.name}. "
        f"Supported: {', '.join(sorted(TEXT_SUFFIXES | PDF_SUFFIXES))}"
    )


def _looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 70:
        return False
    if _MD_HEADING.match(line):
        return True
    if stripped.endswith(_SENTENCE_END):
        return False
    words = stripped.split()
    if not 1 <= len(words) <= 9:
        return False
    if stripped.isupper():
        return True
    # Title Case-ish: most alphabetic words start with a capital.
    alpha = [w for w in words if w[:1].isalpha()]
    if not alpha:
        return False
    capitalised = sum(1 for w in alpha if w[0].isupper())
    return capitalised / len(alpha) >= 0.6


def _heading_text(line: str) -> str:
    match = _MD_HEADING.match(line)
    return (match.group(2) if match else line).strip()


def _pack(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Pack (section, line) pairs into ~CHUNK_CHARS blocks.

    Two rules matter here. First, a heading only forces a new block when the
    current block is already at least 60% full -- otherwise a densely sectioned
    syllabus collapses into dozens of one-line chunks that retrieve badly.
    Second, the tail of each block is carried into the next one, so a fact split
    across a boundary is still fully present in at least one passage.
    """
    blocks: list[tuple[str, str]] = []
    current: list[str] = []
    current_section = items[0][0] if items else ""
    size = 0
    soft_limit = int(config.CHUNK_CHARS * 0.6)
    previous_section = current_section

    def close() -> None:
        nonlocal current, size, current_section
        text = "\n".join(current).strip()
        if text:
            blocks.append((current_section, text))
        carry: list[str] = []
        carried = 0
        for line in reversed(current):
            if carried + len(line) > config.CHUNK_OVERLAP:
                break
            carry.insert(0, line)
            carried += len(line) + 1
        current = carry
        size = carried

    for section, line in items:
        section_changed = section != previous_section
        previous_section = section
        if current and ((size + len(line) + 1 > config.CHUNK_CHARS)
                        or (section_changed and size >= soft_limit)):
            close()
            current_section = section
        if not current:
            current_section = section
        current.append(line)
        size += len(line) + 1
    if current:
        text = "\n".join(current).strip()
        if text:
            blocks.append((current_section, text))
    return blocks


def _running_furniture(pages: list[tuple[int | None, str]]) -> set[str]:
    """Lines repeated across most pages are running headers/footers.

    Without this, a page header like "Delecourt - Negotiations MBA 252" wins the
    heading slot on every page and every passage gets the same useless section
    label. Requires at least 3 pages so short documents are left alone.
    """
    if len(pages) < 3:
        return set()
    counts: dict[str, int] = {}
    for _, text in pages:
        for line in {ln.strip() for ln in text.splitlines() if ln.strip()}:
            if len(line) <= 90:
                counts[line] = counts.get(line, 0) + 1
    threshold = max(2, int(len(pages) * 0.5))
    return {line for line, count in counts.items() if count >= threshold}


def chunk_source(path: Path, source_type: str) -> list[Passage]:
    """Split one file into Passages, keeping page number and section heading."""
    path = path.resolve()
    rel = repo_relative(path)
    source_id = file_source_id(path)
    title = human_title(path)
    passages: list[Passage] = []
    order = 0
    pages = extract_pages(path)
    furniture = _running_furniture(pages)
    for page_number, page_text in pages:
        section = "(document start)"
        items: list[tuple[str, str]] = []
        previous_blank = True
        lines = page_text.splitlines()
        for position, raw_line in enumerate(lines):
            line = raw_line.rstrip()
            if not line.strip():
                previous_blank = True
                continue
            if line.strip() in furniture or line.strip().isdigit():
                continue
            next_line = lines[position + 1].strip() if position + 1 < len(lines) else ""
            is_heading = (
                _looks_like_heading(line)
                and (previous_blank or _MD_HEADING.match(line))
                and not _looks_like_heading(next_line)
            )
            previous_blank = False
            if is_heading:
                section = _heading_text(line)
                items.append((section, _heading_text(line)))
                continue
            items.append((section, line))
        for block_section, block_text in _pack(items):
            order += 1
            passages.append(
                Passage(
                    chunk_id=f"{source_id}-{page_number or 0:03d}-{order:03d}",
                    text=f"[{block_section}]\n{block_text}",
                    source_path=rel,
                    source_id=source_id,
                    source_title=title,
                    source_type=source_type,
                    page=page_number,
                    section=block_section,
                    order=order,
                )
            )
    return passages
