# Ask-mode evidence card — mode-check-cited-offline

**Question:** What are the graded components of Data Mining MBA 247?

| Field | Value |
| --- | --- |
| Mode | `ask` (standalone; chat history not used) |
| Execution | **local** |
| Generation model | `gemma3n:e4b` |
| Embedding model | `embeddinggemma:300m` |
| Runtime | ollama 0.34.4 |
| Retrieval scope | all, top_k=6 |
| Course filter | question names only "Data Mining"; evidence limited to that course |
| Retrieval time | 0.158 s |
| Generation time | 8.21 s |
| Tokens | 2339 prompt / 57 completion |
| Run at | 2026-09-29T21:24:46 |

## Retrieved passages

### [S1] `vault/raw/Data Mining Syllabus.pdf` — page 1
*section:* (document start) · *layer:* raw · *matched by:* keyword #2 (4.42) + vector #2 (0.603) · *chunk:* `fc1ba59e46-001-001`

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

### [S2] `vault/raw/Data Mining Syllabus.pdf` — page 3
*section:* Software · *layer:* raw · *matched by:* keyword #3 (3.24) + vector #7 (0.471) · *chunk:* `fc1ba59e46-003-009`

```text
[Software]
simple calculation problems meant to reinforce your conceptual understanding of the data mining
methods taught in class. These concept checks will be auto-graded on bCourses.
Group Workshop Assignments: In group assignments, you will analyze (large-scale) data sets and
solve data-driven problems using software tools. You work on group assignments during workshop
sessions in Weeks 3, 5, and 8, and hand in your write-up within a week after the day of the workshop.
Students work in groups of 3 or 4. You can choose to form your own group or be randomly assigned
to a group.
Conscientious contributions to the group assignments are strictly required. To enforce this policy, I will
solicit feedback from each of you about the contributions of your team members to group work.
Failure to contribute adequately to the group will result in a grade penalty in this course. In addition, a
```

### [S3] `vault/raw/Data Mining Syllabus.pdf` — page 2
*section:* (document start) · *layer:* raw · *matched by:* keyword #6 (1.25) + vector #5 (0.492) · *chunk:* `fc1ba59e46-002-004`

```text
[(document start)]
Page 2 of 4
Course Format, Topics, and Schedule
The course consists of lectures, in-class discussions, and workshop sessions that provide hands-on
opportunities to apply course concepts, with guidance from the instructional team. This course covers
three major topics: Exploratory Data Analysis (as the first step to interpret data, and as the last step
to convey data), Descriptive Data Mining (using data to identify relationships, aka Unsupervised
Machine Learning), and Predictive Data Mining (using data to make a prediction, aka Supervised
Machine Learning). The week-by-week topics covered are as follows:
Session
(Wed) Topic Reading Due Before Class
(Tue 10 pm)
Week 1
Aug 26
Exploratory Data Analysis
Frequency Distributions, Cross Tabulation
Applications: online retail, gender bias in Berkeley
graduate admissions, dishonesty in mileage reporting for
car insurance
Camm Ch 2,
3.2
```

### [S4] `vault/wiki/Courses/Data Mining MBA 247.md` — section
*section:* Data Mining MBA 247 · *layer:* wiki · *matched by:* keyword #1 (5.87) + vector #1 (0.722) · *chunk:* `71de72b583-000-001`

```text
[Data Mining MBA 247]
Data Mining MBA 247
This course introduces the fundamental principles and practical skills of data mining, focusing on extracting insights from large datasets for data-driven decision-making. Topics include exploratory and descriptive data mining, as well as predictive modeling techniques.
Logistics
- Wednesdays Aug 26 - Oct 28, 2026 (10 weeks) 6:00pm-9:30pm PT
- Chou Hall N300
- Instructor: Luyi Yang
- Email: (contact details in the original source)
- Office: F557 (Email for in-person appointments)
- Assistant: Ziyi Liu (contact details in the original source)
## Grading
- Class Participation: 20%
- 4 Individual Concept Checks: 20%
- 3 Group Workshop Assignments: 30%
- Final Exam: 30%
```

### [S5] `vault/wiki/Courses/Data Mining MBA 247.md` — section
*section:* Attendance and Lateness · *layer:* wiki · *matched by:* vector #6 (0.487) · *chunk:* `71de72b583-000-002`

```text
[Attendance and Lateness]
## Grading
- Class Participation: 20%
- 4 Individual Concept Checks: 20%
- 3 Group Workshop Assignments: 30%
- Final Exam: 30%
Attendance and Lateness
- Class attendance is required, and cold calls will occur.
Assignments and Deadlines
- Group workshop assignments are due within a week after the workshop session.
- Students work in groups of 3 or 4.
Readings and Materials
- Selected chapters of Business Analytics (4th edition) by Camm et al. (required textbook)
## Schedule Highlights
- Online Remote Final Exam Oct 28
```

### [S6] `vault/raw/Data Mining Syllabus.pdf` — page 3
*section:* Software · *layer:* raw · *matched by:* keyword #9 (1.10) + vector #3 (0.506) · *chunk:* `fc1ba59e46-003-010`

```text
[Software]
Failure to contribute adequately to the group will result in a grade penalty in this course. In addition, a
pattern of such behavior will result in an academic performance review.
Final Exam: You will take an online exam to demonstrate your knowledge of data mining.
```

## Actual answer from the model

```text
ANswer: The graded components of Data Mining MBA 247 are Class Participation (20%), 4 Individual Concept Checks (20%), 3 Group Workshop Assignments (30%), and a Final Exam (30%) [S4][S5].
```

## Citation check

- Machine check: **PASS** — cited S4, S5 | unused retrieved passages: S1, S2, S3, S6
- Markers resolving to a retrieved passage: S4, S5
- Markers the model invented: none
- Declared insufficient evidence: False
- Reply-form contract violations: none
- Proper nouns in the answer absent from every cited passage: none

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
