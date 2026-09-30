# Stability runs

Two extra full runs of the same four-question eval set, at the same settings, on the
same index. They exist to show the results are reproducible rather than a lucky draw.

The reason this mattered: with `ask` temperature at 0.1, test-4 produced a correct
refusal on one run and a wrong answer naming the *Negotiations* GSI on the next. An
evidence card that cannot be reproduced is not evidence. Temperature is now 0.0
(`config.ASK_OPTIONS`), and these runs plus the canonical one in the parent directory
are byte-identical in their answers:

| Run | test-1 | test-2 | test-3 | test-4 |
|---|---|---|---|---|
| `20260929-205821` | PASS | PASS | PARTIAL | PASS |
| `20260929-205841` | PASS | PASS | PARTIAL | PASS |
| canonical (parent dir) | PASS | PASS | PARTIAL | PASS |

The *earlier, failing* runs are not here — they are kept separately and unedited in
`../run-1-before-prompt-fix/`, `../run-2-before-contract-fix/` and
`../run-3-before-course-scoping/`, because the failures are part of the record.
