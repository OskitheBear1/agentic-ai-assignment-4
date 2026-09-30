# Required Obsidian screenshots

Three screenshots of the personal memory vault. Put them here with these exact names
so the README's links resolve:

| File | What it must show |
|---|---|
| `note-with-sources.png` | an open note with its short descriptive filename, an H1 matching that filename, its **Source Reference** section, and its **Related Notes** links |
| `index-and-page-list.png` | `index.md` open alongside the file list, showing topic grouping |
| `graph-view.png` | graph view with readable note labels and meaningful connections |

## How to produce them

1. Obsidian → **Open folder as vault** → select `vault/` (not the repo root).
2. **`note-with-sources.png`** — open `wiki/Courses/Negotiations MBA 252.md`. Frame it
   so the filename in the tab, the `# Negotiations MBA 252` heading, the
   `## Source Reference` links and the `## Related Notes` wikilinks are all visible.
3. **`index-and-page-list.png`** — open `index.md` with the file explorer showing
   `Courses/`, `Topics/` and `People/` expanded.
4. **`graph-view.png`** — open Graph view, then:
   - Filters → search `path:wiki/`
   - Filters → turn **Attachments off** (otherwise the four PDFs swamp the view)
   - zoom in until the note labels are legible
   - expect 18 nodes: 4 course notes, 6 topic hubs, 8 people
5. **Record the filter you used** in the README next to the screenshot. The filter is
   presentation only — the filenames underneath are already readable, which
   `./wiki check` enforces.

## Trace to check before you screenshot

Start at `index.md` → click `[[Negotiations MBA 252]]` → scroll to **Related Notes**
→ click `[[Grading and Assessment]]` → that hub links back to all four courses →
return to the course note → **Source Reference** → click `Negotiations Syllabus.pdf`
and confirm the original PDF opens.

`./wiki check` verifies the same thing mechanically: 102 internal links resolving,
0 broken links, 0 machine-style filenames, 0 heading/filename mismatches.
