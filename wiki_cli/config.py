"""Central configuration for the personal wiki harness.

Every path is relative to the repository root so the CLI can be launched from
anywhere. Machine-generated artefacts (retrieval chunks, embeddings, evidence
cards) deliberately live OUTSIDE ``vault/`` so that Obsidian only ever sees
curated Markdown.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- The Obsidian vault (human-readable, curated) -------------------------
VAULT = ROOT / "vault"
RAW_DIR = VAULT / "raw"          # original sources, never modified
WIKI_DIR = VAULT / "wiki"        # generated + reviewed notes
INDEX_PAGE = VAULT / "index.md"  # human landing page
WIKI_FOLDERS = ("Courses", "Topics", "People")

# --- Machine-only artefacts (kept out of the vault) -----------------------
INDEX_DIR = ROOT / ".wiki_index"
CHUNKS_FILE = INDEX_DIR / "chunks.jsonl"
VECTORS_FILE = INDEX_DIR / "vectors.jsonl"
CATALOG_FILE = INDEX_DIR / "source_catalog.json"
MANIFEST_FILE = INDEX_DIR / "ingest_manifest.json"

EVIDENCE_DIR = ROOT / "evidence"
# Human corrections to generated notes, applied after the model writes them.
# Outside the vault, so they are never retrieved as if they were source evidence.
CORRECTIONS_FILE = ROOT / "corrections" / "wiki-corrections.json"
INSTRUCTIONS_DIR = ROOT / "instructions"

# --- Model / runtime -----------------------------------------------------
OLLAMA_HOST = os.environ.get("WIKI_OLLAMA_HOST", "http://127.0.0.1:11434")
LOCAL_CHAT_MODEL = os.environ.get("WIKI_MODEL", "gemma3n:e4b")
LOCAL_EMBED_MODEL = os.environ.get("WIKI_EMBED_MODEL", "embeddinggemma:300m")

# Optional online extension. Never used unless --mode online is passed AND the
# key is present; local is always the default.
ONLINE_CHAT_MODEL = os.environ.get("WIKI_ONLINE_MODEL", "gemma-3-27b-it")
ONLINE_API_KEY_ENV = "GEMINI_API_KEY"
ONLINE_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

# --- Retrieval knobs ------------------------------------------------------
# Passage size is a tradeoff: small chunks retrieve precisely but lose the
# surrounding sentence that makes a number meaningful; large chunks carry
# context but dilute the keyword/vector signal and eat the context window.
# ~900 characters is roughly one syllabus subsection.
CHUNK_CHARS = 900
CHUNK_OVERLAP = 150
TOP_K = 6                # passages handed to the model in ask mode
SEARCH_K = 8             # passages printed by search mode
RRF_K = 60               # reciprocal-rank-fusion damping constant
MAX_PER_DOCUMENT = 3     # passages any single document may contribute to one answer
# Prune weak tail hits instead of padding the prompt to top_k with noise. A hit
# must score at least this fraction of the best hit's fused score to be sent to
# the model. Set from observation: with a flat top_k=6 a single-source question
# filled four slots with unrelated syllabi, which is how a model ends up citing
# the wrong course.
MIN_SCORE_RATIO = 0.35
# The unchanged original is the citable evidence; a generated note is a summary of
# it. Both are indexed, but raw outranks wiki when fused scores are close.
LAYER_WEIGHTS = {"raw": 1.0, "wiki": 0.9}
MAX_CONTEXT_CHARS = 6000  # hard cap on evidence text sent to Gemma

# --- Generation knobs -----------------------------------------------------
# Low temperature for ask/ingest: we want the passages reproduced faithfully,
# not creatively. Chat gets a little more room to draft.
# temperature 0 for ask. At 0.1 the same question produced a correct refusal on one
# run and a wrong answer on the next, which makes an evidence card unreproducible.
ASK_OPTIONS = {"temperature": 0.0, "top_p": 1.0, "num_ctx": 4096, "num_predict": 400}
INGEST_OPTIONS = {"temperature": 0.2, "top_p": 0.9, "num_ctx": 8192, "num_predict": 1400}
CHAT_OPTIONS = {"temperature": 0.6, "top_p": 0.95, "num_ctx": 4096, "num_predict": 600}
ROUTER_OPTIONS = {"temperature": 0.0, "num_ctx": 1024, "num_predict": 6}

CHAT_HISTORY_TURNS = 8   # how much conversation the harness replays


def ensure_dirs() -> None:
    for path in (INDEX_DIR, EVIDENCE_DIR, RAW_DIR, WIKI_DIR):
        path.mkdir(parents=True, exist_ok=True)
    for folder in WIKI_FOLDERS:
        (WIKI_DIR / folder).mkdir(parents=True, exist_ok=True)
