"""Turn an original source into a reviewed wiki note, then keep the vault tidy.

The flow for one source:

    raw file -> local text extraction -> ingest instructions + text -> Gemma
             -> JSON note object -> harness validates and renders Markdown
             -> vault/wiki/<Folder>/<Readable Name>.md

The harness -- not the model -- owns filenames, front matter, wikilinks, source
references, the topic hubs and index.md. Gemma supplies prose and extracted
facts; it never gets to name a file or invent a link. That is what keeps
machine-style names and broken links out of the vault.

Re-ingestion is keyed on ``source_id`` (a content hash of the original file)
via ingest_manifest.json, so ingesting the same source twice updates the same
note instead of creating a second one.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from functools import lru_cache
from datetime import date
from pathlib import Path

from . import config, model, prompts
from .documents import (
    PDF_SUFFIXES,
    TEXT_SUFFIXES,
    extract_pages,
    file_sha256,
    file_source_id,
    human_title,
    repo_relative,
)

# How much of a source is sent to Gemma in one ingestion call. Chosen against
# INGEST_OPTIONS["num_ctx"]: ~18k characters is roughly 4.5k tokens, which
# leaves room for the instructions and a 1.4k-token JSON reply inside a 12k
# context window. Longer sources are truncated and the note says so.
INGEST_CHAR_BUDGET = 18000

TOPIC_VOCABULARY = [
    "Grading and Assessment",
    "Attendance and Absences",
    "Fall 2026 Schedule",
    "Required Readings",
    "Assignments and Deadlines",
    "Course Policies",
]

TOPIC_BLURBS = {
    "Grading and Assessment": "How each course is graded: weights, point totals, and what counts.",
    "Attendance and Absences": "Absence limits, lateness, and how missing a session affects the grade.",
    "Fall 2026 Schedule": "Meeting days, times, rooms, and the term's session dates.",
    "Required Readings": "Books, chapters, and materials each course expects you to read.",
    "Assignments and Deadlines": "Deliverables, submission rules, and due dates.",
    "Course Policies": "Integrity, accommodations, recording, and other stated rules.",
}

_ILLEGAL_FILENAME = re.compile(r"[\\/:*?\"<>|\[\]#^]")
_MACHINE_NAME = re.compile(r"(\b[0-9a-f]{8,}\b|\d{4}-\d{2}-\d{2}|task[-_ ]?\d+|chunk[-_ ]?\d+)", re.I)

# Only instructional staff get their own People note. Guest speakers are listed
# inside the course note instead: fifteen one-line person notes made the graph
# unreadable and none of them was a page anyone would open twice.
_STAFF_ROLE = re.compile(
    r"\b(instructor|co-?instructor|professor|lecturer|faculty|gsi|gsr|"
    r"teaching assistant|graduate student|assistant|reader|tutor)\b", re.I
)


def is_instructional_staff(role: str) -> bool:
    return bool(_STAFF_ROLE.search(role or ""))


class IngestError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Filenames
# --------------------------------------------------------------------------

def clean_note_name(raw: str, fallback: str) -> str:
    """Enforce the naming rules in code rather than trusting the model.

    Short, natural, 2-6 words, no hashes, no timestamps, no export-task titles,
    no sentence punctuation. The filename and the H1 are the same string, so a
    readable graph label is guaranteed by construction.
    """
    name = unicodedata.normalize("NFKC", (raw or "").strip())
    name = name.split("\n")[0]
    name = _ILLEGAL_FILENAME.sub(" ", name)
    name = _MACHINE_NAME.sub(" ", name)         # dates/hashes while separators intact
    name = re.sub(r"[-_]+", " ", name)          # export-style slugs become words
    name = _MACHINE_NAME.sub(" ", name)         # hashes/ids revealed by the split
    name = name.strip(" .,;:!?")
    name = re.sub(r"\s+", " ", name)
    seen: set[str] = set()
    words: list[str] = []
    for word in name.split():                    # slugs repeat themselves a lot
        key = word.lower()
        if key in seen:
            continue
        seen.add(key)
        words.append(word)
    words = words[:6]
    name = " ".join(words).strip(" .,;:!?")
    if len(words) < 2 or len(name) < 4 or not any(c.isalpha() for c in name):
        name = fallback
    return name


def validate_title_against_source(title: str, source_text: str, fallback: str) -> tuple[str, str | None]:
    """Reject or repair a title containing words the source never uses.

    A note title should be built from the document's own vocabulary. This caught
    a real failure: the model produced "Negotiaions MBA 252 Fall 2026" -- a
    misspelling that would have become both the filename and the graph label.
    Any word of four or more letters that does not appear in the source is
    repaired from the source's own vocabulary when a close match exists, and the
    title is otherwise rejected in favour of the filename-derived fallback.
    """
    vocabulary = {w.lower() for w in re.findall(r"[A-Za-z]{3,}", source_text)}
    if not vocabulary:
        return title, None
    repaired: list[str] = []
    notes: list[str] = []
    for word in title.split():
        letters = re.sub(r"[^A-Za-z]", "", word)
        if len(letters) < 4 or letters.lower() in vocabulary:
            repaired.append(word)
            continue
        close = difflib.get_close_matches(letters.lower(), vocabulary, n=1, cutoff=0.82)
        if close:
            replacement = word.replace(letters, close[0].capitalize() if letters[0].isupper() else close[0])
            notes.append(f"'{word}' -> '{replacement}'")
            repaired.append(replacement)
        else:
            return fallback, f"title '{title}' used words absent from the source; fell back to '{fallback}'"
    corrected = " ".join(repaired)
    return corrected, (f"corrected title: {', '.join(notes)}" if notes else None)


def validate_person_name(name: str, source_text: str) -> tuple[str, str | None]:
    """Person names become filenames and graph labels, so they get the same
    source-vocabulary check as titles. The model produced 'Alexaandre Mas' and
    'Ijheh Ogbechie' for names the source spells 'Alexandre Mas' and
    'Ijeh Ogbechie'; both are repaired from the source's own words."""
    vocabulary = {w.lower() for w in re.findall(r"[A-Za-z]{3,}", source_text)}
    if not vocabulary:
        return name, None
    parts: list[str] = []
    notes: list[str] = []
    for word in name.split():
        letters = re.sub(r"[^A-Za-z\u00C0-\u024F]", "", word)
        if len(letters) < 3 or letters.lower() in vocabulary:
            parts.append(word)
            continue
        close = difflib.get_close_matches(letters.lower(), vocabulary, n=1, cutoff=0.75)
        if close:
            fixed = close[0][:1].upper() + close[0][1:]
            notes.append(f"'{word}' -> '{fixed}'")
            parts.append(word.replace(letters, fixed))
        else:
            parts.append(word)
    return " ".join(parts), (", ".join(notes) or None)


