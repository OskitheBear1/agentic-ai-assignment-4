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
| Retrieval time | 0.336 s |
| Generation time | 7.897 s |
| Tokens | 2352 prompt / 51 completion |
| Run at | 2026-09-29T20:33:10 |

## Retrieved passages

### [S1] `vault/raw/Negotiations Syllabus.pdf` — page 2
*section:* Course Description · *layer:* raw · *matched by:* keyword #4 (7.75) + vector #1 (0.565) · *chunk:* `0be2bed38d-002-003`

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
*section:* Course Description · *layer:* raw · *matched by:* keyword #6 (6.60) + vector #2 (0.556) · *chunk:* `0be2bed38d-002-004`

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

### [S3] `vault/raw/Negotiations Syllabus.pdf` — page 2
*section:* Course Description · *layer:* raw · *matched by:* keyword #5 (7.67) + vector #3 (0.553) · *chunk:* `0be2bed38d-002-005`

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

### [S4] `vault/wiki/Courses/Negotiations MBA 252.md` — section
*section:* Negotiations MBA 252 · *layer:* wiki · *matched by:* keyword #1 (11.59) + vector #5 (0.498) · *chunk:* `6bebd4a9dc-000-001`

```text
[Negotiations MBA 252]
Negotiations MBA 252
This course builds skills in negotiation for business and life, covering strategic frameworks and the psychology of negotiation through weekly exercises. Students will practice communication, preparation, and self-awareness.
Logistics
- Wednesdays from 8:00–11:00 AM or 2:00–5:00 PM in C220.
- Dates: 8/26, 9/2, 9/9, 9/16, 9/23, 9/30, 10/7, 10/14, 10/21, 10/28.
- Instructor: Solène Delecourt.
- GSI: Oranda Hou.
- GSR: Irina Liu.
Grading
- Global participation: 40 points (attendance, punctuality, engagement, discussion quality).
- Preparation: 20 points (preparation worksheets submitted before class; missing one costs 2 points).
- Feedback: 20 points (at least one positive and one constructive comment to each negotiation partner via email by Friday midnight).
- In-class quizzes: 20 points (some time during the term).
```

### [S5] `vault/wiki/Courses/Negotiations MBA 252.md` — section
*section:* Grading · *layer:* wiki · *matched by:* keyword #2 (8.40) + vector #4 (0.543) · *chunk:* `6bebd4a9dc-000-002`

```text
[Grading]
- In-class quizzes: 20 points (some time during the term).
- Press team assignment: 10 points (optional, up to 3 bonus points; video reel of another student's negotiation).
- Preparation worksheets are not accepted late.
Attendance and Lateness
- Notify the professor by email at least 24 hours in advance for missed classes.
- Missed a class with 24+ hours' notice: -2 points.
- Missed a class without 24 hours' notice: -3 points.
- First missed class is free if the professor is notified in advance.
- Missing more than 30 minutes of class: -1 point (late) or -2 points (without notice).
- Regular absence or lack of engagement in class will be reflected in the global participation score.
```

### [S6] `vault/raw/AgenticAISyllabus.pdf` — page 5
*section:* (document start) · *layer:* raw · *matched by:* keyword #19 (2.37) + vector #9 (0.428) · *chunk:* `4b5a9caae6-005-015`

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

## Actual answer from the model

```text
**ANswer:** Global participation is worth 40 points in the Negotiaions course [S1][S4]. Global participation is assessed based on attendance, punctuality, engagement, and the quality of discussion [S1][S4].
```

## Citation check

- Machine check: **PASS** — cited S1, S4 | unused retrieved passages: S2, S3, S5, S6
- Markers resolving to a retrieved passage: S1, S4
- Markers the model invented: none
- Declared insufficient evidence: False

> The machine check verifies that every citation marker points at a passage that
> was actually retrieved. Whether the passage *supports* the sentence is a human
> judgement — the full passage text is printed above so it can be checked.
