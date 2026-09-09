"""
Case service module - split into focused submodules.

Structure:
- state.py    : PlatformState singleton management
- crud.py     : Case create, add_document, conversions
- pipeline.py : Document processing and compliance pipeline
- actions.py  : Workflow actions (maker/checker)

Import from this module for backward compatibility.
"""

from .actions import apply_case_action
from .crud import (
    add_document,
    create_case,
    evaluate_case_policy,
    to_case_record,
    to_case_summary,
)
from .pipeline import process_case
from .state import (
    PlatformState,
    get_platform_state,
    reset_platform_state,
)

__all__ = [
    # State
    "PlatformState",
    "get_platform_state",
    "reset_platform_state",
    # CRUD
    "create_case",
    "add_document",
    "evaluate_case_policy",
    "to_case_summary",
    "to_case_record",
    # Pipeline
    "process_case",
    # Actions
    "apply_case_action",
]