# The ingest instructions ask the model not to copy contact details. It does
# anyway, and on one run it mangled one into 'olesky@haaas.bberkeley.edu'. A
# privacy rule that matters is enforced in code, not requested in a prompt.
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")


def redact_contact_details(text: str) -> tuple[str, int]:
    """Strip emails and phone numbers from generated prose.

    The unchanged original in raw/ remains the record for contact details, so
    nothing is lost -- but the shared wiki pages do not republish them, and a
    mangled address can never be mistaken for a real one.
    """
    redacted, emails = _EMAIL.subn("(contact details in the original source)", text)
    redacted, phones = _PHONE.subn("(contact details in the original source)", redacted)
    return redacted, emails + phones


# Local English wordlist, used to tell a misspelled proper noun from an ordinary
# capitalised word. Shipped with macOS/BSD; a built-in fallback covers systems
# without it. Needed because the first version of the proper-noun guard "fixed"
# the bullet "No-class dates: None specified." into "One specified." -- inverting
# the meaning of a correct sentence.
_DICTIONARY_PATHS = ("/usr/share/dict/words", "/usr/dict/words")
_FALLBACK_WORDS = {
    "none", "note", "notes", "each", "some", "this", "that", "these", "those",
    "also", "only", "full", "first", "last", "week", "weeks", "date", "dates",
    "optional", "required", "recommended", "class", "classes", "course",
    "courses", "student", "students", "instructor", "office", "point", "points",
    "grade", "grades", "final", "midterm", "assignment", "assignments",
    "attendance", "participation", "feedback", "preparation", "press", "team",
    "group", "online", "remote", "exam", "exams", "session", "sessions",
    "lecture", "lectures", "reading", "readings", "topic", "topics", "total",
    "bonus", "late", "absence", "absences", "policy", "policies", "speaker",
    "speakers", "guest", "quiz", "quizzes", "project", "projects", "none",
}


