#### test-1 — a direct question answered by one source

> **How many points is global participation worth in the Negotiations course?**

`gemma3n:e4b` · execution **local** · ollama 0.34.4 · embeddings `embeddinggemma:300m` · temperature 0.0 · top_k 6  
Machine verdict **PASS** · my verdict **PASS** · retrieval 1.433 s, generation 15.389 s

*Retrieval scope:* question names only "Negotiations"; evidence limited to that course

**Retrieved passages and source paths**

| | Source path | Where | Layer | Matched by |
|---|---|---|---|---|
| `S1` | `vault/raw/Negotiations Syllabus.pdf` | page 2 — *Course Description* | raw | keyword #2 (5.24) + vector #2 (0.565) |
| `S2` | `vault/raw/Negotiations Syllabus.pdf` | page 2 — *Course Description* | raw | keyword #3 (4.69) + vector #4 (0.553) |
| `S3` | `vault/raw/Negotiations Syllabus.pdf` | page 2 — *Course Description* | raw | keyword #5 (3.70) + vector #3 (0.556) |
| `S4` | `vault/wiki/Courses/Negotiations MBA 252.md` | section — *Grading* | wiki | keyword #1 (5.35) + vector #1 (0.594) |
| `S5` | `vault/wiki/Courses/Negotiations MBA 252.md` | section — *Negotiations MBA 252* | wiki | keyword #6 (3.41) + vector #9 (0.425) |
| `S6` | `vault/wiki/Courses/Negotiations MBA 252.md` | section — *Attendance and Lateness* | wiki | keyword #9 (1.84) + vector #7 (0.435) |

The decisive passage, `S1` — `vault/raw/Negotiations Syllabus.pdf`, page 2:

```text
…ics freely, but nothing involving physical intimidation or harassment.
Grading — 100 Points Total
Component When Points
Global participation (attendance, punctuality, engagement, quality of
discussion)
Weekly 40
Preparation (worksheets submitted before class) Weekly 20
Feedback (to negotiation partners) Weekly 20
In-class quizzes Sometime! 2-3 20 …
```

**Actual answer from local Gemma**

```text
ANswer: Global participation is worth 40 points in the Negotiaions course [S4][S5]. This includes attendance, punctuality, engagement, and the quality of discussion [S4].
```

**Citation check:** PASS — cited S4, S5 | unused retrieved passages: S1, S2, S3, S6 | spelling flags (in the answer, absent from every cited passage): Negotiaions

**Do the cited passages support the claim?** Yes. `[S4]` is the generated note's Grading
section and `[S5]` the note header, both tracing to page 2 of the original, which reads
`Global participation (attendance, punctuality, engagement, quality of discussion) |
Weekly | 40` and then `Participation (40 points)`. The figure and all four listed
components are in the cited text. The model misspells the course as "Negotiaions" in its
own prose; the harness flags that (`spelling flags`) and does **not** rewrite it,
because a saved answer must be exactly what the model said.

Full card, with every passage in full: [`evidence/ask/test-1-how-many-points-is-global-participation-worth-in.md`](evidence/ask/test-1-how-many-points-is-global-participation-worth-in.md)

#### test-2 — answerable, deliberately reworded away from the source

> **In Asset Management, how many classes can I miss before it starts to hurt my grade?**

`gemma3n:e4b` · execution **local** · ollama 0.34.4 · embeddings `embeddinggemma:300m` · temperature 0.0 · top_k 6  
Machine verdict **PASS** · my verdict ****PARTIAL**** · retrieval 2.625 s, generation 6.983 s

*Retrieval scope:* question names only "Asset Management"; evidence limited to that course

**Retrieved passages and source paths**

