"""Shared datetime utilities for TradePulse.

This module provides standardized datetime helpers to ensure all timestamps
are timezone-aware and in UTC.
"""
from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Return current UTC datetime with timezone info.

    Use this instead of datetime.now() to ensure all timestamps
    are timezone-aware and in UTC.

    Returns:
        datetime: Current time in UTC with tzinfo=timezone.utc

    Example:
        >>> from app.utils.datetime import utc_now
        >>> now = utc_now()
        >>> now.tzinfo
        datetime.timezone.utc
    """
    return datetime.now(timezone.utc)