@lru_cache(maxsize=1)
def _english_words() -> frozenset[str]:
    for candidate in _DICTIONARY_PATHS:
        path = Path(candidate)
        if path.exists():
            try:
                words = {
                    line.strip().lower()
                    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
                    if line.strip()
                }
                return frozenset(words | _FALLBACK_WORDS)
            except OSError:
                break
    return frozenset(_FALLBACK_WORDS)


def repair_proper_nouns(text: str, source_text: str) -> tuple[str, list[str]]:
    """Repair capitalised words in generated prose that the source spells another way.

    The model paraphrases freely, so generated prose cannot be required to use
    only the source's vocabulary. Capitalised mid-sentence words are different:
    they are almost always proper nouns lifted from the document, so one that the
    source never uses is a misspelling. This caught 'Amaador' for 'Amador' and
    'Ijheh' for 'Ijeh' inside section bullets, where the name guard -- which only
    inspects the people list -- could not see them.
    """
    vocabulary = {w.lower() for w in re.findall(r"[A-Za-z]{3,}", source_text)}
    if not vocabulary:
        return text, []
    dictionary = _english_words()
    fixes: list[str] = []

    def replace(match: re.Match) -> str:
        word = match.group(0)
        if word.lower() in vocabulary or word.isupper():
            return word
        lowered = word.lower()
        if lowered in dictionary:
            return word          # an ordinary English word, not a misspelled name
        # Accept a regular plural or possessive whose stem is known, so the guard
        # does not "correct" Wednesdays -> Wednesday.
        for stem in (lowered.rstrip("s"), lowered[:-2] if lowered.endswith("es") else ""):
            if stem and (stem in dictionary or stem in vocabulary):
                return word
        close = difflib.get_close_matches(word.lower(), vocabulary, n=1, cutoff=0.8)
        if not close:
            return word
        fixed = close[0][:1].upper() + close[0][1:]
        if fixed != word:
            fixes.append(f"'{word}' -> '{fixed}'")
        return fixed

    # Any capitalised word of 4+ letters. Sentence-initial words no longer need a
    # positional exemption now that the dictionary check protects ordinary words,
    # and dropping it lets a name at the start of a bullet be repaired too.
    repaired = re.sub(r"\b[A-Z][a-z]{3,}\b", replace, text)
    return repaired, fixes


_COURSE_CODE = re.compile(r"\b(?:MBA|EWMBA)\s?/?(?:EWMBA\s?)?(\d{3}[A-Z]?)\b")


def complete_course_code(title: str, source_text: str) -> tuple[str, str | None]:
    """Append the course code when the source states one and the title omits it.

    Keeps the four course notes consistently named. The model supplied the code
    for three of four syllabi unprompted; this makes it four of four without
    inventing anything, since the code is read from the source.
    """
    match = _COURSE_CODE.search(source_text)
    if not match:
        return title, None
    code = match.group(1)
    if code in title:
        return title, None
    completed = f"{title} MBA {code}"
    words = completed.split()
    if len(words) > 6:
        completed = " ".join(words[-6:])
    return completed, f"appended course code from source: '{title}' -> '{completed}'"


# A topic tag is only added when the source visibly evidences it. The model
# under-tagged schedule and attendance on two of four syllabi, so the harness
# verifies the vocabulary against the text rather than trusting the tag list.
TOPIC_EVIDENCE = {
    "Grading and Assessment": re.compile(
        r"\b(grading|grade|points?\s+total|% of (the )?(course )?grade|weight)", re.I),
    "Attendance and Absences": re.compile(
        r"\b(absence|absences|attendance|punctual|arriving late|miss(ed|ing)? (a )?(class|session))", re.I),
    "Fall 2026 Schedule": re.compile(
        r"\b(class (hours|schedule|meetings?)|lectures?:|meets?\s+on|"
        r"(mon|tues|wednes|thurs|fri)day[s]?\b.*\d|room\b|location:)", re.I),
    "Required Readings": re.compile(
        r"\b(required (books?|reading|text)|textbook|reading\(s\)|chapters?\b)", re.I),
    "Assignments and Deadlines": re.compile(
        r"\b(assignment|deliverable|due\b|deadline|submit|submission)", re.I),
    "Course Policies": re.compile(
        r"\b(policy|policies|academic (integrity|misconduct)|plagiar|accommodation|"
        r"recording|DSP\b|honor code)", re.I),
}