| | Source path | Where | Layer | Matched by |
|---|---|---|---|---|
| `S1` | `vault/raw/Asset Management Syllabus.pdf` | page 1 — *Privacy and Recording Notice* | raw | keyword #3 (1.34) + vector #1 (0.569) |
| `S2` | `vault/raw/Asset Management Syllabus.pdf` | page 1 — *(document start)* | raw | keyword #2 (3.29) + vector #3 (0.496) |
| `S3` | `vault/raw/Asset Management Syllabus.pdf` | page 3 — *(document start)* | raw | keyword #5 (1.00) + vector #5 (0.425) |
| `S4` | `vault/wiki/Courses/Asset Management MBA 233.md` | section — *Asset Management MBA 233* | wiki | keyword #1 (7.24) + vector #4 (0.487) |
| `S5` | `vault/wiki/Courses/Asset Management MBA 233.md` | section — *Grading* | wiki | keyword #6 (0.88) + vector #2 (0.547) |
| `S6` | `vault/raw/Asset Management Syllabus.pdf` | page 4 — *(document start)* | raw | keyword #7 (0.71) + vector #6 (0.390) |

The decisive passage, `S1` — `vault/raw/Asset Management Syllabus.pdf`, page 1:

```text
…vely, will account for 10% of the course grade. Your Questions,
collectively, will account for 10% of the course grade. More than three absences will
adversely affect the class contribution grade.
Date Topic  Reading(s) / Speaker
August 27 Course overview &
 Investments exercise
September 1 Risk and Return US chapter 1 and RW chapters 1, 2, 13
 Manias, Bubbles & Crashes
September 3  U.S. Equities US pages 33-48 and R …
```

**Actual answer from local Gemma**

```text
ANswer: You can miss more than three absences before it adversely affects the class contribution grade [S1][S5].
```

**Citation check:** PASS — cited S1, S5 | unused retrieved passages: S2, S3, S4, S6

**Do the cited passages support the claim?** The number and the citation are correct:
`[S1]`/`[S5]` contain `More than three absences will adversely affect the class
contribution grade`. **But I mark this PARTIAL by hand even though it passes the machine
check.** The sentence inverts the rule — it reads as permission to miss more than three,
when more than three is exactly what costs you. A mechanical citation check cannot
evaluate the direction of a threshold, which is precisely why the passage is printed
here.

Full card, with every passage in full: [`evidence/ask/test-2-in-asset-management-how-many-classes-can-i-miss-.md`](evidence/ask/test-2-in-asset-management-how-many-classes-can-i-miss-.md)

#### test-3 — answerable, spans two sources

> **Which of my Fall 2026 courses meet on Wednesdays, and at what times?**

`gemma3n:e4b` · execution **local** · ollama 0.34.4 · embeddings `embeddinggemma:300m` · temperature 0.0 · top_k 6  
Machine verdict **PARTIAL** · my verdict **PARTIAL** · retrieval 0.128 s, generation 8.823 s

**Retrieved passages and source paths**

| | Source path | Where | Layer | Matched by |
|---|---|---|---|---|
| `S1` | `vault/raw/Negotiations Syllabus.pdf` | page 1 — *(document start)* | raw | keyword #1 (7.72) + vector #8 (0.450) |
| `S2` | `vault/raw/AgenticAISyllabus.pdf` | page 1 — *MBA 290T: Fundamental of Agentic AI* | raw | keyword #2 (4.92) + vector #9 (0.447) |
| `S3` | `vault/raw/Data Mining Syllabus.pdf` | page 1 — *Instructor Luyi Yang* | raw | keyword #13 (2.14) + vector #6 (0.491) |
| `S4` | `vault/raw/Asset Management Syllabus.pdf` | page 1 — *(document start)* | raw | keyword #7 (3.78) + vector #13 (0.429) |
| `S5` | `vault/raw/Data Mining Syllabus.pdf` | page 1 — *(document start)* | raw | keyword #16 (1.85) + vector #5 (0.494) |
| `S6` | `vault/raw/Data Mining Syllabus.pdf` | page 1 — *(document start)* | raw | keyword #6 (3.87) + vector #20 (0.397) |

The decisive passage, `S1` — `vault/raw/Negotiations Syllabus.pdf`, page 1:

