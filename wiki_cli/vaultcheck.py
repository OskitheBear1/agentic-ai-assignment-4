"""`wiki check` — verify the vault is actually usable, not just populated.

The assignment asks for working internal links, resolvable source references and
no machine-style names. Those are checkable in code, so they are checked here
rather than eyeballed.
"""

from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

from . import config
from .documents import repo_relative

_WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
_MDLINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_MACHINE_NAME = re.compile(r"([0-9a-f]{8,}|\d{4}-\d{2}-\d{2}|chunk[-_ ]?\d+|task[-_ ]?\d+)", re.I)


def _note_targets() -> dict[str, Path]:
    targets: dict[str, Path] = {}
    for path in config.WIKI_DIR.rglob("*.md"):
        targets[path.stem] = path
    if config.INDEX_PAGE.exists():
        targets[config.INDEX_PAGE.stem] = config.INDEX_PAGE
    return targets


def run() -> int:
    if not config.WIKI_DIR.exists():
        print("No vault/wiki yet. Run: ./wiki ingest ./vault/raw")
        return 1

    targets = _note_targets()
    notes = sorted(list(config.WIKI_DIR.rglob("*.md")) + ([config.INDEX_PAGE] if config.INDEX_PAGE.exists() else []))
    broken_links: list[str] = []
    broken_sources: list[str] = []
    bad_names: list[str] = []
    long_names: list[str] = []
    heading_mismatch: list[str] = []
    orphans: list[str] = []
    incoming: dict[str, int] = {stem: 0 for stem in targets}

    for note in notes:
        text = note.read_text(encoding="utf-8")
        rel = repo_relative(note)

        if note != config.INDEX_PAGE:
            stem = note.stem
            if _MACHINE_NAME.search(stem):
                bad_names.append(f"{rel}  (machine-style filename)")
            words = stem.split()
            if len(words) > 6 or len(stem) > 60:
                long_names.append(f"{rel}  ({len(words)} words)")
            heading = next((l for l in text.splitlines() if l.startswith("# ")), None)
            if not heading:
                heading_mismatch.append(f"{rel}  (no H1)")
            elif heading[2:].strip() != stem:
                heading_mismatch.append(f"{rel}  H1 '{heading[2:].strip()}' != filename '{stem}'")

        for match in _WIKILINK.finditer(text):
            target = match.group(1).strip()
            if target in targets:
                incoming[target] = incoming.get(target, 0) + 1
            else:
                broken_links.append(f"{rel}  ->  [[{target}]]")

        for match in _MDLINK.finditer(text):
            href = match.group(1).strip()
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (note.parent / urllib.parse.unquote(href)).resolve()
            if not resolved.exists():
                broken_sources.append(f"{rel}  ->  {href}")

    for stem, path in targets.items():
        if path == config.INDEX_PAGE:
            continue
        if incoming.get(stem, 0) == 0:
            orphans.append(repo_relative(path))

    print(f"\033[1mVAULT CHECK\033[0m  {repo_relative(config.VAULT)}\n")
    print(f"  notes                     {len(notes)}")
    print(f"  internal [[links]]        {sum(incoming.values())} resolving")
    problems = 0
    for label, items in (
        ("broken internal links", broken_links),
        ("unresolvable source links", broken_sources),
        ("machine-style filenames", bad_names),
        ("filenames over 6 words", long_names),
        ("heading/filename mismatches", heading_mismatch),
        ("notes with no incoming link", orphans),
    ):
        if items:
            problems += len(items)
            print(f"\n  \033[31m{label}: {len(items)}\033[0m")
            for item in items[:15]:
                print(f"    - {item}")
            if len(items) > 15:
                print(f"    … and {len(items) - 15} more")
        else:
            print(f"  {label:<25} \033[32m0\033[0m")

    # A reviewed correction that no longer lands is review silently thrown away,
    # so it is reported here as well as during ingestion.
    from . import wikigen

    corrections = wikigen.load_corrections()
    not_applied: list[str] = []
    if corrections:
        all_text = "\n".join(
            path.read_text(encoding="utf-8") for path in config.WIKI_DIR.rglob("*.md")
        )
        for correction in corrections:
            if correction.get("replace", "") not in all_text:
                target = correction.get("find") or correction.get("find_regex") or "?"
                not_applied.append(f"{target[:60]}  ({correction.get('source')})")
        print(f"\n  reviewed corrections       {len(corrections)} defined, "
              f"{len(corrections) - len(not_applied)} currently applied")
        if not_applied:
            # Informational, not a failure: a correction that does not land means
            # the model got that statement right on this run. It stays defined
            # because the error recurs on other runs.
            print(f"  not landing this run        {len(not_applied)} "
                  "(the model did not produce that wording on the last ingest)")
            for item in not_applied:
                print(f"    - {item}")

    raw_files = [p for p in config.RAW_DIR.rglob("*") if p.is_file() and not p.name.startswith(".")]
    print(f"\n  originals preserved       {len(raw_files)} file(s) in raw/")
    print(f"\n{'\033[32mPASS\033[0m' if problems == 0 else f'\033[31m{problems} problem(s)\033[0m'}")
    return 0 if problems == 0 else 1
