#!/usr/bin/env bash
# The four mode-boundary checks the assignment asks for, in one reproducible run.
# Output is teed to evidence/modes/. Run it offline to produce the offline proof.
set -uo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

stamp="$(date +%Y%m%d-%H%M%S)"
label="${1:-local}"
out="evidence/modes/${stamp}-mode-checks-${label}.txt"
mkdir -p evidence/modes

{
  echo "==============================================================="
  echo " MODE BOUNDARY CHECKS — ${label}"
  echo " $(date)"
  echo "==============================================================="
  echo
  echo "### Network reachability at start of run"
  echo "\$ curl -s -m 5 https://ollama.com"
  if curl -s -m 5 -o /dev/null https://ollama.com 2>/dev/null; then
    echo "REACHABLE — this run is online"
  else
    echo "UNREACHABLE — no internet, which is what the offline run must show"
  fi
  echo "\$ ping -c 1 -W 2000 1.1.1.1"
  ping -c 1 -W 2000 1.1.1.1 2>&1 | tail -3
  echo
  echo "### Runtime and model identity"
  echo "\$ ./wiki doctor"
  ./wiki doctor
  echo
  echo "==============================================================="
  echo "CHECK 1 — chat: capability questions must not search the notes,"
  echo "          must not cite, and must not refuse for lack of evidence."
  echo "CHECK 2 — chat follow-up: 'make that shorter' must use the"
  echo "          conversation, not a fresh lookup."
  echo "CHECK 3 — chat: a fact the user asserts is conversation, not evidence."
  echo "CHECK 4 — chat: a real syllabus question does trigger retrieval + citation."
  echo "==============================================================="
  echo
  printf '%s\n' \
    'what can you help me with?' \
    'what can we do?' \
    'Draft me a 4-bullet plan for keeping on top of all four courses this term.' \
    'make that shorter' \
    'Remember that my Negotiations final exam is on December 15 at 9am.' \
    'How many points is participation worth in Negotiations?' \
    '/exit' | ./wiki chat
  echo
  echo "==============================================================="
  echo "CHECK 5 — search: original passages and paths, NO generated answer."
  echo "==============================================================="
  echo "\$ ./wiki search \"attendance absences deductions\" -k 3"
  ./wiki search "attendance absences deductions" -k 3
  echo
  echo "--- and with the language model not required at all: ---"
  echo "\$ ./wiki search \"hedge funds speaker\" --no-vectors -k 2"
  ./wiki search "hedge funds speaker" --no-vectors -k 2
  echo
  echo "==============================================================="
  echo "CHECK 6 — ask is isolated from chat. The 'December 15' final exam"
  echo "          date was asserted in the chat session above and exists in"
  echo "          no source. Ask mode must not know it."
  echo "==============================================================="
  echo "\$ ./wiki ask \"When is the Negotiations final exam?\" --test-id mode-check-isolation"
  ./wiki ask "When is the Negotiations final exam?" --test-id "mode-check-isolation-${label}"
  echo
  echo "==============================================================="
  echo "CHECK 7 — a standalone ask with citations, for contrast."
  echo "==============================================================="
  echo "\$ ./wiki ask \"What are the graded components of Data Mining MBA 247?\""
  ./wiki ask "What are the graded components of Data Mining MBA 247?" --test-id "mode-check-cited-${label}"
  echo
  echo "==============================================================="
  echo "CHECK 8 — vault integrity"
  echo "==============================================================="
  echo "\$ ./wiki check"
  ./wiki check
  echo
  echo "### Network reachability at end of run"
  if curl -s -m 5 -o /dev/null https://ollama.com 2>/dev/null; then
    echo "REACHABLE — this run is online"
  else
    echo "UNREACHABLE — no internet"
  fi
  echo
  echo "=== end of mode checks ==="
} 2>&1 | tee "$out"

# Strip ANSI colour so the saved file reads cleanly in a browser or editor.
/usr/bin/sed -i '' $'s/\x1b\\[[0-9;]*m//g' "$out"
echo
echo "saved: $out"
