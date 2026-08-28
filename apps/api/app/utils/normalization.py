"""Text normalization utilities for document intelligence and entity resolution.

This module provides standardized text normalization helpers for fuzzy comparison,
reconciliation, and entity matching across the TradePulse platform.
"""
import re
from typing import Any


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_text(value: str | int | float | None) -> str | None:
    """
    Normalize text for fuzzy comparison and reconciliation.

    Performs:
    - Converts to lowercase
    - Removes non-alphanumeric characters (replaced with spaces)
    - Collapses whitespace
    - Returns None for empty strings or None input

    Args:
        value: Text-like value to normalize (str, int, float, or None)

    Returns:
        Normalized string or None if input is None/empty

    Raises:
        TypeError: If value is not text-like (str, int, float, None)

    Examples:
        >>> normalize_text("ABC Corp. Ltd.")
        'abc corp ltd'
        >>> normalize_text("  HELLO  WORLD  ")
        'hello world'
        >>> normalize_text(123)
        '123'
        >>> normalize_text("")
        None
        >>> normalize_text(None)
        None
    """
    if value is None:
        return None
    if not isinstance(value, (str, int, float)):
        raise TypeError(
            f"Cannot normalize {type(value).__name__}. "
            f"Expected str, int, float, or None."
        )

    text = str(value).strip().lower()
    if not text:
        return None

    return _NON_ALNUM.sub(" ", text).strip()


def normalize_entity_name(name: str | None) -> str | None:
    """
    Normalize entity/company name for similarity scoring.

    Alias for normalize_text() with stricter type hint for entity resolution context.
    Use this when normalizing company names, party names, or entity identifiers.

    Args:
        name: Entity name string or None

    Returns:
        Normalized string or None

    Examples:
        >>> normalize_entity_name("ABC Corporation Ltd.")
        'abc corporation ltd'
        >>> normalize_entity_name(None)
        None
    """
    if name is None:
        return None
    return normalize_text(name)
