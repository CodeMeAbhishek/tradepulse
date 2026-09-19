class TradePulseException(RuntimeError):
    """Base exception for TradePulse business logic errors.

    Subclasses are treated as runtime errors so existing callers/tests that
    expect RuntimeError continue to work.
    """

class InvalidVLEIStateError(TradePulseException):
    """Raised when VLEI verifier emits invalid status."""

class DocumentProcessingError(TradePulseException):
    """Raised when document processing fails."""
