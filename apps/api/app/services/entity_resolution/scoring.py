"""Name similarity scoring for GLEIF candidates. Never proves identity alone."""

from __future__ import annotations

import re


def normalize_entity_name(name: str | None) -> str | None:
    if name is None:
        return None
    cleaned = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
    return cleaned or None


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