def verify_topics(proposed: list[str], source_text: str) -> tuple[list[str], list[str]]:
    """Return (final_topics, added_by_evidence)."""
    final = [t for t in TOPIC_VOCABULARY if t in proposed]
    added = []
    for topic in TOPIC_VOCABULARY:
        if topic in final:
            continue
        if len(TOPIC_EVIDENCE[topic].findall(source_text)) >= 2:
            final.append(topic)
            added.append(topic)
    ordered = [t for t in TOPIC_VOCABULARY if t in final]
    return (ordered or ["Course Policies"]), added


def unique_note_path(folder: str, name: str, source_id: str) -> Path:
    """Resolve a collision with a meaningful qualifier, never a random suffix."""
    directory = config.WIKI_DIR / folder
    directory.mkdir(parents=True, exist_ok=True)
    candidate = directory / f"{name}.md"
    if not candidate.exists():
        return candidate
    existing = candidate.read_text(encoding="utf-8", errors="replace")
    if f"source_id: {source_id}" in existing:
        return candidate          # same source -> update in place
    for qualifier in ("Syllabus", "Course", "Notes"):
        alternative = directory / f"{name} - {qualifier}.md"
        if not alternative.exists() or f"source_id: {source_id}" in alternative.read_text(
            encoding="utf-8", errors="replace"
        ):
            return alternative
    raise IngestError(
        f"Cannot find a readable unique name for '{name}' in {folder}/. "
        "Rename the existing note or give this source a clearer title."
    )


# --------------------------------------------------------------------------
# Model output handling
# --------------------------------------------------------------------------

_KEY_ALIASES = {
    "summaary": "summary", "sumary": "summary", "summry": "summary",
    "section": "sections", "topic": "topics", "person": "people",
    "name": "title", "note_title": "title",
}


def parse_note_json(text: str) -> dict:
    """Pull the JSON object out of the model's reply, tolerating fences.

    Two defences beyond the runtime schema: Gemma 3n sometimes writes its
    tokenizer's U+2581 space glyph instead of a real space, and it occasionally
    misspells a key. Both are cheap to repair and expensive to lose a run to.
    """
    candidate = text.replace("\u2581", " ").strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, re.S)
    if fenced:
        candidate = fenced.group(1)
    else:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start == -1 or end == -1:
            raise IngestError(
                "The model did not return a JSON object.\n"
                f"First 300 characters of its reply:\n{text[:300]}"
            )
        candidate = candidate[start : end + 1]
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise IngestError(f"Model returned invalid JSON ({exc}).\n{candidate[:400]}") from exc
    if not isinstance(data, dict):
        raise IngestError(f"Model returned {type(data).__name__}, expected a JSON object.")
    return {_KEY_ALIASES.get(k, k): v for k, v in data.items()}


