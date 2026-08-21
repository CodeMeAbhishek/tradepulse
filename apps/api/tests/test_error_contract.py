"""Error contract unit tests."""

from __future__ import annotations

from tradepulse_contracts import ApiError, ErrorBody, ErrorResponse


def test_error_response_shape() -> None:
    payload = ErrorResponse(
        error=ErrorBody(
            code="REFERENCE_DATA_UNAVAILABLE",
            message="OFAC snapshot is unavailable for this run; sanctions check was not passed.",
            correlation_id="corr-test-1",
            retryable=False,
        )
    )
    dumped = payload.model_dump()
    assert set(dumped.keys()) == {"error"}
    assert set(dumped["error"].keys()) == {"code", "message", "correlation_id", "retryable"}
    assert dumped["error"]["retryable"] is False


def test_api_error_carries_status() -> None:
    exc = ApiError(
        code="DATABASE_UNAVAILABLE",
        message="Database unavailable",
        status_code=503,
        retryable=True,
    )
    assert exc.status_code == 503
    assert exc.retryable is True