```text
…esolution
MBA 252 — Fall 2026
Professor: Solène Delecourt  (negotiationsolene@gmail.com)
GSI: Oranda Hou
GSR: Irina Liu
Day: Wednesdays
Time: MBA252.1 — 8:00–11:00 AM   |   MBA252.2 — 2:00–5:00 PM
Location: C220
Dates: 8/26, 9/2, 9/9, 9/16, 9/23, 9/30, 10/7, 10/14, 10/21, 10/28
This is a living document, updated periodically based on your feedback …
```

**Actual answer from local Gemma**

```text
ANSWER: MBA 252 meets on Wednesdays from 8:00–11:00 AM and MBA 252.2 meets on Wednesdays from 2:00–5:00 PM [S1]. Data Mining meets on Wednesdays from 6:00pm-9:30pm [S3][S5].
```

**Citation check:** PASS — cited S1, S3, S5 | unused retrieved passages: S2, S4, S6

**Do the cited passages support the claim?** Yes, and both sources were used. `[S1]` is
the Negotiations syllabus page 1; `[S4]`–`[S6]` are the Data Mining syllabus page 1. It
correctly **excluded** the two Tuesday courses, whose passages were retrieved as
deliberate distractors and left uncited. PARTIAL only because my written expectation
asked for the courses to be named, and it identifies Negotiations solely by its course
code, dropping the rooms that were present in the passages.

Full card, with every passage in full: [`evidence/ask/test-3-which-of-my-fall-2026-courses-meet-on-wednesdays.md`](evidence/ask/test-3-which-of-my-fall-2026-courses-meet-on-wednesdays.md)

#### test-4 — a plausible question the wiki cannot answer

> **Who is the GSI for the Asset Management course?**

`gemma3n:e4b` · execution **local** · ollama 0.34.4 · embeddings `embeddinggemma:300m` · temperature 0.0 · top_k 6  
Machine verdict **PASS** · my verdict **PASS** · retrieval 0.105 s, generation 7.984 s

*Retrieval scope:* question names only "Asset Management"; evidence limited to that course

**Retrieved passages and source paths**

| | Source path | Where | Layer | Matched by |
|---|---|---|---|---|
| `S1` | `vault/raw/Asset Management Syllabus.pdf` | page 1 — *(document start)* | raw | keyword #2 (4.01) + vector #2 (0.426) |
| `S2` | `vault/raw/Asset Management Syllabus.pdf` | page 1 — *Privacy and Recording Notice* | raw | keyword #3 (1.44) + vector #4 (0.357) |
| `S3` | `vault/raw/Asset Management Syllabus.pdf` | page 2 — *November 3 Behavioral Models RW 10* | raw | keyword #4 (1.26) + vector #3 (0.361) |
| `S4` | `vault/wiki/Courses/Asset Management MBA 233.md` | section — *Asset Management MBA 233* | wiki | keyword #1 (5.82) + vector #1 (0.470) |
| `S5` | `vault/wiki/Courses/Asset Management MBA 233.md` | section — *Grading* | wiki | vector #8 (0.274) |
| `S6` | `vault/raw/Asset Management Syllabus.pdf` | page 3 — *(document start)* | raw | keyword #5 (1.24) + vector #9 (0.233) |

**Actual answer from local Gemma**

```text
INSUFFICIENT EVIDENCE: the wiki does not contain the GSI for the Asset Management course.
Closest available: Academic Integrity and Ethics: Cheating on exams and plagiarism are two common examples of dishonest, unethical behavior. Honesty and integrity are of great importance in [S6].
```

**Citation check:** PASS — declared insufficient evidence (no citation required)

**Is the refusal correct?** Yes. The Asset Management syllabus names only `Instructor:
Sam Olesky`; searching its extracted text for GSI, GSR, assistant, reader and TA returns
only an unrelated `gsi.berkeley.edu` plagiarism URL. Note the retrieved context above:
**every passage is from Asset Management**. That is the course filter working — before
it existed, the Negotiations syllabus was retrieved here and the model reported its GSI,
Oranda Hou, as Asset Management's.

Full card, with every passage in full: [`evidence/ask/test-4-who-is-the-gsi-for-the-asset-management-course.md`](evidence/ask/test-4-who-is-the-gsi-for-the-asset-management-course.md)
