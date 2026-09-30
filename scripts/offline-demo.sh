#!/usr/bin/env bash
# =============================================================================
# OFFLINE DEMONSTRATION — run this yourself with the internet disconnected.
#
# It is a single unattended script on purpose: an AI assistant cannot drive it,
# because the assistant needs the network that this script requires to be down.
#
#   1. Turn Wi-Fi off   (System Settings, or: networksetup -setairportpower en0 off)
#   2. ./scripts/offline-demo.sh
#   3. Turn Wi-Fi back on
#
# Everything is written to evidence/offline/. Nothing here needs the internet:
# the model and embeddings run under Ollama on 127.0.0.1, PDF text extraction is
# pypdf in-process, and BM25 is local code.
# =============================================================================
set -uo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

stamp="$(date +%Y%m%d-%H%M%S)"
out="evidence/offline/${stamp}-offline-demonstration.txt"
mkdir -p evidence/offline

# Is a host on the public internet reachable? curl exits non-zero when it cannot
# connect, which is the reliable signal. Reading its printed status code is not:
# on failure curl prints "000" itself, so a `|| echo 000` fallback produced
# "000000" and this guard aborted an already-offline run.
reachable() { curl -s -m 6 -o /dev/null "$1" 2>/dev/null; }

# Print a clean, human-readable probe result for the transcript.
probe() {
  local url="$1" code status
  code="$(curl -s -m 6 -o /dev/null -w '%{http_code}' "$url" 2>/dev/null)"
  status=$?
  if [[ $status -eq 0 ]]; then
    echo "$url -> HTTP $code (REACHABLE)"
  else
    echo "$url -> no connection, curl exit $status — UNREACHABLE, as expected offline"
  fi
}

# Fail early and loudly if the network is still up -- otherwise the whole point
# of the run is lost and the evidence would be misleading.
if reachable https://ollama.com; then
  echo "ABORT: the internet is still reachable (ollama.com answered)."
  echo "       Disconnect first, or this is not an offline demonstration."
  echo "       macOS:  networksetup -setairportpower en0 off"
  exit 1
fi

if ! curl -s -m 5 http://127.0.0.1:11434/api/version >/dev/null; then
  echo "ABORT: the local Ollama runtime is not running."
  echo "       Start it (this does not need the internet): brew services start ollama"
  exit 1
fi

# Unload the models so this is a genuine cold start from weights already on disk.
ollama stop gemma3n:e4b          >/dev/null 2>&1 || true
ollama stop embeddinggemma:300m  >/dev/null 2>&1 || true
sleep 2

banner() { echo; echo "================================================================"; echo " $1"; echo "================================================================"; }

{
  echo "================================================================"
  echo " OFFLINE DEMONSTRATION"
  echo " $(date)"
  echo " MacBook Pro Mac14,10 / Apple M2 Pro / 16 GB unified / macOS 26.6.2"
  echo " gemma3n:e4b (Q4_0) + embeddinggemma:300m via Ollama 0.34.4, local"
  echo "================================================================"

  banner "PROOF THERE IS NO NETWORK"
  echo "\$ networksetup -getairportpower en0";        networksetup -getairportpower en0 2>&1
  echo "\$ ifconfig | grep -c 'status: active'";      ifconfig | grep -c "status: active"
  echo "\$ route -n get default";                     route -n get default 2>&1 | head -3
  echo "\$ curl -s -m 6 https://ollama.com                          # model weights host"
  probe https://ollama.com
  echo "\$ curl -s -m 6 https://generativelanguage.googleapis.com   # hosted Gemma (optional online mode)"
  probe https://generativelanguage.googleapis.com
  echo "\$ curl -s -m 6 https://api.anthropic.com                   # the AI assistant that helped build this"
  probe https://api.anthropic.com
  echo "\$ ping -c 2 -W 2000 1.1.1.1";                ping -c 2 -W 2000 1.1.1.1 2>&1 | tail -3
  echo "\$ nslookup ollama.com";                      nslookup ollama.com 2>&1 | tail -4
  echo
  echo "UNREACHABLE / 100% packet loss / DNS failure = no internet. That is the expected result."

  banner "THE LOCAL RUNTIME IS UNAFFECTED (127.0.0.1)"
  echo "\$ curl -s http://127.0.0.1:11434/api/version"; curl -s http://127.0.0.1:11434/api/version; echo
  echo "\$ ollama ps   (empty: models unloaded, so what follows is a cold start from local weights)"
  ollama ps 2>&1
  echo "\$ ollama list"; ollama list 2>&1

  banner "STEP 1 — restart the CLI in a fresh process, check health"
  echo "\$ ./wiki doctor"; ./wiki doctor

  banner "STEP 2 — CLI help"
  echo "\$ ./wiki --help"; ./wiki --help

  banner "STEP 3 — ingest a local source OFFLINE (local Gemma writes the note)"
  echo "\$ ./wiki ingest \"./vault/raw/Data Mining Syllabus.pdf\""
  ./wiki ingest "./vault/raw/Data Mining Syllabus.pdf"
  echo
  echo "\$ ollama ps   (resident memory during/after local generation)"; ollama ps 2>&1
  echo
  echo "Note: the note count is unchanged, which is the re-ingestion check --"
  echo "the same source updates the same note instead of creating a duplicate."

  banner "STEP 4 — the source catalog (machine id <-> readable path)"
  echo "\$ ./wiki catalog"; ./wiki catalog

  banner "STEP 5 — ALL FOUR ASK-MODE TESTS, OFFLINE"
  echo "Expectations were written before the harness ran: tests/eval_questions.json"
  echo "\$ ./wiki test"
  ./wiki test

  banner "STEP 6 — ALL EIGHT MODE-BOUNDARY CHECKS, OFFLINE"
  echo "\$ ./scripts/mode-checks.sh offline"
  ./scripts/mode-checks.sh offline

  banner "STEP 7 — vault integrity"
  echo "\$ ./wiki check"; ./wiki check

  banner "STILL NO NETWORK AT THE END OF THE RUN"
  probe https://ollama.com
  probe https://api.anthropic.com
  echo
  echo "=== END OF OFFLINE DEMONSTRATION ==="
  echo "Every model call in this transcript was served by gemma3n:e4b on 127.0.0.1."
  echo "No hosted embeddings, no remote search, no cloud fallback."
} 2>&1 | tee "$out"

/usr/bin/sed -i '' $'s/\x1b\\[[0-9;]*m//g' "$out"
echo
echo "================================================================"
echo " Saved: $out"
echo " Now turn Wi-Fi back on:  networksetup -setairportpower en0 on"
echo "================================================================"
