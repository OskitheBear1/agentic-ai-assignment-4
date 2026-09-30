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
| Retrieval time | 0.153 s |
| Generation time | 6.689 s |
| Tokens | 2293 prompt / 31 completion |
| Run at | 2026-09-29T20:33:34 |

## Retrieved passages

### [S1] `vault/raw/Asset Management Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #2 (6.47) + vector #2 (0.426) · *chunk:* `3f8d5907a6-001-001`

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

### [S2] `vault/raw/Asset Management Syllabus.pdf` — page 2
*section:* November 3 Behavioral Models RW 10 · *layer:* raw · *matched by:* keyword #9 (2.47) + vector #4 (0.361) · *chunk:* `3f8d5907a6-002-005`

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

### [S3] `vault/wiki/Courses/Asset Management MBA 233.md` — section
*section:* Asset Management MBA 233 · *layer:* wiki · *matched by:* keyword #1 (10.11) + vector #1 (0.476) · *chunk:* `18878f29f9-000-001`

```text
[Asset Management MBA 233]
Asset Management MBA 233
This course explores investment strategies for individuals and institutions, combining practical application with academic theory. Students will learn about various investment types, security selection, and portfolio construction.
## Logistics
- Class Hours: Tuesdays and Thursdays 2:00 – 3:30
- Class Location: Cheit Hall, C220
- Instructor: Sam Olesky
- Instructor Email: (contact details in the original source)
- Instructor Office Location: F502N
- Instructor Office Hours: by appointment
- Course Dates: Fall 2026
```

### [S4] `vault/raw/AgenticAISyllabus.pdf` — page 1
*section:* MBA 290T: Fundamental of Agentic AI · *layer:* raw · *matched by:* keyword #3 (4.02) + vector #15 (0.325) · *chunk:* `4b5a9caae6-001-002`

```text
[MBA 290T: Fundamental of Agentic AI]
seven sessions we go from “what is a variable” to building and evaluating a tool-using AI agent — covering
programming foundations, full-stack software systems, machine learning, deep learning and transformers,
LLM behavior and retrieval, and agent architecture.
The focus isconceptual fluency that survives the tools. Models and frameworks change every quarter;
the mechanisms underneath them do not. You will leave able to build, evaluate, and lead technical AI work
— not just talk about it.
Concretely, the course targetsLevel 2 fluency: you do not need a PhD to reason about AI systems, but
knowing how to use ChatGPT is not a differentiator either. Level 2 is understanding how these systems
actually work well enough to make good decisions about them.
Learning Outcomes
A student who successfully completes this course will be able to:
```

### [S5] `vault/raw/Asset Management Syllabus.pdf` — page 1
*section:* Privacy and Recording Notice · *layer:* raw · *matched by:* keyword #14 (0.96) + vector #5 (0.357) · *chunk:* `3f8d5907a6-001-002`

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

### [S6] `vault/raw/Negotiations Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #6 (3.74) + vector #14 (0.325) · *chunk:* `0be2bed38d-001-001`

```text
[(document start)]
Haas School of Business — University of California, Berkeley
Negotiations and Conflict Resolution
MBA 252 — Fall 2026
Professor: Solène Delecourt  (negotiationsolene@gmail.com)
GSI: Oranda Hou
GSR: Irina Liu
Day: Wednesdays
Time: MBA252.1 — 8:00–11:00 AM   |   MBA252.2 — 2:00–5:00 PM
Location: C220
Dates: 8/26, 9/2, 9/9, 9/16, 9/23, 9/30, 10/7, 10/14, 10/21, 10/28
This is a living document, updated periodically based on your feedback
```

## Actual answer from the model

```text
INSUFFICIENT EVIDENCE: the wiki does not contain the GSI for the Asset Management course.
Closest available: Irina Liu [S6].
```

## Citation check

- Machine check: **PASS** — declared insufficient evidence (no citation required)
- Markers resolving to a retrieved passage: S6
- Markers the model invented: none
- Declared insufficient evidence: True

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
