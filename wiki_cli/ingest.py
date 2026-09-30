"""The ingest orchestrator: sources in, reviewed wiki + fresh index out."""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

from . import config, index, model, prompts, wikigen
from .documents import extract_pages, file_sha256, file_source_id, human_title, repo_relative


def _source_text(path: Path) -> tuple[str, int]:
    pages = extract_pages(path)
    text = "\n".join(t for _, t in pages)
    return text, len([p for p, _ in pages if p])


def ingest_one(path: Path, execution_mode: str, manifest: dict, verbose: bool = True) -> dict:
    source_id = file_source_id(path)
    text, page_count = _source_text(path)
    if not text.strip():
        raise wikigen.IngestError(
            f"No text extracted from {path.name}. If it is a scanned PDF you would need "
            "local OCR; this harness does not ship one."
        )
    truncated = len(text) > wikigen.INGEST_CHAR_BUDGET
    fallback_title = wikigen.clean_note_name(human_title(path), "Untitled Source")

    if verbose:
        print(f"  → {path.name}: {page_count or 1} page(s), {len(text):,} characters extracted")
        print(f"    sending {min(len(text), wikigen.INGEST_CHAR_BUDGET):,} characters to "
              f"{config.LOCAL_CHAT_MODEL if execution_mode == 'local' else config.ONLINE_CHAT_MODEL}")

    system, user = prompts.build_ingest_prompt(
        human_title(path), text, wikigen.INGEST_CHAR_BUDGET
    )
    started = time.perf_counter()
    completion = model.generate(
        system, user, config.INGEST_OPTIONS, mode=execution_mode,
        schema=prompts.NOTE_SCHEMA,
    )
    note = wikigen.normalise_note(wikigen.parse_note_json(completion.text), fallback_title)
    raw_title = note["title"]
    note["title"], title_note = wikigen.validate_title_against_source(
        raw_title, text, fallback_title
    )
    note["title"], code_note = wikigen.complete_course_code(note["title"], text)
    if verbose:
        print(f"    model returned '{raw_title}' in {completion.seconds:.1f}s "
              f"({completion.completion_tokens} tokens)")
        for message in (title_note, code_note):
            if message:
                print(f"    \033[33mtitle guard:\033[0m {message}")

    name_fixes: list[str] = []
    for person in note["people"]:
        person["name"], fix = wikigen.validate_person_name(person["name"], text)
        if fix:
            name_fixes.append(fix)
    if verbose and name_fixes:
        print(f"    \033[33mname guard:\033[0m {'; '.join(name_fixes)}")

    prose_fixes: list[str] = []
    redactions = 0
    note["summary"], fixes = wikigen.repair_proper_nouns(note["summary"], text)
    prose_fixes += fixes
    note["summary"], count = wikigen.redact_contact_details(note["summary"])
    redactions += count
    for section in note["sections"]:
        repaired_bullets = []
        for bullet in section["bullets"]:
            bullet, fixes = wikigen.repair_proper_nouns(bullet, text)
            prose_fixes += fixes
            bullet, count = wikigen.redact_contact_details(bullet)
            redactions += count
            repaired_bullets.append(bullet)
        section["bullets"] = repaired_bullets
    if verbose and redactions:
        print(f"    \033[33mprivacy guard:\033[0m redacted {redactions} contact "
              "detail(s) the model copied into the note body")
    if verbose and prose_fixes:
        unique = list(dict.fromkeys(prose_fixes))
        print(f"    \033[33mprose guard:\033[0m {'; '.join(unique[:6])}"
              + (f" (+{len(unique) - 6} more)" if len(unique) > 6 else ""))

    note["topics"], added_topics = wikigen.verify_topics(note["topics"], text)
    if verbose and added_topics:
        print(f"    topic guard: added {', '.join(added_topics)} "
              "(evidenced in the source, not proposed by the model)")

    staff = [p for p in note["people"] if wikigen.is_instructional_staff(p["role"])]
    guests = [p for p in note["people"] if not wikigen.is_instructional_staff(p["role"])]
    if verbose and guests:
        print(f"    {len(staff)} staff note(s); {len(guests)} guest speaker(s) "
              "listed in the course note only")

    previous = manifest["sources"].get(source_id)
    note_path = wikigen.unique_note_path(note["folder"], note["title"], source_id)

    renamed_from = None
    if previous and previous.get("note_path"):
        old_path = config.ROOT / previous["note_path"]
        if old_path.exists() and old_path.resolve() != note_path.resolve():
            old_path.unlink()
            renamed_from = previous["title"]
            wikigen.retarget_links(previous["title"], note["title"])
            if verbose:
                print(f"    renamed note: '{previous['title']}' → '{note['title']}' "
                      "(incoming links updated)")

    source_meta = {
        "source_id": source_id,
        "source_path": repo_relative(path),
        "original_filename": path.name,
        "sha256": file_sha256(path),
        "pages": page_count or 1,
        "model": completion.model,
        "runtime": f"{completion.mode} ({'ollama' if completion.mode == 'local' else 'hosted'})",
        "relative_link": _link_from(note_path, path),
        "guests": guests,
    }
    markdown = wikigen.render_course_note(note, source_meta, truncated)
    markdown, applied, stale = wikigen.apply_corrections(markdown, source_id)
    if verbose and applied:
        print(f"    review guard: re-applied {len(applied)} human correction(s)")
    if verbose and stale:
        for correction in stale:
            target = correction.get("find") or correction.get("find_regex") or "?"
            print(f"    \033[33mstale correction:\033[0m no longer matches "
                  f"\"{target[:60]}\" — review and remove it")
    note_path.write_text(markdown, encoding="utf-8")

    manifest["sources"][source_id] = {
        "title": note["title"],
        "folder": note["folder"],
        "note_path": repo_relative(note_path),
        "source_path": source_meta["source_path"],
        "original_filename": path.name,
        "sha256": source_meta["sha256"],
        "pages": source_meta["pages"],
        "topics": note["topics"],
        "people": staff,
        "guests": guests,
        "summary": note["summary"],
        "model_title": raw_title,
        "title_guard": "; ".join(m for m in (title_note, code_note) if m) or None,
        "name_guard": name_fixes or None,
        "prose_guard": list(dict.fromkeys(prose_fixes)) or None,
        "contact_redactions": redactions or None,
        "topics_added_by_evidence": added_topics or None,
        "corrections_applied": len(applied) or None,
        "corrections_stale": [
            (c.get("find") or c.get("find_regex") or "?")[:80] for c in stale
        ] or None,
        "relative_link": source_meta["relative_link"],
        "ingested": date.today().isoformat(),
        "model": completion.model,
        "truncated_input": truncated,
        "renamed_from": renamed_from,
    }
    return {
        "title": note["title"],
        "note_path": repo_relative(note_path),
        "seconds": round(time.perf_counter() - started, 2),
        "renamed_from": renamed_from,
        "topics": note["topics"],
        "people": [p["name"] for p in staff],
        "title_guard": title_note,
    }


