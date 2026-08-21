"""Entity normalization, GLEIF adapter and candidate scoring."""

from app.services.entity_resolution.scoring import (
    HIGH_SIMILARITY_THRESHOLD,
    normalize_entity_name,
    score_name_similarity,
)
from app.services.entity_resolution.service import EntityResolutionService, PartyIdentityInput

__all__ = [
    "HIGH_SIMILARITY_THRESHOLD",
    "EntityResolutionService",
    "PartyIdentityInput",
    "normalize_entity_name",
    "score_name_similarity",
]
