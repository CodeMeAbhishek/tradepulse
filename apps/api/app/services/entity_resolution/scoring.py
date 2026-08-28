"""Name similarity scoring for GLEIF candidates. Never proves identity alone."""

from __future__ import annotations

from app.utils.normalization import normalize_entity_name


def score_name_similarity(left: str | None, right: str | None) -> float:
    """Token Jaccard-ish score in [0, 1]. High score ≠ verified identity."""
    a = normalize_entity_name(left)
    b = normalize_entity_name(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.92
    ta, tb = set(a.split()), set(b.split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


HIGH_SIMILARITY_THRESHOLD = 0.85