def _link_from(note_path: Path, source_path: Path) -> str:
    """Relative Markdown link from a wiki note to its original in raw/."""
    import os

    target = os.path.relpath(source_path.resolve(), note_path.resolve().parent)
    return target.replace(" ", "%20")


def rebuild_navigation(manifest: dict, verbose: bool = True) -> dict:
    """Rewrite topic hubs, people notes and index.md from the manifest.

    These are harness-assembled navigation pages, not model prose: the links can
    therefore never point at a note that does not exist.
    """
    sources = list(manifest["sources"].values())
    courses = [
        {
            "title": s["title"],
            "original_filename": s["original_filename"],
            "relative_link": s["relative_link"],
            "blurb": (s["summary"].split(". ")[0][:150] or "Course syllabus note."),
        }
        for s in sources
    ]

    topics: dict[str, list[dict]] = {}
    for source in sources:
        for topic in source["topics"]:
            topics.setdefault(topic, []).append(
                {
                    "title": source["title"],
                    "original_filename": source["original_filename"],
                    "relative_link": _relink_for_topic(source),
                }
            )

    people: dict[str, list[dict]] = {}
    for source in sources:
        for person in source["people"]:
            people.setdefault(person["name"], []).append(
                {"role": person["role"], "course": source["title"]}
            )

    # Remove hub/person notes that no longer have a reason to exist, so a
    # re-ingest cannot leave orphans behind.
    for folder, keep in (("Topics", set(topics)), ("People", set(people))):
        for path in (config.WIKI_DIR / folder).glob("*.md"):
            if path.stem not in keep:
                path.unlink()
                if verbose:
                    print(f"    removed stale note {folder}/{path.name}")

    for topic, entries in topics.items():
        (config.WIKI_DIR / "Topics" / f"{topic}.md").write_text(
            wikigen.render_topic_note(topic, entries), encoding="utf-8"
        )
    for name, roles in people.items():
        safe = wikigen.clean_note_name(name, "Course Contact")
        (config.WIKI_DIR / "People" / f"{safe}.md").write_text(
            wikigen.render_person_note(safe, roles), encoding="utf-8"
        )
    config.INDEX_PAGE.write_text(
        wikigen.render_index(courses, topics, people), encoding="utf-8"
    )
    return {"courses": len(courses), "topics": len(topics), "people": len(people)}


def _relink_for_topic(source: dict) -> str:
    """Topic hubs live in wiki/Topics/, one level below the vault root."""
    return "../../" + source["source_path"].split("vault/", 1)[-1].replace(" ", "%20")


def run(target: Path, execution_mode: str = "local", verbose: bool = True) -> dict:
    config.ensure_dirs()
    paths = wikigen.discover_sources(target)
    if not paths:
        raise wikigen.IngestError(
            f"No supported sources found at {target}.\n"
            "Supported: .pdf, .md, .markdown, .txt"
        )
    if execution_mode == "local":
        model.require_local_model(config.LOCAL_CHAT_MODEL)

    manifest = wikigen.load_manifest()
    started = time.perf_counter()
    print(f"\033[1mINGEST\033[0m {len(paths)} source(s) from {repo_relative(target)}\n")

    results = []
    for path in paths:
        results.append(ingest_one(path, execution_mode, manifest, verbose))
    wikigen.save_manifest(manifest)

    print("\n  rebuilding navigation (topic hubs, people, index.md)")
    navigation = rebuild_navigation(manifest, verbose)

    print("  rebuilding retrieval index")
    stats = index.build(verbose=verbose)

    elapsed = time.perf_counter() - started
    print()
    print(f"\033[1mDone\033[0m in {elapsed:.1f}s")
    print(f"  notes: {navigation['courses']} course, {navigation['topics']} topic, "
          f"{navigation['people']} people, 1 index")
    print(f"  index: {stats['passages']} passages "
          f"({stats['raw_passages']} from raw sources, {stats['wiki_passages']} from wiki notes), "
          f"{stats['vectors']} vectors")
    renamed = [r for r in results if r["renamed_from"]]
    if renamed:
        for r in renamed:
            print(f"  renamed: '{r['renamed_from']}' → '{r['title']}'")
    return {"sources": results, "navigation": navigation, "index": stats,
            "seconds": round(elapsed, 1)}
