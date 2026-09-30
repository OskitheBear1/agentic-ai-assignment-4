# Evidence

Saved outputs, so this project can be inspected without rerunning the model.
Nothing here was edited after the fact, and no failed result was replaced with an
invented successful one.

| Path | What it holds |
|---|---|
| `ask/test-*.{md,json}` | the four ask-mode evidence cards — question, every retrieved passage in full with path/page/section, why each was retrieved, exact model identity, local/online mode, actual answer, citation verdict, timings |
| `ask/*-eval-summary.json` | the canonical run of all four tests |
| `ask/stability-runs/` | two more runs at identical settings, showing reproducibility |
| `ask/run-1-before-prompt-fix/` | **failing run.** test-3 PARTIAL, test-4 FAIL — answered "Oranda Hou", the *Negotiations* GSI, for Asset Management |
| `ask/run-2-before-contract-fix/` | **failing run.** the model asserted a fact and disclaimed it in the next line |
| `ask/run-3-before-course-scoping/` | **failing run.** test-4 regressed to "Oranda Hou" after prose-only fixes |
| `ask/mode-check-*.{md,json}` | the two ask cards produced inside the mode-boundary checks |
| `modes/*-mode-checks-*.txt` | all eight mode-boundary checks in one transcript |
| `modes/*-chat-session.{md,json}` | chat transcripts, each turn labelled with the harness's retrieval decision and reason |
| `offline/` | the offline demonstration transcript (`scripts/offline-demo.sh`) |
| `fixes/wiki-review-log.md` | every failure found, whether it was fixed in the harness or in the note, and where the before-state is |
| `fixes/before/` | pre-fix notes, the pre-fix chunk index, the pre-fix vault-check output |
| `screenshots/` | the three required Obsidian screenshots |

My own assessment of the four tests, where it differs from the machine verdict, is in
[`../tests/human_assessment.md`](../tests/human_assessment.md).
