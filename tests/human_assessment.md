# Human assessment of the four ask-mode tests

The machine verdict in `./wiki test` checks three mechanical things: did the
expected source get retrieved, does the answer contain the expected string, and
does every citation marker point at a passage that was actually retrieved. That is
not the same as "the answer is right". This file records the judgement the machine
cannot make, read against the retrieved passages printed in each evidence card.

Run these results come from: local, `gemma3n:e4b` (Q4_0) via Ollama 0.34.4,
`embeddinggemma:300m` for vectors, ask temperature 0.0, `top_k=6`. Identical across
three consecutive runs.

---

## test-1 — "How many points is global participation worth in the Negotiations course?"

- **Machine verdict:** PASS
- **Human verdict:** PASS
- **Answer:** "Global participation is worth 40 points in the Negotiaions course
  [S4][S5]. This includes attendance, punctuality, engagement, and the quality of
  discussion [S4]."
- **Do the cited passages support it?** Yes. The Negotiations grading table gives
  "Global participation (attendance, punctuality, engagement, quality of
  discussion) | Weekly | 40", and the section heading below it reads
  "Participation (40 points)". Both the figure and the four listed components are
  in the cited passages.
- **Defect worth recording:** the model misspells the course as "Negotiaions" in
  its own prose. The harness's spelling check flags it (`spelling flags: Negotiaions`)
  because the word appears in no cited passage. The answer is not rewritten —
  a saved answer must be exactly what the model said.

## test-2 — "In Asset Management, how many classes can I miss before it starts to hurt my grade?"

- **Machine verdict:** PASS
- **Human verdict:** **PARTIAL — the machine check is too lenient here.**
- **Answer:** "You can miss more than three absences before it adversely affects
  the class contribution grade [S1][S5]."
- **Do the cited passages support it?** The passages say "More than three absences
  will adversely affect the class contribution grade." The number and the citation
  are right, and the retrieval is right. But the sentence as written inverts the
  rule: it reads as permission to miss more than three, when more than three is
  exactly what costs you. A reader who trusted the first clause would draw the
  opposite conclusion from the syllabus.
- **Why it passes the machine check:** the check looks for the string "three" and
  for resolvable citations. It has no way to evaluate the direction of a threshold.
  That is the honest limit of a mechanical citation check, and the reason the
  evidence card prints the full passage.
- **What was tried:** the research rules were given an explicit instruction to
  quote a rule or threshold verbatim rather than rephrase it, with this exact
  failure as the worked example. On some runs the model then quoted the sentence
  correctly ("More than three absences will adversely affect the class contribution
  grade in Asset Management [S2]"), and on others it reverted to the inverted
  phrasing. It is not stable at this model size.
- **Retrieval note:** this was the test designed to stress wording. The source says
  "absences" and "adversely affect"; the question says "miss" and "hurt". BM25 alone
  ranked the right passage 10th; the vector half ranked it 6th, and the fusion plus
  the course filter put it in the prompt. The reworded question is answerable
  *because* retrieval is hybrid, not because the model guessed.

## test-3 — "Which of my Fall 2026 courses meet on Wednesdays, and at what times?"

- **Machine verdict:** PARTIAL
- **Human verdict:** PARTIAL, and the answer is factually correct
- **Answer:** "MBA 252 meets on Wednesdays from 8:00–11:00 AM and MBA 252.2 meets
  on Wednesdays from 2:00–5:00 PM [S1]. Data Mining meets on Wednesdays from
  6:00pm-9:30pm [S4][S5][S6]."
- **Do the cited passages support it?** Yes, and both sources were used. [S1] is
  the Negotiations syllabus page 1 ("Day: Wednesdays / Time: MBA252.1 — 8:00–11:00
  AM | MBA252.2 — 2:00–5:00 PM"); [S4]–[S6] are the Data Mining syllabus page 1
  ("Wednesday | Aug 26 - Oct 28, 2026 (10 weeks) | 6:00pm-9:30pm PT | Chou Hall
  N300"). It correctly **excluded** the two Tuesday courses, whose passages were
  retrieved as distractors ([S2] Agentic AI, [S3] Asset Management) and left uncited.
- **Why it is only PARTIAL:** the written expectation required the answer to name
  the courses. It names Negotiations only by its course code, "MBA 252", so a reader
  has to already know which course that is. It also drops the rooms (C220 and Chou
  Hall N300) that were present in the passages.
- **Assessment:** this is the hardest of the four — two sources, and precision
  against two near-miss sources — and the substance is right. The partial is about
  how the answer identifies a course, not about whether it is true.

## test-4 — "Who is the GSI for the Asset Management course?" (expected refusal)

- **Machine verdict:** PASS
- **Human verdict:** PASS
- **Answer:** "INSUFFICIENT EVIDENCE: the wiki does not contain the GSI for the
  Asset Management course."
- **Is the refusal correct?** Yes. The Asset Management syllabus names only
  "Instructor: Sam Olesky". Searching its extracted text for GSI, GSR, assistant,
  reader and TA returns only an unrelated `gsi.berkeley.edu` plagiarism URL.
- **This test failed twice before it passed, and that history matters.** On the
  first two runs the model answered "The GSIs for the Asset Management course are
  Oranda Hou" — Oranda Hou is the GSI for **Negotiations**. On one of those runs it
  then contradicted itself in the next line ("the wiki does not contain the GSIs
  for the Asset Management course"), asserting and disclaiming the same fact.
  Tightening the research rules to demand a subject check helped but did not hold:
  a later run reverted to naming Oranda Hou.
  The fix that worked was structural, not textual — see `course_scope()` in
  `wiki_cli/retrieval.py`. When a question names exactly one course, the candidate
  set is limited to that course's original and its note. The model cannot
  misattribute a GSI it never sees. Refusal has been stable across every run since.
- **Remaining defect:** the `Closest available:` line picks a poor neighbour — an
  academic-integrity paragraph — instead of saying that a GSI exists for a
  *different* course, which the rules ask for. The refusal itself is right; the
  courtesy line is close to useless.

---

## Summary

| Test | Machine | Human | One-line reason |
|---|---|---|---|
| test-1 | PASS | PASS | Correct figure, correct citation; model misspells the course name in its own prose |
| test-2 | PASS | **PARTIAL** | Right number, right citation, but the sentence inverts the direction of the rule |
| test-3 | PARTIAL | PARTIAL | Factually correct for both courses; names Negotiations only by course code, drops rooms |
| test-4 | PASS | PASS | Refuses correctly and stably, after a structural retrieval fix; weak "closest available" line |

Two of four are fully right. One is right in substance and imprecise in naming.
One is right in the number and wrong in the phrasing of the rule it is quoting.
Nothing here was rerun until it looked better: the failing runs are kept in
`evidence/ask/run-1-before-prompt-fix/`, `run-2-before-contract-fix/` and
`run-3-before-course-scoping/`.
