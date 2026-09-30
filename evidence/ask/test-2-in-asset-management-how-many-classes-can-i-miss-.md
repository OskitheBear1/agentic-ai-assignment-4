# Ask-mode evidence card — test-2

**Question:** In Asset Management, how many classes can I miss before it starts to hurt my grade?

| Field | Value |
| --- | --- |
| Mode | `ask` (standalone; chat history not used) |
| Execution | **local** |
| Generation model | `gemma3n:e4b` |
| Embedding model | `embeddinggemma:300m` |
| Runtime | ollama 0.34.4 |
| Retrieval scope | all, top_k=6 |
| Course filter | question names only "Asset Management"; evidence limited to that course |
| Retrieval time | 2.625 s |
| Generation time | 6.983 s |
| Tokens | 2495 prompt / 28 completion |
| Run at | 2026-09-29T21:55:09 |

## Retrieved passages

### [S1] `vault/raw/Asset Management Syllabus.pdf` — page 1
*section:* Privacy and Recording Notice · *layer:* raw · *matched by:* keyword #3 (1.34) + vector #1 (0.569) · *chunk:* `3f8d5907a6-001-002`

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

### [S2] `vault/raw/Asset Management Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #2 (3.29) + vector #3 (0.496) · *chunk:* `3f8d5907a6-001-001`

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

### [S3] `vault/raw/Asset Management Syllabus.pdf` — page 3
*section:* (document start) · *layer:* raw · *matched by:* keyword #5 (1.00) + vector #5 (0.425) · *chunk:* `3f8d5907a6-003-008`

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

### [S4] `vault/wiki/Courses/Asset Management MBA 233.md` — section
*section:* Asset Management MBA 233 · *layer:* wiki · *matched by:* keyword #1 (7.24) + vector #4 (0.487) · *chunk:* `52f744914e-000-001`

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
*section:* Grading · *layer:* wiki · *matched by:* keyword #6 (0.88) + vector #2 (0.547) · *chunk:* `52f744914e-000-002`

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

### [S6] `vault/raw/Asset Management Syllabus.pdf` — page 4
*section:* (document start) · *layer:* raw · *matched by:* keyword #7 (0.71) + vector #6 (0.390) · *chunk:* `3f8d5907a6-004-010`

```text
[(document start)]
There may be times when there is temptation to engage in some kind of cheating in order to
improve a grade or otherwise advance your career.  This could be as blatant as having
someone else sit for you in an exam, or submitting a written assignment that has been copied
from another source.  And it could be as subtle as glancing at a fellow student’s exam when
you are unsure of an answer to a question and are looking for some confirmation.  One might
do any of these things and potentially not get caught.  However, if you cheat, no matter how
much you may have learned in this class, you have failed to learn perhaps the most important
lesson of all.
```

## Actual answer from the model

```text
ANswer: You can miss more than three absences before it adversely affects the class contribution grade [S1][S5].
```

## Citation check

- Machine check: **PASS** — cited S1, S5 | unused retrieved passages: S2, S3, S4, S6
- Markers resolving to a retrieved passage: S1, S5
- Markers the model invented: none
- Declared insufficient evidence: False
- Reply-form contract violations: none
- Proper nouns in the answer absent from every cited passage: none

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
