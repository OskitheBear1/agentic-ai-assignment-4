# Ask-mode evidence card — test-3

**Question:** Which of my Fall 2026 courses meet on Wednesdays, and at what times?

| Field | Value |
| --- | --- |
| Mode | `ask` (standalone; chat history not used) |
| Execution | **local** |
| Generation model | `gemma3n:e4b` |
| Embedding model | `embeddinggemma:300m` |
| Runtime | ollama 0.34.4 |
| Retrieval scope | all, top_k=6 |
| Retrieval time | 0.156 s |
| Generation time | 10.402 s |
| Tokens | 2536 prompt / 80 completion |
| Run at | 2026-09-29T20:54:01 |

## Retrieved passages

### [S1] `vault/raw/Negotiations Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #1 (7.73) + vector #8 (0.450) · *chunk:* `0be2bed38d-001-001`

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

### [S2] `vault/raw/AgenticAISyllabus.pdf` — page 1
*section:* MBA 290T: Fundamental of Agentic AI · *layer:* raw · *matched by:* keyword #2 (4.93) + vector #9 (0.447) · *chunk:* `4b5a9caae6-001-001`

```text
[MBA 290T: Fundamental of Agentic AI]
MBA 290T: Fundamental of Agentic AI
Haas School of Business,
UC–Berkeley Fall 2026
Co-Instructors
Alexandre Mas
Email: amas@berkeley.edu
Office Hours:By appointment only
Pepe Alonso
Email: pepe@berkeley.edu
Office Hours:By appointment only
Class Schedule
Lectures:Tuesdays 4:00 – 6:00 pm PT in N570
First class:Tuesday, August 25, 2026
Last class:Tuesday, October 6, 2026
Final assignment (Assignment 5) due:Tuesday, October 13, 2026
Seven Tuesday sessions, beginning with Class 1 on 8/25 and ending with Class 7 on 10/6.
There isno final examand no final presentation. The course is assessed entirely through attendance and
five graded assignments.
Course Objective
Fundamental of Agentic AI is not a survey course about AI, and it is not a prompt-engineering workshop. In
seven sessions we go from “what is a variable” to building and evaluating a tool-using AI agent — covering
```

### [S3] `vault/raw/Asset Management Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #7 (3.78) + vector #11 (0.429) · *chunk:* `3f8d5907a6-001-001`

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

### [S4] `vault/raw/Data Mining Syllabus.pdf` — page 1
*section:* Instructor Luyi Yang · *layer:* raw · *matched by:* keyword #13 (2.14) + vector #6 (0.491) · *chunk:* `fc1ba59e46-001-003`

```text
[Instructor Luyi Yang]
Class Meetings
Day Dates Time Room
Wednesday Aug 26 - Oct 28, 2026 (10 weeks) 6:00pm-9:30pm PT Chou Hall N300
Instructor Luyi Yang
luyiyang@haas.berkeley.edu
Office: F557 (Email for in-person appointments)
Assistant Ziyi Liu zyliu2023@berkeley.edu
Prerequisite   200S Data and Decisions
Optional Textbook
Selected chapters of Business Analytics (4th edition) by Camm et al.
Publisher: Cengage Learning
```

### [S5] `vault/raw/Data Mining Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #16 (1.85) + vector #5 (0.494) · *chunk:* `fc1ba59e46-001-002`

```text
[(document start)]
business decisions in a variety of real-world business applications, including (but not limited to)
marketing, finance, and operations. Descriptive models provide insights into “What did happen?” and
predictive models, “What could happen?” Topics to be introduced include:
• Exploratory data analysis: frequency distributions, cross-tabulation
• Descriptive data mining: k-means clustering, association rules, text mining
• Predictive data mining: binary classification, logistic regression, k-nearest-neighbors,
classification trees, ensemble methods, Responsible AI
Class Meetings
Day Dates Time Room
Wednesday Aug 26 - Oct 28, 2026 (10 weeks) 6:00pm-9:30pm PT Chou Hall N300
```

### [S6] `vault/raw/Data Mining Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #6 (3.88) + vector #20 (0.397) · *chunk:* `fc1ba59e46-001-001`

```text
[(document start)]
Page 1 of 4
 Haas School of Business
 University of California, Berkeley
Syllabus for MBA/EWMBA 247
Descriptive and Predictive Data Mining
Fall 2026 (2 units)
Course Overview
The importance of data cannot be overemphasized. With the recent explosion in large-scale, high-
resolution data, managers are increasingly required to make data-driven decisions, rather than rely on
experience and intuition alone. A key step in data-driven decision-making is data mining, which
enables businesses to extract useful information and valuable insights from otherwise massive and
unorganized data. This hands-on, introductory course teaches you the fundamental principles and
practical skills you need to develop data mining models that describe and predict the effects of
business decisions in a variety of real-world business applications, including (but not limited to)
```

## Actual answer from the model

```text
**ANSWER:** MBA 252 meets on Wednesdays from 8:00–11:00 AM and MBA 252.2 meets on Wednesdays from 2:00–5:00 PM [S1]. Data Mining meets on Wednesdays from 6:00pm-9:30pm [S4][S5][S6].
```

## Citation check

- Machine check: **PASS** — cited S1, S4, S5, S6 | unused retrieved passages: S2, S3
- Markers resolving to a retrieved passage: S1, S4, S5, S6
- Markers the model invented: none
- Declared insufficient evidence: False
- Reply-form contract violations: none
- Proper nouns in the answer absent from every cited passage: none

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
