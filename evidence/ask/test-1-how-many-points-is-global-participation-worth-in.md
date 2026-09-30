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
| Course filter | question names only "Negotiations"; evidence limited to that course |
| Retrieval time | 1.433 s |
| Generation time | 15.389 s |
| Tokens | 2466 prompt / 43 completion |
| Run at | 2026-09-29T21:54:59 |

## Retrieved passages

### [S1] `vault/raw/Negotiations Syllabus.pdf` — page 2
*section:* Course Description · *layer:* raw · *matched by:* keyword #2 (5.24) + vector #2 (0.565) · *chunk:* `0be2bed38d-002-003`

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

### [S2] `vault/raw/Negotiations Syllabus.pdf` — page 2
*section:* Course Description · *layer:* raw · *matched by:* keyword #3 (4.69) + vector #4 (0.553) · *chunk:* `0be2bed38d-002-005`

```text
[Course Description]
Feedback (20 points)
• Give your negotiation partner at least one positive and one constructive comment immediately after each exercise.
• Email written feedback to your partner by Friday midnight each week, cc'ing the class email with “[Feedback
Submission]” in the subject line.
• Worth ~2 points per week, including Week 10.
Pop quiz (20 points)
• Pop quiz in class to test your basic knowledge of fundamental negotiation concepts
Optional: Press team assignment (up to 3 bonus points)
• Make a video reel of the highlights of someone else's negotiation
```

### [S3] `vault/raw/Negotiations Syllabus.pdf` — page 2
*section:* Course Description · *layer:* raw · *matched by:* keyword #5 (3.70) + vector #3 (0.556) · *chunk:* `0be2bed38d-002-004`

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
*section:* Grading · *layer:* wiki · *matched by:* keyword #1 (5.35) + vector #1 (0.594) · *chunk:* `0a0434975a-000-002`

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

### [S5] `vault/wiki/Courses/Negotiations MBA 252.md` — section
*section:* Negotiations MBA 252 · *layer:* wiki · *matched by:* keyword #6 (3.41) + vector #9 (0.425) · *chunk:* `0a0434975a-000-001`

```text
[Negotiations MBA 252]
Negotiations MBA 252
This course builds skills in negotiation for business and life, covering strategic frameworks and the psychology of negotiation through weekly exercises. Students will practice communication, preparation, and self-awareness.
Logistics
- Wednesdays from 8:00–11:00 AM or 2:00–5:00 PM in C220.
- Dates: 8/26, 9/2, 9/9, 9/16, 9/23, 9/30, 10/7, 10/14, 10/21, 10/28.
- First week focuses on fundamentals with reading from Thompson's 'The Mind and Heart of the Negotiator'.
- Press team assignment due within the first 5 weeks, with up to 3 bonus points.
- Pop quiz to test fundamental negotiation concepts.
```

### [S6] `vault/wiki/Courses/Negotiations MBA 252.md` — section
*section:* Attendance and Lateness · *layer:* wiki · *matched by:* keyword #9 (1.84) + vector #7 (0.435) · *chunk:* `0a0434975a-000-003`

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
ANswer: Global participation is worth 40 points in the Negotiaions course [S4][S5]. This includes attendance, punctuality, engagement, and the quality of discussion [S4].
```

## Citation check

- Machine check: **PASS** — cited S4, S5 | unused retrieved passages: S1, S2, S3, S6 | spelling flags (in the answer, absent from every cited passage): Negotiaions
- Markers resolving to a retrieved passage: S4, S5
- Markers the model invented: none
- Declared insufficient evidence: False
- Reply-form contract violations: none
- Proper nouns in the answer absent from every cited passage: Negotiaions

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
