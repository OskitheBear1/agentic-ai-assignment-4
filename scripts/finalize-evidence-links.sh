#!/usr/bin/env bash
# Replaces the two "to be done" callouts in README.md with real links, once the
# offline transcript and the three Obsidian screenshots exist. Safe to re-run:
# it reports what is still missing and changes nothing until everything is there.
set -uo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec .venv/bin/python scripts/finalize_evidence_links.py "$@"
