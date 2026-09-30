# Ask-mode evidence card — test-4

**Question:** Who is the GSI for the Asset Management course?

| Field | Value |
| --- | --- |
| Mode | `ask` (standalone; chat history not used) |
| Execution | **local** |
| Generation model | `gemma3n:e4b` |
| Embedding model | `embeddinggemma:300m` |
| Runtime | ollama 0.34.4 |
| Retrieval scope | all, top_k=6 |
| Course filter | question names only "Asset Management"; evidence limited to that course |
| Retrieval time | 0.105 s |
| Generation time | 7.984 s |
| Tokens | 2518 prompt / 61 completion |
| Run at | 2026-09-29T21:55:26 |

## Retrieved passages

### [S1] `vault/raw/Asset Management Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #2 (4.01) + vector #2 (0.426) · *chunk:* `3f8d5907a6-001-001`

```text
[(document start)]
Asset Management
MBA 233
Fall 2026
Instructor:  Sam Olesky
Email:  olesky@haas.berkeley.edu
Office Hours:  by appointment
Office Location:  F502N
Class Hours:   Tuesdays and Thursdays 2:00 – 3:30
Class Location: Cheit Hall, C220
Privacy and Recording Notice
Course Description: The course will cover a broad range of investments and structuring
investment portfolios. We will consider investments, security selection and investment
portfolios from the perspective of individual and institutional investors. The course is
designed to develop investing knowledge empirically and through academic theory.
Required books: A Random Walk Down Wall Street, Burton G. Malkiel, 2023 edition, W.
W. Norton & Company, Inc. (RW)
Unconventional Success, David F. Swensen, 2005, Free Press (US)
Grading: Contribution to class discussion will account for 25% of the grade. The midterm
```

### [S2] `vault/raw/Asset Management Syllabus.pdf` — page 1
*section:* Privacy and Recording Notice · *layer:* raw · *matched by:* keyword #3 (1.44) + vector #4 (0.357) · *chunk:* `3f8d5907a6-001-002`

```text
[Privacy and Recording Notice]
Grading: Contribution to class discussion will account for 25% of the grade. The midterm
project will comprise 25% of the grade and the final project will account for 30%.
Assignments, collectively, will account for 10% of the course grade. Your Questions,
collectively, will account for 10% of the course grade. More than three absences will
adversely affect the class contribution grade.
Date Topic  Reading(s) / Speaker
August 27 Course overview &
 Investments exercise
September 1 Risk and Return US chapter 1 and RW chapters 1, 2, 13
 Manias, Bubbles & Crashes
September 3  U.S. Equities US pages 33-48 and RW chapters 3, 4
```

### [S3] `vault/raw/Asset Management Syllabus.pdf` — page 2
*section:* November 3 Behavioral Models RW 10 · *layer:* raw · *matched by:* keyword #4 (1.26) + vector #3 (0.361) · *chunk:* `3f8d5907a6-002-005`

```text
[November 3 Behavioral Models RW 10]
October 27 ETFs – speaker Bart Sikora - BlackRock iShares
October 29 Mutual Funds,  Carl Kawaja – Capital Group
 Fundamental Equities
November 3 Behavioral Models RW 10
 Behavioral mini-presentations
November 5 AI and Machine Learning for Art Amador – Quantum Street AI
 Investments – Speaker
November 10 Active and Passive Management US pages 203-207
   and US chapters 7, 8, 10
November 12 Smart Beta / Factor Investing RW pages 258-273
November 17 Portfolio Construction US chapter 3 and RW pages 347-370
November 19 Rebalancing & US chapter 6
 Volatility Harvesting
```

### [S4] `vault/wiki/Courses/Asset Management MBA 233.md` — section
*section:* Asset Management MBA 233 · *layer:* wiki · *matched by:* keyword #1 (5.82) + vector #1 (0.470) · *chunk:* `52f744914e-000-001`

```text
[Asset Management MBA 233]
Asset Management MBA 233
This course explores investment strategies for individuals and institutions, combining practical application with academic theory. Students will learn about various asset classes, portfolio construction, and investment analysis techniques.
## Logistics
- Class Hours: Tuesdays and Thursdays 2:00 – 3:30
- Class Location: Cheit Hall, C220
- Instructor: Sam Olesky
- Instructor Email: (contact details in the original source)
- Instructor Office Location: F502N
- Instructor Office Hours: by appointment
- Term Dates: Fall 2026
```

### [S5] `vault/wiki/Courses/Asset Management MBA 233.md` — section
*section:* Grading · *layer:* wiki · *matched by:* vector #8 (0.274) · *chunk:* `52f744914e-000-002`

```text
[Grading]
- Instructor Office Location: F502N
- Instructor Office Hours: by appointment
- Term Dates: Fall 2026
Grading
- Contribution to class discussion: 25%
- Midterm project: 25%
- Final project: 30%
- Assignments: 10%
- Questions: 10%
- More than three absences will adversely affect the class contribution grade.
Attendance and Lateness
- More than three absences will adversely affect the class contribution grade.
Assignments and Deadlines
- Assignments are to be completed independently.
Readings and Materials
- A Random Walk Down Wall Street, Burton G. Malkiel, 2023 edition, W. W. Norton & Company, Inc. (RW)
- Unconventional Success, David F. Swensen, 2005, Free Press (US) - Recommended
## Schedule Highlights
- First session: August 27
- Last session: December 3
- No class: November 24
- No class: November 26
- Midterm project work session: October 8
- Final project work session: December 3
```

### [S6] `vault/raw/Asset Management Syllabus.pdf` — page 3
*section:* (document start) · *layer:* raw · *matched by:* keyword #5 (1.24) + vector #9 (0.233) · *chunk:* `3f8d5907a6-003-008`

```text
[(document start)]
in this course will receive a failing grade in the course and will also be reported to the
University Center for Student Conduct.  In order to guarantee that you are not suspected of
cheating, please keep your eyes on your own materials and do not converse with others
during the quizzes and exams.
Plagiarism:  To copy text or ideas from another source without appropriate reference is
plagiarism and will result in a failing grade for your assignment and usually further
disciplinary action.  For additional information on plagiarism and how to avoid it, see, for
example:  http://gsi.berkeley.edu/teachingguide/misconduct/prevent-plag.html
Academic Integrity and Ethics:  Cheating on exams and plagiarism are two common
examples of dishonest, unethical behavior.  Honesty and integrity are of great importance in
```

## Actual answer from the model

```text
INSUFFICIENT EVIDENCE: the wiki does not contain the GSI for the Asset Management course.
Closest available: Academic Integrity and Ethics: Cheating on exams and plagiarism are two common examples of dishonest, unethical behavior. Honesty and integrity are of great importance in [S6].
```

## Citation check

- Machine check: **PASS** — declared insufficient evidence (no citation required)
- Markers resolving to a retrieved passage: S6
- Markers the model invented: none
- Declared insufficient evidence: True
- Reply-form contract violations: none
- Proper nouns in the answer absent from every cited passage: none

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
