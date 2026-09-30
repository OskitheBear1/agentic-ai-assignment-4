# Ask-mode evidence card — test-1

**Question:** How many points is global participation worth in the Negotiations course?

| Field | Value |
| --- | --- |
| Mode | `ask` (standalone; chat history not used) |
| Execution | **local** |
| Generation model | `gemma3n:e4b` |
| Embedding model | `embeddinggemma:300m` |
| Runtime | ollama 0.34.4 |
| Retrieval scope | all, top_k=6 |
| Retrieval time | 0.469 s |
| Generation time | 10.762 s |
| Tokens | 2464 prompt / 49 completion |
| Run at | 2026-09-29T20:53:40 |

## Retrieved passages

### [S1] `vault/raw/Negotiations Syllabus.pdf` — page 2
*section:* Course Description · *layer:* raw · *matched by:* keyword #3 (8.23) + vector #2 (0.565) · *chunk:* `0be2bed38d-002-003`

```text
[Course Description]
you'll practice the skills — communication, preparation, self-awareness — through weekly negotiation exercises.
Course Expectations & Ground Rules
This is an experiential, demanding course. You will negotiate almost every week, and your engagement directly affects your
peers' learning, not just your own. A few ground rules keep the exercises useful and the room safe to experiment in:
• Role instructions are confidential. Do not show or read them to other parties before or during a negotiation.
• Experiment with different tactics freely, but nothing involving physical intimidation or harassment.
Grading — 100 Points Total
Component When Points
Global participation (attendance, punctuality, engagement, quality of
discussion)
Weekly 40
Preparation (worksheets submitted before class) Weekly 20
Feedback (to negotiation partners) Weekly 20
In-class quizzes Sometime! 2-3 20
```

### [S2] `vault/raw/Negotiations Syllabus.pdf` — page 3
*section:* (document start) · *layer:* raw · *matched by:* keyword #2 (8.82) + vector #5 (0.476) · *chunk:* `0be2bed38d-003-007`

```text
[(document start)]
Specifically, for circumstances you couldn't reasonably have predicted 24 hours out, like sudden illness or injury, a family
emergency, or bereavement, we understand that you could not give advance warning. You should still notify us as soon as
you're able, even if that's after the fact. A brief email is enough to invoke this, formal documentation is only needed if the
absence extends beyond a single class.
Punctuality
• Missing more than 30 minutes of a class (arriving late or leaving early): –1 point.
• Missing more than 30 minutes of a class, without advance notice: –2 points.
Global participation score (engagement)
• We are grading your participation and engagement in class. Some people speak less than others, and that's OK. But if
you're checked ou or clearly not paying attention, we notice that and take that as part of the global participation score.
```

### [S3] `vault/raw/Negotiations Syllabus.pdf` — page 2
*section:* Course Description · *layer:* raw · *matched by:* keyword #5 (6.76) + vector #3 (0.556) · *chunk:* `0be2bed38d-002-004`

```text
[Course Description]
Weekly 40
Preparation (worksheets submitted before class) Weekly 20
Feedback (to negotiation partners) Weekly 20
In-class quizzes Sometime! 2-3 20
Press team assignment Once in the first 5 weeks (up to 3 bonus)
Participation (40 points)
Participation means showing up, on time and prepared, and contributing to discussion. Your attendance record and the quality
of your comments are both assessed — see the Policies section below for how absences and lateness affect this score.
Preparation (20 points)
Submit the preparation worksheet for each negotiation exercise before class starts. Late preparation sheets are not accepted
(see Late Assignment Policy); missing one costs 2 points.
Feedback (20 points)
• Give your negotiation partner at least one positive and one constructive comment immediately after each exercise.
```

### [S4] `vault/wiki/Courses/Negotiations MBA 252.md` — section
*section:* Grading · *layer:* wiki · *matched by:* keyword #1 (10.90) + vector #1 (0.594) · *chunk:* `0a0434975a-000-002`

```text
[Grading]
- Press team assignment due within the first 5 weeks, with up to 3 bonus points.
- Pop quiz to test fundamental negotiation concepts.
Grading
- Global participation (attendance, punctuality, engagement, discussion quality): 40 points.
- Preparation (worksheets submitted before class): 20 points. Late preparation sheets are not accepted; missing one costs 2 points.
- Feedback (to negotiation partners): 20 points. Worth ~2 points per week.
- In-class quizzes: 20 points (some time).
- Press team assignment: Up to 3 bonus points.
Attendance and Lateness
- Notify the professor by email at least 24 hours in advance for missed classes.
- Missed a class with 24+ hour notice: -2 points.
- Missed a class without 24-hour notice: -3 points.
- First missed class is free if the professor is notified in advance.
- Missing more than 30 minutes of class (late or early): -1 point.
```

### [S5] `vault/raw/AgenticAISyllabus.pdf` — page 5
*section:* (document start) · *layer:* raw · *matched by:* keyword #20 (2.34) + vector #8 (0.428) · *chunk:* `4b5a9caae6-005-015`

```text
[(document start)]
Each assignment is scored out of 10 points using the shared framework above, applied to the specific assignment
brief. For Assignments 1–4, the lowest of the four scores is dropped and the remaining three scores are
combined equally to make 50% of the final grade. Assignment 5 makes up 30%; attendance makes up 20%.
You get a pass on one missed session in the attendance grade, so you are not penalized for missing a single
class.
Each assignment will have a current Definition of Done in its assignment brief or class deck. That brief may
be updated as the course develops; clearly announced updates supersede this syllabus overview. The shared
grading categories and the assignment’s overall weight remain the consistent structure.
Grade Dispute Policy
If you would like an assignment re-graded, submit a written petition within 72 hours of receiving the grade.
```

### [S6] `vault/wiki/Courses/Negotiations MBA 252.md` — section
*section:* Attendance and Lateness · *layer:* wiki · *matched by:* keyword #7 (4.76) + vector #7 (0.435) · *chunk:* `0a0434975a-000-003`

```text
[Attendance and Lateness]
- First missed class is free if the professor is notified in advance.
- Missing more than 30 minutes of class (late or early): -1 point.
- Missing more than 30 minutes of class without notice: -2 points.
Assignments and Deadlines
- Preparation worksheets are due at the start of class; no late submissions.
- Late assignments are penalized 1 point per day late.
- Feedback to negotiation partners is due by Friday midnight each week via email.
- Press team assignment involves filming and analyzing other students' negotiations.
- Preparation worksheets are never accepted late.
```

## Actual answer from the model

```text
**ANSWER:** Global participation is worth 40 points in the Negotiaions course [S1][S3][S4]. This includes attendance, punctuality, engagement, and the quality of discussion [S3][S4].
```

## Citation check

- Machine check: **PASS** — cited S1, S3, S4 | unused retrieved passages: S2, S5, S6 | spelling flags (in the answer, absent from every cited passage): Negotiaions
- Markers resolving to a retrieved passage: S1, S3, S4
- Markers the model invented: none
- Declared insufficient evidence: False
- Reply-form contract violations: none
- Proper nouns in the answer absent from every cited passage: Negotiaions

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
