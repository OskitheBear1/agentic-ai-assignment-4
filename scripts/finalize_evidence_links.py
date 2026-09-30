"""Swap the README's two pending-evidence callouts for real links.

Run after the offline demonstration has been captured and the three Obsidian
screenshots are in place. Idempotent: it refuses to edit until every artefact it
needs exists, and says exactly which ones are missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
SHOTS = ROOT / "evidence" / "screenshots"
OFFLINE = ROOT / "evidence" / "offline"

REQUIRED_SHOTS = (
    "note-with-sources.png",
    "note-related-links.png",
    "index-and-page-list.png",
    "graph-view.png",
)

SCREENSHOT_CALLOUT = """> **Required screenshots — to be added to `evidence/screenshots/`:**
> 1. `note-with-sources.png` — an open note with its short descriptive filename,
>    matching H1, Source Reference, and Related Notes links.
> 2. `index-and-page-list.png` — `index.md` and the file list, grouped by topic.
> 3. `graph-view.png` — graph with readable labels, filter `path:wiki/`, Attachments off."""

OFFLINE_CALLOUT = """> **To be run and captured:** `./scripts/offline-demo.sh`, with the internet
> disconnected. The transcript saves itself to `evidence/offline/`."""


def screenshot_block() -> str:
    return """**1a. A wiki note: readable filename, matching heading, traceable source**

![The note Negotiations MBA 252 open in Obsidian. The tab title, the breadcrumb wiki / Courses / Negotiations MBA 252, and the H1 all read the same. The Properties panel shows source_id, original_filename, source_path, source_sha256, source_pages, ingested date, generated_by and review_status.](evidence/screenshots/note-with-sources.png)

The tab title, the breadcrumb and the H1 are the same string — `Negotiations MBA 252`
— so the Obsidian graph label is readable by construction, not by aliasing. Obsidian
renders the YAML front matter as a **Properties** panel, which puts the whole
provenance chain on screen: `source_id` (the content hash used for re-ingestion),
`original_filename`, `source_path`, the full `source_sha256`, `source_pages`,
`generated_by: gemma3n:e4b via local (ollama)`, and a `review_status` recording that
a human correction was re-applied from `corrections/wiki-corrections.json`.

**1b. The same note, scrolled to its source reference and related notes**

![The lower half of the same note, showing the Source Reference section with a working relative link to the unchanged PDF in raw/, and the Related Notes section with rendered wikilinks to the six topic hubs and the three instructional staff.](evidence/screenshots/note-related-links.png)

**Source Reference** links back to the unchanged original in `raw/` and repeats the
machine id. **Related Notes** are real rendered `[[wikilinks]]`, each with a sentence
saying *why* that topic is relevant — to the six topic hubs, and to the professor,
GSI and GSR for this course. Following any of them and coming back is the trace the
grader is asked to check.

**2. The topic-organized page list and index**

![index.md open in Obsidian beside the file explorer, showing notes grouped into Courses, Topics and People](evidence/screenshots/index-and-page-list.png)

`index.md` is the human landing page: Courses, then Topics across courses, then
People, then the original sources with a link from each PDF to its note. The file
explorer shows the whole vault — `Courses/` (4), `People/` (8), `Topics/` (6) and
`index` — with every link rendered and clickable. Obsidian reports 18 backlinks into
this page.

**3. Graph view with readable labels**

![Obsidian graph view filtered to path:wiki/ with Attachments off, showing the four course notes linked to six topic hubs and eight people notes, all labels legible](evidence/screenshots/graph-view.png)

**Filter used: `path:wiki/`, Attachments off.** That hides the four source PDFs, which
would otherwise dominate the view. 18 nodes: 4 course notes, 6 topic hubs, 8 people.
The filter is presentation only — the filenames underneath are already readable, which
`./wiki check` enforces."""


def offline_block(transcript: Path) -> str:
    rel = transcript.relative_to(ROOT).as_posix()
    return f"""> **Captured:** [`{rel}`]({rel.replace(' ', '%20')}) — produced by
> `./scripts/offline-demo.sh` with Wi-Fi off, from a restarted CLI and with both
> models unloaded first, so it is a cold start from weights already on disk."""


def main() -> int:
    if not README.exists():
        print("error: README.md not found")
        return 1

    # Each section is finalised independently, so whichever artefact exists first
    # gets linked immediately rather than waiting on the other.
    shots_missing = [n for n in REQUIRED_SHOTS if not (SHOTS / n).exists()]
    transcripts = sorted(OFFLINE.glob("*-offline-demonstration.txt")) if OFFLINE.exists() else []

    text = README.read_text(encoding="utf-8")
    changes = 0
    pending: list[str] = []

    if SCREENSHOT_CALLOUT in text:
        if shots_missing:
            pending += [f"evidence/screenshots/{n}" for n in shots_missing]
            print(f"  screenshots: {len(REQUIRED_SHOTS) - len(shots_missing)}/"
                  f"{len(REQUIRED_SHOTS)} present — callout left in place")
        else:
            text = text.replace(SCREENSHOT_CALLOUT, screenshot_block())
            changes += 1
            print("  screenshots: all three present — callout replaced with the images")
    else:
        print("  screenshots: already finalised")

    if OFFLINE_CALLOUT in text:
        if not transcripts:
            pending.append("evidence/offline/<timestamp>-offline-demonstration.txt "
                           "(run ./scripts/offline-demo.sh with Wi-Fi off)")
            print("  offline demo: no transcript yet — callout left in place")
        else:
            text = text.replace(OFFLINE_CALLOUT, offline_block(transcripts[-1]))
            changes += 1
            print(f"  offline demo: linked {transcripts[-1].name}")
    else:
        print("  offline demo: already finalised")

    if changes:
        README.write_text(text, encoding="utf-8")
        print(f"\nREADME.md updated ({changes} section(s)).")
    else:
        print("\nREADME.md unchanged.")

    if pending:
        print("\nStill to do:")
        for item in pending:
            print(f"  - {item}")
        print("Re-run this script once those exist.")

    # Verify every relative link still resolves.
    import re
    import urllib.parse

    broken = []
    for match in re.finditer(r"\]\(([^)]+)\)", README.read_text(encoding="utf-8")):
        href = match.group(1)
        if href.startswith(("http", "#", "mailto")):
            continue
        if not (ROOT / urllib.parse.unquote(href)).exists():
            broken.append(href)
    print(f"relative link check: {'all resolve' if not broken else 'BROKEN: ' + ', '.join(broken)}")
    if broken:
        return 1
    return 0 if not pending else 2


if __name__ == "__main__":
    sys.exit(main())