def normalise_note(data: dict, fallback_title: str) -> dict:
    folder = data.get("folder") if data.get("folder") in config.WIKI_FOLDERS else "Courses"
    sections = []
    for section in data.get("sections") or []:
        if not isinstance(section, dict):
            continue
        heading = str(section.get("heading") or "").strip()
        bullets = [
            re.sub(r"\s+", " ", str(b).strip().lstrip("-* ").strip())
            for b in (section.get("bullets") or [])
            if str(b).strip()
        ]
        if heading and bullets:
            sections.append({"heading": heading, "bullets": bullets[:8]})
    sections = sections[:6]
    topics = [t for t in (data.get("topics") or []) if t in TOPIC_VOCABULARY]
    people = []
    for person in data.get("people") or []:
        if isinstance(person, dict) and str(person.get("name") or "").strip():
            people.append(
                {
                    "name": re.sub(r"\s+", " ", str(person["name"]).strip()),
                    "role": re.sub(r"\s+", " ", str(person.get("role") or "Listed in syllabus").strip()),
                }
            )
    return {
        "title": clean_note_name(data.get("title", ""), fallback_title),
        "folder": folder,
        "summary": re.sub(r"\s+", " ", str(data.get("summary") or "").strip()),
        "sections": sections,
        "topics": topics or ["Course Policies"],
        "people": people,
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_course_note(note: dict, source: dict, truncated: bool) -> str:
    lines = [
        "---",
        f"title: {note['title']}",
        f"source_id: {source['source_id']}",
        f"original_filename: {source['original_filename']}",
        f"source_path: {source['source_path']}",
        f"source_sha256: {source['sha256']}",
        f"source_pages: {source['pages']}",
        f"ingested: {date.today().isoformat()}",
        f"generated_by: {source['model']} via {source['runtime']}",
        f"review_status: {source.get('review_status', 'model-generated, human-reviewed')}",
        "tags:",
    ]
    lines += [f"  - {topic.lower().replace(' ', '-')}" for topic in note["topics"]]
    lines.append("---")
    lines.append("")
    lines.append(f"# {note['title']}")
    lines.append("")
    lines.append(note["summary"] or "_No summary generated._")
    lines.append("")
    for section in note["sections"]:
        lines.append(f"## {section['heading']}")
        lines += [f"- {bullet}" for bullet in section["bullets"]]
        lines.append("")
    guests = source.get("guests") or []
    if guests:
        lines.append("## Guest Speakers")
        lines += [f"- {g['name']} — {g['role']}" for g in guests]
        lines.append("")
    lines.append("## Source Reference")
    lines.append(
        f"- Original, unchanged: [`{source['original_filename']}`]"
        f"({source['relative_link']}) — {source['pages']} pages, "
        f"sha256 `{source['sha256'][:12]}…`"
    )
    lines.append(
        f"- Machine id for this source: `{source['source_id']}` "
        "(used by the retrieval index and by re-ingestion to update this note in place)"
    )
    if truncated:
        lines.append(
            f"- Note generated from the first {INGEST_CHAR_BUDGET:,} characters of the "
            "extracted text; the original remains complete in `raw/`."
        )
    lines.append("")
    lines.append("## Related Notes")
    for topic in note["topics"]:
        lines.append(
            f"- [[{topic}]] — this course's {topic.lower()} details are compared "
            "against the other courses there."
        )
    for person in note["people"]:
        if is_instructional_staff(person["role"]):
            lines.append(f"- [[{person['name']}]] — {person['role']} for this course.")
    lines.append("- [[index]] — the vault landing page.")
    lines.append("")
    return "\n".join(lines)


def render_topic_note(topic: str, courses: list[dict]) -> str:
    lines = [
        "---",
        f"title: {topic}",
        "note_type: topic hub",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        f"# {topic}",
        "",
        TOPIC_BLURBS.get(topic, "Cross-course topic hub."),
        "",
        "## Courses covering this",
    ]
    for course in sorted(courses, key=lambda c: c["title"]):
        lines.append(
            f"- [[{course['title']}]] — see its notes for the stated rules; "
            f"original syllabus: [`{course['original_filename']}`]({course['relative_link']})"
        )
    lines += [
        "",
        "## How to check a claim here",
        "- Open the linked course note, then follow its **Source Reference** to the",
        "  unchanged original in `raw/`.",
        f"- For a checked, cited answer run: `./wiki ask \"...{topic.lower()}...\"`",
        "",
        "## Related Notes",
        "- [[index]] — grouped list of every note in this vault.",
        "",
    ]
    return "\n".join(lines)


def render_person_note(name: str, roles: list[dict]) -> str:
    lines = [
        "---",
        f"title: {name}",
        "note_type: person",
        f"updated: {date.today().isoformat()}",
        "---",
        "",
        f"# {name}",
        "",
        "Named in the Fall 2026 syllabi held in this vault. Contact details are",
        "deliberately not copied here; they remain in the unchanged original.",
        "",
        "## Roles",
    ]
    for role in sorted(roles, key=lambda r: r["course"]):
        lines.append(f"- {role['role']} — [[{role['course']}]]")
    lines += [
        "",
        "## Related Notes",
        "- [[index]] — grouped list of every note in this vault.",
        "",
    ]
    return "\n".join(lines)


def render_index(courses: list[dict], topics: dict, people: dict) -> str:
    lines = [
        "# Fall 2026 Course Wiki",
        "",
        "Personal memory for Jonathan's Fall 2026 MBA coursework at Berkeley Haas.",
        "Every page here was generated from an original syllabus by a local Gemma",
        "model and then reviewed. The unchanged originals live in `raw/`.",
        "",
        "Ask it a factual question with citations:",
        "",
        "```",
        './wiki ask "How many points is participation worth in Negotiations?"',
        "```",
        "",
        "## Courses",
        "",
    ]
    for course in sorted(courses, key=lambda c: c["title"]):
        lines.append(f"- [[{course['title']}]] — {course['blurb']}")
    lines += ["", "## Topics across courses", ""]
    for topic in TOPIC_VOCABULARY:
        if topic in topics:
            lines.append(f"- [[{topic}]] — {TOPIC_BLURBS[topic]}")
    lines += ["", "## People", ""]
    for name in sorted(people):
        roles = ", ".join(sorted({r["role"] for r in people[name]}))
        lines.append(f"- [[{name}]] — {roles}")
    lines += [
        "",
        "## Original sources",
        "",
        "Preserved byte-for-byte; each course note links back to its own source.",
        "",
    ]
    for course in sorted(courses, key=lambda c: c["original_filename"]):
        # index.md sits at the vault root, so raw/ is one level down, not three.
        href = "raw/" + course["original_filename"].replace(" ", "%20")
        lines.append(
            f"- [`raw/{course['original_filename']}`]({href}) → [[{course['title']}]]"
        )
    lines += [
        "",
        "---",
        "",
        "_Generated and maintained by the `wiki` CLI in this repository._",
        f"_Last rebuilt {date.today().isoformat()}._",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Manifest (dedupe + rename bookkeeping)
# --------------------------------------------------------------------------

def load_corrections() -> list[dict]:
    if not config.CORRECTIONS_FILE.exists():
        return []
    data = json.loads(config.CORRECTIONS_FILE.read_text(encoding="utf-8"))
    return data.get("corrections", [])


def apply_corrections(markdown: str, source_id: str) -> tuple[str, list[dict], list[dict]]:
    """Re-apply reviewed corrections to a freshly generated note.

    A correction carries either a literal ``find`` or a ``find_regex``, plus the
    ``replace`` text and the reason it exists.

    Without this, every re-ingest silently restored the model's misreadings and
    threw away the review. Corrections are exact find/replace pairs recorded
    against a source id, so they are auditable and cannot drift: one whose
    `find` no longer appears is reported as stale rather than ignored.
    """
    applied: list[dict] = []
    stale: list[dict] = []
    for correction in load_corrections():
        if correction.get("source_id") != source_id:
            continue
        replacement = correction.get("replace", "")
        pattern = correction.get("find_regex")
        if pattern:
            # Regex matching exists because the model rewords a line between runs:
            # a correction keyed on "- Required Readings:" stopped matching the moment
            # it wrote "- Required Reading:". An overlay that silently stops applying
            # is worse than no overlay.
            compiled = re.compile(pattern, re.I)
            markdown, count = compiled.subn(replacement, markdown)
            (applied if count else stale).append(correction)
            continue
        find = correction.get("find", "")
        if find and find in markdown:
            markdown = markdown.replace(find, replacement)
            applied.append(correction)
        else:
            stale.append(correction)
    if applied:
        markdown = markdown.replace(
            "review_status: model-generated, human-reviewed",
            f"review_status: model-generated; {len(applied)} reviewed correction(s) "
            "re-applied from corrections/wiki-corrections.json",
        )
    return markdown, applied, stale


def load_manifest() -> dict:
    if config.MANIFEST_FILE.exists():
        return json.loads(config.MANIFEST_FILE.read_text(encoding="utf-8"))
    return {"sources": {}}


def save_manifest(manifest: dict) -> None:
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    config.MANIFEST_FILE.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def retarget_links(old_title: str, new_title: str) -> int:
    """When a note is renamed, fix every incoming [[wikilink]] in the vault."""
    changed = 0
    for path in list(config.WIKI_DIR.rglob("*.md")) + [config.INDEX_PAGE]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        replaced = text.replace(f"[[{old_title}]]", f"[[{new_title}]]")
        if replaced != text:
            path.write_text(replaced, encoding="utf-8")
            changed += 1
    return changed


def discover_sources(target: Path) -> list[Path]:
    target = target.resolve()
    if target.is_file():
        return [target]
    supported = TEXT_SUFFIXES | PDF_SUFFIXES
    return sorted(p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in supported)
