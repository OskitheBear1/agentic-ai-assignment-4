"""Search the local index and return evidence. This is the harness's one tool.

`search` mode exposes the output of this module directly with no model call, so
retrieval quality can be judged independently of whether Gemma answers well.
`ask` mode passes the same output into a prompt.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from . import config, index, model
from .documents import Passage


@dataclass
class Hit:
    passage: Passage
    rank: int                # 1-based position in the fused ranking
    bm25_rank: int | None
    vector_rank: int | None
    bm25_score: float
    vector_score: float
    fused_score: float
    scope_note: str | None = None

    @property
    def label(self) -> str:
        """The citation marker the model is told to use, e.g. S1."""
        return f"S{self.rank}"

    def why(self) -> str:
        parts = []
        if self.bm25_rank:
            parts.append(f"keyword #{self.bm25_rank} ({self.bm25_score:.2f})")
        if self.vector_rank:
            parts.append(f"vector #{self.vector_rank} ({self.vector_score:.3f})")
        return " + ".join(parts) or "no signal"


_COURSE_CODE_IN_QUESTION = re.compile(r"\b(?:MBA|EWMBA)\s?(\d{3}[A-Z]?)\b", re.I)


def _aliases_for(entry: dict) -> list[str]:
    """Names a person might use for one course: its note title, its course code,
    and the subject part of the title with the code stripped off."""
    title = entry.get("title", "")
    aliases = {title}
    match = _COURSE_CODE_IN_QUESTION.search(title)
    if match:
        aliases.add(match.group(0))
        aliases.add(match.group(1))
        subject = _COURSE_CODE_IN_QUESTION.sub("", title).strip(" -–—")
        if len(subject) > 3:
            aliases.add(subject)
    return [a for a in aliases if len(a) > 2]


def course_scope(question: str) -> tuple[set[str] | None, str | None]:
    """If the question names exactly one course, limit evidence to that course.

    This is the fix for the assignment's core failure mode. Asked "who is the GSI
    for Asset Management", the retriever happily returned the Negotiations
    syllabus -- it does contain a GSI -- and the model reported that GSI as Asset
    Management's. Prose instructions to check the subject helped but did not hold
    across runs. Removing the wrong course's passages from the candidate set
    removes the temptation entirely: the model cannot cite what it never sees.

    Two or more courses named, or none, means no restriction, so a comparison
    question still sees every source.
    """
    if not config.MANIFEST_FILE.exists():
        return None, None
    manifest = json.loads(config.MANIFEST_FILE.read_text(encoding="utf-8"))
    lowered = question.lower()
    matched: list[tuple[str, dict]] = []
    for entry in manifest.get("sources", {}).values():
        for alias in _aliases_for(entry):
            if re.search(rf"\b{re.escape(alias.lower())}\b", lowered):
                matched.append((alias, entry))
                break
    if len(matched) != 1:
        return None, None
    alias, entry = matched[0]
    allowed = {entry["source_path"]}
    if entry.get("note_path"):
        allowed.add(entry["note_path"])
    return allowed, f"question names only \"{alias}\"; evidence limited to that course"


def _ranked(scores: list[float], passages: list[Passage], limit: int) -> list[int]:
    order = sorted(range(len(passages)), key=lambda i: scores[i], reverse=True)
    return [i for i in order if scores[i] > 0][:limit]


def retrieve(
    query: str,
    top_k: int = config.TOP_K,
    scope: str = "all",
    use_vectors: bool = True,
    pool: int = 30,
    course_filter: bool = True,
) -> list[Hit]:
    """Hybrid retrieval: BM25 + dense vectors fused by Reciprocal Rank Fusion.

    Returns hits with ``scope_note`` set on the first hit when a course filter was
    applied, so the CLI and the evidence card can say why evidence was narrowed.
    """
    passages = index.load_passages()
    if scope != "all":
        passages = [p for p in passages if p.source_type == scope]
    allowed, note = (course_scope(query) if course_filter else (None, None))
    if allowed:
        narrowed = [p for p in passages if p.source_path in allowed]
        if narrowed:
            passages = narrowed
        else:
            note = None
    if not passages:
        return []

    bm25 = index.Bm25([index.tokenize(p.text) for p in passages])
    keyword_scores = bm25.score(index.tokenize(query))
    keyword_order = _ranked(keyword_scores, passages, pool)

    vector_scores = [0.0] * len(passages)
    vector_order: list[int] = []
    if use_vectors:
        stored = index.load_vectors()
        if stored:
            try:
                query_vector = model.embed_local([query])[0]
            except model.ModelUnavailable:
                # Degrade to keyword-only rather than failing the whole search.
                query_vector = None
            if query_vector:
                for i, passage in enumerate(passages):
                    vector = stored.get(passage.chunk_id)
                    if vector:
                        vector_scores[i] = index.cosine(query_vector, vector)
                vector_order = _ranked(vector_scores, passages, pool)

    fused: dict[int, float] = {}
    for position, i in enumerate(keyword_order, start=1):
        fused[i] = fused.get(i, 0.0) + 1.0 / (config.RRF_K + position)
    for position, i in enumerate(vector_order, start=1):
        fused[i] = fused.get(i, 0.0) + 1.0 / (config.RRF_K + position)

    # A generated note is a useful summary but the unchanged original is the
    # citable evidence, so raw passages are weighted above wiki passages on ties.
    for i in fused:
        fused[i] *= config.LAYER_WEIGHTS.get(passages[i].source_type, 1.0)

    keyword_positions = {i: n for n, i in enumerate(keyword_order, start=1)}
    vector_positions = {i: n for n, i in enumerate(vector_order, start=1)}

    ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)
    if ranked:
        floor = ranked[0][1] * config.MIN_SCORE_RATIO
        ranked = [(i, score) for i, score in ranked if score >= floor]
    ordered = _diversify(ranked, passages, top_k)
    hits = []
    for rank, (i, score) in enumerate(ordered, start=1):
        hits.append(
            Hit(
                passage=passages[i],
                rank=rank,
                bm25_rank=keyword_positions.get(i),
                vector_rank=vector_positions.get(i),
                bm25_score=keyword_scores[i],
                vector_score=vector_scores[i],
                fused_score=score,
                scope_note=note,
            )
        )
    return hits


def _diversify(
    ranked: list[tuple[int, float]], passages: list[Passage], top_k: int
) -> list[tuple[int, float]]:
    """Cap how many passages one document may contribute.

    Without this, a question spanning two syllabi filled all six slots from the
    single document that matched most strongly, and the second source never
    reached the prompt. Overflow is appended only if slots remain unfilled.
    """
    per_document: dict[str, int] = {}
    selected: list[tuple[int, float]] = []
    overflow: list[tuple[int, float]] = []
    for i, score in ranked:
        key = passages[i].source_path
        if per_document.get(key, 0) >= config.MAX_PER_DOCUMENT:
            overflow.append((i, score))
            continue
        per_document[key] = per_document.get(key, 0) + 1
        selected.append((i, score))
        if len(selected) == top_k:
            return selected
    return (selected + overflow)[:top_k]


def format_evidence_block(hits: list[Hit], max_chars: int = config.MAX_CONTEXT_CHARS) -> str:
    """Render hits as the numbered passage list the prompts refer to as [S1]..

    Truncation is explicit and budgeted: the model has a small context window,
    so the harness caps total evidence text instead of sending the whole wiki.
    """
    blocks: list[str] = []
    used = 0
    for hit in hits:
        text = hit.passage.text.strip()
        page = f", page {hit.passage.page}" if hit.passage.page else ""
        header = (
            f"[{hit.label}] from \"{hit.passage.source_title}\" "
            f"({hit.passage.source_path}{page}, section: {hit.passage.section})"
        )
        remaining = max_chars - used - len(header)
        if remaining < 200:
            break
        if len(text) > remaining:
            text = text[:remaining].rstrip() + " ...[truncated]"
        block = f"{header}\n{text}"
        blocks.append(block)
        used += len(block)
    return "\n\n".join(blocks)
